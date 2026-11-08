"""Export completed local gate observations and build their Markdown report."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[2]
ARMS = ("python", "ir", "ain")
ARTIFACTS = ("fit", "before", "after", "training", "result")
WEIGHT_SHA256 = "a961db72e75d52b18e6b0c9d379e51a26973b233385e0e127fdda7d648aec796"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def observation_counts(records, split):
    assigned = [row for row in records if row["split"] == split]
    return {
        "assigned": len(assigned),
        "attempted": sum("input_tokens" in row for row in assigned),
        "timeouts": sum(row.get("error") == "stage_time_limit" for row in assigned),
        "truncated": sum(row.get("truncated", False) for row in assigned),
        "correct": sum(row["correct"] for row in assigned),
        "syntax_valid": sum(row["syntax_ok"] for row in assigned),
        "input_tokens": sum(row.get("input_tokens", 0) for row in assigned),
        "output_tokens": sum(row.get("output_tokens", 0) for row in assigned),
        "seconds": sum(row.get("inference_seconds", 0) for row in assigned),
    }


def make_report(manifest, dataset, results, records, hardware, cpu):
    config = manifest["config"]
    sizes = Counter(row["split"] for row in dataset)
    required = int(config["gate_dev_correct_fraction"] * sizes["dev"] + 0.999999)
    lines = [
        "# RTX 3080 local learning feasibility gate",
        "",
        "6 November 2026. Research direction and concept by Izik Bachar. "
        "Implementation, local execution and report preparation by Codex with collaboration agents.",
        "",
        f"The frozen development threshold was {required}/{sizes['dev']} correct tasks "
        f"({config['gate_dev_correct_fraction']:.0%}) for each adapted condition. "
        "Every assigned task remains in the denominator, including timeouts and invalid outputs.",
        "",
        "| Condition | Development gate | Correct after adaptation |",
        "|---|---|---|",
    ]
    for arm in ARMS:
        counts = observation_counts(records[arm]["after"], "dev")
        passed = counts["correct"] >= required
        lines.append(f"| {arm} | {'Pass' if passed else 'Fail'} | "
                     f"{counts['correct']}/{counts['assigned']} |")
    ain_correct = observation_counts(records["ain"]["after"], "dev")["correct"]
    if ain_correct < required:
        lines.extend(["", "AIN missed the frozen development threshold. Scaling stopped at "
                      "this gate. The memory-fit check succeeded, while executable learning "
                      "under these particular data, adaptation and evaluation settings was "
                      "insufficient for the next whole-agent trial."])
    lines.extend([
        "",
        "This gate measures memory fit, local training throughput and executable language learning. "
        "Cost savings remain unestablished. The whole-agent experiment is specified in "
        "[WHOLE_AGENT_NEXT.md](../../WHOLE_AGENT_NEXT.md).",
        "",
        "## Model and frozen setup",
        "",
        f"Model `{config['model']}`, revision `{config['revision']}`, Apache 2.0 license. "
        f"The pretrained base checkpoint was adapted with seed {config['seed']}, BF16, "
        f"LoRA rank {config['lora_rank']} and alpha {config['lora_alpha']} on "
        f"`{'`, `'.join(config['lora_targets'])}`. The learning rate was "
        f"{config['learning_rate']}. The tokenizer vocabulary and embeddings were retained.",
        "",
        f"The dataset contains {sizes['train']} training, {sizes['dev']} development and "
        f"{sizes['holdout']} structural-holdout tasks. The target exposure was "
        f"{config['epochs']} passes, with {config['gradient_accumulation']} presentations per "
        "optimization update. Equivalent semantic examples were used across conditions. "
        "Numeric AIN is the existing readable IR's numeric serialization.",
        "",
        f"Codex selected the model, data and automatic caps within the user's request to run "
        f"the handoff. The frozen caps were {config['train_seconds_per_arm']} seconds of "
        f"training per condition, {config['eval_seconds_per_stage']} seconds per evaluation "
        f"stage, {config['max_sequence']} training positions, {config['max_new_tokens']} generated "
        f"positions per attempt and {config['peak_reserved_limit_gib']} GiB of CUDA allocator "
        "reserved memory. The controller imposed a 600-second hard limit per condition. "
        "Soft limits were checked between tasks or updates. These were local execution "
        "choices, with no purchased GPU or API budget.",
        "",
        f"Hardware was {manifest['gpu']} with {manifest['gpu_bytes'] / 2**30:.2f} GiB device "
        f"memory, {hardware['TotalPhysicalMemory'] / 2**30:.2f} GiB system RAM and "
        f"{cpu['Name'].strip()} ({cpu['NumberOfCores']} cores, "
        f"{cpu['NumberOfLogicalProcessors']} logical processors). CUDA runtime "
        f"{manifest['cuda_runtime']}, BF16 supported `{manifest['bf16_supported']}`. "
        "The GPU also served desktop applications during execution.",
        "",
        "| Package | Recorded version |",
        "|---|---|",
    ])
    for name, version in manifest["packages"].items():
        lines.append(f"| {name} | {version} |")
    lines.extend([
        "",
        "## Execution outcomes",
        "",
        "The before stage used the unadapted checkpoint through zero-initialized LoRA "
        "updates. A smoke backward pass checked training compatibility without an optimizer "
        "update. Both evaluation stages used greedy generation, one attempt per task, "
        "and task requirements plus the requested output-format label. The fixed language "
        "manual was absent. Development and holdout tasks were interleaved.",
        "",
        "| Condition | Stage | Split | Correct / assigned | Syntax valid | Attempted | "
        "Stage timeouts | At output cap |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for arm in ARMS:
        for stage in ("before", "after"):
            for split in ("dev", "holdout"):
                count = observation_counts(records[arm][stage], split)
                lines.append(
                    f"| {arm} | {stage} | {split} | {count['correct']}/{count['assigned']} | "
                    f"{count['syntax_valid']} | {count['attempted']} | {count['timeouts']} | "
                    f"{count['truncated']} |")
    lines.extend([
        "",
        "Syntax validity includes the declared structural and type checks. A correct program "
        "must return exact integer results on every judge input. The Python evaluator accepts "
        "one restricted return expression, while the existing VM validates IR/AIN programs "
        "with bounded execution. Output-cap flags also include a completion ending exactly "
        "at that cap.",
        "",
        "| Condition | Stage | Input tokens | Output tokens | Inference seconds |",
        "|---|---|---|---|---|",
    ])
    for arm in ARMS:
        for stage in ("before", "after"):
            stage_records = records[arm][stage]
            inputs = sum(row.get("input_tokens", 0) for row in stage_records)
            outputs = sum(row.get("output_tokens", 0) for row in stage_records)
            seconds = sum(row.get("inference_seconds", 0) for row in stage_records)
            lines.append(f"| {arm} | {stage} | {inputs:,} | {outputs:,} | {seconds:.3f} |")
    lines.extend([
        "",
        "Inference timings include generation and device synchronization. Raw prediction "
        "records retain judge timings. Attempted malformed and unsuccessful outputs contribute "
        "to these totals. Assigned tasks skipped at the stage ceiling have zero model work.",
        "",
        "## Training and memory",
        "",
        "| Condition | Presentations | Updates | Processed tokens | Supervised tokens | "
        "Training seconds | Processed tokens / second | Stop reason |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for arm in ARMS:
        training = results[arm]["training"]
        lines.append(
            f"| {arm} | {training['presentations']} | {len(training['updates'])} | "
            f"{training['processed_tokens']:,} | {training['supervised_tokens']:,} | "
            f"{training['seconds']:.3f} | {training['tokens_per_second']:.2f} | "
            f"{training['stop_reason']} |")
    lines.extend([
        "",
        "Training tokens are repeated local model exposures, including prompt positions. "
        "Supervised tokens count target positions used by the loss. These token presentations "
        "are local computation and carry no ChatGPT token charge. Measured training throughput "
        "excludes download, model loading, the smoke pass, evaluation and saving. Token lengths "
        "and computation differ even when semantic exposure matches.",
        "",
        "| Condition | Tokenizer vocabulary | Total parameters with LoRA | Trainable parameters | "
        "Smoke allocated GiB | Smoke reserved GiB | Full allocated GiB | Full reserved GiB |",
        "|---|---|---|---|---|---|---|---|",
    ])
    for arm in ARMS:
        result = results[arm]
        fit = result["fit"]
        lines.append(
            f"| {arm} | {result['vocabulary']:,} | {result['parameters']:,} | "
            f"{result['trainable_parameters']:,} | {fit['peak_allocated_gib']:.3f} | "
            f"{fit['peak_reserved_gib']:.3f} | {result['peak_allocated_gib']:.3f} | "
            f"{result['peak_reserved_gib']:.3f} |")
    lines.extend([
        "",
        "Full peaks cover model loading, smoke, baseline evaluation, training and adapted "
        "evaluation in each condition's process. CUDA allocator measurements exclude desktop "
        "and other processes' device memory. The existing tokenizer and embedding vocabulary "
        "were used throughout, with no added instruction tokens.",
        "",
        "Transformers emitted a sliding-window/SDPA compatibility warning in every arm. "
        "The pinned checkpoint configuration has `use_sliding_window` set to `false`. "
        "The configuration and original warnings are preserved with the observations.",
        "",
        "## Setup recovery and provenance",
        "",
        "The initial unchunked model-weight download failed. Recovery downloaded byte ranges, "
        "assembled the 3,087,467,144-byte weight file and verified its complete SHA-256 before "
        f"loading. The verified digest was `{WEIGHT_SHA256}`. The checkpoint was obtained from "
        f"[the pinned model revision](https://huggingface.co/{config['model']}/tree/"
        f"{config['revision']}). Setup download attempts are separate from the training and "
        "inference timings above.",
        "",
        f"The starting repository commit was `{manifest['git_head']}`. `manifest.json` records "
        "the frozen source hashes, package versions and semantic dataset hash. This export "
        "retains the dataset, hardware records, process statuses, raw predictions, training "
        "updates, fit/result summaries and arm logs. Adapters and model weights remain in "
        "local scratch storage.",
        "",
        "## Limits and next experiment",
        "",
        "All tasks are affine integer transformations that simplify to an input plus a constant. "
        "Repeated net offsets occur, and the structural holdouts are surface compositions "
        "within this small semantic family. These observations support only the declared "
        "executable-fluency screen. One training seed and a tiny dataset provide limited "
        "evidence about variability. The pretrained model already has Python exposure.",
        "",
        "This first gate covers code generation. The requested whole-agent comparison still "
        "requires learned observable records, memory, actions, tools, repair/change/handoff "
        "chains and several compositional domains, using the plan linked above. Correctness, "
        "all-attempt resources, learning amortization and uncertainty must be measured in "
        "that study before drawing an efficiency conclusion.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "work/rtx3080-gate-v1")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "results/rtx3080-2026-11-06")
    arguments = parser.parse_args()
    source = arguments.source.resolve()
    output = arguments.output.resolve()
    if source == output:
        raise ValueError("Source and export directories must differ")
    names = ["manifest.json", "dataset.json", "statuses.json"]
    for arm in ARMS:
        names.extend(f"{arm}-{artifact}.json" for artifact in ARTIFACTS)
        names.append(f"{arm}.log")
    paths = [source / name for name in names]
    paths.extend((source.parent / "hardware.json", source.parent / "cpu.json",
                  source.parent / "model_config.json",
                  source.parent / "model_download_verification.json"))
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError("Run must finish before export. Missing files\n" + "\n".join(missing))
    statuses = load(source / "statuses.json")
    if any(statuses.get(arm) != 0 for arm in ARMS):
        raise RuntimeError("All three condition processes must complete successfully before export")
    manifest = load(source / "manifest.json")
    verification = load(source.parent / "model_download_verification.json")
    if verification["sha256"] != WEIGHT_SHA256 or verification["bytes"] != 3087467144:
        raise ValueError("Model download verification differs from the pinned weights")
    dataset = load(source / "dataset.json")
    digest = hashlib.sha256(json.dumps(dataset, sort_keys=True).encode()).hexdigest()
    if digest != manifest["dataset_sha256"]:
        raise ValueError("Dataset hash differs from the frozen manifest")
    for relative, expected in manifest["source_sha256"].items():
        path = ROOT / relative.replace("\\", "/")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Current source differs from the frozen manifest at {relative}")
    results = {arm: load(source / f"{arm}-result.json") for arm in ARMS}
    records = {arm: {stage: load(source / f"{arm}-{stage}.json") for stage in ("before", "after")}
               for arm in ARMS}
    hardware = load(source.parent / "hardware.json")
    cpu = load(source.parent / "cpu.json")
    report = make_report(manifest, dataset, results, records, hardware, cpu)
    output.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, output / path.name)
    (output / "REPORT.md").write_text(report, encoding="utf-8")
    print(output / "REPORT.md")


if __name__ == "__main__":
    main()
