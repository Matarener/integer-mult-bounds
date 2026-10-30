"""Separate extension-field checks. Nick Petalas. Apache-2.0."""

import itertools
import json
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def bounded(path, maximum):
    with path.open("rb") as stream:
        raw = stream.read(maximum + 1)
    require(len(raw) <= maximum, "input limit")
    return raw


def source_data():
    meta = json.loads(bounded(HERE / "SOURCES.json", 32768))
    inputs = [r for r in meta["files"] if r["usage"] == "input"]
    require(len(inputs) == 1, "one live input")
    pin = inputs[0]
    require(
        pin["path"] == "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json",
        "input path",
    )
    raw = bounded(ROOT / pin["path"], 1_048_576)
    require(sha256(raw).hexdigest() == pin["sha256"], "label SHA256")
    require(
        sha1(
            b"blob " + str(len(raw)).encode() + b"\0" + raw, usedforsecurity=False
        ).hexdigest()
        == pin["git_blob"],
        "label blob",
    )
    rows = json.loads(raw)["recipes"]
    require(
        len(rows) == 112 and sorted(r["port"] for r in rows) == list(range(112)),
        "ports",
    )
    labels = [r["q"] for r in sorted(rows, key=lambda r: r["port"])]
    require(all(type(q) is int and 0 < q < 512 for q in labels), "binary labels")
    raw = bounded(HERE / "RETAINED-RANK32.json", 32768)
    require(
        sha256(raw).hexdigest() == meta["retained_rank32"]["sha256"], "fixture SHA256"
    )
    groups = json.loads(raw)["orthonormal_groups"]
    require(
        len(groups) == 16 and sorted(p for g in groups for p in g) == list(range(112)),
        "partition",
    )
    require(all(len(g) in (4, 6, 8) for g in groups), "even groups")
    return [tuple(q >> k & 1 for k in range(9)) for q in labels], groups


def pairing(x, y):
    return sum(a * b for a, b in zip(x, y, strict=True)) % 2


def field_tables():
    powers = []
    value = 1
    for _ in range(15):
        powers.append(value)
        value *= 2
        if value >= 16:
            value ^= 19
    require(
        value == 1 and set(powers) == set(range(1, 16)), "GF16 multiplicative cycle"
    )
    logs = [-1] * 16
    for exponent, element in enumerate(powers):
        logs[element] = exponent
    return tuple(powers), tuple(logs)


POWERS, LOGS = field_tables()


def times(x, y):
    return 0 if not x or not y else POWERS[(LOGS[x] + LOGS[y]) % 15]


def reciprocal(x):
    require(0 < x < 16, "field divisor")
    return POWERS[-LOGS[x] % 15]


def coefficients(d, e, target):
    denominator = reciprocal(times(d[0], e[1]) ^ times(d[1], e[0]))
    left = times(times(target[0], e[1]) ^ times(target[1], e[0]), denominator)
    right = times(times(d[0], target[1]) ^ times(d[1], target[0]), denominator)
    return left, right


def extension_rank(rows):
    matrix = [list(row) for row in rows]
    width = len(matrix[0]) if matrix else 0
    pivot = 0
    for column in range(width):
        candidates = [i for i in range(pivot, len(matrix)) if matrix[i][column]]
        if not candidates:
            continue
        i = candidates[0]
        matrix[pivot], matrix[i] = matrix[i], matrix[pivot]
        scale = reciprocal(matrix[pivot][column])
        matrix[pivot] = [times(x, scale) for x in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot and matrix[i][column]:
                scale = matrix[i][column]
                matrix[i] = [
                    x ^ times(scale, y)
                    for x, y in zip(matrix[i], matrix[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def prime_rank(rows, prime):
    matrix = [list(row) for row in rows]
    width = len(matrix[0]) if matrix else 0
    pivot = 0
    for column in range(width):
        candidates = [i for i in range(pivot, len(matrix)) if matrix[i][column] % prime]
        if not candidates:
            continue
        i = candidates[0]
        matrix[pivot], matrix[i] = matrix[i], matrix[pivot]
        scale = pow(matrix[pivot][column], -1, prime)
        matrix[pivot] = [x * scale % prime for x in matrix[pivot]]
        for i in range(len(matrix)):
            if i != pivot and matrix[i][column] % prime:
                scale = matrix[i][column]
                matrix[i] = [
                    (x - scale * y) % prime
                    for x, y in zip(matrix[i], matrix[pivot], strict=True)
                ]
        pivot += 1
    return pivot


def expanded_identity(vectors, groups):
    require(
        sorted(p for g in groups for p in g) == list(range(len(vectors)))
        and all(g and len(g) % 2 == 0 for g in groups),
        "positive even partition",
    )
    classes = {}
    planes = {}
    for index, group in enumerate(groups):
        for i, p in enumerate(group):
            classes[p] = (index, i % 2)
            planes[p] = group[i - i % 2 : i - i % 2 + 2]
    # The coordinate construction is separate from the primary packed-bit rank.
    for p, q in itertools.product(range(len(vectors)), repeat=2):
        for i, j in itertools.product(range(2), repeat=2):
            value = int(classes[p] == classes[q]) * pairing(
                vectors[planes[p][i]], vectors[planes[q][j]]
            )
            require(value == int(p == q and i == j), "explicit expanded identity")
    for group in groups:
        gram = [[pairing(vectors[p], vectors[q]) for q in group] for p in group]
        require(
            extension_rank(gram) == prime_rank(gram, 2) == len(group),
            "extension group rank",
        )
    return planes


def general_geometry_controls():
    examples = (
        ([1, 2], [[0, 1]]),
        ([1, 2, 4, 8, 14, 13, 11, 7], [[0, 1, 2, 3], [4, 5, 6, 7]]),
        ([1, 2, 14, 13, 11, 7], [[0, 1], [2, 3, 4, 5]]),
    )
    entries = 0
    for labels, groups in examples:
        vectors = [tuple(q >> k & 1 for k in range(4)) for q in labels]
        expanded_identity(vectors, groups)
        entries += (2 * len(labels)) ** 2
    invalid = (
        ([1, 2, 4], [[0, 1, 2]], "positive even partition"),
        ([1, 1], [[0, 1]], "explicit expanded identity"),
    )
    for labels, groups, message in invalid:
        vectors = [tuple(q >> k & 1 for k in range(4)) for q in labels]
        try:
            expanded_identity(vectors, groups)
        except ValueError as error:
            require(message in str(error), "intended general hypothesis rejection")
        else:
            raise ValueError("invalid general geometry accepted")
    return entries, len(invalid)


def binary_obstruction_and_extension():
    pairs = list(itertools.combinations(range(4), 2))
    binary = ((0, 0), (1, 0), (0, 1), (1, 1))
    admitted = 0
    for assignment in itertools.product(binary, repeat=4):
        if all(
            (assignment[i][0] * assignment[j][1] ^ assignment[i][1] * assignment[j][0])
            for i, j in pairs
        ):
            admitted += 1
    require(admitted == 0, "four binary images impossible")
    images = [(1, x) for x in (1, 2, 4, 8)]
    requests = 0
    for i, j in pairs:
        for target in ((1, 0), (0, 1)):
            left, right = coefficients(images[i], images[j], target)
            require(left and right, "both requested readers active")
            value = tuple(
                times(left, images[i][k]) ^ times(right, images[j][k]) for k in range(2)
            )
            require(value == target, "extension solves four-direction request")
            requests += 1
    triangle = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
    require(
        extension_rank(triangle) == prime_rank(triangle, 2) == 2,
        "binary rank preserved",
    )
    require(prime_rank(triangle, 3) == 3, "wrong-characteristic rank control")
    return requests


def transfer_coefficients():
    tuples = 0
    requests = 0
    for prime in (2, 3, 5, 7):
        directions = [(1, 0), (0, 1)] + [(1, j) for j in range(1, min(prime, 5))]
        images = [(1, 0), (0, 1)] + [(1, POWERS[j]) for j in range(len(directions) - 2)]
        for old in itertools.product(range(prime), repeat=len(directions)):
            tuples += 1
            target = tuple(
                sum(c * d[k] for c, d in zip(old, directions, strict=True)) % prime
                for k in range(2)
            )
            if target not in ((1, 0), (0, 1)):
                continue
            active = [i for i, c in enumerate(old) if c]
            matching = [i for i in active if directions[i] == target]
            new = [0] * len(images)
            if matching:
                new[matching[0]] = 1
            else:
                require(len(active) >= 2, "two active classes")
                i, j = active[-2:]
                new[i], new[j] = coefficients(images[i], images[j], target)
            require(
                all(not c or old[i] for i, c in enumerate(new)),
                "pointwise support containment",
            )
            value = [0, 0]
            for c, d in zip(new, images, strict=True):
                for k in range(2):
                    value[k] ^= times(c, d[k])
            require(tuple(value) == target, "pointwise operator")
            requests += 1
    return tuples, requests


def rectangular_checks(vectors, groups, planes):
    indicators = [g[parity::2] for g in groups for parity in (0, 1)]
    checks = 0
    for a, b in itertools.combinations(indicators, 2):
        source = sorted({q for p in a + b for q in planes[p]})
        for support in (a, b, a[:1] + b[-1:], a + b):
            reader = sorted({q for p in support for q in planes[p]})
            matrix = [[pairing(vectors[p], vectors[q]) for q in reader] for p in source]
            require(
                extension_rank(matrix) == prime_rank(matrix, 2),
                "rectangular extension rank",
            )
            checks += 1
    return checks


def main():
    vectors, groups = source_data()
    planes = expanded_identity(vectors, groups)
    requests = binary_obstruction_and_extension()
    tuples, pointwise = transfer_coefficients()
    ranks = rectangular_checks(vectors, groups, planes)
    general_entries, hypothesis_rejections = general_geometry_controls()
    report = {
        "expanded_entries": 224**2,
        "binary_maps_rejected": 256,
        "four_direction_requests": requests,
        "prime_field_tuples": tuples,
        "pointwise_transfers": pointwise,
        "rectangular_rank_checks": ranks,
        "general_fixture_ports": [2, 8, 6],
        "general_expanded_entries": general_entries,
        "general_hypothesis_rejections": hypothesis_rejections,
    }
    print("PASS_SEPARATE_EXTENSION_CHECK", json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
