"""Black-box probes of pub.group_by_window@1 (no source). Each probe answers one question the shared contract leaves open.
The number of probes needed is itself a measure of contract insufficiency for a third-party implementer."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from benchmark.host.registry import Runtime
G = Runtime().bind("pub.group_by_window@1")
def e(d="pump-1", k="pressure", m="high pressure", t=0, **x): r = {"device": d, "kind": k, "message": m, "timestamp": t}; r.update(x); return r
def show(q, fn):
    try: out = fn(); print(f"Q: {q}\n   -> {json.dumps(out, ensure_ascii=False)}")
    except Exception as ex: print(f"Q: {q}\n   -> raises {type(ex).__name__}: {ex}")
probes = [
 ("device normalisation includes NFKC? ('\ufb01x' vs 'fix')", lambda: len(G([e(d="\ufb01x"), e(d="fix", t=1)], 60))),
 ("device normalisation casefolds? ('STRASSE' vs 'stra\u00dfe')", lambda: len(G([e(d="STRASSE"), e(d="stra\u00dfe", t=1)], 60))),
 ("device internal whitespace collapsed? ('pump  1' vs 'pump 1')", lambda: len(G([e(d="pump  1"), e(d="pump 1", t=1)], 60))),
 ("message keeps case? ('High' vs 'high')", lambda: len(G([e(m="High pressure"), e(m="high pressure", t=1)], 60))),
 ("message edges trimmed? (' high pressure ' vs 'high pressure')", lambda: len(G([e(m=" high pressure "), e(m="high pressure", t=1)], 60))),
 ("window boundary: t=0 and t=60 with window 60", lambda: len(G([e(t=0), e(t=60)], 60))),
 ("window measured from FIRST, not last (0, 40, 80; window 60)", lambda: [g["count"] for g in G([e(t=0), e(t=40), e(t=80)], 60)]),
 ("output values for a group (normalised fields?)", lambda: G([e(d=" Pump-1 ", k="PRESSURE", m="high   pressure", t=5)], 60)),
 ("output order: two keys, later key first in input", lambda: [g["device"] for g in G([e(d="b", t=5), e(d="a", t=1)], 60)]),
 ("output order on equal first timestamps (b before a in input)", lambda: [g["device"] for g in G([e(d="b", t=1), e(d="a", t=1)], 60)]),
 ("stable sort: equal timestamps keep input order in a group?", lambda: G([e(t=1, m="x"), e(t=1, m="x")], 60)),
 ("float timestamps accepted?", lambda: G([e(t=0.5), e(t=1.5)], 60)),
 ("bool timestamp?", lambda: G([e(t=True)], 60)),
 ("missing device field", lambda: G([{"kind": "k", "message": "m", "timestamp": 0}], 60)),
 ("window = 0", lambda: G([e()], 0)),
 ("window = 1.5 (non-integer)", lambda: G([e(t=0), e(t=1)], 1.5)),
 ("extra fields (severity, event_id) kept in output?", lambda: G([e(severity="critical", event_id="e1")], 60)),
 ("empty event list", lambda: G([], 60)),
]
for q, fn in probes: show(q, fn)
print(f"\nprobes needed: {len(probes)}")
