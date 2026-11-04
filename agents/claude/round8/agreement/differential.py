"""Differential interoperability test for group_by_window: sealed reference (via the host) vs three independent variants.
Writes conformance_vectors.json (reference outputs) so any third party can validate a variant without the source."""
import json, os, random, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from benchmark.host.registry import Runtime
import alt_python
REF = Runtime().bind("pub.group_by_window@1")
rng = random.Random(8)
DEV = ["Pump-1", "pump-1", "PUMP\u00a01", "pump 1", "valve", "Valve ", "\u0130stanbul", "istanbul", "\u01c5ab"]
ADV = {"sharp s": ["Stra\u00dfe", "STRASSE"], "final sigma": ["\u03a3\u0391\u03a3", "\u03c3\u03b1\u03c3"], "ligature": ["\ufb01x", "fix"],
       "U+001C separator": ["pump\x1c1"], "U+FEFF BOM": ["pump\ufeff1"]}
MSG = ["high pressure", "High pressure", " high  pressure ", "high\u2028pressure"]
ADV_MSG = {"U+001C separator": ["high\x1cpressure"], "U+FEFF BOM": ["high\ufeffpressure"]}
def case(feature):
    devs = DEV + (ADV.get(feature, []) * 3); msgs = MSG + (ADV_MSG.get(feature, []) * 3)
    evs = [{"device": rng.choice(devs), "kind": rng.choice(["pressure", "PRESSURE", "temp"]), "message": rng.choice(msgs),
            "timestamp": rng.randint(0, 300)} for _ in range(rng.randint(1, 12))]
    return {"events": evs, "window": rng.choice([1, 30, 60, 120]), "feature": feature}
INVALID = [{"events": [{"device": "d", "kind": "k", "message": "m", "timestamp": 1.5}], "window": 60, "feature": "invalid: float timestamp"},
           {"events": [{"device": "d", "kind": "k", "message": "m", "timestamp": True}], "window": 60, "feature": "invalid: bool timestamp"},
           {"events": [{"kind": "k", "message": "m", "timestamp": 1}], "window": 60, "feature": "invalid: missing device"},
           {"events": [], "window": 0, "feature": "invalid: window 0"}, {"events": [], "window": 1.5, "feature": "invalid: window 1.5"},
           {"events": [], "window": True, "feature": "invalid: window True"}]
FEATURES = ["clean", "sharp s", "final sigma", "ligature", "U+001C separator", "U+FEFF BOM"]
cases = [case(f) for f in FEATURES for _ in range(200)] + INVALID
def py_result(fn, c):
    try: return {"ok": True, "groups": fn(c["events"], c["window"])}
    except Exception as e:
        code = getattr(e, "code", None) or {"TypeError": "E_TYPE", "ValueError": "E_WINDOW"}.get(type(e).__name__, type(e).__name__)
        return {"ok": False, "code": code}
ref = [py_result(REF, c) for c in cases]
variants = {"alt_python (contract)": [py_result(alt_python.group_by_window, c) for c in cases]}
payload = json.dumps([{"events": c["events"], "window": c["window"]} for c in cases])
for name, f in [("alt_js_naive (shared text, JS defaults)", "./alt_js_naive.js"), ("alt_js_faithful (contract tables)", "./alt_js_faithful.js")]:
    out = subprocess.run(["node", "run_js.js", f], input=payload, capture_output=True, text=True, cwd=HERE, check=True).stdout
    variants[name] = json.loads(out)
report = {}
print(f"{'variant':42s} " + " ".join(f"{f[:14]:>14s}" for f in FEATURES) + f" {'invalid':>8s}  total")
for name, res in variants.items():
    row = {}
    for f in FEATURES + ["invalid"]:
        idx = [i for i, c in enumerate(cases) if (c["feature"] == f or (f == "invalid" and c["feature"].startswith("invalid")))]
        row[f] = (sum(res[i] == ref[i] for i in idx), len(idx))
    tot = (sum(a for a, _ in row.values()), sum(b for _, b in row.values())); report[name] = {**{k: list(v) for k, v in row.items()}, "total": list(tot)}
    print(f"{name:42s} " + " ".join(f"{a:>9d}/{b:<4d}" for a, b in [row[f] for f in FEATURES]) + f" {row['invalid'][0]:>4d}/{row['invalid'][1]:<3d} {tot[0]}/{tot[1]}")
for name, res in variants.items():
    bad = [i for i in range(len(cases)) if res[i] != ref[i]]
    if bad:
        i = bad[0]; c = cases[i]
        print(f"\nfirst divergence for {name} ({c['feature']}):\n  input devices/messages: {[(e.get('device'), e.get('message')) for e in c['events']][:3]}\n  reference: {json.dumps(ref[i], ensure_ascii=False)[:160]}\n  variant:   {json.dumps(res[i], ensure_ascii=False)[:160]}")
json.dump([{"events": c["events"], "window": c["window"], "expected": r} for c, r in zip(cases, ref)], open(os.path.join(HERE, "conformance_vectors.json"), "w"), ensure_ascii=False)
json.dump(report, open(os.path.join(HERE, "differential_results.json"), "w"), indent=1)
print(f"\nconformance_vectors.json: {len(cases)} cases, {os.path.getsize(os.path.join(HERE, 'conformance_vectors.json'))} bytes")
