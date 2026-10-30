#!/usr/bin/env python3
"""Run the complete preflight through either exact implementation file."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--implementation', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--package', required=True)
    parser.add_argument('--ref', required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.root / 'scripts'))
    spec = importlib.util.spec_from_file_location('publication_check', args.implementation)
    if spec is None or spec.loader is None:
        raise ValueError('implementation is not importable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = module.check(args.root, args.package, args.ref, check_source_history=True)
    print('PASS_RESEARCH_COMMIT_BYTES ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
