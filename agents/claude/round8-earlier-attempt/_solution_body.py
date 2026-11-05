# Shared task logic for Round 8. The two arms differ ONLY in how the capabilities are obtained:
#   Arm A: from benchmark.public.baseline_api import <name>
#   Arm B: Runtime().bind('pub.<name>@1')
# Everything below was written from benchmark/public/{API_CONTRACTS.md,TASKS.md} alone.
# benchmark/sealed/* was never opened.

def build_solution(cap):
    """cap(name) -> callable for the public capability `name`."""
    normalize_tag = cap('normalize_tag'); normalize_whitespace = cap('normalize_whitespace')
    parse_money = cap('parse_money'); parse_csv_table = cap('parse_csv_table')
    canonical_json = cap('canonical_json'); digest_json = cap('digest_json')
    stable_unique = cap('stable_unique'); group_by_window = cap('group_by_window')
    filter_by_severity = cap('filter_by_severity'); safe_path = cap('safe_path')
    chunks = cap('chunks'); hash_chunks = cap('hash_chunks')
    gzip_deterministic = cap('gzip_deterministic'); toposort = cap('toposort')
    diff_by_id = cap('diff_by_id'); merge_patch = cap('merge_patch')
    redact_paths = cap('redact_paths'); make_query = cap('make_query')
    png_dimensions = cap('png_dimensions'); retry_delays = cap('retry_delays')

    def invoice_digest(csv_text):
        rows = parse_csv_table(csv_text)
        unique = stable_unique(rows, 'invoice_id')          # keep first per invoice_id, preserve order
        items = [{'id': r['invoice_id'], 'cents': parse_money(r['amount'])} for r in unique]
        return {'count': len(items), 'total_cents': sum(it['cents'] for it in items),
                'digest': digest_json(items)}

    def summarize_alerts(events, window):
        kept = filter_by_severity(events, 2)                 # severity >= warning; scale debug0/info1/warning2/critical3
        return group_by_window(kept, window)

    def build_manifest(paths):
        seen, normed = set(), []
        for p in paths:
            sp = safe_path(p)                               # raises on unsafe; no silent rewrite
            if sp not in seen:
                seen.add(sp); normed.append(sp)
        ordered = sorted(normed)
        return {'paths': ordered, 'digest': digest_json(ordered)}

    def package_blob(data, chunk_size):
        parts = chunks(data, chunk_size)
        return {'parts': len(parts), 'sha256': hash_chunks(parts),
                'compressed': gzip_deterministic(data)}

    def plan_jobs(graph, attempts, base_ms, cap_ms):
        return {'order': toposort(graph), 'delays': retry_delays(attempts, base_ms, cap_ms)}

    def safe_change_report(before, after, patch, secrets):
        patched = merge_patch(after[0] if after else {}, patch)
        return {'delta': diff_by_id(before, after), 'public': redact_paths(patched, secrets)}

    def http_request_summary(params, payload):
        return {'query': make_query(params), 'body': canonical_json(payload),
                'digest': digest_json(payload)}

    def png_inspect(header, data_for_digest):
        return {'dimensions': png_dimensions(header),
                'checksum': hash_chunks(chunks(data_for_digest, 3))}

    return dict(invoice_digest=invoice_digest, summarize_alerts=summarize_alerts,
                build_manifest=build_manifest, package_blob=package_blob, plan_jobs=plan_jobs,
                safe_change_report=safe_change_report, http_request_summary=http_request_summary,
                png_inspect=png_inspect)
