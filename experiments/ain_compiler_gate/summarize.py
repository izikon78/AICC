"""Export the completed compact compiler experiment and its measured results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.ain_compiler_gate.compiler import compile_program
from experiments.ain_compiler_gate.data import judge

ARMS = ("python", "ir", "ain")


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def counts(records):
    correct = sum(row["correct"] for row in records)
    return {
        "assigned": len(records), "correct": correct,
        "attempted": sum("input_tokens" in row for row in records),
        "timeouts": sum(row.get("error") == "stage_time_limit" for row in records),
        "output_caps": sum(row.get("at_output_cap", False) for row in records),
        "input_tokens": sum(row.get("input_tokens", 0) for row in records),
        "output_tokens": sum(row.get("output_tokens", 0) for row in records),
        "generation_seconds": sum(row.get("inference_seconds", 0) for row in records),
        "compiler_seconds": sum(row.get("compiler_seconds", 0) for row in records),
        "judge_seconds": sum(row.get("judge_seconds", 0) for row in records),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "work/ain-compiler-gate-v2")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "results/rtx3080-2026-11-06-learning-v2")
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise ValueError("Source and export directories must differ")
    manifest = load(source / "manifest.json")
    dataset = load(source / "dataset.json")
    statuses = load(source / "statuses.json")
    if statuses != {arm: 0 for arm in ARMS}:
        raise ValueError("Every arm must finish before export")
    digest = hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest()
    if digest != manifest["dataset_sha256"]:
        raise ValueError("Frozen dataset hash mismatch")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative.replace("\\", "/")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Frozen source hash mismatch for {relative}")
    by_id = {row["id"]: row for row in dataset}
    records = {arm: {stage: load(source / f"{arm}-{stage}.json")
                     for stage in ("before", "after")} for arm in ARMS}
    results = {arm: load(source / f"{arm}-result.json") for arm in ARMS}
    for arm in ARMS:
        for stage in ("before", "after"):
            for record in records[arm][stage]:
                if "input_tokens" in record:
                    replay = judge(arm, record["output"], by_id[record["id"]])
                    for field in ("correct", "syntax_ok", "error", "assembly_sha256"):
                        if replay[field] != record[field]:
                            raise ValueError(f"Replay differs for {arm}/{stage}/{record['id']}")
    output.mkdir(parents=True, exist_ok=True)
    names = ["manifest.json", "dataset.json", "statuses.json"]
    for arm in ARMS:
        names.extend(f"{arm}-{suffix}.json" for suffix in ("before", "after", "training", "result"))
        names.append(f"{arm}.log")
    for name in names:
        shutil.copy2(source / name, output / name)
    for name in ("hardware.json", "cpu.json", "model_download_verification.json"):
        shutil.copy2(source.parent / name, output / name)
    aborted = source.parent / "ain-compiler-gate-v1"
    aborted_output = output / "aborted-v1"
    aborted_output.mkdir(exist_ok=True)
    for path in aborted.iterdir():
        if path.is_file() and path.suffix in (".json", ".log"):
            shutil.copy2(path, aborted_output / path.name)
    aborted_counts = counts(load(aborted / "python-before.json"))
    native = compile_program("ain", "2 7;3 4")
    (output / "example.ain").write_text("2 7;3 4\n", encoding="utf-8")
    (output / "example.ll").write_text(native.llvm_ir, encoding="utf-8")
    (output / "example.s").write_text(native.assembly, encoding="utf-8")
    summary = {arm: {stage: counts(records[arm][stage]) for stage in ("before", "after")}
               for arm in ARMS}
    summary["aborted_v1"] = aborted_counts
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Compact AIN to native code learning test", "",
        "6 November 2026. Research direction by Izik Bachar. Implementation, local execution "
        "and review by Codex with collaboration agents.", "",
        "The compact compiler pipeline executed successfully. After matched adaptation, "
        "Python and readable IR each solved 24/24 tasks, and numeric AIN solved 23/24. "
        "AIN and IR generated the same number of output tokens. The reference measurement "
        "shows that supplying predictable scaffolding through a compiler greatly reduces "
        "source length across the controls.", "",
        "| Adapted condition | Development | Held-out compositions | Generated tokens | "
        "Generation seconds | Compiler seconds |",
        "|---|---|---|---|---|---|",
    ]
    for arm in ARMS:
        item = summary[arm]["after"]
        result = results[arm]["after"]
        lines.append(f"| {arm} | {result['dev']['correct']}/12 | "
                     f"{result['holdout']['correct']}/12 | {item['output_tokens']} | "
                     f"{item['generation_seconds']:.3f} | {item['compiler_seconds']:.3f} |")
    lines.extend([
        "", "Every adapted task was attempted, with zero stage timeouts and zero output-cap "
        "hits. Generated-token totals include EOS. Canonical reference target counts exclude EOS.", "",
        "AIN's single error was `3 6;3 12` for a task requiring `3 6;2 12`. "
        "It parsed and compiled successfully, then subtracted twelve where addition was required.", "",
        "The [reference compiler report](../rtx3080-2026-11-06-reference-v2/REPORT_REFERENCE.md) "
        "records mean target lengths of 102.325 tokens for full AIN and 5.325 for compact AIN, "
        "a 94.8% reduction. Compact readable IR also averages 5.325 tokens, while compact Python "
        "averages 4.525. All 360 reference programs passed nine native execution cases each. "
        "Equivalent reference programs emitted identical assembly across all three frontends.", "",
        "The token reduction comes from the compact input/return and register/type convention "
        "shared by the frontends. The LLVM backend emits assembly through ordinary CPU work "
        "and consumes zero additional LLM generation tokens. The small observed IR/AIN timing "
        "difference supplies little evidence about repeatable speed differences.", "",
        "## Frozen local run", "",
        "Codex selected the same Qwen2.5-1.5B checkpoint, the arithmetic subset and the bounded "
        "run settings within the user's request. The manifest identifies the checkpoint "
        "revision, source/data hashes, GPU and package versions. The model uses BF16 with "
        "rank-16 LoRA on query/value projections, seed 20261106 and learning rate 0.001. "
        "Each arm received 96 paired training tasks repeated three times. The fixed checkpoint "
        "was evaluated using task requirements and a format label, with no recurring manual.", "",
        "The frozen limits were 256 training positions, 64 generated positions per task, "
        "300 training seconds per arm, 120 evaluation seconds per stage, a 600-second hard "
        "process limit and a 7.8 GiB CUDA reserved-memory limit. Development passes at 9/12. "
        "All three arms met that threshold. All three completed 288 presentations and 72 updates.", "",
        "| Condition | Training seconds | Processed tokens | Supervised tokens | "
        "Peak CUDA reserved GiB |",
        "|---|---|---|---|---|",
    ])
    for arm in ARMS:
        result = results[arm]
        training = result["training"]
        lines.append(f"| {arm} | {training['seconds']:.3f} | {training['processed_tokens']} | "
                     f"{training['supervised_tokens']} | {result['peak_reserved_gib']:.3f} |")
    lines.extend([
        "", "Training-token presentations measure local exposures, including prompt positions. "
        "Training timings exclude setup, evaluation and adapter saving. CUDA peaks exclude "
        "desktop applications and other processes. Raw results retain model-loading times, "
        "loss updates and parameter counts.", "",
        "## All-attempt evaluation ledger", "",
        "| Condition | Stage | Correct / assigned | Input tokens | Output tokens | "
        "Generation seconds | Judge seconds | Generation + judge seconds per correct task |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for arm in ARMS:
        for stage in ("before", "after"):
            item = summary[arm][stage]
            per_correct = ((item["generation_seconds"] + item["judge_seconds"]) / item["correct"]
                           if item["correct"] else None)
            value = f"{per_correct:.3f}" if per_correct is not None else "undefined"
            lines.append(f"| {arm} | {stage} | {item['correct']}/{item['assigned']} | "
                         f"{item['input_tokens']} | {item['output_tokens']} | "
                         f"{item['generation_seconds']:.3f} | {item['judge_seconds']:.3f} | {value} |")
    lines.extend([
        "", "Judge time includes parsing, failed parsing attempts, compilation and nine native "
        "execution checks. Compiler time is a component of judge time for compiled candidates. "
        "Each stage's totals include unsuccessful predictions. All assigned examples were "
        "attempted. Development-assistant work and initial environment setup are outside this "
        "local evaluation ledger.", "",
        "## Instrument repair and retained attempts", "",
        "The first compiler review found a Python parser depth limit that rejected sixteen "
        "signed operations while the compact frontends accepted that boundary. The initial "
        "learning attempt was stopped before adaptation. The parser was repaired, a boundary "
        "regression was added, all nine compiler/data tests passed, and fresh reference and "
        "learning manifests were frozen. The arithmetic evaluation tasks use one or two operations.", "",
        f"The interrupted baseline consumed {aborted_counts['input_tokens']} input tokens, "
        f"{aborted_counts['output_tokens']} output tokens and "
        f"{aborted_counts['generation_seconds']:.3f} generation seconds across "
        f"{aborted_counts['attempted']} saved predictions. Its raw observations and interruption "
        "record are retained under `aborted-v1`. The earlier reference run is also retained "
        "with a pointer to the repaired instrument's report.", "",
        "## Scope and reproducibility", "",
        "This screen reuses the previous gate's development tasks and composition holdouts "
        "for engineering diagnosis. Every task is an affine integer transformation, several "
        "net offsets repeat, and there is one training seed. The pretrained checkpoint's "
        "Python familiarity affects the comparison. The compact parser also supplies stronger "
        "structural constraints than the earlier full-envelope interface, equally across arms.", "",
        "The prior full-envelope run used different evaluation time and output caps. Its "
        "comparison with this run describes an engineering change involving representation, "
        "constraints and budgets. The within-run controls share the compiler and limits. "
        "Whole-agent memory, tools, change/repair/handoff chains and broad efficiency still "
        "require the larger experiment.", "",
        "The exact native domain admits at most sixteen add/subtract operations with input "
        "and literal magnitudes bounded by one million. This bounds intermediates safely "
        "inside signed 64-bit arithmetic. Runtime behavior was checked on native code. "
        "The few-instruction functions and Python call overhead provide limited runtime "
        "benchmarking value.", "",
        "The original SDPA warning is preserved in each arm log. The pinned model configuration "
        "has sliding-window attention disabled. Raw predictions were replayed during export, "
        "including assembly hashes, and all frozen source/data hashes matched. Adapter files "
        "are stored in local scratch. `example.ain`, `example.ll` and `example.s` show a complete "
        "compact-source-to-native example with `2 7;3 4` computing `x+3`.", "",
    ])
    (output / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(output / "REPORT.md")


if __name__ == "__main__":
    main()
