#!/usr/bin/env python3
"""Sharp marked and actual-cost64 controls, independently built by conorholds.

Uses only the separate D8+ checker and its rational linear algebra.
Substantial OpenAI Codex assistance; Apache-2.0.
No candidate or predecessor implementation is imported. These finite fixtures
do not prove the marked theorem or global coverage of its actual consumer.
"""

from fractions import Fraction
from math import lcm


def run(geo, exact):
    model = geo.Checks("smoke", 8)
    p = model.pids
    position = {root: i for i, root in enumerate(p)}
    reports = {}

    def unit(root):
        return tuple(Fraction(root == i) for i in p)

    def code(normal):
        return tuple(Fraction(geo.dot(model.roots[i], normal), 4) for i in p)

    def evaluate(root):
        return tuple(Fraction(value, 4) for value in root)

    def pairing_cost(row, column):
        column_mask = geo.bits(i for i, value in zip(p, column) if value)
        return geo.binary_rank(model.rows[i] & column_mask
                               for i, value in zip(p, row) if value)

    def word_weight(word):
        return geo.binary_rank(model.labels[i] for i, value in zip(p, word) if value)

    def contains(word, label):
        support = [model.labels[i] for i, value in zip(p, word) if value]
        return geo.binary_rank(support + [label]) == geo.binary_rank(support)

    for t in (2, 3):
        private = tuple(range(t))
        private_mask = geo.bits(private)
        unmatched = tuple(i for i in range(8) if i not in private)
        groups = [[root for root in p if model.incidence[root] & private_mask == 1 << axis]
                  for axis in private]
        first, second = next((a, b) for a in groups[0] for b in groups[1]
                             if model.dots[a][b] != 0)
        selected = [first, second] + ([groups[2][0]] if t == 3 else [])
        low = [unit(root) for root in selected]
        reflected = []
        gammas = []
        low_xis = []
        for root, axis in zip(selected, private):
            original = model.roots[root]
            coefficient = geo.dot(original, model.frame[axis]) // 4
            reflection = tuple(a - coefficient * b for a, b in zip(original, model.frame[axis]))
            reflected_root = geo.projective(reflection)
            exact.need(reflected_root in model.index and reflected_root != original,
                       "reflected pivot is not a distinct canonical E8 root")
            gamma = Fraction(8, geo.dot(reflected_root, original))
            exact.need(gamma and geo.dot(reflected_root, reflected_root) == 8,
                       "reflection or gamma is degenerate")
            reflected.append(reflected_root)
            gammas.append(gamma)
            low_xis.append(tuple(gamma * value for value in evaluate(reflected_root)))

        normals = [model.roots[i] for i in selected] + [model.frame[i] for i in unmatched]
        dual = exact.inverse([[normal[i] for normal in normals] for i in range(8)])
        high = []
        for normal in normals:
            word = list(code(normal))
            for root, xi in zip(selected, low_xis):
                word[position[root]] -= sum(a * b for a, b in zip(xi, normal))
            high.append(tuple(word))
        words = low + high
        xis = low_xis + dual
        exact.need(exact.rank(words) == 8 + t and all(any(xi) for xi in xis),
                   "intrinsic basis or nonzero-dual condition fails")
        code_coordinates = [tuple(Fraction(model.roots[i][j], 4) for i in p)
                            for j in range(8)]
        exact.need(exact.rank(code_coordinates + low) == 8 + t,
                   "C intersect the unit correction space is nonzero")
        for coordinate, target in enumerate(code_coordinates):
            actual = tuple(sum(xi[coordinate] * word[i] for xi, word in zip(xis, words))
                           for i in range(112))
            exact.need(actual == target, "actual coefficient/code identity fails")

        # Directly verify the claimed sign-flip pattern, not just its weights.
        for index, normal in enumerate(normals):
            base = code(normal)
            for root in p:
                expected = base[position[root]]
                if index < t and root == selected[index]:
                    expected = 0
                elif root in selected:
                    expected = -expected
                exact.need(high[index][position[root]] == expected,
                           "root/frame high does not have the literal flip pattern")

        weights = list(map(word_weight, words))
        corrected = []
        for word, xi in zip(words, xis):
            matched = [axis for axis in range(8)
                       if exact.parallel(xi, evaluate(model.frame[axis])) is not None]
            exact.need(len(matched) <= 1, "ambiguous corrected frame")
            corrected.append(bool(matched and contains(word, model.z[matched[0]])))
        invoice = sum(weights) - sum(corrected)
        exact.need(weights == [1] * t + [8] * 8 and sum(corrected) == t and invoice == 64,
                   "sharp intrinsic invoice fails")

        pivot = model.index[reflected[0]]
        marked = 0
        coefficients = [Fraction(0)] * (8 + t)
        coefficients[0], coefficients[1] = gammas[0], gammas[1]
        g = tuple(sum(c * word[i] for c, word in zip(coefficients, words))
                  for i in range(112))
        ov = [root for root in p if root == pivot or model.dots[root][pivot] == 0]
        exact.need(len(ov) == 60 and all(g[position[root]] == 0 for root in ov),
                   "g does not vanish on O_v")
        exact.need(coefficients[marked] == gammas[0] != 0,
                   "marked coefficient vanishes")
        exact.need(exact.parallel(xis[marked], evaluate(reflected[0])) == gammas[0],
                   "marked restricted dual is not the required root functional")
        epsilon = int(contains(words[marked], model.labels[pivot]))
        exact.need(epsilon == 0, "distinct-root unit unexpectedly has epsilon one")
        equations = [[word[position[root]] for word in words] for root in ov]
        coordinate = [int(i == marked) for i in range(8 + t)]
        restriction_rank = exact.rank(equations)
        exact.need(exact.rank(equations + [coordinate]) > restriction_rank,
                   "rank criterion disagrees with the literal marked witness")

        projected = [tuple(sum(a * b for a, b in zip(xi, model.roots[root])) / 2
                           for root in p) for xi in xis]
        delta = unit(pivot)
        actual_rows = [delta] + [tuple(a - coefficient * b for a, b in zip(row, delta))
                                 for row, coefficient in zip(projected, coefficients)]
        actual_columns = [g] + words
        exact.need(actual_rows[1][position[pivot]] == 0,
                   "marked actual row did not lose the pivot coordinate")
        exact.need(all(any(row) for row in actual_rows) and all(any(col) for col in actual_columns),
                   "actual zero term")
        for family, label in ((actual_rows, "row"), (actual_columns, "column")):
            exact.need(all(exact.parallel(a, b) is None for a, b in geo.combinations(family, 2)),
                       "parallel actual " + label)
        exact.need(exact.rank(actual_rows) == 9 and exact.rank(actual_columns) == 8 + t,
                   "actual rank/slack conditions fail")

        denominator = 1
        for row in actual_rows:
            for value in row:
                denominator = lcm(denominator, value.denominator)
        integral_rows = [tuple(int(denominator * value) for value in row) for row in actual_rows]
        column_denominator = 1
        for column in actual_columns:
            for value in column:
                column_denominator = lcm(column_denominator, value.denominator)
        integral_columns = [tuple(int(column_denominator * value) for value in col)
                            for col in actual_columns]
        entries = 0
        for i, root in enumerate(p):
            for j, other in enumerate(p):
                actual = sum(row[i] * col[j] for row, col in zip(integral_rows, integral_columns))
                exact.need(8 * actual == denominator * column_denominator * model.dots[root][other],
                           "actual entrywise N0 factorization fails")
                entries += 1
        projected_costs = [pairing_cost(a, b) for a, b in zip(projected, words)]
        actual_costs = [pairing_cost(a, b) for a, b in zip(actual_rows, actual_columns)]
        exact.need(sum(projected_costs) == invoice == 64 and sum(actual_costs) == 64,
                   "direct projected or actual binary cost is not64")
        exact.need(actual_costs[0] == 0, "actual singleton pivot is not free")
        reports[f"t{t}"] = {
            "private_axes": private, "selected_root_indices": selected,
            "selected_roots": [model.roots[i] for i in selected],
            "reflected_roots": reflected, "gammas": [str(gamma) for gamma in gammas],
            "selected_first_pair_gram": Fraction(model.dots[first][second], 4).numerator,
            "invoice": invoice, "epsilon": epsilon, "invoice_minus_epsilon": invoice - epsilon,
            "marked_coefficient": str(coefficients[0]),
            "O_v_restriction_rank": restriction_rank,
            "literal_marked_witness": True, "projected_pair_costs": projected_costs,
            "actual_pair_costs": actual_costs, "actual_cost": sum(actual_costs),
            "actual_terms": len(actual_rows), "rank_P": 9, "rank_Q": 8 + t,
            "nonparallel_rows": True, "nonparallel_columns": True,
            "exact_N0_entries_checked": entries}
    return {"status": "pass", "author": "conorholds", "fixtures": reports,
            "boundary": "exact finite sharp controls; S_{<=7}=unit T uses standard support caps; no global decoder or frontier claim"}
