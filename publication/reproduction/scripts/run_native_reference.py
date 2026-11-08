"""Run the optional compact/native reference route with the bundled tokenizer."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--current-python", action="store_true")
args = parser.parse_args()
python = Path(sys.executable) if args.current_python else ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.is_file():
    raise SystemExit("Run setup or explicitly select --current-python in a prepared environment")
if args.output.exists() and any(args.output.iterdir()):
    raise SystemExit("Use a fresh empty output folder")
for script in ("verify_packet.py", "prepare_cache.py"):
    subprocess.run([str(python), str(ROOT / "scripts" / script)], check=True, cwd=ROOT)
env = dict(os.environ, HF_HOME=str(ROOT / "work/huggingface-cache"), HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1")
subprocess.run([str(python), str(ROOT / "experiments/ain_compiler_gate/measure.py"), "--output", str(args.output)], check=True, cwd=ROOT, env=env)
