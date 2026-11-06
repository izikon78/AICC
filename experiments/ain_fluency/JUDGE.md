# Deterministic controller judge

`judge_artifact(path, mode, stage, delta)` in `judge.py` returns a JSON-compatible
report with overall `passed`, `cases`, `passed_cases`, per-case `details`, condition
labels, and the artifact SHA-256. Modes are `python`, `ir`, and `ain`; stages are
`build`, `change`, and `repair`; delta is 30 or 75. Invalid condition labels raise
`ValueError`; invalid artifacts, runtime exceptions, and timeouts fail the judge.

The build stage implements the original frozen AIN v0 streaming controller. The
change and repair stages require the added severity threshold:

```
if admitted_event.timestamp - frontier < delta:
    threshold = min(3, configured_minimum + 1)
else:
    threshold = configured_minimum
```

Full envelope and payload validation precedes all event decisions. Late events
(`timestamp < frontier`) do not reserve an ID. An admitted ID is reserved before
the severity decision, including when that first event is filtered. An end or
watermark drains every eligible buffered event before scoring and committing.
Equality to the frontier is admissible; equality to the delta uses the configured
minimum. These semantics are identical for all three representations.

## What is checked

Each artifact receives the same 55 cases with the same 23 frozen capabilities:

- Four independently calculated boundary traces cover configured minima 0–3,
  equality to the frontier, one tick before the delta, equality to the delta,
  repeated IDs, filtered-first IDs, and a multi-event end drain. Their counters,
  group timestamps, first offsets, counts, severity sums, and commit offsets are
  explicitly asserted rather than inferred by comparing representations.
- Further fixtures cover stable timestamp/offset ordering, anchored windows,
  normalization, EOF versus end, dedupe expiry, malformed late/duplicate events,
  preserving an earlier commit on a future validation error, capacity limits,
  cancellation, policy errors, and policy/precommit authority denial.
- Twenty reproducible streams each contain 50 arrivals and an explicit end.
  Seeds are `880000 + delta * 100 + stream_number`, with duplicate IDs,
  watermarks, events around the frontier, severity levels, and text variants.
- Two crash/replay cases use fresh in-memory sinks and compare both the failed
  prefix and the resumed outcome, for failure before commit and a lost commit
  acknowledgment.

The expected controller is written independently in `reference`; it does not
import the original controller or compare Python output only to AIN output.
It uses the same capability host to isolate orchestration. For every case, the
candidate's returned result and a separate observation of the host's published
result must both equal the expected canonical object, including reports,
checkpoints, counters, trace, status, and error. Operation wrappers also require
an explicit cancellation check before each source admission and complete record
validation before its fields are inspected or processed. Manual error fixtures
assert their expected error category so that an unintended shared failure cannot
pass solely through agreement.

## Execution limits and qualification

Each complete suite runs in a fresh subprocess with a 45-second wall-clock cap.
Artifacts may contain at most 128 KiB. Each IR/AIN invocation has 200,000 VM fuel.
Python artifacts define `run(host)` and use a restricted set of builtins, with no
imports or access to host internals. Host operations must be obtained through
`host.catalog()`; dictionary `.values()`, `.items()`, and `.get()` are supported.
These restrictions control this cooperative experiment; they are not a secure
sandbox against malicious submissions. The existing host remains unchanged.

Qualification tests run the original frozen controller in all three forms,
independently constructed changed IR and encoded AIN at both deltas, the direct
Python oracle serialization, and each of the three type-valid repair defects.
They also check returned-result forgery, missing admission cancellation checks,
load restrictions, artifact size, and timeout reporting. They are deterministic
judge tests, not model-participant observations.

Run qualification from the repository root:

```
python -m unittest discover -s experiments/ain_fluency/tests -p test_judge.py -v
```

## Limits of the evidence

The shared host's algorithms, private-policy fixture, and in-memory sink are
trusted dependencies, not independently reimplemented semantics. Passing this
suite is not a proof of correctness, production durability, security, or model
pretraining fluency. Seeds and cases are public development material, not a
hidden benchmark. There is no production deep-learning workload here. The
judge measures faithful controller construction, change, and repair over a
fixed capability interface; token and time measurements belong to the external
participant runner. The host manifest does not bind the controller's code hash;
the judge records the artifact hash separately.
