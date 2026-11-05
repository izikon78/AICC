# Agent-designed optimization record

## Design scope

The implementations were designed and reviewed by AI coding agents in the same Codex work session. They combine established programming techniques. No claim is made that the algorithms are new to humanity, that the variants were independently blinded, or that a trained agent autonomously invented their source code.

## Alternative flows

1. **Transparent reference:** validate and deduplicate, normalize events, globally sort by timestamp/input ordinal, apply the severity filter, and group.
2. **Cached flow:** retain full validation, deduplicate and filter before normalization/sorting, and cache repeated tag/message normalization within bounded per-job caches.
3. **Partitioned flow:** normalize/group by semantic key, perform smaller per-key sorts, then restore global group-creation order. This changes control/data flow while preserving the documented anchored-window semantics.
4. **Ordered streaming:** validate monotonicity on the complete raw stream and avoid materializing a global sorted record list. It retains exact-ID and output state, so it does not claim constant memory.

The ordinary and AICC execution paths share all four implementations. Faster kernels alone cannot demonstrate a unique benefit of registry indirection.

## Corrections made before the primary run

- A development smoke run exposed a slow cold environment lookup during AICC host construction. The environment identity now uses the process's `sys.platform` constant instead of invoking broader platform introspection in that timed setup. The primary run includes actual host registration/binding costs after this change.
- Review showed that choosing the unrestricted static plan before deciding whether to use the ordered path could produce a weaker baseline. Static fitting now exhaustively compares all four simple conditional policies on the training measurements.
- Runtime handoff restoration now accepts explicit receiving-task obligations/requirements, so a weakened imported record cannot erase those current constraints.
- Optional call-precondition code/default identities are pinned alongside the capability identity.
- Neural timing ingestion rejects zero, negative, missing required, or non-finite measurements. Training rejects empty data and nonpositive epoch counts.
- Numerical finite-difference tests check neural gradients; adversarial cases check dedupe/filter ordering, Unicode, timestamp precision, caller authority, invalidation, and precondition changes.

The larger neural policy is selected from calibration/validation only. Stress results are retained without retuning that policy to the stress workloads.

## Evidence boundaries

The model chooses among supplied flows; it does not generate new programs. The host's compatibility counter does not automatically run semantic conformance tests or prove a contract sufficient. New-host JSON restoration is a deterministic host demonstration, not a fresh AI-agent/provider handoff experiment.

These measurements concern local program execution and a small neural model's training. No API-billed inference tokens, model-development dollars, full lifecycle break-even, or general private-code security guarantee is established.
