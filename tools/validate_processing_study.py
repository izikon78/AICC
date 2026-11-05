"""Verify primary study artifacts and write checksums without running new trials."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'experiments/processing_study'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, default=STUDY / 'results/full-2026-11-05')
    args = parser.parse_args()
    out = args.results.resolve()
    load = lambda name: json.loads((out / name).read_text(encoding='utf-8'))
    before = load('run-config.json')['source_sha256_before_run']
    assert before == load('run-metadata.json')['source_sha256']
    for name, expected in before.items():
        assert hashlib.sha256((STUDY / name).read_bytes()).hexdigest() == expected, name
    raw = load('stress-raw.json')
    assert len(raw) == 45 and all(row['job']['n'] == 1000000 for row in raw)
    signatures = {}
    for row in raw:
        signatures.setdefault(row['job']['name'], set()).add(json.dumps(row['output'], sort_keys=True))
    assert len(signatures) == 3 and all(len(values) == 1 for values in signatures.values())
    splits = load('calibration.json')['splits']
    assert [len(splits[k]) for k in ('train', 'validation', 'test')] == [72, 24, 24]
    seeds = [{r['job']['seed'] for r in splits[k]} for k in ('train', 'validation', 'test')]
    assert len(set.union(*seeds)) == sum(map(len, seeds))
    assert load('binding-scenarios.json')['all_pass']
    assert load('granularity.json')['all_outputs_equal']
    assert load('test-verification.json')['test_methods_passed'] == 44
    model = load('cost-network.json')
    assert model['architecture'] == [8, 32, 16, 3]
    json_files = 0
    files = [p for p in STUDY.rglob('*') if p.is_file() and '__pycache__' not in str(p) and '/smoke-' not in p.as_posix()]
    files += [ROOT / 'README.md', ROOT / 'experiments/README.md', ROOT / 'experiments/lifecycle-pilot/README.md']
    files += [ROOT / 'tools' / name for name in ('processing_granularity.py', 'analyze_processing_study.py', 'plot_processing_study.py', 'validate_processing_study.py')]
    missing = []
    secret = re.compile(rb'github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for p in files:
        data = p.read_bytes()
        assert not secret.search(data), 'credential pattern in ' + p.name
        if p.suffix == '.json': json.loads(data); json_files += 1
        if p.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', data.decode('utf-8')):
                if target.startswith(('http:', 'https:', '#')): continue
                if not (p.parent / target.split('#')[0]).exists(): missing.append((str(p), target))
    assert not missing, missing
    checksums = {str(p.relative_to(out)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'checksums.json'}
    (out / 'checksums.json').write_text(json.dumps(checksums, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'source_hashes_matched': len(before), 'stress_rows_checked': len(raw),
                      'output_groups_matched': len(signatures), 'json_files_parsed': json_files,
                      'files_screened': len(files), 'missing_links': missing,
                      'result_checksums': len(checksums)}, indent=2))


if __name__ == '__main__': main()
