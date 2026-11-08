"""Create a private Python environment; package installation may need Internet."""
from pathlib import Path
import argparse
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--skip-install", action="store_true", help="Use the current preconfigured environment; disclose differing pins")
args = parser.parse_args()
if sys.version_info[:2] != (3, 12): raise SystemExit("Use Python 3.12 for exact reproduction")
subprocess.run([sys.executable, str(ROOT / "scripts/verify_packet.py")], check=True, cwd=ROOT)
if not args.skip_install:
    envdir = ROOT / ".venv"
    python = envdir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not envdir.exists(): subprocess.run([sys.executable, "-m", "venv", str(envdir)], check=True)
    if not python.is_file(): raise SystemExit("Existing .venv is incompatible; preserve it and choose a clean extraction")
    subprocess.run([str(python), "-m", "pip", "install", "-r", str(ROOT / "experiments/approved_workflow_theory/requirements-reproduce.txt")], check=True)
subprocess.run([sys.executable, str(ROOT / "scripts/prepare_cache.py")], check=True, cwd=ROOT)
print("Setup complete. Run scripts/run_reference.py only after the independent seal or in declared known-answer mode.")
