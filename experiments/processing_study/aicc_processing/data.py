"""Reproducible synthetic workload generation and bounded feature inspection."""
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
import random


@dataclass(frozen=True)
class Job:
    name: str
    n: int
    keys: int
    duplicate_rate: float
    ordered: bool
    message_length: int = 24
    window: int = 60
    minimum: int = 1
    seed: int = 1

    def to_dict(self):
        return asdict(self)


def events(job):
    """Generate synthetic events; repeated IDs may have conflicting payloads."""
    rng = random.Random(job.seed)
    now = 0
    messages = [f"measurement {k} " + ('x' * max(0, job.message_length - 20))
                for k in range(job.keys)]
    for i in range(job.n):
        key = rng.randrange(job.keys)
        ordinal = rng.randrange(i) if i and rng.random() < job.duplicate_rate else i
        now = now + rng.randrange(3) if job.ordered else rng.randrange(max(1, job.n // 2))
        yield {
            'event_id': f'e-{ordinal}',
            'device': f'  PUMP-{key} ' if i % 3 else f'pump-{key}',
            'kind': ' ALERT ' if i % 2 else 'alert',
            'message': messages[key] if i % 4 else '  ' + messages[key] + '  ',
            'timestamp': now,
            'severity': rng.randrange(4),
        }


FEATURE_NAMES = ['log_n', 'device_ratio', 'message_ratio', 'id_ratio',
                 'log_message_length', 'qualified_fraction', 'declared_ordered', 'log_window']


def inspect_features(source, job, sample_size=512):
    """Return features AND replayable input. Ordered eligibility is not inferred here.

    The descriptor's ordering flag controls eligibility; the ordered kernel still
    validates the complete raw stream. Sampling cannot prove global order.
    """
    if isinstance(source, list):
        sample = source[:sample_size]
        replay = source
    else:
        iterator = iter(source)
        sample = list(itertools.islice(iterator, sample_size))
        replay = itertools.chain(sample, iterator)
    count = max(1, len(sample))
    features = [math.log2(max(1, job.n)),
                len({e['device'] for e in sample}) / count,
                len({e['message'] for e in sample}) / count,
                len({e['event_id'] for e in sample}) / count,
                math.log2(1 + sum(len(e['message']) for e in sample) / count),
                sum(e['severity'] >= job.minimum for e in sample) / count,
                float(job.ordered), math.log2(job.window)]
    return features, replay


def output_summary(groups):
    digest = hashlib.sha256()
    event_count = severity_sum = 0
    for group in groups:
        digest.update(json.dumps(group, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())
        digest.update(b'\n')
        event_count += group['count']
        severity_sum += group['severity_sum']
    return {'groups': len(groups), 'events_retained': event_count,
            'severity_sum': severity_sum, 'sha256': digest.hexdigest()}


def calibration_jobs(count, seed, prefix):
    """Independent deterministic descriptor/seed populations, not secret grading."""
    rng = random.Random(seed)
    for i in range(count):
        n = rng.choice([800, 1800, 4000, 8000, 14000])
        yield Job(f'{prefix}-{i:03d}', n, rng.choice([4, 24, 128, max(1, n // 3)]),
                  rng.choice([0.0, 0.15, 0.55]), bool(rng.randrange(2)),
                  rng.choice([24, 96, 384]), rng.choice([10, 60, 600]),
                  rng.choice([0, 1, 2]), rng.randrange(1, 2**31))
