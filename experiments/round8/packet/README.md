# AICC Round 8 — research recommendation and experimental pilot

**Strongly recommended research direction, not a proven production architecture.**

Start with `00_SEND_TO_ALL_AGENTS.md`, then `01_EXPERIMENT_PROTOCOL.md` and `benchmark/public/{API_CONTRACTS.md,TASKS.md}`. Send the **same unmodified packet** to Claude, Gemini, Grok and GPT-6. Ask each to return `02_RESULTS_TEMPLATE.md` plus code and logs.

`ARCHITECTURE_RECOMMENDATION.md` is the architectural position to challenge. `ARTICLE_ADDENDUM.md` provides publication wording. The `benchmark` includes 20 normal Python callable capabilities, near misses, a mock scope-based host and reference tests. The `sealed` directory is merely *voluntarily hidden*, not protected by real permissions or cryptography. The tested public functions are small-to-medium and NOT a real-world corpus of large mature software packages.

Do not mistake cross-model agreement for independent experimental evidence. Do not pool token counts from mismatched files/fixtures.
