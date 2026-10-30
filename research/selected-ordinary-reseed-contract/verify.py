#!/usr/bin/env python3
"""Source bindings and exact separators only; does not prove interface semantics."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]


def require(value, message):
    if not value:
        raise SystemExit('FAIL ' + message)


def read(path):
    return json.loads((ROOT / path).read_text())


def strict_below(value, denominator):
    return F((value.numerator * denominator - 1) // value.denominator, denominator)


def step(backend, covered, rho, grid):
    exact = (1-rho)*covered + rho*backend
    admitted = strict_below(exact, grid)
    if not backend < admitted < exact < covered < rho < 1-exact:
        raise ValueError('completed seed or separator gap invalid')
    return admitted


def main():
    selected = read('certificates/selected-result.json')
    require(selected['source_manifest'] == 'certificates/frontier6030-source.json', 'selected source changed')
    manifest = read(selected['source_manifest'])['files']
    for path in ('certificates/frontier6030/CLAIM.json', 'notes/three-stage-cover-bit.tex',
                 'notes/batched-bit-rows.tex', 'docs/research/pr-intake-evidence/pr4359/PROOF-REVIEW.md',
                 'docs/research/pr-intake-evidence/pr4470/PROOF-REVIEW.md'):
        require(manifest.get(path) == hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),
                'selected-source binding ' + path)
    consumer = (ROOT/'research/bit-finite-ordinary-bootstrap/PROOF.md').read_bytes()
    require(hashlib.sha256(consumer).hexdigest() == '5cabee7e5264ab0d674d5d591b4a3880ad460a546bcf5d53067eeeb9aff68df2',
            'PR4814 consumer clause version')
    b = F(read('certificates/frontier6030/CLAIM.json')['ordinary_BIT_saving'])
    require(b == F('0.0034363538396'), 'wrong ordinary seed')
    outer = read('research/g20-conjugation-admission/ORDINARY-RESULT.json')
    covered, rho, grid = F(outer['C1']), F(outer['params']['rho']), outer['params']['grid_denominator']
    levels = []
    for _ in range(6):
        b = step(b, covered, rho, grid)
        levels.append(str(b))
    require(F(levels[4]) < F(outer['admitted']) == F(levels[5]), 'six-level endpoint')
    require(strict_below(F(3,10),10) == F(2,10), 'strict-grid equality control')
    try:
        step(covered, covered, rho, grid)
    except ValueError:
        pass
    else:
        raise SystemExit('FAIL equal seed/covered exponent must reject')
    # Exact finite controls for the separate two-chunk padding lemma.
    for radix in (3,5,17):
        for width in (1,2,7):
            size = radix**width
            binary = 1 << (size-1).bit_length()
            require(size <= binary < 2*size and F(binary**2,size**2) < 4, 'radix adapter control')
    print('PASS_SELECTED_ORDINARY_RESEED_CONTRACT_BINDINGS ' + json.dumps({'levels':levels,
          'scope':'source bindings and arithmetic; conditional interface proof is README.md'}))


if __name__ == '__main__':
    main()
