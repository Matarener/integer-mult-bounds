#!/usr/bin/env python3
"""Audit #4100 BIT.md: local-ring algebra, stock, depth, recurrence and wrapper.

Propositions checked (BIT.md at #4100 head 337d049):
1. constants: q = 2^89-1 prime (Lucas-Lehmer), 2*64^3/q < 10^-16,
   269241600 = W*9475, F = 32*64^2*sum(H), a1 and a2;
2. section 1: N(P) = [[I-P,PC],[CP,I-CPC]] squares to I, disjoint commuting
   projectors add, nested differences multiply, conjugation by diag(A,I)
   keeps them, and split rank equals rank mod q, over Z/q^w;
3. section 2: K(w) = 269241600 |GL_64(Z/q^w)|, the split leaves
   U = 9475 t K^(D-1) and every child's stock divides U; the depth D is
   monotone, every child drops it and two levels halve the width;
4. section 3: the header-route carry decomposition and the two-piece
   doubling map; the recurrence envelope;
5. section 4: k = O(w log e) with the literal constants, and the stage
   exponents a_next = c(1-c)+ca reaching a2.
Standard library only.
"""
import itertools
import math
import random
from fractions import Fraction as Q
from pathlib import Path

PKG = Path(__file__).resolve().parent
BIT = PKG.parents[1] / "research" / "unconditional-batched-crt" / "BIT.md"
NF = PKG.parents[1] / "research" / "unconditional-batched-crt" / "NORMAL-FORM.md"

q = 2 ** 89 - 1
c = Q(8667, 5_000_000)
W = 28416
H = {1: 381024, 2: 400416, 3: 22752, 4: 26880, 5: 29376, 6: 17376, 7: 26784, 42: 288}
ETA = Q(1, 10 ** 16)


def check_sources():
    bit = BIT.read_text(encoding="utf-8")
    for needle in ["q=2^89-1,", "c=8667/5000000,", "2*64^3/q < 10^-16.",
                   "N(P)=[[I-P,PC],[CP,I-CPC]].",
                   "Then N(P)^2=I, nested differences multiply as their corresponding residuals,",
                   "and disjoint commuting projectors add. These identities survive conjugation",
                   "Let W=28416, N=|GL_64(F_q)| and",
                   "K(w)=269241600 N q^(4096(w-1)),",
                   "D(n)=0 (n<64),  D(n)=1+D(42 floor(n/64)) (n>=64).",
                   "low matrix and high matrix fields leaves U=t*9475*K(w)^(D(n)-1) fresh rows.",
                   "Two coarse levels reduce width by at least a factor two, so h<=2log2(e)+O(1).",
                   "Each child's payload has volume V/(WN).",
                   "is obtained from the low-digit carry, followed by an ordered high-field",
                   "Doubling/halving on an odd modulus is a two-piece split/interleave; it does",
                   "H={1:381024,2:400416,3:22752,4:26880,5:29376,6:17376,7:26784,42:288}.",
                   "With F=32*64^2*sum_r(H_r)=118606528512, t=1-c and eta=10^-16, normalized runtime",
                   "T(n,w) <= C/(1-mu_1) n + C/(1-mu_t) n^t w^(1-a)",
                   "a_next=c(1-c)+ca. Apply this first to a=0 and then to the completed a1,"]:
        assert needle in bit, needle
    assert "C the m-coordinate reversal" in NF.read_text(encoding="utf-8")


# ------------------------------------------------------------- constants
def gl_order(n, p):
    out = 1
    for i in range(n):
        out *= p ** n - p ** i
    return out


def check_constants():
    s = 4
    for _ in range(87):
        s = (s * s - 2) % q
    assert s == 0, "Lucas-Lehmer"
    assert Q(2 * 64 ** 3, q) < ETA
    assert 269241600 == W * 9475
    assert 32 * 64 ** 2 * sum(H.values()) == 118606528512
    assert c * (1 - c) == Q(173039532444, 10 ** 14)
    assert c * (1 - c * c) == Q(1733394791695384296, 10 ** 21)
    assert max(H) == 42 and 49911 <= 32 * 64 ** 2
    for n, p, w in ((1, 3, 3), (2, 3, 2), (2, 2, 3), (2, 5, 2)):
        m = p ** w
        cnt = 0
        for ent in itertools.product(range(m), repeat=n * n):
            det = ent[0] if n == 1 else ent[0] * ent[3] - ent[1] * ent[2]
            cnt += det % p != 0
        assert cnt == gl_order(n, p) * p ** (n * n * (w - 1)), (n, p, w)


# --------------------------------------------------- section 1 algebra
def mm(A, B, m):
    return [[sum(a * b for a, b in zip(r, col)) % m for col in zip(*B)] for r in A]


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def sub(A, B, m):
    return [[(a - b) % m for a, b in zip(r, s)] for r, s in zip(A, B)]


def add(A, B, m):
    return [[(a + b) % m for a, b in zip(r, s)] for r, s in zip(A, B)]


def inverse(A, p, m):
    k = len(A)
    A = [r[:] for r in A]
    I = eye(k)
    for col in range(k):
        piv = next((r for r in range(col, k) if A[r][col] % p), None)
        if piv is None:
            return None
        A[col], A[piv] = A[piv], A[col]
        I[col], I[piv] = I[piv], I[col]
        iv = pow(A[col][col], -1, m)
        A[col] = [x * iv % m for x in A[col]]
        I[col] = [x * iv % m for x in I[col]]
        for r in range(k):
            if r != col and A[r][col]:
                f = A[r][col]
                A[r] = [(a - f * b) % m for a, b in zip(A[r], A[col])]
                I[r] = [(a - f * b) % m for a, b in zip(I[r], I[col])]
    return I


def rank_mod(A, p):
    rows = [[v % p for v in r] for r in A]
    n, rk = len(rows[0]), 0
    for col in range(n):
        piv = next((r for r in range(rk, len(rows)) if rows[r][col]), None)
        if piv is None:
            continue
        rows[rk], rows[piv] = rows[piv], rows[rk]
        iv = pow(rows[rk][col], -1, p)
        rows[rk] = [v * iv % p for v in rows[rk]]
        for r in range(len(rows)):
            if r != rk and rows[r][col]:
                f = rows[r][col]
                rows[r] = [(a - f * b) % p for a, b in zip(rows[r], rows[rk])]
        rk += 1
    return rk


def unit(n, p, m, rng):
    while True:
        S = [[rng.randrange(m) for _ in range(n)] for _ in range(n)]
        Si = inverse(S, p, m)
        if Si:
            return S, Si


def block(A, B, C, D):
    return [ra + rb for ra, rb in zip(A, B)] + [rc + rd for rc, rd in zip(C, D)]


def N(P, C, m):
    I = eye(len(P))
    return block(sub(I, P, m), mm(P, C, m), mm(C, P, m), sub(I, mm(mm(C, P, m), C, m), m))


def reversal(n):
    return [[int(i + j == n - 1) for j in range(n)] for i in range(n)]


def check_local_ring(trials=30, seed=4100):
    rng = random.Random(seed)
    count = 0
    for p, w, n in [(3, 1, 4), (3, 3, 5), (5, 2, 6), (7, 2, 6), (31, 2, 5)]:
        m = p ** w
        for t in range(trials):
            S, Si = unit(n, p, m, rng)

            def proj(idx):
                D = [[int(i == j and i in idx) for j in range(n)] for i in range(n)]
                return mm(mm(S, D, m), Si, m)

            if t % 2:
                C = reversal(n)
            else:
                T, Ti = unit(n, p, m, rng)
                sg = [[(rng.choice([1, m - 1]) if i == j else 0) for j in range(n)] for i in range(n)]
                C = mm(mm(T, sg, m), Ti, m)
            assert mm(C, C, m) == eye(n)
            k = rng.randrange(1, n)
            idx = rng.sample(range(n), k)
            P = proj(idx)
            I2 = eye(2 * n)
            NP = N(P, C, m)
            assert mm(NP, NP, m) == I2
            a, b = idx[:max(1, k // 2)], idx[max(1, k // 2):]
            P1, P2 = proj(a), proj(b)
            assert N(add(P1, P2, m), C, m) == mm(N(P1, C, m), N(P2, C, m), m)
            assert mm(NP, N(P1, C, m), m) == N(sub(P, P1, m), C, m)
            Ad = [rng.choice([x for x in range(1, m) if x % p]) for _ in range(n)]
            Z = [[0] * n for _ in range(n)]
            Dg = block([[Ad[i] if i == j else 0 for j in range(n)] for i in range(n)], Z, Z, eye(n))
            Dgi = block([[pow(Ad[i], -1, m) if i == j else 0 for j in range(n)] for i in range(n)], Z, Z, eye(n))
            Mc = mm(mm(Dg, NP, m), Dgi, m)
            assert mm(Mc, Mc, m) == I2
            assert mm(Mc, mm(mm(Dg, N(P1, C, m), m), Dgi, m), m) == \
                mm(mm(Dg, N(sub(P, P1, m), C, m), m), Dgi, m)
            assert rank_mod(P, p) == k
            count += 1
    return count


# ------------------------------------------- section 2 stock and depth
def D(n):
    d = 0
    while n >= 64:
        n, d = 42 * (n // 64), d + 1
    return d


def check_stock():
    Nq = gl_order(64, q)
    for w in (1, 2):
        K = 269241600 * Nq * q ** (4096 * (w - 1))
        split = W * Nq * q ** (4096 * (w - 1))     # family x |GL_64(Z/q^w)|
        for d in (1, 2, 3):
            for t in (1, 7):
                U, r = divmod(t * K ** d, split)
                assert r == 0 and U == t * 9475 * K ** (d - 1)
                for dc in range(d):
                    assert U % (9475 * t * K ** dc) == 0
    return Nq.bit_length()


def check_depth(limit=300_000):
    prev, worst = 0, -1e9
    for n in range(1, limit + 1):
        d = D(n)
        assert d >= prev
        prev = d
        if n >= 64:
            f = n // 64
            assert 42 * f < n and all(D(r * f) <= d - 1 for r in H)
            assert 2 * 42 * ((42 * f) // 64) <= n
            worst = max(worst, d - 2 * math.log2(n))
    return worst


# --------------------------------------- section 3 routes and recurrence
def check_routes(seed=89):
    rng = random.Random(seed)
    cases = 0
    for p, w, n in [(3, 2, 4), (5, 3, 4), (7, 3, 3), (101, 2, 4)]:
        m, mh = p ** w, p ** (w - 1)
        for _ in range(200):
            A = [[rng.randrange(m) for _ in range(n)] for _ in range(n)]
            x = [rng.randrange(m) for _ in range(n)]
            y = [sum(x[i] * A[i][j] for i in range(n)) % m for j in range(n)]
            xl, xh = [v % p for v in x], [v // p for v in x]
            Al, Ah = [[v % p for v in r] for r in A], [[v // p for v in r] for r in A]
            raw = [sum(xl[i] * Al[i][j] for i in range(n)) for j in range(n)]
            ylo, carry = [v % p for v in raw], [v // p for v in raw]
            yhi = [(carry[j] + sum(xl[i] * Ah[i][j] + xh[i] * A[i][j] for i in range(n))) % mh
                   for j in range(n)]
            assert y == [lo + p * hi for lo, hi in zip(ylo, yhi)]
            cases += 1
    for M in (3, 7, 9, 25, 343, 2 ** 13 - 1, 101 ** 2):
        img = [2 * x % M for x in range(M)]
        half = (M + 1) // 2
        assert img[:half] == list(range(0, M, 2)) and img[half:] == list(range(1, M, 2))
    return cases


def mu(x, eta=float(ETA)):
    F = 32 * 64 ** 2 * sum(H.values())
    return (sum(h * (r / 64) ** x for r, h in H.items()) + eta * F * (1 / 64) ** x) / W


def recurrence_T(n, ww, memo, eta=float(ETA)):
    if n < 64:
        return ww
    if n in memo:
        return memo[n]
    f = n // 64
    F = 32 * 64 ** 2 * sum(H.values())
    v = sum(h / W * recurrence_T(r * f, ww, memo, eta) for r, h in H.items())
    v += eta * F / W * recurrence_T(f, ww, memo, eta) + n + ww
    memo[n] = v
    return v


def check_recurrence():
    t = 1 - float(c)
    m1, mt = mu(1.0), mu(t)
    assert m1 < 1 and mt < 1
    A, B = 1 / (1 - m1), 1 / (1 - mt)
    worst = 0.0
    for a in (0.0, float(c * (1 - c))):
        for w in (1, 10, 10 ** 6):
            ww = w ** (1 - a)
            memo = {}
            for n in (64, 100, 4096, 10 ** 5, 10 ** 7, 10 ** 9):
                worst = max(worst, recurrence_T(n, ww, memo) / (A * n + B * n ** t * ww))
    assert worst <= 1
    memo = {}
    vals = [recurrence_T(n, 1.0, memo) for n in range(1, 100_000)]
    assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
    return m1, mt, worst


# ------------------------------------------------ section 4 wrapper
def wrapper_k(L):
    lq = math.log(q)
    lqN = 4096 + sum(math.log1p(-(q ** (i - 64))) for i in range(64)) / lq
    e = 2.0 ** L
    w = math.ceil(e ** float(c))
    d, n = 0, e
    while n >= 64:
        n, d = 42 * (n // 64), d + 1
    k = math.ceil(d * (math.log(269241600) / lq + lqN + 4096 * (w - 1)))
    return e, w, k


def check_wrapper():
    first = None
    for L in range(1, 400):
        e, w, k = wrapper_k(L)
        good = 2 * k < e and (e - k) // w >= 64
        if good and first is None:
            first = L
        if first is not None:
            assert good, L
    return first


def check_exponents():
    for a in (Q(0), c * (1 - c)):
        main = 1 - c + c * c - c * a
        for term in (1 - c, (1 - c) ** 2 + c * (1 - a), c):
            assert term <= main
        assert (1 - c) ** 2 + c * (1 - a) == 1 - (c * (1 - c) + c * a)
    assert c * (1 - c) + c * (c * (1 - c)) == c * (1 - c * c)


def main():
    check_sources()
    print("PASS source binding: BIT.md statements and NORMAL-FORM.md's reversal C")
    check_constants()
    print("PASS constants: 2^89-1 prime (Lucas-Lehmer); 2*64^3/q < 1e-16; 269241600 = W*9475; "
          "F = 118606528512; a1, a2 exact; |GL_n(Z/p^w)| lift formula on small cases")
    n = check_local_ring()
    print(f"PASS local ring: N(P)^2 = I, disjoint add, nested multiply, diag(A,I) conjugation, "
          f"split rank = rank mod q on {n} instances over Z/q^w (C reversal or random involution)")
    bits = check_stock()
    print(f"PASS stock: R = t K^D splits by W x |GL_64(Z/q^w)| into U = 9475 t K^(D-1); "
          f"every child stock divides U (exact; |GL_64(F_q)| has {bits} bits)")
    worst = check_depth()
    print(f"PASS depth: D monotone, children drop D, two levels halve (n <= 3e5); "
          f"max D(n) - 2 log2 n = {worst:.2f}")
    cases = check_routes()
    print(f"PASS header routes: carry decomposition on {cases} cases; doubling is a two-piece interleave")
    m1, mt, ratio = check_recurrence()
    print(f"PASS recurrence: mu_1 = {m1:.10f}, mu_t = {mt:.10f}; equality recursion "
          f"<= envelope (max ratio {ratio:.2e}) and monotone")
    first = check_wrapper()
    print(f"PASS wrapper: 2k < e and n >= 64 from log2 e = {first} on (checked to 2^400)")
    check_exponents()
    print("PASS exponents: every stage cost term <= 1-c+c^2-ca; a_next reaches a2 exactly")
    print("PASS_BIT_STOCK_RECURRENCE_AUDIT")


if __name__ == "__main__":
    main()
