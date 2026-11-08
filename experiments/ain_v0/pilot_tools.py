"""Prepare and judge a bounded, public, same-session agent editing pilot."""
import argparse
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import random
import sys
import unittest

ROOT = Path(__file__).resolve().parent
PILOT = ROOT / "agent_pilot"


def prepare():
    from ain.engine import Host
    from ain.language import encode_ain
    from ain.programs import workflow_ir
    PILOT.mkdir(exist_ok=False)
    instructions = {
        "repair": "Repair an injected boundary defect. A timestamp equal to the current frontier is admitted; only strictly earlier events are late. Preserve every other requirement. Do not alter the host/configuration/counters to hide the defect.",
        "optimize": "Avoid Unicode normalization for below-threshold events while preserving all specified results and effects. Fully validate raw records and reserve first admitted IDs before filtering. The optimized program must normalize exactly the accepted events, including under minimum severities 0, 1, 2 and 3. Do not skip required cancellation, authority or commit checks.",
    }
    assignments = []
    for task in ("repair", "optimize"):
        for mode in ("python", "ir", "ain"):
            cell = PILOT / (mode + "_" + task)
            cell.mkdir()
            doc = workflow_ir()
            if task == "repair":
                next(b for b in doc["blocks"] if b["label"] == "event")["instructions"][-1]["op"] = "le"
            if mode == "python":
                content = (ROOT / "ain" / "reference.py").read_text(encoding="utf-8")
                if task == "repair":
                    content = content.replace('op["timestamp"](record) < op["frontier"](state)',
                                              'op["timestamp"](record) <= op["frontier"](state)')
                suffix = ".py"
            else:
                suffix = ".json"
                if mode == "ain":
                    doc = encode_ain(doc, Host([]).catalog())
                content = json.dumps(doc, indent=2) + "\n"
            for name in ("initial", "candidate"):
                (cell / (name + suffix)).write_text(content, encoding="utf-8")
            task_text = f"""# One-attempt AIN development editing task

Representation: {mode}. Task: {task}.

{instructions[task]}

Edit only candidate{suffix} in this directory. Keep initial{suffix} unchanged.
Read this file, your candidate, ../../programs/catalog.json, ../../LANGUAGE.md,
../../ENGINE.md, and ../../../../docs/ain/COMPLEX_TASK.md. These are the permitted
task sources. Do not read other source programs, attempts, tests, judge code,
results or parent chat. Do not execute code or run tests. You have one submission;
the parent judges it after your final reply. You may inspect and edit your own
artifact using tools. Finish by describing the semantic change in one sentence.

The programs use equal host operations and the same semantic contract. Numeric
AIN is mechanically equivalent to readable IR. No private policy source is
provided. Do not raise capacities, change policy/sink interfaces, add a whole-
workflow host operation, or use Python source evaluation in an IR/AIN program.

The judge will compare durable outputs, error/effect behavior, generated streams,
and the task-specific obligation. This is a public same-host pilot, not a secure
blind experiment. Provider model identity, billed tokens and cost are unavailable.
"""
            (cell / "TASK.md").write_text(task_text, encoding="utf-8")
            assignments.append({"cell": cell.name, "mode": mode, "task": task,
                                "attempt_limit": 1, "initial_sha256": hashlib.sha256((cell / ("initial" + suffix)).read_bytes()).hexdigest()})
    freeze = frozen_hashes()
    (PILOT / "protocol.json").write_text(json.dumps({
        "design": "six fresh-context one-submission development cells; one per representation and task",
        "tasks": assignments, "judge_and_source_sha256": freeze,
        "model_identity": None, "billed_tokens": None, "dollar_cost": None,
        "limitations": ["same shared host; source access restriction is cooperative, not isolation",
                        "no provider attestation, model training or custom tokenizer",
                        "one chain per task/form; no inferential success or timing comparison"]}, indent=2) + "\n", encoding="utf-8")


def frozen_hashes():
    files = [p for p in sorted(ROOT.rglob("*.py")) if "agent_pilot" not in p.parts]
    files += [ROOT / n for n in ("LANGUAGE.md", "ENGINE.md", "programs/catalog.json",
                                 "../../docs/ain/COMPLEX_TASK.md")]
    return {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in files}


def refreeze():
    protocol_path = PILOT / "protocol.json"
    if any(PILOT.rglob("submission-judge.json")) or (PILOT / "dispatch.json").exists():
        raise ValueError("Cannot refreeze after agent attempts begin")
    old = protocol_path.read_bytes()
    (PILOT / ("protocol-preflight-" + hashlib.sha256(old).hexdigest()[:12] + ".json")).write_bytes(old)
    protocol = json.loads(old)
    protocol["previous_preflight_protocol_sha256"] = hashlib.sha256(old).hexdigest()
    protocol["judge_and_source_sha256"] = frozen_hashes()
    for task in protocol["tasks"]:
        path = PILOT / task["cell"] / ("initial.py" if task["mode"] == "python" else "initial.json")
        task["initial_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    order = []
    rng = random.Random(20261105)
    for task in ("repair", "optimize"):
        forms = ["python", "ir", "ain"]
        rng.shuffle(forms)
        order.extend(form + "_" + task for form in forms)
    protocol["dispatch_order"] = order
    protocol_path.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")


def verify_freeze():
    protocol = json.loads((PILOT / "protocol.json").read_text())
    for name, expected in protocol["judge_and_source_sha256"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Frozen judge/source changed: " + name)
    for task in protocol["tasks"]:
        path = PILOT / task["cell"] / ("initial.py" if task["mode"] == "python" else "initial.json")
        if hashlib.sha256(path.read_bytes()).hexdigest() != task["initial_sha256"]:
            raise ValueError("Frozen initial artifact changed: " + task["cell"])


def judge(cell_name, candidate_name=None):
    verify_freeze()
    from ain.engine import Host, WorkflowError
    from ain.language import loads_json, run_ir, run_ain, encode_ain
    from ain import programs, reference
    cell = PILOT / cell_name
    mode, task = cell_name.split("_")
    candidate = cell / (candidate_name or ("candidate.py" if mode == "python" else "candidate.json"))
    baseline_python, baseline_ir = reference.run, programs.workflow_ir
    baseline_ain = encode_ain(baseline_ir(), Host([]).catalog())
    if mode == "python":
        spec = importlib.util.spec_from_file_location("candidate", candidate)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        candidate_run = module.run
        reference.run = candidate_run
    else:
        document = loads_json(candidate.read_text(encoding="utf-8"))
        if mode == "ir":
            programs.workflow_ir = lambda: deepcopy(document)
            programs.workflow_ain = lambda catalog=None: deepcopy(baseline_ain)
            candidate_run = lambda host: run_ir(document, host.catalog(), [host], fuel=100_000_000)
        else:
            programs.workflow_ain = lambda catalog=None: deepcopy(document)
            candidate_run = lambda host: run_ain(document, host.catalog(), [host], fuel=100_000_000)

    # Full expected-effect and generated suite, not just one favorable example.
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    normalization = []
    if task == "optimize":
        sys.path.insert(0, str(ROOT / "tests"))
        from fixtures import event, end, contract_trace
        unique = [event(i + 1, str(i), i * 2, i % 4) for i in range(40)] + [end(41)]
        for fixture, rows in (("unique", unique), ("mixed", contract_trace())):
            for minimum in range(4):
                calls = []
                host = Host(rows, config={"minimum": minimum})
                original_normalize = host.normalize
                def normalize(record):
                    calls.append(record["offset"])
                    return original_normalize(record)
                host.normalize = normalize
                output = candidate_run(host)
                expected = baseline_python(Host(rows, config={"minimum": minimum}))
                expected_offsets = ([i + 1 for i in range(40) if i % 4 >= minimum] if fixture == "unique" else
                                    [[1, 3, 4, 7, 9], [3, 4, 7, 9], [3, 7, 9], [7]][minimum])
                normalization.append({"fixture": fixture, "minimum": minimum,
                                      "actual_calls": len(calls), "required_calls": len(expected_offsets),
                                      "actual_offsets": calls, "required_offsets": expected_offsets,
                                      "same_output": output == expected,
                                      "passed": calls == expected_offsets and output == expected})
    verify_freeze()
    report = {"cell": cell_name, "candidate": candidate.name,
              "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
              "tests_run": result.testsRun, "failures": len(result.failures),
              "errors": len(result.errors), "normalization": normalization,
              "passed": result.wasSuccessful() and all(row["passed"] for row in normalization)}
    tag = "initial" if candidate_name else "submission"
    (cell / (tag + "-judge.log")).write_text(stream.getvalue(), encoding="utf-8")
    (cell / (tag + "-judge.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return report["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("prepare", "refreeze", "judge"))
    parser.add_argument("--cell")
    parser.add_argument("--candidate")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare()
    elif args.action == "refreeze":
        refreeze()
    else:
        try:
            passed = judge(args.cell, args.candidate)
        except Exception as error:
            cell = PILOT / args.cell
            tag = "initial" if args.candidate else "submission"
            report = {"cell": args.cell, "passed": False,
                      "judge_exception": {"type": type(error).__name__, "message": str(error)}}
            (cell / (tag + "-judge.json")).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(report))
            passed = False
        raise SystemExit(0 if passed else 1)
