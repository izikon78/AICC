# Local representation comparison v1

8 November 2026. Concept and research direction by Izik Bachar. Local implementation
and execution by Codex. This is a bounded CPU serialization/semantics experiment.

All five profiles preserved the supplied workflow computations. Compact Python
with compact JSON state had the smallest observed text-token total. The symbolic
AIN view had the largest total. No model generated these artifacts during this
test; its outputs are deterministic fixture representations.

| Profile | Resident input | Resident output | Resident total | Inspect total |
|---|---|---|---|---|
| Python repr | 35,118 | 5,712 | 40,830 | 76,614 |
| Compact Python | 32,316 | 4,548 | 36,864 | 72,648 |
| Readable positional IR | 35,280 | 5,490 | 40,770 | 76,554 |
| Numeric positional arrays | 34,092 | 5,274 | 39,366 | 75,150 |
| Symbolic AIN sketch | 37,908 | 5,634 | 43,542 | 79,326 |

There are 2,160 serialized-request ledger rows and 720 decoded-stage checks.
All decoded actions, independent fixture results, final artifacts, working records
and outgoing memory matched. Fifty separate probes preserved new/long/Unicode
literals, delimiter characters and continuation-relevant deduplication state.
Four regression tests check malformed/unsafe input rejection and typed roundtrips.

The manifest freezes five profiles, example-local IDs assigned by sorted public
operation names and the pinned Qwen2.5-1.5B tokenizer revision. It hashes all
direct implementation/protocol/input dependencies before measurement. These are
local integrity records, not an externally timestamped preregistration. No profile
was tuned or selected after observing its result.

The common task input uses the original frozen rendering. State and observations
use repr in the first profile and compact UTF-8 JSON in the other four. Complete
request strings are tokenized once; diagnostic isolated-component sums retain an
explicit wrapper/boundary difference. No ideal code units, special tokens or
estimated chat framing are included. The observations were executed and decoded
locally; no task-solving probability, inference throughput or economic saving
was measured.

The symbolic AIN codec implements only an approved-call sketch. It does not
define a complete language, optimize the candidate vocabulary or measure a
model already fluent in native semantic tokens. Numeric arrays are a separate
serialization ablation. The profiles share identical approved operation bodies,
including their internal loops. New algorithms, tool discovery and unfamiliar
control-flow composition are outside this test.

The existing eighteen chains and their three templates are reused. The two data
schedules are two views of the same tasks. Supplied correct plans are executed;
they are not newly authored by agents. Named external research systems were not
run. Their relevance is documented separately in the article and related-work
comparison.

Source and environment identities are in `manifest.json` and `environment.json`.
The full strings, component counts and whole-context counts are in `ledger.json`.
`stage-checks.json`, `probes.json`, `totals.json`, `totals.csv` and `summary.json`
retain the raw outcomes. The approved-core ideal-interface calculation remains
a separately labeled theory experiment.
