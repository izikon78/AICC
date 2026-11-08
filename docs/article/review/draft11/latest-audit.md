# Latest experiment audit for Draft 11

Reviewed 7 November 2026. Read-only review of the four assigned remote branch
tips and two local RTX 3080 engineering experiments. Research direction and
concept belong to Izik Bachar. This audit uses the saved code, raw records,
reported provenance and independently recomputed aggregates. It performs no new
model inference, training or large workload replay.

## Branch coverage

| Branch | Reviewed tip | Evidence covered |
|---|---|---|
| research/ain-fluency-current-agents | 60ba43bad3588815ecebe1504c35f2dfe7f0e97d | Completed prompted controller study, continuation, usage analysis and raw stage records |
| research/approved-core-replication | 2b6541a24ef71dcd4390f526042ebf131501fc51 | Frozen conditional workflow suite, Codex reconstruction, specification and raw ledgers |
| claude/approved-core-replication | e9a8a5111717a57427fac50605cf5cbe0c86b316 | Claude first reconstruction, failed exact acquisition, labelled deviation and sensitivity extension |
| research/approved-core-article-draft-10 | 53cb324e70ac801e9636f7fa0972a82fe99ae511 | Consolidated Draft 10 evidence, numeric article projection, downloadable Grok packet and publication validation |

Local directories `experiments/native_learning_gate` and
`experiments/ain_compiler_gate` are saved same-session engineering experiments.
They were untracked at audit start. Their results are described below and should
be published with their source and raw records before article links point at them.

The latest branch contains Codex and Claude approved-core reconstructions. The
Grok approved-core result is pending. The downloadable Grok packet and its local
packaging smoke test are preparation evidence. Existing Grok processing-study
results concern a separate, earlier workload experiment.

## Prompted controller study

Primary records are `experiments/ain_fluency/RESULTS_OVERVIEW.md`, the amended
continuation's `summary.json`, eighteen `stages/*/stage.json` files and
`analysis/known-usage.json` under
`results/current-agent-2026-11-06-continuation/`.

I reconstructed request counts, known usage and correctness directly from every
saved stage record. There are eighteen scored artifacts across Python, readable
IR and numeric AIN, with two build/change/repair chains per representation.
Every artifact passed all fifty-five named execution cases. This is 990 repeated
artifact-case executions. It is appropriate to write “18/18 artifacts each
passed 55 execution cases.” The cases and variants are related observations.

| Representation | Artifacts passing | Requests | Known input | Known output | Usage-missing requests |
|---|---|---|---|---|---|
| Python | 6/6 | 12 | 250,087 | 7,340 | 0 |
| Readable IR | 6/6 | 12 | 282,986 | 15,552 | 0 |
| Numeric AIN | 6/6 | 14 | 278,969 | 16,081 | 2 |

There were eighteen preparation calls and eighteen metered task calls, plus two
account-quota rejections with missing counters. Together they are thirty-eight
requests and 851,015 known input/output tokens. The same signed-in model was
reported as `gpt-6.1-sol` at ultra effort. The record is an amended continuation
after an account interruption. Copied earlier observations in that continuation
must be counted once.

The genuine complete-chain counts are Python 2/2, IR 2/2 and AIN 1/2. The other
AIN chain used a labelled canonical repair fallback because the fault injector
misinterpreted valid register reuse. All final programs were correct. The
injector's static name matching created the excluded handoff.

AIN's complete all-attempt cost is undefined because two request counters are
unknown. Under illustrative all-input 1/output 5 weights, the known lower bound
is 359,374 against Python 286,787 and IR 360,746. That permits at most 0.4%
AIN saving versus IR and is already 25.3% above Python. These quantities are
descriptive hypothetical resource bounds. Keep provider invoices, native-trained
efficiency and the fault-injector outcome separate from that calculation.

## Full-format local adaptation screen

Primary source is `experiments/native_learning_gate/results/rtx3080-2026-11-06/`.
I rebuilt every before/after count from raw predictions, checked those aggregates
against arm results and verified every frozen source hash.

The checkpoint is Qwen2.5-1.5B at pinned revision
`8faed761d45a263340a0528343f099c05c9a4323`, adapted sequentially with rank-16
LoRA and BF16 on the RTX 3080 10 GB host. The dataset has 96 training examples,
12 development examples with new constants and 12 held-out operation
compositions. It uses one seed and three passes, giving 288 presentations and
72 updates per representation. The tasks are affine integer arithmetic, and
some held-out compositions share the same final offset. The base already has
prior Python familiarity.

| Adapted representation | Development | Held-out compositions | Total correct | Attempted | Stage timeouts | Output tokens | Generation seconds |
|---|---|---|---|---|---|---|---|
| Python | 12/12 | 12/12 | 24/24 | 24 | 0 | 417 | 18.726 |
| IR | 10/12 | 5/12 | 15/24 | 20 | 4 | 2,007 | 92.962 |
| AIN | 5/12 | 2/12 | 7/24 | 19 | 5 | 2,028 | 95.128 |

The frozen stage cap is ninety seconds, checked between predictions. A final
generation can take the measured total beyond that cap. Timeouts stay in the
assigned denominator. AIN misses the 9/12 development threshold even if its two
unattempted development examples are granted success. Training completed within
the cap for every arm, taking approximately 69, 70 and 72 seconds. Peak PyTorch
reserved memory is about 3.4 GiB, excluding desktop use and other processes.

This screen establishes actual local adaptation feasibility and a limited
negative correctness result for the chosen full JSON envelope. It is a narrow
adaptation of a text model using its existing tokenizer. It provides development
evidence about that interface and training configuration.

## Compact-source and native compiler screen

Primary sources are `experiments/ain_compiler_gate/results/` folders
`rtx3080-2026-11-06-reference-v2` and
`rtx3080-2026-11-06-learning-v2`. I recomputed reference token sums from all 360
records, recomputed prediction aggregates from all arm files and verified every
frozen source hash.

All three frontends supply the same implicit input/return, type/register
scaffolding and optimized LLVM backend. The supported source subset is bounded
add/subtract accumulator operations. Exact signed-64-bit lowering is protected
by the declared input, literal and operation-count bounds. Actual machine code
was emitted through MCJIT and executed.

| Canonical reference form | Mean full target tokens | Mean compact target tokens | Reduction |
|---|---|---|---|
| Python | 14.325 | 4.525 | 68.4% |
| IR | 92.925 | 5.325 | 94.3% |
| AIN | 102.325 | 5.325 | 94.8% |

All 120 reference programs in each arm passed nine native input cases. The 360
programs account for 3,240 native execution checks. Assembly matches across the
three source forms for all 120 paired tasks. LLVM generates assembly through CPU
computation. Its printed assembly consumes zero additional LLM output tokens.

| Adapted representation | Correct | Output tokens | Generation seconds | Compilation seconds |
|---|---|---|---|---|
| Python | 24/24 | 169 | 7.732 | 0.132 |
| IR | 24/24 | 201 | 9.337 | 0.141 |
| AIN | 23/24 | 201 | 9.164 | 0.131 |

Every adapted task was attempted, with zero stage timeouts or output-cap hits.
AIN's single failure is an incorrect subtraction opcode in a mixed composition.
It parses and compiles correctly but returns the wrong value. All arms received
288 presentations and 72 updates, using the same underlying checkpoint.

The compact screen reuses the earlier development and holdout tasks. It changes
representation and constraints, and its stage cap is 120 seconds with 64 maximum
output positions. The older screen used ninety seconds and 320 output positions.
Its higher correctness is an engineering comparison across changed conditions.
Within the compact run, every arm has matching budgets and the same compiler.

One initial attempt was stopped before adaptation to repair a parser boundary
parity defect. Its eight saved baseline generations consumed 271 input tokens,
412 output tokens and 19.328 generation seconds. The code and report retain that
attempt. The original SDPA warning is retained. The pinned checkpoint's
`use_sliding_window` configuration is false.

## Approved-core conditional workflow theory test

The frozen records live under
`experiments/approved_workflow_theory/results/approved-core-2026-11-06/`.
I reconstructed every aggregate from the raw per-request ledger. The sums match
`totals.json` exactly. There are three five-call templates with six variants
each, eighteen four-stage chains and seventy-two stages per data schedule.
Two schedules produce 144 saved stage records and 2,160 ledger rows across five
representation profiles. There are 216 logical requests per schedule and zero
actual model inference calls.

Premises grant fluent representation, approved core, perfect composition and
equal cost per counted position. Python text tokens and ideal semantic units
are different measured/modelled quantities combined under that assumption.
All arms share the same ten approved functions with actual for/while loops.
New requirements, operands, memory, predecessor artifacts and reprocessed tool
history count. The fixed capacity is 65,536 vocabulary entries, including
fifteen-bit literal payloads and sixty-three frozen interface symbols.

| Schedule | Short-alias Python input/output | Ideal input/output | Total reduction |
|---|---|---|---|
| Resident data | 34,686 / 5,928 | 27,144 / 3,714 | 24.02127345% |
| Inspect data | 70,470 / 5,928 | 62,928 / 3,714 | 12.76996780% |

Total resident counts are 40,614 versus 30,858. Inspect counts are 76,398 versus
66,642. Output-only reduction is about 37.3%. Ideal AIN, ideal IR and ideal
Python match entry by entry under equal semantic-interface opportunity.

These are conditional representation/accounting results. Actual neural
computation, latency, billing, learning costs and success-adjusted unseen-task
performance remain further measurements. The six variants per template and
repeated schedules are related accounting cases.

## Separate-agent reconstructions and sensitivity

Codex's archived separate-agent counter was written in a fresh context on the
same Windows machine/session. Its first independent ledger matched all 2,160
rows. The exact offline reference wrapper also matched with all six assets
verified and twenty tests on its earlier package revision.

Claude's self-reported Opus 5.5 submission at `e9a8a51` supplies a first independent
counter whose raw ledgers and totals I compared directly with the reference.
Every row and aggregate matches. Its exact wrapper failed tokenizer acquisition.
A separately labelled deviation used a byte-identical, hash-verified
`tokenizer.json` from another acquisition route. The remaining five expected
assets were absent and a differently hashed tokenizer-config file was used in
the deviation. The direct reference pipeline then passed twenty-one tests and
matched six reference outputs. Preserve the failed exact attempt and the
deviation label. Claude disclosed earlier AIN work in the same conversation.

The reported model identities and local precomparison seals are provenance
records. Neither is external provider attestation or a third-party timestamp.
The Codex reference implementation is separate from its reconstruction and
should receive its own row rather than inflate the independent-agent count.

I recomputed Claude's sensitivity percentages directly from its saved JSON.

| Sensitivity | Resident | Inspect |
|---|---|---|
| Python memory/observations rendered as compact JSON | 21.41% fewer ideal positions | 11.20% fewer |
| Ideal vocabulary without the 63 static symbols | 40.26% more ideal positions | 21.40% more |
| Break-even unit-cost ratio, common text held fixed | 1.619 times | 1.619 times |

The break-even ratio applies only to representation-dependent units. It differs
from the ratio of entire total-position columns. The no-static-symbol case is
an extreme ablation that exposes the need for useful vocabulary coverage.
Its outcome supplies no measured forecast for a future trained vocabulary.

## Draft 10 display and Grok packet

Commit `1bab065771b6b15101fb9c0300f8dee948cc47d6` adds an article-only numeric JSON
projection of saved semantic plans. It assigns local operation IDs by catalog
order and symbol IDs by the frozen symbol list. Extra type tags support lossless
display. The 144 episode projections round-trip and execute correctly in saved
qualification records. Its JSON token count is separate from the frozen
ideal-unit accounting. Draft 8's @/!/conditional/return sketch and Draft 10's
numeric display are different illustrative presentations. Use one article
notation consistently and label its approved operation catalog and execution
obligations.

Commit `53cb324e70ac801e9636f7fa0972a82fe99ae511` publishes the downloadable packet
and its validation. The local packaging test verified 130 payload files, 59
frozen-package hashes and six tokenizer assets, then passed twenty-one checks
and six reference comparisons from a fresh extracted environment. That is a
packet smoke test. Grok's approved-core reconstruction remains pending.

## Chart recommendations and data artifact

`latest-chart-data.json` contains raw-derived numeric inputs with paths,
configuration and source-hash checks. Useful figures are

1. Correctness across full-envelope and compact adaptation screens, with the
   changed-interface/budget qualification in the caption.
2. Within-compact-run generation time and output tokens alongside success counts.
3. Conditional resident/inspect position demand, explicitly labelled modeled
   ideal units versus measured text tokens under equal-position cost.
4. Separate-agent reconstruction agreement with Grok displayed as pending.
5. Vocabulary and Python-data-rendering sensitivity, carrying the ablation label.

Use separate figures for observed local model measurements and conditional
theory accounting. Their units, correctness assumptions and repeated-task
structure differ. The current prompted controller study supports no complete
all-attempt AIN cost estimate.
