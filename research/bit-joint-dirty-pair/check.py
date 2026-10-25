#!/usr/bin/env python3
"""Finite controls for the written joint-dirty query bound; not a proof kernel.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance.
Only Python's standard library is used; normal execution writes no files.
"""
from fractions import Fraction
from itertools import permutations, product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def multiply(a, b):
    """Rows of a encode coefficients selecting whole rows of b."""
    out = []
    for row in a:
        value = 0
        for j, selected in enumerate(b):
            if row >> j & 1:
                value ^= selected
        out.append(value)
    return tuple(out)


def defect_controls():
    results = []
    for prime, half_dimension in ((3, 1), (3, 2), (3, 3), (5, 2)):
        dimension = 2 * half_dimension
        addresses = list(product(range(prime), repeat=dimension))
        index = {v: i for i, v in enumerate(addresses)}
        size = len(addresses)
        for rank in range(half_dimension + 1):
            action = []
            for point in addresses:
                moved = list(point)
                for i in range(rank):
                    moved[i], moved[half_dimension+i] = moved[half_dimension+i], moved[i]
                action.append(index[tuple(moved)])
            require(all(action[action[i]] == i for i in range(size)), 'involution')
            fixed = sum(i == j for i, j in enumerate(action))
            # The independently eliminated Boolean matrix is I + permutation.
            measured = binary_rank((1 << i) ^ (1 << j) for i, j in enumerate(action))
            predicted_fixed = prime ** (dimension-rank)
            predicted_defect = (size-predicted_fixed)//2
            require(fixed == predicted_fixed and measured == predicted_defect,
                    'actual permutation defect formula')
            results.append({'prime': prime, 'address_dimension': dimension,
                            'query_rank': rank, 'fixed_addresses': fixed,
                            'boolean_defect_rank': measured})
    # With one rank-one query and any second rank, the upper bound remains
    # strictly below the two-rank-two target. The written proof covers all q>2.
    gaps = {str(q): str(Fraction(q-2, 2*q*q)) for q in (3, 5, 7, 11)}
    require(all(Fraction(v) > 0 for v in gaps.values()), 'strict two-call gap')
    require(Fraction(2-2, 2*2*2) == 0, 'characteristic-two boundary control')
    return {'actual_permutation_cases': results,
            'normalized_target_minus_relaxed_rank1_plus_any_rank': gaps,
            'even_address_characteristic_does_not_have_strict_gap': True}


def sylvester_controls():
    # All U in M_3(F2) and VJ in M_(3,2)(F2). This finite check corroborates
    # the written all-dimension inequality; it does not supply its quantifier.
    cases = 0
    both_ranks_at_least_two = 0
    zero_products = 0
    for u in product(range(8), repeat=3):
        rank_u = binary_rank(u)
        for v in product(range(4), repeat=3):
            cases += 1
            rank_v = binary_rank(v)
            rank_uv = binary_rank(multiply(u, v))
            require(rank_uv >= rank_u+rank_v-3, 'Sylvester inequality')
            if rank_u >= 2 and rank_v >= 2:
                both_ranks_at_least_two += 1
                zero_products += rank_uv == 0
    require(cases == 32768 and zero_products == 0, 'three-column obstruction')
    # Four odd calls are allowed by this quotient: two duplicate columns/rows
    # give UV=0 with both ranks two. The invariant must not reject this case.
    u4 = (0b0101, 0b1010)
    v4 = (0b01, 0b10, 0b01, 0b10)
    require(binary_rank(u4) == binary_rank(v4) == 2 and multiply(u4, v4) == (0, 0),
            'four-column boundary positive control')
    # A single required target direction does not force both ranks to be two.
    u2, v2 = (0b11,), (1, 1)
    require(binary_rank(u2) == binary_rank(v2) == 1 and multiply(u2, v2) == (0,),
            'one-output boundary positive control')
    return {'complete_matrix_pairs': cases,
            'pairs_with_both_ranks_at_least_two': both_ranks_at_least_two,
            'zero_products_in_that_class': zero_products,
            'four_columns_allow_zero_product_with_two_directions': True,
            'one_direction_allows_two_columns': True}


def representation_controls():
    # A concrete reason a single finite address field cannot simply be called
    # a faithful group-algebra model. S4 permutes four coordinates over F3.
    # Every point has a repeated coordinate; its stabilizer has even order.
    # Thus the sum of all 24 formal group elements is a nonzero formal vector
    # whose Boolean permutation operator vanishes on all 81 addresses.
    group = list(permutations(range(4)))
    zero_columns = 0
    for point in product(range(3), repeat=4):
        odd_images = set()
        for permutation in group:
            image = tuple(point[i] for i in permutation)
            if image in odd_images:
                odd_images.remove(image)
            else:
                odd_images.add(image)
        zero_columns += not odd_images
    require(len(group) == 24 and zero_columns == 81, 'fixed-field algebra kernel')
    generic = (0, 1, 2, 3)
    images = {tuple(generic[i] for i in permutation) for permutation in group}
    require(len(images) == 24, 'generic point separates all labels over F5')
    return {'formal_support_size': 24, 'F3_addresses_with_zero_operator_column': zero_columns,
            'F5_generic_point': list(generic), 'distinct_images_at_F5_point': len(images),
            'scope': 'S4 coordinate-permutation example; not a counterexample to the uniform-prime bridge'}


def main():
    result = {'status': 'PASS_FINITE_JOINT_QUERY_CONTROLS',
              'defect_rank': defect_controls(),
              'odd_call_rank_obstruction': sylvester_controls(),
              'uniformity_control': representation_controls(),
              'written_tariff_reduction': {
                  'x': '2^(1-b), with 1 <= x <= 2 for 0 <= b <= 1',
                  'zero_or_one_queries': 'impossible by actual-action defect rank',
                  'two_queries': 'each rank >= 2; cost >= 2*x',
                  'three_queries': 'not all rank one; cost >= 2+x >= 2*x',
                  'four_or_more_queries': 'cost >= 4 >= 2*x',
                  'attainment': 'the original separate rank-two queries'},
              'no_new_kappa': True,
              'limits': ['finite controls do not prove the all-parameter theorem',
                         'the uniform-prime bridge is a written proof',
                         'no changed consumer or native execution is verified']}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
