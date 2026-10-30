"""Exact bounded corroboration for overwrite information loss.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Finite algebra only: no chart locality, native operations or physical price.
"""
from fractions import Fraction as F
from itertools import product, combinations
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(matrix):
    """Independent dense row elimination for the decoding oracle."""
    a = [[F(x) for x in row] for row in matrix]
    if not a:
        return 0
    lead = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(lead, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[lead], a[pivot] = a[pivot], a[lead]
        scale = a[lead][col]
        a[lead] = [x / scale for x in a[lead]]
        for i in range(lead + 1, len(a)):
            scale = a[i][col]
            if scale:
                a[i] = [x - scale * y for x, y in zip(a[i], a[lead])]
        lead += 1
        if lead == len(a):
            break
    return lead


def matvec(a, x):
    return tuple(sum(v * w for v, w in zip(row, x)) for row in a)


def multiply(a, b):
    cols = tuple(zip(*b))
    return tuple(tuple(sum(x * y for x, y in zip(row, col)) for col in cols)
                 for row in a)


def unit(n, i):
    return tuple(int(j == i) for j in range(n))


def solve_columns(r, b):
    """Cramer's-rule membership test, separate from the rank oracle.

    The declared finite domains have one or two full-rank columns.
    Return the unique solution or None if b is outside their span.
    """
    n = len(r[0])
    need(n in (1, 2), 'minor solver outside declared domain')
    solution = None
    for rows in combinations(range(len(r)), n):
        if n == 1:
            a = r[rows[0]][0]
            if a:
                solution = (F(b[rows[0]], a),)
                break
        else:
            i, j = rows
            a, c = r[i]
            d, e = r[j]
            determinant = a * e - c * d
            if determinant:
                solution = (F(b[i] * e - c * b[j], determinant),
                            F(a * b[j] - b[i] * d, determinant))
                break
    need(solution is not None, 'full column rank required')
    return solution if matvec(r, solution) == tuple(b) else None


def overwrite(r, p):
    """Rows of the cut map from (old inputs, new independent z)."""
    n = len(r[0])
    return tuple((0,) * n + (1,) if i == p else tuple(row) + (0,)
                 for i, row in enumerate(r))


def decodable(cut, targets):
    augmented = tuple(tuple(row) + (0,) for row in targets)
    return rank(cut + augmented) == rank(cut)


def matrices(m, n, alphabet):
    for values in product(alphabet, repeat=m * n):
        yield tuple(tuple(values[i * n:(i + 1) * n]) for i in range(m))


def exhaustive_targets():
    rows = []
    for m, n, alphabet in ((2, 1, (-1, 0, 1)), (2, 2, (-1, 0, 1)),
                            (3, 2, (0, 1))):
        matrix_count = cases = collisions = feasible = zero_d = 0
        for r in matrices(m, n, alphabet):
            if rank(r) != n:
                continue
            matrix_count += 1
            for p in range(m):
                ep = unit(m, p)
                collision = solve_columns(r, ep)
                cut = overwrite(r, p)
                for suffix_row in product((-1, 0, 1), repeat=m):
                    target = multiply((suffix_row,), r)
                    d = suffix_row[p]
                    actual = decodable(cut, target)
                    predicted = collision is None or d == 0
                    need(actual == predicted, 'membership criterion disagrees with row-span oracle')
                    if collision is not None:
                        need(matvec(cut, collision + (0,)) == (0,) * m,
                             'claimed input collision survives the overwrite')
                        need(matvec(target, collision) == (d,),
                             'collision target difference is not the suffix direction')
                        collisions += 1
                    zero_d += d == 0
                    feasible += actual
                    cases += 1
        rows.append({'shape': [m, n], 'alphabet': list(alphabet), 'full_rank_matrices': matrix_count,
                     'target_cases': cases, 'collision_cases': collisions,
                     'zero_suffix_directions': zero_d, 'decodable_cases': feasible})
    need([row['full_rank_matrices'] for row in rows] == [8, 48, 42], 'domain count changed')
    need(sum(row['target_cases'] for row in rows) == 4410, 'target-case inventory changed')
    return rows


def suffix_shortcut():
    matrices_checked = cases = nonidentity = feasible = 0
    ident = ((1, 0), (0, 1))
    for r in matrices(3, 2, (0, 1)):
        if rank(r) != 2:
            continue
        for s in matrices(2, 3, (0, 1)):
            endpoint = multiply(s, r)
            if rank(endpoint) != 2:
                continue
            matrices_checked += 1
            nonidentity += endpoint != ident
            for p in range(3):
                direction = tuple(row[p] for row in s)
                coordinate = solve_columns(endpoint, direction)
                need(coordinate is not None, 'invertible endpoint solve failed')
                shortcut = matvec(r, coordinate) == unit(3, p)
                collision = solve_columns(r, unit(3, p)) is not None
                actual = decodable(overwrite(r, p), endpoint)
                need(shortcut == collision, 'endpoint-aware shortcut disagrees with membership')
                need(actual == (not shortcut), 'full endpoint decoding oracle disagrees')
                feasible += actual
                cases += 1
    need(nonidentity > 0 and feasible > 0, 'endpoint check lacks discriminating cases')
    return {'endpoint_pairs': matrices_checked, 'nonidentity_endpoints': nonidentity,
            'pivot_cases': cases, 'decodable_cases': feasible}


def fixtures():
    # Dead owned rows do not recover a coordinate that has no remaining copy.
    dead = ((1, 0), (0, 1), (0, 0))
    endpoint = ((2, 0), (0, 1))
    suffix = ((2, 0, 0), (0, 1, 0))
    d = tuple(row[0] for row in suffix)
    need(multiply(suffix, dead) == endpoint, 'endpoint fixture malformed')
    need(not decodable(overwrite(dead, 0), endpoint), 'dead row spuriously restores input')
    need(matvec(dead, solve_columns(endpoint, d)) == unit(3, 0), 'corrected shortcut fails')
    need(matvec(dead, d) != unit(3, 0), 'nonidentity endpoint does not expose missing inverse')

    # The copied pivot is recoverable, including after an invertible suffix
    # turns a copy difference into an individual carrier (originally zero).
    duplicate = ((1, 0), (0, 1), (1, 0))
    suffix3 = ((1, 0, 0), (0, 1, 0), (-1, 0, 1))
    original = multiply(suffix3, duplicate)
    direction = tuple(row[0] for row in suffix3)
    cut = overwrite(duplicate, 0)
    need(original[2] == (0, 0) and direction[2] == -1, 'individual carrier missing')
    need(decodable(cut, original), 'copied pivot falsely rejected')
    after = multiply(suffix3, cut)
    repaired_first = tuple(a + b for a, b in zip(after[0], after[2]))
    need(repaired_first == (1, 0, 0), 'carrier correction does not recover retired value')

    # At the cut itself no row is zero; a same-chart linear combination can
    # nevertheless be a carrier. All three fixture rows are declared co-located.
    combination = ((1, 0, -1),)
    need(all(any(row) for row in duplicate), 'combination fixture has individual zero row')
    need(multiply(combination, duplicate) == ((0, 0),), 'combination not originally zero')
    need(multiply(combination, cut) == ((-1, 0, 1),), 'combination not z minus retired value')
    need(multiply(((1, 0, 1),), duplicate) != ((0, 0),), 'wrong-sign carrier not rejected')

    # No outside defect is an essential hypothesis: a lost pivot does not
    # matter to a target that reads only the unaffected input.
    need(decodable(overwrite(dead, 0), ((0, 1),)), 'zero-direction exception rejected')
    return {'dead_owned_row_does_not_repair': True,
            'nonidentity_endpoint_requires_inverse': True,
            'duplicated_pivot_carrier_repairs': True,
            'same_chart_combination_without_zero_row': True,
            'wrong_sign_combination_rejected': True,
            'zero_direction_exception_retained': True}


def run_controls():
    return {'exhaustive_targets': exhaustive_targets(),
            'suffix_shortcut': suffix_shortcut(), 'fixtures': fixtures()}


if __name__ == '__main__':
    print(json.dumps(run_controls(), sort_keys=True))
    print('PASS_OVERWRITE_INFORMATION_CONTROLS')
