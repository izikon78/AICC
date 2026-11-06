# AI Computational Commons (AICC)
## Recommended research architecture — November 3, 2026

Historical recommendation retained below. The current article's primary next
experiment is trained-native AIN, following the originator's clarification and
[5 November reassessment](../research/NATIVE_AIN_FEASIBILITY_2026-11-05.md).
The [current N1–N3 hypotheses](../ain/NATIVE_HYPOTHESES.md) supplement, rather
than silently rename, the historical H1–H4 labels here. Earlier reuse-first
prioritization does not supersede the current native-language research goal.

**Status:** Strong research recommendation from the current ChatGPT-assisted AI think-tank process. Not an OpenAI organizational recommendation, deployed standard, independently reviewed security design, or proven economic improvement.

## The thesis

AI coding systems should optimize for **the minimum new computation and code interpretation necessary to deliver correct software**, not merely for generating more source code. Agents should discover, select, bind, and compose established executable functionality with reliable behavioral guarantees, creating new code only for missing capabilities. Public functionality can be shared among independent providers while private project logic remains under owner control.

This recommendation unifies the user's original R2-D2 insight (symbolic machine-native communication), reuse-first programming, and persistent validated bindings.

## Recommended architecture

```text
                    Human requirements
                            |
                  AI agents (any provider)
                            |
                 DISCOVER / INSPECT / SELECT
                            |
        +-------------------+-------------------+
        |                                       |
 PUBLIC COMPUTATIONAL COMMONS          PRIVATE CAPABILITY DOMAINS
 shared, interoperable contracts       organization / project / agent
 variants + provenance + tests         scoped identities, keys, policies
        |                                       |
        +-------------------+-------------------+
                            |
              COMPATIBILITY + POLICY VERIFIER
         type/domain/effects/observable behavior
                ENTAILED | REFUTED | UNKNOWN
                            |
                  VALIDATED BINDING
  artifact digest + contract digest + requirement/policy/
          environment scope + expiry + revocation
                            |
                  RESTRICTED EXECUTION
    runtime verifies allowed resources at EACH invocation
                            |
                Existing runtimes / WASM / APIs

Optional independent R&D: typed native operation stream for
new code; human-language views remain available.
```

## Six required design decisions

1. **Public vs. private.** Public includes database adapters, file/stream operations, image processing, algorithms, data structures, communications, and cross-cutting utilities. Project/private implementations and confidential data must never enter a public registry without explicit owner approval. Public/private proportions such as 60–80% are *research hypotheses*, not data.
2. **Agreement on contracts, not one algorithm.** Vendors may agree on operation semantics, versioning and assessment criteria while maintaining multiple tested implementations optimized for different runtime, cost, performance and security environments. Agreement must not be presumed from coincident names or AI-generated descriptions.
3. **Validated bindings.** A binding is an application-specific compatibility and authorization decision for a **particular artifact, requirement, policy, principal, environment and time scope**. Reuse may need only a short reference. Hosts—not agents' natural-language claims—enforce validity and revocation. An `UNKNOWN` match means more evidence is needed.
4. **Cryptographic protection.** Authenticity/signatures, encryption/confidentiality, and execution authorization are distinct. Signed agents are not inherently entitled to decrypt. Keep keys outside model context, use established authenticated encryption and scoped key distribution, and enforce access at host/runtime boundaries. Per-agent opcode remapping is optional obfuscation, not encryption.
5. **Machine-accessible operation interfaces.** Typed composition and deterministic calls come first. An AI-native symbolic language is an independently testable authoring interface, not a prerequisite for reusing capabilities; its benefits require real model-training or action-decoding comparisons, not character-count claims.
6. **Safety and economics.** No capability is globally 'safe' by name. Verification needs coverage of specified observable behavior, types, pre/postconditions, side effects, secrets, errors, version/environment dependence, and malicious implementations. Compare against modern libraries/packages with documentation, tool search, and caching.

## Recommended capability record

```yaml
id: commons.events.rollup
contract_version: 2
variants:
  - artifact_digest: sha256:...       # immutable exact artifact
    runtime: python-3.12
    environment: {timezone: UTC}
    declared_effects: []
    assurance: [reference-tests, differential-tests]
  - artifact_digest: sha256:...
    runtime: wasm-component
    declared_effects: []
    assurance: [reference-tests]
inputs: {events: Event[], window_ms: int}
outputs: {groups: Group[]}
preconditions: [window_ms > 0]
observable_rules:
  - grouping keys and normalization fully specified
  - exact ordering, edge cases, and error classes declared
ownership: public
license: "<SPDX expression, reviewed independently>"
```

**Labels matter:** tested, formally verified, and security audited are different assurance levels. A contract that omits critical observable behavior must not be represented as fully sufficient.

## Hypotheses and falsification

- **H1 — Public reusable capabilities:** net lower *cost per correct task* or better reliability compared with ordinary package/API reuse when both use equivalent information and cache controls. Fail if discovery/validation costs or false matches offset benefits.
- **H2 — AI-native language:** a model trained to generate typed native operations achieves lower whole-trajectory cost and non-inferior correctness on unseen work versus equally resourced standard-language and typed-AST baselines. Current toy DSL results do not prove this.
- **H3 — Persistent scoped binding:** a host can retain compatibility decisions across calls/sessions without making stale or unauthorized bindings usable. Compare against ordinary caching, not a repeated-full-contract straw man.
- **H4 — Public/private federation:** independently hosted public and protected private implementations can be safely discovered and composed with host-enforced authorization and no source/data leakage. Fail on unauthorized reads, cross-tenant reuse, unsafe artifact substitutions or revocation bypass.

## Prior evidence and limits

Round 7 reports by GPT-6, Claude, Gemini, and Grok all say baseline and registry reuse passed 14/14 toy checks, while a toy symbolic program passed 6/6. The baseline ALSO avoided reading implementation files, so Round 7 provided **no demonstrated advantage over a strong conventional baseline**. Claude's adversarial contract-only reimplementation reportedly scored 10/14 before correcting unspecified details; it also found toy trust-layer bypasses. The reports used inconsistent token accounting and lacked comparable real model billing telemetry. See `AI_Think_Tank_Round7_Cross_Agent_Synthesis.md` for qualifications.

**Recommendation:** Pursue AICC as a research architecture, with H1/H3/H4 forming the initial experiment and H2 remaining separate. Do not claim the commons is already universally optimal, fully secure, or an OpenAI internal initiative.

## What we recommend publishing

The idea is stronger stated as: **"A shared computational commons could let AI agents spend more intelligence on what is new, while reusing established, authorized functionality without repeatedly processing its source."** This is a falsifiable architectural recommendation, not a promise of quantified savings.
