#!/usr/bin/env python3
"""Exact permutation-only continuation inventory and all-q branch invariant.
Apache-2.0; substantial OpenAI Codex assistance. Homogeneous interfaces
are preserved; this is not a complete wider physical caller or tail.
"""
from pathlib import Path
from itertools import product as cartesian
import argparse
import hashlib
import json
from joint_coefficient_gate import operators, left_gamma
from native_model import Model, PIN, b, ce, mul, need, phase
from even_parity_source import kernels
from literal_inverse_binding import from_circuit
from gl2_continuation_gate import trace_pair
from fractions import Fraction

HERE = Path(__file__).resolve().parent


def basis(vectors):
    pivots = {}
    out = []
    for original in vectors:
        x = original
        while x:
            bit = x.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = x
                out.append(original)
                break
            x ^= pivots[bit]
    return out


def build(q, schedule):
    need(len(schedule) == q - 2 and all(s in (0, 1) for s in schedule), 'complete routing schedule')
    z = Model(1, 2 * q + 1)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B = [mul(P, A) for P in z.P]
    Q1, F = mul(J.adjoint(), B[0], J), z.prefix(2 * q + 1)
    # Labels0/1 are K row1 / K row2, not physical bank numbers.
    u, v = mul(B[2], J), z.I
    lu, lv = 1, 0
    eu, ev = 1, 0
    counts = [0, 0]
    chosen = [[], []]
    for r in range(2, q + 1):
        chosen[lu].append(('B_even', 2 * r))
        chosen[lv].append(('D_odd', 2 * r + 1))
        counts[lv] += 1
        uu, vv = mul(B[2 * r - 1], u), mul(B[2 * r], J, v)
        eau, eav = eu, ev + 1
        if r == q:
            u, v, eu, ev = uu, vv, eau, eav
        elif schedule[r - 2]:
            u, v = vv, mul(phase(z.n, 2), uu)
            lu, lv = lv, lu
            eu, ev = eav, eau + 2
        else:
            u, v = uu, mul(phase(z.n, 2), vv)
            eu, ev = eau, eav + 2
    words, exponents, current = [None, None], [None, None], [None, None]
    words[lu], words[lv] = u, v
    exponents[lu], exponents[lv] = eu, ev
    current[lu], current[lv] = 1, 3
    base = [mul(J, Q1.adjoint(), B[1].adjoint()),
            mul(J, Q1.adjoint()), mul(J, Q1.adjoint(), B[1].adjoint())]
    coeff = [mul(F, op, words[0 if j == 0 else 1].adjoint(), F.adjoint())
             for j, op in enumerate(base)]
    ranks = [b.native_rank(op) for op in coeff]
    want = [2 * counts[0] + 6, 2 * counts[1] + 8, 2 * counts[1] + 8]
    need(ranks == want, 'all-q routed inverse native rank formulas')
    need(counts[0] + counts[1] == q - 1 and counts[0] >= 1,
         'first D5 and all q-1 odd debts retained')
    need(len(set(op.tab for op in coeff[1:])) == 2, 'split inverse terms are distinct rays')
    return z, words, exponents, current, chosen, coeff, ranks, counts, F


def detail(q, schedule):
    z, words, exponents, current, chosen, coeff, ranks, counts, F = build(q, schedule)
    images = [basis([x for x, zz, ph in op.tab[z.n:]]) for op in coeff]
    overlap = {f'0_vs_{j}': len(images[0]) + len(images[j]) - ce.rank(images[0] + images[j]) for j in (1, 2)}
    overlap['1_vs_2'] = len(images[1]) + len(images[2]) - ce.rank(images[1] + images[2])
    overlap['three_ray_union'] = ce.rank(images[0] + images[1] + images[2])
    records = []
    for j, op in enumerate(coeff):
        owner = 0 if j == 0 else 1
        records.append({'kind': 'single' if j == 0 else 'split_positive' if j == 1 else 'split_negative',
                        'current_physical_bank': current[owner], 'native_arity_per_f': ranks[j],
                        'tensor_phase_exponent': 1 - exponents[owner],
                        'family': 'i^(exponent*(1-f)) times this complete one-coordinate operator tensored f times',
                        'one_coordinate_circuit': op.circuit, 'signed_tableau': [list(t) for t in op.tab],
                        'left_Gamma_rows': list(left_gamma(op)), 'native_output_image_basis': images[j]})
    return {'q': q, 'schedule_0_identity_1_swap': ''.join(map(str, schedule)),
            'odd_D_counts_by_core_row': counts, 'chosen_factors_by_core_row': chosen,
            'homogeneous_factories_by_core_row': [
                {'core_row': j + 1, 'current_physical_bank': current[j],
                 'one_coordinate_circuit': words[j].circuit, 'signed_tableau': [list(t) for t in words[j].tab],
                 'tensor_phase_exponent': exponents[j],
                 'physical_F_factory_arity_per_f': b.native_rank(mul(F, words[j]))}
                for j in range(2)],
            'original_t_inverse_coefficients': records,
            'descriptive_native_output_subspace_overlaps_per_f': overlap,
            'scope': 'The split coefficient is positive ray minus negative ray. B-image overlap is descriptive and is NOT a shared-query invoice or independent owner stock.'}


def run():
    census = []
    for q in range(2, 11):
        records = []
        for schedule in cartesian((0, 1), repeat=q - 2):
            z, words, exps, current, chosen, coeff, ranks, counts, F = build(q, schedule)
            records.append({'schedule': ''.join(map(str, schedule)), 'odd_counts': counts,
                            'inverse_branch_arities': ranks})
        want = 2 * ((q + 1) // 2) + 6
        need(min(max(r['inverse_branch_arities']) for r in records) == want,
             'exact achievable minimax routing exponent')
        need(all(r['inverse_branch_arities'][0] + r['inverse_branch_arities'][1] == 2 * q + 12 for r in records),
             'sum of coefficient support exponents, not a sum-cost bound')
        census.append({'q': q, 'schedule_count': len(records),
                       'minimax_inverse_support_exponent': want, 'native_prefix_margin': 2 * q,
                       'all_schedules': records})
    witnesses = []
    for q in range(6, 11):
        d0 = (q + 1) // 2
        schedule = [0] * (q - 2)
        schedule[d0 - 1] = 1
        witnesses.append(detail(q, schedule))
    # Omitting the actual base B3J=P3N changes the original-column map.
    z, words, exps, current, chosen, coeff, ranks, counts, F = build(2, ())
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B1 = mul(z.P[0], A)
    Q1 = mul(J.adjoint(), B1, J)
    B4 = mul(z.P[3], A)
    bad = mul(F, J, Q1.adjoint(), B4.adjoint(), F.adjoint())
    need(bad.tab != coeff[1].tab, 'dropping base B3J is a real operator defect')
    zs = Model(1, 2)
    Js = kernels(zs)[1]
    B2s = mul(zs.P[1], zs.N.adjoint(), Js)
    identity_key = next(iter(from_circuit(zs.I, 0)))
    B2_key = next(iter(from_circuit(B2s.adjoint(), 0)))
    overlap = trace_pair(identity_key, B2_key)
    need(Fraction(overlap['normalized_modulus_squared']) == Fraction(1, 256),
         'exact spectator-independent split-ray overlap modulus1/16')
    return {'status': 'PASS_PERMUTATION_CONTINUATION_ALL_Q_INVARIANT_AND_CENSUS',
            'scientific_pin': PIN, 'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(HERE / p), 'sha256': hashlib.sha256((HERE / p).read_bytes()).hexdigest()}
                            for p in ('joint_coefficient_gate.py', 'LITERAL-INVERSE-BINDING.json', 'GL2-CONTINUATION-GATE.json', 'gl2_continuation_gate.py')],
            'all_q_domain': 'q>=2,f>=1; frozen actual J, P_s swaps; only identity versus swap of U/V before each nonfinal retained J continuation, with the literal diagonal v minus sign and initial B3J=P3N.',
            'exact_rank_invariant': 'Let d0 be the number of odd D_s=B_sJ factors received by the Krow1 path; d1=q-1-d0. The original-t inverse coefficient on that current path is one Clifford of arity(2d0+6)f. The other coefficient is a difference of two distinct Cliffords, each arity(2d1+8)f.',
            'split_overlap': 'Normalized Hilbert-Schmidt overlap modulus of the two split rays is16^-f: their quotient is unitarily similar to B2^-1. Thus split coefficient max-row support>=(15/32)2^((2d1+8)f). No every-row or sum-native-cost conclusion is made.',
            'split_overlap_one_coordinate_active_three_plane_check': overlap,
            'all_q_minimax': 'min_schedule max coefficient-support exponent r*=2ceil(q/2)+6. Every d0 in1..q-1 is attained by a single swap after its d0-th odd exposure; choose d0 nearestq/2. Both inverse coefficients cannot have sublinear-q support exponents.',
            'native_and_scan_lower_bound': 'Every cleanup at the same declared cut has total actual native arity+binary_ADD_count >=r*f-O(1), r=max(2d0+6,2d1+8). Equal-volume/full-bank transfer is separate. Sum2q+12 is descriptive and is NOT an additive query-cost lower bound.',
            'finite_census': census, 'best_exact_homogeneous_witnesses': witnesses,
            'negative_control': 'Deleting the base B3J changes the actual inverse operator; it is not a zero-cost relabeling.',
            'limits': ['The all-q rank derivation is written separately; finite exact census q2..10 checks511 schedules.',
                       'The witnesses include full branch operators and output-image overlaps but do not serialize all affine public readers or a complete wider physical prefix/cleanup.',
                       'Source-specific monomial endpoints, precision, contraction, owners and tape remain obligations for any positive candidate.',
                       'The support-only window startingq8 is not an exponent or native-saving claim.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'ROUTING-INVENTORY.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved routing inventory differs')
    print(out['status'])
