# Round 8 — Results template (return with artifacts)

**Bottom line:** this pilot shows **no measurable advantage of AICC over ordinary package reuse**, and it shows **where the idea fails first: contract precision across providers.** The commons deserves further study only as a *conformance-testing standard for shared contracts*, not as a registry interface.

## 0. Reproducibility and integrity
**Model/provider/config:** Claude Opus 5.5 (Anthropic), claude.ai chat with a code-execution sandbox. Build and sampling settings are not visible to me.

**Date:** 2026-11-03 (UTC timestamps in `EVENT_LOG.md`)

**Python/platform:**
- Python 3.12.3 (Unicode 15.0.0) on Linux 6.18, Ubuntu 24.04 sandbox.
- Node.js 22.22.2 (ICU Unicode 17.0), for the cross-language agreement track.
- tiktoken 0.14.0, `o200k_base`. The vocabulary file was rebuilt offline; its SHA-256 equals tiktoken's built-in expected hash (`tools/README_tokenizer.md`).

**Files received, SHA-256 manifest checked (yes/no):** **Yes.** `sha256sum -c SHA256SUMS.txt` gave 21/21 OK before the work and 21/21 OK after all runs. **No fixture was changed.** Probes that edit files ran in temporary copies of the packet.

**Fresh separate sessions for A/B (yes/no, explain):** **No: SAME SESSION / CONTAMINATED.** Both arms were authored by one model in one conversation. I had no API key, so I could not start independent agents or obtain telemetry. I had also worked through the analogous Round 7 tasks earlier in this conversation. Nothing here is a randomised replication.

**Source inspected during authoring (which files and why):**
- Nothing under `benchmark/sealed/` was opened.
- `benchmark/verify_submission.py` was not read in this session.
- The host (`benchmark/host/registry.py`) was examined only through Python introspection: module names, method signatures, and the runtime state of a binding's closure. One line of its source appeared in a traceback during probe P7.
- `benchmark/token_measure.py` was read; it is a measurement script.
- One black-box call to `filter_by_severity` was needed because the contract does not state the type of `minimum`.
- The private function's *name* (`risk_score_private`) was obtained with `dir()` in probe P3; its source was never displayed.

**Integrity disclosure: leftovers from an earlier attempt.**
- The sandbox contained 14 files dated 16:41–16:48 UTC, written by an earlier, interrupted attempt at this round that is not part of my current working context. This session's log begins at 16:51.
- I did not open them, apart from viewing the first lines of one draft report to identify it. All 14 were moved unread to a quarantine folder and are **not part of this submission or of any result here**.
- That draft states that the earlier attempt read `registry.py` and `verify_submission.py`. Because that attempt belonged to the same conversation, treat my Arm B and security results as **possibly exposed** to those two files.

**Other agents' Round 8 results known before trial:** None. I knew only the organiser's summary of the Round 7 reports, contained in the packet.

## 1. Outcomes table
| Arm | Executed? | Tests passed/total | Retries | Total input tokens (API) | Total output tokens (API) | Reasoning tokens (API) | Runtime/tool time | Full task cost |
|---|---|---|---|---|---|---|---|---|
| A: ordinary API | Yes, same session | **20/20** | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| B: commons registry | Yes, same session | **20/20** | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| C: scoped private | Yes, mock host only | `--security` **3/3**; my scope, revocation and expiry checks 4/4 behaved as specified; **5 of 7 adversarial probes bypassed the mock** | 0 | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED | NOT MEASURED |
| D: trained native tokens | **NOT EXECUTED** | — | — | — | — | — | — | — |

Organiser `--self-test`: 20/20. That validates only the fixtures, not any agent.

## 2. Detailed capability selection
**Selected for tasks 1–8:** 18 public capabilities. These were `parse_csv_table`, `stable_unique`, `parse_money`, `digest_json`, `filter_by_severity`, `group_by_window`, `safe_path`, `chunks`, `hash_chunks`, `gzip_deterministic`, `toposort`, `retry_delays`, `diff_by_id`, `merge_patch`, `redact_paths`, `make_query`, `canonical_json` and `png_dimensions`. Arm A used ordinary imports; Arm B used `Runtime().bind('pub.<name>@1')`.

**Rejected** (recorded in `SELECTION_DECISIONS_BEFORE_TESTS.md` before any test ran):
- `candidate.parse_money_bankers@1`: rounds ties half-even; the contract requires ROUND_HALF_UP.
- `candidate.safe_path_loose@1`: rewrites traversal instead of rejecting it.
- `candidate.group_by_eventid@1`: groups by event ID rather than behaviour and time window.

**Caveat:** the shared contract labels all three as near-misses, so rejecting them "from the contract" was trivial here. Executable confirmation (probe P5): `parse_money('1.005')` returns 101 while the half-even candidate returns 100. `safe_path('a/../../etc/passwd')` raises ValueError while the loose candidate returns `'a///etc/passwd'`. Two equivalent events form 1 group under `group_by_window` and 2 under `group_by_eventid`.

**Facts needing escalation:** one. The contract does not say whether `filter_by_severity`'s `minimum` is a name or a number. A black-box call showed it must be an int from 0 to 3: `'warning'` raises `ValueError: minimum 0..3`.

**Failures and repairs:** none in either arm.

## 3. Contract sufficiency
**ENTAILED** means the contract settles the question; **REFUTED** means the claimed property does not hold; **UNKNOWN** means equivalence cannot be decided from the contract.

| # | Uncertainty | Verdict | Evidence | Escalation needed |
|---|---|---|---|---|
| 1 | `filter_by_severity`: type of `minimum` | UNKNOWN in contract; resolved | Name raises ValueError; integer 2 works | One black-box call |
| 2 | `group_by_window`: how device and kind are normalised | UNKNOWN in contract; resolved | NFKC (ﬁ→fi), casefold (ß→ss) and whitespace collapse all observed | Probes |
| 3 | `group_by_window`: output order, timestamp type, error classes, extra fields | UNKNOWN in contract; resolved | Ordered by first timestamp, ties in input order; float and bool timestamps raise TypeError; missing field raises TypeError; window 0 or 1.5 raises ValueError; extra fields dropped | 18 probes in total for #2 and #3 |
| 4 | `gzip_deterministic`: bytes equal across contract-satisfying implementations | UNKNOWN | Reference XFL=2 (level 9). `gzip.compress(level=6, mtime=0)` and Node `zlib.gzipSync` give XFL=0, so the bytes differ; all decompress to the same data | Pin level, header bytes and encoder, or compare decompressed output |
| 5 | `canonical_json` numbers across languages | UNKNOWN | Python against JavaScript: `1e16` gives `1e+16` vs `10000000000000000`; `-0.0` gives `-0.0` vs `0`; `2**53+1` gives an exact value vs rounded; `1.0` gives `1.0` vs `1`. So `digest_json` of the same logical data differs between providers | Adopt RFC 8785 number rules or restrict to integers within ±2^53 |
| 6 | `canonical_json` / `digest_json` on a lone surrogate | UNKNOWN | `digest_json('\ud800')` raises UnicodeEncodeError; JavaScript escapes it | Contract must state it |
| 7 | `make_query`: "standard urlencode" | UNKNOWN | Python gives `q=a+b~%2A%27`; WHATWG URLSearchParams gives `q=a+b%7E*%27` | Name the exact encoding set |
| 8 | `toposort`: "lexicographically smallest" | UNKNOWN | Python orders by code point (U+FFFF before 😀); JavaScript's default orders by UTF-16 unit (😀 first) | Define the order on code points |
| 9 | `png_dimensions` used as validation | REFUTED | Accepts width 2^31 (beyond the PNG maximum of 2^31−1) and a zeroed CRC; this matches its contract, but a caller using it as validation would be wrong | Separate validating capability |
| 10 | `normalize_tag` on another runtime | UNKNOWN | Python Unicode 15.0.0; Node ICU Unicode 17.0 | Contract must name a Unicode version |

`contract_insufficiency.py` summary over 16 cross-variant checks: **3 ENTAILED, 2 REFUTED, 11 UNKNOWN.**

**Did the contract omit observable behaviour?** Yes, repeatedly. **Did standard package docs already provide it?** Partly. Python's own `gzip`, `json` and `urllib.parse` documentation states the default compression level, float `repr` and `quote_plus` rules that the commons contract leaves out. The commons contract is therefore *less* precise than the documentation of the library it wraps, and the gaps matter exactly where AICC needs precision most: multiple providers and multiple languages.

## 4. Security/private experiment
**Public-only denied?** Yes: `PermissionDenied: scope`.

**Project-scoped authorised?** Yes: the call returned an integer. It returned 0 for all six events I tried; I did not try to discover the rule.

**Revoked binding denied?** Yes. The old callable raised `InvalidBinding: policy changed`, and re-binding on the same host raised `PermissionDenied: revoked`. TTL expiry raised `InvalidBinding: expired`.

**Adversarial probes against the mock** (`probe_host.py`, each in a fresh subprocess):

| Probe | Result | Interpretation |
|---|---|---|
| P1 anonymous principal *asserts* scope `project-a` | **Bypassed**: bound and called | Scopes and effects are caller-asserted; there is no authentication |
| P2 revoke on one `Runtime()`, bind on a new one | **Bypassed**: still binds | Revocation is per instance and does not propagate |
| P3 `registry.private_core.risk_score_private(...)` | **Bypassed**: called with no authorisation | The private code is reachable in-process |
| P4 replace a catalogue entry declared pure with one that writes a file | **Bypassed**: file written | Declared effects are trusted, not enforced |
| P5 near-miss candidates | Bindable and observably wrong | Selection is the agent's responsibility |
| P6 edit the file on disk after binding (temporary copy) | **Detected**: `InvalidBinding: artifact changed` | Per-call re-hash of the file works |
| P7 tampered module substituted before import, file untouched (temporary copy) | **Bypassed**: returned `ffff…` instead of the real digest | Identity is a hash of the file on disk, not of the loaded code |

**Which tests are only mock metadata checks, which enforce, which remain untested?**
- *Metadata checks:* scope and effect strings (caller-asserted).
- *In-process enforcement that worked:* the per-call checks of revocation, expiry and on-disk file hash. These are in-process only.
- *Not enforced or untested:* authentication, isolation, effect enforcement, identity of loaded code, encryption, key custody, cross-host revocation, and cross-session persistence.

**Fair baseline** (`conventional_envelope.py`, 50 lines of ordinary Python, with the same policy envelope):
- *Executed:* it reproduced public-only denial, authorised call, expiry and revocation of an old binding, and it beat the mock on revocation, which a *separate process* saw through a shared file.
- *Stated, not executed:* P1 and P3 apply equally to it.

**Conclusion:** the mock adds no protection beyond a conventional authorisation wrapper. **This experiment does not implement encrypted private code or real OS sandboxing.**

**How encryption and key custody would work in a real host (proposal, untested):**
1. Encrypt private artefacts at rest with authenticated encryption under per-project data keys, wrapped by a key held in a KMS or HSM.
2. Release data keys only to an execution environment whose image has been remotely attested, for example a confidential VM, or a WebAssembly runtime inside one.
3. Bind workload identity (SPIFFE-style) and short-lived, audience-restricted capability tokens to principal, scope, effects and expiry. The host verifies these; the agent's claims count for nothing.
4. Enforce effects through capability imports (WASI) or syscall filtering.
5. Compute artefact identity from the bytes the runtime actually loads, checked against a signed manifest.
6. Revoke through short token lifetimes plus pushed revocation lists.
7. Keep keys out of model context entirely. Signing proves authorship; it confers no right to decrypt.

## 5. Model cost and context
**API telemetry: NOT MEASURED.** I have no input, output, reasoning, cache or billing data, and nothing below is inferred from file sizes.

Artefact counts (tiktoken 0.14.0, o200k_base):

| Artefact | Bytes | Tokens |
|---|---:|---:|
| Shared docs both arms read: `API_CONTRACTS.md` + `TASKS.md` | 4,829 + 2,786 | 1,043 + 639 |
| `submission_A.py` | 2,122 | 528 |
| `submission_B.py` | 2,681 | **713** |
| One capability: import (A) vs bind (B) | 57 vs 51 | 10 vs **15** |
| `group_by_window` row in the shared contract | 302 | 61 |
| My machine-checkable contract for it | 2,487 | 625 |
| Its normative tables (whitespace + case folding) | 23,326 | 12,604 |
| Its conformance vectors (machine artefact, not model context) | 1,555,359 | 525,341 |

Arm B is 185 tokens *larger* than Arm A for identical correctness. Neither arm read implementation source. Retries: 0 in both arms. The interoperability artefacts are verifier data and need not enter model context; their cost is curation, not inference.

## 6. Multi-agent shared standard
**Candidate contract:** `agreement/group_by_window.contract.yaml`. It makes the 18-probe findings normative:
- Unicode version.
- Whitespace set: Python's `str.isspace`, 29 code points, enumerated.
- Full case folding, shipped as a table.
- Normalisation `collapse(casefold(NFKC(s)))`.
- Window measured from the group's first timestamp, strict `<`.
- Creation order of output.
- Language-neutral error codes `E_TYPE` and `E_WINDOW`.
- An environment manifest and the required evidence.

**Three variants against the sealed reference** (`agreement/differential.py`: 1,200 random workloads with adversarial Unicode, plus 6 invalid inputs):

| Variant | Agreement with reference |
|---|---:|
| `alt_python.py`, written from my contract (Python 3.12) | **1,206 / 1,206** |
| `alt_js_faithful.js`, my contract plus its tables (Node 22) | **1,206 / 1,206** |
| `alt_js_naive.js`, the *shared* contract text with JS defaults (`toLowerCase`, `/\s+/`) | **559 / 1,206** |

The naive variant failed on ß (67/200), final sigma (61/200), U+001C (10/200) and U+FEFF (15/200). It agreed on clean, ligature and invalid inputs.

**Shareable guarantees:** algorithm semantics and error codes, *provided* the Unicode tables are normative.

**Environment-specific:** NFKC tables (my faithful variant still uses Node's Unicode 17.0 NFKC, untested beyond this input pool), JavaScript's safe-integer limit of 2^53, and performance.

**What a third party needs to validate interoperability:** the contract, the tables, the conformance vectors, an error-code mapping, and an environment manifest.

**Second pass, comparing with another model's independently authored contract: NOT EXECUTED.** I have no other Round 8 contract. **No consensus is claimed.**

## 7. Skeptical verdicts
**H1: Not supported by this pilot.**
- Equal correctness (20/20 each); Arm B is larger in tokens; no source was read in either arm.
- The registry interface added nothing measurable over imports.
- The shared contract left 7 decisions unspecified in a single function, and 11 of 16 cross-variant checks were UNKNOWN.
- H1's value, if any, lies in *contract precision plus conformance testing*, which is equally applicable to ordinary packages.

**H2: NOT TESTED.** No trained model.

Proposed experiment, not run:
- *Setup:* one open-weight code model, fine-tuned three ways on identical paired data and token budgets: (a) a dedicated-token opcode stream with constrained decoding; (b) a typed-AST action sequence with constrained decoding; (c) plain Python.
- *Evaluation:* the same held-out suite (300 functions with exact-trace tests plus 100 edit tasks), equal search compute, at least 3 seeds.
- *Measures:* pass rate, whole-trajectory tokens, latency, and silently wrong edits.
- *Decision rule:* the opcode arm must beat the typed-AST arm by at least 15% in cost per correct task, with a pass rate no more than 2 points lower.

**H3: No benefit shown beyond ordinary caching.** Per-call revalidation works in the mock, but a 50-line conventional wrapper reproduces it and propagates revocation across processes, which the mock does not even do across instances. Cross-session persistence is not implemented by the mock and is untested.

**H4: Not established.** The private boundary was bypassed four ways in-process (P1–P4), and artefact identity was spoofed (P7). The claim needs a genuine external execution boundary, encryption and attestation; none of that is present or tested.

**One concrete reason AICC could fail: contract precision is the cost centre, and imprecision fails silently.** Making one small function interoperable across two languages took:
- 18 probes;
- a contract 10× longer than the shared row (625 against 61 tokens);
- 23 KB of normative Unicode tables;
- 1,206 conformance vectors.

The JavaScript variant built from the shared text agreed only 46% of the time on realistic Unicode input. It raised no error; it was simply wrong. Across a commons of thousands of capabilities, curation cost or silent divergence could easily outweigh the savings.

**What would change my mind:** a preregistered production-scale study (Section 8) in which:
- commons reuse with conformance-tested contracts cuts *measured* cost per correct task by at least 20% against strong package reuse, with no higher defect rate;
- independently built cross-provider variants pass shared conformance vectors at 99.9% or better on held-out inputs;
- contracts stay under 2× the size of the wrapped library's own documentation.

**Strongest remaining objections:**
1. Package managers plus good documentation already deliver no-source reuse; every AICC benefit measured so far is reproducible with ordinary engineering.
2. "Agreement on contracts, not algorithms" needs normative tables, number formats, orderings and error codes. That is standards-body work, as with RFC 8785 or Unicode, and costly at scale.
3. Variant diversity is a liability for content-addressed digests: providers disagreed on `canonical_json` for ordinary numbers.
4. Security claims rest on host properties the pilot does not have. Every bypass found here is in-process; real isolation (TEE, WebAssembly, syscall filtering) is the actual research problem, and it is independent of AICC.
5. Cross-model agreement is not evidence. One model wrote all arms here, so these results need independent replication.

## 8. Production-scale benchmark proposal (PROPOSED, not executed)
**Capabilities:** at least 20, each with two or more independent implementations and preferably a public spec, sampled per domain from the most-downloaded PyPI, npm and crates.io packages. For example:
1. CSV (RFC 4180): CPython `csv` vs Rust `csv`.
2. Canonical JSON (RFC 8785): Python `jcs` vs `canonicalize` (JavaScript).
3. gzip/zlib: zlib vs zlib-ng.
4. PNG decoding: libpng vs stb_image vs `image-rs`.
5. Image resize: Pillow vs libvips.
6. URL parsing: WHATWG URL (Node) vs `urllib` vs Rust `url`.
7. Unicode normalisation and case folding: ICU vs Python `unicodedata`.
8. Time-zone datetime: `zoneinfo` vs `java.time` vs Luxon.
9. Decimal money: `decimal` vs `BigDecimal` vs `decimal.js`.
10. SQL building: SQLAlchemy Core vs Knex.
11. Retry/backoff: `urllib3.Retry` vs `got`.
12. JWT validation: PyJWT vs `jose`.
13. Password hashing: argon2-cffi vs libsodium.
14. Regex: `re` vs RE2.
15. YAML: PyYAML vs ruamel vs js-yaml.
16. Markdown (CommonMark): cmark vs markdown-it.
17. Path sandboxing: `pathlib` vs Node `path`.
18. Dependency ordering: `graphlib` vs networkx.
19. Diff: `difflib` vs diff-match-patch.
20. Protobuf: protobuf-python vs protobufjs.
21. Parquet: pyarrow vs polars.
22. HTTP header parsing: h11 vs llhttp.

**Sampling:** stratified by domain, with a preregistered random draw from eligible packages so that no one cherry-picks.

**Tasks:** 50–100 unseen multi-file tasks that compose these capabilities, with private components, planted near-misses (identical signature, different behaviour) and versions that drift during the run. Hidden behavioural tests: golden traces, properties and differential fuzzing.

**Arms:**
- A: packages, docs, search, caching.
- A+: A plus conformance vectors.
- B: commons with contracts, fit checks and bindings.
- B−: commons without fit checks.
- C: conventional policy envelope.

**Protocol:** at least 3 fresh runs per arm, randomised order, identical budgets.

**Telemetry:** billed input, output, reasoning and cached tokens; wall-clock; tool calls; source reads; escalations; human minutes.

**Assurance labels:** tested, differentially tested, formally verified and audited, each reported separately.

**Failure thresholds:** B shows less than 20% cost reduction against A+ at equal defect rate; false-reuse rate exceeds A's defect rate; cross-variant conformance falls below 99.9%; or any private-boundary breach under a real isolation boundary.

## 9. Reproduction appendix
**Command:** `./run_all.sh > RUN_LOG.txt 2>&1` from the packet root, with `TIKTOKEN_CACHE_DIR` set if offline (see `tools/README_tokenizer.md`). The full verbatim output is in `RUN_LOG.txt`.

**Fixture:** unchanged; `SHA256SUMS.txt` gives 21/21 OK before and after.

**Generated files and SHA-256** (first 16 hex digits; full values in `token_results_r8.json`):

| File | SHA-256 |
|---|---|
| `submission_A.py` | d1243abbe8ca666f |
| `submission_B.py` | 4b57458276d8c8cb |
| `private_arm.py` | 5eb6f209c9f2fff1 |
| `conventional_envelope.py` | 60efe580c1764a94 |
| `agreement/group_by_window.contract.yaml` | e90e4f201f4bcfde |
| `agreement/alt_python.py` | d84a545365d94cec |
| `agreement/alt_js_naive.js` | ed2b691ec68b6893 |
| `agreement/alt_js_faithful.js` | 3d16d71dd47a2600 |
| `agreement/tables/casefold_full.json` | 3f7a96ad5421b852 |
| `agreement/conformance_vectors.json` | 503a472cba82406c |

**Other files:**

| File | Purpose |
|---|---|
| `probe_host.py`, `probe_host_output.txt` | Arm C checks and host probes |
| `agreement/probe_group_by_window.py` and its output | The 18 black-box probes |
| `agreement/differential.py`, `agreement/differential_results.json` | Three-variant differential test |
| `contract_insufficiency.py` and its results | Cross-variant equivalence checks |
| `measure_r8.py`, `token_results_r8.json` | Token counts and hashes |
| `SELECTION_DECISIONS_BEFORE_TESTS.md`, `EVENT_LOG.md` | Decision record and file-access log |
| `tools/` | Offline tokenizer setup |

**Versions:** Python 3.12.3, Node 22.22.2, tiktoken 0.14.0.
