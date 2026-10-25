"""Literal actual-reader minimum for the PR3573 exceptional single-hub star.

The row model is the relaxed model of PR3698: each extremal premise is one
row, an admissible evaluator separates the row's mark from the other mark,
and a reader support lies in that row's premise (or, for a source row, in
one of the mark's minimal reader premises). Charge is twice the number of
active ports where both the reader coefficient and the evaluator are nonzero.

This file proves the minimum by enumerating that finite model and checks the
written pairing lower bound, the GF4 hub transfer, and WITNESS.json.
"""

import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ZERO = Fraction(0)
WIDTH = 4
NAMES = "gdthxy"
RAW = {
    "g": (0, 0, 1, 0),
    "d": (1, 1, 0, 0),
    "t": (1, 1, 1, 0),
    "h": (0, 0, 0, 1),
    "x": (1, 0, 1, -1),
    "y": (0, 1, 1, -1),
}
QUERIES = [tuple(Fraction(a) for a in RAW[name]) for name in NAMES]
MARKS = [tuple(Fraction(a) for a in row) for row in ((1, 0, 0, 0), (0, 1, 0, 0))]
INDEX = {name: i for i, name in enumerate(NAMES)}
READERS = {
    0: ["ghx", "dthx", "gdhy", "thy", "dxy", "gtxy"],
    1: ["gdhx", "thx", "ghy", "dthy", "dxy", "gtxy"],
}
SOURCES = {
    0: ["gx", "thx", "ty", "ghy"],
    1: ["tx", "ghx", "gy", "thy"],
}
STRICT_BEARING = {
    0: {"ghx": 1, "dthx": 3, "gdhy": 1, "thy": 1, "dxy": 2, "gtxy": 2},
    1: {"gdhx": 1, "thx": 1, "ghy": 1, "dthy": 3, "dxy": 2, "gtxy": 2},
}
FORCED = {(0, "dxy"), (0, "gtxy"), (1, "dxy"), (1, "gtxy")}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rref(matrix, rhs):
    rows = [list(row) + [rhs[i]] for i, row in enumerate(matrix)]
    columns = len(matrix[0]) if matrix else 0
    pivots, rank = [], 0
    for col in range(columns):
        chosen = next((i for i in range(rank, len(rows)) if rows[i][col] != 0), None)
        if chosen is None:
            continue
        rows[rank], rows[chosen] = rows[chosen], rows[rank]
        pivot = rows[rank][col]
        rows[rank] = [value / pivot for value in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col] != 0:
                factor = rows[i][col]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(rows):
            break
    consistent = all(row[-1] == 0 for row in rows if all(value == 0 for value in row[:-1]))
    if not consistent:
        return None
    particular = [ZERO] * columns
    for i, col in enumerate(pivots):
        particular[col] = rows[i][-1]
    return particular


def in_span(vectors, target):
    if not vectors:
        return all(value == 0 for value in target)
    matrix = [[vector[j] for vector in vectors] for j in range(WIDTH)]
    return rref(matrix, list(target)) is not None


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def ids(spec):
    return [INDEX[name] for name in spec]


def coefficients(support, mark):
    matrix = [[QUERIES[i][j] for i in support] for j in range(WIDTH)]
    return rref(matrix, list(MARKS[mark]))


def evaluator(mark, killed):
    constraints = [list(MARKS[mark]), list(MARKS[1 - mark])]
    targets = [Fraction(1), ZERO]
    for i in killed:
        constraints.append(list(QUERIES[i]))
        targets.append(ZERO)
    return rref(constraints, targets)


def extremal_premises():
    readers, sources = {0: [], 1: []}, {0: [], 1: []}
    for mark in (0, 1):
        for size in range(7):
            for comb in combinations(range(6), size):
                vectors = [QUERIES[i] for i in comb]
                if in_span(vectors, MARKS[mark]) and all(
                    not in_span([QUERIES[i] for i in comb if i != j], MARKS[mark]) for j in comb
                ):
                    readers[mark].append("".join(NAMES[i] for i in comb))
                outside = not in_span([MARKS[1 - mark]] + vectors, MARKS[mark])
                if not outside:
                    continue
                added = [j for j in range(6) if j not in comb]
                if all(
                    in_span([MARKS[1 - mark]] + vectors + [QUERIES[j]], MARKS[mark])
                    for j in added
                ):
                    sources[mark].append("".join(NAMES[i] for i in comb))
    return readers, sources


def exact_supports(mark, pool):
    found = {}
    for size in range(1, len(pool) + 1):
        for pick in combinations(ids(pool), size):
            solution = coefficients(pick, mark)
            if solution is None:
                continue
            exact = tuple(i for i, coeff in zip(pick, solution) if coeff != 0)
            if exact not in found:
                found[exact] = tuple(coeff for coeff in solution if coeff != 0)
    return found


def best_row(kind, mark, spec):
    pools = [spec] if kind == "reader" else READERS[mark]
    extra = () if kind == "reader" else tuple(ids(spec))
    best = None
    for pool in pools:
        for support, coeffs in exact_supports(mark, pool).items():
            for killed_count in range(len(support), -1, -1):
                for extra_killed in combinations(support, killed_count):
                    killed = tuple(sorted(set(extra) | set(extra_killed)))
                    phi = evaluator(mark, killed)
                    if phi is None:
                        continue
                    alive = tuple(
                        i for i in support if dot(phi, QUERIES[i]) != 0
                    )
                    record = {
                        "kind": kind,
                        "mark": mark,
                        "premise": spec,
                        "pool": pool,
                        "support": "".join(NAMES[i] for i in support),
                        "u": [str(coeff) for coeff in coeffs],
                        "phi": [str(value) for value in phi],
                        "alive": "".join(NAMES[i] for i in alive),
                        "cost": len(alive),
                    }
                    key = (
                        record["cost"],
                        record["pool"],
                        record["support"],
                        tuple(record["u"]),
                        tuple(record["phi"]),
                    )
                    if best is None or key < best[0]:
                        best = (key, record)
                    break
    require(best is not None, "no admissible row for " + spec)
    return best[1]


def row_order():
    rows = []
    for mark in (0, 1):
        for spec in SOURCES[mark]:
            rows.append(("source", mark, spec))
        for spec in READERS[mark]:
            rows.append(("reader", mark, spec))
    return rows


def canonical_rows():
    return [best_row(kind, mark, spec) for kind, mark, spec in row_order()]


def bearing_count(mark, spec):
    best = None
    for size in range(1, len(spec) + 1):
        for pick in combinations(ids(spec), size):
            if coefficients(pick, mark) is None:
                continue
            count = sum(1 for i in pick if QUERIES[i][mark] != 0)
            best = count if best is None else min(best, count)
    return best


def phi_family(mark, alpha, beta):
    if mark == 0:
        return (Fraction(1), ZERO, alpha, beta)
    return (ZERO, Fraction(1), alpha, beta)


def assert_pairing():
    """The four forced rows pay at least two for every admissible evaluator."""
    samples = (ZERO, Fraction(1), Fraction(-1), Fraction(1, 3))
    unique = {
        (0, "dxy"): (Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)),
        (1, "dxy"): (Fraction(1, 2), Fraction(-1, 2), Fraction(1, 2)),
        (0, "gtxy"): (Fraction(-1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(-1, 2)),
        (1, "gtxy"): (Fraction(-1, 2), Fraction(1, 2), Fraction(-1, 2), Fraction(1, 2)),
    }
    for (mark, spec), coeffs in unique.items():
        support = ids(spec)
        solution = coefficients(support, mark)
        require(solution == list(coeffs), "unique reader changed: " + spec)
        require(
            all(coefficients(pick, mark) is None for pick in combinations(support, len(support) - 1)),
            "a proper subset spans " + spec,
        )
        for alpha in samples:
            for beta in samples:
                phi = phi_family(mark, alpha, beta)
                values = [dot(phi, QUERIES[i]) for i in support]
                if spec == "dxy":
                    # phi(d) = 1 and the x/y evaluations differ by 1.
                    require(values[0] == 1, "d is invisible")
                    require(values[1] - values[2] == (1 if mark == 0 else -1), "x/y gap")
                else:
                    require(values[1] - values[0] == 1, "g/t gap")
                    require(values[2] - values[3] == (1 if mark == 0 else -1), "x/y gap")
                require(sum(value != 0 for value in values) >= 2, "pairing cost dropped")


def gf4_transfer(replace_y=None):
    one, w = (1, 0), (0, 1)

    def add(left, right):
        return (left[0] ^ right[0], left[1] ^ right[1])

    def mul(left, right):
        a, b = left
        c, d = right
        return ((a & c) ^ (b & d), (a & d) ^ (b & c) ^ (b & d))

    def scale(scalar, vector):
        return [mul(scalar, entry) for entry in vector]

    def vadd(left, right):
        return [add(a, b) for a, b in zip(left, right)]

    zero, e1 = (0, 0), one
    e = [e1, zero, zero, zero]
    f = [zero, e1, zero, zero]
    g = [zero, zero, e1, zero]
    h = [zero, zero, zero, e1]
    images = {
        "g": g,
        "d": vadd(vadd(e, f), scale(w, vadd(g, h))),
        "t": vadd(vadd(vadd(e, f), g), scale(w, h)),
        "h": h,
        "x": vadd(vadd(e, g), h),
        "y": vadd(vadd(f, g), h),
    }
    if replace_y is not None:
        images["y"] = replace_y
    marks = (e, f)

    def contained(vectors, target):
        if not vectors:
            return all(entry == zero for entry in target)
        columns = len(vectors)
        rows = [[vectors[col][row] for col in range(columns)] + [target[row]] for row in range(4)]
        pivot_row = 0
        for col in range(columns):
            chosen = next((i for i in range(pivot_row, 4) if rows[i][col] != zero), None)
            if chosen is None:
                continue
            rows[pivot_row], rows[chosen] = rows[chosen], rows[pivot_row]
            inverse = next(cand for cand in ((1, 0), (0, 1), (1, 1)) if mul(rows[pivot_row][col], cand) == one)
            rows[pivot_row] = [mul(inverse, entry) for entry in rows[pivot_row]]
            for i in range(4):
                if i != pivot_row and rows[i][col] != zero:
                    factor = rows[i][col]
                    rows[i] = [add(a, mul(factor, b)) for a, b in zip(rows[i], rows[pivot_row])]
            pivot_row += 1
        return all(row[-1] == zero for row in rows if all(entry == zero for entry in row[:-1]))

    failures = 0
    for mask in range(64):
        chosen = [i for i in range(6) if mask >> i & 1]
        for mark in (0, 1):
            old_reader = in_span([QUERIES[i] for i in chosen], MARKS[mark])
            old_outside = not in_span([MARKS[1 - mark]] + [QUERIES[i] for i in chosen], MARKS[mark])
            new_vectors = [images[NAMES[i]] for i in chosen]
            if old_reader and not contained(new_vectors, marks[mark]):
                failures += 1
            if old_outside and not (not contained([marks[1 - mark]] + new_vectors, marks[mark])):
                failures += 1
    require(failures == 0, "GF4 hub transfer failed " + str(failures) + " implications")


def parse_phi(values):
    return tuple(Fraction(value) for value in values)


def check_record(record):
    mark = record["mark"]
    support = ids(record["support"])
    coeffs = [Fraction(value) for value in record["u"]]
    phi = parse_phi(record["phi"])
    require(len(coeffs) == len(support), "coefficient width")
    total = [ZERO] * WIDTH
    for coeff, i in zip(coeffs, support):
        total = [a + coeff * b for a, b in zip(total, QUERIES[i])]
    require(tuple(total) == MARKS[mark], "reader misses the mark: " + record["premise"])
    require(dot(phi, MARKS[mark]) == 1 and dot(phi, MARKS[1 - mark]) == 0, "evaluator")
    if record["kind"] == "source":
        for i in ids(record["premise"]):
            require(dot(phi, QUERIES[i]) == 0, "source evaluator sees " + NAMES[i])
        require(set(record["support"]).issubset(set(record["pool"])), "source reader pool")
    else:
        require(set(record["support"]).issubset(set(record["premise"])), "reader premise")
    alive = "".join(NAMES[i] for i in support if dot(phi, QUERIES[i]) != 0)
    require(alive == record["alive"] and len(alive) == record["cost"], "recorded cost")
    require(all(coeff != 0 for coeff in coeffs), "zero coefficient inside support")


def gram_and_charges(records):
    ports = 2 * len(records)
    a = [0] * ports
    b = [0] * ports
    q_values = [[ZERO] * ports for _ in range(6)]
    u_values = [[ZERO] * ports for _ in range(6)]
    for row, record in enumerate(records):
        active = 2 * row
        if record["mark"] == 0:
            a[active] = 1
        else:
            b[active] = 1
        phi = parse_phi(record["phi"])
        support = {name: Fraction(coeff) for name, coeff in zip(record["support"], record["u"])}
        for i, name in enumerate(NAMES):
            q_values[i][active] = dot(phi, QUERIES[i])
            u_values[i][active] = support.get(name, ZERO)
    for left in range(ports):
        for right in range(ports):
            target = a[left] * a[right] + b[left] * b[right]
            got = sum(u_values[i][left] * q_values[i][right] for i in range(6))
            require(got == target, "Gram mismatch")
    charges = []
    for i in range(6):
        count = sum(
            1
            for record in records
            if NAMES[i] in record["support"]
            and Fraction(dict(zip(record["support"], record["u"]))[NAMES[i]]) != 0
            and NAMES[i] in record["alive"]
        )
        charges.append(2 * count)
    return charges


def audit():
    readers, sources = extremal_premises()
    require(
        {mark: set(specs) for mark, specs in readers.items()}
        == {mark: set(specs) for mark, specs in READERS.items()}
        and {mark: set(specs) for mark, specs in sources.items()}
        == {mark: set(specs) for mark, specs in SOURCES.items()},
        "extremal table drifted",
    )
    for mark in (0, 1):
        for spec, expected in STRICT_BEARING[mark].items():
            require(bearing_count(mark, spec) == expected, "strict bearing count")
    assert_pairing()
    gf4_transfer()
    records = canonical_rows()
    for record in records:
        check_record(record)
        lower = 2 if (record["mark"], record["premise"]) in FORCED and record["kind"] == "reader" else 1
        require(record["cost"] == lower, "row minimum is not the proved bound")
    stored = json.loads((ROOT / "WITNESS.json").read_text(encoding="utf-8"))
    require(stored["rows"] == records, "WITNESS.json is not the canonical minimum")
    charges = gram_and_charges(records)
    require(charges == stored["query_charges"], "charge vector")
    require(sum(record["cost"] for record in records) == 24, "unit total")
    require(sum(charges) == 48 and len(records) == 20, "charge or row count")
    return {
        "rows": 20,
        "units": 24,
        "baseline": 40,
        "charge": 48,
        "excess": 8,
        "forced_reader_rows": ["E dxy", "E gtxy", "F dxy", "F gtxy"],
        "query_charges": charges,
    }


def main():
    result = audit()
    print("PASS_SINGLE_HUB_TWO_BEARING", json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
