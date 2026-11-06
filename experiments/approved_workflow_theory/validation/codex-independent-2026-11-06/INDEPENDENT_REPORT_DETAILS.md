# Independent approved-core accounting recreation

The first independently written counter matched the published reference exactly on both schedule/profile totals and every request ledger. The separate exact reference rerun also matched. No accounting correction, expected-number tuning or failed measurement attempt occurred.

## Independence and order of work

I began with no AIN background supplied to me. I first read only `AGENT_START_HERE.md`, then `REPLICATION_SPEC.md`, `trace-inputs.json`, pinned requirements and tokenizer hashes. I ran only `reproduce.py --prepare-tokenizer` to obtain and verify assets. I next consulted the expressly permitted `workloads.py` for approved implementations and fixture oracles. I wrote my own generic and typed counters, Python program/action renderers, recurrence and aggregation. I did not inspect reference accounting.py, run.py, report.py, the article brief, reference aggregates or reference ledgers before freezing the first results.

Git revision: `395278bc369b1c33141381a73872725ca4dd4a7b`. The first output freeze is timestamped `2026-11-06T21:49:36.450567+00:00`; the additional canonical-ledger seal is timestamped `2026-11-06T21:49:52.082065+00:00`. These are local provenance records, not third-party timestamp attestations.

Only after preserving source, complete first ledgers, totals, hashes, environment, renderer text and execution evidence did I run the published independent comparator. I then ran the exact offline reference wrapper into a different new folder. After both succeeded, I read ARTICLE_REPRODUCTION_BRIEF.md, README.md and reference accounting/rendering/report code to assess interpretation and explain implementation differences.

All filesystem mutations were confined to this fresh checkout's `work/` directory. Python bytecode generation was disabled and HF_HOME pointed to `work/tokenizer-cache` on every tokenizer/reference command. Tracked files are unchanged. The pre-existing Python environment was used without installation changes.

## Environment and hashes

Python: `3.12.14 (main, Aug 25 2026, 14:01:42) [MSC v.1944 64 bit (AMD64)]`. Platform: `Windows-11-10.0.26200-SP0`. No Torch, TensorFlow or Flax installation was needed; all work used CPU execution and tokenizer assets. All applicable pinned package versions match (`final-validation.json`), and `initial-v1/manifest.json` records every installed package.

Tokenizer: `Qwen/Qwen2.5-1.5B`, revision `8faed761d45a263340a0528343f099c05c9a4323`, encoding with `add_special_tokens=False`. All six assets were SHA-256 verified before counting and verified again by my counter. Windows emitted a cache symlink warning and stored duplicate files instead; this changed neither asset hashes nor results.

| Evidence | SHA-256 |
|---|---|
| First independent counter | `e56101a0937ef7285fddc9910b5f1d24e9e0394c135ad9d1f90ef7ec91170e01` |
| Initial canonical ledgers | `467047c105ed2d11968e22a68d5156996bf41896cb4b218b658bcb330e23a1b8` |
| Initial episodes.json bytes | `3088e9a339f31fd286562d00151de43a2113aecaf52647013004f7b790991e3f` |
| Initial totals.json bytes | `6e886ff6e89b6b1c0bebbb8849fe2dbd3715ce4db62d6e1370177151f0332798` |
| Canonical totals (reference comparator) | `aa2abf6604467e7c28365eadee47fe9e8d90a1c2d7c563cbc97dd165d61651c6` |
| First freeze.json | `891ae8ef1ef9b44f08c5f70364c3ef77c7261465ae35d2218e350f1bf632ad81` |

Original input hashes:

| Input | SHA-256 |
|---|---|
| AGENT_START_HERE.md | `f8869eccc4a1a71346223f0d8d46324aa4035d66b176cb31318a7694d3d7d2c3` |
| REPLICATION_SPEC.md | `6349f4bfe754b438f2d13888aad496e665bc01a4331b9abe415de452de909f42` |
| trace-inputs.json | `6f54c67509944390c7730438fc2d3058b3cb1aa5a89915674918579e5550b31e` |
| workloads.py | `6382ece9a227fa892bbd7e0a2cd4f7a979b7b2178e9aa1be4ae55e1e1f0ab52e` |
| requirements-reproduce.txt | `3d43a3aa93cf63bba1fe0a2f8cbebcb208bbe3f88263888584b346d6df6fa2c8` |
| tokenizer-files.sha256.json | `4c582268af2eeac1a2cd049c5e08bf245ee8ebe95e223c5c1c9b30ced6cc3932` |

The extracted approved sources and fixtures are retained separately. `final-validation.json` records their file hashes as well as the exact wrapper's independently frozen source and fixture hashes. Tokenizer asset hashes and full package versions are in the first manifest.

## Measured and modeled totals

| Schedule | Profile | Input | Output | Input + output |
|---|---|---:|---:|---:|
| resident | python | 36,222 | 6,066 | 42,288 |
| resident | python_aliases | 34,686 | 5,928 | 40,614 |
| resident | ideal_ain | 27,144 | 3,714 | 30,858 |
| resident | ideal_ir | 27,144 | 3,714 | 30,858 |
| resident | ideal_python | 27,144 | 3,714 | 30,858 |
| inspect | python | 72,006 | 6,066 | 78,072 |
| inspect | python_aliases | 70,470 | 5,928 | 76,398 |
| inspect | ideal_ain | 62,928 | 3,714 | 66,642 |
| inspect | ideal_ir | 62,928 | 3,714 | 66,642 |
| inspect | ideal_python | 62,928 | 3,714 | 66,642 |

resident: `40,614 - 30,858 = 9,756` counted positions saved versus short-alias Python, or `24.02127345%`.

inspect: `76,398 - 66,642 = 9,756` counted positions saved versus short-alias Python, or `12.76996780%`.

The Python rows combine measured Qwen text-token counts and fixed framing positions. The ideal rows combine the same measured common text with declared ideal code units and fixed framing. Equal cost per position is assumed. All three ideal labels tie by construction under the same semantic interface; this experiment establishes no advantage unique to AIN over equally ideal IR or Python.

## Verification and implementation differences

The independent attempt contains 144 supplied episodes (72 per data schedule), 432 logical requests across schedules and 2,160 ledger rows across five profiles. My 17 boundary checks passed, including UTF-8 payloads, bool/integer distinction, signed operand boundaries, generic versus typed lists, invalid values, nonfinite floats, length limits, cycles and depth limits. All 144 episode action replays matched the final artifact, working records, memory and oracle result. Both independently rendered Python forms executed correctly for each episode (288 rendering checks). All 36 repair episodes confirmed that the injected broken program changed the result.

My counter uses direct integer totals and a token cache, rather than the reference's diagnostic breakdown dictionaries. I preserve dictionary insertion order for Python repr/text rendering; generic ideal sums are order-insensitive. I replay the supplied actions and verify rendered lambdas against permitted fixture oracles. The reference additionally reconstructs its semantic episodes itself and validates Python programs through a restricted AST reader. My own result is an independent accounting/rendering recreation from published semantic traces, with approved workload execution reused as the specification permits.

The independent comparator returned exit code 0 with `matches_reference: true`, exact totals and exact per-request ledgers, and `first_difference: null` for both files. The canonical ledger hash independently sealed before comparison equals the comparator's actual and expected ledger hashes. No earliest discrepancy exists.

The exact offline wrapper returned exit code 0, all 20 package tests passed, and fixtures, approved core sources, totals, full episodes (except execution_seconds), summary and normalized manifest matched. Host timings remain in fresh raw outputs. Only episode execution timing is excluded; source path separators are normalized for cross-platform comparison.

## Ambiguities and bugs observed

1. REPLICATION_SPEC says the approved signatures supply operand types, including field-dependent equality types, but config.catalog_schema contains only argument names. The frozen JSON values and special write(program) rule were sufficient to reproduce every count. A generalized typed interface would benefit from an explicit type schema. No alternate accounting was introduced.
2. The generated reference REPORT.md says 'Sixteen focused tests passed', while logs/tests.log records 20 tests, all passing. The sentence is hardcoded in report.py. This is stale reporting prose and does not affect the arithmetic or wrapper comparison.
3. No installation, accounting or environment compatibility bug blocked reproduction. The Windows cache symlink and unavailable model-framework messages were diagnostic only.

## Scientific interpretation

The package makes its premises usable by a new agent: fluent optimized representation, fully approved shared core and correct predefined composition plans. I could reconstruct the integer result from the documented rules without seeing expected numbers. This supports reproducibility of the conditional accounting example. It does not demonstrate that an agent learned AIN, planned the workflows without supplied traces, generated arbitrary new control flow, or used less real inference time, energy or money.

The 18 chains are six variants of three composition templates; the two data schedules replay the same tasks. The functions and loops execute inside the shared approved core. Context exposure, framing, vocabulary, payload packing and tokenization are frozen model choices. Changes to those assumptions or actual model evaluation should be a separately versioned extension.

## Retained files and rerun commands

- `independent_counter.py` and byte-identical `initial-counter-preserved.py`: first independent implementation.
- `initial-v1/episodes.json`, `totals.json`, `renderings.json`, `checks.json`, `manifest.json`, `freeze.json`, `independent-report-before-comparison.md`: unchanged first attempt.
- `initial-canonical-ledgers.json` and `precomparison-seal.json`: canonical ledger and pre-reference provenance.
- `initial-v1/comparison.json`: successful independent reference comparison, added after the freeze.
- `exact-reference-offline-v1/`: separate fresh reference artifacts, environment, report, comparison and complete tests/run/report logs.
- `final-validation.json`: post-comparison integrity, package pins, checks and extraction hashes.

Run from the checkout root with the pinned Python environment. The independent script has no user-specific filesystem paths; it expects its prescribed location at work/independent-agent and accepts a fresh output directory via CLI. Tokenizer assets resolve under work/tokenizer-cache.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:HF_HOME=Join-Path (Get-Location) 'work\tokenizer-cache'
& $envPython experiments/approved_workflow_theory/reproduce.py --prepare-tokenizer
& $envPython work/independent-agent/independent_counter.py --output work/independent-agent/new-independent-attempt
# Preserve and seal the new implementation/outputs before comparing.
& $envPython experiments/approved_workflow_theory/reproduce.py --compare work/independent-agent/new-independent-attempt
& $envPython experiments/approved_workflow_theory/reproduce.py --offline --output work/independent-agent/new-exact-reference-attempt
```

The original attempt remains preserved. No correction or extension was needed to match.
