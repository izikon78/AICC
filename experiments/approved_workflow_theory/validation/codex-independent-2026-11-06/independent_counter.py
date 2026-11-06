"""Independent REPLICATION_SPEC v1 implementation; no reference imports.

Written before consulting reference counts, ledgers or accounting code.
Only workloads.py approved implementations/oracles are reused for execution.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "experiments" / "approved_workflow_theory"
sys.path.insert(0, str(PACKAGE))
import workloads  # Explicitly permitted execution components and fixture oracles.

PROFILES = ("python", "python_aliases", "ideal_ain", "ideal_ir", "ideal_python")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


class IndependentCounter:
    def __init__(self, configuration, tokenizer):
        self.config = configuration
        self.symbols = frozenset(configuration["static_symbols"])
        self.schema = configuration["catalog_schema"]
        self.tokenizer = tokenizer
        self.text_cache = {}
        self.allocation = 32768 + 8 + len(self.symbols)
        if self.allocation > configuration["vocabulary_entries"]:
            raise ValueError("illustrative vocabulary capacity exceeded")

    def text(self, value):
        if value not in self.text_cache:
            self.text_cache[value] = len(self.tokenizer.encode(value, add_special_tokens=False))
        return self.text_cache[value]

    @staticmethod
    def bounded_length(value):
        if not 0 <= value <= 32767:
            raise ValueError("length exceeds fifteen-bit length field")
        return value

    def scalar_payload(self, text):
        size = self.bounded_length(len(text.encode("utf-8")))
        return 2 + (8 * size + 14) // 15

    def generic(self, value, depth=0, active=None):
        if depth > 128:
            raise ValueError("record nesting exceeds 128 levels")
        kind = type(value)
        if value is None or kind is bool:
            return 1
        if kind is str:
            return 1 if value in self.symbols else self.scalar_payload(value)
        if kind is int:
            return self.scalar_payload(str(value))
        if kind is float:
            if not math.isfinite(value):
                raise ValueError("nonfinite float")
            return self.scalar_payload(json.dumps(value, allow_nan=False, separators=(",", ":")))
        if kind not in (list, dict):
            raise TypeError(f"not a JSON-compatible value: {kind.__name__}")
        self.bounded_length(len(value))
        active = set() if active is None else active
        identity = id(value)
        if identity in active:
            raise ValueError("cyclic container")
        active.add(identity)
        try:
            if kind is list:
                return 2 + sum(self.generic(item, depth + 1, active) for item in value)
            if any(type(key) is not str for key in value):
                raise TypeError("dictionary key is not an ordinary string")
            return 2 + sum(self.generic(key, depth + 1, active) + self.generic(item, depth + 1, active)
                           for key, item in value.items())
        finally:
            active.remove(identity)

    def typed(self, value, depth=0, active=None):
        if depth > 128:
            raise ValueError("operand nesting exceeds 128 levels")
        if type(value) is int and -16384 <= value <= 16383:
            return 1
        if type(value) is list:
            self.bounded_length(len(value))
            active = set() if active is None else active
            identity = id(value)
            if identity in active:
                raise ValueError("cyclic typed operand")
            active.add(identity)
            try:
                return 1 + sum(self.typed(item, depth + 1, active) for item in value)
            finally:
                active.remove(identity)
        return self.generic(value, depth, active)

    def approved_sequence(self, sequence, actions=False):
        cost = 1  # Sequence length.
        self.bounded_length(len(sequence))
        for call in sequence:
            op = call["op"]
            arguments = call["args"]
            names = self.schema[op]
            if set(arguments) != set(names):
                raise ValueError(f"incorrect argument set for {op}")
            cost += 1  # Learned operation reference.
            for name in names:
                value = arguments[name]
                cost += self.approved_sequence(value) if actions and op == "write" and name == "program" else self.typed(value)
        return cost

    def function_name(self, op, aliases):
        return self.config["aliases"][op] if aliases else op

    def render_program(self, calls, aliases=False):
        expression = "r"
        for call in calls:
            name = self.function_name(call["op"], aliases)
            operands = [repr(call["args"][key]) for key in self.schema[call["op"]]]
            expression = name + "(" + ",".join([expression] + operands) + ")"
        return "lambda r:" + expression

    def render_actions(self, actions, aliases=False):
        statements = []
        for action in actions:
            op = action["op"]
            operands = []
            for key in self.schema[op]:
                operand = action["args"][key]
                operands.append(self.render_program(operand, aliases) if op == "write" and key == "program" else repr(operand))
            statements.append(self.function_name(op, aliases) + "(" + ",".join(operands) + ")")
        return ";".join(statements)

    def ledger(self, episode):
        common = self.text(json.dumps(episode["common_input"], separators=(",", ":")))
        ledger = []
        for profile in PROFILES:
            textual = profile.startswith("python")
            aliases = profile == "python_aliases"
            predecessor = episode["predecessor"]
            memory = episode["incoming_memory"]
            artifact_cost = (self.text(self.render_program(predecessor, aliases)) if textual else self.approved_sequence(predecessor)) if predecessor else 0
            memory_cost = (self.text(repr(memory)) if textual else self.generic(memory)) if memory else 0
            history = 0
            for index, (actions, observation) in enumerate(zip(episode["actions"], episode["host_observations"], strict=True)):
                response = self.text(self.render_actions(actions, aliases)) if textual else self.approved_sequence(actions, actions=True)
                observed = self.text(repr(observation)) if textual else self.generic(observation)
                framing = 4 + 3 * index
                row = dict(profile=profile, turn=index + 1, common_input_text_tokens=common,
                           artifact_input_units=artifact_cost, memory_input_units=memory_cost,
                           reprocessed_history_units=history, shared_framing_positions=framing,
                           input_positions=common + artifact_cost + memory_cost + history + framing,
                           authored_content_units=response, output_positions=response + 1,
                           host_observation_units=observed)
                ledger.append(row)
                history += response + 1 + observed
        return ledger


def self_checks(counter):
    checks = {
        "static_string": counter.generic("record") == 1,
        "new_utf8_string": counter.generic("\u00e9") == 4,
        "empty_string": counter.generic("") == 2,
        "booleans": counter.generic(True) == counter.generic(False) == 1,
        "generic_integer": counter.generic(1) == 3,
        "signed_typed_bounds": counter.typed(-16384) == counter.typed(16383) == 1,
        "outside_typed_bounds": counter.typed(-16385) == 6 and counter.typed(16384) == 5,
        "typed_list": counter.typed([1, True, "record"]) == 4,
        "generic_list": counter.generic([1, True, "record"]) == 7,
        "empty_sequence": counter.approved_sequence([]) == 1,
    }
    cases = [float("nan"), float("inf"), {1: "a"}, (1,), "x" * 32768]
    cyclic = []
    cyclic.append(cyclic)
    cases.append(cyclic)
    deeply_nested = None
    for _ in range(130):
        deeply_nested = [deeply_nested]
    cases.append(deeply_nested)
    for index, value in enumerate(cases):
        try:
            counter.generic(value)
        except (TypeError, ValueError):
            checks[f"reject_invalid_{index}"] = True
        else:
            checks[f"reject_invalid_{index}"] = False
    if not all(checks.values()):
        raise AssertionError(checks)
    return checks


def execution_checks(episodes, fixtures, counter):
    fixture_map = {(chain["id"], stage["stage"]): stage for chain in fixtures for stage in chain["stages"]}
    evidence = []
    for episode in episodes:
        fixture = fixture_map[episode["chain"], episode["stage"]]
        program = deepcopy(episode["predecessor"])
        memory = deepcopy(episode["incoming_memory"])
        working = []
        checks = 0
        for batch in episode["actions"]:
            for call in batch:
                op, args = call["op"], call["args"]
                if op == "record":
                    working.append(deepcopy(args["value"]))
                elif op == "write":
                    program = deepcopy(args["program"])
                elif op == "patch":
                    target = program[args["index"]]
                    if args["kind"] == "op":
                        target["op"] = args["value"]
                    elif args["kind"] == "arg":
                        target["args"][args["key"]] = args["value"]
                    else:
                        raise ValueError("unrecognized patch kind")
                elif op == "check":
                    assert workloads.execute(program, fixture["task"]) == workloads.expected(fixture["task"])
                    checks += 1
                elif op == "remember":
                    memory = deepcopy(args["value"])
                elif op == "submit":
                    assert checks == 1
                else:
                    raise ValueError("unknown host tool")
        assert program == episode["artifact"] == fixture["plan"]
        assert memory == episode["outgoing_memory"]
        assert working == episode["working_records"]
        expected = workloads.expected(fixture["task"])
        for aliases in (False, True):
            namespace = {counter.function_name(name, aliases): record["fn"] for name, record in workloads.CATALOG.items()}
            rendered = eval(counter.render_program(program, aliases), {"__builtins__": {}, **namespace})
            assert rendered(deepcopy(fixture["task"]["records"])) == expected
        broken_rejected = None
        if "broken_plan" in fixture:
            broken_rejected = workloads.execute(fixture["broken_plan"], fixture["task"]) != expected
            assert broken_rejected
        evidence.append(dict(chain=episode["chain"], stage=episode["stage"], schedule=episode["schedule"],
                             check_passed=True, both_python_renderings_passed=True,
                             injected_defect_changes_result=broken_rejected, actual_output=expected))
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    output = options.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    data = json.loads((PACKAGE / "trace-inputs.json").read_text(encoding="utf-8"))
    snapshot = ROOT / "work" / "tokenizer-cache" / "hub" / "models--Qwen--Qwen2.5-1.5B" / "snapshots" / data["tokenizer"]["revision"]
    tokenizer_hashes = {name: sha256(snapshot / name) for name in data["tokenizer"]["files"]}
    assert tokenizer_hashes == data["tokenizer"]["files"]
    tokenizer = AutoTokenizer.from_pretrained(str(snapshot), local_files_only=True)
    counter = IndependentCounter(data["config"], tokenizer)
    unit_checks = self_checks(counter)
    episodes = deepcopy(data["episodes"])
    totals = {schedule: {profile: {} for profile in PROFILES} for schedule in ("resident", "inspect")}
    renderings = []
    for episode in episodes:
        episode["ledger"] = counter.ledger(episode)
        for row in episode["ledger"]:
            accumulator = totals[episode["schedule"]][row["profile"]]
            for name, value in row.items():
                if name not in ("profile", "turn"):
                    accumulator[name] = accumulator.get(name, 0) + value
        renderings.append(dict(chain=episode["chain"], stage=episode["stage"], schedule=episode["schedule"],
                               python=counter.render_program(episode["artifact"]),
                               python_aliases=counter.render_program(episode["artifact"], True),
                               python_actions=[counter.render_actions(batch) for batch in episode["actions"]],
                               python_alias_actions=[counter.render_actions(batch, True) for batch in episode["actions"]]))
    execution = execution_checks(episodes, data["fixtures"], counter)
    write_json(output / "episodes.json", episodes)
    write_json(output / "totals.json", totals)
    write_json(output / "renderings.json", renderings)
    write_json(output / "checks.json", dict(unit_checks=unit_checks, execution=execution))
    package_versions = {distribution.metadata["Name"]: distribution.version for distribution in importlib.metadata.distributions()}
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), git_revision=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    python=sys.version, python_executable=sys.executable, platform=platform.platform(), packages=dict(sorted(package_versions.items())),
                    input_hashes={name: sha256(PACKAGE / name) for name in ("AGENT_START_HERE.md", "REPLICATION_SPEC.md", "trace-inputs.json", "workloads.py", "requirements-reproduce.txt", "tokenizer-files.sha256.json")},
                    tokenizer_revision=data["tokenizer"]["revision"], tokenizer_hashes=tokenizer_hashes,
                    implementation_hash=sha256(__file__), vocabulary_allocation=counter.allocation,
                    reference_material_consulted_before_freeze=["AGENT_START_HERE.md", "REPLICATION_SPEC.md", "trace-inputs.json", "requirements-reproduce.txt", "tokenizer-files.sha256.json", "workloads.py"],
                    reference_actions_before_freeze=["reproduce.py --prepare-tokenizer only; source not read"],
                    assumptions=["equal cost per common text token and modeled code unit", "perfect composition", "fluent learned representation", "approved core", "zero model inference calls"],
                    episode_count=len(episodes), ledger_rows=sum(len(episode["ledger"]) for episode in episodes),
                    execution_passes=len(execution), rendering_execution_passes=2 * len(execution))
    write_json(output / "manifest.json", manifest)
    initial_report = """# Independent recreation before reference comparison

I began without AIN background and read the start document, the replication
specification and semantic trace inputs. I wrote the counter and renderer from
the specification. I reused only workloads.py for approved component execution
and independent fixture expectations. No reference accounting.py, run.py,
report.py, article brief, reference ledger or aggregate file was read before
these outputs were frozen. reproduce.py was executed only with
--prepare-tokenizer; it verified all six pinned tokenizer hashes.

This directory preserves the first independent attempt. episodes.json contains
the complete supplied semantic episodes with independently derived request
ledgers. totals.json sums them. renderings.json preserves the actual text used
for Python counts. checks.json records boundary checks and all executable
results. manifest.json records inputs, environment and source hashes.

Python counts use the pinned Qwen tokenizer with add_special_tokens=False.
Ideal counts are declared accounting units, not measured native AIN tokens.
The common text and representation units are combined assuming equal cost per
position. Correct plans, approved components and fluency are supplied premises.
No model inference, model training, energy or planning success was measured.

Specification ambiguity: catalog_schema supplies argument names but contains no
explicit operand type schema, despite prose saying signatures supply types.
For these frozen inputs, typed rules are unambiguous from JSON value types and
the special write(program) rule. This would need elaboration for a general
implementation, particularly field-dependent equality operands.
"""
    (output / "independent-report-before-comparison.md").write_text(initial_report, encoding="utf-8")
    frozen = dict(frozen_utc=datetime.now(timezone.utc).isoformat(), implementation_sha256=sha256(__file__),
                  outputs_sha256={path.name: sha256(path) for path in sorted(output.iterdir()) if path.is_file()},
                  status="Frozen before any reference aggregate or ledger comparison")
    write_json(output / "freeze.json", frozen)
    print(json.dumps(dict(implementation_sha256=frozen["implementation_sha256"], freeze_sha256=sha256(output / "freeze.json"),
                          episodes=len(episodes), ledger_rows=manifest["ledger_rows"], unit_checks=len(unit_checks), execution_passes=len(execution),
                          totals={schedule: {profile: {key: totals[schedule][profile][key] for key in ("input_positions", "output_positions", "authored_content_units")} for profile in PROFILES} for schedule in totals}), indent=2))


if __name__ == "__main__":
    main()
