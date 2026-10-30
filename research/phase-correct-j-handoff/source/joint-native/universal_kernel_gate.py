#!/usr/bin/env python3
"""Fixed-core cleanup support gate independent of the chosen quadratic J.

The identity T=C R only needs J^2=-I. Native/support costs still require
the stated separate-call and full-output implementation contract.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse
import hashlib
import json
from joint_coefficient_gate import operators, expected_gamma, left_gamma
from native_model import Model, PIN, b, ce, mul, need, phase, same
from even_parity_source import kernels, source_chart

HERE = Path(__file__).resolve().parent


def gm(a, c):
    """Exact signed plane algebra: N_i^2=-I and permutations relabel N_i."""
    xa, pa, sa = a
    xc, pc, sc = c
    moved = sum(1 << pa[j] for j in range(len(pa)) if xc >> j & 1)
    return xa ^ moved, tuple(pa[pc[j]] for j in range(len(pa))), sa * sc * (-1) ** ((xa & moved).bit_count())


def gi(a):
    x, p, s = a
    pi = tuple(p.index(j) for j in range(len(p)))
    return sum(1 << pi[j] for j in range(len(p)) if x >> j & 1), pi, s * (-1) ** x.bit_count()


def group_words(q):
    planes = 2 * q + 2
    ident = (0, tuple(range(planes)), 1)
    def n(i):
        return 1 << i, ident[1], 1
    def p(i):
        out = list(ident[1])
        out[0], out[i] = out[i], out[0]
        return 0, tuple(out), 1
    def prod(*args):
        out = ident
        for a in args:
            out = gm(out, a)
        return out
    Dv = ident
    for r in range(2, q + 1):
        Dv = prod(p(2 * r + 1), n(0), Dv)
    Dv = (Dv[0], Dv[1], Dv[2] * (-1) ** (q - 2))
    F = prod(*(n(j) for j in range(1, planes)))
    G = prod(n(0), p(1), n(0), p(2), gi(Dv))
    Rinv = prod((0, ident[1], -1), G, gi(F))
    support = [3, 4] + list(range(6, 2 * q + 1, 2))
    need(Rinv[0] == sum(1 << j for j in support), 'exact all-q native support of R inverse')
    need(len(support) == q, 'q distinct native planes')
    R = gi(Rinv)
    need(prod(R, Rinv) == prod(Rinv, R) == ident, 'signed all-f inverse of R')
    return {'F': F, 'G': G, 'R': R, 'R_inverse': Rinv,
            'R_inverse_native_planes': support}


def physical_normal(z, normal):
    bits, perm, sign = normal
    rows = [0] * z.n
    for src, dst in enumerate(perm):
        for half in (0, 1):
            for bit in range(z.f):
                rows[(2 * dst + half) * z.f + bit] = 1 << ((2 * src + half) * z.f + bit)
    values = [z.N if j == 0 else z.T[j - 1] for j in range(len(perm)) if bits >> j & 1]
    return mul(phase(z.n, 0 if sign == 1 else 2), *values, ce.perm(z.n, rows))


def complement_gamma(q, fs):
    n = (4 * q + 4) * fs
    rows = [0] * n
    for plane in [3, 4] + list(range(6, 2 * q + 1, 2)):
        for half in (0, 1):
            for bit in range(fs):
                j = (2 * plane + half) * fs + bit
                rows[j] = 1 << j
    return tuple(rows)


def examples():
    z = Model(1, 5)
    _, J0 = kernels(z)
    M = source_chart(z)
    fresh12 = mul(z.P[0], z.P[1], z.P[0])
    # Conjugating N0 times a disjoint involution gives a true nontrivial
    # X-character linear part while preserving square -I exactly.
    Jaffine = mul(M, z.N, fresh12, M.adjoint())
    candidates = [('frozen_even_J', J0), ('old_common_N', z.N), ('nontrivial_X_linear_J', Jaffine)]
    q = 2
    _, _, _, _, _, _, Dv, F, _, _ = operators(q, 1)
    G = mul(z.N, z.P[0], z.N, z.P[1], Dv.adjoint())
    R = mul(phase(z.n, 2), F, G.adjoint())
    out = []
    for name, J in candidates:
        same(mul(J, J), phase(z.n, 2), 'candidate exact J square -I')
        T = mul(F, J)
        need(b.native_rank(T) == z.n, 'candidate actual full FJ output')
        C = mul(F, J.adjoint(), G, F.adjoint())
        same(mul(C, R), T, 'universal phase-exact C R=T')
        ranks = [b.native_rank(mul(z.prefix(s), J, z.prefix(s).adjoint())) for s in range(6)]
        need(all(r >= 2 for r in ranks), 'separate source query arity lower bound')
        need(b.native_rank(C) >= 8, 'universal cleanup native lower bound on changed kernel')
        out.append({'J': name, 'J_native_arity': b.native_rank(J),
                    'FJ_native_arity': b.native_rank(T), 'coefficient_native_arity': b.native_rank(C),
                    'source_query_arities_by_completed_stage': ranks,
                    'exact_Gaussian_phase_identity': 'PASS'})
    return out


def run():
    checks = []
    for q in range(2, 17):
        signed = group_words(q)
        for fs in (1, 2):
            z, J, A, B1, B2, Q1, Dv, F, C, collapsed = operators(q, fs)
            G = mul(z.N, z.P[0], z.N, z.P[1], Dv.adjoint())
            Rinv = mul(phase(z.n, 2), G, F.adjoint())
            R = Rinv.adjoint()
            need(left_gamma(Rinv) == complement_gamma(q, fs), 'actual complete Gamma of R inverse')
            need(b.native_rank(R) == b.native_rank(Rinv) == 2 * q * fs,
                 'independent exact universal complement arity')
            literal = physical_normal(z, signed['R_inverse'])
            need(literal.tab == Rinv.tab, 'signed plane all-f normal form tableau')
            if fs == 1 and q in (2, 3):
                same(literal, Rinv, 'signed plane normal form actual global phase')
            checks.append({'q': q, 'f': fs, 'R_native_arity': b.native_rank(R),
                           'R_inverse_native_planes': signed['R_inverse_native_planes'],
                           'normal_form_sign': signed['R_inverse'][2],
                           'normal_form_plane_permutation': list(signed['R_inverse'][1])})
    return {'status': 'PASS_UNIVERSAL_FIXED_CORE_JOINT_CLEANUP_GATE', 'scientific_pin': PIN,
            'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'source_pins': [{'path': str(HERE / p), 'sha256': hashlib.sha256((HERE / p).read_bytes()).hexdigest()}
                            for p in ('joint_coefficient_gate.py', 'JOINT-COEFFICIENT-GATE.json', 'LITERAL-INVERSE-BINDING.json')],
            'identity': 'G=N P1 N P2 Dv^-1; T=F J; C=F J^-1 G F^-1; R=-F G^-1. Then C R=T exactly because -J^-1=J follows from J^2=-I.',
            'J_domain': 'Any actual invertible linear operator family J with phase-exact J^2=-I, for which the stated source-code/prefix equations and full FJ endpoint hold. No X-character, Clifford, commutation or uniform tensor assumption on J is needed for the operator support identity.',
            'R_domain': 'The fixed physical swaps P1/P2 and Dv=(-1)^(q-2)(P_(2q+1)N)...(P5N) remain unchanged. Native N_i^2=-I and whole-plane swaps relabel N_i phase-exactly for every f.',
            'all_q_R_rank_proof': 'R^-1=-G F^-1 has exact left native planes{3,4,6,8,...,2q}, q distinct planes, followed by a literal whole-plane ADDRESS and the saved sign. Therefore both R and its inverse are Clifford with nativearity2qf and exact row support2^(2qf).',
            'universal_coefficient_support': 'If the target T=FJ has exactly2^(mf) nonzeros in every row, m=4q+4, row-support submultiplicativity in T=C R forces max_row_support(C)>=2^((2q+4)f). C need not itself be a Clifford. Left monomial output adapters preserve this lower bound.',
            'cleanup_tariff': 'Every complete tail in the stated native/monomial/binary-ADD model satisfies sum actual native arities + S >= (2q+4)f, on all banks and all original columns. The independent source-bound full-scan transfer gate decides whether S growing linearly in f is admitted.',
            'source_call_lower_bound': 'For K_s=F_s J F_s^-1, T=(F_k F_s^-1)K_s F_s. The fresh factors have total nativearity(m-2)f. A Clifford K_s must therefore have nativearity>=2f. Without a Clifford assumption the exact analogous support inequality is max_row_support(K_s)>=2^(2f); assigning it a native arity still needs its admitted implementation.',
            'separate_call_profile_scope': 'For separately exposed J source/input/continuation calls, fixed scalar bank skeleton and individually paid fresh progresses, every such Clifford K_s costs>=2f. Thus prefix native mass>=n*m-2q. With an admissible sublinear-full-scan cleanup native mass>=2q+4, total>=n*m+4. Cross-cut fusion, different source-code/post maps, changed core or endpoint/owner contracts are not covered by this separate-call counting.',
            'actual_normal_form_checks': checks, 'changed_kernel_examples': examples(),
            'limits': ['The literal original-column prefix is independently pinned for q2/q3; all-q application uses the written caller interface/induction.',
                       'The root full-scan cost note is a separate source-bound implementation theorem, not a consequence of this support count alone.',
                       'A changed source-code map or base core can change G and the complement R; such a construction must rederive all original columns, phases, native queries and stock.',
                       'No all-size multiplication theorem, owner, precision, tape or improved kappa is claimed.'],
            'no_new_kappa': True}


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'UNIVERSAL-KERNEL-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved universal kernel gate differs')
    print(out['status'])
