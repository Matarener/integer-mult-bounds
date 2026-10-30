"""Replay the pinned G20 package with an explicit gzip level.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The two producer variants retain their source notices and all source checks.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/g20-conjugation-admission'
VARIANTS = {
    'integration.py': ('gzip.compress(raw, mtime=0)',
                       'gzip.compress(raw, compresslevel=COMPRESSION_LEVEL, mtime=0)'),
    'global_retirement.py': ('gzip.compress(stream,mtime=0)',
                            'gzip.compress(stream,compresslevel=COMPRESSION_LEVEL,mtime=0)'),
}
IMPORT = 'from replay_options import COMPRESSION_LEVEL\n'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    files = json.loads((HERE / 'SOURCES.json').read_bytes())['files']
    inputs = [row for row in files if row['usage'] == 'input']
    for row in inputs:
        need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
             'source hash ' + row['path'])
    return len(inputs)


def check_variant(name, text):
    original = (SOURCE / name).read_text()
    old, new = VARIANTS[name]
    need(original.count(old) == 1, 'One pinned compression call in ' + name)
    # The complete source text must match, except for the import and keyword.
    expected = original.replace(old, new)
    lines = expected.splitlines(keepends=True)
    # Use the source's local import path, including under isolated Python.
    index = 1 + next(i for i, line in enumerate(lines)
                     if line.startswith('sys.path.insert('))
    lines.insert(index, IMPORT)
    need(text == ''.join(lines), 'producer variant changed a source check: ' + name)


def controls():
    rejected = []
    for name in VARIANTS:
        text = (HERE / 'producers' / name).read_text()
        check_variant(name, text)
        for label, mutant in [('deleted_check', text.replace('need(', 'print(', 1)),
                              ('wrong_level_binding', text.replace('compresslevel=COMPRESSION_LEVEL',
                                                                   'compresslevel=0')),
                              ('extra_statement', text + '\nraise SystemExit(0)\n')]:
            try:
                check_variant(name, mutant)
            except ValueError:
                rejected.append(name + ':' + label)
            else:
                raise ValueError('Producer mutation accepted: ' + label)
    return rejected


def replay(level):
    need(type(level) is int and 0 <= level <= 9, 'gzip level must be an integer from0 through9')
    inputs = authenticate()
    rejected = controls()
    with tempfile.TemporaryDirectory(prefix='g20-compression-') as folder:
        root = Path(folder) / 'package'
        shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        # Only the disposable copy needs write access. The sealed input stays read-only.
        root.chmod(0o755)
        for path in root.rglob('*'):
            path.chmod(0o755 if path.is_dir() else 0o644)
        for name in VARIANTS:
            (root / name).write_bytes((HERE / 'producers' / name).read_bytes())
        (root / 'replay_options.py').write_text('COMPRESSION_LEVEL = ' + str(level) + '\n')
        args = [sys.executable, '-I', '-B', '-W', 'error']
        if sys.flags.optimize:
            args.append('-O')
        completed = subprocess.run(args + [str(root / 'verify.py')], cwd=root,
                                   capture_output=True, text=True, timeout=570)
        need(completed.returncode == 0, completed.stdout + completed.stderr)
        expected = ['PASS_REBUILT ' + name for name in
                    ['integration.py', 'global_retirement.py', 'ordinary.py', 'independent.py']]
        expected += ['PASS_REJECTED_MISSING_TARGET_DEBIT',
                     'PASS_G20_CONJUGATION_COMPLETE_ORDINARY_003507719059749']
        need(completed.stdout.splitlines() == expected, 'Complete source verifier receipt')
    need(authenticate() == inputs, 'Source inventory changed')
    return {'source_inputs': inputs, 'producer_controls': rejected,
            'source_stdout_sha256': sha256(completed.stdout.encode()).hexdigest(),
            'source_receipt': expected, 'compression_level': level}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--level', type=int, choices=range(10), default=1)
    args = parser.parse_args()
    print(json.dumps(replay(args.level), sort_keys=True))
    print('PASS_COMPLETE_G20_COMPRESSION_REPLAY')


if __name__ == '__main__':
    main()
