"""Differential fuzz: contract-only reimplementation vs the reference baseline (which Arm B also reuses)."""
import random, json, traceback
from benchmark.public import baseline_api as REF
import reimpl_from_contract as MINE
rng = random.Random(8)
def rand_tag():
    parts = []
    for _ in range(rng.randint(0, 4)):
        parts.append(rng.choice(["Disk", "DISK", "dísk", "ﬁle", "A", "  ", "\t", "Ⅳ", "ß", "x"]))
    return rng.choice([" ", "  ", "\t", "\n"]).join(parts)
def rand_money():
    sign = rng.choice(["", "+", "-"]); whole = str(rng.randint(0, 999)); frac = rng.choice(["", "." + str(rng.randint(0, 9999))])
    return rng.choice([sign + whole + frac, "  " + sign + whole + frac + " ", "1.005", "2.675", "0.005"])
def rand_params():
    d = {}
    for _ in range(rng.randint(0, 5)):
        k = rng.choice(["a","b","q","z","key"]); v = rng.choice([True, False, None, "A B", "/", rng.randint(0,9), [1,2], ["x","y"]])
        d[k] = v
    return d
def rand_events():
    out = []; t = 0
    for i in range(rng.randint(0, 12)):
        t += rng.choice([0, 1, 30, 59, 60, 61, 200])
        out.append({"device": rng.choice(["A ","a","  A","dev"]), "kind": rng.choice([" ALERT","alert","Alert"]),
                    "message": rng.choice(["Disk  low","Disk low","disk low"]), "timestamp": t, "severity": "info"})
    rng.shuffle(out); return out
def rand_delays(): return (rng.randint(0, 8), rng.choice([1, 10, 100]), rng.choice([50, 450, 10000]))
SUITES = {
 "normalize_tag": (rand_tag, 1), "normalize_whitespace": (rand_tag, 1), "parse_money": (rand_money, 1),
 "canonical_json": (lambda: rng.choice([1, 1.0, {"b":1,"a":[1,2]}, {"é":1}, [True, None], "x"]), 1),
 "make_query": (rand_params, 1), "group_by_window": (rand_events, 1), "retry_delays": (rand_delays, 3),
}
def call(fn, arg, arity):
    try: return ("ok", fn(*arg) if arity > 1 else fn(arg))
    except Exception as e: return ("err", type(e).__name__)
report = {}
for name, (gen, arity) in SUITES.items():
    ref, mine = getattr(REF, name), getattr(MINE, name)
    disagree, ex = 0, None
    for _ in range(2000):
        arg = gen()
        a, b = call(ref, arg, arity), call(mine, arg, arity)
        if a != b:
            disagree += 1
            if ex is None: ex = (arg, a, b)
    report[name] = {"disagree": disagree, "of": 2000, "example": ex}
    flag = "" if disagree == 0 else "  <-- DIVERGES"
    print(f"{name:22s} disagree {disagree:4d}/2000{flag}")
    if ex and disagree: print(f"    first: input={ex[0]!r}  ref={ex[1]}  mine={ex[2]}")
json.dump(report, open("reimpl_fuzz_results.json","w"), default=str, indent=1)
