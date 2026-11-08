# Approved-core workflow theory experiment

For an independent article reproduction, begin with
[AGENT_START_HERE.md](AGENT_START_HERE.md). It introduces AIN from scratch and
provides exact-rerun and independent-reconstruction instructions. The standalone
CPU setup is pinned in `requirements-reproduce.txt`.

Izik Bachar requested a test of an already existing, short, optimized AIN used
by agents with fully approved core code. This experiment takes fluent language
knowledge and core approval as premises. It additionally holds composition
correctness fixed through oracle plans, isolating representation and reuse costs.
Codex prepared the implementation and measurement model with collaboration agents.

## Cases and observable work

The fixtures contain eighteen four-stage chains across three workflow templates.
They process events, resolve versioned cache entries and simulate publication
with bounded retries. The stages are build, change, repair and fresh-context
handoff. There are seventy-two stages and 216 logical agent requests per schedule.
Ten shared approved functions contain real filtering, grouping, deduplication,
version selection, `for` loops and a bounded `while` retry loop. Every pipeline
composes five generic functions, with explicit arguments and new requirements.

Build writes a new composition. Change patches one argument. Repair corrects one
injected defect. Handoff uses the existing artifact and persisted memory. Every
stage records its selected requirements, checks execution, persists memory and
submits. Correctness is checked against separately implemented fixture oracles.
The ordinary and short-alias Python renderings round-trip through a restricted
AST reader and run through the same approved implementations.

Publication effects are deterministic simulated records. The six variations per
domain share a composition template. Their counts describe these workloads and
do not supply independent statistical research samples.

## Frozen accounting assumptions

The AIN condition uses a theoretical approved-call interface with known argument
types and order. Each learned operation reference costs one code unit. A bounded
program length costs one unit. Typed signed integers in the fifteen-bit range
cost one unit, public field references cost one unit and list arguments include
their length and every element. New strings and larger scalar values carry
explicit type, length and fifteen-bit UTF-8 payload charges. Structured memory
and observations include keys, container framing and all values.

The illustrative vocabulary has 65,536 entries, including 32,768 payload values,
eight type/atom tags and a frozen set of approved interface symbols. This is a
fixed resource model for the premise, with a capacity check. Its code units are
separate from tokens measured using an existing pretrained text tokenizer.

Python and readable IR also receive the same ideal interface in control columns.
Identical semantic streams then have identical unit counts. Practical Python
columns count Qwen2.5-1.5B text tokens for the approved function calls, with both
descriptive function names and fixed short aliases. The shared function bodies
already exist in every condition. Their source is preserved as a setup reference.

Task requirements, parameter values, schema and data handle use the same common
input text in every condition. The resident schedule keeps business records in
host storage and passes a handle. The inspect schedule also sends all records in
each initial request context. Each stage starts a fresh conversation with its
predecessor artifact and persisted memory, then accumulates all three tool turns.
Prior actions and tool observations are counted again whenever reprocessed.
The fixed framing assumption charges four input positions per request plus
three per previous action/observation pair, and one response-end position.
The auxiliary `byte_fallback_units` field is a raw payload-byte diagnostic.
The primary results use the fixed fifteen-bit encoding described above.

Totals combine common text tokens and representation units under an explicitly
equal-cost-per-position assumption. They describe conditional context and output
position demand. GPU inference, learned composition accuracy and the learning
cost of a future AIN system remain open measurements. Core approval and fluent
knowledge are assumed before the run. Any additional setup cost is a separate
parameter in amortization, with the same shared library available to Python.

## Run and inspect

From the repository root using the environment established in earlier work,

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s experiments/approved_workflow_theory -p 'test_*.py' -v
& .\.venv\Scripts\python.exe experiments/approved_workflow_theory/run.py
& .\.venv\Scripts\python.exe experiments/approved_workflow_theory/report.py
```

The command freezes source hashes, fixture hash, codebook, interfaces and
assumptions before measuring. A fresh results directory is required for each
run. Every fixture, approved function body, action, observation, memory value,
predecessor artifact and per-request ledger is saved for review.

The completed observations and report are under
`results/approved-core-2026-11-06/`. The reporting command verifies the frozen
source and fixture hashes and replays every saved artifact before reporting.
