# Recorded results for agent replication

This is a reading guide to the frozen engineering measurements, not a record of new trials executed while preparing the agent packet.

**Frozen source/results reference:** commit [`75de32b757b8bdc43886213ee6b9dd9470717918`](https://github.com/izikon78/AICC/tree/75de32b757b8bdc43886213ee6b9dd9470717918). Primary run: 5 November 2026. Original artifacts are under [`../results/full-2026-11-05/`](../results/full-2026-11-05/).

The source and metadata hashes are recorded in [run-config.json](../results/full-2026-11-05/run-config.json) and [run-metadata.json](../results/full-2026-11-05/run-metadata.json). The recorded environment used Windows, Python 3.12.14, NumPy 2.3.5, and Python Unicode data 15.0.0. The host had 12 logical CPUs. Stress workers used one numerical-library thread and ran sequentially in fresh child processes; the machine was not exclusive or frequency-pinned.

## Experimental comparisons

- `reference`: transparent ordinary global-sort flow.
- `static`: ordinary invocation of the best of four simple conditional policies, selected on training measurements. The selected policy uses `partitioned` for unordered jobs and `ordered` when input is declared ordered.
- `aicc_static`: the same static policy and kernels through AICC registration/binding.
- `learned`: ordinary invocation after feature inspection and a trained neural cost model chooses a supplied plan.
- `aicc_learned`: the same learned model and kernels through AICC registration/binding.

Every ordinary and AICC arm may use the optimized implementations. Reference-to-static differences measure ordinary algorithm/flow optimization. AICC-to-ordinary comparisons around the same plan concern the measured host setup/invocation path. They do not establish reduced model development cost or a general advantage of a registry.

## Million-event job measurements

There were **45 executions**: three matched synthetic job shapes, five modes, and three repetitions. Each execution processed one million raw event rows. Modes/repetitions reuse the same three seed/shape datasets; these are not 45 million unique real-world events.

Times below are seconds. Each median is calculated over three executions for that job and mode. Pipeline min/max values are observations, not confidence bounds. Peak MiB is the median process-lifetime high-water working set, including imports, inputs, outputs, and digest preparation; it is not isolated kernel allocation.

| Job | Mode | Pipeline median s | Pipeline min-max s | Whole-worker median s | Peak process MiB |
|---|---|---:|---:|---:|---:|
| repeated-shuffled | reference | 6.231347 | 5.743074-7.987534 | 10.667214 | 814.402 |
| repeated-shuffled | static | 3.226232 | 3.162744-3.336701 | 7.366733 | 561.715 |
| repeated-shuffled | aicc_static | 3.227102 | 3.222664-4.406012 | 7.620207 | 561.828 |
| repeated-shuffled | learned | 3.182558 | 2.951274-4.081192 | 7.792786 | 563.672 |
| repeated-shuffled | aicc_learned | 3.625496 | 3.188776-3.663950 | 7.281121 | 563.086 |
| diverse-shuffled | reference | 8.649674 | 8.057585-10.203322 | 19.112862 | 1060.156 |
| diverse-shuffled | static | 6.417942 | 6.271958-7.123092 | 17.015386 | 845.504 |
| diverse-shuffled | aicc_static | 6.506443 | 6.365651-6.772627 | 17.796901 | 846.207 |
| diverse-shuffled | learned | 6.255770 | 6.248137-8.063349 | 17.077512 | 849.512 |
| diverse-shuffled | aicc_learned | 6.609283 | 6.327997-6.890805 | 17.658272 | 847.387 |
| ordered-stream | reference | 7.796453 | 7.261004-8.866050 | 8.753058 | 515.523 |
| ordered-stream | static | 5.385320 | 5.317977-5.907234 | 6.140841 | 135.762 |
| ordered-stream | aicc_static | 5.326457 | 5.158247-5.343197 | 6.079846 | 135.777 |
| ordered-stream | learned | 6.028008 | 5.958981-6.213320 | 6.855133 | 210.996 |
| ordered-stream | aicc_learned | 5.461108 | 5.379821-5.473152 | 6.146808 | 210.742 |

Sources: [stress-raw.json](../results/full-2026-11-05/stress-raw.json), [stress-summary.json](../results/full-2026-11-05/stress-summary.json), and [REPORT.md](../results/full-2026-11-05/REPORT.md).

For materialized-list jobs, pipeline time excludes input-list generation and model loading; those components are recorded separately. For the ordered-stream job, generator consumption occurs inside pipeline time for every mode. Whole-worker wall time includes child startup/imports, preparation, model/policy loading, processing, output hashing, and serialization. All workers import NumPy through the common harness, including reference/static workers.

The ordinary static flow used approximately 31.0%, 20.2%, and 73.7% less peak working set than the reference on the repeated, diverse, and ordered shapes respectively. These are descriptive comparisons of process working sets under this harness, not universal memory guarantees. Ordered processing still retains exact-ID and output state, so it is not constant-memory.

### Equal-job mix: sum of three per-job medians

This calculation gives each of the three measured shapes equal weight. It **sums per-job medians**; it is not a separate observed run, a general workload distribution, a dollar estimate, or an inference-token result.

| Mode | Sum of pipeline medians s | Reduction versus reference | Sum of whole-worker medians s | Reduction versus reference |
|---|---:|---:|---:|---:|
| reference | 22.677474 | baseline | 38.533134 | baseline |
| static | 15.029494 | 33.725% | 30.522960 | 20.788% |
| aicc_static | 15.060003 | 33.590% | 31.496953 | 18.260% |
| learned | 15.466336 | 31.799% | 31.725430 | 17.667% |
| aicc_learned | 15.695887 | 30.786% | 31.086201 | 19.326% |

Calculate each reduction as `100 * (1 - mode_sum / reference_sum)`. Retain the whole-worker column: kernel/pipeline gains do not eliminate startup, generation, loading, and hashing costs. These reductions originate in shared algorithm/flow optimizations and do not isolate an AICC benefit.

Small differences between modes running the same kernel can include scheduling, cache state, and host noise. Do not interpret a small apparent AICC speedup as evidence that the binding accelerates the underlying algorithm. Explicitly measured AICC registration/binding had a median **1.6723 ms** across the AICC stress workers.

## Output checks

Within each shape, all 15 execution records had the same group count, retained-event count, severity sum, and SHA-256 digest of the ordered group output. These checks concern the supplied jobs; they do not prove correctness on every input.

| Shape | Output groups | Retained events | Severity sum | Output SHA-256 |
|---|---:|---:|---:|---|
| repeated-shuffled | 49,367 | 651,662 | 1,301,787 | `b4976982669566fbb1f2493a27d35da50a2d7f71340b82d7e13400ff3e149ead` |
| diverse-shuffled | 712,972 | 713,608 | 1,427,605 | `2c52242c415917ec4ec967b9075f245d3591a6ea19979b867a147e985ef8ec11` |
| ordered-stream | 49,518 | 681,930 | 1,364,236 | `b7122424f5f2709f1d76339a0998084f9e3195492f9e301b8acd242fe043128e` |

The exact normalization, first-input-ID deduplication, severity-filter ordering, anchored-window, and group-order rules are in the [kernel contract](../KERNEL_CONTRACT.md). Optimization must preserve those rules. The ordered plan checks every raw timestamp, including duplicate/filtered rows; a sample cannot prove the full ordering precondition.

## Actual neural training

The locally trained network has **867 parameters**: 8 inputs, ReLU hidden layers of 32 and 16 units, and 3 predicted log-runtime outputs. It uses masked normalized log-runtime squared error and Adam to select among supplied plans. This is actual neural-network training, not LLM fine-tuning, native-operation-token training, or source-code/algorithm invention.

| Item | Recorded value |
|---|---:|
| Training jobs | 72 |
| Validation jobs | 24 |
| Held-out calibration jobs | 24 |
| Calibration sizes | 800-14,000 events |
| Timed calibration samples | Two per eligible plan/job |
| Calibration data collection | 19.602584 s |
| Neural training itself | 0.321241 s |
| Epochs attempted | 900 |
| Validation-selected epoch | 164 |
| Selected validation loss | 0.1913282940 |
| Held-out selected-kernel time, neural | 0.457296850 s |
| Held-out selected-kernel time, simple policy | 0.453058100 s |
| Held-out retrospective oracle time | 0.422301300 s |
| Neural selection matched retrospective oracle | 11/24 jobs |

Feature/target normalization and simple-policy selection use training rows only; epoch selection uses validation loss. Calibration split seeds are disjoint. The test population is evaluated after model selection. The simple policy exhaustively compares four training-only policies: each of `cached`/`partitioned` for unrestricted input, with or without an ordered fast path when declared.

The neural selected-kernel total was **0.9356% higher** than the simple policy on the held-out calibration jobs. This estimate excludes selection overhead; stress pipeline time includes feature inspection and neural inference. The retrospective oracle is a bound using already measured costs, not an available executable agent.

On the million-event ordered job, the learned model chose partitioning while the simple policy chose ordered streaming. The ordinary learned mode used more time and memory. Million-event jobs extrapolate far beyond calibration sizes, and the frozen model was not retuned on their results. Neural selection did not consistently improve the strong conventional policy.

Report data-collection cost separately from training time: the 0.321241-second training figure excludes the 19.602584-second measurement collection. Reusing these weights in another run is a frozen-model remeasurement, not newly executed training; retraining on fresh measurements is a different condition.

Sources: [calibration.json](../results/full-2026-11-05/calibration.json), [learning-report.json](../results/full-2026-11-05/learning-report.json), [cost-network.json](../results/full-2026-11-05/cost-network.json), and [static-policy.json](../results/full-2026-11-05/static-policy.json).

## Binding-state and test checks

The [binding scenario record](../results/full-2026-11-05/binding-scenarios.json) reports **nine passing checks**:

1. Cold binding.
2. Twenty calls reuse one metadata fit check.
3. Repeat binding can reuse an exact compatibility decision.
4. A new receiving host revalidates the JSON record and current receiving requirements.
5. An incompatible receiving task cannot trust the old record.
6. An unrelated capability update leaves a binding usable.
7. A relevant declared dependency change rejects an old alias.
8. Revocation rejects a restored alias.
9. A caller scope assertion does not grant host authority.

Both Runtime objects are in the same Python process. The raw scope string's word `processes` is a wording error, not evidence of a new OS-process or AI-provider handoff. Compatibility counters concern metadata fit, not automatic semantic proofs. The host remains an in-process research mechanism without production authentication, isolation, confidentiality, or complete transitive integrity assurance.

The [test verification record](../results/full-2026-11-05/test-verification.json) records **44 unittest methods passing** in 1.007 seconds, using `python -m unittest discover -s tests -q` from the study directory. These include engineering/adversarial/differential/numerical checks. The count is test methods, not independent model trials, and no new test run is claimed by this packet.

## Operation granularity microbenchmark

This separate exploratory warm-call check uses the same mathematical integer transformation through split, fused, and whole-batch paths. It checked **8,096 operation inputs**, then equal million-value checksums, with three randomized repetitions of each of six modes in the same process.

| Mode | Median s | Observed min-max s |
|---|---:|---:|
| ordinary_split | 0.270652 | 0.268140-0.284820 |
| ordinary_fused | 0.248713 | 0.226743-0.250913 |
| aicc_split | 4.615543 | 4.456708-5.800829 |
| aicc_fused | 2.286713 | 2.273048-2.495043 |
| ordinary_batch | 0.192520 | 0.188192-0.676033 |
| aicc_batch | 0.203634 | 0.186535-0.227837 |

The AICC split-to-batch ratio is about **22.7x** in this specific warm-call microbenchmark. Ordinary batching benefits too; the AICC and ordinary batch paths execute identical batch code. Host setup is excluded here, unlike its measured inclusion in the stress pipelines.

Policy remains fixed in this microbenchmark. A whole batch checks the binding on entry while per-value calls check repeatedly. Equal mathematical outputs do not establish equal mid-batch revocation, expiry, or cancellation responsiveness. A real batching contract must define those observables or add checkpoints.

Source: [granularity.json](../results/full-2026-11-05/granularity.json) and [`tools/processing_granularity.py`](../../../tools/processing_granularity.py).

## Interpretation boundaries for all replications

- Faster processing must be attributed to the relevant kernel, plan selector, or host comparison; shared optimizations are not an exclusive AICC benefit.
- The measurements are synthetic same-session engineering results. No independently blinded model/provider authoring, AI-agent lifecycle economics, or universal behavior/security proof was executed.
- No API-billed tokens, dollar savings, private-code isolation guarantee, new native-language model, or previously unknown algorithm is established.
- Preserve the frozen version-one results. Any changed selector, source, calibration range, workload seeds, repetitions, or measurement scope belongs to a separately identified condition and result directory.

See the [full interpretation](../results/full-2026-11-05/ANALYSIS.md), [integrity audit](../results/full-2026-11-05/audit.json), and [checksum list](../results/full-2026-11-05/checksums.json) for the original record.
