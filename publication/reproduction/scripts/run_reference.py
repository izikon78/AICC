"""Run the frozen exact reference wrapper with locally bundled tokenizer assets."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--current-python", action="store_true", help="Use current interpreter instead of packet .venv; record any package differences")
args = parser.parse_args()
python = Path(sys.executable) if args.current_python else ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.is_file(): raise SystemExit("Run scripts/setup.py first, or explicitly use --current-python with a prepared environment")
subprocess.run([str(python), str(ROOT / "scripts/verify_packet.py")], check=True, cwd=ROOT)
subprocess.run([str(python), str(ROOT / "scripts/prepare_cache.py")], check=True, cwd=ROOT)
env = dict(os.environ, HF_HOME=str(ROOT / "work/huggingface-cache"), HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", PYTHONDONTWRITEBYTECODE="1")
result = subprocess.run([str(python), str(ROOT / "experiments/approved_workflow_theory/reproduce.py"), "--offline", "--output", str(args.output)], cwd=ROOT, env=env)
raise SystemExit(result.returncode)
