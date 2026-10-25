"""Actual optimized CLI rejection controls in a private Git-free source copy.

Only the temporary copy is mutated. The package and declared inputs are checked
for byte equality after all controls. Standard library only; no network or Git.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = Path('research/p112-triad-matroid-boundary')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((HERE / 'VERIFY.json').read_bytes())
    files = sorted(p for p in HERE.iterdir() if p.is_file())
    files += [ROOT / name for name in manifest['inputs']]
    before = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files}
    rejected = []
    with TemporaryDirectory(prefix='p112-triad-controls-') as directory:
        exported = Path(directory)
        for source in files:
            destination = exported / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        need(not (exported / '.git').exists(), 'Git-free export')
        script = exported / PACKAGE / 'verify.py'

        def invoke(expected=None):
            result = subprocess.run([sys.executable, '-I', '-O', '-Werror', '-B', str(script)],
                                    cwd=exported, text=True, capture_output=True, timeout=45)
            if expected is None:
                need(result.returncode == 0, 'restored CLI: ' + result.stderr[-2000:])
                need(json.loads(result.stdout)['status'] == 'PASS', 'restored result status')
            else:
                need(result.returncode != 0, 'corrupt CLI accepted: ' + expected)
                need(expected in result.stderr, 'unexpected rejection: ' + result.stderr[-2000:])

        def corrupt(relative, mutation, expected):
            target = exported / relative
            original = target.read_bytes()
            target.write_bytes(mutation(original))
            try:
                invoke(expected)
            finally:
                target.write_bytes(original)
            rejected.append(str(relative))

        # A semantically unchanged but unauthenticated input must fail before
        # computation, as must a changed retained mathematical premise.
        for relative in ('research/p112-rational-decoder-gate/CANDIDATE.json',
                         'research/p112-five-term-reader-floor/TEMPLATES.json'):
            corrupt(Path(relative), lambda raw: raw + b'\n', 'proof input hash')
        corrupt(PACKAGE / 'RETAINED-PR3538-PROOF.md', lambda raw: raw + b'\n',
                'retained proof hash')

        def false_minimum(raw):
            receipt = json.loads(raw)
            receipt['classes'][0]['VVV_minimum'] -= 1
            return json.dumps(receipt).encode('utf-8')

        corrupt(PACKAGE / 'RESULT.json', false_minimum,
                'complete per-signature minima and multiplicities')
        invoke()
    after = {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in files}
    need(before == after, 'scientific source tree changed')
    print(json.dumps({'status': 'PASS_CONTROLS', 'rejected_corruptions': rejected,
                      'restored_git_free_cli': 'PASS', 'source_tree_unchanged': True},
                     separators=(',', ':')))


if __name__ == '__main__':
    main()
