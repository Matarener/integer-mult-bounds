"""Run both unchanged PR5818 small-control commands in fresh interpreters."""
import subprocess
import sys
from pathlib import Path
import tempfile

import retained
from retained import baseline
from setup_cache import require


if __name__ == '__main__':
    require(not sys.argv[1:], 'No inherited-control arguments')
    original = retained.HERE
    with tempfile.TemporaryDirectory(prefix='setup-custody-control-') as temporary:
        root = Path(temporary)
        (root / 'inputs').mkdir()
        raw = bytearray((original / 'inputs/PR5818.tar').read_bytes())
        raw[len(raw) // 2] ^= 1
        (root / 'inputs/PR5818.tar').write_bytes(raw)
        retained.HERE = root
        try:
            try:
                retained.payload()
            except ValueError as error:
                require(str(error) == 'Exact PR5818 bundle', 'Exact top-level corruption predicate')
            else:
                raise ValueError('Corrupted top-level bundle accepted')
        finally:
            retained.HERE = original
    print('PASS_LITERAL_SETUP_BUNDLE_CORRUPTION_BEFORE_IMPORT', flush=True)
    with baseline() as base:
        for script in ('checks.py', 'custody_controls.py'):
            command = [sys.executable, '-B']
            if sys.flags.optimize:
                command.append('-O')
            command.append(str(base / script))
            completed = subprocess.run(command)
            require(completed.returncode == 0, 'Original control command passed: ' + script)
