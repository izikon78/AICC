# Processing and AIN prototype branch audit

Reviewed 7 November 2026 for Draft 11. This review reads the assigned branch tips,
their unique experiment reports and preserved raw summaries. The chart data was
recomputed from the three retained 45-worker matrices. Million-event processing
jobs and model runs were not repeated during this review.

## Branch coverage

| Branch tip | Unique content reviewed | How it enters the article |
|---|---|---|
| `origin/research/processing-and-learning-study` `63d012095a6db66a71918cb574fb2c6ceaecf147` | Original study at parent `75de32b757b8bdc43886213ee6b9dd9470717918`, calibration, 45 stress records, 867-parameter cost selector, granularity microbenchmark, exact replication packet | Runtime/memory and selector findings, distinct from native-language learning |
| `origin/claude/processing-study-replication` `2f17cd3825f8e9785c919da2add80d1e35e97b97` | Claude report, interrupted run 001, complete run 002, source/hash identity, exploratory size and checkpoint probes; final tip records owner-authorized upload | Separate Linux remeasurement and separately labeled exploratory probes |
| `origin/research/ain-language-and-study-results` `261ed8ee3e870df1ab51a40aeb1e2a9e32f3d549` | Grok import at parent `9a0fb7fd89e3fe0ce48bc691c3b659bc6c94c6ef`, three-record synthesis, Draft 8, chart data, AIN research plan/complex task | Review/synthesis stage, with the Grok Windows submission retained as source evidence |
| `origin/research/ain-v0-foundation` `dcb47b51245a51a7474949f04c47464d1363d755` | Codex typed mutable-register VM; 69 engineering tests; corrected 27-worker run; six fresh-context edit cells; earlier failed instrument attempt | Executable language foundation and local edit feasibility, with measured VM overhead |
| `origin/claude/ain-v0-plan-execution` `a28436311f152ce65bdb317918c49d75c256bf25` | Separate coarse operator-graph implementation; 47 hand cases, 12 crash cases, 400 differential traces, mutants, type errors, token counts | Separate implementation evidence with audit-discovered gaps |
| `origin/research/native-ain-hypothesis-reassessment` `e86d372701d42b8036eceabc4e4d40326230ef10` | Reassessment at parent `67085ff`; native hypotheses, literature evidence map, full theory/article inventory, independent replay/token recount/adversarial probes; tip aligns title and opening | Explains the transition to native learning and preserves the scope of previous negative findings |

The branch history is cumulative. Repeated files on descendant branches are the
same observations. Claude's alternative AIN prototype branches from `261ed8e`
and has a different implementation from the Codex mutable-register VM.

## Primary source map

- `docs/research/REPLICATION_SYNTHESIS_2026-11-05.md` is the canonical processing
  comparison and states measurement boundaries and exclusions.
- Original source/results are under `experiments/processing_study/results/full-2026-11-05/`.
- Claude's complete record is under
  `experiments/processing_study/results/anthropic-claude-opus-5.5-2026-11-05-trackA-002/`.
  Its earlier interrupted `trackA-001` contains five stress rows and is excluded
  from the complete-matrix comparisons.
- Grok's complete record is under
  `experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/`.
  The original submitted 7z archive has SHA-256
  `7294263b7fb8f7cc1c77c0d508a6ce5ab56271405bfcc5a38f90d7682f3acc9c`.
- For each complete record, `stress-raw.json`, `stress-summary.json`,
  `learning-report.json` and `granularity.json` supply the chart values.
- `agents/claude/processing-study-replication-2026-11-05/AGENT_REPORT.md` and its
  `logs/batch_checkpoint_probe_K250.json` and K300 probe preserve the fake-clock
  checkpoint observations.
- Codex prototype findings are in `experiments/ain_v0/FIRST_EXECUTION_REPORT.md`,
  `results/development-002/validation.json`, `workers.json`, `summary.json`,
  `environment.json` and `agent_pilot/summary.json` at `dcb47b5` and descendants.
- Claude prototype source/report exists at `a284363...:experiments/ain_v0/README.md`.
  The later preserved replay is `docs/research/native-reassessment/claude-review-evidence.json`.

## Processing results suitable for the main article

There are 135 completed million-event worker executions, comprising 45 per
record. They replay the same three public workload shapes and seeds. The three
agent labels describe original or separately submitted execution records on
different hosts. Absolute seconds cannot rank AI-provider speed or authoring skill.

Raw reaggregation verified all 45 unique job/mode/repeat combinations in every
complete record, all three medians per cell and all output signatures within
each workload and across the three records. Output signatures are

| Workload | Groups | Retained events | Severity sum |
|---|---:|---:|---:|
| repeated-shuffled | 49,367 | 651,662 | 1,301,787 |
| diverse-shuffled | 712,972 | 713,608 | 1,427,605 |
| ordered-stream | 49,518 | 681,930 | 1,364,236 |

For an equal-job mixture, the descriptive metric is one minus the sum of
candidate per-job medians divided by the sum of reference per-job medians.

| Recorded host | Ordinary pipeline reduction | AICC pipeline reduction | Ordinary complete-worker reduction | AICC complete-worker reduction |
|---|---:|---:|---:|---:|
| Original Codex Windows 11 | 33.73% | 33.59% | 20.79% | 18.26% |
| Claude Linux | 36.29% | 37.24% | 22.59% | 22.73% |
| Grok Windows 10 | 34.88% | 34.85% | 23.02% | 23.06% |

These ratios show shared optimized processing flows remaining usable through
AICC bindings. The same optimized ordinary implementations produce similar
gains. With three repeats on non-exclusive hosts, direction-varying binding
deltas supply limited evidence about a small additional binding effect.

Pipeline time includes plan selection, applicable feature/inference work, AICC
host setup and processing. Materialized-list generation, model loading and output
hashing are excluded. Ordered generator consumption occurs within every mode's
pipeline. Complete-worker time adds startup/imports, preparation, hashing,
serialization, exit and parent-observed overhead. Peak process memory is a
lifetime high-water value including inputs, outputs, imports and hashing. Linux
RSS and Windows working-set accounting differ.

Within-host ordinary-static pipeline reductions span approximately 26-48%
originally, 22-54% for Claude and 28-53% for Grok. Peak-process reductions span
approximately 20-74%. A percentage across shapes is descriptive and has no
confidence-interval interpretation. Source data retains all medians and repeats.

## Learned selector findings

Each record trained the same NumPy network with architecture 8-32-16-3, 867
parameters. Training/validation/held-out populations have 72/24/24 jobs, with
training sizes 800-14,000 events. The one-million-event stress jobs extrapolate
beyond that size range.

| Record | Label collection | Neural fitting | Selected epoch / 900 | Learned held-out kernel sum | Static held-out kernel sum |
|---|---:|---:|---:|---:|---:|
| Codex | 19.603 s | 0.321 s | 164 | 0.457297 s | 0.453058 s |
| Claude | 12.560 s | 0.155 s | 456 | 0.255129 s | 0.255130 s |
| Grok | 8.224 s | 0.157 s | 900 | 0.200323 s | 0.194538 s |

The learned selector is about 0.94% higher than static originally, practically
tied in Claude's run and about 2.97% higher in Grok's. Claude's tiny difference
of roughly 0.00000019 seconds supplies little practical speed evidence. Held-out
kernel sums exclude feature/inference overhead, which stress pipelines include.
The network learns costs among supplied implementations. It supplies no native
program authoring evidence. The article should retain this unfavorable finding.

## Granularity and cooperative checkpoints

The warm invocation study verified 8,096 integer cases and equal million-value
checksums, with three randomized repetitions of each invocation form.

| Record | Ordinary batch median | AICC batch median | AICC split median | Split/batch ratio |
|---|---:|---:|---:|---:|
| Codex | 0.192520 s | 0.203634 s | 4.615543 s | 22.7x |
| Claude | 0.122542 s | 0.122587 s | 3.533783 s | 28.8x |
| Grok | 0.107619 s | 0.108678 s | 2.686590 s | 24.7x |

The reusable design lesson is to amortize host dispatch with a useful operation
granularity. Ordinary batching benefits too. Claude's additional deterministic
fake-clock probe triggers revocation or caller cancellation during element 250
of 1,000. Per-item checking finishes that element and stops before the next;
100-element chunks permit 50 subsequent elements; a whole batch permits 750.
An expiry boundary at 300 is aligned with a chunk boundary and supplies a
different observation. Cancellation is a caller check in this probe. These are
cooperative in-process counters/exceptions, with no real-time guarantees.

Claude's post-hoc size sweep uses warm processes, list input throughout and
kernel-only timing. It stores neither output-equality checks nor individual
timing samples. Keep it exploratory and outside the primary chart.

## Codex AIN v0 foundation

At `dcb47b5`, 69 engineering methods pass. The corrected run contains 27 workers
on three 20,000-event inputs, three representations and three repeats, totaling
540,000 event visits. All canonical output/effect traces match. The three numeric
AIN execution medians are 20.819, 25.013 and 20.036 seconds, versus Python's
15.991, 20.417 and 13.676. This Python VM implementation has measured AIN overhead
of 22.5-46.5%. Its processing measurements use `tracemalloc` and include in-memory
history/checkpoint retention, with extra preflight checking for IR/AIN.

The first instrumentation attempt preserves four Windows process-handle
reporting failures and an interrupted fifth worker. The corrected run begins a
new hash-frozen result set and excludes the earlier attempt in full.

Six fresh-context collaboration-agent edits pass their frozen judges on the
first submission: one frontier-equality repair and one requested normalization
optimization in Python, IR and numeric AIN. On forty unique events, normalization
calls fall from 40 to 30/20/10 at minimum severity 1/2/3 with equivalent results.
The saved edit changes operation count; its full optimized end-to-end runtime
was unmeasured. Agent billing, exact provider model version and sampling settings
were unavailable. These are six localized same-session edit cases.

The numeric codec and readable IR have the same mutable-register control-flow
graph. Program byte sizes are Python 1,523; compact IR JSON 3,410; numeric AIN 798.
The codebook alone adds 4,076 bytes. Those sizes describe serializations and do
not determine language-model or economic efficiency.

## Claude operator-graph prototype and later review

Claude's `a284363` branch makes the 23-line numeric sketch executable through
21 coarse approved graph operations. It reports 47 hand-derived cases across
three forms, 12 crash/recovery cases, 400 differential traces with zero
differences, six detected mutants, 13/14 matching type-error codes and three
sink checks. The later replay verified all 23 submitted source hashes and
reproduced those recorded results. The prototypes' conformance is composition
agreement around shared primitives.

The independent `o200k_base` recount verifies program counts 298 tokens in both
IR and AIN. Program plus codebook totals are IR 580 and AIN 666. Python's 1,245
program tokens contain more operator logic, so that comparison is unmatched.

Later adversarial review found three concrete gaps. Trailing records after END
in the same run can be accepted. A restored negative group count can survive and
be published. Forced conformance failures and zero detected mutants still return
exit code 0. The prototype therefore needs judge/semantic repairs before serving
as the instrument for a learned-language trial. Its graph operators also hide
the dedupe/grouping logic that a substantial new-authoring task should expose.

## Reassessment and interpretation

The native reassessment indexes 85 records, 60 byte-distinct contents and 25
duplicates, with 50 unique narrative contents fully read and other evidence
classified separately. Its literature map has 21 selected primary sources.
That audit restores trained-native learning as the central hypothesis and keeps
authoring, compilation, inference mechanisms and AICC lifecycle claims separate.

Suitable article conclusion: the project now has executable semantics work,
conformance checks, localized edits, behavior-preserving optimized flows,
cross-host remeasurements and explicit reasons to strengthen judges and learned
controls. The processing and small selector studies establish those engineering
findings. Native learning, broad authoring efficiency and lifecycle savings
require the later appropriately matched tests.

## Chart-ready output

`work/article11-review/processing-native-chart-data.json` contains full-precision
medians, within-host equal-job mixtures, selector data, granularity data and
SHA-256 identities of the four primary JSON files for each record. Every summary
median was recalculated from the raw workers and matched the stored summary.
`recompute_processing_chart_data.py` is the reproducible helper used for this audit.
