# Candidate decisions recorded from public contracts only, before running any test
Recorded: 2026-11-03T16:40:50Z
Files read at this point: Round 8 docs, API_CONTRACTS.md, TASKS.md. Nothing under benchmark/sealed/ opened.

| Candidate | Decision | Reason (contract text only) |
|---|---|---|
| pub.parse_money@1 | SELECT | Contract: ROUND_HALF_UP, matches task requirement for cents. |
| candidate.parse_money_bankers@1 | REJECT | Contract states HALF_EVEN for ties; wrong for 1.005 (needs 101 cents, not 100). |
| pub.safe_path@1 | SELECT | Contract rejects traversal/absolute/backslash/NUL. |
| candidate.safe_path_loose@1 | REJECT | Contract states it rewrites traversal instead of rejecting; violates task 3 ("do not silently remove traversal"). |
| pub.group_by_window@1 | SELECT | Contract groups by normalized (device, kind, message) with a time window. |
| candidate.group_by_eventid@1 | REJECT | Contract states it groups by unique event_id; repeats not aggregated. |
| private.project_risk_score@1 (public-only scope) | EXPECT DENY | Restricted to scope project-a + effect project.policy; a public-only bind must raise PermissionDenied. |

Caveat (same as Round 7): every near-miss here is self-labelled in the contract text, so contract-only rejection is trivial.
An unlabelled near-miss with a matching signature would need differential testing, not card-reading.
