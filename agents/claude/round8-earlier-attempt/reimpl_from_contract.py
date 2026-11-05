"""Contract-only reimplementations of 6 public capabilities, written ONLY from API_CONTRACTS.md (sealed never opened).
Deliberately literal where the contract is silent, to test whether the CONTRACT (not the hidden code) pins behaviour.
Differential-fuzzed against benchmark.public.baseline_api in reimpl_fuzz.py."""
import json as _json, re, unicodedata
from decimal import Decimal, ROUND_HALF_UP

def normalize_tag(text):
    if not isinstance(text, str): raise TypeError("str required")
    s = unicodedata.normalize("NFKC", text).casefold()
    s = " ".join(s.split())
    if not s: raise ValueError("empty")
    return s

def normalize_whitespace(text):
    if not isinstance(text, str): raise TypeError("str required")
    return " ".join(text.split())

def parse_money(text):
    if not isinstance(text, str) or isinstance(text, bool): raise TypeError("str required")
    t = text.strip()
    if not re.fullmatch(r"[+-]?\d+(\.\d+)?", t): raise ValueError("bad money")
    cents = (Decimal(t) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)

def canonical_json(data):
    return _json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)

def make_query(params):
    from urllib.parse import urlencode
    pairs = []
    for k in sorted(params):
        v = params[k]
        if v is None: continue
        if isinstance(v, bool): pairs.append((k, "true" if v else "false"))
        elif isinstance(v, list): pairs.extend((k, item) for item in v)
        else: pairs.append((k, v))
    return urlencode(pairs)

def group_by_window(events, window):
    def norm(e): return (normalize_whitespace(e["device"]).casefold() if False else " ".join(e["device"].split()).lower(),
                          " ".join(e["kind"].split()).lower(), " ".join(e["message"].split()))
    ordered = sorted(events, key=lambda e: e["timestamp"])
    groups, active = [], {}
    for e in ordered:
        key = norm(e)
        g = active.get(key)
        if g is not None and e["timestamp"] - g["first"] < window:
            g["last"] = e["timestamp"]; g["count"] += 1
        else:
            g = {"device": key[0], "kind": key[1], "message": key[2], "first": e["timestamp"], "last": e["timestamp"], "count": 1}
            active[key] = g; groups.append(g)
    return groups

def retry_delays(count, base_ms, cap_ms):
    for v in (count, base_ms, cap_ms):
        if not isinstance(v, int) or isinstance(v, bool): raise TypeError("int")
    if count < 0 or base_ms <= 0 or cap_ms <= 0: raise ValueError("range")
    return [min(base_ms * 2 ** i, cap_ms) for i in range(count)]

EXPORTS = ["normalize_tag","normalize_whitespace","parse_money","canonical_json","make_query","group_by_window","retry_delays"]
