"""Exact A8 model and small witnesses for the one-coset theorem.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The model/deficiency setup credits PR1224 and PR1248; no source code is imported.
Normal functions are pure and never read or write files.
"""

from fractions import Fraction
from itertools import combinations, product


OMEGA = 511
MODEL = "Standard E8 roots scaled by 2; A8 label order"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() % 2


def dot(left, right):
    require(len(left) == len(right), "dot-product dimensions differ")
    return sum(x * y for x, y in zip(left, right))


def binary_rank(values):
    pivots = {}
    for initial in values:
        value = initial
        require(type(value) is int and value >= 0, "binary vector is not a nonnegative integer")
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def rational_rank(rows):
    """Forward Gaussian elimination over Q; not a modular deficiency test."""
    if not rows:
        return 0
    width = len(rows[0])
    require(all(len(row) == width for row in rows), "ragged rational matrix")
    work = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for column in range(width):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for i in range(rank + 1, len(work)):
            if work[i][column]:
                factor = work[i][column] / work[rank][column]
                for j in range(column, width):
                    work[i][j] -= factor * work[rank][j]
        rank += 1
        if rank == len(work):
            break
    return rank


def determinant(rows):
    """Bareiss determinant with exact divisions and explicit row swaps."""
    n = len(rows)
    require(all(len(row) == n for row in rows), "determinant matrix is not square")
    if not n:
        return 1
    work = [list(row) for row in rows]
    previous, sign = 1, 1
    for column in range(n - 1):
        pivot = next((i for i in range(column, n) if work[i][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign = -sign
        value = work[column][column]
        for i in range(column + 1, n):
            for j in range(column + 1, n):
                numerator = value * work[i][j] - work[i][column] * work[column][j]
                require(numerator % previous == 0, "nonexact Bareiss division")
                work[i][j] = numerator // previous
            work[i][column] = 0
        previous = value
    return sign * work[-1][-1]


def build_model():
    roots, labels = [], []
    for i, j in combinations(range(9), 2):
        row = [0] * 9
        row[i], row[j] = 3, -3
        roots.append(tuple(row))
        labels.append(OMEGA ^ (1 << i) ^ (1 << j))
    for subset in combinations(range(9), 3):
        roots.append(tuple(2 if i in subset else -1 for i in range(9)))
        labels.append(sum(1 << i for i in subset))
    require(len(roots) == len(set(roots)) == len(set(labels)) == 120, "A8 root inventory")
    require(binary_rank(labels) == 9, "binary label span is not nine")
    require(all(sum(row) == 0 and dot(row, row) == 18 for row in roots), "A8 root norm")
    for i, row in enumerate(roots):
        for j, other in enumerate(roots):
            value = dot(row, other)
            require(value % 9 == 0, "root Gram entry is not integral after rescaling")
            require(parity(labels[i] & labels[j]) == (1 + value // 9) % 2,
                    "label/Gram identity")
            require(parity(labels[i] & labels[j]) == int(i == j or value == 0),
                    "labels do not represent canonical dense COPY pairing")
    return {"roots": tuple(roots), "labels": tuple(labels)}


def standard_roots():
    """Standard E8 representatives, with scalar coordinates multiplied by two."""
    result = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            result.append(tuple(row))
    result += [row for row in product((-1, 1), repeat=8)
               if row[0] == 1 and sum(x < 0 for x in row) % 2 == 0]
    require(len(result) == len(set(result)) == 120, "standard root inventory")
    return tuple(result)


def canonical(row):
    return tuple(row) if next(x for x in row if x) > 0 else tuple(-x for x in row)


def standard_binding(model):
    """Rational star isometry; return standard roots in oriented A8 row order."""
    star = []
    for j in range(1, 8):
        row = [0] * 8
        row[0] = row[j] = 2
        star.append(tuple(row))
    star.append((1,) * 8)
    require(all(dot(x, y) == 4 * (1 + int(i == j))
                for i, x in enumerate(star) for j, y in enumerate(star)), "star Gram matrix")
    lookup = {canonical(row): i for i, row in enumerate(model["roots"])}
    oriented = [None] * 120
    for root in standard_roots():
        raw = [dot(root, other) for other in star]
        require(all(value % 4 == 0 for value in raw), "nonintegral star pairing")
        inner = [value // 4 for value in raw]
        total = sum(inner)
        require(total % 3 == 0, "nonintegral A8 image")
        image = tuple(3 * value - total // 3 for value in inner) + (-total // 3,)
        require(canonical(image) in lookup, "standard root missing from A8 alphabet")
        index = lookup[canonical(image)]
        sign = 1 if image == model["roots"][index] else -1
        require(oriented[index] is None, "standard/A8 line map not injective")
        oriented[index] = tuple(sign * value for value in root)
    require(all(row is not None for row in oriented), "standard/A8 line map not onto")
    for i, row in enumerate(oriented):
        for j, other in enumerate(oriented):
            require(9 * dot(row, other) == 4 * dot(model["roots"][i], model["roots"][j]),
                    "standard/A8 isometry scaling")
    return tuple(oriented)


def pair_profiles():
    for n00 in range(10):
        for n01 in range(10 - n00):
            for n10 in range(10 - n00 - n01):
                n11 = 9 - n00 - n01 - n10
                a = ((1 << (n10 + n11)) - 1) << (n00 + n01)
                b = (((1 << n01) - 1) << n00) | (
                    ((1 << n11) - 1) << (n00 + n01 + n10))
                if a and b and a != b:
                    yield (n00, n01, n10, n11), a, b


def forbidden(a, b):
    """Pairs that MUST have scalar intersection rank eight, not an iff edge test."""
    return bool(parity(a & b) or (
        parity(a) == parity(b) == 0
        and (a.bit_count() // 2) % 2 == (b.bit_count() // 2) % 2))


def _selected_minor(model, a, b=None):
    """Use F3 to select standard-coordinate witnesses, then certify over Z."""
    scalar_rows = standard_binding(model)
    basis, selected = {}, []
    for index, (label, row) in enumerate(zip(model["labels"], scalar_rows)):
        if not parity(label & a) or (b is not None and not parity(label & b)):
            continue
        values = [value % 3 for value in row]
        for pivot, old in sorted(basis.items()):
            factor = values[pivot]
            values = [(x - factor * y) % 3 for x, y in zip(values, old)]
        pivot = next((i for i, value in enumerate(values) if value), None)
        if pivot is None:
            continue
        scale = pow(values[pivot], -1, 3)
        basis[pivot] = [value * scale % 3 for value in values]
        selected.append(index)
        if len(selected) == 8:
            value = determinant([scalar_rows[i] for i in selected])
            require(value != 0, "selected minor has zero integer determinant")
            require(abs(value) & (abs(value) - 1) == 0, "selected minor is not a unit over Z[1/2]")
            return {"rows": selected, "determinant": value}
    raise ValueError("no eight-row witness for required character/profile")


def make_certificate(model):
    singles = [{"weight": k, "normal": (1 << k) - 1,
                **_selected_minor(model, (1 << k) - 1)} for k in range(1, 10)]
    pairs = [{"counts": list(counts), "a": a, "b": b,
              **_selected_minor(model, a, b)}
             for counts, a, b in pair_profiles() if forbidden(a, b)]
    return {"schema_version": 1, "model": MODEL,
            "single_types": singles, "forbidden_pairs": pairs}


def check_certificate(model, certificate):
    scalar_rows = standard_binding(model)
    require(type(certificate) is dict and set(certificate) == {
        "schema_version", "model", "single_types", "forbidden_pairs"}, "certificate schema")
    require(type(certificate["schema_version"]) is int and certificate["schema_version"] == 1
            and certificate["model"] == MODEL, "certificate model/version")
    singles, pairs = certificate["single_types"], certificate["forbidden_pairs"]
    require(type(singles) is list and len(singles) == 9, "single inventory count")
    require(type(pairs) is list and len(pairs) == 100, "forbidden inventory count")
    expected = {tuple(counts): (a, b) for counts, a, b in pair_profiles() if forbidden(a, b)}
    require(len(list(pair_profiles())) == 192 and len(expected) == 100, "profile enumeration")
    seen_single, seen_pair, determinants = set(), set(), []
    for item, kind in [(row, "single") for row in singles] + [(row, "pair") for row in pairs]:
        fields = {"weight", "normal", "rows", "determinant"} if kind == "single" else {
            "counts", "a", "b", "rows", "determinant"}
        require(type(item) is dict and set(item) == fields, "witness schema")
        if kind == "single":
            weight = item["weight"]
            require(type(weight) is int and 1 <= weight <= 9, "single weight")
            a, b = item["normal"], None
            require(type(a) is int and a == (1 << weight) - 1, "single normal binding")
            require(weight not in seen_single, "duplicate single type")
            seen_single.add(weight)
        else:
            counts = item["counts"]
            require(type(counts) is list and len(counts) == 4
                    and all(type(n) is int and 0 <= n <= 9 for n in counts), "profile counts")
            key = tuple(counts)
            require(key in expected and key not in seen_pair, "unknown/duplicate forbidden profile")
            a, b = item["a"], item["b"]
            require(type(a) is type(b) is int and (a, b) == expected[key], "normal/profile binding")
            seen_pair.add(key)
        rows, value = item["rows"], item["determinant"]
        require(type(rows) is list and len(rows) == 8
                and all(type(i) is int and 0 <= i < 120 for i in rows)
                and len(set(rows)) == 8, "minor root indices")
        require(type(value) is int and value != 0, "minor determinant type/value")
        for index in rows:
            label = model["labels"][index]
            require(parity(label & a) and (b is None or parity(label & b)), "witness support membership")
        require(determinant([scalar_rows[i] for i in rows]) == value, "integer minor determinant")
        require(abs(value) & (abs(value) - 1) == 0, "minor is not a unit over Z[1/2]")
        determinants.append(abs(value))
    require(seen_single == set(range(1, 10)) and seen_pair == set(expected), "incomplete type coverage")
    return {"single_types": 9, "valid_pair_profiles": 192,
            "forbidden_pair_profiles": 100, "nonzero_integer_minors": len(determinants),
            "determinants_absolute": sorted(set(determinants)),
            "all_minors_units_over_Z_half": True}


def reflection_transport(model):
    """Check all S9 generators over Z[1/2], without reducing the A8 isometry at3."""
    scalar = standard_binding(model)
    lookup = {canonical(row): i for i, row in enumerate(scalar)}
    root_lookup = {row: i for i, row in enumerate(model["roots"])}
    for k in range(8):
        pair = tuple(3 if j == k else -3 if j == k + 1 else 0 for j in range(9))
        alpha = scalar[root_lookup[pair]]
        # Numerator of the reflection I - alpha alpha^T / 4.
        numerator = [[4 * int(i == j) - alpha[i] * alpha[j] for j in range(8)]
                     for i in range(8)]
        require(all(sum(numerator[i][t] * numerator[t][j] for t in range(8)) == 16 * int(i == j)
                    for i in range(8) for j in range(8)), "reflection is not invertible over Z[1/2]")
        for i, row in enumerate(scalar):
            product = dot(row, alpha)
            require(product % 4 == 0, "root reflection quotient is not integral")
            image = tuple(x - (product // 4) * y for x, y in zip(row, alpha))
            require(canonical(image) in lookup, "root reflection leaves the fixed alphabet")
            target = lookup[canonical(image)]
            label = model["labels"][i]
            swap = ((label >> k) ^ (label >> (k + 1))) & 1
            label_image = label ^ ((1 << k) | (1 << (k + 1))) if swap else label
            require(model["labels"][target] == label_image, "reflection/S9 label action differs")
            require(all(4 * image[j] == sum(numerator[j][t] * row[t] for t in range(8))
                        for j in range(8)), "reflection integer transport identity")
    return {"adjacent_generators": 8, "root_line_transports": 960,
            "involution_matrix_entries": 512, "denominators_are_powers_of_two": True}


def certificate_text(certificate):
    """Keep each explicit witness on one line so the certificate is reviewable."""
    import json
    blocks = ['{', '  "schema_version": 1,', '  "model": ' + json.dumps(MODEL) + ',']
    for name in ("single_types", "forbidden_pairs"):
        blocks.append('  ' + json.dumps(name) + ': [')
        rows = certificate[name]
        for index, row in enumerate(rows):
            blocks.append('    ' + json.dumps(row, separators=(',', ':')) + (',' if index + 1 < len(rows) else ''))
        blocks.append('  ]' + (',' if name == "single_types" else ''))
    return '\n'.join(blocks + ['}', ''])


def support_weight(model, values):
    require(len(values) == 120, "support vector length")
    return binary_rank(label for label, value in zip(model["labels"], values) if value)


def copy_rank(model, p, q):
    require(len(p) == len(q) == 120, "factor length")
    columns = [label for label, value in zip(model["labels"], q) if value]
    return binary_rank(sum(parity(label & column) << j for j, column in enumerate(columns))
                       for label, value in zip(model["labels"], p) if value)
