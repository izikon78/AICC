# Independent package validation

A separate Codex agent started with no AIN conversation history in a fresh Git
checkout at commit `395278bc369b1c33141381a73872725ca4dd4a7b`. It read the agent
start guide, specification and semantic inputs, then wrote its own renderer and
counter. Approved workload components were reused under the published premise.

The first result was sealed before comparison. It matched both schedule totals
and every one of the 2,160 per-request ledger rows. The subsequent exact offline
rerun also matched every deterministic reference file. The retained evidence
includes the original independently written counter, pre-comparison seal,
canonical ledgers, raw observations, boundary/execution checks and comparisons.

The agent reported seventeen boundary checks, 144 workflow execution checks and
288 Python-rendering execution checks. It recorded zero corrections to its first
implementation before obtaining the match. Consult its own report for reading
order and limits. This is a separate-agent reconstruction within the same Codex
session and machine. External agents can provide additional independent reviews.

Two packaging findings were addressed after the tested commit. The specification
now lists explicit operand-type contracts for the supplied cases. The report
generator describes test outcomes through the accompanying logs instead of a
hardcoded count. The reproduction comparator also records malformed external
outputs as structured mismatches. The primary frozen accounting inputs are
identified by the original source and fixture hashes.

## Rerun the archived independent implementation

The archived source expects the documented work-directory location. From a fresh
repository checkout after installing the CPU requirements, copy
`independent_counter.py` to `work/independent-agent/independent_counter.py`. This
restores its repository-relative package lookup and preserves its content hash.
Prepare the pinned tokenizer with the main package's `--prepare-tokenizer` option.
Then run

```text
PATH_TO_ENV_PYTHON work/independent-agent/independent_counter.py --output work/independent-agent/your-new-run
PATH_TO_ENV_PYTHON experiments/approved_workflow_theory/reproduce.py --compare work/independent-agent/your-new-run
```

The counter reads the supplied semantic trace inputs and writes fresh observations.
Its original SHA-256 is
`e56101a0937ef7285fddc9910b5f1d24e9e0394c135ad9d1f90ef7ec91170e01`.
Keep every new attempt in a fresh output directory. Review the archived reference
evidence only after preserving your independent first result if following the
article's independent-reconstruction workflow.
