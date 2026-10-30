#!/usr/bin/env python3
"""Finite controls for the free-basis-change diagonal minimum.

PROOF.md is the argument. This script checks its finite consequences on small
rings, with free invertible scalar maps placed anywhere in the word:

* Klein ring F2[C2 x C2], n = 2: every word S0 F1 S1 F2 S2 with at most two
  factors I + u y^T (u in R^2, y in F2^2). Each diagonal endpoint is reached
  first at length t(d), and every diagonal with t(d) <= 2 is reached.
* F2[S3] (nonabelian), n = 2: every word with at most one factor.
* F3[x]/(x^2), n = 2: every word with at most one factor and free GL2(F3)
  maps. The first length is the number of entries outside F3^x.
* The kernel lemma: dim_K (D T - I) K^n >= t_K(D) for every diagonal D and
  every T in GL_n(K), over the three rings at n = 2 and the Klein ring at n = 3.
* The normal form: conjugating a factor by a free map gives a factor.

Standard library only. Read-only. Prints a receipt digest bound to this file
and to the declared input.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
INPUT = ROOT / "research/f2-right-vector-diagonal-minimum/PROOF.md"


def need(cond: bool, msg: str) -> None:
    """Fail closed; unlike assert, this survives python -O."""
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


class Ring:
    """A finite K-algebra given by element tables. Elements are ints 0..size-1."""

    def __init__(self, name, size, add, mul, one, zero, scalars, units):
        self.name = name
        self.size = size
        self.add = add  # add[a][b]
        self.mul = mul  # mul[a][b]
        self.one = one
        self.zero = zero
        self.scalars = scalars  # embedded field K, as ring elements, index = field value
        self.units = units  # embedded K^x
        self.neg = [next(b for b in range(size) if add[a][b] == zero) for a in range(size)]

    def sub(self, a, b):
        return self.add[a][self.neg[b]]


def klein_ring() -> Ring:
    # F2[C2 x C2]: group elements g = (a,b) in F2^2 index 0..3; ring element = 4-bit mask.
    def gmul(g, h):
        return g ^ h

    add = [[a ^ b for b in range(16)] for a in range(16)]
    mul = [[0] * 16 for _ in range(16)]
    for a in range(16):
        for b in range(16):
            r = 0
            for g in range(4):
                if a >> g & 1:
                    for h in range(4):
                        if b >> h & 1:
                            r ^= 1 << gmul(g, h)
            mul[a][b] = r
    return Ring("F2[C2xC2]", 16, add, mul, one=1, zero=0, scalars=[0, 1], units=[1])


def s3_ring() -> Ring:
    perms = list(itertools.permutations(range(3)))
    index = {p: i for i, p in enumerate(perms)}
    ident = index[(0, 1, 2)]

    def gmul(g, h):
        p, q = perms[g], perms[h]
        return index[tuple(p[q[k]] for k in range(3))]

    size = 1 << 6
    add = [[a ^ b for b in range(size)] for a in range(size)]
    mul = [[0] * size for _ in range(size)]
    for a in range(size):
        for b in range(size):
            r = 0
            for g in range(6):
                if a >> g & 1:
                    for h in range(6):
                        if b >> h & 1:
                            r ^= 1 << gmul(g, h)
            mul[a][b] = r
    one = 1 << ident
    return Ring("F2[S3]", size, add, mul, one=one, zero=0, scalars=[0, one], units=[one])


def dual_f3_ring() -> Ring:
    # F3[x]/(x^2): element a + b x encoded as a + 3 b.
    def dec(e):
        return e % 3, e // 3

    def enc(a, b):
        return (a % 3) + 3 * (b % 3)

    add = [[0] * 9 for _ in range(9)]
    mul = [[0] * 9 for _ in range(9)]
    for e in range(9):
        a, b = dec(e)
        for f in range(9):
            c, d = dec(f)
            add[e][f] = enc(a + c, b + d)
            mul[e][f] = enc(a * c, a * d + b * c)
    return Ring("F3[x]/(x^2)", 9, add, mul, one=1, zero=0, scalars=[0, 1, 2], units=[1, 2])


# ---------------------------------------------------------------------------
# n x n matrices over a Ring, stored as flat tuples in row-major order.


def mat_mul(R: Ring, A, B, n):
    out = []
    for i in range(n):
        for j in range(n):
            acc = R.zero
            for k in range(n):
                acc = R.add[acc][R.mul[A[i * n + k]][B[k * n + j]]]
            out.append(acc)
    return tuple(out)


def identity(R: Ring, n):
    return tuple(R.one if i == j else R.zero for i in range(n) for j in range(n))


def is_diagonal(R: Ring, M, n):
    return all(M[i * n + j] == R.zero for i in range(n) for j in range(n) if i != j)


def t_count(R: Ring, M, n):
    """Number of diagonal entries outside the embedded unit group K^x."""
    return sum(1 for i in range(n) if M[i * n + i] not in R.units)


def scalar_gl(R: Ring, n):
    """All invertible n x n matrices with entries in the embedded field K."""
    ident = identity(R, n)
    mats = list(itertools.product(R.scalars, repeat=n * n))
    out = []
    for A in mats:
        for B in mats:
            if mat_mul(R, A, B, n) == ident:
                out.append(A)
                break
    return out


def factors(R: Ring, n):
    """All matrices I + u y^T with u in R^n and y in K^n, y nonzero."""
    ident = identity(R, n)
    out = set()
    for u in itertools.product(range(R.size), repeat=n):
        for y in itertools.product(R.scalars, repeat=n):
            if all(c == R.zero for c in y):
                continue
            M = list(ident)
            for i in range(n):
                for j in range(n):
                    M[i * n + j] = R.add[M[i * n + j]][R.mul[u[i]][y[j]]]
            out.add(tuple(M))
    return out


def inverse_in(R, S, group, n):
    ident = identity(R, n)
    return next(T for T in group if mat_mul(R, S, T, n) == ident)


def check_normal_form(R: Ring, n, facs, group):
    """S F S^{-1} is again a factor for every free map S and factor F."""
    for S in group:
        Si = inverse_in(R, S, group, n)
        for F in facs:
            need(mat_mul(R, mat_mul(R, S, F, n), Si, n) in facs, f"{R.name}: conjugate left the alphabet")
    return len(group) * len(facs)


def first_lengths(R: Ring, n, max_len, facs, group):
    """Map each diagonal endpoint of a word S0 F1 S1 ... FL SL (L <= max_len)
    to its first length L.

    By the normal form every such word equals F'1 ... F'L S with factors F'
    and one free map S, and conversely. The search uses that form; the
    normal-form premise is checked separately by check_normal_form.
    """
    first = {}
    layer = {identity(R, n)}
    seen = set(layer)
    for length in range(max_len + 1):
        for Q in layer:
            for S in group:
                P = mat_mul(R, Q, S, n)
                if is_diagonal(R, P, n) and P not in first:
                    first[P] = length
        if length == max_len:
            break
        nxt = set()
        for Q in layer:
            for F in facs:
                P = mat_mul(R, Q, F, n)
                if P not in seen:
                    nxt.add(P)
        seen |= nxt
        layer = nxt
    return first


def check_first_lengths(R: Ring, n, max_len):
    facs = factors(R, n)
    group = scalar_gl(R, n)
    conj = check_normal_form(R, n, facs, group)
    first = first_lengths(R, n, max_len, facs, group)
    for P, length in first.items():
        need(length >= t_count(R, P, n), f"{R.name}: diagonal below its count at length {length}")
        need(length == t_count(R, P, n), f"{R.name}: first length differs from t_K")
    diagonals = 0
    for entries in itertools.product(range(R.size), repeat=n):
        D = tuple(entries[i] if i == j else R.zero for i in range(n) for j in range(n))
        if t_count(R, D, n) <= max_len:
            diagonals += 1
            need(D in first, f"{R.name}: diagonal with t <= {max_len} not reached")
    return {
        "ring": R.name,
        "n": n,
        "max_factors": max_len,
        "factor_alphabet": len(facs),
        "free_maps": len(group),
        "conjugations_checked": conj,
        "diagonals_reached": len(first),
        "diagonals_with_t_le_max": diagonals,
    }


def kernel_lemma(R: Ring, n):
    """dim_K of the image of w -> (D T - I) w on K^n is at least t_K(D)."""
    group = scalar_gl(R, n)
    ident = identity(R, n)
    vectors = list(itertools.product(R.scalars, repeat=n))
    q = len(R.scalars)
    cases = 0
    tight = 0
    for entries in itertools.product(range(R.size), repeat=n):
        D = tuple(entries[i] if i == j else R.zero for i in range(n) for j in range(n))
        t = t_count(R, D, n)
        for T in group:
            M = mat_mul(R, D, T, n)
            M = tuple(R.sub(M[k], ident[k]) for k in range(n * n))
            image = set()
            for w in vectors:
                image.add(tuple(
                    _row_dot(R, M, w, i, n) for i in range(n)
                ))
            # The image is a K-subspace; its size is q^dim.
            dim = 0
            while q ** dim < len(image):
                dim += 1
            need(q ** dim == len(image), f"{R.name}: image is not a K-subspace")
            need(dim >= t, f"{R.name}: kernel lemma fails")
            cases += 1
            tight += dim == t
    return {"ring": R.name, "n": n, "cases": cases, "tight_cases": tight}


def _row_dot(R, M, w, i, n):
    acc = R.zero
    for k in range(n):
        acc = R.add[acc][R.mul[M[i * n + k]][w[k]]]
    return acc


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    need(INPUT.is_file(), f"missing declared input {INPUT}")
    klein, s3, dual = klein_ring(), s3_ring(), dual_f3_ring()

    # Sanity: S3 ring is nonabelian, the dual-number ring has K = F3.
    need(any(s3.mul[a][b] != s3.mul[b][a] for a in range(64) for b in range(64)), "F2[S3] commutes")

    searches = [
        check_first_lengths(klein, 2, 2),
        check_first_lengths(s3, 2, 1),
        check_first_lengths(dual, 2, 1),
    ]
    lemmas = [kernel_lemma(klein, 2), kernel_lemma(s3, 2), kernel_lemma(dual, 2), kernel_lemma(klein, 3)]

    # Free maps can absorb entries in K^x: over F3, diag(2,2) needs no factor.
    dual_first = first_lengths(dual, 2, 0, factors(dual, 2), scalar_gl(dual, 2))
    need(dual_first.get((2, 0, 0, 2)) == 0, "F3: diag(2,2) should be free")

    # Sharpness control (#4099's witness): an R-valued right vector breaks the
    # count. With u = (z1, z2) and y = (z2, z1), one factor is diag(1+z1z2, 1+z1z2).
    z1, z2 = 0b0011, 0b0101
    witness = tuple(
        klein.add[klein.one if i == j else 0][klein.mul[(z1, z2)[i]][(z2, z1)[j]]]
        for i in range(2) for j in range(2)
    )
    need(is_diagonal(klein, witness, 2) and t_count(klein, witness, 2) == 2, "witness control")
    need(witness not in factors(klein, 2), "witness must lie outside the K-valued alphabet")

    result = {"searches": searches, "kernel_lemma": lemmas}
    blob = json.dumps(result, sort_keys=True).encode()
    receipt = hashlib.sha256(
        blob + sha256(Path(__file__)).encode() + sha256(INPUT).encode()
    ).hexdigest()
    for row in searches:
        print(json.dumps(row, sort_keys=True))
    for row in lemmas:
        print(json.dumps(row, sort_keys=True))
    print(f"input_sha256={sha256(INPUT)}")
    print(f"receipt_sha256={receipt}")
    print(
        "PASS_RIGHT_VECTOR_DIAGONAL_FREE_BASIS "
        + " ".join(f"{r['ring']}:n{r['n']}:L{r['max_factors']}={r['diagonals_reached']}" for r in searches)
        + " no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
