"""Compile matched reference programs and count their model-facing tokens."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.ain_compiler_gate.compiler import compile_program
from experiments.ain_compiler_gate.data import ARMS, CASES, format_prompt, make_dataset
from experiments.native_learning_gate.data import format_prompt as legacy_prompt
from experiments.native_learning_gate.data import make_dataset as legacy_dataset

MODEL = "Qwen/Qwen2.5-1.5B"
REVISION = "8faed761d45a263340a0528343f099c05c9a4323"


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def expected_result(steps, value):
    for operation, constant in steps:
        value = value + constant if operation == "add" else value - constant
    return value


def report(summary, count):
    lines = [
        "# Compact source to native code reference test", "",
        "6 November 2026. Research direction by Izik Bachar. Implementation and local "
        "execution by Codex with collaboration agents.", "",
        f"All {count} reference programs per condition were compiled with the same LLVM "
        "backend and checked against independently computed integer results. "
        "The observations below measure reference serialization and compilation. "
        "Learned candidate correctness is recorded by the separate adaptation run.", "",
        "| Source | Mean full target tokens | Mean compact target tokens | Reduction | "
        "Compact prompt + target tokens | Native-correct programs | Compile seconds |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        item = summary[arm]
        lines.append(f"| {arm} | {item['legacy_target_tokens'] / count:.3f} | "
                     f"{item['compact_target_tokens'] / count:.3f} | "
                     f"{item['target_reduction_fraction']:.1%} | "
                     f"{item['compact_prompt_and_target_tokens'] / count:.3f} | "
                     f"{item['correct']}/{count} | {item['compile_seconds']:.3f} |")
    lines.extend([
        "", "The full form is the earlier complete Python function or IR/AIN envelope. "
        "Compact Python supplies an expression in x. Compact IR and AIN supply the same "
        "sequence of accumulator operations and explicit integer literals. The compiler "
        "supplies the input/return convention, types, registers and envelope in every "
        "condition. All source forms use the same optimization and native-code backend.", "",
        f"Assembly was identical across the three compact forms for "
        f"{summary['shared']['identical_assembly']}/{count} tasks. Each compiled program "
        f"was checked on {len(CASES)} inputs, including the declared input limits. "
        "Generated assembly files and their token lengths are saved as diagnostic artifacts. "
        "Assembly is emitted by LLVM through ordinary CPU computation and requires zero "
        "additional model generation tokens.", "",
        "The token reduction comes from the compact source contract. Changing only the "
        "compiler target leaves the model-facing source sequence to be counted in full. "
        "Compiler-generated assembly token counts describe its text size and carry no "
        "LLM inference charge in this pipeline.", "",
        "## Measurement boundary", "",
        f"The tokenizer is `{MODEL}` at revision `{REVISION}` with base vocabulary. "
        "Counts use `add_special_tokens=False`. Prompt and target totals include their "
        "actual concatenated text. Training/inference accounting belongs to the separate "
        "adaptation run. The full and compact target figures compare canonical reference "
        "programs with equivalent behavior.", "",
        "Compilation time includes strict parsing, shared IR construction, verification, "
        "optimization, assembly emission and JIT setup as measured by the compiler. "
        "The few-instruction functions are too small for a useful end-to-end runtime "
        "speed claim through Python/ctypes call timing.", "",
        "The semantic domain is integer input and literal magnitudes up to 1,000,000, "
        "with at most 16 operations. These bounds allow exact signed-64-bit native "
        "arithmetic for every admitted program. The earlier VM has broader integer "
        "semantics. All current reference tasks are affine arithmetic and some held-out "
        "compositions share net offsets. This screen provides limited generalization evidence.", "",
        "The dataset and source hashes, versions and target information are preserved in "
        "`reference-manifest.json`. Every compiled row retains its token counts, native "
        "outputs and assembly hash in `reference-records.json`. The sample files show the "
        "same task at each source/compiler boundary.", "",
        "Implementation follows the official "
        "[llvmlite native compilation example](https://llvmlite.readthedocs.io/en/v0.44.0/user-guide/binding/examples.html).", "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results/rtx3080-2026-11-06")
    arguments = parser.parse_args()
    output = arguments.output
    if (output / "reference-manifest.json").exists():
        raise RuntimeError("Choose a fresh output directory to preserve earlier measurements")
    output.mkdir(parents=True, exist_ok=True)
    from transformers import AutoTokenizer
    import llvmlite.binding as llvm

    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    rows = make_dataset()
    legacy = {row["id"]: row for row in legacy_dataset()}
    source_files = [Path(__file__), Path(__file__).with_name("compiler.py"),
                    Path(__file__).with_name("data.py"), ROOT / "experiments/native_learning_gate/data.py",
                    ROOT / "experiments/ain_v0/ain/language.py"]
    manifest = {"model": MODEL, "revision": REVISION, "cases": CASES,
                "target": llvm.get_default_triple(), "llvm_version": llvm.llvm_version_info,
                "packages": {name: importlib.metadata.version(name) for name in
                             ("llvmlite", "transformers", "tokenizers")},
                "dataset_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
                "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in source_files}}
    save(output / "reference-manifest.json", manifest)
    records = []
    summary = {arm: {"correct": 0, "compile_seconds": 0.0, "legacy_target_tokens": 0,
                     "compact_target_tokens": 0, "compact_prompt_and_target_tokens": 0,
                     "legacy_prompt_and_target_tokens": 0} for arm in ARMS}
    summary["shared"] = {"identical_assembly": 0}
    sample = next(row["id"] for row in rows if row["family"] == "sub_add")
    count_tokens = lambda text: len(tokenizer(text, add_special_tokens=False).input_ids)
    for row in rows:
        assembly_hashes = []
        for arm in ARMS:
            program = compile_program(arm, row["targets"][arm])
            actual = [program.run(value) for value in CASES]
            expected = [expected_result(row["steps"], value) for value in CASES]
            digest = hashlib.sha256(program.assembly.encode()).hexdigest()
            assembly_hashes.append(digest)
            record = {"id": row["id"], "split": row["split"], "arm": arm,
                      "correct": actual == expected, "outputs": actual,
                      "compile_seconds": program.compile_seconds, "assembly_sha256": digest,
                      "assembly_tokens": count_tokens(program.assembly),
                      "legacy_target_tokens": count_tokens(row["legacy_targets"][arm]),
                      "compact_target_tokens": count_tokens(row["targets"][arm]),
                      "compact_prompt_and_target_tokens": count_tokens(format_prompt(row, arm) + row["targets"][arm]),
                      "legacy_prompt_and_target_tokens": count_tokens(legacy_prompt(legacy[row["id"]], arm)
                                                                       + row["legacy_targets"][arm])}
            records.append(record)
            for key in summary[arm]:
                summary[arm][key] += record[key]
            if row["id"] == sample:
                for suffix, content in (("compact.txt", row["targets"][arm]),
                                        ("full.txt", row["legacy_targets"][arm]),
                                        ("ll", program.llvm_ir), ("s", program.assembly)):
                    (output / f"sample-{arm}.{suffix}").write_text(content + "\n", encoding="utf-8")
        summary["shared"]["identical_assembly"] += len(set(assembly_hashes)) == 1
    for arm in ARMS:
        summary[arm]["target_reduction_fraction"] = 1 - summary[arm]["compact_target_tokens"] / summary[arm]["legacy_target_tokens"]
    save(output / "reference-records.json", records)
    save(output / "reference-summary.json", summary)
    (output / "REPORT_REFERENCE.md").write_text(report(summary, len(rows)), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if any(summary[arm]["correct"] != len(rows) for arm in ARMS):
        raise RuntimeError("Compiled reference correctness failed")


if __name__ == "__main__":
    main()
