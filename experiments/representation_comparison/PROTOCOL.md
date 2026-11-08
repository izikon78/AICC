# Matched representation comparison, version 1

Prepared 8 November 2026 under Izik Bachar's research direction. This is one
bounded CPU comparison of local representations, with no model pilot. This
protocol and the implementation are hashed before measuring the results.

## Fixed comparison

Use every one of the 144 episodes in the frozen approved-core trace inputs.
They cover eighteen four-stage chains and both resident and inspect schedules.
The schedules reuse the same tasks. The actions are supplied correct compositions.
Every profile receives the same approved operations, argument schemas, task
information, observations, predecessor and memory. No function body is regenerated.

Five profiles are fixed before execution,

| Profile | Program/actions | Memory and observations |
|---|---|---|
| python_repr | Existing short-alias nested Python calls and repr literals | Python repr |
| python_compact | Same calls with whitespace-free Python literal containers | Compact JSON |
| readable_ir | Positional JSON call arrays with descriptive operation names | Compact JSON |
| numeric_arrays | Same positional JSON arrays with example-local operation IDs | Compact JSON |
| symbolic_ain | Bounded article-style @/!/return call-stream sketch | Compact JSON |

The numeric arrays are an encoding ablation, not a replacement for the article's
symbolic notation. Symbolic AIN is a reversible illustration subset for these
approved-call fixtures, not a complete AIN standard or a newly trained language.
IDs follow sorted approved names, fixed independently of tokenizer outcomes.
Readable and numeric arrays give exactly the same positional-operand opportunity.
All formats retain task-specific literals. Compact JSON uses UTF-8 characters
without ASCII escaping. Common task input preserves the frozen original rendering.

## Execution and measurement

Decode every artifact and action batch. Replay all decoded stages through the
same approved functions and independent fixture oracle. Round-trip all memory
and observations with exact JSON-compatible types. Reject unknown operations,
wrong arities and nonliteral Python operands. No eval or exec is used.

The actual model-input text has a common input followed by A, M and H sections
for predecessor artifact, memory and accumulated action/observation history.
History adds X and O sections after each response and observation. Encode each
complete request once using the pinned Qwen2.5-1.5B tokenizer, with no special
tokens. Encode each complete response once. Report literal tokenizer counts,
UTF-8 byte counts and input/output totals for the two schedules separately.
No hypothetical learned-code units or artificial chat framing are mixed in.
These strings are fixture contexts, not a provider's real chat template.

Isolated component token counts are diagnostic. BPE boundaries make their sum
potentially different from the complete-context count, so report the difference.
All repetitions and failures remain in the ledger. No cross-format inference
speed, task-success probability, energy or billing result is produced.

Additional fixed probes check long/new/Unicode literals and delimiter characters,
malformed input, and whether distinct deduplication state survives a handoff.
Probe counts are separate from the workflow totals. This experiment does not
measure library discovery, new algorithms or unknown control-flow composition.

## Reproduction and interpretation

Run with the existing approved-core dependency pins and cached pinned tokenizer,

```text
python -m unittest discover -s experiments/representation_comparison -p test_*.py -v
python experiments/representation_comparison/run.py --output work/representation-comparison-new
```

The output must be fresh. Save source/input hashes before token measurement,
then raw per-request contexts, decoded-stage checks, probe records, CSV and JSON
totals. Do not tune formats after observing outcomes. Changed encodings require
a new protocol/version rather than replacing these results.

The named external systems in the related-work section are literature/project
comparisons. ToolkenGPT, CodeAct, AINL and the other full systems are not executed
by this test. A measured local control must not be attributed to those systems.
