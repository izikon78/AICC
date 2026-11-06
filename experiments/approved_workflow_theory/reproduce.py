"""Reproduce the frozen CPU experiment or compare an independent ledger."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
REFERENCE = PACKAGE / "results/approved-core-2026-11-06"
sys.path.insert(0, str(ROOT))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode("utf-8")).hexdigest()


def first_difference(expected, actual, path="$ "):
    if type(expected) is not type(actual):
        return {"path": path.strip(), "expected": expected, "actual": actual}
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            return {"path": path.strip(), "expected_keys": sorted(expected), "actual_keys": sorted(actual)}
        for key in expected:
            difference = first_difference(expected[key], actual[key], f"{path.strip()}.{key}")
            if difference:
                return difference
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return {"path": path.strip(), "expected_length": len(expected), "actual_length": len(actual)}
        for index, (left, right) in enumerate(zip(expected, actual, strict=True)):
            difference = first_difference(left, right, f"{path.strip()}[{index}]")
            if difference:
                return difference
    elif expected != actual:
        return {"path": path.strip(), "expected": expected, "actual": actual}
    return None


def canonical_episodes(episodes):
    result = deepcopy(episodes)
    for episode in result:
        episode.pop("execution_seconds", None)
    return result


def independent_view(episodes):
    """Independent reimplementations supply keys and complete per-turn ledgers."""
    return [{key: episode[key] for key in ("chain", "domain", "stage", "schedule", "ledger")}
            for episode in episodes]


def compare(output, independent=False):
    filenames = ("totals.json", "episodes.json") if independent else (
        "fixtures.json", "approved_core_sources.json", "totals.json", "episodes.json", "summary.json")
    checks = {}
    for name in filenames:
        if not (output / name).is_file():
            checks[name] = {"match": False, "error": "missing output file"}
            continue
        expected = read_json(REFERENCE / name)
        actual = read_json(output / name)
        if name == "episodes.json":
            expected, actual = canonical_episodes(expected), canonical_episodes(actual)
            if independent:
                expected, actual = independent_view(expected), independent_view(actual)
        difference = first_difference(expected, actual)
        checks[name] = {"match": difference is None, "first_difference": difference,
                        "expected_canonical_sha256": canonical_hash(expected),
                        "actual_canonical_sha256": canonical_hash(actual)}
    if not independent:
        expected = read_json(REFERENCE / "manifest.json")
        actual = read_json(output / "manifest.json")
        for value in (expected, actual):
            value["source_sha256"] = {key.replace("\\", "/"): digest
                                      for key, digest in value["source_sha256"].items()}
        difference = first_difference(expected, actual)
        checks["manifest.json"] = {"match": difference is None, "first_difference": difference}
    result = {"mode": "independent accounting" if independent else "exact reproduction",
              "matches_reference": all(check["match"] for check in checks.values()),
              "reference": "results/approved-core-2026-11-06",
              "excluded_runtime_fields": ["episodes[*].execution_seconds"],
              "manifest_normalization": "Source path separators normalized to '/'",
              "checks": checks}
    write_json(output / "comparison.json", result)
    return result


def verify_frozen_sources():
    manifest = read_json(REFERENCE / "manifest.json")
    for relative, expected in manifest["source_sha256"].items():
        actual = hashlib.sha256((ROOT / relative.replace("\\", "/")).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen experiment source hash differs at {relative}")


def verify_package():
    manifest = read_json(PACKAGE / "PACKAGE_MANIFEST.json")
    for relative, expected in manifest["sha256"].items():
        path = (PACKAGE / relative).resolve()
        if not path.is_relative_to(PACKAGE) or not path.is_file():
            raise ValueError(f"Missing or invalid package file {relative}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Package file hash differs for {relative}")


def prepare_tokenizer(offline):
    from huggingface_hub import hf_hub_download

    expected = read_json(PACKAGE / "tokenizer-files.sha256.json")
    model, revision = expected["repository"], expected["revision"]
    files = {}
    for name, digest in expected["files"].items():
        path = Path(hf_hub_download(model, filename=name, revision=revision,
                                   local_files_only=offline))
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"Pinned tokenizer asset hash differs for {name}")
        files[name] = actual
    return {"repository": model, "revision": revision, "files": files}


def command(arguments, logfile):
    with logfile.open("w", encoding="utf-8") as stream:
        process = subprocess.run([sys.executable, *arguments], cwd=ROOT, stdout=stream,
                                 stderr=subprocess.STDOUT, timeout=180)
    if process.returncode:
        raise RuntimeError(f"Command failed with exit {process.returncode}. Read {logfile}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/approved-workflow-replication/local-run")
    parser.add_argument("--offline", action="store_true", help="Use already cached, hash-verified tokenizer assets")
    parser.add_argument("--prepare-tokenizer", action="store_true", help="Fetch and verify only tokenizer assets")
    parser.add_argument("--compare", type=Path, help="Compare independent totals.json and per-episode ledgers")
    args = parser.parse_args()
    verify_package()
    if args.prepare_tokenizer:
        print(json.dumps(prepare_tokenizer(args.offline), indent=2))
        return
    if args.compare:
        output = args.compare.resolve()
        if output == REFERENCE.resolve() or REFERENCE.resolve() in output.parents:
            raise ValueError("Independent output must be separate from the reference results")
        result = compare(output, independent=True)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["matches_reference"] else 1)
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("Choose a fresh empty output directory")
    output.mkdir(parents=True, exist_ok=True)
    logs = output / "logs"
    logs.mkdir()
    provenance = {"python": sys.version, "platform": platform.platform(),
                  "model_inference_calls": 0,
                  "packages": {name: importlib.metadata.version(name) for name in
                               ("transformers", "tokenizers", "huggingface-hub")}}
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    provenance["git_commit"] = git.stdout.strip() if git.returncode == 0 else None
    try:
        if sys.version_info[:2] != (3, 12):
            raise ValueError("Exact reference reproduction uses Python 3.12")
        verify_frozen_sources()
        provenance["tokenizer"] = prepare_tokenizer(args.offline)
        write_json(output / "reproduction-environment.json", provenance)
        command(["-m", "unittest", "discover", "-s", "experiments/approved_workflow_theory",
                 "-p", "test_*.py", "-v"], logs / "tests.log")
        command([str(PACKAGE / "run.py"), "--output", str(output)], logs / "run.log")
        command([str(PACKAGE / "report.py"), "--results", str(output)], logs / "report.log")
        result = compare(output)
        print(json.dumps(result, indent=2))
        print(f"Report saved at {output / 'REPORT.md'}")
        raise SystemExit(0 if result["matches_reference"] else 1)
    except Exception as error:
        write_json(output / "reproduction-failure.json", {"error": repr(error), "environment": provenance})
        raise


if __name__ == "__main__":
    main()
