"""Reject corruption and actual defects in the literal matrix audit.

Prepared for DLamdata with substantial OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
source = (HERE/'verify.py').read_text()
mutations = [
    ('wrong-first-overlap-expectation', 'hist[F(1, 2)] == 2*((1 << (2*n))-1)',
     'hist[F(1, 2)] == ((1 << (2*n))-1)', 'First Clifford overlap count'),
    ('tensor-width-erased', 'width) for b in matrices]',
     '1) for b in matrices]', 'Four-width positive fixture'),
    ('wrong-H-square-expectation', "== rotate(identity(1)), 'H-prime square retains i'",
     "== identity(1), 'H-prime square retains i'", 'H-prime square retains i'),
]
results = []
with tempfile.TemporaryDirectory(prefix='clifford-matrix-controls-') as tmp:
    root = Path(tmp)
    for name, old, new, diagnostic in mutations + [
        ('source-corrupted', None, None, 'Frozen source byte mismatch'),
        ('receipt-corrupted', None, None, 'Matrix receipt mismatch'),
    ]:
        target = root/name
        shutil.copytree(HERE, target, ignore=shutil.ignore_patterns('__pycache__'))
        # A read-only source export is valid input; only the temporary copy is edited.
        target.chmod(0o700)
        for path in target.rglob('*'):
            path.chmod(0o700 if path.is_dir() else 0o600)
        if old is not None:
            if source.count(old) != 1:
                raise RuntimeError('Mutation site not unique: '+name)
            (target/'verify.py').write_text(source.replace(old, new))
        elif name == 'source-corrupted':
            with (target/'source/PR5526-PROOF.md').open('ab') as stream:
                stream.write(b'\ncorruption control\n')
        else:
            path = target/'MATRIX-RESULT.json'
            result = json.loads(path.read_text())
            result['groups'][1]['exact_matrices'] += 1
            path.write_text(json.dumps(result))
        for optimized in (False, True):
            command = [sys.executable, '-I'] + (['-O'] if optimized else [])
            command += ['-W', 'error', '-B', str(target/'verify.py')]
            run = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if run.returncode == 0 or diagnostic not in run.stderr:
                raise RuntimeError('Wrong rejection: '+name+' '+run.stderr)
            results.append({'mutation':name,'optimized':optimized,
                            'exit':run.returncode,'diagnostic':diagnostic})
print(json.dumps(results,indent=2))
print('PASS_CLIFFORD_MATRIX_MUTATIONS')
