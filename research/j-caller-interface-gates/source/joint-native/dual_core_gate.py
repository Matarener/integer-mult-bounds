#!/usr/bin/env python3
"""Exact changed dual-retraction core and its charged support tariff.

This changes the old base core. It is not an application of the old
fixed-core lower bound. Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
from joint_coefficient_gate import f, PIN, Model, kernels, mul, phase, b, need, left_gamma
from literal_inverse_binding import from_circuit, product as family_product

HERE = Path(__file__).resolve().parent


# Polynomials in two central variables lambda,mu with free-operator
# coefficients. No sampled scalar identity is used for the core proof.
def pol(a, degree=(0, 0)):
    return {degree: a} if a else {}


def pa(a, c):
    out = dict(a)
    for d, v in c.items():
        value = f.add(out.get(d, f.Z), v)
        if value:
            out[d] = value
        else:
            out.pop(d, None)
    return out


def pn(a):
    return {d: f.neg(v) for d, v in a.items()}


def pp(a, c):
    out = {}
    for d, x in a.items():
        for e, y in c.items():
            out = pa(out, pol(f.mul(x, y), (d[0] + e[0], d[1] + e[1])))
    return out


def pm(a, c):
    return [[sum_pol(pp(x, y) for x, y in zip(row, col)) for col in zip(*c)] for row in a]


def sum_pol(items):
    out = {}
    for x in items:
        out = pa(out, x)
    return out


def formal_core():
    I, Z = pol(f.I), {}
    lam, mu = pol(f.I, (1, 0)), pol(f.I, (0, 1))
    Q, B = pol(f.mono((1,))), pol(f.mono((2,)))
    Qi, Bi = pol(f.mono((-1,))), pol(f.mono((-2,)))
    T1 = [[Q, Z], [pn(pp(lam, pa(Q, pn(I)))), I]]
    T1i = [[Qi, Z], [pp(lam, pa(I, pn(Qi))), I]]
    T2 = [[pa(I, pn(pp(mu, pa(B, pn(I))))), pp(mu, pa(B, pn(I)))],
          [pp(pa(I, mu), pa(I, pn(B))), pa(I, pp(pa(I, mu), pa(B, pn(I))))]]
    T2i = [[pa(I, pn(pp(mu, pa(Bi, pn(I))))), pp(mu, pa(Bi, pn(I)))],
           [pp(pa(I, mu), pa(I, pn(Bi))), pa(I, pp(pa(I, mu), pa(Bi, pn(I))))]]
    E = [[I, Z], [Z, I]]
    need(pm(T1, T1i) == pm(T1i, T1) == E, 'symbolic lambda core inverse')
    need(pm(T2, T2i) == pm(T2i, T2) == E, 'symbolic mu core inverse')
    K, Ki = pm(T2, T1), pm(T1i, T2i)
    need(pm(K, Ki) == pm(Ki, K) == E, 'full symbolic lambda/mu core inverse')
    expected = [pp(Qi, pa(pa(I, mu), pn(pp(mu, Bi)))),
                pp(mu, pp(Qi, pa(Bi, pn(I))))]
    need(Ki[0] == expected, 'first inverse row independent of lambda')

    Q0, B0 = f.mono((1,)), f.mono((2,))
    dual = [[Q0, f.Z], [f.add(Q0, f.neg(B0)), B0]]
    dual_i = [[f.inv(Q0), f.Z], [f.add(f.inv(Q0), f.neg(f.inv(B0))), f.inv(B0)]]
    need(f.mm(dual, dual_i) == f.mm(dual_i, dual) == f.eye(2), 'exact dual core')
    wrong = [row[:] for row in dual_i]
    wrong[1][0] = f.neg(wrong[1][0])
    need(f.mm(dual, wrong) != f.eye(2), 'wrong lower-left inverse sign rejected')
    L, Li = [[f.I, f.Z], [f.I, f.I]], [[f.I, f.Z], [f.neg(f.I), f.I]]
    need(dual == f.mm(f.mm(L, [[Q0, f.Z], [f.Z, B0]]), Li), 'dual directions diagonalize core')
    return {
        'symbolic_central_parameters': ['lambda', 'mu'],
        'identity_checked_without_parameter_sampling': True,
        'T1': '[[Q1,0],[-lambda*(Q1-I),I]]',
        'T2': 'I + (mu,1+mu)^T*(P2tilde-I)*(-1,1)',
        'K_inverse_first_row': ['Q1^-1*((1+mu)*I-mu*P2tilde^-1)',
                                'mu*Q1^-1*(P2tilde^-1-I)'],
        'dual_parameters': {'lambda': -1, 'mu': 0},
        'dual_K': f.sm(dual), 'dual_K_inverse': f.sm(dual_i),
        'negative_control': 'Negate Q1^-1-P2tilde^-1 in the lower-left inverse; full original-column multiplication rejects it.',
        'orthogonality': 'r1*w2=0 and r2*w1=0; r_i*w_i=I at lambda=-1,mu=0',
    }


def general_source_dual(q):
    k = 2 * q + 1
    J, Ji = f.N, f.inv(f.N)
    S = {s: f.mono((s,)) for s in range(1, k + 1)}
    shift = 10 * k
    N = {s: f.mono((shift + s,)) for s in range(1, k + 1)}
    F = {0: f.I}
    for s in range(1, k + 1):
        F[s] = f.prod(N[s], F[s - 1])
    B1 = f.prod(f.inv(F[1]), S[1], J)
    Q1 = f.prod(Ji, B1, J)
    D = {s: f.neg(f.prod(f.inv(F[s]), S[s], F[s - 1])) for s in range(1, k + 1)}
    Dv = f.I
    for r in range(2, q):
        Dv = f.prod(f.neg(D[2 * r + 1]), Dv)
    Dv = f.prod(D[k], Dv)
    C = f.prod(F[k], J, f.inv(Q1), f.inv(Dv), f.inv(F[k]))
    R = f.neg(f.prod(F[k], Dv, Ji, f.inv(F[1]), S[1]))
    need(f.prod(C, R) == f.prod(F[k], J), 'changed dual-core exact complement')
    K2i = f.prod(F[1], Ji, f.inv(F[1]))
    out = f.I
    for s in range(k, 4, -2):
        out = f.prod(out, S[s], N[s - 1])
    out = f.prod(out, N[3], N[2], K2i, S[1])
    need(R == out, 'dual complement telescope without source/frame commutation')
    need(f.prod(C, f.neg(R)) != f.prod(F[k], J), 'wrong dual complement sign rejected')
    return {'q': q, 'native_N_factors_outside_K2_inverse': q + 1,
            'native_K2_inverse_factors': 1, 'complement_native_mass_per_f': 2 * q + 4,
            'cleanup_support_exponent_per_f': 2 * q,
            'R': f.serial(R)}


def rays(q, fs, c1, c2):
    z = Model(fs, 2 * q + 1)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B1, B2 = mul(z.P[0], A), mul(z.P[1], A)
    T1 = mul(J, B1) if c1 else B1
    T2 = mul(J, B2) if c2 else B2
    Q = mul(J.adjoint(), T1, J)
    Dv = z.I
    for r in range(2, q + 1):
        Dv = mul(z.P[2 * r], z.N, Dv)
    Dv = mul(phase(z.n, 2 * (q - 2)), Dv)
    F = z.prefix(2 * q + 1)
    U = mul(F, J, Q.adjoint(), Dv.adjoint(), F.adjoint())
    V = mul(F, J, Q.adjoint(), T2.adjoint(), Dv.adjoint(), F.adjoint())
    return z, U, V


BLOCKS = {
    (0, 0): ((1, 1, 0), (1, 0, 0), (0, 0, 1)),
    (0, 1): ((0, 1, 1), (1, 0, 0), (1, 0, 0)),
    (1, 0): ((0, 0, 0), (0, 1, 0), (0, 0, 1)),
    (1, 1): ((1, 0, 1), (0, 1, 0), (1, 0, 0)),
}


def gamma(q, fs, c1, c2, which):
    n = (4 * q + 4) * fs
    out = [0] * n
    block = BLOCKS[c1, c2] if which == 'B' else (
        ((1, 1, 0), (1, 0, 0), (0, 0, 0)) if c1 else
        ((0, 0, 0), (0, 1, 0), (0, 0, 0)))
    for half in (0, 1):
        for bit in range(fs):
            ix = lambda plane: (2 * plane + half) * fs + bit
            for i, row in enumerate(block):
                out[ix(i)] = sum(x << ix(j) for j, x in enumerate(row))
            for plane in range(5, 2 * q + 2, 2):
                out[ix(plane)] = 1 << ix(plane)
    return tuple(out)


def phase_check(q, c1, c2, U1, V1):
    z = Model(1, 2 * q + 1)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B1, B2 = mul(z.P[0], A), mul(z.P[1], A)
    T1 = mul(J, B1) if c1 else B1
    T2 = mul(J, B2) if c2 else B2
    Q = mul(J.adjoint(), T1, J)
    Dv = z.I
    for r in range(2, q + 1):
        Dv = mul(z.P[2 * r], z.N, Dv)
    Dv = mul(phase(z.n, 2 * (q - 2)), Dv)
    F = z.prefix(2 * q + 1)
    common = from_circuit(mul(F, J, Q.adjoint()), 2 * q + 2 - c1)
    U = family_product(family_product(common, from_circuit(Dv.adjoint(), 5 - 3 * q)),
                       from_circuit(F.adjoint(), -2 * q - 1))
    V = family_product(family_product(family_product(common, from_circuit(T2.adjoint(), -c2)),
                                      from_circuit(Dv.adjoint(), 5 - 3 * q)),
                       from_circuit(F.adjoint(), -2 * q - 1))
    e = 6 - 3 * q - c1
    need(U == from_circuit(U1, e), 'A ray all-f Gaussian unit')
    need(V == from_circuit(V1, e - c2), 'B ray all-f Gaussian unit')
    return {'q': q, 'extra_source_continuations': [c1, c2],
            'A_tensor_phase_exponent': e, 'B_tensor_phase_exponent': e - c2,
            'all_four_f_mod4_residues': 'PASS'}


def run():
    checks, phases = [], []
    for q in range(2, 13):
        for fs in (1, 2):
            for c1 in (0, 1):
                for c2 in (0, 1):
                    z, U, V = rays(q, fs, c1, c2)
                    ra, rb = 2 * q + 2 * c1, 2 * q + (4 if c1 == c2 else 2)
                    need(left_gamma(U) == gamma(q, fs, c1, c2, 'A'), 'all-q A Gamma formula')
                    need(left_gamma(V) == gamma(q, fs, c1, c2, 'B'), 'all-q B Gamma formula')
                    need(b.native_rank(U) == ra * fs and b.native_rank(V) == rb * fs, 'changed core ray native arities')
                    checks.append({'q': q, 'f': fs, 'source_continuations': [c1, c2],
                                   'A_arity': ra * fs, 'B_arity': rb * fs})
                    if fs == 1 and q in (2, 3, 4):
                        phases.append(phase_check(q, c1, c2, U, V))
    return {
        'status': 'PASS_DUAL_CORE_AND_PARAMETER_STRATA_SUPPORT_GATE',
        'scientific_pin': PIN,
        'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_pins': [{'path': str(HERE / name), 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest()}
                        for name in ('joint_coefficient_gate.py', 'LITERAL-INVERSE-BINDING.json', 'COST-SCOPE.md')],
        'generic_rank_one_core': formal_core(),
        'dual_general_source_free_word_checks': [general_source_dual(q) for q in range(2, 26)],
        'actual_ray_rank_checks': checks, 'actual_ray_all_f_phase_checks': phases,
        'continuation_flags': 'c1=1[lambda!=-1],c2=1[mu!=-1] in the stated literal compiler; each flagged source gets one separately charged J continuation.',
        'physical_V_inverse_coefficient': '(1+mu)*A-mu*B; A=F J Q1^-1 Dv^-1 F^-1; B=F J Q1^-1 P2tilde^-1 Dv^-1 F^-1.',
        'ray_ranks_per_f': {'A': '2q+2*c1', 'B': '2q+4 if c1=c2, otherwise2q+2'},
        'strata': [
            {'lambda': '-1', 'mu': '-1', 'extra_J_queries': 0, 'cleanup_rank_lower': '2q+4', 'mass_over_stock_lower': 4},
            {'lambda': 'other', 'mu': '-1', 'extra_J_queries': 1, 'cleanup_rank_lower': '2q+2', 'mass_over_stock_lower': 4},
            {'lambda': '-1', 'mu': '0', 'extra_J_queries': 1, 'cleanup_rank_lower': '2q', 'mass_over_stock_lower': 2},
            {'lambda': 'other', 'mu': '0', 'extra_J_queries': 2, 'cleanup_rank_lower': '2q+2', 'mass_over_stock_lower': 6},
            {'lambda': '-1', 'mu': 'other than-1,0', 'extra_J_queries': 1, 'cleanup_rank_lower': '2q+2', 'mass_over_stock_lower': 4},
            {'lambda': 'other', 'mu': 'other than-1,0', 'extra_J_queries': 2, 'cleanup_rank_lower': '2q+4', 'mass_over_stock_lower': 8},
        ],
        'two_ray_cancellation_argument': 'In each mixed stratum the nonzero B coefficient has greater native arity than A. Every row has at least2^(rankB*f)-2^(rankA*f) surviving entries, even when nonzero scalar coefficients depend on f. The two rays are never combined into a tensor power of their sum.',
        'support_tariff': 'Complete joint tail native arity plus literal binary ADD count is at least the listed exponent timesf minusO(1). The single-ray strata have noO(1) loss.',
        'cost_scope': 'Unweighted support is unconditional within the native/monomial/binary-ADD circuit model. The mass-over-stock column additionally assumes equal-volume full-bank native child normalization, separately charged early continuation/query sites, and the parent full-scan transfer hypotheses. It is not a weighted-volume moment result.',
        'binding_scope': 'The all-q core/H interface is a stated premise; this producer does not claim a full literal changed prefix. A separate caller source-bound receipt and independent derivative binding must establish the physical retraction flags and the original-column H/L for each admitted prefix.',
        'escape': 'A changed compiler that shares or fuses the extra source continuation with an already charged query, a new retained continuation or owner/target contract, or a different source-retraction direction family is outside the tariff.',
        'no_new_kappa': True,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'DUAL-CORE-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved dual core support gate differs')
    print(out['status'])
