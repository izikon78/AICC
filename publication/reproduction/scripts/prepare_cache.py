"""Seed a private Hugging Face cache from the six pinned bundled assets."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
spec = json.loads((ROOT / "experiments/approved_workflow_theory/tokenizer-files.sha256.json").read_text(encoding="utf-8"))
cache = ROOT / "work/huggingface-cache"
snapshot = cache / "hub" / ("models--" + spec["repository"].replace("/", "--")) / "snapshots" / spec["revision"]
snapshot.mkdir(parents=True, exist_ok=True)
for name, expected in spec["files"].items():
    source = ROOT / "tokenizer-assets" / name
    if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
        raise ValueError("Bundled tokenizer hash differs: " + name)
    target = snapshot / name
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != expected:
        raise ValueError("Existing private cache file differs; preserve and inspect: " + str(target))
    if not target.exists(): shutil.copy2(source, target)
print(json.dumps({"assets_verified": len(spec["files"]), "HF_HOME": str(cache), "model_weights_downloaded": False}, indent=2))
