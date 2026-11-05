"""AIN v0 typed core: one operation catalog, two front ends (readable typed IR and numeric AIN), one AST,
one deterministic type checker, and an interpreter that lowers the operator graph onto lazy stream stages.

v0 is an OPERATOR-GRAPH core matching docs/ain/COMPLEX_TASK.md's sketch: programs wire the 21 operations, whose
bodies come from the shared primitives. In v0 the AIN spelling is a mechanical renaming of the typed IR, so plan
forms 3 (symbolic spelling) and 4 (AIN candidate) COINCIDE and are merged."""
import copy, re
from . import primitives as P

ENTRY = ("Source", "Manifest", "Policy", "Sink", "Cancel")
LINEAR = {"Source", "Records", "Valid", "Admitted", "Unique", "Normalized", "Kept", "Epochs", "Grouped", "Finalized",
          "Scored", "Ordered", "Resolved", "Staged", "Committed", "Acked", "Retired"}
# id: (ir name, argument types, result type, effect)
CATALOG = {
    "010": ("config.validate", ("IntList9",), "Config", None),
    "011": ("manifest.pin", ("Manifest", "Config"), "Pinned", None),
    "012": ("checkpoint.restore", ("Sink", "Pinned", "Config"), "State", "sink.read"),
    "013": ("source.open", ("Source", "State", "Cancel"), "Records", "source.read"),
    "101": ("record.validate", ("Records", "Config"), "Valid", None),
    "102": ("record.admit", ("Valid", "State", "Config"), "Admitted", None),
    "103": ("event.dedupe", ("Admitted", "State", "Config"), "Unique", None),
    "104": ("event.normalize", ("Unique", "State", "Config"), "Normalized", None),
    "105": ("event.filter", ("Normalized", "Severity", "Config"), "Kept", None),
    "106": ("epoch.buffer", ("Kept", "State", "Config"), "Epochs", None),
    "107": ("epoch.group", ("Epochs", "State", "Config"), "Grouped", None),
    "108": ("epoch.finalize", ("Grouped", "State", "Config"), "Finalized", None),
    "109": ("policy.score", ("Finalized", "Policy", "Pinned", "Cancel", "Config"), "Scored", "policy.invoke"),
    "110": ("report.order", ("Scored", "Config"), "Ordered", None),
    "111": ("epoch.resolve", ("Ordered", "Cancel", "Config"), "Resolved", None),
    "112": ("txn.stage", ("Resolved", "State", "Pinned", "Config"), "Staged", None),
    "113": ("txn.commit", ("Staged", "Sink", "Cancel", "Config"), "Committed", "sink.commit"),
    "114": ("cursor.advance", ("Committed", "State", "Config"), "Acked", None),
    "115": ("state.retire", ("Acked", "Config"), "Retired", None),
    "116": ("stream.drain", ("Retired", "Cancel", "Config"), "Outcome", None),
}
BY_NAME = {v[0]: k for k, v in CATALOG.items()}


class CoreError(Exception):
    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}"); self.code, self.detail = code, detail


# ---------------------------------------------------------------- AST: params, statements (op, args), return ref
# arg = ("v", index) | ("int", n) | ("list", (n, ...)); value index: params 0..4, statement k -> 5 + k
def _lex(text, spec):
    pos, out = 0, []
    for m in re.finditer(spec, text):
        if m.start() != pos and text[pos:m.start()].strip():
            raise CoreError("E_SYNTAX", f"unexpected {text[pos:m.start()].strip()[:12]!r}")
        pos = m.end()
        if m.lastgroup != "ws":
            out.append((m.lastgroup, m.group()))
    if text[pos:].strip():
        raise CoreError("E_SYNTAX", f"unexpected {text[pos:].strip()[:12]!r}")
    return out


class _Toks:
    def __init__(self, toks): self.t, self.i = toks, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else ("eof", "")
    def take(self, kind=None, val=None):
        k, v = self.peek()
        if (kind and k != kind) or (val is not None and v != val):
            raise CoreError("E_SYNTAX", f"expected {val or kind}, got {v or k!r}")
        self.i += 1; return v


def _args(ts, ref):
    args = []
    ts.take("p", "(")
    while True:
        k, v = ts.peek()
        if k == "int":
            args.append(("int", int(ts.take())))
        elif v == "[":
            ts.take(); items = [int(ts.take("int"))]
            while ts.peek()[1] == ",":
                ts.take(); items.append(int(ts.take("int")))
            ts.take("p", "]"); args.append(("list", tuple(items)))
        else:
            args.append(ref(ts))
        if ts.peek()[1] == ",":
            ts.take(); continue
        ts.take("p", ")"); return tuple(args)


IR_SPEC = r"(?P<ws>\s+)|(?P<op>[a-z_]+(?:\.[a-z_]+)+)|(?P<id>[A-Za-z_][A-Za-z0-9_]*)|(?P<int>\d+)|(?P<p>[(){}\[\],;:=])"
AIN_SPEC = r"(?P<ws>\s+)|(?P<fn>@\d\d)|(?P<val>%\d\d)|(?P<op>!\d\d\d)|(?P<int>\d+)|(?P<p>[(){}\[\],;=])"


def parse_ir(text):
    ts = _Toks(_lex(text, IR_SPEC)); names = {}
    ts.take("id", "fn"); ts.take("id"); ts.take("p", "("); types = []
    while True:
        n = ts.take("id"); ts.take("p", ":"); t = ts.take("id")
        if n in names: raise CoreError("E_REDEFINED", n)
        names[n] = len(types); types.append(t)
        if ts.peek()[1] == ",": ts.take(); continue
        ts.take("p", ")"); break
    def ref(t):
        n = t.take("id")
        if n not in names: raise CoreError("E_UNDEFINED", n)
        return ("v", names[n])
    ts.take("p", "{"); stmts = []
    while ts.peek()[1] != "return":
        n = ts.take("id"); ts.take("p", "="); opname = ts.take("op")
        if opname not in BY_NAME: raise CoreError("E_UNKNOWN_OP", opname)
        args = _args(ts, ref); ts.take("p", ";")
        if n in names: raise CoreError("E_REDEFINED", n)
        stmts.append((BY_NAME[opname], args)); names[n] = len(types) + len(stmts) - 1
    ts.take("id", "return"); r = ref(ts); ts.take("p", ";"); ts.take("p", "}")
    if ts.peek()[0] != "eof": raise CoreError("E_RETURN", "text after return")
    return {"params": tuple(types), "stmts": tuple(stmts), "ret": r[1]}


def parse_ain(text):
    ts = _Toks(_lex(text, AIN_SPEC)); names = {}
    if ts.take("fn") != "@00": raise CoreError("E_UNKNOWN_OP", "entry must be @00")
    ts.take("p", "("); n_params = 0
    while True:
        v = ts.take("val")
        if v in names: raise CoreError("E_REDEFINED", v)
        names[v] = n_params; n_params += 1
        if ts.peek()[1] == ",": ts.take(); continue
        ts.take("p", ")"); break
    def ref(t):
        v = t.take("val")
        if v not in names: raise CoreError("E_UNDEFINED", v)
        return ("v", names[v])
    ts.take("p", "{"); stmts = []
    while ts.peek()[1] != "!001":
        v = ts.take("val"); ts.take("p", "="); op = ts.take("op")[1:]
        if op not in CATALOG: raise CoreError("E_UNKNOWN_OP", "!" + op)
        args = _args(ts, ref); ts.take("p", ";")
        if v in names: raise CoreError("E_REDEFINED", v)
        stmts.append((op, args)); names[v] = n_params + len(stmts) - 1
    ts.take("op", "!001"); ts.take("p", "("); r = ref(ts); ts.take("p", ")"); ts.take("p", ";"); ts.take("p", "}")
    if ts.peek()[0] != "eof": raise CoreError("E_RETURN", "text after return")
    # AIN parameters are typed by position (entry signature); an arity mismatch is reported by the checker.
    return {"params": ENTRY[:n_params] + ("?",) * max(0, n_params - len(ENTRY)), "stmts": tuple(stmts), "ret": r[1]}


# ---------------------------------------------------------------- deterministic type checker (first error wins)
def check(ast):
    if tuple(ast["params"]) != ENTRY:
        raise CoreError("E_PARAMS", f"expected {ENTRY}, got {tuple(ast['params'])}")
    types = list(ENTRY); uses = [0] * (len(ENTRY) + len(ast["stmts"])); effects = set(); filters = []
    for k, (op, args) in enumerate(ast["stmts"]):
        name, want, out, eff = CATALOG[op]
        if len(args) != len(want):
            raise CoreError("E_ARITY", f"!{op} {name}: expected {len(want)} arguments, got {len(args)}")
        for i, (a, w) in enumerate(zip(args, want)):
            if w == "IntList9":
                if a[0] != "list" or len(a[1]) != 9: raise CoreError("E_LITERAL", f"!{op} arg {i + 1}: nine-integer list required")
            elif w == "Severity":
                if a[0] != "int" or not 0 <= a[1] <= 3: raise CoreError("E_LITERAL", f"!{op} arg {i + 1}: severity literal 0..3 required")
                filters.append(a[1])
            elif a[0] != "v":
                raise CoreError("E_LITERAL", f"!{op} arg {i + 1}: value of type {w} required, got literal")
            elif types[a[1]] != w:
                raise CoreError("E_TYPE", f"!{op} {name} arg {i + 1}: expected {w}, got {types[a[1]]}")
            else:
                uses[a[1]] += 1
                if types[a[1]] in LINEAR and uses[a[1]] > 1:
                    raise CoreError("E_LINEAR_REUSE", f"!{op} arg {i + 1}: stream of type {w} consumed twice")
        if eff: effects.add(eff)
        types.append(out)
    if types[ast["ret"]] != "Outcome":
        raise CoreError("E_RETURN", f"return type {types[ast['ret']]}, expected Outcome")
    for i, t in enumerate(types):
        if t in LINEAR and uses[i] == 0:
            raise CoreError("E_LINEAR_UNUSED", f"stream value #{i} of type {t} is never consumed")
    if len(filters) != 1:
        raise CoreError("E_STATIC_CONFIG", f"exactly one event.filter required for configuration hoisting, found {len(filters)}")
    return {"effects": sorted(effects), "minimum": filters[0], "types": types}


# ---------------------------------------------------------------- printers (for round-trip and examples)
def to_ain(ast):
    ref = lambda i: f"%{90 + i:02d}" if i < len(ENTRY) else f"%{i - len(ENTRY):02d}"
    fmt = lambda a: ref(a[1]) if a[0] == "v" else str(a[1]) if a[0] == "int" else "[" + ",".join(map(str, a[1])) + "]"
    lines = ["@00(" + ",".join(ref(i) for i in range(len(ENTRY))) + ") {"]
    lines += [f"  {ref(len(ENTRY) + k)} = !{op}({','.join(fmt(a) for a in args)});" for k, (op, args) in enumerate(ast["stmts"])]
    return "\n".join(lines + [f"  !001({ref(ast['ret'])});", "}"]) + "\n"


def to_ir(ast, names):
    fmt = lambda a: names[a[1]] if a[0] == "v" else str(a[1]) if a[0] == "int" else "[" + ", ".join(map(str, a[1])) + "]"
    head = ", ".join(f"{names[i]}: {t}" for i, t in enumerate(ENTRY))
    lines = [f"fn workflow({head}) {{"]
    lines += [f"  {names[len(ENTRY) + k]} = {CATALOG[op][0]}({', '.join(fmt(a) for a in args)});" for k, (op, args) in enumerate(ast["stmts"])]
    return "\n".join(lines + [f"  return {names[ast['ret']]};", "}"]) + "\n"


# ---------------------------------------------------------------- lowering interpreter
class _Stream:
    def __init__(self, it, **meta): self.it, self.meta = it, meta
    def __iter__(self): return self.it


class _Ref:
    def __init__(self): self.s, self.pos = None, 0


def run(ast, env, info=None):
    """Lower the checked graph onto lazy generator stages over the shared primitives; return the outcome."""
    info = info or check(ast)
    hooks, sink, crash = env["hooks"], env["sink"], env.get("crash")
    ctx = {"fence": None, "pinned": None}

    def op010(lit):
        P.check_unicode(); return P.validate_config(list(lit), info["minimum"])   # D-29: filter literal hoisted
    def op011(manifest, cfg):
        ctx["pinned"] = P.pin_manifest(manifest, cfg, info["effects"]); return ctx["pinned"]
    def op012(snk, pinned, cfg):
        ctx["fence"] = snk.acquire_fence(); ref = _Ref(); ref.s, ref.pos = P.restore_state(snk, pinned, cfg, env["records"]); return ref
    def op013(source, ref, cancel):
        def gen():
            for r in source[ref.pos:]:
                if cancel("admit"): raise P.Cancelled()
                yield r
        return _Stream(gen(), cursor=ref.s["cursor"], ended=ref.s["complete"])
    def op101(records, cfg):
        def gen():
            prev, ended = records.meta["cursor"], records.meta["ended"]
            for r in records:
                kind = P.validate_record(r, prev, ended); prev = r["offset"]; yield kind, r
        return _Stream(gen())
    def op102(valid, ref, cfg):
        def gen():
            for kind, r in valid:
                if kind == "event" and r["timestamp"] < P.frontier(ref.s["watermark"], cfg["lateness"]):
                    ref.s["counters"]["late"] += 1; continue
                if kind == "watermark":
                    if r["watermark"] < ref.s["watermark"]:
                        raise P.WorkflowError("WATERMARK_ORDER", r["offset"], f"{r['watermark']} < {ref.s['watermark']}")
                    ref.s["watermark"] = r["watermark"]
                yield kind, r
        return _Stream(gen())
    def op103(admitted, ref, cfg):
        def gen():
            for kind, r in admitted:
                if kind == "event":
                    key = P.dedupe_key(r)
                    if key in ref.s["dedupe"]:
                        ref.s["counters"]["duplicate"] += 1; continue
                    if len(ref.s["dedupe"]) >= cfg["dedupe_entries"]:
                        raise P.WorkflowError("CAPACITY", r["offset"], "dedupe_entries")
                    ref.s["dedupe"][key] = r["timestamp"]
                yield kind, r
        return _Stream(gen())
    def op104(unique, ref, cfg):
        def gen():
            for kind, r in unique:
                if kind == "event":
                    r = {**r, "n_device": P.norm_tag(r["device"]), "n_kind": P.norm_tag(r["kind"]), "n_message": P.collapse(r["message"])}
                yield kind, r
        return _Stream(gen())
    def op105(normalized, minimum, cfg):
        def gen():
            for kind, r in normalized:
                if kind == "event" and r["severity"] < minimum:
                    ref_state()["counters"]["filtered"] += 1; continue
                yield kind, r
        return _Stream(gen())
    def op106(kept, ref, cfg):
        def gen():
            for kind, r in kept:
                if kind == "event":
                    if len(ref.s["buffer"]) >= cfg["buffered_events"]:
                        raise P.WorkflowError("CAPACITY", r["offset"], "buffered_events")
                    ref.s["buffer"].append(r); ref.s["counters"]["accepted"] += 1
                else:
                    end = kind == "end"
                    yield {"offset": r["offset"], "c": P.INF if end else P.frontier(r["watermark"], cfg["lateness"]), "end": end}
        return _Stream(gen())
    def op107(epochs, ref, cfg):
        def gen():
            for ep in epochs:
                c = ep["c"]; s = ref.s
                due = sorted((e for e in s["buffer"] if P.lt(e["timestamp"], c)), key=lambda e: (e["timestamp"], e["offset"]))
                s["buffer"] = [e for e in s["buffer"] if not P.lt(e["timestamp"], c)]
                for e in due: P.add_to_group(s, e, cfg)
                yield ep
        return _Stream(gen())
    def op108(grouped, ref, cfg):
        def gen():
            for ep in grouped:
                c = ep["c"]; s = ref.s
                final = sorted((g for g in s["groups"] if c == P.INF or g["first"] + cfg["window"] <= c), key=lambda g: (g["first"], g["first_offset"]))
                if len(final) > cfg["epoch_reports"]:
                    raise P.WorkflowError("CAPACITY", ep["offset"], "epoch_reports")
                done = {g["first_offset"] for g in final}
                s["groups"] = [g for g in s["groups"] if g["first_offset"] not in done]
                s["newest"] = {k: v for k, v in s["newest"].items() if v not in done}
                yield {**ep, "final": final}
        return _Stream(gen())
    def op109(finalized, policy, pinned, cancel, cfg):
        def gen():
            for ep in finalized:
                results, stop = P.run_policy_calls(ep["final"], policy, pinned["policy_version"], cfg, hooks, env["schedule"])
                yield {**ep, "results": results, "stop": stop}
        return _Stream(gen())
    def op110(scored, cfg):
        return _Stream(({**ep, "ordered": [ep["results"].get(i) for i in range(len(ep["final"]))]} for ep in scored))
    def op111(ordered, cancel, cfg):
        def gen():
            for ep in ordered:
                P.resolve_epoch(ep["results"], ep["stop"]); yield ep
        return _Stream(gen())
    def op112(resolved, ref, pinned, cfg):
        def gen():
            for ep in resolved:
                s = ref.s
                reports = [P.make_report(sink.source_id, g, ep["ordered"][i], pinned["policy_version"]) for i, g in enumerate(ep["final"])]
                s["dedupe"] = P.evict_dedupe(s["dedupe"], ep["c"], cfg["horizon"])
                s["cursor"], s["complete"] = ep["offset"], ep["end"]
                if crash and crash.fire("before_stage", ep["offset"]): raise P.Crash()
                yield {**ep, "payload": {"epoch": [sink.source_id, ep["offset"]], "reports": reports,
                                         "checkpoint": {"manifest_id": pinned["id"], "config": cfg, "state": copy.deepcopy(s)}}}
        return _Stream(gen())
    def op113(staged, snk, cancel, cfg):
        def gen():
            for ep in staged:
                off, payload = ep["offset"], ep["payload"]
                if crash and crash.fire("before_commit", off): raise P.Crash()
                if cancel("commit"): raise P.Cancelled()
                if not hooks["authority"]("commit"): raise P.WorkflowError("AUTHORITY", off, "commit")
                snk.commit(ctx["fence"], payload["epoch"], payload)
                if crash and crash.fire("after_commit", off): raise P.Crash()
                if crash and crash.fire("ack_lost_retry", off): snk.commit(ctx["fence"], payload["epoch"], payload)
                yield ep
        return _Stream(gen())
    def op114(committed, ref, cfg):
        return _Stream(({**ep, "acked": True} for ep in committed))
    def op115(acked, cfg):
        def gen():
            for ep in acked:
                state_ref[0].s = copy.deepcopy(ep["payload"]["checkpoint"]["state"]); yield ep
        return _Stream(gen())
    def op116(retired, cancel, cfg):
        try:
            for ep in retired:
                if ep["end"]: return P.outcome("COMPLETED")
            return P.outcome("COMPLETED" if state_ref[0].s["complete"] else "SUSPENDED")
        except P.Cancelled:
            return P.outcome("CANCELLED")
        except P.WorkflowError as e:
            return P.outcome("FAILED", e)

    state_ref = [None]
    ref_state = lambda: state_ref[0].s
    impl = {k: v for k, v in locals().items() if k.startswith("op")}
    values = [env["records"], env["manifest"], env["policy"], sink, hooks["cancel"]]
    try:
        for op, args in ast["stmts"]:
            argv = [values[a[1]] if a[0] == "v" else a[1] for a in args]
            out = impl["op" + op](*argv)
            if op == "012": state_ref[0] = out
            values.append(out)
        return values[ast["ret"]]
    except P.Cancelled:
        return P.outcome("CANCELLED")
    except P.WorkflowError as e:
        return P.outcome("FAILED", e)
