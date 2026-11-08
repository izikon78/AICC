from copy import deepcopy
import unittest

from experiments.approved_workflow_theory.workloads import (
    CATALOG, bounded_retry, catalog_sources, execute, expected, make_chains,
)


class WorkflowTests(unittest.TestCase):
    def test_all_72_workflow_stages_match_independent_oracles(self):
        chains = make_chains()
        self.assertEqual(len(chains), 18)
        self.assertEqual({chain["domain"] for chain in chains}, {"events", "cache", "publication"})
        for chain in chains:
            self.assertEqual([stage["stage"] for stage in chain["stages"]],
                             ["build", "change", "repair", "handoff"])
            for stage in chain["stages"]:
                with self.subTest(chain=chain["id"], stage=stage["stage"]):
                    self.assertEqual(execute(stage["plan"], stage["task"]), expected(stage["task"]))

    def test_changes_have_observable_effects_and_broken_predecessors_fail(self):
        for chain in make_chains():
            build, change, repair, handoff = chain["stages"]
            self.assertNotEqual(expected(build["task"]), expected(change["task"]))
            self.assertNotEqual(execute(repair["broken_plan"], repair["task"]), expected(repair["task"]))
            self.assertEqual(expected(repair["task"]), expected(handoff["task"]))

    def test_event_order_boundary_and_cache_version_ties(self):
        chains = {chain["id"]: chain for chain in make_chains()}
        events = chains["events-00"]["stages"][0]
        self.assertEqual(execute(events["plan"], events["task"]),
                         [{"group": "A", "total": 8}, {"group": "B", "total": 20}])
        cache = chains["cache-00"]["stages"][0]
        self.assertEqual(execute(cache["plan"], cache["task"]),
                         [{"key": "alpha", "value": "new-0", "version": 2},
                          {"key": "delta", "value": "first", "version": 7}])

    def test_retry_while_loop_success_exhaustion_and_exact_delays(self):
        rows = [{"id": "success", "failures": 2}, {"id": "exhaust", "failures": 3}]
        result = bounded_retry(rows, limit=3, base_delay=5)
        self.assertEqual([(row["attempts"], row["delays"], row["committed"]) for row in result],
                         [(3, [5, 10], True), (3, [5, 10], False)])
        for limit in (0, 17, True):
            with self.assertRaises(ValueError):
                bounded_retry(rows, limit=limit, base_delay=1)

    def test_plans_reject_unknown_capabilities_and_mutate_no_inputs(self):
        stage = make_chains()[0]["stages"][0]
        original = deepcopy(stage)
        execute(stage["plan"], stage["task"])
        self.assertEqual(stage, original)
        for plan in ([{"op": "unknown", "args": {}}],
                     [{"op": "dedupe_by", "args": {}}],
                     [{"op": "sort_by", "args": {"field": "id"}, "extra": 1}]):
            with self.assertRaises(ValueError):
                execute(plan, stage["task"])
        self.assertEqual(set(catalog_sources()), set(CATALOG) | {"_integer"})
        self.assertIn("while attempts < limit", catalog_sources()["bounded_retry"])


if __name__ == "__main__":
    unittest.main()
