"""Source custody only: freeze a new stage without imports or scientific runs."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    args = parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in args.name):
        raise ValueError('Simple new stage name required')
    stage = HERE / 'stages' / args.name
    stage.mkdir()
    shutil.copytree(HERE / 'baseline', stage / 'baseline')
    for name in ('PLAN.md', 'PLAN.json', 'run_guarded.py', 'freeze_stage.py'):
        shutil.copy2(HERE / name, stage / name)
    for directory in ('integration', 'priorities'):
        for source in sorted((HERE / directory).rglob('*')):
            if source.is_symlink():
                raise ValueError('Symlinked working source')
            if source.is_file() and source.suffix in ('.py', '.c', '.json', '.md'):
                if source.suffix == '.py':
                    ast.parse(source.read_bytes())
                target = stage / source.relative_to(HERE)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    jobs = {}
    for lane in ('none', 'sets', 'guards', 'trace', 'all'):
        jobs['finite-' + lane] = {'lanes': lane, 'finite_only': True}
        jobs['finite-O-' + lane] = {'lanes': lane, 'finite_only': True, 'optimized': True}
        jobs['full-' + lane] = {'lanes': lane, 'finite_only': False}
    (stage / 'JOBS.json').write_text(json.dumps(jobs, indent=2, sort_keys=True) + '\n')
    rows = {}
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            path.chmod(0o444 | (path.stat().st_mode & 0o111))
            rows[str(path.relative_to(stage))] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                                                'mode': path.stat().st_mode & 0o777}
    receipt = {'schema': 'h25-bookkeeping-immutable-stage-v1', 'files': rows,
               'runner_sha256': hashlib.sha256((HERE / 'run_guarded.py').read_bytes()).hexdigest(),
               'baseline_head': '4f4159820c37f01d245784d1186bd51fcbc8ebb6',
               'baseline_arm': 'native C, original controls and observations retained',
               'scientific_execution_during_freeze': False}
    (stage / 'STAGE.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    (stage / 'STAGE.json').chmod(0o444)
    for path in sorted(stage.rglob('*'), reverse=True):
        if path.is_dir():
            path.chmod(0o555)
    stage.chmod(0o555)
    print(json.dumps({'stage': str(stage), 'files': len(rows),
                      'stage_sha256': hashlib.sha256((stage / 'STAGE.json').read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
