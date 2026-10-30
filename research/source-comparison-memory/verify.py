#!/usr/bin/env python3
"""Replay the new source-comparison contracts; do not benchmark in CI.

Produced by Nick Petalas. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]


def main():
    path = ROOT / "tests/test_research_source_comparison.py"
    spec = importlib.util.spec_from_file_location("source_comparison_contracts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful() or result.testsRun != 7 or result.skipped:
        raise SystemExit("source comparison contracts failed or were skipped")
    paths = (ROOT / "scripts/research_package.py", path, Path(__file__).resolve())
    receipt = {"tests": result.testsRun, "failures": len(result.failures),
               "errors": len(result.errors), "python": sys.version,
               "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in paths}}
    print("PASS_SOURCE_COMPARISON_MEMORY " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
