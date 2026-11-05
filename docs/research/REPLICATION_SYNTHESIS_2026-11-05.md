# Processing study replication synthesis

Reviewed 5 November 2026 for the AICC project and the proposed AI Native Language research direction. This synthesis compares the original study with two submitted Track A remeasurements. It recalculates recorded data; it does not claim another execution of either submitted million-event matrix.

The repeated positive finding is that substantial, behavior-preserving optimizations can remain usable through the prototype's capability bindings. Within each reported host, optimized ordinary execution saves substantial processing time and process memory, and the AICC path preserves the outputs with similar measured performance. The evidence also identifies a useful capability granularity and a learned selector that needs stronger evaluation. It does not establish financial savings, an AICC-specific throughput advantage, or the effectiveness of an AI-native programming representation.

## Records and provenance

| Record | Recorded environment | Python | Logical CPUs | Complete stress workers | Unit methods reported passing | Binding scenarios passing |
|---|---|---|---:|---:|---:|---:|
| Original Codex study | Windows 11 | 3.12.14 | 12 | 45 | 44 | 9 |
| Claude complete Track A run 002 | Linux | 3.12.3 | 1 | 45 | 44 | 9 |
| Grok Track A run 001 | Windows 10 | 3.12.12 | 16 | 45 | 44 | 9 |

All three records use NumPy 2.3.5, Python Unicode data 15.0.0, the same public workload generator and seeds, three repetitions per job/mode, and one numerical-library thread per fresh sequential stress worker. Hosts were not exclusive or frequency-pinned. The two submissions' provider identities and environments are self-reported: Claude Opus 5.5 attributed to Anthropic and Grok 4.7 attributed to xAI. The archive review checks evidence consistency; it does not authenticate provider identity or independently attest remote execution.

- Original source and results: commit `75de32b757b8bdc43886213ee6b9dd9470717918`, under [full-2026-11-05](../../experiments/processing_study/results/full-2026-11-05/).
- Replication assignment: commit `63d012095a6db66a71918cb574fb2c6ceaecf147`; see the [agent packet](../../experiments/processing_study/agent-replication/README.md).
- Claude submission reviewed at commit `2f17cd3825f8e9785c919da2add80d1e35e97b97`: [report and supplied logs](../../agents/claude/processing-study-replication-2026-11-05/AGENT_REPORT.md), [complete run 002](../../experiments/processing_study/results/anthropic-claude-opus-5.5-2026-11-05-trackA-002/), and [interrupted run 001](../../experiments/processing_study/results/anthropic-claude-opus-5.5-2026-11-05-trackA-001/).
- Grok submission: [report and imported artifacts](../../experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/). Its supplied binary archive is `grok-4.7-2026-11-05-trackA-001.7z`, SHA-256 `7294263b7fb8f7cc1c77c0d508a6ce5ab56271405bfcc5a38f90d7682f3acc9c`. Publication provenance should retain that binary archive identity alongside the imported-file manifest.

The submitted source manifests before and after execution agree with the eleven frozen Python source identities. Grok's archive contains those identity records rather than copies of the source files executed remotely. Its 16 listed asset hashes match the supplied files; the archive contains those assets plus checksums.json. Claude's reviewed manifest contains 45 matching files. These checks detect inconsistency or changed supplied bytes; hashes alone do not prove authorship, experimental independence, or that a particular remote process ran those bytes.

Claude preserves an earlier interrupted attempt with five completed stress workers. Those partial stress rows are excluded from every comparison here. Grok reports an earlier aborted unit-test wrapper launch before calibration, followed by the retained successful test log; no stress rows were excluded in its complete run. The retained Windows unit log includes PowerShell's stderr wrapper formatting and ends with 44 tests and OK; that formatting is not itself a Python test failure.

The three complete matrices contain **135 completed million-event worker executions**, replaying the same three dataset shapes and seeds. They are not 135 independent datasets or independent authoring tasks. The separate [lifecycle pilot](../../experiments/lifecycle-pilot/PROTOCOL.md) proposes **135 linked stage executions** across 27 project chains. The matching number is a coincidence: that proposed trial was not completed by these stress remeasurements.

## Comparisons and measurement boundaries

| Mode | Plan selection | Invocation |
|---|---|---|
| reference | Transparent global-sort reference | Ordinary function |
| static | Best of four simple conditional policies fitted on training measurements | Ordinary function |
| aicc_static | The same static policy | AICC binding |
| learned | Locally trained cost model | Ordinary function |
| aicc_learned | The same local cost model | AICC binding |

The static baseline can choose cached or partitioned processing and optionally substitute ordered streaming on declared ordered input. Every ordinary and AICC path can use the same eligible implementations. Reference-to-static gains therefore concern ordinary algorithm and flow optimization; static-to-aicc_static comparisons concern binding around that same policy.

Pipeline time includes plan selection, applicable feature inspection/inference, AICC host construction and registration/binding, and processing. It excludes model loading, materialized-list generation, and output hashing. Generator consumption is included for the ordered-stream case in every mode. Complete-worker time additionally includes process startup/imports, preparation/loading, hashing, serialization, exit, and parent-observed process overhead.

Peak memory is a process-lifetime high-water value including imports, inputs, outputs, and hashing; it is not isolated kernel allocation. Every mode imports NumPy through the common harness. Linux high-water RSS and Windows peak working set have different operating-system accounting, so absolute cross-host memory values are not interchangeable. MiB means 1,048,576 bytes. See the [measurement specification](../../experiments/processing_study/agent-replication/MEASUREMENTS.md) for exact fields and formulas.

## Equivalent outputs and usable optimized capabilities

Every complete record contains all 45 `(job, mode, repeat)` combinations. All 15 signatures within each workload match, and the three workload signatures also match the original record across submissions. Calibration checks full group equality against the reference for each eligible plan before accepting timing labels. The output counts are:

| Workload | Groups | Retained events | Severity sum |
|---|---:|---:|---:|
| repeated-shuffled | 49,367 | 651,662 | 1,301,787 |
| diverse-shuffled | 712,972 | 713,608 | 1,427,605 |
| ordered-stream | 49,518 | 681,930 | 1,364,236 |

Full SHA-256 output digests, raw rows, tests, and source identities remain in each record. This supports equivalence on the executed cases, not correctness for every possible input. The unchanged [kernel contract](../../experiments/processing_study/KERNEL_CONTRACT.md) preserves validation of discarded rows, first-input duplicate identity, Unicode rules, severity filtering, anchored windows, integer precision, and output order. Ordered execution validates the entire raw stream; exact deduplication and returned groups still require growing state.

### Median pipeline seconds within each host

Each cell is a median of three fresh-process executions. Absolute seconds must not be used to rank AI providers or infer that one authoring agent is faster than another.

| Record | Workload | Reference | Ordinary static | AICC static |
|---|---|---:|---:|---:|
| Original Windows | repeated-shuffled | 6.231 | 3.226 | 3.227 |
| Original Windows | diverse-shuffled | 8.650 | 6.418 | 6.506 |
| Original Windows | ordered-stream | 7.796 | 5.385 | 5.326 |
| Claude Linux | repeated-shuffled | 4.878 | 2.250 | 2.081 |
| Claude Linux | diverse-shuffled | 6.269 | 4.891 | 4.889 |
| Claude Linux | ordered-stream | 5.148 | 3.242 | 3.258 |
| Grok Windows | repeated-shuffled | 2.872 | 1.364 | 1.328 |
| Grok Windows | diverse-shuffled | 3.763 | 2.717 | 2.738 |
| Grok Windows | ordered-stream | 3.268 | 2.368 | 2.385 |

The original ordinary static path reduced pipeline time by approximately 26-48% across these shapes. Claude's within-host reductions were approximately 22-54%; Grok's were approximately 28-53%. These are descriptive ranges across the three workloads, not confidence intervals or population estimates. The same optimized implementations remain usable through AICC.

### Median peak process memory in MiB

| Record | Workload | Reference | Ordinary static | AICC static |
|---|---|---:|---:|---:|
| Original Windows | repeated-shuffled | 814.4 | 561.7 | 561.8 |
| Original Windows | diverse-shuffled | 1060.2 | 845.5 | 846.2 |
| Original Windows | ordered-stream | 515.5 | 135.8 | 135.8 |
| Claude Linux | repeated-shuffled | 815.7 | 561.9 | 561.6 |
| Claude Linux | diverse-shuffled | 1065.1 | 847.2 | 847.1 |
| Claude Linux | ordered-stream | 515.7 | 136.6 | 136.8 |
| Grok Windows | repeated-shuffled | 814.0 | 559.9 | 560.1 |
| Grok Windows | diverse-shuffled | 1057.4 | 844.9 | 843.9 |
| Grok Windows | ordered-stream | 513.7 | 133.7 | 133.5 |

Ordinary optimized reductions are approximately 20-74% within each host. Do not add these per-process peaks as though all jobs ran concurrently, or interpret a peak reduction as measured hosting savings.

## Equal-job mixture and binding setup

For an explicit mixture containing one job of each shape, the following percentages use `100 * (1 - sum(candidate per-job medians) / sum(reference per-job medians))`. A sum of medians is not a separately observed combined run or a pooled estimator. Real deployments need their own declared workload weights.

| Record | Ordinary pipeline saved | AICC pipeline saved | Ordinary complete worker saved | AICC complete worker saved |
|---|---:|---:|---:|---:|
| Original Windows | 33.73% | 33.59% | 20.79% | 18.26% |
| Claude Linux | 36.29% | 37.24% | 22.59% | 22.73% |
| Grok Windows | 34.88% | 34.85% | 23.02% | 23.06% |

These are combined-path improvements relative to the reference, primarily arising from the shared optimized code. They are not an isolated AICC contribution. The ordinary-versus-AICC deltas change by job and metric; three repeats on non-exclusive hosts do not establish a consistent extra binding benefit, prove zero effect, or supply a formal noise threshold.

Explicit median host registration/binding across the 18 AICC workers in each record was 1.672 ms originally, 0.917 ms in Claude's submission, and 0.822 ms in Grok's. These setup measurements show that the prototype can expose a substantial batch operation at small setup cost relative to the measured processing, while preserving the need to evaluate actual lifetime and invocation costs.

## Actual neural training and its boundary

All complete Track A records trained the same 867-parameter NumPy cost model: 8 inputs, hidden layers of 32 and 16 ReLU units, and 3 predicted log-runtime outputs. Each used 72 training, 24 validation, and 24 held-out jobs, with disjoint event seeds and two timed samples per eligible plan. The training range was 800-14,000 events. Normalization and the four-policy static fit use training rows; validation selects the saved epoch.

| Record | Timing-label collection seconds | Neural fitting seconds | Selected epoch of 900 | Held-out learned kernel sum | Held-out static kernel sum | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Original Windows | 19.603 | 0.321 | 164 | 0.457297 s | 0.453058 s | Learned approximately 0.94% higher |
| Claude Linux complete run | 12.560 | 0.155 | 456 | 0.255129 s | 0.255130 s | Practical tie |
| Grok Windows | 8.224 | 0.157 | 900 | 0.200323 s | 0.194538 s | Learned approximately 2.97% higher |

The held-out sums exclude feature inspection and inference; stress pipeline timings include those costs. Claude's difference is about 0.00000019 seconds across the held-out sums and is not evidence of an efficiency advantage. The retrospective best-plan oracle is an evaluation bound, not an executable agent. Collection and fitting costs must be reported separately rather than citing fitting alone as the cost of learning.

The original and Grok models chose partitioning on the million-event ordered stream, while the strongest simple policy chose ordered streaming. Claude's complete model chose ordered streaming. Remeasuring the same descriptor populations can therefore change the learned choice; million-event workloads also extrapolate beyond calibration sizes. Across the complete records, this selector has no reliable demonstrated advantage over the strong static policy. The results neither establish that a better selector is impossible nor identify extrapolation as the sole cause of its failures.

This model selects among supplied implementations. It does not author new algorithms, generate programs, train an LLM, or implement or validate an AI-native programming language. The priority of exploring a working AI Native Language is a research strategy, not a result from this network.

## Capability granularity gives a concrete design constraint

The separate warm in-process microbenchmark checks 8,096 integer inputs and equal million-value checksums, then measures three randomized repetitions of each of six invocation forms. Host setup is excluded. It must not be pooled with fresh-process stress timings.

| Record | Ordinary whole-batch median | AICC whole-batch median | AICC split median | AICC split to batch ratio |
|---|---:|---:|---:|---:|
| Original Windows | 0.192520 s | 0.203634 s | 4.615543 s | 22.7x |
| Claude Linux | 0.122542 s | 0.122587 s | 3.533783 s | 28.8x |
| Grok Windows | 0.107619 s | 0.108678 s | 2.686590 s | 24.7x |

A useful repeated finding is that per-value host dispatch can dominate tiny operations, while a larger bound capability amortizes it. Ordinary batching benefits too, and ordinary/AICC whole-batch paths run identical batch code. These ratios do not establish an exclusive AICC acceleration or AI-token savings.

Batching also changes when authority is checked. Claude supplied a separate deterministic fake-clock probe: a trigger during element 250 leaves 50 subsequent elements in a 100-element chunk or 750 in a whole batch; per-item invocation finishes the triggering element and stops before the next. Cancellation is a caller-level flag, not an independently demonstrated Runtime cancellation feature. The probe records counters/exceptions, not output-equivalence checks or checkpoint timings, and its expiry case is boundary-aligned. These are cooperative in-process observations rather than real-time interruption guarantees. Grok did not inject mid-batch expiry, revocation, or cancellation, so its submission adds granularity timing evidence without replicating that probe.

Claude's separate post-hoc size sweep uses warm processes, list input in every shape, kernel-only timings, and public workload seeds. It saves neither output-equality checks nor individual timing samples. Its results remain exploratory and are not combined with the main fresh-process comparison.

## Publication claims and the next AI Native Language study

The article can emphasize three demonstrated engineering points: equivalent optimized flows on the executed inputs, reuse of those flows through scoped bindings, and the need for appropriate capability granularity. It should retain the selector's unfavorable results as a concrete reason to test stronger calibration and fallback strategies.

A next language experiment must first define executable semantics and implement the representation/compiler or runtime. It can then compare conventional source, a competent typed-AST or action representation, and a proposed native-operation representation with matched model/training resources, tool/library access, task semantics, and correctness criteria. Keep the capability layer constant initially to isolate the representation question. Fresh tasks must require genuinely new logic and changes, not only selection of prewritten functions. Report correctness, repair effort, complete task time, available model billing, and language/training/setup costs. A later factorial experiment can investigate any interaction with AICC.

A guarded selector is another possible follow-up, but a guard that delegates to static outside the training range can avoid a poor choice without adding learned value. Compare unguarded, guarded, and static policies using a fixed practical margin, paired uncertainty, and genuinely new descriptor and event-seed populations. Excluding the three population-generator seeds alone is insufficient; check the full generated seed sets. The current public fixed-seed matrix is a remeasurement fixture, not a hidden evaluation set.

All three complete records leave billed authoring tokens, dollar cost, human review effort, setup/maintenance, failure repair, and full lifecycle economics unmeasured. No model API calls inside the benchmark does not mean free development. Passing in-process binding checks does not establish production isolation, confidentiality, or safe federation. No previously unknown algorithm or trained native-operation language was demonstrated.

## Attribution

Izik Bachar originated the concept and architecture and directs the research. Codex and its same-session coding agents implemented and reviewed the original processing study and prepared this synthesis. The Linux remeasurement and additional exploratory probes are attributed to Claude in its supplied report; the second Windows remeasurement is attributed to Grok in its supplied archive. Those are separately submitted execution records using the same public code and inputs. They are not blinded independent software-authoring trials, and this publication review does not convert self-reported identities into verified provider attestations.
