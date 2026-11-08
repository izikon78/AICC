"""Fill AICC_Efficiency_Measurement_Template.csv: one row per executed harness trial, plus explicit NOT EXECUTED and
authoring rows. Every model-telemetry field is NOT MEASURED: no model API or billing access existed in this environment."""
import csv, json
cols = list(csv.reader(open("/mnt/user-data/uploads/AICC_Efficiency_Measurement_Template.csv")))[0]
NM = "NOT MEASURED"
trials = json.load(open("harness_trials.json"))
rt = json.load(open("runtime_results.json"))
bind_ms = rt["E1"]["bind() itself (one-time, per capability)"]["median_ns"] / 1e6
base = {c: NM for c in cols}
out = []
for i, t in enumerate(trials, 1):
    r = dict(base)
    r.update({"run_id": f"R9-H{i:03d}", "trial_timestamp_utc": t["ts"], "provider": "none: harness execution, no model call",
              "model_id": "n/a (artefacts authored by Claude Opus 5.5 earlier in this conversation)", "model_configuration": "n/a",
              "arm": t["arm"], "task_id": t["task"], "trial_index": t["trial"], "session_id": "sandbox-2026-11-03 (single session)",
              "warm_or_cold": "cold" if t["trial"] == 1 else "warm (fresh process; OS file cache warm)",
              "success_hidden_tests": f"{t['passed']}/{t['total']}" if t["passed"] is not None else NM,
              "security_pass": f"{t['passed']}/{t['total']}" if t["arm"] == "B-security" else "n/a",
              "registry_amortized_usd": "NOT MEASURED (no curation cost data)", "total_cost_usd": NM,
              "wall_time_ms": f"{t['wall_ms']:.2f}", "model_time_ms": "0 (no model call in this row)", "tool_time_ms": f"{t['wall_ms']:.2f}",
              "bind_time_ms": f"{18 * bind_ms:.3f} (18 binds x median {bind_ms*1000:.1f} us, from E1)" if t["arm"] == "B" else "n/a",
              "verification_time_ms": f"{t['wall_ms']:.2f}", "cpu_time_ms": f"{t['cpu_ms']:.2f}", "peak_rss_mb": f"{t['peak_rss_mb']:.1f}",
              "llm_calls": 0, "tool_calls": 1, "retries": 0, "implementation_source_reads": 0,
              "contract_reads": "n/a at run time (authoring read API_CONTRACTS.md + TASKS.md once)",
              "notes": "Times the harness executing finished code; NOT agent development time. Python startup (~17 ms) dominates.",
              "raw_usage_log_path": "NOT AVAILABLE (no model API)", "test_log_path": "harness_trials.json"})
    out.append(r)
authoring = [("A", "R8-composition-T1..T8", "R8 authoring of submission_A.py in this chat: 20/20 first attempt, 0 retries, 1 black-box probe (filter_by_severity minimum)"),
             ("B", "R8-composition-T1..T8", "R8 authoring of submission_B.py in the SAME chat as A (contaminated): 20/20 first attempt, 0 retries"),
             ("C", "R7-T1-controller", "R7 authoring of controller_submission.sym (contaminated by prior exposure): 6/6 first attempt, 0 retries")]
for j, (arm, task, note) in enumerate(authoring, 1):
    r = dict(base); r.update({"run_id": f"R9-AUTH{j}", "trial_timestamp_utc": "2026-11-03 (earlier rounds; exact time in round logs)", "provider": "Anthropic (claude.ai chat)",
              "model_id": "Claude Opus 5.5", "model_configuration": "claude.ai chat with code sandbox; settings not visible", "arm": arm, "task_id": task,
              "trial_index": 1, "session_id": "one shared chat session (SAME SESSION / CONTAMINATED)", "warm_or_cold": "n/a",
              "success_hidden_tests": "20/20" if arm != "C" else "6/6", "security_pass": "n/a", "retries": 0, "implementation_source_reads": 0,
              "notes": note + ". No API telemetry exposed in this interface.", "raw_usage_log_path": "NOT AVAILABLE", "test_log_path": "round logs (RUN_LOG.txt)"})
    out.append(r)
for arm, note in [("D", "NOT EXECUTED: no symbolic grammar in the packets can express the R8 composition tasks; no AICC-bound symbolic artefact exists"),
                  ("E", "NOT EXECUTED: requires a model trained or adapted on dedicated operation tokens; not available")]:
    r = dict(base); r.update({"run_id": f"R9-{arm}", "arm": arm, "task_id": "n/a", "notes": note, "success_hidden_tests": "NOT EXECUTED"}); out.append(r)
with open("AICC_Efficiency_Measurements_Claude.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerows(out)
print("rows written:", len(out), "| columns:", len(cols))
