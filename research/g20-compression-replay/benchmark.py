"""Measure complete G20 replays in fresh serial processes.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Run this audit separately from the registered correctness check.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import zlib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    verify.authenticate()
    rows = []
    for mode in ['source', 1, 2, 0, 0, 2, 1, 'source', 'source', 1, 2, 0]:
        command = [sys.executable, '-I', '-B', '-W', 'error']
        if mode == 'source':
            command += [str(verify.SOURCE / 'verify.py')]
        else:
            command += [str(HERE / 'verify.py'), '--level', str(mode)]
        start = time.perf_counter()
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        seconds = time.perf_counter() - start
        verify.need(result.returncode == 0, result.stdout + result.stderr)
        if mode == 'source':
            digest = sha256(result.stdout.encode()).hexdigest()
        else:
            receipt = json.loads(result.stdout.splitlines()[0])
            digest = receipt['source_stdout_sha256']
        verify.need(not rows or digest == rows[0]['source_stdout_sha256'],
                    'All modes must complete the same source receipt')
        rows.append({'mode': mode, 'seconds': seconds, 'source_stdout_sha256': digest})
        medians = {str(key): statistics.median(row['seconds'] for row in rows if row['mode'] == key)
                   for key in dict.fromkeys(row['mode'] for row in rows)}
        output = {'python': platform.python_version(), 'platform': platform.platform(),
                  'machine': platform.machine(), 'zlib': zlib.ZLIB_VERSION,
                  'method': 'Fresh serial processes; alternating order; warm operating-system cache; no profiler.',
                  'rows': rows, 'median_seconds': medians,
                  'speedup_vs_unmodified_source': {key: medians['source'] / value
                                                 for key, value in medians.items() if key != 'source'}}
        args.output.write_text(json.dumps(output, indent=2) + '\n')
        print(json.dumps(rows[-1]), flush=True)
    verify.authenticate()


if __name__ == '__main__':
    main()
