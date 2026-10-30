"""Compare complete fresh E7 replays. Ali Romman with OpenAI Codex. Apache-2.0."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
from runpy import run_path
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run_path(str(HERE / 'verify.py'))['authenticate']()
    records = []
    for label in ('old', 'new', 'new', 'old', 'old', 'new'):
        entry = HERE / ('source/verify.py' if label == 'old' else 'classify.py')
        start = time.perf_counter()
        result = subprocess.run([sys.executable, '-I', '-B', str(entry)],
                                capture_output=True, check=True, timeout=180)
        seconds = time.perf_counter() - start
        if not result.stdout.startswith(b'PASS_E7_MINIMUM_SUPPORT_CLASSIFICATION\n'):
            raise ValueError('Missing complete classification result')
        record = dict(implementation=label, seconds=seconds,
                      stdout_sha256=sha256(result.stdout).hexdigest(),
                      stderr_sha256=sha256(result.stderr).hexdigest())
        records.append(record)
        print(json.dumps(record), flush=True)
    if len({row['stdout_sha256'] for row in records}) != 1:
        raise ValueError('Scientific output differs')
    medians = {name: statistics.median(row['seconds'] for row in records
                                      if row['implementation'] == name)
               for name in ('old', 'new')}
    receipt = dict(python=sys.version, platform=platform.platform(),
                   command_flags=['-I', '-B'], serial=True, records=records,
                   median_seconds=medians, speed_ratio=medians['old'] / medians['new'])
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
