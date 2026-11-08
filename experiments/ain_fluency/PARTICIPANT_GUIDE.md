# Current-agent AIN fluency study: participant material

The study compares Python source, readable typed IR, and numeric AIN v0 while
keeping the stream contract and the 23 host capabilities fixed. IR and AIN have
the same control-flow graph semantics. AIN's numbers are ordinary text tokens;
this experiment does not give a model new native tokens or train its weights.

Each scored submission is preceded by a separately measured preparation call.
Preparation supplies the public stream contract, host behavior, complete catalog
metadata and digest, representation grammar, and a small arithmetic loop example.
It asks five fixed comprehension/syntax questions, including decoding a small
program in the assigned representation. The coding call receives that exact
preparation exchange. Its result is graded even if preparation failed; a failed
preparation gate prevents that chain from counting as primary success. All
preparation usage belongs in the cost comparison.

The tasks form a chain:

1. Build the complete controller from the original prose contract. No completed
   controller source is shown in preparation or the build prompt.
2. Change filtering so an otherwise admissible unique event whose timestamp is
   less than `delta` ticks ahead of the current frontier uses threshold
   `min(3, minimum + 1)`; other events use `minimum`. The two chain variants use
   `delta=30` and `delta=75`. ID reservation still occurs before filtering.
3. A fresh participant receives a defective handoff of the changed artifact and
   repairs it against the original contract plus that change.

The model must use no tools, repository access, external information, tests, or
imports. This is an instruction-based restriction, not a security boundary.
Opaque host values may be used only through the supplied catalog. The controller
must express its own source loop, admission decisions, pending-event loop, and
epoch sequencing. Grouping, policy scheduling and transactions are shared host
services, so correctness agreement is not three independent semantic engines.

Preparation returns `{"fluency": {...}}`. A scored answer returns exactly
`{"fluency": {...}, "program": "...", "explanation": "..."}`. `program` is a
string containing the entire source or serialized JSON program. The exact JSON
schemas and questions are exported by `tasks.py`. Python defines `run(host)`;
IR/AIN take one opaque host parameter and return an opaque result.

The evaluator preserves the original predecessor and records structural mutation
metadata. Handoff preparation attempts three interacting defects: admitting
frontier equality incorrectly, filtering before reserving an ID, and draining
only one pending event. It revalidates IR/AIN type correctness after mutation.
It also constructs each single-defect variant from the same predecessor or
fallback source and checks that each independently fails behavioral evaluation
before classifying the compound handoff as three verified defects.
Structural mutation cannot recognize every correct alternative program layout.
When unsupported, it uses a fixed canonical changed artifact and records
`fallback=true`, the reason, and source/output hashes. That repair is diagnostic
only: it cannot count as a genuine predecessor-preserving successful chain.
The same applies to stages continued after an incorrect predecessor.

Canonical controller fallbacks live in evaluator helpers solely to keep failed
chains inspectable. They are never included in preparation or build prompts.
The model-facing repair prompt does not reveal the mutation locations or supply
the correction. No participant trials may begin until the plan is uploaded.
