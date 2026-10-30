"""Independent exact E8 fixture checks, prepared by conorholds with Codex.

Apache-2.0. No candidate implementation, certificate or float rank is imported.
Root ordering/labels are the declared A8 pair-then-triple ordering of PR3755,
head 9ab51a1a90da57a55d1ef75f20ecd4b2705b3f52. The standard-coordinate
realization below is derived directly from an eight-root Gram star.
"""

from fractions import Fraction
from itertools import combinations, product
from math import lcm
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(x, y):
    require(len(x) == len(y), "dot dimensions")
    return sum(a * b for a, b in zip(x, y))


def binary_rank(values):
    pivots = {}
    for value in values:
        require(type(value) is int and value >= 0, "binary input")
        while value:
            bit = value & -value
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def root_model():
    # Star s_1,...,s_8 has Gram I+J in norm-two coordinates.
    # If x in Q^9 has sum zero, r=sum_{i<9} x_i s_i is an isometry.
    # For triples x=1_T-(1/3)1, sum(2s_i)/3=(5,1,...,1).
    star = [tuple(2 * int(j in (0, i)) for j in range(8))
            for i in range(1, 8)] + [(1,) * 8, (0,) * 8]
    rows, labels = [], []
    for i, j in combinations(range(9), 2):
        rows.append(tuple(a - b for a, b in zip(star[i], star[j])))
        labels.append(511 ^ (1 << i) ^ (1 << j))
    for triple in combinations(range(9), 3):
        rows.append(tuple(sum(star[i][j] for i in triple) - (5 if j == 0 else 1)
                          for j in range(8)))
        labels.append(sum(1 << i for i in triple))
    return tuple(rows), tuple(labels)


class Field:
    def __init__(self, prime=0):
        require(prime in (0, 3, 5, 7), "supported field")
        self.prime = prime

    def scalar(self, value):
        q = Fraction(value)
        return (q.numerator * pow(q.denominator, -1, self.prime) % self.prime
                if self.prime else q)

    def clean(self, value):
        return value % self.prime if self.prime else value

    def inverse(self, value):
        return pow(value, -1, self.prime) if self.prime else 1 / value

    def combine(self, *terms):
        require(bool(terms) and len({len(v) for _, v in terms}) == 1, "vector dimensions")
        terms = [(self.scalar(c), v) for c, v in terms]
        return tuple(self.clean(sum(c * v[i] for c, v in terms))
                     for i in range(len(terms[0][1])))

    def rank(self, vectors):
        basis = {}
        for vector in vectors:
            work = [self.scalar(x) for x in vector]
            for pivot, old in sorted(basis.items()):
                coefficient = work[pivot]
                if coefficient:
                    work = [self.clean(x - coefficient * y) for x, y in zip(work, old)]
            pivot = next((i for i, value in enumerate(work) if value), None)
            if pivot is not None:
                inverse = self.inverse(work[pivot])
                basis[pivot] = [self.clean(x * inverse) for x in work]
        return len(basis)

    def ray(self, vector):
        pivot = next((x for x in vector if x), None)
        if pivot is None:
            return None
        inverse = self.inverse(pivot)
        return tuple(self.clean(x * inverse) for x in vector)


def standard_inventory():
    def positive(row):
        return row if next(x for x in row if x) > 0 else tuple(-x for x in row)
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            roots.add(tuple(2 if t == i else 2 * sign if t == j else 0 for t in range(8)))
    roots.update(row for row in product((-1, 1), repeat=8)
                 if row[0] == 1 and sum(x < 0 for x in row) % 2 == 0)
    return {positive(row) for row in roots}


def check_model(rows, labels):
    require(len(set(rows)) == len(set(labels)) == 120, "model inventory")
    positive = lambda row: row if next(x for x in row if x) > 0 else tuple(-x for x in row)
    require({positive(row) for row in rows} == standard_inventory(), "standard E8 binding")
    require(binary_rank(labels) == 9, "full binary label span")
    for i, row in enumerate(rows):
        require(dot(row, row) == 8, "norm-two root")
        for j, other in enumerate(rows):
            gram = dot(row, other)
            require(gram % 4 == 0, "integral norm-two Gram")
            beta = (labels[i] & labels[j]).bit_count() % 2
            require(beta == (1 + gram // 4) % 2 == int(i == j or gram == 0),
                    "dense binary pairing / Gram")
    require(Field().rank(rows) == 8, "scalar root span")


def support_weight(vector, labels):
    return binary_rank(label for x, label in zip(vector, labels) if x)


def term_cost(left, right, labels):
    supported = [label for x, label in zip(right, labels) if x]
    return binary_rank(sum(((label & other).bit_count() % 2) << j
                           for j, other in enumerate(supported))
                       for x, label in zip(left, labels) if x)


def product_equal(left, right, rows, field):
    require(len(left) == len(right), "term counts")
    if field.prime:
        denominator, target_scale = 1, field.scalar(Fraction(1, 8))
        p, q = left, right
    else:
        denominator = lcm(*(Fraction(x).denominator for v in left + right for x in v))
        p = [tuple(int(x * denominator) for x in v) for v in left]
        q = [tuple(int(x * denominator) for x in v) for v in right]
        target_scale = Fraction(denominator * denominator, 8)
    return all(field.clean(sum(p[t][i] * q[t][j] for t in range(len(p))))
               == field.clean(target_scale * dot(rows[i], rows[j]))
               for i in range(120) for j in range(120))


def frame_data(rows, field):
    # Choose the usual D8 orthogonal frame, retaining the model's orientation.
    indices = []
    for a in range(0, 8, 2):
        for sign in (-1, 1):
            target = tuple(2 if j == a else 2 * sign if j == a + 1 else 0
                           for j in range(8))
            indices.append(next(i for i, row in enumerate(rows)
                                if row == target or row == tuple(-x for x in target)))
    require(all(dot(rows[i], rows[j]) == 8 * int(i == j) for i in indices for j in indices),
            "orthogonal frame")
    code = [tuple(field.scalar(Fraction(dot(row, rows[i]), 4)) for row in rows)
            for i in indices]
    units = [tuple(field.scalar(int(j == i)) for j in range(120)) for i in indices]
    return indices, code, units


def extension_fixture(k, code, units, field):
    require(1 <= k <= 8, "extension size")
    e, d, f = code, units, field
    r = f.combine((1, e[0]), (-4, d[0]))
    h = f.combine((1, e[0]), (-2, d[0]))
    left = [h] + [f.combine((Fraction(1, 2), e[i]), (Fraction(-1, 4), r))
                  for i in range(1, k)] + [f.combine((Fraction(1, 4), r))]
    right = d[:k] + [f.combine((1, r), *((1, d[i]) for i in range(1, k)))]
    left += [f.combine((Fraction(-1, 2), e[i])) for i in range(1, k)]
    right += [f.combine((1, d[i]), (Fraction(-1, 2), e[i])) for i in range(1, k)]
    left += [f.combine((Fraction(1, 4), e[i])) for i in range(k, 8)] + [d[0]]
    right += e[k:] + [h]
    return left, right


def eleven_fixture(code, units, field):
    e, d, f = code, units, field
    left = [f.combine((1, e[0]), (-2, d[0])),
            f.combine((Fraction(1, 2), e[1]), (Fraction(-1, 4), e[2])),
            f.combine((Fraction(1, 4), e[0]), (-1, d[0])),
            f.combine((Fraction(-1, 2), e[1])),
            f.combine((Fraction(1, 4), e[2]))]
    right = [d[0], d[1], f.combine((1, e[0]), (-4, d[0])),
             f.combine((1, d[1]), (Fraction(-1, 2), e[1])),
             f.combine((1, e[2]), (1, d[1]))]
    left += [f.combine((Fraction(1, 4), x)) for x in e[3:]] + [d[0]]
    right += e[3:] + [f.combine((1, e[0]), (-2, d[0]))]
    return left, right


def normalized(left, right, field):
    return (all(any(v) for v in left + right)
            and len({field.ray(v) for v in left}) == len(left)
            and len({field.ray(v) for v in right}) == len(right))


def merge(left, right, field):
    """Independent alternating ray aggregation; nonzero zero-cost atoms stay."""
    left, right = list(left), list(right)
    while True:
        previous = len(left)
        for side in range(2):
            groups = {}
            for p, q in zip(left, right):
                if not any(p) or not any(q):
                    continue
                key = field.ray(p)
                scalar = next(x for x in p if x)
                contribution = field.combine((scalar, q))
                groups[key] = (field.combine((1, groups[key]), (1, contribution))
                               if key in groups else contribution)
            surviving = [(p, q) for p, q in groups.items() if any(q)]
            if not surviving:
                return [], []
            left, right = [list(x) for x in zip(*surviving)]
            left, right = right, left
        if len(left) == previous:
            return left, right


def check_fixture(left, right, k, rows, labels, code, units, field):
    require(product_equal(left, right, rows, field), "exact all-pairs product")
    require(normalized(left, right, field), "active pairwise nonproportional factors")
    require((field.rank(left), field.rank(right)) == (9, 8 + k), "actual ranks")
    require(field.rank(left + code + units[:1]) == 9, "singleton containment")
    require(field.rank(right + code + units[:k]) == 8 + k, "actual full coordinate Q")
    costs = [term_cost(p, q, labels) for p, q in zip(left, right)]
    require(sum(costs) == 72, "linear COPY equality")
    require(sum(c == 0 for c in costs) == 2, "two active zero-cost atoms")
    for p, q, cost in zip(left, right, costs):
        require(cost <= min(support_weight(p, labels), support_weight(q, labels)),
                "pairing rank bound")
    merged_p, merged_q = merge(left, right, field)
    require(len(merged_p) == len(left) and product_equal(merged_p, merged_q, rows, field),
            "normalizer stability")
    return costs


def check_controls(rows, labels, code, units, field):
    f = field
    left, right = eleven_fixture(code, units, f)
    require(not product_equal(left[1:], right[1:], rows, f), "deleted nonzero free atom")
    broken = list(left)
    broken[1] = f.combine((Fraction(1, 2), code[1]))
    require(not product_equal(broken, right, rows, f), "omitted shear compensation")
    require(not product_equal([f.combine((2, p)) for p in left], right, rows, f),
            "wrong target scaling")
    ordinary_p = [f.combine((Fraction(1, 4), x)) for x in code]
    ordinary_q = list(code)
    a = next(i for i, x in enumerate(units[0]) if x)
    b = next(i for i, row in enumerate(rows) if i != a and dot(row, rows[a]) != 0)
    delta_b = tuple(f.scalar(int(i == b)) for i in range(120))
    h = f.combine((1, code[0]), (-2, units[0]))
    padded_p = ordinary_p + [units[0], f.combine((-1, units[0]))] * 2
    padded_q = ordinary_q + [h, h, delta_b, delta_b]
    require(product_equal(padded_p, padded_q, rows, f), "raw cancellation product")
    require((f.rank(padded_p), f.rank(padded_q)) == (9, 10), "raw padding ranks")
    require(f.rank(padded_q + code + [units[0], delta_b]) == 10, "raw full pair space")
    require(all(any(v) for v in padded_p + padded_q), "padding atoms really nonzero")
    require([term_cost(p, q, labels) for p, q in zip(padded_p, padded_q)] == [9] * 8 + [0] * 4,
            "padding charges")
    require(not normalized(padded_p, padded_q, f), "padding rejected by normalization")
    mp, mq = merge(padded_p, padded_q, f)
    require((len(mp), f.rank(mp), f.rank(mq)) == (8, 8, 8), "padding rank drop")
    require(product_equal(mp, mq, rows, f), "padding merge exactness")
    one_p, one_q = extension_fixture(1, code, units, f)
    require(f.rank(one_q + code + units[:2]) == 10 and f.rank(one_q) == 9,
            "ambient inclusion is not actual full Q")
    require(sorted(term_cost(p, q, labels) for p, q in zip(one_p, one_q)) == [0, 0] + [9] * 8,
            "ambient-only concave equality countercontrol")
    zero = (f.scalar(0),) * 120
    inactive_p = ordinary_p + [zero, zero, units[0]]
    inactive_q = ordinary_q + [units[0], units[1], zero]
    require(product_equal(inactive_p, inactive_q, rows, f), "inactive padding product")
    require((f.rank(inactive_p), f.rank(inactive_q)) == (9, 10), "inactive padding raw ranks")
    require(not normalized(inactive_p, inactive_q, f), "inactive atoms rejected")
    return {"raw_padding_ranks": [9, 10], "merged_padding_ranks": [8, 8],
            "raw_padding_charges": [9] * 8 + [0] * 4,
            "ambient_only_actual_ranks": [9, 9], "failure_controls": 6}


def verify():
    rows, labels = root_model()
    check_model(rows, labels)
    result = {"root_lines": 120, "gram_pairing_checks": 14400, "fields": {}}
    for prime in (0, 3, 5, 7):
        f = Field(prime)
        indices, code, units = frame_data(rows, f)
        require(f.rank(code) == 8, "code dimension in field")
        fixtures = []
        for k in range(1, 9):
            p, q = extension_fixture(k, code, units, f)
            costs = check_fixture(p, q, k, rows, labels, code, units, f)
            expected = [0, 0] + [1] * (k - 1) + [8] * (k - 1) + [9] * (9 - k)
            require(sorted(costs) == sorted(expected), "k-family exact charge profile")
            fixtures.append({"k": k, "terms": len(p), "ranks": [9, 8 + k], "costs": costs})
        p, q = eleven_fixture(code, units, f)
        sharp = check_fixture(p, q, 2, rows, labels, code, units, f)
        require(sorted(sharp) == [0, 0, 1, 8] + [9] * 7, "sharp concave profile")
        result["fields"][str(prime) if prime else "Q"] = {
            "frame_coordinates": indices, "extension_family": fixtures,
            "eleven_term_sharp_costs": sharp,
            "controls": check_controls(rows, labels, code, units, f)}
    return result


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
