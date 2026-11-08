"""Matched local adaptations of compact programs compiled through LLVM."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.ain_compiler_gate.data import format_prompt, judge, make_dataset
from experiments.native_learning_gate.run import MODEL, REVISION, log, save, summarize

ARMS = ("python", "ir", "ain")
CONFIG = {
    "model": MODEL, "revision": REVISION, "seed": 20261106,
    "epochs": 3, "gradient_accumulation": 4,
    "learning_rate": 0.001, "lora_rank": 16, "lora_alpha": 32,
    "lora_targets": ["q_proj", "v_proj"], "max_sequence": 256,
    "max_new_tokens": 64, "train_seconds_per_arm": 300,
    "eval_seconds_per_stage": 120, "hard_seconds_per_arm": 600,
    "peak_reserved_limit_gib": 7.8, "dev_threshold": 9,
    "purpose": "compact authoring with a common native compiler backend",
}


def evaluate(model, tokenizer, rows, arm, path):
    import torch

    model.eval()
    records = []
    started = time.perf_counter()
    for row in rows:
        record = {"id": row["id"], "split": row["split"]}
        if time.perf_counter() - started >= CONFIG["eval_seconds_per_stage"]:
            record.update(output="", syntax_ok=False, correct=False, error="stage_time_limit")
        else:
            inputs = tokenizer(format_prompt(row, arm), return_tensors="pt").to("cuda")
            torch.cuda.synchronize()
            begin = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(
                    **inputs, do_sample=False, max_new_tokens=CONFIG["max_new_tokens"],
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id, use_cache=True,
                )
            torch.cuda.synchronize()
            seconds = time.perf_counter() - begin
            new_ids = generated[0, inputs.input_ids.shape[1]:]
            text = tokenizer.decode(new_ids, skip_special_tokens=True)
            begin = time.perf_counter()
            verdict = judge(arm, text, row)
            record.update(output=text, input_tokens=inputs.input_ids.numel(),
                          output_tokens=len(new_ids), inference_seconds=seconds,
                          judge_seconds=time.perf_counter() - begin,
                          at_output_cap=len(new_ids) == CONFIG["max_new_tokens"], **verdict)
        records.append(record)
        save(path, records)
        log("prediction", arm=arm, stage=path.stem, id=row["id"],
            correct=record["correct"], error=record["error"])
    return records


def run_arm(arm, rows, directory):
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    set_seed(CONFIG["seed"])
    torch.set_num_threads(4)
    if not torch.cuda.is_available() or not torch.cuda.is_bf16_supported():
        raise RuntimeError("CUDA with BF16 is required for this frozen run")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    training_rows = [row for row in rows if row["split"] == "train"]
    examples = []
    for row in training_rows:
        prefix = tokenizer(format_prompt(row, arm), add_special_tokens=False).input_ids
        target = tokenizer(row["targets"][arm], add_special_tokens=False).input_ids
        tokens = prefix + target + [tokenizer.eos_token_id]
        if len(tokens) > CONFIG["max_sequence"]:
            raise ValueError("Training example exceeds the frozen context")
        examples.append((tokens, [-100] * len(prefix) + target + [tokenizer.eos_token_id]))
    dev = [row for row in rows if row["split"] == "dev"]
    heldout = [row for row in rows if row["split"] == "holdout"]
    evaluation = [row for pair in zip(dev, heldout, strict=True) for row in pair]
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, local_files_only=True, torch_dtype=torch.bfloat16,
        attn_implementation="sdpa", device_map={"": 0}, low_cpu_mem_usage=True,
    )
    model = get_peft_model(model, LoraConfig(
        r=CONFIG["lora_rank"], lora_alpha=CONFIG["lora_alpha"],
        target_modules=CONFIG["lora_targets"], lora_dropout=0,
        bias="none", task_type="CAUSAL_LM",
    ))
    load_seconds = time.perf_counter() - started
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.config.use_cache = False
    before = evaluate(model, tokenizer, evaluation, arm, directory / f"{arm}-before.json")
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),
                                 lr=CONFIG["learning_rate"])
    model.train()
    order = list(range(len(examples)))
    rng = random.Random(CONFIG["seed"])
    updates = []
    processed = 0
    supervised = 0
    presentations = 0
    stopped = "epochs_complete"
    torch.cuda.synchronize()
    started = time.perf_counter()
    for epoch in range(CONFIG["epochs"]):
        rng.shuffle(order)
        for offset in range(0, len(order), CONFIG["gradient_accumulation"]):
            if time.perf_counter() - started >= CONFIG["train_seconds_per_arm"]:
                stopped = "training_time_limit"
                break
            indices = order[offset:offset + CONFIG["gradient_accumulation"]]
            optimizer.zero_grad(set_to_none=True)
            losses = []
            for index in indices:
                tokens, labels = examples[index]
                batch = {"input_ids": torch.tensor([tokens], device="cuda"),
                         "labels": torch.tensor([labels], device="cuda")}
                loss = model(**batch).loss
                if not torch.isfinite(loss):
                    raise RuntimeError("Nonfinite loss")
                (loss / len(indices)).backward()
                losses.append(loss.item())
                processed += len(tokens)
                supervised += sum(label != -100 for label in labels)
                presentations += 1
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            torch.cuda.synchronize()
            update = {"step": len(updates) + 1, "epoch": epoch + 1,
                      "loss": sum(losses) / len(losses),
                      "elapsed_seconds": time.perf_counter() - started}
            updates.append(update)
            if len(updates) % 6 == 0:
                log("train", arm=arm, **update)
            if torch.cuda.max_memory_reserved() / 2**30 > CONFIG["peak_reserved_limit_gib"]:
                stopped = "memory_limit"
                break
        if stopped != "epochs_complete":
            break
    seconds = time.perf_counter() - started
    training = {"updates": updates, "presentations": presentations,
                "processed_tokens": processed, "supervised_tokens": supervised,
                "seconds": seconds, "tokens_per_second": processed / seconds,
                "stop_reason": stopped}
    save(directory / f"{arm}-training.json", training)
    model.save_pretrained(directory / f"{arm}-adapter")
    after = evaluate(model, tokenizer, evaluation, arm, directory / f"{arm}-after.json")
    result = {"arm": arm, "before": summarize(before), "after": summarize(after),
              "training": training, "load_seconds": load_seconds,
              "parameters": sum(p.numel() for p in model.parameters()),
              "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
              "vocabulary": len(tokenizer),
              "peak_allocated_gib": torch.cuda.max_memory_allocated() / 2**30,
              "peak_reserved_gib": torch.cuda.max_memory_reserved() / 2**30,
              "dev_gate_pass": summarize(after)["dev"]["correct"] >= CONFIG["dev_threshold"]}
    save(directory / f"{arm}-result.json", result)
    log("arm_complete", **{key: result[key] for key in ("arm", "after", "dev_gate_pass")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/ain-compiler-gate-v2")
    parser.add_argument("--arm", choices=ARMS)
    args = parser.parse_args()
    rows = make_dataset()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.arm:
        try:
            run_arm(args.arm, rows, args.output)
        except Exception as error:
            save(args.output / f"{args.arm}-failure.json", {"error": repr(error)})
            raise
        return
    import torch
    sources = [Path(__file__), Path(__file__).with_name("data.py"),
               Path(__file__).with_name("compiler.py"),
               ROOT / "experiments/native_learning_gate/run.py",
               ROOT / "experiments/native_learning_gate/data.py",
               ROOT / "experiments/ain_v0/ain/language.py"]
    manifest = {"config": CONFIG,
                "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sources},
                "dataset_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
                "packages": {name: importlib.metadata.version(name) for name in
                             ("torch", "transformers", "peft", "accelerate", "llvmlite")},
                "gpu": torch.cuda.get_device_name(), "cuda_runtime": torch.version.cuda}
    if (args.output / "manifest.json").exists():
        raise RuntimeError("A fresh output directory is required")
    save(args.output / "manifest.json", manifest)
    save(args.output / "dataset.json", rows)
    log("frozen", **manifest)
    statuses = {}
    for arm in ARMS:
        with (args.output / f"{arm}.log").open("w", encoding="utf-8") as stream:
            process = subprocess.Popen([sys.executable, "-u", str(Path(__file__)),
                                        "--arm", arm, "--output", str(args.output)],
                                       stdout=stream, stderr=subprocess.STDOUT)
            try:
                statuses[arm] = process.wait(timeout=CONFIG["hard_seconds_per_arm"])
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                statuses[arm] = "hard_timeout"
        save(args.output / "statuses.json", statuses)
        log("arm_exit", arm=arm, status=statuses[arm])
        if statuses[arm] != 0:
            raise RuntimeError(f"Arm {arm} failed, see preserved log")


if __name__ == "__main__":
    main()
