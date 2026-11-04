# Existing prototype recheck — 4 November 2026

[Raw result record](2026-11-04-prototype-recheck.json).

The source programs are from commit `88ad03f1c230b6979ea372d08c4c70f6b7abaac8`. They were run in temporary copies on Windows with Python 3.12.14 and Node v24.22.1. The historical source files and imported archives were not modified.

## Commands and inputs

For the binding-state check, copy `experiments/round7/packet/fixtures/` and `agents/claude/round7/h3_binding_cache.py` into a separate directory, then run `python h3_binding_cache.py` there.

For conformance, copy `experiments/round8/packet/benchmark/` and `agents/claude/round8/agreement/` into another directory with Node available on PATH, then run `python agreement/differential.py` there. The script writes result/vector files, which is why a separate copy is required. The environment used UTF-8 text I/O and disabled Python bytecode output.

## Observed scope

- The H3 prototype made 20 alias calls after one full validation and detected the supplied changes to environment, requirement, policy, contract, implementation, and revocation. Additional supplied tampered-code and declared-effect cases were rejected.
- Existing Python and table-assisted JavaScript variants matched 1,206/1,206 supplied cases; naive JavaScript matched 559/1,206.

These are executions of previously authored programs on an existing test pool. One original contributor wrote the variants. This is not a new independently authored or held-out agent study. Matching this pool does not prove universal equivalence across runtimes/environments.

The H3 prototype is in-process and does not supply production isolation or complete dependency, identity, policy, or security assurance. No billed model usage, inference cost, agent development time, or cross-agent knowledge transfer was measured.
