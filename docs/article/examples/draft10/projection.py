"""Article-only numeric display projection of the frozen semantic call stream.

This lossless codec was added for Draft 10. It is NOT the frozen ideal-unit
accounting, a proposed finalized AIN grammar, or a model-generated program.
The numeric JSON is decoded before executing the unchanged approved functions.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TRACE = ROOT / "experiments/approved_workflow_theory/trace-inputs.json"


class Projection:
    """Names become frozen-reference IDs; value tags make display unambiguous."""
    def __init__(self, config):
        self.schema = config["catalog_schema"]
        self.operations = list(self.schema)
        self.symbols = list(config["static_symbols"])
        self.op_ids = {name: i + 1 for i, name in enumerate(self.operations)}
        self.symbol_ids = {name: i + 1 for i, name in enumerate(self.symbols)}

    def value(self, value):
        if type(value) is str:
            return [0, self.symbol_ids[value]] if value in self.symbol_ids else [4, *value.encode("utf-8")]
        if type(value) is int:
            return [1, value]
        if type(value) is bool:
            return [2, int(value)]
        if value is None:
            return [3]
        if type(value) is list:
            return [5, len(value), *[self.value(item) for item in value]]
        if type(value) is dict:
            return [6, len(value), *[[self.value(k), self.value(v)] for k, v in value.items()]]
        if type(value) is float:
            # Floats are not used in the selected example. Exact text is lossless.
            return [7, *json.dumps(value, allow_nan=False).encode("ascii")]
        raise TypeError(type(value).__name__)

    def unvalue(self, data):
        tag = data[0]
        if tag == 0: return self.symbols[data[1] - 1]
        if tag == 1: return data[1]
        if tag == 2: return bool(data[1])
        if tag == 3: return None
        if tag == 4: return bytes(data[1:]).decode("utf-8")
        if tag == 5:
            if data[1] != len(data) - 2: raise ValueError("list length")
            return [self.unvalue(item) for item in data[2:]]
        if tag == 6:
            if data[1] != len(data) - 2: raise ValueError("record length")
            return {self.unvalue(k): self.unvalue(v) for k, v in data[2:]}
        if tag == 7: return json.loads(bytes(data[1:]).decode("ascii"))
        raise ValueError("unknown display tag")

    def call(self, call):
        return [self.op_ids[call["op"]], *[self.value(call["args"][name]) for name in self.schema[call["op"]]]]

    def uncall(self, data):
        name = self.operations[data[0] - 1]
        if len(data) - 1 != len(self.schema[name]): raise ValueError("argument count")
        return {"op": name, "args": {key: self.unvalue(value) for key, value in zip(self.schema[name], data[1:])}}

    def program(self, plan):
        return [len(plan), *[self.call(call) for call in plan]]

    def unprogram(self, data):
        if data[0] != len(data) - 1: raise ValueError("program length")
        return [self.uncall(call) for call in data[1:]]


def apply_actions(predecessor, actions):
    plan = deepcopy(predecessor)
    for batch in actions:
        for call in batch:
            args = call["args"]
            if call["op"] == "write":
                plan = deepcopy(args["program"])
            elif call["op"] == "patch":
                target = plan[args["index"]]
                if args["kind"] == "op": target["op"] = args["value"]
                else: target["args"][args["key"]] = args["value"]
    return plan


def qualify():
    trace = json.loads(TRACE.read_text(encoding="utf-8"))
    codec = Projection(trace["config"])
    path = ROOT / "experiments/approved_workflow_theory/workloads.py"
    spec = importlib.util.spec_from_file_location("approved_workloads", path)
    workload = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(workload)
    tasks = {(chain["id"], stage["stage"]): stage["task"] for chain in trace["fixtures"] for stage in chain["stages"]}
    checks = []
    for episode in trace["episodes"]:
        decoded = codec.unprogram(codec.program(episode["artifact"]))
        decoded_actions = [[codec.uncall(codec.call(call)) for call in batch] for batch in episode["actions"]]
        task = tasks[(episode["chain"], episode["stage"])]
        checks.append({"chain": episode["chain"], "stage": episode["stage"], "schedule": episode["schedule"],
                       "program_roundtrip": decoded == episode["artifact"],
                       "action_roundtrip": decoded_actions == episode["actions"],
                       "actions_reconstruct_program": apply_actions(episode["predecessor"], decoded_actions) == decoded,
                       "decoded_program_matches_oracle": workload.execute(decoded, task) == workload.expected(task)})
    return {"scope": "New Draft 10 display projection; not new model inference or frozen efficiency data",
            "episodes": len(checks), "passed": all(all(row[k] for k in
                ("program_roundtrip", "action_roundtrip", "actions_reconstruct_program", "decoded_program_matches_oracle")) for row in checks),
            "checks": checks}


if __name__ == "__main__":
    result = qualify()
    print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
