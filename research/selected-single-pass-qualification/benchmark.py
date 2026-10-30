"""Bounded serial comparison; retain every run and stop without retry."""
import argparse
import fcntl
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

from source import prepared

HERE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise ValueError(why)


def compare(folder):
    original = (folder / 'runs/baseline-verify/stdout.txt').read_bytes()
    cross = (folder / 'runs/baseline-cross/stdout.txt').read_bytes()
    joint = (folder / 'runs/candidate-normal/stdout.txt').read_bytes()
    marker = b'PASS_COMPLETE_SELECTED_QUADRATIC_REPLAY\n'
    require(original.endswith(marker), 'Complete original verify output')
    source_output = original[:-len(marker)]
    require(cross.startswith(source_output), 'Identical full legacy source output')
    cross_tail = cross[len(source_output):]
    require(cross_tail.startswith(b'PASS_ALL_SELECTED_LITERAL_STATES '), 'Complete original cross output')
    require(joint.startswith(original + cross_tail), 'Both complete original scientific outputs retained')
    tail = joint[len(original + cross_tail):]
    require(tail.startswith(b'PASS_SINGLE_PASS_COMPLETE_QUALIFICATION ') and tail.count(b'\n') == 1,
            'Only declared orchestration output added')
    receipts = {name: json.loads((folder / 'runs' / name / 'receipt.json').read_bytes())
                for name in ('baseline-verify', 'baseline-cross', 'candidate-normal')}
    require(all(r['status'] == 'PASS' for r in receipts.values()), 'Every guarded run passed')
    old_wall = sum(receipts[n]['wall_seconds'] for n in ('baseline-verify', 'baseline-cross'))
    new_wall = receipts['candidate-normal']['wall_seconds']
    cpu = lambda r: r['usage']['user_seconds'] + r['usage']['system_seconds']
    old_cpu = sum(cpu(receipts[n]) for n in ('baseline-verify', 'baseline-cross'))
    new_cpu = cpu(receipts['candidate-normal'])
    result = {'baseline_wall_seconds': old_wall, 'candidate_wall_seconds': new_wall,
              'baseline_cpu_seconds': old_cpu, 'candidate_cpu_seconds': new_cpu,
              'wall_fraction_saved': 1 - new_wall / old_wall, 'cpu_fraction_saved': 1 - new_cpu / old_cpu,
              'original_verify_stdout_sha256': sha256(original).hexdigest(),
              'original_cross_stdout_sha256': sha256(cross).hexdigest(),
              'complete_output_equivalence': True, 'samples_per_arm': 1,
              'limitations': 'One source-bound fresh-process pair on a shared host; not a median or universal speedup.'}
    (folder / 'COMPARISON.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    require(min(result['wall_fraction_saved'], result['cpu_fraction_saved']) >= .15,
            'At least 15 percent time and CPU saving before expansion')
    print('PASS_SINGLE_PASS_FIRST_PAIR', json.dumps(result, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('pair', 'optimized'))
    parser.add_argument('--workdir', type=Path, required=True)
    args = parser.parse_args()
    folder = args.workdir.resolve()
    if args.phase == 'pair':
        folder.mkdir(parents=True)  # Refuse an existing first-pair directory.
    require(folder.is_dir(), 'Existing comparison work directory')
    with (folder / 'execution.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.phase == 'optimized':
            saved = json.loads((folder / 'COMPARISON.json').read_bytes())
            require(saved['complete_output_equivalence'] and min(saved['wall_fraction_saved'],
                    saved['cpu_fraction_saved']) >= .15, 'First pair gate before qualification')
        with prepared() as root:
            namespace = runpy.run_path(str(HERE / 'guard.py'))
            run = namespace['run']
            run.__globals__.update(HERE=folder, SOURCE=root, MANIFEST=HERE / 'INPUT-MANIFEST.json',
                                  AGGREGATE=900 if args.phase == 'pair' else 1500)
            if args.phase == 'pair':
                run('baseline-verify', 'research/selected-quadratic-replay/verify.py')
                run('baseline-cross', 'research/selected-quadratic-replay/cross.py')
                run('candidate-normal', str(HERE / 'joint.py'))
                compare(folder)
            else:
                run('candidate-optimized', str(HERE / 'joint.py'), True)
                require((folder / 'runs/candidate-normal/stdout.txt').read_bytes() ==
                        (folder / 'runs/candidate-optimized/stdout.txt').read_bytes(),
                        'Complete normal and optimized outputs identical')
                print('PASS_SINGLE_PASS_OPTIMIZED_QUALIFICATION', flush=True)


if __name__ == '__main__':
    main()
