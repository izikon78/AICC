"""Read-only post-run reconciliation against raw CLI events and frozen hashes."""
import hashlib
import json
from pathlib import Path
import sys

STUDY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(STUDY))
import run


def audit(folder):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    checks, attempts, known, unknown = [], 0, 0, 0
    for path in sorted((folder / 'stages').glob('*/stage.json')):
        row = json.loads(path.read_text(encoding='utf-8'))
        checks.append((row['id'] + ':functional', row['judge'].get('passed') is True
                       and row['judge'].get('passed_cases') == 55 and row['judge'].get('cases') == 55))
        checks.append((row['id'] + ':gates', row['preparation_passed'] is True and row['fluency_passed'] is True))
        checks.append((row['id'] + ':oracle', not any(x.get('oracle_manual_gate') is False
                                                    for x in row['judge'].get('details', []))))
        for kind in ('preparation_call', 'task_call'):
            for attempt in row[kind]['attempts']:
                attempts += 1
                relative = attempt.get('raw_events') or f"{kind.removesuffix('_call')}/attempt-{attempt['attempt']}.jsonl"
                raw = run.parse_events((path.parent / relative).read_text(encoding='utf-8'))
                checks.append((row['id'] + ':' + relative, all(raw[key] == attempt[key]
                              for key in ('usage', 'response_text', 'tool_violations', 'turn_completed'))))
                checks.append((row['id'] + ':no_tools', not attempt['tool_violations']))
                checks.append((row['id'] + ':no_timeout', not attempt['timed_out']))
                known += attempt['usage'] is not None
                unknown += attempt['usage'] is None
    checks.append(('frozen_sources', run.source_hashes() == manifest['source_sha256']))
    original = STUDY / 'results/current-agent-2026-11-06'
    for name, expected in manifest.get('original_dataset_sha256', {}).items():
        checks.append(('original:' + name, hashlib.sha256((original / name).read_bytes()).hexdigest() == expected))
    for name, expected in manifest.get('continuation_source_sha256', {}).items():
        checks.append(('adapter:' + name, hashlib.sha256((run.ROOT / name).read_bytes()).hexdigest() == expected))
    old = STUDY.parent / 'ain_v0'
    inventory = json.loads((old / 'ARTIFACT_HASHES.json').read_text(encoding='utf-8'))
    for name, expected in inventory.items():
        checks.append(('earlier:' + name, hashlib.sha256((old / name).read_bytes()).hexdigest() == expected))
    return {'passed': all(value for _, value in checks), 'checks': len(checks),
            'failed_checks': [name for name, value in checks if not value],
            'scored_stages': len(list((folder / 'stages').glob('*/stage.json'))),
            'attempts': attempts, 'metered_attempts': known, 'unmetered_attempts': unknown,
            'earlier_artifacts_unchanged': len(inventory)}


if __name__ == '__main__':
    result = audit(sys.argv[1])
    print(json.dumps(result, indent=2))
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    raise SystemExit(0 if result['passed'] else 1)
