"""Maximal two-source stagewise-exact entrance for the full prefix. Apache-2.0."""

import json
import sys

from engine import (HERE, INPUTS, coefficients, digest, divisible_pi, in_newton, load,
                    monomial, native, need, wrapper)
from module import invariants
from proof_inputs import authenticate
from trace import baseline, first_failure, matrix, prepared, replay, schedule


def admitted_fixture(rows, active, recipes):
    pivots = {}
    for al, _, bl, _ in rows:
        row = al ^ bl
        for _ in range(513):
            if not row:
                break
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
        else:
            raise ValueError('residue elimination capacity')
    need(len(pivots) == 19, 'Gaussian residue rank')
    free = next(s for s in range(512) if s not in pivots)
    kernel = 1 << free
    for bit, row in sorted(pivots.items()):
        if (row & kernel).bit_count() % 2:
            kernel |= 1 << bit
    need(all(((al ^ bl) & kernel).bit_count() % 2 == 0 for al, _, bl, _ in rows),
         'residue-kernel fixture')
    masks = [s for s in range(512) if kernel & (1 << s)]
    y = [(0, 0)] * 512
    for mask in masks:
        term = monomial(mask, mask.bit_count() + 3)
        y = [(a + c, b + d) for (a, b), (c, d) in zip(y, term, strict=True)]
    need(in_newton(y), 'admitted fixture in B9')
    need(first_failure(replay(y, active, recipes)[0]) is None, 'full-prefix admission')
    need(any(not divisible_pi(z, s.bit_count() + 4)
             for s, z in enumerate(coefficients(y))), 'fixture outside four B9')
    return {'pi3_newton_basis_masks': masks, 'source_sha256': digest(y),
            'source_outside_four_B9': True, 'all_checkpoints_exact': True}


def witness(active, recipes):
    w = monomial(2, 4)
    y = wrapper(w, recipes[1092]['right_plan'], inverse=True)
    for event in (1056, 131):
        y = native(y, recipes[event], inverse=True)
    need(in_newton(y), 'witness Newton entrance')
    checks, _ = replay(y, active, recipes)
    old_checks = [row for row in checks if row[0].split(':')[0] in
                  ('1090', '1092', '1129')]
    need(first_failure(old_checks) is None, 'old slice admitted')
    failure = first_failure(checks)
    need(failure == {'checkpoint': '1190:addend:D10', 'address': 0,
                     'scaled_value': [-2, 2]}, 'additional-read witness')
    need(first_failure(replay([(4 * a, 4 * b) for a, b in y], active, recipes)[0])
         is None, 'four-times source positive control')
    return {'source_sha256': digest(y), 'newton_coefficients':
            [[s, list(z)] for s, z in enumerate(coefficients(y)) if z != (0, 0)],
            'first_failure': failure, 'slice_admitted': True}


def calculate():
    proofs = authenticate()
    word, raw = load()
    active, reads = schedule(word)
    recipes = prepared(raw, active)
    keys, rows, endpoint_digest, zero = matrix(active, recipes)
    full = invariants(rows)
    old = []
    for cut, key in enumerate(keys):
        if key.split(':')[0] in ('1090', '1092', '1129'):
            old.extend(rows[512 * cut:512 * (cut + 1)])
    calibration = invariants(old)
    need(calibration['index_B9_log2'] == 280 and
         calibration['pi_exponent_multiplicities'] == [326, 112, 56, 16, 2],
         'PR3449 sharp-module calibration')
    need(280 < full['index_B9_log2'] < 2048, 'strict intermediate full module')
    return {'schema_version': 1, 'source_hashes': INPUTS,
            'retained_proof_hashes': proofs,
            'independent_product_baseline': baseline(word),
            'prefix_events': 2025, 'active_events': [i for i, _, _ in active],
            'quarter_reads': reads, 'checkpoints': keys,
            'identically_zero_congruence_checkpoints': zero,
            'gaussian_constraint_rows': len(rows), 'matrix_sha256': digest(rows),
            'all_512_collector_endpoint_digest': endpoint_digest,
            'maximal_full_prefix_module': full, 'slice_calibration': calibration,
            'separating_witness': witness(active, recipes),
            'admitted_correlated_fixture': admitted_fixture(rows, active, recipes)}


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'usage: verify.py [--emit]')
    result = calculate()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    with (HERE / 'RESULT.json').open('rb') as handle:
        raw = handle.read(1024 * 1024 + 1)
    need(len(raw) <= 1024 * 1024, 'receipt capacity')
    need(digest(json.loads(raw)) == digest(result), 'complete receipt mismatch')
    print('PASS_P104_CORRELATED_FULL_PREFIX index_log2=' +
          str(result['maximal_full_prefix_module']['index_B9_log2']))


if __name__ == '__main__':
    main()
