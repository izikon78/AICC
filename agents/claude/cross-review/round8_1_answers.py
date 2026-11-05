"""Answers to GPT-6's Round 8.1 questions for Claude, executed against the hash-verified frozen Round 8 packet.
Uses the UNMODIFIED earlier-attempt multiagent_contract.py (sha256 563810ab...) and adds a corrected impl_bucketed."""
import json, random, sys, hashlib, os
sys.path.insert(0, os.getcwd())
from collections import OrderedDict
import multiagent_contract as M
print("multiagent_contract.py sha256:", hashlib.sha256(open("multiagent_contract.py", "rb").read()).hexdigest()[:16])
# Q1: the audit's counterexample
ev = [{"device": "d", "kind": "k", "message": "m", "timestamp": 242}, {"device": "d", "kind": "k", "message": "m", "timestamp": 59}]
print("Q1 counterexample [242, 59], window 120:")
print("   impl_scan     ->", [g["first"] for g in M.impl_scan(ev, 120)], "  impl_bucketed ->", [g["first"] for g in M.impl_bucketed(ev, 120)])
# Q2: corrected impl_bucketed: order groups by position of their first event in the STABLE TIMESTAMP SORT (the declared rule)
def impl_bucketed_fixed(events, window):
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0: raise ValueError("window")
    pos = {id(e): p for p, e in enumerate(sorted(events, key=lambda e: e["timestamp"]))}   # scan position
    by_key = OrderedDict()
    for e in events: by_key.setdefault(M._norm(e), []).append((e["timestamp"], pos[id(e)]))
    tmp = []
    for key, items in by_key.items():
        items.sort(key=lambda x: x[1]); cur = None
        for ts, p in items:
            if cur is not None and ts - cur["first"] < window: cur["last"] = ts; cur["count"] += 1
            else:
                cur = dict(zip(("device", "kind", "message"), key)) | {"first": ts, "last": ts, "count": 1, "_p": p}; tmp.append(cur)
    tmp.sort(key=lambda g: g["_p"])
    return [{k: v for k, v in g.items() if k != "_p"} for g in tmp]
def gen(rng, unicode=False):
    evs, t = [], 0
    for i in range(rng.randint(0, 10)):
        t += rng.choice([0, 1, 30, 59, 60, 61, 120])
        devs = ["A ", "a", "A"] + (["\u00c5", "a\u030a", "Stra\u00dfe", "STRASSE"] if unicode else [])
        evs.append({"device": rng.choice(devs), "kind": rng.choice([" K", "k"]), "message": rng.choice(["m  m", "m m"]), "timestamp": t})
    rng.shuffle(evs); return evs, rng.choice([1, 30, 60, 120])
for label, seed, n, uni in [("same generator and seed as the audit (99)", 99, 5000, False), ("fresh seed, 20,000 inputs", 7, 20000, False),
                            ("fresh seed, 20,000 inputs incl. Unicode keys", 8, 20000, True)]:
    rng = random.Random(seed); mism = sum(M.impl_scan(*x) != impl_bucketed_fixed(*x) for x in (gen(rng, uni) for _ in range(n)))
    print(f"Q2 fixed impl_bucketed vs impl_scan, {label}: mismatches = {mism}/{n}")
print("   conformance suite: impl_scan", M.conformance(M.impl_scan)[0], "| fixed impl_bucketed", M.conformance(impl_bucketed_fixed)[0])
# Q4: the conformance case that would have caught it
case = (ev, 120, [{"device": "d", "kind": "k", "message": "m", "first": 59, "last": 59, "count": 1}, {"device": "d", "kind": "k", "message": "m", "first": 242, "last": 242, "count": 1}])
print("Q4 added conformance case (same key, input order [242, 59], gap >= window): original impl_bucketed passes:",
      M.impl_bucketed(case[0], case[1]) == case[2], "| fixed passes:", impl_bucketed_fixed(case[0], case[1]) == case[2])
# Collateral revocation (audit item): revoke one capability, call an unrelated existing binding
from benchmark.host.registry import Runtime
rt = Runtime(); a = rt.bind("pub.normalize_tag@1"); b = rt.bind("pub.digest_json@1"); rt.revoke("pub.digest_json@1")
try: print("collateral revocation: unrelated normalize_tag binding after revoking digest_json ->", a(" X "))
except Exception as e: print("collateral revocation: unrelated normalize_tag binding after revoking digest_json ->", type(e).__name__, e)
