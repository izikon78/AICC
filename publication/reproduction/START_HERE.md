# Reproduce the final experiments

Concept and research direction by Izik Bachar. Packaging and checks by Codex.
This guide stands alone. Prior knowledge of AIN or previous article drafts is
unnecessary. The [language theory](../AIN_THEORY.md) explains the notation and
the premises used by the final study.

Download [AICC_Final_Experiments_Packet.zip](https://github.com/izikon78/AICC/raw/refs/heads/codex/ain-final-draft/publication/downloads/AICC_Final_Experiments_Packet.zip),
extract it and run the commands below **from the extracted packet root**. The
ZIP is a curated copy of the final experiment sources and records. It contains
no model weights, saved adapters, credentials or previous article drafts.

## Select a route before reading outcomes

| Route | Question | Requirements |
|---|---|---|
| A Independent reconstruction | Can another agent reconstruct the prescribed accounting from its specification? | Python 3.12, pinned tokenizer/packages, independently written counter |
| B Exact reference replay | Does the frozen implementation produce the same deterministic result? | Python 3.12, CPU, pinned packages |
| C Native compiler checks | Do the compact source forms execute equivalent bounded integer programs? | Python, CPU and llvmlite 0.44.0 |
| D Processing study | Can another host rerun the completed processing workload and compare within-host behavior? | Python, NumPy, sufficient RAM/time |
| E Adaptation research | Can another investigator rerun the saved small-model learning configuration? | Separate CUDA/PyTorch environment, model download and suitable GPU |

Route A must preserve its first implementation, outputs and hashes before opening
result-bearing files. Reading this article or earlier totals is prior exposure.
Disclose it and label the reconstruction accordingly. Route B is a known-answer
replay. It establishes code/output compatibility and makes no independence claim.

For Route A begin with [the independent guide](INDEPENDENT_RECONSTRUCTION.md).
The archived `experiments/approved_workflow_theory/AGENT_START_HERE.md` is retained
byte-for-byte because the frozen package manifest hashes it. Its earlier reading
navigation is superseded by this guide and the standalone theory document. No
earlier article is required or included.

## Route B Exact reference replay

From a fresh extraction with Python 3.12,

```text
python scripts/verify_packet.py
python scripts/setup.py
python scripts/run_reference.py --output work/reference-001
```

Setup creates a private `.venv`, installs the exact approved-core dependency
pins, verifies six bundled tokenizer assets and seeds a private cache. Dependency
installation may need the Internet. The test itself then runs offline with no
model-weight download, inference call or GPU. The packet is not an offline Python
distribution.

For an already prepared Python 3.12 environment,

```text
python scripts/setup.py --skip-install
python scripts/run_reference.py --current-python --output work/reference-001
```

Record all package differences from `requirements-reproduce.txt` as deviations.
Do not overwrite a first output folder. Preserve failures and later corrections
in separate folders. The wrapper saves its environment, test log, complete
request ledgers and six deterministic comparisons. Runtime durations are excluded
from exact ledger comparison.

## Routes C, D and E

[SUPPLEMENTARY_TESTS.md](SUPPLEMENTARY_TESTS.md) gives commands, dependency
boundaries and interpretations for compiler, processing and adaptation work.
The final source and saved records are included. A check of those saved records
is distinct from a fresh training or million-event execution.

## Interpretation and return evidence

The approved-core test executes supplied correct compositions. It counts measured
Python text tokens and modeled ideal code units under fluent-vocabulary,
approved-core, perfect-composition and equal-position-cost premises. Actual
learned-agent inference speed, planning success, energy and billing require
separate measurements. Equal ideal interfaces receive equal encoding treatment.

Fill `SUBMISSION_TEMPLATE.json`. Return the report, provider/model identity as
reported, prior exposure/read order, environment, complete first outputs, source
and input hashes, test/comparison logs, all failures and deviations. Report actual
authoring-provider usage when available. Unknown usage remains unknown. Keep
authoring-agent usage separate from the CPU experiment's model-inference count.

The frozen reference and prior Codex/Claude records are available for comparison
after a first seal. Grok has a completed earlier processing record; its
approved-core reconstruction remains pending. No recipient result is assumed
by this package, and no submission is sent automatically.

`PACKET_MANIFEST.json` identifies every payload file and SHA-256 value.
`AICC_Final_Experiments_Packet.manifest.json` beside the ZIP records the archive
hash and size. These are integrity records, not external proof of model identity.
