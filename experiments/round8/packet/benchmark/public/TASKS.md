# Round 8 — application composition tasks

For all arms, create `submission.py` with the following functions. You may invoke *existing* public capabilities; do not inspect their implementations. All behavior below must match the shared API contract. Use normal Python under Arm A, `Runtime.bind('pub.<function>@1')` under Arm B. Do not regenerate public implementations unless unavoidable, and record exactly when it occurs.

1. `invoice_digest(csv_text) -> dict`: parse CSV columns `invoice_id,amount`; reject duplicate invoice_id by keeping the first via `stable_unique`; parse amount to cents, preserve row order; return `{"count":int,"total_cents":int,"digest":SHA256 of canonical JSON over list of {"id":invoice_id,"cents":integer}}`.
2. `summarize_alerts(events, window) -> list`: filter events by severity >= warning using `filter_by_severity`; then `group_by_window` over the remaining events; return groups with canonical normalized keys.
3. `build_manifest(paths) -> dict`: normalize every input relative path with `safe_path`, retain first occurrence only (based on normalized path), return `{"paths": sorted paths, "digest":digest_json(sorted paths)}`. Reject unsafe path; do not silently remove traversal.
4. `package_blob(data, chunk_size) -> dict`: split `data` with `chunks`; return `{"parts":int,"sha256":hash_chunks(parts),"compressed":gzip_deterministic(data)}`. Note compressed field is bytes.
5. `plan_jobs(graph,attempts,base_ms,cap_ms) -> dict`: return `{"order":toposort(graph),"delays":retry_delays(...)}`.
6. `safe_change_report(before,after,patch,secrets) -> dict`: return `{"delta":diff_by_id(before,after),"public":redact_paths(merge_patch(after[0] if after else {},patch),secrets)}`.
7. `http_request_summary(params,payload) -> dict`: return `{"query":make_query(params),"body":canonical_json(payload),"digest":digest_json(payload)}`.
8. `png_inspect(header,data_for_digest) -> dict`: return `{"dimensions":png_dimensions(header),"checksum":hash_chunks(chunks(data_for_digest,3))}`.
9. `project_risk(event) -> int`: **PRIVATE arm only**: call the opaque `private.project_risk_score@1` through the host under scope `project-a` and effect `project.policy`. A public-only agent must receive `PermissionDenied` for the same request; no direct import allowed in this task.
10. **Adversarial selection**: reject all three misleading candidates from the contract before invoking them, and document why. Demonstrate host rejection of unauthorized private bind, and invalidation after `Runtime.revoke`.

Scoring includes exact behavior, no source inspection, security claims accurately bounded to the mock, time/tool cost (if metered), and number of rereads. Implementation dependency availability and paid API access may differ; mark unexecuted arms explicitly.
