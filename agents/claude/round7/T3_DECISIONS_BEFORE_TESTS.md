# T3 candidate decisions, recorded from contract cards only, before any test was run
Recorded: 2026-11-03T14:28:28Z (UTC, sandbox clock)
Files read at this point: 00_SEND_TO_EVERY_AGENT.md, README.md, 01_EXPERIMENT_PROTOCOL.md, 02_RESULTS_TEMPLATE.md,
fixtures/baseline_api.md, fixtures/activity_contract.md, fixtures/capability_cards.md.
Not opened: fixtures/capabilities.py, registry.py, test_tasks.py, binding_checks.py, symbolic_runtime.py, token_measure.py.

| Handle | Decision | Reason (contract evidence only) |
|---|---|---|
| cap:controller.logs@1 | SELECT | Card points to the baseline_api.md contract, which matches T1 exactly (runs<=0 -> no messages; ordinal i+1). |
| cap:controller.logs_zero_based@1 | REJECT | Card states restart messages use zero-based i ("run 1 of 2"); T1 requires i+1 ("run 2 of 2"). |
| cap:activity.rollup@1 | SELECT | Card points to activity_contract.md, the T2 contract. |
| cap:activity.rollup_by_eventid@1 | REJECT | Card states it partitions by event ID, so repeats are not aggregated; T2 groups by normalized (device, kind, message). |
| cap:activity.rollup_and_save@1 | REJECT | Card declares effect filesystem.write; T2 is pure and the caller policy is allowed_effects=(). |

Caveat recorded in advance: every near-miss card here *announces* its own defect ("Near-miss", "effect: filesystem.write").
Rejection "by contract alone" is therefore trivial in this packet; an unlabeled near-miss would need executable evidence.
