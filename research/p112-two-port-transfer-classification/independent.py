"""Separate integer-minor and GF4 dual-functional check of the exact map table."""

import hashlib
import json
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path

DIR = Path(__file__).resolve().parent
P = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
MARKS = ((0, 1), (0, 3), (3, 4))


def check(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    path = DIR / name
    check(
        not path.is_symlink() and path.is_file() and path.stat().st_size <= 65536,
        "bounded regular fixture",
    )
    return json.loads(path.read_text())


def times(a, b):
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return value


def det(rows):
    size = len(rows)
    total = 0
    for perm in permutations(range(size)):
        sign = (
            -1
            if sum(perm[i] > perm[j] for i in range(size) for j in range(i + 1, size))
            % 2
            else 1
        )
        term = sign
        for i in range(size):
            term *= rows[i][perm[i]]
        total += term
    return total


@lru_cache(maxsize=16384)
def integer_rank(columns):
    if not columns:
        return 0
    dim = len(columns[0])
    check(dim <= 4 and len(columns) <= 8, "minor capacity")
    for k in range(min(dim, len(columns)), 0, -1):
        for selected in combinations(columns, k):
            for axes in combinations(range(dim), k):
                if det(tuple(tuple(v[j] for j in axes) for v in selected)):
                    return k
    return 0


def dot(a, b):
    value = 0
    for x, y in zip(a, b, strict=True):
        value ^= times(x, y)
    return value


@lru_cache(maxsize=2048)
def annihilators(v):
    result = 0
    for i, functional in enumerate(product(range(4), repeat=len(v))):
        if dot(functional, v) == 0:
            result |= 1 << i
    return result


def predicates(queries, marks, target=False):
    check(len(queries) <= 6 and len(marks[0]) <= 4, "predicate capacity")
    answer = []
    for mask in range(1 << len(queries)):
        cols = tuple(v for i, v in enumerate(queries) if mask >> i & 1)
        if target:
            null = (1 << (4 ** len(marks[0]))) - 1
            for v in cols:
                null &= annihilators(v)
            row = tuple(
                (
                    bool((null & annihilators(marks[1 - j])) & ~annihilators(marks[j])),
                    not bool(null & ~annihilators(marks[j])),
                )
                for j in range(2)
            )
        else:
            rank = integer_rank(cols)
            row = tuple(
                (
                    integer_rank(cols + (marks[1 - j], marks[j]))
                    > integer_rank(cols + (marks[1 - j],)),
                    integer_rank(cols + (marks[j],)) == rank,
                )
                for j in range(2)
            )
        answer.append(row)
    return answer


def transfer(a, b):
    n = [0, 0]
    good = True
    for before, after in zip(a, b, strict=True):
        for j, kind in product(range(2), repeat=2):
            if before[j][kind]:
                n[kind] += 1
                good &= after[j][kind]
    return n, good


def build(row, points, target=False):
    e, f = row["ports"]
    marks = tuple(tuple(points[i]) for i in row["marks"])
    ids = tuple(i for i in range(7) if i not in row["marks"])
    rest = tuple(i for i in ids if i not in (e, f))
    difference = tuple(
        x ^ y if target else x - y for x, y in zip(points[e], points[f], strict=True)
    )
    q0 = tuple(tuple(points[i]) for i in ids)
    q1 = tuple(tuple(points[i]) for i in rest) + (difference,)
    last = 1 if target else -1
    q2 = tuple(tuple(points[i]) + (0,) for i in rest) + (
        (0, 0, 0, 1),
        tuple(points[e]) + (last,),
        tuple(points[f]) + (last,),
    )
    return ((q0, marks), (q1, marks), (q2, tuple(v + (0,) for v in marks)))


def input_shapes(data):
    check(data["schema"] == 1 and data["polynomial"] == 7, "field metadata")
    check(data["points"] == [list(v) for v in P], "old representatives")
    wanted = [
        (list(m), list(p))
        for m in MARKS
        for p in combinations([i for i in range(7) if i not in m], 2)
    ]
    check([(r["marks"], r["ports"]) for r in data["cases"]] == wanted, "case inventory")
    for row in data["cases"]:
        points = row["coherent_points"]
        if points is None:
            check((row["marks"], row["ports"]) == ([0, 1], [4, 5]), "exception key")
            points, dim, size = row["star_queries"], 4, 6
        else:
            dim, size = 3, 7
            check(
                all(points[i] == list(P[i]) for i in row["marks"]), "fixed mark columns"
            )
        check(len(points) == size, "fixture length")
        check(
            all(
                len(v) == dim and all(type(x) is int and 0 <= x < 4 for x in v)
                for v in points
            ),
            "finite field entries",
        )


def proof_premises():
    a, b, g, d, x, y, t = [P[i] for i in (0, 1, 2, 3, 4, 5, 6)]
    r = tuple(u - v for u, v in zip(x, y, strict=True))
    readers = [
        ((g, x), a),
        ((g, y), b),
        ((y, t), a),
        ((x, t), b),
        ((d, r), a),
        ((d, r), b),
        ((g, t, r), a),
        ((g, t, r), b),
    ]
    sources = [((b, g), a), ((a, g), b), ((b, x), a), ((a, y), b), ((b, t), a)]
    check(
        all(integer_rank(q + (v,)) == integer_rank(q) for q, v in readers),
        "all obstruction readers",
    )
    check(
        all(integer_rank(q + (v,)) > integer_rank(q) for q, v in sources),
        "all obstruction sources",
    )
    return {"reader_premises": len(readers), "source_premises": len(sources)}


def input_bytes():
    for entry in load("SOURCES.json")["files"]:
        if entry["usage"] == "input":
            p = DIR.parents[1] / entry["path"]
            check(
                p.is_file() and not p.is_symlink() and p.stat().st_size <= 65536,
                "source file boundary",
            )
            check(
                hashlib.sha256(p.read_bytes()).hexdigest() == entry["sha256"],
                "source digest",
            )


def extrema(table):
    result = []
    for j in range(2):
        readers, sources = [], []
        for mask, row in enumerate(table):
            if row[j][1] and not any(
                table[mask ^ (1 << i)][j][1] for i in range(6) if mask >> i & 1
            ):
                readers.append(mask)
            if row[j][0] and not any(
                table[mask | (1 << i)][j][0] for i in range(6) if not mask >> i & 1
            ):
                sources.append(mask)
        result.append({"minimal_readers": readers, "maximal_sources": sources})
    return result


def calculate():
    input_bytes()
    data = load("MAPS.json")
    input_shapes(data)
    templates = load("../p112-query-series-transfer/PREDECESSOR-TEMPLATES.json")[
        "points"
    ]
    rows, source_count, reader_count, fixed_count = [], 0, 0, 0
    stream = hashlib.sha256()
    exceptional_extremal = None
    for row in data["cases"]:
        old = [predicates(*v) for v in build(row, P)]
        baseline = build(row, templates[MARKS.index(tuple(row["marks"]))], True)
        fixed_good = all(
            transfer(a, predicates(*b, True))[1]
            for a, b in zip(old[:2], baseline[:2], strict=True)
        )
        fixed_count += fixed_good
        coherent = row["coherent_points"] is not None
        if coherent:
            new = [
                predicates(*v, True) for v in build(row, row["coherent_points"], True)
            ]
        else:
            marks = tuple(P[i] + (0,) for i in row["marks"])
            new = [
                predicates(tuple(tuple(v) for v in row["star_queries"]), marks, True)
            ]
            old = old[2:]
            exceptional_extremal = extrema(old[0])
        counts = []
        for a, b in zip(old, new, strict=True):
            count, good = transfer(a, b)
            check(good, "marked transfer failed: " + str((row["marks"], row["ports"])))
            counts.append(count)
            source_count += count[0]
            reader_count += count[1]
            stream.update(json.dumps([a, b], separators=(",", ":")).encode())
        rows.append(
            {
                "marks": row["marks"],
                "ports": row["ports"],
                "coherent": coherent,
                "previous_fixed_map": fixed_good,
                "counts": counts,
            }
        )
    check(
        sum(row["coherent"] for row in rows) == 29 and fixed_count == 13,
        "classification totals",
    )
    return {
        "cases": rows,
        "previous_fixed_coherent": fixed_count,
        "coherent_cases": 29,
        "star_cases": 30,
        "source_premises": source_count,
        "reader_premises": reader_count,
        "stream_sha256": stream.hexdigest(),
        "obstruction": proof_premises(),
        "exceptional_extremal": exceptional_extremal,
    }


def main():
    result = calculate()
    check(result == load("RESULT.json"), "result table mismatch")
    print("PASS_INDEPENDENT_TWO_PORT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
