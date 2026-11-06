"""Judge qualification with known-correct artifacts and independently made faults.

These are deterministic development checks, never model-participant trials.
"""
import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import judge
from ain.language import encode_ain, validate_ir
from ain.programs import workflow_ir, workflow_ain


def python_fixture(stage="build", delta=30):
    """Serialize the judge's direct reference, for loader/subprocess plumbing."""
    node = ast.parse(inspect.getsource(judge.reference)).body[0]
    node.name = "run"
    node.args.args = node.args.args[:1]
    node.args.defaults = []
    class Constants(ast.NodeTransformer):
        def visit_Name(self, child):
            if child.id == "stage":
                return ast.copy_location(ast.Constant(stage), child)
            if child.id == "delta":
                return ast.copy_location(ast.Constant(delta), child)
            return child
    return ast.unparse(ast.fix_missing_locations(Constants().visit(node))) + "\n"


def changed_ir(delta):
    """Hand-build changed CFG independently of the direct imperative oracle."""
    program = workflow_ir()
    program["registers"].update(gap="int", c_delta="int")
    blocks = {block["label"]: block for block in program["blocks"]}
    blocks["entry"]["instructions"].append({"op":"const", "dest":"c_delta", "value":delta})
    blocks["reserve"]["instructions"][-1:] = [
        {"op":"sub", "dest":"gap", "left":"stamp", "right":"frontier"},
        {"op":"lt", "dest":"b", "left":"gap", "right":"c_delta"}]
    blocks["reserve"]["terminator"] = {"op":"branch", "cond":"b",
        "then":"near", "else":"threshold"}
    program["blocks"].extend([
        {"label":"near", "instructions":[{"op":"lt", "dest":"b", "left":"minimum", "right":"c3"}],
         "terminator":{"op":"branch", "cond":"b", "then":"increment", "else":"threshold"}},
        {"label":"increment", "instructions":[{"op":"add", "dest":"minimum", "left":"minimum", "right":"c1"}],
         "terminator":{"op":"jump", "target":"threshold"}},
        {"label":"threshold", "instructions":[{"op":"lt", "dest":"b", "left":"sev", "right":"minimum"}],
         "terminator":{"op":"branch", "cond":"b", "then":"filtered", "else":"accept"}},
    ])
    return program


class JudgeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def artifact(self, source, name="candidate.py"):
        path = Path(self.directory.name) / name
        path.write_text(source if isinstance(source, str) else json.dumps(source), encoding="utf-8")
        return path

    def check(self, path, mode="python", stage="build", delta=30):
        report = judge.judge_artifact(path, mode, stage, delta)
        self.assertTrue(report.get("passed"), json.dumps(report, indent=2))
        self.assertEqual(report["cases"], 55)
        self.assertEqual(report["passed_cases"], 55)
        self.assertEqual(report["judge_exit_code"], 0)
        return report

    def test_frozen_original_three_representations(self):
        paths = {
            "python":judge.STUDY / "ain" / "reference.py",
            "ir":self.artifact(workflow_ir(), "original-ir.json"),
            "ain":self.artifact(workflow_ain(), "original-ain.json"),
        }
        for mode, path in paths.items():
            with self.subTest(mode=mode):
                self.check(path, mode)

    def test_changed_three_representations_both_deltas(self):
        for delta in (30, 75):
            ir = changed_ir(delta)
            validate_ir(ir, judge.Host([]).catalog())
            sources = {"python":python_fixture("change", delta), "ir":ir,
                       "ain":encode_ain(ir, judge.Host([]).catalog())}
            for mode, source in sources.items():
                with self.subTest(mode=mode, delta=delta):
                    path = self.artifact(source, mode + str(delta) + (".py" if mode=="python" else ".json"))
                    self.check(path, mode, "change", delta)

    def test_unchanged_controller_fails_change(self):
        for delta in (30,75):
            report=judge.judge_artifact(judge.STUDY / "ain" / "reference.py", "python", "change", delta)
            self.assertFalse(report["passed"])
            self.assertFalse(next(item for item in report["details"]
                                  if item["case"]=="near_frontier_manual_minimum_1")["passed"])

    def test_each_type_valid_repair_fault_is_rejected(self):
        for fault in ("late-equality", "reserve-after-filter", "one-record-drain"):
            ir = changed_ir(30)
            blocks = {block["label"]:block for block in ir["blocks"]}
            if fault=="late-equality":
                blocks["event"]["instructions"][-1]["op"]="le"
            elif fault=="reserve-after-filter":
                reserve=blocks["reserve"]["instructions"].pop(0)
                blocks["accept"]["instructions"].insert(0,reserve)
            else:
                blocks["pop"]["terminator"]["target"]="finalize"
            validate_ir(ir, judge.Host([]).catalog())
            for mode, value in (("ir",ir), ("ain",encode_ain(ir,judge.Host([]).catalog()))):
                with self.subTest(fault=fault, mode=mode):
                    path=self.artifact(value, fault+mode+".json")
                    report=judge.judge_artifact(path,mode,"repair",30)
                    self.assertFalse(report["passed"], json.dumps(report))
                    self.assertGreater(report["cases"]-report["passed_cases"],0)

    def test_manual_boundary_expectations_all_minima(self):
        for delta in (30,75):
            for stage in ("build","change","repair"):
                for case in judge._cases(delta):
                    if case.get("manual")!="near":
                        continue
                    with self.subTest(delta=delta,stage=stage,minimum=case["minimum"]):
                        result, canonical, audit = judge._execute(
                            lambda host:judge.reference(host,stage,delta), case["records"],case["config"])
                        self.assertEqual(result,canonical)
                        self.assertFalse(audit)
                        self.assertTrue(judge._manual_check(case,result,stage,delta))

    def test_return_cannot_forge_successful_effects(self):
        path=self.artifact(python_fixture().replace("return operations[22](host, state)","return {}"))
        report=judge.judge_artifact(path)
        self.assertFalse(report["passed"])

    def test_admission_requires_explicit_cancellation_check(self):
        source=python_fixture().replace("operations[3](host)","pass")
        report=judge.judge_artifact(self.artifact(source))
        self.assertFalse(report["passed"])
        self.assertTrue(any("missing cancellation check" in violation
                            for item in report["details"] for violation in item.get("violations",[])))

    def test_restricted_python_no_imports_or_host_internals(self):
        for source in ("import os\ndef run(host): return {}", "def run(host): return host.outcome()"):
            report=judge.judge_artifact(self.artifact(source))
            self.assertFalse(report["passed"])
            self.assertEqual(report["error"],"ARTIFACT_LOAD_OR_JUDGE_ERROR")

    def test_load_errors_and_size_limit_fail_closed(self):
        for path in (Path(self.directory.name)/"missing.py",
                     self.artifact("#"*(judge.ARTIFACT_LIMIT+1))):
            report=judge.judge_artifact(path)
            self.assertFalse(report["passed"])
            self.assertEqual(report["error"],"ARTIFACT_LOAD_OR_JUDGE_ERROR")

    def test_timeout_report(self):
        with patch.object(judge.subprocess,"run",side_effect=subprocess.TimeoutExpired("judge",judge.TIMEOUT)):
            report=judge.judge_artifact(self.artifact(python_fixture()))
        self.assertFalse(report["passed"])
        self.assertEqual(report["error"],"JUDGE_TIMEOUT")


if __name__=="__main__":
    unittest.main()
