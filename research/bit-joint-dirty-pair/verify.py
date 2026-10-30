#!/usr/bin/env python3
"""Replay the source-bound finite evidence; the written proof is not kernel checked."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BOOTSTRAP = """from hashlib import sha256
from pathlib import Path
import sys
p = Path(sys.argv[1]).resolve()
b = p.read_bytes()
if sha256(b).hexdigest() != sys.argv[2]:
    raise ValueError('executed checker hash ' + p.name)
exec(compile(b, str(p), 'exec'), {'__name__': '__main__', '__file__': str(p)})
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    # String comparison preserves distinctions such as true versus 1.
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def main():
    manifest_bytes = (ROOT/'MANIFEST.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    expected_names = set(manifest['files'])
    observed_names = {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()}
    require(observed_names == expected_names | {'MANIFEST.json'}, 'complete package file inventory')
    authenticated = {}
    for name, digest in manifest['files'].items():
        path = ROOT/name
        authenticated[name] = path.read_bytes()
        require(not path.is_symlink() and sha256(authenticated[name]).hexdigest() == digest,
                'package hash '+name)
    flags = ['-I', '-B'] + (['-O'] if sys.flags.optimize else [])
    receipts = {}
    for key, filename in (('source', 'source_check.py'), ('finite_controls', 'check.py')):
        replay = subprocess.run([sys.executable, *flags, '-c', BOOTSTRAP,
                                 str(ROOT/filename), manifest['files'][filename]],
                                check=True, capture_output=True, text=True, timeout=45)
        require(not replay.stderr, 'unexpected checker stderr '+filename)
        receipts[key] = json.loads(replay.stdout)
    expected = json.loads(authenticated['RESULT.json'])
    require(canonical(receipts) == canonical(expected), 'full semantic receipts')
    require(receipts['source']['no_new_kappa'] is True and
            receipts['finite_controls']['no_new_kappa'] is True, 'scope markers')
    for name, original in authenticated.items():
        require((ROOT/name).read_bytes() == original, 'package changed during replay '+name)
    require(observed_names == {str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file()},
            'package inventory changed during replay')
    require((ROOT/'MANIFEST.json').read_bytes() == manifest_bytes, 'manifest changed during replay')
    print('PASS_JOINT_DIRTY_PAIR source_columns=660 sylvester_pairs=32768 '
          'optimum=2Phi_m(2) uniform_unary_full_endpoint no_new_kappa')


if __name__ == '__main__':
    main()
