# Final experiment evidence

Prepared 8 November 2026 under Izik Bachar's research direction. This index maps
the final article's empirical and conditional claims to primary experiment
records. Reading earlier article drafts is unnecessary. The records preserve
their original source manifests, raw observations and contributor provenance.

## Selected final records

| Evidence | Primary final records | What the evidence supports |
|---|---|---|
| Processing and capability reuse | [Original complete run](../experiments/processing_study/results/full-2026-11-05/), [Claude complete run](../experiments/processing_study/results/anthropic-claude-opus-5.5-2026-11-05-trackA-002/), [Grok complete run](../experiments/processing_study/results/grok-4.7-2026-11-05-trackA-001/) | Equivalent supplied processing flows, within-host runtime/memory observations, binding granularity and cost-model selection |
| Full-format local adaptation baseline | [Frozen report and predictions](../experiments/native_learning_gate/results/rtx3080-2026-11-06/REPORT.md) | Small-model executable learning with the complete IR/AIN envelope, including unfavorable outcomes |
| Compact source and native compilation | [Repaired reference run](../experiments/ain_compiler_gate/results/rtx3080-2026-11-06-reference-v2/REPORT_REFERENCE.md), [final learning run](../experiments/ain_compiler_gate/results/rtx3080-2026-11-06-learning-v2/REPORT.md) | Bounded source-to-native execution, common-backend controls and actual local adapted-model observations |
| Approved-core workflow theory | [Reference report](../experiments/approved_workflow_theory/results/approved-core-2026-11-06/REPORT.md), [specification](../experiments/approved_workflow_theory/REPLICATION_SPEC.md), [semantic traces](../experiments/approved_workflow_theory/trace-inputs.json) | Conditional representation demand for supplied correct build/change/repair/handoff workflows |
| Separate reconstructions | [Codex first counter](../experiments/approved_workflow_theory/validation/codex-independent-2026-11-06/INDEPENDENT_REPORT.md), [Claude first counter](../experiments/approved_workflow_theory/validation/claude-opus-5.5-independent-2026-11-06/INDEPENDENT_REPORT.md) | Exact agreement with the frozen conditional accounting specification |
| Assumption sensitivity | [Claude extension results](../experiments/approved_workflow_theory/validation/claude-opus-5.5-independent-2026-11-06/extension-v1/sensitivity.json) | Dependence on data rendering, known vocabulary and representation-dependent unit cost |

The earlier Round 7/8 exercises, alternative language VMs and prompted-controller
study remain in repository history. They supply no additional result rows in
this final selection. Their exclusion narrows the publication to the final
processing records, matched local screens and approved-core workflow test.

## Processing claims and boundaries

The three complete processing records each contain 45 million-event workers.
They compare three public synthetic workload shapes, five execution modes and
three repetitions. The combined count is 135 completed workers and 135 million
event visits. The modes, repetitions and hosts reuse the same matched dataset
shapes and seeds. Output signatures agree across the retained records.

| Reported contributor and host | Ordinary optimized pipeline reduction | AICC optimized pipeline reduction |
|---|---|---|
| Codex, Windows 11 | 33.73% | 33.59% |
| Claude, Linux | 36.29% | 37.24% |
| Grok, Windows 10 | 34.88% | 34.85% |

Each percentage uses the equal-weight sum of three within-host workload medians
relative to that host's reference flow. Ordinary optimized code and the AICC
path use the same eligible kernels. The reference-to-optimized difference
measures shared implementation improvements. Small differences between binding
and ordinary invocation have limited resolution with three repetitions on
nonexclusive hosts. Absolute cross-host seconds supply no agent-speed ranking.

The raw sources are `stress-raw.json`, `stress-summary.json`,
`learning-report.json` and `granularity.json` in each final run directory.
Ordinary optimized process peaks are about 20–74% below their corresponding
reference peaks across workload/host cells. Peaks include process-lifetime
imports, inputs, outputs and hashing. Linux RSS and Windows peak working set
have different accounting definitions.

The 867-parameter selector's learned versus simple-policy held-out kernel sums
are 0.45729685/0.45305810 seconds for Codex, 0.25512938/0.25512957 for Claude and
0.200323/0.194538 for Grok. Learning was slightly worse or practically tied.
These are kernel-only calibration comparisons. Stress pipeline observations
also charge feature inspection and applicable inference/host work.

The original invocation microbenchmark records about 0.192520 seconds for an
ordinary batch, 0.203634 for an AICC batch and 4.615543 for split AICC calls.
Split/batch ratios are 22.7, 28.8 and 24.7 across the three records. These results
motivate suitable operation granularity. Cooperative cancellation and revocation
require their own checkpoint design and cannot be inferred from warm-call time.

## Local model and compiler claims

Both local screens adapt the pinned Qwen2.5-1.5B pretrained checkpoint with one
seed, rank-16 LoRA and its existing tokenizer. Each condition receives 96
training examples repeated three times, with 288 presentations and 72 updates.
There are twelve development and twelve composition-holdout tasks. All tasks
are affine integer arithmetic, several net offsets repeat and the pretrained
checkpoint has prior Python exposure.

| Format and condition | Correct / 24 assigned | Generated tokens | Generation seconds |
|---|---|---|---|
| Full Python | 24/24 | 417 | 18.726 |
| Full readable IR | 15/24 | 2,007 | 92.962 |
| Full numeric AIN | 7/24 | 2,028 | 95.128 |
| Compact Python | 24/24 | 169 | 7.732 |
| Compact readable IR | 24/24 | 201 | 9.337 |
| Compact numeric AIN | 23/24 | 201 | 9.164 |

Generated totals include unsuccessful predictions and EOS. Full-format IR left
four assigned tasks unattempted at the stage ceiling and AIN left five. They
remain in the denominator. The full AIN development score was 5/12, below its
frozen 9/12 gate even if both development timeouts were granted success.

Full format used a 90-second evaluation-stage ceiling and 320-token output cap.
Compact form used 120 seconds, 64 output tokens, stronger structural constraints
and the same native compiler for every condition. The comparison between screens
describes a development change involving format, constraints, backend and budgets.
Within-screen controls support the direct condition comparison. One seed and
reused arithmetic tasks limit broader inference.

The repaired native reference run compiled 120 programs per condition, checked
each on nine inputs and obtained 3,240 correct native program/input checks.
All 120 matched task triplets emitted identical optimized assembly. Mean full
versus compact canonical target text-token counts were 14.325/4.525 for Python,
92.925/5.325 for IR and 102.325/5.325 for AIN. Canonical counts exclude EOS.
Predictable scaffolding is supplied by the compiler in every condition. LLVM
assembly emission uses CPU computation and consumes no additional generated
model tokens in this pipeline.

The admitted native domain contains at most sixteen add/subtract operations and
input/literal magnitudes at most one million. The few-instruction functions and
Python call overhead offer little runtime benchmarking value. The single compact
AIN failure compiled correctly but used subtraction where addition was required.
Observed compact compilation totals were 0.132/0.141/0.131 seconds for the
Python/IR/AIN candidates, respectively.

## Conditional workflow claims

The workflow test grants fluent optimized representation, approved reusable core,
supplied correct composition and equal cost per counted position. It executes
eighteen chains spanning three fixed five-call templates. Each chain has build,
change, repair and handoff stages. Two data schedules each contain 72 stages and
216 logical requests. Five representation profiles and both schedules produce
2,160 deterministic per-request ledger rows. There are zero model inference
calls in this test.

The shared core contains ten public functions, four explicit for loops, one while
loop and seven comprehensions. Its source is 603 Qwen text tokens. All conditions
receive the approved core without repeated generation of those bodies. The test
charges new operands, predecessor artifacts, incoming memory and repeated tool
history. The modeled vocabulary has 65,536 entries, fifteen-bit payload units and
63 frozen public-interface symbols.

| Schedule | Short-alias Python total | Ideal interface total | Conditional reduction |
|---|---|---|---|
| Business records behind a host handle | 40,614 | 30,858 | 24.02127345% |
| Business records in request context | 76,398 | 66,642 | 12.76996780% |

The resident input/output pairs are 34,686/5,928 for Python and 27,144/3,714 for
the ideal interface. Inspect pairs are 70,470/5,928 and 62,928/3,714. Python totals
combine measured text tokens and fixed assumed framing. Ideal totals combine
modeled semantic units with common text/framing under the equal-cost premise.
Ideal AIN, ideal readable IR and ideal Python tie entry by entry. The result
supports compact learned interfaces and reuse as a conditional mechanism.

Of the resident difference of 9,756 positions, 7,542 arise from repeated history,
artifacts and memory and 2,214 from authored output. Output-only reduction is
37.3%. Real prompt caching, inference work per position, model composition errors,
learning, maintenance, billing and energy require separate instruments and costs.

Claude's separately versioned sensitivity extension yields 21.41%/11.20% fewer
positions when Python memory/observations use compact JSON. Removing the 63
known static symbols makes ideal encoding 40.26%/21.40% larger. This is an extreme
ablation, exposing useful-vocabulary coverage. The 1.619-times break-even ratio
applies to representation-dependent unit cost with common text held fixed.

## Reconstruction and provenance

The separate Codex first counter and Claude first counter each match all 2,160
rows and both schedules' totals. Codex's reconstruction used a fresh context on
the same machine/session. Claude disclosed earlier AIN exposure. Claude's exact
wrapper failed during tokenizer acquisition. Its labeled deviation acquired a
hash-verified tokenizer JSON through another route, passed 21 checks and matched
six deterministic reference outputs. Preserve the failure and deviation records
beside the successful counter. Local seals record local order and hashes.

Contributor identities and remote environments retain their submitters'
self-reported status. These records document independent implementations under a
shared public specification, without provider attestation or an externally
timestamped blind trial. Grok's processing submission is complete. A Grok
approved-core result remains pending and contributes no workflow result row.

## Reproduction dependencies and retained attempts

The primary CPU packet should preserve the approved-core `PACKAGE_MANIFEST.json`,
its frozen source/data closure, pinned requirements, tokenizer assets and license,
and both reconstruction records. A top-level current guide supplies the
standalone theory and directs reference replay versus independent reconstruction.
Expected results and the article are post-seal material for a new independent
counter. Prior exposure must be disclosed when those results were already read.

Native CPU validation needs `ain_compiler_gate` source/tests,
`native_learning_gate/data.py` and the existing `ain_v0/ain/language.py` module.
That module supplies shared IR validation and scalar execution, with standard
library imports. Including it is a code dependency, without importing old VM
performance claims into the final article. Reference token recounting also needs
the frozen tokenizer; native compilation needs the pinned llvmlite package.
Retraining needs the separately pinned GPU framework/model environment and
weights. A CPU packet replay cannot recreate model learning by itself.

The earlier incomplete Claude processing run `trackA-001`, the pre-repair native
reference directory and compact learning's `aborted-v1` are provenance. They
remain preserved where required for an honest all-attempt record, with their
status explicit. Final summary tables use the complete/repaired directories
listed above. No archived unfavorable final condition is dropped.
