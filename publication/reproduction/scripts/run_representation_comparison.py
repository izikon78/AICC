"""Run the local text comparison from an extracted final research packet."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", required=True)
parser.add_argument("--current-python", action="store_true")
args = parser.parse_args()
python = Path(sys.executable) if args.current_python else ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
if not python.is_file():
    raise SystemExit("Run scripts/setup.py first or select --current-python")
subprocess.run([str(python), str(ROOT / "scripts/prepare_cache.py")], cwd=ROOT, check=True)
env = os.environ.copy()
env.update(HF_HOME=str(ROOT / "work/huggingface-cache"), HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
subprocess.run([str(python), "-m", "unittest", "discover", "-s", "experiments/representation_comparison", "-p", "test_*.py", "-v"], cwd=ROOT, env=env, check=True)
subprocess.run([str(python), "experiments/representation_comparison/run.py", "--output", args.output], cwd=ROOT, env=env, check=True)
