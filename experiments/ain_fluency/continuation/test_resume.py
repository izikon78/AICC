"""Checks against saved pre-interruption prompts; no participant calls."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resume


class ContinuationChecks(unittest.TestCase):
    def test_prompt_construction_matches_all_saved_tasks_exactly(self):
        paths = list((resume.ORIGINAL / 'stages').glob('*/stage.json'))
        self.assertEqual(8, len(paths))
        for path in paths:
            row = json.loads(path.read_text(encoding='utf-8'))
            stage_dir = path.parent
            prior = ((stage_dir / 'predecessor.txt').read_text(encoding='utf-8')
                     if row['stage'] != 'build' else None)
            prep = (stage_dir / 'preparation/prompt.txt').read_text(encoding='utf-8')
            response = row['preparation_call']['attempts'][-1]['response_text']
            actual = resume.task_prompt_for(prep, response, row['mode'], row['stage'], row['delta'], prior)
            self.assertEqual((stage_dir / 'task/prompt.txt').read_text(encoding='utf-8'), actual, row['id'])

    def test_empty_rejection_is_not_a_semantic_retry(self):
        attempt = {'turn_completed': False, 'substantive_response': False,
                   'timed_out': False, 'tool_violations': []}
        self.assertTrue(resume.empty_service_rejection(attempt))
        for patch in ({'turn_completed': True}, {'substantive_response': True},
                      {'timed_out': True}, {'tool_violations': ['command_execution']}):
            self.assertFalse(resume.empty_service_rejection({**attempt, **patch}))

    def test_original_source_hashes_unchanged(self):
        manifest = json.loads((resume.ORIGINAL / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['source_sha256'], resume.frozen.source_hashes())


if __name__ == '__main__': unittest.main()
