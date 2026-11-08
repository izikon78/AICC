"""Focused semantic and isolation checks for the scalar gate data/judge."""
import json
from collections import Counter
import unittest

from experiments.native_learning_gate.data import ARMS, format_prompt, judge, make_dataset


class DataTests(unittest.TestCase):
    def test_every_target_executes_against_independent_oracle(self):
        for row in make_dataset():
            for arm in ARMS:
                with self.subTest(row=row["id"], arm=arm):
                    self.assertEqual(judge(arm, row["targets"][arm], row),
                                     {"syntax_ok": True, "correct": True, "error": None})

    def test_split_sizes_constants_and_structure_contract(self):
        rows = make_dataset()
        self.assertEqual(rows, make_dataset())
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        self.assertEqual(Counter(row["split"] for row in rows),
                         {"train": 96, "dev": 12, "holdout": 12})
        train = [row for row in rows if row["split"] == "train"]
        dev = [row for row in rows if row["split"] == "dev"]
        holdout = [row for row in rows if row["split"] == "holdout"]
        self.assertTrue({constant for row in train for _, constant in row["steps"]}.isdisjoint(
            {constant for row in dev for _, constant in row["steps"]}))
        self.assertTrue({row["family"] for row in train}.isdisjoint(
            {row["family"] for row in holdout}))
        for row in rows:
            for arm in ARMS:
                self.assertNotIn("{format}", format_prompt(row, arm))

    def test_wrong_executable_program_fails_correctness(self):
        row = make_dataset()[0]
        wrong = judge("python", "def solve(x):\n    return x - 1", row)
        self.assertTrue(wrong["syntax_ok"])
        self.assertFalse(wrong["correct"])
        numeric = json.loads(row["targets"]["ain"])
        numeric[6][0][0][0][2] = 99
        self.assertFalse(judge("ain", json.dumps(numeric), row)["correct"])

    def test_python_source_cannot_execute_effects_or_escape_restricted_ast(self):
        row = make_dataset()[0]
        hostile = (
            "import os\ndef solve(x):\n    return x + 1",
            "def solve(x):\n    return __import__('os').getcwd()",
            "def solve(x):\n    return x.__class__",
            "def solve(x):\n    return True",
            "def solve(x=open('probe', 'w')):\n    return x",
            "@print\ndef solve(x):\n    return x",
            "def solve(x):\n    while True: pass\n    return x",
        )
        for source in hostile:
            with self.subTest(source=source):
                result = judge("python", source, row)
                self.assertFalse(result["syntax_ok"])
                self.assertFalse(result["correct"])

    def test_invalid_json_and_equivalent_python_expression(self):
        row = make_dataset()[0]
        self.assertFalse(judge("ir", '{"version":0,"version":0}', row)["syntax_ok"])
        self.assertFalse(judge("ain", "[]", row)["syntax_ok"])
        self.assertTrue(judge("python", "def solve(x):\n    return 1 + x", row)["correct"])


if __name__ == "__main__":
    unittest.main()
