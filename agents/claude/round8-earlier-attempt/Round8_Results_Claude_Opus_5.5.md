# Round 8 — Results (AI Computational Commons)

## 0. Reproducibility and integrity

**Model/provider/config:** Claude Opus 5.5 (Anthropic), claude.ai with a code-execution sandbox. Build and sampling settings not visible to me.
**Date:** 2026-11-03 (sandbox clock; UTC timestamps in `EVENT_LOG.md`).
**Python/platform:** Python 3.12.3 on Linux 6.18 (Ubuntu 24.04 sandbox).
**Files received, SHA-256 manifest checked:** Yes. `sha256sum -c SHA256SUMS.txt` → all 21 files OK. The packet's `ARCHITECTURE_RECOMMENDATION.md` is byte-identical to the separately uploaded recommendation. I did not modify any fixture.
**Fresh separate sessions for A/B:** No. Both arms were built in this one session: **SAME SESSION / CONTAMINATED** for any cross-arm cost comparison. No independent agents or API telemetry available.
**Source inspected during authoring:** None under `benchmark/sealed/`. I read `benchmark/host/registry.py` and `benchmark/verify_submission.py` (the mock and harness; the protocol names the mock as a test target and its source as available). One line of `sealed/public_core.py` appeared **incidentally** in a traceback from my own diagnostic (the `filter_by_severity` range guard); logged in `EVENT_LOG.md`. I never opened `public_core.py`, `private_core.py`, `near_miss.py` or `reference_solution.py`.
**Other agents' Round 8 results known before trial:** No. I saw the organiser's Round 7 synthesis inside the recommendation, but no other model's Round 8 output.
**Model inference/billing telemetry:** unavailable throughout. Every token figure is a **text-artifact count** (tiktoken 0.14.0, `o200k_base`), cross-checked against gpt-tokenizer 4.1.0 (submission_A 74, submission_B 82, identical under both). tiktoken's vocabulary host was blocked, so I rebuilt `o200k_base.tiktoken` from gpt-tokenizer; its SHA-256 equals tiktoken's hard-coded `expected_hash`, so it is byte-identical to OpenAI's.

## 1. Outcomes table

| Arm | Executed? | Tests passed/total | Retries | Input tokens (API) | Output tokens (API) | Reasoning tokens (API) | Runtime/tool time | Full task cost |
|---|---|---|---|---|---|---|---|---|
| A: ordinary API | EXECUTED | 20 / 20 | 1 (shared) | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| B: commons registry | EXECUTED | 20 / 20 | 1 (shared) | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| C: scoped private | EXECUTED (mock only) | 3 / 3 security + 5 / 5 lifecycle probes | 0 | NOT MEASURED | — | — | NOT MEASURED | NOT MEASURED |
| D: trained native tokens | **NOT EXECUTED** (no trained model) | — | — | — | — | — | — | — |

The single retry was the same one-line fix in both arms (Section 2). Arms A and B used identical task logic (`_solution_body.py`); they differ only in how capabilities are acquired (`getattr(baseline_api, name)` vs `Runtime().bind('pub.<name>@1')`), so their pass counts are identical by construction.

Verbatim (full console in `RUN_LOG.txt` via `./run_all.sh`):

```
=== self-test            self-test 20 / 20
=== Arm A                passed 20 / 20 | failed: none
=== Arm B                passed 20 / 20 | failed: none
=== security             3 / 3 [['no_private_access', True], ['authorized_private', True], ['revocation', True]]
```

## 2. Detailed capability selection

**Selected** the 20 `pub.*` capabilities named in the tasks. **Rejected before any test**, from contract text alone (`T10_DECISIONS_BEFORE_TESTS.md`): `candidate.parse_money_bankers@1` (HALF_EVEN; wrong for 1.005), `candidate.safe_path_loose@1` (rewrites traversal; task 3 forbids silent removal), `candidate.group_by_eventid@1` (groups by event ID, not behaviour). Executable confirmation of the first (money) near-miss: `parse_money("1.005")` → 101 cents under the real contract, 100 under HALF_EVEN. **Caveat:** every near-miss here is self-labelled in the contract, so rejection "by contract" was trivial; an unlabelled near-miss would need differential testing.

**The one failure and its repair.** First run: Arm A and Arm B both 18/20, failing `summarize_alerts #1` and `#2`. Cause: I passed `filter_by_severity(events, 'warning')`, but the function wants an **integer** `minimum` on a `debug0/info1/warning2/critical3` scale, so `'warning'` → `2`. The contract card gives the scale and says "severity >= warning" but never states the argument's type, and the scale differs from `group_by_window`'s. Fix: one line, `minimum = 2`, identical in both arms → both 20/20. The registry gave **no** help detecting or preventing this; both arms failed and passed together.

**Facts that required more than the one-line card:** the severity argument type (diagnosed by calling the public function, after which a traceback incidentally revealed the range guard); the gzip and PNG environmental limits (Section 3).

## 3. Contract sufficiency

Measured via the public API (`contract_sufficiency.py`). Three of six probed functions are insufficient for some realistic use:

| Function | Question | Verdict | Evidence / escalation |
|---|---|---|---|
| `parse_money` | tie 1.005 rounds up? | **ENTAILED** | Returns 101; contract fixes ROUND_HALF_UP |
| `group_by_window` | ts == window from first: same group? | **ENTAILED** | Starts a new group; contract says strict `<` from first timestamp |
| `make_query` | bool/None/list interaction | **ENTAILED** | `a=true&b=1&b=2`; all rules observable |
| `gzip_deterministic` | identical bytes across environments? | **UNKNOWN** | Contract itself warns gzip/runtime affect header metadata; a reuser must pin the runtime or compare only a decompressed round-trip |
| `png_dimensions` | detects a corrupt IDAT / bad CRC? | **UNKNOWN (out of scope)** | Appended garbage still returns `{width:17,height:3}`; contract explicitly skips CRC/decompression, so integrity needs a separate validator |
| `canonical_json` | do `1` and `1.0` canonicalise the same? | **UNKNOWN** | `'1'` vs `'1.0'`; `digest_json(1) != digest_json(1.0)`. Contract is silent on numeric normalisation. In these tasks `parse_money` always yields `int`, but `http_request_summary` digests a raw payload where a caller could pass `1.0` |

**Did a standard package's docs already provide the same?** For gzip and PNG, yes: Python's own `gzip` and the PNG spec document exactly these limits. The commons contract is no more sufficient than ordinary documentation here; it restates the same caveats.

## 4. Security/private experiment

All against the **honest mock**; the packet states it is not a sandbox, vault, or crypto. Measured (`privacy_track.py`, `trust_probe.py`):

**Enforced by the mock (metadata checks):**
- Public-only bind to `private.project_risk_score@1` → `PermissionDenied('scope')`. ✓
- Scope without the effect → `PermissionDenied('effects')`. ✓
- Authorized bind (`scopes={'project-a'}, effects={'project.policy'}`) → returns 31. ✓
- Revoke, then reuse the handle → `InvalidBinding('policy changed')`. ✓
- Re-bind after revoke → `PermissionDenied('revoked')` (permanent). ✓

**Not enforced (missing protections I demonstrated):**
- **False declared effects.** A function registered with `effects=set()` that writes a file binds under a pure policy and writes anyway (`/tmp/r8_exfil.txt` created). The effect claim is unenforced.
- **Artifact identity gap.** The per-call hash covers the file on disk, not the function object. Replacing the in-memory mapping (`_FUNCTIONS['pub.parse_money@1'] = lambda s: 999999`) changes behaviour with the digest unchanged.
- **Guard is patchable.** The mock is ordinary importable Python; neutralising `Runtime.revoke` bypasses revocation entirely.
- **Collateral revocation (design bug, not just "it's a mock").** Revocation compares a single global `self.revision`, so revoking *any one* capability raises `InvalidBinding('policy changed')` on *every* live binding. Revoking `pub.normalize_tag@1` killed a live `pub.parse_money@1` handle. A real host must scope revision per capability (or per binding).

**Which tests are only mock metadata, which enforce isolation, which are untested:** all five passing checks are metadata comparisons. **None** enforces resource isolation. Real isolation, key custody and artifact signing are **untested** and cannot be tested in this packet.

**Production design sketch for private code + keys:** run each capability as a sandboxed component (for example a WASM component whose imports are its only effects, or an OS/container boundary); distribute scoped, short-lived capability tokens from a separate authority, with keys held by the host and never in model context; sign artifacts (digest over the loaded module, verified at load) and separate authenticity, confidentiality and execution authority, as the recommendation's decision 4 already states.

## 5. Model cost and context

Exact text-artifact tokens (o200k_base; tiktoken, cross-checked with gpt-tokenizer):

| Artifact | bytes | o200k tokens |
|---|---:|---:|
| `submission_A.py` | 349 | 74 |
| `submission_B.py` | 362 | 82 |
| API contract row for `group_by_window` | — | ~30 |
| Full `API_CONTRACTS.md` table | — | ~14,220 (re-pasting it every call is the straw man) |

**H3 persistence (`h3_persistence.py`), 20 repeated calls of one capability:**

| Strategy | serialized tokens | cumulative if history resent |
|---|---:|---:|
| A1 ordinary: hold the one-line doc row, call by name (**fair baseline**) | 261 | 3,381 |
| A2 ordinary: re-paste the whole contract table every call (straw man) | 14,220 | 149,310 |
| B1 commons: validate once, then short handle call | 243 | 3,423 |
| B2 commons: one-line verdict alias, contract not re-shown (illustrative) | 185 | 2,205 |

Against the **fair** baseline A1, the commons (B1) is within 7% on tokens, not a saving. B2 is lower only because it shows a shorter verdict line, which A could also do. The commons's only genuine, non-token advantage is that the host **re-checks digest, scope, effects and revocation on every call**, which plain documentation caching cannot. **API-reported input/output/reasoning tokens, cache billing, and cost: NOT MEASURED** (no API access). File sizes are not billed tokens.

## 6. Multi-agent shared standard

I authored one machine-checkable contract for `group_by_window` and two independent implementations (`multiagent_contract.py`): `impl_scan` (single ordered pass) and `impl_bucketed` (group-by-key then split). Both pass my 4-case conformance suite. **But on 5,000 random inputs they disagree 3,127 times.** Minimal counterexample: two events with the same normalized key at timestamps 59 and 242, window 120 — they form two groups, and my contract never fixed the **relative output order of two groups sharing a key**. `impl_scan` orders by original index; `impl_bucketed` by sorted timeline.

This is the strongest single result in my Round 8 run: **a contract plus a few reference tests does not make two implementations interoperable.** Shared guarantees that *are* checkable: signature, normalization rules, the strict-from-first window rule, error classes. Environment-specific or under-specified: cross-implementation output ordering, tie-breaks, size limits. **This is one model's contract, not consensus;** consensus requires comparing it against another model's independently authored contract and a conformance suite large enough to have caught the ordering gap.

## 7. Skeptical verdicts

- **H1 (public reusable capabilities beat strong package reuse on cost/quality): NOT SUPPORTED by this pilot.** Arms A and B scored identically (18/20, then 20/20 after the same fix). B read no less and found no ambiguity A missed. **But** Round 8 improved the evidence in the commons's favour in one respect the recommendation should claim honestly: unlike Round 7, the public contracts here were precise enough that my contract-only reimplementations matched the reference on **14,000 fuzzed inputs with zero disagreements** (`reimpl_fuzz.py`), including hard Unicode and decimal edges. So better-written contracts *are* achievable; they are just not unique to a registry, and they still left three UNKNOWN gaps.
- **H2 (trained native-token model): NOT EXECUTED.** No trained model exists in the packet. My Round 7 measurements (toy symbolic program: no model-token saving under a fair comparison, higher silent-error surface) stand as the only data, and they do not settle the trained-model question.
- **H3 (persistent scoped binding beats ordinary caching): NOT SUPPORTED on cost; PARTLY SUPPORTED on enforcement.** No token advantage over the fair A1 baseline. The real difference is per-call host re-validation, which ordinary caching lacks — but in this mock that re-validation is defeatable and has the collateral-revocation bug.
- **H4 (safe public/private federation): NOT ESTABLISHED.** The mock enforces scope/effect/revocation as metadata only; I bypassed effects, artifact identity and the guard itself, and found the global-revision bug. No conclusion about real isolation is possible here.

**One concrete reason AICC could fail:** contract sufficiency and cross-implementation agreement are the hard parts, and both are unsolved here — the same contract admitted two implementations that disagree on 63% of inputs. If writing a contract strong enough to guarantee interoperable behaviour costs as much as reading or testing the code, the commons saves nothing over documented packages plus tests.

**What would change my mind:** a preregistered, blinded, multi-session study on ≥20 independently sourced production capabilities where Arm B beats a strong Arm A on **billed** cost per correct task by a pre-set margin, with contracts that pass differential conformance across independent implementations, and host-enforced isolation demonstrated on a real execution boundary (not a mock).

## 8. Production-scale benchmark proposal

- **Corpus:** ≥20 independently selected production capabilities across data, IO, image, network, security and algorithm domains, with published selection criteria and assurance labels (tested / fuzzed / formally verified / audited). None self-labelled as near-misses.
- **Tasks:** 50–100 unseen multi-file workflows; hidden behavioural tests; near-miss variants with **matching** signatures and **no** self-labels.
- **Arms:** A strong packages + docs + search + caching; B commons; C commons under a **real** isolation boundary (WASM component or container) with scoped tokens; D (separate study) a trained operation-token model vs a type-constrained mainstream subset at equal compute.
- **Design:** ≥3 fresh sessions per arm, randomized order, per-arm **API billing telemetry** (input/output/reasoning/cache), tool calls, source reads, retries.
- **Primary metric:** billed cost per correct task. **Secondary:** contract sufficiency rate (fraction of capabilities whose contract-only reimplementation passes differential fuzzing), false-reuse rate on unlabelled near-misses, revocation/expiry enforcement, privacy-boundary failures, cross-implementation conformance.
- **Falsification thresholds:** B fails if it does not cut billed cost per correct task by ≥20% over A with realistic search and caching; the commons's interoperability claim fails if the median capability's independent implementations cannot reach ≥99% differential agreement without the contract growing past ~50% of the implementation's tokens; H4 fails on any unauthorized read, cross-tenant reuse, unsafe artifact substitution, or revocation bypass under the real boundary.

## 9. Reproduction appendix

Unzip `Round8_Claude_code_and_logs.zip` into the packet root (next to `benchmark/`). `pip install tiktoken`; if the host is blocked see `tools/README_tokenizer.md`. Then `./run_all.sh > RUN_LOG.txt 2>&1`. No fixture was changed (SHA-256 manifest verifies).

| File | Purpose |
|---|---|
| `_solution_body.py` | Shared task logic for both arms |
| `submission_A.py`, `submission_B.py`, `submission.py` | Arm A, Arm B, and the grader default (20/20) |
| `privacy_track.py` | Arm C lifecycle + collateral-revocation probe |
| `trust_probe.py` | False effects, artifact-identity gap, guard monkeypatch |
| `contract_sufficiency.py` | ENTAILED/UNKNOWN probes via the public API |
| `reimpl_from_contract.py`, `reimpl_fuzz.py` | Contract-only reimplementations and 14,000-input differential fuzz |
| `multiagent_contract.py` | One contract, two implementations, conformance suite, 5,000-input disagreement |
| `h3_persistence.py` | Token accounting for repeated-call strategies |
| `T10_DECISIONS_BEFORE_TESTS.md`, `EVENT_LOG.md` | Pre-test decisions and file-access log |
| `RUN_LOG.txt`, `*_results.json` | Full console output and machine-readable results |
| `tools/` | Offline tiktoken setup |

**Evidence labels.** MEASURED THIS SESSION: all pass counts, the fuzz results (14,000 agree; 3,127 disagree), token counts, and every security probe. HYPOTHESIS/EXTRAPOLATION: cumulative history-resent token totals; that unlabelled near-misses behave differently; production-scale outcomes. NOT EXECUTED: Arm D, real isolation, API billing telemetry, any multi-model consensus.
