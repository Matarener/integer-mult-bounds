#!/usr/bin/env python3
"""Fresh subprocess pairs; timings are evidence, never a CI acceptance threshold."""
import argparse
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from time import perf_counter
import fast_moments
import workload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worker', choices=('reference', 'fast'))
    ap.add_argument('--pairs', type=int, default=3)
    ap.add_argument('--output', type=Path)
    args = ap.parse_args()
    if args.worker:
        engine = fast_moments.load_engine(args.worker == 'fast')
        start = perf_counter()
        receipt = workload.run(engine)
        print(json.dumps({'mode': args.worker, 'seconds': perf_counter()-start,
                          'sha256': workload.digest(receipt)}))
        return
    if not 1 <= args.pairs <= 20:
        ap.error('--pairs must be 1..20')
    samples = []
    for j in range(args.pairs):
        order = ('reference', 'fast') if j % 2 == 0 else ('fast', 'reference')
        for mode in order:
            output = subprocess.check_output([sys.executable, '-B', __file__, '--worker', mode], text=True)
            samples.append(json.loads(output))
    if len({x['sha256'] for x in samples}) != 1:
        raise ValueError('different mathematical outputs; timing comparison invalid')
    medians = {mode: statistics.median(x['seconds'] for x in samples if x['mode'] == mode)
               for mode in ('reference', 'fast')}
    result = {'python': sys.version, 'platform': platform.platform(), 'samples': samples,
              'median_seconds': medians, 'median_speedup': medians['reference']/medians['fast'],
              'scope': '24 ranks x 12 exponents, complete moments and strict allowances; cold engine caches',
              'new_kappa': None}
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.output:
        if args.output.exists():
            raise ValueError('refusing to overwrite benchmark evidence')
        args.output.write_bytes(encoded.encode())
    print(encoded)


if __name__ == '__main__':
    main()
