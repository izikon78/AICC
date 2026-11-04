"""Verify archived source bytes and rerun the available small official fixtures.

Uses Python 3.10+ standard library only. No model calls or inference measurements.
Run: python tools/verify_research_import.py --output docs/research/verification-2026-11-04.json
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify_hashes():
    manifest = json.loads((ROOT / 'reference/import-manifest.json').read_text())
    checks = []
    for item in manifest['sources'] + manifest['archive_members']:
        if 'destination' not in item:
            continue
        path = ROOT / item['destination']
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        checks.append({'path': item['destination'], 'match': actual == item['sha256']})
    packet = ROOT / 'experiments/round8/packet'
    packet_checks = []
    for line in (packet / 'SHA256SUMS.txt').read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        name = name.lstrip('*')
        actual = hashlib.sha256((packet / name).read_bytes()).hexdigest()
        packet_checks.append({'path': name, 'match': actual == expected})
    return {
        'source_associations': len(checks),
        'all_source_hashes_match': all(x['match'] for x in checks),
        'source_failures': [x for x in checks if not x['match']],
        'round8_manifest_files': len(packet_checks),
        'round8_manifest_pass': all(x['match'] for x in packet_checks),
        'round8_manifest_failures': [x for x in packet_checks if not x['match']],
    }


def trial(label, cwd, arguments, expected_total, plain=False):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    result = subprocess.run([sys.executable, *arguments], cwd=cwd, env=env,
                            capture_output=True, text=True, encoding='utf-8', timeout=60)
    if plain:
        passed = sum(line.startswith('PASS:') for line in result.stdout.splitlines())
        data = {'passed': passed, 'total': expected_total, 'output': result.stdout.splitlines()}
    else:
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            data = {'passed': 0, 'total': expected_total, 'parse_error': True}
    ok = result.returncode == 0 and data.get('passed') == expected_total and data.get('total') == expected_total
    return {'label': label, 'command': ['python', *arguments], 'expected_total': expected_total,
            'exit_code': result.returncode, 'ok': ok, 'result': data,
            **({'stderr': result.stderr} if result.stderr else {})}


def run_trials():
    base = ROOT / 'work'
    base.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='import-verification-', dir=base) as temp:
        target = Path(temp).resolve()
        if not target.is_relative_to(base.resolve()):
            raise ValueError('Verification directory escaped the repository work folder')
        r7, r8 = target / 'r7', target / 'r8'
        shutil.copytree(ROOT / 'experiments/round7/packet', r7)
        shutil.copytree(ROOT / 'experiments/round8/packet', r8)
        for name in ['submission.py', 'submission_registry.py', 'controller_submission.py', 'controller_submission.sym']:
            shutil.copyfile(ROOT / 'agents/claude/round7' / name, r7 / name)
        for name in ['submission_A.py', 'submission_B.py']:
            shutil.copyfile(ROOT / 'agents/claude/round8' / name, r8 / name)
        for name in ['submission_armA.py', 'submission_armB.py']:
            shutil.copyfile(ROOT / 'agents/grok/round8' / name, r8 / name)
        tests = []
        for name in ['submission.py', 'submission_registry.py']:
            tests.append(trial('Round 7 Claude ' + name, r7, ['fixtures/test_tasks.py', '--submission', name], 14))
        tests.append(trial('Round 7 Claude Python controller', r7, ['fixtures/test_tasks.py', '--python-controller', 'controller_submission.py'], 6))
        tests.append(trial('Round 7 Claude symbolic controller', r7, ['fixtures/test_tasks.py', '--symbolic', 'controller_submission.sym'], 6))
        tests.append(trial('Round 7 simple binding checks', r7, ['fixtures/binding_checks.py'], 3, plain=True))
        tests.append(trial('Round 8 fixture self-test (reference only)', r8, ['-m', 'benchmark.verify_submission', '--self-test'], 20))
        for author, name in [('Claude', 'submission_A.py'), ('Claude', 'submission_B.py'),
                             ('Grok', 'submission_armA.py'), ('Grok', 'submission_armB.py')]:
            tests.append(trial('Round 8 ' + author + ' ' + name, r8, ['-m', 'benchmark.verify_submission', '--submission', name], 20))
        tests.append(trial('Round 8 simple mock security checks', r8, ['-m', 'benchmark.verify_submission', '--security'], 3))
        return tests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    hashes = verify_hashes()
    if not hashes['all_source_hashes_match'] or not hashes['round8_manifest_pass']:
        print(json.dumps(hashes, indent=2))
        return 1
    tests = run_trials()
    report = {
        'review_date': '2026-11-04', 'python': platform.python_version(),
        'platform': platform.system(), 'hash_verification': hashes,
        'test_commands': len(tests), 'all_pass': all(t['ok'] for t in tests), 'tests': tests,
        'limitations': [
            'Runs existing finished code; not independent model authoring or cost trials.',
            'Official scope/binding checks are mock tests, not a security assurance.',
            'The self-test compares reference code against itself and is not an agent result.',
            'No tokenizer, model API, billed cost, or inference latency measurement was performed.',
            'The historical extended fuzz/audit variants and Language A/B runtimes remain incomplete.',
        ],
    }
    if args.output:
        destination = args.output if args.output.is_absolute() else ROOT / args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2, ensure_ascii=True) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'hash_verification': hashes, 'test_commands': len(tests),
                      'all_pass': report['all_pass'],
                      'results': [{'label': t['label'], 'ok': t['ok'], 'passed': t['result'].get('passed'),
                                   'total': t['result'].get('total')} for t in tests]}, indent=2))
    return 0 if report['all_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
