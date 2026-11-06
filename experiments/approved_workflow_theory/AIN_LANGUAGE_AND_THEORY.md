# AIN language theory and the notation used by this test

Concept and research direction by Izik Bachar. This guide prepares an agent with
no AIN background to understand the approved-core theory experiment.

The primary article source is
[Draft 8, PDF pages 1-4](https://github.com/izikon78/AICC/blob/4df5ab0f54b2c2951c21e62bc089707bc495646d/docs/article/AICC_Article_Draft_8_Review.pdf).
Page 4 shows the numeric admission-program sketch, including a function reference,
operation calls, conditional exits, indexed fields and return values. The
[Markdown companion](https://github.com/izikon78/AICC/blob/4df5ab0f54b2c2951c21e62bc089707bc495646d/docs/article/AICC_Article_Draft_8.md#admission-order-that-an-optimizer-must-preserve)
contains the same syntax example. Read that source before the accounting model.

## The proposed language

AIN means AI Native Language. The proposal is a machine-oriented executable
representation that an agent learns before performing tasks. Short learned
references identify operations, approved functions and reusable computation.
Operands supply arguments, values, references and new task information. A
deterministic compiler or runtime gives the representation its execution meaning.

A function reference can invoke an approved implementation containing many
instructions, other functions and loops. The agent can compose those references,
change arguments, patch a composition, store working information and hand work
to another agent. Human-readable names and source can be rendered for review.
The reference's short spelling and its tokenization are separate design choices.

AICC means AI Computational Commons. It is the related capability-reuse
architecture. This experiment grants every condition the same approved functions.
It studies the resource demand of the representations used to compose them.

## Premise of the current theory test

Izik requested that the optimized short language, fluent use of it and approved
core code be treated as already available. The experiment models that condition
through an abstract approved-call interface with fixed counting rules. It also
supplies correct composition plans so representation demand can be isolated.

The future optimized language's complete concrete grammar remains abstract in
this experiment. Its assumed interface is specified precisely enough to recreate
the accounting and execute the supplied semantic cases. The concrete AIN v0
prototype has a separate grammar, linked below.

## Abstract program structure

The following describes semantic structure for the replication. It is metanotation
for the accounting model. A future optimized implementation can choose its
display characters and physical encoding.

```text
program          = bounded ordered sequence of approved calls
approved call    = learned function reference + ordered typed arguments
argument         = public reference | integer | new literal | structured value
agent interaction = working record | artifact write/patch | check | memory | submit
```

The approved function's contract supplies argument order, operand types and
execution meaning. Every new argument and literal carries an explicit charge.
The abstract sequence has a known input and passes each operation's output to
the next approved operation. Function bodies are already present in the core.

For example, the fixture's semantic description of a filtering operation is

```json
{"op":"filter_gte","args":{"field":"severity","value":3}}
```

This JSON is a human-inspectable description of the call. In the ideal accounting
model, this call requires one learned operation unit, one public field-reference
unit and one small-integer operand unit. A one-call program also has one
program-length unit. The new threshold value therefore contributes to the cost.
The same semantic interface is available to the ideal IR and Python controls.

The five-call event workflow keeps event records, reserves the first occurrence
of each identifier, filters by severity and timestamp, and groups values. Its
operations and arguments are supplied in `trace-inputs.json`. The approved
function bodies perform their filtering, traversal and aggregation loops.

## Functions, for/while loops and changes

The current core has ten approved public functions. Their implementations contain
four explicit for loops, a bounded while retry loop and seven comprehensions.
The agent-authored programs compose those functions. A change patches one
argument, repair patches one injected defect, and handoff uses the saved artifact
and memory. This exercises the premise that approved function and loop bodies
can be reused through short references.

General newly authored control flow belongs to the broader language theory.
The older prototype expresses branches and loops through typed registers,
basic blocks and jump/branch terminators. Its concrete grammar and execution
rules are published in the prototype document below.

## Read the appropriate specification

| Document | What it specifies |
|---|---|
| [REPLICATION_SPEC.md](REPLICATION_SPEC.md) | Complete abstract interface, operand rules, serialization and per-request accounting for this theory test |
| [AIN v0 language specification](../ain_v0/LANGUAGE.md) | Implemented prototype grammar, numeric encoding, types, functions/catalog calls, branches, loops and validation |
| [Canonical native hypotheses](../../docs/ain/NATIVE_HYPOTHESES.md) | The claims about learned authoring, compilation, inference mechanisms and AICC reuse |
| [Complex workflow and symbolic sketch](../../docs/ain/COMPLEX_TASK.md) | A larger semantic workload and an illustrative machine-facing notation |
| [Agent start guide](AGENT_START_HERE.md) | Independent reconstruction and exact-rerun procedure |

For this package, reproduce the frozen abstract-interface accounting first.
Preserve any proposed syntax or encoding changes in a separate version. The
article's conditional results depend on the published counting assumptions,
perfect composition and equal cost per counted position. Actual trained-agent
speed and resource use require a separately instrumented model experiment.
