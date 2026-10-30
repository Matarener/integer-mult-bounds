"""Bounded receipt index; no scientific imports, replay, compilation or timing."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    rows = []
    for path in sorted((HERE / 'runtime/runs').glob('*/receipt.json')):
        raw = json.loads(path.read_bytes())
        usage = raw.get('usage') or {}
        if 'raw' in usage:
            try:
                usage = json.loads(usage['raw'].strip().splitlines()[-1])
            except (ValueError, IndexError):
                usage = {}
        science_path = path.parent / 'science/receipt.json'
        science = json.loads(science_path.read_bytes()) if science_path.exists() else {}
        row = {'label': raw['label'], 'status': raw['status'], 'wall': raw['wall_seconds'],
               'cpu': (usage['user_seconds'] + usage['system_seconds']) if 'user_seconds' in usage else None,
               'stage_sha256': raw['stage_sha256'], 'termination': raw['termination'],
               'source_unchanged': raw['source_bytes_and_modes_unchanged'],
               'science_status': science.get('status'), 'lanes': science.get('lanes'),
               'has_complete_science_anchor': 'science' in science}
        rows.append(row)
    result = {'runs': rows, 'spent_seconds': sum(row['wall'] for row in rows),
              'failed_attempts': sum(row['status'] != 'PASS' for row in rows)}
    (HERE / 'validation/RUN-INDEX.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    status_path = HERE / 'STATUS.json'
    status = json.loads(status_path.read_bytes())
    status.update(scientific_runs_started=bool(rows), new_round_spent_seconds=result['spent_seconds'],
                  retained_failed_attempts=result['failed_attempts'])
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'run_count': len(rows), 'spent_seconds': result['spent_seconds'],
                      'failed_attempts': result['failed_attempts'], 'index': 'validation/RUN-INDEX.json',
                      'runs': [{k: row[k] for k in ('label', 'status', 'wall', 'cpu')} for row in rows]},
                     sort_keys=True))


if __name__ == '__main__':
    main()
