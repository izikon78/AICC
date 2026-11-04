"""Reference components for experimental comparisons. Treat implementations as sealed.

For Arm A use baseline_api.md. For Arm B use capability_cards.md and registry.py.
Do not inspect this file during a trial unless you explicitly record that an inspection
trigger fired. Running it as part of the tests does NOT count as reading it.
"""
from collections import defaultdict


def controller_logs(runs: int) -> list[str]:
    """Produce the exact messages from the original C# running example."""
    messages = []
    for i in range(runs):
        if i == 0:
            messages.append(f"Starting controller service for {runs} runs")
        else:
            messages.append(f"Restarting controller service for run {i+1} of {runs}")
    return messages


def controller_logs_near_miss(runs: int) -> list[str]:
    """A WRONG but superficially compatible candidate: restart number is zero-based."""
    messages = []
    for i in range(runs):
        if i == 0:
            messages.append(f"Starting controller service for {runs} runs")
        else:
            messages.append(f"Restarting controller service for run {i} of {runs}")
    return messages


_SEVERITY = {'info': 0, 'warning': 1, 'critical': 2}


def rollup_activity(events: list[dict], window_seconds: int = 600,
                    min_severity: int = 0) -> list[dict]:
    """Produce deterministic device-activity aggregations (see capability contract)."""
    if not isinstance(window_seconds, int) or isinstance(window_seconds, bool) or window_seconds <= 0:
        raise ValueError('window_seconds must be a positive integer')
    if not isinstance(min_severity, int) or isinstance(min_severity, bool) or min_severity not in (0, 1, 2):
        raise ValueError('min_severity must be 0, 1, or 2')
    if not isinstance(events, list):
        raise TypeError('events must be a list')

    clean = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        event_id = ev.get('event_id')
        device = ev.get('device')
        kind = ev.get('kind')
        msg = ev.get('message')
        ts = ev.get('timestamp')
        severity = ev.get('severity')
        if not isinstance(event_id, str) or not event_id.strip():
            continue
        if not isinstance(device, str) or not device.strip():
            continue
        if not isinstance(kind, str) or not kind.strip():
            continue
        if not isinstance(msg, str):
            continue
        if not isinstance(ts, int) or isinstance(ts, bool) or ts < 0:
            continue
        if not isinstance(severity, str) or severity.strip().lower() not in _SEVERITY:
            continue
        sev = severity.strip().lower()
        if _SEVERITY[sev] < min_severity:
            continue
        clean.append({
            'event_id': event_id.strip(),
            'device': device.strip().lower(),
            'kind': kind.strip().lower(),
            'message': ' '.join(msg.split()),
            'timestamp': ts,
            'severity': sev,
        })

    clean.sort(key=lambda e: (e['timestamp'], e['event_id']))
    # Group by normalized identity, resetting the group when the time window lapses.
    # The window is relative to the most recently accepted event, not group start.
    active = {}
    output = []
    for e in clean:
        key = (e['device'], e['kind'], e['message'])
        old = active.get(key)
        if old is None or e['timestamp'] - old['last_timestamp'] > window_seconds:
            group = {
                'device': e['device'],
                'kind': e['kind'],
                'message': e['message'],
                'first_timestamp': e['timestamp'],
                'last_timestamp': e['timestamp'],
                'severity': e['severity'],
                'count': 1,
                'event_ids': [e['event_id']],
            }
            active[key] = group
            output.append(group)
            continue
        old['last_timestamp'] = e['timestamp']
        old['count'] += 1
        old['event_ids'].append(e['event_id'])
        if _SEVERITY[e['severity']] > _SEVERITY[old['severity']]:
            old['severity'] = e['severity']

    return sorted(output, key=lambda e: (e['first_timestamp'], e['device'], e['kind'], e['message']))


def rollup_by_eventid_near_miss(events: list[dict], window_seconds: int = 600,
                                min_severity: int = 0) -> list[dict]:
    """WRONG compatible-looking candidate: grouping by event_id instead of behavior."""
    groups = rollup_activity(events, window_seconds, min_severity)
    if not events:
        return groups
    # Same function signature, plausible output type, but breaks aggregation.
    wrong = []
    for g in groups:
        if len(g['event_ids']) <= 1:
            wrong.append(g)
        else:
            for ident in g['event_ids']:
                split = dict(g)
                split['event_ids'] = [ident]
                split['count'] = 1
                wrong.append(split)
    return wrong


def rollup_and_save_denylisted(events: list[dict], window_seconds: int = 600,
                               min_severity: int = 0) -> list[dict]:
    """A policy-disallowed candidate. It is never invoked by the authorized registry."""
    return rollup_activity(events, window_seconds, min_severity)
