# Round 8 — Results template (return with artifacts)

## 0. Reproducibility and integrity
Model/provider/config:
Date:
Python/platform:
Files received, SHA-256 manifest checked (yes/no):
Fresh separate sessions for A/B (yes/no, explain):
Source inspected during authoring (which files and why):
Other agents' Round 8 results known before trial:

## 1. Outcomes table
| Arm | Executed? | Tests passed/total | Retries | Total input tokens (API) | Total output tokens (API) | Reasoning tokens (API) | Runtime/tool time | Full task cost |
|---|---|---|---|---|---|---|---|---|
| A: ordinary API | | | | | | | | |
| B: commons registry | | | | | | | | |
| C: scoped private | | | | | | | | |
| D: trained native tokens | | | | | | | | |

## 2. Detailed capability selection
Which functions/variants were selected? What was rejected? Which facts required full contract or source inspection? For each failure, report the task, exact trace, and repair.

## 3. Contract sufficiency
List at least 3 uncertainties, with `ENTAILED`, `REFUTED`, or `UNKNOWN`, evidence and necessary escalation. Did the contract omit observable behavior? Did a standard package's docs already provide it?

## 4. Security/private experiment
Public-only denied? Project-scoped authorized? Revoked binding denied? Which tests are only mock metadata checks, which actually enforce resource isolation, which remain untested? How would private code encryption and key custody work in a real host?

## 5. Model cost and context
Provide exact source/contract/handle token counts under a named tokenizer (if available). More importantly, include actual input/output/reasoning telemetry, prompt-cache billing, retries and tool use where available. If absent, write `NOT MEASURED`. Do not infer billed tokens from file sizes.

## 6. Multi-agent shared standard
Write a candidate contract for one public function and two alternative implementations. Explain which guarantees could be shared and which are environment-specific. Do not report 'consensus' unless multiple independently authored variants have actually been compared.

## 7. Skeptical verdicts
H1 verdict; H2 verdict; H3 verdict; H4 verdict. One concrete reason AICC could fail, and what empirical result would change your mind.

## 8. Production-scale benchmark proposal
Select at least 20 independent, larger real-world capability candidates and a defensible sampling method; identify a 50–100 task suite, hidden tests, randomization, baselines, telemetry, assurance criteria, and failure thresholds. Mark all unexecuted work as proposed.

## 9. Reproduction appendix
Commands, hashes, generated files, logs, exact versions, and whether any fixture was changed.
