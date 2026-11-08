# Historical and branch audit for article Draft 11

Review date 7 November 2026. Scope assigned to this reviewer was the early/main/archive/cross-review history, Round 7 and Round 8 fixtures, the early Language A/B prototypes, Round 9 efficiency diagnostics and the lifecycle proposal. Processing-study, later AIN v0, current-agent fluency and approved-core/native-local studies are reviewed by other tasks.

## Branch coverage and content deduplication

The companion `history-branch-inventory.json` records the exact tips, tree counts and all blob contents absent from the Draft 10 tip `53cb324e70ac801e9636f7fa0972a82fe99ae511`. Blob comparison ignores filename relocation when establishing duplicate content.

| Branch | Pinned tip | Tree files | Findings |
|---|---|---:|---|
| main | c7d7ccd2fcefe46da44be51bd97328d9a190f451 | 1 | Project-entry README. It points to a research branch and contains no experiment dataset. Its status statements predate the new local adaptation screens. |
| claude/results | 93c0c175ee3c996ac3b28fee76600e1350e15d23 | 95 | Round 7, Round 8 and Round 9 results. All experiment blob contents are represented at the Draft 10 tip. Its README is the only unique blob relative to that tip. |
| research/consolidated-archive-2026-11-04 | c6eb51028f7172b6a0d4c349fab56be3ecf5ac25 | 179 | Imported archive plus lifecycle protocol. Three README variants are unique versus Draft 10; the underlying experimental contents are represented. |
| claude/cross-review | 4cd023fb78e966d202ace372d4e4bbf9588a5456 | 219 | Fifty blob contents absent from Draft 10, including recovered earlier Round 8 artifacts, the Language A/B v2 runtime and raw results, and corrections. This branch supplies substantive evidence beyond the integrated research branch. |

The files reviewed include complete branch entry READMEs, the complete cross-review and provenance report, recovered raw result JSON, the raw round8 agreement tables, original per-agent reports, official protocol, verification JSON and lifecycle protocol/configuration. Runtime and mutation code relevant to reported failures was inspected. One minimal recovered ordering counterexample was executed for this audit. Large fuzz suites and old model sessions were not rerun.

## Article-ready experiment chronology

| Stage | Supported observations and source scope | Article interpretation |
|---|---|---|
| Early Language A/B v2, dated 2 November in its README | Shared AST/parser/checker/interpreter, numeric opcode encoder/decoder and Python/C# projections are recovered on claude/cross-review. Raw `a_b_results.json` contains an if/else controller with 20 opcode entries and a ternary controller with 18; explicit templates are also stored. | Executable language prototypes and serialization examples. They supply concrete historical examples, with no trained native model. |
| Round 7 reuse/controller fixture, reported 3 November | Claude, GPT-6, Grok and Gemini reports each describe ordinary reuse 14/14, registry reuse 14/14, Python controller 6/6, symbolic controller 6/6, and mock binding checks 3/3. Claude/Grok/GPT-6 disclose same-session exploratory arms. Gemini reports three local trials, without equivalent raw fresh-agent records in this imported set. | Use per-report labels. The 4 November import independently executed supplied Claude artifacts and confirms the listed suite outcomes. Aggregate reports do not create four independent randomized native-agent studies. |
| Round 7 semantic and mutation probes | Claude's contract-only implementation scored 10/14; official reuse both 14/14. `h2_probe_results.json` records 246 mutations, including 22 silently wrong and 3 parser crashes. | Typed or compact syntax can admit semantically wrong programs. This is a synthetic mutation diagnostic, with no model error-rate estimate. |
| Round 8 workflow composition, reported 3 November | Supplied Claude later and Grok submissions pass ordinary/registry 20/20; mock checks 3/3. Gemini initially claimed 24/24 but corrected to 20 official workflow cases plus three mock checks. | Explain equal-capability ordinary reuse succeeds. Reuse without source-body reading is feasible, while economic gain is still unmeasured. |
| Recovered earlier Claude Round 8 attempt | The interrupted 16:41–16:48 UTC attempt scored 18/20 before a one-line minimum-type repair to 20/20. The later same-conversation attempt began at 16:51 and probed the ambiguity before its first 20/20. | Report two related attempts. Cite 18/20→20/20 for first exposure and preserve later provenance. They are separate artifact revisions from one conversation. |
| Cross-review ordering correction, 4 November | Original two implementations disagreed on 3,127/5,000 generated inputs. The written contract required group creation order during stable timestamp scan. The bucketed implementation violated that rule. Cross-review's corrected variant agreed on 5,000 old-seed, 20,000 fresh-seed and 20,000 Unicode-key comparisons against its paired scan implementation. | An implementation defect escaped a four-case conformance suite. Withdraw the older claim that the particular output-order rule had been omitted. The three fixed comparison batches establish internal agreement of these two implementations. |
| Cross-language contract agreement | Round 8 raw `agreement/differential_results.json` records contract-based Python 1,206/1,206 and faithful JavaScript with explicit normalization tables 1,206/1,206. Naive JavaScript defaults agree on 559/1,206. | Cross-runtime normalization and ordering requirements need precise contracts. All alternatives were authored by the same Claude conversation. |
| Recovered ASCII-fuzz qualification | Seven functions had 2,000 agreements each, totaling 14,000. The earlier `group_by_window` reimplementation then agreed with the later reference on 467/1,206 Unicode adversarial vectors. | The 14,000 count has narrow generator coverage. It should appear beside the adversarial result if cited. |
| Round 8 mock authority and identity | Official mock 3/3 coexists with Claude's five bypasses in seven adversarial probes, including asserted scope, private direct import, declared-pure file write and loaded-code substitution. Cross-review reproduces collateral invalidation of an unrelated binding after a different capability is revoked. | The prototype checks metadata in one process. A production isolation or cryptographic security conclusion requires additional apparatus. |
| Round 9 tokenizer/runtime/harness diagnostics | Claude measured saved artifact tokens and finished-program runtime. AICC solution 713 o200k tokens versus ordinary 528. Symbolic controller 29 versus Python with equal host templates 27. Fifty subprocess harness rows execute finished programs, with zero model calls. | Static tokens and runtime are useful apparatus data. They supply no billed agent-development or trained-language result. |
| Lifecycle pilot proposal, prepared 4 November | Proposed 27 chains and 135 linked stage executions across cold/warm/handoff/relevant/unrelated changes. Configuration has status PLANNED and null provider, budget and billing fields. | Keep in future work. The 135 planned lifecycle stages are separate from the 135 completed processing workers described elsewhere. |

## Recovered evidence changes the archive-status narrative

`docs/research/REVIEW_2026-11-04.md` accurately records the archive available at its review date, including missing earlier Claude artifacts and Language A/B runtime. The cross-review branch subsequently publishes those materials. A new article should acknowledge the recovery and corrections instead of carrying the earlier missing-artifact statement forward as current.

The present reviewer executed the recovered two-event counterexample from the original source blob. Input timestamps `[242,59]`, window 120, produce scan output `[59,242]` and original bucketed output `[242,59]`. The source contract explicitly states group creation order during the ordered scan. The exact script SHA-256 and output are preserved in `order-counterexample-replay.json`. This selected replay is additional to the historical cross-review reports; the full historical fuzz counts above remain their archived executed records.

## Detailed raw evidence useful for charts

### Early token diagnostics

- Round 7 Claude: symbolic program 29 o200k tokens versus Python controller with equal host-held templates 27. The 139-token full Python file is a different context boundary. The symbolic grammar itself occupies 1,143 tokens in that experiment. Source `agents/claude/round9-efficiency/token_table.json` or report section 3.1 at `93c0c17`.
- Round 8 Claude: ordinary solution 528 and registry solution 713 o200k tokens, with exact source hashes in `agents/claude/round8/token_results_r8.json`. This is one saved solution pair, not an inferred average cost of AICC.
- Frozen API contract, baseline API, implementation counts were 1,043/97/2,198 in Claude's cross-review, while Gemini's corrected report says 912/98/1,842. Byte hashes match the packet; the tokenizer discrepancy needs reconciliation. Source `agents/claude/cross-review/frozen_token_counts.txt` at `4cd023f`.

### Runtime diagnostics

`agents/claude/round9-efficiency/runtime_results.json` has 15 repetitions per microbenchmark. Recorded medians for normalize_tag are 0.25555 microseconds direct, 0.42985 ordinary policy wrapper, 14.97324 AICC mock with per-call file rehash. At controller n=1000, recorded medians are native Python 184.662 microseconds, Language A projected to Python 205.241, Round 7 symbolic interpreter 949.943, Language A interpreter 4,135.824, and Language B decode/interpreter 4,283.616. These are host implementation choices in a single reported sandbox. They supply no language-training inference comparison. If charted, identify each runtime strategy and environment and retain repetitions, p95 and sample-loop limits.

`AICC_Efficiency_Measurements_Claude.csv` contains 55 total rows, comprising 50 finished-program harness rows, three historical authoring-note rows and two unexecuted-arm placeholders. The fifty `R9-H` rows record zero model calls. The other five record unavailable model-call telemetry. Billing and model-token fields are unavailable. Grok's partial CSV contains three explanatory rows with unavailable metering, coarse `<1000` ms timings and no model-call measurements. Gemini's precise efficiency claims lack corresponding raw measurement records in the reviewed archive.

### Early mutation and production-size probes

At `4cd023f`, `agents/claude/language-prototypes-v2/mutation_results.json` records 4,000 synthetic mutations per surface. Same-class Language B has 574 silently wrong cases, broad-opcode mutation 247, Language A character mutation 173, and Python character mutation 77. Mutation operators differ across surfaces. These counts describe each operator's probe distribution and cannot be compared as observed model reliability.

`prod_results.json` analyzes 12 Python standard-library files. The script measures 84,892 original source tokens, 45,109 after Python minification, and estimates 38,671 under an AST-leaf/atomic syntax accounting model with docs omitted. Code inspection confirms this is a source categorization/ideal-unit estimate, with no production AIN translation, execution or trained model. Retain as exploratory theory history if useful; keep it out of empirical language-efficiency charts.

## Claims requiring careful treatment

Gemini's efficiency report asserts a 14.2% syntax-error increase, ten-use break-even, 0.15–0.50 ms binding overhead and a successful Round 8 symbolic+AICC arm. The supplied protocol/harness offers no trained opcode arm and the earlier grammar lacks the containers/sorting/calls needed for those workflows. Raw trial data for those precise assertions was absent from the reviewed material. Cross-review explicitly identifies these gaps. Gemini's Round 8.1 correction resolves the official 20+3 case count, but its file-token counts remain inconsistent with the hash-verified Claude recount.

Grok's old efficiency report carefully labels unavailable tokenizer/billing data and its partial CSV. Its literature summaries are secondary to this historical audit and should be independently verified from primary publications before new article citations. No current primary-literature verification was performed by this reviewer.

Model/provider identities and remote sandbox details are contributor reports. Cross-agent discussion and shared packets weaken claims of blinding. The old source archive is synthetic research material, with the advertised sealed directories publicly accessible in Git. It cannot function as an unseen evaluation set for future trials.

## Pinned source links for the article

- [Archive audit and its 11-command replay](https://github.com/izikon78/AICC/blob/c6eb51028f7172b6a0d4c349fab56be3ecf5ac25/docs/research/REVIEW_2026-11-04.md)
- [Machine-readable import verification](https://github.com/izikon78/AICC/blob/c6eb51028f7172b6a0d4c349fab56be3ecf5ac25/docs/research/verification-2026-11-04.json)
- [Claude Round 7](https://github.com/izikon78/AICC/blob/93c0c175ee3c996ac3b28fee76600e1350e15d23/agents/claude/round7/Round7_Results_Claude_Opus_5.5.md)
- [Claude Round 8 later attempt](https://github.com/izikon78/AICC/blob/93c0c175ee3c996ac3b28fee76600e1350e15d23/agents/claude/round8/Round8_Results_Claude_Opus_5.5.md)
- [Cross-review corrections and recovered records](https://github.com/izikon78/AICC/blob/4cd023fb78e966d202ace372d4e4bbf9588a5456/agents/claude/cross-review/CROSS_REVIEW_2026-11-04.md)
- [Earlier attempt provenance](https://github.com/izikon78/AICC/blob/4cd023fb78e966d202ace372d4e4bbf9588a5456/agents/claude/round8-earlier-attempt/PROVENANCE.md)
- [Raw cross-language agreement](https://github.com/izikon78/AICC/blob/93c0c175ee3c996ac3b28fee76600e1350e15d23/agents/claude/round8/agreement/differential_results.json)
- [Round 9 report](https://github.com/izikon78/AICC/blob/93c0c175ee3c996ac3b28fee76600e1350e15d23/agents/claude/round9-efficiency/AICC_Efficiency_Research_Report_Claude.md)
- [Recovered Language A/B prototype package](https://github.com/izikon78/AICC/tree/4cd023fb78e966d202ace372d4e4bbf9588a5456/agents/claude/language-prototypes-v2)
- [Gemini Round 8.1 correction](https://github.com/izikon78/AICC/blob/c6eb51028f7172b6a0d4c349fab56be3ecf5ac25/agents/gemini/round8/ai_think_tank_round_8_1_correction_reconciliation_gemini.md)
- [Grok Round 8.1 reconciliation](https://github.com/izikon78/AICC/blob/c6eb51028f7172b6a0d4c349fab56be3ecf5ac25/agents/grok/round8/Grok_Round8.1_Response.md)
- [Lifecycle proposal](https://github.com/izikon78/AICC/blob/c6eb51028f7172b6a0d4c349fab56be3ecf5ac25/experiments/lifecycle-pilot/README.md)

## Scope statement for publication

This audit reviews branch narratives, raw result tables and selected code, deduplicates source blobs and executes the minimal recovered ordering counterexample. All fourteen recovered earlier-attempt files match the published SHA-256 manifest, checked directly against the Git blobs. `history-integrity-checks.json` preserves those checks and the CSV row classification. The historical import report preserves its own larger official-suite replay. This audit supplies no new large fuzz run or repeated stochastic agent generation. Article tables should distinguish contributor-executed, independently replayed, modeled and planned rows.
