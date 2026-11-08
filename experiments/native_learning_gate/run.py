"""Bounded local adaptation screen. Run from the repository root."""
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

from experiments.native_learning_gate.data import format_prompt, judge, make_dataset

MODEL = "Qwen/Qwen2.5-1.5B"
REVISION = "8faed761d45a263340a0528343f099c05c9a4323"
ARMS = ("python", "ir", "ain")
CONFIG = {
    "model": MODEL, "revision": REVISION, "seed": 20261106,
    "arms": ARMS, "epochs": 3, "gradient_accumulation": 4,
    "learning_rate": 0.001, "lora_rank": 16, "lora_alpha": 32,
    "lora_targets": ["q_proj", "v_proj"], "max_sequence": 512,
    "max_new_tokens": 320, "train_seconds_per_arm": 300,
    "eval_seconds_per_stage": 90, "peak_reserved_limit_gib": 7.8,
    "gate_dev_correct_fraction": 0.75,
    "purpose": "memory, throughput and executable language-learning screen",
}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def log(event, **details):
    print(json.dumps({"event": event, **details}), flush=True)


def evaluate(model, tokenizer, rows, arm, stage, output):
    import torch

    model.eval()
    records = []
    started = time.perf_counter()
    for row in rows:
        prompt = format_prompt(row, arm)
        if time.perf_counter() - started >= CONFIG["eval_seconds_per_stage"]:
            records.append({"id": row["id"], "split": row["split"],
                            "correct": False, "error": "stage_time_limit",
                            "syntax_ok": False, "output": ""})
            save(output, records)
            continue
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        torch.cuda.synchronize()
        begin = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **inputs, do_sample=False, max_new_tokens=CONFIG["max_new_tokens"],
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id, use_cache=True,
            )
        torch.cuda.synchronize()
        inference_seconds = time.perf_counter() - begin
        new_ids = generated[0, inputs.input_ids.shape[1]:]
        text = tokenizer.decode(new_ids, skip_special_tokens=True)
        begin = time.perf_counter()
        verdict = judge(arm, text, row)
        records.append({"id": row["id"], "split": row["split"],
                        "output": text, "input_tokens": inputs.input_ids.numel(),
                        "output_tokens": len(new_ids),
                        "truncated": len(new_ids) == CONFIG["max_new_tokens"],
                        "inference_seconds": inference_seconds,
                        "judge_seconds": time.perf_counter() - begin, **verdict})
        save(output, records)
        log("prediction", arm=arm, stage=stage, id=row["id"], **verdict)
    return records


def summarize(records):
    result = {}
    for split in ("dev", "holdout"):
        items = [r for r in records if r["split"] == split]
        result[split] = {
            "correct": sum(r["correct"] for r in items), "assigned": len(items),
            "syntax_valid": sum(r["syntax_ok"] for r in items),
            "inference_seconds": sum(r.get("inference_seconds", 0) for r in items),
            "input_tokens": sum(r.get("input_tokens", 0) for r in items),
            "output_tokens": sum(r.get("output_tokens", 0) for r in items),
        }
    return result


def run_arm(arm, rows, output):
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    set_seed(CONFIG["seed"])
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    tokenizer.pad_token = tokenizer.eos_token
    train_rows = [r for r in rows if r["split"] == "train"]
    examples = []
    for row in train_rows:
        prefix = tokenizer(format_prompt(row, arm), add_special_tokens=False).input_ids
        target = tokenizer(row["targets"][arm], add_special_tokens=False).input_ids
        token_ids = prefix + target + [tokenizer.eos_token_id]
        if len(token_ids) > CONFIG["max_sequence"]:
            raise ValueError(f"Sequence exceeds frozen context: {row['id']}")
        examples.append((token_ids, [-100] * len(prefix) + target + [tokenizer.eos_token_id]))
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    if dtype != torch.bfloat16:
        raise RuntimeError("This gate requires verified BF16 support")
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=REVISION, torch_dtype=dtype, attn_implementation="sdpa",
        device_map={"": 0}, low_cpu_mem_usage=True,
    )
    load_seconds = time.perf_counter() - started
    model = get_peft_model(model, LoraConfig(
        r=CONFIG["lora_rank"], lora_alpha=CONFIG["lora_alpha"],
        target_modules=CONFIG["lora_targets"], lora_dropout=0,
        bias="none", task_type="CAUSAL_LM",
    ))
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model.config.use_cache = False
    model.train()
    tokens, labels = examples[0]
    batch = {"input_ids": torch.tensor([tokens], device="cuda"),
             "labels": torch.tensor([labels], device="cuda")}
    torch.cuda.synchronize()
    started = time.perf_counter()
    smoke_loss = model(**batch).loss
    smoke_loss.backward()
    torch.cuda.synchronize()
    smoke_seconds = time.perf_counter() - started
    model.zero_grad(set_to_none=True)
    smoke = {"loss": smoke_loss.item(), "seconds": smoke_seconds,
             "tokens": len(tokens), "peak_allocated_gib": torch.cuda.max_memory_allocated() / 2**30,
             "peak_reserved_gib": torch.cuda.max_memory_reserved() / 2**30}
    save(output / f"{arm}-fit.json", smoke)
    log("fit", arm=arm, **smoke)
    if not math.isfinite(smoke["loss"]) or smoke["peak_reserved_gib"] > CONFIG["peak_reserved_limit_gib"]:
        raise RuntimeError("Memory/finite-loss gate failed")
    development = [r for r in rows if r["split"] == "dev"]
    holdout = [r for r in rows if r["split"] == "holdout"]
    evaluation = [row for pair in zip(development, holdout, strict=True) for row in pair]
    before = evaluate(model, tokenizer, evaluation, arm, "before", output / f"{arm}-before.json")
    model.train()
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),
                                 lr=CONFIG["learning_rate"])
    order = list(range(len(examples)))
    rng = random.Random(CONFIG["seed"])
    updates = []
    processed_tokens = 0
    supervised_tokens = 0
    presentations = 0
    torch.cuda.synchronize()
    started = time.perf_counter()
    stopped = "epochs_complete"
    for epoch in range(CONFIG["epochs"]):
        rng.shuffle(order)
        for offset in range(0, len(order), CONFIG["gradient_accumulation"]):
            if time.perf_counter() - started > CONFIG["train_seconds_per_arm"]:
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
                    raise RuntimeError("Nonfinite training loss")
                (loss / len(indices)).backward()
                losses.append(loss.item())
                processed_tokens += len(tokens)
                supervised_tokens += sum(label != -100 for label in labels)
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
    train_seconds = time.perf_counter() - started
    training = {"updates": updates, "seconds": train_seconds,
                "processed_tokens": processed_tokens, "supervised_tokens": supervised_tokens,
                "presentations": presentations, "tokens_per_second": processed_tokens / train_seconds,
                "stop_reason": stopped}
    save(output / f"{arm}-training.json", training)
    model.save_pretrained(output / f"{arm}-adapter")
    after = evaluate(model, tokenizer, evaluation, arm, "after", output / f"{arm}-after.json")
    dev = summarize(after)["dev"]
    result = {"arm": arm, "load_seconds": load_seconds, "dtype": str(dtype),
              "parameters": sum(p.numel() for p in model.parameters()),
              "trainable_parameters": sum(p.numel() for p in model.parameters() if p.requires_grad),
              "vocabulary": len(tokenizer), "fit": smoke, "training": training,
              "peak_allocated_gib": torch.cuda.max_memory_allocated() / 2**30,
              "peak_reserved_gib": torch.cuda.max_memory_reserved() / 2**30,
              "before": summarize(before), "after": summarize(after),
              "dev_gate_pass": dev["correct"] / dev["assigned"] >= CONFIG["gate_dev_correct_fraction"]}
    save(output / f"{arm}-result.json", result)
    log("arm_complete", arm=arm, after=result["after"], dev_gate_pass=result["dev_gate_pass"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "work/rtx3080-gate-v1")
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
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    manifest = {"config": CONFIG, "git_head": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), Path(__file__).with_name("data.py"),
                                       ROOT / "experiments/ain_v0/ain/language.py")},
        "dataset_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
        "packages": {name: importlib.metadata.version(name) for name in
                     ("torch", "transformers", "peft", "accelerate", "huggingface-hub")},
        "gpu": torch.cuda.get_device_name(), "gpu_bytes": torch.cuda.get_device_properties(0).total_memory,
        "cuda_runtime": torch.version.cuda, "bf16_supported": torch.cuda.is_bf16_supported()}
    if (args.output / "manifest.json").exists():
        raise RuntimeError("Choose a fresh output directory to preserve earlier runs")
    save(args.output / "manifest.json", manifest)
    save(args.output / "dataset.json", rows)
    log("frozen", **manifest)
    statuses = {}
    for arm in ARMS:
        with (args.output / f"{arm}.log").open("w", encoding="utf-8") as stream:
            process = subprocess.Popen([sys.executable, "-u", str(Path(__file__)), "--arm", arm,
                                        "--output", str(args.output)], stdout=stream, stderr=subprocess.STDOUT)
            try:
                statuses[arm] = process.wait(timeout=600)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                statuses[arm] = "hard_timeout_600_seconds"
        save(args.output / "statuses.json", statuses)
        log("arm_exit", arm=arm, status=statuses[arm])
        if statuses[arm] != 0:
            raise RuntimeError(f"Arm {arm} failed, see preserved log")


if __name__ == "__main__":
    main()
