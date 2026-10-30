#!/usr/bin/env python3
"""Registered check: equivalence tests and controls, then PR6030's unchanged primary verifier with fast tables.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0.
The exhaustive differential replay over the real workload is the separate command `run.py --mode differential`.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_equivalence  # noqa: E402
import run  # noqa: E402

if __name__ == '__main__':
    test_equivalence.main()
    run.main(['run.py', '--mode', 'fast'])
