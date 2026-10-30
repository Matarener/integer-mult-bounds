#!/usr/bin/env python3
"""Reproduce scoped P104 negative screens; Python 3.12, standard library.

Jonathan Capalbo (jon314159), with substantial OpenAI Codex assistance.
Apache-2.0. No new kappa, supplier admission, or general optimality claim.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD_PATH = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
WORD_PIN = '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f'
VENDOR_PINS = {
    'vendor/pr6045/leakfix.py': 'dbbdc9ff9ebb55f1b9e832dcbe1aa5e407e7932a8d958a006bdaca6055e7f4ee',
    'vendor/pr6045/inputs/shapesplit.py': '11e8ef691b28fb4f401a8c2e97b6d462e7a004f0e215a28579d6a654b4ca3304',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticated_inputs():
    raw = (ROOT / WORD_PATH).read_bytes()
    need(digest(raw) == WORD_PIN, 'selected WORD bytes do not match the pinned PR6030 input')
    vendor = json.loads((HERE / 'VENDOR.json').read_text(encoding='utf-8'))
    declared = {row['path']: row['sha256'] for row in vendor['files']}
    need(declared == VENDOR_PINS, 'vendor declaration differs from frozen input set')
    for path, expected in VENDOR_PINS.items():
        need(digest((HERE / path).read_bytes()) == expected, 'vendored source drift: ' + path)
    decoded = gzip.decompress(raw)
    word = json.loads(decoded)
    need((word['public'], word['owned_fields'], len(word['program'])) == (770, 29, 22803),
         'unexpected selected-word dimensions')
    return word, dict(word_path=WORD_PATH, word_sha256=WORD_PIN,
                      decoded_sha256=digest(decoded), vendor_sha256=VENDOR_PINS)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    need(spec is not None and spec.loader is not None, 'cannot load package module ' + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def compute():
    word, sources = authenticated_inputs()
    # -B prevents writes but not stale bytecode reads. Isolate both before any
    # research module or frozen dependency is imported, including direct runs.
    with tempfile.TemporaryDirectory(prefix='p104-negative-pycache-') as cache:
        old_cache, old_write = sys.pycache_prefix, sys.dont_write_bytecode
        sys.pycache_prefix, sys.dont_write_bytecode = cache, True
        try:
            endpoints = load('endpoints')
            private_queries = load('private_queries')
            carrier = load('carrier')
            review_controls = load('review_controls')
            print('Checking fixed-word carrier programs...', flush=True)
            c = carrier.run(word, HERE / 'vendor/pr6045')
            print('Checking both endpoint windows...', flush=True)
            e = endpoints.run(word)
            print('Checking five private-query output seams...', flush=True)
            p = private_queries.run(word)
            print('Checking independent certificate and controls...', flush=True)
            review = review_controls.run(word, c, endpoints, private_queries)
            return dict(schema_version=1, sources=sources, carrier=c, endpoints=e,
                        private_queries=p, independent_review=review)
        finally:
            sys.pycache_prefix, sys.dont_write_bytecode = old_cache, old_write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write the checked semantic receipt to this new file')
    args = parser.parse_args()
    expected_path = HERE / 'EXPECTED.json'
    need(expected_path.is_file(), 'missing committed EXPECTED.json')
    expected = json.loads(expected_path.read_text(encoding='utf-8'))
    actual = compute()
    canonical = json.dumps(actual, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    need(actual == expected, 'semantic replay differs from EXPECTED.json; do not silently regenerate a claim')
    if args.output:
        need(not args.output.exists(), 'refusing to overwrite receipt')
        args.output.write_text(json.dumps(actual, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('PASS_P104_FIXED_WORD_NEGATIVE_SCREENS', digest(canonical.encode('utf-8')))


if __name__ == '__main__':
    main()
