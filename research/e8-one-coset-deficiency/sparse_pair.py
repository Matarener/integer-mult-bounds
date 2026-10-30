"""Independent finite sparse-pair controls, using dense binary COPY ranks.

Prepared by conorholds with substantial AI assistance. Apache-2.0.
No candidate modules or binary labels are imported. The F3 census is exhaustive;
the F5/F7 planted checks are controls, not exhaustive proofs over those fields.
The written argument supplies the extension to every odd characteristic.
The merge-proof variant was proposed and independently checked by the
Claude Fable 5.1 AI auditor; this is not human review.
"""
from collections import Counter
from itertools import combinations, product
import json


class VerificationError(ValueError):
    """An exact finite identity or semantic control failed."""


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def dot(left, right):
    return sum(x * y for x, y in zip(left, right))


def scalar_rank(rows, width, prime=3):
    basis = {}
    for initial in rows:
        row = [x % prime for x in initial]
        for pivot in range(width):
            if not row[pivot]:
                continue
            if pivot not in basis:
                scale = pow(row[pivot], -1, prime)
                basis[pivot] = [scale * x % prime for x in row]
                break
            factor = row[pivot]
            row = [(x - factor * y) % prime for x, y in zip(row, basis[pivot])]
    return len(basis)


def projective_key(column, prime):
    """Canonical scalar ray, computed without candidate matrix arithmetic."""
    pivot = next((x % prime for x in column if x % prime), None)
    if pivot is None:
        return None
    scale = pow(pivot, -1, prime)
    return tuple(scale * x % prime for x in column)


def pairwise_nonproportional(columns, prime):
    keys = [projective_key(column, prime) for column in columns]
    return all(key is not None for key in keys) and len(set(keys)) == len(keys)


def normalize_proportional(P, Q, prime):
    """Delete inactive terms and merge actual proportional factors on either side."""
    need(len(P) == len(Q), "normalizer factor lengths")
    terms = [(tuple(x % prime for x in p), tuple(x % prime for x in q))
             for p, q in zip(P, Q)]
    merges = zero_terms_removed = 0
    while True:
        active = [term for term in terms if all(any(column) for column in term)]
        zero_terms_removed += len(terms) - len(active)
        terms = active
        merged = False
        for side in (0, 1):
            seen = {}
            for index, term in enumerate(terms):
                key = projective_key(term[side], prime)
                if key not in seen:
                    seen[key] = index
                    continue
                previous = seen[key]
                pivot = next(i for i, x in enumerate(terms[previous][side]) if x)
                scale = term[side][pivot] * pow(terms[previous][side][pivot], -1, prime) % prime
                other = 1 - side
                combined = tuple((x + scale * y) % prime
                                 for x, y in zip(terms[previous][other], term[other]))
                replacement = list(terms[previous])
                replacement[other] = combined
                terms[previous] = tuple(replacement)
                del terms[index]
                merges += 1
                merged = True
                break
            if merged:
                break
        if not merged:
            return ([term[0] for term in terms], [term[1] for term in terms],
                    {"merges": merges, "zero_terms_removed": zero_terms_removed})


def build_model():
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, sign * 2
            roots.append(tuple(row))
    roots.extend((1,) + signs for signs in product((-1, 1), repeat=7)
                 if signs.count(-1) % 2 == 0)
    need(len(roots) == len(set(roots)) == 120, "root inventory")
    need(all(dot(root, root) == 8 for root in roots), "doubled root norms")
    table = tuple(sum(int(i == j or dot(r, s) == 0) << j
                      for j, s in enumerate(roots)) for i, r in enumerate(roots))
    return tuple(roots), table


def support_weight(support, table, stop_at_nine=True):
    basis = {}
    while support:
        low = support & -support
        support ^= low
        row = table[low.bit_length() - 1]
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
        if stop_at_nine and len(basis) == 9:
            return 9
    return len(basis)


def support_bits(column):
    return sum(int(x != 0) << i for i, x in enumerate(column))


def factor_copy_costs(P, Q, table):
    costs = []
    for p, q in zip(P, Q):
        reader_support = support_bits(q)
        costs.append(support_weight(support_bits(p), tuple(row & reader_support for row in table)))
    return costs


def check_factor_product(P, Q, roots, prime):
    need(len(P) == len(Q), "sharp product factor lengths")
    need(all(len(column) == len(roots) for column in P + Q), "sharp product column lengths")
    eighth = pow(8, -1, prime)
    for i, root in enumerate(roots):
        for j, other in enumerate(roots):
            need(sum(p[i] * q[j] for p, q in zip(P, Q)) % prime
                 == eighth * dot(root, other) % prime, "sharp entrywise N0 product")


def hole(root, coefficient, prime, factor=1):
    return tuple(-factor * coefficient * x * pow(8, -1, prime) % prime for x in root)


def expected_weight(h, s, t, roots, a, b, prime, nonorthogonal, hole_factor=1):
    if not any(h):
        return int(bool(s)) + int(bool(t))
    for coefficient, other, index in ((s, t, a), (t, s, b)):
        if coefficient and h == hole(roots[index], coefficient, prime, hole_factor):
            if not other or nonorthogonal:
                return 8
    return 9


def check_point(h, s, t, roots, table, a, b, prime, nonorthogonal, hole_factor=1):
    values = [(dot(root, h) + (s if i == a else t if i == b else 0)) % prime
              for i, root in enumerate(roots)]
    actual = support_weight(sum(int(x != 0) << i for i, x in enumerate(values)), table)
    expected = expected_weight(h, s, t, roots, a, b, prime, nonorthogonal, hole_factor)
    need(actual == expected, "actual support weight contradicts sparse-ray classification")
    return actual


def rejected(action):
    try:
        action()
    except VerificationError:
        return True
    return False


def inverse(matrix, prime):
    size = len(matrix)
    work = [[x % prime for x in row] + [int(i == j) for j in range(size)]
            for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next((i for i in range(column, size) if work[i][column]), None)
        need(pivot is not None, "sharp normal basis is singular")
        work[column], work[pivot] = work[pivot], work[column]
        scale = pow(work[column][column], -1, prime)
        work[column] = [scale * x % prime for x in work[column]]
        for i in range(size):
            if i != column and work[i][column]:
                factor = work[i][column]
                work[i] = [(x - factor * y) % prime for x, y in zip(work[i], work[column])]
    need(all(row[:size] == [int(i == j) for j in range(size)]
             for i, row in enumerate(work)), "sharp inverse identity")
    return [tuple(row[size:]) for row in work]


def sharp_fixture(roots, table, a, b, name, prime, merge_proof=False):
    """Check either the original collapsing control or the sheared sharp fixture."""
    half = pow(2, -1, prime)
    scalar_roots = [tuple(half * x % prime for x in root) for root in roots]
    normals = [scalar_roots[a], scalar_roots[b]]
    need(scalar_rank(normals, 8, prime) == 2, "sharp pair independence")
    for coordinate in range(8):
        axis = tuple(int(i == coordinate) for i in range(8))
        if scalar_rank(normals + [axis], 8, prime) > len(normals):
            normals.append(axis)
    need(len(normals) == 8, "sharp normal basis coverage")
    dual = inverse(list(zip(*normals)), prime)  # Rows of M^-1 are columns of M^-t.
    need(all(dot(h, d) % prime == int(i == j)
             for i, h in enumerate(normals) for j, d in enumerate(dual)), "sharp dot dual")

    def evaluate(normal):
        return tuple(dot(root, normal) % prime for root in scalar_roots)

    def unit(index):
        return tuple(int(i == index) for i in range(120))

    units = [unit(a), unit(b)]
    holes = [tuple((x - half * y) % prime for x, y in zip(unit_column, evaluate(normal)))
             for unit_column, normal in zip(units, normals[:2])]
    P = units + holes + [evaluate(h) for h in normals[2:]]
    readers = [evaluate(d) for d in dual]
    Q = readers[:2] + [tuple(-x % prime for x in q) for q in readers[:2]]
    Q += [tuple(half * x % prime for x in q) for q in readers[2:]]
    if merge_proof:
        for index in range(2):
            P[4 + index] = tuple((x + y) % prime for x, y in zip(P[4 + index], units[index]))
            Q[index] = tuple((x - half * y) % prime
                             for x, y in zip(readers[index], readers[2 + index]))
    need(all(any(column) for column in P + Q), "inactive sharp term")
    ranks = [scalar_rank(zip(*factor), len(factor), prime) for factor in (P, Q)]
    need(ranks == [10, 8], "sharp factor ranks")
    weights = [support_weight(support_bits(column), table) for column in P]
    need(weights == [1, 1, 8, 8] + [9] * 6, "sharp support weights")
    need(all(support_weight(support_bits(q), table) == 9 for q in Q), "sharp reader weights")
    costs = factor_copy_costs(P, Q, table)
    need(costs == weights and sum(costs) == 72, "sharp actual COPY ranks")
    check_factor_product(P, Q, roots, prime)
    nonproportional = [pairwise_nonproportional(factor, prime) for factor in (P, Q)]
    need(nonproportional == [True, merge_proof], "sharp proportionality control")

    clean_P, clean_Q, normalization = normalize_proportional(P, Q, prime)
    check_factor_product(clean_P, clean_Q, roots, prime)
    clean_ranks = [scalar_rank(zip(*factor), len(factor), prime) for factor in (clean_P, clean_Q)]
    clean_costs = factor_copy_costs(clean_P, clean_Q, table)
    clean_nonproportional = [pairwise_nonproportional(factor, prime) for factor in (clean_P, clean_Q)]
    need(normalization == {"merges": 0 if merge_proof else 2, "zero_terms_removed": 0},
         "sharp proportional normalization actions")
    need(len(clean_P) == (10 if merge_proof else 8), "sharp normalized term count")
    need(clean_ranks == ([10, 8] if merge_proof else [8, 8]), "sharp normalized ranks")
    need(clean_nonproportional == [True, True], "sharp normalization did not terminate")
    need(sum(clean_costs) == 72, "sharp normalization COPY control")
    if merge_proof:
        need((clean_P, clean_Q) == (P, Q), "merge-proof factorization was changed by normalization")
        uncompensated_Q = readers[:2] + Q[2:]
        need(rejected(lambda: check_factor_product(P, uncompensated_Q, roots, prime)),
             "omitted reader compensation mutation was accepted")
    normalization.update({"terms": len(clean_P), "factor_ranks": clean_ranks,
                          "pairwise_nonproportional": clean_nonproportional,
                          "term_copy_costs": clean_costs, "copy": sum(clean_costs),
                          "product_entries_checked": 14400})
    result = {"prime": prime, "pair_type": name, "indices": [a, b],
              "variant": "merge_proof" if merge_proof else "collapsing_positive_control",
              "factor_ranks": ranks, "all_terms_active": True,
              "pairwise_nonproportional": nonproportional,
              "term_copy_costs": costs, "copy": sum(costs), "product_entries_checked": 14400,
              "proportional_normalization": normalization}
    if merge_proof:
        result["omitted_reader_compensation_mutation_rejected"] = True
    return result


def run():
    """Return deterministic finite coverage, classification, and control results."""
    roots, table = build_model()
    need(support_weight((1 << 120) - 1, table, False) == 9, "dense COPY rank")
    a = 0
    orthogonal = next(i for i in range(1, 120) if dot(roots[a], roots[i]) == 0)
    nonorthogonal = next(i for i in range(1, 120) if dot(roots[a], roots[i]) != 0)
    cases = [(orthogonal, "orthogonal", False), (nonorthogonal, "nonorthogonal", True)]
    code = []
    for h in product(range(3), repeat=8):
        first = next((x for x in h if x), 0)
        if first == 2:
            continue
        values = tuple(dot(root, h) % 3 for root in roots)
        bits = sum(int(x != 0) << i for i, x in enumerate(values))
        need(support_weight(bits, table) == (9 if first else 0), "codeword support weight")
        code.append((h, first, values, bits))
    need(len(code) == 3281, "projective scalar-code coverage")
    census, planted, fixtures, merge_proof_fixtures = [], [], [], []
    for b, name, nonorth in cases:
        need(scalar_rank([root + (int(i == a), int(i == b))
                          for i, root in enumerate(roots)], 10) == 10, "extension rank")
        H = [roots[a] + (0, 0), roots[b] + (0, 0),
             (0,) * 8 + (1, 0), (0,) * 8 + (0, 1)]
        need(scalar_rank(H, 10) == 4, "four-dimensional low-weight container")
        low_weight, histogram, pure = [], Counter(), 0
        for h, first, values, initial in code:
            cache = {}
            for s, t in product(range(3), repeat=2):
                if not first and next((x for x in (s, t) if x), 0) != 1:
                    continue
                support = initial
                for index, value in ((a, s), (b, t)):
                    if bool(values[index]) != bool((values[index] + value) % 3):
                        support ^= 1 << index
                if support not in cache:
                    cache[support] = support_weight(support, table)
                w = cache[support]
                need(w > 0, "nonzero projective vector collapsed")
                need(w == expected_weight(h, s, t, roots, a, b, 3, nonorth),
                     "exhaustive F3 sparse-ray classification")
                histogram[w] += 1
                if w <= 7:
                    need(not any(h), "weight at most seven outside pure external plane")
                    pure += 1
                if w <= 8:
                    vector = h + (s, t)
                    need(scalar_rank(H + [vector], 10) == 4,
                         "weight at most eight outside H")
                    low_weight.append((w, vector))
        count = sum(histogram.values())
        need(count == 29524, "complete F3 projective extension coverage")
        prefix = [scalar_rank([v for w, v in low_weight if w <= k], 10) for k in range(9)]
        need(prefix == [0, 2, 2, 2, 2, 2, 2, 2, 4], "weight-filter rank profile")
        minimum = sum(10 - rank for rank in prefix)
        need(minimum == 72, "F3 minimum basis weight")
        census.append({"pair_type": name, "indices": [a, b], "projective_points": count,
                       "weight_histogram": {str(k): v for k, v in sorted(histogram.items())},
                       "prefix_ranks_0_to_8": prefix, "minimum_basis_weight": minimum,
                       "weight_le7_pure_external_rays": pure,
                       "weight_le8_rays_in_H": len(low_weight),
                       "classified_projective_rays": count})
        for prime in (5, 7):
            pair_vectors = singleton_vectors = 0
            for s, t in product(range(1, prime), repeat=2):
                normals = ((0,) * 8, hole(roots[a], s, prime), hole(roots[b], t, prime))
                weights = [check_point(h, s, t, roots, table, a, b, prime, nonorth)
                           for h in normals]
                need(weights == ([2, 8, 8] if nonorth else [2, 9, 9]),
                     "planted two-coset deficiencies")
                pair_vectors += 3
            for index in (a, b):
                for coefficient in range(1, prime):
                    s, t = (coefficient, 0) if index == a else (0, coefficient)
                    weights = [check_point(h, s, t, roots, table, a, b, prime, nonorth)
                               for h in ((0,) * 8, hole(roots[index], coefficient, prime))]
                    need(weights == [1, 8], "planted singleton deficiencies")
                    singleton_vectors += 2
            planted.append({"prime": prime, "pair_type": name,
                            "nonzero_coefficient_pairs": (prime - 1) ** 2,
                            "two_coset_vectors_checked": pair_vectors,
                            "singleton_vectors_checked": singleton_vectors})
        fixtures.extend(sharp_fixture(roots, table, a, b, name, prime) for prime in (3, 5, 7))
        merge_proof_fixtures.extend(sharp_fixture(roots, table, a, b, name, prime, merge_proof=True)
                                    for prime in (3, 5, 7))
    correct_hole = hole(roots[a], 1, 3)
    controls = {
        "wrong_nonorthogonal_branch_rejected": rejected(lambda: check_point(
            correct_hole, 1, 1, roots, table, a, nonorthogonal, 3, False)),
        "wrong_orthogonal_branch_rejected": rejected(lambda: check_point(
            correct_hole, 1, 1, roots, table, a, orthogonal, 3, True)),
        "wrong_hole_factor_two_rejected": rejected(lambda: check_point(
            hole(roots[a], 1, 3, 2), 1, 0, roots, table, a, nonorthogonal, 3, True, 2)),
    }
    need(all(controls.values()), "semantic mutation control was accepted")
    return {"status": "PASS_SPARSE_PAIR_FINITE_CONTROLS", "root_lines": 120,
            "binary_copy_rank": 9, "code_projective_points": 3280,
            "f3_cases": census, "planted_field_checks": planted,
            "sharp_fixtures": fixtures, "merge_proof_sharp_fixtures": merge_proof_fixtures,
            "controls": controls}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
