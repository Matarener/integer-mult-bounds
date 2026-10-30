"""Bounded original B,C,C,B,B,C order, retaining every Linux sample."""
import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path
import statistics

import guard
from replay import EXPECTED
from source import require

PACKAGE = Path(__file__).resolve().parent
ORDER = ('baseline', 'candidate', 'candidate', 'baseline', 'baseline', 'candidate')


def scientific(folder, label, mode):
    raw = (folder / 'runs' / label / 'stdout.txt').read_bytes()
    lines = raw.decode().splitlines()
    require(len(lines) == 2 and lines[0] == 'PASS_P104_INTEGER_ERROR_REPLAY', 'Complete original output')
    data = json.loads(lines[1])
    require(set(data) == {'mode', 'receipt', 'seconds'} and data['mode'] == mode,
            'Complete original output schema and mode')
    require(data['receipt'] == EXPECTED, 'Every original scientific receipt field')
    return data


def summary(folder, labels, threshold=True):
    rows = []
    for number, mode in labels:
        label = f'sample-{number}-{mode}'
        receipt = json.loads((folder / 'runs' / label / 'receipt.json').read_bytes())
        require(receipt['status'] == 'PASS', 'Every measurement passed')
        data = scientific(folder, label, mode)
        rows.append({'label': label, 'mode': mode, 'wall_seconds': receipt['wall_seconds'],
                     'cpu_seconds': receipt['usage']['user_seconds'] + receipt['usage']['system_seconds'],
                     'kernel_max_rss_kib': receipt['usage']['kernel_max_rss_kib'],
                     'sampled_group_rss_bytes': receipt['sampled_process_group_rss_bytes'],
                     'internal_seconds': data['seconds'], 'receipt': data['receipt']})
    medians = {mode: {kind: statistics.median(r[kind] for r in rows if r['mode'] == mode)
                      for kind in ('wall_seconds', 'cpu_seconds')} for mode in ('baseline', 'candidate')}
    saving = {kind: 1 - medians['candidate'][kind] / medians['baseline'][kind]
              for kind in ('wall_seconds', 'cpu_seconds')}
    result = {'order': [r['mode'] for r in rows], 'runs': rows, 'medians': medians,
              'fraction_saved': saving, 'speedup_wall': medians['baseline']['wall_seconds'] /
              medians['candidate']['wall_seconds'], 'complete_scientific_receipts_equal': True,
              'gate_passed': min(saving.values()) >= .15,
              'limits': {'per_command_seconds': 180, 'cumulative_seconds': 900,
                         'sampled_group_rss_bytes': 1073741824, 'automatic_retries': 0},
              'limitations': 'Fresh processes on an unreserved Linux host, unflushed OS caches, three samples per arm at most; no universal speed claim. Qualification is separate.'}
    target = 'FIRST-PAIR.json' if len(rows) == 2 else 'BENCHMARK.json'
    (folder / target).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    if threshold:
        require(result['gate_passed'], 'At least 15 percent wall and CPU saving before expansion')
    print('PASS_PRECISION_LINUX_COMPARISON', json.dumps(result, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('pair', 'remaining'))
    parser.add_argument('--workdir', type=Path, required=True)
    args = parser.parse_args()
    folder = args.workdir.resolve()
    if args.phase == 'pair':
        folder.mkdir(parents=True)
    require(folder.is_dir(), 'Existing comparison directory')
    with (folder / 'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        guard.HERE = folder
        if args.phase == 'remaining':
            first = json.loads((folder / 'FIRST-PAIR.json').read_bytes())
            require(first['gate_passed'] and first['complete_scientific_receipts_equal'], 'First pair gate')
        selected = list(enumerate(ORDER, 1))[:2] if args.phase == 'pair' else list(enumerate(ORDER, 1))[2:]
        for number, mode in selected:
            label = f'sample-{number}-{mode}'
            guard.run(label, mode + '.py')
            scientific(folder, label, mode)
        summary(folder, list(enumerate(ORDER, 1))[:2] if args.phase == 'pair' else list(enumerate(ORDER, 1)))


if __name__ == '__main__':
    main()
