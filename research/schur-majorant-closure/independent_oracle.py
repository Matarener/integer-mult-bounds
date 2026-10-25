#!/usr/bin/env python3
"""Exact bordered-minor oracle for principal Schur majorant preservation.

No primary implementation/imports. Gaussian rationals use Fraction pairs;
Schur entries are ratios of bordered determinants, not elimination updates.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


@dataclass(frozen=True, slots=True)
class G:
    real: F = F(0)
    imag: F = F(0)

    def __add__(self, other):
        other = other if isinstance(other, G) else G(F(other))
        return G(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.real, -self.imag)

    def __sub__(self, other):
        return self + -as_g(other)

    def __rsub__(self, other):
        return as_g(other) + -self

    def __mul__(self, other):
        other = as_g(other)
        return G(self.real * other.real - self.imag * other.imag,
                 self.real * other.imag + self.imag * other.real)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = as_g(other)
        denominator = other.real * other.real + other.imag * other.imag
        need(denominator != 0, 'Gaussian division by zero')
        return G((self.real * other.real + self.imag * other.imag) / denominator,
                 (self.imag * other.real - self.real * other.imag) / denominator)

    def __bool__(self):
        return bool(self.real or self.imag)


def as_g(value):
    return value if isinstance(value, G) else G(F(value))


def mu(value):
    return abs(value.real) + abs(value.imag)


def modulus_squared(value):
    return value.real * value.real + value.imag * value.imag


ZERO, ONE = G(), G(F(1))


@lru_cache(maxsize=100000)
def determinant(matrix):
    n = len(matrix)
    if n == 0:
        return ONE
    if n == 1:
        return matrix[0][0]
    answer = ZERO
    for column, entry in enumerate(matrix[0]):
        if entry:
            minor = tuple(tuple(row[j] for j in range(n) if j != column) for row in matrix[1:])
            term = entry * determinant(minor)
            answer = answer + (term if column % 2 == 0 else -term)
    return answer


def principal(matrix, indices):
    return tuple(tuple(matrix[i][j] for j in indices) for i in indices)


def schur(matrix, eliminated, retained):
    """S_ij = det(A_(E+i,E+j))/det(A_EE), with original E order."""
    eliminated, retained = tuple(eliminated), tuple(retained)
    pivot = determinant(principal(matrix, eliminated))
    need(bool(pivot), 'singular eliminated principal block')
    return tuple(tuple(determinant(tuple(tuple(matrix[r][c] for c in eliminated + (j,))
                                        for r in eliminated + (i,))) / pivot
                       for j in retained) for i in retained)


def identity_plus(h):
    return tuple(tuple(h[i][j] + (ONE if i == j else ZERO) for j in range(len(h)))
                 for i in range(len(h)))


def row_column_sums(matrix):
    n = len(matrix)
    return ([sum(matrix[i]) for i in range(n)],
            [sum(matrix[i][j] for i in range(n)) for j in range(n)])


def majorant_schur(p, eliminated, retained):
    minus = tuple(tuple((ONE if i == j else ZERO) - p[i][j] for j in range(len(p)))
                  for i in range(len(p)))
    s = schur(minus, eliminated, retained)
    q = tuple(tuple((ONE if i == j else ZERO) - s[i][j] for j in range(len(s)))
              for i in range(len(s)))
    need(all(not z.imag and z.real >= 0 for row in q for z in row),
         'nonnegative Schur majorant failed')
    return tuple(tuple(z.real for z in row) for row in q)


def check_partition(h, p, rho, kind, eliminated, retained):
    s = schur(identity_plus(h), eliminated, retained)
    q = majorant_schur(p, eliminated, retained)
    for i in range(len(s)):
        for j in range(len(s)):
            delta = s[i][j] - (ONE if i == j else ZERO)
            if kind == 'mu':
                need(mu(delta) <= q[i][j], 'component-majorant Schur bound failed')
            else:
                need(modulus_squared(delta) <= q[i][j] * q[i][j],
                     'modulus-majorant Schur bound failed')
    rows, columns = row_column_sums(q)
    need(max(rows, default=F(0)) <= rho and max(columns, default=F(0)) <= rho,
         'same-rho row/column majorant bound failed')
    return s


def normalize(h, p, rho):
    rows, cols = row_column_sums(p)
    budget = max(rows + cols, default=F(0))
    scale = rho / budget if budget else F(1)
    return (tuple(tuple(z * scale for z in row) for row in h),
            tuple(tuple(z * scale for z in row) for row in p))


def matrix_cases():
    alphabet = (ZERO, G(F(1, 8)), G(F(-1, 8)), G(F(0), F(1, 8)),
                G(F(0), F(-1, 8)), G(F(1, 8), F(1, 8)), G(F(-1, 8), F(-1, 8)))
    for index, values in enumerate(product(alphabet, repeat=4)):
        h = (values[:2], values[2:])
        p = tuple(tuple(mu(z) for z in row) for row in h)
        yield 'all_2x2_' + str(index), h, p, F(1, 2), 'mu'
    seed = 0x51C4
    for n, count in ((3, 16), (4, 8)):
        for number in range(count):
            entries = []
            for _ in range(n * n):
                seed = (1103515245 * seed + 12345) % (1 << 31)
                entries.append(alphabet[(seed >> 8) % len(alphabet)])
            h = tuple(tuple(entries[i * n:(i + 1) * n]) for i in range(n))
            p = tuple(tuple(mu(z) for z in row) for row in h)
            rho = (F(1, 4), F(1, 2), F(3, 4), F(7, 8))[number % 4]
            h, p = normalize(h, p, rho)
            yield f'dense_mu_{n}_{number}', h, p, rho, 'mu'
    for n, count in ((3, 8), (4, 4)):
        for number in range(count):
            h_rows, p_rows = [], []
            for _ in range(n):
                h_row, p_row = [], []
                for _ in range(n):
                    seed = (1103515245 * seed + 12345) % (1 << 31)
                    r, sign = (seed % 3), (-1 if seed & 8 else 1)
                    h_row.append(G(F(3 * sign * r, 32), F(4 * r, 32)))
                    p_row.append(F(5 * r, 32))
                h_rows.append(tuple(h_row))
                p_rows.append(tuple(p_row))
            rho = (F(1, 4), F(1, 2), F(3, 4), F(7, 8))[number % 4]
            h, p = normalize(tuple(h_rows), tuple(p_rows), rho)
            yield f'dense_modulus_{n}_{number}', h, p, rho, 'modulus'
    # Toeplitz examples corroborate the source's recursive family without
    # importing its coefficient-generation or circuit implementation.
    for number in range(4):
        coefficients = tuple(alphabet[(2 * j + number) % len(alphabet)] for j in range(4))
        total = sum(mu(z) for z in coefficients)
        scale = F(1, 2) / total if total else F(1)
        h = tuple(tuple(coefficients[i - j] * scale if i >= j else ZERO
                        for j in range(4)) for i in range(4))
        p = tuple(tuple(mu(z) for z in row) for row in h)
        yield f'toeplitz_4_{number}', h, p, F(1, 2), 'mu'


def validate_input(h, p, rho, kind):
    need(F(0) <= rho < 1, 'rho outside contracting domain')
    for i in range(len(h)):
        for j in range(len(h)):
            need(p[i][j] >= 0, 'negative entry majorant')
            if kind == 'mu':
                need(mu(h[i][j]) <= p[i][j], 'input component majorant failed')
            else:
                need(modulus_squared(h[i][j]) <= p[i][j] ** 2, 'input modulus majorant failed')
    rows, columns = row_column_sums(p)
    need(max(rows) <= rho and max(columns) <= rho, 'input row/column budget failed')


def nested_histories(h, p, rho, kind):
    original = identity_plus(h)
    n, checked = len(h), 0
    stack = [(original, tuple(range(n)), ())]
    while stack:
        current, labels, eliminated = stack.pop()
        expected = check_partition(h, p, rho, kind, eliminated, labels)
        need(current == expected, 'nested elimination/restriction history not principal Schur description')
        checked += 1
        if len(labels) > 1:
            for position, label in enumerate(labels):
                keep_positions = tuple(i for i in range(len(labels)) if i != position)
                new_labels = tuple(labels[i] for i in keep_positions)
                stack.append((principal(current, keep_positions), new_labels, eliminated))
                stack.append((schur(current, (position,), keep_positions), new_labels, eliminated + (label,)))
    return checked


def controls():
    rho = F(3, 4)
    h = ((ZERO, G(rho), ZERO), (G(rho), ZERO, ZERO), (G(rho), ZERO, ZERO))
    s = schur(identity_plus(h), (0,), (1, 2))
    delta = tuple(tuple(mu(s[i][j] - (ONE if i == j else ZERO)) for j in range(2)) for i in range(2))
    rows, columns = row_column_sums(delta)
    need(max(rows) <= rho < max(columns) and max(columns) == F(9, 8),
         'row-only counterexample is not discriminating')
    ht = tuple(tuple(h[j][i] for j in range(3)) for i in range(3))
    st = schur(identity_plus(ht), (0,), (1, 2))
    d = tuple(tuple(mu(st[i][j] - (ONE if i == j else ZERO)) for j in range(2)) for i in range(2))
    r, c = row_column_sums(d)
    need(max(c) <= rho < max(r), 'column-only counterexample is not discriminating')
    column_only_max_row = max(r)
    singular_h = ((G(F(-1)),),)
    need(mu(singular_h[0][0]) == 1 and not determinant(identity_plus(singular_h)),
         'rho=1 singularity witness failed')
    # A=I is perfectly admitted, but selecting different row/column indices
    # gives [0], not a near-identity principal restriction.
    identity_two = ((ONE, ZERO), (ZERO, ONE))
    nonprincipal = ((identity_two[0][1],),)
    need(mu(nonprincipal[0][0] - ONE) == 1, 'nonprincipal witness failed')
    # A sign fault can retain the norm bound; distinguish it by the exact
    # principal block-of-inverse identity, not an invented norm violation.
    a = ((ONE, G(F(1, 4))), (G(F(1, 4)), ONE))
    proper = schur(a, (0,), (1,))[0][0]
    wrong = ONE + G(F(1, 16))
    inverse_block = a[0][0] / determinant(a)
    need(ONE / proper == inverse_block and ONE / wrong != inverse_block,
         'Schur correction sign control failed to separate inverse identity')
    need(mu(proper - ONE) <= F(1, 2) and mu(wrong - ONE) <= F(1, 2),
         'sign-control scope assertion false')
    sharp = []
    for r in (F(0), F(1, 4), F(1, 2), F(3, 4), F(7, 8)):
        diagonal = ((G(r), ZERO), (ZERO, G(r)))
        p = ((r, F(0)), (F(0), r))
        endpoint = check_partition(diagonal, p, r, 'mu', (0,), (1,))
        need(mu(endpoint[0][0] - ONE) == r, 'sharpness equality failed')
        sharp.append(str(r))
    return {'row_only_input_rho': str(rho), 'row_only_output_max_column': str(max(columns)),
            'column_only_output_max_row': str(column_only_max_row),
            'rho_1_singular_eliminated_block': True,
            'nonprincipal_restriction_I2_rows0_cols1_is_zero': True,
            'wrong_schur_sign_rejected_by_inverse_identity': True,
            'wrong_schur_sign_also_satisfies_norm_bound': True,
            'sharpness_diagonal_nonempty_elimination_rhos': sharp}


def run():
    families, partition_count, histories, matrices = {}, 0, 0, 0
    digest = hashlib.sha256()
    for label, h, p, rho, kind in matrix_cases():
        validate_input(h, p, rho, kind)
        n, count = len(h), 0
        for assignment in product(range(3), repeat=n):
            # 0=eliminate, 1=retain, 2=drop before the principal restriction.
            eliminated = tuple(i for i, state in enumerate(assignment) if state == 0)
            retained = tuple(i for i, state in enumerate(assignment) if state == 1)
            if not retained:
                continue
            endpoint = check_partition(h, p, rho, kind, eliminated, retained)
            digest.update(repr((label, eliminated, retained, endpoint)).encode())
            count += 1
        if (label.startswith('dense_mu_3_') and int(label.rsplit('_', 1)[1]) < 4
                or label.startswith('dense_modulus_3_') and int(label.rsplit('_', 1)[1]) < 4
                or label.startswith('dense_mu_4_') and int(label.rsplit('_', 1)[1]) < 2
                or label.startswith('dense_modulus_4_') and int(label.rsplit('_', 1)[1]) < 2):
            histories += nested_histories(h, p, rho, kind)
        family = 'all_2x2' if label.startswith('all_2x2') else label.rsplit('_', 1)[0]
        families[family] = families.get(family, 0) + 1
        matrices += 1
        partition_count += count
    return {'status': 'PASS', 'method': 'exact Gaussian-rational bordered-minor ratios; no Gaussian-elimination routine',
            'matrices': matrices, 'families': families, 'principal_E_K_D_partitions': partition_count,
            'nested_history_states': histories, 'endpoint_digest': digest.hexdigest(),
            'controls': controls(), 'finite_cap': {'max_matrix_dimension': 4,
                'all_2x2_alphabet_size': 7, 'all_2x2_rho': '1/2',
                'other_rhos': ['1/4', '1/2', '3/4', '7/8']},
            'limitations': ['Finite corroboration; arbitrary-size lemma needs the separate written proof.',
                'No physical tape, full caller/generator precision, multiplication theorem, or new kappa.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(payload, end='')


if __name__ == '__main__':
    main()
