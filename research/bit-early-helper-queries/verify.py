#!/usr/bin/env python3
"""Verify the pinned forward BIT helper-query interface and its controls."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import model

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE_PATHS = {
    'research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz',
    'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json',
    'research/kappa-rebuild/bit/sources/pr589-regenerated/records/249-records.bin',
    'research/kappa-rebuild/bit/BIT-P3-NATIVE-BINDING.json',
}


def check_sources(pins, changed=None):
    result = {}
    for row in pins:
        path = row['path']
        data = changed[path] if changed and path in changed else (ROOT / path).read_bytes()
        digest = sha256(data).hexdigest()
        if digest != row['sha256']:
            raise ValueError('Source bytes differ: ' + path)
        result[path] = digest
    return result


def run():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    pins = [row for row in sources['files'] if row['usage'] == 'input']
    paths = [row['path'] for row in pins]
    declared = json.loads((PACKAGE / 'VERIFY.json').read_text())['inputs']
    if len(paths) != 4 or set(paths) != SOURCE_PATHS or set(declared) != SOURCE_PATHS:
        raise ValueError('The four live source inputs must be pinned and declared')
    checked = check_sources(pins)
    controls = []
    for path in sorted(SOURCE_PATHS):
        data = (ROOT / path).read_bytes()
        changed = bytes([data[0] ^ 1]) + data[1:]
        try:
            check_sources(pins, {path: changed})
        except ValueError as error:
            if str(error) != 'Source bytes differ: ' + path:
                raise
            controls.append({'source': path, 'result': 'REJECT_CHANGED_BYTES'})
        else:
            raise ValueError('A source mutation passed: ' + path)
    evidence = model.run()
    return {
        'schema_version': 1,
        'status': 'PASS_BIT_EARLY_HELPER_QUERIES',
        'publication_base': sources['base_commit'],
        'source_sha256': checked,
        'source_mutation_controls': controls,
        'evidence': evidence,
        'new_kappa': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    retained = PACKAGE / 'RESULT.json'
    if retained.exists() and json.loads(retained.read_text()) != result:
        raise ValueError('The retained result differs from the exact replay')
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS_BIT_EARLY_HELPER_QUERIES queries=222 routes=111 source_controls=4 owned_controls=5 new_kappa=false')


if __name__ == '__main__':
    main()
