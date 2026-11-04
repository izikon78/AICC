"""Arm B: public commons. Same contract text as Arm A; each capability is a validated binding from the host.
Near-miss candidates (candidate.*) are never bound; see SELECTION_DECISIONS_BEFORE_TESTS.md."""
from benchmark.host.registry import Runtime

_rt = Runtime()
canonical_json = _rt.bind("pub.canonical_json@1")
chunks = _rt.bind("pub.chunks@1")
diff_by_id = _rt.bind("pub.diff_by_id@1")
digest_json = _rt.bind("pub.digest_json@1")
filter_by_severity = _rt.bind("pub.filter_by_severity@1")
group_by_window = _rt.bind("pub.group_by_window@1")
gzip_deterministic = _rt.bind("pub.gzip_deterministic@1")
hash_chunks = _rt.bind("pub.hash_chunks@1")
make_query = _rt.bind("pub.make_query@1")
merge_patch = _rt.bind("pub.merge_patch@1")
parse_csv_table = _rt.bind("pub.parse_csv_table@1")
parse_money = _rt.bind("pub.parse_money@1")
png_dimensions = _rt.bind("pub.png_dimensions@1")
redact_paths = _rt.bind("pub.redact_paths@1")
retry_delays = _rt.bind("pub.retry_delays@1")
safe_path = _rt.bind("pub.safe_path@1")
stable_unique = _rt.bind("pub.stable_unique@1")
toposort = _rt.bind("pub.toposort@1")

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
