"""Exact low/high lowering for a complete rational RIGHT word.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The elementary carry identity retains the selected-bit-qadic-route credit.
"""
from fractions import Fraction as F
from math import gcd, lcm


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def matrix(word, n=8):
    out = identity(n)
    for op in word:
        kind, i = op[:2]
        need(type(i) is int and 0 <= i < n, 'source coordinate')
        c = F(op[-1])
        need(c and c.denominator & (c.denominator-1) == 0, 'dyadic coefficient')
        if kind == 'ADD':
            j = op[2]
            need(len(op) == 4 and type(j) is int and 0 <= j < n and i != j, 'ADD destination')
            for row in out:
                row[j] += c*row[i]
        else:
            need(kind == 'SCALE' and len(op) == 3 and abs(c.numerator) & (abs(c.numerator)-1) == 0, 'dyadic unit scale')
            for row in out:
                row[i] *= c
    return out


def modular(c, modulus):
    c = F(c)
    return c.numerator*pow(c.denominator, -1, modulus) % modulus


def high_word(values, word, modulus):
    out = list(values)
    for op in word:
        c = modular(op[-1], modulus)
        if op[0] == 'ADD':
            out[op[2]] = (out[op[2]] + c*out[op[1]]) % modulus
        else:
            out[op[1]] = c*out[op[1]] % modulus
    return out


def carry(low, s, q):
    """Compute the width-independent exact dyadic carry, with q cancelled."""
    need(type(q) is int and q > 1 and gcd(q, 12) == 1, 'source modulus guard')
    need(len(low) == len(s) and all(type(x) is int and 0 <= x < q for x in low), 'canonical low digits')
    target, shifts = [], []
    for column in zip(*s):
        denominator = lcm(*(x.denominator for x in column))
        numerator = sum(x*(a.numerator*(denominator//a.denominator)) for x, a in zip(low, column))
        t = numerator*pow(denominator, -1, q) % q
        delta = numerator-denominator*t
        need(delta % q == 0, 'exact carry divisibility')
        c = F(delta//q, denominator)
        need(c.denominator & (c.denominator-1) == 0, 'dyadic carry after q cancellation')
        need(abs(c) < sum(map(abs, column), F(0))+1, 'uniform carry height')
        target.append(t); shifts.append(c)
    return target, shifts


def fused(low, high, word, s, q, width):
    need(type(width) is int and width >= 1, 'positive width')
    modulus = q**(width-1)
    need(len(high) == len(low) and all(type(x) is int and 0 <= x < modulus for x in high), 'canonical high digits')
    target, shifts = carry(low, s, q)
    result = high_word(high, word, modulus)
    result = [(x+modular(c, modulus)) % modulus for x, c in zip(result, shifts)]
    return target, result


def elementary(low, high, word, q, width):
    """Separate factor-by-factor integer identity, before carry fusion."""
    lo, hi = list(low), list(high); modulus = q**(width-1)
    for op in word:
        a = F(op[-1]); i = op[1]
        if op[0] == 'ADD':
            j = op[2]; low_n = a.denominator*lo[j]+a.numerator*lo[i]
            high_n = a.denominator*hi[j]+a.numerator*hi[i]
        else:
            j = i; low_n = a.numerator*lo[j]; high_n = a.numerator*hi[j]
        t = low_n*pow(a.denominator, -1, q) % q
        k, rem = divmod(low_n-a.denominator*t, q)
        need(rem == 0, 'elementary carry is integral')
        hi[j] = (high_n+k)*pow(a.denominator, -1, modulus) % modulus
        lo[j] = t
    return lo, hi


def dense_oracle(values, s, modulus):
    """Direct full-width modular matrix multiplication; no split or carry."""
    return [sum(x*modular(a, modulus) for x, a in zip(values, col)) % modulus for col in zip(*s)]


def potential_carry_columns(s):
    return [j for j, col in enumerate(zip(*s))
            if sum(x == 1 for x in col) != 1 or sum(x != 0 for x in col) != 1]


def embedded(low, high, word, s, active, f, q, width):
    """Apply the N=127f cover map to all rows and lanes, in place on copies."""
    n = 127*f
    need(len(active) == 8 and len(set(active)) == 8 and all(0 <= x < 127 for x in active), 'active cover axes')
    need(len(low) == len(high) == n*n, 'full cover size')
    lo, hi = list(low), list(high)
    for row in range(n):
        for lane in range(f):
            addresses = [row*n+axis*f+lane for axis in active]
            a, b = fused([lo[x] for x in addresses], [hi[x] for x in addresses], word, s, q, width)
            for address, x, y in zip(addresses, a, b):
                lo[address], hi[address] = x, y
    return lo, hi
