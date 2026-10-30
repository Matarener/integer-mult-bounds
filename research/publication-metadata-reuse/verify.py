#!/usr/bin/env python3
"""Run finite publication controls and emit a source-bound receipt."""
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATTERNS = ('test_research_publication_metadata_reuse.py',
            'test_research_source_history.py', 'test_research_commit_bytes.py',
            'test_research_commit_modes.py', 'test_research_git_replacements.py')


def main():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for pattern in PATTERNS:
        tests = loader.discover(str(ROOT / 'tests'), pattern=pattern)
        if tests.countTestCases() == 0:
            raise ValueError('no controls found: ' + pattern)
        suite.addTests(tests)
    count = suite.countTestCases()
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    if not result.wasSuccessful() or result.testsRun != count:
        raise SystemExit(1)
    names = ['scripts/check_research_commit.py', 'scripts/research_package.py',
             'scripts/export_research_package.py', 'scripts/new_research_package.py',
             'research/publication-metadata-reuse/verify.py']
    names.extend('tests/' + pattern for pattern in PATTERNS)
    receipt = {'schema': 'publication-metadata-reuse-controls/v1', 'tests_run': count,
               'skipped': [(str(test), reason) for test, reason in result.skipped],
               'source_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                                 for name in names}}
    print('PASS_PUBLICATION_METADATA_REUSE ' + json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
