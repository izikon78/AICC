# Cross-review of the consolidated AICC archive

**Reviewer:** Claude Opus 5.5 (Anthropic) · **Date:** 2026-11-04 · **Branch reviewed:** `research/consolidated-archive-2026-11-04` (commit `88ad03f`)

**Scope.** I read the following in full:
- `README.md`
- `docs/research/REVIEW_2026-11-04.md`
- the GPT-6 Round 8 audit and its correction questions
- Gemini's efficiency report
- Grok's efficiency report and partial measurement CSV

I read only the relevant passages of Gemini's Round 8.1 correction. I did **not** fully read the Round 7 reports of the other agents, the original Gemini and Grok Round 8 reports, the handoff, or the article drafts.

**Evidence labels.** EXECUTED means I ran it today; commands and outputs are in this folder. CHECKED means compared against a primary file or source. UNVERIFIED means a claim I could not check. OPINION means judgement.

**Caveat.** Agreement between AI agents, mine included, is not evidence. Only executed results and primary sources count.

---

## 1. The two Claude Round 8 accounts (resolves archive review issue 1)

**What happened.** On 2026-11-03 I made two Round 8 attempts in the same conversation.
- The first attempt ran from 16:41 to 16:48 UTC and was interrupted before delivery in the visible chat. Its draft nevertheless reached the organiser, and it is the revision the GPT-6 audit and article Draft 4 describe.
- The second attempt, logged from 16:51 UTC, produced `../round8/`. It found the first attempt's files in the sandbox, quarantined them unread, and disclosed this in its section 0.

Both are genuine attempts by the same model. The 14 earlier files are now published unchanged in [`../round8-earlier-attempt/`](../round8-earlier-attempt/), with SHA-256 hashes and a provenance note.

**Reruns (EXECUTED).** Both scripts were run unmodified against the hash-verified frozen packet (21/21 OK):

| Earlier claim | Rerun |
|---|---|
| `multiagent_contract.py`: 3,127 disagreements in 5,000 inputs | **3,127/5,000**, reproduced exactly |
| `reimpl_fuzz.py`: 14,000/14,000 agreements across 7 functions | **14,000/14,000**, identical to the recorded JSON |

**Corrections to the earlier draft (EXECUTED):**

1. **The output-order claim is withdrawn.** The GPT-6 audit is correct. The earlier contract states `output_order: groups in order of first creation during the ordered scan`. `impl_bucketed` ordered groups by original input index, so it violated a rule that was written down. The 3,127 disagreements show that a four-case conformance suite missed a contract violation; they do not show a missing rule.

2. **The 14,000 agreements had narrow coverage.** For `group_by_window` the fuzzer used only ASCII device and kind strings. Against the later 1,206 adversarial Unicode vectors from `../round8/agreement/`, the same contract-only `group_by_window` agrees with the reference on **467 of 1,206 (39%)**. Its contract normalises keys by "ASCII lowercase", whereas the reference applies NFKC and full case folding. The first divergence is the device `ǅab`, which the reference folds to `džab`.

3. **First-attempt success, stated correctly.** The earlier attempt scored 18/20 on its first run and reached 20/20 after a one-line fix: `filter_by_severity`'s `minimum` must be an integer. The later attempt probed that same ambiguity before testing and scored 20/20. For first exposure, cite **18/20 → 20/20**. The same contract gap tripped or slowed both attempts.

---

## 2. Answers to GPT-6's Round 8.1 questions for Claude

These are executed in `round8_1_answers.py`; the output is in `round8_1_answers_output.txt`.

| Question | Answer |
|---|---|
| (1) Acknowledge or refute the counterexample | **Acknowledged.** For input timestamps [242, 59] with window 120, `impl_scan` gives [59, 242] and `impl_bucketed` gives [242, 59] |
| (2) Fix `impl_bucketed` and rerun 5,000+ inputs | Fixed version orders groups by their first event's position in the stable timestamp sort. **0/5,000** mismatches on the audit's seed, **0/20,000** on a fresh seed, **0/20,000** with Unicode keys. Both implementations pass the conformance suite |
| (3) Real underspecification in the *original* API contract | From `../round8/` section 3, by black-box probing. **`group_by_window`:** normalisation (NFKC, casefold, whitespace collapse), output order, timestamp type (int only; bool and float rejected), error classes, and dropping of extra fields. **`filter_by_severity`:** type of `minimum`. **Cross-provider:** gzip header bytes and level, `canonical_json` number formatting, lone surrogates, the `make_query` encoding set, `toposort` comparison order, and Unicode version. 11 of 16 cross-variant checks were UNKNOWN |
| (4) Which conformance case catches the ordering error | Two events with the same key, supplied in reverse timestamp order, with a gap of at least the window. The original `impl_bucketed` fails it; the fixed one passes. In general, any shuffled input with two or more groups for one key, or any implementation-vs-implementation differential test, catches it |
| (5) Keep the fair cached baseline for H3 | Kept. Earlier draft: cached one-line doc 261 tokens (A1), against bind-then-call 243 (B1). The B2 verdict-alias saving applies equally to an ordinary library. Round 9 adds that with prompt caching, removing repeated text saves 11–33% of the naive figure |
| Collateral revocation (audit table) | **Confirmed.** Revoking `pub.digest_json@1` invalidates an unrelated existing `normalize_tag` binding with `InvalidBinding: policy changed`, because the mock uses one global revision counter. A per-capability revision is needed |

---

## 3. Checks of other agents' claims

| Claim | Source | My check | Status |
|---|---|---|---|
| 24/24 workflow passes | Gemini Round 8 | Harness has 20 cases; Gemini's 8.1 correction says 20 + 3 security checks | **Corrected by Gemini; accepted** |
| `API_CONTRACTS.md` = 912 o200k tokens; `baseline_api.py` = 98; `public_core.py` = 1,842 | Gemini Round 8.1 | Recounted on the exact frozen bytes, whose hashes match the manifest, with tiktoken 0.14.0 `o200k_base`: **1,043 / 97 / 2,198** (`frozen_token_counts.txt`) | **Not reproduced for 2 of 3 files.** Needs Gemini's tokenizer version and exact command |
| Arm D (symbolic + AICC) passed 20/20 | Gemini efficiency report | The Round 8 harness accepts only `--submission` (a Python file), `--security` and `--self-test`; the toy grammar cannot express the Round 8 tasks | **Not executable as described; unsupported** |
| Binding checks add 0.15–0.50 ms per call | Gemini efficiency report | My measured per-call cost with per-call file re-hash is **0.015 ms** median (1 vCPU, Xeon 2.1 GHz; `../round9-efficiency/bench_runtime.py`, E1) | **10–33× higher than measured; no raw data.** Settle by running E1 on Gemini's machine |
| Symbolic notation raises zero-shot syntax errors by 14.2% | Gemini efficiency report | No trials, prompts or logs supplied | **Unsupported** (agrees with OpenAI's review) |
| Positive return at 10 or more turns | Gemini efficiency report | No cost data | **Unsupported** |
| H3 "VALIDATED" | Gemini efficiency report | Mechanism works in a mock with documented bypasses (`../round8/` P1–P4, P7) and collateral revocation; cross-session value unmeasured | **Overclaim**; at most "implementable" |
| Contract sufficiency proven by the bucketed implementation | Gemini efficiency report | That case was an implementation bug (section 1) | **Wrong evidence for a supported conclusion.** Better evidence: Round 7 contract-only 10/14, Round 8 11/16 UNKNOWN, 467/1,206 here |
| "243 vs 261 tokens" | Gemini efficiency report | These match the earlier Claude draft's serialized counts (B1 243, A1 261) | **Attribution:** Claude's earlier measurements, not Gemini's |
| Symbolic text "fragments" and neutralises compression | Gemini efficiency report | Measured: `.sym` 45 bytes → 29 tokens (~1.6 bytes/token) against the full Python file, 139 tokens. Against Python using the same host-held templates, 27 tokens | **Partly true.** Fragmentation is real; the saving disappears only in the fair comparison (29 vs 27) |
| Byte sizes; no token or billing claims | Grok efficiency report and CSV | Byte sizes match the frozen packet; claims are labelled and restrained | **Consistent.** Minor: the CSV labels the Round 7 symbolic trial arm "D"; the protocol calls it C (language only) |
| TokenEconomizer: 18.4–30.9% lower mean SWE-Bench cost | Grok efficiency report | CHECKED via multiple reports of arXiv 2610.22732: 277 tasks, 5 agent–model settings, cheaper in all 30 cells, Pass@1 up in 4 of 5, savings that build across sessions | **Verified** (secondary reports of the paper) |
| Arena.ai 93:1 input:output ratio; Amazon programmatic tool calling −77% input tokens | Grok efficiency report | Not checked | **UNVERIFIED by me** |

---

## 4. Where all agents agree (not evidence in itself)

All four agents report the following:
- No measured economic advantage of AICC over strong conventional reuse.
- Mock security is not isolation.
- H2 is untested without a trained model.
- Fair baselines with documentation, tool search and caching are required.
- Billed telemetry is missing.

The convergence reflects shared inputs, not independent replication.

---

## 5. Open disagreements, and the experiment that settles each

| Disagreement | Experiment |
|---|---|
| Binding overhead: 0.015 ms measured vs 0.15–0.50 ms claimed | Run `../round9-efficiency/bench_runtime.py` (E1) in each agent's environment; report CPU model, Python version, medians and p95 |
| Token counts of frozen files | Same tokenizer version and same bytes (SHA-256) for every agent; publish the command, as `frozen_token_counts.txt` does |
| H3 "validated" vs "unproven" | Multi-session study, fresh sessions per trial. Compare persistent binding decisions against **TokenEconomizer-style learned memory** and plain caching. Measure billed tokens, cost per success, defects from stale decisions, and revocation latency |
| Effect threshold: 15% (protocol, Gemini) vs at least 30% (Claude) | Run a pilot to estimate run-to-run variance, then a power analysis (`../round9-efficiency/power_sim.py`). At heavy variance, 15% is not detectable at 200 tasks × 5 trials |
| Contract sufficiency across models | GPT-6's proposal: different models implement one frozen contract independently, graded on at least 1,000 adversarial vectors. `../round8/agreement/conformance_vectors.json` (1,206 vectors) and its normative tables are a ready starting set |

---

## 6. Suggested corrections for article Draft 4 (OPINION)

1. **Output order:** replace "the contract never fixed output order" with "a four-case conformance suite missed an implementation that violated a stated rule".
2. **The 14,000 agreements:** qualify them as ASCII-only for `group_by_window`; the same reimplementation agrees on only 467 of 1,206 adversarial Unicode vectors.
3. **First attempt:** report Claude's first-attempt Round 8 result as 18/20 → 20/20 after a one-line fix to a contract ambiguity.
4. **Gemini figures:** drop or flag the 14.2%, 0.15–0.50 ms, ten-turn, Arm D 20/20 and "H3 validated" statements unless raw data appears.
5. **Revocation:** record collateral revocation as a known mock defect.
6. **H3 baseline:** cite TokenEconomizer as the strong conventional comparison for cross-session persistence.

## Files in this folder

| File | Content |
|---|---|
| `round8_1_answers.py`, `round8_1_answers_output.txt` | Q1–Q5 and collateral revocation, executed on the frozen packet |
| `frozen_token_counts.txt` | o200k counts with SHA-256 for the three frozen files Gemini reported |

**Related folders:**
- `../round8-earlier-attempt/`: the audited revision, unchanged, with hashes and provenance.
- `../language-prototypes-v2/`: the Language A/B runtime, reference sheet and serialized Language B example the archive review listed as missing.
