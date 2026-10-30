#!/usr/bin/env python3
"""Alternate complete publication preflights; all generated files stay in scratch."""
import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

BASE = '721c03822c421b7f7fcbb2598993b947c4d88419'
IMPLEMENTATION = 'scripts/check_research_commit.py'
PACKAGE = 'research/physical-gaussian-core'
ROOT = Path(__file__).resolve().parents[2]


def checked_run(argv, **kwargs):
    result = subprocess.run(argv, capture_output=True, check=False, timeout=60, **kwargs)
    if result.returncode != 0 or result.stderr:
        raise ValueError('command failed: ' + repr(argv) + '\n' + result.stderr.decode())
    return result.stdout


def prepare(scratch):
    env = os.environ.copy()
    env['GIT_NO_REPLACE_OBJECTS'] = '1'
    source = checked_run(['git', 'show', BASE + ':' + IMPLEMENTATION], cwd=ROOT, env=env)
    baseline = scratch / 'check_research_commit_before.py'
    baseline.write_bytes(source)
    return {'before': baseline, 'after': ROOT / IMPLEMENTATION}


def command(implementation):
    return [sys.executable, '-I', '-W', 'error', '-B',
            str(Path(__file__).with_name('run_check.py')),
            '--implementation', str(implementation), '--root', str(ROOT),
            '--package', PACKAGE, '--ref', BASE]


def measure(paths, rounds):
    # Every sample includes startup, imports, all file comparisons and ancestry.
    expected = checked_run(command(paths['before']), cwd=ROOT)
    if checked_run(command(paths['after']), cwd=ROOT) != expected:
        raise ValueError('warmup complete receipts differ')
    rows = []
    for trial in range(rounds):
        for side in ('before', 'after'):
            start = time.perf_counter()
            actual = checked_run(command(paths[side]), cwd=ROOT)
            seconds = time.perf_counter() - start
            if actual != expected:
                raise ValueError('complete receipt differs at ' + side)
            rows.append({'trial': trial + 1, 'side': side, 'seconds': seconds})
    return rows, expected


def summarize(rows):
    result = {}
    for side in ('before', 'after'):
        values = [row['seconds'] for row in rows if row['side'] == side]
        result[side] = {'median': statistics.median(values),
                        'minimum': min(values), 'maximum': max(values), 'runs': len(values)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch-dir', type=Path, required=True)
    parser.add_argument('--rounds', type=int, default=5)
    args = parser.parse_args()
    if not 5 <= args.rounds <= 30:
        parser.error('rounds must be between 5 and 30')
    args.scratch_dir.mkdir(parents=True, exist_ok=True)
    paths = prepare(args.scratch_dir)
    load_before = os.getloadavg() if hasattr(os, 'getloadavg') else None
    rows, expected = measure(paths, args.rounds)
    summary = summarize(rows)
    receipt = {
        'schema': 'lazy-publication-digests-benchmark/v1', 'base_commit': BASE,
        'package': PACKAGE, 'python': sys.version, 'platform': platform.platform(),
        'cpu_count': os.cpu_count(), 'load_before': load_before,
        'load_after': os.getloadavg() if hasattr(os, 'getloadavg') else None,
        'implementation_sha256': {side: hashlib.sha256(path.read_bytes()).hexdigest()
                                  for side, path in paths.items()},
        'complete_stdout': expected.decode(), 'samples': rows, 'summary': summary,
        'median_fraction_saved': 1 - summary['after']['median'] / summary['before']['median'],
        'errors': 0,
        'verdict': ('faster' if summary['after']['maximum'] < summary['before']['minimum']
                    else 'inconclusive'),
    }
    output = args.scratch_dir / 'benchmark.json'
    output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
