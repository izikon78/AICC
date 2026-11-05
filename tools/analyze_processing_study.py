"""Validate recorded processing outputs and produce a bounded interpretation.

This reads existing measurements; it does not rerun or retune the experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'experiments/processing_study'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, required=True)
    args = parser.parse_args()
    out = args.results
    load = lambda name: json.loads((out / name).read_text(encoding='utf-8'))
    raw, summary, learning = load('stress-raw.json'), load('stress-summary.json'), load('learning-report.json')
    config, metadata, granularity = load('run-config.json'), load('run-metadata.json'), load('granularity.json')
    before = config['source_sha256_before_run']
    after = metadata['source_sha256']
    assert before == after, 'Study source changed during the primary run'
    assert all(hashlib.sha256((STUDY / p).read_bytes()).hexdigest() == digest for p, digest in before.items())
    assert len(raw) == 3 * 5 * config['repeats'] == 45
    assert all(row['job']['n'] == config['events_per_job'] == 1000000 for row in raw)
    groups = {}
    for row in raw:
        groups.setdefault((row['job']['name'], row['mode']), []).append(row)
    assert len(groups) == 15 and all(len(rows) == 3 for rows in groups.values())
    for name in {row['job']['name'] for row in raw}:
        hashes = {json.dumps(row['output'], sort_keys=True) for row in raw if row['job']['name'] == name}
        assert len(hashes) == 1
    calibration = load('calibration.json')['splits']
    seed_sets = [{r['job']['seed'] for r in calibration[split]} for split in ('train', 'validation', 'test')]
    assert not (seed_sets[0] & seed_sets[1] or seed_sets[0] & seed_sets[2] or seed_sets[1] & seed_sets[2])
    binding = load('binding-scenarios.json')
    assert binding['all_pass'] and granularity['all_outputs_equal']
    setup_ms = statistics.median(row['host_register_bind_seconds'] * 1000 for row in raw if row['mode'].startswith('aicc'))
    evaluation = learning['held_out_kernel_evaluation']
    learned_difference = 100 * (evaluation['learned_kernel_seconds'] / evaluation['static_kernel_seconds'] - 1)
    by_job = {}
    for row in summary: by_job.setdefault(row['job'], {})[row['mode']] = row
    g = {row['mode']: row for row in granularity['summary']}
    coarse_ratio = g['aicc_split']['median_seconds'] / g['aicc_batch']['median_seconds']
    audit = {'source_files_unchanged': len(before), 'stress_executions': len(raw),
             'events_per_execution': 1000000, 'matched_dataset_shapes': len(by_job),
             'all_workload_output_signatures_match': True, 'calibration_seeds_disjoint': True,
             'binding_scenarios_passed': len(binding['checks']),
             'granularity_operation_checks': granularity['differential_operation_cases'],
             'granularity_outputs_match': True, 'aicc_setup_median_ms': setup_ms}
    (out / 'audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8', newline='\n')
    text = ['# Interpretation of the 5 November engineering run', '',
            'The implementation successfully executes equivalent event-processing flows and trains a small neural cost model. It does not establish AICC economic superiority, production security, or a trained AI-native programming language.', '',
            '## Larger jobs', '',
            '| Million-event job | Reference seconds | Optimized ordinary seconds | AICC + same optimization seconds | Reference / optimized | Peak memory reduction, reference to ordinary optimized |',
            '|---|---:|---:|---:|---:|---:|']
    for name, modes in by_job.items():
        ref, base, host = modes['reference'], modes['static'], modes['aicc_static']
        reduction = 100 * (1 - base['median_peak_mib'] / ref['median_peak_mib'])
        text.append(f'| {name} | {ref["median_pipeline_seconds"]:.3f} | {base["median_pipeline_seconds"]:.3f} | '
                    f'{host["median_pipeline_seconds"]:.3f} | {ref["median_pipeline_seconds"]/base["median_pipeline_seconds"]:.2f}x | {reduction:.1f}% |')
    text += ['', 'These improvements arise from agent-designed combinations of caching, filtering, partitioning, and ordered streaming. Every ordinary and AICC path can use them. Registry indirection is not credited for the algorithm improvements.', '',
             f'There were 45 separate executions of million-event jobs, reusing three matched synthetic datasets across five modes and three repetitions. All output summaries and SHA-256 digests matched within each job shape. AICC registration and binding took a median {setup_ms:.3f} ms across the AICC workers.', '',
             '## Variation and overhead', '',
             '| Job | Mode | Median seconds | Observed minimum–maximum seconds |',
             '|---|---|---:|---:|']
    for (name, mode), rows in sorted(groups.items()):
        values = [r['pipeline_seconds'] for r in rows]
        text.append(f'| {name} | {mode} | {statistics.median(values):.3f} | {min(values):.3f}–{max(values):.3f} |')
    text += ['', 'These ranges are observations from three runs, not confidence intervals. The host was not exclusive or frequency-pinned. Differences between identical selected kernels across fresh processes include noise and host activity; a small apparent AICC speedup is not evidence that the binding makes the kernel faster. The explicitly timed setup cost is more interpretable than attributing an entire process-to-process difference to the registry. Every worker imports NumPy through the common harness, including the reference/static modes; peak process memory includes that common instrumentation.', '',
             '## Actual neural learning', '',
             f'The 867-parameter, two-hidden-layer network used {learning["train_jobs"]} training jobs and {learning["validation_jobs"]} validation jobs; {learning["test_jobs"]} other jobs were held out. Data collection took {learning["data_collection_seconds"]:.2f}s and neural training took {learning["training_seconds"]:.2f}s. Validation selected epoch {learning["training"]["selected_epoch"]} of {learning["training"]["epochs_attempted"]} attempted epochs.', '',
             f'On the held-out calibration jobs, selected kernel time totaled {evaluation["learned_kernel_seconds"]:.4f}s versus {evaluation["static_kernel_seconds"]:.4f}s for the simple policy: the learned choice was {learned_difference:.2f}% higher. This estimate excludes selection overhead. The end-to-end stress timings include features and inference.', '',
             'On the million-event ordered stream, the learned model chose partitioning while the simpler policy chose ordered streaming. The learned ordinary path used more time and memory. The larger jobs are size extrapolation beyond 800–14,000-row calibration, and the model was not retuned on these results. This is an important negative result: adding a neural selector did not consistently improve the strong conventional policy.', '',
             '## Combining operations into a larger capability', '',
             f'The exploratory warm-call microbenchmark checked {granularity["differential_operation_cases"]:,} operation inputs and equal million-value checksums, then measured three randomized repetitions per path.', '',
             '| Path | Median seconds | Observed min–max seconds |', '|---|---:|---:|']
    for mode, row in g.items():
        text.append(f'| {mode} | {row["median_seconds"]:.4f} | {row["min_seconds"]:.4f}–{row["max_seconds"]:.4f} |')
    text += ['', f'Two AICC calls per value took {g["aicc_split"]["median_seconds"]:.3f}s; one AICC call around the entire batch took {g["aicc_batch"]["median_seconds"]:.3f}s, or {coarse_ratio:.1f}x less elapsed time in this microbenchmark. Ordinary batch execution took {g["ordinary_batch"]["median_seconds"]:.3f}s. Coarse operations avoid repeated host/Python dispatch; ordinary batching benefits too. This is not an inference-token or dollar saving.', '',
             'The fusion microbenchmark holds authorization/policy fixed. A batch checks its binding on entry, whereas per-event calls check repeatedly. Batching does not establish equal mid-batch revocation, expiry, or cancellation responsiveness; a real contract must permit batch-level checks or specify additional checkpoints. The equality checks here concern mathematical outputs under the fixed policy.', '',
             '## What this supports', '',
             '- An AI coding agent can implement and check equivalent alternative flows, then expose the optimized operation through an AICC binding.',
             '- Batch-sized capabilities can keep invocation costs small relative to useful processing; tiny per-event bindings can be expensive.',
             '- Runtime metadata can represent selective invalidation and receiver revalidation in the tested host scenarios. Both runtimes are objects in one Python process. The word "processes" in the raw scenario scope string is a wording error; no fresh OS-process or model/provider handoff was executed.',
             '- Actual local neural training is feasible, but this learned selector does not demonstrate a reliable advantage over the simple policy.', '',
             '## What remains open', '',
             '- Full lifecycle economics, billed model tokens, human curation effort, and independent model/provider authoring.',
             '- Real authentication, private execution isolation, complete transitive integrity, and hostile-host security.',
             '- More representative calibration, distribution-shift guards, uncertainty-aware fallback, and fresh evaluation for any revised selector.',
             '- General-purpose AI-native operation-token training and claims of algorithmic novelty.', '',
             'The appropriate next implementation is a conservative selector that falls back when a job lies outside calibration, followed by new workloads/seeds that have not been used to revise that selector. Keep existing results as the frozen version-one record.', '',
             'See [the primary report](REPORT.md), [raw worker records](stress-raw.json), [learning record](learning-report.json), [granularity record](granularity.json), and [integrity audit](audit.json).', '',
             '## Figures', '', '![Measured processing time](runtime.png)', '', '![Peak process working set](memory.png)', '', '![Training and validation loss](learning.png)']
    (out / 'ANALYSIS.md').write_text('\n'.join(text) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(audit, indent=2))


if __name__ == '__main__': main()
