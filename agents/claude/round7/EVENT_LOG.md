# Event log (files opened, inspections, retries)
2026-11-03T14:28:28Z  Read: 00, README, 01, 02, baseline_api.md, activity_contract.md, capability_cards.md
2026-11-03T14:28:28Z  T3 decisions recorded before tests (T3_DECISIONS_BEFORE_TESTS.md)
2026-11-03T14:29:32Z  Arm A run: 14/14, 0 retries, 0 source files. Arm B run: 14/14, 0 retries, 0 source files.
2026-11-03T14:30:45Z  Counterexamples run. Incidental exposure: the and_save traceback printed one line of registry.py (raise CapabilityDenied). capabilities.py still unopened.
2026-11-03T14:31:25Z  Adversarial held-out tests: accepted capability SPEC 29/29, 10 UNSPEC behaviours recorded.
2026-11-03T14:31:45Z  Contract-only reimplementation: harness 10/14; variants V1-V3 run; differential fuzz recorded.
2026-11-03T14:32:01Z  Read symbolic_runtime.py (grammar documentation, allowed by protocol for Arm D) and token_measure.py (measurement script).
2026-11-03T14:32:29Z  Arm C and Arm D written and run (first attempt).
2026-11-03T14:33:23Z  tiktoken 0.14.0 with official o200k/cl100k files rebuilt from gpt-tokenizer 4.1.0 (SHA-256 verified); ran token_measure.py unmodified (prints sizes of all fixtures incl. capabilities.py, never its content).
2026-11-03T14:34:33Z  H2 symbolic probes run (mutations, lexing hazard, bool divergence, fair tokens).
2026-11-03T14:35:07Z  INSPECT (post-trial): read registry.py and binding_checks.py. Reason: protocol T3/H3 asks what the toy binding check does and does not establish. All reuse trials (A, B, counterexamples) were complete before this read. capabilities.py still unopened.
2026-11-03T14:35:51Z  H3 trust probes run (lying capability + audit hook, digest TOCTOU, over-invalidation). capabilities.py never opened (probe (c) appended a line to a temp copy without reading it).
2026-11-03T14:36:41Z  h3_binding_cache.py self-test run.
2026-11-03T14:39:58Z  Report written; packaged deliverables. capabilities.py never opened at any point.
