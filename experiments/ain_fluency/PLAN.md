# AIN fluency simulation: published protocol and predictions

Protocol version 1, 6 November 2026. Status at publication: **no participant trials run**. Publish this document before running participants; record its Git commit and the later harness-freeze commit with the results. Concept, architecture and research direction: **Izik Bachar**, with Codex experiment design and implementation assistance. This is an additional engineering experiment, not confirmation of the native-training hypothesis.

## Question and scope

Can a current AI agent, after matched preparation and an objective fluency check, build, change and repair a nontrivial workflow controller more economically in numeric AIN than in Python or readable IR, while preserving correctness?

Preparation is supplied in context. The task call replays the preparation transcript. This simulates demonstrated familiarity; it does not make the language native to model weights, change the tokenizer, reveal internal reasoning or measure how far a model “travels” to find syntax. Numeric AIN and readable IR share exactly the same VM and capabilities. The engine already implements grouping, scheduling and durable effects; participants author the controller, not those engine algorithms.

## Frozen assignments

Six assigned chains: three forms (Python, readable IR, numeric AIN) times two boundary-threshold variants (delta 30 and 75). Each chain has three scored stages, giving **18 scored submissions**:

1. Build a complete controller from the contract, catalog and grammar. No completed workflow is supplied as a language example.
2. Change that controller: for an admitted event whose timestamp minus current frontier is strictly below delta, use `min(3, minimum + 1)` as its severity threshold; otherwise use minimum. Reserve the first admitted ID before filtering. Preserve all other behavior.
3. Repair a supplied changed controller with three faults: equality is wrongly rejected at the late boundary, filtering precedes reservation, and only one pending event is drained. Apply the faults to the predecessor where structurally supported; otherwise supply an explicitly labeled canonical fallback. Record exactly which mutations applied and their provenance.

Each scored submission has a **separate preparation call** beforehand: 18 preparation calls plus 18 task calls, or 36 planned calls. Preparation asks objective semantic and syntax questions. Grade it before task generation. The task receives the full preparation prompt and response in its context, with the relevant predecessor artifact. It runs even if preparation failed, so the assigned work is not selected for favorable fluency. Failed preparation disqualifies that stage and the primary chain, while its usage remains counted.

Use identical semantic information and capability catalog across forms, with form-specific syntax documentation and small arithmetic examples. Measure different prompt lengths. Do not put hidden judge fixtures or expected results in participant context. Fresh isolated working directories and read-only execution reduce accidental repository access; this cooperative shared-host setup is not a security isolation claim. Tool use by participants is a protocol violation.

## Outcomes and honest denominators

Functional success requires exact independent-oracle agreement on result, counters, ordering, checkpoints, errors and durable effect traces. Include explicit boundary examples, deterministic seeded streams, cancellation, capacity, authority and recovery cases. Validate typing and execution; cap VM fuel. Python receives the same host catalog and a restricted syntax/builtins surface, not extra engine functionality.

Primary chain success requires all three stages to pass both fluency and hidden correctness checks, no participant tool use, and a genuine predecessor-derived repair with all three verified faults. A canonical fallback is a repair diagnostic and **cannot rescue primary chain success**. Unsupported fault injection is a harness limitation, reported separately from model incorrectness. Also report stage success and diagnostic repair success so that this limitation is visible.

Report total resources for **all assigned attempts**, divided by successful chains where defined, with fluency failures, functional failures, fallback and timeouts retained. Zero successful chains means undefined cost per successful chain; never report zero cost. Six chains contain only two paired workflow variants, not 18 independent tasks. No significance claim, population confidence interval or general native-language conclusion is supported.

## Execution and stopping rules

Pin the existing signed-in Codex model identifier `gpt-6.1-sol`, reasoning effort `ultra`, Codex CLI version, source hashes and seed 20261106. Record requested model identity; it is not independent provider attestation of a fixed model snapshot. Use fresh ephemeral noninteractive calls, read-only mode, no participant tools, and strict JSON response schemas. Replay preparation explicitly rather than claiming persistent learned weights.

Run forms in seeded shuffled order within each variant/stage block, sequentially. Per-call wall-clock cap: **300 seconds**. One substantive submission per call, with no corrective feedback or semantic retry. At most one infrastructure retry is permitted only if there was no substantive response; retain both attempts and all available usage. A timeout is not automatically a free retry. A missing/invalid predecessor is replaced only to allow later diagnostics, with the chain failure preserved. No adaptive early stopping on promising results. Stop at all 36 planned calls, plus at most the allowed infrastructure retries, or a genuine service/access failure preventing continuation. Record incomplete assignments as incomplete, never successful.

Capture raw JSONL, final response, CLI exit code, elapsed time, preparation score, artifact, judge report and usage. Do not store credentials, personal access tokens or full user configuration. Keep stderr privately if it contains local machine details; publish a scrubbed diagnostic summary. Source and plan changes after the first participant call require a new explicitly labeled protocol version and a separate run; do not silently tune against outcomes.

## Resource accounting

Use CLI-reported input, cached-input, output and reasoning-output fields. Cached input is a subset of input. Preserve raw fields; do not add reasoning tokens to output without verified billing semantics. A reported missing category remains unknown, not zero. Measure preparation, replay, failed attempts and fallback-related participant work. Show raw tokens and elapsed time, plus a cache-neutral sensitivity view. CLI elapsed time includes service variability and is not compiler speed or isolated model compute.

The signed-in account does not expose a per-call dollar invoice here. Report **normalized hypothetical resource cost**, not realized dollar savings. Primary sensitivity weights per token: uncached input 1, cached input 0.1, output 5. A separate cache-neutral view uses input 1 and output 5. These are illustrative weights, not OpenAI prices. Compute output weights 1 and 10 as additional sensitivity checks. Unknown usage makes the corresponding aggregate incomplete.

Savings relative to baseline B are `1 - (AIN total normalized cost / AIN successful chains) / (B total normalized cost / B successful chains)`, only when both denominators exist. Also show raw cost per assigned stage and success rates. Compare with both Python and readable IR; the IR comparison isolates the current numeric encoding more directly.

## Predictions frozen before trials

The neutral engineering prediction is **0% net saving versus readable IR** for this current mechanically equivalent codec. There is no calibrated basis for promising positive savings; AIN may cost more once preparation, replay and errors are counted. No directional point prediction versus Python is justified by existing evidence.

A conditional optimistic scenario is **10–20% normalized cost saving**, not a confidence interval or measured result. It requires enough task-related cost to be reducible without harming correctness:

| Scenario | Assumed reducible share | Assumed reduction of that share | Added overhead | Net saving |
|---|---:|---:|---:|---:|
| Optimistic modest | 60% | 25% | 5% | 10% |
| Optimistic strong | 80% | 30% | 4% | 20% |
| Downside example | 40% | 10% | 10% | -6% |

Formula: reducible share times reduction minus added overhead. These values are assumptions. Accuracy dominates: spending 10% less per attempt but succeeding only 80% as often raises cost per success by 12.5%. Actual native training and amortized learning could behave differently and require the separately documented trained-native pilot.

## Reproduction and publication

AI agents should use the frozen participant guide, run all forms with matched model/settings, retain every assigned attempt, independently execute the hidden judge and publish raw usage and failures. Do not claim savings from character count or smaller source alone. Release the runner, independent judge, deterministic tests, protocol/source hashes, artifacts, score tables and charts. Keep this pre-run prediction intact when adding the result report. Preserve earlier AIN experiments unchanged.

Codex JSONL usage and ephemeral execution are documented in the [official noninteractive-mode guide](https://learn.chatgpt.com/docs/non-interactive-mode). This repository's trained-native protocol remains the next experiment for a claim about language learned into model weights.
