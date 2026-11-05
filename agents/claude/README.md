# Claude (Anthropic) — think-tank contributions

Contributed by Claude Opus 5.5 working in a claude.ai chat with a code sandbox, pushed on behalf of the repository owner.
Each round folder holds the results report, the code written for it, raw outputs and the full console log.

| Folder | Round | Main report |
|---|---|---|
| `round7/` | Round 7: H1 reuse, H2 symbolic authoring, H3 bindings (toy packet) | `round7/Round7_Results_Claude_Opus_5.5.md` |
| `round8/` | Round 8: AI Computational Commons (AICC) composition, private scope, cross-provider agreement | `round8/Round8_Results_Claude_Opus_5.5.md` |
| `round9-efficiency/` | Efficiency study: tokens, cost, computing time, power analysis, decisive-benchmark harness | `round9-efficiency/AICC_Efficiency_Research_Report_Claude.md` |
| `cross-review/` | Cross-review of the consolidated archive: reconciliation of the two Round 8 accounts, answers to GPT-6's Round 8.1 questions, checks of other agents' claims | `cross-review/CROSS_REVIEW_2026-11-04.md` |
| `round8-earlier-attempt/` | The earlier, interrupted Round 8 attempt that the GPT-6 audit and Draft 4 describe; unchanged, with hashes and corrections | `round8-earlier-attempt/PROVENANCE.md` |
| `language-prototypes-v2/` | Language A/B parser, type checker, interpreter, opcode encoder, reference sheet and serialized Language B example (v2 review) | `language-prototypes-v2/README.md` |

## Provenance and limits (apply to every round)
- One model, one conversation: arms were authored in the same session, so cross-arm comparisons are **contaminated**, not independent replications.
- No model API access: billed input, output, reasoning tokens, dollar cost and inference latency are **NOT MEASURED**. Token figures are tiktoken `o200k_base` counts of text artefacts only.
- The organisers' packets (fixtures, sealed implementations) are **not** included here. Reproduction scripts (`run_all.sh`) expect the original packets at the paths named inside them.
- Round 8 has two attempts from the same conversation: `round8-earlier-attempt/` (first, interrupted, audited by GPT-6) and `round8/` (delivered). See `cross-review/CROSS_REVIEW_2026-11-04.md`, section 1.
- `round9-efficiency/dry_run_trials.csv` is a **synthetic test fixture**, not data.

Evidence labels used in the reports: MEASURED, TOKENIZER, LITERATURE, MODEL, SIMULATION, OPINION, NOT MEASURED, NOT EXECUTED.
