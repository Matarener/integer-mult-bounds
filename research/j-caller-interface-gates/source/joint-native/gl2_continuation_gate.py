#!/usr/bin/env python3
"""All scalar GL2 choices at the q3 continuation retain a ten-f support cost.

Source fixtures are replayed directly from physical circuits by this lane's
independent inverse-row implementation. Apache-2.0; substantial OpenAI
Codex assistance. No supplier or exponent claim.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import argparse
import hashlib
import json
from literal_inverse_binding import *
from joint_coefficient_gate import Model, kernels, mul, b, ce

HERE = Path(__file__).resolve().parent
CALLER = HERE.parent / 'caller-joint'
PINS = {
    'mixed_continuation.py': '5f0c4f4cf69476fc579a934b9ff39b94fd64327e5d452f21e11a81b02ad041f9',
    'MIXED-CONTINUATION-RANK-ONLY.json': '2f8ba67723a8c0ef46d609896224f76b4be23ca08d24aa5a70bcfc8c7504330e',
}


def base_paths():
    z = Model(1, 7)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B = [mul(P, A) for P in z.P]
    Q1, F = mul(J.adjoint(), B[0], J), z.prefix(7)
    aa = [mul(J, Q1.adjoint(), mul(B[2], J).adjoint(), B[3].adjoint()),
          mul(J, Q1.adjoint(), B[1].adjoint(), mul(B[2], J).adjoint(), B[3].adjoint()),
          mul(J, Q1.adjoint(), B[1].adjoint(), mul(B[4], J).adjoint())]
    v = [mul(F, op, mul(B[6], J).adjoint(), F.adjoint()) for op in aa]
    u = [mul(F, op, B[5].adjoint(), F.adjoint()) for op in aa]
    need([b.native_rank(op) for op in u] == [8] * 3, 'all U branch native arities')
    need([b.native_rank(op) for op in v] == [10] * 3, 'all V branch native arities')
    need(len(set(op.tab for op in v)) == 3, 'three V rays distinct up to every scalar phase')
    return z, u, v


def trace_pair(ka, kb):
    # Exact Hilbert-Schmidt trace in the X basis. Unit scalar phases have
    # been normalized into each coefficient vector; this preserves modulus.
    a, c, n = 0, 0, len(ka[0])
    for x in range(1 << n):
        if act(ka, x) == act(kb, x):
            p = (qval(kb, x) - qval(ka, x)) % 4
            if p == 0:
                a += 1
            elif p == 1:
                c += 1
            elif p == 2:
                a -= 1
            else:
                c -= 1
    dim = 1 << n
    return {'trace_integer_Gaussian': [a, c], 'dimension': dim,
            'normalized_modulus_squared': str(Q(a * a + c * c, dim * dim))}


def literal_row(events, n, m):
    row = [{} for _ in range(n)]
    row[1] = from_circuit(ce.ident(m), 0)
    native = 0
    for event in events:
        typ = event['kind']
        if typ == 'ADD':
            row[event['src']] = sumexpr(row[event['src']], scale(row[event['dst']], -Q(event['coefficient'])))
        elif typ == 'SCALE':
            need(Q(event['coefficient']) != 0, 'invertible scalar bridge')
            row[event['bank']] = scale(row[event['bank']], 1 / Q(event['coefficient']))
        elif typ == 'BANK_SWAP':
            i, j = event['banks']
            row[i], row[j] = row[j], row[i]
        else:
            op = circuit_op(event['one_coordinate_literal_circuit'], m)
            need(op.tab == tuple(tuple(t) for t in event['one_coordinate_tableau']),
                 'mixed prefix actual literal signed tableau')
            if typ == 'NATIVE':
                need(b.native_rank(op) == 2, 'actual source/fresh/continuation arity2')
                native += 1
            else:
                need(b.native_rank(op) == 0, 'actual mixed prefix monomial')
            row[event['bank']] = product(row[event['bank']], from_circuit(op.adjoint(), -event['phase_exponent']))
    need(native == 61, 'same exact q3 prefix native profile')
    return row


def beta_delta(M):
    # P=diag(1,-1) M includes the diagonal handoff's v'=-Vbar-JA.
    a, bb = M[0]
    c, d = M[1]
    det = a * d - bb * c
    need(det != 0, 'genuine scalar GL2')
    beta, delta = bb / det, -a / det
    need(beta != 0 or delta != 0, 'invertible P inverse has nonzero second column')
    return beta, delta


def run():
    for name, digest in PINS.items():
        need(hashlib.sha256((CALLER / name).read_bytes()).hexdigest() == digest, 'mixed fixture source pin ' + name)
    z, upaths, vpaths = base_paths()
    vf = [from_circuit(op, -1) for op in vpaths]
    keys = [next(iter(x)) for x in vf]
    gram = []
    for i, j in combinations(range(3), 2):
        pair = trace_pair(keys[i], keys[j])
        need(Q(pair['normalized_modulus_squared']) <= Q(1, 256), 'one-bit normalized overlap at most1/16')
        gram.append(dict(pair, rays=[i, j]))
    source = json.loads((CALLER / 'MIXED-CONTINUATION-RANK-ONLY.json').read_text())
    matrices = {'upper': [[Q(1), Q(1)], [Q(0), Q(1)]],
                'lower': [[Q(1), Q(0)], [Q(1), Q(1)]],
                'balanced': [[Q(1), Q(1)], [Q(1), Q(-1)]]}
    records = []
    for fixture in source['fixtures']:
        M = matrices[fixture['name']]
        beta, delta = beta_delta(M)
        predicted = sumexpr(sumexpr(scale(vf[0], beta), scale(vf[1], -beta)), scale(vf[2], delta))
        row = literal_row(fixture['prefix_events'], 8, 16)
        F, J = z.prefix(7), kernels(z)[1]
        actual = product(from_circuit(mul(F, J), 8), row[3])
        need(actual == predicted and actual, 'mixed continuation inverse coefficient exact all f residues')
        bad = sumexpr(sumexpr(scale(vf[0], beta), scale(vf[1], beta)), scale(vf[2], delta))
        if beta:
            need(bad != actual, 'wrong A second-ray sign rejected by physical original-column inverse')
        records.append({'name': fixture['name'], 'M': [[str(x) for x in r] for r in M],
                        'beta': str(beta), 'delta': str(delta),
                        'inverse_V_ray_count': len(actual), 'coefficient': serial(actual),
                        'all_f_literal_binding': 'PASS'})
    need(sumexpr(vf[0], scale(vf[0], -1)) == {}, 'identical rays cancel before any support count')
    return {'status': 'PASS_ANY_SCALAR_GL2_Q3_CONTINUATION_SUPPORT_GATE', 'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(CALLER / n), 'sha256': h} for n, h in PINS.items()]
                           + [{'path': str(HERE / 'literal_inverse_binding.py'), 'sha256': hashlib.sha256((HERE / 'literal_inverse_binding.py').read_bytes()).hexdigest()}],
            'q': 3, 'ambient_arity': 16, 'prefix_native_H2': 61, 'full_stock': 128,
            'new_cut': 'Before the nonfinal retained J continuation, set(Ubar,Vbar)=M(U,V). The next homogeneous state is P*diag(B4,B5J)*(u1,v1), P=diag(1,-1)M.',
            'exact_inverse_column': 'C_tV=F [beta*A+delta*B] (B7J)^-1 F^-1, where(beta,delta)=column2(P^-1), A=J Q1^-1(I-B2^-1)(B3J)^-1 B4^-1, B=J Q1^-1 B2^-1(B5J)^-1.',
            'all_GL2_survival': 'If M is invertible, (beta,delta) is nonzero. The three distinct V rays have coefficient groups(beta,-beta,delta), hence at least one survives at every f, even when M depends on f.',
            'native_branch_arities_per_f': {'U': [8, 8, 8], 'V': [10, 10, 10]},
            'V_branch_uniform_tensor_phase': 'Each displayed V_j,f=i^(f-1) V_j,1^tensor(f). Its global unit is retained in the exact coefficient vector, not dropped. U branches have exponent0.',
            'V_branch_one_coordinate_definitions': [op.circuit for op in vpaths],
            'normalized_Gram_pairs': gram,
            'uniform_Gram_bound': 'All offdiagonal Gram magnitudes are<=1/16 before tensoring, hence<=16^-f. Gershgorin gives lambda_min>=1-2*16^-f>=7/8 for every f>=1 and every coefficient vector, with no coefficient size restriction.',
            'support_proof': 'For c=(beta,-beta,delta), ||C_tV||_F^2 >= (7/8)*D*||c||_2^2, D=2^(16f). Each entry has squared magnitude <=3*||c||_2^2*2^(-10f). Thus total nonzeros >=(7/24)*D*2^(10f), and maximum-row support >=(7/24)*2^(10f). This is a maximum/global support statement, not an every-row claim.',
            'complete_tail_tariff': 'total_native_arity+binary_ADD_count >=10f+log2(7/24). This remains true for f-dependent arbitrary Gaussian GL2 coefficients. Combined with the parent full-scan premises, cleanup fixed native mass>=10, while the prefix deficit is6.',
            'literal_candidate_bindings': records,
            'scope': 'Every invertible scalar GL2 at this ONE q3 handoff cut, in the fixed physical prefix with the frozen J and swaps, and actual F7J original-input targets. Larger q schedules, different coupled operator-valued bridges, source/delivery/base changes and cross-cut native fusion are not covered.',
            'evidence_domain': 'Written arbitrary-GL2 Gram/support proof, exact rational normalized overlaps, and independent literal original-t inverse replay of all three saved candidates at all four f residues. Distinct one-bit rays are normalized up to scalar before support reasoning.',
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'GL2-CONTINUATION-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved q3 GL2 gate differs')
    print(out['status'])
