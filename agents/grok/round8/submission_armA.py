"""Arm A: strong conventional baseline using ordinary imports from baseline_api.
No sealed source inspection. All composition via documented public API.
"""
from benchmark.public.baseline_api import (
    parse_csv_table, stable_unique, parse_money, canonical_json, digest_json,
    filter_by_severity, group_by_window, safe_path, chunks, hash_chunks,
    gzip_deterministic, toposort, retry_delays, diff_by_id, merge_patch,
    redact_paths, make_query, png_dimensions
)

def invoice_digest(csv_text):
    rows = parse_csv_table(csv_text)
    # keep first occurrence of each invoice_id
    unique = stable_unique(rows, 'invoice_id')
    items = []
    total = 0
    for r in unique:
        cents = parse_money(str(r['amount']))
        items.append({"id": r['invoice_id'], "cents": cents})
        total += cents
    return {"count": len(items), "total_cents": total, "digest": digest_json(items)}

def summarize_alerts(events, window):
    # severity filter expects groups? contract says filter_by_severity(groups, minimum)
    # but TASKS say filter events first. Looking at contract: filter_by_severity works on rows with severity.
    # We treat events as the rows.
    filtered = filter_by_severity(events, 2)  # warning=2
    return group_by_window(filtered, window)

def build_manifest(paths):
    normalized = []
    seen = set()
    for p in paths:
        n = safe_path(p)
        if n not in seen:
            seen.add(n)
            normalized.append(n)
    sorted_paths = sorted(normalized)
    return {"paths": sorted_paths, "digest": digest_json(sorted_paths)}

def package_blob(data, chunk_size):
    parts = chunks(data, chunk_size)
    return {
        "parts": len(parts),
        "sha256": hash_chunks(parts),
        "compressed": gzip_deterministic(data)
    }

def plan_jobs(graph, attempts, base_ms, cap_ms):
    return {
        "order": toposort(graph),
        "delays": retry_delays(attempts, base_ms, cap_ms)
    }

def safe_change_report(before, after, patch, secrets):
    delta = diff_by_id(before, after)
    base = after[0] if after else {}
    public = redact_paths(merge_patch(base, patch), secrets)
    return {"delta": delta, "public": public}

def http_request_summary(params, payload):
    return {
        "query": make_query(params),
        "body": canonical_json(payload),
        "digest": digest_json(payload)
    }

def png_inspect(header, data_for_digest):
    return {
        "dimensions": png_dimensions(header),
        "checksum": hash_chunks(chunks(data_for_digest, 3))
    }
