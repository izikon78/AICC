"""Contract-insufficiency probes: for each capability, compare the bound reference with an alternative implementation that
also satisfies the SHARED contract text (another Python setting or Node.js). Differences mean equivalence across
variants is UNKNOWN from the contract alone. All calls go through the host; no sealed source is read."""
import gzip, json, struct, subprocess, sys, unicodedata, zlib
from benchmark.host.registry import Runtime
rt = Runtime(); B = lambda n: rt.bind(f"pub.{n}@1")
def node(js): return subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout.strip()
rows = []
def row(cap, question, ref, alt, verdict, note=""):
    rows.append((cap, question, verdict)); print(f"[{verdict}] {cap}: {question}\n    reference: {ref}\n    alternative: {alt}" + (f"\n    note: {note}" if note else ""))
# 1 gzip bytes
data = b"hello world " * 100
ref = B("gzip_deterministic")(data)
alts = {"gzip.compress level 6, mtime 0": gzip.compress(data, compresslevel=6, mtime=0),
        "zlib wbits=31 (gzip container)": (lambda c: c.compress(data) + c.flush())(zlib.compressobj(9, zlib.DEFLATED, 31)),
        "Node zlib.gzipSync": bytes.fromhex(node(f"process.stdout.write(require('zlib').gzipSync(Buffer.from('{data.decode()}')).toString('hex'))"))}
for k, v in alts.items():
    row("gzip_deterministic", f"byte-identical to '{k}'?", f"{len(ref)} bytes, XFL={ref[8]} OS={ref[9]}, sha {__import__('hashlib').sha256(ref).hexdigest()[:12]}",
        f"{len(v)} bytes, XFL={v[8]} OS={v[9]}, decompresses equal: {gzip.decompress(v) == data}",
        "ENTAILED" if v == ref else "UNKNOWN", "contract fixes mtime only; level, XFL/OS header bytes and deflate encoder are unspecified")
# 2 canonical_json numbers vs JSON.stringify (ECMAScript / RFC 8785-style number output)
vals = {"1e16": 1e16, "1e21": 1e21, "-0.0": -0.0, "0.1+0.2": 0.1 + 0.2, "2**53+1": 2**53 + 1, "1.0": 1.0}
for label, v in vals.items():
    ref = B("canonical_json")({"x": v}); js = node(f"process.stdout.write(JSON.stringify({{x: {repr(v) if not isinstance(v, int) else str(v)}}}))")
    row("canonical_json", f"number {label} formatted identically in JS?", ref, js, "ENTAILED" if ref == js else "UNKNOWN",
        "digest_json differs whenever this differs" if ref != js else "")
# 3 lone surrogate
for cap in ("canonical_json", "digest_json"):
    try: r = repr(B(cap)("\ud800"))
    except Exception as e: r = f"raises {type(e).__name__}"
    row(cap, "lone surrogate '\\ud800'", r, node("process.stdout.write(JSON.stringify('\\ud800'))"), "UNKNOWN", "contract silent; JS escapes, Python behaviour shown")
# 4 make_query vs WHATWG URLSearchParams
params = {"q": "a b~*'", "flag": True, "tags": ["x", "y z"]}
ref = B("make_query")(params)
js = node("const p=new URLSearchParams([['flag','true'],['q',\"a b~*'\"],['tags','x'],['tags','y z']]);process.stdout.write(p.toString())")
row("make_query", "same encoding as URLSearchParams (another 'standard urlencode')?", ref, js, "ENTAILED" if ref == js else "UNKNOWN",
    "'standard urlencode' means Python urllib here; ~ * ' are encoded differently by WHATWG serialisers")
# 5 toposort lexicographic order: code points vs UTF-16 code units
g = {"\uffff": [], "\U0001F600": []}
ref = B("toposort")(g)
js = node("process.stdout.write(JSON.stringify(['\\uffff','\\ud83d\\ude00'].sort()))")
row("toposort", "'lexicographically smallest' identical in JS default ordering?", json.dumps(ref), js,
    "ENTAILED" if json.dumps(ref) == js else "UNKNOWN", "Python compares code points; JS compares UTF-16 code units")
# 6 png_dimensions: spec-invalid width and bad CRC
def ihdr(w, h, crc=b"\0\0\0\0"): return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h) + bytes([8, 2, 0, 0, 0]) + crc
for label, hdr in [("width 2^31 (PNG spec max is 2^31-1), CRC zeroed", ihdr(2**31, 1)), ("width 1, CRC zeroed", ihdr(1, 1))]:
    try: r = repr(B("png_dimensions")(hdr))
    except Exception as e: r = f"raises {type(e).__name__}: {e}"
    row("png_dimensions", label, r, "a spec-validating decoder (e.g. libpng) rejects both", "REFUTED" if not r.startswith("raises") else "ENTAILED",
        "contract only promises a positive width/height and explicitly skips CRC; callers treating it as validation are wrong")
# 7 environment dependence of Unicode normalisation
row("normalize_tag", "results identical on another runtime?", f"Python {sys.version.split()[0]} Unicode {unicodedata.unidata_version}",
    f"Node {node('process.stdout.write(process.version)')} ICU Unicode {node('process.stdout.write(process.versions.unicode)')}", "UNKNOWN",
    "NFKC and casefold tables differ by Unicode version; the shared contract names no version")
json.dump(rows, open("contract_insufficiency_results.json", "w"), indent=1)
print("\nsummary:", {v: sum(1 for r in rows if r[2] == v) for v in ("ENTAILED", "REFUTED", "UNKNOWN")})
