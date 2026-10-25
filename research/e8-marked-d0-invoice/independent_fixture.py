#!/usr/bin/env python3
"""Independent omitted-g and paid-pivot controls in doubled D8+ coordinates.

Prepared by conorholds. Imports only the separately implemented private D8+
checker. No candidate or predecessor implementation is imported. Exact
rational linear algebra and entrywise integer matrix products are used.
"""

from fractions import Fraction
from math import lcm


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def row_reduce(matrix, columns=None):
    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return rows, []
    width = len(rows[0]) if columns is None else columns
    pivots = []
    top = 0
    for column in range(width):
        pivot = next((i for i in range(top, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[top], rows[pivot] = rows[pivot], rows[top]
        divisor = rows[top][column]
        rows[top] = [value / divisor for value in rows[top]]
        for i in range(len(rows)):
            if i != top and rows[i][column]:
                multiplier = rows[i][column]
                rows[i] = [a - multiplier * b for a, b in zip(rows[i], rows[top])]
        pivots.append(column)
        top += 1
        if top == len(rows):
            break
    return rows, pivots


def rank(matrix):
    return len(row_reduce(matrix)[1])


def inverse(matrix):
    size = len(matrix)
    augmented = [list(row) + [int(i == j) for j in range(size)]
                 for i, row in enumerate(matrix)]
    reduced, pivots = row_reduce(augmented, size)
    need(pivots == list(range(size)), "normal matrix is singular")
    return [row[size:] for row in reduced]


def parallel(left, right):
    pivot = next((i for i, value in enumerate(right) if value), None)
    if pivot is None:
        return None
    ratio = Fraction(left[pivot], right[pivot])
    return ratio if ratio and all(a == ratio * b for a, b in zip(left, right)) else None


def run(geometry):
    model = geometry.Checks("smoke", 8)
    p = model.pids
    position = {root: i for i, root in enumerate(p)}

    def unit(root):
        return tuple(int(i == root) for i in p)

    def code(normal):
        return tuple(Fraction(geometry.dot(model.roots[i], normal), 4) for i in p)

    def evaluation(root):
        return tuple(Fraction(value, 4) for value in model.roots[root])

    def contains(word, label):
        support = [model.labels[i] for i, value in zip(p, word) if value]
        return geometry.binary_rank(support + [label]) == geometry.binary_rank(support)

    v = p[0]
    private = tuple(i for i in range(8) if model.incidence[v] >> i & 1)[:3]
    private_mask = geometry.bits(private)
    remaining = tuple(i for i in range(8) if i not in private)
    selected = [next(root for root in p
                     if model.incidence[root] & private_mask == 1 << axis
                     and model.dots[root][v] == 0)
                for axis in private]
    normals = [model.roots[i] for i in selected] + [model.frame[i] for i in remaining]
    dual = inverse([[normal[i] for normal in normals] for i in range(8)])
    low_xis = [tuple(2 * value for value in dual[i]) for i in range(3)]
    low = [unit(root) for root in selected]
    high = []
    for normal in normals:
        word = list(code(normal))
        for root, xi in zip(selected, low_xis):
            word[position[root]] -= sum(a * b for a, b in zip(xi, normal))
        need(all(value.denominator == 1 for value in word), "unexpected nonintegral column")
        high.append(tuple(int(value) for value in word))
    words = low + high
    xis = low_xis + dual
    need(all(any(xi) for xi in xis), "zero restricted dual")
    need(rank(words) == 11 and rank(low) == 3, "column or low-basis dependence")
    code_coordinates = [tuple(Fraction(model.roots[i][j], 4) for i in p)
                        for j in range(8)]
    need(rank(code_coordinates) == 8 and rank(code_coordinates + low) == 11,
         "C intersect T is not zero")
    for coordinate, target in enumerate(code_coordinates):
        actual = tuple(sum(xi[coordinate] * word[i] for xi, word in zip(xis, words))
                       for i in range(112))
        need(actual == target, "literal code/dual expansion fails")

    weights = [geometry.binary_rank(model.labels[i] for i, value in zip(p, word) if value)
               for word in words]
    corrected = []
    for word, xi in zip(words, xis):
        frame_matches = [j for j, root in enumerate(model.frame_ids)
                         if parallel(xi, evaluation(root)) is not None]
        need(len(frame_matches) <= 1, "a row matches more than one frame")
        corrected.append(bool(frame_matches and contains(word, model.z[frame_matches[0]])))
    invoice = sum(weights) - sum(corrected)
    need(invoice == 64, "omitted-g fixture invoice is not64")

    # Build actual row factors for N0=G/2 and check every one of its entries.
    row_factors = [tuple(sum(a * b for a, b in zip(xi, model.roots[root])) / 2
                         for root in p) for xi in xis]
    denominator = 1
    for row in row_factors:
        for value in row:
            denominator = lcm(denominator, value.denominator)
    integral_rows = [tuple(int(denominator * value) for value in row) for row in row_factors]
    entries = 0
    for i, root in enumerate(p):
        for j, other in enumerate(p):
            actual = sum(row[i] * word[j] for row, word in zip(integral_rows, words))
            need(8 * actual == denominator * model.dots[root][other],
                 "entrywise exact N0 factorization fails")
            entries += 1
    pair_costs = []
    for row, word in zip(row_factors, words):
        columns = geometry.bits(root for root, value in zip(p, word) if value)
        pair_costs.append(geometry.binary_rank(model.rows[root] & columns
                                              for root, value in zip(p, row) if value))
    need(sum(pair_costs) == invoice, "direct pairing costs disagree with the invoice")

    marked = next(k for k in range(3, 11) if parallel(xis[k], evaluation(v)) is not None)
    epsilon = int(contains(words[marked], model.labels[v]))
    ov = [root for root in p if root == v or model.dots[root][v] == 0]
    need(len(ov) == 60, "O_v size")
    equations = [[word[position[root]] for word in words] for root in ov]
    coordinate = [int(i == marked) for i in range(11)]
    restriction_rank = rank(equations)
    augmented_rank = rank(equations + [coordinate])
    witness_exists = augmented_rank > restriction_rank
    need(epsilon == 1 and restriction_rank == 11 and not witness_exists,
         "omitted-g fixture has a rebate or witness error")

    # Turn the omitted-g boundary into an exact paid-pivot sharp decoder.
    # Editing all three low rows separates their projected parallel pairs;
    # editing the marked high supplies its one-unit rebate. The pivot must
    # pay one because no word vanishing on O_v has this marked coefficient.
    gamma = parallel(xis[marked], evaluation(v))
    need(gamma is not None, "paid pivot mark is not a root functional")
    coefficients = [Fraction(1)] * 3 + [Fraction(0)] * 8
    coefficients[marked] = gamma
    pivot_word = tuple(sum(coefficient * word[i]
                           for coefficient, word in zip(coefficients, words))
                       for i in range(112))
    pivot_row = unit(v)
    paid_rows = [pivot_row] + [
        tuple(value - coefficient * delta for value, delta in zip(row, pivot_row))
        for row, coefficient in zip(row_factors, coefficients)
    ]
    paid_columns = [pivot_word] + words
    need(all(any(row) for row in paid_rows), "paid pivot has a zero actual row")
    need(all(any(word) for word in paid_columns), "paid pivot has a zero actual column")
    need(all(parallel(left, right) is None
             for left, right in geometry.combinations(paid_rows, 2)),
         "paid pivot has parallel actual rows")
    need(all(parallel(left, right) is None
             for left, right in geometry.combinations(paid_columns, 2)),
         "paid pivot has parallel actual columns")
    rank_p, rank_q = rank(paid_rows), rank(paid_columns)
    need(rank_p == 9 and rank_q == 11, "paid pivot factor ranks are not (9,11)")
    need(paid_rows[marked + 1][position[v]] == 0,
         "paid pivot marked actual row does not lose v")

    # Clear both independent rational denominators, then compare all N0
    # entries as integers. No support, invoice or rank proxy substitutes for
    # the literal factorization equations.
    paid_row_denominator = paid_column_denominator = 1
    for row in paid_rows:
        for value in row:
            paid_row_denominator = lcm(paid_row_denominator, Fraction(value).denominator)
    for word in paid_columns:
        for value in word:
            paid_column_denominator = lcm(paid_column_denominator, Fraction(value).denominator)
    paid_integral_rows = [tuple(int(paid_row_denominator * value) for value in row)
                          for row in paid_rows]
    paid_integral_columns = [tuple(int(paid_column_denominator * value) for value in word)
                             for word in paid_columns]
    paid_entries = 0
    for i, root in enumerate(p):
        for j, other in enumerate(p):
            actual = sum(row[i] * word[j]
                         for row, word in zip(paid_integral_rows, paid_integral_columns))
            need(8 * actual == (paid_row_denominator * paid_column_denominator
                                * model.dots[root][other]),
                 "paid pivot entrywise exact N0 factorization fails")
            paid_entries += 1

    paid_pair_costs = []
    for row, word in zip(paid_rows, paid_columns):
        columns = geometry.bits(root for root, value in zip(p, word) if value)
        paid_pair_costs.append(geometry.binary_rank(model.rows[root] & columns
                                                   for root, value in zip(p, row) if value))
    rebate_rows = [j for j, (before, after) in enumerate(zip(pair_costs, paid_pair_costs[1:]))
                   if after < before]
    marked_rebate = pair_costs[marked] - paid_pair_costs[marked + 1]
    need(paid_pair_costs[0] == 1, "paid pivot binary cost is not one")
    need(rebate_rows == [marked] and marked_rebate == 1,
         "paid pivot does not have exactly the marked one-unit rebate")
    need(sum(paid_pair_costs) == invoice == 64, "paid pivot actual cost is not sharp at64")
    paid_pivot_sharp = {
        "terms": len(paid_rows), "rank_P": rank_p, "rank_Q": rank_q,
        "nonzero_actual_rows_and_columns": True,
        "nonparallel_actual_rows": True, "nonparallel_actual_columns": True,
        "eta": [str(value) for value in coefficients], "marked_gamma": str(gamma),
        "pivot_cost": paid_pair_costs[0], "marked_rebate": marked_rebate,
        "rebate_rows": rebate_rows, "direct_pair_costs": paid_pair_costs,
        "invoice": invoice, "epsilon": epsilon, "actual_cost": sum(paid_pair_costs),
        "exact_N0_entries_checked": paid_entries,
    }

    # Independent necessary-condition test for the Sigma4 carrier3+unit
    # argument: the allegedly simultaneous two swaps would force the pattern
    # below, which is absent from every actual XOR carrier triple.
    pset = set(p)
    unit_obstruction_cases = 0
    for a, b in geometry.combinations(p, 2):
        for frame_index, z in enumerate(model.z):
            c = model.label_index.get(model.labels[a] ^ model.labels[b] ^ z)
            if c not in pset or c <= b:
                continue
            for unit_root, left, right in ((a, b, c), (b, a, c), (c, a, b)):
                forbidden = (geometry.dot(model.frame[frame_index], model.roots[left]) != 0
                             and geometry.dot(model.frame[frame_index], model.roots[right]) != 0
                             and model.dots[left][right] != 0
                             and model.dots[unit_root][left] == 0
                             and model.dots[unit_root][right] == 0)
                need(not forbidden, "carrier3+unit parity obstruction is false")
                unit_obstruction_cases += 1

    return {"status": "pass", "author": "conorholds", "coordinate_model": "explicit doubled D8+; Gram-row binary labels",
            "pivot_root_index": v, "pivot_root": model.roots[v],
            "private_frame_indices": private, "selected_root_indices": selected,
            "selected_roots": [model.roots[i] for i in selected],
            "marked_column_index": marked, "column_rank": 11,
            "C_intersect_unit_T_dimension": 0,
            "weights": weights, "corrected": corrected,
            "direct_pair_costs": pair_costs, "invoice": invoice, "epsilon": epsilon,
            "invoice_minus_epsilon": invoice - epsilon,
            "O_v_size": len(ov), "O_v_restriction_rank": restriction_rank,
            "restriction_nullity": 11 - restriction_rank,
            "marked_witness_exists": witness_exists, "exact_N0_entries_checked": entries,
            "carrier3_unit_necessary_patterns_checked": unit_obstruction_cases,
            "paid_pivot_sharp": paid_pivot_sharp,
            "limit": "parent unmarked fixture is not a two-sided counterexample; nested paid control is an exact actual decoder; low-weight-part identification uses geometric support caps"}
