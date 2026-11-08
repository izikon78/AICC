"""Run local processing/learning experiments; no model API or remote training."""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'worker':
        from aicc_processing.benchmark import worker
        from aicc_processing.data import Job
        config = json.loads(sys.argv[2])
        print(json.dumps(worker(Job(**config['job']), config['mode'], config['model_dir'], config['streaming'])))
        return
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--events', type=int, default=1000000)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--train-jobs', type=int, default=72)
    parser.add_argument('--validation-jobs', type=int, default=24)
    parser.add_argument('--test-jobs', type=int, default=24)
    parser.add_argument('--epochs', type=int, default=900)
    parser.add_argument('--reuse-model', action='store_true')
    args = parser.parse_args()
    if min(args.events, args.repeats, args.train_jobs, args.validation_jobs, args.test_jobs, args.epochs) < 1:
        parser.error('All counts must be positive')
    from aicc_processing.benchmark import calibrate, run_stress, report, source_manifest, write_json
    args.output.mkdir(parents=True, exist_ok=True)
    if (args.output / 'stress-raw.json').exists():
        parser.error('Output already contains stress results; use a new directory')
    write_json(args.output / 'run-config.json', {'events_per_job': args.events, 'repeats': args.repeats,
        'train_jobs': args.train_jobs, 'validation_jobs': args.validation_jobs, 'test_jobs': args.test_jobs,
        'epochs': args.epochs, 'reuse_model': args.reuse_model, 'source_sha256_before_run': source_manifest()})
    if not args.reuse_model:
        calibrate(args.output, args.train_jobs, args.validation_jobs, args.test_jobs, args.epochs)
    from aicc_processing.scenarios import run as state_checks
    state_result = state_checks()
    write_json(args.output / 'binding-scenarios.json', state_result)
    if not state_result['all_pass']:
        raise AssertionError('Binding state demonstration failed')
    run_stress(args.output, args.events, args.repeats)
    report(args.output)
    print('COMPLETE: ' + str(args.output / 'REPORT.md'), flush=True)


if __name__ == '__main__':
    main()
