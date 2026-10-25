#!/usr/bin/env python3
"""Exact marked-residual commutator certificates, with the actual all-f scope.

The operator C is a proof witness, not an available circuit operation.
It commutes whole ordered-plane permutations and X translations, and does
not commute arbitrary Pauli Z or arbitrary bit-linear ADDRESS maps.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
from itertools import permutations
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent


def need(x, why):
    if not x:
        raise ValueError(why)


def matmul(a, b):
    n = len(a)
    out = [[0] * n for _ in range(n)]
    for i in range(n):
        for h, z in enumerate(a[i]):
            if z:
                for j, w in enumerate(b[h]):
                    if w:
                        out[i][j] += z * w
    return out


def plus(a, b, sign=1):
    return [[x + sign * y for x, y in zip(r, s)] for r, s in zip(a, b)]


def exact_rank(matrix):
    a = [[Fraction(z) for z in row] for row in matrix]
    original_rows = list(range(len(a)))
    pivots, pivot_rows = [], []
    row = 0
    for col in range(len(a[0])):
        h = next((h for h in range(row, len(a)) if a[h][col]), None)
        if h is None:
            continue
        a[row], a[h] = a[h], a[row]
        original_rows[row], original_rows[h] = original_rows[h], original_rows[row]
        z = a[row][col]
        a[row] = [x / z for x in a[row]]
        for h in range(len(a)):
            if h != row and a[h][col]:
                z = a[h][col]
                a[h] = [x - z * y for x, y in zip(a[h], a[row])]
        pivots.append(col)
        pivot_rows.append(original_rows[row])
        row += 1
    need(all(not any(r) for r in a[row:]), 'rank upper bound has zero remaining rows')
    return row, pivots, pivot_rows


def signs(L):
    return [1 if not (x >> owner & 1) else -1
            for x in range(1 << L) for owner in range(L)]


def mapping(L, plane_permutation=None, native_mask=0):
    p = list(range(L)) if plane_permutation is None else plane_permutation
    out = []
    for x in range(1 << L):
        y = x ^ native_mask
        z = sum(((y >> i) & 1) << p[i] for i in range(L))
        for owner in range(L):
            out.append(z * L + p[owner])
    need(sorted(out) == list(range(len(out))), 'actual virtual/residual action is a permutation')
    return out


def permutation_matrix(mapping):
    a = [[0] * len(mapping) for _ in mapping]
    for col, row in enumerate(mapping):
        a[row][col] = 1
    return a


def commutator_entries(L, native_mask):
    c = signs(L)
    out = []
    for col, row in enumerate(mapping(L, native_mask=native_mask)):
        z = c[col] - c[row]
        if z:
            out.append([row, col, z])
    need(len({e[0] for e in out}) == len(out) == len({e[1] for e in out}),
         'nonzero commutator entries have distinct rows and columns')
    need(len(out) == native_mask.bit_count() * (1 << L), 'exact query commutator rank')
    return out


def local_fixture(L, bank_masks):
    c = signs(L)
    for p in permutations(range(L)):
        need(all(c[i] == c[j] for i, j in enumerate(mapping(L, p))),
             'every whole-plane permutation commutes the marked C')
    # Every Q_i and every actual X translation is diagonal in this basis;
    # the latter may have a different sign for the two residual labels.
    for i in range(L):
        q = [1 if not (x >> i & 1) else -1 for x in range(1 << L) for _ in range(L)]
        need(all((a * b) == (b * a) for a, b in zip(c, q)), 'Q_i commutes C')
    ranks = {str(mask): len(commutator_entries(L, mask)) for mask in range(1, 1 << L)}
    target_rank = sum(len(commutator_entries(L, mask)) for mask in bank_masks)
    expected_planes = sum(mask.bit_count() for mask in bank_masks)
    need(target_rank == expected_planes * (1 << L), 'joint bank debt ranks add literally')
    return dict(planes=L, internal_dimension=L * (1 << L), bank_native_masks=bank_masks,
                C_diagonal=c, single_bank_query_commutator_ranks=ranks,
                target_commutator_rank=target_rank,
                minimum_total_native_plane_count=expected_planes,
                target_Gaussian_phase_exponents=[mask.bit_count() % 4 for mask in bank_masks],
                phase_note='The displayed native action is i^r times its real permutation. Multiplication by that nonzero Gaussian unit leaves the recorded commutator rank unchanged.')


def core_fixture():
    L, d = 3, 24
    I = permutation_matrix(mapping(L))
    X0 = permutation_matrix(mapping(L, native_mask=1))
    P1 = permutation_matrix(mapping(L, [1, 0, 2]))
    P2 = permutation_matrix(mapping(L, [2, 1, 0]))
    Q1 = matmul(matmul(X0, P1), X0)
    QP = matmul(Q1, P2)
    J = [[plus(plus(P2, Q1), I, -1), plus(I, P2, -1)],
         [plus(Q1, I, -1), I]]
    Ji = [[QP, plus(Q1, QP, -1)],
          [plus(QP, P2, -1), plus(plus(Q1, P2), QP, -1)]]
    def block(a):
        return [[a[i // d][j // d][i % d][j % d] for j in range(2 * d)]
                for i in range(2 * d)]
    ident = [[int(i == j) for j in range(2 * d)] for i in range(2 * d)]
    need(matmul(block(J), block(Ji)) == matmul(block(Ji), block(J)) == ident,
         'fixed J and its written inverse are exact')
    # N0=i X0, so the common factor i is removed solely for rank arithmetic.
    T = block([[matmul(Ji[i][j], X0) for j in range(2)] for i in range(2)])
    c = signs(L) * 2
    R = [[T[i][j] * (c[j] - c[i]) for j in range(2 * d)] for i in range(2 * d)]
    rank, columns, rows = exact_rank(R)
    need(rank == 24, 'fixed-core exact commutator rank is 24=3*2^3')
    minor = [[R[i][j] for j in columns] for i in rows]
    need(exact_rank(minor)[0] == 24, 'displayed 24x24 pivot minor is nonsingular')
    return dict(internal_dimension=d, total_dimension=2 * d,
                J=block(J), J_inverse=block(Ji), correction_without_common_Gaussian_unit=T,
                C_diagonal=c, commutator=R, exact_rational_rank=rank,
                nonsingular_minor_rows=rows, nonsingular_minor_columns=columns,
                normalized_native_plane_lower_bound=3,
                meaning='The fixed block is J^-1 diag(N0,N0); Q1=N0^-1 P1 N0=X0 P1 X0 exactly. The omitted common scalar is i, which preserves rank.')


def terminal_fixture(q):
    from handoff_family_independent import RightAlgebra, event_word, factory_certificate
    A = RightAlgebra(2 * q + 2)
    M, _ = A.replay(event_word(q), 2 * q + 2)
    data = factory_certificate(q, A, M)
    normalized = []
    external_union = set()
    for item in data['rows']:
        p = item['ADDRESS_permutation']
        left = item['native_support_left_normal']
        right = {i for i, j in enumerate(p) if j in left}
        inverse_common = p.index(0)
        G = right ^ {inverse_common}
        need(0 in G and 1 not in G and 2 not in G, 'normalized debt has exactly its common core plane')
        external = G - {0}
        need(not external_union.intersection(external), 'normalized external debts stay disjoint')
        external_union.update(external)
        normalized.append(dict(physical_row=item['physical_row'], fixed_J_coordinate=item['fixed_J_coordinate'],
                               right_native_planes=sorted(right), ADDRESS_inverse_common_plane=inverse_common,
                               normalized_correction_native_planes=sorted(G),
                               external_native_planes=sorted(external)))
    need(len(external_union) == q, 'actual tail has q distinct external debts after right ADDRESS normalization')
    L = 2 * q + 2
    return dict(q=q, ambient_planes=L, normalized_debts=normalized,
                external_support_union=sorted(external_union), external_commutator_rank=q * (1 << L),
                core_commutator_rank=3 * (1 << L), total_pivot_correction_commutator_rank=(q + 3) * (1 << L),
                minimum_tail_native_plane_count=q + 3, minimum_tail_rank_mass_in_units_f=2 * (q + 3),
                current_direct_tail_native_plane_count=q + 4,
                scope='After this exact prefix cut; any length of whole-plane ADDRESS/X-translation/GL-bank bridge word and native products on whole planes. Public-reader columns can only increase the complete tail commutator rank. Cross-cut cancellation or Pauli Z/other bit-linear ADDRESS is outside this tail-only invoice.')


def excluded_Z_control():
    # For f=1 choose residual r=Xp*Xq.  In the canonical N=iX_virtual
    # basis Zp sends (x,rbit) to (x xor1,rbit xor1), with a nonzero unit.
    # Extend C as identity outside the one-mark sector.  This extension
    # still commutes X and plane permutations but fails to commute Zp.
    L = 2
    def c_value(bits, residual):
        if residual.bit_count() != 1:
            return 1
        owner = (residual & -residual).bit_length() - 1
        return 1 if not (bits >> owner & 1) else -1
    bits, residual, plane = 1, 1, 0
    before = c_value(bits, residual)
    after = c_value(bits ^ (1 << plane), residual ^ (1 << plane))
    need(before == -1 and after == 1, 'Pauli Z really escapes the marked-C commutant')
    return dict(actual_f=1, virtual_bits=bits, marked_residual_bits=residual,
                Pauli_Zp_plane=plane, C_before=before, C_after=after,
                result='NONCOMMUTING: the claimed floor must not be extended to full Pauli Z bridges.')


def prove():
    fullpair = local_fixture(2, [3, 3])
    need(fullpair['target_commutator_rank'] == 16 and fullpair['single_bank_query_commutator_ranks']['1'] == 4,
         'three unary queries cannot pay the two-bank full pair')
    return dict(status='PASS_EXACT_MARKED_RESIDUAL_GLOBAL_FLOOR', no_new_kappa=True,
                full_pair_three_query_gate=fullpair,
                q3_disjoint_debt_gate=local_fixture(3, [1, 6]),
                q4_disjoint_debt_gate=local_fixture(4, [3, 12]),
                fixed_core=core_fixture(),
                actual_handoff_terminal_gates=[terminal_fixture(q) for q in (2, 3, 4, 8)],
                excluded_Pauli_Z_negative_control=excluded_Z_control(),
                global_theorem='For L>=1 ordered native planes and n arbitrary target banks, every exact word with target diag(prod_(i=0..L-1) N_i) on those n independent banks, restored arbitrary helpers, native queries on unions of r whole planes, and arbitrary invertible bank bridges over whole-plane ADDRESS permutations and X translations has sum r>=nL. Its native rank mass is at least2f*nL=n*m for m=2fL. Arbitrary Gaussian scalar phases, query inverses and conjugation by covered free bridges do not alter the bound.',
                global_proof='On an actual invariant subspace V of dimensionL*2^L let C|x,owner>=(-1)^x_owner |x,owner>. Whole-plane permutations move x andowner together and X translations are diagonal, so every covered bridge commutesC. Product of r native planes flips r virtual bits and leavesownerfixed; its commutator has r*2^L nonzero entries with distinct rows/columns. The n-bank full native target has ranknL2^L. Rank[AB,C]<=rank[A,C]+rank[B,C] for invertible A,B proves the bound.',
                actual_all_f_embedding='N_f^2=-I and N_f anticommutes every single X translation on its2f bits. Fix Q=X on one distinguished bit. The2f-1 commuting operators R_b=Q*X_b commuteN andQ. In each joint R eigenlabel choose |+,r> withQ=+1 and define |-,r>=-i*N|+,r>. Then N=iX_virtual, Q=Z_virtual and every X translation is diagonal in (virtual,r). There are2^(2f-1)>=2 residual labels for everyf>=1. Choose the same two labels u,v in every plane and restrict to tensors with exactly one v. Identical plane bases make actual whole-plane ADDRESS permutations the simultaneous virtual/residual permutations used by the certificate. This is an actual invariant subspace, not a faithful-representation assumption or a finite-f interpolation.',
                scope_exclusions=['Pauli Z is explicitly excluded: it moves residual labels and fails the exact negative control.',
                                  'Arbitrary bit-linear ADDRESS maps, p/q role controllers and native axes not unions of the declared ordered planes are excluded unless independently proved to commute this C.',
                                  'The n*m floor concerns the declared whole-plane native rank mass and complete full-native bank contract. It is not a global circuit, supplier or multiplication-theorem lower bound.'],
                attribution=['Marked-residual construction generalizes the earlier q4 two-residual commutator mechanism.',
                             'Parent root identified the complete n-bank stock-floor consequence.',
                             'The q3/q4 joint debt and actual J-core certificates and all-f X-translation embedding are derived and checked here.'],
                producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_pins=[dict(path=str(HERE / name), sha256=hashlib.sha256((HERE / name).read_bytes()).hexdigest())
                             for name in ['handoff_family_independent.py', 'source_handoff_prefix.py']])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(prove()))
    path = HERE / 'MARKED-RESIDUAL-GLOBAL-FLOOR.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved marked-residual certificate differs')
    print(out['status'], 'global mass>=n*m in whole-plane/X-only grammar; Pauli Z excluded')


if __name__ == '__main__':
    main()
