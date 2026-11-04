"""Held-out adversarial tests derived ONLY from fixtures/activity_contract.md and fixtures/baseline_api.md.
SPEC  = the contract states the expected behaviour; PASS/FAIL is meaningful.
UNSPEC = the contract does not decide; we record what the reused capability actually does.
Run: python adversarial_contract_tests.py [submission.py ...]   (black-box: calls run_rollup / run_controller)"""
import copy, importlib.util, json, sys

def load(path):
    spec = importlib.util.spec_from_file_location("sub_" + path.replace("/", "_").replace(".", "_"), path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def ev(i, d="pump-1", k="pressure", m="high pressure", t=0, s="warning", **extra):
    e = {"event_id": i, "device": d, "kind": k, "message": m, "timestamp": t, "severity": s}; e.update(extra); return e

def keyset(groups): return [(g["device"], g["kind"], g["message"], g["first_timestamp"], g["last_timestamp"], g["count"], list(g["event_ids"])) for g in groups]

def raises(fn, *a, **k):
    try: fn(*a, **k); return None
    except Exception as e: return type(e).__name__

def tests(R, C):
    out = []
    def spec(name, ok, detail=""): out.append(("SPEC", name, "PASS" if ok else "FAIL", detail))
    def unspec(name, observed): out.append(("UNSPEC", name, "OBSERVED", observed))
    # ---------- controller (baseline_api.md) ----------
    spec("controller: runs=1 single start message", C(1) == ["Starting controller service for 1 runs"])
    spec("controller: runs=4 ordinals 2..4", C(4)[1:] == [f"Restarting controller service for run {k} of 4" for k in (2, 3, 4)])
    spec("controller: large runs=100000 returns 100000 messages", len(C(100000)) == 100000)
    try: unspec("controller: runs=True (bool is an int subclass in Python)", repr(C(True)))
    except Exception as e: unspec("controller: runs=True", "raises " + type(e).__name__)
    try: unspec("controller: runs=3.0 (float)", repr(C(3.0))[:120])
    except Exception as e: unspec("controller: runs=3.0 (float)", "raises " + type(e).__name__)
    # ---------- rollup: validity ----------
    base = [ev("a", t=10)]
    spec("bool timestamp is invalid and skipped", len(R(base + [ev("b", t=True)])) == 1 and R(base + [ev("b", t=True)])[0]["count"] == 1)
    spec("negative timestamp is invalid", R(base + [ev("b", t=-5)])[0]["count"] == 1)
    spec("float timestamp 20.0 is invalid", R(base + [ev("b", t=20.0)])[0]["count"] == 1)
    spec("numeric-string timestamp '20' is invalid", R(base + [ev("b", t="20")])[0]["count"] == 1)
    spec("blank event_id '   ' is invalid", R(base + [ev("   ", t=20)])[0]["count"] == 1)
    spec("non-string message (None) is invalid", R(base + [ev("b", m=None, t=20)])[0]["count"] == 1)
    spec("empty-string message is valid (contract only requires a string)", len(R([ev("a", m="", t=1)])) == 1)
    spec("non-dict entries are skipped silently", len(R([None, "x", 5, ["l"], ev("a", t=1)])) == 1)
    spec("severity is case-insensitive ('CRITICAL')", len(R([ev("a", s="CRITICAL", t=1)])) == 1)
    spec("unknown severity 'error' is invalid", R([ev("a", s="error", t=1)]) == [])
    # ---------- rollup: normalisation ----------
    g = R([ev("a", d=" Pump-1 ", k="PRESSURE", t=0), ev("b", d="pump-1", k="pressure", t=5)])
    spec("device/kind trimmed and lower-cased, so the two events group", len(g) == 1 and g[0]["count"] == 2)
    g = R([ev("a", m="high   pressure", t=0), ev("b", m="high pressure", t=5)])
    spec("message internal whitespace collapsed", len(g) == 1 and g[0]["count"] == 2)
    g = R([ev("a", d="pump  1", t=0), ev("b", d="pump 1", t=5)])
    spec("device is NOT whitespace-collapsed (contract: trim + lowercase only)", len(g) == 2, f"groups={len(g)}")
    # ---------- rollup: windows, filtering, ordering ----------
    spec("window boundary inclusive (600 apart, window 600)", len(R([ev("a", t=0), ev("b", t=600)])) == 1)
    spec("601 apart starts a new group", len(R([ev("a", t=0), ev("b", t=601)])) == 2)
    spec("chaining on most recent accepted timestamp (0, 500, 1000)", len(R([ev("a", t=0), ev("b", t=500), ev("c", t=1000)])) == 1)
    g = R([ev("a", t=0, s="warning"), ev("b", t=500, s="info"), ev("c", t=1000, s="warning")], min_severity=1)
    spec("filtered events do not extend a window", len(g) == 2, f"groups={len(g)}")
    g = R([ev("b", t=5), ev("a", t=5), ev("c", t=1)])
    spec("event_ids in processing order (timestamp, event_id)", g[0]["event_ids"] == ["c", "a", "b"], str(g[0]["event_ids"]))
    g = R([ev("a", d="b-dev", t=5), ev("b", d="a-dev", t=5), ev("c", d="c-dev", t=1)])
    spec("groups ordered by (first_timestamp, device, ...)", [x["device"] for x in g] == ["c-dev", "a-dev", "b-dev"])
    g = R([ev("a", t=0, s="warning"), ev("b", t=1, s="critical"), ev("c", t=2, s="info")])
    unspec("representation of highest severity in output", repr(g[0]["severity"]))
    # ---------- rollup: errors ----------
    spec("window_seconds=True -> ValueError", raises(R, base, window_seconds=True) == "ValueError")
    spec("window_seconds=600.0 -> ValueError", raises(R, base, window_seconds=600.0) == "ValueError")
    spec("min_severity=True -> ValueError", raises(R, base, min_severity=True) == "ValueError")
    spec("min_severity=1.0 -> ValueError", raises(R, base, min_severity=1.0) == "ValueError")
    spec("events as tuple -> TypeError", raises(R, tuple(base)) == "TypeError")
    spec("events=None -> TypeError", raises(R, None) == "TypeError")
    unspec("both events and window invalid: which error wins", raises(R, None, window_seconds=0))
    # ---------- rollup: mutation ----------
    data = [ev(" a ", d=" PUMP ", m="x  y", t=3, s="WARNING"), ev("b", t=4)]
    snap = copy.deepcopy(data); R(data)
    spec("input list and dicts are not mutated", data == snap)
    # ---------- rollup: behaviours the contract leaves open ----------
    g = R([ev("a", s=" info ", t=1)]); unspec("severity with surrounding spaces ' info '", "valid" if g else "skipped")
    g = R([ev("a", m="  high pressure ", t=0), ev("b", m="high pressure", t=5)])
    unspec("message leading/trailing whitespace: groups with trimmed twin?", f"groups={len(g)}, message={g[0]['message']!r}")
    g = R([ev(" b", t=5), ev("a", t=5)])
    unspec("sort key uses trimmed or raw event_id; ids reported", repr(g[0]["event_ids"]))
    g = R([ev("a", t=1), ev("a", t=2)]); unspec("duplicate event_id counted twice?", f"count={g[0]['count']}, ids={g[0]['event_ids']}")
    g = R([ev("a", m="high\u00a0pressure", t=0), ev("b", m="high pressure", t=5)])
    unspec("non-breaking space treated as whitespace in message", f"groups={len(g)}")
    g = R([ev("a", t=1, extra_field=1)]); unspec("extra keys in event dicts", "accepted" if g else "skipped")
    return out

if __name__ == "__main__":
    paths = sys.argv[1:] or ["submission.py", "submission_registry.py"]
    results = {}
    for p in paths:
        m = load(p); rows = tests(m.run_rollup, m.run_controller); results[p] = rows
        n_spec = sum(1 for r in rows if r[0] == "SPEC"); n_pass = sum(1 for r in rows if r[2] == "PASS")
        print(f"\n### {p}: SPEC {n_pass}/{n_spec} pass")
        for r in rows:
            if r[2] != "PASS": print(f"  [{r[0]}] {r[1]}: {r[2]} {r[3]}")
    if len(paths) > 1:
        same = all(results[paths[0]] == results[p] for p in paths[1:])
        print(f"\nidentical results across {paths}: {same}")
    json.dump({p: rows for p, rows in results.items()}, open("adversarial_results.json", "w"), indent=1)
