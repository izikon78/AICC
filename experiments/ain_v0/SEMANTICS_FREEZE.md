# Proposed semantics freeze v0.1 for the AIN streaming task (plan deliverable 1)

**Status:** proposed by Claude Opus 5.5 on 2026-11-05 while implementing `docs/ain/COMPLEX_TASK.md`. **Requires the owner's review before it is treated as frozen.** Each decision resolves a point the task contract leaves open, and each is implemented identically in every form through the shared primitives (`ain_v0/primitives.py`). Contract text that already decides a point is not repeated here.

## Decisions

| ID | Topic | Decision |
|---|---|---|
| D-01 | Configuration | Nine values in this order: window, lateness, horizon, concurrency, queue, buffered_events, dedupe_entries, open_groups, epoch_reports. All are at most 2^63−1 and positive, except lateness ≥ 0; horizon ≥ window. Violations raise `INVALID_CONFIG` before any sink access |
| D-02 | Integers | "Integer" means the exact `int` type. `bool` and subclasses are rejected everywhere: configuration, offsets, timestamps, watermarks, severity and policy outputs |
| D-03 | Minimum severity | Part of the configuration identity stored in checkpoints, even though the sketch writes it as a literal of operation 105 (see D-29) |
| D-04 | Record envelope | A mapping with `type` ∈ {event, watermark, end} and `offset`. Events have exactly the contract's seven fields plus the envelope; watermarks add `watermark`; end markers add nothing. Extra or missing keys raise `INVALID_RECORD` |
| D-05 | Text | The contract's exact whitespace set, **not** Python's (`str.split` would also treat U+001C–U+001F as whitespace). Device and kind are NFKC, then casefold, then collapse; message is collapse only. Unicode 15.0.0 is pinned; any other version raises `UNICODE_VERSION` |
| D-06 | Error priority within a record | Envelope or offset type → `OFFSET_ORDER` → `AFTER_END` → field `INVALID_RECORD` → `WATERMARK_ORDER` → late → duplicate → `CAPACITY` (dedupe) → filtered → `CAPACITY` (buffer) |
| D-07 | String limits | Counted in Unicode scalar values. Tenant and event_id 1–128; device and kind 0–256 (empty allowed); message 0–4,096. Any surrogate code point is rejected |
| D-08 | Ranges | Offsets, timestamps and watermark values 0 to 2^63−1 |
| D-09 | Offsets | Equal offsets are `OFFSET_ORDER` (strictly increasing) |
| D-10 | Equal watermarks | Allowed. Every valid watermark creates and commits an epoch, even one with zero reports |
| D-11 | Manifest | Identity = SHA-256 (16 hex characters) of the canonical manifest JSON. The policy version is pinned. The manifest must grant the program's static effect set, otherwise `EFFECT_DENIED` |
| D-12 | Restore | The cursor is the offset of the last committed watermark or end record; replay resumes at the following source record. A checkpoint for another manifest or configuration, or a cursor absent from the source, raises `INVALID_CHECKPOINT` |
| D-13 | Dedupe | Identity is the exact (tenant, event_id) pair, with collision-free encoding. The first admitted timestamp is kept. Eviction when C ≥ first + horizon is computed at the watermark and **staged in that epoch's payload** |
| D-14 | End marker | Logical +∞ frontier: drains all buffered events, finalises all groups, evicts all dedupe entries, leaves the watermark value unchanged, sets `complete = true` |
| D-15 | Groups | One newest group per key. Finalised groups are removed, so a key whose newest group was finalised opens a new group |
| D-16 | Overflow | Count and severity sum are checked before each update; `OVERFLOW` carries the event's offset |
| D-17 | Policy executor | At most `concurrency` calls running and `queue` waiting; submission blocks and never drops. Simulated deterministically with a pluggable completion order. Calls are pure, so results may be computed at start |
| D-18 | Policy errors | The epoch's remaining calls still run (permitted by the contract), so the lowest failing index does not depend on completion order |
| D-19 | Precedence within an epoch | `CANCELLED` > `AUTHORITY` > `POLICY_ERROR` (lowest finalised index). A failure at a policy start stops new starts and drains the running calls |
| D-20 | Check order | At each check point the cancellation token is checked first, then authority |
| D-21 | Policy output | `(score: int 0–1000, reason ∈ {0, 1, 2, 3, 10, 20, 30})`. Anything else, or a raised exception, is `POLICY_ERROR` for that group. The allowlist is an example fixture |
| D-22 | Sink | Fence tokens increase with each acquisition. A token other than the current fence, or a cursor regression, raises `FENCED`. An existing epoch identity with an identical canonical payload returns the existing receipt without appending; a different payload raises `CONFLICT` |
| D-23 | Publication | Reports and checkpoint appear together in one commit. Nothing from a failed or cancelled epoch is visible |
| D-24 | Crash | Not an outcome. A new writer with a new fence restores the latest checkpoint and replays |
| D-25 | Counters | Cumulative, stored in the checkpoint, assigned at arrival. Records after the last committed watermark count towards the next epoch |
| D-26 | Input exhaustion | Ending without an explicit end marker gives `SUSPENDED`; uncommitted state is discarded and replayed on restart. Restart from a complete checkpoint gives `COMPLETED` with no further records, or `AFTER_END` if one appears |
| D-27 | Observation | Conformance compares an implementation-neutral checkpoint view, visible reports, the sink log, the cancel/authority check log, and the policy start/completion trace |
| D-28 | Report | `group_id = "<source_id>:<first_offset>"`, plus tenant, normalised device/kind/message, first, last, first_offset, count, severity_sum, score, reason and policy_version |
| D-29 | Lowering | The single `event.filter` literal is hoisted into configuration before execution; exactly one filter operation is required |
| D-30 | Sketch typing gap | Operations 105 (filtered counter) and 115 (state replacement) mutate workflow state **without a State argument** in the sketch. v0 reaches state through the lowering context, so their types do not show the effect. A later core should make state effects explicit |
| D-31 | Capacity | Checked before insertion. `epoch_reports` is checked on the finalised count and carries the watermark's offset |
| D-32 | Authority points | Checked only before each policy start and before commit, as the contract states; never at admission |

## Open questions for the owner

1. **D-03/D-29:** keep the minimum severity as an operation literal (hoisted), or move it into the configuration list?
2. **D-17:** v0 simulates concurrency deterministically. Real asynchronous execution needs its own conformance layer; equal outputs do not test races.
3. **D-25:** cumulative or per-epoch counters in published checkpoints?
4. **AIN parameter typing:** AIN types parameters by position, so a mistyped parameter cannot be written at all; IR can write one and gets `E_PARAMS`. Is positional typing intended?
5. **D-30:** should the core require an explicit State argument, or an effect annotation, for every state-mutating operation?
6. **Real-time and fairness:** the contract claims no real-time cancellation bound; v0 measures none.
