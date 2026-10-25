"""Separate minors/subset-collapse and GF4 annihilator implementation."""

import hashlib
import json
from itertools import combinations, permutations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
P = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def check(value, message):
    if not value:
        raise ValueError(message)


def fixture(name):
    path = ROOT / name
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536,
        "independent bounded fixture",
    )
    return json.loads(path.read_bytes())


def determinant(rows):
    n = len(rows)
    check(n <= 4, "minor dimension capacity")
    total = 0
    for perm in permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        term = (-1) ** inversions
        for i in range(n):
            term *= rows[i][perm[i]]
        total += term
    return total


def rational_rank(columns):
    if not columns:
        return 0
    dimension = len(columns[0])
    check(dimension <= 4 and len(columns) <= 7, "minor input capacity")
    for size in range(min(dimension, len(columns)), 0, -1):
        for chosen in combinations(columns, size):
            for axes in combinations(range(dimension), size):
                if determinant([[c[j] for j in axes] for c in chosen]):
                    return size
    return 0


def quadrangle_maps():
    vertices = (0, 1, 2, 6)
    matchings = (
        frozenset((frozenset((0, 1)), frozenset((2, 6)))),
        frozenset((frozenset((0, 2)), frozenset((1, 6)))),
        frozenset((frozenset((0, 6)), frozenset((1, 2)))),
    )
    result = []
    for image in permutations(vertices):
        mapping = dict(zip(vertices, image, strict=True))
        for index, matching in enumerate(matchings):
            translated = frozenset(
                frozenset(mapping[x] for x in edge) for edge in matching
            )
            mapping[index + 3] = matchings.index(translated) + 3
        result.append(tuple(mapping[j] for j in range(7)))
    return sorted(result)


def bases():
    data = fixture("PREDECESSOR-TEMPLATES.json")
    check(
        data["polynomial"] == 7
        and data["representative_pairs"] == [[0, 1], [0, 3], [3, 4]],
        "independent GF4 template header",
    )
    check(
        len(data["points"]) == 3 and all(len(row) == 7 for row in data["points"]),
        "independent template count",
    )
    check(
        all(
            len(c) == 3 and all(type(x) is int and 0 <= x < 4 for x in c)
            for row in data["points"]
            for c in row
        ),
        "independent template shape",
    )
    for marks in combinations(range(7), 2):
        images = []
        for pair, template in zip(
            data["representative_pairs"], data["points"], strict=True
        ):
            for relabel in quadrangle_maps():
                if {relabel[j] for j in pair} == set(marks):
                    columns = [None] * 7
                    for j in range(7):
                        columns[relabel[j]] = tuple(template[j])
                    images.append(columns)
        check(bool(images), "independent marked orbit coverage")
        order = [j for j in range(7) if j not in marks] + list(marks)
        yield marks, tuple(P[j] for j in order), tuple(images[0][j] for j in order)


def paths(marks):
    yield ()
    for kind in ("series", "parallel"):
        for j in range(5):
            yield ((kind, j),)
    if marks in ((0, 1), (0, 3), (3, 4)):
        for first in ("series", "parallel"):
            for second in ("series", "parallel"):
                for j in (0, 5):
                    yield ((first, 0), (second, j))


def lift(columns, path):
    result = list(columns)
    for kind, index in path:
        t = len(result) - 2
        if kind == "series":
            result = [tuple(c) + (int(j == index),) for j, c in enumerate(result)]
            added = (0,) * (len(result[0]) - 1) + (1,)
        else:
            check(kind == "parallel", "independent rewrite kind")
            added = result[index]
        result.insert(t, added)
    return tuple(result)


def collapse(mask, path):
    for depth in range(len(path) - 1, -1, -1):
        kind, index = path[depth]
        appended = 5 + depth
        first, second = bool(mask >> index & 1), bool(mask >> appended & 1)
        active = first and second if kind == "series" else first or second
        mask &= (1 << appended) - 1
        mask &= ~(1 << index)
        if active:
            mask |= 1 << index
    return mask


def gf4_dot(left, right):
    result = 0
    for x, y in zip(left, right, strict=True):
        result ^= MUL[x][y]
    return result


def profiles(columns):
    t, d = len(columns) - 2, len(columns[0])
    check(t <= 7 and d <= 5, "annihilator capacity")
    source = [[False] * (1 << t) for _ in range(2)]
    outside = [[False] * (1 << t) for _ in range(2)]
    for functional in product(range(4), repeat=d):
        values = [gf4_dot(functional, c) for c in columns]
        zeros = sum(1 << i for i in range(t) if not values[i])
        for j in range(2):
            if values[t + j]:
                outside[j][zeros] = True
                if not values[t + 1 - j]:
                    source[j][zeros] = True
    for flags in source + outside:
        for bit in range(t):
            for mask in range(1 << t):
                if not mask >> bit & 1:
                    flags[mask] |= flags[mask | (1 << bit)]
    return source, [[not x for x in row] for row in outside]


def base_profiles(columns):
    ranks = [
        rational_rank([c for j, c in enumerate(columns) if mask >> j & 1])
        for mask in range(128)
    ]
    source, reader = [], []
    for j in range(2):
        a, b = 1 << (5 + j), 1 << (6 - j)
        source.append([ranks[s | a | b] > ranks[s | b] for s in range(32)])
        reader.append([ranks[s | a] == ranks[s] for s in range(32)])
    return source, reader


def witness():
    data = fixture("WITNESS.json")
    q, u, marks, labels = (
        data[k] for k in ("queries", "readers", "targets", "binary_labels")
    )
    check(
        len(q) == len(u) == 6
        and len(marks) == 2
        and all(len(c) == 4 for c in q + u + marks),
        "independent witness shape",
    )
    check(
        all(type(x) is int and abs(x) <= 2 for c in q + u + marks for x in c),
        "independent coefficient bound",
    )
    check(
        labels == [1, 2, 4, 8] and data["groups"] == [[0, 1], [2, 3]],
        "independent label contract",
    )
    check(marks == [[1, 0, 0, 0], [0, 1, 0, 0]], "independent literal targets")
    for i, j in product(range(4), repeat=2):
        check(
            sum(u[k][i] * q[k][j] for k in range(6)) == sum(v[i] * v[j] for v in marks),
            "independent literal operator",
        )
    check(rational_rank(q) == rational_rank(u) == 4, "independent factor ranks")
    charges = []
    for index in range(6):
        left = [
            j for pair in data["groups"] if any(q[index][x] for x in pair) for j in pair
        ]
        right = [
            j for pair in data["groups"] if any(u[index][x] for x in pair) for j in pair
        ]
        rows = [
            sum(
                ((labels[a] & labels[b]).bit_count() % 2) << k
                for k, b in enumerate(right)
            )
            for a in left
        ]
        basis = [0] * 4
        for row in rows:
            for bit in range(3, -1, -1):
                if row >> bit & 1:
                    if basis[bit]:
                        row ^= basis[bit]
                    else:
                        basis[bit] = row
                        break
        charges.append(sum(bool(x) for x in basis))
    return {
        "factor_ranks": [4, 4],
        "charges": charges,
        "bill": sum(charges),
        "pair_floor": 4,
    }


def main():
    closure = fixture("SOURCE-CLOSURE.json")
    check(
        len(closure) == 2
        and [r["local_path"] for r in closure]
        == ["PREDECESSOR-PROOF.md", "PREDECESSOR-TEMPLATES.json"],
        "independent closure paths",
    )
    for row in closure:
        check(
            hashlib.sha256((ROOT / row["local_path"]).read_bytes()).hexdigest()
            == row["sha256"],
            "independent source closure hash",
        )
    count = sources = readers = 0
    stream = hashlib.sha256()
    for marks, old, new in bases():
        old_source, old_reader = base_profiles(old)
        for path in paths(marks):
            new_source, new_reader = profiles(lift(new, path))
            s = r = 0
            for mask in range(1 << (5 + len(path))):
                collapsed = collapse(mask, path)
                for j in range(2):
                    if old_source[j][collapsed]:
                        check(new_source[j][mask], "independent source transfer")
                        s += 1
                    if old_reader[j][collapsed]:
                        check(new_reader[j][mask], "independent reader transfer")
                        r += 1
            stream.update(
                (json.dumps([marks, path, s, r], separators=(",", ":")) + "\n").encode()
            )
            count += 1
            sources += s
            readers += r
    result = {
        "cases": count,
        "source_premises": sources,
        "reader_premises": readers,
        "stream_sha256": stream.hexdigest(),
        "witness": witness(),
    }
    check(result == fixture("RESULT.json"), "independent frozen result mismatch")
    print("PASS_INDEPENDENT_QUERY_SERIES " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
