#!/usr/bin/env python3
"""Exact full-insertion obstruction for the canonical common-cut relay.

Apache-2.0. Written with substantial OpenAI Codex assistance.
Frozen predecessor code/data are read only. No randomized search is used.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = Path('/Users/ross/git/math/.research-automation/runs/kappa-major-20261018T1330Z/shared-helper-algebra')
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PINS = {
    'SOURCE-COMMON-FRAME-INVERSE-SEARCH.json': 'bc45cf6f3ab114c565fd330d01174092bf4a32d94d3e3e2c49f80ccaa602bb99',
    'SOURCE-D4-BUS-INPUT.json': '93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd',
    'canonical_endpoints.py': '0bbd62dd84f7f7172a57b04abcccd62831042cc417c491970ede42d257cb41a6',
    'noncommon_b1.py': '4badaf9158a945da34dd4497508d36483da52a87968b24d0553ef18d858e8c49',
    'NONCOMMON-B1.json': '7e59465f98810f3daa73a14a15d434ddced3a09ce3fb931eeb81f34721e25cff',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


# Independent binary implementation. Matrices are columns packed as integers.
def binary_image(columns, vector):
    value = 0
    while vector:
        bit = vector & -vector
        value ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return value


def binary_product(left, right):
    return tuple(binary_image(left, column) for column in right)


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            pivot = vector.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = vector
                break
            vector ^= pivots[pivot]
    return len(pivots)


def binary_tableau(operator):
    return tuple(x | (z << operator.n) for x, z, _ in operator.tab)


def native_rank(operator):
    n = operator.n
    return binary_rank(v & ((1 << n) - 1) for v in binary_tableau(operator)[n:])


def address(rows, value):
    return sum(((row & value).bit_count() % 2) << index for index, row in enumerate(rows))


# Independent Gaussian-dyadic sparse state evaluator, retaining global phase.
def gaussian_unit(value, phase):
    real, imag = value
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[phase % 4]


def sparse_column(operator, basis=0):
    state, denominator = {basis: (1, 0)}, 0
    for event in operator.circuit:
        kind = event[0]
        if kind == 'P':
            state = {address(event[1], x): value for x, value in state.items()}
        elif kind == 'X':
            state = {x ^ event[1]: value for x, value in state.items()}
        elif kind == 'phase':
            state = {x: gaussian_unit(value, event[1]) for x, value in state.items()}
        elif kind == 'D':
            rows, alpha = event[1:]
            result = {}
            for x, value in state.items():
                phase = sum(alpha[i] for i in range(operator.n) if x >> i & 1)
                for i in range(operator.n):
                    if x >> i & 1:
                        phase += 2 * ((rows[i] >> (i + 1)) & (x >> (i + 1))).bit_count()
                result[x] = gaussian_unit(value, phase)
            state = result
        elif kind == 'C':
            direction, sign = event[1:]
            result = {}
            for x, (a, b) in state.items():
                for y, value in ((x, (a-sign*b, b+sign*a)),
                                 (x ^ direction, (a+sign*b, b-sign*a))):
                    u, v = result.get(y, (0, 0))
                    result[y] = u + value[0], v + value[1]
            state = {x: value for x, value in result.items() if value != (0, 0)}
            denominator += 1
        else:
            raise ValueError(event)
        while denominator and all(not ((a | b) & 1) for a, b in state.values()):
            state = {x: (a // 2, b // 2) for x, (a, b) in state.items()}
            denominator -= 1
    return state, denominator


def standard_product(ce, *operators):
    """Return operators[0] ... operators[-1] in conventional product order."""
    result = ce.ident(operators[0].n)
    for operator in reversed(operators):
        result = result.then(operator)
    return result


def canonical_predecessor():
    for name, expected in PINS.items():
        need(hashlib.sha256((OLD / name).read_bytes()).hexdigest() == expected, 'frozen source pin: ' + name)
    spec = importlib.util.spec_from_file_location('stabilizer_frozen_endpoint', OLD / 'canonical_endpoints.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(hashlib.sha256(module.CP.read_bytes()).hexdigest() == '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962', 'native compiler pin')
    return module


def deliberate_monomial(ce, n, cut, variant):
    """Dense pair stabilizer: nonorthogonal GL2, fresh GL, and cross chirps.

    This is one prescribed construction, not a seed or search. The common
    address matrix is A=[[0,1],[1,1]], and Q_CC=I+A^-T A^-1=[[1,1],[1,0]].
    """
    rows = [1 << i for i in range(n)]
    rows[:2] = [2, 3]
    fresh = list(range(2, n))
    # Swap completed and future directions, then mix every fresh direction.
    past = 2 + 5 * (cut + 1) - 1
    future = 2 + 5 * (cut + 1)
    if future < n:
        rows[past], rows[future] = rows[future], rows[past]
    for index in range(len(fresh) - 1):
        a, b = fresh[index], fresh[index + 1]
        rows[a] ^= rows[b]
    rows[0] ^= sum(1 << i for i in fresh if (i + variant) % 2 == 0)
    rows[1] ^= sum(1 << i for i in fresh if (i + variant) % 3 == 0)
    quadratic = [3, 1] + [0] * (n - 2)
    for i in fresh:
        j = (i + variant) % 2
        quadratic[i] ^= 1 << j
        quadratic[j] ^= 1 << i
        if (i + variant) % 3 == 1:
            quadratic[i] ^= 1 << i
    for a, b in zip(fresh[::2], fresh[1::2]):
        quadratic[a] ^= 1 << b
        quadratic[b] ^= 1 << a
    operator = ce.perm(n, rows).then(ce.diag(n, quadratic)).then(ce.xgate(n, (1 << (2 + variant % (n - 2))) | 1))
    common = ce.cgate(n, 1).adjoint().then(ce.cgate(n, 2))
    other = standard_product(ce, common, operator, common.adjoint())
    need(native_rank(operator) == native_rank(other) == 0, 'prescribed full pair stabilizer admission')
    # Sparse complete-column phase witness for the actual rank-zero conjugate.
    state, den = sparse_column(other)
    need(den == 0 and len(state) == 1 and next(iter(state.values())) in ((1, 0), (0, 1), (-1, 0), (0, -1)), 'actual second-cut monomial phase')
    return operator, {'address_rows': rows, 'quadratic_rows': quadratic, 'second_front_zero_column': [list(state.items()), den]}


def verify_free_word():
    """Independent group-ring replay of the frozen arbitrary-input B1 word."""
    data = json.loads((OLD / 'NONCOMMON-B1.json').read_text())

    def reduce(word):
        result = []
        for symbol in word:
            if result and result[-1] == -symbol:
                result.pop()
            else:
                result.append(symbol)
        return tuple(result)

    rows = [{((), 0): 1}, {((), 1): 1}]
    for gate in data['word']:
        if gate['op'] == 'LEFT':
            rows[gate['dst']] = {(reduce(tuple(gate['word']) + word), column): coefficient for (word, column), coefficient in rows[gate['dst']].items()}
        elif gate['op'] == 'ADD':
            destination = dict(rows[gate['dst']])
            for key, coefficient in rows[gate['src']].items():
                destination[key] = destination.get(key, 0) + gate['q'] * coefficient
                if destination[key] == 0:
                    del destination[key]
            rows[gate['dst']] = destination
        elif gate['op'] == 'EXCHANGE':
            rows = [rows[1], {key: -coefficient for key, coefficient in rows[0].items()}]
        else:
            raise ValueError(gate)
    endpoint = (-3, 5, -2, 4, -1)
    need(rows == [{(endpoint, 0): 1}, {(endpoint, 1): 1}], 'independent arbitrary-column group-ring identity')
    return {'input_columns': 2, 'free_invertible_operators': 5, 'endpoint': list(endpoint)}


def run():
    old = canonical_predecessor()
    ce = old.ce
    records, phase_cases, controls = [], [], []
    for group in range(3):
        for coordinate, p in enumerate(old.bus['groups7'][group]):
            q = old.bus['groups7'][(group + 1) % 3][coordinate]
            r = old.bus['groups7'][(group + 2) % 3][coordinate]
            chart = ce.perm(7, ce.transpose(old.completion(p, q), 7))
            if group == 2:
                pre = old.build(7, old.winner[p]['pre_events'])
            else:
                direction = q ^ r
                pre = ce.perm(7, [(1 << i) ^ (direction if direction >> i & 1 else 0) for i in range(7)])
            canonical_pre, _ = ce.monomial(chart.then(pre).then(chart.adjoint()))
            local_p = canonical_pre.adjoint()
            local_fresh = ce.fourier(7, range(2, 7))
            local_common = ce.cgate(7, 1).then(ce.cgate(7, 2).adjoint())
            first = standard_product(ce, local_fresh, local_p, local_common)
            rank_first = native_rank(first)
            need(rank_first == (3 if group == 2 else 5), 'actual fixed first-factor native rank')
            # Complete phase check against the pinned compiler's literal lowering.
            recipe, lowered = ce.lower_child(first)
            need(recipe['rank'] == rank_first and first.tab == lowered.tab, 'native lowering signed tableau')
            need(sparse_column(first) == sparse_column(lowered), 'independent local global phase')
            cases = []
            for length in (1, 3, 5, 9):
                n = 2 + 5 * length
                cp, cq = ce.cgate(n, 1), ce.cgate(n, 2)
                common = cp.then(cq.adjoint())
                fresh = [ce.fourier(n, range(2 + 5 * stage, 7 + 5 * stage)) for stage in range(length)]
                ps = [old.embed(n, canonical_pre.circuit, [0, 1] + list(range(2 + 5 * stage, 7 + 5 * stage))).adjoint() for stage in range(length)]
                qtotal, baseline, fpast, factored = ps[0], ps[0], fresh[0], standard_product(ce, fresh[0], ps[0], common)
                monomials = []
                for stage in range(1, length):
                    monomial, _ = deliberate_monomial(ce, n, stage - 1, stage)
                    monomials.append(monomial)
                    insertion = standard_product(ce, fpast.adjoint(), monomial, fpast)
                    qtotal = standard_product(ce, ps[stage], insertion, qtotal)
                    baseline = standard_product(ce, ps[stage], baseline)
                    fpast = standard_product(ce, fresh[stage], fpast)
                    factor = standard_product(ce, fresh[stage], ps[stage])
                    need(native_rank(factor) == 5, 'later factor native rank')
                    factored = standard_product(ce, factor, monomial, factored)
                original = standard_product(ce, fpast, qtotal, common)
                need(original.tab == factored.tab, 'exact signed tableau of telescoping factorization')
                # Independent columns/multiplication agree with exact compiler.
                independent = binary_product(binary_tableau(fpast), binary_product(binary_tableau(qtotal), binary_tableau(common)))
                need(independent == binary_tableau(original), 'independent symplectic endpoint multiplication')
                rank_y = native_rank(original)
                bound = 5 * (length - 1) + rank_first
                need(rank_y <= bound < n, 'universal theorem bound on deliberate insertion')
                baseline_y = standard_product(ce, fpast, baseline, common)
                need(native_rank(baseline_y) == bound, 'identity insertion attains universal Y bound')
                fx = standard_product(ce, ce.fourier(n), ce.xgate(n, 1), qtotal)
                rank_x = native_rank(fx)
                # At genuine B1 size17, independently compare full columns for
                # a representative A port and C port; this fixes global phase.
                if length == 3 and coordinate == 0 and group in (0, 2):
                    original_state = sparse_column(original)
                    need(original_state == sparse_column(factored), 'global B1 exact Gaussian column')
                    phase_wrong = factored.then(ce.Op(n, ce.identity(n), [('phase', 1)]))
                    need(phase_wrong.tab == original.tab and sparse_column(phase_wrong) != original_state, 'global-phase omission control')
                    phase_cases.append({'group': group, 'p': p, 'n': n, 'output_support': len(original_state[0]), 'denominator_depth': original_state[1]})
                cases.append({'L': length, 'm': n, 'X_native_rank': rank_x, 'Y_native_rank': rank_y, 'Y_rank_upper_bound': bound, 'identity_insertion_Y_native_rank': native_rank(baseline_y), 'Y_deficit_lower_bound': n - bound})
            records.append({'group': group, 'coordinate': coordinate, 'p': p, 'q': q, 'first_factor_rank': rank_first, 'cases': cases})
    # An undressed logical ADDRESS swap has a real hidden native query.
    n = 4
    cp, cq, past = ce.cgate(n, 1), ce.cgate(n, 2), ce.cgate(n, 4)
    dx = standard_product(ce, cp, past)
    swap = ce.perm(n, [1, 2, 8, 4])
    dressed = standard_product(ce, dx.adjoint(), swap, dx)
    need(native_rank(standard_product(ce, dx, dressed, dx.adjoint())) == 0, 'dressed swap admitted')
    hidden = native_rank(standard_product(ce, dx, swap, dx.adjoint()))
    need(hidden == 2, 'undressed swap admission control')
    common = standard_product(ce, cq, cp.adjoint())
    no_chirp = ce.perm(n, [2, 3, 4, 8])
    need(native_rank(standard_product(ce, common, no_chirp, common.adjoint())) > 0, 'common chirp omission control')
    wrong_inverse = standard_product(ce, past, swap, past)
    right_inverse = standard_product(ce, past.adjoint(), swap, past)
    need(wrong_inverse.tab != right_inverse.tab, 'positive/adjoint past-frame control')
    controls.extend(['undressed_swap_costs_rank2', 'common_chirp_omission_breaks_second_front', 'past_frame_inverse_sign_is_essential', 'global_phase_i_rejected_on_two_B1_ports'])
    return {
        'status': 'PASS_FULL_MONOMIAL_INSERTION_Y_RANK_OBSTRUCTION_NO_NEW_KAPPA',
        'scientific_pin': PIN,
        'sources_sha256': PINS,
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'free_word': verify_free_word(),
        'theorem': {'C_Y_rank_upper': '5L-2 = m-4', 'AB_Y_rank_upper': '5L = m-2', 'm': '2+5L', 'quantifiers': 'Every L>=1; every locally admitted monomial pre_s on common2 plus own fresh5 with fixed first-factor ranks3/5; every insertion whose physical X-cut pullback is any invertible monomial. Second-front admission is unnecessary for the upper bound. Arbitrary permutations and diagonal nonzero phases, including non-Clifford monomials, are covered by the row-support proof.'},
        'factorization': 'F_all P_last (F_past^-1 M_last-1 F_past) ... P_1 (F_0^-1 M_0 F_0) P_0 R = (F_last P_last) M_last-1 ... (F_1 P_1) M_0 (F_0 P_0 R)',
        'records': records,
        'independent_global_phase_cases': phase_cases,
        'defect_controls': controls,
        'all_size': 'Tensor columnwise over f>=1: each later factor has row support2^(5f), first factor2^(3f) C or2^(5f) A/B; monomials preserve support. Thus terminal Y has row support <=2^((m-4)f) C or2^((m-2)f) A/B and cannot be a rank-mf native child, even with arbitrary input values.',
        'cost_boundary': {'OPEN_local_histogram': {'1': 8, '2': 40, '3': 16}, 'OPEN_local_rank_mass': 136, 'ordinary_helpers': 0, 'private_fields': 0, 'isolated_unary_completion_rank_lower_bound_per_twelve_port_Y_bank': 32, 'insertion_scans': 'All actual monomial address/phase scans remain paid; zero native rank does not mean zero work.'},
        'limits': ['No arbitrary multibank insertion, changed scalar word, changed entrance code, overlapping local fresh supports, or different raw local boundary is excluded.', 'The proof does not calculate an optimal paid completion word, owner allocation, all-size rounded precision, physical tape controller, or positive conditional kappa.', 'This is a written all-parameter proof with finite exact operator checks, not formal-kernel verification.'],
        'attribution': 'Uses frozen source-carrier/common-F normalizers and canonical endpoint charts from the2026-10-18 run; predecessor complex and algebra lanes plus root own those constructions. This lane supplies the exact telescoping argument, full arbitrary-monomial support bound, independent symplectic arithmetic and Gaussian phase evaluator.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    output = json.loads(json.dumps(run()))
    target = HERE / 'FULL-STABILIZER-BOUND.json'
    if args.write:
        target.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(target.read_bytes()) == output, 'stored exact receipt mismatch')
    print(output['status'])
    print('12 ports x L1/3/5/9; arbitrary-monomial proof;2 exact n17 phase checks;4 defect controls')


if __name__ == '__main__':
    main()
