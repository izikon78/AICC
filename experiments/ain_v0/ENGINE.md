# AIN v0 workflow host and fixture interface

This standard-library implementation supplies the 23 capabilities frozen in
[INTEGRATION.md](INTEGRATION.md). The readable Python reference and the two VM
serializations own the source loop, admission decisions, buffering/drain loop,
and epoch sequencing. They share these capability bodies. Agreement among them
does not constitute three independent implementations of stream semantics.

The host implements the contract in
[COMPLEX_TASK.md](../../docs/ain/COMPLEX_TASK.md). It uses exact Python integers
for timestamp/window/horizon comparisons and rejects signed-result overflow.
It requires a Python runtime reporting Unicode `15.0.0`; its whitespace set is
explicit and does not use the runtime's broader `str.isspace()` definition.
Each event is fully validated before late/duplicate/filter classification.

## Running and inspecting

`Host(records, config=None, sink=None, **options)` takes a plain replayable list
of decoded record envelopes. `Config` accepts the fields/defaults in the frozen
ABI, including severity `minimum=1`. Boolean integers, unknown fields, nonplain
objects, invalid Unicode scalars, and malformed records are rejected. Inputs
are safely copied. A malformed future record raises its validation error when
admitted, allowing earlier valid epochs to remain committed. Copying rejects
custom accessors without invoking them; a deferred error retains no such object.

The source may grow by appending a suffix. A checkpoint stores a SHA-256 digest
of the exact source prefix through its committed cursor, plus a separate
configuration/policy/Unicode manifest. Restore checks that prefix and boundary,
permits additional records, and rejects a changed or truncated committed prefix.
Pass the complete replayable log, including the committed prefix, on restart.
Source exhaustion without an explicit end returns `INCOMPLETE`, without flushing
uncommitted work. A record appended after durable end is a validation error.

The result is canonical JSON data with `status`, `reports`, `counters`,
`checkpoint`, `trace`, and `error`. Status is `COMPLETE`, `INCOMPLETE`, `ERROR`,
or `CANCELLED`. Reports, counters, checkpoint and effect trace reflect committed
state only, even when a later epoch fails. An error has `code`, `message`, and
`details`. `Host.outcome(error)` constructs the same result after a
`WorkflowError`; unexpected host errors propagate through the runner.

Each report contains `source_id`, `group_id`, `tenant`, `device`, `kind`,
`message`, `first_timestamp`, `last_timestamp`, `first_offset`, `count`,
`severity_sum`, `score`, `reason`, and `policy_version`. Group identity is the
SHA-256 of canonical JSON `[source_id, first_offset]`. Canonical commit trace
entries contain `source_id`, `epoch_offset`, ordered `reports`, and the complete
checkpoint. Policy thread timing and completion order do not enter this trace.

## Trusted local fixture options

These are Python test hooks, not serializable instructions or capabilities
available to an untrusted program. No private-policy source, sandbox, secrecy,
or isolation property is demonstrated by these fixtures.

| Option | Interface |
|---|---|
| `source_id` | Nonempty exact Unicode identifier, at most 256 scalars; default `default` |
| `writer_token` | Positive integer from `sink.acquire(source_id)`; omitted means acquire on restore |
| `policy` | Callable `(group_copy, pinned_version, cancel_event)` returning `(score, reason)` or exactly `{"score": int, "reason": int}` |
| `policy_version` | Pinned nonempty string, default `fixture-v1`; a callable's optional `.version` must match before invocation and commit |
| `allowed_tenants` | Identifier collection, or `None` for unrestricted synthetic fixture tenancy |
| `allowed_reasons` | Nonempty integer allowlist; default `(0,1,2,3)` |
| `authority` | Callable `(stage, group_copy_or_None)` returning exactly `True`; stages are `policy` and `precommit` |
| `cancel` | `threading.Event`-like token with `is_set()`, or a callable returning whether cancellation was requested |
| `fault` | `before_commit`, `after_commit`, or callable `(stage, host)`; a callable may raise `WorkflowError` to inject failure |

The default synthetic policy returns
`(min(1000, severity_sum * 100 // count), 0)`. Policy exceptions or invalid
results become sanitized `POLICY` errors with the canonical `group_index`;
private exception text is not included. All epoch outcomes are inspected before
publication. The lowest finalized-group index failure wins regardless of
completion order. Cancellation observed during that epoch takes precedence.

Every scoring epoch creates at most `concurrency` worker threads and a bounded
`queue.Queue(maxsize=queue)` of waiting indices. Workers check cancellation and
authority before policy invocation. The producer blocks on the bounded queue;
the source loop cannot read another record until the scoring epoch commits or
fails. A caller cancellation sets the shared cooperative policy event, prevents
queued work from invoking policy after observing cancellation, and drains
running work. There is no preemption or real-time cancellation bound.

Operational telemetry is available separately as `host.scheduler`:
`peak_running`, `peak_waiting`, `started`, `finished`. It is excluded from
canonical workflow results because timing is not deterministic. The Python
fixture runs on threads; it provides real bounded asynchronous scheduling but
does not establish CPU parallel speedup under Python's GIL.

## Reference transactions and recovery

`Sink` is an in-memory transactional test double. It is not process-durable
storage. Its mutex and a single replacement store publish reports/checkpoint/
receipt/trace together. The restart tests reuse the same sink object to model
durable state. A future storage adapter needs its own atomicity and crash tests.

`sink.acquire(source_id)` advances a fencing token. A stale token cannot publish.
`sink.commit(source_id, epoch_offset, {"reports": ..., "checkpoint": ...}, token)`
returns a receipt. Same epoch plus same canonical payload returns the existing
receipt; a changed payload gives `EPOCH_CONFLICT`. Existing complete sources and
backward cursors cannot advance. `sink.snapshot()` returns a consistent
inspection view. `reports`, `checkpoints`, `receipts`, `trace`, and `fences` are
also exposed for trusted quiescent inspection and corruption test fixtures.

`before_commit` raises `CRASH_BEFORE_COMMIT` before publication. `after_commit`
raises `LOST_ACK` after atomic publication but before the caller receives the
receipt. Restart verifies its checkpoint and resumes after its cursor, so a
lost acknowledgment cannot append duplicate reports. Sink idempotence separately
handles retries of the identical epoch payload under a current fencing token.
Integrity hashes detect accidental corruption; they are not authentication.

Named failures include `VALIDATION`, `CAPACITY` (with `resource`), `OVERFLOW`,
`POLICY`, `POLICY_VERSION`, `AUTHORITY`, `CHECKPOINT`, `FENCED`, `EPOCH_CONFLICT`,
`CANCELLED`, `CRASH_BEFORE_COMMIT`, `LOST_ACK`, and dependency mismatch
`DEPENDENCY`. Configuration/source restore mismatch gives `CHECKPOINT`; policy
manifest mismatch gives `POLICY_VERSION`.

## Storage and measurement boundaries

Pending events, retained IDs, unfinished groups, and staged epoch reports obey
their explicit capacity limits before insertion. Queue entries, worker copies,
policy outcomes, the checkpoint snapshot, and transaction copies also consume
memory. The host retains a safe copy of the replayable input list. This test
sink retains output/checkpoint trace history and makes transaction copies.
Memory therefore includes bounded active state and growing input/output history;
the complete system is not constant-storage. Prefix verification and hashing
are included work; no production checkpoint I/O or network latency is modeled.

No paid model calls, model training, special tokenizer, billing-token savings,
energy savings, or independent provider reproduction are established here.
