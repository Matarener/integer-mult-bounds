#!/usr/bin/env python3
"""A single original-column coefficient constrains the unfactored J cleanup.

Apache-2.0; substantial OpenAI Codex assistance. This is a scoped exact
coefficient/support gate, not a complete supplier or a new exponent.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent
NATIVE = FROZEN / 'native-frames'
PINS = {
    NATIVE / 'native_model.py': 'b4291b2868f91f6e77058e58e936b2efe965a9d9ae58095745fa2dad8c1d5c68',
    NATIVE / 'even_parity_source.py': '961f136e4bc1b5da930bdd4ba9bbb594892b9e27f7ab44749d747d4fe16b4cb3',
    NATIVE / 'EVEN-PARITY-SOURCE.json': 'dbeea9cb1abe6fff72cc98e98d9f70eed578d5094cf5f310ed7c500e26af3f3c',
    FROZEN / 'caller' / 'free_ops.py': '5806fe91b9fda162d5986b12e085b14eb3df9a4703f749f61c1f10363138ca77',
}
for path, digest in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError('frozen source pin differs: ' + str(path))
sys.path.insert(0, str(NATIVE))
from native_model import Model, PIN, b, ce, mul, need, phase, same
from even_parity_source import kernels
from lifted_algebra import Algebra

spec = importlib.util.spec_from_file_location('joint_gate_free_ops', FROZEN / 'caller' / 'free_ops.py')
f = importlib.util.module_from_spec(spec)
spec.loader.exec_module(f)


def formal_core():
    """Independent inverse formula over arbitrary noncommuting Q1/B2."""
    Q, B2 = f.mono((1,)), f.mono((2,))
    Qi, Bi = f.inv(Q), f.inv(B2)
    K = [[f.add(f.add(B2, Q), f.neg(f.I)), f.add(f.I, f.neg(B2))],
         [f.add(Q, f.neg(f.I)), f.I]]
    Kinv = [[f.prod(Qi, Bi), f.prod(Qi, f.add(f.I, f.neg(Bi)))],
            [f.prod(f.add(Qi, f.neg(f.I)), Bi),
             f.add(Qi, f.prod(f.add(f.I, f.neg(Qi)), Bi))]]
    need(f.mm(K, Kinv) == f.mm(Kinv, K) == f.eye(2),
         'independent arbitrary-Q1/B2 core inverse both orders')

    # Four public inputs and two arbitrary pivot inputs. Public coupling L
    # has eight independent noncommuting coefficients; it is not set zero.
    n, p = 6, 4
    Du, Dv = f.mono((3,)), f.mono((4,))
    H = [[f.mul(Du, x) for x in K[1]], [f.mul(Dv, x) for x in K[0]]]
    Hinv = f.mm(Kinv, [[f.Z, f.inv(Dv)], [f.inv(Du), f.Z]])
    need(f.mm(H, Hinv) == f.mm(Hinv, H) == f.eye(2), 'whole pivot inverse')
    L = [[f.mono((10 + 4 * i + j,)) for j in range(p)] for i in range(2)]
    M = f.eye(n)
    for i in range(p):
        M[i][i] = f.N
    for i in range(2):
        M[p + i] = L[i] + H[i]
    W = f.eye(n)
    for i in range(2):
        for j in range(p):
            W[p + i][j] = f.neg(f.prod(f.N, f.summ(f.mul(Hinv[i][k], L[k][j])
                                                              for k in range(2)), f.inv(f.N)))
        for j in range(2):
            W[p + i][p + j] = f.prod(f.N, Hinv[i][j])
    target = [[f.N if i == j else f.Z for j in range(n)] for i in range(n)]
    need(f.mm(W, M) == target, 'joint correction all six original columns including public L')
    Minv = f.eye(n)
    for i in range(p):
        Minv[i][i] = f.inv(f.N)
    for i in range(2):
        for j in range(p):
            Minv[p + i][j] = f.neg(f.prod(f.summ(f.mul(Hinv[i][k], L[k][j])
                                                      for k in range(2)), f.inv(f.N)))
        for j in range(2):
            Minv[p + i][p + j] = Hinv[i][j]
    need(f.mm(M, Minv) == f.mm(Minv, M) == f.eye(n), 'full prefix inverse with all coupling')
    coefficient = f.prod(f.N, Qi, Bi, f.inv(Dv))
    need(W[p][p + 1] == coefficient, 'single current V to original t coefficient independent of L')
    mutant = [row[:] for row in W]
    mutant[p][p + 1] = f.prod(f.N, Bi, Qi, f.inv(Dv))
    need(f.mm(mutant, M) != target, 'reversed Schur inverse order defect rejected')
    return {
        'independent_original_columns': n,
        'independent_public_coupling_coefficients': 8,
        'K': f.sm(K), 'K_inverse': f.sm(Kinv),
        'H_row_order': ['Du * K_row2', 'Dv * K_row1'],
        'required_retarded_coefficient': 'J Q1^-1 B2^-1 Dv^-1',
        'coefficient_free_word': f.serial(coefficient),
        'public_L_cannot_change_coefficient': True,
        'defect_control': 'reverse Q1^-1 and B2^-1, rejected on original columns',
    }


def operators(q, fsize):
    z = Model(fsize, 2 * q + 1)
    _, J = kernels(z)
    A = mul(z.N.adjoint(), J)
    B1, B2 = mul(z.P[0], A), mul(z.P[1], A)
    Q1 = mul(J.adjoint(), B1, J)
    Dv = z.I
    for r in range(2, q + 1):
        Dv = mul(z.P[2 * r], z.N, Dv)
    Dv = mul(phase(z.n, 2 * (q - 2)), Dv)
    F = z.prefix(2 * q + 1)
    C = mul(F, J, Q1.adjoint(), B2.adjoint(), Dv.adjoint(), F.adjoint())
    collapsed = mul(F, A.adjoint(), z.P[0].adjoint(), z.N,
                    z.P[1].adjoint(), Dv.adjoint(), F.adjoint())
    return z, J, A, B1, B2, Q1, Dv, F, C, collapsed


def expected_gamma(q, fsize):
    n = (4 * q + 4) * fsize
    rows = [0] * n
    for half in (0, 1):
        for bit in range(fsize):
            ix = lambda plane: (2 * plane + half) * fsize + bit
            x, y = ix(0), ix(1)
            rows[x] = (1 << x) | (1 << y)
            rows[y] = 1 << x
            for plane in [2] + list(range(5, 2 * q + 2, 2)):
                rows[ix(plane)] = 1 << ix(plane)
    return tuple(rows)


def left_gamma(op):
    # U has binary form S(Gamma) P. Recover Gamma=B P^-1 independently.
    n = op.n
    acols = tuple(x for x, zz, ph in op.tab[:n])
    need(all(zz == 0 and x.bit_count() == 1 for x, zz, ph in op.tab[:n]),
         'actual coefficient X image is a coordinate permutation')
    arows = ce.transpose(acols, n)
    ainv_cols = ce.transpose(ce.inv(arows, n), n)
    bcols = tuple(x for x, zz, ph in op.tab[n:])
    def apply_cols(cols, word):
        out = 0
        while word:
            bit = word & -word
            out ^= cols[bit.bit_length() - 1]
            word ^= bit
        return out
    gamma_cols = tuple(apply_cols(bcols, x) for x in ainv_cols)
    return ce.transpose(gamma_cols, n)


def all_f_phase(q, C1):
    a = Algebra(2 * q + 1)
    _, j1 = kernels(a.model)
    J = a.lift(j1, exponent=1)
    A = a.product(a.adjoint(a.N), J)
    B1, B2 = a.product(a.P[0], A), a.product(a.P[1], A)
    Q1 = a.product(a.product(a.adjoint(J), B1), J)
    Dv = a.one
    for r in range(2, q + 1):
        Dv = a.product(a.product(a.P[2 * r], a.N), Dv)
    Dv = a.scale(Dv, (-1) ** (q - 2))
    F = a.one
    for t in a.T:
        F = a.product(F, t)
    C = F
    for x in (J, a.adjoint(Q1), a.adjoint(B2), a.adjoint(Dv), a.adjoint(F)):
        C = a.product(C, x)
    exponent = 6 - 3 * q
    need(C == a.lift(C1, exponent=exponent), 'complete all-f Gaussian tensor phase, all four residues')
    return {'q': q, 'tensor_phase_exponent': exponent,
            'identity': 'C_f=i^((6-3q)*(1-f)) C_1^tensor(f), after bit regrouping',
            'all_four_f_mod4_residues': 'PASS'}


def run():
    core = formal_core()
    rank_checks, row_checks, phase_checks = [], [], []
    for q in range(2, 13):
        for fs in (1, 2):
            z, J, A, B1, B2, Q1, Dv, F, C, collapsed = operators(q, fs)
            gamma = left_gamma(C)
            need(gamma == expected_gamma(q, fs), 'exact all-q block-diagonal left Gamma formula')
            need(b.native_rank(C) == (2 * q + 4) * fs,
                 'unfactored original-column coefficient native arity')
            need(C.tab == collapsed.tab, 'actual collapsed signed tableau')
            if fs == 1 and q in (2, 3, 4):
                same(C, collapsed, 'exact core collapse with mandatory global phases')
                state, depth = b.sparse_column(C.adjoint())
                need(len(state) == 1 << ((2 * q + 4) * fs), 'actual row support including all cancellations')
                row_checks.append({'q': q, 'f': fs, 'row_nonzeros': len(state), 'Gaussian_depth': depth})
                phase_checks.append(all_f_phase(q, C))
            rank_checks.append({'q': q, 'f': fs, 'native_arity': b.native_rank(C),
                                'native_margin_per_f': 2 * q,
                                'Gamma_formula': 'two copies of [[1,1],[1,0]] on(0,1), plus diagonal2 andodd5..2q+1'})
    return {
        'status': 'PASS_UNFACTORED_JOINT_J_COEFFICIENT_SUPPORT_GATE',
        'scientific_pin': PIN,
        'producer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_pins': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                        for p in list(PINS) + [NATIVE / 'lifted_algebra.py']],
        'formal_original_column_core': core,
        'physical_coefficient': 'C_tV=F J Q1^-1 B2^-1 Dv^-1 F^-1, Q1=J^-1B1J, B_s=P_s N^-1J',
        'exact_collapsed_operator': 'F (N^-1J)^-1 P1^-1 N P2^-1 Dv^-1 F^-1',
        'Dv': '(-1)^(q-2) (P_(2q+1)N)...(P5N)',
        'target_gauge': 'The actual isolated output on original t is F J t. Its outgoing left monomial gauge preserves the support bound. No arbitrary replacement of its input right gauge or desired target operator is made.',
        'all_q_native_arity': '(2q+4)f for q>=2,f>=1',
        'rank_checks': rank_checks,
        'actual_row_support_checks': row_checks,
        'all_f_phase_checks': phase_checks,
        'support_tariff': 'For the complete bank-by-address linear tail, let r_j be each native query actual arity and S the number of binary bank-ADD primitives. Then sum_j r_j+S >= (2q+4)f. Monomial ADDRESS/bank routing, nonzero Gaussian pointwise scales and phases have row branching1; each ADD has branching<=2; a rank-r native Fourier child with monomial adapters has branching2^r. Arbitrary cancellations and extra dirty/restored banks cannot increase the upper bound.',
        'bounded_word_corollary': 'If sum r_j=R*f and S=o(f), then R>=2q+4 asymptotically. In particular R<2q cannot provide positive native deficit in such a tail. This is an explicit model premise, not an assertion that bounded-in-f scans are a repository default.',
        'growing_scan_requirement': 'If R<2q, S >= (2q+4-R)f >4f. A paid O(f) full/partial scan construction is not excluded by this combinatorial gate. Its outer-transfer allowance belongs to the root source-bound scan audit.',
        'extra_dirty_banks': 'Any number of independent additional dirty banks may be used and restored exactly. The full required inverse is unique on all inputs, so its original-V/current-bank coefficient remains C_tV. Initial/final zero private cells do not improve the maximum-row-support induction either.',
        'limits': ['The full actual all-q physical prefix and source-bound H/L binding are owned by the caller lane and are not inferred from the homogeneous factory formulas alone.',
                   'A changed initial core, right input chart/target operator, coupled owner endpoint, nonlinear computation or scan alphabet outside the stated row-branching model is not covered.',
                   'Any operator-valued ADD with multiple monomial terms must expose those primitive ADDs or charge its actual row branching; it is not a free scalar ADD.',
                   'No kappa, all-size supplier, owner allocation, precision or fixed-tape claim is made.'],
        'no_new_kappa': True,
    }


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(run()))
    path = HERE / 'JOINT-COEFFICIENT-GATE.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved joint coefficient gate differs')
    print(out['status'])
    print('native arity (2q+4)f; exact support tariff sum(r_j)+S >= (2q+4)f')
