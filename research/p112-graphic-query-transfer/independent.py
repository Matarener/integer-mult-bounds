"""Separate path/cut, determinant and GF4-dual certificate implementation."""

import hashlib
import itertools
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
EDGES = ((0, 2), (2, 1), (0, 3), (3, 1), (2, 3))
TABLE = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def check(ok, label):
    if not ok:
        raise ValueError(label)


def load(path):
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 131072,
        "regular bounded data",
    )
    return json.loads(path.read_text())


def sources():
    for item in load(PACKAGE / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            p = ROOT / item["path"]
            check(p.is_file() and not p.is_symlink(), "regular source")
            check(
                hashlib.sha256(p.read_bytes()).hexdigest() == item["sha256"],
                "source integrity",
            )


def determinant(matrix):
    n = len(matrix)
    check(1 <= n <= 5, "determinant bound")
    total = 0
    for perm in itertools.permutations(range(n)):
        term = (-1) ** sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        for i, j in enumerate(perm):
            term *= matrix[i][j]
        total += term
    return total


def rank3(columns):
    if not any(any(c) for c in columns):
        return 0
    for triple in itertools.combinations(columns, 3):
        if determinant(triple):
            return 3
    for a, b in itertools.combinations(columns, 2):
        if any(
            a[i] * b[j] != a[j] * b[i] for i, j in itertools.combinations(range(3), 2)
        ):
            return 2
    return 1


def cut_truth(v, edges, subset):
    for assignment in range(1 << (v - 2)):
        side = [0, 1] + [(assignment >> i) & 1 for i in range(v - 2)]
        if all(
            not (subset >> i & 1) or side[a] == side[b]
            for i, (a, b) in enumerate(edges)
        ):
            return False, side
    return True, None


def path_certificate(v, edges, subset):
    parent = {0: None}
    for _ in range(v):
        for i, (a, b) in enumerate(edges):
            if subset >> i & 1:
                if a in parent and b not in parent:
                    parent[b] = (a, i, 1)
                if b in parent and a not in parent:
                    parent[a] = (b, i, -1)
    check(1 in parent, "primal path exists")
    coefficients = [0] * len(edges)
    vertex = 1
    for _ in range(v):
        if vertex == 0:
            break
        previous, edge, sign = parent[vertex]
        coefficients[edge] = sign
        vertex = previous
    check(vertex == 0, "bounded path")
    return coefficients


def graph_checks():
    result = []
    for v in range(2, 6):
        edges = list(itertools.combinations(range(v), 2))
        columns = [
            tuple(int(b == j) - int(a == j) for j in range(1, v)) for a, b in edges
        ]
        bits = []
        for subset in range(1 << len(edges)):
            truth, side = cut_truth(v, edges, subset)
            if truth:
                coefficients = path_certificate(v, edges, subset)
                check(
                    all(
                        sum(
                            c[j] * x for c, x in zip(columns, coefficients, strict=True)
                        )
                        == int(j == 0)
                        for j in range(v - 1)
                    ),
                    "exact path sum",
                )
            else:
                check(side[1] == 1 and side[0] == 0, "dual normalization")
                check(
                    all(
                        sum(side[j + 1] * c[j] for j in range(v - 1)) == 0
                        for i, c in enumerate(columns)
                        if subset >> i & 1
                    ),
                    "exact cut annihilator",
                )
            bits.append(int(truth))
        result.append(
            {
                "vertices": v,
                "edges": len(edges),
                "subsets": len(bits),
                "truth_sha256": hashlib.sha256(bytes(bits)).hexdigest(),
            }
        )
    return result


def dot4(a, b):
    value = 0
    for x, y in zip(a, b, strict=True):
        value ^= TABLE[x][y]
    return value


def base_predicates(pair, template):
    order = [i for i in range(7) if i not in pair] + pair
    old = [POINTS[i] for i in order]
    new = [template[i] for i in order]
    ranks = [
        rank3([c for i, c in enumerate(old) if subset >> i & 1])
        for subset in range(128)
    ]
    functionals = list(itertools.product(range(4), repeat=3))
    zeros = [
        sum(1 << i for i, c in enumerate(new) if dot4(f, c) == 0) for f in functionals
    ]
    predicates = []
    for subset in range(32):
        row = []
        for j, k in ((32, 64), (64, 32)):
            source = ranks[subset | j | k] > ranks[subset | k]
            reader = ranks[subset | j] == ranks[subset]
            if source:
                check(
                    any(z & (subset | k) == subset | k and not z & j for z in zeros),
                    "dual source transfer",
                )
            if reader:
                check(
                    all(z & subset != subset or z & j for z in zeros),
                    "dual reader transfer",
                )
            row.extend((source, reader))
        predicates.append(row)
    return predicates


def marked_checks():
    data = load(ROOT / "research/p112-query-series-transfer/PREDECESSOR-TEMPLATES.json")
    check(
        data["polynomial"] == 7
        and data["representative_pairs"] == [[0, 1], [0, 3], [3, 4]],
        "template header",
    )
    result = []
    for pair, points in zip(data["representative_pairs"], data["points"], strict=True):
        check(
            len(points) == 7
            and all(
                len(c) == 3 and all(type(x) is int and 0 <= x < 4 for x in c)
                for c in points
            ),
            "template dimensions",
        )
        predicates = base_predicates(pair, points)
        for query in range(5):
            source = reader = 0
            for subset in range(512):
                edge_subset = (subset >> query) & 31
                old_subset = subset & ((1 << query) - 1)
                old_subset |= (subset >> (query + 5)) << (query + 1)
                if cut_truth(4, EDGES, edge_subset)[0]:
                    old_subset |= 1 << query
                row = predicates[old_subset]
                source += row[0] + row[2]
                reader += row[1] + row[3]
            result.append(
                {"pair": pair, "query": query, "source": source, "reader": reader}
            )
    return result


def literal_checks():
    w = load(PACKAGE / "WITNESS.json")
    q, u = w["queries"], w["readers"]
    check(
        len(q) == len(u) == 9
        and all(
            len(c) == 6 and all(type(x) is int and abs(x) <= 2 for x in c)
            for c in q + u
        ),
        "literal shapes",
    )
    expected = [
        [0, 1, 0, 0, 0, 0],
        [0, -1, 0, 0, 1, 0],
        [0, 0, 0, 1, 0, 0],
        [0, 0, 0, -1, 1, 0],
        [0, -1, 0, 1, 0, 0],
        [1, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 1, 0],
    ]
    check(
        q == expected and w["endpoint_diagonal"] == [1, 0, 1, 0, 0, 0],
        "literal dictionary",
    )
    for i, j in itertools.product(range(6), repeat=2):
        check(
            sum(u[k][i] * q[k][j] for k in range(9)) == int(i == j and i in (0, 2)),
            "exact literal endpoint",
        )
    for columns in (q, u):
        check(all(c[5] == 0 for c in columns), "rank upper bound")
        check(
            any(
                determinant([[c[i] for i in range(5)] for c in block])
                for block in itertools.combinations(columns, 5)
            ),
            "rank lower bound",
        )
    check(
        w["labels"] == [1, 2, 4, 8, 16, 32] and w["groups"] == [[0, 1], [2, 3], [4, 5]],
        "identity Gram groups",
    )
    charges = [
        2
        * len(
            {i // 2 for i, x in enumerate(a) if x}
            & {i // 2 for i, x in enumerate(b) if x}
        )
        for a, b in zip(q, u, strict=True)
    ]
    check(
        charges == w["charges"] and sum(charges) == w["total"] >= 4,
        "separate plane bill",
    )
    return {"ranks": [5, 5], "charges": charges, "total": sum(charges), "floor": 4}


def non_read_once():
    truth = [cut_truth(4, EDGES, m)[0] for m in range(32)]

    def minimal(family):
        return [
            m
            for m in range(1, 32)
            if family[m]
            and all(not family[m ^ (1 << i)] for i in range(5) if m >> i & 1)
        ]

    paths = minimal(truth)
    cuts = minimal([not truth[31 ^ m] for m in range(32)])
    for family in (paths, cuts):
        for split in range(1, 31):
            check(
                any(m & split and m & (31 ^ split) for m in family),
                "every root split has co-occurrence",
            )
    return {"minimal_paths": paths, "minimal_cuts": cuts, "read_once": False}


def main():
    sources()
    actual = {
        "graphs": graph_checks(),
        "marked": marked_checks(),
        "bridge": non_read_once(),
        "witness": literal_checks(),
    }
    check(actual == load(PACKAGE / "RESULT.json"), "independent frozen evidence")
    print("PASS_INDEPENDENT_GRAPHIC_TRANSFER", json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
