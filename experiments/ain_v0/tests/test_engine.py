"""Expected-case workflow conformance, including state/effect adversaries.

Cross-representation agreement shares the host. Golden expectations here test
observable semantics in addition to agreement; they are same-session development
evidence, not a blinded language experiment or a security certification.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import threading
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
from ain.engine import Config, Host, Sink, WorkflowError, checkpoint_integrity
from ain.runner import execute
from ain import reference
from fixtures import (
    MODES, MAX_I64, REPORT_GROUP_FIELDS, event, watermark, end, expected_group,
    counters, constant_policy, contract_trace,
)


class WorkflowConformanceTests(unittest.TestCase):
    def run_mode(self, records, mode, **options):
        options.setdefault('policy', constant_policy())
        return execute(deepcopy(records), mode=mode, **options)

    def assert_success(self, result, groups, counts, status='COMPLETE'):
        self.assertEqual(result['status'], status, result)
        self.assertIsNone(result['error'])
        self.assertEqual(result['counters'], counts)
        projected = [{key: report[key] for key in REPORT_GROUP_FIELDS} for report in result['reports']]
        self.assertEqual(projected, groups)
        allowed = set(REPORT_GROUP_FIELDS) | {'source_id', 'group_id', 'score', 'reason', 'policy_version'}
        for report in result['reports']:
            self.assertEqual(set(report), allowed)
            self.assertEqual(report['source_id'], 'default')
            self.assertEqual((report['score'], report['reason'], report['policy_version']), (77, 2, 'fixture-v1'))
            self.assertEqual(len(report['group_id']), 64)
            int(report['group_id'], 16)

    def assert_error(self, result, code, reports=0):
        self.assertEqual(result['status'], 'ERROR', result)
        self.assertEqual(result['error']['code'], code, result)
        self.assertEqual(len(result['reports']), reports)

    def test_documented_ten_record_trace_has_explicit_outputs_and_effects(self):
        groups = [expected_group(150, 200, 4, 2, 3), expected_group(780, 780, 7, 1, 3),
                  expected_group(1400, 1400, 9, 1, 2)]
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                result = self.run_mode(contract_trace(), mode, sink=sink)
                self.assert_success(result, groups, counters(late=1, duplicate=1, filtered=1, accepted=4))
                self.assertTrue(result['checkpoint']['complete'])
                self.assertEqual(result['checkpoint']['cursor'], 10)
                self.assertEqual([entry['epoch_offset'] for entry in sink.trace], [5, 8, 10])
                self.assertEqual([len(entry['reports']) for entry in sink.trace], [1, 1, 1])

    def test_empty_end_commits_but_input_exhaustion_is_not_end(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                result = self.run_mode([end(1)], mode)
                self.assert_success(result, [], counters())
                self.assertTrue(result['checkpoint']['complete'])
                empty = self.run_mode([], mode)
                self.assertEqual(empty['status'], 'INCOMPLETE')
                self.assertIsNone(empty['checkpoint'])
                partial = self.run_mode([event(1, 'A', 0)], mode)
                self.assertEqual(partial['status'], 'INCOMPLETE')
                self.assertEqual(partial['reports'], [])
                self.assertIsNone(partial['checkpoint'])

    def test_first_input_id_wins_before_filtering_and_timestamp_sort(self):
        records = [event(1, 'A', 100, 0), event(2, 'A', 0, 3), event(3, 'B', 20, 2), end(4)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode), [expected_group(20, 20, 3, 1, 2)],
                                    counters(duplicate=1, filtered=1, accepted=1))

    def test_tenant_and_event_id_are_exact_identifiers(self):
        records = [event(1, 'A', 0), event(2, 'a', 0), event(3, ' A', 0),
                   event(4, 'A', 0, tenant='T'), end(5)]
        groups = [expected_group(0, 0, 1, 3, 3), expected_group(0, 0, 4, 1, 1, tenant='T')]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode), groups, counters(accepted=4))

    def test_nfkc_casefold_and_explicit_whitespace_normalization(self):
        spaces = ''.join(chr(code) for code in [*range(9, 14), 32, 0x85, 0xA0, 0x1680,
                                               *range(0x2000, 0x200B), 0x2028, 0x2029, 0x202F,
                                               0x205F, 0x3000])
        records = [event(1, 'A', 0, 1, device='  ＰＵＭＰ-K  ', kind='\tALERT\u00a0', message='a'+spaces+'b'),
                   event(2, 'B', 1, 2, device='pump-k', kind='alert', message='a b'), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode),
                                    [expected_group(0, 1, 1, 2, 3, device='pump-k', message='a b')],
                                    counters(accepted=2))

    def test_python_extra_whitespace_controls_bom_and_zero_width_are_not_collapsed(self):
        excluded = ['\x1c', '\x1d', '\x1e', '\x1f', '\ufeff', '\u200b']
        records = [event(i+1, str(i), 0, device='a'+char+'b') for i, char in enumerate(excluded)]
        records += [event(7, 'space', 0, device='a b'), end(8)]
        groups = [expected_group(0, 0, i+1, 1, 1, device='a'+char+'b') for i, char in enumerate(excluded)]
        groups.append(expected_group(0, 0, 7, 1, 1, device='a b'))
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode), groups, counters(accepted=7))

    def test_message_case_and_compatibility_characters_remain_distinct(self):
        messages = ['m', 'M', 'ﬁ', 'fi']
        records = [event(i+1, str(i), 0, message=m) for i, m in enumerate(messages)] + [end(5)]
        groups = [expected_group(0, 0, i+1, 1, 1, message=m) for i, m in enumerate(messages)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode), groups, counters(accepted=4))

    def test_unicode_scalar_size_limits_are_inclusive_and_minimum_zero_is_valid(self):
        records = [event(0, '😀'*128, MAX_I64, 0, tenant='😀'*128, device='D'*256,
                         kind='K'*256, message='😀'*4096), end(1)]
        group = expected_group(MAX_I64, MAX_I64, 0, 1, 0, tenant='😀'*128,
                               device='d'*256, kind='k'*256, message='😀'*4096)
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode, config=Config(minimum=0)),
                                    [group], counters(accepted=1))

    def test_anchored_windows_strict_boundary_and_creation_ties(self):
        records = [event(1, 'A', 9), event(2, 'B', 0), event(3, 'C', 10),
                   event(4, 'D', 18), event(5, 'E', 10, device='z'),
                   event(6, 'F', 10, device='a'), end(7)]
        groups = [expected_group(0, 9, 2, 2, 2), expected_group(10, 18, 3, 2, 2),
                  expected_group(10, 10, 5, 1, 1, device='z'), expected_group(10, 10, 6, 1, 1, device='a')]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode, config=Config(window=10)), groups, counters(accepted=6))

    def test_frontier_equality_waits_and_remains_admissible(self):
        config = Config(window=10, lateness=0, dedupe_horizon=20)
        records = [event(1, 'A', 10), watermark(2, 10), event(3, 'B', 10),
                   event(4, 'C', 9, 3), end(5)]
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                result = self.run_mode(records, mode, config=config, sink=sink)
                self.assert_success(result, [expected_group(10, 10, 1, 2, 2)], counters(late=1, accepted=2))
                self.assertEqual(sink.trace[0]['reports'], [])
                self.assertEqual(len(sink.trace[0]['checkpoint']['pending']), 1)

    def test_horizon_eviction_is_exact_and_late_id_does_not_reserve(self):
        config = Config(window=10, lateness=0, dedupe_horizon=20)
        records = [event(1, 'A', 5, 0), watermark(2, 24), event(3, 'A', 24, 3),
                   watermark(4, 25), event(5, 'A', 24, 3), event(6, 'A', 25, 2), end(7)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode, config=config),
                                    [expected_group(25, 25, 6, 1, 2)],
                                    counters(late=1, duplicate=1, filtered=1, accepted=1))

    def test_later_duplicate_does_not_change_original_retention_timestamp(self):
        config = Config(window=10, lateness=0, dedupe_horizon=20)
        records = [event(1, 'A', 500, 0), event(2, 'A', 1, 3), watermark(3, 25),
                   event(4, 'A', 100, 3), end(5)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode, config=config), [],
                                    counters(duplicate=2, filtered=1))

    def test_end_is_infinity_and_exact_timestamp_arithmetic_does_not_wrap(self):
        records = [event(1, 'A', MAX_I64, 3), watermark(2, MAX_I64), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_success(self.run_mode(records, mode, config=Config(lateness=0)),
                                    [expected_group(MAX_I64, MAX_I64, 1, 1, 3)], counters(accepted=1))

    def test_validation_is_not_skipped_for_duplicate_filtered_or_late_rows(self):
        mutations = [lambda row: row['event'].update(severity=True),
                     lambda row: row['event'].update(timestamp=1.5),
                     lambda row: row['event'].update(message='\ud800'),
                     lambda row: row['event'].update(extra='unexpected')]
        for mode in MODES:
            for context in ('duplicate', 'filtered', 'late'):
                for i, mutate in enumerate(mutations):
                    with self.subTest(mode=mode, context=context, mutation=i):
                        bad = event(2, 'A' if context == 'duplicate' else 'B', 0, 0)
                        mutate(bad)
                        prefix = [watermark(1, 500)] if context == 'late' else [event(1, 'A', 0, 0)]
                        result = self.run_mode(prefix+[bad, end(3)], mode)
                        self.assert_error(result, 'VALIDATION')

    def test_strict_record_shapes_bounds_and_plain_values(self):
        invalid = [None, [], {'offset': 1, 'kind': 'bogus'},
                   {'offset': True, 'kind': 'end'}, {'offset': -1, 'kind': 'end'},
                   {'offset': MAX_I64+1, 'kind': 'end'}, {'offset': 1, 'kind': 'end', 'extra': 0}]
        for field, value in [('timestamp', -1), ('timestamp', MAX_I64+1), ('severity', 4),
                             ('tenant', ''), ('event_id', ''), ('tenant', 't'*129),
                             ('event_id', 'a'*129), ('device', 'd'*257), ('kind', 'k'*257),
                             ('message', 'm'*4097), ('message', 3)]:
            row = event(1, 'A', 0); row['event'][field] = value; invalid.append(row)
        class MappingWithCallback(dict):
            def __getitem__(self, key):
                raise AssertionError('a user mapping callback executed')
        invalid.append(MappingWithCallback(offset=1, kind='end'))
        for mode in MODES:
            for i, row in enumerate(invalid):
                with self.subTest(mode=mode, case=i):
                    self.assert_error(self.run_mode([row], mode), 'VALIDATION')

    def test_configuration_rejects_boolean_nonpositive_and_inconsistent_limits(self):
        positive = ('window', 'dedupe_horizon', 'concurrency', 'queue', 'buffered_events',
                    'dedupe_entries', 'open_groups', 'epoch_reports')
        for name in positive:
            for value in (0, -1, True, 1.5):
                with self.subTest(field=name, value=value):
                    with self.assertRaises(WorkflowError) as caught:
                        Config(**{name: value})
                    self.assertEqual(caught.exception.code, 'VALIDATION')
        for kwargs in ({'lateness': -1}, {'lateness': True}, {'minimum': True}, {'minimum': 4},
                       {'window': 10, 'dedupe_horizon': 9}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(WorkflowError): Config(**kwargs)

    def test_offsets_and_watermarks_are_monotone_but_equal_watermarks_are_valid(self):
        for mode in MODES:
            for records in ([event(1, 'A', 0), event(1, 'B', 1)],
                            [watermark(2, 100), watermark(1, 101)],
                            [watermark(1, 100), watermark(2, 99)]):
                with self.subTest(mode=mode, records=records):
                    self.assert_error(self.run_mode(records, mode), 'VALIDATION')
            self.assert_success(self.run_mode([watermark(1, 100), watermark(2, 100), end(3)], mode), [], counters())

    def test_new_event_after_durable_end_is_rejected(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                first = self.run_mode([end(1)], mode, sink=sink)
                self.assertEqual(first['status'], 'COMPLETE')
                result = self.run_mode([end(1), event(2, 'A', 0)], mode, sink=sink)
                self.assert_error(result, 'VALIDATION')
                self.assertEqual(result['checkpoint']['cursor'], 1)

    def test_each_state_capacity_fails_atomically_with_a_named_resource(self):
        cases = [
            ('dedupe_entries', Config(dedupe_entries=1), [event(1, 'A', 0, 0), event(2, 'B', 1, 0), end(3)]),
            ('buffered_events', Config(buffered_events=1), [event(1, 'A', 0), event(2, 'B', 1), end(3)]),
            ('open_groups', Config(window=10, lateness=0, open_groups=1),
             [event(1, 'A', 0, device='a'), event(2, 'B', 1, device='b'), watermark(3, 5)]),
            ('epoch_reports', Config(window=10, lateness=0, epoch_reports=1),
             [event(1, 'A', 0, device='a'), event(2, 'B', 1, device='b'), watermark(3, 20)]),
        ]
        for mode in MODES:
            for resource, config, records in cases:
                with self.subTest(mode=mode, resource=resource):
                    sink = Sink()
                    result = self.run_mode(records, mode, config=config, sink=sink)
                    self.assert_error(result, 'CAPACITY')
                    self.assertEqual(result['error']['details']['resource'], resource)
                    self.assertEqual(sink.trace, [])
                    self.assertEqual(sink.checkpoints, {})

    def test_count_and_severity_overflow_via_trusted_boundary_fixture(self):
        # Construct a valid group through the primitive, then place it at the
        # arithmetic boundary. This avoids pretending to execute 2**63 events.
        for field in ('count', 'severity_sum'):
            with self.subTest(field=field):
                host = Host([], policy=constant_policy(), config=Config(window=10))
                catalog = host.catalog()
                state = catalog[0]['fn'](host)
                catalog[18]['fn'](host, state, event(1, 'A', 0))
                group = next(iter(state.groups.values()))[0]
                group[field] = MAX_I64
                with self.assertRaises(WorkflowError) as caught:
                    catalog[18]['fn'](host, state, event(2, 'B', 1, 3))
                self.assertEqual(caught.exception.code, 'OVERFLOW')
                self.assertEqual(host.sink.reports, [])

    def test_counter_overflow_is_not_wrapped_or_silently_serialized(self):
        for category, name in enumerate(('late', 'duplicate', 'filtered', 'accepted')):
            with self.subTest(counter=name):
                host = Host([], policy=constant_policy())
                catalog = host.catalog()
                state = catalog[0]['fn'](host)
                state.counters[name] = MAX_I64
                with self.assertRaises(WorkflowError) as caught:
                    catalog[14]['fn'](host, state, category)
                self.assertEqual(caught.exception.code, 'OVERFLOW')

    def test_private_policy_output_types_and_reason_allowlist(self):
        invalid = [(True, 0), (-1, 0), (1001, 0), (1, True), (1, 999),
                   {'score': 1, 'reason': 0, 'secret': 'PRIVATE_SENTINEL'}]
        records = [event(1, 'A', 0), end(2)]
        for mode in MODES:
            for i, value in enumerate(invalid):
                with self.subTest(mode=mode, case=i):
                    def policy(group, version, cancellation, value=value): return value
                    result = self.run_mode(records, mode, policy=policy)
                    self.assert_error(result, 'POLICY')
                    self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))

    def test_reverse_completion_still_publishes_creation_order(self):
        records = [event(1, 'A', 0, device='z'), event(2, 'B', 0, device='a'), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                second_finished = threading.Event()
                completed = []
                lock = threading.Lock()
                def policy(group, version, cancellation):
                    if group['first_offset'] == 1:
                        if not second_finished.wait(2): raise RuntimeError('scheduler did not run the other call')
                    with lock: completed.append(group['first_offset'])
                    if group['first_offset'] == 2: second_finished.set()
                    return 77, 2
                result = self.run_mode(records, mode, config=Config(concurrency=2, queue=1), policy=policy)
                self.assert_success(result, [expected_group(0, 0, 1, 1, 1, device='z'),
                                             expected_group(0, 0, 2, 1, 1, device='a')], counters(accepted=2))
                self.assertEqual(completed, [2, 1])

    def test_lowest_group_policy_error_wins_over_completion_order(self):
        records = [event(1, 'A', 0, device='z'), event(2, 'B', 0, device='a'), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                second_finished = threading.Event()
                def policy(group, version, cancellation):
                    if group['first_offset'] == 1:
                        if not second_finished.wait(2): raise RuntimeError('first fixture timed out')
                    else: second_finished.set()
                    raise ValueError('PRIVATE_SENTINEL')
                result = self.run_mode(records, mode, config=Config(concurrency=2, queue=1), policy=policy)
                self.assert_error(result, 'POLICY')
                self.assertEqual(result['error']['details']['group_index'], 0)
                self.assertNotIn('PRIVATE_SENTINEL', json.dumps(result))

    def test_scheduler_respects_running_and_waiting_limits(self):
        records = [event(i+1, str(i), 0, device=str(i)) for i in range(6)] + [end(7)]
        host = Host(records, config=Config(concurrency=2, queue=1), policy=constant_policy())
        result = reference.run(host)
        self.assertEqual(result['status'], 'COMPLETE')
        self.assertEqual(len(result['reports']), 6)
        self.assertLessEqual(host.scheduler['peak_running'], 2)
        self.assertLessEqual(host.scheduler['peak_waiting'], 1)

    def test_authority_is_checked_per_policy_and_immediately_before_commit(self):
        records = [event(1, 'A', 0, device='a'), event(2, 'B', 0, device='b'), end(3)]
        for mode in MODES:
            for denied_stage in ('policy', 'precommit'):
                with self.subTest(mode=mode, stage=denied_stage):
                    seen = []
                    def authority(stage, group):
                        seen.append(stage)
                        if stage != denied_stage: return True
                        return stage == 'policy' and group['first_offset'] != 2
                    result = self.run_mode(records, mode, authority=authority)
                    self.assert_error(result, 'AUTHORITY')
                    self.assertIn(denied_stage, seen)

    def test_tenant_scope_and_policy_version_are_pinned(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assert_error(self.run_mode([event(1, 'A', 0, tenant='private'), end(2)], mode,
                                                allowed_tenants=('public',)), 'AUTHORITY')
                sink = Sink()
                self.run_mode([watermark(1, 0)], mode, sink=sink)
                changed = constant_policy(); changed.version = 'fixture-v2'
                self.assert_error(self.run_mode([watermark(1, 0)], mode, sink=sink,
                                                policy=changed, policy_version='fixture-v2'), 'POLICY_VERSION')

    def test_policy_version_change_during_work_is_rejected_before_commit(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                def policy(group, version, token):
                    policy.version = 'changed-during-work'
                    return 77, 2
                policy.version = 'fixture-v1'
                result = self.run_mode([event(1, 'A', 0), end(2)], mode, policy=policy)
                self.assert_error(result, 'POLICY_VERSION')

    def test_cancellation_before_admission_leaves_sink_unchanged(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                cancel = threading.Event(); cancel.set()
                sink = Sink()
                result = self.run_mode([event(1, 'A', 0), end(2)], mode, sink=sink, cancel=cancel)
                self.assertEqual(result['status'], 'CANCELLED')
                self.assertEqual(result['reports'], [])
                self.assertEqual(sink.trace, [])

    def test_cancellation_during_policy_takes_precedence_and_preserves_prior_epoch(self):
        records = [event(1, 'A', 0, device='a'), watermark(2, 1000),
                   event(3, 'B', 1000, device='b'), event(4, 'C', 1000, device='c'), end(5)]
        for mode in MODES:
            with self.subTest(mode=mode):
                cancel = threading.Event()
                invoked = []
                def policy(group, version, token):
                    invoked.append(group['first_offset'])
                    if group['first_offset'] == 3:
                        cancel.set()
                        raise ValueError('PRIVATE_SENTINEL')
                    return 77, 2
                sink = Sink()
                result = self.run_mode(records, mode, sink=sink, cancel=cancel,
                                       config=Config(concurrency=1, queue=1), policy=policy)
                self.assertEqual(result['status'], 'CANCELLED')
                self.assertEqual(len(result['reports']), 1)
                self.assertEqual(result['checkpoint']['cursor'], 2)
                self.assertEqual([row['epoch_offset'] for row in sink.trace], [2])
                self.assertEqual(invoked, [1, 3])

    def test_observed_cancellation_drains_inflight_calls_without_publishing(self):
        records = [event(1, 'A', 0, device='a'), event(2, 'B', 0, device='b'), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                cancel, second_started, release = threading.Event(), threading.Event(), threading.Event()
                finished = []
                lock = threading.Lock()
                def policy(group, version, token):
                    if group['first_offset'] == 1:
                        if not second_started.wait(2): raise RuntimeError('second fixture did not start')
                        cancel.set()
                        release.set()
                    else:
                        second_started.set()
                        if not release.wait(2): raise RuntimeError('first fixture did not release')
                    with lock: finished.append(group['first_offset'])
                    return 77, 2
                result = self.run_mode(records, mode, cancel=cancel, policy=policy,
                                       config=Config(concurrency=2, queue=1))
                self.assertEqual(result['status'], 'CANCELLED')
                self.assertEqual(result['reports'], [])
                self.assertEqual(sorted(finished), [1, 2])

    def test_cancel_at_precommit_is_observed_before_publication(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                cancel = threading.Event()
                def authority(stage, group):
                    if stage == 'precommit': cancel.set()
                    return True
                result = self.run_mode([event(1, 'A', 0), end(2)], mode, cancel=cancel, authority=authority)
                self.assertEqual(result['status'], 'CANCELLED')
                self.assertEqual(result['reports'], [])

    def test_failure_before_commit_rolls_back_and_replay_publishes_once(self):
        records = [event(1, 'A', 0), watermark(2, 1000), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                failed = self.run_mode(records, mode, sink=sink, fault='before_commit')
                self.assert_error(failed, 'CRASH_BEFORE_COMMIT')
                self.assertEqual(sink.checkpoints, {})
                self.assertEqual(sink.trace, [])
                replay = self.run_mode(records, mode, sink=sink)
                self.assert_success(replay, [expected_group(0, 0, 1, 1, 1)], counters(accepted=1))
                self.assertEqual([row['epoch_offset'] for row in sink.trace], [2, 3])

    def test_lost_ack_recovery_does_not_duplicate_visible_publication(self):
        records = [event(1, 'A', 0), watermark(2, 1000), end(3)]
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                lost = self.run_mode(records, mode, sink=sink, fault='after_commit')
                self.assert_error(lost, 'LOST_ACK', reports=1)
                self.assertEqual(lost['checkpoint']['cursor'], 2)
                replay = self.run_mode(records, mode, sink=sink)
                self.assert_success(replay, [expected_group(0, 0, 1, 1, 1)], counters(accepted=1))
                self.assertEqual([row['epoch_offset'] for row in sink.trace], [2, 3])

    def test_same_epoch_same_payload_is_idempotent_and_different_payload_conflicts(self):
        sink = Sink()
        result = self.run_mode([event(1, 'A', 0), watermark(2, 1000)], 'python', sink=sink)
        self.assertEqual(result['status'], 'INCOMPLETE')
        transaction = {'reports': deepcopy(sink.trace[0]['reports']),
                       'checkpoint': deepcopy(sink.trace[0]['checkpoint'])}
        before = deepcopy(sink.trace)
        token = sink.fences['default']
        sink.commit('default', 2, deepcopy(transaction), token)
        self.assertEqual(sink.trace, before)
        transaction['reports'][0]['score'] = 76
        with self.assertRaises(WorkflowError) as caught:
            sink.commit('default', 2, transaction, token)
        self.assertEqual(caught.exception.code, 'EPOCH_CONFLICT')
        self.assertEqual(sink.trace, before)

    def test_stale_writer_cannot_commit(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                stale = sink.acquire('default')
                sink.acquire('default')
                result = self.run_mode([event(1, 'A', 0), end(2)], mode, sink=sink, writer_token=stale)
                self.assert_error(result, 'FENCED')
                self.assertEqual(sink.trace, [])

    def test_checkpoint_tampering_and_config_mismatch_are_rejected(self):
        for mode in MODES:
            for change in ('integrity', 'shape', 'config'):
                with self.subTest(mode=mode, change=change):
                    sink = Sink()
                    self.run_mode([watermark(1, 0)], mode, sink=sink)
                    options = {}
                    if change == 'integrity': sink.checkpoints['default']['cursor'] = 999
                    elif change == 'shape':
                        snapshot = sink.checkpoints['default']
                        snapshot['pending'] = [{'untrusted': 'not a record'}]
                        snapshot['integrity'] = checkpoint_integrity(snapshot)
                    else: options['config'] = Config(window=601)
                    result = self.run_mode([watermark(1, 0)], mode, sink=sink, **options)
                    self.assert_error(result, 'CHECKPOINT')

    def test_append_only_restart_resumes_the_committed_prefix(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                sink = Sink()
                original = [watermark(1, 0)]
                first = self.run_mode(original, mode, sink=sink)
                self.assertEqual(first['status'], 'INCOMPLETE')
                appended = original + [event(2, 'A', 0), end(3)]
                result = self.run_mode(appended, mode, sink=sink)
                self.assert_success(result, [expected_group(0, 0, 2, 1, 1)], counters(accepted=1))
                self.assertEqual([entry['epoch_offset'] for entry in sink.trace], [1, 3])

    def test_changed_or_truncated_committed_prefix_cannot_resume(self):
        original = [event(1, 'A', 0), watermark(2, 1000)]
        for mode in MODES:
            for change in ('changed', 'truncated'):
                with self.subTest(mode=mode, change=change):
                    sink = Sink()
                    self.run_mode(original, mode, sink=sink)
                    records = deepcopy(original)
                    if change == 'changed': records[0]['event']['message'] = 'different'
                    else: records = records[:1]
                    records.append(end(3))
                    result = self.run_mode(records, mode, sink=sink)
                    self.assert_error(result, 'CHECKPOINT', reports=1)
                    self.assertEqual(result['checkpoint']['cursor'], 2)

    def test_old_or_duplicate_offset_in_appended_suffix_is_not_silently_skipped(self):
        for mode in MODES:
            for bad_offset in (0, 1):
                with self.subTest(mode=mode, offset=bad_offset):
                    sink = Sink()
                    self.run_mode([watermark(1, 0)], mode, sink=sink)
                    result = self.run_mode([watermark(1, 0), event(bad_offset, 'A', 0)], mode, sink=sink)
                    self.assert_error(result, 'VALIDATION')
                    self.assertEqual(result['checkpoint']['cursor'], 1)

    def test_invalid_future_row_does_not_erase_an_already_committed_epoch(self):
        for mode in MODES:
            for value in (1.5, '\ud800'):
                with self.subTest(mode=mode, invalid_value=repr(value)):
                    bad = event(3, 'B', 1000)
                    if isinstance(value, str): bad['event']['message'] = value
                    else: bad['event']['timestamp'] = value
                    records = [event(1, 'A', 0), watermark(2, 1000), bad, end(4)]
                    sink = Sink()
                    result = self.run_mode(records, mode, sink=sink)
                    self.assert_error(result, 'VALIDATION', reports=1)
                    self.assertEqual(result['checkpoint']['cursor'], 2)
                    self.assertEqual(result['counters'], counters(accepted=1))
                    self.assertEqual([entry['epoch_offset'] for entry in sink.trace], [2])

    def test_group_identity_is_stable_on_replay_and_scoped_by_source(self):
        records = [event(1, 'A', 0), end(2)]
        for mode in MODES:
            with self.subTest(mode=mode):
                one = self.run_mode(records, mode)
                again = self.run_mode(records, mode)
                other = self.run_mode(records, mode, source_id='other')
                self.assertEqual(one['reports'][0]['group_id'], again['reports'][0]['group_id'])
                self.assertNotEqual(one['reports'][0]['group_id'], other['reports'][0]['group_id'])


if __name__ == '__main__': unittest.main()
