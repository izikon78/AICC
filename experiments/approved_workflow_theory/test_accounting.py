"""Regression checks for the conditional code-unit ledger."""
import math
import unittest

from experiments.approved_workflow_theory.accounting import (
    MAX_LENGTH, PAYLOAD_ENTRIES, TYPE_ENTRIES, VOCABULARY_SIZE,
    count_call_stream, count_ideal, measure_message, text_token_count,
)


class AccountingTests(unittest.TestCase):
    def test_every_key_container_and_new_literal_is_charged(self):
        count = count_ideal({"op": "filter_eq", "args": ["new", 12]},
                            {"op", "args", "filter_eq"})
        # Two containers, three static names, two scalar headers/lengths,
        # and ceil(24/15) + ceil(16/15) packed literal payload units.
        self.assertEqual(count["static_units"], 3)
        self.assertEqual(count["structure_units"], 8)
        self.assertEqual(count["literal_utf8_bytes"], 5)
        self.assertEqual(count["literal_units"], 4)
        self.assertEqual(count["units"], 15)
        self.assertEqual(count["byte_fallback_units"], 16)
        self.assertEqual(count_ideal([True, False, None], set())["units"], 5)

    def test_new_literal_information_increases_the_count(self):
        small = count_ideal({"value": "a"}, {"value"})
        large = count_ideal({"value": "abcdefghij"}, {"value"})
        unicode_value = count_ideal("é", set())
        self.assertGreater(large["units"], small["units"])
        self.assertEqual(unicode_value["literal_utf8_bytes"], 2)
        self.assertEqual(unicode_value["literal_units"], 2)

    def test_static_renaming_and_equal_semantic_controls_match(self):
        verbose = {"approved_operation": ["approved_argument", 127]}
        compact = {"a": ["b", 127]}
        self.assertEqual(count_ideal(verbose, {"approved_operation", "approved_argument"}),
                         count_ideal(compact, {"a", "b"}))
        result = measure_message(verbose, "approved_operation(127)",
                                 {"approved_operation", "approved_argument"})
        self.assertEqual(result["ideal_ain_units"], result["ideal_ir_units"])
        self.assertEqual(result["ideal_ain_units"], result["ideal_python_units"])

    def test_fixed_capacity_and_payload_bounds_are_enforced(self):
        count = count_ideal("a" * MAX_LENGTH, set())
        self.assertEqual(count["literal_units"], math.ceil(MAX_LENGTH * 8 / 15))
        with self.assertRaises(ValueError):
            count_ideal("a" * (MAX_LENGTH + 1), set())
        with self.assertRaises(ValueError):
            count_ideal([None] * (MAX_LENGTH + 1), set())
        capacity = VOCABULARY_SIZE - PAYLOAD_ENTRIES - TYPE_ENTRIES
        count_ideal(None, {f"symbol_{index}" for index in range(capacity)})
        with self.assertRaises(ValueError):
            count_ideal(None, {f"symbol_{index}" for index in range(capacity + 1)})

    def test_invalid_values_and_cycles_fail(self):
        cycle = []
        cycle.append(cycle)
        for value in (float("nan"), float("inf"), {1: "invalid"}, cycle):
            with self.subTest(value=type(value).__name__):
                with self.assertRaises((TypeError, ValueError)):
                    count_ideal(value, set())
        with self.assertRaises(TypeError):
            count_ideal("x", {17})

    def test_cached_tokenizer_counts_are_separately_observed(self):
        self.assertEqual(text_token_count("x+7-4"), 5)
        self.assertEqual(text_token_count("2 7;3 4"), 7)

    def test_approved_call_stream_charges_opcode_and_each_typed_operand(self):
        schema = {"filter_gte": ("field", "value"), "project": ("fields",)}
        plan = [{"op": "filter_gte", "args": {"value": 12, "field": "severity"}}]
        count = count_call_stream(plan, {"severity"}, schema)
        self.assertEqual(count["units"], 4)  # length, operation, field, signed integer
        self.assertEqual(count["literal_units"], 1)
        self.assertEqual(count["literal_utf8_bytes"], 2)
        reordered = [{"op": "filter_gte", "args": {"field": "severity", "value": 12}}]
        self.assertEqual(count, count_call_stream(reordered, {"severity"}, schema))
        projection = [{"op": "project", "args": {"fields": ["severity", "id"]}}]
        self.assertEqual(count_call_stream(projection, {"severity", "id"}, schema)["units"], 5)

    def test_call_stream_fallback_and_schema_reject_hidden_operands(self):
        schema = {"take": ("value",)}
        for value in (-16_384, 16_383):
            count = count_call_stream([{"op": "take", "args": {"value": value}}], set(), schema)
            self.assertEqual(count["units"], 3)
        large = count_call_stream([{"op": "take", "args": {"value": 16_384}}], set(), schema)
        self.assertGreater(large["units"], 3)
        for call in ({"op": "take", "args": {}},
                     {"op": "take", "args": {"value": 1, "extra": "hidden"}},
                     {"op": "unknown", "args": {"value": 1}}):
            with self.assertRaises(ValueError):
                count_call_stream([call], set(), schema)


if __name__ == "__main__":
    unittest.main()
