"""Exact overlapping corank-one header counts; standard library, read-only."""

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b, q):
    return a ^ b if q == 4 else (a + b) % q


def neg(a, q):
    return a if q == 4 else -a % q


def mul(a, b, q):
    if q != 4:
        return a * b % q
    value = 0
    for _ in range(2):
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return value


def dot(a, b, q):
    value = 0
    for x, y in zip(a, b, strict=True):
        value = add(value, mul(x, y, q), q)
    return value


def binary_count(m):
    need(2 <= m <= 64, "binary dimension outside bounded replay domain")
    n = m - 1
    numerator = 9**n - 2 * 7**n + 5**n
    need(numerator >= 0 and numerator % 4 == 0, "integral nonnegative count")
    return numerator // 4


def pair_total(q, m):
    return (q**m - 1) * (q**m - q) * q ** (2 * m - 4)


def rank_weight(a, q):
    if not any(a):
        return 2 * q * q - 1
    determinant = add(mul(a[0], a[3], q), neg(mul(a[1], a[2], q), q), q)
    return 0 if determinant else q - 1


def transfer_counts(q, maximum):
    need(q in (2, 3, 4, 5, 7) and 2 <= maximum <= 64, "transfer domain")
    states = [
        a for a in itertools.product(range(q), repeat=4) if a[0] != 1 and a[3] != 1
    ]
    increments = [
        (a, rank_weight(a, q))
        for a in itertools.product(range(q), repeat=4)
        if rank_weight(a, q)
    ]
    index = {a: i for i, a in enumerate(states)}
    transitions = [[] for _ in states]
    for i, a in enumerate(states):
        for b, weight in increments:
            target = tuple(add(x, y, q) for x, y in zip(a, b, strict=True))
            if target in index:
                transitions[i].append((index[target], weight))
    final = [
        rank_weight(
            (
                add(1, neg(a[0], q), q),
                neg(a[1], q),
                neg(a[2], q),
                add(1, neg(a[3], q), q),
            ),
            q,
        )
        for a in states
    ]
    current = [0] * len(states)
    current[index[(0, 0, 0, 0)]] = 1
    result = {}
    for length in range(1, maximum):
        following = [0] * len(states)
        for i, count in enumerate(current):
            for target, weight in transitions[i]:
                following[target] += count * weight
        current = following
        result[length + 1] = sum(x * y for x, y in zip(current, final, strict=True))
    return result


def vector_guard(u, a, q):
    prefix = 0
    for x, y in zip(u[:-1], a[:-1], strict=True):
        prefix = add(prefix, mul(x, y, q), q)
        if prefix == 1:
            return False
    return True


def enumerate_pairs(q, m):
    """Enumerate X=(u,v), Y=(a;b) directly, imposing YX=I_2."""
    need(
        (q, m)
        in (
            (2, 2),
            (2, 3),
            (2, 4),
            (2, 5),
            (2, 6),
            (3, 2),
            (3, 3),
            (3, 4),
            (4, 2),
            (4, 3),
            (5, 2),
            (5, 3),
        ),
        "pair census domain",
    )
    vectors = list(itertools.product(range(q), repeat=m))
    total = good = single = 0
    for u in vectors[1:]:
        multiples = {tuple(mul(c, x, q) for x in u) for c in range(q)}
        for v in vectors:
            if v in multiples:
                continue
            left = []
            right = []
            for a in vectors:
                values = (dot(a, u, q), dot(a, v, q))
                if values == (1, 0):
                    left.append(vector_guard(u, a, q))
                elif values == (0, 1):
                    right.append(vector_guard(v, a, q))
            need(len(left) == len(right) == q ** (m - 2), "left inverse fibers")
            # Every combination is explicitly visited, including failed pairs.
            for first in left:
                for second in right:
                    total += 1
                    single += first
                    good += first and second
    need(total == pair_total(q, m), "complete normalized-pair count")
    return total, good, single


def inverse(a, q):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        unit = next(c for c in range(1, q) if mul(rows[j][j], c, q) == 1)
        rows[j] = [mul(unit, x, q) for x in rows[j]]
        for i in range(n):
            if i != j:
                factor = neg(rows[i][j], q)
                rows[i] = [
                    add(x, mul(factor, y, q), q)
                    for x, y in zip(rows[i], rows[j], strict=True)
                ]
    need(
        all(rows[i][j] == int(i == j) for i in range(n) for j in range(n)),
        "inverse endpoint",
    )
    return [row[n:] for row in rows]


def full_guard(a, q):
    """Literal no-pivot Gaussian guard test through rank m-1."""
    rows = [list(row) for row in a]
    n = len(rows)
    for j in range(n - 1):
        pivot = rows[j][j]
        if not pivot:
            return False
        unit = next(c for c in range(1, q) if mul(pivot, c, q) == 1)
        for i in range(j + 1, n):
            factor = neg(mul(rows[i][j], unit, q), q)
            for k in range(j, n):
                rows[i][k] = add(rows[i][k], mul(factor, rows[j][k], q), q)
    return True


def conjugate_complement(g, gi, axis, q):
    return [
        [
            add(int(i == j), neg(mul(g[i][axis], gi[axis][j], q), q), q)
            for j in range(len(g))
        ]
        for i in range(len(g))
    ]


def enumerate_headers(q, m):
    need(
        (q, m) in ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (5, 2)),
        "header census domain",
    )
    total = good = single = first_only = 0
    fibers = {}
    for entries in itertools.product(range(q), repeat=m * m):
        g = [entries[i * m : (i + 1) * m] for i in range(m)]
        gi = inverse(g, q)
        if gi is None:
            continue
        total += 1
        p = conjugate_complement(g, gi, 0, q)
        r = conjugate_complement(g, gi, 1, q)
        first, second = full_guard(p, q), full_guard(r, q)
        good += first and second
        single += first
        first_only += bool(p[0][0] and r[0][0])
        for axis, matrix in enumerate((p, r)):
            u = [row[axis] for row in g]
            need(
                full_guard(matrix, q) == vector_guard(u, gi[axis], q),
                "literal elimination versus scalar prefix guards",
            )
        key = tuple(row[k] for row in g for k in (0, 1)) + tuple(gi[0] + gi[1])
        fibers[key] = fibers.get(key, 0) + 1
    gl = 1
    for i in range(m):
        gl *= q**m - q**i
    need(total == gl, "complete GL domain")
    need(len(fibers) == pair_total(q, m), "all normalized pairs reached")
    need(set(fibers.values()) == {gl // pair_total(q, m)}, "equal conjugation fibers")
    return total, good, single, first_only


def check_formula_and_controls(tables):
    for m, count in tables[2].items():
        need(count == binary_count(m), "binary closed form versus transfer")
        joint = Fraction(count, pair_total(2, m))
        single = Fraction(3 ** (m - 1), (2**m - 1) * 2 ** (m - 1))
        need(joint < single * single, "strict negative correlation")
        need((count > 0) == (m >= 3), "exact binary existence threshold")
    # Directly enumerate local factorizations, independent of rank weights.
    for q in tables:
        counts = {}
        for a, b, c, d in itertools.product(range(q), repeat=4):
            matrix = (mul(a, c, q), mul(a, d, q), mul(b, c, q), mul(b, d, q))
            counts[matrix] = counts.get(matrix, 0) + 1
        for matrix in itertools.product(range(q), repeat=4):
            need(
                counts.get(matrix, 0) == rank_weight(matrix, q), "local factor weights"
            )
    controls = [
        (
            Fraction(binary_count(3), pair_total(2, 3)) != Fraction(9, 28) ** 2,
            "independence product",
        ),
        (binary_count(4) != (8**3 - 2 * 6**3 + 4**3) // 4, "lost zero factor"),
        (binary_count(3) != (9**2 + 2 * 7**2 + 5**2) // 4, "even parity target"),
    ]
    for condition, label in controls:
        need(condition, "failed control: " + label)
    return len(controls)


def check_sources(package, root):
    sources = json.loads((package / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            actual = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
            need(actual == row["sha256"], "source hash mismatch: " + row["path"])


def emit_receipt(package, root, result):
    manifest = json.loads((package / "VERIFY.json").read_text())
    paths = sorted([p for p in package.iterdir() if p.is_file()])
    paths += [root / name for name in manifest["inputs"]]
    result["sha256"] = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths
    }
    print("PASS_CORANKONE_PAIR_HEADER_LAW " + json.dumps(result, sort_keys=True))


def main():
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    check_sources(package, root)
    tables = {q: transfer_counts(q, 64 if q == 2 else 10) for q in (2, 3, 4, 5, 7)}
    pair_cases = (
        (2, 2),
        (2, 3),
        (2, 4),
        (2, 5),
        (2, 6),
        (3, 2),
        (3, 3),
        (3, 4),
        (4, 2),
        (4, 3),
        (5, 2),
        (5, 3),
    )
    header_cases = ((2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (4, 2), (5, 2))
    pair_results = {}
    for q, m in pair_cases:
        total, good, single = enumerate_pairs(q, m)
        need(good == tables[q][m], "direct pair census versus transfer")
        marginal = Fraction(
            (q * q - q + 1) ** (m - 1) * (q - 1), q ** (m - 1) * (q**m - 1)
        )
        need(Fraction(single, total) == marginal, "single-request specialization")
        pair_results[f"{q},{m}"] = [total, good, single]
    header_results = {}
    for q, m in header_cases:
        total, good, single, first_only = enumerate_headers(q, m)
        need(
            Fraction(good, total) == Fraction(tables[q][m], pair_total(q, m)),
            "literal header census versus transfer",
        )
        header_results[f"{q},{m}"] = [total, good, single, first_only]
    need(
        header_results["2,3"][1] != header_results["2,3"][3],
        "first-pivot-only control must differ",
    )
    controls = check_formula_and_controls(tables) + 1
    for q, table in tables.items():
        need(
            Fraction(table[2], pair_total(q, 2))
            == Fraction((q - 1) * (q - 2), q * (q + 1)),
            "rank-one pair boundary",
        )
    result = {
        "pairs": pair_results,
        "headers": header_results,
        "transfer_cases": sum(len(t) for t in tables.values()),
        "controls": controls,
    }
    emit_receipt(package, root, result)


if __name__ == "__main__":
    main()
