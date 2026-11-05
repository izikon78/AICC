"""Shared effectful primitives for the AIN v0 streaming-workflow study (docs/ain/COMPLEX_TASK.md).

Every form (Python reference, typed IR, AIN) reaches exactly these primitives. What differs between forms is the
composition an author writes. Decisions not fixed by the task contract are numbered D-xx in SEMANTICS_FREEZE.md.
"""
import copy, hashlib, json, unicodedata
from collections import deque

I64 = 2**63 - 1
UNICODE_VERSION = "15.0.0"
INF = "INF"  # logical positive-infinity frontier for the explicit end marker (D-14)
# D-05: the contract's exact whitespace set, NOT Python str.split()/isspace (which also include U+001C..U+001F).
WS = frozenset(chr(c) for c in (0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0x85, 0xA0, 0x1680, *range(0x2000, 0x200B),
                                0x2028, 0x2029, 0x202F, 0x205F, 0x3000))
EVENT_FIELDS = ("tenant", "event_id", "device", "kind", "message", "timestamp", "severity")
REASONS = frozenset({0, 1, 2, 3, 10, 20, 30})  # D-21: example allowlist of numeric reason codes
REQUIRED_EFFECTS = frozenset({"source.read", "sink.read", "sink.commit", "policy.invoke"})


class WorkflowError(Exception):
    def __init__(self, code, offset=None, detail=""):
        super().__init__(f"{code} at {offset}: {detail}")
        self.code, self.offset, self.detail = code, offset, detail


class Cancelled(Exception):
    pass


class Crash(Exception):
    """Simulated process crash. Not an outcome: the harness restarts a new writer (D-24)."""


def is_int(x):
    return type(x) is int  # D-02: bool is not an integer; subclasses rejected


def collapse(s):
    out, cur = [], []
    for ch in s:
        if ch in WS:
            if cur:
                out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return " ".join(out)


def norm_tag(s):
    return collapse(unicodedata.normalize("NFKC", s).casefold())


def check_unicode():
    if unicodedata.unidata_version != UNICODE_VERSION:
        raise WorkflowError("UNICODE_VERSION", None, unicodedata.unidata_version)


# ---------------------------------------------------------------- configuration (D-01..D-03)
CONFIG_KEYS = ("window", "lateness", "horizon", "concurrency", "queue", "buffered_events", "dedupe_entries",
               "open_groups", "epoch_reports")


def validate_config(values, minimum):
    if not isinstance(values, list) or len(values) != 9 or not all(is_int(v) for v in values):
        raise WorkflowError("INVALID_CONFIG", None, "nine integers required")
    cfg = dict(zip(CONFIG_KEYS, values))
    for k, v in cfg.items():
        if v > I64 or (v < 0 if k == "lateness" else v <= 0):
            raise WorkflowError("INVALID_CONFIG", None, k)
    if cfg["horizon"] < cfg["window"]:
        raise WorkflowError("INVALID_CONFIG", None, "horizon < window")
    if not is_int(minimum) or not 0 <= minimum <= 3:
        raise WorkflowError("INVALID_CONFIG", None, "minimum")
    cfg["minimum"] = minimum
    return cfg


def frontier(watermark, lateness):
    return INF if watermark == INF else max(0, watermark - lateness)


def lt(a, b):  # a < b with INF on the right
    return True if b == INF else a < b


# ---------------------------------------------------------------- record validation (D-06..D-10 error priority)
def _check_str(x, field, offset, lo, hi):
    if type(x) is not str or not lo <= len(x) <= hi or any(0xD800 <= ord(c) <= 0xDFFF for c in x):
        raise WorkflowError("INVALID_RECORD", offset, field)


def validate_record(r, prev_offset, ended):
    """Priority: envelope/offset type -> offset order -> after-end -> fields -> (watermark order, by caller)."""
    if type(r) is not dict or r.get("type") not in ("event", "watermark", "end"):
        raise WorkflowError("INVALID_RECORD", r.get("offset") if type(r) is dict else None, "envelope")
    off = r.get("offset")
    if not is_int(off) or not 0 <= off <= I64:
        raise WorkflowError("INVALID_RECORD", off if is_int(off) else None, "offset")
    if prev_offset is not None and off <= prev_offset:
        raise WorkflowError("OFFSET_ORDER", off, f"after {prev_offset}")
    if ended:
        raise WorkflowError("AFTER_END", off, "record after end marker")
    kind = r["type"]
    want = {"event": {"type", "offset", *EVENT_FIELDS}, "watermark": {"type", "offset", "watermark"},
            "end": {"type", "offset"}}[kind]
    if set(r) != want:
        raise WorkflowError("INVALID_RECORD", off, "fields")
    if kind == "watermark":
        w = r["watermark"]
        if not is_int(w) or not 0 <= w <= I64:
            raise WorkflowError("INVALID_RECORD", off, "watermark")
    elif kind == "event":
        _check_str(r["tenant"], "tenant", off, 1, 128)
        _check_str(r["event_id"], "event_id", off, 1, 128)
        _check_str(r["device"], "device", off, 0, 256)
        _check_str(r["kind"], "kind", off, 0, 256)
        _check_str(r["message"], "message", off, 0, 4096)
        if not is_int(r["timestamp"]) or not 0 <= r["timestamp"] <= I64:
            raise WorkflowError("INVALID_RECORD", off, "timestamp")
        if not is_int(r["severity"]) or not 0 <= r["severity"] <= 3:
            raise WorkflowError("INVALID_RECORD", off, "severity")
    return kind


# ---------------------------------------------------------------- workflow state and checkpoints
def new_state():
    return {"cursor": None, "watermark": 0, "counters": {"late": 0, "duplicate": 0, "filtered": 0, "accepted": 0},
            "dedupe": {}, "buffer": [], "groups": [], "newest": {}, "complete": False}


def dedupe_key(r):
    return json.dumps([r["tenant"], r["event_id"]], ensure_ascii=False)  # exact, collision-free (D-13)


def group_key(e):
    return (e["tenant"], e["n_device"], e["n_kind"], e["n_message"])


def add_to_group(state, e, cfg):
    """Anchored grouping with capacity and signed-64 overflow checks (D-15, D-16)."""
    k = json.dumps(group_key(e), ensure_ascii=False)
    gid = state["newest"].get(k)
    g = next((x for x in state["groups"] if x["first_offset"] == gid), None) if gid is not None else None
    if g is not None and e["timestamp"] - g["first"] < cfg["window"]:
        if g["count"] + 1 > I64:
            raise WorkflowError("OVERFLOW", e["offset"], "count")
        if g["severity_sum"] + e["severity"] > I64:
            raise WorkflowError("OVERFLOW", e["offset"], "severity_sum")
        g["last"] = e["timestamp"]; g["count"] += 1; g["severity_sum"] += e["severity"]
    else:
        if len(state["groups"]) >= cfg["open_groups"]:
            raise WorkflowError("CAPACITY", e["offset"], "open_groups")
        g = {"tenant": e["tenant"], "device": e["n_device"], "kind": e["n_kind"], "message": e["n_message"],
             "first": e["timestamp"], "last": e["timestamp"], "first_offset": e["offset"], "count": 1,
             "severity_sum": e["severity"]}
        state["groups"].append(g); state["newest"][k] = e["offset"]


def evict_dedupe(dedupe, c, horizon):
    return {k: t for k, t in dedupe.items() if not (c == INF or c >= t + horizon)}


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def observable_checkpoint(cp):
    """Implementation-neutral view used by the conformance harness (D-27)."""
    if cp is None:
        return None
    s = cp["state"]
    return {"cursor": s["cursor"], "watermark": s["watermark"], "counters": s["counters"], "complete": s["complete"],
            "dedupe": sorted([k, t] for k, t in s["dedupe"].items()),
            "buffered_offsets": sorted(e["offset"] for e in s["buffer"]),
            "open_groups": sorted([g["first"], g["first_offset"], g["last"], g["count"], g["severity_sum"]] for g in s["groups"]),
            "manifest_id": cp["manifest_id"], "config": cp["config"]}


# ---------------------------------------------------------------- reference transactional sink (D-22..D-26)
class Sink:
    def __init__(self, source_id):
        self.source_id, self.fence, self.published, self.epochs, self.checkpoint, self.log = source_id, 0, [], {}, None, []

    def acquire_fence(self):
        self.fence += 1; self.log.append(["fence", self.fence]); return self.fence

    def latest_checkpoint(self):
        return copy.deepcopy(self.checkpoint)

    def commit(self, token, epoch_id, payload):
        key = canonical(epoch_id); digest = hashlib.sha256(canonical(payload).encode()).hexdigest()
        if token != self.fence:
            self.log.append(["fenced", epoch_id, token]); raise WorkflowError("FENCED", epoch_id[1], f"token {token} != {self.fence}")
        if key in self.epochs:
            if self.epochs[key]["digest"] != digest:
                self.log.append(["conflict", epoch_id]); raise WorkflowError("CONFLICT", epoch_id[1], "payload differs")
            self.log.append(["idempotent", epoch_id]); return self.epochs[key]["receipt"]
        cur = self.checkpoint["state"]["cursor"] if self.checkpoint else None
        if cur is not None and epoch_id[1] <= cur:
            raise WorkflowError("FENCED", epoch_id[1], "cursor regression")
        receipt = {"epoch": epoch_id, "seq": len(self.epochs) + 1, "digest": digest}
        self.published.extend(copy.deepcopy(payload["reports"]))
        self.epochs[key] = {"digest": digest, "receipt": receipt}
        self.checkpoint = copy.deepcopy(payload["checkpoint"])
        self.log.append(["commit", epoch_id, len(payload["reports"])])
        return receipt


# ---------------------------------------------------------------- bounded private-policy executor (D-17..D-21)
def run_policy_calls(groups, policy, version, cfg, hooks, schedule):
    """Deterministic simulation of <=concurrency running and <=queue waiting calls.
    Returns (results, stop) where results[i] is ("ok", score, reason) | ("error", detail) and stop is None,
    "CANCELLED" or "AUTHORITY". Waiting work is never dropped to satisfy limits; submission blocks instead."""
    n, waiting, running, results, stop, nxt = len(groups), deque(), [], {}, None, 0
    stats = hooks["stats"]
    while True:
        while stop is None and nxt < n and len(waiting) < cfg["queue"]:
            waiting.append(nxt); nxt += 1
        while stop is None and waiting and len(running) < cfg["concurrency"]:
            if hooks["cancel"]("policy_start"):
                stop = "CANCELLED"; break
            if not hooks["authority"]("policy_start"):
                stop = "AUTHORITY"; break
            i = waiting.popleft(); running.append(i); stats["starts"].append(i)
            try:
                out = policy(groups[i], version)
                ok = (isinstance(out, tuple) and len(out) == 2 and is_int(out[0]) and 0 <= out[0] <= 1000
                      and is_int(out[1]) and out[1] in REASONS)
                results[i] = ("ok", out[0], out[1]) if ok else ("error", "invalid policy output")
            except Exception as ex:  # declared policy errors (fixtures raise PolicyFailure)
                results[i] = ("error", type(ex).__name__)
            if nxt < n and len(waiting) < cfg["queue"]:  # keep the queue topped up between starts
                waiting.append(nxt); nxt += 1
        stats["max_running"] = max(stats["max_running"], len(running))
        stats["max_waiting"] = max(stats["max_waiting"], len(waiting))
        if not running:
            if stop is not None or (nxt >= n and not waiting):
                break
            continue
        j = schedule(running)            # completion order is arbitrary; the scheduler fixes it for a test
        running.remove(j); stats["completions"].append(j)
    return results, stop


class PolicyFailure(Exception):
    pass


def resolve_epoch(results, stop):
    """D-19 precedence: CANCELLED > AUTHORITY > lowest-index POLICY_ERROR."""
    if stop == "CANCELLED":
        raise Cancelled()
    if stop == "AUTHORITY":
        raise WorkflowError("AUTHORITY", None, "policy_start")
    bad = sorted(i for i, r in results.items() if r[0] == "error")
    if bad:
        raise WorkflowError("POLICY_ERROR", None, f"group index {bad[0]}")


# ---------------------------------------------------------------- manifest pinning and checkpoint restore (D-11, D-12)
def pin_manifest(manifest, cfg, effects_used):
    if type(manifest) is not dict or type(manifest.get("policy_version")) is not str:
        raise WorkflowError("INVALID_CONFIG", None, "manifest")
    missing = set(effects_used) - set(manifest.get("effects", ()))
    if missing:
        raise WorkflowError("EFFECT_DENIED", None, ",".join(sorted(missing)))
    return {"id": hashlib.sha256(canonical(manifest).encode()).hexdigest()[:16], "policy_version": manifest["policy_version"]}


def restore_state(sink, pinned, cfg, records):
    """Returns (state, start_position). The cursor is the offset of the last committed record; replay resumes at
    the record after it (D-12). A checkpoint for another manifest or configuration is rejected."""
    cp = sink.latest_checkpoint()
    if cp is None:
        return new_state(), 0
    if cp.get("manifest_id") != pinned["id"] or cp.get("config") != cfg or type(cp.get("state")) is not dict:
        raise WorkflowError("INVALID_CHECKPOINT", None, "manifest/config/state mismatch")
    state = cp["state"]
    for i, r in enumerate(records):
        if type(r) is dict and r.get("offset") == state["cursor"]:
            return state, i + 1
    raise WorkflowError("INVALID_CHECKPOINT", state.get("cursor"), "cursor not in source")


def make_report(source_id, g, result, version):
    return {"group_id": f"{source_id}:{g['first_offset']}", "tenant": g["tenant"], "device": g["device"],
            "kind": g["kind"], "message": g["message"], "first": g["first"], "last": g["last"],
            "first_offset": g["first_offset"], "count": g["count"], "severity_sum": g["severity_sum"],
            "score": result[1], "reason": result[2], "policy_version": version}


def outcome(status, err=None):
    return {"status": status, "error": None if err is None else {"code": err.code, "offset": err.offset, "detail": err.detail}}
