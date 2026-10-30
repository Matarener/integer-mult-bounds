"""Separate finite-field and expanded-identity check, no verifier import."""

import itertools
import json
from hashlib import sha1, sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent


def require(test, message):
    if not test:
        raise ValueError(message)


def bounded_json(path, limit=1_048_576):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, "input size limit")
    return raw, json.loads(raw)


def source():
    _, metadata = bounded_json(HERE / "SOURCES.json", 32768)
    pins = [r for r in metadata["files"] if r["usage"] == "input"]
    require(len(pins) == 1, "one live label input")
    expected = "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    require(pins[0]["path"] == expected, "label path")
    raw, data = bounded_json(HERE.parents[1] / expected)
    pairs = ((raw, pins[0]),)
    raw_groups, certificate = bounded_json(HERE / "RETAINED-RANK32.json", 32768)
    pairs += ((raw_groups, metadata["retained_rank32"]),)
    for payload, pin in pairs:
        require(sha256(payload).hexdigest() == pin["sha256"], "input SHA256")
        header = b"blob " + str(len(payload)).encode() + b"\0"
        require(
            sha1(header + payload, usedforsecurity=False).hexdigest()
            == pin["git_blob"],
            "input blob",
        )
    recipes = data["recipes"]
    require(type(recipes) is list and len(recipes) == 112, "112 labels")
    require(sorted(r["port"] for r in recipes) == list(range(112)), "port IDs")
    labels = [r["q"] for r in sorted(recipes, key=lambda r: r["port"])]
    require(all(type(q) is int and 0 < q < 512 for q in labels), "label range")
    groups = certificate["orthonormal_groups"]
    require(len(groups) == 16 and all(len(g) in (4, 6, 8) for g in groups), "groups")
    require(sorted(p for g in groups for p in g) == list(range(112)), "partition")
    return labels, groups


def elimination(matrix, prime):
    require(
        len(matrix) <= 224 and all(len(row) <= 224 for row in matrix), "rank capacity"
    )
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "rectangular matrix")
    a = [[v % prime for v in row] for row in matrix]
    pivot = 0
    for col in range(width):
        candidates = [i for i in range(pivot, len(a)) if a[i][col]]
        if not candidates:
            continue
        at = candidates[0]
        a[pivot], a[at] = a[at], a[pivot]
        scale = pow(a[pivot][col], -1, prime)
        a[pivot] = [v * scale % prime for v in a[pivot]]
        for i in range(pivot + 1, len(a)):
            scale = a[i][col]
            a[i] = [
                (x - scale * y) % prime for x, y in zip(a[i], a[pivot], strict=True)
            ]
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def coordinates(label):
    return [(label >> bit) & 1 for bit in range(9)]


def dot(left, right):
    return sum(x * y for x, y in zip(left, right, strict=True)) % 2


def expanded_identity():
    labels, groups = source()
    vectors = [coordinates(q) for q in labels]
    supports = [set(g[side::2]) for g in groups for side in (0, 1)]
    planes = [g[i : i + 2] for g in groups for i in range(0, len(g), 2)]
    owner = {p: pair for pair in planes for p in pair}
    expanded = []
    for p in range(112):
        for axis in range(2):
            row = []
            for q in range(112):
                scalar = sum(p in s and q in s for s in supports)
                row.extend(
                    scalar * dot(vectors[owner[p][axis]], vectors[r]) for r in owner[q]
                )
            expanded.append(row)
    require(
        all(
            v == int(i == j)
            for i, row in enumerate(expanded)
            for j, v in enumerate(row)
        ),
        "expanded I224",
    )
    baseline = 0
    for support in supports:
        closure = sorted({r for p in support for r in owner[p]})
        gram = [[dot(vectors[p], vectors[q]) for q in closure] for p in closure]
        baseline += elimination(gram, 2)
    require(baseline == 224, "literal tariff 224")
    return {"entries": 224 * 224, "baseline": baseline}


def det(a):
    # Signed permutation expansion, independent of the primary cofactor routine.
    total = 0
    for permutation in itertools.permutations(range(3)):
        inversions = sum(
            permutation[i] > permutation[j] for i in range(3) for j in range(i + 1, 3)
        )
        product = 1
        for i in range(3):
            product *= a[i][permutation[i]]
        total += (-1) ** inversions * product
    return total


def binary_candidate(points):
    # Choose the two coordinate bit-vectors directly, not grid permutations.
    for xb in range(1, 7):
        x = [(xb >> i) & 1 for i in range(3)]
        for yb in range(1, 7):
            y = [(yb >> i) & 1 for i in range(3)]
            candidate = [[x[i], y[i], 1] for i in range(3)]
            if det(candidate) == 0:
                continue
            if all(
                points[i][axis] != points[j][axis]
                or candidate[i][axis] == candidate[j][axis]
                for i in range(3)
                for j in range(i + 1, 3)
                for axis in range(2)
            ):
                return candidate
    raise ValueError("binary equality assignment unavailable")


def field_check(prime):
    require(prime in (2, 3, 5), "finite field inventory")
    points = list(itertools.product(range(prime), repeat=2))
    count, zeros, classes = 0, 0, set()
    for triple in itertools.permutations(points, 3):
        matrix = [[*point, 1] for point in triple]
        if det(matrix) % prime == 0:
            continue
        candidate = binary_candidate(triple)
        require(abs(det(candidate)) == 1, "unimodular replacement")
        classes.add(
            tuple(
                triple[i][axis] == triple[j][axis]
                for axis in range(2)
                for i, j in ((0, 1), (0, 2), (1, 2))
            )
        )
        for i in range(3):
            j, k = (i + 1) % 3, (i + 2) % 3
            for axis in range(2):
                require(
                    triple[j][axis] != triple[k][axis]
                    or candidate[j][axis] == candidate[k][axis],
                    "reader zero",
                )
        for axis in range(2):
            for seed in range(prime):
                old_zeros = [
                    i for i in range(3) if (seed + triple[i][axis]) % prime == 0
                ]
                replacement = -candidate[old_zeros[0]][axis] if old_zeros else 0
                require(
                    all(replacement + candidate[i][axis] == 0 for i in old_zeros),
                    "query zero",
                )
                zeros += len(old_zeros)
        count += 1
    expected = prime * prime * (prime * prime - 1) * (prime * prime - prime)
    require(count == expected, "complete affine-triangle enumeration")
    return {
        "prime": prime,
        "triangles": count,
        "zero_constraints": zeros,
        "equality_classes": len(classes),
    }


def main():
    _, result = bounded_json(HERE / "RESULT.json")
    require(len(result["equality_classes"]) == 13, "primary class count")
    fields = [field_check(p) for p in (2, 3, 5)]
    require(fields[-1]["equality_classes"] == 13, "all thirteen classes reached")
    print(
        json.dumps(
            {
                "status": "PASS_SEPARATE_THREE_QUERY",
                "errors": 0,
                "fields": fields,
                "expanded": expanded_identity(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
