"""Differential test: reused capability (via Arm A wrapper) vs the independent contract-only implementation.
Each feature class injects exactly one kind of contract-ambiguous input; disagreements are attributed to that feature."""
import json, random, importlib.util
def load(p):
    s = importlib.util.spec_from_file_location(p.replace(".", "_"), p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
REF, MINE = load("submission.py").run_rollup, load("contract_reimpl.py").run_rollup
rng = random.Random(7)
DEV, KIND, MSG = ["pump-1", "pump-2", "valve-a"], ["pressure", "temp"], ["high pressure", "sensor lost", "door open"]
def clean(i, t):
    return {"event_id": f"e{i:03d}", "device": rng.choice(DEV), "kind": rng.choice(KIND), "message": rng.choice(MSG),
            "timestamp": t, "severity": rng.choice(["info", "warning", "critical"])}
def variant(e, feature):
    e = dict(e)
    if feature == "severity padded with spaces": e["severity"] = " " + e["severity"] + " "
    elif feature == "message edge whitespace": e["message"] = "  " + e["message"] + " "
    elif feature == "message non-breaking space": e["message"] = e["message"].replace(" ", "\u00a0")
    elif feature == "event_id padded": e["event_id"] = " " + e["event_id"]
    elif feature == "mixed case and padding in device/kind": e["device"] = "  " + e["device"].upper(); e["kind"] = e["kind"].title() + " "
    elif feature == "duplicate event_ids": e["event_id"] = "dup"
    elif feature == "none (clean control)": pass
    return e
FEATURES = ["none (clean control)", "mixed case and padding in device/kind", "event_id padded", "duplicate event_ids",
            "severity padded with spaces", "message edge whitespace", "message non-breaking space"]
def strip_sev(groups): return [{k: v for k, v in g.items() if k != "severity"} for g in groups]
report = {}
for f in FEATURES:
    diff_any = diff_nosev = 0
    for trial in range(300):
        evs, t = [], 0
        for i in range(rng.randint(1, 25)):
            t += rng.choice([0, 30, 200, 599, 600, 601, 1500]); e = clean(i, t)
            evs.append(variant(e, f) if rng.random() < 0.5 else e)
        rng.shuffle(evs); w = rng.choice([60, 600, 3600]); s = rng.choice([0, 1, 2])
        a, b = REF(evs, w, s), MINE(evs, w, s)
        diff_any += a != b; diff_nosev += strip_sev(a) != strip_sev(b)
    report[f] = {"trials": 300, "disagree": diff_any, "disagree_ignoring_severity_format": diff_nosev}
    print(f"{f:42s} disagree {diff_any:3d}/300   ignoring severity representation {diff_nosev:3d}/300")
json.dump(report, open("differential_results.json", "w"), indent=1)
