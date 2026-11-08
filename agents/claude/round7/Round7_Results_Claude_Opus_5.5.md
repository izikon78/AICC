# Round 7 — Independent AI agent experiment results

**Model/provider:** Claude Opus 5.5 (Anthropic)
**Model version / configuration (if known):** claude.ai chat with a code-execution sandbox; build and sampling settings not visible to me.
**Date:** 2026-11-03 (sandbox clock, UTC timestamps in `EVENT_LOG.md`)
**Tools available and actually used:** bash, Python 3.12.3, Node.js 22.22.2, tiktoken 0.14.0, the npm package gpt-tokenizer 4.1.0 (only to rebuild tiktoken's vocabulary files offline). No model API key, so no independent agents and no API usage telemetry. Web search was available but not used for this round.
**Python version / OS / tokenizer version:** Python 3.12.3 on Linux 6.18 (Ubuntu 24.04 sandbox). tiktoken 0.14.0 with `o200k_base` (primary) and `cl100k_base`. tiktoken's download host was blocked, so I rebuilt both vocabulary files from gpt-tokenizer 4.1.0. Their SHA-256 equals the `expected_hash` hard-coded in tiktoken (o200k_base `446a9538…`, cl100k_base `223921b7…`), so they are byte-identical to OpenAI's files. The packet's `token_measure.py` ran unmodified.
**Other models' responses seen before this test?** No Round 7 results from any model. Earlier in this same conversation I saw the organiser's restatement of questions attributed to Grok and Gemini (v3 brief) and the Round 5 feedback, but no other model's measurements. **Prior exposure:** I implemented the T1 C# example myself in Rounds 2–5 of this conversation.
**Any implementation automatically indexed/read?** No. `fixtures/capabilities.py` was never opened or printed. `token_measure.py` hashed and tokenised it without displaying it. `registry.py` and `binding_checks.py` were read only after all reuse trials were complete, for the reason logged in `EVENT_LOG.md`. One line of `registry.py` appeared in a traceback during a counterexample run.
**Fresh trials per arm:** 1 per arm, all in this one session: **EXPLORATORY SAME-SESSION**. Independent fresh trials: **NOT EXECUTED** (no access to independent agents or an API).

## 1. Status and verdict

| Hypothesis | Measured, partially tested, or not tested | Provisional verdict | What would change the verdict? |
|---|---|---|---|
| H1: no-body-reading reuse | **Partially tested.** Correctness, documentation tokens and contract sufficiency measured on this packet | **No incremental benefit shown over the strong baseline here.** Arms A and B both passed 14/14 with zero source reads and zero retries. B read 337 *more* documentation tokens (976 against 639, o200k), because its cards point to the same contracts A read. The core premise, using code from its contract without reading it, **failed a direct test**: an implementation faithful to the written contract failed 4 of 5 hidden rollup cases, because the reference depends on two choices the contract never states | A multi-session, multi-capability benchmark in which B (handles plus machine-checked contracts) beats A on cost per correct task by a pre-registered margin, with contracts that pass a differential sufficiency test (Section 8) |
| H2: native authoring | **Toy feasibility measured; H2 itself NOT TESTED** (no trained or adapted model) | **Toy evidence is negative on cost.** The symbolic program passed 6/6, but under a fair comparison it is not shorter in model tokens (29 o200k against 27 for Python using the same host-held templates). It required 1,143 tokens of grammar documentation, accepted 22 of 246 single-token mutations that run but give wrong output, and the parser has a crash bug and an identifier-lexing hazard | A trained or adapted opcode model that beats a type-constrained mainstream-language subset at equal compute on held-out tasks with exact-trace grading |
| H3: reusable validated binding | **Partially tested.** Payload sizes measured; toy checks pass 3/3; three trust probes; my prototype tested against six change types | **Payload reduction is real but mostly a straw-man comparison; trust is not established by the packet's binding.** Twenty calls cost 6,030 tokens with the contract reprinted every time, 1,062 with the contract shown once and full handles, 735 with an alias, and 230 with one-line verdicts. But the toy binding let a capability declared pure write a file, passed its digest check while tampered code ran, and invalidated every handle after one unrelated comment | Cross-session agent experiments showing fewer context tokens *and* no rise in defects with cached decisions, plus runtime enforcement that blocks undeclared effects in a real sandbox |

## 2. Exact test results

| Arm | Status (EXECUTED / NOT EXECUTED / CONTAMINATED) | Passed / total | Source files read | Retries | Notes |
|---|---|---:|---:|---:|---|
| A: normal Python API reuse | EXECUTED, EXPLORATORY SAME-SESSION | 14 / 14 | 0 | 0 | Two delegating wrappers written from `baseline_api.md` and `activity_contract.md` |
| B: registry and handles | EXECUTED, EXPLORATORY SAME-SESSION | 14 / 14 | 0 | 0 | Binds `cap:controller.logs@1` and `cap:activity.rollup@1` with `allowed_effects=()`. `expected_digest` was **not** passed, so the binding was not pinned |
| C: newly authored Python | EXECUTED; **CONTAMINATED by prior exposure** (same example implemented in Rounds 2–5) | 6 / 6 | 0 | 0 | Raises TypeError for bool, mirroring C#'s static `int` |
| D: toy symbolic program | EXECUTED; same prior-exposure caveat | 6 / 6 | 1 (`symbolic_runtime.py`, grammar documentation as the protocol directs) | 0 | 45-byte program |
| H3 binding checks | EXECUTED | 3 / 3 PASS | 2, after trials (`registry.py`, `binding_checks.py`) | 0 | Toy checks only; see Sections 4 and 5 |
| Counterexample: zero-based logger | EXECUTED | 11 / 14 | 0 | n/a | Fails n = 2, 3, 17; passes n ≤ 1 |
| Counterexample: rollup by event ID | EXECUTED | 12 / 14 | 0 | n/a | Fails rollup cases 1 and 3 |
| Counterexample: rollup and save | EXECUTED | denied at bind | 0 | n/a | `CapabilityDenied: denied effects: ['filesystem.write']` |
| Held-out adversarial tests (mine) | EXECUTED | 29 / 29 contract-stated checks | 0 | n/a | Plus 10 behaviours the contract leaves open, recorded in Section 4 |
| Contract-only reimplementation (mine) | EXECUTED | 10 / 14 | 0 | n/a | Fails rollup cases 1–4; cause isolated in Section 4 |

Verbatim console excerpts (full output in `RUN_LOG.txt`, produced by `./run_all.sh`):

```
=================================================================== ARM A: python fixtures/test_tasks.py --submission submission.py
{
  "passed": 14,
  "total": 14,
=================================================================== ARM B: python fixtures/test_tasks.py --submission submission_registry.py
{
  "passed": 14,
  "total": 14,
=================================================================== ARM C: python fixtures/test_tasks.py --python-controller controller_submission.py
{
  "passed": 6,
  "total": 6,
=================================================================== ARM D: python fixtures/test_tasks.py --symbolic controller_submission.sym
{
  "passed": 6,
  "total": 6,
=================================================================== H3: python fixtures/binding_checks.py
PASS: unauthorized effect denied
PASS: mismatching artifact digest denied
PASS: reuse binding available
=================================================================== COUNTEREXAMPLE zero_based
{"passed": 11, "total": 14, "failed": ["controller n=2", "controller n=3", "controller n=17"]}
=================================================================== COUNTEREXAMPLE by_eventid
{"passed": 12, "total": 14, "failed": ["rollup case 1", "rollup case 3"]}
=================================================================== COUNTEREXAMPLE and_save
registry.CapabilityDenied: denied effects: ['filesystem.write']
```

## 3. Reproducible artifact/token accounting

All token counts: tiktoken 0.14.0, `o200k_base` (cl100k_base in brackets where measured). These are text-artefact counts, not model inference.

| Artifact or generated content | Exact bytes/chars | Tokenizer & version | Exact tokens (if run) | How measured |
|---|---:|---|---:|---|
| Ordinary API documentation (Arm A read `baseline_api.md` + `activity_contract.md`) | 2,933 bytes (1,205 + 1,728) | tiktoken 0.14.0 o200k_base | 639 (264 + 375) | `fixtures/token_measure.py`, unmodified |
| Registry card + matching contract (Arm B read `capability_cards.md` + both contracts) | 4,369 bytes (1,436 + 1,205 + 1,728) | same | 976 (337 + 264 + 375) | `fixtures/token_measure.py` |
| Source implementation inspected | 0 (none inspected). For reference, `capabilities.py` = 5,319 bytes | same | 0 read; the avoided file is 1,206 tokens | `token_measure.py`, which tokenises without displaying |
| Python submission (Arm C file / function only) | 549 / 342 bytes | same | 139 [138] / 97 [95] | `h3_payloads.py` |
| Symbolic submission (Arm D) | 45 bytes | same | 29 [29] | `h3_payloads.py` |
| Alias binding + 20 calls (contract once, then alias) | 2,771 bytes | same | 735 [730] | `h3_payloads.py`; exact payload in `h3_payloads/` |
| Repeated contract + 20 calls | 25,731 bytes | same | 6,030 [5,980] | `h3_payloads.py`; exact payload in `h3_payloads/` |
| *Extra:* contract once, full handles, no alias | 4,023 bytes | same | 1,062 [1,039] | `h3_payloads.py` |
| *Extra, illustrative design:* one-line verdicts + alias, contract never re-shown | 517 bytes | same | 230 [228] | `h3_payloads.py` |
| *Extra:* fair Python with the same host-held templates as Arm D | 61 bytes | same | 27 | `h2_symbolic_probe.py` |
| *Extra:* grammar documentation the Arm D author read (`symbolic_runtime.py`) | 4,573 bytes | same | 1,143 | `token_measure.py` |

**Derived, not measured inference:** if each of the 20 calls were a separate model turn that resends the whole history, cumulative input would be 61,850 tokens (contract repeated), 16,330 (contract once, full handles), 13,240 (contract once, alias) and 3,140 (verdict lines). This is arithmetic on measured payloads under a stated assumption, with no prompt caching.

**API-reported input tokens:** unavailable
**API-reported output tokens:** unavailable
**Reasoning tokens:** unavailable
**Total cost per successful task:** unavailable. **TOTAL MODEL TOKENS: UNKNOWN.**

## 4. Contract sufficiency and near misses

- **Near-miss chosen/rejected and reason** (recorded in `T3_DECISIONS_BEFORE_TESTS.md` before any test ran). Selected `cap:controller.logs@1` and `cap:activity.rollup@1`. Rejected `controller.logs_zero_based` (card states a zero-based restart ordinal; T1 needs i+1), `activity.rollup_by_eventid` (card states it partitions by event ID, so repeats are not aggregated) and `activity.rollup_and_save` (declares `filesystem.write`; the policy is pure). Executable confirmation: 11/14, 12/14, and denied at bind. **Caveat:** every near-miss card announces its own defect, so rejection "by contract alone" was trivial here. The zero-based candidate passes every case with n ≤ 1, so a test suite without restarts would have accepted it.
- **Strongest contract that looked compatible but wasn't: `activity_contract.md` itself, as a basis for using code without reading it.** My independent implementation, written only from that contract with literal readings, scored 10/14 (rollup cases 1–4 failed). Changing one reading at a time isolated the cause:

  | Variant | Harness |
  |---|---:|
  | Literal reading of the contract | 10 / 14 |
  | + severity reported as a name ("critical") instead of the contract's 0–2 scale | 11 / 14 |
  | + severity trimmed before matching | 11 / 14 |
  | + message trimmed at the edges and split on any Unicode whitespace (contract: "collapsing internal whitespace") | **14 / 14** |

  With both hidden choices adopted, my implementation agreed with the reused capability on **2,100 / 2,100** fuzzed workloads. With the literal reading, the disagreement attributable to each ambiguity, excluding severity format, was 264/300 (padded severity), 263/300 (message edge whitespace) and 261/300 (non-breaking space). The controller contract promises "decimal formatting", yet the reused capability returns `['Starting controller service for True runs']` for `runs=True`.
- **Did the model need to inspect implementation? Trigger and exact file:** No. `capabilities.py` was never opened. `registry.py` and `binding_checks.py` were read after all trials, solely to answer T3/H3's question about what the toy check establishes.
- **Which behavior remained unspecified by a contract?** Observed in the reused capability (UNSPEC in `adversarial_contract_tests.py`):
  1. Severity output representation (`'critical'`).
  2. Severity matched after trimming (`' info '` accepted).
  3. Message edges trimmed.
  4. Non-breaking space treated as whitespace.
  5. Sort key and output use trimmed IDs.
  6. Duplicate IDs counted twice.
  7. Extra keys accepted.
  8. Parameter errors win when both events and parameters are invalid.
  9. `controller_logs(True)` prints "True".
  10. `controller_logs(3.0)` raises TypeError.
- **What failed before execution vs only after tests?**
  - *Before execution:* the three labelled near-misses, by reading cards; `rollup_and_save`, mechanically refused at bind.
  - *Only after tests:* the restart-ordinal error (had its card not admitted it), the event-ID aggregation error, both hidden contract choices, and the bool formatting.
  - *Only with runtime controls:* a capability that *declares* no effects but writes a file. The toy registry bound and ran it; a CPython audit hook blocked the write before it happened (`h3_trust_probe.py`). An agent declaring a component safe proved nothing in either case.

## 5. H3 binding persistence

- **What information was in the initial validation?**
  - *Packet registry:* handle ID; declared effects against caller-supplied `allowed_effects`; an optional SHA-256 of the whole `capabilities.py` file. Arm B did not pass the digest.
  - *My prototype* (`h3_binding_cache.py`): additionally, a per-function digest of the code that will execute, compared with a manifest produced by a separate clean process; contract digest; obligation digest; policy digest; environment digest; verifier version; three executable tests.
- **What information was *not* reintroduced on subsequent calls?** The contract text and the tests. The 20 calls used `c(k)` and `r(batch_k, 600, 1)`. The prototype re-checked every key component and the revocation list on each call without showing anything to a model: one full validation, then 20 alias calls.
- **How were trust, revocation, policy and environment changes handled?**
  - *The packet's registry handles none of them.* It has no revocation, no environment, requirement or policy in the binding, and `bind` returns the bare function with full interpreter authority. Probes showed three failures: (a) a capability declared pure bound under `allowed_effects=()` and wrote a file; (b) with a tampered `capabilities` module already in memory, `bind(..., expected_digest=FILE_HASH)` passed and the handle returned `['Starting controller service for 2 runs', 'EXFILTRATED']`, because the digest hashes the file on disk, not the code that runs; (c) appending one comment changed the single file digest and denied every handle.
  - *My prototype* raised a named `StaleBinding` for each of: locale change, new obligation, policy change, contract text change, implementation replaced in-process, and revoked digest. It refused tampered code at validation, and its per-function digests did not change after the unrelated appended comment. It is not a security mechanism: in-process code can patch it, and it has no signatures or isolation. Its locale check is conservative, since Python's integer formatting here ignores locale.
  - *What this toy check does not establish about real zero-trust security:* publisher or artefact authenticity (the digest is unsigned and optional); integrity of loaded code (TOCTOU shown above); enforcement of effects (they are self-declared; shown above); any guarantee about caller policy (it is caller-asserted); revocation, expiry or scope; isolation; supply-chain provenance; environment binding; cross-process or cross-agent trust.
- **Does the experiment actually test persistent model familiarity, or only smaller serialized payloads?** Only smaller serialized payloads. In a real conversation, a contract supplied once stays in the history and is processed on every turn (13,240 cumulative tokens in the derived estimate). Reprinting it before every call is a straw man no agent would use. Cross-session persistence, where H3 should matter most, was **NOT EXECUTED**.

## 6. H2 analysis

- **Was the output executable, valid and behaviorally correct?** Yes: 6/6 on the first attempt, with zero revisions. This is contaminated by my prior exposure to T1 and by having read the full runtime source, which revealed the lexer's details.
- **Was the language shorter in model tokens, not only characters?** Not under a fair comparison. The symbolic program is 29 o200k tokens; Python with the same host-held templates is 27; Python with the strings inline is 44; Arm C's full file is 139, including docstring and type check. The apparent saving comes from moving the message strings into the runtime, not from the notation. The author also needed the 1,143-token grammar file.
- **Were symbol fragments problematic for the available tokenizer?** Yes. o200k split the 45-byte program into 29 tokens, about 1.6 bytes per token against about 3.5 for the Python function. Pieces included `'(n'`, `':I'`, `'){'`, `',!'` and `'(T'`; no opcode was a single token.
- **Did any silent logical error escape type/grammar checks?** Yes. Of 246 single-token mutations of the Arm D program:

  | Outcome | Mutants |
  |---|---:|
  | Rejected by grammar | 202 (82.1%) |
  | Parser crash with a raw `ValueError` | 3 (1.2%) |
  | Crashed while running | 10 (4.1%) |
  | **Silently wrong** | **22 (8.9%)** |
  | Harmless | 9 (3.7%) |

  Silently wrong examples include `?(n=0,…)` and `?(i=1,…)`. The parser crash is a bug: after `+`, `term` calls `int()` without checking for a digit, for example `R(n+i){…}`. The lexer also rejects identifiers that begin with `R` or `I`, or with `T0`/`T1`, such as `Runs`, `Idx`, `Items` and `T1x`, because its alternation matches those tokens first. Outside the tested domain the arms diverge on `True`: the symbolic runtime raises TypeError, the reused Python capability prints "True runs", and Arm C raises TypeError.
- **Would a dedicated operation-token model differ, and how could that be tested without assuming the answer?** Possibly; this packet cannot tell. Test it with one open-weight base model and three decoders over the same held-out tasks graded by exact traces: (1) unconstrained Python; (2) a type-constrained strict Python subset; (3) a dedicated-token opcode language, fine-tuned on validated pairs with replay of original-language data. Give each the same search compute and measure pass rate, whole-trajectory tokens, latency and silently wrong edits. H2's distinctive claim stands only if (3) beats (2), not merely (1).

## 7. Strongest skeptical conclusion

**H1.** In this packet the registry arm adds nothing measurable over a strong baseline that already calls documented library functions without reading their source. It reads more documentation and achieves the same result. Its central premise, that a contract lets an agent use code it never reads, failed a direct test: code faithful to the written contract fails the hidden tests, because the reference depends on choices the contract never states. Reuse worked here because the tests were written against the implementation, not because the contract was sufficient. Contract sufficiency, not the registry, is the unsolved problem, and it applies equally to ordinary libraries.

**H2.** The toy notation saved no model tokens under a fair comparison, needed a grammar document roughly as large as the implementation H1 avoids reading, and showed a nonzero silent-error surface plus two tooling defects. Nothing here supports authoring in a new notation with existing models; the trained-model question remains open and untested.

**H3.** Smaller payloads are trivially achievable. The hard part, keeping correctness and authorisation valid as things change, is not delivered by a declared-effects table and an optional file hash. Without runtime enforcement and digests of the code that actually runs, cached bindings risk becoming cached false confidence.

## 8. One architecture change and one decisive experiment

**Change: verify contract sufficiency before binding, and bind to the code that runs.** Each capability should ship a machine-checkable contract, an oracle test suite, and at least one independent contract-satisfying implementation or mutant set. The registry runs differential tests between them, and refuses to mark a contract sufficient while contract-satisfying behaviours disagree on any caller-observable output. In this packet that would have flagged severity representation and message trimming. Bindings key on per-function digests checked against a trusted manifest (as in `h3_binding_cache.py`), and calls run under a runtime effect guard.

**Low-cost decisive experiment.** Take 20 capabilities from real libraries. Have agents write implementations from the contracts alone, with no source. Fuzz each against the real implementation, tighten the contract until agreement, and record the tokens each tightening adds.
- *Strong baseline:* Arm A, ordinary API plus documentation.
- *Falsification threshold:* if the median contract cannot reach 90% fuzz agreement without growing beyond 50% of the implementation's tokens, H1's "use without reading" premise fails for that class of code.
- *H3 companion:* fresh agent sessions with and without a verdict cache. Cached decisions must cut context tokens by at least 30% with no increase in defects.

## 9. Evidence labels

- **MEASURED IN THIS SESSION:**
  - Arms A–D pass counts.
  - Binding checks 3/3.
  - Counterexample scores (11/14, 12/14, bind denial).
  - 29/29 contract-stated checks and the 10 unspecified behaviours.
  - Contract-only reimplementation 10/14 and the variant attribution.
  - Fuzz results, including 2,100/2,100 agreement for variant V3.
  - All byte and token counts in Section 3 (tiktoken 0.14.0, o200k_base and cl100k_base).
  - H2 mutation counts, the lexing hazard and the parser crash.
  - H3 trust probes (a)–(c).
  - The prototype's invalidation results.
- **REPORTED BY CLAUDE / GEMINI / GROK, NOT REPLICATED:** none from other models in this round. Organiser's note: sample solutions passed 14/14 and 6/6. That was not replicated; I used my own solutions.
- **HYPOTHESIS / EXTRAPOLATION:**
  - Cumulative history-resent token totals: derived arithmetic.
  - That real near-misses will not label themselves.
  - That contract-sufficiency failures generalise beyond this fixture.
  - Any outcome for a dedicated-token model.
  - Cross-session behaviour of agents with or without cached decisions.

## 10. Files / commands / reproduction

Unzip `Round7_Claude_code_and_logs.zip` into the packet root, next to `fixtures/`.

- **Tokenizer setup:** `pip install tiktoken`. If the download host is blocked, see `tools/README_tokenizer.md`.
- **Run everything:** `./run_all.sh > RUN_LOG.txt 2>&1`.

| File | Purpose |
|---|---|
| `submission.py` | Arm A wrappers |
| `submission_registry.py` | Arm B wrappers via `registry.bind` |
| `controller_submission.py` | Arm C |
| `controller_submission.sym` | Arm D: `@1(n:I){R(n,i){?(i=0,!7(T0,n),!7(T1,i+1,n))}}` |
| `counterexamples/submission_*.py` | The three rejected candidates in an otherwise identical wrapper |
| `adversarial_contract_tests.py` | Held-out contract-derived tests, run black-box |
| `contract_reimpl.py`, `variants/` | Independent contract-only implementation and single-change variants |
| `differential_fuzz.py` | Reused capability against the contract-only implementation, attributed by feature |
| `h2_symbolic_probe.py` | Mutations, lexing hazard, bool divergence, fair token comparison |
| `h3_payloads.py`, `h3_payloads/` | Exact serialised payloads for the 20-call comparison |
| `h3_trust_probe.py` | Lying capability with audit-hook guard, digest-versus-loaded-code gap, over-invalidation |
| `h3_binding_cache.py` | Scoped, revocable binding prototype with self-test |
| `T3_DECISIONS_BEFORE_TESTS.md`, `EVENT_LOG.md` | Decision record and file-access log |
| `RUN_LOG.txt` | Full verbatim console output |
| `*_results*.json` | Machine-readable results |
| `tools/export_ranks.js`, `tools/README_tokenizer.md` | Offline tiktoken setup |
