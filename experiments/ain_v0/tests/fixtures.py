"""Plain, deterministic workflow inputs and hand-written expected groups.

These are development fixtures, not hidden or independently authored grading.
"""
from copy import deepcopy

MODES = ('python', 'ir', 'ain')
MAX_I64 = 2**63 - 1
COUNTER_NAMES = ('late', 'duplicate', 'filtered', 'accepted')
REPORT_GROUP_FIELDS = (
    'tenant', 'device', 'kind', 'message', 'first_timestamp', 'last_timestamp',
    'first_offset', 'count', 'severity_sum',
)


def event(offset, event_id, timestamp, severity=1, *, tenant='t', device='pump',
          kind='alert', message='m'):
    return {'offset': offset, 'kind': 'event', 'event': {
        'tenant': tenant, 'event_id': event_id, 'timestamp': timestamp,
        'severity': severity, 'device': device, 'kind': kind, 'message': message,
    }}


def watermark(offset, timestamp):
    return {'offset': offset, 'kind': 'watermark', 'timestamp': timestamp}


def end(offset):
    return {'offset': offset, 'kind': 'end'}


def expected_group(first, last, first_offset, count, severity_sum, *, tenant='t',
                   device='pump', kind='alert', message='m'):
    return dict(zip(REPORT_GROUP_FIELDS, (
        tenant, device, kind, message, first, last, first_offset, count, severity_sum,
    )))


def counters(late=0, duplicate=0, filtered=0, accepted=0):
    return {'late': late, 'duplicate': duplicate, 'filtered': filtered, 'accepted': accepted}


def constant_policy(score=77, reason=2):
    def policy(group, version, cancel_event):
        return score, reason
    policy.version = 'fixture-v1'
    return policy


def contract_trace():
    return [event(1, 'A', 100, 0), event(2, 'A', 90, 3), event(3, 'B', 200, 2),
            event(4, 'C', 150, 1), watermark(5, 900), event(6, 'D', 779, 3),
            event(7, 'D', 780, 3), watermark(8, 1500), event(9, 'A', 1400, 2), end(10)]


def clone(value):
    return deepcopy(value)
