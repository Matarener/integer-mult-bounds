"""Pivot-policy swap floor for the paid pivoted BIT fallback. Apache-2.0.

The compiler family is the one of PR4235: at stage k = 0..r-1 a unit pivot
is chosen anywhere in residual rows k..m-1 and columns 0..m-1-k of M = P C;
a paid head swap is charged when its row is not k and a paid tail swap when
its column is not m-1-k; ordered clearing ADDs follow.  Over Z/q^w the
itinerary depends only on the residue field, so F_q censuses suffice.
"""

import argparse
import hashlib
import itertools
import json
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE_FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def mul(a, b, q):
    return [[sum(x * y for x, y in zip(row, col)) % q for col in zip(*b)] for row in a]


def inverse(a, q):
    n = len(a)
    rows = [list(row) + [int(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        i = next(i for i in range(k, n) if rows[i][k] % q)
        rows[k], rows[i] = rows[i], rows[k]
        scale = pow(rows[k][k], -1, q)
        rows[k] = [x * scale % q for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                c = rows[i][k]
                rows[i] = [(x - c * y) % q for x, y in zip(rows[i], rows[k])]
    return [row[n:] for row in rows]


def gaussian_binomial(m, r, q):
    num = den = 1
    for i in range(r):
        num *= q ** (m - i) - 1
        den *= q ** (i + 1) - 1
    return num // den


def idempotents(m, r, q):
    """Every rank-r idempotent once: image in RREF, complement as a graph."""
    for piv in itertools.combinations(range(m), r):
        free = [(i, j) for i in range(r) for j in range(m) if j > piv[i] and j not in piv]
        comp = [j for j in range(m) if j not in piv]
        for vals in itertools.product(range(q), repeat=len(free)):
            basis = [[int(j == piv[i]) for j in range(m)] for i in range(r)]
            for (i, j), v in zip(free, vals):
                basis[i][j] = v
            for graph in itertools.product(range(q), repeat=r * (m - r)):
                kernel = []
                for t, c in enumerate(comp):
                    v = [int(j == c) for j in range(m)]
                    for i in range(r):
                        v = [(x + graph[t * r + i] * y) % q for x, y in zip(v, basis[i])]
                    kernel.append(v)
                g = [list(col) for col in zip(*(basis + kernel))]
                e = [[int(i == j and i < r) for j in range(m)] for i in range(m)]
                yield mul(mul(g, e, q), inverse(g, q), q)


def stage(a, k, i, j, q):
    """Swap pivot (i, j) to (k, last) and clear; returns the new residual."""
    m = len(a)
    last = m - 1 - k
    b = [list(row) for row in a]
    b[k], b[i] = b[i], b[k]
    for row in b:
        row[last], row[j] = row[j], row[last]
    inv = pow(b[k][last], -1, q)
    for ii in range(k + 1, m):
        c = b[ii][last] * inv % q
        if c:
            b[ii] = [(x - c * y) % q for x, y in zip(b[ii], b[k])]
    for jj in range(last):
        c = b[k][jj] * inv % q
        if c:
            for row in b:
                row[jj] = (row[jj] - c * row[last]) % q
    return tuple(map(tuple, b))


def candidates(a, k, q):
    m = len(a)
    return [(i, j) for i in range(k, m) for j in range(m - k) if a[i][j] % q]


def optimum(p, r, q):
    """Minimum paid swaps over every pivot policy (exact DFS with memo)."""
    m = len(p)

    @lru_cache(None)
    def go(k, a):
        if k == r:
            require(all(x == 0 for row in a[r:] for x in row[: m - r]), "zero remainder")
            return 0
        best = None
        cands = candidates(a, k, q)
        require(cands, "split rank supplies a unit pivot")
        for i, j in sorted(cands, key=lambda c: (c[0] != k) + (c[1] != m - 1 - k)):
            cost = (i != k) + (j != m - 1 - k)
            if best is not None and cost >= best:
                continue
            total = cost + go(k + 1, stage(a, k, i, j, q))
            if best is None or total < best:
                best = total
        return best

    return go(0, tuple(tuple(row[::-1]) for row in p))


def run_policy(p, r, q, choose):
    m = len(p)
    a, paid = tuple(tuple(row[::-1]) for row in p), 0
    for k in range(r):
        cands = candidates(a, k, q)
        require(cands, "split rank supplies a unit pivot")
        i, j = choose(a, k, cands)
        paid += (i != k) + (j != m - 1 - k)
        a = stage(a, k, i, j, q)
    require(all(x == 0 for row in a[r:] for x in row[: m - r]), "zero remainder")
    return paid


def first_unit(a, k, cands):
    return cands[0]


def suffix_policy(r):
    """Explicit attaining policy for the diagonal suffix projector."""
    def choose(a, k, cands):
        m = len(a)
        last = m - 1 - k
        if (k, last) in cands:
            return (k, last)
        want = max(r, m - r) + k  # nonzero, outside 0..r-1, still in place
        pick = [c for c in cands if c[0] == want]
        require(len(pick) == 1, "outside suffix row is untouched and monomial")
        return pick[0]
    return choose


def suffix(m, r):
    return [[int(i == j and i >= m - r) for j in range(m)] for i in range(m)]


def floor(m, r):
    return 2 * min(r, m - r)


CENSUS = [(3, 2, (1,)), (3, 3, (1, 2)), (3, 4, (1, 2, 3)), (3, 5, (1, 4)),
          (3, 6, (5,)), (5, 2, (1,)), (5, 3, (1, 2)), (5, 4, (3,))]


EXTENDED = [(3, 5, (2, 3))]


def census(domains):
    rows = []
    for q, m, ranks in domains:
        for r in ranks:
            hist, first_max, count = {}, 0, 0
            for p in idempotents(m, r, q):
                count += 1
                s = optimum(p, r, q)
                f = run_policy(p, r, q, first_unit)
                require(s <= f <= 2 * r, "optimum <= first-unit <= 2r")
                hist[s] = hist.get(s, 0) + 1
                first_max = max(first_max, f)
            require(count == q ** (r * (m - r)) * gaussian_binomial(m, r, q),
                    f"complete idempotent census q={q} m={m} r={r}")
            d = suffix(m, r)
            require(optimum(d, r, q) == floor(m, r), "suffix optimum equals the floor")
            worst = max(hist)
            require(floor(m, r) <= worst <= 2 * r, "policy floor and ceiling")
            rows.append({"q": q, "m": m, "r": r, "idempotents": count,
                         "optimal_histogram": {str(k): v for k, v in sorted(hist.items())},
                         "optimal_worst": worst, "first_unit_worst": first_max,
                         "floor": floor(m, r)})
    return rows


def boundary():
    """Literal m = 64 suffix fixtures for every rank, and the child bills."""
    m, rows = 64, []
    for r in range(1, m):
        d = suffix(m, r)
        attained = run_policy(d, r, 3, suffix_policy(r))
        first = run_policy(d, r, 3, first_unit)
        require(attained == floor(m, r), f"explicit policy attains the floor at r={r}")
        require(first == 2 * r, f"first-unit policy pays 2r at r={r}")
        rows.append((r, attained, first))
    ranks = range(1, 43)
    best_f2 = max(1 + 6 * floor(m, r) for r in ranks)
    old_f2 = max(1 + 12 * r for r in ranks)
    best_f1 = max(1 + 2 * floor(m, r) for r in ranks)
    old_f1 = max(1 + 4 * r for r in ranks)
    require((best_f2, old_f2, best_f1, old_f1) == (385, 505, 129, 169), "boundary bills")
    return {"m": 64, "ranks_checked": len(rows),
            "first_unit_equals_2r": True, "explicit_policy_equals_floor": True,
            "boundary_r_le_42_children_f_ge_2": {"every_policy_at_least": best_f2,
                                                "pr4235_at_most": old_f2},
            "boundary_r_le_42_children_f_eq_1": {"every_policy_at_least": best_f1,
                                                "pr4235_at_most": old_f1}}


def controls():
    """A policy that skips a required swap must be rejected."""
    m, r, q = 6, 2, 3
    a = tuple(tuple(row[::-1]) for row in suffix(m, r))
    require(not candidates(a, 0, q) or all(c != (0, m - 1) for c in candidates(a, 0, q)),
            "home pivot is absent on the suffix projector")
    try:
        stage(a, 0, 0, m - 1, q)
    except ValueError:
        pass
    else:
        raise AssertionError("a zero pivot was accepted")
    return {"zero_home_pivot_rejected": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--extended", action="store_true",
                        help="also run the opt-in m=5 rank-2/3 census over F3 (minutes)")
    args = parser.parse_args()
    domains = CENSUS + (EXTENDED if args.extended else [])
    report = {"status": "PASS_BIT_PIVOT_POLICY_FLOOR",
              "files_sha256": {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest()
                               for n in PACKAGE_FILES},
              "extended": args.extended, "census": census(domains), "boundary": boundary(), "controls": controls()}
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.receipt:
        require(args.receipt.is_absolute() and not args.receipt.exists(),
                "receipt path is absolute and new")
        args.receipt.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
