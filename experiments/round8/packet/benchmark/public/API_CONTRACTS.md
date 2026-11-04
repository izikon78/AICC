# Common API contracts — same authoritative behavior for Arm A and Arm B

**These descriptions are a starter specification, not formally proved complete.** Both arms must receive the same text below; do not create a straw-man baseline with less information. Calls below are ordinary Python functions (A) or `pub.<name>@1` binds (B). All functions described as pure; direct real-world effects (network, DB, filesystem) are intentionally *not* executed by this benchmark.

| Function `name(args)` | Observable contract and caveats |
|---|---|
| `normalize_tag(text)` | Unicode NFKC, casefold, split on Python Unicode whitespace, join with a single ASCII space, reject empty string; error on non-str |
| `normalize_whitespace(text)` | Collapse Python Unicode whitespace with split/join, preserving letter case; non-str TypeError |
| `parse_money(text)` | Signed decimal string to integer cents, ROUND_HALF_UP, whitespace stripped; booleans/nonstrings rejected, no comma/exponent allowed |
| `parse_csv_table(text)` | CSV with header, returns list of dict rows; duplicate/empty headers or extra columns invalid; entirely empty rows skipped |
| `canonical_json(data)` | JSON text with sorted object keys, UTF-8-friendly literal Unicode, no extra spaces, reject NaN/Infinity |
| `digest_json(data)` | SHA-256 hex lowercase over `canonical_json(data).encode('utf-8')` |
| `stable_unique(rows,field)` | Keep first row for each distinct canonical-JSON value at that field; deepcopy resulting rows; missing field KeyError |
| `group_by_window(events,window)` | Sort events stably by timestamp; grouping key is normalized device, normalized kind, whitespace-collapsed exact-case message; group stays open iff timestamp minus group FIRST timestamp is strictly less than window; output keys device/kind/message/first/last/count |
| `filter_by_severity(groups,minimum)` | Select rows where normalized row.severity (default info) is at least minimum (debug=0,info=1,warning=2,critical=3); unknown severity error; preserves order |
| `safe_path(path)` | Reject absolute, Windows drive prefix, backslashes, NUL, parent segments; strip harmless `.` and empty POSIX segments; empty result error |
| `chunks(data,size)` | Divide bytes into contiguous ordered chunks of size; empty input → empty list; invalid size error |
| `hash_chunks(chunks)` | SHA-256 hex of concatenated bytes of chunks; reject non-byte chunks |
| `gzip_deterministic(data)` | GZIP compression with mtime=0 (gzip version and runtime may affect header metadata; only run same-environment comparisons) |
| `toposort(graph)` | Graph mapping task → list of dependencies; lexicographically smallest currently available node first; missing dependency and cycles error |
| `diff_by_id(before,after)` | Compare lists of dicts with unique id; return sorted string-IDs in added/removed/changed using canonical JSON equality |
| `merge_patch(base,patch)` | JSON merge-patch semantics: nonobject patch replaces whole value; null values in a dict remove keys recursively |
| `redact_paths(data,paths)` | Deepcopy, delete existing nested dictionary keys at dotted field paths; nonexistent paths unchanged; no wildcard paths |
| `make_query(params)` | Sort key names, URL encode pairs with standard urlencode; list values repeated in order, None omitted, booleans lowercase |
| `png_dimensions(bytes)` | Only validate PNG signature and IHDR header, read positive width/height; does NOT validate full image/CRC or decompression safety |
| `retry_delays(count,base_ms,cap_ms)` | Exponential base*2^index, capped, return delay list; nonnegative count, positive base/cap, integers only |

**Private function:** `private.project_risk_score@1(event)` takes a dict and returns a demonstration integer risk score. The implementation stays opaque; only an authorization-bearing host may invoke it. This is an intentionally toy business rule, not a safe risk model.

## Deliberate near-miss candidates (Arm B)

- `candidate.parse_money_bankers@1`: same input/output signature as `parse_money` but uses HALF_EVEN for ties; wrong for `1.005`.
- `candidate.safe_path_loose@1`: accepts/re-writes traversal patterns instead of rejecting; wrong security contract.
- `candidate.group_by_eventid@1`: groups by unique event_id rather than normalized behavior and time window.
- `private.project_risk_score@1`: restricted to scope `project-a`, requires declared effect `project.policy`; public-only agents must not bind it.

## Important limits

Neither conventional imports nor this registry can prove contracts are sufficient from type signatures alone. Untrusted code may lie about effects. This Python mock does not sandbox imports, protect keys, encrypt private code or enforce OS permissions. Security conclusions must be marked as not established until backed by a true external execution boundary.
