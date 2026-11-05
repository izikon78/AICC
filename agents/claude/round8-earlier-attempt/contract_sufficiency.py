"""H1 core probe: does the PUBLIC CONTRACT (API_CONTRACTS.md) decide behaviour, or does correctness depend on the
hidden implementation? Calls go through the public baseline API (allowed). For four functions I pick inputs the
contract text does not clearly resolve and record ENTAILED / UNKNOWN with what a reuser would have to do."""
from benchmark.public import baseline_api as api
import platform, sys, json
rows = []
def rec(fn, question, verdict, observed, escalation):
    rows.append({"fn": fn, "question": question, "verdict": verdict, "observed": observed, "escalation": escalation})

# 1. parse_money rounding at the documented tie 1.005 (contract: ROUND_HALF_UP) -- ENTAILED
rec("parse_money", "tie 1.005 rounds up?", "ENTAILED", repr(api.parse_money("1.005")),
    "contract states ROUND_HALF_UP; near-miss uses HALF_EVEN -> 100")
# 2. gzip_deterministic byte-for-byte reproducibility across environments -- UNKNOWN per contract's own caveat
g = api.gzip_deterministic(b"hello world")
rec("gzip_deterministic", "are compressed bytes identical across gzip/runtime versions?", "UNKNOWN",
    f"{len(g)} bytes here, header[:4]={g[:4].hex()}, python={platform.python_version()}",
    "contract says 'gzip version and runtime may affect header metadata; only same-environment comparisons'. A reuser must pin the runtime or compare only a decompressed round-trip.")
# 3. png_dimensions on a truncated/!CRC file (contract: validates signature+IHDR only, NOT CRC) -- UNKNOWN for integrity
good = b'\x89PNG\r\n\x1a\n'+(13).to_bytes(4,'big')+b'IHDR'+(17).to_bytes(4,'big')+(3).to_bytes(4,'big')
corrupt = good + b'\x00\x00\x00\x00IDATxxxxCORRUPT'
rec("png_dimensions", "does it detect a corrupt IDAT / bad CRC?", "UNKNOWN (out of contract scope)",
    f"dims on header-only={api.png_dimensions(good)}; appended-garbage still returns={api.png_dimensions(corrupt)}",
    "contract explicitly does NOT validate CRC/decompression; a reuser needing integrity must add a full PNG validator.")
# 4. canonical_json with integer vs float that compare equal (1 vs 1.0) -- contract silent on number normalisation
try:
    a1, a2 = api.canonical_json(1), api.canonical_json(1.0)
    rec("canonical_json", "do 1 and 1.0 canonicalise the same?", "UNKNOWN" if a1 != a2 else "ENTAILED-ish",
        f"canonical_json(1)={a1!r}, canonical_json(1.0)={a2!r}",
        "contract does not state numeric normalisation; digests of 1 vs 1.0 differ, which a reuser might not expect.")
except Exception as e:
    rec("canonical_json", "1 vs 1.0", "ERROR", type(e).__name__, "n/a")
# 5. make_query boolean rendering order with list values (contract: booleans lowercase, list repeated) -- check interaction
rec("make_query", "bool + None + list interaction", "ENTAILED",
    api.make_query({'b':[1,2],'a':True,'z':None}),
    "contract specifies sorted keys, repeated list values, None omitted, booleans lowercase; all observable.")
# 6. group_by_window boundary: strictly-less-than window on FIRST timestamp (contract says 'strictly less than', first ts)
evs = [{'device':'d','kind':'k','message':'m','timestamp':0,'severity':'info'},
       {'device':'d','kind':'k','message':'m','timestamp':60,'severity':'info'}]
rec("group_by_window", "ts exactly == window from first: same group?", "ENTAILED",
    json.dumps(api.group_by_window(evs,60), default=str),
    "contract: open iff (ts - first) < window, strict; 60 with window 60 starts a new group. Observable and well-specified.")
print(json.dumps(rows, indent=1, default=str))
json.dump(rows, open("sufficiency_results.json","w"), indent=1, default=str)
unknowns = [r['fn'] for r in rows if r['verdict'].startswith('UNKNOWN')]
print("\nUNKNOWN (contract-insufficient for some real use):", unknowns)
