# Development log

- 2026-11-05: Began the first AIN v0 implementation from the published AIN plan.
  Split host semantics, language implementation and conformance review across
  collaboration agents. Root authored matched workflow control flow and this
  protocol before any measured run. There was no pre-existing AIN runtime.
- Integration choice: mutable typed registers, void calls omit `dest`, and the
  numeric codec preserves control flow while replacing labels/registers/operation
  references with integers. Catalog metadata is pinned; this is not executable
  implementation authentication or sandboxing.
- Development checks found eager validation of future malformed records, a
  whole-input digest preventing append-only restart, a negative-offset replay
  shortcut, and ambiguity when an appended suffix reused a committed offset.
  Fixed admission-time validation, committed-prefix hashing and replay boundary
  selection. These were development failures before the recorded measurements,
  not exclusions from a successful benchmark run.
- A separate driver review required preserving timeout/invalid-output failures,
  hashing the export/docs, and specifying repeated preflight validation and memory
  instrumentation. Applied those changes before source freeze.
- Measurement attempt `development-001` aborted: four workers reached final
  reporting but ctypes failed to pass a 64-bit Windows process handle to the
  memory-counter API. Interrupted worker 5; did not start workers 6–27. Retained
  raw errors and original hashes. Declared API argument/return types explicitly,
  verified a 50-event worker, and began a distinct `development-002` result set.
- Corrected run `development-002`: 27/27 workers completed, all three per-workload
  canonical hashes match, source manifest unchanged, no completed-run exclusions.
- Pilot preflight caught a Windows-newline bookkeeping mismatch: initial artifact
  digests had been calculated before text-mode newline conversion. Corrected
  hashing to use actual file bytes before any agent dispatch; preserved the
  rejected preflight report and prior protocol revisions. All six initial
  negative controls then failed their assigned task as intended.
- Six fresh-context one-submission editing cells completed. Three boundary repairs
  and three requested normalization reorderings passed the frozen judge without
  feedback/retry or human repair. Returned diffs were inspected; no unrelated
  behavior or source changes were present. All protocol/source hashes verified
  around each judgment. This was not a blinded provider comparison.
