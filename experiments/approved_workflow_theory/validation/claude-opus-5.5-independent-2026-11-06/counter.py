"""Independent reconstruction of the approved-core accounting (Claude Opus 5.5, 2026-11-06).

Written from REPLICATION_SPEC.md (version 1), AGENT_START_HERE.md, AIN_LANGUAGE_AND_THEORY.md, Draft 8 pages 1-4
and trace-inputs.json ONLY. The reference accounting.py, run.py, report.py, results/ and validation/ were not opened.
Execution checks use the approved function sources supplied in trace-inputs.json, run by this file's own executor,
and the oracle workloads.expected(task), which the spec permits reusing.

usage: python counter.py TRACE_INPUTS TOKENIZER_JSON WORKLOADS_PY OUTPUT_DIR
"""
import copy, hashlib, importlib.util, json, math, os, sys, time
from tokenizers import Tokenizer

PROFILES = ("python", "python_aliases", "ideal_ain", "ideal_ir", "ideal_python")
FIELDS = ("profile", "turn", "common_input_text_tokens", "artifact_input_units", "memory_input_units",
          "reprocessed_history_units", "shared_framing_positions", "input_positions", "authored_content_units",
          "output_positions", "host_observation_units")
TOKENIZER_SHA256 = "c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539"
MAX_PAYLOAD, MAX_DEPTH, SMALL_INT = 32767, 128, (-16384, 16383)
sha = lambda path: hashlib.sha256(open(path, "rb").read()).hexdigest()


# ---------------------------------------------------------------- text tokens (pinned Qwen2.5 tokenizer.json)
def make_counter(tokenizer_path):
    if sha(tokenizer_path) != TOKENIZER_SHA256:
        raise SystemExit("tokenizer.json hash does not match the pinned revision")
    tok = Tokenizer.from_file(tokenizer_path)
    return lambda text: len(tok.encode(text, add_special_tokens=False).ids)


# ---------------------------------------------------------------- Python rendering
def render_pipeline(calls, schema, name):
    expr = "r"
    for call in calls:
        operands = [repr(call["args"][a]) for a in schema[call["op"]]]
        expr = name(call["op"]) + "(" + ",".join([expr] + operands) + ")"
    return "lambda r:" + expr


def render_action(action, schema, name):
    if action["op"] == "write":
        return name("write") + "(" + render_pipeline(action["args"]["program"], schema, name) + ")"
    return name(action["op"]) + "(" + ",".join(repr(action["args"][a]) for a in schema[action["op"]]) + ")"


def render_batch(batch, schema, name):
    return ";".join(render_action(a, schema, name) for a in batch)


# ---------------------------------------------------------------- ideal units
class Units:
    def __init__(self, static_symbols, schema):
        self.static, self.schema = frozenset(static_symbols), schema

    @staticmethod
    def payload(nbytes):
        if nbytes > MAX_PAYLOAD:
            raise ValueError("scalar payload exceeds 32,767 bytes")
        return math.ceil(8 * nbytes / 15)

    def generic(self, v, depth=0, path=()):
        if depth > MAX_DEPTH:
            raise ValueError("nesting beyond 128 levels")
        t = type(v)
        if t is str:
            return 1 if v in self.static else 2 + self.payload(len(v.encode("utf-8")))
        if t is bool or v is None:
            return 1
        if t is int:
            return 2 + self.payload(len(str(v).encode("utf-8")))
        if t is float:
            if v != v or v in (float("inf"), float("-inf")):
                raise ValueError("nonfinite float")
            return 2 + self.payload(len(json.dumps(v, allow_nan=False, separators=(",", ":")).encode("utf-8")))
        if t in (list, dict):
            if id(v) in path:
                raise ValueError("cycle")
            if len(v) > MAX_PAYLOAD:
                raise ValueError("container exceeds 32,767 items")
            p = path + (id(v),)
            if t is list:
                return 2 + sum(self.generic(x, depth + 1, p) for x in v)
            if not all(type(k) is str for k in v):
                raise ValueError("non-string dictionary key")
            return 2 + sum(self.generic(k, depth + 1, p) + self.generic(x, depth + 1, p) for k, x in v.items())
        raise TypeError(f"unsupported type {t.__name__}")

    def typed(self, v, depth=0):
        t = type(v)
        if t is int and SMALL_INT[0] <= v <= SMALL_INT[1]:
            return 1
        if t is bool:
            return 1
        if t is list:
            if len(v) > MAX_PAYLOAD:
                raise ValueError("list exceeds 32,767 items")
            return 1 + sum(self.typed(x, depth + 1) for x in v)
        return self.generic(v, depth)

    def sequence(self, calls):
        return 1 + sum(1 + sum(self.typed(c["args"][a]) for a in self.schema[c["op"]]) for c in calls)

    def action(self, a):
        if a["op"] == "write":
            return 1 + self.sequence(a["args"]["program"])
        if a["op"] in ("record", "remember"):
            return 1 + self.generic(a["args"]["value"])
        return 1 + sum(self.typed(a["args"][k]) for k in self.schema[a["op"]])

    def batch(self, batch):
        return 1 + sum(self.action(a) for a in batch)


# ---------------------------------------------------------------- per-request recurrence
def ledger(episode, profile, cfg, count, units):
    schema = cfg["catalog_schema"]
    if profile.startswith("python"):
        name = (lambda op: cfg["aliases"][op]) if profile == "python_aliases" else (lambda op: op)
        A = count(render_pipeline(episode["predecessor"], schema, name)) if episode["predecessor"] else 0
        M = count(repr(episode["incoming_memory"])) if episode["incoming_memory"] else 0
        R_of = lambda b: count(render_batch(b, schema, name))
        O_of = lambda o: count(repr(o))
    else:
        A = units.sequence(episode["predecessor"]) if episode["predecessor"] else 0
        M = units.generic(episode["incoming_memory"]) if episode["incoming_memory"] else 0
        R_of, O_of = units.batch, units.generic
    C = count(json.dumps(episode["common_input"], separators=(",", ":")))
    H, rows = 0, []
    for i, (batch, obs) in enumerate(zip(episode["actions"], episode["host_observations"])):
        R, O = R_of(batch), O_of(obs)
        F = cfg["shared_request_framing"] + cfg["history_pair_framing"] * i
        out = R + cfg["response_end"]
        rows.append(dict(zip(FIELDS, (profile, i + 1, C, A, M, H, F, C + A + M + H + F, R, out, O))))
        H = H + out + O
    return rows


# ---------------------------------------------------------------- replay and execution checks
def load_core(sources):
    ns = {}
    exec(sources["_integer"], ns)
    for k, src in sources.items():
        if k != "_integer":
            exec(src, ns)
    return ns


def apply_patch(program, args):
    p = copy.deepcopy(program); call = p[args["index"]]
    if args["kind"] == "op":
        call["op"] = args["value"]
    else:
        call["args"][args["key"]] = args["value"]
    return p


def replay(episode):
    """Host replay of the episode's actions: returns the artifact and memory the actions produce."""
    artifact, memory = copy.deepcopy(episode["predecessor"]), None
    for batch in episode["actions"]:
        for a in batch:
            if a["op"] == "write": artifact = copy.deepcopy(a["args"]["program"])
            elif a["op"] == "patch": artifact = apply_patch(artifact, a["args"])
            elif a["op"] == "remember": memory = a["args"]["value"]
    return artifact, memory


def run_plan(core, plan, records):
    rows = copy.deepcopy(records)
    for call in plan:
        rows = core[call["op"]](rows, **call["args"])
    return rows


def main(trace_path, tokenizer_path, workloads_path, out_dir):
    t0 = time.time(); trace = json.load(open(trace_path, encoding="utf-8")); cfg = trace["config"]
    count = make_counter(tokenizer_path); units = Units(cfg["static_symbols"], cfg["catalog_schema"])
    spec = importlib.util.spec_from_file_location("workloads", workloads_path); W = importlib.util.module_from_spec(spec); spec.loader.exec_module(W)
    core = load_core(trace["approved_core_sources"])
    tasks = {(f["id"], s["stage"]): s for f in trace["fixtures"] for s in f["stages"]}
    episodes, totals, checks = [], {s: {p: {k: 0 for k in FIELDS[2:]} for p in PROFILES} for s in cfg["data_schedules"]}, []
    for e in trace["episodes"]:
        rows = [r for p in PROFILES for r in ledger(e, p, cfg, count, units)]
        for r in rows:
            for k in FIELDS[2:]:
                totals[e["schedule"]][r["profile"]][k] += r[k]
        fx = tasks[(e["chain"], e["stage"])]
        art, mem = replay(e)
        ts = time.perf_counter(); mine = run_plan(core, e["artifact"], fx["task"]["records"]); secs = time.perf_counter() - ts
        oracle = W.expected(fx["task"])
        checks.append({"chain": e["chain"], "stage": e["stage"], "schedule": e["schedule"],
                       "replayed_artifact_equals_artifact": art == e["artifact"], "replayed_memory_equals_outgoing": mem == e["outgoing_memory"],
                       "artifact_equals_fixture_plan": e["artifact"] == fx["plan"], "own_executor_equals_oracle": mine == oracle,
                       "reference_execute_equals_oracle": W.execute(e["artifact"], fx["task"]) == oracle, "supplied_success": e["success"],
                       "execution_seconds_host": secs})
        episodes.append({**e, "ledger": rows})
    os.makedirs(out_dir, exist_ok=True)
    json.dump(episodes, open(os.path.join(out_dir, "episodes.json"), "w"), indent=1)
    json.dump(totals, open(os.path.join(out_dir, "totals.json"), "w"), indent=1)
    json.dump(checks, open(os.path.join(out_dir, "checks.json"), "w"), indent=1)
    allc = lambda k: sum(c[k] for c in checks)
    print(f"episodes {len(episodes)}, ledger rows {sum(len(e['ledger']) for e in episodes)}, seconds {time.time() - t0:.1f}")
    for k in ("replayed_artifact_equals_artifact", "replayed_memory_equals_outgoing", "artifact_equals_fixture_plan", "own_executor_equals_oracle", "reference_execute_equals_oracle", "supplied_success"):
        print(f"  {k}: {allc(k)}/{len(checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
