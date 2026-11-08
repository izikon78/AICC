"""Arm A: ordinary package reuse. Written from benchmark/public/API_CONTRACTS.md and TASKS.md only.
No sealed source opened. One black-box probe: filter_by_severity's 'minimum' must be an int 0..3 (contract silent on type)."""
from benchmark.public.baseline_api import (
    canonical_json, chunks, diff_by_id, digest_json, filter_by_severity, group_by_window, gzip_deterministic,
    hash_chunks, make_query, merge_patch, parse_csv_table, parse_money, png_dimensions, redact_paths,
    retry_delays, safe_path, stable_unique, toposort,
)

WARNING = 2  # contract scale: debug=0, info=1, warning=2, critical=3


def invoice_digest(csv_text):
    rows = stable_unique(parse_csv_table(csv_text), "invoice_id")
    items = [{"id": r["invoice_id"], "cents": parse_money(r["amount"])} for r in rows]
    return {"count": len(items), "total_cents": sum(i["cents"] for i in items), "digest": digest_json(items)}


def summarize_alerts(events, window):
    return group_by_window(filter_by_severity(events, WARNING), window)


def build_manifest(paths):
    seen, out = set(), []
    for p in paths:
        q = safe_path(p)  # raises on unsafe input; traversal is never silently removed
        if q not in seen:
            seen.add(q); out.append(q)
    out = sorted(out)
    return {"paths": out, "digest": digest_json(out)}


def package_blob(data, chunk_size):
    parts = chunks(data, chunk_size)
    return {"parts": len(parts), "sha256": hash_chunks(parts), "compressed": gzip_deterministic(data)}


def plan_jobs(graph, attempts, base_ms, cap_ms):
    return {"order": toposort(graph), "delays": retry_delays(attempts, base_ms, cap_ms)}


def safe_change_report(before, after, patch, secrets):
    return {"delta": diff_by_id(before, after), "public": redact_paths(merge_patch(after[0] if after else {}, patch), secrets)}


def http_request_summary(params, payload):
    return {"query": make_query(params), "body": canonical_json(payload), "digest": digest_json(payload)}


def png_inspect(header, data_for_digest):
    return {"dimensions": png_dimensions(header), "checksum": hash_chunks(chunks(data_for_digest, 3))}
