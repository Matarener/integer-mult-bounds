"""Alternating complete-command measurements, produced by Nick Petalas."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time

from verify import authenticate, execute, require


HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, choices=range(5, 11), default=5)
    args = parser.parse_args()
    authenticate()
    samples, expected = [], None
    for iteration in range(args.rounds):
        for name in ('retained_source.py', 'fast.py'):
            start = time.perf_counter()
            result = execute(HERE / name)
            elapsed = time.perf_counter()-start
            require(result.returncode == 0 and not result.stderr, 'measured command failed')
            if expected is None:
                expected = result.stdout
            require(result.stdout == expected, 'measured complete output changed')
            require(result.stdout.endswith(b'PASS_R16_RADICAL_TRIPLE_FANOUT no_new_kappa\n'),
                    'measured workload did not finish')
            samples.append(dict(engine=name, round=iteration+1, wall_seconds=elapsed,
                                stdout_sha256=hashlib.sha256(result.stdout).hexdigest()))
    summary = {}
    for name in ('retained_source.py', 'fast.py'):
        values = [s['wall_seconds'] for s in samples if s['engine'] == name]
        summary[name] = dict(median=statistics.median(values), minimum=min(values),
                             maximum=max(values))
    report = dict(samples=samples, summary=summary, errors=0, python=sys.version,
                  platform=platform.platform(), cpu_count=os.cpu_count(),
                  stdout_equal=True, load_average=os.getloadavg(),
                  source_sha256=hashlib.sha256((HERE/'retained_source.py').read_bytes()).hexdigest(),
                  fast_sha256=hashlib.sha256((HERE/'fast.py').read_bytes()).hexdigest())
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
