# Final publication figures and data

Prepared 8 November 2026 under Izik Bachar's research direction. The four
quantitative figures retain the verified observations from the final experiment
records. The additional workflow diagram depicts the proposed complete system.
Each figure has a 300-dpi PNG and a vector SVG with selectable text. At the
intended 6.5-inch printed width, all labels are at least nine points.

| Article order | Figure files | Interpretation |
|---|---|---|
| 1 | `ain-aicc-workflow.png`, `.svg` | Proposed learned-agent and governed execution architecture, with optional charged human-readable projection |
| 2 | `processing-cost.png`, `.svg`, `.csv` | Within-host pipeline medians normalized to each record's own reference |
| 3 | `memory-cost.png`, `.svg`, `.csv` | Process-lifetime peaks normalized within each host and workload |
| 4 | `adaptation-correctness.png`, `.svg`, `.csv` | Assigned-task correctness in two local model screens with different interfaces and evaluation caps |
| 5 | `approved-core-demand.png`, `.svg`, `.csv` | Conditional total position demand under the frozen representation model |

## Data identity and scope

`chart-data.json` preserves the frozen 7 November observation snapshot, all 22
directly used source-file hashes, raw-derived chart inputs and measurement
boundaries. Its quantitative values and the four CSV files are unchanged from
the audited snapshot. Repository commits and branch names inside the snapshot
record provenance. The final builder reads this local snapshot and the primary
experiment records directly. Earlier article documents and temporary audit
directories are unnecessary.

`render-metadata.json` records the plotting version, dimensions, snapshot hash
and hashes for every PNG/SVG/CSV output. The final builder verifies each primary
source hash before drawing. The complete claim-to-record map is
[the final evidence index](../EVIDENCE.md).

The workflow diagram has no quantitative data. It connects tasks and saved
records, a proposed fluent agent, executable records and memory, host-managed
bindings, approved execution and returned observations. Its caption explicitly
states that existing experiments implement selected components. The complete
learned-agent architecture remains proposed.

## Measurement boundaries

The processing records contain three complete 45-worker matrices using the same
three public workload shapes and seeds. Comparisons normalize separately within
each reported host. Absolute seconds supply no provider-speed ranking. Ordinary
and AICC paths use the same optimized implementations. Process peaks include
imports, inputs, outputs and hashing. Linux RSS and Windows working-set
observations have different definitions.

The local adaptation figure scores Python/readable IR/numeric AIN as 24/15/7 out
of 24 assigned tasks in full format and 24/24/23 in compact form. These are
one-seed screens on reused affine arithmetic cases. Full format has a 90-second
stage cap and 320-token output cap. Compact form has 120 seconds, 64 output
tokens, stronger structural constraints and a common native backend. The figure
describes a development progression with changed interfaces and budgets. It
cannot isolate the causal effect of compilation.

The conditional workflow totals are 40,614 versus 30,858 for resident data and
76,398 versus 66,642 for records in context. Python totals combine measured text
tokens and fixed assumed framing. Ideal totals combine modeled semantic units
with common text/framing. Premises grant fluent language, approved core, supplied
correct composition and equal cost per counted position. Ideal AIN, readable IR
and Python tie. There are zero model inference calls in that accounting run.

## Rebuild

Use Python 3.12 and an isolated Matplotlib environment. From the repository root,

```text
python -m venv work/final-chart-env
work/final-chart-env/Scripts/python.exe -m pip install matplotlib==3.11.2
work/final-chart-env/Scripts/python.exe tools/build_final_figures.py
```

On Unix, the environment's Python is under `bin/python`. The builder's default
output is `publication/figures`. To render elsewhere while using the published
data, supply `--output PATH`. `--data PATH` selects a separately reviewed snapshot.
Changed observations or accounting rules require a new experiment/data version.
The builder does not train models, call a model API or rerun timed workloads.
