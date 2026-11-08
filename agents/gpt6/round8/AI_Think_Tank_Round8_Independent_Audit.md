# AI Computational Commons — Round 8 Independent Audit

**Date:** 2026-11-03  
**Reviewer:** GPT-6 / ChatGPT  
**Status:** Technical audit of supplied Claude and Gemini reports; *not* a multi-agent research consensus.

## Scope and integrity

- Inputs: the supplied Round 8 packet, Claude Opus 5.5 report and code/logs archive, and Gemini 3 Flash report.
- The uploaded Round 8 packet ZIP is byte-identical (SHA-256) to the originally supplied packet in this conversation.
- I extracted Claude's code into a copy of the original packet and ran the supplied tests and probes without editing the official fixture.
- No Grok Round 8 result was included in this upload. No newly trained native-opcode model was evaluated.
- Agent-reported input/output *API billing* and hidden reasoning-token measurements are not independently available in this audit.

## Reproduced results

| Item | Reproduced outcome | Interpretation |
|---|---|---|
| Official workflow tests, ordinary-library arm A | **20/20** | Correct on supplied cases |
| Official workflow tests, commons arm B | **20/20** | Correct on supplied cases; no demonstrated advantage over arm A |
| Basic mock private security checks | **3/3** | Only metadata/policy checks, not actual isolation |
| Claude contract-based reimplementation fuzzing | **14,000/14,000 agreements** across 7 functions | Promising narrowly: adequate contracts *can* guide implementation of these functions; independently authored multiple-agent compliance is not established |
| Claude two-implementation comparison | **3,127 disagreements / 5,000 generated inputs** | Real divergences, but one submitted implementation violates Claude's explicitly declared output-order rule |
| Claude trust probes | Side-effect bypass, loaded-function/artifact mismatch, and policy-guard bypass reproduced | Python mock is not an isolation boundary |
| Claude revocation probe | Revoking one capability invalidates unrelated handles | A per-capability revision/version is needed |

### Important correction to the Claude result

Claude's new `multiagent_contract.py` says: `output_order: groups in order of first creation during the ordered scan`. Its `impl_scan` sorts events by timestamp before creating groups. Its `impl_bucketed` instead sorts final groups by the **original input index** of the first event. These are not equivalent.

Minimal counterexample, two events with the same normalized key and timestamps **242, 59** supplied in that input order, with window 120:

- `impl_scan`: two groups ordered **59, 242**.
- `impl_bucketed`: two groups ordered **242, 59**.

The 3,127 disagreements therefore do **not** prove Claude's newly written contract omitted the output ordering. They show that a few conformance tests failed to detect an implementation violating an explicitly stated contract. The *original common API contract* in the experimental packet was itself less precise about output order, which remains a genuine specification concern.

Also, Claude authored *both* alternatives. They are two implementations, not independently authored implementations by different agents.

## Gemini reconciliation needed

Gemini reports 24/24 test passes, but the frozen official `benchmark/verify_submission.py` contains exactly **20** workflow cases (and Gemini's quoted case list names only those 20). Original packet sizes:

| Artifact | Frozen packet bytes | Gemini-reported bytes |
|---|---:|---:|
| `benchmark/public/API_CONTRACTS.md` | 4,829 | 3,184 |
| `benchmark/public/baseline_api.py` | 433 | 512 |
| `benchmark/sealed/public_core.py` | 8,794 | 5,420 |

These cannot be pooled into a comparable token experiment without Gemini's actual tested artifacts and logs. Its document token counts are not documented end-to-end API billing telemetry. This does not establish that Gemini fabricated tests; its actual inputs may have differed.

## Cost results: strongest fair baseline

Claude's reported `o200k_base` text-token accounting for 20 repeated calls:

| Scenario | Serialized tokens | Cumulative tokens if history resent |
|---|---:|---:|
| Ordinary library, one-line documentation cached (fair baseline) | 261 | 3,381 |
| Commons, bind then call (B1) | 243 | 3,423 |
| Commons, compressed verdict alias (B2) | 185 | 2,205 |

The fair difference between A1 and B1 is small, and B2's optimization could be applied to an ordinary library too. The large reductions versus repeatedly re-pasting a full contract are not evidence of a unique AICC advantage. These are *serialized text/token measurements*, not billed per-task inference costs.

## Security results

The public/private separation, scope and revocation policy are plausible designs, but this packet has no production sandbox, cryptographic authorization, protected key custody, or loaded-artifact identity attestation. The three passing toy checks do not demonstrate an agent-private confidentiality guarantee. Key next controls include isolation outside agent-accessible Python, deny-by-default effects, precise per-capability revocation, code identity checked against what is executed, and tenant- and purpose-scoped authorization. Encryption at rest/in transit is separate from execution safety.

## Scientific verdict

- **H1 (reuse-first):** feasible; not yet superior to a strong documented existing-library baseline.
- **H2 (new AI-native language):** untested in this round; no native trained-opcode model was run.
- **H3 (persistent bindings):** the idea is implementable; distinct economic value beyond ordinary caching unproven.
- **H4 (federated public/private commons):** promising as an architectural target, not established by this mock or small task suite.

The valuable result is **a much sharper testable research agenda**, not a proof of superior efficiency.

## Proposed next step: Round 8.1 corrections before Round 9

1. **Freeze one identical artifact set** with SHA-256 manifest and report raw full test output. Require same official 20-case suite plus an explicit extended test suite when applicable.
2. **Independent implementations of the same contract.** Have *different* models implement a shared frozen specification without reading each other's code, and third-party grade 1,000+ edge/adversarial inputs. Compare complete *observable traces*, ordering, errors, Unicode, side effects, and environment assumptions.
3. **Contract checking:** return `ENTAILED`, `REFUTED`, or `UNKNOWN` for a proposed substitution. Require escalation on unknown.
4. **Fair reuse baseline:** ordinary packages + good docs + retrieval + caching vs AICC with exactly the same information/permissions; measure input, output, reasoning, cached billing, repair and integration cost per correct task.
5. **Real private boundary:** test an actual sandbox/container/WASM boundary, loaded module digest, no secret access, scoped authorization, revocation and malicious-effect attempts. No public/private security claims from mock metadata checks alone.
6. **H2 independently:** native-token/typed-action models require a separate experiment with an adapted model at equal compute; don't infer H2 from minified text files.

**Implication for article:** AICC should remain a **recommended architecture to investigate**, not a demonstrated breakthrough. The R2-D2 motivation and the possibility of shared public/private capability knowledge remain compelling open hypotheses.
