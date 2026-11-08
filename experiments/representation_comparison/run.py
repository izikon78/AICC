"""Matched CPU representation test over frozen correct workflow traces."""
from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from copy import deepcopy
import csv
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.approved_workflow_theory.accounting import MODEL, REVISION, text_token_count
from experiments.approved_workflow_theory.run import ALIASES, CATALOG_SCHEMA, TOOLS, SCHEMA
from experiments.approved_workflow_theory.workloads import execute, expected

HERE = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/approved_workflow_theory/trace-inputs.json"
PROFILES = ("python_repr", "python_compact", "readable_ir", "numeric_arrays", "symbolic_ain")
IDS = {name: index + 1 for index, name in enumerate(sorted(SCHEMA))}
BY_ID = {value: name for name, value in IDS.items()}
BY_ALIAS = {value: name for name, value in ALIASES.items()}


def dumps(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equal(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def py_literal(value, compact):
    if not compact:
        return repr(value)
    if type(value) is list:
        return "[" + ",".join(py_literal(x, True) for x in value) + "]"
    if type(value) is dict:
        return "{" + ",".join(repr(k) + ":" + py_literal(v, True) for k, v in value.items()) + "}"
    return repr(value)


def checked_call(name, values, schema):
    if name not in schema or type(values) is not list or len(values) != len(schema[name]):
        raise ValueError("Unknown operation or incorrect approved arity")
    return {"op": name, "args": dict(zip(schema[name], values, strict=True))}


def arrays(calls, numeric, actions=False):
    schema = TOOLS if actions else CATALOG_SCHEMA
    rows = []
    for call in calls:
        name, args = call["op"], call["args"]
        if name not in schema or set(args) != set(schema[name]):
            raise ValueError("Call differs from the approved schema")
        values = [arrays(args[k], numeric) if actions and name == "write" and k == "program" else args[k]
                  for k in schema[name]]
        rows.append([IDS[name] if numeric else name, *values])
    return rows


def from_arrays(rows, numeric, actions=False):
    if type(rows) is not list:
        raise ValueError("Expected a call list")
    schema = TOOLS if actions else CATALOG_SCHEMA
    result = []
    for row in rows:
        if type(row) is not list or not row:
            raise ValueError("Expected a nonempty instruction array")
        name = BY_ID.get(row[0]) if numeric and type(row[0]) is int else row[0] if not numeric and type(row[0]) is str else None
        call = checked_call(name, row[1:], schema)
        if actions and name == "write":
            call["args"]["program"] = from_arrays(call["args"]["program"], numeric)
        result.append(call)
    return result


def program(plan, profile):
    if profile in ("readable_ir", "numeric_arrays"):
        return dumps(arrays(plan, profile == "numeric_arrays"))
    if profile == "symbolic_ain":
        body = "".join("r=!" + str(IDS[c["op"]]) + "(r" +
                       "".join("," + dumps(c["args"][k]) for k in CATALOG_SCHEMA[c["op"]]) + ");" for c in plan)
        return "@0(r){" + body + "^[r];}"
    expression = "r"
    for call in plan:
        values = [py_literal(call["args"][k], profile == "python_compact") for k in CATALOG_SCHEMA[call["op"]]]
        expression = ALIASES[call["op"]] + "(" + ",".join([expression, *values]) + ")"
    return "lambda r:" + expression


class SymbolicReader:
    """Read only the declared reversible call-stream sketch, not general AIN."""
    def __init__(self, source):
        self.source, self.index = source, 0

    def take(self, token):
        if not self.source.startswith(token, self.index):
            raise ValueError("Unexpected symbolic token")
        self.index += len(token)

    def literal(self):
        value, used = json.JSONDecoder().raw_decode(self.source[self.index:])
        self.index += used
        return value

    def call(self, schema, with_rows=False):
        self.take("!")
        match = re.match(r"[0-9]+", self.source[self.index:])
        if match is None:
            raise ValueError("Missing operation identifier")
        self.index += len(match[0])
        name = BY_ID.get(int(match[0]))
        if name not in schema:
            raise ValueError("Unknown operation identifier")
        self.take("(")
        if with_rows:
            self.take("r")
        values = []
        for i, key in enumerate(schema[name]):
            if with_rows or i:
                self.take(",")
            values.append(self.plan() if name == "write" and key == "program" else self.literal())
        self.take(");")
        return checked_call(name, values, schema)

    def plan(self):
        self.take("@0(r){")
        result = []
        while self.source.startswith("r=", self.index):
            self.take("r=")
            result.append(self.call(CATALOG_SCHEMA, True))
        self.take("^[r];}")
        return result

    def done(self):
        if self.index != len(self.source):
            raise ValueError("Trailing symbolic content")


def python_plan(node):
    if (not isinstance(node, ast.Lambda) or len(node.args.args) != 1
            or node.args.args[0].arg != "r" or node.args.posonlyargs or node.args.kwonlyargs
            or node.args.vararg or node.args.kwarg or node.args.defaults):
        raise ValueError("Expected a plain one-argument lambda")
    result = []

    def visit(child):
        if isinstance(child, ast.Name) and child.id == "r":
            return
        if not isinstance(child, ast.Call) or not isinstance(child.func, ast.Name) or child.keywords:
            raise ValueError("Only approved positional calls are admitted")
        name = BY_ALIAS.get(child.func.id)
        if name not in CATALOG_SCHEMA or len(child.args) != len(CATALOG_SCHEMA[name]) + 1:
            raise ValueError("Unknown approved call or arity")
        visit(child.args[0])
        result.append(checked_call(name, [ast.literal_eval(x) for x in child.args[1:]], CATALOG_SCHEMA))
    visit(node.body)
    return result


def decode_program(text, profile):
    if profile in ("readable_ir", "numeric_arrays"):
        return from_arrays(json.loads(text), profile == "numeric_arrays")
    if profile == "symbolic_ain":
        reader = SymbolicReader(text)
        result = reader.plan()
        reader.done()
        return result
    return python_plan(ast.parse(text, mode="eval").body)


def actions_text(actions, profile):
    if profile in ("readable_ir", "numeric_arrays"):
        return dumps(arrays(actions, profile == "numeric_arrays", True))
    statements = []
    for action in actions:
        name = action["op"]
        values = [program(action["args"][k], profile) if name == "write" and k == "program"
                  else dumps(action["args"][k]) if profile == "symbolic_ain"
                  else py_literal(action["args"][k], profile == "python_compact") for k in TOOLS[name]]
        label = "!" + str(IDS[name]) if profile == "symbolic_ain" else ALIASES[name]
        statements.append(label + "(" + ",".join(values) + ")")
    return ";".join(statements) + (";" if profile == "symbolic_ain" else "")


def decode_actions(text, profile):
    if profile in ("readable_ir", "numeric_arrays"):
        return from_arrays(json.loads(text), profile == "numeric_arrays", True)
    if profile == "symbolic_ain":
        reader = SymbolicReader(text)
        result = []
        while reader.index < len(text):
            result.append(reader.call(TOOLS))
        return result
    result = []
    for statement in ast.parse(text, mode="exec").body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            raise ValueError("Only call expressions are admitted")
        node = statement.value
        if not isinstance(node.func, ast.Name) or node.keywords:
            raise ValueError("Only approved positional tools are admitted")
        name = BY_ALIAS.get(node.func.id)
        values = [python_plan(x) if name == "write" else ast.literal_eval(x) for x in node.args]
        result.append(checked_call(name, values, TOOLS))
    return result


def state_text(value, profile):
    return repr(value) if profile == "python_repr" else dumps(value)


def decode_state(text, profile):
    return ast.literal_eval(text) if profile == "python_repr" else json.loads(text)


def replay(episode, batches, task):
    current, memory = deepcopy(episode["predecessor"]), deepcopy(episode["incoming_memory"])
    records, checked = [], False
    for actions in batches:
        for action in actions:
            name, args = action["op"], action["args"]
            if name == "record": records.append(deepcopy(args["value"]))
            elif name == "write": current = deepcopy(args["program"])
            elif name == "patch":
                if args["kind"] == "op": current[args["index"]]["op"] = args["value"]
                elif args["kind"] == "arg": current[args["index"]]["args"][args["key"]] = args["value"]
                else: raise ValueError("Invalid patch kind")
            elif name == "check":
                checked = equal(execute(current, task), expected(task))
                if not checked: raise ValueError("Decoded computation fails independent fixture oracle")
            elif name == "remember": memory = deepcopy(args["value"])
            elif name == "submit" and not checked: raise ValueError("Unchecked submission")
    if not (checked and equal(current, episode["artifact"]) and equal(memory, episode["outgoing_memory"])
            and equal(records, episode["working_records"])):
        raise ValueError("Decoded stage does not preserve artifact/state")


def probes():
    values = ["new-field", "用户🧪", "x" * 2048, 'a;^[r];}!5(\"', -16385, 16384, True, None, [1, "é", False]]
    results = []
    for profile in PROFILES:
        for index, value in enumerate(values):
            plan = [{"op": "filter_eq", "args": {"field": "unknown_field", "value": value}}]
            artifact = program(plan, profile)
            if not equal(plan, decode_program(artifact, profile)):
                raise ValueError("New literal roundtrip failed")
            if not equal(value, decode_state(state_text(value, profile), profile)):
                raise ValueError("State roundtrip failed")
            results.append({"profile": profile, "case": index, "roundtrip": True,
                            "program_text_tokens": text_token_count(artifact)})
        before = [{"seen": ["a"], "last_output": []}, {"seen": [], "last_output": []}]
        restored = [decode_state(state_text(x, profile), profile) for x in before]
        decisions = ["reject" if "a" in x["seen"] else "accept" for x in restored]
        if decisions != ["reject", "accept"]: raise ValueError("Handoff loses continuation state")
        results.append({"profile": profile, "case": "continuation_state", "roundtrip": True,
                        "next_decisions": decisions, "state_free_records_collide": True})
    return results


def run(output):
    if output.exists():
        raise FileExistsError("Preserve prior observations; choose a fresh output directory")
    output.mkdir(parents=True)
    frozen = [HERE / n for n in ("PROTOCOL.md", "run.py", "test_comparison.py")]
    frozen += [ROOT / "experiments/approved_workflow_theory" / n
               for n in ("trace-inputs.json", "accounting.py", "run.py", "workloads.py")]
    manifest = {"protocol": 1, "model_calls": 0, "training_runs": 0,
                "tokenizer": {"model": MODEL, "revision": REVISION}, "profiles": list(PROFILES),
                "operation_ids": IDS, "source_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in frozen},
                "packages": {n: importlib.metadata.version(n) for n in ("transformers", "tokenizers")},
                "context": "Complete literal fixture requests; no model chat template or special tokens",
                "external_systems_executed": [], "supplied_correct_compositions": True}
    save(output / "manifest.json", manifest)
    source = json.loads(TRACE.read_text(encoding="utf-8"))
    tasks = {(chain["id"], s["stage"]): s["task"] for chain in source["fixtures"] for s in chain["stages"]}
    totals, checks, ledger = {}, [], []
    for episode in source["episodes"]:
        common = json.dumps(episode["common_input"], separators=(",", ":"))
        for profile in PROFILES:
            predecessor = program(episode["predecessor"], profile) if episode["predecessor"] else ""
            memory = state_text(episode["incoming_memory"], profile) if episode["incoming_memory"] else ""
            if predecessor and not equal(decode_program(predecessor, profile), episode["predecessor"]):
                raise ValueError("Predecessor roundtrip failed")
            if memory and not equal(decode_state(memory, profile), episode["incoming_memory"]):
                raise ValueError("Incoming memory roundtrip failed")
            batches = []
            history = ""
            aggregate = totals.setdefault(episode["schedule"], {}).setdefault(profile, defaultdict(int))
            for turn, batch in enumerate(episode["actions"]):
                response = actions_text(batch, profile)
                decoded = decode_actions(response, profile)
                if not equal(decoded, batch): raise ValueError("Action roundtrip changes semantic input")
                batches.append(decoded)
                observation = state_text(episode["host_observations"][turn], profile)
                if not equal(decode_state(observation, profile), episode["host_observations"][turn]):
                    raise ValueError("Observation roundtrip failed")
                context = common + "\nA:\n" + predecessor + "\nM:\n" + memory + "\nH:\n" + history
                row = {"chain": episode["chain"], "stage": episode["stage"], "schedule": episode["schedule"],
                       "profile": profile, "turn": turn + 1, "input_text_tokens": text_token_count(context),
                       "output_text_tokens": text_token_count(response), "input_utf8_bytes": len(context.encode()),
                       "output_utf8_bytes": len(response.encode()),
                       "common_tokens_isolated": text_token_count(common),
                       "artifact_tokens_isolated": text_token_count(predecessor),
                       "memory_tokens_isolated": text_token_count(memory),
                       "history_tokens_isolated": text_token_count(history),
                       "request_text": context, "response_text": response, "observation_text": observation}
                row["total_text_tokens"] = row["input_text_tokens"] + row["output_text_tokens"]
                row["wrapper_and_boundary_delta"] = row["input_text_tokens"] - sum(row[k] for k in
                        ("common_tokens_isolated", "artifact_tokens_isolated", "memory_tokens_isolated", "history_tokens_isolated"))
                for key, value in row.items():
                    if type(value) is int and key != "turn": aggregate[key] += value
                ledger.append(row)
                history += "X:\n" + response + "\nO:\n" + observation + "\n"
            replay(episode, batches, tasks[(episode["chain"], episode["stage"])])
            checks.append({"chain": episode["chain"], "stage": episode["stage"], "schedule": episode["schedule"],
                           "profile": profile, "decoded_execution_and_state_match": True})
    literal_probes = probes()
    save(output / "ledger.json", ledger)
    save(output / "stage-checks.json", checks)
    save(output / "probes.json", literal_probes)
    save(output / "totals.json", totals)
    with (output / "totals.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["schedule", "profile", *next(iter(totals["resident"].values())).keys()]
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        for schedule, profiles in totals.items():
            for profile, values in profiles.items(): writer.writerow({"schedule": schedule, "profile": profile, **values})
    summary = {"episodes": len(source["episodes"]), "profiles": len(PROFILES), "request_rows": len(ledger),
               "decoded_stage_checks_passed": len(checks), "separate_probes_passed": len(literal_probes),
               "model_calls": 0, "external_systems_executed": [], "all_stage_checks_passed": True}
    save(output / "summary.json", summary)
    if any(sha(ROOT / name) != digest for name, digest in manifest["source_sha256"].items()):
        raise ValueError("Frozen source/input changed during measurement")
    print(dumps({"summary": summary, "totals": totals}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "results/comparison-v1")
    run(parser.parse_args().output)
