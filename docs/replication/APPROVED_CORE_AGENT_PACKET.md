# Downloadable approved-core replication packet

The ZIP produced by `tools/build_approved_core_agent_packet.py` is intended for
Grok and other AI agents to reproduce the latest approved-core accounting test.
It contains the unchanged frozen experiment, semantic traces, exact dependency
pins, comparison code, reference and earlier-agent evidence, bundled pinned
tokenizer assets and license, setup/cache helpers, a Grok assignment and a pending
submission template. Draft 10 PDF/Word may be added under `review-after-seal/`.

The top-level `START_HERE.md` separates independent reconstruction from exact
reference-code replay. An independent agent should preserve and seal its first
counter and ledgers before reading expected totals or the new article. If it has
already read them, it must disclose prior exposure instead of claiming blinded
independence. Reference/validation files remain at original paths because the
frozen package manifest and exact comparison depend on them.

## Build

From the repository root, with Python 3.12:

```text
python tools/build_approved_core_agent_packet.py --output work/agent-packet/AICC_Approved_Core_Agent_Packet.zip --article-pdf PATH_TO_DRAFT10.pdf --article-docx PATH_TO_DRAFT10.docx --article-source docs/article/AICC_Article_Draft_10.md
```

Article arguments are optional for a replication-only package. The builder
creates a fresh staging directory, verifies the original package hashes, verifies
all six tokenizer asset hashes, writes a complete payload manifest and creates a
ZIP plus a small external ZIP-hash/size manifest. It never includes model weights,
credentials, `.venv` or arbitrary working-directory files.

The first build downloads only missing public tokenizer assets at the frozen
revision. `--no-download` requires an already populated verified local asset
cache. `--overwrite` is needed to replace an existing named ZIP. Frozen study
files are never edited by packaging.

## Recipient setup

Extract the ZIP, open `START_HERE.md` and select a route. Standard commands are:

```text
python scripts/verify_packet.py
python scripts/setup.py
python scripts/run_reference.py --output work/grok-exact-001
```

The setup helper creates a private `.venv` and installs the exact pinned research
requirements. Internet may be needed for Python packages; the ZIP is not a full
offline Python distribution. The bundled tokenizer assets seed a private Hugging
Face cache, so the reference run itself uses `--offline` and requires no Hugging
Face asset download or model framework/weights. Existing prepared environments
may use `--skip-install` and `--current-python`, with any package-pin differences
reported as deviations.

The assigned test is CPU-only conditional accounting with prescribed correct
actions. It is separate from a future learned whole-agent training experiment.
The packet's Grok result fields remain `??` or null until actual evidence arrives.
The owner will send the ZIP to agents and return their result files; this build
does not send messages or claim any pending replication has executed.

## Packaging validation

The replication-only packet was extracted into a fresh Windows directory with
spaces in its path. Its payload manifest verified, setup created a private Python
3.12 environment and installed the pinned requirements, and the bundled tokenizer
cache was used with the frozen wrapper's `--offline` mode. The actual test log
records 21 passing checks; all six deterministic reference comparisons matched.
The original package's 59 hashes and all six tokenizer asset hashes verified.
No model weights, inference calls or GPU were needed for this smoke test.

PDF/Word and chart assets added to the final packet are additional post-seal
review material. The final builder verifies their bytes in the packet manifest
without changing the frozen test. The public reference report contains historical
test-count prose; use the actual versioned test log when reporting check counts.
