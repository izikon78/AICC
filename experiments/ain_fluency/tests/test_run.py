"""Metering/parser controls, not participant outcomes."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import run


class MeteringTests(unittest.TestCase):
    def test_seeded_schedule_has_all_assigned_stages_in_order(self):
        order = run.schedule()
        self.assertEqual(18, len(order))
        self.assertEqual(18, len({x['id'] for x in order}))
        for mode in ('python', 'ir', 'ain'):
            for delta in (30, 75):
                self.assertEqual(['build', 'change', 'repair'],
                                 [x['stage'] for x in order if x['mode'] == mode and x['delta'] == delta])

    def test_usage_keeps_reasoning_and_cached_subsets_raw(self):
        usage = {'input_tokens': 100, 'cached_input_tokens': 80,
                 'output_tokens': 30, 'reasoning_output_tokens': 20}
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"x":1}'}},
                  {'type': 'turn.completed', 'usage': usage}]
        result = run.parse_events('\n'.join(json.dumps(e) for e in events))
        self.assertEqual(usage, result['usage'])
        self.assertEqual([], result['tool_violations'])

    def test_missing_completion_has_unknown_usage(self):
        result = run.parse_events('{"type":"turn.started"}\npartial')
        self.assertIsNone(result['usage'])
        self.assertFalse(result['turn_completed'])
        self.assertEqual(1, result['invalid_jsonl_lines'])

    def test_tool_use_is_flagged(self):
        result = run.parse_events(json.dumps({'type': 'item.started', 'item': {'type': 'command_execution'}}))
        self.assertEqual(['command_execution'], result['tool_violations'])

    def test_fluency_requires_exact_types(self):
        answer = run.tasks.expected_fluency()
        self.assertTrue(run.score_fluency({'fluency': answer}))
        answer['sum_0_to_4'] = True
        self.assertFalse(run.score_fluency({'fluency': answer}))

    def test_only_exhausted_empty_infrastructure_failure_stops_service(self):
        attempt = {'turn_completed': False, 'substantive_response': False,
                   'timed_out': False, 'tool_violations': []}
        self.assertFalse(run.service_failed({'attempts': [attempt]}))
        self.assertTrue(run.service_failed({'attempts': [attempt, attempt]}))
        for patch in ({'timed_out': True}, {'turn_completed': True},
                      {'substantive_response': True}, {'tool_violations': ['command_execution']}):
            self.assertFalse(run.service_failed({'attempts': [attempt, {**attempt, **patch}]}))


if __name__ == '__main__':
    unittest.main()
