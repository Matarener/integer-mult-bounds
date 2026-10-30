#!/usr/bin/env python3
"""Independent exact checks for the budget proof and its scope boundaries.

Standard library only. No imports from the proposed verifier, no subprocesses,
networking, or writes. Polynomials are listed in ascending degree order.
The written proof supplies the uniform analytic inequalities.
"""

from fractions import Fraction as F
from math import comb, isqrt
import hashlib
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def polynomial_product(left, right):
    terms = {}
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            terms[i + j] = terms.get(i + j, 0) + a * b
    return [terms.get(i, 0) for i in range(len(left) + len(right) - 1)]


def value(coefficients, point):
    return sum(c * point ** i for i, c in enumerate(coefficients))


def derivative(coefficients):
    return [i * coefficients[i] for i in range(1, len(coefficients))] or [0]


def trimmed(coefficients):
    answer = list(coefficients)
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def remainder(numerator, denominator):
    work = trimmed([F(c) for c in numerator])
    denominator = trimmed([F(c) for c in denominator])
    need(denominator != [0], 'division by zero polynomial')
    while work != [0] and len(work) >= len(denominator):
        offset = len(work) - len(denominator)
        coefficient = work[-1] / denominator[-1]
        for j, c in enumerate(denominator):
            work[offset + j] -= coefficient * c
        work = trimmed(work)
    return work


def sturm_count(coefficients, lower, upper):
    """Count distinct roots in an interval with non-root endpoints."""
    need(lower < upper, 'reversed interval')
    need(value(coefficients, lower) and value(coefficients, upper), 'root at endpoint')
    sequence = [trimmed([F(c) for c in coefficients])]
    sequence.append(derivative(sequence[0]))
    while sequence[-1] != [0]:
        next_polynomial = [-c for c in remainder(sequence[-2], sequence[-1])]
        if next_polynomial == [0]:
            break
        sequence.append(next_polynomial)

    def variations(point):
        signs = []
        for polynomial in sequence:
            v = value(polynomial, point)
            if v:
                signs.append(1 if v > 0 else -1)
        return sum(a != b for a, b in zip(signs, signs[1:]))

    return variations(lower) - variations(upper)


def endpoint_polynomial(h, endpoint=2):
    # Binomial expansions independently construct each endpoint factor.
    first = [comb(h, j) * (-1) ** (h - j) for j in range(h + 1)]
    second = [comb(h, j) * (-endpoint) ** (h - j) for j in range(h + 1)]
    return polynomial_product(first, second)


def profiles(coefficients, rank_base=2):
    old = [max(0, -c) for c in coefficients]
    new = [max(0, c) for c in coefficients]
    old_count, new_count = sum(old), sum(new)
    old_mass = sum(c * rank_base ** j for j, c in enumerate(old))
    new_mass = sum(c * rank_base ** j for j, c in enumerate(new))
    need(old_count == new_count, 'counts differ')
    need(old_mass == new_mass, 'rank masses differ')
    return {
        'coefficients_low_to_high': coefficients,
        'old': old,
        'new': new,
        'calls_per_profile': old_count,
        'rank_mass_per_profile': old_mass,
        'rank_base': rank_base,
    }


def exact_scope_examples():
    # Seven ranks, two interior roots, integer counts, endpoint order one.
    n = 10
    residual = [1 - 2 * (n + 1) ** 2, 4 * n * (n + 1) - 4,
                6 - 2 * n * n, -4, 1]
    q = [-c for c in polynomial_product(endpoint_polynomial(1), residual)]
    high_degree = profiles(q)
    need(q == [482, -1595, 1937, -1010, 180, 7, -1], 'quartic coefficients')
    need(high_degree['calls_per_profile'] == 2606, 'quartic call count')
    need(high_degree['rank_mass_per_profile'] == 11334, 'quartic rank mass')
    need(sturm_count(residual, F(1), F(2)) == 2, 'quartic interior root count')
    left, middle, right = F(1099, 1000), F(11, 10), F(1101, 1000)
    need(value(residual, left) < 0 < value(residual, middle), 'left bracket signs')
    need(value(residual, right) < 0, 'right bracket sign')
    need(sturm_count(residual, left, middle) == 1, 'left bracket root count')
    need(sturm_count(residual, middle, right) == 1, 'right bracket root count')
    need(value(derivative(q), 1) and value(derivative(q), 2), 'endpoint roots not simple')
    # ln(s/r) < s/r-1 < right/left-1 = 2/1099.
    product_upper = high_degree['calls_per_profile'] * (right / left - 1)
    need(product_upper == F(5212, 1099) < 12, 'strict extended-bound violation')
    high_degree.update({
        'interior_roots': 2,
        'root_brackets': [[str(left), str(middle)], [str(middle), str(right)]],
        'residual_at_bracket_points': [str(value(residual, x)) for x in (left, middle, right)],
        'strict_upper_for_W_times_ln_root_ratio': str(product_upper),
        'violated_extension': 'allowing rank support through 2^6 while retaining the 12 constant',
    })

    # The original five ranks, but an edge loss rather than two interior roots.
    residual = polynomial_product([-11, 10], [1, 1])
    edge = profiles(polynomial_product(endpoint_polynomial(1), residual))
    need(edge['coefficients_low_to_high'] == [-22, 31, 12, -31, 10], 'edge coefficients')
    need(edge['calls_per_profile'] == 53 and edge['rank_mass_per_profile'] == 270,
         'edge count or mass')
    need(sturm_count(residual, F(1), F(2)) == 1, 'edge root count')
    sample_checks = []
    for k in (1, 2, 3):
        # 2^(k/4)>11/10, so every factor's sign is fixed without decimals.
        need(2 ** k * 10 ** 4 > 11 ** 4, 'sample is not beyond edge loss')
        sample_checks.append({'p': str(F(k, 4)), 'sign': -1})
    need(2 * 10 ** 8 < 11 ** 8, 'p=1/8 is not inside edge loss')
    need(F(1, 4) < F(120, 7 * 53), 'grid fails rational mesh criterion')
    edge.update({'interior_roots': 1, 'sample_signs': sample_checks,
                 'positive_witness': 'p=1/8',
                 'maximum_grid_gap': '1/4',
                 'safe_mesh_threshold_for_the_two_crossing_class': str(F(120, 7 * 53)),
                 'violated_extension': 'applying the mesh corollary to edge losses'})

    # Five different integer ranks: the power-of-two constant does not transfer.
    q = polynomial_product(endpoint_polynomial(1, endpoint=3), [12, -17, 6])
    other_alphabet = profiles(q, rank_base=3)
    need(q == [36, -99, 98, -41, 6], 'base-three coefficients')
    need(other_alphabet['calls_per_profile'] == 140, 'base-three call count')
    need(other_alphabet['rank_mass_per_profile'] == 1404, 'base-three rank mass')
    # ln(9/8)<1/8; ln2<7/10; ln3>2*(1/2+(1/2)^3/3)=13/12.
    lhs_upper = F(140, 8) * F(7, 10)
    rhs_lower = 12 * F(13, 12)
    need(lhs_upper == F(49, 4) < rhs_lower == 13, 'base-three bound violation')
    other_alphabet.update({'roots': ['4/3', '3/2'],
                           'width': 'ln(9/8)/ln(3)',
                           'strict_upper_for_W_ln_root_ratio_ln2': str(lhs_upper),
                           'strict_lower_for_12_ln3': str(rhs_lower),
                           'violated_extension': 'transferring 12/ln2 to arbitrary five-rank alphabets'})
    return {'higher_degree': high_degree, 'edge_window': edge, 'other_alphabet': other_alphabet}


def independent_census(budget=1000):
    """Use shifted-root parameters a*y^2-t*y+k, y=x-1.

    This is a different enumeration from the proposed verifier's (a,-b,c)
    loops. Endpoint positivity and the interior vertex isolate both roots.
    """
    ceiling = budget // 3
    count = rational = 0
    digest = hashlib.sha256()
    minimum_calls = None
    best_objective, minimizers = None, []
    for a in range(1, (ceiling - 1) // 4 + 1):
        for t in range(1, 2 * a):
            kmin = max(1, t - a + 1)
            kmax = min((t * t - 1) // (4 * a), ceiling - 4 * a - 2 * t)
            for k in range(kmin, kmax + 1):
                b, c = -(2 * a + t), a + t + k
                delta = t * t - 4 * a * k
                need(delta > 0 and k > 0 and a - t + k > 0, 'shifted root conditions')
                q = polynomial_product(endpoint_polynomial(1), [c, b, a])
                cert = profiles(q)
                D, z = 4 * a + 2 * t + k, -b
                W, Z = 3 * D, (budget // 3 - 1) // 2
                need(cert['calls_per_profile'] == W <= budget, 'half-L1 normalization')
                need(all(q[j] * q[j + 1] < 0 for j in range(4)), 'coefficient alternation')
                need(D == 2 * z + k and k >= 1 and z > isqrt(delta), 'discrete identities')
                need(Z >= z > 1 and delta * Z * Z >= z * z, 'discrete root-ratio bound')
                need(F(2, z) >= F(12, budget - 3), 'continuous shifted-budget bound')
                count += 1
                rational += isqrt(delta) ** 2 == delta
                minimum_calls = W if minimum_calls is None else min(W, minimum_calls)
                objective = F(delta, z * z)
                item = {'a': a, 'b': b, 'c': c, 'calls_per_profile': W}
                if best_objective is None or objective < best_objective:
                    best_objective, minimizers = objective, [item]
                elif objective == best_objective:
                    minimizers.append(item)
                digest.update(f'{a},{b},{c}\n'.encode())
    return {'budget_per_profile': budget, 'quadratics': count,
            'rational_root_pairs': rational, 'irrational_root_pairs': count - rational,
            'minimum_calls_seen': minimum_calls,
            'minimum_Delta_over_trace_squared': str(best_objective),
            'all_minimizing_quadratics': minimizers,
            'shifted_enumeration_order_sha256': digest.hexdigest(),
            'discrete_and_shifted_continuous_bounds_checked': True}


def exact_attainment():
    results = []
    for h in (1, 2, 3, 8, 16, 32):
        S = 6 ** h // 2
        for n in (3, 4, 10, 100, 10 ** 4, 10 ** 9):
            a, b, c = n * (n - 1), -(2 * n * n - 1), n * (n + 1)
            q = polynomial_product(endpoint_polynomial(h), [c, b, a])
            q = [(-1) ** (h + 1) * x for x in q]
            cert = profiles(q)
            N = S * (4 * n * n - 1)
            Z = (N // S - 1) // 2
            need(cert['calls_per_profile'] == N, 'attainment call count')
            need(a + b + c == 1 and b * b - 4 * a * c == 1, 'attainment k or discriminant')
            need(Z == -b and Z > 1, 'attainment Z')
            ratio = F(n * n, n * n - 1)
            need(ratio == F(Z + 1, Z - 1), 'exact lower-bound attainment')
            need(F(1) < F(n + 1, n) < F(n, n - 1) < F(2), 'strict interior roots')
            results.append({'h': h, 'n': n, 'budget': N, 'Z': Z,
                            'exact_minimum_width': f'log2({ratio})'})
    return results


def main():
    receipt = {'status': 'pass', 'arithmetic': 'integer and Fraction only',
               'scope_counterexamples': exact_scope_examples(),
               'independent_census': independent_census(),
               'discrete_bound_attainment': exact_attainment(),
               'limits': ['finite corroboration, not proof assistant verification',
                          'independent implementation by another AI worker',
                          'does not establish physical supplier realizability']}
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
