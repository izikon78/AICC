"""Build a portable approved-core replication ZIP without model weights or credentials.

The original experiment files are copied byte-for-byte. Top-level instructions
separate independent reconstruction from post-seal reference/article review.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments/approved_workflow_theory"
FROZEN_BASE = "e9a8a5111717a57427fac50605cf5cbe0c86b316"
PACKET_NAME = "AICC_Approved_Core_Agent_Packet"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path, value):
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


START_HERE = """# Start here for the approved-core replication

Research direction and concept: Izik Bachar. This packet is for Grok or another
AI agent to reproduce the latest approved-core workflow accounting experiment.
It is a CPU experiment. It does not train a model or require a GPU/model download.
No model weights, account credentials or API tokens are included.

## Choose the route before opening result-bearing files

### Route A Independent reconstruction

1. Record your agent/provider/model identity, environment and every file you read.
   If you have already seen reference totals or the new article, disclose that.
   A known-answer replay is useful but must not be called a blinded reconstruction.
2. Read GROK_ASSIGNMENT.md, then
   experiments/approved_workflow_theory/AGENT_START_HERE.md. Follow its required
   theory reading, including only pages 1-4 of the bundled Draft 8 PDF. Continue
   with REPLICATION_SPEC.md, AIN_LANGUAGE_AND_THEORY.md, trace-inputs.json,
   requirements-reproduce.txt and tokenizer-files.sha256.json. Consult only the
   expressly permitted workload interface before implementing your own counter.
3. Do not open accounting.py, run.py, report.py, reproduce.py, study README.md,
   ARTICLE_REPRODUCTION_BRIEF.md, results/, validation/ or review-after-seal/
   until your first implementation and complete ledgers are preserved and sealed.
   These files are retained at original paths so frozen package checks still work;
   their presence is not an instruction to read them early.
4. Write an independent counter/renderer, replay the supplied semantic actions,
   preserve your first totals.json and episodes.json with every per-request row,
   and record code/input/tokenizer/output hashes before comparing. Do not repair
   a mismatch by tuning to the expected numbers. Preserve the first attempt.
5. After sealing, run the frozen comparator, explain any earliest discrepancy,
   then use Route B for an exact reference-code environment check. Review the
   article and earlier agents only afterwards.

### Route B Exact reference rerun or known-answer verification

Read the study and its expected results openly, then use the setup commands below.
This checks frozen code and output compatibility. It is not independent authoring
or model learning. Keep failures and any deviations in separate output folders.

## Setup and bundled tokenizer

Python 3.12 is required for the reference environment. From this packet's root:

    python scripts/verify_packet.py
    python scripts/setup.py
    python scripts/run_reference.py --output work/grok-exact-001

On Windows, `py -3.12` may be used instead of `python` for the first two commands.
The setup helper creates .venv, installs the exact pinned Python requirements and
copies the bundled, hash-verified tokenizer assets into a private local cache.
The reference wrapper then runs with --offline. Internet is normally needed to
install the Python dependencies; this packet is not a complete offline Python
environment. No Hugging Face download is needed for the six bundled assets.

For an existing prepared environment, use:

    python scripts/setup.py --skip-install
    python scripts/prepare_cache.py

Record a deviation if your packages differ from the pins. Do not describe such
a run as the full exact pinned environment. Never substitute tokenizer bytes.

## What to return

Return your report, filled GROK_SUBMISSION_TEMPLATE.json, independent source,
first untouched ledgers and seal, comparison output, exact-rerun logs, environment
versions and all deviations. Zip your fresh work/ outputs; do not include .venv,
cache copies, credentials or model weights. Send the files back to the project
owner. No result is assumed in advance; pending Grok fields are ?? or null.

## Interpretation boundary

Python text-token counts are observed with the pinned tokenizer. Ideal code units
are modeled under learned-vocabulary, approved-core, correct-composition and
equal-cost-per-position premises. Ideal AIN, ideal IR and ideal Python receive
equal encoding opportunities. The test does not measure real model inference,
training, agent planning success, GPU time, power or monetary savings.

The packet snapshot and all payload hashes are in PACKET_MANIFEST.json. Its
source study is based on commit e9a8a5111717a57427fac50605cf5cbe0c86b316.
The new article and any display-code companion are under review-after-seal/;
they do not change the frozen measurement or its inputs.
"""


GROK_ASSIGNMENT = """# Grok replication assignment

Perform the approved-core workflow theory replication in START_HERE.md Route A.
The original frozen experiment is experiments/approved_workflow_theory/.
Do not infer a target result from the theory. Reconstruct the documented counts
and Python rendering from the semantic inputs and pinned tokenizer, preserve
your first attempt, and only then compare. Use equal accounting opportunities
for AIN, readable IR and Python; do not add privileged operations to one form.

## Required evidence

- Provider, model/version as reported, date, operating system, Python and package
  versions; say whether identity is self-reported or externally recorded.
- Exact read order and any exposure to published results before sealing.
- SHA-256 hashes of the specification, trace inputs, workload source, tokenizer,
  independent implementation, first ledgers and first totals.
- Every semantic stage episode and every profile/request ledger row, in the
  frozen order. Include all inputs, outputs, memory and history recurrence.
- Execution and action/memory replay checks against the permitted oracle.
- Your original code and outputs even if wrong; corrections in a separate folder.
- Comparator exit code, first differing field if any, exact reference wrapper
  outcome, complete logs and any environmental or acquisition deviations.
- Actual provider usage when available. Missing authoring or experimental model
  telemetry stays unknown, not zero. Separate authoring-agent usage from the
  experiment's model_calls field.
- A critical assessment of the premises. Extensions must be separately versioned
  and must retain the frozen result rather than overwrite it.

## Important distinctions

The supplied traces already give correct actions. Replaying them tests accounting
and executable approved composition, not a model discovering a plan. Functions
and loops execute inside shared approved code. Resident and inspect schedules
reuse the same task families with different model-context exposure. They are not
independent populations or financial invoices.

If you have already read the article or totals, complete Route B and/or clearly
label your reconstruction as prior-exposed. Do not claim blinded independence.
The new article is intentionally stored under review-after-seal/.

## Return package

Fill GROK_SUBMISSION_TEMPLATE.json. Return a ZIP with your report, code, first
unmodified observations/seal, comparison, rerun logs and extension evidence.
Do not return .venv, cached duplicate assets, credentials or model weights.
The project owner will supply the result to the coordinating agent; you do not
need to publish or send messages to anyone else.
"""


VERIFY_SCRIPT = '''"""Verify payload bytes and safe relative paths before using the packet."""
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
'''


CACHE_SCRIPT = '''"""Seed a private Hugging Face cache from the six pinned bundled assets."""
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
'''


SETUP_SCRIPT = '''"""Create a private Python environment; package installation may need Internet."""
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
'''


REFERENCE_SCRIPT = '''"""Run the frozen exact reference wrapper with locally bundled tokenizer assets."""
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
'''


def submission_template():
    return {
        "status": "PENDING", "agent": {"name": "Grok", "provider": "??", "model_identity": "??", "identity_evidence": "??"},
        "date_utc": "??", "mode": "??", "prior_exposure_to_expected_results": None,
        "files_read_before_first_seal": [], "environment": {"os": "??", "python": "??", "packages": {}},
        "input_and_source_sha256": {}, "tokenizer": {"repository": "Qwen/Qwen2.5-1.5B", "revision": "8faed761d45a263340a0528343f099c05c9a4323", "asset_sha256": {}},
        "independent_counter_sha256": "??", "first_output_sha256": {}, "first_seal": "??",
        "episodes": None, "ledger_rows": None, "execution_checks": None,
        "schedules": {s: {"short_alias_python_input": None, "short_alias_python_output": None,
                          "ideal_input": None, "ideal_output": None, "total_reduction_percent": "??"}
                      for s in ("resident", "inspect")},
        "all_ideal_profiles_equal": None, "comparison_exit_code": None, "first_difference": None,
        "exact_reference_outcome": "??", "exact_reference_test_count": None,
        "all_attempts_and_deviations": [], "authoring_provider_usage": None,
        "experiment_model_inference_calls": None, "assumption_assessment": "??",
        "extensions_separately_versioned": [], "returned_files": []}


def verify_frozen_source():
    manifest = json.loads((STUDY / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    for name, expected in manifest["sha256"].items():
        if digest(STUDY / name) != expected:
            raise ValueError("Frozen source changed: " + name)
    return len(manifest["sha256"])


def acquire_assets(cache, allow_download=True):
    spec = json.loads((STUDY / "tokenizer-files.sha256.json").read_text(encoding="utf-8"))
    cache.mkdir(parents=True, exist_ok=True)
    # Windows system certificate trust; no TLS verification bypass.
    try:
        from pip._vendor import truststore
        truststore.inject_into_ssl()
    except ImportError:
        pass
    for name, expected in spec["files"].items():
        target = cache / name
        if not target.exists() and name == "tokenizer.json" and (ROOT / "work/tokenizer.json").is_file():
            shutil.copy2(ROOT / "work/tokenizer.json", target)
        if target.exists():
            if digest(target) != expected:
                raise ValueError("Cached asset hash differs: " + name)
            continue
        if not allow_download:
            raise FileNotFoundError("Missing bundled tokenizer asset: " + name)
        url = f"https://huggingface.co/{spec['repository']}/resolve/{spec['revision']}/{name}"
        with urlopen(url, timeout=45) as response:
            content = response.read(20 * 1024 * 1024)
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError("Downloaded asset hash differs: " + name)
        target.write_bytes(content)
    return spec


def safe_zip(source, destination):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                relative = PurePosixPath(source.name, path.relative_to(source).as_posix())
                if relative.is_absolute() or ".." in relative.parts:
                    raise ValueError("Unsafe ZIP path")
                archive.write(path, relative.as_posix())


def copy_background_document(source, destination):
    """Make optional background navigation portable; frozen study files are untouched."""
    content = source.read_text(encoding="utf-8")
    def link(match):
        prefix, target = match.groups()
        if "://" in target or target.startswith("#") or target.startswith("mailto:"):
            return match.group(0)
        location, separator, anchor = target.partition("#")
        resolved = (source.parent / location).resolve()
        if not resolved.is_relative_to(ROOT):
            raise ValueError("Background link escapes repository")
        relative = resolved.relative_to(ROOT).as_posix()
        base = "https://raw.githubusercontent.com/izikon78/AICC/" if prefix.startswith("!") else "https://github.com/izikon78/AICC/blob/"
        url = base + FROZEN_BASE + "/" + relative + ("#" + anchor if separator else "")
        return prefix + "(" + url + ")"
    write(destination, re.sub(r"(!?\[[^\]]*\])\(([^)]+)\)", link, content))


def build(args):
    checked = verify_frozen_source()
    cache = ROOT / "work/agent-packet/tokenizer-assets"
    spec = acquire_assets(cache, allow_download=not args.no_download)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    staging = ROOT / "work/agent-packet" / ("stage-" + stamp) / PACKET_NAME
    staging.mkdir(parents=True)
    files = subprocess.check_output(["git", "ls-files", "-z", "experiments/approved_workflow_theory"], cwd=ROOT).decode().split("\0")
    for name in filter(None, files):
        source = ROOT / name
        if source.is_file():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for name in spec["files"]:
        target = staging / "tokenizer-assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cache / name, target)
    write_json(staging / "tokenizer-assets/SOURCE.json", {"repository": spec["repository"], "revision": spec["revision"], "sha256": spec["files"], "license_file": "LICENSE", "model_weights_included": False})
    write(staging / "START_HERE.md", START_HERE)
    write(staging / "GROK_ASSIGNMENT.md", GROK_ASSIGNMENT)
    write_json(staging / "GROK_SUBMISSION_TEMPLATE.json", submission_template())
    write(staging / "scripts/verify_packet.py", VERIFY_SCRIPT)
    write(staging / "scripts/prepare_cache.py", CACHE_SCRIPT)
    write(staging / "scripts/setup.py", SETUP_SCRIPT)
    write(staging / "scripts/run_reference.py", REFERENCE_SCRIPT)
    write(staging / "SETUP.ps1", 'param([string]$Python="python")\n& $Python (Join-Path $PSScriptRoot "scripts/setup.py")\nexit $LASTEXITCODE\n')
    write(staging / "setup.sh", '#!/usr/bin/env sh\nset -eu\ncd "$(dirname "$0")"\n"${PYTHON:-python3}" scripts/setup.py\n')
    theory_pdf = ROOT / "docs/article/AICC_Article_Draft_8_Review.pdf"
    theory_md = ROOT / "docs/article/AICC_Article_Draft_8.md"
    for source in (theory_pdf,):
        target = staging / "docs/article" / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    copy_background_document(theory_md, staging / "docs/article" / theory_md.name)
    for relative in ("docs/ain/NATIVE_HYPOTHESES.md", "docs/ain/COMPLEX_TASK.md"):
        source = ROOT / relative
        copy_background_document(source, staging / relative)
    # Theory guide links the old grammar only as background, not this measurement.
    for name in ("LANGUAGE.md",):
        source = ROOT / "experiments/ain_v0" / name
        if source.is_file():
            target = staging / "experiments/ain_v0" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_background_document(source, target)
    for source in (args.article_pdf, args.article_docx, args.article_source):
        if source:
            source = source.resolve()
            if not source.is_file():
                raise FileNotFoundError("Requested article artifact is missing: " + str(source))
            target = staging / "review-after-seal/article" / source.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    examples = ROOT / "docs/article/examples/draft10"
    if examples.is_dir():
        shutil.copytree(examples, staging / "review-after-seal/article/examples/draft10", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    figures = ROOT / "docs/article/figures/draft10"
    if figures.is_dir():
        shutil.copytree(figures, staging / "review-after-seal/article/figures/draft10", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    write(staging / "review-after-seal/README.md", "# Open only after the independent first seal\n\nThe article contains expected aggregates. Prior exposure must be disclosed.\nEarlier agents and the reference result are also retained at their original\npaths under experiments/approved_workflow_theory/results and validation so the\nfrozen package manifest and exact wrapper remain usable.\n")
    provenance = {"packet_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
                  "frozen_study_base_commit": FROZEN_BASE,
                  "packaging_worktree_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "repository": "https://github.com/izikon78/AICC", "frozen_package_files_verified": checked,
                  "tokenizer_assets_verified": len(spec["files"]), "model_weights_included": False,
                  "grok_status": "PENDING", "new_article_included": bool(args.article_pdf or args.article_docx),
                  "independence_note": "Result files are retained at original paths but must not be read before the first seal in Route A.",
                  "sha256": {p.relative_to(staging).as_posix(): digest(p) for p in sorted(staging.rglob("*")) if p.is_file()}}
    write_json(staging / "PACKET_MANIFEST.json", provenance)
    result = subprocess.run([sys.executable, str(staging / "scripts/verify_packet.py")], cwd=staging, capture_output=True, text=True, check=True)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise FileExistsError("Choose a fresh --output or explicitly use --overwrite")
    safe_zip(staging, output)
    summary = {"zip": str(output), "zip_sha256": digest(output), "bytes": output.stat().st_size,
               "staging": str(staging), "verification": json.loads(result.stdout),
               "frozen_files_verified": checked, "tokenizer_assets_verified": len(spec["files"])}
    write_json(output.with_suffix(".manifest.json"), summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--article-pdf", type=Path)
    parser.add_argument("--article-docx", type=Path)
    parser.add_argument("--article-source", type=Path)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    build(parser.parse_args())
