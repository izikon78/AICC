# Harness qualification before participant execution

6 November 2026. No participant trials had run when this record was written.

The final integrated qualification command completed successfully:

```text
python -m unittest discover -s experiments/ain_fluency/tests -v
Ran 35 tests in 59.416s
OK
```

This includes baseline and changed controllers in all forms, manually calculated
threshold boundaries, invalid-return rejection, cancellation audit, recovery,
typing, timeout reporting, metering, unknown counters, zero-success accounting,
canonical fallback exclusion, schema consistency, and supported mutation aliases.
Each single injected fault was behaviorally rejected in all three forms at both
deltas, separately from the combined corruption. The runner repeats these
single-fault checks for every actual handoff before genuine-chain eligibility.

All 133 hashes in the earlier AIN v0 artifact inventory remain unchanged.
Reporter SVG generation was smoke-tested with both balanced and zero-success
synthetic accounting fixtures; those fixtures are not experimental observations.
No GitHub credential patterns were found in the new source/material files.

Runtime: Python 3.12.14, Codex CLI 0.166.0-alpha.6. The requested participant model
is gpt-6.1-sol with reasoning effort ultra. Exact runtime, source hashes, plan
commit, harness commit and usage will be recorded by the experiment manifest.
