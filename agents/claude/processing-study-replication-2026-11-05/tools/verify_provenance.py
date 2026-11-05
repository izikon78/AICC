"""Provenance check for the AICC processing-study replication (Claude). Read-only: never rewrites any study file.
1. Eleven measured Python sources vs run-config.json.source_sha256_before_run and run-metadata.json.source_sha256.
2. The 21 original result assets vs results/full-2026-11-05/checksums.json."""
import hashlib, json, os, sys, glob
STUDY = sys.argv[1]; ORIG = os.path.join(STUDY, "results", "full-2026-11-05")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
cfg = json.load(open(os.path.join(ORIG, "run-config.json"))); meta = json.load(open(os.path.join(ORIG, "run-metadata.json")))
before = cfg["source_sha256_before_run"]; recorded = meta["source_sha256"]
print(f"run-config source entries: {len(before)} | run-metadata source entries: {len(recorded) if isinstance(recorded, dict) else type(recorded).__name__}")
current = {os.path.relpath(p, STUDY).replace(os.sep, "/"): sha(p) for p in glob.glob(os.path.join(STUDY, "**", "*.py"), recursive=True)}
ok = True
for rel, h in sorted(before.items()):
    cur = current.get(rel); rec = recorded.get(rel) if isinstance(recorded, dict) else None
    status = "OK" if cur == h and rec == h else "MISMATCH"; ok &= status == "OK"
    print(f"  {status:8s} {rel:42s} frozen {h[:12]}  current {str(cur)[:12]}  run-metadata {str(rec)[:12]}")
extra = sorted(set(current) - set(before))
print("python files in study dir not in the frozen manifest:", extra or "none")
cs = json.load(open(os.path.join(ORIG, "checksums.json")))
items = cs.items() if isinstance(cs, dict) and all(isinstance(v, str) for v in cs.values()) else (cs.get("files") or cs.get("sha256") or cs).items()
n = good = 0
for name, h in items:
    p = os.path.join(ORIG, name); n += 1
    if os.path.exists(p) and sha(p) == h: good += 1
    else: print("  ASSET MISMATCH:", name)
print(f"original result assets matching checksums.json: {good}/{n}")
print("SOURCE_HASHES_MATCH_FROZEN:", ok and not extra)
