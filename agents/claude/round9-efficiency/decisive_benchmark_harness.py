"""Harness for the proposed decisive benchmark (Section 7 of the report). Records every trial in the
AICC_Efficiency_Measurement_Template.csv schema and computes the primary paired metric with a bootstrap CI.
STATUS: the trial loop, CSV logging and statistics are TESTED in --dry-run mode with a SYNTHETIC client whose usage
numbers are fabricated test fixtures. Real provider adapters are NOT implemented and NOT tested: plug in an adapter that
returns the provider's own usage object (uncached input, cached input, output, reasoning) and billed cost."""
import argparse, csv, json, random, statistics, time, uuid
COLS = list(csv.reader(open("/mnt/user-data/uploads/AICC_Efficiency_Measurement_Template.csv")))[0]
ARMS = {"A": "packages + docs + tool search + caching", "B": "same implementations via AICC registry + bindings",
        "C": "same tools as A, symbolic authoring", "D": "AICC registry + symbolic authoring"}

class SyntheticClient:
    """TEST FIXTURE ONLY. Returns made-up usage so the pipeline can be exercised without an API key."""
    def __init__(self, seed): self.rng = random.Random(seed)
    def run_task(self, arm, task):
        u = {"input_uncached_tokens": self.rng.randint(20_000, 60_000), "input_cached_tokens": self.rng.randint(50_000, 300_000),
             "output_tokens": self.rng.randint(2_000, 9_000), "reasoning_tokens": self.rng.randint(1_000, 8_000),
             "llm_calls": self.rng.randint(5, 30), "tool_calls": self.rng.randint(5, 40), "retries": self.rng.randint(0, 2)}
        u["model_bill_usd"] = round(u["input_uncached_tokens"] * 3e-6 + u["input_cached_tokens"] * 3e-7 + (u["output_tokens"]) * 1.5e-5, 4)
        return u, self.rng.random() < 0.8, True

def run(client, tasks, trials, out_csv, registry_amortized_usd=0.0, provider="SYNTHETIC-DRY-RUN"):
    plan = [(arm, t, k) for arm in ARMS for t in tasks for k in range(1, trials + 1)]
    random.Random(42).shuffle(plan)                                   # randomised trial order
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader()
        for arm, task, k in plan:
            t0 = time.perf_counter(); usage, ok, safe = client.run_task(arm, task); wall = (time.perf_counter() - t0) * 1000
            reg = registry_amortized_usd if arm in ("B", "D") else 0.0
            row = {c: "" for c in COLS}
            row.update({"run_id": str(uuid.uuid4())[:8], "trial_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "provider": provider,
                        "arm": arm, "task_id": task, "trial_index": k, "session_id": f"fresh-{arm}-{task}-{k}", "warm_or_cold": "cold",
                        "success_hidden_tests": int(ok), "security_pass": int(safe), "registry_amortized_usd": reg,
                        "total_cost_usd": round(usage["model_bill_usd"] + reg, 4), "wall_time_ms": round(wall, 2), **usage})
            w.writerow(row)

def analyse(path, a="A", b="B", boot=2000):
    rows = list(csv.DictReader(open(path)))
    def cpct(rs):  # amortized cost per successful task: all spend (including failures) / successes
        s = sum(int(r["success_hidden_tests"]) and int(r["security_pass"]) for r in rs)
        return sum(float(r["total_cost_usd"]) for r in rs) / s if s else float("inf")
    by = lambda arm: [r for r in rows if r["arm"] == arm]
    tasks = sorted({r["task_id"] for r in rows}); rng = random.Random(0); diffs = []
    ga = {t: [r for r in by(a) if r["task_id"] == t] for t in tasks}; gb = {t: [r for r in by(b) if r["task_id"] == t] for t in tasks}
    for _ in range(boot):   # two-level bootstrap: resample tasks, then trials within each task (tasks-only is anti-conservative)
        pick = [rng.choice(tasks) for _ in tasks]
        ra = [rng.choice(ga[t]) for t in pick for _ in ga[t]]; rb = [rng.choice(gb[t]) for t in pick for _ in gb[t]]
        diffs.append(cpct(rb) / cpct(ra) - 1)
    diffs.sort()
    sr = lambda rs: sum(int(r["success_hidden_tests"]) for r in rs) / len(rs)
    return {"cpct_" + a: cpct(by(a)), "cpct_" + b: cpct(by(b)), "relative_change_b_vs_a": cpct(by(b)) / cpct(by(a)) - 1,
            "ci95": (diffs[int(0.025 * boot)], diffs[int(0.975 * boot)]), "success_rate_diff": sr(by(b)) - sr(by(a))}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    if not a.dry_run: raise SystemExit("No real provider adapter is implemented. Use --dry-run to test the pipeline.")
    run(SyntheticClient(1), [f"T{i:02d}" for i in range(1, 13)], 3, "dry_run_trials.csv", registry_amortized_usd=0.01)
    res = analyse("dry_run_trials.csv"); print("DRY RUN (synthetic numbers, not results):", json.dumps(res, indent=1))
