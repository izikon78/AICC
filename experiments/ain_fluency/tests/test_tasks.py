"""Deterministic prompt/corruptor qualification; these are not model trials."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import tasks
from ain.language import run_ain, run_ir, validate_ir


def local_operand_fixture():
    source = tasks.canonical_changed_program("python", 30)
    return source.replace(
        '            if op["timestamp"](record) < op["frontier"](state):',
        '            stamp = op["timestamp"](record)\n'
        '            boundary = op["frontier"](state)\n'
        '            if stamp < boundary:')


def numeric_alias_fixture(raw_catalog=False):
    source = local_operand_fixture()
    binding = 'op = {item["name"]: item["fn"] for item in host.catalog().values()}'
    replacement = ('op = host.catalog()' if raw_catalog else
                   'op = {key: item["fn"] for key, item in host.catalog().items()}')
    source = source.replace(binding, replacement)
    for item in tasks.catalog_metadata():
        reference = 'op[' + str(item["id"]) + ']'
        if raw_catalog:
            reference += '["fn"]'
        source = source.replace('op["' + item["name"] + '"]', reference)
    # Resolve function aliases, then scalar aliases, rather than requiring
    # direct catalog-call operands inside the comparison or loop condition.
    suffix = '["fn"]' if raw_catalog else ''
    definitions = []
    for name, identifier in (("ts_fn", 7), ("frontier_fn", 6),
                             ("reserve_fn", 9), ("buffer_fn", 13),
                             ("pending_fn", 16)):
        original = 'op[' + str(identifier) + ']' + suffix
        source = source.replace(original + '(', name + '(')
        definitions.append('    ' + name + ' = ' + original)
    source = source.replace('    state =', '\n'.join(definitions) + '\n    state =', 1)
    return source


def named_function_alias_fixture():
    source = local_operand_fixture()
    definitions = []
    for local, name in (("T", "timestamp"), ("F", "frontier"),
                        ("R", "reserve"), ("B", "buffer"),
                        ("P", "pending_ready")):
        reference = 'op["' + name + '"]'
        source = source.replace(reference + '(', local + '(')
        definitions.append('    ' + local + ' = ' + reference)
    return source.replace('    state =', '\n'.join(definitions) + '\n    state =', 1)


class TasksTests(unittest.TestCase):
    def test_schemas_match_fixed_gate_shape_and_decode_syntax(self):
        expected = tasks.expected_fluency()
        self.assertEqual(expected["syntax_value"], 14)
        for schema in (tasks.response_schema(), tasks.fluency_response_schema()):
            gate = schema["properties"]["fluency"]
            self.assertEqual(set(gate["required"]), set(expected))
            self.assertEqual(set(gate["properties"]), set(expected))
            self.assertFalse(gate["additionalProperties"])
        for mode in tasks.MODES:
            example = tasks._syntax_question(mode)
            if mode == "python":
                scope = {}
                exec(compile(example, "<frozen-arithmetic>", "exec"), scope)
                value = scope["sample"]()
            else:
                value = (run_ir if mode == "ir" else run_ain)(json.loads(example), {}, [])
            self.assertEqual(value, expected["syntax_value"])

    def test_preparation_has_no_canonical_controller(self):
        for mode in tasks.MODES:
            prompt = tasks.preparation_prompt_for(mode, "build", 30)
            self.assertNotIn(tasks.canonical_build_program(mode), prompt)
            self.assertIn("SYNTAX PROGRAM FOR syntax_value", prompt)
            self.assertNotIn("PREDECESSOR ARTIFACT", prompt)
            self.assertIn(tasks.catalog_digest(), prompt)

    def test_supported_python_local_numeric_and_function_aliases(self):
        for source in (local_operand_fixture(), named_function_alias_fixture(), numeric_alias_fixture(),
                       numeric_alias_fixture(raw_catalog=True)):
            with self.subTest(source=source[:100]):
                output = tasks.corrupt_artifact(source, "python", 30)
                info = tasks.corruption_info()
                self.assertFalse(info["fallback"], info)
                self.assertEqual(info["mutation_count"], 3)
                self.assertEqual(len(info["faults"]), 3)
                parsed = ast.parse(output)
                self.assertTrue(any(isinstance(node, ast.LtE) for node in ast.walk(parsed)))
                compile(output, "<qualified-corruption>", "exec")

    def test_alias_program_is_correct_and_compound_corruption_is_rejected(self):
        import judge
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "controller.py"
            source = numeric_alias_fixture(raw_catalog=True)
            path.write_text(source, encoding="utf-8")
            good = judge.judge_artifact(path, "python", "change", 30)
            self.assertTrue(good["passed"], good)
            path.write_text(tasks.corrupt_artifact(source, "python", 30), encoding="utf-8")
            bad = judge.judge_artifact(path, "python", "repair", 30)
            self.assertFalse(bad["passed"], bad)
            self.assertFalse(tasks.corruption_info()["fallback"])

    def test_each_fault_is_behavioral_in_every_mode_and_delta(self):
        import judge
        with tempfile.TemporaryDirectory() as directory:
            for mode in tasks.MODES:
                for delta in tasks.DELTAS:
                    source = tasks.canonical_changed_program(mode, delta)
                    tasks.corrupt_artifact(source, mode, delta)
                    info = tasks.corruption_info()
                    variants = tasks.corruption_variants(source, mode, delta)
                    self.assertEqual(tasks.corruption_info(), info)
                    self.assertEqual(set(variants), set(info["faults"]))
                    for fault, program in variants.items():
                        with self.subTest(mode=mode, delta=delta, fault=fault):
                            path = Path(directory) / ("variant.py" if mode == "python" else "variant.json")
                            path.write_text(program, encoding="utf-8")
                            report = judge.judge_artifact(path, mode, "repair", delta)
                            self.assertEqual(report["judge_exit_code"], 1, report)
                            self.assertEqual(report["cases"], 55, report)
                            self.assertFalse(report["passed"], report)
                            self.assertTrue(any(not item["passed"] and "exception" not in item
                                                for item in report["details"]), report)

    def test_single_fault_variants_share_compound_fallback_source(self):
        for mode in tasks.MODES:
            tasks.corrupt_artifact("invalid", mode, 30)
            metadata = tasks.corruption_info()
            variants = tasks.corruption_variants("invalid", mode, 30)
            self.assertEqual(tasks.corruption_info(), metadata)
            direct = tasks.corruption_variants(tasks.canonical_changed_program(mode, 30), mode, 30)
            self.assertEqual(variants, direct)
            self.assertEqual(tasks.corruption_info(), metadata)

    def test_unrecognized_layout_is_explicit_fallback_and_metadata_is_a_copy(self):
        for mode in tasks.MODES:
            output = tasks.corrupt_artifact("not a program", mode, 75)
            info = tasks.corruption_info()
            self.assertTrue(info["fallback"])
            self.assertTrue(info["reason"])
            self.assertIn("fallback_source_sha256", info)
            self.assertEqual(info["mutation_count"], 3)
            if mode == "python":
                compile(output, "<fallback>", "exec")
            else:
                document = json.loads(output)
                if mode == "ain":
                    document = tasks.decode_ain(document, tasks._catalog())
                validate_ir(document, tasks._catalog())
                self.assertTrue(info["type_valid"])
            info["fallback"] = False
            self.assertTrue(tasks.corruption_info()["fallback"])


if __name__ == "__main__":
    unittest.main()
