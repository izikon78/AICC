"""Independent accounting examples: no participant model or judge execution."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fluency_report", HERE / "report.py")
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


def attempt(input_tokens=100, cached=40, output=10, reasoning=3):
    return {"usage": {"input_tokens": input_tokens, "cached_input_tokens": cached,
                      "output_tokens": output, "reasoning_output_tokens": reasoning},
            "elapsed_seconds": 2.5, "exit_code": 0, "timed_out": False,
            "tool_violations": []}


def assignments():
    records = []
    for mode in ("python", "ir", "ain"):
        for delta in (30, 75):
            for stage in ("build", "change", "repair"):
                records.append({"id": f"d{delta}-{stage}-{mode}", "mode": mode,
                                "delta": delta, "stage": stage,
                                "preparation_passed": True, "fluency_passed": True,
                                "stage_passed": True, "genuine_handoff": True,
                                "fallback": False, "judge": {"passed": True},
                                "preparation_call": {"attempts": [attempt()]},
                                "task_call": {"attempts": [attempt()]}})
    return records


class AccountingExamples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "manifest.json").write_text(json.dumps({
            "model": "fake-for-unit-tests", "effort": "ultra", "plan_commit": "pretrial",
            "harness_commit": "frozen", "order": []}), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def save(self, records):
        for index, row in enumerate(records):
            folder = self.root / "stages" / str(index)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "stage.json").write_text(json.dumps(row), encoding="utf-8")
        return report.build_summary(self.root)

    def test_complete_balanced_run_and_reasoning_not_added_twice(self):
        summary = self.save(assignments())
        self.assertEqual(summary["observed_stages"], 18)
        for mode in ("python", "ir", "ain"):
            row = summary["modes"][mode]
            self.assertEqual(row["successful_chains"], 2)
            resource = row["resources"]
            self.assertEqual(resource["attempts"], 12)
            self.assertEqual(resource["usage_totals"], {
                "input_tokens": 1200, "cached_input_tokens": 480,
                "output_tokens": 120, "reasoning_output_tokens": 36})
            # 720 uncached + .1*480 cached + 5*120 output = 1368.
            self.assertEqual(resource["normalized_costs"]["primary"], 1368)
            self.assertEqual(resource["normalized_costs"]["cache_neutral"], 1800)
            self.assertEqual(row["cost_per_assigned_stage"]["primary"], 228)
            self.assertEqual(row["cost_per_successful_chain"]["primary"], 684)
        self.assertEqual(summary["ain_saving_fraction_per_successful_chain"]["ir"]["primary"], 0)

    def test_infrastructure_retry_is_not_free(self):
        rows = assignments()
        row = next(row for row in rows if row["mode"] == "ain")
        retry = attempt()
        retry["exit_code"] = 1
        row["preparation_call"]["attempts"].insert(0, retry)
        summary = self.save(rows)
        ain = summary["modes"]["ain"]
        self.assertEqual(ain["resources"]["attempts"], 13)
        self.assertEqual(ain["resources"]["normalized_costs"]["primary"], 1482)
        self.assertAlmostEqual(summary["ain_saving_fraction_per_successful_chain"]["ir"]["primary"], -1 / 12)

    def test_fallback_success_still_excludes_primary_chain(self):
        rows = assignments()
        repair = next(row for row in rows if row["mode"] == "ain" and row["stage"] == "repair")
        repair["fallback"] = True
        repair["genuine_handoff"] = False
        summary = self.save(rows)
        ain = summary["modes"]["ain"]
        self.assertEqual(ain["functional_passes"], 6)
        self.assertEqual(ain["diagnostic_repair_passes"], 2)
        self.assertEqual(ain["successful_chains"], 1)
        self.assertEqual(ain["cost_per_successful_chain"]["primary"], 1368)
        self.assertEqual(summary["ain_saving_fraction_per_successful_chain"]["ir"]["primary"], -1)

    def test_zero_successes_never_means_zero_cost(self):
        rows = assignments()
        for row in rows:
            if row["mode"] == "ain":
                row["preparation_passed"] = False
        summary = self.save(rows)
        ain = summary["modes"]["ain"]
        self.assertEqual(ain["successful_chains"], 0)
        self.assertEqual(ain["resources"]["normalized_costs"]["primary"], 1368)
        self.assertIsNone(ain["cost_per_successful_chain"]["primary"])
        self.assertIsNone(summary["ain_saving_fraction_per_successful_chain"]["ir"]["primary"])

    def test_missing_whole_usage_is_unknown_and_preserves_known_subtotals(self):
        rows = assignments()
        rows[0]["task_call"]["attempts"][0]["usage"] = None
        summary = self.save(rows)
        resource = summary["modes"]["python"]["resources"]
        self.assertFalse(resource["complete"])
        self.assertIsNone(resource["usage_totals"]["input_tokens"])
        self.assertEqual(resource["known_usage_subtotals"]["input_tokens"], 1100)
        self.assertEqual(resource["missing_counters_by_attempt"]["input_tokens"], 1)
        self.assertTrue(all(value is None for value in resource["normalized_costs"].values()))

    def test_optional_reasoning_unknown_does_not_destroy_known_cost(self):
        rows = assignments()
        del rows[0]["task_call"]["attempts"][0]["usage"]["reasoning_output_tokens"]
        resource = self.save(rows)["modes"]["python"]["resources"]
        self.assertFalse(resource["complete"])
        self.assertIsNone(resource["usage_totals"]["reasoning_output_tokens"])
        self.assertEqual(resource["normalized_costs"]["primary"], 1368)

    def test_missing_cached_count_only_invalidates_costs_that_use_cache(self):
        rows = assignments()
        del rows[0]["task_call"]["attempts"][0]["usage"]["cached_input_tokens"]
        resource = self.save(rows)["modes"]["python"]["resources"]
        self.assertIsNone(resource["normalized_costs"]["primary"])
        self.assertEqual(resource["normalized_costs"]["cache_neutral"], 1800)

    def test_missing_assignment_is_incomplete_not_a_success(self):
        rows = assignments()
        rows.pop(0)
        summary = self.save(rows)
        python = summary["modes"]["python"]
        self.assertEqual(python["successful_chains"], 1)
        self.assertFalse(python["assignments_complete"])
        self.assertIsNone(python["resources"]["normalized_costs"]["primary"])
        self.assertEqual(summary["missing_assignments"], [("python", 30, "build")])

    def test_duplicate_record_counts_resources_but_cannot_create_chain(self):
        rows = assignments()
        rows.append(deepcopy(rows[0]))
        summary = self.save(rows)
        python = summary["modes"]["python"]
        self.assertEqual(python["resources"]["attempts"], 14)
        self.assertEqual(python["successful_chains"], 1)
        self.assertIsNone(python["resources"]["normalized_costs"]["primary"])
        self.assertEqual(summary["duplicate_assignments"], [("python", 30, "build")])

    def test_tool_violation_disqualifies_even_if_declared_stage_passes(self):
        rows = assignments()
        rows[0]["task_call"]["attempts"][0]["tool_violations"] = ["command_execution"]
        summary = self.save(rows)
        self.assertEqual(summary["modes"]["python"]["successful_chains"], 1)
        self.assertEqual(summary["modes"]["python"]["stage_passes"], 5)

    def test_invalid_cache_subset_not_reported_as_primary_saving(self):
        rows = assignments()
        rows[0]["task_call"]["attempts"][0]["usage"]["cached_input_tokens"] = 101
        resource = self.save(rows)["modes"]["python"]["resources"]
        self.assertIsNone(resource["normalized_costs"]["primary"])
        self.assertEqual(resource["normalized_costs"]["cache_neutral"], 1800)
        self.assertTrue(resource["issues"])

    def test_markdown_and_json_are_writable_for_zero_successes(self):
        rows = assignments()
        for row in rows:
            row["genuine_handoff"] = False
        self.save(rows)
        summary = report.write_report(self.root, charts=False)
        self.assertEqual(summary["figures"], [])
        parsed = json.loads((self.root / "summary.json").read_text(encoding="utf-8"))
        self.assertIsNone(parsed["modes"]["ain"]["cost_per_successful_chain"]["primary"])
        text = (self.root / "RESULTS.md").read_text(encoding="utf-8")
        self.assertIn("undefined / incomplete", text)
        self.assertIn("not dollar charges or realized savings", text)
        self.assertIn("two paired", text)


if __name__ == "__main__":
    unittest.main()
