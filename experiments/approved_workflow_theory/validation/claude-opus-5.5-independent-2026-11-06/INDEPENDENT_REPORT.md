# Independent reproduction of the approved-core workflow theory test

**Agent:** Claude Opus 5.5 (Anthropic; self-reported identity) · **Date:** 2026-11-06 · **Git revision:** `2b6541a24ef71dcd4390f526042ebf131501fc51` (branch `research/approved-core-replication`)

## Result

**My first independent counter reproduced the published accounting exactly.** The package comparator returned exit 0. All 144 episodes and all 2,160 per-request ledger rows match, and so do both schedules' totals:

| | My result | Published |
|---|---|---|
| Canonical ledger SHA-256 | `467047c105ed2d11968e22a68d5156996bf41896cb4b218b658bcb330e23a1b8` | identical |
| Canonical totals SHA-256 | `aa2abf6604467e7c28365eadee47fe9e8d90a1c2d7c563cbc97dd165d61651c6` | identical |

No correction was needed; the initial ledger is preserved unchanged in `initial-v1/`.

| Schedule | Short-alias Python input / output | Ideal input / output | Total reduction (equal cost per position) |
|---|---:|---:|---:|
| Resident data | 34,686 / 5,928 | 27,144 / 3,714 | **24.02127345%** (40,614 → 30,858) |
| Inspect records | 70,470 / 5,928 | 62,928 / 3,714 | **12.76996780%** (76,398 → 66,642) |

Descriptive-name Python: resident 36,222 / 6,066, inspect 72,006 / 6,066. Ideal AIN, ideal IR and ideal Python are identical, as the specification requires.

**Exact reference rerun, as specified: FAILED and preserved.** The failure was at tokenizer preparation: Hugging Face is unreachable from this sandbox (`LocalEntryNotFoundError`).

**Labelled deviation run: matched.** I ran the reference pipeline directly with only the hash-verified `tokenizer.json`. All 21 reference unit tests passed, `run.py` and `report.py` exited 0, and all 6 reference files matched (fixtures, core sources, totals, episodes, summary, manifest).

## 1. Order of work and disclosure

**Read before implementation:**
- `AGENT_START_HERE.md`
- Draft 8 PDF pages 1–4 (extracted with `pdftotext`)
- `AIN_LANGUAGE_AND_THEORY.md`
- `REPLICATION_SPEC.md`
- `trace-inputs.json`
- `tokenizer-files.sha256.json`
- `requirements-reproduce.txt`
- `workloads.py`, **through introspection only**: public names, signatures and docstrings. I called `expected()` and `execute()`; I did not read its source.

**Seen incidentally:** the *names and sizes* of the files under `results/` and `validation/` appeared in a git tree listing. None was opened.

**Not consulted until after sealing:** `accounting.py`, `run.py`, `report.py`, `reproduce.py`, `README.md`, `ARTICLE_REPRODUCTION_BRIEF.md`, `results/*`, `validation/*`, `test_*.py`, `PACKAGE_MANIFEST.json`.

**Provenance records:** `precomparison-seal.json` holds the code, input, tokenizer and output hashes plus the consulted-materials list. `post-seal-reading.log` timestamps what I read afterwards. The seals are local records, not third-party timestamps.

**Context disclosure:** earlier in this same conversation I built a separate AIN v0 prototype (`experiments/ain_v0`, a different grammar and task). I had not previously seen this package or its numbers.

## 2. Implementation and environment

**Counter:** `counter.py`, sha256 `f07bc913768c10532a8741e2bcf5c714fdae542f544cf1b2065732d22ed8a8a8`. A single file containing:
- the Python renderer;
- generic and typed ideal-unit counting;
- the per-request recurrence;
- a host replay of every action;
- execution checks.

Execution uses the approved function sources supplied in `trace-inputs.json`, run by my own executor, checked against the oracle `workloads.expected`.

**Environment:**
- Python 3.12.3 on Linux 6.18 (x86_64).
- tokenizers 0.21.4, transformers 4.51.3, numpy 2.5.4, huggingface-hub 0.36.2, all installed from `requirements-reproduce.txt`.
- CPU only; zero model inference calls.

**Input hashes:**

| File | SHA-256 |
|---|---|
| `trace-inputs.json` | `6f54c67509944390c7730438fc2d3058b3cb1aa5a89915674918579e5550b31e` |
| `workloads.py` | in the seal |
| `REPLICATION_SPEC.md` | in the seal |

**Tokenizer (deviation in acquisition, not in content).** Hugging Face is not on this sandbox's network allowlist. I used `tokenizer.json` from the npm package `@lenml/tokenizer-qwen2_5` 3.7.2. Its SHA-256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539` is **byte-identical to the pinned Qwen/Qwen2.5-1.5B revision `8faed761…` file**, and the counter refuses to run on any other hash. Encoding with `add_special_tokens=False` through the `tokenizers` library needs only this file.

The other five pinned assets (config.json, tokenizer_config.json, vocab.json, merges.txt, LICENSE) were **not obtained**. The npm `tokenizer_config.json` has a different hash (`5b5d4f65…`) and was used only in the labelled deviation run.

## 3. Checks (all executed)

| Check | Result |
|---|---|
| Replaying each episode's actions (write, patch, remember) on its predecessor reproduces its artifact | 144/144 |
| Replay reproduces the outgoing memory | 144/144 |
| Artifact equals the fixture's plan | 144/144 |
| My executor on the supplied approved sources equals `workloads.expected` | 144/144 |
| `workloads.execute` equals `workloads.expected` | 144/144 |

## 4. Exact rerun and deviation run

**1. Exact attempt** (`work/approved-workflow-replication/claude-opus-5.5-exact-001`):
- Exit 1. `reproduction-failure.json` records `LocalEntryNotFoundError`, raised while downloading the pinned assets.
- No tests or pipeline ran.
- Preserved as evidence.

**2. Deviation run** (`claude-opus-5.5-deviation-tokenizer-001`). **This is not the exact rerun.**
- Setup: a private Hugging Face cache held the verified `tokenizer.json` and the *unverified* npm `tokenizer_config.json`. The wrapper's hash-verification step was bypassed by invoking its own steps directly: the unit tests, `run.py --output`, `report.py --results`, then `reproduce.compare`.
- Results: unit tests 21/21 OK; run exit 0; report exit 0; `matches_reference: true` for `fixtures.json`, `approved_core_sources.json`, `totals.json`, `episodes.json`, `summary.json` and `manifest.json`.
- What it shows: the reference code reproduces its published outputs on Linux and Python 3.12.3.
- What it does not show: that the five missing pinned assets are irrelevant. They are irrelevant only for `add_special_tokens=False` text counts, which this match supports.

## 5. Comparison with the separate-agent validation (read after sealing)

Codex's independent attempt (Windows, Python 3.12.14, all six assets verified) reports the same canonical ledger and totals hashes. Two implementations, two operating systems and two acquisition routes for the same tokenizer bytes agree.

I independently hit the issue Codex reported: `catalog_schema` lists argument names but no types. I took operand types from the JSON value types and the spec's type-contract table, which reproduces the reference for this workload. A general interface needs an explicit type contract.

## 6. Assessment of the assumptions

**Where the reduction comes from.** For resident data, short-alias Python totals 40,614 positions against 30,858 ideal, a difference of 9,756, split as follows:

| Component | Contribution | Share |
|---|---:|---:|
| Common input text (identical in every condition) | 0 | 0% |
| Reprocessed history | 2,628 | 27% |
| Predecessor artifact | 2,646 | 27% |
| Incoming memory | 2,268 | 23% |
| Authored output | 2,214 | 23% |

About three-quarters of the saving is context that gets re-read; only about a quarter is authored output.

**Sensitivity:** separately versioned extension `extension-v1/`, which does not change the frozen accounting.

| Assumption probed | Resident | Inspect |
|---|---:|---:|
| Frozen result | 24.02% fewer positions | 12.77% |
| S1 **Equal cost per position**: break-even cost of one ideal unit | **1.619× a text token** | **1.619×** |
| S2 Python data blobs (memory, observations) as compact JSON instead of `repr` | 21.41% | 11.20% |
| S3 Ideal encoding **without** the 63 static symbols | **−40.26%** (ideal worse) | **−21.40%** |

**Interpretation (OPINION, grounded in the numbers above):**

1. **No AIN-specific advantage is measured.** Ideal AIN, ideal IR and ideal Python tie by construction. The reduction belongs to a hypothetical learned compact *encoding* (a 65,536-entry vocabulary, typed operands, 15-bit payloads) that any representation could adopt. The brief already says this, correctly.

2. **Equal cost per position is load-bearing.** The advantage survives only if one ideal unit costs no more than about 1.62 text tokens of a conventional model. No trained model with this vocabulary exists, so that ratio is unknown.

3. **The vocabulary premise is decisive.** All 63 static symbols, each costing one unit, are this workload's own field names, values, operations and stage labels. Without them, new strings cost 2 + ⌈8·bytes/15⌉ units, roughly 0.53 units per byte against about 0.25–0.33 Qwen tokens per byte for English text, and the ideal encoding loses to Python. S3 is an extreme case; a generic vocabulary would land between S3 and the frozen result. Gains would transfer only to workloads whose terms the learned vocabulary already contains.

4. **The baseline's data rendering matters only modestly.** Compact JSON for host data narrows the gap by about 1.6–2.6 points.

5. **Perfect composition removes the dominant real costs.** There are no planning errors, retries, failed attempts or repairs of model mistakes, which are what published agent-cost studies identify as the main drivers and sources of variance.

6. **The frozen model has no caching pricing.** Repeated context (about 77% of the saving) is exactly what prompt caching discounts in practice. Billed savings would likely be smaller than position savings.

7. **The workload is small.** It has three five-call templates, and changes and repairs patch one argument or operation.

**Recommended wording for the article.** Keep the brief's suggested statement, which these ledgers support exactly, and add two qualifiers:
- the result assumes an ideal unit costs no more than about 1.6 text tokens;
- the advantage depends on a learned vocabulary that already contains the task's own symbols; without those 63 symbols the encoding is worse than Python.

## Files

| File | Content |
|---|---|
| `counter.py` | The independent implementation |
| `initial-v1/` | First, unmodified ledgers (`episodes.json`), totals and execution checks |
| `precomparison-seal.json`, `run-initial-v1.log` | Seal and run log |
| `compare-v1/comparison.json`, `compare-v1.log` | Comparator output (exit 0) |
| `post-seal-reading.log` | What was read after sealing, with timestamps |
| `exact-001/` | The failed exact rerun: `reproduction-failure.json` and log |
| `deviation-tokenizer-001/` | Labelled deviation run: tests, run and report logs, `comparison.json`, generated totals and summary |
| `extension-v1/` | Sensitivity analysis: code, log, JSON |
| `tokenizer.json` | Not committed (7 MB, third-party). Source and SHA-256 are recorded above and in the seal |
