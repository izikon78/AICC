# Draft protocol: a model that already knows AIN

6 November 2026 · proposed next study, not preregistered or executed

Research direction: Izik Bachar. Prepared by OpenAI Codex from the repository
audit and primary-source review. Numeric resource caps and the actual training
stack remain to be frozen; this file is not approval to incur charges.

## Question and scope

Does learning an executable AIN representation before evaluation reduce measured
resources per correct unseen programming task against competent, equally equipped
conventional-source and typed-IR controls?

Fixed language knowledge lives in trained parameters and the selected vocabulary.
No AIN grammar/codebook primer is supplied at evaluation. All arms receive the
same necessary task/project/private-capability information. A model's fluent
description of AIN is insufficient: it must generate executable, correct programs.

The first study is a bounded program-synthesis/repair experiment, not a frontier
assistant, a general intelligence result, or a proof about every future AIN.

## Gate 0: repair and freeze the measuring instrument

1. Preserve both prototype implementations and all old results unchanged.
2. Fix/port regression cases for records after END in the same run, invalid
   restored-state invariants, and nonzero exits on failed conformance/mutation
   gates. Reconcile outcome/error priority and checkpoint contracts explicitly.
3. Use a common neutral trace format and independently reviewed expectations.
   Check malformed inputs, exact boundaries, effects, capacities, authority,
   cancellation and recovery, not only cross-implementation agreement.
4. Include real asynchronous fixtures and deterministic simulations, labeled
   separately. Persistent storage/isolation remains a separate systems experiment.
5. Freeze source, judges, semantic data generator and splits by hash. Commit
   final-task commitments before tuning; keep judges and final cases outside
   the model's accessible tools. Record design changes and restart evaluation
   under a new version after a material change.

## Gate 1: enough language to author the problem

Use one typed semantic core with expressions, control flow, finite state and
containers, bounded resource operations and explicit effects. Dedupe/grouping and
finalization changes must be expressible in submitted programs. A fixed pipeline
of prewritten whole-task operators is ineligible as the primary authoring test.
Unicode normalization, private scoring and transactional effects may be shared
capabilities if their boundaries and implementations are identical in every arm.

Generate equivalent representations from a common executable AST; keep human-
readable projections outside the native program's inference path. Literal data,
identifiers, references, operands, diagnostics and metadata all count. Do not
hide an unbounded program or constant inside one supposedly free opcode token.

Use at least three compositional workload domains with many structural templates,
such as temporal event processing, versioned state/cache rules and asynchronous
publication/retry workflows. Reserve new templates, compositions and task families
as well as data seeds. Include cases without a suitable reusable capability.

## Gate 2: controls that isolate the mechanism

| Arm | What is learned before evaluation | Role |
|---|---|---|
| Competent conventional source | Source syntax/semantics and equal libraries | Practical baseline |
| Readable typed IR | Same semantic core and equal libraries | Strong structural baseline |
| Numeric spelling of the same IR | Mechanically identical core | Opaque-spelling control |
| AIN candidate | Any genuinely different proposed structure | Native-design hypothesis |

Merge the last two if they coincide. Do not invent independent architecture labels.

Where the experiment includes dedicated instruction tokens, give readable IR
the same semantic-token opportunity. An opaque display glyph and a readable
label that index the same learned vocabulary entry are a renaming control. Use
separate ablations for structural representation, tokenizer/vocabulary and
type/grammar-constrained decoding. Match access to constraints and diagnostics;
conventional code can also benefit from them.

Publish vocabulary size, embedding/output-head parameter counts, total parameters,
active context length and actual work in any auxiliary encoder/decoder. Report
any residual differences rather than declaring approximate controls identical.

## Gate 3: actual native learning

Preferred clean mechanism test: small matched models trained from scratch on
equivalent program tasks. This controls prior familiarity with Python and opaque
AIN. The shared task format must itself be learned in every arm; an untrained
natural-language interface must not become an accidental bottleneck in one arm.

Alternative applied test: matched copies of one pretrained code model, with equal
adaptation opportunities. Label this adaptation, record prior-language exposure
as a limitation, and include the unadapted original. Adaptation is not evidence
of a model pretrained from birth solely in AIN.

A real trainable checkpoint and training-capable tokenizer/embedding interface
are required. Prompting an existing assistant, uploading a language manual or
giving a conversation persistent memory does not perform this experiment.

Report two fairness views where feasible:

- **Equal semantic exposure:** equivalent programs/tasks and presentation counts;
  measure actual training computation instead of equalizing raw token counts.
- **Equal training compute:** fixed total measured training budget, comparable
  tuning opportunities, and reported semantic exposure in each arm.

Different sequence lengths change the data that fits a token budget. Equal raw
tokens are not automatically equal training information. Retain unsuccessful
training runs, data generation/label costs and checkpoint selection work. Use
multiple independently seeded trainings; three is a useful development target,
not a guarantee of adequate statistical power.

## Gate 4: evaluate correct work, not compact strings

Evaluate construction, semantic edits, interacting-defect repair, equivalent-flow
optimization and handoff. An initial fluency gate checks syntax/types, execution
and semantic generalization; it has no per-session fixed-language primer.

Use the same feedback, tool and attempt budgets. Keep every assigned task,
including zero-success cells and timeouts. A successful chain must pass all
required functional/effect/resource cases and its handoff/change stages.

Record separately:

| Ledger | Required observations |
|---|---|
| Model inference | Input/output units, latent/forward steps, prefill/decode time, actual GPU/CPU time, peak memory, candidates and repairs |
| Tools and compilation | Retrieval, checking, diagnostics, parsing, lowering, backend optimization and wall time |
| Emitted program | Equivalent output/effect traces, runtime, memory and resource/cancellation behavior |
| Training/setup | Data and labeling, tokenizer construction, all training/tuning runs, hardware-hours and actual charges where available |
| Lifecycle | Repeated changes, human review, library/contract/binding maintenance, deployment and invalidation |

Cross-tokenizer unit counts and token-level perplexities are descriptive; they
are not shared compute, quality or billing units. A custom vocabulary's unit is
not automatically priced like a hosted API's token. No billing relationship is
assumed where none is measured.

Primary efficiency outcome: total measured inference + tool resources from all
assigned attempts divided by correctly completed chains, reported with success
rate. Also show the correctness–compute frontier. Compilation speed is a separate
sub-outcome; runtime speed and training amortization use separate ledgers.

Use paired comparisons by task and uncertainty that respects shared task family
and training seed. Do not use individual token timings, input rows or reruns of
one program as independent research samples. A development screen estimates
variability; final sample size and decision margins must be fixed before opening
the final set.

## Gate 5: decide whether to continue

Before final evaluation, fill and freeze:

- Model architecture/size, vocabulary design, hardware and training stack.
- Training-data/template splits, semantic exposure and compute ceilings.
- Allowed tuning runs, seeds, attempts and total cash/hardware-hour cap.
- Primary resource metric, practical improvement margin and correctness tolerance.
- Final task count, uncertainty method, stopping rules and artifact release scope.

**Continue** if native AIN passes the correctness gate and beats the strongest
matched control by the declared practical margin under the declared uncertainty
rule. **Pause scaling** if it fails correctness, shows no useful gain within the
budget, or only beats an artificially weak baseline. A wide interval is an
inconclusive pilot, not proof of success or a universal rejection.

If equal-token readable IR matches AIN, report a structural/tokenization result
and reconsider whether a separate opaque language is worth maintaining. Publish
negative findings and failed attempts. Do not keep changing the representation
on the final set until a favorable result appears.

Keep the broad and specific decisions distinct: if both learned AIN and readable
IR improve on conventional source, record support for the shared native-
computational mechanism even when AIN has no additional advantage over IR.

## Later AICC and AI-implementation experiments

First hold library access constant. Later cross trained representation with
ordinary versus AICC binding using identical bodies, contracts and authority
checks. Include discovery, verification and maintenance costs and workloads with
little reuse. Estimate incremental lifecycle break-even only when actual recurring
savings are positive. Expressing the AI's implementation in AIN needs a distinct
compiler/graph/kernel study; identical kernels have no demonstrated source-language
saving. No large commons build or full AI rewrite is required for the first gate.

Sources and rationale: [native feasibility review](../research/NATIVE_AIN_FEASIBILITY_2026-11-05.md).
