# Native AIN: the research thesis and three hypotheses

6 November 2026 · revised research direction under Izik Bachar

This is the current interpretation of the originator's goal. Historical drafts,
reviewer opinions and measured artifacts remain records of their own conditions.
This document changes the research priority; it does not retroactively change
what the earlier experiments tested.

## Central thesis

After learning AIN during training, a model may require less total work to
produce and maintain correct programs because its executable representation is
designed for machine generation and manipulation. AICC may add a separate benefit
by reusing established, authorized computation across projects.

**Native knowledge means the fixed language is learned before evaluation.**
Its grammar and established core operations do not need to be retaught in every
prompt. New task requirements, project schemas, unknown libraries and private
interfaces can still require context. Training and vocabulary construction have
costs that belong in the appropriate training/lifecycle ledger.

Human readability is an optional projection. Opaque symbols are a permissible
design choice, not an efficiency mechanism by themselves. A conventional typed
IR with equally good tokens and tools is a required control.

## N1: writing and compilation

**N1a, model authoring:** matched trained models using AIN can construct, edit,
repair or hand off correct unseen programs with lower total inference/tool work
than the strongest matched conventional-source or readable-IR control.

Measure success, all decoding/latent steps, candidate samples, retries, checking,
tool calls, latency, memory and actual applicable compute/billing. A short failed
program is not a successful inexpensive task. Costs of failures count.

**N1b, compilation:** AIN can reduce parsing, checking or lowering work for a
specified compiler pipeline. Measure it separately on equivalent programs with
the same target optimizations, then report its share of the entire task cost.
Compiler gains cannot be inferred from output length or substituted for model
generation savings. Equivalent compiler IR can make frontend differences small.

Status: technically plausible; neither N1a nor N1b is established by this project.
The current numeric interpreter's runtime overhead is a prototype result, not a
measurement of a trained model's authoring or a fair optimizing-compiler study.

There are two levels of conclusion. If trained computational AIN and readable IR
both beat competent conventional source, that supports the broader value of a
learned computational representation. If they tie each other, it does not establish
an advantage specific to AIN's separate design or opaque spelling. The research
could then adopt the successful shared structure without maintaining a redundant
language. These are different decisions, not a universal rejection from an IR tie.

## N2: architecture-aligned representation and less inference work

The originator's term "less traveling" is interpreted as **less measured work
to reach a correct program**: fewer generation/latent steps, less repeated
context processing, fewer invalid syntax/type choices, fewer repairs, or better
data movement and execution layout where a systems mechanism is actually built.

A trained typed/structural representation might reduce uncertainty and invalid
choices. For a conventional fixed-depth dense Transformer, a different opcode
still uses the layer stack for each forward step. Shorter spelling does not
establish a shorter neural path. Latent-state reasoning, sparse/adaptive depth
and instruction-token generation are different mechanisms and need separate
controls. This distinction follows from the [Transformer architecture](https://arxiv.org/html/1706.03762v7).

Test a correctness–compute frontier, with the same tools and parameter/training
accounting. Give readable IR equivalent semantic-token and constrained-decoding
opportunities. If it matches AIN, attribute the result to structure, tokenization
or checking rather than to opaque naming.

Status: plausible as a resource/reliability hypothesis. Literal shorter neural
"travel" from machine-like syntax is not an established mechanism.

## N3: AI systems implemented in AIN, with AICC reuse

Separate the long-term claims:

- **AI implementation:** expressing an AI's source or computation graph in AIN
  could expose better optimization or reduce development effort. Execution gains
  require changed compiled computation, kernels, scheduling or memory behavior.
  The same graph and kernels have no identified saving from the source spelling.
- **AICC lifecycle reuse:** governed discovery, compatibility evidence and scoped
  bindings may reduce repeated implementation and verification work. Compare
  with competent ordinary libraries using the same bodies and semantic evidence.
- **Combined effect:** trained AIN plus AICC may have an interaction beyond either
  contribution. A factorial comparison is needed; additivity is not assumed.

| | Ordinary shared-library binding | AICC governed discovery/binding |
|---|---|---|
| Trained conventional source / IR | Control | AICC contribution |
| Trained AIN | AIN contribution | Joint contribution and interaction |

Model weights/activations, model-generated programs, AI implementation source and
agent-to-agent latent messages are distinct objects. Their results are not
interchangeable evidence. [OpenXLA](https://openxla.org/xla/architecture) already
illustrates machine-oriented graph compilation; [DreamCoder](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf)
provides prior work on learned executable libraries.

Status: a conditional systems/economics hypothesis. This project has not measured
native-trained AIN, AICC lifecycle savings or an optimized AI implementation in AIN.

## What the existing records mean

- Existing processing studies measure algorithm/runtime/binding behavior. The
  867-parameter selector predicts supplied plan costs; it is not an AIN model.
- The Codex AIN prototype supplies program-level control flow, real bounded
  asynchronous fixtures, 69 passing engineering methods, 27 matched processing
  workers and six one-submission editing cells. These are public development
  cases on a cooperative shared host, without trained AIN weights.
- Claude's separate operator-graph prototype adds linear stream typing, mutation
  tests and proposed semantics. Its 47 hand cases, 12 recovery cases and 400
  differential traces reproduce. Review also found trailing-END, checkpoint-
  validation and failing-exit-status gaps; passing shared tests is not a proof.
- Claude's 298-vs-298 program-token and 666-vs-580 program-plus-codebook counts
  describe one spelling under `o200k_base`. They do not test a trained native
  vocabulary, and are not recurring primer costs in the native condition.
- Earlier contributors' "validated" or "rejected" labels are opinions unless
  supported by an experiment that actually matches the hypothesis and controls.

## Next gate

The primary next experiment is **matched native learning**, with a frozen
executable core and independently reviewed judge as prerequisites. More
fixed-model spelling comparisons are optional diagnostics, not a required route
to N1/N2. See the [feasibility reassessment](../research/NATIVE_AIN_FEASIBILITY_2026-11-05.md)
and [draft native-training protocol](TRAINED_NATIVE_PILOT_PROTOCOL.md).

No paid training/API run, model purchase or GPU rental is started or authorized
by these documents. The protocol must become concrete and resource-bounded
before execution. An experiment is intended to find out whether the hypothesis
survives; the article cannot assume the desired answer.
