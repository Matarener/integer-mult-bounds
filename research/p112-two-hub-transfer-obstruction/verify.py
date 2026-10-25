"""Exact premises and literal support obstruction. Standard library only."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
MUL = ((0, 0, 0, 0), (0, 1, 2, 3), (0, 2, 3, 1), (0, 3, 1, 2))
NAMES = "gdthxykzw"
QUERIES = (
    (0, 0, 1, 0, 0),
    (1, 1, 0, 0, 0),
    (1, 1, 1, 0, 0),
    (0, 0, 0, 1, 0),
    (1, 0, 1, -1, 0),
    (0, 1, 1, -1, 0),
    (0, 0, 0, 0, 1),
    (1, 0, 1, 0, -1),
    (0, 1, 1, 0, -1),
)
MARKS = ((1, 0, 0, 0, 0), (0, 1, 0, 0, 0))
SOURCES = (
    (0, "ghk"),
    (1, "ghk"),
    (0, "hx"),
    (0, "gx"),
    (0, "ghz"),
    (1, "gy"),
    (1, "hy"),
)
READERS = (
    (0, "ghx"),
    (1, "ghy"),
    (0, "gkz"),
    (1, "gkw"),
    (0, "thy"),
    (1, "thx"),
    (0, "tkw"),
    (1, "tkz"),
    (0, "dxy"),
    (1, "dxy"),
    (0, "dzw"),
    (1, "dzw"),
    (0, "gtxy"),
    (1, "gtxy"),
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(name):
    path = HERE / name
    require(path.is_file() and not path.is_symlink(), "regular input: " + name)
    require(path.stat().st_size <= 1048576, "bounded input: " + name)
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
            rows[i] = [
                x ^ MUL[scale][y] if field else x - scale * y
                for x, y in zip(rows[i], rows[count], strict=True)
            ]
        count += 1
        if count == len(rows):
            break
    return count


def contains(columns, vector, field=False):
    return rank(columns + [vector], field) == rank(columns, field)


def flags(queries, marks, field=False):
    require(len(queries) <= 9, "subset capacity")
    out = []
    for mask in range(1 << len(queries)):
        selected = [v for i, v in enumerate(queries) if mask >> i & 1]
        out.append(
            tuple(
                (
                    not contains(selected + [marks[1 - j]], marks[j], field),
                    contains(selected, marks[j], field),
                )
                for j in range(2)
            )
        )
    return out


def extremal(table):
    result = []
    for mark in range(2):
        readers = [m for m, row in enumerate(table) if row[mark][1]]
        sources = [m for m, row in enumerate(table) if row[mark][0]]
        result.append(
            {
                "minimal_readers": [
                    m
                    for m in readers
                    if not any(k != m and k & m == k for k in readers)
                ],
                "maximal_sources": [
                    m
                    for m in sources
                    if not any(k != m and k & m == m for k in sources)
                ],
            }
        )
    return result


def validate_config():
    config = read("CONFIG.json")
    require(config["queries"] == [list(v) for v in QUERIES], "two-hub geometry")
    require(config["marks"] == [list(v) for v in MARKS], "independent marks")
    require(config["query_names"] == NAMES, "query indexing")
    require(
        config["premises"]
        == {
            "source": [list(v) for v in SOURCES],
            "reader": [list(v) for v in READERS],
        },
        "complete obstruction premises",
    )
    for kind, premises in ((0, SOURCES), (1, READERS)):
        for mark, letters in premises:
            selected = [QUERIES[NAMES.index(c)] for c in letters]
            predicate = (
                not contains(selected + [MARKS[1 - mark]], MARKS[mark])
                if kind == 0
                else contains(selected, MARKS[mark])
            )
            require(predicate, "obstruction premise")


def star_control():
    origin = read("ORIGINS.json")
    require(
        hashlib.sha256((HERE / "PREDECESSOR-MAPS.json").read_bytes()).hexdigest()
        == origin["sha256"],
        "retained predecessor bytes",
    )
    old = [v[:4] for v in QUERIES[:6]]
    data = read("PREDECESSOR-MAPS.json")
    row = next(
        r for r in data["cases"] if r["marks"] == [0, 1] and r["ports"] == [4, 5]
    )
    new = row["star_queries"]
    require(
        len(new) == 6
        and all(
            len(v) == 4 and all(type(x) is int and 0 <= x < 4 for x in v) for v in new
        ),
        "GF4 star shape",
    )
    marks = [v[:4] for v in MARKS]
    before, after = flags(old, marks), flags(new, marks, True)
    for a, b in zip(before, after, strict=True):
        require(
            all(not a[j][k] or b[j][k] for j in range(2) for k in range(2)),
            "one-star transfer",
        )
    return before, after


def witness_rows():
    rows = [
        (kind, mark, letters)
        for kind, data in (("source", SOURCES), ("reader", READERS))
        for mark, letters in data
    ]
    return sorted(rows, key=lambda row: row[1])


def full_operator(specs, readers, queries):
    entries = 0
    for p in range(42):
        for r in range(42):
            actual = (
                sum(readers[p // 2][i] * queries[r // 2][i] for i in range(9))
                if p % 2 == r % 2 == 0
                else 0
            )
            expected = int(p % 2 == r % 2 == 0 and specs[p // 2][1] == specs[r // 2][1])
            require(actual == expected, "literal full operator")
            entries += 1
    return entries


def literal_witness():
    data = read("WITNESS.json")
    specs = witness_rows()
    require(data["rows"] == [list(v) for v in specs], "literal premise coverage")
    require(
        len(data["functionals"]) == len(data["readers"]) == 21, "literal row capacity"
    )
    functions = [[Fraction(x) for x in v] for v in data["functionals"]]
    readers = [[Fraction(x) for x in v] for v in data["readers"]]
    require(
        all(len(v) == 5 for v in functions) and all(len(v) == 9 for v in readers),
        "literal matrix shape",
    )
    require(rank(functions) == 5, "injective coordinate embedding")
    require(
        all(x.denominator == 1 for fn in functions for x in fn)
        and all(x.denominator in (1, 2) for u in readers for x in u),
        "odd-characteristic premise certificates",
    )
    queries = [
        [sum(a * b for a, b in zip(fn, q, strict=True)) for q in QUERIES]
        for fn in functions
    ]
    for (kind, mark, letters), fn, u, q in zip(
        specs, functions, readers, queries, strict=True
    ):
        require(fn[mark] == 1 and fn[1 - mark] == 0, "literal indicator values")
        require(
            all(
                sum(u[i] * QUERIES[i][j] for i in range(9)) == MARKS[mark][j]
                for j in range(5)
            ),
            "literal reader identity",
        )
        if kind == "source":
            require(
                all(q[NAMES.index(c)] == 0 for c in letters), "literal source zeros"
            )
        else:
            require(
                all(not u[i] or NAMES[i] in letters for i in range(9)),
                "literal reader support",
            )
    entries = full_operator(specs, readers, queries)
    charges = [
        2
        * sum(bool(u[i]) and bool(q[i]) for u, q in zip(readers, queries, strict=True))
        for i in range(9)
    ]
    return {
        "ports": 42,
        "group_sizes": [24, 18],
        "query_rank": rank(queries),
        "reader_rank": rank(readers),
        "operator_entries": entries,
        "charges": charges,
        "bill": sum(charges),
        "original_bill": 42,
    }


def calculate():
    validate_config()
    table = flags(list(QUERIES), list(MARKS))
    before, after = star_control()
    stream = json.dumps([table, before, after], separators=(",", ":")).encode()
    return {
        "two_hub_subsets": 512,
        "one_star_subsets": 64,
        "two_hub_source_premises": sum(r[j][0] for r in table for j in range(2)),
        "two_hub_reader_premises": sum(r[j][1] for r in table for j in range(2)),
        "obstruction_sources": 7,
        "obstruction_readers": 14,
        "extremal": extremal(table),
        "stream_sha256": hashlib.sha256(stream).hexdigest(),
        "literal": literal_witness(),
    }


def main():
    result = calculate()
    require(result == read("RESULT.json"), "result mismatch")
    print("PASS_TWO_HUB_OBSTRUCTION", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
