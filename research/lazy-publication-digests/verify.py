#!/usr/bin/env python3
"""Exercise the real byte, history, immutable-object and executable-mode checks."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TESTS = (
    'test_research_commit_bytes.py',
    'test_research_source_history.py',
    'test_research_commit_modes.py',
    'test_research_git_replacements.py',
)


def main():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in TESTS:
        discovered = loader.discover(str(ROOT / 'tests'), pattern=name)
        if discovered.countTestCases() == 0:
            raise ValueError('required test module is empty: ' + name)
        suite.addTests(discovered)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    sources = ['scripts/check_research_commit.py', 'scripts/research_package.py']
    sources.extend('tests/' + name for name in TESTS)
    sources.extend('research/lazy-publication-digests/' + name
                   for name in ('verify.py', 'benchmark.py', 'run_check.py'))
    print('PASS_LAZY_PUBLICATION_DIGESTS ' + json.dumps({
        'tests': result.testsRun, 'skipped': len(result.skipped),
        'failures': len(result.failures), 'errors': len(result.errors),
        'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                          for name in sources},
    }, sort_keys=True))


if __name__ == '__main__':
    main()
