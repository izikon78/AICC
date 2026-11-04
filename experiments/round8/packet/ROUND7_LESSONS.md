# Round 7 lessons entering Round 8

All four model reports (GPT-6, Claude, Gemini and Grok) reported 14/14 for both ordinary API reuse and registry binding, 6/6 for both Python and the toy symbolic implementation, and 3/3 on toy effect/digest binding checks. These are small same-purpose tasks, not four independently preregistered randomized experiments.

**Negative evidence:** Ordinary package reuse also avoided reading implementation code. Thus Round 7 found no registry advantage over a strong baseline. The toy DSL's byte compactness was not established as cheaper end-to-end LLM work. No agent ran a model fine-tuned to emit true operation tokens.

**Claude adversarial results as reported:** a contract-only reimplementation initially scored 10/14 when omitted behavior (severity formatting and normalization details) became observable. The simple registry allowed effect misdeclarations and artifact identity corner cases. These show that reference-to-code and signature/type agreement alone do not establish safety or behavior.

**Data integrity:** Gemini's reported input sizes differed from the supplied Round 7 files; do not pool its reported tokenizer numbers until byte-identical artifacts and scripts are available. No model published comparable API-reported total inference/billing costs.

**Round 8 change:** Test a layered public/private computational commons and real composition tasks with equal conventional-package baselines, explicit near misses and mock private scopes. Treat claims of 'public consensus,' 'secure encryption,' 'proven savings,' or '60–80% functionality covered' as hypotheses until independently measured.
