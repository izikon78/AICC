"""Semantic and rejection checks for the bounded comparison apparatus."""
import unittest
from experiments.representation_comparison.run import (
    PROFILES, actions_text, decode_actions, decode_program, decode_state, equal, program, state_text,
)


class ComparisonTests(unittest.TestCase):
    def test_new_literals_delimiters_types_and_nested_actions_survive(self):
        values = ["用户🧪;^[r];}", ["é", False, None, -16385], {"fresh": True, "n": 1}]
        for profile in PROFILES:
            for value in values:
                plan = [{"op": "filter_eq", "args": {"field": "new", "value": value}}]
                actions = [{"op": "write", "args": {"program": plan}}, {"op": "check", "args": {}}]
                self.assertTrue(equal(plan, decode_program(program(plan, profile), profile)))
                self.assertTrue(equal(actions, decode_actions(actions_text(actions, profile), profile)))
                self.assertTrue(equal(value, decode_state(state_text(value, profile), profile)))

    def test_python_decoder_rejects_effects_and_unapproved_structure(self):
        cases = ["lambda r:__import__('os')", "lambda r:r.__class__", "lambda r=1:r", "lambda r,*x:r", "lambda x:x"]
        for value in cases:
            with self.subTest(value=value), self.assertRaises((ValueError, SyntaxError)):
                decode_program(value, "python_compact")
        for value in ["import os", "x=1", "__import__('os')", "a(r,field='id')"]:
            with self.subTest(value=value), self.assertRaises((ValueError, SyntaxError)):
                decode_actions(value, "python_repr")

    def test_unknown_ids_wrong_arities_and_trailing_code_rejected(self):
        for profile, value in [("numeric_arrays", "[[999,1]]"), ("readable_ir", '[["filter_eq","x"]]'),
                               ("symbolic_ain", "@0(r){r=!999(r);^[r];}"),
                               ("symbolic_ain", "@0(r){^[r];}extra")]:
            with self.subTest(profile=profile), self.assertRaises(ValueError): decode_program(value, profile)

    def test_type_and_continuation_state_are_not_collapsed(self):
        self.assertFalse(equal(True, 1))
        for profile in PROFILES:
            a = decode_state(state_text({"seen": ["a"], "last_output": []}, profile), profile)
            b = decode_state(state_text({"seen": [], "last_output": []}, profile), profile)
            self.assertIn("a", a["seen"])
            self.assertNotIn("a", b["seen"])


if __name__ == "__main__": unittest.main()
