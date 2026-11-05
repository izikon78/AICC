# AI Computational Commons (AICC)

Research archive for two related, independently testable ideas:

1. A shared computational commons where agents discover and compose capabilities through precise behavioral contracts and scoped bindings.
2. An AI-native programming representation capable of expressing new logic, potentially using dedicated operation tokens instead of human-language keywords.

**Concept and architecture: Izik Bachar. Research status: open, exploratory, and not economically validated.** The available pilots show small-task feasibility and important contract/security limitations. They do not establish lower billed model cost, faster agent development, a secure private execution boundary, or the benefits of a trained native-operation model.

## Start here

- [Implemented processing study: million-event jobs, optimized flows, and local neural training](experiments/processing_study/README.md)
- [Next steps: AICC reuse across agents and software changes](experiments/lifecycle-pilot/README.md)
- [Future-value research brief](docs/research/NEXT_STUDY_AICC_FUTURE_VALUE.md)
- [Review of the supplied archive, corrections, and unresolved evidence](docs/research/REVIEW_2026-11-04.md)
- [Detailed conversation handoff](docs/handoff/AICC_Codex_Conversation_Handoff.md) — a supplied reconstruction, not a complete verbatim chat export
- [Architecture recommendation](docs/architecture/AI_Computational_Commons_Architecture_Recommendation.md)
- [Article drafts and credits](docs/article/README.md)
- [Experiments and reproduction](experiments/README.md)
- [Original-file manifest and exclusions](reference/README.md)

## Research contributions

| Contributor | Available materials |
|---|---|
| Claude / Anthropic | [Provenance](agents/claude/README.md), [Round 7](agents/claude/round7/), [Round 8](agents/claude/round8/), [efficiency measurements](agents/claude/round9-efficiency/) |
| ChatGPT / GPT-6 / OpenAI | [Round 7 report](agents/gpt6/round7/AI_Think_Tank_Round7_GPT6_Report.md), [Round 8 audit](agents/gpt6/round8/AI_Think_Tank_Round8_Independent_Audit.md), [correction questions](agents/gpt6/round8/AI_Think_Tank_Round8_Correction_Questions.md) |
| Gemini / Google | [Round 7](agents/gemini/round7/ai_think_tank_round_7_experiment_results_gemini.md), [Round 8](agents/gemini/round8/ai_think_tank_round_8_experiment_results_gemini.md), [Round 8.1 correction](agents/gemini/round8/ai_think_tank_round_8_1_correction_reconciliation_gemini.md), [efficiency report](agents/gemini/efficiency/aicc_efficiency_independent_research_report.md) |
| Grok / xAI | [Early reviews](agents/grok/history/Grok_Responses_for_OpenAI.md), [Round 7](agents/grok/round7/Grok_Round7_Experiment_Results.md), [Round 8 and 8.1](agents/grok/round8/), [efficiency report](agents/grok/efficiency/Grok_AICC_Efficiency_Independent_Research_Report.md) |

Contributor names and model versions are those attributed by the supplied sources. Archived reports retain their original claims, including claims qualified or contradicted elsewhere. Read the [review](docs/research/REVIEW_2026-11-04.md) before combining results or quoting efficiency figures.

## Verify the recovered fixtures

Python 3.10+; no third-party packages or model API credentials are required:

```shell
python tools/verify_research_import.py
```

The [recorded verification](docs/research/verification-2026-11-04.json) checks source hashes and reruns eleven commands against the historical Round 7/8 fixtures. It executes existing code, not new independent AI authoring trials. Mock security checks are not production security assurance.

## Archive boundaries

The import reviewed 40 supplied files, consolidated 11 byte-identical duplicate copies, and excluded an operational controller log and an unrelated Windows metadata binary from this public repository. Original research documents and retained archives are preserved byte-for-byte; [the manifest](reference/import-manifest.json) records all input filenames, hashes, mappings, and exclusions. Existing Claude research was retained.

No access token is included. A token previously pasted into chat should be revoked through GitHub settings; repository access uses the configured authorization.
