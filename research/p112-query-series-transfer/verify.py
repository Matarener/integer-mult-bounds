"""Exact marked-pair transfer and query-series controls. Standard library only."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
LINES = frozenset((11, 21, 97, 38, 82, 76))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    path = ROOT / name
    require(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536,
        "regular bounded fixture",
    )
    return json.loads(path.read_text())


def multiply(a, b):
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def rank(columns, binary=False):
    if not columns:
        return 0
    rows = [list(c) if binary else list(map(Fraction, c)) for c in columns]
    pivots = 0
    for j in range(len(rows[0])):
        k = next((i for i in range(pivots, len(rows)) if rows[i][j]), None)
        if k is None:
            continue
        rows[pivots], rows[k] = rows[k], rows[pivots]
        pivot = rows[pivots][j]
        if binary:
            inverse = next(x for x in range(1, 4) if multiply(pivot, x) == 1)
            rows[pivots] = [multiply(x, inverse) for x in rows[pivots]]
        else:
            rows[pivots] = [x / pivot for x in rows[pivots]]
        for i in range(pivots + 1, len(rows)):
            scale = rows[i][j]
            if binary:
                rows[i] = [
                    x ^ multiply(scale, y)
                    for x, y in zip(rows[i], rows[pivots], strict=True)
                ]
            else:
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[pivots], strict=True)
                ]
        pivots += 1
        if pivots == len(rows):
            break
    return pivots


def automorphisms():
    result = []
    for perm in permutations(range(7)):
        image = frozenset(
            sum(1 << perm[i] for i in range(7) if mask >> i & 1) for mask in LINES
        )
        if image == LINES:
            result.append(perm)
    require(len(result) == 24, "quadrangle automorphism count")
    return result


def marked_cases():
    data = load("PREDECESSOR-TEMPLATES.json")
    require(data["polynomial"] == 7, "GF4 polynomial")
    require(
        data["representative_pairs"] == [[0, 1], [0, 3], [3, 4]], "representative pairs"
    )
    require(
        len(data["points"]) == 3 and all(len(row) == 7 for row in data["points"]),
        "template count",
    )
    require(
        all(
            len(c) == 3 and all(type(x) is int and 0 <= x < 4 for x in c)
            for row in data["points"]
            for c in row
        ),
        "template column shape",
    )
    autos = automorphisms()
    for a, b in combinations(range(7), 2):
        selected = None
        for marks, template in zip(
            data["representative_pairs"], data["points"], strict=True
        ):
            for perm in autos:
                if {perm[marks[0]], perm[marks[1]]} == {a, b}:
                    mapped = [None] * 7
                    for i in range(7):
                        mapped[perm[i]] = tuple(template[i])
                    selected = mapped
                    break
            if selected is not None:
                break
        require(selected is not None, "marked orbit coverage")
        order = [i for i in range(7) if i not in (a, b)] + [a, b]
        yield (a, b), tuple(POINTS[i] for i in order), tuple(selected[i] for i in order)


def expand(columns, index, kind):
    queries, marks = list(columns[:-2]), list(columns[-2:])
    require(0 <= index < len(queries), "query index bound")
    if kind == "parallel":
        queries.append(queries[index])
        return tuple(queries + marks)
    require(kind == "series", "rewrite kind")
    queries = [tuple(c) + (0,) for c in queries]
    marks = [tuple(c) + (0,) for c in marks]
    queries[index] = queries[index][:-1] + (1,)
    queries.append((0,) * (len(queries[0]) - 1) + (1,))
    return tuple(queries + marks)


def suite():
    for pair, old, new in marked_cases():
        yield pair, (), old, new
        for kind in ("series", "parallel"):
            for j in range(5):
                yield pair, ((kind, j),), expand(old, j, kind), expand(new, j, kind)
        if pair in ((0, 1), (0, 3), (3, 4)):
            for first in ("series", "parallel"):
                for second in ("series", "parallel"):
                    for j in (0, 5):
                        path = ((first, 0), (second, j))
                        yield (
                            pair,
                            path,
                            expand(expand(old, 0, first), j, second),
                            expand(expand(new, 0, first), j, second),
                        )


def implications(old, new):
    t = len(old) - 2
    require(t <= 7 and len(old[0]) <= 5, "finite replay capacity")
    old_ranks, new_ranks = [], []
    for mask in range(1 << len(old)):
        old_ranks.append(rank([c for i, c in enumerate(old) if mask >> i & 1]))
        new_ranks.append(rank([c for i, c in enumerate(new) if mask >> i & 1], True))
    require(new_ranks[3 << t] == 2, "independent new marks")
    sources = readers = 0
    for mask in range(1 << t):
        for a, b in ((1 << t, 2 << t), (2 << t, 1 << t)):
            if old_ranks[mask | a | b] > old_ranks[mask | b]:
                require(
                    new_ranks[mask | a | b] > new_ranks[mask | b], "source transfer"
                )
                sources += 1
            if old_ranks[mask | a] == old_ranks[mask]:
                require(new_ranks[mask | a] == new_ranks[mask], "reader transfer")
                readers += 1
    return sources, readers


def witness():
    data = load("WITNESS.json")
    q, u, targets = data["queries"], data["readers"], data["targets"]
    require(len(q) == len(u) == 6 and all(len(c) == 4 for c in q + u), "witness shape")
    require(
        all(type(x) is int and abs(x) <= 2 for c in q + u for x in c),
        "witness coefficients",
    )
    require(targets == [[1, 0, 0, 0], [0, 1, 0, 0]], "literal targets")
    require(
        q
        == [
            list(c)
            for c in expand(
                tuple(POINTS[i] for i in (2, 3, 4, 5, 6, 0, 1)), 0, "series"
            )[:-2]
        ],
        "series witness binding",
    )
    for i in range(4):
        for j in range(4):
            actual = sum(x[i] * y[j] for x, y in zip(u, q, strict=True))
            require(actual == int(i == j and i < 2), "literal operator")
    require(rank(q) == rank(u) == 4, "rank four on both factors")
    require(
        data["binary_labels"] == [1, 2, 4, 8] and data["groups"] == [[0, 1], [2, 3]],
        "orthonormal witness labels",
    )
    charges = []
    for reader, query in zip(u, q, strict=True):
        left = {j for j in range(4) if query[j // 2 * 2] or query[j // 2 * 2 + 1]}
        right = {j for j in range(4) if reader[j // 2 * 2] or reader[j // 2 * 2 + 1]}
        charges.append(len(left & right))
    require(charges == [2, 0, 4, 4, 2, 2], "rectangular witness tariff")
    return {
        "factor_ranks": [4, 4],
        "charges": charges,
        "bill": sum(charges),
        "pair_floor": 4,
    }


def main():
    closure = load("SOURCE-CLOSURE.json")
    require(
        len(closure) == 2
        and [s["local_path"] for s in closure]
        == ["PREDECESSOR-PROOF.md", "PREDECESSOR-TEMPLATES.json"],
        "closure paths",
    )
    for source in closure:
        require(
            hashlib.sha256((ROOT / source["local_path"]).read_bytes()).hexdigest()
            == source["sha256"],
            "source closure hash",
        )
    sources = readers = cases = 0
    stream = hashlib.sha256()
    for pair, path, old, new in suite():
        s, r = implications(old, new)
        sources += s
        readers += r
        cases += 1
        stream.update(
            (json.dumps([pair, path, s, r], separators=(",", ":")) + "\n").encode()
        )
    result = {
        "cases": cases,
        "source_premises": sources,
        "reader_premises": readers,
        "stream_sha256": stream.hexdigest(),
        "witness": witness(),
    }
    expected = load("RESULT.json")
    require(result == expected, "frozen result mismatch")
    print("PASS_QUERY_SERIES_TRANSFER " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
