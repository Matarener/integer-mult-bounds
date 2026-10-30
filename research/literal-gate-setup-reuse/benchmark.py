"""Fresh bounded serial pair; no retry, sampling or cached acceptance."""
import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

from retained import baseline
from setup_cache import require

HERE = Path(__file__).resolve().parent
EXPECTED = 'c796be009d692546eab74e3ac084ec6badf45245841d81f101c2a164c0a6eaba'


def compare(folder):
    labels = ('baseline', 'candidate')
    receipts = {n: json.loads((folder / 'runs' / n / 'receipt.json').read_bytes()) for n in labels}
    outputs = [(folder / 'runs' / n / 'stdout.txt').read_bytes() for n in labels]
    require(outputs[0] == outputs[1] and sha256(outputs[0]).hexdigest() == EXPECTED,
            'Complete frozen scientific output equivalence')
    require(all(r['status'] == 'PASS' for r in receipts.values()), 'Both complete runs passed')
    cpu = lambda r: r['usage']['user_seconds'] + r['usage']['system_seconds']
    old, new = (receipts[n] for n in labels)
    result = {'baseline_wall_seconds': old['wall_seconds'], 'candidate_wall_seconds': new['wall_seconds'],
              'baseline_cpu_seconds': cpu(old), 'candidate_cpu_seconds': cpu(new),
              'wall_fraction_saved': 1 - new['wall_seconds'] / old['wall_seconds'],
              'cpu_fraction_saved': 1 - cpu(new) / cpu(old), 'complete_stdout_equal': True,
              'samples_per_arm': 1, 'limitations': 'One pair on a shared host; not statistical or universal.'}
    (folder / 'COMPARISON.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    require(min(result['wall_fraction_saved'], result['cpu_fraction_saved']) >= .15,
            'At least 15 percent wall and CPU saving')
    print('PASS_LITERAL_SETUP_FIRST_PAIR', json.dumps(result, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('pair', 'optimized'))
    parser.add_argument('--workdir', type=Path, required=True)
    args = parser.parse_args()
    folder = args.workdir.resolve()
    if args.phase == 'pair':
        folder.mkdir(parents=True)  # Existing evidence is never overwritten.
    require(folder.is_dir(), 'Existing comparison directory')
    with (folder / 'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.phase == 'optimized':
            saved = json.loads((folder / 'COMPARISON.json').read_bytes())
            require(saved['complete_stdout_equal'] and min(saved['wall_fraction_saved'],
                    saved['cpu_fraction_saved']) >= .15, 'First pair gate before optimized run')
        with baseline() as base:
            sys.path.insert(0, str(base))
            from source import prepared
            with prepared() as root:
                run = runpy.run_path(str(base / 'guard.py'))['run']
                run.__globals__.update(HERE=folder, SOURCE=root, MANIFEST=base / 'INPUT-MANIFEST.json',
                                      AGGREGATE=900 if args.phase == 'pair' else 1500)
                if args.phase == 'pair':
                    run('baseline', str(base / 'joint.py'))
                    run('candidate', str(HERE / 'verify.py'))
                    compare(folder)
                else:
                    run('candidate-optimized', str(HERE / 'verify.py'), True)
                    require((folder / 'runs/candidate/stdout.txt').read_bytes() ==
                            (folder / 'runs/candidate-optimized/stdout.txt').read_bytes(),
                            'Complete normal and optimized stdout identical')
                    print('PASS_LITERAL_SETUP_OPTIMIZED_QUALIFICATION', flush=True)


if __name__ == '__main__':
    main()
