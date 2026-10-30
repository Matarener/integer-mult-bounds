#!/usr/bin/env python3
"""Check native equality cuts with exact independent matrix calculations.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from cuts import audit
from exact import (G, adjoint, bank_gate, cross_rank, equality_indices, eye,
                   fourier_rank, gate, literal_cross, mul, need,
                   one_axis_cliffords, power_tensor, rank, tensor)


def authenticated_sources():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for item in manifest.get('retained_files', []):
        payload = (HERE / item['local_path']).read_bytes()
        need(hashlib.sha256(payload).hexdigest() == item['sha256'],
             'retained source hash: ' + item['local_path'])
    return len(manifest.get('retained_files', []))


def native_checks():
    maps = [(u, f, k) for u in one_axis_cliffords()
            for f, k in ((2, 1), (3, 1), (4, 1), (4, 2), (6, 3))]
    rng = random.Random(5582)
    for n, samples in ((2, 32), (3, 16)):
        for sample in range(samples):
            u = eye(1 << n)
            for _ in range(9):
                kind = rng.choice(('Q', 'S', 'X', 'CX', 'CZ'))
                i, j = rng.sample(range(n), 2)
                u = mul(gate(n, kind, i, j), u)
            maps.append((u, 2, 1))
            if n == 2 and sample < 4:
                maps.append((u, 4, 2))
    counts = {}
    partial_isometries = 0
    for u, f, k in maps:
        d, r = len(u), fourier_rank(u)
        b = literal_cross(u, f, k)
        expected = d**(f-k) * (1 - Q(1, 1 << (k*r)))
        need(rank(b) == expected, 'literal native cut tariff')
        counts[str(r)] = counts.get(str(r), 0) + 1
        gram = mul(adjoint(b), b)
        need(mul(gram, gram) == gram, 'unit nonzero cut singular values')
        partial_isometries += 1
    return {'literal_cross_blocks': len(maps), 'fourier_ranks': counts,
            'partial_isometry_checks': partial_isometries,
            'one_axis_projective_classes': 24}


def chronological_checks():
    rng = random.Random(16582)
    registers, v = 3, 4
    inside = [r*v+i for r in range(registers) for i in equality_indices(2, 2, 1)]
    orbit = one_axis_cliffords()
    prefixes = 0
    for _ in range(48):
        word, budget = eye(registers*v), 0
        for step in range(10):
            dst, src = rng.sample(range(registers), 2)
            coefficient = rng.choice((1, -1, G('i'), Q(1, 2)))
            if step in (2, 6):
                u = rng.choice(orbit)
                payload = power_tensor(u, 2)
                kind = rng.choice(('add', 'apply'))
                budget += cross_rank(payload, equality_indices(2, 2, 1))
            else:
                u = gate(1, rng.choice(('S', 'X')))
                payload = power_tensor(u, 2)
                kind = rng.choice(('add', 'apply', 'copy', 'clear'))
                need(cross_rank(payload, equality_indices(2, 2, 1)) == 0,
                     'ordinary map must preserve the cut')
            event = bank_gate(registers, payload, kind, dst, src, coefficient)
            word = mul(event, word)
            need(cross_rank(word, inside) <= budget, 'chronological rank budget')
            prefixes += 1
    return {'words': 48, 'complete_dirty_prefixes': prefixes}


def obstruction_checks():
    native = []
    for r in (1, 2, 3):
        u = eye(8)
        for j in range(r):
            u = mul(gate(3, 'Q', j), u)
        native.append(rank(literal_cross(u, 2, 1)))
    need(native == [4, 6, 7], 'literal rank-one/two/three prices')
    need(native[0]+native[2] < 2*native[1], 'equal-mass fusion fails')

    q = power_tensor(gate(1, 'Q'), 2)
    initial = tuple(eye(4)) + tuple(q) + tuple(q)
    source_inside = equality_indices(2, 2, 1)
    available_inside = [r*4+i for r in range(3) for i in source_inside]
    need(cross_rank(initial, source_inside, available_inside) == 1,
         'duplicate observations have one joint cut rank')

    # One field query cannot move two independent coordinate-three inputs.
    target = [[G(0) for _ in range(6)] for _ in range(6)]
    target[0][2] = G(1)
    target[4][5] = G(1)
    need(cross_rank(target, [2, 5]) == 2, 'input bottleneck has rank two')
    two_calls = eye(12)
    for source, output_coordinate in ((0, 0), (1, 1)):
        two_calls = mul(bank_gate(4, eye(3), 'copy', source+2, source), two_calls)
        paid = [[G(0) for _ in range(3)] for _ in range(3)]
        paid[output_coordinate][2] = G(1)
        two_calls = mul(bank_gate(4, paid, 'apply', source+2), two_calls)
    expected = [list(row) for row in eye(12)[:6]]
    expected += [[G(0) for _ in range(12)] for _ in range(6)]
    expected[6][2] = G(1)
    expected[10][5] = G(1)
    need(two_calls == tuple(map(tuple, expected)), 'complete two-call packing endpoint')

    # A map on only one tensor column is not an ordinary columnwise lift.
    bad_free = tensor(gate(1, 'X'), eye(2))
    need(cross_rank(bad_free, source_inside) == 2, 'noncolumnwise escape control')
    return {'literal_small_native_ranks': native, 'duplicate_cache_joint_rank': 1,
            'single_input_bottleneck': 2, 'noncolumnwise_cut_rank': 2}


def polynomial_checks():
    delayed = []
    profitable = []
    need(130**128 > 2*129**128, 'exact raw-saving comparison at 1/256')
    for k in range(1, 13):
        m = 1 << (k+1)
        data = {'paid': {'1': 3, '3': m}, 'targets': {'2': m+3}}
        result = audit(data)
        need(result['status'] == 'FAIL_NECESSARY_EQUALITY_CUTS' and
             result['witness']['k'] == k, 'first failure at a prescribed cut')
        if k > 1:
            need(audit(dict(data, width=2*k-1))['status'] ==
                 'PASS_NECESSARY_EQUALITY_CUTS', 'width cutoff must apply')
        need(audit(dict(data, width=2*k))['status'] ==
             'FAIL_NECESSARY_EQUALITY_CUTS', 'failure at the first valid width')
        delayed.append(k)
        phantom = {'paid': {'1': 9, '3': 7*m+12},
                   'targets': {'2': 3*m+21, '4': 4*m}}
        result = audit(phantom)
        need(result['status'] == 'FAIL_NECESSARY_EQUALITY_CUTS' and
             result['witness']['k'] == k, 'profitable profile first failing cut')
        need(130*(21*m+45) <= 129*(22*m+42), 'raw moment ratio bound')
        # Check the factored polynomial by a separate exact evaluation.
        for j in range(1, k+2):
            x = Q(1, 1 << j)
            literal = 9*(1-x)+(7*m+12)*(1-x**3)-(3*m+21)*(1-x**2)-4*m*(1-x**4)
            need(literal == x*(m*x-3)*(3-4*x)*(1-x), 'profitable polynomial identity')
        profitable.append(k)
    rng = random.Random(5922)
    cases = [{side: {str(r): rng.randrange(8) for r in range(1, 8)}
              for side in ('paid', 'targets')} for _ in range(192)]
    for delta in product(range(-2, 3), repeat=4):
        cases.append({'paid': {str(r): max(c, 0) for r, c in enumerate(delta, 1)},
                      'targets': {str(r): max(-c, 0) for r, c in enumerate(delta, 1)}})
    for data in cases:
        result = audit(data)
        p = {int(r): c for r, c in data['paid'].items()}
        t = {int(r): c for r, c in data['targets'].items()}
        limit = (result['tail']['certified_from_k'] + 24
                 if type(result['tail']) is dict else 24)
        highest = max(p.keys() | t.keys())
        values = [Q(sum((p[r]-t[r])*((1 << (k*highest)) - (1 << (k*(highest-r))))
                        for r in p), 1 << (k*highest)) for k in range(1, limit+1)]
        failed = result['status'] == 'FAIL_NECESSARY_EQUALITY_CUTS'
        need(failed == any(x < 0 for x in values), 'direct independent tariff evaluation')
        if failed:
            need(result['witness']['k'] == next(k for k, x in enumerate(values, 1) if x < 0),
                 'first failure witness')
    need(audit({'paid': {'0': 17, '1': 2}, 'targets': {'1': 2}})['tail'] ==
         'identically zero', 'rank-zero jobs are ordinary')
    need(audit({'paid': {'1': 1}, 'targets': {'1': 2}, 'width': 1})['status'] ==
         'NO_EQUALITY_CUT_AT_THIS_WIDTH', 'no invented width-one cut')
    invalid = [({'paid': {'01': 1}, 'targets': {}}, 'rank encoding'),
               ({'paid': {'1': True}, 'targets': {}}, 'boolean count'),
               ({'paid': {'1': -1}, 'targets': {}}, 'negative count'),
               ({'paid': {}, 'targets': {}, 'width': 0}, 'zero width')]
    for data, label in invalid:
        try:
            audit(data)
        except ValueError:
            pass
        else:
            raise ValueError('accepted invalid input: '+label)
    return {'delayed_first_failures': delayed, 'random_profile_pairs': 192,
            'exhaustive_rank_four_differences': 625,
            'profitable_first_failures': profitable,
            'profitable_raw_saving': '1/256',
            'invalid_input_controls': len(invalid)}


def source_screens():
    path = HERE / 'evidence' / 'p104-result.json'
    source = json.loads(path.read_text())
    invoice = {side: source['complete_cost'][side] for side in ('paid', 'targets')}
    result = audit(invoice)
    need(result['status'] == 'PASS_NECESSARY_EQUALITY_CUTS', 'P104 source tariff screen')
    need(source['complete_cost']['paid_calls'] == sum(invoice['paid'].values()) == 69930,
         'P104 paid census')
    need(source['complete_cost']['productive_fields'] == sum(invoice['targets'].values()) == 12814,
         'P104 target census')
    return {'status': 'PASS_SOURCE_PROFILE_SCREEN_ONLY',
            'paid_calls': 69930, 'target_jobs': 12814,
            'cut_test': result, 'source_native_word_replayed': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = {'status': 'PASS_NATIVE_EQUALITY_CUT',
              'authenticated_sources': authenticated_sources(),
              'native': native_checks(), 'chronological': chronological_checks(),
              'obstructions': obstruction_checks(), 'polynomials': polynomial_checks(),
              'source_screen': source_screens(), 'no_new_kappa': True}
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE / 'RESULT.json').write_text(text)
    else:
        need(text == (HERE / 'RESULT.json').read_text(), 'retained result comparison')
    print(text)


if __name__ == '__main__':
    main()
