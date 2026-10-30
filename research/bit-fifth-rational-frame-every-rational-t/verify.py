#!/usr/bin/env python3
"""Exact eight-call minimum for the fifth rational frame R_t, every rational t.

Model (PR #2085 / PR #2112): four roles, target diag([A+P],[A+Q],[B+P],[B+Q]),
paid factors I + ([F]-1)N with F in {A,B,P,Q,R_t}, R_t = (1,t)^T(1,t), and N a
rank-one idempotent in M4(F2). The proof in README.md has three finite inputs,
each recomputed here:

1. lattice: the images of the labels and targets in L/2L, L = ZA+ZB+ZP+ZR_t,
   depend only on the parity of the denominator of t (checked on a grid; the
   general argument is in the README);
2. support: every monomial of an expanded word has exponent equal to a subset
   sum of its labels, so each target frame is such a sum; with at most seven
   calls, R_t occurs in such a sum only at t = 0 (exact, all rational t);
3. first order: rank/trace floors over all 65,536 binary 4x4 masks.

Positive control: the direct eight-call word, multiplied exactly in F2[L].
Prepared by Nick Petalas. Apache-2.0.
"""

from __future__ import annotations

import itertools
import math
import sys
from fractions import Fraction as Fr

ROLES = 4
MAX_CALLS = 7

# Symmetric 2x2 rational matrices [[a, c], [c, b]] in the basis (A, B, P),
# where A = E11, B = E22, P = (1/2)[[1,1],[1,1]]: coordinates (a-c, b-c, 2c).
A = (Fr(1), Fr(0), Fr(0))
B = (Fr(0), Fr(1), Fr(0))
P = (Fr(0), Fr(0), Fr(1))
Q = (Fr(1), Fr(1), Fr(-1))  # Q = A + B - P


def vadd(*vs):
    return tuple(sum(x) for x in zip(*vs))


def vscale(k, v):
    return tuple(k * x for x in v)


def r_frame(t: Fr):
    """R_t = (1,t)^T(1,t) = [[1,t],[t,t^2]] in (A,B,P) coordinates."""
    return (1 - t, t * t - t, 2 * t)


def as_matrix(v):
    a, b, p = v
    return ((a + p / 2, p / 2), (p / 2, b + p / 2))


TARGETS = (vadd(A, P), vadd(A, Q), vadd(B, P), vadd(B, Q))


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


# ---------------------------------------------------------------- frames ----

def check_frames() -> None:
    expect = {
        "A": ((1, 0), (0, 0)),
        "B": ((0, 0), (0, 1)),
        "P": ((Fr(1, 2), Fr(1, 2)), (Fr(1, 2), Fr(1, 2))),
        "Q": ((Fr(1, 2), Fr(-1, 2)), (Fr(-1, 2), Fr(1, 2))),
    }
    for name, v in zip("ABPQ", (A, B, P, Q)):
        check(as_matrix(v) == expect[name], f"frame {name}")
    for t in (Fr(1, 2), Fr(-3, 4), Fr(5, 6), Fr(2, 3), Fr(7)):
        m = as_matrix(r_frame(t))
        check(m == ((1, t), (t, t * t)), f"R_t matrix at t={t}")
        check(m[0][0] * m[1][1] - m[0][1] * m[1][0] == 0, "R_t rank one")
    dets = [as_matrix(c) for c in TARGETS]
    for m in dets:
        check(m[0][0] * m[1][1] - m[0][1] ** 2 == Fr(1, 2), "target det 1/2")


# --------------------------------------------------------------- lattice ----

def integer_basis(rows):
    """Row-reduce integer vectors to a basis of their Z-span (echelon form)."""
    rows = [list(r) for r in rows if any(r)]
    basis = []
    col = 0
    ncols = len(rows[0]) if rows else 0
    while rows and col < ncols:
        piv = [r for r in rows if r[col] != 0]
        rest = [r for r in rows if r[col] == 0]
        while len(piv) > 1:
            piv.sort(key=lambda r: abs(r[col]))
            head = piv[0]
            new = [head]
            for r in piv[1:]:
                k = r[col] // head[col]
                r = [x - k * y for x, y in zip(r, head)]
                if r[col] != 0:
                    new.append(r)
                elif any(r):
                    rest.append(r)
            piv = new
        if piv:
            basis.append(piv[0])
        rows = [r for r in rest if any(r)]
        col += 1
    return basis


def solve3(basis, v):
    """Coordinates of v in a 3x3 rational basis (rows), by Cramer's rule."""
    def det(m):
        return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
                - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
    cols = [list(c) for c in zip(*basis)]  # columns = basis vectors
    d = det(cols)
    out = []
    for i in range(3):
        m = [row[:] for row in cols]
        for r in range(3):
            m[r][i] = v[r]
        out.append(Fr(det(m), d))
    return out


def mod2_images(t: Fr):
    """Images in L/2L (L = span of A,B,P,R_t) of the five labels and targets."""
    labels = {"A": A, "B": B, "P": P, "Q": Q, "R": r_frame(t)}
    den = math.lcm(*(x.denominator for v in labels.values() for x in v))
    ints = [[int(x * den) for x in v] for v in labels.values()]
    basis = integer_basis(ints)
    check(len(basis) == 3, f"rank-three lattice at t={t}")

    def image(v):
        coords = solve3(basis, [x * den for x in v])
        check(all(c.denominator == 1 for c in coords), f"lattice membership t={t}")
        return tuple(int(c) % 2 for c in coords)

    return ({k: image(v) for k, v in labels.items()},
            [image(c) for c in TARGETS])


def gf2_rank_vectors(vs):
    rows = [int("".join(map(str, v)), 2) for v in vs]
    rank = 0
    for bit in reversed(range(3)):
        piv = next((r for r in rows if r >> bit & 1), None)
        if piv is None:
            continue
        rank += 1
        rows = [r ^ piv if r >> bit & 1 else r for r in rows if r != piv]
    return rank


def xor(u, v):
    return tuple(a ^ b for a, b in zip(u, v))


def check_lattice_grid():
    """Parity classification of L/2L on all t = p/q, 1<=q<=24, |p|<=48."""
    cases = {"odd": 0, "even": 0}
    for q in range(1, 25):
        for p in range(-48, 49):
            if math.gcd(p, q) != 1:
                continue
            t = Fr(p, q)
            img, tgt = mod2_images(t)
            if q % 2:
                # Inclusion ZA+ZB+ZP -> L is an isomorphism mod 2.
                check(gf2_rank_vectors([img["A"], img["B"], img["P"]]) == 3,
                      f"odd q: A,B,P basis mod 2 at t={t}")
                check(img["Q"] == xor(xor(img["A"], img["B"]), img["P"]), "Q odd")
                want_r = img["A"] if p % 2 == 0 else (0, 0, 0)
                check(img["R"] == want_r, f"odd q: R image at t={t}")
                check(tgt == [xor(img["A"], img["P"]), xor(img["A"], img["Q"]),
                              xor(img["B"], img["P"]), xor(img["B"], img["Q"])],
                      "odd q: targets")
                cases["odd"] += 1
            else:
                check(img["B"] == (0, 0, 0), f"even q: B in 2L at t={t}")
                check(gf2_rank_vectors([img["A"], img["P"], img["R"]]) == 3,
                      f"even q: A,P,R basis mod 2 at t={t}")
                ap = xor(img["A"], img["P"])
                check(img["Q"] == ap, f"even q: Q = A+P mod 2L at t={t}")
                check(tgt == [ap, img["P"], img["P"], ap], f"even q: targets t={t}")
                cases["even"] += 1
    return cases


# --------------------------------------------------------------- support ----

def support_exceptions():
    """All rational t where a target is a nonnegative sum of <=7 labels using R_t.

    For n_R >= 1 the P-coordinate equation n_P - n_Q + 2 n_R t = c_P fixes t,
    so the enumeration covers every rational t exactly.
    """
    exceptional = {}
    no_r_reps = {i: [] for i in range(ROLES)}
    for n in itertools.product(range(MAX_CALLS + 1), repeat=5):
        if sum(n) > MAX_CALLS:
            continue
        na, nb, np_, nq, nr = n
        for i, c in enumerate(TARGETS):
            if nr == 0:
                s = vadd(vscale(na, A), vscale(nb, B), vscale(np_, P), vscale(nq, Q))
                if s == c:
                    no_r_reps[i].append(n)
                continue
            t = Fr(c[2] - np_ + nq, 2 * nr)
            s = vadd(vscale(na, A), vscale(nb, B), vscale(np_, P), vscale(nq, Q),
                     vscale(nr, r_frame(t)))
            if s == c:
                exceptional.setdefault(t, []).append((i, n))
    return exceptional, no_r_reps


# ----------------------------------------------------------- first order ----

def gf2_rank_matrix(rows):
    rows = list(rows)
    rank = 0
    for bit in range(ROLES):
        piv = next((r for r in rows if r >> bit & 1), None)
        if piv is None:
            continue
        rank += 1
        rows = [r ^ piv if r >> bit & 1 else r for r in rows if r != piv]
    return rank


def mask_rows(m):
    return [(m >> (ROLES * i)) & 0xF for i in range(ROLES)]


def diag(bits):
    return sum(1 << (ROLES * i + i) for i, b in enumerate(bits) if b)


RANK = [0] * (1 << 16)
TRACE = [0] * (1 << 16)


def fill_tables():
    for m in range(1 << 16):
        rows = mask_rows(m)
        RANK[m] = gf2_rank_matrix(rows)
        TRACE[m] = sum(rows[i] >> i & 1 for i in range(ROLES)) & 1


def f_floor(m):
    """Fewest rank-one idempotents with sum m (rank and trace parity)."""
    r = RANK[m]
    return r + ((r - TRACE[m]) & 1)


def g_floor(m):
    """Same, when the label must occur at least once."""
    v = f_floor(m)
    return v if v else 2


def check_idempotents():
    count = 0
    for x in range(1, 16):
        for y in range(1, 16):
            if bin(x & y).count("1") & 1:
                m = sum(((x >> i & 1) * y) << (ROLES * i) for i in range(ROLES))
                check(RANK[m] == 1 and TRACE[m] == 1, "idempotent rank/trace")
                count += 1
    check(count == 120, "120 rank-one idempotents")
    return count


PA = diag((1, 0, 0, 1))
PB = diag((0, 1, 1, 0))
PI = diag((1, 1, 1, 1))


def odd_floor():
    return min(f_floor(s) + f_floor(s ^ PA) + f_floor(s ^ PB) + f_floor(s ^ PI)
               for s in range(1 << 16))


def even_floor(m1=PA, m2=PI):
    return min(g_floor(s) + g_floor(s ^ m1) + g_floor(s ^ m2)
               for s in range(1 << 16))


# ------------------------------------------------------- positive control ----

def ga_mul(x, y):
    out = set()
    for a in x:
        for b in y:
            out ^= {vadd(a, b)}
    return frozenset(out)


ZERO = (Fr(0), Fr(0), Fr(0))
ONE = frozenset({ZERO})
NULL = frozenset()


def factor(label, role):
    m = [[ONE if i == j else NULL for j in range(ROLES)] for i in range(ROLES)]
    m[role][role] = frozenset({label})
    return m


def mat_mul(x, y):
    out = []
    for i in range(ROLES):
        row = []
        for j in range(ROLES):
            acc = set()
            for k in range(ROLES):
                acc ^= set(ga_mul(x[i][k], y[k][j]))
            row.append(frozenset(acc))
        out.append(row)
    return out


def word_product(word):
    m = [[ONE if i == j else NULL for j in range(ROLES)] for i in range(ROLES)]
    for label, role in word:
        m = mat_mul(m, factor(label, role))
    return m


def target_matrix():
    return [[frozenset({TARGETS[i]}) if i == j else NULL for j in range(ROLES)]
            for i in range(ROLES)]


def main() -> int:
    check_frames()
    cases = check_lattice_grid()
    exceptional, no_r = support_exceptions()
    check(set(exceptional) == {Fr(0)}, f"exceptional set {sorted(exceptional)}")
    expect_reps = {0: (1, 0, 1, 0, 0), 1: (1, 0, 0, 1, 0),
                   2: (0, 1, 1, 0, 0), 3: (0, 1, 0, 1, 0)}
    for i in range(ROLES):
        check(no_r[i] == [expect_reps[i]], f"unique R-free support of role {i}")

    fill_tables()
    idem = check_idempotents()
    f8 = odd_floor()
    check(f8 == 8, f"odd-denominator first-order floor {f8}")
    g5 = even_floor()
    check(g5 == 5, f"even-denominator visible floor {g5}")
    even_total = g5 + 2 + 1  # two R calls with zero sum, at least one B call
    check(even_total == 8, "even-denominator total")
    # Control: dropping the P-coordinate bits of roles 2 and 3 lowers the
    # visible floor, so those mask bits are live.
    mutated = even_floor(m2=diag((1, 1, 0, 0)))
    check(mutated < g5, "mutated mask lowers the floor")

    direct = [(A, 0), (P, 0), (A, 1), (Q, 1), (B, 2), (P, 2), (B, 3), (Q, 3)]
    check(word_product(direct) == target_matrix(), "direct eight-call word")
    check(word_product(direct[:-1]) != target_matrix(), "dropped call fails")

    print("PASS_FIFTH_RATIONAL_FRAME_EVERY_T_EXACT_MINIMUM_8 "
          f"grid_odd={cases['odd']} grid_even={cases['even']} "
          f"support_exceptions={sorted(str(t) for t in exceptional)} "
          f"idempotents={idem} odd_floor={f8} even_visible_floor={g5} "
          f"even_total={even_total} mutated_visible_floor={mutated} direct_calls=8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
