# Proposed AIN task: a transactional streaming workflow

Status update, 5 November 2026: this contract now has an [AIN v0 development implementation](../../experiments/ain_v0/README.md), shared Python/IR controls and local engineering measurements. The original numeric sketch below remains illustrative; the implemented grammar is documented in [LANGUAGE.md](../../experiments/ain_v0/LANGUAGE.md). Neither is evidence of a language-trained model.

The task is intended to test whether an agent can express, change, and optimize substantial computation with a precise machine-oriented representation. It combines event-time ordering, retained state, private policy, bounded asynchronous work, and atomic publication. AICC could supply some capabilities; the identical bodies and contracts must also be available through ordinary libraries.

This is a **new contract**. The [frozen processing kernels](../../experiments/processing_study/KERNEL_CONTRACT.md) deduplicate globally over a finite input and return their groups. This proposal has finite-horizon deduplication, watermarks, durable checkpoints, and effects. Its future measurements must not be pooled with the existing million-event results or described as the same behavior.

## Inputs and fixed example configuration

A source is a replayable, single-consumer log with stable record offsets. A record is an event, a watermark, or an explicit end marker. A crash is not an end marker. Only one writer may advance a given source's committed checkpoint; a fencing token rejects stale writers.

| Parameter | Example value | Meaning |
|---|---:|---|
| `window` | 600 | Anchored grouping width, in integer logical ticks |
| `lateness` | 120 | Frontier lags the latest watermark by this many ticks |
| `dedupe_horizon` | 1,200 | Event-time retention after the first admitted occurrence |
| `concurrency` | 8 | Maximum running private-policy calls |
| `queue` | 32 | Maximum waiting private-policy calls, excluding running calls |
| `buffered_events` | 100,000 | Maximum admitted events awaiting event-time processing |
| `dedupe_entries` | 200,000 | Maximum retained event IDs |
| `open_groups` | 100,000 | Maximum unfinished groups |
| `epoch_reports` | 100,000 | Maximum finalized reports staged for one transaction |

All parameters are positive integers except `lateness`, which may be zero. Booleans are not integers for this contract. The horizon must be at least the window width. Limits are part of the task, not parameters an optimizer may silently raise.

Every event has exactly seven fields: strings `tenant`, `event_id`, `device`, `kind`, and `message`, plus integer `timestamp` and `severity`. Timestamps and stable record offsets are between zero and signed 64-bit maximum; severity is 0 through 3. Tenant and event ID are nonempty and at most 128 Unicode scalar values; tags are at most 256 and message at most 4,096. Reject unpaired surrogates. Validate every record before deciding whether it is late, duplicate, or below a severity threshold. Use plain decoded values, not objects with user-defined accessors.

The task receives a tenant-scoped, versioned private scoring function and a publication sink. The agent receives their interfaces and permitted test fixtures, not production private-rule source. A synthetic fixture is not evidence that the host protects secrets from adversarial code.

## Observable stream semantics

1. **Admission and offsets.** Input offsets strictly increase. Validate the complete record at its source offset. A valid watermark is nondecreasing; a decreasing watermark is an error. Start with watermark zero. For a watermark `W`, define frontier `C = max(0, W - lateness)`.
2. **Late records.** An event arriving with `timestamp < C` is counted as late and discarded. Equality is admitted. A late event does not reserve an ID. Timestamps need not be in order among admitted events.
3. **Finite dedupe.** Among currently retained IDs, the first admitted input occurrence of `(tenant, event_id)` wins, regardless of a later duplicate's timestamp, content, or severity. Reserve an ID before severity filtering. A low-severity first occurrence can therefore suppress a later high-severity duplicate. Retain it until a watermark advances `C >= first_timestamp + dedupe_horizon`; then evict it. A new admitted occurrence after eviction is new work. This is deliberately not global deduplication.
4. **Normalization and filtering.** Normalize device and kind with Unicode NFKC, case folding, then whitespace collapse. Collapse message whitespace while preserving case. Collapse replaces each maximal whitespace run with U+0020 and trims both ends; the whitespace set is U+0009–000D, U+0020, U+0085, U+00A0, U+1680, U+2000–200A, U+2028, U+2029, U+202F, U+205F, and U+3000. Pin Unicode 15.0.0 for normalization/case folding in the initial condition; another version is a separate dependency condition. The example minimum severity is one; a configurable minimum must be an integer from zero through three, excluding booleans. Tenant and event ID are exact identifiers and are never case folded.
5. **Event-time processing.** Buffer surviving admitted events. At each watermark, consume all buffered events with `timestamp < C`, in ascending `(timestamp, source_offset)` order. Rows exactly at the frontier wait. No source record after that watermark is consumed until its epoch has either committed or failed.
6. **Anchored groups.** Group by `(tenant, normalized_device, normalized_kind, normalized_message)`. For each key, an event joins its newest group exactly when `event.timestamp - group.first < window`; otherwise open a new group. Track first/last timestamp, first offset, count, and severity sum. The window does not slide with the last event.
7. **Finalization.** A group is complete when `group.first + window <= C`. Sort all groups finalized in an epoch by `(first_timestamp, first_offset)`. Exact arithmetic is used for frontier/window/horizon comparisons; intermediate additions cannot wrap. Count and severity sum must fit a signed 64-bit result; detect overflow and fail the epoch, without wrapping or publishing partial reports.
8. **End marker.** A valid explicit end marker drains all remaining buffered events and finalizes all groups. Treat it as a logical positive-infinity frontier, not a maximum timestamp that could lose boundary events. Publish the final checkpoint and mark the source complete. A new event after that checkpoint is an error.

Late, duplicate, filtered, and accepted counters belong to the epoch checkpoint. Define each raw event's category in that order; a duplicate is not counted again as filtered. Normalization and exact dedupe must preserve the specified result even if caching or partitioning changes the execution flow.

## Private work, concurrency, and failure

Invoke the pinned private-policy version once for each finalized group. For a group and version, the policy is deterministic and free of external side effects. It returns an integer score from 0 through 1,000 and an allowlisted numeric reason code, or a declared error. Output reports contain the group fields, score, reason code, policy version, and a stable group identity derived from source identity and first offset. Private intermediate data are excluded from logs and reports.

At most eight calls run and at most 32 wait in the example configuration. Apply backpressure before reading more source input; do not discard or reorder work to satisfy those limits. Completion order is arbitrary. Publication order must still follow the finalized-group order. Limits also apply when an operator is fused or implemented in another language.

Complete and inspect the epoch's policy outcomes before publication. If calls fail, report the failed group with the lowest finalized-group index, irrespective of completion order. An implementation may continue the remaining epoch calls to make this result deterministic. No report from that epoch becomes visible.

Check host authority immediately before each policy invocation and before transaction commit. AICC binding, if used, must satisfy the same rule. Batching calls is not equivalent if it removes required checks. This is a cooperative in-process contract, not preemption or a production security boundary.

Cancellation is a caller-level token. Check it before admission of the next source record, before starting each policy call, and immediately before commit. Once observed, start no new policy calls, request cooperative cancellation, drain running calls, discard that epoch's uncommitted state and reports, and return `CANCELLED`. A running policy call need not stop in the middle of an instruction. Completed earlier epochs remain committed. No real-time cancellation bound is claimed. A cancellation observed during an epoch takes precedence over its policy-error result.

## Atomic publication and recovery

At a watermark, stage one transaction containing the ordered reports, counters, source cursor, watermark, retained dedupe entries, buffered events, and unfinished groups. The policy/version manifest and configuration are part of the checkpoint identity. Do not commit while policy work remains outstanding.

The sink must atomically publish the reports and the corresponding checkpoint under the writer's fencing token. Its epoch identity is `(source_id, watermark_record_offset)`; the explicit end marker also has its own stable offset. Repeating the same epoch with the same canonical transaction payload returns its existing receipt without appending reports. Reusing that identity with a different payload is an error. Concurrent stale writers cannot commit over a newer cursor.

Before commit failure, visible reports and checkpoint remain unchanged. After a successful commit, restart resumes after that cursor with its saved state. A crash after the sink commits but before the caller receives the receipt is handled by the same idempotent epoch identity. Pure policy work may run again after a retry; report publication must not be duplicated. These properties depend on the proposed sink contract and must be tested with a reference sink before they are claimed.

Capacity checks occur before inserting a new buffered event, dedupe entry, unfinished group, or staged report. Exceeding a limit fails the epoch with a named `CAPACITY` error; no silent drop or automatic capacity increase is permitted. If watermarks stop advancing, the workflow may reach a limit and fail. It does not promise progress on every stream.

The bounds constrain active in-memory state, with bounded-size event fields. Checkpoint copies, task queues, and transaction staging must be included in memory accounting. The durable input log and published output history can grow. Do not describe the whole system as constant-storage or reuse the old workload's memory numbers.

## Illustrative machine-facing AIN sketch

The following 23-line data-flow sketch uses numeric operations and value references. It is an illustration of a possible encoding, with **no English operation keywords**. The surrounding tables carry its meaning. The node declarations describe a graph; they do not imply eagerly materializing an unbounded stream. Types, effect edges, error paths, checkpointing, and execution rules still require a complete grammar and implementation.

```text
@00(%90,%91,%92,%93,%94) {
  %00 = !010([600,120,1200,8,32,100000,200000,100000,100000]);
  %01 = !011(%91,%00);
  %02 = !012(%93,%01,%00);
  %03 = !013(%90,%02,%94);
  %04 = !101(%03,%00);
  %05 = !102(%04,%02,%00);
  %06 = !103(%05,%02,%00);
  %07 = !104(%06,%02,%00);
  %08 = !105(%07,1,%00);
  %09 = !106(%08,%02,%00);
  %10 = !107(%09,%02,%00);
  %11 = !108(%10,%02,%00);
  %12 = !109(%11,%92,%01,%94,%00);
  %13 = !110(%12,%00);
  %14 = !111(%13,%94,%00);
  %15 = !112(%14,%02,%01,%00);
  %16 = !113(%15,%93,%94,%00);
  %17 = !114(%16,%02,%00);
  %18 = !115(%17,%00);
  %19 = !116(%18,%94,%00);
  !001(%19);
}
```

The five arguments are the source, pinned manifest, private policy handle, transactional sink, and cancellation token respectively. Numeric operation IDs are local placeholders, not assigned AICC registry IDs or dedicated tokenizer tokens.

| Operation(s) | Human-readable semantic obligation |
|---|---|
| `010`, `011` | Validate configuration and pin interfaces, types, versions, and effect permissions |
| `012`, `013` | Restore the fenced checkpoint; open its replay cursor and cancellation-aware source |
| `101`, `102` | Validate raw records and offsets; check watermark and late-admission rules |
| `103`, `104` | Apply finite-horizon dedupe; normalize grouping fields |
| `105`, `106` | Apply severity filtering; buffer and order eligible events below the frontier |
| `107`, `108` | Form anchored groups; finalize the safe epoch prefix in deterministic order |
| `109` | Run bounded private scoring with the specified queue, authority, and cancellation checks |
| `110`, `111` | Restore output order; resolve cancellation or deterministic policy failures |
| `112`, `113` | Stage complete reports and state; atomically/idempotently commit after final checks |
| `114`, `115` | Advance the acknowledged cursor and retire expired state in the committed snapshot |
| `116`, `001` | Continue until an explicit end marker, or return the specified terminal outcome |

Retirement and the resulting snapshot must already be represented in the payload staged by `112`; the later acknowledgment cannot mutate durable state outside that transaction. The notation compresses a graph description, not the work of implementing its operators. A typed IR and conventional code must receive the same operators and documentation. Merely replacing their names with numbers is a control condition, not the native-language hypothesis proven.

## A concrete semantic trace, not an execution claim

Use one tenant/key, window 600, lateness 120, minimum severity one, and the limits above. Assume the example policy fixture returns a constant score/reason so only stream semantics are illustrated.

| Arrival | Record | Required consequence |
|---:|---|---|
| 1 | ID `A`, timestamp 100, severity 0 | Reserve `A`, then filter the event |
| 2 | ID `A`, timestamp 90, severity 3 | Duplicate: it cannot replace the first occurrence |
| 3 | ID `B`, timestamp 200, severity 2 | Admit to the event-time buffer |
| 4 | ID `C`, timestamp 150, severity 1 | Admit despite arrival after timestamp 200 |
| 5 | Watermark 900 | Frontier 780; process `C` then `B`. Finalize their shared group anchored at 150, with last 200, count two, severity sum three. Commit this epoch atomically |
| 6 | ID `D`, timestamp 779, severity 3 | Late: discard without reserving `D` |
| 7 | ID `D`, timestamp 780, severity 3 | Equality is admitted; the discarded row did not reserve `D` |
| 8 | Watermark 1,500 | Frontier 1,380; finalize `D`'s group. Evict `A`, whose first admitted timestamp plus horizon is 1,300, in the same checkpoint |
| 9 | ID `A`, timestamp 1,400, severity 2 | Admit as a new occurrence after horizon eviction |
| 10 | Explicit end marker | Drain and finalize `A`; commit the final checkpoint |

The trace was originally specified by inspection. It is now checked against explicit expected outputs and commits in the development suite's `test_documented_ten_record_trace_has_explicit_outputs_and_effects`. Separate cases exercise normalization, exact window boundaries, timestamp limits, checkpoint retry, cancellation, policy failures, and capacity exhaustion. See the [expected cases](../../experiments/ain_v0/EXPECTED_CASES.md) for implemented coverage and its limits.

## Required task variations and conformance evidence

- Change arrival order without changing the required event-time order; separately test equal timestamps using stable offsets.
- Change watermark/lateness rules and demonstrate both admitted and rejected boundary events.
- Change grouping semantics only when the task explicitly requests it; distinguish anchored windows from sliding windows.
- Inject malformed duplicates, low-severity first occurrences, repeated IDs after eviction, and late rows with reused IDs.
- Inject signed-result overflow, decreasing offsets/watermarks, an invalid restored checkpoint, and each capacity error.
- Force reverse policy completion, multiple policy failures, queue saturation, authority changes, and caller cancellation at each declared checkpoint.
- Crash before staging, before atomic commit, and after commit/before acknowledgment; replay must preserve exactly one visible publication per epoch.
- Ask an agent to optimize, repair, and hand off the implementation while preserving the same effect trace and limits.

The reference, conventional typed IR, symbolic-spelling control, and AIN candidate must use the same generated traces, private-policy fixtures, transaction harness, and resource limits. Differential output equality alone does not test recovery or authority behavior; compare the visible effect/state traces too. The [first development study](../../experiments/ain_v0/README.md) now records test definitions and local outcomes. Those cases are engineering evidence, not a completed final model evaluation.
