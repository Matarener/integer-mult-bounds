"""Exact two-port boundary and hub transfer checks. Standard library only."""

import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
POINTS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1))
PAIRS = ((0, 1), (0, 3), (3, 4))
MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(name):
    path = HERE / name
    require(path.is_file() and not path.is_symlink(), "regular input: " + name)
    require(path.stat().st_size <= 65536, "bounded input: " + name)
    return json.loads(path.read_text())


def rank(columns, field=False):
    if not columns:
        return 0
    rows = [list(v) if field else list(map(Fraction, v)) for v in columns]
    count = 0
    for j in range(len(rows[0])):
        pivot = next((i for i in range(count, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[count], rows[pivot] = rows[pivot], rows[count]
        scale = rows[count][j]
        if field:
            inv = next(i for i in range(1, 4) if MUL[scale][i] == 1)
            rows[count] = [MUL[inv][x] for x in rows[count]]
        else:
            rows[count] = [x / scale for x in rows[count]]
        for i in range(count + 1, len(rows)):
            scale = rows[i][j]
            if field:
                rows[i] = [
                    x ^ MUL[scale][y] for x, y in zip(rows[i], rows[count], strict=True)
                ]
            else:
                rows[i] = [
                    x - scale * y for x, y in zip(rows[i], rows[count], strict=True)
                ]
        count += 1
        if count == len(rows):
            break
    return count


def contains(columns, v, field=False):
    return rank(columns + [v], field) == rank(columns, field)


def flags(queries, marks, field=False):
    require(len(queries) <= 6 and len(marks) == 2, "finite flag capacity")
    result = []
    for mask in range(1 << len(queries)):
        selected = [v for i, v in enumerate(queries) if mask >> i & 1]
        result.append(
            tuple(
                (
                    not contains(selected + [marks[1 - j]], marks[j], field),
                    contains(selected, marks[j], field),
                )
                for j in range(2)
            )
        )
    return result


def compare(old, new):
    sources = readers = 0
    failures = []
    for mask, (before, after) in enumerate(zip(old, new, strict=True)):
        for mark in range(2):
            for kind in range(2):
                if before[mark][kind]:
                    sources += kind == 0
                    readers += kind == 1
                    if not after[mark][kind]:
                        failures.append((mask, mark, kind))
    return sources, readers, failures


def shapes(data):
    require(data["schema"] == 1 and data["polynomial"] == 7, "map format/field")
    require(data["points"] == [list(p) for p in POINTS], "exact old representatives")
    wanted = [
        (list(m), list(p))
        for m in PAIRS
        for p in combinations([i for i in range(7) if i not in m], 2)
    ]
    require(
        [(r["marks"], r["ports"]) for r in data["cases"]] == wanted,
        "ordered 30-case coverage",
    )
    for row in data["cases"]:
        points = row["coherent_points"]
        if points is None:
            require(
                row["marks"] == [0, 1] and row["ports"] == [4, 5],
                "unique exceptional case",
            )
            points, dim = row["star_queries"], 4
            require(len(points) == 6, "exceptional query count")
        else:
            dim = 3
            require(len(points) == 7, "coherent point count")
            require(
                all(points[i] == list(POINTS[i]) for i in row["marks"]), "fixed marks"
            )
        require(
            all(
                len(v) == dim and all(type(x) is int and 0 <= x < 4 for x in v)
                for v in points
            ),
            "bounded GF4 columns",
        )


def star(points, ports, field=False):
    e, f = ports
    # The caller supplies all seven points and determines the unreplaced indices.
    h = (0, 0, 0, 1)
    x = tuple(points[e]) + ((1 if field else -1),)
    y = tuple(points[f]) + ((1 if field else -1),)
    return h, x, y


def configurations(row, points, field=False):
    marks = [tuple(points[i]) for i in row["marks"]]
    ids = [i for i in range(7) if i not in row["marks"]]
    e, f = row["ports"]
    rest = [i for i in ids if i not in (e, f)]
    diff = tuple(
        x ^ y if field else x - y for x, y in zip(points[e], points[f], strict=True)
    )
    h, x, y = star(points, (e, f), field)
    return (
        ([tuple(points[i]) for i in ids], marks),
        ([tuple(points[i]) for i in rest] + [diff], marks),
        (
            [tuple(points[i]) + (0,) for i in rest] + [h, x, y],
            [v + (0,) for v in marks],
        ),
    )


def exceptional_premises():
    e, f, g, d, b, c, t = [POINTS[i] for i in (0, 1, 2, 3, 4, 5, 6)]
    r = tuple(x - y for x, y in zip(b, c, strict=True))
    reads = [
        ([g, b], e),
        ([g, c], f),
        ([c, t], e),
        ([b, t], f),
        ([d, r], e),
        ([d, r], f),
        ([g, t, r], e),
        ([g, t, r], f),
    ]
    sources = [([f, g], e), ([e, g], f), ([f, b], e), ([e, c], f), ([f, t], e)]
    require(all(contains(q, v) for q, v in reads), "obstruction reader premises")
    require(all(not contains(q, v) for q, v in sources), "obstruction source premises")
    return {"reader_premises": len(reads), "source_premises": len(sources)}


def source_bytes():
    sources = read_json("SOURCES.json")
    for entry in sources["files"]:
        if entry["usage"] == "input":
            path = HERE.parents[1] / entry["path"]
            require(
                path.is_file() and not path.is_symlink(), "live source regular file"
            )
            require(path.stat().st_size <= 65536, "live source capacity")
            require(
                hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                "live source hash",
            )


def extremal(predicates):
    out = []
    for j in range(2):
        readers = [m for m, row in enumerate(predicates) if row[j][1]]
        sources = [m for m, row in enumerate(predicates) if row[j][0]]
        minimal = [
            m for m in readers if not any(k != m and k & m == k for k in readers)
        ]
        maximal = [
            m for m in sources if not any(k != m and k & m == m for k in sources)
        ]
        out.append({"minimal_readers": minimal, "maximal_sources": maximal})
    return out


def calculate():
    source_bytes()
    data = read_json("MAPS.json")
    shapes(data)
    source = reader = 0
    templates = read_json("../p112-query-series-transfer/PREDECESSOR-TEMPLATES.json")[
        "points"
    ]
    old_compatible = 0
    stream = hashlib.sha256()
    results = []
    exceptional_extremal = None
    for row in data["cases"]:
        old = configurations(row, POINTS)
        old_flags = [flags(*config) for config in old]
        baseline = configurations(
            row, templates[PAIRS.index(tuple(row["marks"]))], True
        )
        baseline_good = all(
            not compare(before, flags(*after, True))[2]
            for before, after in zip(old_flags[:2], baseline[:2], strict=True)
        )
        old_compatible += baseline_good
        points = row["coherent_points"]
        checks = []
        if points is not None:
            new = configurations(row, points, True)
            checks = [flags(*config, True) for config in new]
        else:
            marks = [POINTS[i] + (0,) for i in row["marks"]]
            checks = [flags([tuple(v) for v in row["star_queries"]], marks, True)]
            old_flags = old_flags[2:]
            exceptional_extremal = extremal(old_flags[0])
        counts = []
        for before, after in zip(old_flags, checks, strict=True):
            ns, nr, bad = compare(before, after)
            require(
                not bad, "transfer failure " + str((row["marks"], row["ports"], bad))
            )
            source += ns
            reader += nr
            counts.append([ns, nr])
            stream.update(json.dumps([before, after], separators=(",", ":")).encode())
        results.append(
            {
                "marks": row["marks"],
                "ports": row["ports"],
                "coherent": points is not None,
                "previous_fixed_map": baseline_good,
                "counts": counts,
            }
        )
    require(sum(r["coherent"] for r in results) == 29, "29 coherent constructions")
    require(old_compatible == 13, "13 predecessor fixed maps")
    return {
        "cases": results,
        "previous_fixed_coherent": old_compatible,
        "coherent_cases": 29,
        "star_cases": 30,
        "source_premises": source,
        "reader_premises": reader,
        "stream_sha256": stream.hexdigest(),
        "obstruction": exceptional_premises(),
        "exceptional_extremal": exceptional_extremal,
    }


def main():
    result = calculate()
    require(result == read_json("RESULT.json"), "result table mismatch")
    print("PASS_TWO_PORT_TRANSFER", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
