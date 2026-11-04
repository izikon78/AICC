"""Arm B: commons registry binds. Same contracts as A. Reject near-misses from cards alone.
No sealed source inspection.
"""
from benchmark.host.registry import Runtime, PermissionDenied, InvalidBinding

rt = Runtime()

# Reject near-misses from API_CONTRACTS.md description alone:
# candidate.parse_money_bankers@1 — HALF_EVEN instead of HALF_UP (wrong for 1.005)
# candidate.safe_path_loose@1 — rewrites traversal instead of rejecting
# candidate.group_by_eventid@1 — groups by event_id not normalized behavior+window

_parse_csv = rt.bind('pub.parse_csv_table@1')
_stable_unique = rt.bind('pub.stable_unique@1')
_parse_money = rt.bind('pub.parse_money@1')
_canonical_json = rt.bind('pub.canonical_json@1')
_digest_json = rt.bind('pub.digest_json@1')
_filter_sev = rt.bind('pub.filter_by_severity@1')
_group_win = rt.bind('pub.group_by_window@1')
_safe_path = rt.bind('pub.safe_path@1')
_chunks = rt.bind('pub.chunks@1')
_hash_chunks = rt.bind('pub.hash_chunks@1')
_gzip = rt.bind('pub.gzip_deterministic@1')
_toposort = rt.bind('pub.toposort@1')
_retry = rt.bind('pub.retry_delays@1')
_diff = rt.bind('pub.diff_by_id@1')
_merge = rt.bind('pub.merge_patch@1')
_redact = rt.bind('pub.redact_paths@1')
_make_query = rt.bind('pub.make_query@1')
_png_dim = rt.bind('pub.png_dimensions@1')

def invoice_digest(csv_text):
    rows = _parse_csv(csv_text)
    unique = _stable_unique(rows, 'invoice_id')
    items = []
    total = 0
    for r in unique:
        cents = _parse_money(str(r['amount']))
        items.append({"id": r['invoice_id'], "cents": cents})
        total += cents
    return {"count": len(items), "total_cents": total, "digest": _digest_json(items)}

def summarize_alerts(events, window):
    filtered = _filter_sev(events, 2)
    return _group_win(filtered, window)

def build_manifest(paths):
    normalized = []
    seen = set()
    for p in paths:
        n = _safe_path(p)
        if n not in seen:
            seen.add(n)
            normalized.append(n)
    sorted_paths = sorted(normalized)
    return {"paths": sorted_paths, "digest": _digest_json(sorted_paths)}

def package_blob(data, chunk_size):
    parts = _chunks(data, chunk_size)
    return {
        "parts": len(parts),
        "sha256": _hash_chunks(parts),
        "compressed": _gzip(data)
    }

def plan_jobs(graph, attempts, base_ms, cap_ms):
    return {
        "order": _toposort(graph),
        "delays": _retry(attempts, base_ms, cap_ms)
    }

def safe_change_report(before, after, patch, secrets):
    delta = _diff(before, after)
    base = after[0] if after else {}
    public = _redact(_merge(base, patch), secrets)
    return {"delta": delta, "public": public}

def http_request_summary(params, payload):
    return {
        "query": _make_query(params),
        "body": _canonical_json(payload),
        "digest": _digest_json(payload)
    }

def png_inspect(header, data_for_digest):
    return {
        "dimensions": _png_dim(header),
        "checksum": _hash_chunks(_chunks(data_for_digest, 3))
    }
