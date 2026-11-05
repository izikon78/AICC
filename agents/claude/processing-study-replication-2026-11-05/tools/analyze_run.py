"""Recompute every summary from RAW records (stress-raw.json, granularity.json) for any run directory.
Formulas from MEASUREMENTS.md. Writes <out>.json and <out>.md. Read-only on the run directory."""
import json, os, statistics as st, sys
run, out = sys.argv[1], sys.argv[2]
rows = json.load(open(os.path.join(run, "stress-raw.json")))
MODES = ["reference", "static", "aicc_static", "learned", "aicc_learned"]
MiB = 1048576
jobs = sorted({r["job"]["name"] for r in rows}, key=lambda j: ["repeated-shuffled", "diverse-shuffled", "ordered-stream"].index(j) if j in ["repeated-shuffled", "diverse-shuffled", "ordered-stream"] else 9)
combos = {(r["job"]["name"], r["mode"], r["repeat"]) for r in rows}
res = {"rows": len(rows), "unique_combinations": len(combos), "expected": len(jobs) * len(MODES) * len({r["repeat"] for r in rows})}
sig = lambda r: (r["output"]["groups"], r["output"]["events_retained"], r["output"]["severity_sum"], r["output"]["sha256"])
res["signatures"] = {j: sorted({sig(r) for r in rows if r["job"]["name"] == j}) for j in jobs}
res["all_signatures_match_within_job"] = all(len(v) == 1 for v in res["signatures"].values())
summ = {}
for j in jobs:
    for m in MODES:
        rs = [r for r in rows if r["job"]["name"] == j and r["mode"] == m]
        if not rs: continue
        f = lambda k, sc=1.0: [r[k] / sc for r in rs]
        summ[(j, m)] = {"job": j, "mode": m, "repetitions": len(rs), "selected_plans": sorted({r["selected_plan"] for r in rs}),
            "median_pipeline_seconds": st.median(f("pipeline_seconds")), "min_pipeline_seconds": min(f("pipeline_seconds")), "max_pipeline_seconds": max(f("pipeline_seconds")),
            "median_worker_wall_seconds": st.median(f("worker_wall_seconds")), "min_worker_wall_seconds": min(f("worker_wall_seconds")), "max_worker_wall_seconds": max(f("worker_wall_seconds")),
            "median_peak_mib": st.median(f("process_peak_working_set_bytes", MiB)), "min_peak_mib": min(f("process_peak_working_set_bytes", MiB)), "max_peak_mib": max(f("process_peak_working_set_bytes", MiB)),
            "median_cpu_seconds": st.median(f("cpu_seconds")), "median_kernel_seconds": st.median(f("kernel_seconds")),
            "median_feature_seconds": st.median(f("feature_seconds")), "median_selection_seconds": st.median(f("selection_seconds")),
            "median_host_register_bind_seconds": st.median(f("host_register_bind_seconds")),
            "raw_pipeline_seconds": f("pipeline_seconds"), "raw_worker_wall_seconds": f("worker_wall_seconds"), "raw_peak_mib": f("process_peak_working_set_bytes", MiB),
            "output_signature": res["signatures"][j][0][3] if len(res["signatures"][j]) == 1 else "MISMATCH"}
res["mode_summaries"] = list(summ.values())
aicc_bind = [r["host_register_bind_seconds"] for r in rows if r["mode"].startswith("aicc")]
res["aicc_register_bind_median_ms"] = st.median(aicc_bind) * 1000; res["aicc_register_bind_max_ms"] = max(aicc_bind) * 1000
mix = {m: {"pipeline": sum(summ[(j, m)]["median_pipeline_seconds"] for j in jobs), "worker": sum(summ[(j, m)]["median_worker_wall_seconds"] for j in jobs)} for m in MODES}
for m in MODES:
    for k in ("pipeline", "worker"): mix[m][k + "_reduction_vs_reference_percent"] = 100 * (1 - mix[m][k] / mix["reference"][k])
res["equal_job_mix"] = mix
PAIRS = [("reference", "static", "algorithm/flow optimization"), ("static", "aicc_static", "AICC binding around optimized code"),
         ("static", "learned", "learned plan selection vs strong static"), ("learned", "aicc_learned", "AICC binding around learned code"),
         ("reference", "aicc_static", "complete delivered path (not AICC-specific)")]
comps = []
for j in jobs:
    for b, c, why in PAIRS:
        for metric, key in [("pipeline_seconds", "median_pipeline_seconds"), ("worker_wall_seconds", "median_worker_wall_seconds"), ("peak_mib", "median_peak_mib")]:
            bv, cv = summ[(j, b)][key], summ[(j, c)][key]
            comps.append({"job": j, "baseline_mode": b, "candidate_mode": c, "metric": metric, "statistic": "median of repetitions",
                          "baseline_value": bv, "candidate_value": cv, "saved_percent": 100 * (bv - cv) / bv, "speedup_ratio": bv / cv, "interpretation": why})
res["comparisons"] = comps
gpath = os.path.join(run, "granularity.json")
if os.path.exists(gpath):
    g = json.load(open(gpath)); res["granularity"] = {"differential_operation_cases": g["differential_operation_cases"], "all_outputs_equal": g["all_outputs_equal"], "summary": g["summary"]}
json.dump(res, open(out + ".json", "w"), indent=1, default=str)
L = [f"rows {res['rows']}, unique combinations {res['unique_combinations']} of {res['expected']}, all output signatures match within job: {res['all_signatures_match_within_job']}",
     f"AICC register+bind median {res['aicc_register_bind_median_ms']:.4f} ms (max {res['aicc_register_bind_max_ms']:.4f} ms)", "",
     "| Job | Mode | Plans | Pipeline median s | min-max s | Worker median s | min-max s | Peak MiB median | CPU median s |", "|---|---|---|---:|---:|---:|---:|---:|---:|"]
for s in res["mode_summaries"]:
    L.append(f"| {s['job']} | {s['mode']} | {'/'.join(s['selected_plans'])} | {s['median_pipeline_seconds']:.6f} | {s['min_pipeline_seconds']:.3f}-{s['max_pipeline_seconds']:.3f} | {s['median_worker_wall_seconds']:.6f} | {s['min_worker_wall_seconds']:.3f}-{s['max_worker_wall_seconds']:.3f} | {s['median_peak_mib']:.3f} | {s['median_cpu_seconds']:.3f} |")
L += ["", "| Mode | Sum pipeline medians s | vs reference | Sum worker medians s | vs reference |", "|---|---:|---:|---:|---:|"]
for m in MODES: L.append(f"| {m} | {mix[m]['pipeline']:.6f} | {mix[m]['pipeline_reduction_vs_reference_percent']:.3f}% | {mix[m]['worker']:.6f} | {mix[m]['worker_reduction_vs_reference_percent']:.3f}% |")
L += ["", "| Job | Baseline → candidate | Pipeline saved % | Worker saved % | Peak MiB saved % |", "|---|---|---:|---:|---:|"]
for j in jobs:
    for b, c, _ in PAIRS:
        v = {x["metric"]: x["saved_percent"] for x in comps if x["job"] == j and x["baseline_mode"] == b and x["candidate_mode"] == c}
        L.append(f"| {j} | {b} → {c} | {v['pipeline_seconds']:.2f}% | {v['worker_wall_seconds']:.2f}% | {v['peak_mib']:.2f}% |")
if "granularity" in res:
    L += ["", f"granularity: {res['granularity']['differential_operation_cases']} differential cases, all outputs equal: {res['granularity']['all_outputs_equal']}", "", "```", json.dumps(res["granularity"]["summary"], indent=1)[:1500], "```"]
open(out + ".md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
