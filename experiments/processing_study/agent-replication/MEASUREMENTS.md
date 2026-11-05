# Measurement definitions and submission requirements

Read these definitions before reporting savings. Original raw field names are in [stress-raw.json](../results/full-2026-11-05/stress-raw.json); primary summaries are in [stress-summary.json](../results/full-2026-11-05/stress-summary.json).

## Required time, memory, and correctness fields

| Field | Unit | Meaning and boundary |
|---|---|---|
| pipeline_seconds | seconds | Plan selection, applicable feature/inference and host register/bind, and kernel execution. Excludes model load, materialized-list generation, and output digesting. Generator consumption is inside timing for streaming input in every mode. |
| kernel_seconds | seconds | Selected function invocation; for AICC includes binding-call checks, for streaming includes consumption. Do not call it identical isolated arithmetic work across input representations. |
| feature_seconds | seconds | Prefix feature inspection/replay preparation for learned selection |
| selection_seconds | seconds | Static choice or neural inference |
| host_register_bind_seconds | seconds | AICC host construction, capability registration, and initial bind; zero in ordinary modes |
| model_load_seconds | seconds | Policy read plus neural weights read where applicable; separate from pipeline |
| input_preparation_seconds | seconds | Materialized list creation or generator-object creation; generator consumption occurs later |
| digest_seconds | seconds | Output-summary hashing after processing |
| worker_wall_seconds | seconds | Parent-observed child-process duration: startup/imports/preparation/loading/pipeline/digest/serialization/exit and process management overhead |
| cpu_seconds | CPU seconds | Child process CPU time across the pipeline, excluding the same outside-pipeline preparation/load/digest stages |
| process_peak_working_set_bytes | bytes | Process-lifetime peak, including imports, input, output, digest, and allocator state. Convert with 1 MiB = 1,048,576 bytes; not isolated kernel allocations or billed memory. |
| selected_plan | categorical | reference, cached, partitioned, or ordered; retain per-run selection |
| output | structured | Exact groups, events_retained, severity_sum, and SHA-256; all four fields must agree within each matched workload |
| full_validations | count/null | Declared compatibility-fit checks for AICC; not semantic conformance proofs |

All worker modes import NumPy through the common harness. Windows peak memory is PeakWorkingSetSize. Other platforms use process high-water RSS through resource.getrusage, with platform-specific units converted in the implementation. Cross-platform memory values are not identical operating-system accounting; disclose platform and missing measurements rather than inventing zeros.

## Comparisons and formulas

For each `(job, mode)`, report every raw sample plus median, minimum, maximum, repetition count, selected plans, and output status. Use the same statistic and scope in both sides of a comparison.

```text
time_saved_percent = 100 * (baseline_time - candidate_time) / baseline_time
speedup_ratio = baseline_time / candidate_time
memory_reduction_percent = 100 * (baseline_peak_MiB - candidate_peak_MiB) / baseline_peak_MiB
extra_time_percent = 100 * (candidate_time / baseline_time - 1)
```

Negative saved percentages mean a regression; do not clamp them to zero. A speedup of 1.93x is approximately 48% less time, not 93% saved time. Peak-memory reductions are not automatically bill reductions or savings in memory-time product.

| Claim | Baseline | Candidate | Attribution |
|---|---|---|---|
| Algorithm/flow optimization | reference | static | Ordinary optimization available to both approaches |
| AICC binding around optimized code | static | aicc_static | Matched implementation/policy with binding; include noise and setup |
| Learned plan selection | static | learned | Strong static control; include sampling/inference for end-to-end claims |
| AICC binding around learned code | learned | aicc_learned | Same learned choices/model; binding and execution variation |
| Complete delivered path | reference | aicc_static | Combined path; does not isolate an AICC-specific contribution |
| Invocation granularity | aicc_split | aicc_batch | Fixed-policy warm microbenchmark; retain ordinary split/fused/batch controls |

The original approximate 34% processing reduction is `1 - sum(aicc_static job medians)/sum(reference job medians)` for one of each of the three jobs. The analogous complete-worker result is about 18%. This is an explicit equal-job mixture of medians, not a pooled estimator, universal average, statistically significant effect, or cloud bill reduction. For another deployment, declare its workload weights before computing a weighted result. Peak memory should be reported per workload rather than summed as simultaneous RAM savings.

Three repetitions on one non-exclusive host support descriptive ranges only. Do not label the observed minimum–maximum as a confidence interval. Preserve all samples; record host activity, failures, reruns, timeout/correctness failures, and exclusion rules. Summed per-job medians need not equal a median of total runtimes.

## Learning and cost accounting

Report calibration collection and training time separately, count attempted and selected epochs, record split descriptors/seeds and model/policy identities, and distinguish kernel-only held-out estimates from actual end-to-end runs. Track A measures new training; Track B copies historical training metadata and performs no new fit. Record any remeasurement or retuning that occurred after looking at evaluation results.

For economic claims record actual measured AI input/output/cache tokens, billed charges/currency and billing evidence, human review time, agent retries, library construction, validation, registry/dependency maintenance, failures/repair, model calibration/training, hosting, and repeated-use costs. Unknown values remain null or NOT_MEASURED; do not infer billed model tokens from source text length. This study made no model API calls in the benchmark, but the AI coding session's authoring cost was not metered here. No benchmark API call is not the same as free development.

Only when comparable monetary inputs are available:

```text
net_savings = conventional_total_cost - aicc_total_cost
net_savings_percent = 100 * net_savings / conventional_total_cost
conventional_total_cost(N) = conventional_setup + N * conventional_per_job
aicc_total_cost(N) = aicc_setup + N * aicc_per_job
break_even_N = ceiling((aicc_setup - conventional_setup) /
                       (conventional_per_job - aicc_per_job))
```

The break-even expression requires consistent scope/units and a positive per-job advantage; clamp a negative setup difference to an appropriate zero threshold, and handle zero/negative denominators as no positive break-even from reuse under that model. Add maintenance/failure costs explicitly if they vary with use. Do not substitute processing wall time for monetary cost unless an actual applicable billing relationship is recorded. Hypothetical estimates must be labeled assumptions, not observed savings.

## Return these artifacts

Use a unique run ID such as `provider-model-date-trackA-001`, with no secrets or personal account data in filenames. Keep review-only, smoke, frozen replication, local retraining, and improved-code runs separate.

1. `AGENT_REPORT.md`: identity and scope; source/model/policy provenance; exact commands and dates; environment; tests/scenarios; 15-row time/memory comparison; neural and granularity findings; all failures/deviations; supported/rejected/unresolved claims; proposed next experiment. If no code ran, say so prominently.
2. Completed [submission-template.json](submission-template.json), preserving null for unmeasured quantities. Add one `mode_summary` entry for each job/mode and one `comparisons` entry for each stated effect. State that reported source/provider identity is self-reported when it cannot be independently verified.
3. Actual run-config.json, run-metadata.json, stress-raw.json, stress-summary.json, binding-scenarios.json, granularity.json; own unit-test and console logs with exit statuses; calibration/model/policy/learning artifacts, with copied historical artifacts clearly identified for Track B.
4. A SHA-256 manifest covering submitted result files, command logs and any modified source/configuration; source hashes before/after; original artifact references. Include failed-worker.json/failed-output.json and any other recorded failure evidence if produced. Do not alter their contents to create a clean-looking result.
5. A separate branch/patch for changes and a concise comparison against the unchanged baseline. Keep credentials, environment secrets, and private datasets out of public submissions. Each agent's report must be attributable to its actual authoring session; code execution by one host does not establish independent provider participation.

Before submitting, check all matrix combinations, output signatures, counts, measurement units, artifact origin labels, and links. If a resource limit prevented completion, return the partial record with an incomplete status and the exact last successful step. Do not fill missing results with original-study values.
