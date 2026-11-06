"""Execute matched approved-core workflows and account for ideal fluent agents."""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from experiments.approved_workflow_theory.accounting import count_call_stream, count_ideal, text_token_count
from experiments.approved_workflow_theory.workloads import CATALOG_SCHEMA, catalog_sources, execute, expected, make_chains

PROFILES = ("python", "python_aliases", "ideal_ain", "ideal_ir", "ideal_python")
TOOLS = {"record": ("value",), "write": ("program",),
         "patch": ("index", "kind", "key", "value"), "check": (),
         "remember": ("value",), "submit": ()}
SCHEMA = {**CATALOG_SCHEMA, **TOOLS}
ALIASES = {name: chr(97 + index) for index, name in enumerate(sorted(SCHEMA))}
DOMAIN_RULES = {
    "events": "Keep event records. Reserve the first occurrence of each id before severity filtering. "
              "Keep severity >= minimum and timestamp < cutoff. Sum value by group in key order.",
    "cache": "Select the highest version per key, keeping the first tie. Then exclude deleted "
             "and expired entries (expires must be > now). Return key,value,version in key order.",
    "publication": "Keep the first occurrence of each id before enabled filtering. Retry enabled "
                   "records up to limit attempts with exponential base_delay. Return id,status,"
                   "attempts,delays,committed in id order. Effects are simulated.",
}
# Public interface vocabulary is frozen independently of generated task values.
STATIC = set(SCHEMA) | set(TOOLS) | {
    "domain", "parameters", "stage", "artifact", "passed", "stored", "submitted",
    "checks_passed", "field", "value", "key_field", "value_field", "version_field", "fields",
    "limit", "base_delay", "minimum", "cutoff", "now", "index", "kind", "key", "op", "arg",
    "events", "cache", "publication", "build", "change", "repair", "handoff", "p",
    "event", "id", "severity", "timestamp", "group", "total", "version", "deleted", "expires",
    "enabled", "failures", "status", "attempts", "delays", "committed",
}
CONFIG = {"assumed_approved_core": True, "assumed_fluent_representation": True,
          "assumed_perfect_composer": True, "model_calls": 0, "vocabulary_entries": 65536,
          "literal_payload_bits": 15, "turns_per_stage": 3,
          "shared_request_framing": 4, "history_pair_framing": 3, "response_end": 1,
          "data_schedules": ["resident", "inspect"], "stages": ["build", "change", "repair", "handoff"],
          "catalog_schema": SCHEMA, "static_symbols": sorted(STATIC), "aliases": ALIASES}


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def python_program(plan, aliases=False):
    expression = "r"
    for call in plan:
        name = ALIASES[call["op"]] if aliases else call["op"]
        arguments = [repr(call["args"][key]) for key in CATALOG_SCHEMA[call["op"]]]
        expression = f"{name}({','.join([expression] + arguments)})"
    return "lambda r:" + expression


def parse_python_program(source, aliases=False):
    """Validate generated fixture source without eval or exec."""
    expression = ast.parse(source, mode="eval").body
    if not isinstance(expression, ast.Lambda) or len(expression.args.args) != 1:
        raise ValueError("Expected a one-argument lambda fixture")
    inverse = {value: key for key, value in ALIASES.items()} if aliases else {name: name for name in CATALOG_SCHEMA}
    plan = []

    def visit(node):
        if isinstance(node, ast.Name) and node.id == "r":
            return
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.keywords:
            raise ValueError("Expected calls to approved functions")
        name = inverse[node.func.id]
        fields = CATALOG_SCHEMA[name]
        if len(node.args) != len(fields) + 1:
            raise ValueError("Fixture argument count mismatch")
        visit(node.args[0])
        plan.append({"op": name, "args": {key: ast.literal_eval(value)
                                          for key, value in zip(fields, node.args[1:], strict=True)}})

    visit(expression.body)
    return plan


def action_units(actions):
    total = 1  # Bounded sequence length, then known-arity instructions.
    for action in actions:
        name = action["op"]
        if name == "write":
            total += 1 + count_call_stream(action["args"]["program"], STATIC, CATALOG_SCHEMA)["units"]
        else:
            total += count_call_stream([action], STATIC, TOOLS)["units"] - 1
    return total


def python_actions(actions, aliases=False):
    statements = []
    for action in actions:
        name = ALIASES[action["op"]] if aliases else action["op"]
        if action["op"] == "write":
            arguments = [python_program(action["args"]["program"], aliases)]
        else:
            arguments = [repr(action["args"][key]) for key in TOOLS[action["op"]]]
        statements.append(f"{name}({','.join(arguments)})")
    return ";".join(statements)


def patch_for(before, after):
    changes = []
    for index, (old, new) in enumerate(zip(before, after, strict=True)):
        if old["op"] != new["op"]:
            changes.append({"index": index, "kind": "op", "key": None, "value": new["op"]})
        for key, value in new["args"].items():
            if old["args"].get(key) != value:
                changes.append({"index": index, "kind": "arg", "key": key, "value": value})
    return changes


def call(name, **args):
    return {"op": name, "args": args}


def episode(chain, stage, predecessor, memory, schedule):
    target = stage["plan"]
    current = deepcopy(stage.get("broken_plan", predecessor))
    old = deepcopy(current)
    work = {"domain": chain["domain"], "parameters": stage["task"]["parameters"],
            "stage": stage["stage"]}
    persisted = {"domain": chain["domain"], "parameters": stage["task"]["parameters"],
                 "artifact": "p", "checks_passed": True}
    first = [call("record", value=work)]
    if stage["stage"] == "build":
        first.append(call("write", program=target))
    else:
        first.extend(call("patch", **patch) for patch in patch_for(current, target))
    turns = [first, [call("check")], [call("remember", value=persisted), call("submit")]]
    observations = []
    working_records = []
    stored_memory = deepcopy(memory)
    execution_seconds = 0.0
    checked = False
    for actions in turns:
        for action in actions:
            args = action["args"]
            if action["op"] == "record":
                working_records.append(deepcopy(args["value"]))
            elif action["op"] == "remember":
                stored_memory = deepcopy(args["value"])
            elif action["op"] == "write":
                current = deepcopy(args["program"])
            elif action["op"] == "patch":
                if args["kind"] == "op":
                    current[args["index"]]["op"] = args["value"]
                else:
                    current[args["index"]]["args"][args["key"]] = args["value"]
            elif action["op"] == "check":
                started = time.perf_counter()
                actual = execute(current, stage["task"])
                checked = actual == expected(stage["task"])
                execution_seconds += time.perf_counter() - started
                if not checked:
                    raise ValueError("Oracle composition failed execution")
            elif action["op"] == "submit":
                if not checked or stored_memory != persisted:
                    raise ValueError("Submission requires checked execution and persisted memory")
        observations.append({"passed": True} if actions[0]["op"] == "check"
                            else {"submitted": True} if actions[-1]["op"] == "submit"
                            else {"stored": True})
    for aliases in (False, True):
        restored = parse_python_program(python_program(current, aliases), aliases)
        if restored != current or execute(restored, stage["task"]) != expected(stage["task"]):
            raise ValueError("Python rendering differs from the common semantics")
    common = {"requirements": DOMAIN_RULES[chain["domain"]], "stage": stage["stage"],
              "parameters": stage["task"]["parameters"], "data_handle": "records",
              "schema": sorted(stage["task"]["records"][0])}
    if schedule == "inspect":
        common["records"] = stage["task"]["records"]
    common_text = json.dumps(common, separators=(",", ":"))
    common_tokens = text_token_count(common_text)
    ledger = []
    for profile in PROFILES:
        native = profile.startswith("ideal_")
        aliases = profile == "python_aliases"
        artifact_cost = (count_call_stream(old, STATIC, CATALOG_SCHEMA)["units"] if native and old
                         else text_token_count(python_program(old, aliases)) if old else 0)
        memory_cost = (count_ideal(memory, STATIC)["units"] if native and memory
                       else text_token_count(repr(memory)) if memory else 0)
        history = 0
        for index, actions in enumerate(turns):
            response = action_units(actions) if native else text_token_count(python_actions(actions, aliases))
            observation = (count_ideal(observations[index], STATIC)["units"] if native
                           else text_token_count(repr(observations[index])))
            ledger.append({"profile": profile, "turn": index + 1,
                           "common_input_text_tokens": common_tokens,
                           "artifact_input_units": artifact_cost, "memory_input_units": memory_cost,
                           "reprocessed_history_units": history,
                           "shared_framing_positions": 4 + 3 * index,
                           "input_positions": common_tokens + artifact_cost + memory_cost + history + 4 + 3 * index,
                           "authored_content_units": response,
                           "output_positions": response + 1, "host_observation_units": observation})
            history += response + 1 + observation
    return {"chain": chain["id"], "domain": chain["domain"], "stage": stage["stage"],
            "schedule": schedule, "success": checked, "actions": turns,
            "host_observations": observations, "common_input": common,
            "predecessor": old, "incoming_memory": memory, "outgoing_memory": stored_memory,
            "working_records": working_records,
            "artifact": current, "python_program": python_program(current),
            "python_alias_program": python_program(current, True),
            "artifact_ideal_units": count_call_stream(current, STATIC, CATALOG_SCHEMA),
            "execution_seconds": execution_seconds,
            "host_business_data_bytes": len(json.dumps(stage["task"]["records"]).encode()),
            "ledger": ledger}, current, stored_memory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).parent / "results/approved-core-2026-11-06")
    args = parser.parse_args()
    if (args.output / "manifest.json").exists():
        raise ValueError("Choose a fresh directory to preserve earlier measurements")
    chains = make_chains()
    sources = [Path(__file__).with_name(name) for name in ("run.py", "workloads.py", "accounting.py")]
    manifest = {"config": CONFIG,
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                "fixture_sha256": hashlib.sha256(json.dumps(chains, sort_keys=True).encode()).hexdigest(),
                "packages": {name: importlib.metadata.version(name) for name in ("transformers", "tokenizers")},
                "conditions": "Conditional oracle traces under approved-core, fluent-language and perfect-composer assumptions"}
    save(args.output / "manifest.json", manifest)
    save(args.output / "fixtures.json", chains)
    save(args.output / "approved_core_sources.json", catalog_sources())
    episodes = []
    totals = {}
    for schedule in CONFIG["data_schedules"]:
        aggregate = {profile: defaultdict(int) for profile in PROFILES}
        for chain in chains:
            previous, memory = [], {}
            for stage in chain["stages"]:
                record, previous, memory = episode(chain, stage, previous, memory, schedule)
                episodes.append(record)
                for row in record["ledger"]:
                    result = aggregate[row["profile"]]
                    for key, value in row.items():
                        if key not in ("profile", "turn"):
                            result[key] += value
        totals[schedule] = {profile: dict(values) for profile, values in aggregate.items()}
    save(args.output / "episodes.json", episodes)
    save(args.output / "totals.json", totals)
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
