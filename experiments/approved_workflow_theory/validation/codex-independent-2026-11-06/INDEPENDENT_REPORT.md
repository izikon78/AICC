# Independent reconstruction: first attempt matched

I reconstructed this accounting without prior AIN background on Git commit
`395278bc369b1c33141381a73872725ca4dd4a7b`. Both the first independent
counter and a subsequent exact offline reference rerun matched the published
results. No corrections to the counter or ledgers were needed.

**Read order.** I began only with AGENT_START_HERE.md, then read
REPLICATION_SPEC.md, semantic trace-inputs.json, pinned requirements and tokenizer
hashes. I ran only tokenizer preparation and consulted the expressly permitted
workloads.py for approved execution components and fixture oracles. I wrote my
own counting, Python rendering, recurrence and aggregation code. Before seeing
reference accounting.py/run.py/report.py, article observations, aggregate counts
or reference ledgers, I preserved source, all first ledgers, totals, environment
and hashes. I compared only after freezing; reference implementation review
followed the successful runs. The seals are local provenance records rather than
third-party timestamp attestations.

**Frozen evidence.** Source SHA-256:
`e56101a0937ef7285fddc9910b5f1d24e9e0394c135ad9d1f90ef7ec91170e01`.
Canonical ledger SHA-256:
`467047c105ed2d11968e22a68d5156996bf41896cb4b218b658bcb330e23a1b8`.
Canonical totals SHA-256:
`aa2abf6604467e7c28365eadee47fe9e8d90a1c2d7c563cbc97dd165d61651c6`.
The comparator confirmed the same ledger/totals hashes, with no differing field.
`precomparison-seal.json`, `initial-v1/freeze.json` and
`initial-v1/manifest.json` preserve dates, byte hashes and consulted materials.

| Schedule | Short-alias Python input/output | Ideal input/output | Total reduction |
|---|---:|---:|---:|
| resident | 34,686 / 5,928 | 27,144 / 3,714 | 24.02127345% |
| inspect | 70,470 / 5,928 | 62,928 / 3,714 | 12.76996780% |

**Checks and environment.** All 144 episodes, 2,160 profile/request ledger rows,
17 independent boundary checks, 144 execution replays and 288 rendered-Python
execution checks passed. The injected defects changed results in all 36 repair
episodes. The independent comparator returned exit 0 and exact matches; the
separate reference wrapper returned exit 0, passed all 20 package tests and
matched fixtures, sources, totals, episodes, summary and normalized manifest.
Only episode execution_seconds was excluded from deterministic comparison.
Python 3.12.14 on Windows 11 used the CPU-only pinned dependencies; every
applicable package pin matched. All six assets of Qwen/Qwen2.5-1.5B revision
`8faed761d45a263340a0528343f099c05c9a4323` were verified.
Full package, source, fixture, input and tokenizer hashes are retained in the
manifests and final-validation.json. All mutations stayed under checkout/work/;
tracked files remained unchanged.

**Two findings, as observed on this commit.** The specification says signatures
supply operand types, but catalog_schema lists only argument names. JSON value
types and the special program rule sufficed for this frozen workload; a general
interface needs an explicit type contract. The generated report says sixteen
tests passed, while its tests.log records twenty, all passing. This stale prose
does not change the counts.

Python text tokens are measured; ideal units are modeled. Common text and ideal
units share an assumed cost per position. Approved components, fluent
representation and correct supplied composition are premises. Ideal AIN, IR and
Python tie. The result reproduces conditional accounting across three workflow
templates, not measured model learning, planning success, latency or energy.

**Retained files.** independent_counter.py (also initial-counter-preserved.py);
initial-v1/ (untouched first ledgers/totals/renderings/checks/provenance plus later
comparison.json); initial-canonical-ledgers.json; precomparison-seal.json;
exact-reference-offline-v1/ (fresh raw artifacts and logs); final-validation.json;
and INDEPENDENT_REPORT_DETAILS.md. No failed measurement attempt or corrected
accounting version occurred.
