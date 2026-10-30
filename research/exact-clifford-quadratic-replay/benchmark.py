"""Measure complete fresh-process replay; preserve every scientific result."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def benchmark(rounds, output):
    if rounds < 3 or output.exists():
        raise ValueError('Use at least three rounds and a fresh output path')
    records = []; reference = None
    orders = [('literal', 'tables', 'quadratic'), ('quadratic', 'tables', 'literal'),
              ('tables', 'literal', 'quadratic')]
    for round_ in range(rounds):
        for engine in orders[round_ % len(orders)]:
            command = [sys.executable, '-I', '-W', 'error', '-B', str(ROOT / 'run.py'), '--engine', engine]
            start = time.perf_counter()
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            elapsed = time.perf_counter() - start
            if process.returncode or process.stderr:
                raise ValueError('Replay failed: ' + engine + '\n' + process.stdout + process.stderr)
            if 'PASS_COMPLETE_SOURCE_RESULT a501b899b5f70e7cde6a10af4e4c2530cf9f4cb6ba53504828bf855ed3b74093' not in process.stdout:
                raise ValueError('Missing complete result equality')
            digest = sha256(process.stdout.encode()).hexdigest()
            if reference is not None and digest != reference:
                raise ValueError('Scientific stdout differs between engines')
            reference = digest
            record = dict(round=round_ + 1, engine=engine, seconds=elapsed, stdout_sha256=digest)
            records.append(record)
            print(json.dumps(record), flush=True)
    medians = {engine: statistics.median(r['seconds'] for r in records if r['engine'] == engine)
               for engine in orders[0]}
    result = dict(status='PASS_EQUAL_COMPLETE_REPLAY_BENCHMARK', utc=datetime.now(timezone.utc).isoformat(),
                  python=sys.version, platform=platform.platform(), machine=platform.machine(),
                  command_template=[sys.executable, '-I', '-W', 'error', '-B', 'run.py', '--engine', 'ENGINE'],
                  rounds=rounds, records=records, median_seconds=medians,
                  speedup_over_literal=medians['literal'] / medians['quadratic'],
                  speedup_over_tables=medians['tables'] / medians['quadratic'],
                  scope='Complete PR5698 replay including source admission, every old check and complete result equality. Fresh evaluator processes; operating-system caches are not flushed.')
    with output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(result['status'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    benchmark(args.rounds, args.output)
