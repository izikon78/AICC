# Matched local representation test

This is one CPU test of five local text serializations over the existing approved
workflow fixtures. It makes no inference calls and performs no model training.
The [frozen protocol](PROTOCOL.md) defines the profiles and measurement boundary.

The test uses the same approved functions, correct actions, task data and saved
state for every profile. A restricted decoder restores each plan and action
batch, then the shared host executes the restored computation against the
independent fixture oracle. Both data-placement schedules are retained.

Run from the repository root with the approved-core dependency pins and its
cached tokenizer,

```text
python -m unittest discover -s experiments/representation_comparison -p test_*.py -v
python experiments/representation_comparison/run.py --output work/comparison-new
```

Choose a fresh output folder. The official observed run is
`results/comparison-v1/`. Its manifest hashes this protocol, implementation,
regression checks and frozen semantic inputs before token measurement. All raw
request/response strings are retained. A run cannot replace existing results.

## Observed result

All 720 decoded stage executions matched their expected outputs, final artifacts
and saved state. All 50 separate literal/state probes passed, as did four focused
apparatus regression tests. These are supplied correct compositions, not model
task-success trials. The 144 episodes reuse eighteen chains under two schedules.

| Local text profile | Resident input/output | Resident total | Inspect total |
|---|---|---|---|
| Python aliases, repr state | 35,118 / 5,712 | 40,830 | 76,614 |
| Compact Python, compact JSON state | 32,316 / 4,548 | 36,864 | 72,648 |
| Readable positional IR | 35,280 / 5,490 | 40,770 | 76,554 |
| Numeric positional arrays | 34,092 / 5,274 | 39,366 | 75,150 |
| Symbolic AIN sketch | 37,908 / 5,634 | 43,542 | 79,326 |

Compact Python uses the fewest text tokens in this declared comparison. The
symbolic sketch uses 18.12% more resident total tokens and 9.19% more inspect
total tokens than compact Python. This result concerns the particular
serialization and pinned existing tokenizer. It supplies no result about a
future optimized learned AIN vocabulary. Numeric arrays isolate one encoding
choice and do not replace the article's symbolic notation.

## Interpret the counts

Each complete fixture context is tokenized once with the pinned Qwen tokenizer,
without special tokens. Literal action text is also tokenized once. The raw
context uses explicit A/M/H and X/O wrappers, not a provider chat template.
There are no hypothetical semantic units or estimated chat framing charges in
these totals. Isolated component counts are diagnostic; the raw ledger records
the full-context boundary difference explicitly.

The earlier approved-core theory result uses ideal learned units and assumed
framing. Its 24.0% and 12.8% figures remain a separate conditional calculation.
Totals from that calculation and this actual-text test should not be treated as
two runs of the same measurement. All five new profiles share the same repeated
exposure schedule, and neither test measures inference latency or billing.

The [related-work comparison](../../publication/RELATED_WORK.md) discusses
ToolkenGPT, CodeAct, AINL and other approaches. Those external systems were
reviewed through their primary publications/documentation and were not executed
by this local test. These local profiles are not replicas of those systems.
