# Round 5 — Reply to the Think Tank (continues the v3 review)

Nov 2, 2026 · @Izik bachar

## About this reply

This continues my v3 review and answers the seven Round 5 requests without repeating v3's tables. Every number carries one of four labels:

- **New measurement:** produced by code I ran in my sandbox during this turn.
- **Prior measurement:** from my v2 or v3 runs earlier in this conversation.
- **Estimate:** arithmetic on measured sizes under stated assumptions. It is not a measurement of inference.
- **Unmeasured:** needs model runs I cannot do here; each such term comes with a falsifiable experiment.

| Round 5 request | Answered in |
| --- | --- |
| 1. Contract caching beyond first use | Section 1 |
| 2. Whole applications, not tiny functions | Section 5 |
| 3. Strong baseline separating five sources of gain | Section 4 |
| 4. Contract sufficiency test | Section 2 |
| 5. Token costs versus whole-task cost | Sections 1 and 6 |
| 6. H2 on its own merits | Section 7 |
| 7. Trust and malicious components | Section 3 |

**One correction to v3 up front: contracts are for the verifier, verdicts are for the model.** In v3 I charged the model for reading the full 127-token sufficient contract. If a tool checks the contract against the caller's obligations, the model only needs a short selection card and a verdict. Section 1 recomputes the costs on that basis.

**Continuation marker.** If this reply stops early, any section still showing a placeholder was not written. Ask me to "continue Round 5 from section N", naming the first unwritten section.
