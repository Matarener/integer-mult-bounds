"""Replay committed mathematical evidence. Nick Petalas, Apache-2.0."""

import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    """Compile the exact read bytes, bypassing all preexisting bytecode caches."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    rows = [row for row in manifest['files'] if row['usage'] == 'input']
    require(len(rows) == 3, 'source closure differs')
    for row in rows:
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT),
                'source absent or nonregular')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'],
                'source bytes differ')


def run():
    sources()
    tapes = load('direct_twiddle_tapes', PACKAGE / 'tapes.py')
    checks = load('direct_twiddle_checks', PACKAGE / 'checks.py')
    canonical = load('direct_twiddle_canonical', ROOT / 'research/synthetic-twiddle-circuit/circuit.py')
    return {'schema_version': 1, 'small': checks.small(tapes, canonical),
            'wide': checks.wide(tapes, canonical), 'boundary_rejections': checks.boundaries(tapes),
            'failed_read_restoration_and_retry': checks.failures(tapes),
            'scope': 'Four sequential data tapes with supplied immutable shape control; no encoded parser, complete consumer, supplier or kappa.'}


def main():
    result = run()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2))
    else:
        require(not sys.argv[1:], 'unknown arguments')
        require(result == json.loads((PACKAGE / 'RESULT.json').read_bytes()), 'receipt differs')
        print('PASS_DIRECT_TWIDDLE_TAPES', result['small']['addresses'], len(result['wide']))


if __name__ == '__main__':
    main()
