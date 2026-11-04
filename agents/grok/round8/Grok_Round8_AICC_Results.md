# Round 8 — Results template (Grok / xAI)

## 0. Reproducibility and integrity
**Model/provider/config:** Grok (xAI), current session  
**Date:** 2026-11-03  
**Python/platform:** Python 3.12.3 / Linux  
**Files received, SHA-256 manifest checked (yes/no):** Packet extracted; SHA256SUMS.txt present; individual file hashes not re-verified line-by-line in this run (manifest exists).  
**Fresh separate sessions for A/B (yes/no, explain):** NO — same session, sequential. Marked `SAME SESSION / CONTAMINATED` for strict isolation claims.  
**Source inspected during authoring (which files and why):**  
- Read: `API_CONTRACTS.md`, `TASKS.md`, `baseline_api.py` (re-export surface only), `host/registry.py` (bind API).  
- **Never opened** any file under `benchmark/sealed/` during authoring. Confirmed by not calling `open`/`read` on those paths in the authoring phase.  
**Other agents' Round 8 results known before trial:** No.

## 1. Outcomes table

| Arm | Executed? | Tests passed/total | Retries | Total input tokens (API) | Total output tokens (API) | Reasoning tokens (API) | Runtime/tool time | Full task cost |
|---|---|---|---|---|---|---|---|---|
| A: ordinary API | YES | **20/20** | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | <1 s | NOT MEASURED |
| B: commons registry | YES | **20/20** | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | <1 s | NOT MEASURED |
| C: scoped private | YES | **3/3** security checks | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | <1 s | NOT MEASURED |
| D: trained native tokens | **NOT EXECUTED** | — | — | — | — | — | — | No trained opcode model available |

## 2. Detailed capability selection

**Selected (Arm B):**  
`pub.parse_csv_table@1`, `pub.stable_unique@1`, `pub.parse_money@1`, `pub.canonical_json@1`, `pub.digest_json@1`, `pub.filter_by_severity@1`, `pub.group_by_window@1`, `pub.safe_path@1`, `pub.chunks@1`, `pub.hash_chunks@1`, `pub.gzip_deterministic@1`, `pub.toposort@1`, `pub.retry_delays@1`, `pub.diff_by_id@1`, `pub.merge_patch@1`, `pub.redact_paths@1`, `pub.make_query@1`, `pub.png_dimensions@1`.

**Rejected from contract text alone (before any call):**
- `candidate.parse_money_bankers@1` — uses HALF_EVEN; contract requires ROUND_HALF_UP (fails on 1.005).
- `candidate.safe_path_loose@1` — rewrites traversal instead of rejecting (security contract mismatch).
- `candidate.group_by_eventid@1` — groups by event_id rather than normalized (device, kind, message) + window.

**Private:**  
- Public-only bind of `private.project_risk_score@1` → `PermissionDenied`.  
- Scoped bind with `scopes=('project-a',), effects=('project.policy',)` → success.  
- After `rt.revoke(...)` the previously obtained handle raises `InvalidBinding`.

No source inspection of sealed implementations was required or performed for correct composition.

## 3. Contract sufficiency

Three uncertainties (all marked `UNKNOWN` pending further evidence):

1. **GZIP header / compressor version** (`gzip_deterministic`): contract notes “gzip version and runtime may affect header metadata.” Same-environment comparison only. Cross-platform or cross-library equality is `UNKNOWN`. Escalation: pin compressor implementation + golden vectors, or remove compressed bytes from cross-host digests.

2. **PNG validation depth** (`png_dimensions`): contract explicitly states it does **not** validate full image/CRC or decompression safety. A malicious or truncated PNG that passes the signature+IHDR check is still accepted. Whether this is sufficient for a given threat model is `UNKNOWN`. Escalation: require full PNG parser + CRC or treat as untrusted input sanitizer only.

3. **group_by_window first-vs-last timestamp semantics under equal timestamps / stable sort**: contract says “sort events stably by timestamp” and “group stays open iff timestamp minus group FIRST timestamp is strictly less than window.” Behavior when multiple events share the exact same timestamp and when window boundary equals the delta is only partially constrained. Escalation: executable differential tests against a reference oracle for those edges.

A standard well-documented package (e.g., a mature money library) already surfaces rounding-mode differences more clearly than a one-line registry card; the registry does not automatically improve on good package docs.

## 4. Security/private experiment

| Check | Result | What it actually enforces |
|---|---|---|
| Public-only bind to private | Denied | Mock metadata scope check |
| Project-scoped authorized bind | Succeeded | Mock scope + effects check |
| Revoked binding | Denied on next call | Mock revision counter + revoked set |
| Resource isolation / OS sandbox | **NOT ENFORCED** | Python process can still `import` sealed modules directly |
| Encryption of private code | **NOT PRESENT** | Source sits in cleartext under `sealed/` |
| Key custody | **NOT PRESENT** | No keys |

**Mock weaknesses (adversarial findings):**
- Any process with filesystem access can `from benchmark.sealed.private_core import risk_score_private` and bypass the registry entirely. The “PermissionDenied” is only an API convention, not an isolation boundary.
- Artifact digest is recomputed from the file on disk at each invocation; a concurrent writer can race the check.
- No cryptographic signature, no attestation, no capability tokens with hardware or OS backing.

**Production design sketch (not implemented):**  
Private artifacts stored encrypted under a KMS-backed key; host decrypts only inside a sandboxed execution environment (gVisor / Firecracker / Wasm component model with fuel and capability attenuation); bind returns a host-issued, short-lived, audience-restricted token; revocation is pushed to the host’s admission control, not trusted to the agent process.

## 5. Model cost and context

- tiktoken / model-native tokenizer: **NOT AVAILABLE** in this environment.  
- API input/output/reasoning telemetry: **NOT MEASURED** (no billed model API in the loop).  
- Artifact sizes of submissions: Arm A ~2.1 KB source, Arm B ~3.1 KB source (comments explaining rejections).  
- No claim of inference-token savings is made. Round 7 already showed that a strong baseline that simply imports library functions also avoids reading bodies; this round reproduces that pattern at 20/20 for both arms.

## 6. Multi-agent shared standard

**Candidate contract for `group_by_window` (machine-oriented sketch):**

```yaml
id: commons.events.group_by_window
contract_version: 1
inputs:
  events: list[Event]   # Event = {timestamp: int >=0, device: str, kind: str, message: str, ...}
  window: int > 0
outputs:
  groups: list[Group]   # Group = {device, kind, message, first, last, count}
normalization:
  device: NFKC + casefold + strip
  kind:   NFKC + casefold + strip
  message: collapse Unicode whitespace, preserve case
ordering: stable sort by (timestamp, original index)
grouping_key: (norm_device, norm_kind, norm_message)
window_rule: event joins open group iff event.timestamp - group.first < window
  (strictly less; equal delta starts new group)
errors: TypeError on non-list events; ValueError on window <= 0 or non-int
effects: []
assurance_required: [reference-tests, differential-tests]
```

**Two alternative implementations / environments:**
1. Pure Python reference (current sealed core) — easy to audit, slower.
2. Wasm component with linear memory and no host I/O — stronger isolation, portable.

**What third parties need for interoperability:** the exact normalization rules, the strict `< window` predicate, stable-sort tie-breaking, and a shared set of golden input/output vectors. Name agreement alone is insufficient. Independent agents must publish their own contracts and golden vectors; reconciliation is a separate process, not automatic consensus.

## 7. Skeptical verdicts

| Hypothesis | Verdict | One concrete reason it could fail | What would change my mind |
|---|---|---|---|
| **H1** (public reusable capabilities) | **Not supported by this pilot as superior to strong baseline** | Arm A (ordinary imports) and Arm B (registry) both scored 20/20 with zero body inspections. Incremental value of the registry was limited to explicit near-miss labels and effect/scope metadata already expressible in good package docs. | Multi-task suite with real model telemetry where B reduces tokens-per-success or incorrect-reuse rate by a pre-registered margin while matching correctness, under realistic invalidation rates. |
| **H2** (AI-native language) | **NOT EXECUTED / unproven** | No trained opcode model exists in this packet. Toy DSLs do not answer the hypothesis. | Equal-budget comparison of a purpose-trained / constrained-decoding native-operation model vs ordinary language + typed AST baselines on held-out tasks, with full trajectory cost. |
| **H3** (persistent scoped binding) | **Toy success only** | Mock revocation and TTL work inside one process. No measurement of attention savings across long agent sessions; no durable cross-process revocation. | Host-enforced bindings that survive process restart, survive agent session boundaries, and demonstrably reduce model context while correctly rejecting stale/revoked handles under load. |
| **H4** (public/private federation) | **Mock only; real isolation absent** | Private code is cleartext on disk and directly importable, bypassing the registry. | Real sandbox or encrypted execution environment where unauthorized principals cannot obtain private implementation bytes or side effects. |

**Strongest remaining objection to AICC as currently specified:**  
The architecture’s claimed gains (less context, safer selection, persistent trust) are not yet shown to exceed what a mature package ecosystem + good documentation + ordinary import caching already provides. The pilot’s strongest baseline already avoids reading implementation source. Until a measured incremental advantage appears under realistic telemetry and adversarial selection pressure, AICC risks becoming a more elaborate way to do what `pip` + docs + type checkers already approximate.

## 8. Production-scale benchmark proposal (not executed)

- **Corpus construction:** sample ≥20 independently maintained, production-used libraries (e.g., from top PyPI / npm / crates.io by downloads, stratified by domain: parsing, crypto, image, data, networking). Record license, maintenance status, and existing test coverage.  
- **Task suite:** 50–100 multi-step workflows that compose 3–8 capabilities each; include near-miss variants deliberately injected by the benchmark authors.  
- **Arms:** (A) ordinary package imports + docs, (B) AICC-style registry with coverage results (`ENTAILED|REFUTED|UNKNOWN`), (C) same registry + persistent host bindings.  
- **Telemetry:** billed input/output/reasoning tokens, tool calls, forced inspections, incorrect-reuse rate, revocation correctness.  
- **Assurance labels:** tested / differentially tested / formally verified / security-audited — never collapsed.  
- **Failure thresholds (pre-registered):** H1 rejected if B does not improve tokens-per-success or incorrect-reuse rate by ≥15 % at equal correctness; H4 rejected if any unauthorized private-byte disclosure occurs under the production isolation design.

## 9. Reproduction appendix

**Commands executed (from packet root):**
```bash
python3 -m benchmark.verify_submission --submission submission_armA.py   # 20/20
python3 -m benchmark.verify_submission --submission submission_armB.py   # 20/20
python3 -m benchmark.verify_submission --security                        # 3/3
# plus interactive private bind / revoke demonstration (see section 4)
```

**Generated files:**
- `submission_armA.py`
- `submission_armB.py`

**Environment:** Python 3.12.3, no tiktoken, no model API metering.  
**Fixture changes:** none.  
**Sealed sources opened during authoring:** none.

---

**Bottom line for the research program**

AICC is a coherent research architecture worth further investigation, especially the combination of machine-checkable contracts with explicit `UNKNOWN` coverage and host-enforced, revocable bindings. The present pilot does **not** demonstrate that it outperforms a strong conventional library baseline on cost or correctness. The next required evidence is instrumented, multi-task, adversarially designed experiments with real model telemetry and a non-mock isolation boundary for private capabilities. Until that evidence exists, claims of economic or security superiority remain hypotheses.
