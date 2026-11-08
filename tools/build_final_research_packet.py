"""Build the final curated experiment packet without earlier article drafts.

Frozen research files are copied byte-for-byte. Current standalone guides take
precedence over historical reading navigation retained for hash verification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments/approved_workflow_theory"
PACKET = "AICC_Final_Experiments_Packet"
PROCESSING_RUNS = (
    "full-2026-11-05",
    "anthropic-claude-opus-5.5-2026-11-05-trackA-002",
    "grok-4.7-2026-11-05-trackA-001",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def tracked(prefix):
    return filter(None, subprocess.check_output(["git", "ls-files", "-z", prefix], cwd=ROOT).decode().split("\0"))


def payload_files():
    names = set(tracked("experiments/approved_workflow_theory"))
    names.update(tracked("experiments/native_learning_gate"))
    names.update(tracked("experiments/representation_comparison"))
    for name in tracked("experiments/ain_compiler_gate"):
        if "/results/" not in name or any("/results/" + run + "/" in name for run in (
                "rtx3080-2026-11-06-reference-v2", "rtx3080-2026-11-06-learning-v2")):
            names.add(name)
    for name in tracked("experiments/processing_study"):
        if "/results/" not in name or any("/results/" + run + "/" in name for run in PROCESSING_RUNS):
            if not name.endswith((".png", ".svg")):
                names.add(name)
    names.update(("experiments/ain_v0/ain/__init__.py", "experiments/ain_v0/ain/language.py"))
    return sorted(names)


def copy_file(relative, staging, target=None):
    source = ROOT / relative
    destination = staging / (target or relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_assets(staging, asset_directory=None):
    spec = json.loads((STUDY / "tokenizer-files.sha256.json").read_text())
    asset_directory = asset_directory or ROOT / "work/final-research-packet/tokenizer-assets"
    asset_directory.mkdir(parents=True, exist_ok=True)
    published = ROOT / "publication/downloads/AICC_Final_Experiments_Packet.zip"
    archive = zipfile.ZipFile(published) if published.is_file() else None
    try:
        for name, expected in spec["files"].items():
            cache = asset_directory / name
            if cache.is_file():
                content = cache.read_bytes()
            elif archive:
                member = next(p for p in archive.namelist() if p.endswith("/tokenizer-assets/" + name))
                content = archive.read(member)
            else:
                url = f"https://huggingface.co/{spec['repository']}/resolve/{spec['revision']}/{name}"
                with urlopen(url, timeout=45) as response:
                    content = response.read(20 * 1024 * 1024)
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError("Tokenizer bytes differ: " + name)
            if not cache.exists():
                cache.write_bytes(content)
            target = staging / "tokenizer-assets" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    finally:
        if archive:
            archive.close()
    write_json(staging / "tokenizer-assets/SOURCE.json", {
        "repository": spec["repository"], "revision": spec["revision"],
        "sha256": spec["files"], "license_file": "LICENSE", "model_weights_included": False})
    return len(spec["files"])


def verify_frozen():
    manifest = json.loads((STUDY / "PACKAGE_MANIFEST.json").read_text())
    for name, expected in manifest["sha256"].items():
        if digest(STUDY / name) != expected:
            raise ValueError("Frozen package bytes differ: " + name)
    for folder in ("native_learning_gate/results/rtx3080-2026-11-06",
                   "ain_compiler_gate/results/rtx3080-2026-11-06-learning-v2",
                   "ain_compiler_gate/results/rtx3080-2026-11-06-reference-v2"):
        path = ROOT / "experiments" / folder
        name = "reference-manifest.json" if "reference-v2" in folder else "manifest.json"
        record = json.loads((path / name).read_text())
        for source, expected in record["source_sha256"].items():
            if digest(ROOT / source.replace("\\", "/")) != expected:
                raise ValueError("Frozen local study source differs: " + source)
    return len(manifest["sha256"])


def build(args):
    frozen_count = verify_frozen()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    staging = ROOT / "work/final-research-packet" / ("stage-" + stamp) / PACKET
    staging.mkdir(parents=True)
    for name in payload_files():
        copy_file(name, staging)
    assets_count = copy_assets(staging, args.asset_directory)
    for source in sorted((ROOT / "publication/reproduction").rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
            relative = source.relative_to(ROOT).as_posix()
            if "/validation/" not in relative:
                copy_file(relative, staging)
    for source in sorted((ROOT / "publication/reproduction/scripts").glob("*.py")):
        copy_file(source.relative_to(ROOT).as_posix(), staging, "scripts/" + source.name)
    copy_file("publication/AIN_THEORY.md", staging)
    for name in ("EVIDENCE.md", "RESEARCH_PLAN.md", "RELATED_WORK.md"):
        if (ROOT / "publication" / name).is_file():
            copy_file("publication/" + name, staging)
    for source in sorted((ROOT / "publication/examples").rglob("*")):
        if source.is_file() and "__pycache__" not in source.parts and source.suffix != ".pyc":
            copy_file(source.relative_to(ROOT).as_posix(), staging)
    figures = ROOT / "publication/figures"
    if figures.is_dir():
        for source in sorted(figures.rglob("*")):
            if source.is_file():
                copy_file(source.relative_to(ROOT).as_posix(), staging)
        copy_file("tools/build_final_figures.py", staging)
    (staging / "START_HERE.md").write_text(
        "# Final experiment packet\n\nRead [the current standalone guide](publication/reproduction/START_HERE.md)\n"
        "and select an independent reconstruction or exact replay route before\n"
        "opening outcomes. Run its commands from this extracted root.\n\n"
        "All final research files and asset hashes are in PACKET_MANIFEST.json.\n"
        "Earlier article drafts are not required or included.\n", encoding="utf-8")
    write_json(staging / "SUBMISSION_TEMPLATE.json", {
        "status": "PENDING", "agent": {"provider": None, "model_identity_as_reported": None,
        "identity_evidence": None}, "date_utc": None, "route": None,
        "prior_exposure_to_expected_results": None, "files_read_before_first_seal": [],
        "environment": {}, "source_and_input_sha256": {}, "first_output_sha256": {},
        "first_seal": None, "all_attempts_and_deviations": [], "comparison": {},
        "authoring_provider_usage": None, "experiment_model_inference_calls": None,
        "assumption_assessment": None, "returned_files": []})
    manifest = {
        "packet_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "repository": "https://github.com/izikon78/AICC",
        "packaging_worktree_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "frozen_approved_core_files_verified": frozen_count, "tokenizer_assets_verified": assets_count,
        "final_processing_records": list(PROCESSING_RUNS), "model_weights_included": False,
        "saved_adapters_included": False, "earlier_article_drafts_included": False,
        "independent_route": "publication/reproduction/INDEPENDENT_RECONSTRUCTION.md",
        "legacy_navigation": "Unchanged frozen study guides remain for hash integrity; current standalone guides supersede their earlier reading navigation.",
        "sha256": {p.relative_to(staging).as_posix(): digest(p) for p in sorted(staging.rglob("*")) if p.is_file()}}
    write_json(staging / "PACKET_MANIFEST.json", manifest)
    result = subprocess.run([sys.executable, str(staging / "scripts/verify_packet.py")], cwd=staging,
                            capture_output=True, text=True, check=True)
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise FileExistsError("Use a fresh output or --overwrite")
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                key = PurePosixPath(staging.name, path.relative_to(staging).as_posix())
                if key.is_absolute() or ".." in key.parts:
                    raise ValueError("Unsafe ZIP path")
                archive.write(path, key.as_posix())
    summary = {"file": output.name, "sha256": digest(output), "bytes": output.stat().st_size,
               "payload_files_verified": json.loads(result.stdout)["files_checked"],
               "frozen_approved_core_files_verified": frozen_count, "tokenizer_assets_verified": assets_count,
               "packaging_source_commit": manifest["packaging_worktree_head"]}
    write_json(output.with_suffix(".manifest.json"), summary)
    print(json.dumps(dict(summary, staging=str(staging)), indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "publication/downloads/AICC_Final_Experiments_Packet.zip")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--asset-directory", type=Path,
                        help="Directory containing the six pinned tokenizer assets; otherwise reuse the final ZIP/cache or download verified public assets")
    build(parser.parse_args())
