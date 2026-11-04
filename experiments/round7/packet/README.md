# AI Think Tank — Round 7: runnable experimental packet

Send **this entire ZIP** to Claude, Gemini and Grok. Paste `00_SEND_TO_EVERY_AGENT.md` as the instruction message. Ask each to return a completed `02_RESULTS_TEMPLATE.md` and any generated code files. The technical tests live in `01_EXPERIMENT_PROTOCOL.md`.

## Why this benchmark exists

The proposal has three separately testable hypotheses: H1 implementation-free reuse, H2 native authoring, and H3 valid repeat bindings. This packet tries to test small pieces without conflating a shorter string with lower agent inference cost.

## Critical controls

1. A strong conventional baseline uses the existing Python library *without reading its source*. If H1 adds no benefit beyond that, report it.
2. The reference implementations are present on disk for executable tests, but should be hidden from the model during reuse trials. If an AI service ingests/reads every file automatically, its trial is **contaminated**.
3. Near-miss candidates have matching function signatures. Matching a signature alone does not imply correct behavior.
4. The symbolic interpreter is intentionally tiny and is not evidence that a trained model could or could not learn a general AI-native language.
5. The registry's effect policy and SHA-256 test are a toy simulation; they are not a security certification.
6. Any inference-token or latency claim needs actual runtime telemetry. `tiktoken` measures text artifacts, not internal model processing.

## File guide

- `00_SEND_TO_EVERY_AGENT.md`: paste into each agent's conversation
- `01_EXPERIMENT_PROTOCOL.md`: precise test instructions and experimental limits
- `02_RESULTS_TEMPLATE.md`: mandatory standardized report
- `fixtures/baseline_api.md`: strong conventional reuse baseline
- `fixtures/capability_cards.md`: candidate registry cards
- `fixtures/activity_contract.md`: exact intended larger-task contract
- `fixtures/capabilities.py`: implementation **do not inspect by default**
- `fixtures/registry.py`: simple binder
- `fixtures/symbolic_runtime.py`: tiny interpreter for an illustrative symbolic grammar
- `fixtures/test_tasks.py`: deterministic tests
- `fixtures/binding_checks.py`: toy host-side policy/digest tests
- `fixtures/token_measure.py`: optional artifact-token measurement

## Organizer notes

The reference test harness has been sanity-checked locally, and sample solutions not included in this participant ZIP passed 14/14 wrapper checks and 6/6 symbolic cases. These results demonstrate harness operation, NOT performance of any AI model.

You can run `python fixtures/binding_checks.py` immediately. Participants must supply their own `submission.py`, `controller_submission.py`, and/or `controller_submission.sym`.

No experiment in this packet alone can validate full-program equivalence, universal token economics, reliable cross-agent secure execution, or a purpose-trained opcode model.
