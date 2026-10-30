"""Time serial fresh processes with identical complete scientific output."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from pins import authenticate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    authenticate()
    implementation = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}
    rows = []
    expected = None
    for mode in ('literal', 'quadratic', 'quadratic', 'literal', 'literal', 'quadratic'):
        authenticate()
        if implementation != {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob('*.py'))}:
            raise ValueError('Benchmark implementation changed between processes')
        path = (ROOT / 'research/p104-helper-subspace-splits/verify.py'
                if mode == 'literal' else HERE / 'run.py')
        start = time.perf_counter()
        run = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT,
                             capture_output=True, timeout=600)
        elapsed = time.perf_counter() - start
        if run.returncode or run.stderr:
            raise ValueError('Benchmark replay failed: ' + run.stderr.decode(errors='replace'))
        digest = sha256(run.stdout).hexdigest()
        if expected is None:
            expected = digest
        if digest != expected:
            raise ValueError('Complete scientific stdout differs')
        row = {'mode': mode, 'seconds': elapsed, 'stdout_sha256': digest}
        rows.append(row)
        print(json.dumps(row, sort_keys=True), flush=True)
    medians = {mode: statistics.median(r['seconds'] for r in rows if r['mode'] == mode)
               for mode in ('literal', 'quadratic')}
    result = {'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine(),
              'implementation_sha256': implementation,
              'rows': rows, 'median_seconds': medians,
              'median_speedup': medians['literal'] / medians['quadratic'],
              'scope': 'Complete selected scientific replay; fresh processes, warm OS caches, variable host load. Extra adapter corpus and literal cross-check are separate.',
              'inputs': {r['path']: r['sha256'] for r in json.loads((HERE / 'SOURCES.json').read_bytes())['files'] if r['usage'] == 'input'}}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
