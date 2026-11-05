"""Mutation adequacy of the conformance suite: deliberately wrong implementations must be detected.
Each mutant patches the shared primitives / reference composition; it is run against the HAND and CRASH cases."""
import importlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness, cases
from ain_v0 import primitives as P, reference as R

def global_dedupe(d, c, h): return dict(d)                                  # no horizon eviction
def sliding_window(state, e, cfg):                                           # joins while ts - LAST < window
    orig = P.add_to_group.__wrapped__ if hasattr(P.add_to_group, "__wrapped__") else None
    k = json.dumps(P.group_key(e), ensure_ascii=False); gid = state["newest"].get(k)
    g = next((x for x in state["groups"] if x["first_offset"] == gid), None) if gid is not None else None
    if g is not None and e["timestamp"] - g["last"] < cfg["window"]:
        g["last"] = e["timestamp"]; g["count"] += 1; g["severity_sum"] += e["severity"]; return
    return ORIG["add_to_group"](state, e, cfg)
def python_split_collapse(s): return " ".join(s.split())                     # Python whitespace, not the contract set
def late_reserves_id(state, r, cfg):                                         # late rows reserve their ID
    if r["timestamp"] < P.frontier(state["watermark"], cfg["lateness"]):
        state["counters"]["late"] += 1; state["dedupe"].setdefault(P.dedupe_key(r), r["timestamp"]); return
    return ORIG["admit_event"](state, r, cfg)
def filter_before_reserve(state, r, cfg):                                    # low-severity first rows do not reserve
    if r["severity"] < cfg["minimum"] and r["timestamp"] >= P.frontier(state["watermark"], cfg["lateness"]) and P.dedupe_key(r) not in state["dedupe"]:
        state["counters"]["filtered"] += 1; return
    return ORIG["admit_event"](state, r, cfg)
def batched_checks(groups, policy, version, cfg, hooks, schedule):           # cancellation/authority only at batch entry
    if groups and hooks["cancel"]("policy_start"): return {}, "CANCELLED"
    if groups and not hooks["authority"]("policy_start"): return {}, "AUTHORITY"
    quiet = dict(hooks); quiet["cancel"] = lambda p: False; quiet["authority"] = lambda p: True
    return ORIG["run_policy_calls"](groups, policy, version, cfg, quiet, schedule)

ORIG = {"add_to_group": P.add_to_group, "admit_event": R.admit_event, "run_policy_calls": P.run_policy_calls}
MUTANTS = {
    "global dedupe instead of horizon dedupe": [(P, "evict_dedupe", global_dedupe), (R, "evict_dedupe", global_dedupe)],
    "sliding window instead of anchored": [(P, "add_to_group", sliding_window), (R, "add_to_group", sliding_window)],
    "Python whitespace instead of contract set": [(P, "collapse", python_split_collapse), (R, "collapse", python_split_collapse)],
    "late rows reserve their IDs": [(R, "admit_event", late_reserves_id)],
    "severity filter before ID reservation": [(R, "admit_event", filter_before_reserve)],
    "batched away per-call cancel/authority checks": [(P, "run_policy_calls", batched_checks), (R, "run_policy_calls", batched_checks)],
}
report = {}
for name, patches in MUTANTS.items():
    saved = [(m, a, getattr(m, a)) for m, a, _ in patches]
    for m, a, f in patches: setattr(m, a, f)
    try:
        caught = [c["name"] for c in cases.HAND if c["expect"](harness.execute("reference", c))]
    finally:
        for m, a, f in saved: setattr(m, a, f)
    report[name] = caught
    print(f"{name:48s} detected by {len(caught):2d} case(s): {', '.join(caught[:4])}{' ...' if len(caught) > 4 else ''}")
json.dump(report, open(os.path.join(os.path.dirname(harness.HERE), "results", "mutant-detection.json"), "w"), indent=1)
print("mutants detected:", sum(1 for v in report.values() if v), "of", len(report))
