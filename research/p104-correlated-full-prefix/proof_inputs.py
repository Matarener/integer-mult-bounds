"""Authenticate retained mathematical premises without foreign Git objects."""

import hashlib
import json

from engine import HERE, need

PINS = {
    'PR3382_PROOF.md': '1ca8c0e7e78f0f39de6cff7accc68ccd3901bfb50759bf7a2e2896bcf63bf081',
    'PR3416_PROOF.md': '0dc1c35158902299fc8748c8baf89205483562f041e9050580e6579c331ebeb5',
    'PR3449_PROOF.md': '66ed7dbf4748eb590b1e8fe4c41ef924c1c45461c66d9de4cf00771a2a403ea0',
}


def authenticate():
    for name, expected in PINS.items():
        path = HERE / 'inputs' / name
        need(path.is_file() and not path.is_symlink(), 'regular proof source')
        with path.open('rb') as handle:
            raw = handle.read(1024 * 1024 + 1)
        need(len(raw) <= 1024 * 1024 and hashlib.sha256(raw).hexdigest() == expected,
             'retained proof digest')
    with (HERE / 'inputs/ORIGINS.json').open('rb') as handle:
        raw = handle.read(16385)
    need(len(raw) <= 16384, 'proof origins capacity')
    origins = json.loads(raw)['retained_proofs']
    need(len(origins) == 3 and {r['file']: r['sha256'] for r in origins} == PINS,
         'proof origins inventory')
    return PINS
