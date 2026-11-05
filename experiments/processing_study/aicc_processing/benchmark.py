"""Measured calibration, real local MLP training, and fresh-process CPU jobs."""
from dataclasses import asdict
from datetime import datetime, timezone
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time
import unicodedata

import numpy as np
from . import kernels
from .data import Job, calibration_jobs, events, inspect_features, output_summary, FEATURE_NAMES
from .learning import CostNetwork, PLANS, evaluate, fit, fit_static, static_choice
from .runtime import Runtime

STUDY = Path(__file__).resolve().parents[1]
REPOSITORY = STUDY.parents[1]
MODES = ('reference', 'static', 'aicc_static', 'learned', 'aicc_learned')


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def source_manifest():
    return {str(p.relative_to(STUDY)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(STUDY.rglob('*.py')) if '__pycache__' not in str(p)}


def make_runtime():
    environment = {'python': platform.python_version(), 'unicode': unicodedata.unidata_version,
                   'platform': sys.platform, 'contract': 'events-v1'}
    runtime = Runtime(environment=environment)
    dependencies = {'kernel_module_sha256': hashlib.sha256(Path(kernels.__file__).read_bytes()).hexdigest(),
                    'contract_sha256': hashlib.sha256((STUDY / 'KERNEL_CONTRACT.md').read_bytes()).hexdigest()}
    for plan, function in kernels.VARIANTS.items():
        runtime.register('events.' + plan + '@1', function, contract_version='events-v1',
                         obligations=('exact-event-groups',), dependencies=dependencies,
                         properties={'behavior': 'events-v1', 'input_order': 'ordered' if plan == 'ordered' else 'any'})
    return runtime


def measure_calibration(job, repeats=2):
    source = list(events(job))
    feature_start = time.perf_counter()
    features, _ = inspect_features(source, job)
    feature_seconds = time.perf_counter() - feature_start
    expected = kernels.process_reference(source, job.window, job.minimum)
    eligible = list(PLANS if job.ordered else PLANS[:-1])
    samples = {plan: [] for plan in eligible}
    rng = random.Random(job.seed ^ 81231)
    for _ in range(repeats):
        order = eligible.copy()
        rng.shuffle(order)
        for plan in order:
            gc.collect()
            start = time.perf_counter()
            actual = kernels.VARIANTS[plan](source, job.window, job.minimum)
            duration = time.perf_counter() - start
            if actual != expected:
                raise AssertionError(f'Calibration output mismatch: {job.name}, {plan}')
            samples[plan].append(duration)
            del actual
    return {'job': job.to_dict(), 'features': features, 'feature_seconds': feature_seconds,
            'times': {plan: statistics.median(samples[plan]) if plan in samples else None for plan in PLANS},
            'samples': samples, 'output': output_summary(expected)}


def calibrate(output, train_count=72, validation_count=24, test_count=24, epochs=900):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    populations = {'train': list(calibration_jobs(train_count, 1105, 'train')),
                   'validation': list(calibration_jobs(validation_count, 2205, 'validation')),
                   'test': list(calibration_jobs(test_count, 3305, 'test'))}
    seeds = [job.seed for jobs in populations.values() for job in jobs]
    if len(seeds) != len(set(seeds)):
        raise AssertionError('Calibration split seeds overlap')
    dataset = {}
    for split, jobs in populations.items():
        dataset[split] = []
        for i, job in enumerate(jobs):
            dataset[split].append(measure_calibration(job))
            if (i + 1) % 8 == 0 or i + 1 == len(jobs):
                print(f'CALIBRATION {split}: {i + 1}/{len(jobs)}', flush=True)
    collection_seconds = time.perf_counter() - start
    write_json(output / 'calibration.json', {'feature_names': FEATURE_NAMES, 'splits': dataset,
        'measurement': 'median of two kernel executions on the same materialized synthetic job',
        'collection_seconds': collection_seconds,
        'limit': 'Synthetic same-session calibration; seeds separate, not independently hidden authoring tasks.'})
    training_start = time.perf_counter()
    model, training = fit(dataset['train'], dataset['validation'], epochs=epochs)
    training_seconds = time.perf_counter() - training_start
    policy = fit_static(dataset['train'])
    model.save(output / 'cost-network.json', {'trained_on': len(dataset['train']),
               'validation_jobs': len(dataset['validation']), 'maximum_training_events': 14000,
               'training': training, 'seed': 7, 'training_seconds': training_seconds})
    write_json(output / 'static-policy.json', policy)
    evaluation = evaluate(model, policy, dataset['test'])
    report = {'training': training, 'training_seconds': training_seconds,
              'data_collection_seconds': collection_seconds, 'static_policy': policy,
              'held_out_kernel_evaluation': evaluation,
              'train_jobs': len(dataset['train']), 'validation_jobs': len(dataset['validation']),
              'test_jobs': len(dataset['test']), 'trainable_parameters': sum(w.size for w in model.weights) + sum(b.size for b in model.biases),
              'large_job_limit': 'Jobs above 14,000 events are size extrapolation. No tuning on stress results.',
              'deep_learning_scope': 'Actual two-hidden-layer neural cost-model training, not LLM/native-opcode training.'}
    write_json(output / 'learning-report.json', report)
    print(f'TRAINED: {report["trainable_parameters"]} parameters; held-out kernel seconds '
          f'learned={evaluation["learned_kernel_seconds"]:.4f}, static={evaluation["static_kernel_seconds"]:.4f}', flush=True)
    return report


def peak_memory():
    """Process-lifetime high-water working set, including Python/input/output/model."""
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        size = ctypes.c_size_t
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD),
                        *[(name, size) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                          'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                          'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]]
        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        current = ctypes.windll.kernel32.GetCurrentProcess
        current.restype = wintypes.HANDLE
        get_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        if get_info(current(), ctypes.byref(counters), counters.cb):
            return counters.PeakWorkingSetSize
        return None
    try:
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == 'darwin' else value * 1024)
    except ImportError:
        return None


def worker(job, mode, model_dir, streaming=False):
    model_dir = Path(model_dir)
    model_load_start = time.perf_counter()
    policy = json.loads((model_dir / 'static-policy.json').read_text())
    model = CostNetwork.load(model_dir / 'cost-network.json') if 'learned' in mode else None
    model_load_seconds = time.perf_counter() - model_load_start
    prepare = time.perf_counter()
    source = events(job) if streaming else list(events(job))
    input_preparation_seconds = time.perf_counter() - prepare
    start = time.perf_counter()
    cpu_start = time.process_time()
    feature_seconds = inference_seconds = host_seconds = 0.0
    if mode == 'reference':
        plan = 'reference'
    elif mode in ('static', 'aicc_static'):
        choose_start = time.perf_counter()
        plan = static_choice(policy, job.ordered)
        inference_seconds = time.perf_counter() - choose_start
    else:
        feature_start = time.perf_counter()
        features, source = inspect_features(source, job)
        feature_seconds = time.perf_counter() - feature_start
        inference_start = time.perf_counter()
        plan = model.choose(features, job.ordered)
        inference_seconds = time.perf_counter() - inference_start
    function = kernels.VARIANTS[plan]
    full_validations = None
    if mode.startswith('aicc'):
        host_start = time.perf_counter()
        host = make_runtime()
        function = host.bind('events.' + plan + '@1', obligations=('exact-event-groups',),
                             requirements={'behavior': 'events-v1', 'input_order': 'ordered' if plan == 'ordered' else 'any'})
        host_seconds = time.perf_counter() - host_start
        full_validations = host.full_validations
    kernel_start = time.perf_counter()
    groups = function(source, job.window, job.minimum)
    kernel_seconds = time.perf_counter() - kernel_start
    pipeline_seconds = time.perf_counter() - start
    cpu_seconds = time.process_time() - cpu_start
    digest_start = time.perf_counter()
    summary = output_summary(groups)
    digest_seconds = time.perf_counter() - digest_start
    return {'job': job.to_dict(), 'mode': mode, 'selected_plan': plan, 'streaming_input': streaming,
            'pipeline_seconds': pipeline_seconds, 'kernel_seconds': kernel_seconds,
            'feature_seconds': feature_seconds, 'selection_seconds': inference_seconds,
            'host_register_bind_seconds': host_seconds, 'model_load_seconds': model_load_seconds,
            'input_preparation_seconds': input_preparation_seconds, 'digest_seconds': digest_seconds,
            'cpu_seconds': cpu_seconds, 'process_peak_working_set_bytes': peak_memory(),
            'full_validations': full_validations, 'output': summary,
            'timing_scope': 'pipeline includes selection/host setup/execution; generator creation consumes inside pipeline for streaming; list generation and model loading separate',
            'memory_scope': 'process lifetime high-water working set including imports, input, output, and digest; not isolated kernel allocations'}


def stress_jobs(n):
    return [(Job('repeated-shuffled', n, 64, 0.15, False, 24, 600, 1, 71001), False),
            (Job('diverse-shuffled', n, max(4, min(100000, n // 10)), 0.05, False, 64, 60, 1, 72001), False),
            (Job('ordered-stream', n, 32, 0.10, True, 96, 600, 1, 73001), True)]


def run_stress(output, n=1000000, repeats=3):
    output = Path(output).resolve()
    tasks = [(job, streaming, mode, repeat) for job, streaming in stress_jobs(n)
             for repeat in range(repeats) for mode in MODES]
    random.Random(441105).shuffle(tasks)
    rows = []
    expected = {}
    for i, (job, streaming, mode, repeat) in enumerate(tasks):
        config = {'job': job.to_dict(), 'mode': mode, 'streaming': streaming, 'model_dir': str(output)}
        env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
                   OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        start = time.perf_counter()
        result = subprocess.run([sys.executable, str(STUDY / 'run_study.py'), 'worker', json.dumps(config)],
                                capture_output=True, text=True, encoding='utf-8', env=env, timeout=180)
        wall = time.perf_counter() - start
        if result.returncode:
            write_json(output / 'failed-worker.json', {'job': job.to_dict(), 'mode': mode,
                       'repeat': repeat, 'stderr': result.stderr, 'stdout': result.stdout, 'exit_code': result.returncode})
            raise RuntimeError('Stress worker failed; preserved failed-worker.json')
        row = json.loads(result.stdout)
        row.update(repeat=repeat, worker_wall_seconds=wall)
        signature = row['output']
        if job.name in expected and signature != expected[job.name]:
            write_json(output / 'failed-output.json', row)
            raise AssertionError('Stress output mismatch; preserved failed-output.json')
        expected[job.name] = signature
        rows.append(row)
        write_json(output / 'stress-raw.json', rows)
        print(f'STRESS {i+1}/{len(tasks)} {job.name} {mode}: {row["pipeline_seconds"]:.3f}s '
              f'plan={row["selected_plan"]}, peak={row["process_peak_working_set_bytes"]/1048576:.1f} MiB', flush=True)
    summary = []
    for job, streaming in stress_jobs(n):
        for mode in MODES:
            group = [r for r in rows if r['job']['name'] == job.name and r['mode'] == mode]
            summary.append({'job': job.name, 'mode': mode, 'events_per_run': n, 'repeats': repeats,
                'streaming_input': streaming, 'median_pipeline_seconds': statistics.median(r['pipeline_seconds'] for r in group),
                'median_worker_wall_seconds': statistics.median(r['worker_wall_seconds'] for r in group),
                'median_peak_mib': statistics.median(r['process_peak_working_set_bytes'] / 1048576 for r in group),
                'selected_plans': sorted({r['selected_plan'] for r in group}),
                'output': group[0]['output']})
    write_json(output / 'stress-summary.json', summary)
    return summary


def report(output):
    output = Path(output)
    learning = json.loads((output / 'learning-report.json').read_text())
    summary = json.loads((output / 'stress-summary.json').read_text())
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                'numpy': np.__version__, 'unicode': unicodedata.unidata_version,
                'platform': platform.platform(), 'logical_cpus': os.cpu_count(),
                'source_sha256': source_manifest(), 'billed_model_tokens': 'NOT_MEASURED',
                'billed_model_cost': 'NOT_MEASURED', 'independent_agent_trials': 'NOT_EXECUTED',
                'new_neural_training': 'EXECUTED_LOCAL_NUMPY_MLP',
                'algorithm_authorship': 'same-session AI agents designed combinations of established techniques'}
    write_json(output / 'run-metadata.json', metadata)
    lines = ['# Processing and local neural-selection study', '',
             'Measured execution of synthetic jobs and actual local cost-model training. This is not an inference-billing study, an independently blinded multi-agent trial, or a demonstration of novel algorithms.', '',
             '## Stress workloads', '',
             '| Job | Mode | Selected plan | Median pipeline seconds | Peak process MiB |',
             '|---|---|---|---:|---:|']
    for r in summary:
        lines.append(f'| {r["job"]} | {r["mode"]} | {", ".join(r["selected_plans"])} | {r["median_pipeline_seconds"]:.4f} | {r["median_peak_mib"]:.1f} |')
    lines += ['', 'All listed modes produced identical output summaries and SHA-256 digests within each workload.', '',
              '## Attribution and pairwise comparisons', '']
    for job in sorted({r['job'] for r in summary}):
        values = {r['mode']: r['median_pipeline_seconds'] for r in summary if r['job'] == job}
        lines.append(f'- **{job}:** reference/static = {values["reference"]/values["static"]:.2f}x; '
                     f'AICC-static/static = {values["aicc_static"]/values["static"]:.3f}x; '
                     f'learned/static = {values["learned"]/values["static"]:.3f}x; '
                     f'AICC-learned/learned = {values["aicc_learned"]/values["learned"]:.3f}x.')
    evaluation = learning['held_out_kernel_evaluation']
    lines += ['', 'The first ratio reflects ordinary algorithm/flow optimization. For the other ratios, values below 1 mean lower measured time and values above 1 mean higher measured time. Both ordinary and AICC modes receive the same optimized kernels and learned model. Small registry differences may be timing noise.', '',
              '## Actual neural training', '',
              f'- Architecture: 8 inputs, two hidden layers (32 and 16 ReLU units), 3 log-runtime outputs; {learning["trainable_parameters"]} trainable parameters.',
              f'- Measured calibration: {learning["train_jobs"]} training, {learning["validation_jobs"]} validation, {learning["test_jobs"]} held-out jobs, separate seeds.',
              f'- Data collection: {learning["data_collection_seconds"]:.2f}s; training: {learning["training_seconds"]:.2f}s; selected epoch: {learning["training"]["selected_epoch"]}.',
              f'- Held-out kernel-only sum: learned {evaluation["learned_kernel_seconds"]:.4f}s; static {evaluation["static_kernel_seconds"]:.4f}s; retrospective oracle {evaluation["oracle_kernel_seconds"]:.4f}s.',
              '- The held-out kernel-only sum excludes feature/inference overhead; the stress worker pipeline timings include those costs.',
              '- The model selects among supplied plans. It does not synthesize a new algorithm, train an LLM, or learn a native-opcode programming language.', '',
              '## Measurement boundaries', '',
              '- Stress jobs above 14,000 events are size extrapolation beyond the calibration range; no retuning on stress results.',
              '- Fresh child processes, randomized task order, and matched generated inputs; each case uses identical seed and shape across modes.',
              '- List-input pipeline timing excludes list generation and model loading; their measured times are in the raw records. Streaming pipeline timing includes generator consumption for every mode.',
              '- Worker wall time additionally includes process/import/startup, generation, loading, execution, digesting and serialization. Peak working set is a process-lifetime high-water mark.',
              '- Ordered input is declared by the job descriptor and then validated on every raw row; sample features do not establish the order precondition.',
              '- Exact dedupe and returned output require memory proportional to unique IDs and group count; streaming is not constant-memory.',
              '- Configured duplicate_rate is a probability of referencing an earlier ordinal, not an exact measured duplicate fraction.',
              '- The AICC host is in-process with declared dependency identities, not a production authentication/isolation boundary.',
              '- Prototype full_validations counts compatibility checks, not an automatic semantic proof or a conformance-test run.',
              '- No monetary model cost, billed tokens, cross-provider authoring, or lifecycle break-even was measured.', '',
              'Raw records, model weights, training history, environment and source hashes accompany this report.']
    (output / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    return metadata
