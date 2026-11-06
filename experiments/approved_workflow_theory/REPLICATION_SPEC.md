# Independent accounting specification, version 1

Read this specification and `trace-inputs.json` before implementing an independent
counter. Preserve your own first ledger before consulting the reference totals.
The supplied traces are predefined correct-agent actions under the experiment's
premises. Independent reconstruction concerns encoding, context accounting and
execution of the approved components. Model training is a separate experiment.

## Inputs and output contract

`trace-inputs.json` supplies the frozen configuration, approved core source,
fixture tasks and semantic episodes. It contains no reference ledgers or aggregate
results. Preserve list order and dictionary insertion order when rendering Python
or common input text. JSON object key order has no effect on ideal-unit sums.

Each episode identifies `chain`, `domain`, `stage` and `schedule`. It supplies
three action batches, their host observations, the common request input, the
predecessor artifact, incoming memory and final artifact. Shared approved functions
may be reused from `workloads.py`. Keep the accounting and renderer independent
of `accounting.py`, `run.py` and `report.py`.

Write `episodes.json` containing the episodes in supplied order, with a `ledger`
list added to every episode. Write `totals.json` with `resident` and `inspect`
objects, each containing these profiles in order

```text
python, python_aliases, ideal_ain, ideal_ir, ideal_python
```

Within each episode, ledger rows are ordered by profile, then turns 1, 2 and 3.
Each profile uses the same actions and semantics. The two data schedules replay
the same workflow tasks with different common input exposure. Absolute position
counts combine common text tokens and representation units under an assumed
equal cost per position.

After freezing your outputs and implementation hash, compare with

```text
python experiments/approved_workflow_theory/reproduce.py --compare PATH_TO_YOUR_OUTPUT
```

The comparator checks exact totals and every per-request ledger. It writes
`comparison.json` and returns exit code 1 for a mismatch. Explain the first
disagreement and preserve your initial result before correcting your implementation.

## Text-token boundary

Use `Qwen/Qwen2.5-1.5B` tokenizer revision
`8faed761d45a263340a0528343f099c05c9a4323`. Exact package pins are in
`requirements-reproduce.txt` and tokenizer asset hashes in
`tokenizer-files.sha256.json`. Call encoding with `add_special_tokens=False`.
Only tokenizer files are required. Python 3.12 is the reference environment.

Common input text is exactly Python's

```python
json.dumps(episode["common_input"], separators=(",", ":"))
```

Default `ensure_ascii=True` applies. Each request includes this full common text
again. Resident input supplies requirements, parameters, schema and a data handle.
Inspect input additionally contains business records. Host data remaining behind
a handle has zero model-context positions until exposed by a tool.

## Python rendering

Render each pipeline from its ordered calls. Start expression `r`. For each call,
look up argument names in `config.catalog_schema[op]` and take their values in
that order. Replace expression with

```text
FUNCTION_NAME(previous_expression,repr(argument_1),repr(argument_2),...)
```

There are no spaces after inserted commas. Use Python 3.12 `repr` for operand
values, including list spacing and booleans. The final artifact is `lambda r:`
followed immediately by the expression. Descriptive Python uses the approved
operation name. Short-alias Python uses `config.aliases[name]`.

Render an action batch by joining statements with `;`, with no inserted spaces.
A write action is `write(PROGRAM)` with the rendered lambda as its argument.
Every other action uses its approved argument order and Python `repr` values.
Short-alias mode applies aliases to both pipeline functions and host tools.

Render incoming memory and host observations with Python `repr`. Empty incoming
memory and an empty predecessor artifact each have zero input cost. Their absence
is supplied by the known episode contract. Every populated predecessor artifact
uses the appropriate Python program rendering.

## Ideal generic-record units

The illustrative vocabulary has 65,536 entries. It reserves 32,768 fifteen-bit
payload values and eight entries for list, dict, str, int, float, true, false and
null. Lengths use the same payload values when expected in a length position.
The frozen static-symbol set is `config.static_symbols`. Its entries cost one
unit each. Total allocated entries must fit inside the vocabulary capacity.

Count a JSON-compatible value recursively with these rules

| Value | Unit charge |
|---|---|
| Known static string | 1 |
| Boolean or null | 1 |
| New string | 2 + ceil(8 × UTF-8 byte length / 15) |
| Integer | 2 + ceil(8 × decimal-text byte length / 15) |
| Finite float | 2 + ceil(8 × canonical-JSON-text byte length / 15) |
| List | 2 + sum of child charges |
| Dictionary | 2 + sum of key charges and value charges |

String payloads use raw UTF-8 without JSON quotes. Integer text is `str(value)`.
Float text is `json.dumps(value, allow_nan=False, separators=(",", ":"))`.
Every dictionary key must be a string. Scalar payloads and container item counts
are bounded to 32,767 so their lengths occupy one payload unit. Reject unsupported
types, nonfinite floats, cycles and nesting beyond 128 levels.

Generic memory and observations use this model. Typed call operands below have
more specific rules because approved signatures already supply their types.

## Ideal approved-call units

The frozen signature and argument order of each approved function/tool are in
`config.catalog_schema`. In this accounting model signatures also supply operand
types, including list element types and field-dependent equality operand types.

A bounded call sequence costs one length unit, then one learned operation unit
per call and all operands in signature order. Operand dictionary field names
are supplied by the signature and incur zero repeated emission cost.

| Typed operand | Unit charge |
|---|---|
| Exact integer from -16,384 through 16,383 | 1 |
| List | 1 length unit + recursively counted typed elements |
| Other value | Generic-record rule above |

Booleans use the generic one-unit atom rule, with exact Python type checks so
`True` is handled separately from integer 1. Lists are bounded to 32,767 items.
Known static strings cost one unit. New strings and larger integers retain the
generic type, length and payload charges. New operand information always counts.

For ideal action batches, charge one sequence-length unit, then each host tool's
one-unit operation and typed operands. A write action has the special typed
`program` operand. Its charge is the pipeline call sequence described above.
This avoids repeatedly encoding a program as generic JSON metadata.

All three ideal profiles use exactly these same semantics and interface. Names
serve as labels for the shared learned representation opportunity.

## Per-request recurrence

For each episode/profile, initialize history payload H to zero. Determine
predecessor artifact cost A and incoming memory cost M once for that episode.
They are included again in every request. Artifact cost is its Python text-token
count or ideal approved-call count. Memory cost is Python `repr` token count or
ideal generic-record count. Empty values cost zero as described above.

For each action/observation pair at zero-based turn index i,

```text
C = token_count(common_input_text)
R = action-batch text-token count or ideal action-batch units
O = observation repr text-token count or ideal generic-record units
F = 4 + 3*i
input_positions = C + A + M + H + F
output_positions = R + 1
H_next = H + output_positions + O
```

F represents the fixed common request framing and preceding message-pair framing.
The output increment represents one response-end position. Host observations
are charged to inference input when subsequently reprocessed. The final host
acknowledgement remains in the raw host ledger even when no later request uses it.

Every ledger row has these exact fields

```text
profile, turn, common_input_text_tokens, artifact_input_units,
memory_input_units, reprocessed_history_units, shared_framing_positions,
input_positions, authored_content_units, output_positions,
host_observation_units
```

`turn` is one-based. `authored_content_units` is R. Aggregate each schedule/profile
by summing every numeric field except turn. Exclude profile labels from totals.
Do not add host observations again to input/output totals outside the recurrence.

## Execution and scientific interpretation

Ten approved components implement filtering, deduplication, aggregation, version
selection, projection, sorting and bounded retry. The supplied function bodies
contain actual for/while loops. Episode actions record working information, write
or patch an artifact, execute checks, store memory and submit. Build writes once,
change and repair patch once, and handoff reuses the prior artifact. Publication
effects are deterministic simulations. Check artifacts against the independent
fixture expectations exposed by the supplied workload module.

Record your Git revision, environment, tokenizer/file hashes, own source hashes,
input hashes and all deviations. Host execution timings can differ. The exact
reference rerun compares parsed JSON and excludes only per-episode
`execution_seconds`; it normalizes source-path separators in manifests.

The equal-unit-cost and perfect-composition assumptions are part of the question.
Measured Python text-token counts and modeled ideal units should retain their
labels. Actual model inference, energy, task-planning success and language-learning
cost require separately instrumented experiments. Keep changes to this model in
a new version and preserve the initial replication output for article review.
