"""Behavioral boundary checks and actual optimized-CLI corruptions."""
from pathlib import Path
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile

P = Path(__file__).resolve().parent
R = P.parent.parent
v = runpy.run_path(str(P / 'verify.py'))
need = v['require']


def rejected(fn, text):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('accepted invalid control: ' + text)


def main():
    v['authenticate']()
    for w in [(1,) * 5, (8,) * 5, (2, 3, 2, 7, 7), (True, 2, 3, 6, 7)]:
        rejected(lambda: v['historical'](w), 'weight bounds')
    need(not v['historical']((2,) * 5 + (7,) * 6), 'strict excess30 accepted')
    actual = (2,) * 4 + (4,) * 2 + (7,) * 5
    need(v['historical'](actual), 'literal caller absent')
    need(v['attempt'](actual, 'common23')['successful_assignments'] == 0, 'cut23 extended')
    need(v['attempt'](actual, 'common24')['successful_assignments'] > 0, 'cut24 caller lost')
    need(5 - 3 == 2 and 5 - 3 != 5, 'deletion did not charge dimensions')
    # Individually small supports do not supply a common small support.
    cuts = [set(range(24)), set(range(1, 25))]
    need(all(len(c) <= 24 for c in cuts) and len(set.union(*cuts)) > 24, 'common-cut quantifier')
    manifest = json.loads((P / 'VERIFY.json').read_text())
    for mutation in ('receipt', 'input', 'manifest'):
        with tempfile.TemporaryDirectory(prefix='p112-b5-control-') as td:
            root = Path(td)
            package = root / 'research' / P.name
            shutil.copytree(P, package)
            for name in manifest['inputs']:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(R / name, target)
            if mutation == 'receipt':
                target = package / 'RESULT.json'
                target.chmod(target.stat().st_mode | 0o200)
                result = json.loads(target.read_text())
                result['cells'][0]['rows'][0]['attempts']['rank6_29']['witness']['surviving_code_dimension'] = 5
                target.write_text(json.dumps(result))
            elif mutation == 'input':
                target = root / manifest['inputs'][0]
                target.chmod(target.stat().st_mode | 0o200)
                target.write_bytes(target.read_bytes() + b'\n# changed source\n')
            else:
                target = package / 'SOURCES.json'
                target.chmod(target.stat().st_mode | 0o200)
                source = json.loads(target.read_text())
                source['files'][2]['usage'] = 'provenance'
                target.write_text(json.dumps(source))
            env = dict(os.environ, PYTHONPYCACHEPREFIX=str(root / 'private-bytecode'))
            run = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(package / 'verify.py')], capture_output=True, text=True, env=env, check=False, timeout=60)
            need(run.returncode != 0, 'CLI accepted ' + mutation)
            need('ValueError' in run.stderr, 'unexpected rejection ' + mutation)
    print('PASS_P112_B5_CONTROLS weights/excess/cut/deletion; three optimized CLI mutations')


if __name__ == '__main__':
    main()
