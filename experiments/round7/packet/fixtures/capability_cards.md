# Registry cards — Arm B and H3

This experiment intentionally includes *near-miss* candidates and an effect-denied candidate. A signature match is not proof of equivalence.

Use `from registry import bind` to obtain a validated function handle, then call it. The registry binds versioned identifiers and rejects effects not in the caller's policy. The example registry is a **simulation**, not an actual cryptographic certificate or hardened sandbox.

- `cap:controller.logs@1` — `int -> list[str]`; pure. Exact messages and negative-input behavior: see `baseline_api.md` (same contract as conventional API).
- `cap:controller.logs_zero_based@1` — `int -> list[str]`; pure. **Near-miss:** restart messages number each restart with zero-based `i`, e.g. 2 runs says `run 1 of 2`, not `run 2 of 2`.
- `cap:activity.rollup@1` — `(list[dict], window_seconds:int, min_severity:int) -> list[dict]`; pure. Contract: see `activity_contract.md`.
- `cap:activity.rollup_by_eventid@1` — same signature; pure. **Near-miss:** partitions by individual event IDs, not by normalized event behavior, so repeats are not aggregated.
- `cap:activity.rollup_and_save@1` — same signature; **effect**: `filesystem.write`; not allowed under pure-only execution policies. Never bind for this task.

The artifact file SHA-256 is computed by the runtime. No capability should be trusted solely because an identifier matches the user's intended label.
