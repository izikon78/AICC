"""Run the full AIN v0 conformance suite and write results/conformance-results.json and a console summary."""
import copy, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import execute, PROGRAMS, HERE
from cases import HAND, CRASH, random_cases, SPEC, C
from ain_v0 import core, primitives as P

FORMS = ("reference", "ir", "ain")
dump = lambda o: json.dumps(o, sort_keys=True, ensure_ascii=False, default=str)
results = {"started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "hand": [], "crash": [], "random": {}, "type_errors": [], "sink": []}

# 1. hand-derived cases: expectation on every form + identical effect traces across forms
for case in HAND:
    obs = {f: execute(f, case) for f in FORMS}
    fails = {f: case["expect"](obs[f]) for f in FORMS}
    same = len({dump(o) for o in obs.values()}) == 1
    results["hand"].append({"name": case["name"], "status": obs["reference"]["outcomes"][-1]["status"],
                            "error": (obs["reference"]["outcomes"][-1]["error"] or {}).get("code"),
                            "expectation_failures": fails, "forms_identical": same})

# 2. crash cases: INVARIANT = publications equal the uninterrupted run; each epoch committed exactly once
baseline = execute("reference", C("baseline", SPEC, None))
for case in CRASH:
    obs = {f: execute(f, case) for f in FORMS}
    o = obs["reference"]
    ok = (o["published"] == baseline["published"] and o["checkpoint"] == baseline["checkpoint"]
          and sum(1 for x in o["sink_log"] if x[0] == "commit") == 3 and o["outcomes"][-1]["status"] == "COMPLETED")
    results["crash"].append({"name": case["name"], "attempts": [x["status"] for x in o["outcomes"]],
                             "idempotent_receipts": sum(1 for x in o["sink_log"] if x[0] == "idempotent"),
                             "exactly_once_and_equal_to_uninterrupted": ok, "forms_identical": len({dump(x) for x in obs.values()}) == 1})

# 3. random differential traces: no oracle, forms must agree exactly
rand = random_cases(400); mism = []; dist = {}
for case in rand:
    obs = {f: execute(f, case) for f in FORMS}
    if len({dump(o) for o in obs.values()}) != 1:
        mism.append(case["name"])
    out = obs["reference"]["outcomes"][-1]; key = out["status"] + ("/" + out["error"]["code"] if out["error"] else "")
    dist[key] = dist.get(key, 0) + 1
results["random"] = {"cases": len(rand), "mismatches": mism, "outcome_distribution": dict(sorted(dist.items()))}

# 4. type errors: identical mutations through both front ends must give identical deterministic errors
ir_text, ain_text = open(os.path.join(PROGRAMS, "workflow.ir")).read(), open(os.path.join(PROGRAMS, "workflow.ain")).read()
base = core.parse_ir(ir_text)
NAMES = ["source", "manifest", "policy", "sink", "cancel", "config", "pinned", "state", "records", "valid", "admitted", "unique",
         "normalized", "kept", "epochs", "grouped", "finalized", "scored", "ordered", "resolved", "staged", "committed", "acked", "retired", "outcome"]
idx = {op: k for k, (op, _) in enumerate(base["stmts"])}
def mut(fn):
    a = copy.deepcopy({"params": base["params"], "stmts": [list(s) for s in base["stmts"]], "ret": base["ret"]}); fn(a)
    a["stmts"] = [tuple(s) for s in a["stmts"]]; return a
def setarg(op, i, val): return lambda a: a["stmts"][idx[op]].__setitem__(1, a["stmts"][idx[op]][1][:i] + (val,) + a["stmts"][idx[op]][1][i + 1:])
AST_MUTATIONS = {
    "arity: epoch.group missing config": lambda a: a["stmts"][idx["107"]].__setitem__(1, a["stmts"][idx["107"]][1][:2]),
    "type: dedupe before admission": setarg("103", 0, ("v", 5 + idx["101"])),
    "type: commit through policy handle (effect bypass)": setarg("113", 1, ("v", 2)),
    "type: policy and pinned swapped": lambda a: a["stmts"][idx["109"]].__setitem__(1, (("v", 5 + idx["108"]), ("v", 5 + idx["011"]), ("v", 2), ("v", 4), ("v", 5))),
    "literal: integer where Config expected": setarg("105", 2, ("int", 3)),
    "literal: severity 4": setarg("105", 1, ("int", 4)),
    "literal: eight-value configuration": setarg("010", 0, ("list", (600, 120, 1200, 8, 32, 100000, 200000, 100000))),
    "linear: stream consumed twice": lambda a: a["stmts"].insert(idx["107"] + 1, ["107", (("v", 5 + idx["106"]), ("v", 7), ("v", 5))]),
    "return: returns a stream, not Outcome": lambda a: a.__setitem__("ret", 5 + idx["115"]),
}
for label, fn in AST_MUTATIONS.items():
    a = mut(fn); names = NAMES + [f"extra{i}" for i in range(5)]
    for dst in (None,):
        pass
    try:
        ir_v = core.parse_ir(core.to_ir(a, names)); ir_err = None; core.check(ir_v)
    except core.CoreError as e: ir_err = [e.code, e.detail]
    try:
        ain_v = core.parse_ain(core.to_ain(a)); ain_err = None; core.check(ain_v)
    except core.CoreError as e: ain_err = [e.code, e.detail]
    results["type_errors"].append({"mutation": label, "level": "AST", "ir": ir_err, "ain": ain_err, "identical": ir_err == ain_err})
TEXT_MUTATIONS = {
    "undefined value": (("records = source.open(source, state, cancel);", "records = source.open(source, stat, cancel);"), ("!013(%90,%02,%94)", "!013(%90,%29,%94)")),
    "redefined value": (("valid = record.validate", "records = record.validate"), ("%04 = !101", "%03 = !101")),
    "unknown operation": (("event.dedupe(", "event.dedup("), ("!103(", "!199(")),
    "missing semicolon": (("config.validate([600, 120, 1200, 8, 32, 100000, 200000, 100000, 100000]);", "config.validate([600, 120, 1200, 8, 32, 100000, 200000, 100000, 100000])"),
                          ("100000,100000]);", "100000,100000])")),
    "wrong entry signature": (("source: Source,", "source: Sink,"), ("@00(%90,%91,%92,%93,%94)", "@00(%90,%91,%92,%93)")),
}
for label, ((io, inew), (ao, anew)) in TEXT_MUTATIONS.items():
    errs = []
    for parse, text, old, new in ((core.parse_ir, ir_text, io, inew), (core.parse_ain, ain_text, ao, anew)):
        assert old in text, label
        try:
            core.check(parse(text.replace(old, new, 1))); errs.append(None)
        except core.CoreError as e: errs.append([e.code, e.detail])
    results["type_errors"].append({"mutation": label, "level": "text", "ir": errs[0], "ain": errs[1], "identical": errs[0][0] == errs[1][0] if errs[0] and errs[1] else False})

# 5. sink conformance (shared by all forms): fencing, idempotent repeat, conflicting payload
s = P.Sink("src-1"); f1 = s.acquire_fence()
pay = {"epoch": ["src-1", 5], "reports": [{"r": 1}], "checkpoint": {"state": {"cursor": 5}}}
r1 = s.commit(f1, ["src-1", 5], pay); r2 = s.commit(f1, ["src-1", 5], pay)
results["sink"].append({"case": "idempotent repeat returns existing receipt, no new reports", "pass": r1 == r2 and len(s.published) == 1})
try:
    s.commit(f1, ["src-1", 5], {**pay, "reports": [{"r": 2}]}); ok = False
except P.WorkflowError as e: ok = e.code == "CONFLICT"
results["sink"].append({"case": "same epoch identity with different payload is CONFLICT", "pass": ok})
f2 = s.acquire_fence()
try:
    s.commit(f1, ["src-1", 9], {**pay, "epoch": ["src-1", 9]}); ok = False
except P.WorkflowError as e: ok = e.code == "FENCED"
results["sink"].append({"case": "stale writer cannot commit after a newer fence", "pass": ok and len(s.published) == 1})

results["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
os.makedirs(os.path.join(os.path.dirname(HERE), "results"), exist_ok=True)
json.dump(results, open(os.path.join(os.path.dirname(HERE), "results", "conformance-results.json"), "w"), indent=1, ensure_ascii=False)
hf = [h for h in results["hand"] if any(h["expectation_failures"].values()) or not h["forms_identical"]]
print(f"hand cases: {len(results['hand'])}, failing {len(hf)}")
for h in hf: print("  FAIL", h["name"], h["expectation_failures"], "identical" if h["forms_identical"] else "FORMS DIFFER")
print(f"crash cases: {len(results['crash'])}, invariant holds {sum(c['exactly_once_and_equal_to_uninterrupted'] for c in results['crash'])}, forms identical {sum(c['forms_identical'] for c in results['crash'])}")
print(f"random differential: {results['random']['cases']} cases, mismatches {len(results['random']['mismatches'])}, outcomes {results['random']['outcome_distribution']}")
print(f"type-error mutations: {len(results['type_errors'])}, identical across front ends {sum(t['identical'] for t in results['type_errors'])}")
for t in results["type_errors"]: print(f"  {t['level']:4s} {t['mutation']:48s} IR {t['ir'][0] if t['ir'] else None:16s} AIN {t['ain'][0] if t['ain'] else None}")
print(f"sink cases: {sum(c['pass'] for c in results['sink'])}/{len(results['sink'])} pass")
