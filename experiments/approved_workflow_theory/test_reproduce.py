import tempfile
from pathlib import Path
import unittest

from experiments.approved_workflow_theory.reproduce import (
    REFERENCE, canonical_episodes, canonical_hash, compare,
    first_difference, read_json, write_json,
)


class ReproductionTests(unittest.TestCase):
    def test_canonical_json_hash_ignores_mapping_order(self):
        self.assertEqual(canonical_hash({"a": 1, "b": [2]}),
                         canonical_hash({"b": [2], "a": 1}))
        difference = first_difference({"value": [1, 2]}, {"value": [1, 9]})
        self.assertEqual(difference["path"], "$.value[1]")

    def test_runtime_exclusion_is_limited_to_episode_timing(self):
        episode = {"execution_seconds": 1.0, "ledger": [{"input_positions": 3}],
                   "common_input": {"execution_seconds": "business literal"}}
        result = canonical_episodes([episode])[0]
        self.assertNotIn("execution_seconds", result)
        self.assertEqual(result["common_input"]["execution_seconds"], "business literal")
        self.assertIn("execution_seconds", episode)

    def test_independent_comparison_accepts_exact_ledgers_and_rejects_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            totals = read_json(REFERENCE / "totals.json")
            episodes = canonical_episodes(read_json(REFERENCE / "episodes.json"))
            write_json(directory / "totals.json", totals)
            write_json(directory / "episodes.json", episodes)
            self.assertTrue(compare(directory, independent=True)["matches_reference"])
            episodes[0]["ledger"][0]["input_positions"] += 1
            write_json(directory / "episodes.json", episodes)
            result = compare(directory, independent=True)
            self.assertFalse(result["matches_reference"])
            self.assertEqual(result["checks"]["episodes.json"]["first_difference"]["path"],
                             "$[0].ledger[0].input_positions")

    def test_missing_independent_results_fail_comparison(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = compare(Path(temporary), independent=True)
            self.assertFalse(result["matches_reference"])
            self.assertEqual(result["checks"]["totals.json"]["error"], "missing output file")

    def test_malformed_independent_output_is_recorded_as_a_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "totals.json").write_text("{", encoding="utf-8")
            write_json(directory / "episodes.json", [{"chain": "incomplete"}])
            result = compare(directory, independent=True)
            self.assertFalse(result["matches_reference"])
            self.assertIn("JSONDecodeError", result["checks"]["totals.json"]["error"])
            self.assertIn("KeyError", result["checks"]["episodes.json"]["error"])
            self.assertFalse(read_json(directory / "comparison.json")["matches_reference"])


if __name__ == "__main__":
    unittest.main()
