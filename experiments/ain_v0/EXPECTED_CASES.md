# AIN v0 expected workflow cases

These are same-session development conformance cases for the proposed transactional workflow. They are public and were written while the implementation was being developed. They are not a hidden benchmark, independently authored oracle, model-training result, or production security certification. Passing the three serializations through a shared host cannot by itself establish that the host is correct.

The tests therefore assert hand-written expected groups, counts, committed offsets, visible publication and rollback, and rejection conditions. The Python, readable IR and numeric AIN paths run the same inputs and must meet those expectations. A few shared-primitive boundary tests intentionally inspect the host directly; their scope is stated below. Recorded results must state the implementation revision and actual test outcome rather than treating this inventory as a passing record.

## Golden ten-record trace

The [task contract](../../docs/ain/COMPLEX_TASK.md) specifies arrivals A-low, A-duplicate, B, C, watermark 900, D-late, D-at-frontier, watermark 1500, A-after-eviction, end. The expected reports are:

| First timestamp | Last timestamp | First source offset | Count | Severity sum | Committing offset |
|---:|---:|---:|---:|---:|---:|
| 150 | 200 | 4 | 2 | 3 | 5 |
| 780 | 780 | 7 | 1 | 3 | 8 |
| 1400 | 1400 | 9 | 1 | 2 | 10 |

All have tenant t, normalized device pump, kind alert and message m. The local constant scoring fixture returns score 77/reason 2 under policy version fixture-v1; these numbers are test fixtures, not learned or private production results. Final counters are late 1, duplicate 1, filtered 1, accepted 4. Final cursor is 10 and complete is true. There are three visible atomic commits, each publishing one report.

## Adversarial coverage

| Area | Required observation |
|---|---|
| EOF and end | Empty end commits; plain input exhaustion does not drain, finalize, or fabricate a terminal checkpoint |
| First occurrence | An earlier input with low severity wins even if a duplicate has an earlier timestamp and higher severity |
| Identifier domains | Tenant and event ID remain exact, including case and whitespace |
| Unicode | NFKC/casefold apply to tags; messages preserve case and compatibility characters; the contract's explicit whitespace set is collapsed |
| Extra Python whitespace | U+001C through U+001F, BOM and zero-width space remain significant instead of adopting Python split semantics |
| Grouping | Windows are anchored and strict; timestamp ties use first source offset rather than key order |
| Frontier | Equality waits in the buffer but is admissible; late discarded IDs do not reserve identity |
| Finite retention | Eviction occurs at the exact first-timestamp-plus-horizon boundary; later duplicates cannot rewrite that timestamp |
| Integer limits | End acts as infinity for maximum signed timestamps; grouping arithmetic does not wrap; category counters fail rather than wrap at signed maximum |
| Strict validation | Invalid duplicate, filtered, or late rows are still rejected; exact record shapes, inclusive Unicode-scalar field sizes, primitive types and surrogate rejection are checked; a malformed future row cannot prevent an earlier epoch from committing |
| Configuration | Boolean/nonpositive limits, invalid minimum severity, and horizon smaller than window are rejected |
| Monotonic input | Offsets strictly increase; watermarks may repeat but may not decrease; new events after durable completion are rejected |
| Capacities | Dedupe entries, buffered events, open groups and staged reports each fail with a named CAPACITY error and no uncommitted publication |
| Aggregate overflow | Trusted boundary fixtures place an already-created group at signed-result maximum, then require OVERFLOW on a further count/severity addition; this does not pretend to execute 2**63 events |
| Policy outputs | Score/reason types, ranges and allowlist are enforced; unexpected private fields and exception messages do not leak into canonical reports |
| Completion order | A deterministic synchronization fixture completes the second policy call before the first while publication stays in group order |
| Error order | Multiple failed policies select the lowest finalized-group index, independent of completion order |
| Scheduler | Running and waiting telemetry remain within the declared bounds; this is tested separately from canonical output |
| Authority | Every private invocation and precommit must check host authority; tenant access and policy version are pinned |
| Cancellation | Before admission, during policy work and at precommit; observed cancellation takes precedence over policy failure and preserves earlier durable epochs |
| Atomic rollback | Failure before commit leaves no report/checkpoint; replay commits once |
| Lost acknowledgment | A committed epoch is retained after LOST_ACK; replay resumes without duplicate publication |
| Sink identity | Same epoch/payload is idempotent; a changed payload conflicts; stale fencing tokens cannot commit |
| Restored state | Integrity tampering, malformed restored state and changed configuration are rejected; append-only input can resume while modified/truncated committed prefixes and old offsets in the suffix are rejected; a checksum is not an authentication boundary |
| Stable group identity | Replaying the same source/first offset preserves identity; changing source identity changes it |

## Run and interpret

From experiments/ain_v0 with the bundled or declared Python environment:

```shell
python -m unittest discover -s tests -v
```

Retain stdout, stderr, exit status, source revision and failures. The fixture hooks are local trusted test functions. Queue and cancellation observations do not establish isolation, real-time interruption, or a secure private-code boundary. Representation comparisons use the same shared catalog and workflow primitives, so a later language-effect study needs fresh authoring/edit tasks and the separate controlled research protocol.
