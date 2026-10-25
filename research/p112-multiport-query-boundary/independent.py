"""Independent minors, annihilator and path/cut replay; no primary imports."""

import hashlib
import json
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
TABLE = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
P = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))


def check(value, name):
    if not value:
        raise ValueError(name)


def read(path):
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size <= 65536,
        "bounded regular source",
    )
    return json.loads(path.read_bytes())


def determinant(rows):
    n = len(rows)
    check(n <= 4 and all(len(r) == n for r in rows), "minor capacity")
    result = 0
    for order in permutations(range(n)):
        sign = (
            -1
            if sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n)) % 2
            else 1
        )
        term = sign
        for i in range(n):
            term *= rows[i][order[i]]
        result += term
    return result


@lru_cache(maxsize=8192)
def rational_rank(columns):
    if not columns:
        return 0
    check(len(columns) <= 8 and len(columns[0]) <= 4, "rank capacity")
    for size in range(min(len(columns), len(columns[0])), 0, -1):
        for cs in combinations(columns, size):
            for rs in combinations(range(len(columns[0])), size):
                if determinant([[c[i] for i in rs] for c in cs]):
                    return size
    return 0


def dot(a, b):
    result = 0
    for x, y in zip(a, b, strict=True):
        result ^= TABLE[x][y]
    return result


def closures(columns):
    check(len(columns) <= 8 and len(columns[0]) <= 4, "annihilator capacity")
    zero_sets = []
    for f in product(range(4), repeat=len(columns[0])):
        zero_sets.append(sum(1 << i for i, c in enumerate(columns) if dot(f, c) == 0))
    result = []
    for mask in range(1 << len(columns)):
        closed = (1 << len(columns)) - 1
        for zeros in zero_sets:
            if mask & zeros == mask:
                closed &= zeros
        result.append(closed)
    return result


def audit(q, m, nq, nm):
    columns = tuple(q + m)
    t = len(q)
    ranks = [
        rational_rank(tuple(c for i, c in enumerate(columns) if mask >> i & 1))
        for mask in range(1 << len(columns))
    ]
    closed = closures(nq + nm)
    check(ranks[3 << t] == 2 and closed[1 << t] & (2 << t) == 0, "independent marks")
    failures = []
    for mask in range(1 << t):
        for j in (0, 1):
            mark, other = 1 << (t + j), 1 << (t + 1 - j)
            if (
                ranks[mask | other | mark] > ranks[mask | other]
                and closed[mask | other] & mark
            ):
                failures.append([mask, j, "source"])
            if ranks[mask | mark] == ranks[mask] and closed[mask] & mark == 0:
                failures.append([mask, j, "reader"])
    return failures


def all_cases():
    data = read(BASE / "research/p112-query-series-transfer/PREDECESSOR-TEMPLATES.json")
    check(
        data["polynomial"] == 7
        and data["representative_pairs"] == [[0, 1], [0, 3], [3, 4]],
        "templates",
    )
    check(len(data["points"]) == 3, "case count")
    results = []
    for marks, mapped in zip(data["representative_pairs"], data["points"], strict=True):
        check(
            len(mapped) == 7
            and all(
                len(c) == 3 and all(type(x) is int and 0 <= x < 4 for x in c)
                for c in mapped
            ),
            "field values",
        )
        indices = [i for i in range(7) if i not in marks]
        q, nq = [P[i] for i in indices], [tuple(mapped[i]) for i in indices]
        m, nm = [P[i] for i in marks], [tuple(mapped[i]) for i in marks]
        check(not audit(q, m, nq, nm), "base transfer")
        for a, b in combinations(indices, 2):
            keep = [i for i in indices if i not in (a, b)]
            old = [(*P[i], 0) for i in keep] + [(0, 0, 0, 1), (*P[a], -1), (*P[b], -1)]
            new = [(*mapped[i], 0) for i in keep] + [
                (0, 0, 0, 1),
                (*mapped[a], 1),
                (*mapped[b], 1),
            ]
            fails = audit(old, [(*x, 0) for x in m], new, [(*x, 0) for x in nm])
            results.append(
                {
                    "marks": marks,
                    "ports": [a, b],
                    "source_failures": sum(x[2] == "source" for x in fails),
                    "reader_failures": sum(x[2] == "reader" for x in fails),
                    "first_failure": fails[0] if fails else None,
                }
            )
    return results


def literal():
    w = read(HERE / "WITNESS.json")
    q, u = w["queries"], w["readers"]
    check(len(q) == len(u) == 6 and all(len(c) == 4 for c in q + u), "literal shape")
    check(
        q
        == [
            [1, 1, 0, 0],
            [1, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 1, -1],
            [0, 1, 1, -1],
        ],
        "query binding",
    )
    check(
        all(type(x) is int and abs(x) <= 4 for c in q + u for x in c),
        "coefficient bounds",
    )
    for i, j in product(range(4), repeat=2):
        check(
            sum(u[k][i] * q[k][j] for k in range(6)) == int(i == j and i < 2),
            "endpoint",
        )
    check(
        rational_rank(tuple(map(tuple, q))) == rational_rank(tuple(map(tuple, u))) == 4,
        "factor ranks",
    )
    check(
        w["groups"] == [[0, 1], [2, 3]] and w["binary_labels"] == [1, 2, 4, 8],
        "label model",
    )
    costs = [
        sum(2 for i in (0, 2) if any(a[i : i + 2]) and any(b[i : i + 2]))
        for a, b in zip(q, u, strict=True)
    ]
    check(costs == w["charges"] and sum(costs) == w["total_charge"], "charge")
    return {"ranks": [4, 4], "charges": costs, "total": sum(costs), "baseline": 4}


def path_or_cut(selected, potentials, a, b):
    paths = {a: ()}
    for _ in range(4):
        for x, y in selected:
            for u, v in ((x, y), (y, x)):
                if u in paths and v not in paths:
                    paths[v] = (*paths[u], (u, v))
    if b in paths:
        check(len(paths[b]) <= 4, "simple path capacity")
        summed = [
            sum(potentials[y][i] - potentials[x][i] for x, y in paths[b])
            for i in range(4)
        ]
        check(
            summed == [potentials[b][i] - potentials[a][i] for i in range(4)],
            "path certificate",
        )
        return
    cut = [int(v not in paths) - int(0 not in paths) for v in range(1, 5)]
    check(
        all(
            sum(c * (potentials[y][i] - potentials[x][i]) for i, c in enumerate(cut))
            == 0
            for x, y in selected
        ),
        "cut annihilation",
    )
    check(
        sum(c * (potentials[b][i] - potentials[a][i]) for i, c in enumerate(cut)) != 0,
        "cut separates",
    )


def projection():
    edges = list(combinations(range(5), 2))
    potentials = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    for mask in range(1024):
        selected = [edge for i, edge in enumerate(edges) if mask >> i & 1]
        for a, b in combinations(range(3), 2):
            path_or_cut(selected, potentials, a, b)
        # Every GF4 boundary functional must extend iff constant on terminal components.
        extensions = set()
        for values in product(range(4), repeat=4):
            labels = (0, *values)
            if all(labels[x] == labels[y] for x, y in selected):
                extensions.add(values[:2])
        predicted = set()
        for v1, v2 in product(range(4), repeat=2):
            labels = (0, v1, v2)
            ok = True
            for start in range(3):
                seen = {start}
                for _ in range(4):
                    seen |= {
                        v for x, y in selected for u, v in ((x, y), (y, x)) if u in seen
                    }
                ok = ok and all(
                    labels[start] == labels[end] for end in range(3) if end in seen
                )
            if ok:
                predicted.add((v1, v2))
        check(extensions == predicted, "complete boundary annihilators")
    return {"vertices": 5, "terminals": 3, "edge_subsets": 1024, "fields": ["Q", "GF4"]}


def main():
    for row in read(HERE / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            check(
                hashlib.sha256((BASE / row["path"]).read_bytes()).hexdigest()
                == row["sha256"],
                "source hash",
            )
    rows = all_cases()
    actual = {
        "cases": rows,
        "safe": sum(r["first_failure"] is None for r in rows),
        "unsafe": sum(r["first_failure"] is not None for r in rows),
        "literal": literal(),
        "projection": projection(),
    }
    check(actual == read(HERE / "RESULT.json"), "independent exact result")
    print("PASS_INDEPENDENT_MULTIPORT_QUERY_BOUNDARY")
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    main()
