"""Real optimized/unoptimized CLI controls. ToikY/Codex, Apache-2.0."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def run(root, checker, optimized, expected):
    args = [sys.executable, '-I', '-Werror', '-B'] + (['-O'] if optimized else [])
    args.append(str(root / checker))
    if checker == 'independent.py':
        args += ['--word', str(root / 'source/inputs/BASE-WORD.json.gz'),
                 '--check', str(root / 'INDEPENDENT-RESULT.json')]
    proc = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=30)
    need((proc.returncode == 0) == expected,
         f'{checker} optimized={optimized} expected={expected}: {proc.stdout}{proc.stderr}')
    if expected:
        need('PASS_' in proc.stdout, 'positive receipt')

def mutate(root, case):
    if case == 'source':
        path = root / 'source/inputs/BASE-WORD.json.gz'
        raw = bytearray(path.read_bytes()); raw[-1] ^= 1
        path.write_bytes(raw)
    elif case in ('primary-price', 'independent-cap'):
        path = root / ('RESULT.json' if case == 'primary-price' else 'INDEPENDENT-RESULT.json')
        data = json.loads(path.read_text())
        if case == 'primary-price':
            data['canonical_delta']['1'] += 1
        else:
            data['maximal_entrance'] = [261, 133, 85, 45]
        path.write_text(json.dumps(data))
    elif case == 'missing-primary':
        (root / 'RESULT.json').unlink()
    elif case == 'missing-independent':
        (root / 'INDEPENDENT-RESULT.json').unlink()
    else:
        raise ValueError(case)

def main():
    checks = 0
    for optimized in (False, True):
        for checker in ('verify.py', 'independent.py'):
            run(ROOT, checker, optimized, True); checks += 1
        for case, checkers in (
            ('source', ('verify.py', 'independent.py')),
            ('primary-price', ('verify.py',)),
            ('independent-cap', ('verify.py', 'independent.py')),
            ('missing-primary', ('verify.py',)),
            ('missing-independent', ('verify.py', 'independent.py'))):
            with tempfile.TemporaryDirectory(prefix='warp0-cli-') as temp:
                owned = Path(temp) / 'package'
                shutil.copytree(ROOT, owned, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                # Registry exports are read-only; mutate only owned copies.
                os.chmod(owned, 0o755)
                for child in owned.rglob('*'):
                    os.chmod(child, 0o755 if child.is_dir() else 0o644)
                mutate(owned, case)
                for checker in checkers:
                    run(owned, checker, optimized, False); checks += 1
    print(json.dumps({'status': 'PASS_WARP_ZERO_REAL_CLI_CONTROLS', 'checks': checks}, sort_keys=True))
if __name__ == '__main__':
    main()
