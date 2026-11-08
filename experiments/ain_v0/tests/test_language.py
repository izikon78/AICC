"""Conformance and hostile-document checks for the standalone typed VM."""

import copy
import json
from pathlib import Path
import unittest

from ain.language import (FuelExhausted, LanguageError, decode_ain, encode_ain,
                          load_json, loads_ain, loads_ir, loads_json, run_ain,
                          run_ir, validate_ir)


def constant_program(value=7, type_name="int"):
    return {"version": 0, "registers": {"x": type_name}, "parameters": [],
            "return_type": type_name, "entry": "start", "blocks": [
                {"label": "start", "instructions": [{"op": "const", "dest": "x", "value": value}],
                 "terminator": {"op": "return", "value": "x"}}]}


def sum_program():
    return {"version": 0,
            "registers": {"n": "int", "i": "int", "sum": "int", "one": "int", "more": "bool"},
            "parameters": ["n"], "return_type": "int", "entry": "start", "blocks": [
                {"label": "start", "instructions": [
                    {"op": "const", "dest": "i", "value": 0},
                    {"op": "const", "dest": "sum", "value": 0},
                    {"op": "const", "dest": "one", "value": 1}],
                 "terminator": {"op": "jump", "target": "test"}},
                {"label": "test", "instructions": [
                    {"op": "lt", "dest": "more", "left": "i", "right": "n"}],
                 "terminator": {"op": "branch", "cond": "more", "then": "step", "else": "done"}},
                {"label": "step", "instructions": [
                    {"op": "add", "dest": "sum", "left": "sum", "right": "i"},
                    {"op": "add", "dest": "i", "left": "i", "right": "one"}],
                 "terminator": {"op": "jump", "target": "test"}},
                {"label": "done", "instructions": [],
                 "terminator": {"op": "return", "value": "sum"}}]}


def call_program(return_type="int"):
    inst = {"op": "call", "fn": "probe", "args": []}
    if return_type != "void":
        inst["dest"] = "x"
    return {"version": 0, "registers": {} if return_type == "void" else {"x": return_type},
            "parameters": [], "return_type": return_type, "entry": "start", "blocks": [
                {"label": "start", "instructions": [inst],
                 "terminator": ({"op": "return"} if return_type == "void" else
                                {"op": "return", "value": "x"})}]}


def catalog(fn=lambda: 11, return_type="int"):
    return {19: {"name": "probe", "args": [], "return": return_type,
                 "effect": "pure", "fn": fn}}


class LanguageTests(unittest.TestCase):
    def test_exact_arithmetic_loop_and_both_serializations(self):
        program = sum_program()
        encoded = encode_ain(program, {})
        for n in (0, 1, 2, 10, 100):
            expected = n * (n - 1) // 2
            self.assertEqual(run_ir(program, {}, [n]), expected)
            self.assertEqual(run_ain(encoded, {}, [n]), expected)

    def test_codec_is_semantic_and_numeric_round_trip_is_stable(self):
        encoded = encode_ain(sum_program(), {})
        decoded = decode_ain(encoded, {})
        self.assertEqual(list(decoded["registers"]), ["r0", "r1", "r2", "r3", "r4"])
        self.assertEqual(encode_ain(decoded, {}), encoded)
        self.assertEqual(loads_ain(json.dumps(encoded), {}), encoded)
        self.assertEqual(loads_ir(json.dumps(sum_program()), {}), sum_program())

    def test_large_integer_is_exact_and_negative_values_are_allowed(self):
        program = constant_program(10 ** 100)
        program["blocks"][0]["instructions"].append({"op": "add", "dest": "x", "left": "x", "right": "x"})
        self.assertEqual(run_ir(program, {}, []), 2 * 10 ** 100)
        self.assertEqual(run_ir(constant_program(-123), {}, []), -123)

    def test_move_sub_le_eq_and_not(self):
        program = {"version": 0, "registers": {"a": "int", "b": "int", "c": "bool", "d": "bool"},
                   "parameters": ["a"], "return_type": "bool", "entry": "b", "blocks": [
                       {"label": "b", "instructions": [
                           {"op": "move", "dest": "b", "src": "a"},
                           {"op": "sub", "dest": "b", "left": "b", "right": "a"},
                           {"op": "le", "dest": "c", "left": "b", "right": "a"},
                           {"op": "eq", "dest": "d", "left": "c", "right": "c"},
                           {"op": "not", "dest": "d", "src": "d"}],
                        "terminator": {"op": "return", "value": "d"}}]}
        self.assertIs(run_ain(encode_ain(program, {}), {}, [4]), False)

    def test_scalar_string_equality(self):
        p = {"version": 0, "registers": {"a": "str", "b": "str", "same": "bool"},
             "parameters": ["a", "b"], "return_type": "bool", "entry": "entry", "blocks": [
                 {"label": "entry", "instructions": [{"op": "eq", "dest": "same", "left": "a", "right": "b"}],
                  "terminator": {"op": "return", "value": "same"}}]}
        self.assertIs(run_ir(p, {}, ["Straße", "strasse"]), False)

    def test_named_and_positional_arguments_and_strict_scalar_types(self):
        self.assertEqual(run_ir(sum_program(), {}, {"n": 4}), 6)
        for args in ([True], [4, 5], [], "4", {"n": 4, "extra": 1}):
            with self.subTest(args=args), self.assertRaises(LanguageError):
                run_ir(sum_program(), {}, args)

    def test_bool_is_not_integer_in_source_or_numeric_metadata(self):
        p = constant_program(True)
        with self.assertRaises(LanguageError):
            validate_ir(p, {})
        for path in ("version", "register_type", "parameter", "entry", "opcode", "target"):
            encoded = encode_ain(sum_program(), {})
            if path == "version": encoded[0] = False
            elif path == "register_type": encoded[2][0] = False
            elif path == "parameter": encoded[3][0] = False
            elif path == "entry": encoded[5] = False
            elif path == "opcode": encoded[6][0][0][0][0] = False
            else: encoded[6][0][1][1] = False
            with self.subTest(path=path), self.assertRaises(LanguageError):
                decode_ain(encoded, {})

    def test_uninitialized_read_rejected_on_a_join(self):
        p = {"version": 0, "registers": {"condition": "bool", "x": "int"},
             "parameters": ["condition"], "return_type": "int", "entry": "entry", "blocks": [
                 {"label": "entry", "instructions": [], "terminator": {"op": "branch", "cond": "condition", "then": "yes", "else": "join"}},
                 {"label": "yes", "instructions": [{"op": "const", "dest": "x", "value": 1}], "terminator": {"op": "jump", "target": "join"}},
                 {"label": "join", "instructions": [], "terminator": {"op": "return", "value": "x"}}]}
        with self.assertRaisesRegex(LanguageError, "not initialized"):
            validate_ir(p, {})
        p["blocks"][0]["instructions"] = [{"op": "const", "dest": "x", "value": 0}]
        self.assertEqual(run_ir(p, {}, [False]), 0)
        self.assertEqual(run_ir(p, {}, [True]), 1)

    def test_loop_backedge_cannot_supply_first_iteration_initialization(self):
        p = sum_program()
        p["blocks"][0]["instructions"] = [i for i in p["blocks"][0]["instructions"] if i["dest"] != "sum"]
        with self.assertRaisesRegex(LanguageError, "not initialized"):
            validate_ir(p, {})

    def test_read_before_write_within_block_is_rejected(self):
        p = constant_program()
        p["blocks"][0]["instructions"].insert(0, {"op": "move", "dest": "x", "src": "x"})
        with self.assertRaises(LanguageError):
            validate_ir(p, {})

    def test_all_blocks_are_type_checked_before_first_effect(self):
        calls = []
        cat = catalog(lambda: calls.append(1) or 7)
        p = call_program()
        p["blocks"].append({"label": "unreachable", "instructions": [
            {"op": "const", "dest": "missing", "value": 1}], "terminator": {"op": "return", "value": "x"}})
        with self.assertRaises(LanguageError):
            run_ir(p, cat, [])
        self.assertEqual(calls, [])

    def test_unknown_keys_and_missing_fields_are_rejected(self):
        cases = []
        p = constant_program(); p["surprise"] = 0; cases.append(p)
        p = constant_program(); del p["return_type"]; cases.append(p)
        p = constant_program(); p["blocks"][0]["instructions"][0]["note"] = "x"; cases.append(p)
        p = constant_program(); p["blocks"][0]["terminator"]["target"] = "start"; cases.append(p)
        for p in cases:
            with self.subTest(p=p), self.assertRaises(LanguageError):
                validate_ir(p, {})

    def test_duplicate_labels_and_parameters_and_unknown_targets(self):
        p = sum_program(); p["parameters"] = ["n", "n"]
        with self.assertRaises(LanguageError): validate_ir(p, {})
        p = sum_program(); p["blocks"][1]["label"] = "start"
        with self.assertRaises(LanguageError): validate_ir(p, {})
        p = sum_program(); p["blocks"][0]["terminator"]["target"] = "absent"
        with self.assertRaises(LanguageError): validate_ir(p, {})

    def test_wrong_operator_return_branch_and_call_types(self):
        p = sum_program(); p["blocks"][1]["terminator"]["cond"] = "n"
        with self.assertRaises(LanguageError): validate_ir(p, {})
        p = constant_program(); p["return_type"] = "str"
        with self.assertRaises(LanguageError): validate_ir(p, {})
        p = call_program(); p["blocks"][0]["instructions"][0]["args"] = ["x"]
        with self.assertRaises(LanguageError): validate_ir(p, catalog())
        p = constant_program("x", "str"); p["blocks"][0]["instructions"].append({"op": "add", "dest": "x", "left": "x", "right": "x"})
        with self.assertRaises(LanguageError): validate_ir(p, {})

    def test_void_calls_and_void_return_omit_destination_and_value(self):
        calls = []
        p = call_program("void"); cat = catalog(lambda: calls.append(1), "void")
        self.assertIsNone(run_ain(encode_ain(p, cat), cat, []))
        self.assertEqual(calls, [1])
        p["blocks"][0]["instructions"][0]["dest"] = None
        with self.assertRaises(LanguageError): validate_ir(p, cat)
        p = call_program("void"); p["blocks"][0]["terminator"]["value"] = None
        with self.assertRaises(LanguageError): validate_ir(p, cat)

    def test_scalar_catalog_result_contract_is_checked(self):
        with self.assertRaises(LanguageError):
            run_ir(call_program(), catalog(lambda: True), [])
        with self.assertRaises(LanguageError):
            run_ir(call_program("void"), catalog(lambda: 1, "void"), [])

    def test_host_exceptions_are_not_hidden_or_converted(self):
        failure = RuntimeError("host failure")
        def fail(): raise failure
        with self.assertRaises(RuntimeError) as caught:
            run_ir(call_program(), catalog(fail), [])
        self.assertIs(caught.exception, failure)

    def test_catalog_names_ids_signatures_and_effects_are_pinned(self):
        cat = catalog(); encoded = encode_ain(call_program(), cat)
        changed = []
        c = catalog(); c[19]["name"] = "other"; changed.append(c)
        c = catalog(); c[19]["args"] = ["int"]; changed.append(c)
        c = catalog(); c[19]["return"] = "str"; changed.append(c)
        c = catalog(); c[19]["effect"] = "state"; changed.append(c)
        c = {20: cat[19]}; changed.append(c)
        for c in changed:
            with self.subTest(c=c), self.assertRaisesRegex(LanguageError, "identity mismatch"):
                run_ain(encoded, c, [])

    def test_schema_pin_is_not_callable_implementation_authentication(self):
        encoded = encode_ain(call_program(), catalog())
        self.assertEqual(run_ain(encoded, catalog(lambda: 22), []), 22)

    def test_invalid_catalogs_are_rejected_without_invoking_them(self):
        cases = [{True: catalog()[19]}, catalog(), catalog(), catalog()]
        cases[1][20] = cases[1][19].copy()
        cases[2][19]["effect"] = "network"
        cases[3][19]["fn"] = "__import__('os')"
        for c in cases:
            with self.subTest(c=c), self.assertRaises(LanguageError): validate_ir(call_program(), c)

    def test_loop_fuel_is_exact_and_does_not_call_before_available_step(self):
        p = {"version": 0, "registers": {}, "parameters": [], "return_type": "void",
             "entry": "loop", "blocks": [{"label": "loop", "instructions": [],
                                             "terminator": {"op": "jump", "target": "loop"}}]}
        with self.assertRaises(FuelExhausted): run_ir(p, {}, [], fuel=17)
        calls = []
        with self.assertRaises(FuelExhausted):
            run_ir(call_program(), catalog(lambda: calls.append(1) or 7), [], fuel=0)
        self.assertEqual(calls, [])
        self.assertEqual(run_ir(constant_program(), {}, [], fuel=2), 7)
        for fuel in (-1, True, 1.5):
            with self.subTest(fuel=fuel), self.assertRaises(LanguageError): run_ir(p, {}, [], fuel=fuel)

    def test_numeric_unknown_opcodes_arity_and_out_of_range_references(self):
        cases = []
        p = encode_ain(constant_program(), {}); p[6][0][0][0][0] = 99; cases.append(p)
        p = encode_ain(constant_program(), {}); p[6][0][0][0].append(4); cases.append(p)
        p = encode_ain(constant_program(), {}); p[6][0][0][0][1] = 100; cases.append(p)
        p = encode_ain(constant_program(), {}); p[6][0][1] = [100, 100]; cases.append(p)
        p = encode_ain(constant_program(), {}); p[2][0] = 9; cases.append(p)
        for p in cases:
            with self.subTest(p=p), self.assertRaises(LanguageError): decode_ain(p, {})

    def test_no_opaque_constants_or_opaque_comparison(self):
        with self.assertRaises(LanguageError): validate_ir(constant_program({}, "state"), {})
        p = {"version": 0, "registers": {"x": "state", "b": "bool"}, "parameters": ["x"],
             "return_type": "bool", "entry": "a", "blocks": [{"label": "a", "instructions": [
                 {"op": "eq", "dest": "b", "left": "x", "right": "x"}],
                 "terminator": {"op": "return", "value": "b"}}]}
        with self.assertRaises(LanguageError): validate_ir(p, {})

    def test_strict_json_rejects_duplicate_keys_and_nonfinite_literals(self):
        for text in ('{"a":1,"a":2}', '{"a":{"x":1,"x":2}}', '[NaN]', '[Infinity]', '[-Infinity]', '[1e10000]'):
            with self.subTest(text=text), self.assertRaises(LanguageError): loads_json(text)
        self.assertEqual(loads_json('{"a":[1,true,"x"]}'), {"a": [1, True, "x"]})
        with self.assertRaises(LanguageError): loads_json('{bad')

    def test_arithmetic_example_files_are_authorable_and_equivalent(self):
        directory = Path(__file__).resolve().parents[1] / "programs"
        readable = load_json(directory / "arithmetic-example.ir.json")
        numeric = load_json(directory / "arithmetic-example.ain.json")
        self.assertEqual(encode_ain(readable, {}), numeric)
        self.assertEqual(run_ir(readable, {}, [10]), 45)
        self.assertEqual(run_ain(numeric, {}, [10]), 45)


if __name__ == "__main__":
    unittest.main()
