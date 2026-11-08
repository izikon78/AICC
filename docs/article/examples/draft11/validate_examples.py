"""Inspect article sketches and check declared contracts with deterministic mocks.

This helper checks isolated call sites. It supplies no AIN parser or compiler.
It performs no database/network access and starts no operating-system threads.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


DIRECTORY = Path(__file__).resolve().parent


def check_structure(package):
    catalog_ids = set()
    functions = set()
    checks = []
    for example in package["examples"]:
        signature = re.search(r"@(\d+)\(([^)]*)\)\s*\{", example["ain"])
        if signature is None or int(signature[1]) in functions:
            raise ValueError("Missing or duplicate example function identifier")
        functions.add(int(signature[1]))
        catalog = {item["id"]: item for item in example["catalog"]}
        if len(catalog) != len(example["catalog"]) or set(catalog) & catalog_ids:
            raise ValueError("Catalog operation identifiers must be unique")
        catalog_ids.update(catalog)
        observed = []
        for match in re.finditer(r"!(\d+)\(([^\n;]*)\)", example["ain"]):
            identifier = int(match[1])
            if identifier not in catalog:
                raise ValueError(f"Undeclared operation {identifier}")
            arguments = ast.parse("operation(" + match[2] + ")", mode="eval").body
            if not isinstance(arguments, ast.Call) or arguments.keywords:
                raise ValueError("Expected positional example arguments")
            if len(arguments.args) != catalog[identifier]["arity"]:
                raise ValueError(f"Wrong argument count for operation {identifier}")
            if catalog[identifier]["arity"] != len(catalog[identifier]["parameters"]):
                raise ValueError("Catalog arity and parameter list differ")
            observed.append(identifier)
        if observed != example["expected_call_ids"] or set(observed) != set(catalog):
            raise ValueError("Displayed call sequence differs from the catalog contract")
        if "^[" not in example["ain"] or not example["ain"].strip().endswith("}"):
            raise ValueError("Expected a function return bundle and closing block")
        if len(example["source"].splitlines()) > 12 or len(example["ain"].splitlines()) > 8:
            raise ValueError("Print example exceeds the agreed line budget")
        checks.append({"example": example["id"], "passed": True,
                       "function_id": int(signature[1]), "call_ids": observed,
                       "source_lines": len(example["source"].splitlines()),
                       "ain_lines": len(example["ain"].splitlines())})
    return checks


class MockScope:
    """Model the declared owned-resource cleanup contract."""

    def __init__(self):
        self.resources = []
        self.events = []

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        for resource in reversed(self.resources):
            if resource["live"]:
                if resource["kind"] == "worker":
                    self.events.append(["stop", resource["reference"]])
                self.close(resource)
        return False

    def own(self, kind, reference):
        resource = {"kind": kind, "reference": reference, "live": True}
        self.resources.append(resource)
        self.events.append(["open", kind, reference])
        return resource

    def close(self, resource):
        if not resource["live"]:
            raise ValueError("Resource already released")
        resource["live"] = False
        label = "join" if resource["kind"] == "worker" else "close"
        self.events.append([label, resource["reference"]])


def database_case(fault=None):
    scope = MockScope()
    rows = [{"Id": 1, "Name": "Ada"}, {"Id": 2, "Name": None}]
    actual = None
    error = None
    try:
        with scope:
            database = scope.own("database", "db")
            if fault == "connect":
                raise RuntimeError("simulated connection failure")
            scope.events.append(["query", "SELECT * FROM Users"])
            if fault == "query":
                raise RuntimeError("simulated query failure")
            actual = deepcopy(rows)
            scope.close(database)
    except RuntimeError as failure:
        error = str(failure)
    assert all(not item["live"] for item in scope.resources)
    assert scope.events.count(["close", "db"]) == 1
    assert (actual == rows and actual is not rows) if fault is None else error is not None
    return scope.events


def http_case(payload=b'[{"id":1,"name":"Ada"}]', fault=None):
    scope = MockScope()
    actual = None
    error = None
    try:
        with scope:
            response = scope.own("http", "response")
            scope.events.append(["get", "https://example.test/users", 10])
            if fault == "open":
                raise RuntimeError("simulated HTTP failure")
            actual = json.loads(payload.decode("utf-8"))
            scope.close(response)
    except (RuntimeError, UnicodeDecodeError, json.JSONDecodeError) as failure:
        error = type(failure).__name__
    assert all(not item["live"] for item in scope.resources)
    assert scope.events.count(["close", "response"]) == 1
    if fault is None:
        assert actual == [{"id": 1, "name": "Ada"}]
    else:
        assert error is not None
    return scope.events


def thread_case(fail_second=False):
    scope = MockScope()
    error = None
    try:
        with scope:
            first = scope.own("worker", 1)
            if fail_second:
                raise RuntimeError("simulated second spawn failure")
            second = scope.own("worker", 2)
            # Reverse completion is allowed while the explicit joins stay ordered.
            scope.events.extend([["completed", 2, 9], ["completed", 1, 7]])
            scope.close(first)
            scope.close(second)
    except RuntimeError as failure:
        error = str(failure)
    assert all(not item["live"] for item in scope.resources)
    if fail_second:
        assert error is not None
        assert scope.events[-2:] == [["stop", 1], ["join", 1]]
    else:
        assert scope.events[-2:] == [["join", 1], ["join", 2]]
        assert [event[1] for event in scope.events if event[0] == "completed"] == [2, 1]
    return scope.events


def paid_totals(rows):
    totals = {}
    for row in rows:
        assert type(row["paid"]) is bool
        assert type(row["amount_cents"]) is int
        assert row["customer"].isascii()
        if row["paid"]:
            totals[row["customer"]] = totals.get(row["customer"], 0) + row["amount_cents"]
    return dict(sorted(totals.items()))


def active_emails(rows):
    values = []
    for row in rows:
        assert type(row["active"]) is bool
        assert type(row["email"]) is str and row["email"].isascii()
        if row["active"] and row["email"] not in values:
            values.append(row["email"])
    return tuple(sorted(values))


def contract_scenarios():
    scenarios = []
    for fault in (None, "connect", "query"):
        events = database_case(fault)
        scenarios.append({"case": "database_" + (fault or "success"), "passed": True, "events": events})
    for name, payload, fault in (
        ("success", b'[{"id":1,"name":"Ada"}]', None),
        ("bad_json", b"{", "parse"),
        ("bad_utf8", b"\xff", "decode"),
        ("open_error", b"[]", "open"),
    ):
        scenarios.append({"case": "http_" + name, "passed": True,
                          "events": http_case(payload, fault)})
    for failure in (False, True):
        scenarios.append({"case": "threads_second_spawn_failure" if failure else "threads_reverse_completion",
                          "passed": True, "events": thread_case(failure)})
    rows = [{"paid": True, "customer": "B", "amount_cents": 200},
            {"paid": False, "customer": "A", "amount_cents": 999},
            {"paid": True, "customer": "A", "amount_cents": 150},
            {"paid": True, "customer": "A", "amount_cents": -50},
            {"paid": True, "customer": "B", "amount_cents": 2**70}]
    actual = paid_totals(rows)
    assert list(actual.items()) == [("A", 100), ("B", 200 + 2**70)]
    scenarios.append({"case": "ruby_paid_refunds_and_exact_large_integers", "passed": True,
                      "result": list(actual.items())})
    assert paid_totals([]) == {}
    scenarios.append({"case": "ruby_empty_input", "passed": True})
    emails = [{"active": True, "email": "b@example.test"},
              {"active": False, "email": "hidden@example.test"},
              {"active": True, "email": "A@example.test"},
              {"active": True, "email": "b@example.test"},
              {"active": True, "email": "a@example.test"}]
    actual = active_emails(emails)
    assert actual == ("A@example.test", "a@example.test", "b@example.test")
    scenarios.append({"case": "java_active_distinct_ascii_order", "passed": True, "result": actual})
    assert active_emails([]) == ()
    scenarios.append({"case": "java_empty_input", "passed": True})
    return scenarios


def main():
    source = DIRECTORY / "examples.json"
    package = json.loads(source.read_text(encoding="utf-8"))
    structural = check_structure(package)
    scenarios = contract_scenarios()
    result = {
        "examples_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "examples": len(structural), "unique_catalog_operations": sum(len(e["catalog"]) for e in package["examples"]),
        "structural_checks_passed": all(item["passed"] for item in structural),
        "mock_contract_scenarios": len(scenarios),
        "mock_contract_scenarios_passed": sum(item["passed"] for item in scenarios),
        "actual_ain_compiler_runs": 0, "actual_database_connections": 0,
        "actual_http_requests": 0, "actual_os_threads_started": 0,
        "source_compiler_execution": "Documentary source reviewed against API contracts, without running these five language toolchains",
        "structure": structural, "scenarios": scenarios,
    }
    (DIRECTORY / "validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key not in ("structure", "scenarios")}, indent=2))


if __name__ == "__main__":
    main()
