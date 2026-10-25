"""Separate primitive-integer rank and exhaustive GF4-functional checker."""

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABELS = "gdthxykzw"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def load(name):
    path = ROOT / name
    check(path.is_file() and not path.is_symlink(), "regular input")
    check(path.stat().st_size <= 1048576, "input capacity")
    return json.loads(path.read_text())


def integer_rank(matrix):
    basis = {}
    for original in matrix:
        row = list(original)
        for column, pivot in sorted(basis.items()):
            a, b = row[column], pivot[column]
            row = [b * x - a * y for x, y in zip(row, pivot, strict=True)]
            divisor = math.gcd(*row)
            if divisor:
                row = [x // divisor for x in row]
        first = next((j for j, x in enumerate(row) if x), None)
        if first is not None:
            basis[first] = row
    return len(basis)


def rational_rank(matrix):
    integers = []
    for row in matrix:
        denominator = math.lcm(*(x.denominator for x in row))
        integers.append([int(x * denominator) for x in row])
    return integer_rank(integers)


def product(a, b):
    value = 0
    for bit in range(2):
        if b >> bit & 1:
            value ^= a << bit
    return value ^ (7 if value & 4 else 0)


def orthogonal(forms, vector):
    for form in forms:
        value = 0
        for x, y in zip(form, vector, strict=True):
            value ^= product(x, y)
        if value:
            return False
    return True


def predicate_table(queries, marks, extension=False):
    check(len(queries) <= 9 and len(marks[0]) <= 5, "finite table capacity")
    forms = list(itertools.product(range(4), repeat=len(marks[0]))) if extension else []
    out = []
    for mask in range(2 ** len(queries)):
        selected = [q for j, q in enumerate(queries) if mask & (2**j)]
        row = []
        for j in range(2):
            if extension:
                annihilators = [v for v in forms if orthogonal(selected, v)]
                reader = orthogonal(annihilators, marks[j])
                with_other = [v for v in annihilators if orthogonal([marks[1 - j]], v)]
                source = not orthogonal(with_other, marks[j])
            else:
                r = integer_rank(selected)
                reader = integer_rank(selected + [marks[j]]) == r
                source = integer_rank(
                    selected + [marks[1 - j], marks[j]]
                ) > integer_rank(selected + [marks[1 - j]])
            row.append((source, reader))
        out.append(tuple(row))
    return out


def old_geometry():
    e, f, g, h, k = [tuple(int(i == j) for i in range(5)) for j in range(5)]
    zero = (0,) * 5

    def add(a, b):
        return tuple(x + y for x, y in zip(a, b, strict=True))

    def edge(a, b):
        return tuple(x - y for x, y in zip(a, b, strict=True))

    queries = [g, add(e, f), add(add(e, f), g)]
    terminals = [zero, add(e, g), add(f, g)]
    for hub in (h, k):
        queries.extend(
            [edge(hub, terminals[0]), edge(terminals[1], hub), edge(terminals[2], hub)]
        )
    return queries, [e, f]


def premises(table, config):
    sources = [
        (0, "ghk"),
        (1, "ghk"),
        (0, "hx"),
        (0, "gx"),
        (0, "ghz"),
        (1, "gy"),
        (1, "hy"),
    ]
    readers = [
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
    ]
    check(
        config["premises"]
        == {"source": [list(v) for v in sources], "reader": [list(v) for v in readers]},
        "complete obstruction premises",
    )
    for kind, values in enumerate((sources, readers)):
        for mark, letters in values:
            mask = sum(2 ** LABELS.index(c) for c in letters)
            check(table[mask][mark][kind], "obstruction premise")
    rows = [
        (kind, mark, letters)
        for kind, values in (("source", sources), ("reader", readers))
        for mark, letters in values
    ]
    return sorted(rows, key=lambda v: v[1])


def full_operator(u, q, rows):
    for p in range(42):
        for r in range(42):
            value = (
                sum(u[p // 2][i] * q[r // 2][i] for i in range(9))
                if not (p % 2 or r % 2)
                else 0
            )
            check(
                value
                == int(not (p % 2 or r % 2) and rows[p // 2][1] == rows[r // 2][1]),
                "literal full operator",
            )


def literal(queries, marks, rows):
    witness = load("WITNESS.json")
    check(witness["rows"] == [list(r) for r in rows], "literal premise coverage")
    check(
        len(witness["functionals"]) == len(witness["readers"]) == 21,
        "literal row capacity",
    )
    functions = [list(map(Fraction, r)) for r in witness["functionals"]]
    u = [list(map(Fraction, r)) for r in witness["readers"]]
    check(
        all(len(v) == 5 for v in functions) and all(len(v) == 9 for v in u),
        "literal matrix shape",
    )
    check(rational_rank(functions) == 5, "injective coordinate embedding")
    check(
        all(x.denominator == 1 for fn in functions for x in fn)
        and all(x.denominator in (1, 2) for r in u for x in r),
        "odd-characteristic premise certificates",
    )
    q = [[sum(fn[j] * v[j] for j in range(5)) for v in queries] for fn in functions]
    for n, (kind, mark, letters) in enumerate(rows):
        check(
            functions[n][mark] == 1 and functions[n][1 - mark] == 0,
            "literal indicator values",
        )
        check(
            all(
                sum(u[n][i] * queries[i][j] for i in range(9)) == marks[mark][j]
                for j in range(5)
            ),
            "literal reader identity",
        )
        if kind == "source":
            check(
                all(q[n][LABELS.index(c)] == 0 for c in letters), "literal source zeros"
            )
        else:
            check(
                all(not x or LABELS[i] in letters for i, x in enumerate(u[n])),
                "literal reader support",
            )
    full_operator(u, q, rows)
    charges = []
    for i in range(9):
        left = [2 * n + b for n in range(21) if q[n][i] for b in range(2)]
        right = [2 * n + b for n in range(21) if u[n][i] for b in range(2)]
        rectangle = [[int(a == b) for b in right] for a in left]
        charges.append(integer_rank(rectangle))
    return {
        "ports": 42,
        "group_sizes": [24, 18],
        "query_rank": rational_rank(q),
        "reader_rank": rational_rank(u),
        "operator_entries": 1764,
        "charges": charges,
        "bill": sum(charges),
        "original_bill": 42,
    }


def boundary(table):
    out = []
    for j in range(2):
        minimal, maximal = [], []
        for mask, row in enumerate(table):
            sub = [mask ^ (1 << i) for i in range(9) if mask >> i & 1]
            sup = [mask | (1 << i) for i in range(9) if not mask >> i & 1]
            if row[j][1] and not any(table[k][j][1] for k in sub):
                minimal.append(mask)
            if row[j][0] and not any(table[k][j][0] for k in sup):
                maximal.append(mask)
        out.append({"minimal_readers": minimal, "maximal_sources": maximal})
    return out


def calculate():
    queries, marks = old_geometry()
    config = load("CONFIG.json")
    check(config["queries"] == [list(v) for v in queries], "two-hub geometry")
    check(config["marks"] == [list(v) for v in marks], "independent marks")
    check(config["query_names"] == LABELS, "query indexing")
    table = predicate_table(queries, marks)
    rows = premises(table, config)
    data = (ROOT / "PREDECESSOR-MAPS.json").read_bytes()
    check(
        hashlib.sha256(data).hexdigest() == load("ORIGINS.json")["sha256"],
        "retained predecessor bytes",
    )
    star = next(
        r
        for r in json.loads(data)["cases"]
        if r["marks"] == [0, 1] and r["ports"] == [4, 5]
    )["star_queries"]
    check(
        len(star) == 6
        and all(
            len(v) == 4 and all(type(x) is int and 0 <= x < 4 for x in v) for v in star
        ),
        "GF4 star shape",
    )
    before = predicate_table([q[:4] for q in queries[:6]], [v[:4] for v in marks])
    after = predicate_table(star, [v[:4] for v in marks], True)
    check(
        all(
            not a[j][k] or b[j][k]
            for a, b in zip(before, after, strict=True)
            for j in range(2)
            for k in range(2)
        ),
        "one-star transfer",
    )
    stream = json.dumps([table, before, after], separators=(",", ":")).encode()
    return {
        "two_hub_subsets": 512,
        "one_star_subsets": 64,
        "two_hub_source_premises": sum(row[j][0] for row in table for j in range(2)),
        "two_hub_reader_premises": sum(row[j][1] for row in table for j in range(2)),
        "obstruction_sources": 7,
        "obstruction_readers": 14,
        "extremal": boundary(table),
        "stream_sha256": hashlib.sha256(stream).hexdigest(),
        "literal": literal(queries, marks, rows),
    }


def main():
    result = calculate()
    check(result == load("RESULT.json"), "result mismatch")
    print("PASS_TWO_HUB_INDEPENDENT", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
