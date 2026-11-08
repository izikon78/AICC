# Independent reconstruction route

Read this guide before opening result-bearing material. If expected counts or
the article have already been read, record the exposure and describe the work
as a prior-exposed reconstruction. A useful exact replay remains available.

1. Record provider, model identity as reported, date, environment and read order.
2. Read [the standalone language theory](../AIN_THEORY.md). It explains the
   conceptual notation. The accounting experiment uses the precise semantic
   format and cost rules in `REPLICATION_SPEC.md`, which govern reconstruction.
3. Read only these study inputs initially, using paths from the extracted root,

```text
experiments/approved_workflow_theory/REPLICATION_SPEC.md
experiments/approved_workflow_theory/trace-inputs.json
experiments/approved_workflow_theory/workloads.py
experiments/approved_workflow_theory/requirements-reproduce.txt
experiments/approved_workflow_theory/tokenizer-files.sha256.json
tokenizer-assets/SOURCE.json
```

The traces supply correct actions, requirements, inputs and observations. They
contain no reference aggregate ledger. The permitted workload implementation
defines the executable approved operations. Implement the accounting and Python
renderer independently from those semantic inputs and the specification.

Do not open `accounting.py`, `run.py`, `report.py`, `reproduce.py`, study README,
`ARTICLE_REPRODUCTION_BRIEF.md`, study `results/` or `validation/`, publication
evidence/figures/article, or archived local-study outcomes before preserving a
first seal. Result-bearing files remain at their original paths for manifest
integrity and post-seal comparison. Their presence is not a direction to read
them early. The packet manifest exposes paths and hashes, not aggregate counts.

Write your first `episodes.json` and `totals.json` exactly as specified. Preserve
the untouched counter, tokenizer/input hashes and outputs, record their SHA-256
values and timestamp in a seal, and list everything read before it. Preserve
the first attempt even when it fails.

After sealing, open the frozen comparator and run,

```text
python experiments/approved_workflow_theory/reproduce.py --compare work/independent-first
```

The comparator writes the first mismatch and exits nonzero when comparison
fails. Explain any discrepancy. Corrections belong in a separately versioned
folder. Then follow Route B for a reference-code environment replay and read
the published outcomes and prior agents.

This route tests independent reconstruction of prescribed accounting and
execution of supplied operations. It provides no test of an agent discovering
the workflow, learning AIN from scratch or reducing actual inference cost.
