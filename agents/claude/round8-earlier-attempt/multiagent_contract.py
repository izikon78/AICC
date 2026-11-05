"""Round 8 multi-agent track: one independently authored machine-checkable contract for group_by_window,
plus two alternative implementations, plus an executable conformance suite a third party could run.
This is ONE model's contract; it is NOT consensus."""
import json, bisect
from collections import OrderedDict

CONTRACT = {
 "id": "commons.group_by_window", "contract_version": 1,
 "signature": "group_by_window(events: list[dict], window: int) -> list[dict]",
 "preconditions": ["isinstance(window, int) and not isinstance(window, bool)", "window > 0",
                   "every event has str device, str kind, str message, int (non-bool) timestamp >= 0"],
 "normalization": {"device": "str.split()-collapse then ASCII lowercase", "kind": "same as device",
                   "message": "str.split()-collapse, preserve case"},
 "ordering": "stable sort by timestamp ascending (ties keep input order)",
 "grouping_key": ["norm_device", "norm_kind", "norm_message"],
 "window_rule": "a group stays open iff (event.timestamp - group.first) < window  (STRICT, measured from FIRST)",
 "output_row": {"device": "norm", "kind": "norm", "message": "norm", "first": "int", "last": "int", "count": "int>=1"},
 "output_order": "groups in order of first creation during the ordered scan",
 "declared_effects": [], "determinism": "pure; identical input -> identical output",
 "explicitly_unspecified": ["behaviour when two distinct groups could merge after a later event (no re-merge)",
                            "tie-break across equal timestamps beyond input order", "max input size / overflow"],
 "assurance": ["reference-conformance-suite-v1 (below)"], "license": "CC0-1.0 (illustrative)",
}

def _norm(e): 
    d = " ".join(e["device"].split()).lower(); k = " ".join(e["kind"].split()).lower(); m = " ".join(e["message"].split())
    return d, k, m

def impl_scan(events, window):   # variant 1: single ordered scan, dict of open groups
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0: raise ValueError("window")
    out, active = [], {}
    for e in sorted(events, key=lambda e: e["timestamp"]):
        key = _norm(e); g = active.get(key)
        if g is not None and e["timestamp"] - g["first"] < window:
            g["last"] = e["timestamp"]; g["count"] += 1
        else:
            g = dict(zip(("device","kind","message"), key)) | {"first": e["timestamp"], "last": e["timestamp"], "count": 1}
            active[key] = g; out.append(g)
    return out

def impl_bucketed(events, window):   # variant 2: group by key first, then split each key's timeline
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0: raise ValueError("window")
    by_key = OrderedDict()
    for idx, e in enumerate(events): by_key.setdefault(_norm(e), []).append((e["timestamp"], idx))
    tmp = []
    for key, items in by_key.items():
        items.sort()  # by timestamp then original index
        cur = None
        for ts, idx in items:
            if cur is not None and ts - cur["first"] < window:
                cur["last"] = ts; cur["count"] += 1
            else:
                cur = dict(zip(("device","kind","message"), key)) | {"first": ts, "last": ts, "count": 1, "_o": idx}
                tmp.append(cur)
    tmp.sort(key=lambda g: g["_o"])   # first-creation order == order of each group's first event in a stable sort
    return [{k: v for k, v in g.items() if k != "_o"} for g in tmp]

def conformance(impl):
    cases = [
        ([], 60, []),
        ([{"device":"A ","kind":" K","message":"m  m","timestamp":5,"severity":"info"}], 60,
         [{"device":"a","kind":"k","message":"m m","first":5,"last":5,"count":1}]),
        ([{"device":"d","kind":"k","message":"m","timestamp":0},{"device":"d","kind":"k","message":"m","timestamp":60}], 60,
         [{"device":"d","kind":"k","message":"m","first":0,"last":0,"count":1},
          {"device":"d","kind":"k","message":"m","first":60,"last":60,"count":1}]),
        ([{"device":"d","kind":"k","message":"m","timestamp":0},{"device":"d","kind":"k","message":"m","timestamp":59}], 60,
         [{"device":"d","kind":"k","message":"m","first":0,"last":59,"count":2}]),
    ]
    for events, window, want in cases:
        got = impl(events, window)
        if got != want: return False, (events, window, want, got)
    try: impl([], 0); return False, "window=0 not rejected"
    except Exception: pass
    return True, None

if __name__ == "__main__":
    print(json.dumps(CONTRACT, indent=1))
    import random
    rng = random.Random(99); mismatches = 0
    for _ in range(5000):
        evs, t = [], 0
        for i in range(rng.randint(0,10)):
            t += rng.choice([0,1,30,59,60,61,120])
            evs.append({"device":rng.choice(["A ","a","A"]),"kind":rng.choice([" K","k"]),"message":rng.choice(["m  m","m m"]),"timestamp":t})
        rng.shuffle(evs); w = rng.choice([1,30,60,120])
        if impl_scan(evs,w) != impl_bucketed(evs,w): mismatches += 1
    c1, e1 = conformance(impl_scan); c2, e2 = conformance(impl_bucketed)
    print(f"\nconformance: impl_scan={c1}, impl_bucketed={c2}")
    print(f"two independent implementations agree on 5000 random inputs: {mismatches==0} (mismatches={mismatches})")
    print("what a third party needs to validate interoperability: the signature, the normalization rules,")
    print("the STRICT-from-first window rule, the output-order rule, and this conformance suite as shared tests.")
    print("NOT consensus: this is one model's contract; agreement requires comparing it to another model's independently authored one.")
