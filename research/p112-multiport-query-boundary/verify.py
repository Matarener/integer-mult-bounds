"""Exact two-port interface audit. No predecessor executable imports."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    require(path.is_file() and not path.is_symlink(), "regular input")
    require(path.stat().st_size <= 65536, "input capacity")
    return json.loads(path.read_text())


def mul(a, b):
    result = 0
    for _ in range(2):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return result


def rank(columns, field):
    require(len(columns) <= 12, "column capacity")
    if not columns:
        return 0
    require(len(columns[0]) <= 5, "dimension capacity")
    rows = [list(c) if field == 4 else list(map(Fraction, c)) for c in columns]
    count = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(count, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        value = rows[count][j]
        if field == 4:
            inverse = next(x for x in (1, 2, 3) if mul(value, x) == 1)
            rows[count] = [mul(x, inverse) for x in rows[count]]
        else:
            rows[count] = [x / value for x in rows[count]]
        for i in range(count + 1, len(rows)):
            scale = rows[i][j]
            rows[i] = [
                x ^ mul(scale, y) if field == 4 else x - scale * y
                for x, y in zip(rows[i], rows[count], strict=True)
            ]
        count += 1
        if count == len(rows):
            break
    return count


def contains(columns, vector, field):
    return rank(columns, field) == rank([*columns, vector], field)


def difference(a, b, field):
    return tuple(x ^ y if field == 4 else x - y for x, y in zip(a, b, strict=True))


def violations(queries, marks, mapped_queries, mapped_marks):
    failures = []
    require(len(queries) == len(mapped_queries) <= 6, "query capacity")
    for mask in range(1 << len(queries)):
        old = [q for i, q in enumerate(queries) if mask >> i & 1]
        new = [q for i, q in enumerate(mapped_queries) if mask >> i & 1]
        for j in (0, 1):
            if not contains([*old, marks[1 - j]], marks[j], 0) and contains(
                [*new, mapped_marks[1 - j]], mapped_marks[j], 4
            ):
                failures.append([mask, j, "source"])
            if contains(old, marks[j], 0) and not contains(new, mapped_marks[j], 4):
                failures.append([mask, j, "reader"])
    return failures


def star(queries, pair, field):
    a, b = pair
    result = [tuple(q) + (0,) for i, q in enumerate(queries) if i not in pair]
    result.extend(
        (
            (0, 0, 0, 1),
            (*queries[a], -1 if field == 0 else 1),
            (*queries[b], -1 if field == 0 else 1),
        )
    )
    return result


def cases():
    data = load(REPO / "research/p112-query-series-transfer/PREDECESSOR-TEMPLATES.json")
    require(data["polynomial"] == 7, "GF4 polynomial")
    require(data["representative_pairs"] == [[0, 1], [0, 3], [3, 4]], "marked cases")
    require(len(data["points"]) == 3, "template count")
    result = []
    for marks, template in zip(
        data["representative_pairs"], data["points"], strict=True
    ):
        require(
            len(template) == 7 and all(len(c) == 3 for c in template), "template shape"
        )
        require(
            all(type(x) is int and 0 <= x < 4 for c in template for x in c),
            "GF4 values",
        )
        indices = [i for i in range(7) if i not in marks]
        q, m = [POINTS[i] for i in indices], [POINTS[i] for i in marks]
        nq, nm = (
            [tuple(template[i]) for i in indices],
            [tuple(template[i]) for i in marks],
        )
        require(not violations(q, m, nq, nm), "inherited base transfer")
        for pair in combinations(range(5), 2):
            sq, snq = star(q, pair, 0), star(nq, pair, 4)
            sm, snm = [(*c, 0) for c in m], [(*c, 0) for c in nm]
            full = violations(sq, sm, snq, snm)
            rest = [c for i, c in enumerate(q) if i not in pair]
            nrest = [c for i, c in enumerate(nq) if i not in pair]
            reduced = violations(
                [*rest, difference(q[pair[0]], q[pair[1]], 0)],
                m,
                [*nrest, difference(nq[pair[0]], nq[pair[1]], 4)],
                nm,
            )
            require(bool(full) == bool(reduced), "terminal-partition criterion")
            result.append(
                {
                    "marks": marks,
                    "ports": [indices[i] for i in pair],
                    "source_failures": sum(x[2] == "source" for x in full),
                    "reader_failures": sum(x[2] == "reader" for x in full),
                    "first_failure": full[0] if full else None,
                }
            )
    return result


def witness():
    data = load(ROOT / "WITNESS.json")
    q, u = data["queries"], data["readers"]
    require(len(q) == len(u) == 6 and all(len(c) == 4 for c in q + u), "literal shape")
    require(
        all(type(x) is int and abs(x) <= 4 for c in q + u for x in c), "literal values"
    )
    expected_q = star([POINTS[i] for i in (2, 3, 4, 5, 6)], (0, 3), 0)
    require(q == [list(c) for c in expected_q], "literal star binding")
    product = [
        [sum(x[i] * y[j] for x, y in zip(u, q, strict=True)) for j in range(4)]
        for i in range(4)
    ]
    require(
        product == [[int(i == j and i < 2) for j in range(4)] for i in range(4)],
        "literal product",
    )
    require(rank(q, 0) == rank(u, 0) == 4, "actual factor ranks")
    require(data["binary_labels"] == [1, 2, 4, 8], "orthogonal labels")
    require(data["groups"] == [[0, 1], [2, 3]], "complete plane partition")
    charges = []
    for x, y in zip(u, q, strict=True):
        closed_u = {i for i in range(4) if x[i // 2 * 2] or x[i // 2 * 2 + 1]}
        closed_q = {i for i in range(4) if y[i // 2 * 2] or y[i // 2 * 2 + 1]}
        charges.append(len(closed_u & closed_q))
    require(
        charges == data["charges"] and sum(charges) == data["total_charge"],
        "literal bill",
    )
    return {"ranks": [4, 4], "charges": charges, "total": sum(charges), "baseline": 4}


def projection_suite():
    edges = list(combinations(range(5), 2))
    potentials = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    for mask in range(1024):
        component = list(range(5))
        selected = [edge for i, edge in enumerate(edges) if mask >> i & 1]
        for a, b in selected:
            old, new = component[b], component[a]
            component = [new if c == old else c for c in component]
        generators = [
            difference(potentials[b], potentials[a], 0)
            for a, b in combinations(range(3), 2)
            if component[a] == component[b]
        ]
        for field in (0, 4):
            columns = [
                difference(potentials[b], potentials[a], field) for a, b in selected
            ]
            boundary = [
                tuple(x % 2 for x in g) if field == 4 else g for g in generators
            ]
            dim = rank(columns, field) - rank([c[2:] for c in columns], field)
            require(dim == rank(boundary, field), "boundary intersection dimension")
            require(
                all(contains(columns, g, field) for g in boundary), "boundary inclusion"
            )
    return {"vertices": 5, "terminals": 3, "edge_subsets": 1024, "fields": ["Q", "GF4"]}


def main():
    for row in load(ROOT / "SOURCES.json")["files"]:
        if row["usage"] == "input":
            require(
                hashlib.sha256((REPO / row["path"]).read_bytes()).hexdigest()
                == row["sha256"],
                "source hash",
            )
    rows = cases()
    result = {
        "cases": rows,
        "safe": sum(x["first_failure"] is None for x in rows),
        "unsafe": sum(x["first_failure"] is not None for x in rows),
        "literal": witness(),
        "projection": projection_suite(),
    }
    require(result == load(ROOT / "RESULT.json"), "exact scientific result")
    print("PASS_MULTIPORT_QUERY_BOUNDARY")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
