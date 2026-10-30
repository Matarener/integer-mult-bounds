"""Finite controls for the query-price threshold of the #5554 path family.

The theorem is the written proof in README.md. This script checks it on every
mask with p <= P_MAX pairs, at several exponents, block ranks and query
prices, using 60-digit decimal arithmetic. It is a finite control, not a proof.
"""
import hashlib
import functools
import itertools
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path

getcontext().prec = 60
TOL = Decimal('1e-45')
P_MAX = 6
HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'kappa-architecture-frontier' / 'PROOF.md'
SOURCE_SHA256 = 'c16fd82b009e9ec2a1f2bea5543cce8318f13f70ed062b29b2c425c03e3534e1'
EQUATION_1 = 'E=v(2p+1)+(L-v)n-2v f(1+bn)'


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)


def dec(x):
    return Decimal(x.numerator) / Decimal(x.denominator)


@functools.lru_cache(maxsize=None)
def f(z, t):
    """f(z)=z^t with f(0)=0, for integer z >= 0."""
    if z == 0:
        return Decimal(0)
    return (dec(t) * Decimal(z).ln()).exp()


def path_cost(bits, p, a, b, t, w):
    """Equation (1) of #5554 with v=1, L=0 and QUERY price w per stage."""
    n = sum(bits)
    total = dec(w) * (2 * p + 1 - n) - 2 * f(1 + b * n, t)
    for j in range(1, p):
        h = sum(bits[:2 * j]) if j <= a else sum(bits[2 * j + 1:])
        e = bits[2 * j]
        total += 2 * (f(b * h, t) + e * f(b, t) - f(1 + b * (h + e), t))
    return total


def canonical(n, b, t, w):
    """Canonical invoice (2)-(3) of #5554 with v=1, L=0 and query price w."""
    def delta(z):
        return f(z + 1, t) - f(z, t)
    if n < 3:
        return dec(w) * (3 - n) - 2 * f(1 + b * n, t)
    a = (n - 3) // 2
    d = n - 3 - a
    side = sum(delta(b * k) for k in range(2, a + 2))
    side += sum(delta(b * k) for k in range(2, d + 2))
    return dec(w) * (n - 3) - 2 * f(1 + b * n, t) - 2 * side


def g(k, b, t):
    return f(b, t) + f(b * k + b + 1, t) - f(b * k + 2 * b, t)


def minima(b, t, w):
    best = {}
    for p in range(1, P_MAX + 1):
        for a in range(p):
            for bits in itertools.product((0, 1), repeat=2 * p + 1):
                n = sum(bits)
                cost = path_cost(bits, p, a, b, t, w)
                if n not in best or cost < best[n]:
                    best[n] = cost
    return best


def main():
    data = SOURCE.read_bytes()
    require(hashlib.sha256(data).hexdigest() == SOURCE_SHA256, 'source bytes')
    require(EQUATION_1 in data.decode(), 'source equation (1) not found')
    exponents = (F(1, 2), F(9, 10), F(4983, 5000), F(999, 1000))
    blocks = (2, 8)
    checks = 0
    for b in blocks:
        for t in exponents:
            gs = [g(k, b, t) for k in range(0, 64)]
            require(all(x < y for x, y in zip(gs, gs[1:])), 'g_k not increasing')
            require(gs[0] > 1, 'g_0 <= 1')
            g1 = gs[1]
            g1_frac = F(str(g1))  # 60-digit decimal, used only to place w
            inside = (F(1), (1 + g1_frac) / 2, g1_frac - F(1, 10**40))
            for w in inside:
                got = minima(b, t, w)
                for n, value in got.items():
                    # No mask with p <= P_MAX beats the canonical invoice; it is
                    # attained in range when its own p=max(1,n-2) <= P_MAX.
                    c = canonical(n, b, t, w)
                    require(value > c - TOL,
                            f'canonical beaten b={b} t={t} w={float(w)} n={n}')
                    if n <= P_MAX + 2:
                        require(value < c + TOL, f'canonical not attained n={n}')
                    checks += 1
            w = g1_frac + F(1, 100)
            got = minima(b, t, w)
            for n, value in got.items():
                gap = canonical(n, b, t, w) - value
                if 6 <= n <= P_MAX + 3:
                    require(gap >= 2 * (dec(w) - g1) - TOL,
                            f'n={n} gap below the merge witness')
                checks += 1
            # Explicit n=6 merge witness: right side 10,10 -> 11 at k=1.
            canon6 = (1, 1, 0, 1, 0, 1, 0, 1, 1)  # p=4, a=1, canonical
            merged = (1, 1, 0, 1, 1, 1, 1)        # p=3, a=1, one 11 pair
            c0 = path_cost(canon6, 4, 1, b, t, w)
            c1 = path_cost(merged, 3, 1, b, t, w)
            require(abs(c0 - canonical(6, b, t, w)) < TOL, 'n=6 canonical mask')
            require(abs((c0 - c1) - 2 * (dec(w) - g1)) < TOL, 'merge identity')
            require(c1 < c0, 'merge witness does not win above g_1')
            # Below w=1 an outer 00 pair is profitable at every n: unbounded.
            w = F(99, 100)
            for n in range(0, 3):
                base = (0,) * (3 - n) + (1,) * n
                ext = (0, 0, 0) + base[1:]
                drop = path_cost(base, 1, 0, b, t, w) - path_cost(ext, 2, 1, b, t, w)
                require(abs(drop - 2 * (1 - dec(w))) < TOL, '00 pair gain')
            checks += 1
    print(f'PASS_PATH_QUERY_PRICE_THRESHOLD masks_p_le={P_MAX} '
          f'block_ranks={len(blocks)} exponents={len(exponents)} checks={checks}')


if __name__ == '__main__':
    sys.exit(main())
