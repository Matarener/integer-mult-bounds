"""Read-only exact replay with authenticated source closure and fixed receipt."""

import hashlib
import json
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def load(name, path):
    """Compile authenticated source bytes directly, never consuming a .pyc."""
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('changed or missing source: ' + row['path'])


def main():
    if sys.argv[1:]:
        raise ValueError('this read-only verifier accepts no arguments')
    sources()
    circuit = load('twiddle_circuit', PACKAGE / 'circuit.py')
    checks = load('twiddle_checks', PACKAGE / 'checks.py')
    physical = load('canonical_physical', ROOT / 'research/synthetic-layout-independent/physical.py')
    actual = checks.report(circuit, physical)
    expected = json.loads((PACKAGE / 'RESULT.json').read_text())
    circuit.require(actual == expected, 'scientific receipt differs')
    print(json.dumps(actual, sort_keys=True))


if __name__ == '__main__':
    main()
