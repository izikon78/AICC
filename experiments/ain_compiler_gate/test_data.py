"""Checks for matched semantic data and native executable judgments."""
from collections import Counter
import unittest

from experiments.ain_compiler_gate.data import ARMS, format_prompt, judge, make_dataset
from experiments.native_learning_gate.data import make_dataset as make_legacy_dataset


class DataTests(unittest.TestCase):
    def test_compact_rows_preserve_prior_tasks_and_splits(self):
        rows = make_dataset()
        legacy_rows = make_legacy_dataset()
        self.assertEqual(rows, make_dataset())
        self.assertEqual(Counter(row["split"] for row in rows),
                         {"train": 96, "dev": 12, "holdout": 12})
        for row, legacy in zip(rows, legacy_rows, strict=True):
            for field in ("id", "split", "family", "steps"):
                self.assertEqual(row[field], legacy[field])
            self.assertEqual(row["legacy_targets"], legacy["targets"])
            for arm in ARMS:
                prompt = format_prompt(row, arm)
                self.assertNotIn("{format}", prompt)
                self.assertTrue(prompt.endswith("\n"))

    def test_every_compact_target_executes_as_machine_code(self):
        for row in make_dataset():
            for arm in ARMS:
                with self.subTest(row=row["id"], arm=arm):
                    result = judge(arm, row["targets"][arm], row)
                    self.assertTrue(result["syntax_ok"], result["error"])
                    self.assertTrue(result["correct"], result["error"])
                    self.assertGreaterEqual(result["compiler_seconds"], 0)
                    self.assertEqual(len(result["assembly_sha256"]), 64)

    def test_wrong_valid_program_fails_semantic_judge(self):
        row = make_dataset()[0]
        for arm, source in (("python", "x-1"), ("ir", "sub 1"), ("ain", "3 1")):
            with self.subTest(arm=arm):
                result = judge(arm, source, row)
                self.assertTrue(result["syntax_ok"])
                self.assertFalse(result["correct"])
                self.assertIn("wrong result", result["error"])

    def test_unsafe_and_invalid_sources_fail_before_execution(self):
        row = make_dataset()[0]
        cases = (("python", "__import__('os').getcwd()"),
                 ("python", "x.__class__"),
                 ("python", "x*2"),
                 ("ir", "call system"),
                 ("ir", "add 1000001"),
                 ("ain", "8 1"),
                 ("ain", "2 1;garbage"))
        for arm, source in cases:
            with self.subTest(arm=arm, source=source):
                result = judge(arm, source, row)
                self.assertFalse(result["syntax_ok"])
                self.assertFalse(result["correct"])
                self.assertIsNone(result["assembly_sha256"])


if __name__ == "__main__":
    unittest.main()
