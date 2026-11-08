"""Equivalent event-processing plans for an AICC optimization experiment.

The plans combine established techniques: predicate pushdown, bounded normalization
caches, per-key partitioning, and an ordered-input fast path. They were designed by
an AI coding agent; no claim of algorithmic novelty or autonomous discovery is made.
All conventional and AICC arms may use every plan under the same preconditions.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from functools import lru_cache
from typing import Any, Callable
import unicodedata


Event = Mapping[str, Any]
Group = dict[str, Any]
Key = tuple[str, str, str]
Record = tuple[int, int, Key, int]


class OrderPreconditionError(ValueError):
    """The ordered plan received decreasing raw-input timestamps."""


def normalize_tag(value: str) -> str:
    """NFKC, full case folding, then Python Unicode-whitespace collapse."""
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def normalize_message(value: str) -> str:
    """Collapse/trim Unicode whitespace; preserve case and other characters."""
    return " ".join(value.split())


def _parameters(window: int, minimum: int) -> None:
    if not isinstance(window, int) or isinstance(window, bool) or window <= 0:
        raise ValueError("window must be a positive int, excluding bool")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or not 0 <= minimum <= 3:
        raise ValueError("minimum must be an int in 0..3, excluding bool")


def _unique_validated(events: Iterable[Event], *, ordered: bool = False):
    """Validate all raw rows, then keep the first occurrence of each exact ID.

    The ordered precondition is checked on every valid raw row, including rows
    later eliminated by deduplication or severity filtering. No input is mutated.
    """
    seen: set[str] = set()
    previous_timestamp: int | None = None
    for ordinal, event in enumerate(events):
        if not isinstance(event, Mapping):
            raise TypeError("each event must be a mapping")
        try:
            event_id = event["event_id"]
            device, kind, message = event["device"], event["kind"], event["message"]
            timestamp, severity = event["timestamp"], event["severity"]
        except KeyError as error:
            raise TypeError("each event requires event_id/device/kind/message/timestamp/severity") from error
        if not all(isinstance(value, str) for value in (event_id, device, kind, message)):
            raise TypeError("event_id, device, kind and message must be strings")
        if not isinstance(timestamp, int) or isinstance(timestamp, bool):
            raise TypeError("timestamp must be an int, excluding bool")
        if not isinstance(severity, int) or isinstance(severity, bool):
            raise TypeError("severity must be an int, excluding bool")
        if not 0 <= severity <= 3:
            raise ValueError("severity must be in 0..3")
        if ordered and previous_timestamp is not None and timestamp < previous_timestamp:
            raise OrderPreconditionError("ordered plan requires nondecreasing raw timestamps")
        previous_timestamp = timestamp
        if event_id in seen:
            continue
        seen.add(event_id)
        yield timestamp, ordinal, device, kind, message, severity


def _new_group(key: Key, timestamp: int, ordinal: int, severity: int) -> Group:
    return {
        "device": key[0], "kind": key[1], "message": key[2],
        "first": timestamp, "last": timestamp, "count": 1,
        "severity_sum": severity, "first_ordinal": ordinal,
    }


def _group_sorted(records: Iterable[Record], window: int) -> list[Group]:
    groups: list[Group] = []
    current: dict[Key, Group] = {}
    for timestamp, ordinal, key, severity in records:
        group = current.get(key)
        if group is None or timestamp - group["first"] >= window:
            group = _new_group(key, timestamp, ordinal, severity)
            current[key] = group
            groups.append(group)
        else:
            group["last"] = timestamp
            group["count"] += 1
            group["severity_sum"] += severity
    return groups


def _normalizers():
    # Bounded and local: no growing process-wide cache or cache leakage between jobs.
    return (lru_cache(maxsize=8192)(normalize_tag),
            lru_cache(maxsize=4096)(normalize_message))


def process_reference(events: Iterable[Event], window: int, minimum: int = 0) -> list[Group]:
    """Transparent global-sort reference; no normalization cache or filter pushdown."""
    _parameters(window, minimum)
    records: list[Record] = []
    for timestamp, ordinal, device, kind, message, severity in _unique_validated(events):
        key = normalize_tag(device), normalize_tag(kind), normalize_message(message)
        records.append((timestamp, ordinal, key, severity))
    records.sort(key=lambda record: (record[0], record[1]))
    return _group_sorted((record for record in records if record[3] >= minimum), window)


def process_cached(events: Iterable[Event], window: int, minimum: int = 0) -> list[Group]:
    """Global sort with early filtering and bounded per-job normalization caches."""
    _parameters(window, minimum)
    tag, message_norm = _normalizers()
    records: list[Record] = []
    for timestamp, ordinal, device, kind, message, severity in _unique_validated(events):
        if severity < minimum:
            continue
        key = tag(device), tag(kind), message_norm(message)
        records.append((timestamp, ordinal, key, severity))
    records.sort(key=lambda record: (record[0], record[1]))
    return _group_sorted(records, window)


def process_partitioned(events: Iterable[Event], window: int, minimum: int = 0) -> list[Group]:
    """Normalize/partition once, sort within each key, then merge group creation order.

    The alternative flow can reduce sorting work when many keys each contain few
    events. Its extra dictionaries/lists can instead lose on other workloads.
    """
    _parameters(window, minimum)
    tag, message_norm = _normalizers()
    partitions: dict[Key, list[tuple[int, int, int]]] = {}
    for timestamp, ordinal, device, kind, message, severity in _unique_validated(events):
        if severity < minimum:
            continue
        key = tag(device), tag(kind), message_norm(message)
        partitions.setdefault(key, []).append((timestamp, ordinal, severity))
    groups: list[Group] = []
    for key, rows in partitions.items():
        rows.sort()  # timestamp, unique raw ordinal, severity (the last never breaks a tie)
        group: Group | None = None
        for timestamp, ordinal, severity in rows:
            if group is None or timestamp - group["first"] >= window:
                group = _new_group(key, timestamp, ordinal, severity)
                groups.append(group)
            else:
                group["last"] = timestamp
                group["count"] += 1
                group["severity_sum"] += severity
    groups.sort(key=lambda group: (group["first"], group["first_ordinal"]))
    return groups


def process_ordered(events: Iterable[Event], window: int, minimum: int = 0) -> list[Group]:
    """One-pass grouping, valid only for nondecreasing raw-input timestamps.

    The precondition is checked while consuming the stream. An unsorted job raises
    OrderPreconditionError; it never silently uses the ordered fast path.
    """
    _parameters(window, minimum)
    tag, message_norm = _normalizers()

    def records():
        for timestamp, ordinal, device, kind, message, severity in _unique_validated(events, ordered=True):
            if severity >= minimum:
                yield timestamp, ordinal, (tag(device), tag(kind), message_norm(message)), severity

    return _group_sorted(records(), window)


VARIANTS: dict[str, Callable[..., list[Group]]] = {
    "reference": process_reference,
    "cached": process_cached,
    "partitioned": process_partitioned,
    "ordered": process_ordered,
}


def process(events: Iterable[Event], window: int, minimum: int = 0,
            variant: str = "cached") -> list[Group]:
    """Run a named equivalent plan. Selection policy belongs outside this module."""
    try:
        implementation = VARIANTS[variant]
    except KeyError as error:
        raise ValueError("unknown processing variant: " + str(variant)) from error
    return implementation(events, window, minimum)
