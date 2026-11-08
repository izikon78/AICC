"""Verify payload bytes and safe relative paths before using the packet."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "PACKET_MANIFEST.json").read_text(encoding="utf-8"))
bad = []
for name, expected in manifest["sha256"].items():
    key = PurePosixPath(name)
    candidate = (ROOT / Path(*key.parts)).resolve()
    if key.is_absolute() or ".." in key.parts or not candidate.is_relative_to(ROOT):
        bad.append({"path": name, "error": "unsafe path"}); continue
    if not candidate.is_file() or hashlib.sha256(candidate.read_bytes()).hexdigest() != expected:
        bad.append({"path": name, "error": "missing or changed bytes"})
print(json.dumps({"passed": not bad, "files_checked": len(manifest["sha256"]), "errors": bad}, indent=2))
raise SystemExit(0 if not bad else 1)
