"""Exploratory warm-call study of operation fusion and coarse AICC capabilities.

All paths compute the same synthetic integer checksum. No model API calls.
"""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments/processing_study'))
from aicc_processing.runtime import Runtime


def stage_one(value):
    return (value * 17 + 3) % 65521


def stage_two(value):
    return ((value ^ 12345) * 7) % 65521


def fused(value):
    return ((((value * 17 + 3) % 65521) ^ 12345) * 7) % 65521


def batch(count):
    total = 0
    for value in range(count):
        total += ((((value * 17 + 3) % 65521) ^ 12345) * 7) % 65521
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--events', type=int, default=1000000)
    parser.add_argument('--repeats', type=int, default=3)
    args = parser.parse_args()
    if args.events < 1 or args.repeats < 1: parser.error('positive counts required')
    if args.output.exists(): parser.error('preserve existing result; choose a new output')
    rng = random.Random(5191)
    checks = list(range(-2048, 2048)) + [rng.randrange(-10**15, 10**15) for _ in range(4000)]
    assert all(fused(value) == stage_two(stage_one(value)) for value in checks)
    host = Runtime(environment={'python': platform.python_version(), 'platform': sys.platform})
    dependency = {'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for name, fn in [('one', stage_one), ('two', stage_two), ('fused', fused), ('batch', batch)]:
        host.register(name, fn, dependencies=dependency)
    one = host.bind('one'); two = host.bind('two')
    merged = host.bind('fused'); entire = host.bind('batch')
    modes = ('ordinary_split', 'ordinary_fused', 'aicc_split', 'aicc_fused', 'ordinary_batch', 'aicc_batch')
    trials = [(repeat, mode) for repeat in range(args.repeats) for mode in modes]
    rng.shuffle(trials)
    rows = []
    expected = batch(args.events)
    for repeat, mode in trials:
        start = time.perf_counter(); cpu = time.process_time()
        if mode == 'ordinary_split':
            result = sum(stage_two(stage_one(i)) for i in range(args.events))
        elif mode == 'ordinary_fused':
            result = sum(fused(i) for i in range(args.events))
        elif mode == 'aicc_split':
            result = sum(two(one(i)) for i in range(args.events))
        elif mode == 'aicc_fused':
            result = sum(merged(i) for i in range(args.events))
        elif mode == 'ordinary_batch': result = batch(args.events)
        else: result = entire(args.events)
        cpu = time.process_time() - cpu
        elapsed = time.perf_counter() - start
        if result != expected: raise AssertionError('granularity output mismatch')
        rows.append({'mode': mode, 'repeat': repeat, 'seconds': elapsed, 'cpu_seconds': cpu, 'checksum': result})
        print(f'GRANULARITY {mode}: {elapsed:.4f}s', flush=True)
    summary = [{'mode': mode, 'median_seconds': statistics.median(r['seconds'] for r in rows if r['mode'] == mode),
                'min_seconds': min(r['seconds'] for r in rows if r['mode'] == mode),
                'max_seconds': max(r['seconds'] for r in rows if r['mode'] == mode)} for mode in modes]
    result = {'scope': 'exploratory warm invocation microbenchmark; not agent/model cost or production security',
              'python': platform.python_version(), 'platform': sys.platform, 'events_per_run': args.events,
              'repeats': args.repeats, 'differential_operation_cases': len(checks), 'all_outputs_equal': True,
              'source_sha256': dependency['source_sha256'], 'summary': summary, 'raw': rows,
              'limits': ['Known algebraic fusion, not algorithmic novelty.',
                         'Same process; randomized repeated order; host setup excluded.',
                         'AICC and ordinary batch paths use identical batch code.',
                         'No billed inference, cross-agent transfer, or security assurance.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__': main()
