# Draft 11 figures and source data

Prepared 7 November 2026 under Izik Bachar's research direction. These figures
were built with Matplotlib from audited, retained observations. PNG and SVG
versions use the same figure objects and data. All text is at least 9 points at
the intended 6.5-inch width. PNGs are 300 dpi, and SVG text remains selectable.

## Figure files

| Files | Quantity and interpretation |
|---|---|
| `processing-cost.png` and `.svg` | Equal-job sums of pipeline medians, normalized to each host's own reference |
| `memory-cost.png` and `.svg` | Process-lifetime peak ratios, normalized separately within each host and workload |
| `adaptation-correctness.png` and `.svg` | Correct cases among 24 assigned tasks in each local representation screen |
| `approved-core-demand.png` and `.svg` | Conditional total position demand for text Python and the shared ideal interface |

The accompanying four CSV files retain full-precision chart inputs.
`chart-data.json` retains the reviewed data, measurement boundaries, branch/base
commit identities and SHA-256 values for every directly used source file.
`render-metadata.json` identifies the plotting version, image dimensions and
output hashes. The builder verifies all frozen input hashes before rendering.

## Processing and memory

The original record was produced by Codex on Windows 11. Claude submitted a
Linux remeasurement, and Grok submitted a second Windows record. Each complete
matrix contains 45 workers. All 135 workers reuse the same three public dataset
shapes and seeds. Source reports retain their self-reported environments and
agent identities. Figure 1 compares within-host reductions and supplies no
cross-provider authoring or inference-speed ranking.

Pipeline medians include selection, applicable feature/inference work, host setup
and processing. The mixture gives each workload one equal weight and sums its
three-repeat cell median. Figure 2 uses lifetime process peaks including imports,
inputs, outputs and hashing. Linux RSS and Windows working-set accounting have
different definitions. Each peak comparison uses that workload's own host
reference. The ordinary and AICC paths use the same eligible optimized code.

## Adaptation diagnostic

The full-format screen scores Python 24/24, readable IR 15/24 and numeric AIN
7/24. The compact/native screen scores 24/24, 24/24 and 23/24 respectively.
Both use one Qwen2.5-1.5B checkpoint, one seed and 288 training presentations per
arm. These are related, reused arithmetic cases. Full format has a 90-second
stage cap and 320-token output cap. Compact form has a 120-second stage cap and
64-token output cap. Full-format IR skips four assigned tasks at its stage time
limit, and AIN skips five. Assigned tasks remain in the denominator.

Serialization, structural constraints, backend and caps all change between
these two screens. Figure 3 presents development diagnostics. It supplies limited
evidence about broad generalization or the causal contribution of compilation.
Raw files retain unsuccessful predictions, exact source hashes and timings.

## Approved-core theory

The resident-data totals are short-alias Python 40,614 and ideal interface 30,858.
The inspect-data totals are 76,398 and 66,642. Conditional reductions are 24.0213%
and 12.7700%. The Python values combine measured Qwen text tokens with fixed
assumed framing. Ideal values
combine modeled semantic units with the same common text and framing. Comparing
totals assumes equal cost per counted position.

Ideal AIN, readable IR and Python have identical values under the same learned
interface. The premises grant fluent language knowledge, approved shared core
code and supplied correct composition. Each schedule contains 18 chains and
72 executed stages; the two schedules replay the same semantic tasks. Model
inference calls inside this theory benchmark are zero. GPU throughput, billing,
energy and learned-agent task success require their own measurements.

## Rebuild

Use an isolated chart environment, keeping experiment environments separate.
From the repository root,

```text
python -m venv --system-site-packages work/article11-chart-env
PATH_TO_CHART_ENV_PYTHON -m pip install matplotlib==3.11.2
PATH_TO_CHART_ENV_PYTHON tools/build_article11_figures.py
```

The default build reads this folder's published data snapshot and verifies the
referenced raw files in the repository. The `--refresh` option regenerates the
snapshot from the two original audit JSON inputs. Use `--processing-audit` and
`--latest-audit` to provide their locations during a separately reviewed update.
Preserve a new article/data version if observations or accounting rules change.
