# Candidate decisions from public contract text only, recorded before any test ran (2026-11-03T16:51:48Z)
| Candidate | Decision | Contract evidence |
|---|---|---|
| pub.<name>@1 for the 20 listed functions | SELECT for tasks 1-8 | API_CONTRACTS.md table |
| candidate.parse_money_bankers@1 | REJECT | HALF_EVEN ties; contract and task 1 require ROUND_HALF_UP (1.005 -> 101 cents, not 100) |
| candidate.safe_path_loose@1 | REJECT | rewrites traversal; task 3 says reject unsafe paths, never silently remove traversal |
| candidate.group_by_eventid@1 | REJECT | groups by event_id; task 2 needs normalized device/kind/message plus the time window |
| private.project_risk_score@1 | Bind only in the private arm with scope project-a and effect project.policy | API_CONTRACTS.md private section |
Caveat recorded in advance: all three near-misses are labelled as near-misses in the shared contract, so rejecting them "from the contract" is trivial in this packet.
