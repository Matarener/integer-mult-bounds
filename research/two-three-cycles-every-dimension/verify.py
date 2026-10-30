"""Finite corroboration for the all-dimension two-3-cycle reduction.

Model: M_R(F2[GL_n(F2)]). A group element is a tuple of row bitmasks, so the
coordinate CNOT with row i gaining bit j is x_i <- x_i + x_j ("writes i,
reads j"). An algebra element is a frozenset of group elements (F2
coefficients). A paid call is D(g, N) = I + ([g] + [e]) N with N a rank-one
binary idempotent. The written proof is PROOF.md; these checks exercise its
lemmas on concrete words. They do not search for length-10 or length-11 words.
"""

from __future__ import annotations

import itertools
import json
import random
import sys

MARK = "PASS_TWO_THREE_CYCLES_EVERY_DIMENSION"


def need(cond, msg):
    if not cond:
        raise SystemExit("FAIL: " + msg)


def gmul(a, b, n):
    out = []
    for i in range(n):
        acc = 0
        for k in range(n):
            if a[i] >> k & 1:
                acc ^= b[k]
        out.append(acc)
    return tuple(out)


def ident(n):
    return tuple(1 << i for i in range(n))


def cnot(n, i, j):
    g = list(ident(n))
    g[i] ^= 1 << j
    return tuple(g)


def gtranspose(g, n):
    return tuple(sum(((g[r] >> c) & 1) << r for r in range(n)) for c in range(n))


def amul(x, y, n):
    acc = set()
    for g in x:
        for h in y:
            acc ^= {gmul(g, h, n)}
    return frozenset(acc)


def mmul(X, Y, n):
    R = len(X)
    out = []
    for i in range(R):
        row = []
        for j in range(R):
            acc = set()
            for k in range(R):
                acc ^= amul(X[i][k], Y[k][j], n)
            row.append(frozenset(acc))
        out.append(tuple(row))
    return tuple(out)


def scalar(M, n):
    e = frozenset({ident(n)})
    return tuple(tuple(e if M[i][j] else frozenset() for j in range(len(M))) for i in range(len(M)))


def idempotents(R):
    out = []
    for u in range(1, 1 << R):
        for v in range(1, 1 << R):
            if bin(u & v).count("1") % 2 == 1:
                out.append(tuple(tuple((u >> i & 1) & (v >> j & 1) for j in range(R)) for i in range(R)))
    return out


def call(g, N, n):
    """I + ([g] + [e]) N."""
    R = len(N)
    e = ident(n)
    x = frozenset({g}) ^ frozenset({e}) if g != e else frozenset()
    rows = []
    for i in range(R):
        row = []
        for j in range(R):
            v = frozenset({e}) if i == j else frozenset()
            if N[i][j]:
                v = v ^ x
            row.append(v)
        rows.append(tuple(row))
    return tuple(rows)


def product(word, n, R):
    P = scalar(tuple(tuple(int(i == j) for j in range(R)) for i in range(R)), n)
    for g, N in word:
        P = mmul(P, call(g, N, n), n)
    return P


def mmap(P, f):
    return tuple(tuple(frozenset(f(x)) for x in row) for row in P)


def proj_row_stab(P, k, n):
    want = 1 << k
    return mmap(P, lambda x: {g for g in x if g[k] == want})


def augment(P):
    return tuple(tuple(len(x) % 2 for x in row) for row in P)


def f2rank(M):
    rows = [sum(b << j for j, b in enumerate(r)) for r in M]
    rank = 0
    for bit in range(len(M[0]) if M else 0):
        piv = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def delete_coord(g, k, n):
    keep = [r for r in range(n) if r != k]
    out = []
    for r in keep:
        m = 0
        for pos, c in enumerate(keep):
            if g[r] >> c & 1:
                m |= 1 << pos
        out.append(m)
    return tuple(out)


def writes(g, n):
    e = ident(n)
    return next(i for i in range(n) if g[i] != e[i])


def reads(g, n):
    e = ident(n)
    i = writes(g, n)
    return next(j for j in range(n) if (g[i] ^ e[i]) >> j & 1)


def three_cycle(n):
    # rows 0,1,2 of c are rows 1,2,0 of the identity; all other rows fixed
    e = ident(n)
    return tuple([e[1], e[2], e[0]] + list(e[3:]))


def three_cycle_inverse(n):
    e = ident(n)
    return tuple([e[2], e[0], e[1]] + list(e[3:]))


def main():
    rng = random.Random(20261027)
    stats = {}

    # A. every paid call is an involution (n=5, R=2: 20 CNOTs x 6 idempotents)
    n, R = 5, 2
    Ns = idempotents(R)
    need(len(Ns) == 6, "six rank-one idempotents in M_2(F2)")
    gens = [cnot(n, i, j) for i in range(n) for j in range(n) if i != j]
    I2 = scalar(((1, 0), (0, 1)), n)
    for g in gens:
        for N in Ns:
            D = call(g, N, n)
            need(mmul(D, D, n) == I2, "paid call is an involution")
    stats["involution_calls"] = len(gens) * len(Ns)

    # B. I + N has F2-rank R-1 for every rank-one idempotent, R = 2 and 3
    for RR in (2, 3):
        for N in idempotents(RR):
            M = tuple(tuple((int(i == j) + N[i][j]) % 2 for j in range(RR)) for i in range(RR))
            need(f2rank(M) == RR - 1, "rank(I+N) = R-1")
    stats["idempotents_checked"] = {"R2": 6, "R3": len(idempotents(3))}

    # C. projection identity pi_k(P) = A (I+N_t) B when k is written once
    trials = 0
    for _ in range(150):
        k = rng.randrange(n)
        L = rng.randrange(2, 8)
        t = rng.randrange(L)
        others = [g for g in gens if writes(g, n) != k]
        once = [g for g in gens if writes(g, n) == k]
        word = [(rng.choice(others), rng.choice(Ns)) for _ in range(L)]
        word[t] = (rng.choice(once), rng.choice(Ns))
        P = product(word, n, R)
        A = product(word[:t], n, R)
        B = product(word[t + 1:], n, R)
        Nt = word[t][1]
        IN = scalar(tuple(tuple((int(i == j) + Nt[i][j]) % 2 for j in range(R)) for i in range(R)), n)
        need(proj_row_stab(P, k, n) == mmul(mmul(A, IN, n), B, n), "projection identity")
        rest = mmul(mmul(A, mmap(scalar(Nt, n), lambda x: {word[t][0]} if x else set()), n), B, n)
        need(all(g[k] != 1 << k for row in rest for x in row for g in x), "written-once term leaves the stabilizer")
        need(f2rank(augment(proj_row_stab(P, k, n))) == R - 1, "projected augmentation has rank R-1")
        trials += 1
    stats["projection_trials"] = trials

    # D/E. restriction (k never written) and quotient (k never read) are homomorphisms
    for mode in ("restrict", "quotient"):
        for _ in range(60):
            k = rng.randrange(3, n)
            if mode == "restrict":
                pool = [g for g in gens if writes(g, n) != k]
            else:
                pool = [g for g in gens if reads(g, n) != k]
            word = [(rng.choice(pool), rng.choice(Ns)) for _ in range(rng.randrange(1, 7))]
            P = product(word, n, R)
            lhs = mmap(P, lambda x: _reduce_set(x, k, n))
            short = [(delete_coord(g, k, n), N) for g, N in word]
            short = [(g, N) for g, N in short if g != ident(n - 1)]
            need(lhs == product(short, n - 1, R), mode + " homomorphism")
        stats[mode + "_trials"] = 60

    # F. transpose anti-automorphism reverses words and keeps calls legal
    for _ in range(60):
        word = [(rng.choice(gens), rng.choice(Ns)) for _ in range(rng.randrange(1, 7))]
        P = product(word, n, R)
        tP = tuple(tuple(frozenset(gtranspose(g, n) for g in P[j][i]) for j in range(R)) for i in range(R))
        tw = [(gtranspose(g, n), tuple(tuple(N[j][i] for j in range(R)) for i in range(R))) for g, N in reversed(word)]
        need(all(writes(a, n) == reads(b, n) for (a, _), (b, _) in zip(tw, reversed(word))), "transpose swaps write and read")
        need(tP == product(tw, n, R), "transpose anti-automorphism")
    stats["transpose_trials"] = 60

    # G. exhaustive single-write lemma instance: n=4, R=2, all words of length <= 3
    n4 = 4
    gens4 = [cnot(n4, i, j) for i in range(n4) for j in range(n4) if i != j]
    letters = [(g, N) for g in gens4 for N in Ns]
    calls4 = {(g, N): call(g, N, n4) for g, N in letters}
    I24 = scalar(((1, 0), (0, 1)), n4)
    checked = 0
    stack = [((), I24)]
    while stack:
        word, P = stack.pop()
        if word:
            counts = [0] * n4
            for g, _ in word:
                counts[writes(g, n4)] += 1
            for k in range(n4):
                if counts[k] == 1:
                    proj = proj_row_stab(P, k, n4)
                    need(f2rank(augment(proj)) == 1, "single-write projection has augmentation rank 1")
                    checked += 1
        if len(word) < 3:
            for lt in letters:
                if word and word[-1] == lt:
                    continue
                stack.append((word + (lt,), mmul(P, calls4[lt], n4)))
    stats["exhaustive_single_write_cases_n4_len_le3"] = checked

    # H. the 12-call upper bound in every dimension (shown at n=5): spectators untouched
    c = three_cycle(n)
    swap01 = [cnot(n, 0, 1), cnot(n, 1, 0), cnot(n, 0, 1)]
    swap12 = [cnot(n, 1, 2), cnot(n, 2, 1), cnot(n, 1, 2)]
    seq = swap01 + swap12
    acc = ident(n)
    for g in seq:
        acc = gmul(acc, g, n)
    need(acc in (c, three_cycle_inverse(n)), "two swaps give a coordinate 3-cycle")
    c = acc
    E00 = ((1, 0), (0, 0))
    E11 = ((0, 0), (0, 1))
    word12 = [(g, E00) for g in seq] + [(g, E11) for g in seq]
    T = product(word12, n, R)
    need(T == ((frozenset({c}), frozenset()), (frozenset(), frozenset({c}))), "12-call word realizes diag([c],[c])")
    need(all(writes(g, n) < 3 and reads(g, n) < 3 for g, _ in word12), "upper word never touches spectators")
    stats["upper_bound_calls"] = len(word12)

    # I. counting: L' = W_T + W_S with W_T >= 6, W_S >= 2s; W_T = a+b, R_T = a+c, etc.
    profiles = []
    for L in range(0, 12):
        for s in range(0, 6):
            for wt in range(6, L + 1):
                ws = L - wt
                if ws >= 2 * s and (s > 0 or ws == 0):
                    profiles.append((L, s, wt, ws))
    need(all(s <= 2 for _, s, _, _ in profiles), "length <= 11 forces at most two live spectators")
    need(all(s <= 1 for L, s, _, _ in profiles if L <= 9), "length <= 9 forces at most one live spectator")
    residual = sorted({(L, wt, ws) for L, s, wt, ws in profiles if s == 2})
    need(residual == [(10, 6, 4), (11, 6, 5), (11, 7, 4)], "residual write profiles")
    stats["residual_s2_write_profiles"] = [list(r) for r in residual]

    # J. controls: the identity fails when a corrupted factor is used
    k = 0
    word = [(cnot(n, 1, 2), Ns[0]), (cnot(n, 0, 3), Ns[1]), (cnot(n, 2, 4), Ns[2])]
    P = product(word, n, R)
    A = product(word[:1], n, R)
    B = product(word[2:], n, R)
    bad = mmul(A, B, n)
    need(proj_row_stab(P, k, n) != bad, "control: dropping I+N_t is detected")
    need(f2rank(((1, 0), (0, 1))) == 2, "control: identity has full rank, unlike I+N")
    stats["controls"] = 2

    print(MARK, json.dumps(stats, sort_keys=True))


def _reduce_set(x, k, n):
    out = set()
    for g in x:
        out ^= {delete_coord(g, k, n)}
    return out


if __name__ == "__main__":
    sys.exit(main())
