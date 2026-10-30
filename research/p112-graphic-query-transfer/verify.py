"""Exact graphic-interface and literal-bill certificate. Standard library only."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
BRIDGE = ((0, 2), (2, 1), (0, 3), (3, 1), (2, 3))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    require(path.is_file() and not path.is_symlink(), "regular input")
    require(path.stat().st_size <= 131072, "bounded input")
    return json.loads(path.read_text())


def authenticate():
    pins = read(PACKAGE / "SOURCES.json")
    for row in pins["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            require(path.is_file() and not path.is_symlink(), "regular source")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "source hash",
            )


def mul(a, b):
    answer = 0
    for _ in range(2):
        if b & 1:
            answer ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return answer


def rank(columns, field=0):
    if not columns:
        return 0
    rows = [list(c) if field else list(map(Fraction, c)) for c in columns]
    require(len(rows) <= 12 and len(rows[0]) <= 6, "rank capacity")
    r = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        inverse = (
            next(x for x in range(1, 4) if mul(rows[r][j], x) == 1)
            if field
            else 1 / rows[r][j]
        )
        rows[r] = [mul(x, inverse) if field else x * inverse for x in rows[r]]
        for i in range(r + 1, len(rows)):
            scale = rows[i][j]
            rows[i] = [
                x ^ mul(scale, y) if field else x - scale * y
                for x, y in zip(rows[i], rows[r], strict=True)
            ]
        r += 1
        if r == len(rows):
            break
    return r


def connected(vertices, edges, mask):
    reached = {0}
    for _ in range(vertices):
        for i, (a, b) in enumerate(edges):
            if mask >> i & 1 and (a in reached or b in reached):
                reached.update((a, b))
    return 1 in reached


def network(vertices, edges, terminal, field=0):
    d = len(terminal)
    potentials = [(0,) * (d + vertices - 2), tuple(terminal) + (0,) * (vertices - 2)]
    for v in range(vertices - 2):
        potentials.append((0,) * d + tuple(int(i == v) for i in range(vertices - 2)))
    return [
        tuple(
            x ^ y if field else x - y
            for x, y in zip(potentials[b], potentials[a], strict=True)
        )
        for a, b in edges
    ]


def graph_suite():
    records = []
    for v in range(2, 6):
        edges = tuple(combinations(range(v), 2))
        vectors = network(v, edges, (1,))
        stream = []
        for mask in range(1 << len(edges)):
            selected = [c for i, c in enumerate(vectors) if mask >> i & 1]
            truth = connected(v, edges, mask)
            for field in (0, 1):
                actual = (
                    [tuple(x % 2 for x in c) for c in selected] if field else selected
                )
                target = (1,) + (0,) * (v - 2)
                require(
                    (rank(actual + [target], field) == rank(actual, field)) == truth,
                    "graphic span",
                )
            stream.append(int(truth))
        records.append(
            {
                "vertices": v,
                "edges": len(edges),
                "subsets": len(stream),
                "truth_sha256": hashlib.sha256(bytes(stream)).hexdigest(),
            }
        )
    return records


def expanded(columns, query, field):
    q = list(columns[:5])
    edges = network(4, BRIDGE, q[query], field)
    old = [tuple(c) + (0, 0) for c in columns]
    return old[:query] + edges + old[query + 1 :]


def marked_suite():
    templates = read(
        ROOT / "research/p112-query-series-transfer/PREDECESSOR-TEMPLATES.json"
    )
    require(
        templates["polynomial"] == 7
        and templates["representative_pairs"] == [[0, 1], [0, 3], [3, 4]],
        "template header",
    )
    records = []
    for pair, points in zip(
        templates["representative_pairs"], templates["points"], strict=True
    ):
        require(
            len(points) == 7
            and all(
                len(c) == 3 and all(type(x) is int and 0 <= x < 4 for x in c)
                for c in points
            ),
            "template shape",
        )
        order = [i for i in range(7) if i not in pair] + pair
        for e in range(5):
            old = expanded([POINTS[i] for i in order], e, 0)
            new = expanded([points[i] for i in order], e, 1)
            tables = []
            for columns, field in ((old, 0), (new, 1)):
                tables.append(
                    [
                        rank([c for i, c in enumerate(columns) if mask >> i & 1], field)
                        for mask in range(1 << 11)
                    ]
                )
            a, b = tables
            require(a[3 << 9] == b[3 << 9] == 2, "independent marks")
            source = reader = 0
            for mask in range(1 << 9):
                for j, k in ((1 << 9, 2 << 9), (2 << 9, 1 << 9)):
                    if a[mask | j | k] > a[mask | k]:
                        require(b[mask | j | k] > b[mask | k], "source transfer")
                        source += 1
                    if a[mask | j] == a[mask]:
                        require(b[mask | j] == b[mask], "reader transfer")
                        reader += 1
            records.append(
                {"pair": pair, "query": e, "source": source, "reader": reader}
            )
    return records


def binary_rank(rows):
    pivots = {}
    for row in rows:
        for bit in range(6, -1, -1):
            if row >> bit & 1:
                if bit in pivots:
                    row ^= pivots[bit]
                else:
                    pivots[bit] = row
                    break
    return len(pivots)


def rectangular_charges(q, u, labels):
    charges = []
    for x, y in zip(q, u, strict=True):
        a = {
            j
            for i, value in enumerate(x)
            if value
            for j in (2 * (i // 2), 2 * (i // 2) + 1)
        }
        b = {
            j
            for i, value in enumerate(y)
            if value
            for j in (2 * (i // 2), 2 * (i // 2) + 1)
        }
        rows = [
            sum(
                ((labels[i] & labels[j]).bit_count() % 2) << k
                for k, j in enumerate(sorted(b))
            )
            for i in sorted(a)
        ]
        charges.append(binary_rank(rows))
    return charges


def witness():
    w = read(PACKAGE / "WITNESS.json")
    q, u = w["queries"], w["readers"]
    require(
        len(q) == len(u) == 9
        and all(
            len(c) == 6 and all(type(x) is int and abs(x) <= 2 for x in c)
            for c in q + u
        ),
        "witness shape",
    )
    terminal = (0, 0, 0, 0, 1, 0)
    gadget = network(4, BRIDGE, (0, 0, 1))
    mapping = (0, 2, 4, 1, 3)
    mapped = [
        [
            next((c[k] for k, port in enumerate(mapping) if port == j), 0)
            for j in range(6)
        ]
        for c in gadget
    ]
    tail = [
        [1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0],
    ]
    require(
        q == mapped + tail and terminal == tuple(q[0][j] + q[1][j] for j in range(6)),
        "literal graphic dictionary",
    )
    for p in range(6):
        for r in range(6):
            require(
                sum(x[p] * y[r] for x, y in zip(u, q, strict=True))
                == int(p == r and p in (0, 2)),
                "literal operator",
            )
    require(rank(q) == rank(u) == 5, "actual factor ranks")
    require(w["endpoint_diagonal"] == [1, 0, 1, 0, 0, 0], "endpoint declaration")
    require(
        w["labels"] == [1, 2, 4, 8, 16, 32] and w["groups"] == [[0, 1], [2, 3], [4, 5]],
        "binary geometry",
    )
    charges = rectangular_charges(q, u, w["labels"])
    require(charges == w["charges"] and sum(charges) == w["total"] >= 4, "literal bill")
    return {"ranks": [5, 5], "charges": charges, "total": sum(charges), "floor": 4}


def bridge_certificate():
    true = [mask for mask in range(32) if connected(4, BRIDGE, mask)]
    paths = [
        m
        for m in true
        if all((m ^ (1 << i)) not in true for i in range(5) if m >> i & 1)
    ]
    cuts = [
        m
        for m in range(1, 32)
        if (31 ^ m) not in true
        and all((31 ^ (m ^ (1 << i))) in true for i in range(5) if m >> i & 1)
    ]
    require(
        paths == [3, 12, 22, 25] and cuts == [5, 10, 22, 25], "bridge paths and cuts"
    )
    for family in (paths, cuts):
        pairs = [
            (i, j)
            for m in family
            for i in range(5)
            for j in range(i)
            if m >> i & 1 and m >> j & 1
        ]
        reached = {0}
        for _ in range(5):
            for i, j in pairs:
                if i in reached or j in reached:
                    reached.update((i, j))
        require(len(reached) == 5, "non-read-once co-occurrence")
    return {"minimal_paths": paths, "minimal_cuts": cuts, "read_once": False}


def main():
    authenticate()
    actual = {
        "graphs": graph_suite(),
        "marked": marked_suite(),
        "bridge": bridge_certificate(),
        "witness": witness(),
    }
    require(actual == read(PACKAGE / "RESULT.json"), "frozen result")
    print("PASS_GRAPHIC_QUERY_TRANSFER", json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
