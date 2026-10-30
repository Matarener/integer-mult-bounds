#!/usr/bin/env python3
"""Compare complete publication checks, with imports and profiling outside timing."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = '721c03822c421b7f7fcbb2598993b947c4d88419'
PACKAGES = ('research/stage-zero-forced-translation',
            'research/p104-helper470-twin-rung-removal')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('cannot load checker: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(baseline, candidate, package, repeats):
    samples = {'baseline': [], 'candidate': []}
    receipt = None
    for _ in range(repeats):
        for arm, checker in (('baseline', baseline), ('candidate', candidate)):
            start = time.perf_counter()
            result = checker.check(ROOT, package, BASE, check_source_history=True)
            samples[arm].append(time.perf_counter() - start)
            if receipt is None:
                receipt = result
            if result != receipt:
                raise ValueError('complete publication receipts differ')
    summary = {}
    for arm, values in samples.items():
        summary[arm] = {'seconds': values, 'median_seconds': statistics.median(values),
                        'range_seconds': [min(values), max(values)]}
    summary['fraction_reduced'] = 1 - (summary['candidate']['median_seconds'] /
                                       summary['baseline']['median_seconds'])
    return {'package': package, 'complete_receipt': receipt, 'samples': summary,
            'successful_checks': 2 * repeats, 'errors': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=9, choices=range(5, 32))
    args = parser.parse_args()
    if not args.scratch.is_dir():
        parser.error('--scratch must name an existing external directory')
    if args.scratch.resolve().is_relative_to(ROOT):
        parser.error('scratch must be outside the checkout')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import research_package as runner
    original = subprocess.run(
        ['git', 'show', BASE + ':scripts/check_research_commit.py'], cwd=ROOT,
        env=runner.git_source_env(), capture_output=True, check=True, timeout=30).stdout
    current = ROOT / 'scripts/check_research_commit.py'
    with tempfile.TemporaryDirectory(dir=args.scratch) as temporary:
        path = Path(temporary) / 'baseline.py'
        path.write_bytes(original)
        baseline = load_module('baseline_publication_checker', path)
        candidate = load_module('candidate_publication_checker', current)
        results = [compare(baseline, candidate, name, args.repeats) for name in PACKAGES]
    report = {'schema': 'publication-metadata-reuse-benchmark/v1', 'base_commit': BASE,
              'python': sys.version, 'platform': platform.platform(),
              'baseline_sha256': hashlib.sha256(original).hexdigest(),
              'candidate_sha256': hashlib.sha256(current.read_bytes()).hexdigest(),
              'runner_sha256': hashlib.sha256((ROOT / 'scripts/research_package.py').read_bytes()).hexdigest(),
              'timed_region': 'complete check(); imports and baseline extraction excluded',
              'order': 'baseline,candidate repeated', 'results': results}
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
