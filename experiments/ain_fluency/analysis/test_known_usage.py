"""Synthetic accounting/bound examples; never execute a participant model."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("known_usage", Path(__file__).with_name("known_usage.py"))
analysis = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(analysis)


def attempt(scale=1):
    return {"usage": {"input_tokens": round(100 * scale),
                      "cached_input_tokens": round(40 * scale),
                      "output_tokens": round(10 * scale), "reasoning_output_tokens": 3},
            "exit_code": 0, "tool_violations": [], "turn_completed": True}


def records(ain_scale=1):
    rows = []
    for mode in ("python", "ir", "ain"):
        for delta in (30, 75):
            for stage in ("build", "change", "repair"):
                rows.append({"id": f"d{delta}-{stage}-{mode}", "mode": mode,
                             "delta": delta, "stage": stage, "stage_passed": True,
                             "preparation_passed": True, "fluency_passed": True,
                             "judge": {"passed": True}, "genuine_handoff": True,
                             "fallback": False,
                             "preparation_call": {"attempts": [attempt(ain_scale if mode == "ain" else 1)]},
                             "task_call": {"attempts": [attempt(ain_scale if mode == "ain" else 1)]}})
    return rows


def add_unmetered(rows):
    row = next(row for row in rows if row["mode"] == "ain")
    unknown = {"usage": None, "exit_code": 1, "tool_violations": [], "turn_completed": False}
    row["task_call"]["attempts"][:0] = [deepcopy(unknown), deepcopy(unknown)]


class KnownUsageBounds(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.manifest = {"status": "complete_amended_continuation", "plan_commit": "pretrial",
                         "harness_commit": "frozen", "continuation_commit": "amended"}

    def tearDown(self):
        self.temp.cleanup()

    def save(self, rows):
        (self.root / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        for index, row in enumerate(rows):
            folder = self.root / "stages" / str(index)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "stage.json").write_text(json.dumps(row), encoding="utf-8")
        return analysis.analyze(self.root)

    def test_known_subtotal_bound_is_not_a_missing_usage_point_estimate(self):
        rows = records(.8)
        add_unmetered(rows)
        result = self.save(rows)
        ain = result["modes"]["ain"]
        cost = ain["costs"]["primary"]
        self.assertEqual(ain["attempts"], 14)
        self.assertEqual(ain["wholly_unmetered_attempts"], 2)
        self.assertAlmostEqual(cost["known_metered_subtotal"], 1094.4)
        self.assertAlmostEqual(cost["cost_lower_bound"], 1094.4)
        self.assertIsNone(cost["exact_total"])
        self.assertIsNone(ain["exact_token_totals"]["input_tokens"])
        self.assertEqual(ain["known_token_subtotals"]["input_tokens"], 960)
        bound = result["ain_savings_upper_bounds_per_assigned_stage"]["ir"]["primary"]
        self.assertAlmostEqual(bound["savings_upper_bound_fraction"], .2)
        self.assertIsNone(bound["point_savings_estimate"])

    def test_failure_with_known_usage_is_retained(self):
        rows = records()
        failed = attempt()
        failed["exit_code"] = 1
        rows[0]["task_call"]["attempts"].insert(0, failed)
        result = self.save(rows)
        self.assertEqual(result["modes"]["python"]["attempts"], 13)
        self.assertEqual(result["modes"]["python"]["costs"]["primary"]["exact_total"], 1482)

    def test_fallback_harness_eligibility_separate_from_functional_passes(self):
        rows = records(.8)
        add_unmetered(rows)
        repair = next(row for row in rows if row["mode"] == "ain" and row["stage"] == "repair")
        repair.update(fallback=True, genuine_handoff=False)
        result = self.save(rows)
        ain = result["modes"]["ain"]
        self.assertEqual(ain["functional_stage_passes"], 6)
        self.assertEqual(ain["full_stage_passes"], 6)
        self.assertEqual(ain["successful_chains"], 1)
        self.assertEqual(ain["fallback_stages"], 1)
        self.assertAlmostEqual(result["ain_savings_upper_bounds_per_assigned_stage"]["ir"]["primary"]
                               ["savings_upper_bound_fraction"], .2)
        self.assertAlmostEqual(result["ain_savings_upper_bounds_per_primary_chain"]["ir"]["primary"]
                               ["savings_upper_bound_fraction"], -.6)

    def test_zero_success_makes_primary_comparison_undefined(self):
        rows = records()
        for row in rows:
            if row["mode"] == "ain":
                row["preparation_passed"] = False
        result = self.save(rows)
        self.assertEqual(result["modes"]["ain"]["successful_chains"], 0)
        self.assertIsNone(result["ain_savings_upper_bounds_per_primary_chain"]["ir"]["primary"]
                          ["savings_upper_bound_fraction"])
        self.assertEqual(result["ain_savings_upper_bounds_per_assigned_stage"]["ir"]["primary"]
                         ["savings_upper_bound_fraction"], 0)

    def test_incomplete_baseline_does_not_yield_savings_bound(self):
        rows = records()
        rows[0]["task_call"]["attempts"][0]["usage"] = None
        result = self.save(rows)
        self.assertIsNone(result["ain_savings_upper_bounds_per_assigned_stage"]["python"]["primary"]
                          ["savings_upper_bound_fraction"])
        self.assertIsNone(result["ain_savings_upper_bounds_per_primary_chain"]["python"]["primary"]
                          ["savings_upper_bound_fraction"])

    def test_zero_cost_baseline_has_no_ratio(self):
        rows = records()
        for row in rows:
            if row["mode"] == "ir":
                for kind in ("preparation_call", "task_call"):
                    row[kind]["attempts"][0] = attempt(0)
        result = self.save(rows)
        self.assertIsNone(result["ain_savings_upper_bounds_per_assigned_stage"]["ir"]["primary"]
                          ["savings_upper_bound_fraction"])

    def test_partial_categories_use_valid_conservative_cost_bounds(self):
        # Known input 100, unknown cache: it could all be cached, giving 10,
        # rather than an unjustified uncached-input cost of 100.
        value = analysis._cost({"input_tokens": 100, "output_tokens": 10}, .1, 5)
        self.assertFalse(value["complete"])
        self.assertEqual(value["known_metered_subtotal"], 0)
        self.assertEqual(value["lower_bound"], 60)
        # Known cache 40 requires at least 40 input; its contribution is 4.
        value = analysis._cost({"cached_input_tokens": 40, "output_tokens": 10}, .1, 5)
        self.assertEqual(value["lower_bound"], 54)
        # Cache-neutral cost needs no cache counter.
        value = analysis._cost({"input_tokens": 100, "output_tokens": 10}, 1, 5)
        self.assertTrue(value["complete"])
        self.assertEqual(value["lower_bound"], 150)

    def test_invalid_cache_subset_rejected(self):
        with self.assertRaisesRegex(ValueError, "Cached input exceeds"):
            analysis._cost({"input_tokens": 10, "cached_input_tokens": 11, "output_tokens": 0}, .1, 5)

    def test_analysis_refuses_running_or_partial_dataset(self):
        self.manifest["status"] = "running"
        with self.assertRaisesRegex(ValueError, "complete_amended_continuation"):
            self.save(records())

    def test_all_assignments_required_no_selected_subset(self):
        with self.assertRaisesRegex(ValueError, "18 unique"):
            self.save(records()[:-1])

    def test_markdown_keeps_bounds_distinct_from_primary_outcome(self):
        rows = records(.8)
        add_unmetered(rows)
        self.save(rows)
        result = analysis.write_analysis(self.root, charts=False)
        output = self.root / "analysis"
        self.assertEqual(result["figures"], [])
        text = (output / "KNOWN_USAGE.md").read_text(encoding="utf-8")
        self.assertIn("2 wholly unmetered", text)
        self.assertIn("not the success-adjusted primary savings outcome", text)
        self.assertIn("≤ +20.0%", text)
        self.assertIn("harness limitation", text)
        self.assertIn("not invoices or dollar", text)


if __name__ == "__main__":
    unittest.main()
