# Round 7 — Independent AI agent experiment results

**Model/provider:** Grok (xAI)
**Model version / configuration (if known):** Grok 4 (current session)
**Date:** 2026-11-03
**Tools available and actually used:** Python 3 standard library, bash, file I/O. No external LLM API metering. tiktoken NOT installed.
**Python version / OS / tokenizer version:** Python 3.x on Linux; tiktoken unavailable → no model-token counts, only bytes/chars.
**Other models' responses seen before this test?** Partial earlier rounds (Claude measurements referenced in Round 5); no full Round 7 peer results seen before execution.
**Any implementation automatically indexed/read?** No. `capabilities.py` was never opened or displayed in this session for H1 arms. Only public contracts and the registry/bind API were used.
**Fresh trials per arm:** Single exploratory run per arm in one session (EXPLORATORY SAME-SESSION). Independent fresh conversations not available in this environment.

## 1. Status and verdict

| Hypothesis | Measured, partially tested, or not tested | Provisional verdict | What would change the verdict? |
|---|---|---|---|
| H1: no-body-reading reuse | Partially tested (toy scale, same-session) | Neutral / not yet supported as superior to strong baseline | End-to-end model-token + repair measurements on multi-task suite where B beats A under realistic invalidation rates |
| H2: native authoring | Partially tested (toy grammar only) | Not supported by this packet | Trained/adapted model on general tasks showing lower cost-per-success than ordinary language under same registry |
| H3: reusable validated binding | Partially tested (toy registry) | Plausible at toy scale; security claims unsupported | Persistent binding with real revocation, environment change, and measured attention savings across long sessions |

## 2. Exact test results

| Arm | Status | Passed / total | Source files read | Retries | Notes |
|---|---|---:|---:|---:|---|
| A: normal Python API reuse | EXECUTED | 14/14 | 0 (`capabilities.py` never opened) | 0 | Strong baseline; imports only |
| B: registry and handles | EXECUTED | 14/14 | 0 | 0 | Rejected 3 near-miss/effect-denied cards from contracts alone |
| C: newly authored Python | EXECUTED | 6/6 | 0 (no reference import) | 0 | Fresh implementation of T1 |
| D: toy symbolic program | EXECUTED | 6/6 | 0 | 0 | 46-byte program; grammar-constrained |
| H3 binding checks | EXECUTED | 3/3 PASS | 0 | 0 | Effect denial + digest mismatch + successful bind |

Exact test console output:

```
=== binding_checks.py ===
PASS: unauthorized effect denied
PASS: mismatching artifact digest denied
PASS: reuse binding available

=== Arm A (submission_armA.py) ===
{"passed": 14, "total": 14, ... all cases true}

=== Arm B (submission_armB.py) ===
{"passed": 14, "total": 14, ... all cases true}

=== Arm C (controller_submission.py) ===
{"passed": 6, "total": 6, ... all cases true}

=== Arm D (controller_submission.sym) ===
{"passed": 6, "total": 6, ... all cases true}
```

## 3. Reproducible artifact/token accounting

| Artifact or generated content | Exact bytes/chars | Tokenizer & version | Exact tokens (if run) | How measured |
|---|---:|---|---:|---|
| Ordinary API documentation (baseline_api.md) | 1205 B / 1203 chars | tiktoken unavailable | NOT MEASURED | Path.read_bytes / read_text |
| Registry cards (capability_cards.md) | 1436 B / 1424 chars | — | NOT MEASURED | same |
| Activity contract | 1728 B / 1728 chars | — | NOT MEASURED | same |
| Source implementation inspected | 0 (never opened) | — | 0 | Session log |
| Python submission Arm A | 334 B / 332 chars | — | NOT MEASURED | same |
| Python submission Arm B | 783 B / 777 chars | — | NOT MEASURED | same |
| Python controller (Arm C) | 406 B / 406 chars | — | NOT MEASURED | same |
| Symbolic submission (Arm D) | 46 B / 46 chars | — | NOT MEASURED | same |
| Alias binding + 20 calls | NOT EXECUTED as separate payload measurement | — | — | — |
| Repeated contract + 20 calls | NOT EXECUTED as separate payload measurement | — | — | — |

**API-reported input tokens:** unavailable  
**API-reported output tokens:** unavailable  
**Reasoning tokens:** unavailable  
**Total cost per successful task:** unavailable (no model telemetry)

Note: Artifact size differences cannot be equated to model inference cost. Arm B submission is larger than Arm A because it embeds rejection rationale comments; a production binder would not need that text in the callable path.

## 4. Contract sufficiency and near misses

- Near-miss chosen/rejected and reason:
  - `cap:controller.logs_zero_based@1` — rejected from card text alone: restart ordinals are zero-based (`run 1 of 2` instead of `run 2 of 2`).
  - `cap:activity.rollup_by_eventid@1` — rejected from card text: partitions by individual event IDs, does not merge equivalent normalized behavior.
  - `cap:activity.rollup_and_save@1` — rejected from card text: declares `filesystem.write` effect, forbidden under pure-only policy.

- Strongest contract that looked compatible but wasn't: the zero-based controller card shares signature, purity, and overall purpose with the correct card; only the ordinal semantics differ. Signature matching alone would have accepted it.

- Did the model need to inspect implementation? No. Trigger never fired. Files opened for H1: only `baseline_api.md`, `capability_cards.md`, `activity_contract.md`, `registry.py` (API surface).

- Which behavior remained unspecified by a contract? Exact interaction of concurrent writers, clock sources for windows, and full failure modes under malformed nested structures are only partially covered even in the activity contract.

- What failed before execution vs only after tests? The three near-misses were rejected before any execution by reading the cards. The binding_checks.py also rejected the effect-denied and digest-mismatched cases before execution.

## 5. H3 binding persistence

- What information was in the initial validation? Identifier, allowed_effects set, optional expected_digest (SHA-256 of capabilities.py). Registry returns a bound callable only if effects ⊆ allowed and digest matches (when supplied).

- What information was *not* reintroduced on subsequent calls? In this toy, the bound function object can be held and called repeatedly without re-supplying the contract text. No automatic re-validation on environment change is implemented.

- How were trust, revocation, policy and environment changes handled? Only static checks at bind time. No revocation list, no environment fingerprint, no dependency-version tracking beyond the single file hash. Changing capabilities.py after bind is invisible to already-held callables.

- Does the experiment actually test persistent model familiarity, or only smaller serialized payloads? Only the latter. The model never “remembers” a binding across independent sessions; the test only shows that a host-side handle can avoid reprinting contract text inside one process.

## 6. H2 analysis

- Was the output executable, valid and behaviorally correct? Yes. The 46-byte program `@1(n:I){R(n,i){?(i=0,!7(T0,n),!7(T1,i+1,n))}}` passed all 6 T1 cases.
- Was the language shorter in **model tokens**, not only characters? Unknown — tiktoken unavailable. Character count is 46 vs 406 for the Python equivalent, but BPE fragmentation of symbols is unmeasured.
- Were symbol fragments problematic for the available tokenizer? Not tested.
- Did any silent logical error escape type/grammar checks? Not in this single correct program. The grammar rejects wrong template arity and unknown opcodes at parse time; semantic operand errors (e.g., using `i` instead of `i+1`) would still produce wrong traces and fail the behavioral tests.
- Would a dedicated operation-token model differ, and how could that be tested without assuming the answer? Yes, potentially. Fair test: same task suite and registry, three composition surfaces (ordinary Python, textual symbolic under constrained decoding, dedicated atomic tokens / typed action API), measure end-to-end tokens including repairs and exact pass rate. Toy compression ratios are irrelevant.

**Important limit stated by the protocol itself:** this toy language “is not general-purpose and does not test learned atomic-token vocabularies.” H2 remains untested at the level required by the hypothesis.

## 7. Strongest skeptical conclusion

H1 does not yet show an advantage over a strong conventional baseline that already imports library functions without reading their source. Both Arm A and Arm B achieved 14/14 with zero source inspections. The only added value of the registry in this packet is explicit near-miss rejection and effect checking — useful, but obtainable with ordinary package metadata and linters.  

H2 is supported only at the level of “a tiny hand-written symbolic program can pass the same unit tests.” It supplies no evidence about model authoring cost, token efficiency under real tokenizers, or reliability under distribution shift.  

H3’s binding mechanism works for the toy policy/digest checks but provides no measurement of attention savings across long agent sessions and no real revocation or environment binding.  

Therefore the packet does not establish that the proposed architecture reduces total cost per correctly completed task relative to competent conventional reuse.

## 8. One architecture change and one decisive experiment

**Architecture change:** Make contract obligations first-class and machine-checkable (input domain, exact observable traces where required, effect sets, concurrency assumptions). A bind operation should return not only a callable but an explicit `Coverage` result: `entailed | refuted | unknown`. `unknown` forces escalation (more tests, inspect, or human review) instead of silent acceptance.

**Decisive low-cost experiment:**  
- Same multi-task suite, same model.  
- Arm A: ordinary imports + package docs (strong baseline).  
- Arm B: registry with the coverage-result rule above, implementation hidden by default.  
- Measure: total model+tool tokens, forced inspection rate, exact behavioral match, invalidation spikes.  
- Falsification threshold: if B does not reduce tokens-per-success by a pre-registered margin (e.g., ≥20 %) while matching correctness, and inspection rate stays low, reject H1 for that capability class.

## 9. Evidence labels

- **MEASURED IN THIS SESSION:**  
  - Arm A/B/C/D pass counts (14/14, 14/14, 6/6, 6/6)  
  - binding_checks.py 3/3 PASS  
  - Artifact byte/char counts listed above  
  - Zero source inspections of capabilities.py for H1 arms  
  - Successful rejection of three near-miss/effect-denied cards from contract text alone  

- **REPORTED BY CLAUDE / GEMINI / GROK, NOT REPLICATED:**  
  - Earlier Claude artifact-token numbers (o200k_base) from Round 5  

- **HYPOTHESIS / EXTRAPOLATION:**  
  - Any claim that registry reuse saves end-to-end model tokens  
  - Any claim that the toy symbolic language improves model authoring cost or reliability  
  - Security properties beyond the toy effect/digest checks  

## 10. Files / commands / reproduction

Generated files (in packet root):

- `submission_armA.py`
- `submission_armB.py`
- `controller_submission.py`
- `controller_submission.sym`

Commands executed (all from packet root):

```bash
python3 fixtures/binding_checks.py
python3 fixtures/test_tasks.py --submission submission_armA.py
python3 fixtures/test_tasks.py --submission submission_armB.py
python3 fixtures/test_tasks.py --python-controller controller_submission.py
python3 fixtures/test_tasks.py --symbolic controller_submission.sym
```

All returned the JSON pass/fail structures shown in section 2. No `capabilities.py` source was read during the H1 arms.

---

**End of Grok Round 7 report.**
