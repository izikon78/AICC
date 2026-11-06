"""Shared transactional-stream capabilities for the AIN v0 development study.

These are trusted, in-process services, not a security boundary.  The private
policy used here is a test fixture.  See ENGINE.md for hooks and limitations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import copy
import hashlib
import heapq
import json
import queue
import threading
import unicodedata

MAX_INT = (1 << 63) - 1
COUNTERS = ("late", "duplicate", "filtered", "accepted")
WHITESPACE = frozenset(chr(c) for c in (
    *range(0x09, 0x0e), 0x20, 0x85, 0xa0, 0x1680,
    *range(0x2000, 0x200b), 0x2028, 0x2029, 0x202f, 0x205f, 0x3000))
GROUP_KEYS = {"tenant", "device", "kind", "message", "first_timestamp",
              "last_timestamp", "first_offset", "count", "severity_sum"}


class WorkflowError(Exception):
    def __init__(self, code, message="", **details):
        self.code, self.message, self.details = str(code), str(message), details
        super().__init__(self.message or self.code)

    def data(self):
        return {"code": self.code, "message": self.message, "details": self.details}


def _fail(message, code="VALIDATION", **details):
    raise WorkflowError(code, message, **details)


def _int(value, name, low=0, high=MAX_INT, code="VALIDATION"):
    if type(value) is not int or not low <= value <= high:
        _fail("invalid integer", code, field=name)
    return value


def _text(value, name, maximum, nonempty=False, code="VALIDATION"):
    if (type(value) is not str or len(value) > maximum or
            (nonempty and not value) or
            any(0xd800 <= ord(c) <= 0xdfff for c in value)):
        _fail("invalid Unicode string", code, field=name)
    return value


def _plain(value, depth=0):
    """Reject subclasses/accessors, floats, and non-JSON values before copying."""
    if depth > 32:
        _fail("input nesting exceeds limit")
    if type(value) in (str, int, bool) or value is None:
        if type(value) is str:
            _text(value, "string", 65536)
        return value
    if type(value) is list:
        return [_plain(x, depth + 1) for x in value]
    if type(value) is dict and all(type(k) is str for k in value):
        return {_text(k, "object key", 65536): _plain(v, depth + 1)
                for k, v in value.items()}
    _fail("only plain decoded JSON data are accepted")


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def checkpoint_integrity(snapshot):
    return _digest({k: v for k, v in snapshot.items() if k != "integrity"})


def collapse(value):
    parts, part = [], []
    for c in value:
        if c in WHITESPACE:
            if part:
                parts.append("".join(part))
                part = []
        else:
            part.append(c)
    if part:
        parts.append("".join(part))
    return " ".join(parts)


@dataclass(frozen=True)
class Config:
    window: int = 600
    lateness: int = 120
    dedupe_horizon: int = 1200
    concurrency: int = 8
    queue: int = 32
    buffered_events: int = 100000
    dedupe_entries: int = 200000
    open_groups: int = 100000
    epoch_reports: int = 100000
    minimum: int = 1

    def __post_init__(self):
        for key, value in asdict(self).items():
            _int(value, key, 0 if key in ("lateness", "minimum") else 1,
                 3 if key == "minimum" else MAX_INT)
        if self.dedupe_horizon < self.window:
            _fail("dedupe horizon must be at least window", field="dedupe_horizon")


@dataclass
class State:
    cursor: int = -1
    watermark: int = 0
    complete: bool = False
    seen: dict = field(default_factory=dict)
    pending: list = field(default_factory=list)
    groups: dict = field(default_factory=dict)
    counters: dict = field(default_factory=lambda: dict.fromkeys(COUNTERS, 0))
    epoch_offset: int | None = None


@dataclass
class _InvalidRecord:
    """An inert deferred admission error; never retains an accessor object."""
    error: WorkflowError


class Sink:
    """Thread-safe in-memory reference transaction sink (not durable storage)."""
    def __init__(self):
        self._store = {"reports": [], "checkpoints": {}, "receipts": {},
                       "trace": [], "payloads": {}}
        self.fences = {}
        self._lock = threading.RLock()

    @property
    def reports(self):
        return self._store["reports"]

    @property
    def checkpoints(self):
        return self._store["checkpoints"]

    @property
    def receipts(self):
        return self._store["receipts"]

    @property
    def trace(self):
        return self._store["trace"]

    @property
    def _payloads(self):
        return self._store["payloads"]

    def snapshot(self):
        """Read a consistent inspection view; receipts use tuple identity keys."""
        with self._lock:
            return copy.deepcopy({k: v for k, v in self._store.items() if k != "payloads"})

    def acquire(self, source_id="default"):
        with self._lock:
            token = self.fences.get(source_id, 0) + 1
            self.fences[source_id] = token
            return token

    def commit(self, source_id, epoch_offset, payload, writer_token):
        staged = _plain(payload)
        if type(staged) is not dict or set(staged) != {"reports", "checkpoint"}:
            _fail("invalid transaction", "CHECKPOINT")
        snapshot = staged["checkpoint"]
        if (type(snapshot) is not dict or snapshot.get("source_id") != source_id or
                snapshot.get("cursor") != epoch_offset or
                snapshot.get("integrity") != checkpoint_integrity(snapshot) or
                type(staged["reports"]) is not list):
            _fail("invalid transaction checkpoint", "CHECKPOINT")
        identity, digest = (source_id, epoch_offset), _digest(staged)
        with self._lock:
            if type(writer_token) is not int or writer_token != self.fences.get(source_id):
                _fail("stale writer fencing token", "FENCED")
            if identity in self.receipts:
                if self._payloads[identity] != digest:
                    _fail("epoch identity reused with another payload", "EPOCH_CONFLICT")
                return copy.deepcopy(self.receipts[identity])
            previous = self.checkpoints.get(source_id)
            if previous is not None and epoch_offset <= previous["cursor"]:
                _fail("writer cannot move committed cursor backward", "FENCED")
            if previous is not None and previous["complete"]:
                _fail("completed source cannot publish another epoch", "FENCED")
            receipt = {"source_id": source_id, "epoch_offset": epoch_offset,
                       "payload_sha256": digest}
            # Build every replacement before making any visible assignment.
            new_reports = self.reports + copy.deepcopy(staged["reports"])
            new_checkpoints = {**self.checkpoints, source_id: copy.deepcopy(snapshot)}
            new_trace = self.trace + [{"source_id": source_id,
                                      "epoch_offset": epoch_offset, **copy.deepcopy(staged)}]
            new_receipts = {**self.receipts, identity: receipt}
            new_payloads = {**self._payloads, identity: digest}
            self._store = {"reports": new_reports, "checkpoints": new_checkpoints,
                           "trace": new_trace, "receipts": new_receipts,
                           "payloads": new_payloads}
            return copy.deepcopy(receipt)


def _fixture_policy(group, version, cancel_event):
    return min(1000, group["severity_sum"] * 100 // group["count"]), 0


class Host:
    def __init__(self, records, config=None, sink=None, **options):
        known = {"source_id", "writer_token", "policy", "policy_version",
                 "allowed_tenants", "allowed_reasons", "authority", "cancel", "fault"}
        if set(options) - known:
            _fail("unknown host options", fields=sorted(set(options) - known))
        if type(records) is not list:
            _fail("source must be a plain replayable list")
        self.records = []
        for record in records:
            try:
                self.records.append(_plain(record))
            except WorkflowError as error:
                # Validate a malformed future record when it is admitted, after
                # any earlier epoch has committed. Do not retain hostile objects.
                self.records.append(_InvalidRecord(error))
        if config is None:
            config = Config()
        elif type(config) is dict:
            if set(config) - set(Config.__dataclass_fields__):
                _fail("unknown configuration fields")
            config = Config(**config)
        if type(config) is not Config:
            _fail("configuration must be Config or a plain dictionary")
        self.config, self.sink = config, sink if sink is not None else Sink()
        if type(self.sink) is not Sink:
            _fail("sink must be the reference Sink")
        self.source_id = _text(options.get("source_id", "default"), "source_id", 256, True)
        self.writer_token = options.get("writer_token")
        if self.writer_token is not None:
            _int(self.writer_token, "writer_token", 1)
        self.policy = options.get("policy", _fixture_policy)
        if not callable(self.policy):
            _fail("policy must be a trusted local fixture callable")
        self.policy_version = _text(options.get("policy_version", "fixture-v1"),
                                    "policy_version", 128, True)
        tenants = options.get("allowed_tenants")
        if tenants is not None:
            if type(tenants) not in (list, tuple, set, frozenset):
                _fail("allowed_tenants must be a collection of identifiers")
            for tenant in tenants:
                _text(tenant, "allowed_tenants", 128, True)
            tenants = sorted(set(tenants))
        self.allowed_tenants = tenants
        reasons = options.get("allowed_reasons", (0, 1, 2, 3))
        if type(reasons) not in (list, tuple, set, frozenset) or not reasons:
            _fail("allowed_reasons must be a nonempty integer collection")
        for reason in reasons:
            _int(reason, "allowed_reasons")
        self.allowed_reasons = sorted(set(reasons))
        self.authority, self.cancel = options.get("authority"), options.get("cancel")
        if self.authority is not None and not callable(self.authority):
            _fail("authority must be a local fixture callable")
        if (self.cancel is not None and not callable(self.cancel) and
                not callable(getattr(self.cancel, "is_set", None))):
            _fail("cancel must be a callable or event token")
        self.fault = options.get("fault")
        if self.fault is not None and not callable(self.fault) and self.fault not in (
                "before_commit", "after_commit"):
            _fail("unknown fault hook")
        self.cancel_event = threading.Event()
        self._cancel_lock, self._metrics_lock = threading.Lock(), threading.Lock()
        self._index, self.state = 0, None
        self.scheduler = {"peak_running": 0, "peak_waiting": 0,
                          "started": 0, "finished": 0}
        self.manifest = {"config": asdict(config), "policy_version": self.policy_version,
                         "allowed_tenants": tenants, "allowed_reasons": self.allowed_reasons,
                         "unicode": "15.0.0"}

    def _observe_cancel(self):
        with self._cancel_lock:
            if self.cancel_event.is_set():
                return True
            if self.cancel is not None:
                value = self.cancel() if callable(self.cancel) else self.cancel.is_set()
                if value:
                    self.cancel_event.set()
            return self.cancel_event.is_set()

    def check_cancel(self):
        if self._observe_cancel():
            _fail("caller cancelled the workflow", "CANCELLED")

    def _version(self):
        if getattr(self.policy, "version", self.policy_version) != self.policy_version:
            _fail("private policy version differs from pinned version", "POLICY_VERSION")

    def _authority(self, stage, group=None):
        self._version()
        if group is not None and self.allowed_tenants is not None:
            if group["tenant"] not in self.allowed_tenants:
                _fail("tenant is outside private-policy scope", "AUTHORITY")
        if self.authority is not None and self.authority(stage, copy.deepcopy(group)) is not True:
            _fail("host authority denied", "AUTHORITY", stage=stage)

    def restore(self):
        if unicodedata.unidata_version != "15.0.0":
            _fail("Unicode dependency must be 15.0.0", "DEPENDENCY",
                  actual=unicodedata.unidata_version)
        self._version()
        with self.sink._lock:
            snapshot = copy.deepcopy(self.sink.checkpoints.get(self.source_id))
        state = State()
        if snapshot is not None:
            state = self._restore_snapshot(snapshot)
        if self.writer_token is None:
            self.writer_token = self.sink.acquire(self.source_id)
        # Fresh input is never skipped. Restored input was fingerprinted through
        # precisely its durable cursor; an appended suffix is allowed.
        self._index = self._prefix_length(state.cursor) if snapshot is not None else 0
        self.state = state
        return state

    def _restore_snapshot(self, snap):
        expected = {"version", "source_id", "manifest", "cursor", "watermark",
                    "complete", "seen", "pending", "groups", "counters", "integrity",
                    "source_prefix_sha256"}
        if (type(snap) is not dict or set(snap) != expected or snap.get("version") != 0 or
                snap.get("source_id") != self.source_id or
                snap.get("integrity") != checkpoint_integrity(snap)):
            _fail("checkpoint integrity or structure mismatch", "CHECKPOINT")
        manifest = snap["manifest"]
        if type(manifest) is not dict:
            _fail("invalid checkpoint manifest", "CHECKPOINT")
        policy_keys = ("policy_version", "allowed_tenants", "allowed_reasons")
        if any(manifest.get(k) != self.manifest[k] for k in policy_keys):
            _fail("checkpoint private-policy manifest mismatch", "POLICY_VERSION")
        if manifest != self.manifest:
            _fail("checkpoint source or configuration manifest mismatch", "CHECKPOINT")
        cursor = _int(snap["cursor"], "cursor", code="CHECKPOINT")
        prefix_length = self._prefix_length(cursor)
        if _digest(self.records[:prefix_length]) != snap["source_prefix_sha256"]:
            _fail("committed source prefix differs from checkpoint", "CHECKPOINT")
        watermark = _int(snap["watermark"], "watermark", code="CHECKPOINT")
        if type(snap["complete"]) is not bool:
            _fail("invalid completion flag", "CHECKPOINT")
        if (type(snap["counters"]) is not dict or set(snap["counters"]) != set(COUNTERS)):
            _fail("invalid checkpoint counters", "CHECKPOINT")
        for key, value in snap["counters"].items():
            _int(value, key, code="CHECKPOINT")
        for key in ("seen", "pending", "groups"):
            if type(snap[key]) is not list:
                _fail("invalid checkpoint state collection", "CHECKPOINT", field=key)
        state = State(cursor=cursor, watermark=watermark, complete=snap["complete"],
                      counters=copy.deepcopy(snap["counters"]))
        frontier = max(0, watermark - self.config.lateness)
        for entry in snap["seen"]:
            if type(entry) is not dict or set(entry) != {"tenant", "event_id", "timestamp"}:
                _fail("invalid checkpoint ID entry", "CHECKPOINT")
            _text(entry["tenant"], "tenant", 128, True, "CHECKPOINT")
            _text(entry["event_id"], "event_id", 128, True, "CHECKPOINT")
            ts = _int(entry["timestamp"], "timestamp", code="CHECKPOINT")
            key = (entry["tenant"], entry["event_id"])
            if key in state.seen or ts + self.config.dedupe_horizon <= frontier:
                _fail("invalid retained checkpoint ID", "CHECKPOINT")
            state.seen[key] = ts
        pending_offsets = set()
        for record in snap["pending"]:
            try:
                self._validate_shape(record, normalized=True)
            except WorkflowError:
                _fail("invalid checkpoint pending event", "CHECKPOINT")
            if (record["kind"] != "event" or record["offset"] > cursor or
                    record["offset"] in pending_offsets):
                _fail("invalid checkpoint pending cursor", "CHECKPOINT")
            pending_offsets.add(record["offset"])
            if record["event"]["timestamp"] < frontier:
                _fail("checkpoint pending event precedes frontier", "CHECKPOINT")
            heapq.heappush(state.pending, (record["event"]["timestamp"], record["offset"], record))
        group_offsets = set()
        for group in snap["groups"]:
            if type(group) is not dict or set(group) != GROUP_KEYS:
                _fail("invalid checkpoint group", "CHECKPOINT")
            for key in ("tenant", "device", "kind", "message"):
                _text(group[key], key, 65536, key == "tenant", "CHECKPOINT")
            first = _int(group["first_timestamp"], "first_timestamp", code="CHECKPOINT")
            last = _int(group["last_timestamp"], "last_timestamp", code="CHECKPOINT")
            offset = _int(group["first_offset"], "first_offset", code="CHECKPOINT")
            count = _int(group["count"], "count", 1, code="CHECKPOINT")
            total = _int(group["severity_sum"], "severity_sum", code="CHECKPOINT")
            if (last < first or last - first >= self.config.window or offset > cursor or
                    offset in group_offsets or total > 3 * count or
                    first + self.config.window <= frontier):
                _fail("invalid checkpoint group invariants", "CHECKPOINT")
            group_offsets.add(offset)
            key = tuple(group[x] for x in ("tenant", "device", "kind", "message"))
            state.groups.setdefault(key, []).append(copy.deepcopy(group))
        for groups in state.groups.values():
            groups.sort(key=lambda g: (g["first_timestamp"], g["first_offset"]))
            if any(b["first_timestamp"] - a["first_timestamp"] < self.config.window
                   for a, b in zip(groups, groups[1:])):
                _fail("overlapping checkpoint anchored groups", "CHECKPOINT")
        if (len(state.seen) > self.config.dedupe_entries or
                len(state.pending) > self.config.buffered_events or
                sum(map(len, state.groups.values())) > self.config.open_groups or
                (state.complete and (state.seen or state.pending or state.groups))):
            _fail("checkpoint exceeds limits or completed state is not empty", "CHECKPOINT")
        # Only the verified committed prefix defines this boundary. A duplicate
        # old offset in a new suffix is validated on admission, after restore.
        boundary = self.records[prefix_length - 1]
        if boundary.get("kind") not in ("watermark", "end"):
            _fail("checkpoint cursor is not a source epoch boundary", "CHECKPOINT")
        if ((boundary["kind"] == "end") != state.complete or
                (not state.complete and boundary.get("timestamp") != watermark)):
            _fail("checkpoint boundary does not match source", "CHECKPOINT")
        return state

    def _prefix_length(self, cursor):
        previous = -1
        for index, record in enumerate(self.records):
            try:
                self._validate_shape(record)
            except WorkflowError:
                _fail("committed source prefix is invalid or truncated", "CHECKPOINT")
            if record["offset"] <= previous or record["offset"] > cursor:
                _fail("committed source cursor is absent or reordered", "CHECKPOINT")
            previous = record["offset"]
            if previous == cursor:
                return index + 1
        _fail("committed source prefix is truncated", "CHECKPOINT")

    def has_next(self):
        return self._index < len(self.records)

    def next_record(self):
        if not self.has_next():
            _fail("read beyond source")
        record = self.records[self._index]
        self._index += 1
        return record

    def _validate_shape(self, record, normalized=False):
        if type(record) is _InvalidRecord:
            raise record.error
        if type(record) is not dict or type(record.get("kind")) is not str:
            _fail("invalid record envelope")
        kind = record["kind"]
        expected = {"event": {"offset", "kind", "event"},
                    "watermark": {"offset", "kind", "timestamp"},
                    "end": {"offset", "kind"}}
        if kind not in expected or set(record) != expected[kind]:
            _fail("invalid record kind or fields")
        _int(record["offset"], "offset")
        if kind == "watermark":
            _int(record["timestamp"], "timestamp")
        elif kind == "event":
            event = record["event"]
            if type(event) is not dict or set(event) != {
                    "tenant", "event_id", "timestamp", "severity", "device", "kind", "message"}:
                _fail("event must have exactly seven declared fields")
            _int(event["timestamp"], "timestamp")
            _int(event["severity"], "severity", 0, 3)
            for key in ("tenant", "event_id"):
                _text(event[key], key, 128, True)
            for key in ("device", "kind"):
                # NFKC/casefold may expand an admitted 256-scalar raw tag.
                _text(event[key], key, 65536 if normalized else 256)
            _text(event["message"], "message", 4096)

    def validate_record(self, state, record):
        self._validate_shape(record)
        if state.complete:
            _fail("source record occurs after explicit end")
        if state.epoch_offset is not None:
            _fail("previous epoch must commit before source admission", "CHECKPOINT")
        if record["offset"] <= state.cursor:
            _fail("source offsets must strictly increase")
        if record["kind"] == "watermark" and record["timestamp"] < state.watermark:
            _fail("watermark decreased")
        state.cursor = record["offset"]

    def reserve(self, state, record):
        if len(state.seen) >= self.config.dedupe_entries:
            _fail("retained IDs exceed capacity", "CAPACITY", resource="dedupe_entries")
        event = record["event"]
        state.seen[(event["tenant"], event["event_id"])] = event["timestamp"]

    def normalize(self, record):
        event = dict(record["event"])
        for key in ("device", "kind"):
            event[key] = collapse(unicodedata.normalize("NFKC", event[key]).casefold())
        event["message"] = collapse(event["message"])
        return {**record, "event": event}

    def buffer(self, state, record):
        if len(state.pending) >= self.config.buffered_events:
            _fail("buffered events exceed capacity", "CAPACITY", resource="buffered_events")
        heapq.heappush(state.pending, (record["event"]["timestamp"], record["offset"], record))

    def count(self, state, category):
        if type(category) is not int or not 0 <= category < len(COUNTERS):
            _fail("unknown event count category")
        key = COUNTERS[category]
        if state.counters[key] == MAX_INT:
            _fail("counter exceeds signed 64-bit result", "OVERFLOW", field=key)
        state.counters[key] += 1

    def advance(self, state, record):
        state.epoch_offset = record["offset"]
        if record["kind"] == "end":
            state.complete = True
            state.seen.clear()
        else:
            state.watermark = record["timestamp"]
            frontier = max(0, state.watermark - self.config.lateness)
            state.seen = {key: ts for key, ts in state.seen.items()
                          if ts + self.config.dedupe_horizon > frontier}

    def pending_ready(self, state):
        return bool(state.pending and (state.complete or state.pending[0][0] <
                                       max(0, state.watermark - self.config.lateness)))

    def aggregate(self, state, record):
        event = record["event"]
        key = tuple(event[x] for x in ("tenant", "device", "kind", "message"))
        groups = state.groups.get(key, [])
        if groups and event["timestamp"] - groups[-1]["first_timestamp"] < self.config.window:
            group = groups[-1]
            if group["count"] == MAX_INT or group["severity_sum"] > MAX_INT - event["severity"]:
                _fail("group result exceeds signed 64-bit integer", "OVERFLOW")
            group["count"] += 1
            group["severity_sum"] += event["severity"]
            group["last_timestamp"] = event["timestamp"]
        else:
            if sum(map(len, state.groups.values())) >= self.config.open_groups:
                _fail("unfinished groups exceed capacity", "CAPACITY", resource="open_groups")
            group = {x: event[x] for x in ("tenant", "device", "kind", "message")}
            group.update(first_timestamp=event["timestamp"], last_timestamp=event["timestamp"],
                         first_offset=record["offset"], count=1, severity_sum=event["severity"])
            state.groups.setdefault(key, []).append(group)

    def ready_groups(self, state):
        ready, retained = [], {}
        frontier = max(0, state.watermark - self.config.lateness)
        for key, groups in state.groups.items():
            for group in groups:
                if state.complete or group["first_timestamp"] + self.config.window <= frontier:
                    if len(ready) >= self.config.epoch_reports:
                        _fail("staged reports exceed capacity", "CAPACITY", resource="epoch_reports")
                    ready.append(group)
                else:
                    retained.setdefault(key, []).append(group)
        state.groups = retained
        return sorted(ready, key=lambda g: (g["first_timestamp"], g["first_offset"]))

    def _invoke_policy(self, index, group):
        self.check_cancel()
        self._authority("policy", group)
        self.check_cancel()
        with self._metrics_lock:
            self._running += 1
            self.scheduler["started"] += 1
            self.scheduler["peak_running"] = max(self.scheduler["peak_running"], self._running)
        try:
            try:
                result = self.policy(copy.deepcopy(group), self.policy_version, self.cancel_event)
            except Exception:
                _fail("private policy declared failure", "POLICY", group_index=index)
            if type(result) in (tuple, list) and len(result) == 2:
                score, reason = result
            elif type(result) is dict and set(result) == {"score", "reason"}:
                score, reason = result["score"], result["reason"]
            else:
                _fail("private policy returned an invalid result", "POLICY", group_index=index)
            if (type(score) is not int or not 0 <= score <= 1000 or
                    type(reason) is not int or reason not in self.allowed_reasons):
                _fail("private policy result violates interface", "POLICY", group_index=index)
            return {"source_id": self.source_id,
                    "group_id": _digest([self.source_id, group["first_offset"]]),
                    **group, "score": score, "reason": reason,
                    "policy_version": self.policy_version}
        finally:
            with self._metrics_lock:
                self._running -= 1
                self.scheduler["finished"] += 1

    def score(self, state, groups):
        self.check_cancel()
        if not groups:
            return []
        # Only queue indices; groups already count against epoch_reports staging.
        work = queue.Queue(maxsize=self.config.queue)
        condition, outcomes = threading.Condition(), [None] * len(groups)
        self._running, finished = 0, [0]

        def worker():
            while True:
                index = work.get()
                if index is None:
                    work.task_done()
                    return
                try:
                    outcomes[index] = self._invoke_policy(index, groups[index])
                except WorkflowError as error:
                    outcomes[index] = error
                except BaseException as error:
                    # Unexpected host implementation errors remain visible on caller.
                    outcomes[index] = error
                finally:
                    work.task_done()
                    with condition:
                        finished[0] += 1
                        condition.notify_all()

        workers = [threading.Thread(target=worker, name=f"ain-policy-{i}", daemon=True)
                   for i in range(min(self.config.concurrency, len(groups)))]
        for thread in workers:
            thread.start()
        submitted = 0
        try:
            while submitted < len(groups) and not self._observe_cancel():
                try:
                    work.put(submitted, timeout=0.01)
                except queue.Full:
                    continue
                submitted += 1
                with self._metrics_lock:
                    self.scheduler["peak_waiting"] = max(self.scheduler["peak_waiting"], work.qsize())
            with condition:
                while finished[0] < submitted:
                    self._observe_cancel()
                    condition.wait(timeout=0.01)
        finally:
            # A cancelled queued item is drained without invoking its policy.
            for _ in workers:
                work.put(None)
            for thread in workers:
                thread.join()
        self.check_cancel()
        for index, outcome in enumerate(outcomes):
            if isinstance(outcome, WorkflowError):
                if outcome.code == "CANCELLED":
                    _fail("caller cancelled the workflow", "CANCELLED")
                if "group_index" not in outcome.details:
                    outcome.details["group_index"] = index
                raise outcome
            if isinstance(outcome, BaseException):
                raise outcome
        return outcomes

    def snapshot(self, state):
        snapshot = {"version": 0, "source_id": self.source_id,
                    "manifest": copy.deepcopy(self.manifest), "cursor": state.cursor,
                    "source_prefix_sha256": _digest(self.records[:self._index]),
                    "watermark": state.watermark, "complete": state.complete,
                    "seen": [{"tenant": k[0], "event_id": k[1], "timestamp": v}
                             for k, v in sorted(state.seen.items())],
                    "pending": [copy.deepcopy(item[2]) for item in sorted(state.pending)],
                    "groups": sorted((copy.deepcopy(g) for gs in state.groups.values() for g in gs),
                                     key=lambda g: (g["first_timestamp"], g["first_offset"])),
                    "counters": dict(state.counters)}
        snapshot["integrity"] = checkpoint_integrity(snapshot)
        return snapshot

    def _fault(self, stage):
        if callable(self.fault):
            self.fault(stage, self)
        elif self.fault == stage:
            _fail("injected transaction fault", "CRASH_BEFORE_COMMIT" if stage ==
                  "before_commit" else "LOST_ACK", stage=stage)

    def commit(self, state, reports):
        self.check_cancel()
        if state.epoch_offset is None:
            _fail("commit requires a watermark or explicit end", "CHECKPOINT")
        payload = {"reports": reports, "checkpoint": self.snapshot(state)}
        self._fault("before_commit")
        # Recheck after fixture hooks, immediately before the atomic transaction.
        self.check_cancel()
        self._authority("precommit")
        self.check_cancel()
        self.sink.commit(self.source_id, state.epoch_offset, payload, self.writer_token)
        self._fault("after_commit")
        state.epoch_offset = None

    @staticmethod
    def error_result(error, source_id="default", sink=None):
        if type(sink) is not Sink:
            sink = None
        if (type(source_id) is not str or not source_id or len(source_id) > 256 or
                any(0xd800 <= ord(c) <= 0xdfff for c in source_id)):
            # Constructor errors must not trigger secondary lookup/hash errors.
            sink, source_id = None, "default"
        with sink._lock if sink is not None else threading.RLock():
            checkpoint = copy.deepcopy(sink.checkpoints.get(source_id)) if sink else None
            reports = [copy.deepcopy(r) for r in sink.reports if r.get("source_id") == source_id] if sink else []
            trace = [copy.deepcopy(t) for t in sink.trace if t["source_id"] == source_id] if sink else []
        counters = checkpoint.get("counters") if type(checkpoint) is dict else None
        if type(counters) is not dict or set(counters) != set(COUNTERS):
            counters = dict.fromkeys(COUNTERS, 0)
        return {"status": ("CANCELLED" if error and error.code == "CANCELLED" else
                           "ERROR" if error else
                           "COMPLETE" if type(checkpoint) is dict and checkpoint.get("complete") is True
                           else "INCOMPLETE"),
                "reports": reports, "counters": copy.deepcopy(counters),
                "checkpoint": checkpoint, "trace": trace,
                "error": error.data() if error else None}

    def outcome(self, error=None):
        return self.error_result(error, self.source_id, self.sink)

    def catalog(self):
        definitions = [
            ("restore", ["host"], "state", "state", lambda h: h.restore()),
            ("has_next", ["host"], "bool", "input", lambda h: h.has_next()),
            ("next_record", ["host"], "record", "input", lambda h: h.next_record()),
            ("check_cancel", ["host"], "void", "state", lambda h: h.check_cancel()),
            ("validate_record", ["host", "state", "record"], "void", "state", lambda h, s, r: h.validate_record(s, r)),
            ("record_kind", ["record"], "int", "pure", lambda r: {"event": 0, "watermark": 1, "end": 2}[r["kind"]]),
            ("frontier", ["state"], "int", "pure", lambda s: max(0, s.watermark - self.config.lateness)),
            ("timestamp", ["record"], "int", "pure", lambda r: r["event"]["timestamp"]),
            ("seen", ["host", "state", "record"], "bool", "state", lambda h, s, r: (r["event"]["tenant"], r["event"]["event_id"]) in s.seen),
            ("reserve", ["host", "state", "record"], "void", "state", lambda h, s, r: h.reserve(s, r)),
            ("severity", ["record"], "int", "pure", lambda r: r["event"]["severity"]),
            ("minimum", ["host"], "int", "pure", lambda h: h.config.minimum),
            ("normalize", ["record"], "record", "pure", lambda r: self.normalize(r)),
            ("buffer", ["host", "state", "record"], "void", "state", lambda h, s, r: h.buffer(s, r)),
            ("count", ["host", "state", "int"], "void", "state", lambda h, s, c: h.count(s, c)),
            ("advance", ["host", "state", "record"], "void", "state", lambda h, s, r: h.advance(s, r)),
            ("pending_ready", ["host", "state"], "bool", "state", lambda h, s: h.pending_ready(s)),
            ("pop_pending", ["host", "state"], "record", "state", lambda h, s: heapq.heappop(s.pending)[2]),
            ("aggregate", ["host", "state", "record"], "void", "state", lambda h, s, r: h.aggregate(s, r)),
            ("ready_groups", ["host", "state"], "groups", "state", lambda h, s: h.ready_groups(s)),
            ("score", ["host", "state", "groups"], "reports", "policy", lambda h, s, g: h.score(s, g)),
            ("commit", ["host", "state", "reports"], "void", "commit", lambda h, s, r: h.commit(s, r)),
            ("result", ["host", "state"], "result", "state", lambda h, s: h.outcome()),
        ]
        return {i: {"name": name, "args": args, "return": result,
                    "effect": effect, "fn": fn}
                for i, (name, args, result, effect, fn) in enumerate(definitions)}
