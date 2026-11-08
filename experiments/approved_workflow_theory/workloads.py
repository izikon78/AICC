"""Executable workflow fixtures under a perfectly approved shared-core assumption.

Plans are a neutral fixture representation for accounting. Their operation names
identify shared capabilities and do not specify a proposed AIN language. Each
condition receives these same implementations, operands and task records.
Publication/retry effects are deterministic simulations, with no external I/O.
"""
from __future__ import annotations

from copy import deepcopy
import inspect


def _integer(value, name, minimum=0, maximum=1_000_000):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer between {minimum} and {maximum}")
    return value


def filter_eq(rows, field, value):
    return [row for row in rows if row[field] == value]


def filter_gte(rows, field, value):
    return [row for row in rows if row[field] >= value]


def filter_lt(rows, field, value):
    return [row for row in rows if row[field] < value]


def filter_gt(rows, field, value):
    return [row for row in rows if row[field] > value]


def dedupe_by(rows, field):
    seen = set()
    result = []
    for row in rows:
        identity = row[field]
        if identity not in seen:
            seen.add(identity)
            result.append(row)
    return result


def group_sum(rows, key_field, value_field):
    totals = {}
    for row in rows:
        key = row[key_field]
        value = _integer(row[value_field], value_field, minimum=-1_000_000)
        totals[key] = totals.get(key, 0) + value
    return [{key_field: key, "total": totals[key]} for key in sorted(totals)]


def latest_by(rows, key_field, version_field):
    latest = {}
    for row in rows:
        key = row[key_field]
        version = _integer(row[version_field], version_field)
        if key not in latest or version > latest[key][version_field]:
            latest[key] = row
    return list(latest.values())


def sort_by(rows, field):
    return sorted(rows, key=lambda row: row[field])


def project(rows, fields):
    return [{field: row[field] for field in fields} for row in rows]


def bounded_retry(rows, limit, base_delay):
    """Simulate transient failures, bounded retries and successful commits."""
    _integer(limit, "limit", minimum=1, maximum=16)
    _integer(base_delay, "base_delay", minimum=1, maximum=1024)
    result = []
    for row in rows:
        failures = _integer(row["failures"], "failures")
        attempts = 0
        delays = []
        committed = False
        while attempts < limit:
            attempts += 1
            if attempts > failures:
                committed = True
                break
            if attempts < limit:
                delays.append(base_delay * 2 ** (attempts - 1))
        result.append({**row, "attempts": attempts, "delays": delays,
                       "committed": committed,
                       "status": "committed" if committed else "exhausted"})
    return result


CATALOG = {
    "filter_eq": {"args": ["field", "value"], "fn": filter_eq, "effect": "pure"},
    "filter_gte": {"args": ["field", "value"], "fn": filter_gte, "effect": "pure"},
    "filter_lt": {"args": ["field", "value"], "fn": filter_lt, "effect": "pure"},
    "filter_gt": {"args": ["field", "value"], "fn": filter_gt, "effect": "pure"},
    "dedupe_by": {"args": ["field"], "fn": dedupe_by, "effect": "pure"},
    "group_sum": {"args": ["key_field", "value_field"], "fn": group_sum, "effect": "pure"},
    "latest_by": {"args": ["key_field", "version_field"], "fn": latest_by, "effect": "pure"},
    "sort_by": {"args": ["field"], "fn": sort_by, "effect": "pure"},
    "project": {"args": ["fields"], "fn": project, "effect": "pure"},
    "bounded_retry": {"args": ["limit", "base_delay"], "fn": bounded_retry, "effect": "pure"},
}

CATALOG_SCHEMA = {name: tuple(record["args"]) for name, record in CATALOG.items()}


def catalog_sources():
    """Return approved implementation source, including the shared validator."""
    return {"_integer": inspect.getsource(_integer),
            **{name: inspect.getsource(record["fn"]) for name, record in CATALOG.items()}}


def execute(plan, task_data):
    """Execute a validated plan against a private copy of the task input."""
    if type(plan) is not list or not 1 <= len(plan) <= 24:
        raise ValueError("expected one to twenty-four approved operation calls")
    rows = deepcopy(task_data["records"])
    if type(rows) is not list or any(type(row) is not dict for row in rows):
        raise ValueError("records must be a list of ordinary objects")
    for instruction in plan:
        if type(instruction) is not dict or set(instruction) != {"op", "args"}:
            raise ValueError("each call requires op and args")
        name = instruction["op"]
        if type(name) is not str or name not in CATALOG:
            raise ValueError("unknown approved capability")
        record = CATALOG[name]
        arguments = instruction["args"]
        if type(arguments) is not dict or set(arguments) != set(record["args"]):
            raise ValueError(f"arguments do not match approved capability {name}")
        rows = record["fn"](rows, **arguments)
    return rows


def expected(task):
    """Independent fixture oracles, separate from the approved pipeline functions."""
    records = task["records"]
    parameters = task["parameters"]
    if task["domain"] == "events":
        totals = {}
        encountered = set()
        for row in records:
            if row["kind"] != "event" or row["id"] in encountered:
                continue
            encountered.add(row["id"])
            if row["severity"] >= parameters["minimum"] and row["timestamp"] < parameters["cutoff"]:
                totals[row["group"]] = totals.get(row["group"], 0) + row["value"]
        return [{"group": key, "total": value} for key, value in sorted(totals.items())]
    if task["domain"] == "cache":
        answer = []
        keys = sorted({row["key"] for row in records})
        for key in keys:
            candidates = [row for row in records if row["key"] == key]
            newest = max(row["version"] for row in candidates)
            winner = next(row for row in candidates if row["version"] == newest)
            if not winner["deleted"] and winner["expires"] > parameters["now"]:
                answer.append({field: winner[field] for field in ("key", "value", "version")})
        return answer
    if task["domain"] == "publication":
        first = {}
        for row in reversed(records):
            first[row["id"]] = row
        answer = []
        for identity in sorted(first):
            row = first[identity]
            if not row["enabled"]:
                continue
            success = row["failures"] < parameters["limit"]
            attempts = min(row["failures"] + 1, parameters["limit"])
            answer.append({"id": identity, "status": "committed" if success else "exhausted",
                           "attempts": attempts,
                           "delays": [parameters["base_delay"] * 2 ** i for i in range(attempts - 1)],
                           "committed": success})
        return answer
    raise ValueError("unknown task domain")


def _call(operation, **arguments):
    return {"op": operation, "args": arguments}


def _plan(domain, parameters):
    if domain == "events":
        return [_call("filter_eq", field="kind", value="event"),
                _call("dedupe_by", field="id"),
                _call("filter_gte", field="severity", value=parameters["minimum"]),
                _call("filter_lt", field="timestamp", value=parameters["cutoff"]),
                _call("group_sum", key_field="group", value_field="value")]
    if domain == "cache":
        return [_call("latest_by", key_field="key", version_field="version"),
                _call("filter_eq", field="deleted", value=False),
                _call("filter_gt", field="expires", value=parameters["now"]),
                _call("sort_by", field="key"),
                _call("project", fields=["key", "value", "version"])]
    return [_call("dedupe_by", field="id"),
            _call("filter_eq", field="enabled", value=True),
            _call("bounded_retry", limit=parameters["limit"], base_delay=parameters["base_delay"]),
            _call("sort_by", field="id"),
            _call("project", fields=["id", "status", "attempts", "delays", "committed"])]


def _records(domain, seed):
    if domain == "events":
        return [
            {"id": "control", "kind": "watermark", "group": "A", "severity": 9, "timestamp": 0, "value": 99},
            {"id": "duplicate", "kind": "event", "group": "A", "severity": 1, "timestamp": 1, "value": 7},
            {"id": "duplicate", "kind": "event", "group": "A", "severity": 4, "timestamp": 2, "value": 700},
            {"id": "a", "kind": "event", "group": "A", "severity": 2, "timestamp": 3, "value": 10 + seed},
            {"id": "b", "kind": "event", "group": "A", "severity": 3, "timestamp": 4, "value": -2},
            {"id": "c", "kind": "event", "group": "B", "severity": 4, "timestamp": 5, "value": 20 + seed},
            {"id": "boundary", "kind": "event", "group": "B", "severity": 9, "timestamp": 20 + seed, "value": 100},
            {"id": "future", "kind": "event", "group": "B", "severity": 9, "timestamp": 30 + seed, "value": 1000},
        ]
    if domain == "cache":
        return [
            {"key": "alpha", "version": 1, "value": "old", "deleted": False, "expires": 100},
            {"key": "alpha", "version": 2, "value": f"new-{seed}", "deleted": False, "expires": 14 + seed},
            {"key": "beta", "version": 1, "value": "original", "deleted": False, "expires": 100},
            {"key": "beta", "version": 3, "value": "removed", "deleted": True, "expires": 100},
            {"key": "beta", "version": 2, "value": "stale", "deleted": False, "expires": 100},
            {"key": "gamma", "version": 4, "value": "boundary", "deleted": False, "expires": 10 + seed},
            {"key": "delta", "version": 7, "value": "first", "deleted": False, "expires": 100},
            {"key": "delta", "version": 7, "value": "second", "deleted": False, "expires": 100},
        ]
    return [
        {"id": "a", "enabled": True, "failures": 0},
        {"id": "a", "enabled": True, "failures": 9},
        {"id": "b", "enabled": True, "failures": 1},
        {"id": "c", "enabled": True, "failures": 3},
        {"id": "d", "enabled": True, "failures": 9},
        {"id": "disabled", "enabled": False, "failures": 0},
        {"id": "disabled", "enabled": True, "failures": 0},
        {"id": f"extra-{seed}", "enabled": True, "failures": 2},
    ]


def make_chains():
    """Return 18 matched four-stage workflow chains, totaling 72 episodes."""
    chains = []
    for domain in ("events", "cache", "publication"):
        for seed in range(6):
            if domain == "events":
                original = {"minimum": 2, "cutoff": 20 + seed}
                changed = {**original, "minimum": 3}
            elif domain == "cache":
                original = {"now": 10 + seed}
                changed = {"now": 15 + seed}
            else:
                original = {"limit": 3, "base_delay": 1 + seed}
                changed = {**original, "limit": 4}
            stages = []
            for stage in ("build", "change", "repair", "handoff"):
                parameters = original if stage == "build" else changed
                task = {"domain": domain, "parameters": deepcopy(parameters),
                        "records": _records(domain, seed)}
                plan = _plan(domain, parameters)
                record = {"stage": stage, "plan": plan, "task": task,
                          "requirements": f"{domain} workflow with parameters {parameters!r}",
                          "memory": {"domain": domain, "parameters": deepcopy(parameters)}}
                if stage == "repair":
                    broken = deepcopy(plan)
                    if domain == "events":
                        broken[3]["op"] = "filter_gte"
                    elif domain == "cache":
                        broken[1]["args"]["value"] = True
                    else:
                        broken[2]["args"]["limit"] = 1
                    record["broken_plan"] = broken
                stages.append(record)
            chains.append({"id": f"{domain}-{seed:02d}", "domain": domain, "stages": stages})
    return chains
