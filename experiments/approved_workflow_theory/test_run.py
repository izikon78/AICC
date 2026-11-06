from copy import deepcopy
import unittest

from experiments.approved_workflow_theory.run import (
    episode, parse_python_program, patch_for, python_program,
)
from experiments.approved_workflow_theory.workloads import execute, expected, make_chains


class TraceTests(unittest.TestCase):
    def test_python_alias_and_descriptive_renderings_execute_same_plan(self):
        for chain in make_chains():
            for stage in chain["stages"]:
                for aliases in (False, True):
                    plan = parse_python_program(python_program(stage["plan"], aliases), aliases)
                    self.assertEqual(plan, stage["plan"])
                    self.assertEqual(execute(plan, stage["task"]), expected(stage["task"]))

    def test_change_and_repair_each_need_one_patch_and_handoff_reuses(self):
        for chain in make_chains():
            build, change, repair, handoff = chain["stages"]
            self.assertEqual(len(patch_for(build["plan"], change["plan"])), 1)
            self.assertEqual(len(patch_for(repair["broken_plan"], repair["plan"])), 1)
            self.assertEqual(patch_for(repair["plan"], handoff["plan"]), [])

    def test_history_is_reprocessed_and_equal_ideal_controls_tie(self):
        chain = make_chains()[0]
        stage = chain["stages"][0]
        before = deepcopy(stage)
        record, artifact, memory = episode(chain, stage, [], {}, "resident")
        self.assertEqual(stage, before)
        self.assertTrue(record["success"])
        self.assertEqual(artifact, stage["plan"])
        self.assertTrue(memory["checks_passed"])
        profiles = {profile: [row for row in record["ledger"] if row["profile"] == profile]
                    for profile in ("ideal_ain", "ideal_ir", "ideal_python")}
        for turn in range(3):
            counts = [{key: value for key, value in profiles[profile][turn].items() if key != "profile"}
                      for profile in profiles]
            self.assertEqual(counts[0], counts[1])
            self.assertEqual(counts[0], counts[2])
        rows = profiles["ideal_ain"]
        self.assertEqual(rows[0]["reprocessed_history_units"], 0)
        self.assertEqual(rows[1]["reprocessed_history_units"],
                         rows[0]["output_positions"] + rows[0]["host_observation_units"])
        self.assertGreater(rows[2]["reprocessed_history_units"], rows[1]["reprocessed_history_units"])
        inspected, _, _ = episode(chain, stage, [], {}, "inspect")
        self.assertGreater(inspected["ledger"][0]["common_input_text_tokens"],
                           record["ledger"][0]["common_input_text_tokens"])


if __name__ == "__main__":
    unittest.main()
