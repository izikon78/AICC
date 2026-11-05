# Synthetic processing workflow: kernel contract v1

These kernels are an engineering workload for studying AICC composition and agent-designed optimization. They are not a new event-processing standard, a hidden benchmark, or a production security boundary.

## API and data

`process(events, window, minimum=0, variant="cached") -> list[dict]` dispatches through `VARIANTS`. Direct functions `process_reference`, `process_cached`, `process_partitioned`, and `process_ordered` have `(events, window, minimum=0)` signatures. All take a single-pass iterable of event mappings and do not mutate their input.

Each mapping requires these fields; extra fields are ignored:

| Field | Type and meaning |
|---|---|
| `event_id` | Python string; exact identity for deduplication, without trimming/case folding |
| `device`, `kind` | Python strings; normalized grouping tags |
| `message` | Python string; case-preserving message text |
| `timestamp` | Python integer, excluding booleans; negative timestamps are allowed |
| `severity` | Python integer 0 through 3, excluding booleans |

`window` must be a positive Python integer excluding booleans. `minimum` must be a Python integer from 0 through 3 excluding booleans. Invalid parameters raise `ValueError` before input is consumed, checking window first.

## Observable behavior

1. Validate every raw event before deduplication or severity filtering. A malformed duplicate or filtered row is still an error. Non-mapping rows, missing fields, wrong string/integer types, or boolean timestamps/severities raise `TypeError`. Out-of-range integer severity raises `ValueError`. Input is processed in iteration order and the first encountered error wins.
2. Assign each raw event a zero-based input ordinal. Deduplicate by exact `event_id`, keeping its first raw-input occurrence, even if a later duplicate has an earlier timestamp or greater severity.
3. Remove retained events whose severity is less than `minimum`. Deduplication therefore precedes filtering: a low-severity first occurrence suppresses a high-severity later duplicate.
4. Define `collapse(s) = " ".join(s.split())`, using Python's Unicode whitespace definition. Normalize device/kind as `collapse(NFKC(s).casefold())`. Normalize message with `collapse(s)` only; preserve message case and non-whitespace characters. The grouping key is the resulting `(device, kind, message)` tuple.
5. Process surviving events in ascending `(timestamp, raw input ordinal)` order.
6. Maintain the most recently opened group for each key. An event belongs to it only when `event.timestamp - group.first < window`; the window is anchored to the first event, not extended from the last event. Otherwise create a new group.
7. Output groups in creation order, equivalent to ascending `(first, first_ordinal)`. Each group has exactly `device`, `kind`, `message`, `first`, `last`, `count`, `severity_sum`, and `first_ordinal`. `last` is its last timestamp, `count` counts retained events, and `severity_sum` sums their severities. Empty input returns an empty list.

Dictionary key order is consistent across supplied variants but is not a separate semantic condition. Python Unicode data/version is an environmental dependency; record it with benchmark results. Matching supplied tests does not prove equivalence for every input/environment.

## Four alternative execution flows

- **reference:** normalize deduplicated events, globally sort, filter, and group. This is the transparent reference and is not the only conventional baseline.
- **cached:** filter before normalization/sort and use bounded per-job normalization caches (8,192 tag strings and 4,096 messages).
- **partitioned:** filter/normalize, partition by normalized key, sort within keys, group, then sort group creation order. This trades one global event sort for smaller sorts plus partitioning/output ordering costs.
- **ordered:** check that **all valid raw input timestamps** are nondecreasing, including duplicates and filtered rows, and group in one pass without a global event sort. A decreasing timestamp raises `OrderPreconditionError`, a `ValueError` subclass. A job violating this precondition must not be routed here. The check follows row validation and can therefore raise before a later malformed row would be encountered.

Every conventional and AICC experimental arm must be allowed to use every applicable variant. A speedup from caching, filter pushdown, partitioning, or avoiding a sort is an algorithm/flow optimization, not evidence that registry indirection uniquely improves performance.

These are AI-agent-designed combinations of established techniques; they are not claimed to be previously unknown to humans or autonomously discovered. A learned routing policy may select among them, but that does not by itself constitute learning a new algorithm.

## Resource and safety boundaries

The cached variants bound their normalization caches and ordered execution avoids materializing a sorted event list. Exact deduplication still requires memory proportional to the unique event IDs; returned groups require memory proportional to the group count. This is not a constant-memory claim. The partitioned variant additionally retains per-key event rows.

The kernels do not call external services or perform file/network operations. A custom user-defined iterable/mapping can execute its own code; this module is not a sandbox for adversarial Python objects. Tests and processing jobs should use synthetic ordinary mappings. Authorization and AICC binding invalidation are the responsibility of an external host/runtime with explicitly stated assurance limits.
