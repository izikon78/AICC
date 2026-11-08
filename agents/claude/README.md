# Claude (Anthropic) — think-tank contributions

Contributed by Claude Opus 5.5 working in a claude.ai chat with a code sandbox, pushed on behalf of the repository owner.
Each round folder holds the results report, the code written for it, raw outputs and the full console log.

| Folder | Round | Main report |
|---|---|---|
| `round7/` | Round 7: H1 reuse, H2 symbolic authoring, H3 bindings (toy packet) | `round7/Round7_Results_Claude_Opus_5.5.md` |
| `round8/` | Round 8: AI Computational Commons (AICC) composition, private scope, cross-provider agreement | `round8/Round8_Results_Claude_Opus_5.5.md` |
| `round9-efficiency/` | Efficiency study: tokens, cost, computing time, power analysis, decisive-benchmark harness | `round9-efficiency/AICC_Efficiency_Research_Report_Claude.md` |

## Provenance and limits (apply to every round)
- One model, one conversation: arms were authored in the same session, so cross-arm comparisons are **contaminated**, not independent replications.
- No model API access: billed input, output, reasoning tokens, dollar cost and inference latency are **NOT MEASURED**. Token figures are tiktoken `o200k_base` counts of text artefacts only.
- The organisers' packets (fixtures, sealed implementations) are **not** included here. Reproduction scripts (`run_all.sh`) expect the original packets at the paths named inside them.
- Round 8 disclosure: 14 leftover files from an earlier interrupted attempt were quarantined unread and excluded; see `round8/Round8_Results_Claude_Opus_5.5.md`, section 0.
- `round9-efficiency/dry_run_trials.csv` is a **synthetic test fixture**, not data.

Evidence labels used in the reports: MEASURED, TOKENIZER, LITERATURE, MODEL, SIMULATION, OPINION, NOT MEASURED, NOT EXECUTED.
