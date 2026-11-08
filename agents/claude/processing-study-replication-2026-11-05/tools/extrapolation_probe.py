"""Post-replication probe (Claude): learned plan choices inside vs outside the 800-14,000 calibration range.
For each stress job shape at several sizes: each model's choice (original frozen, Track A run-001, run-002) and the static
policy's choice, plus measured kernel time of EVERY eligible plan (median of 3, gc before each, randomized order, one warm
process, list input for all shapes). Kernel-only; not the fresh-process stress protocol. Unchanged frozen sources."""
import gc, json, random, statistics, sys, time
S = "/home/claude/ps/AICC/experiments/processing_study"; sys.path.insert(0, S)
from aicc_processing import kernels
from aicc_processing.data import events, inspect_features
from aicc_processing.learning import CostNetwork, static_choice
from aicc_processing.benchmark import stress_jobs
MODELS = {"original": f"{S}/results/full-2026-11-05", "trackA-001": f"{S}/results/anthropic-claude-opus-5.5-2026-11-05-trackA-001",
          "trackA-002": f"{S}/results/anthropic-claude-opus-5.5-2026-11-05-trackA-002"}
nets = {k: CostNetwork.load(f"{v}/cost-network.json") for k, v in MODELS.items()}
policy = json.load(open(f"{MODELS['trackA-002']}/static-policy.json"))
rng = random.Random(20261105); out = []
for n in (800, 14000, 100000, 1000000):
    for job, _streaming in stress_jobs(n):
        data = list(events(job)); feats, _ = inspect_features(data, job)
        plans = ["cached", "partitioned"] + (["ordered"] if job.ordered else [])
        reps = 3; order = [p for p in plans for _ in range(reps)]; rng.shuffle(order); times = {p: [] for p in plans}
        for p in order:
            gc.collect(); t = time.perf_counter(); kernels.VARIANTS[p](data, job.window, job.minimum); times[p].append(time.perf_counter() - t)
        med = {p: statistics.median(v) for p, v in times.items()}; best = min(med, key=med.get)
        choices = {k: net.choose(feats, job.ordered) for k, net in nets.items()}; choices["static"] = static_choice(policy, job.ordered)
        row = {"n": n, "job": job.name, "in_calibration_range": 800 <= n <= 14000, "median_kernel_seconds": med, "best_plan": best,
               "choices": choices, "regret_percent": {k: 100 * (med[c] / med[best] - 1) for k, c in choices.items()}}
        out.append(row); del data; gc.collect()
        print(f"n={n:>8} {job.name:18s} best={best:11s} " + " ".join(f"{k}:{c}({row['regret_percent'][k]:+.1f}%)" for k, c in choices.items()), flush=True)
json.dump(out, open("/home/claude/ps/agent_logs/extrapolation_probe.json", "w"), indent=1)
print("DONE")
