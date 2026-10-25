#!/usr/bin/env python3
"""Retain selected public research deltas using the prior authenticated fetcher.

The retained Git blob checks and immutable commit URLs are credited to
kappa-1745-continuation/fetch_pull.py. No old directory is mutated.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'kappa-1745-continuation/fetch_pull.py'

if __name__ == '__main__':
    spec = importlib.util.spec_from_file_location('retained_public_pull_fetcher', SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.main()
