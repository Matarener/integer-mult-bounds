#!/usr/bin/env python3
"""Certified full-cell preparation. Ali Romman with OpenAI Codex. Apache-2.0."""
from fractions import Fraction as F
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from math import isqrt
from functools import lru_cache
import json
from hashlib import sha256

def need(ok, msg):
    if not ok:
        raise ValueError(msg)

def ceilq(x):
    return -(-x.numerator // x.denominator)

def quant(x, b, upper=False):
    s = 1 << b
    return F(ceilq(x * s) if upper else x.numerator * s // x.denominator, s)

@lru_cache(None)
def pi_bounds(bits):

    def atan(q):
        n = bits + 8
        total = sum((F((-1) ** k, (2 * k + 1) * q ** (2 * k + 1)) for k in range(n)), F())
        nxt = F((-1) ** n, (2 * n + 1) * q ** (2 * n + 1))
        return (min(total, total + nxt), max(total, total + nxt))
    a, b = atan(5)
    c, d = atan(239)
    return (quant(16 * a - 4 * d, bits), quant(16 * b - 4 * c, bits, True))

def expneg(x, bits):
    x = F(x)
    need(type(bits) is int and bits >= 0 and (x >= 0), 'nonnegative exponent and precision')
    k = 0
    while x > 1:
        x /= 2
        k += 1
    work = bits + 2 * k + 2 * (bits + 2 * k + 20).bit_length() + 16
    while True:
        scale = 1 << work
        xl = x.numerator * scale // x.denominator
        xu = ceilq(x * scale)
        low = high = sl = su = scale
        n = work + 8
        for j in range(1, n + 1):
            low = low * xl // (scale * j)
            high = -(-high * xu // (scale * j))
            sl += low
            su += high
        tail = -(-3 * high * xu // (scale * (n + 1)))
        low = scale * scale // (su + tail)
        high = -(-scale * scale // sl)
        for _ in range(k):
            low = low * low // scale
            high = -(-high * high // scale)
        if high - low <= 1 << work - bits:
            return (F(low, scale), F(high, scale))
        work *= 2

@lru_cache(None)
def inverse_guard(p, alpha, theta):
    """Bound both absolute inverse norms by a finite q-product interval."""
    rho = 1 + theta
    need(alpha * alpha <= p, 'polynomial alpha guard')
    bits = 64 + 16*p.bit_length()
    plo, phi = pi_bounds(bits)
    lower, _ = expneg(phi*alpha*alpha*rho/4, bits)
    need(lower >= F(1, p**4), 'finite product guard')
    _, upper_q = expneg(2*plo/(alpha*alpha*rho), bits)
    scale = 1 << bits
    q = ceilq(upper_q*scale)
    need(0 < q < scale, 'strict q-product ratio')
    power, product, terms = q, scale, 0
    while True:
        terms += 1
        product = product*(scale-power)//scale
        following = -(-power*q//scale)
        tail = F(following, scale-q)
        if tail <= F(1, 1 << 32):
            break
        power = following
    product_lower = F(product, scale)*(1-tail)
    need(product_lower > 0, 'positive product lower bound')
    exponential_lower, _ = expneg(phi/(4*alpha*alpha), bits)
    square_scale = 1 << 64
    root_integer = isqrt(ceilq(rho/theta*square_scale))
    while root_integer*root_integer < rho/theta*square_scale:
        root_integer += 1
    root = F(root_integer, 1 << 32)
    sharpened = ceilq(alpha*(1+alpha*root)/(exponential_lower*product_lower**3))
    bound = min(5*p**6, sharpened)
    return bound, dict(uniform_bound=5*p**6, q_product_bound=sharpened,
                       finite_product_terms=terms, product_lower=str(product_lower),
                       interval_bits=bits)

def parameters(p, alpha, theta, t):
    need(type(p) is int and type(alpha) is int and (type(t) is int) and isinstance(theta, F) and (p >= 16) and (alpha >= 3) and (F(1, 4 * p * p) <= theta <= F(1, p * p)) and (t >= 0), 'production domain')
    n = theta.denominator // theta.numerator
    B, _ = inverse_guard(p, alpha, theta)
    g = (B - 1).bit_length()
    q = t + 2 * g + 4
    w = max(alpha, isqrt((7 * alpha * alpha * (q + 3) + 29) // 30))
    while 30 * w * w < 7 * alpha * alpha * (q + 3):
        w += 1
    width = min(n, 2 * w + 1)
    l = q + (width - 1).bit_length() + 2
    out = t + g + (n - 1).bit_length() + 4
    return (n, B, g, q, w, l, out)

def reference(p, alpha, theta, t):
    n, B, g, q, w, l, out = parameters(p, alpha, theta, t)
    plo, phi = pi_bounds(l + 20)
    rho = 1 + theta
    a = [[0] * n for _ in range(n)]
    terms = 0
    for k in range(n):
        for i in range(max(0, k - w), min(n, k + w + 1)):
            z = (F(i) - (F(k) + F(1, 2)) / rho) ** 2 / (alpha * alpha)
            lo, _ = expneg(phi * z, l + 10)
            _, hi = expneg(plo * z, l + 10)
            lo /= alpha
            hi /= alpha
            mid = (lo + hi) / 2
            s = 1 << l
            v = (2 * mid.numerator * s + mid.denominator) // (2 * mid.denominator)
            need(F(v - 1, s) <= lo <= hi <= F(v + 1, s), 'certified entry rounding')
            a[k][i] = v
            terms += 1
    return (a, dict(p=p, alpha=alpha, theta=str(theta), N=n, B=B, G=g, Q=q, W=w, entry_bits=l, inverse_bits=out, formed_entries=terms, inverse_guard=inverse_guard(p, alpha, theta)[1]))

def inverse_candidate(a, l, bits, digits):
    n = len(a)
    with localcontext() as c:
        c.prec = digits
        scale = Decimal(2) ** l
        lu = [[Decimal(v) / scale for v in row] for row in a]
        perm = list(range(n))
        for k in range(n):
            p = max(range(k, n), key=lambda i: abs(lu[i][k]))
            need(lu[p][k] != 0, 'nonzero candidate pivot')
            lu[k], lu[p] = (lu[p], lu[k])
            perm[k], perm[p] = (perm[p], perm[k])
            upper = [(j, lu[k][j]) for j in range(k + 1, n) if lu[k][j]]
            for i in range(k + 1, n):
                if lu[i][k]:
                    f = lu[i][k] / lu[k][k]
                    lu[i][k] = f
                    for j, u in upper:
                        lu[i][j] -= f * u
        lower = [[(j, lu[i][j]) for j in range(i) if lu[i][j]] for i in range(n)]
        upper = [[(j, lu[i][j]) for j in range(i + 1, n) if lu[i][j]] for i in range(n)]
        result = [[0] * n for _ in range(n)]
        scale = Decimal(2) ** bits
        for col in range(n):
            y = [Decimal(0)] * n
            for i in range(n):
                y[i] = Decimal(perm[i] == col) - sum((v * y[j] for j, v in lower[i]), Decimal(0))
            for i in range(n - 1, -1, -1):
                y[i] = (y[i] - sum((v * y[j] for j, v in upper[i]), Decimal(0))) / lu[i][i]
            for i in range(n):
                result[i][col] = int((y[i] * scale).to_integral_value(rounding=ROUND_HALF_EVEN))
    return result

def residual(a, r, l, out):
    n = len(a)
    den = 1 << l + out
    cols = [0] * n
    rowmax = 0
    for i, row in enumerate(a):
        acc = [0] * n
        for k, v in enumerate(row):
            if v:
                for j, u in enumerate(r[k]):
                    acc[j] += v * u
        acc[i] -= den
        rowmax = max(rowmax, sum(map(abs, acc)))
        for j, v in enumerate(acc):
            cols[j] += abs(v)
    return F(max(rowmax, max(cols)), den)

def norms(r, out):
    return F(max(max((sum(map(abs, row)) for row in r)), max((sum((abs(row[j]) for row in r)) for j in range(len(r))))), 1 << out)

def exact_candidate(a, entry_bits, output_bits):
    """Use exact elimination if the numerical proposal fails its certificate."""
    n = len(a)
    scale = 1 << entry_bits
    rows = [[F(v, scale) for v in row] + [F(i == j) for j in range(n)] for i, row in enumerate(a)]
    for k in range(n):
        pivot = next((i for i in range(k, n) if rows[i][k]), None)
        need(pivot is not None, 'invertible dyadic reference')
        rows[k], rows[pivot] = (rows[pivot], rows[k])
        value = rows[k][k]
        rows[k] = [x / value for x in rows[k]]
        for i in range(n):
            if i != k and rows[i][k]:
                value = rows[i][k]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[k])]
    scale = 1 << output_bits
    return [[(2 * x.numerator * scale + x.denominator) // (2 * x.denominator) for x in row[n:]] for row in rows]

def certify(a, r, meta, accuracy):
    n = meta['N']
    need(len(a) == len(r) == n and all((len(row) == n for row in a + r)), 'complete square arrays')
    epsilon = residual(a, r, meta['entry_bits'], meta['inverse_bits'])
    inverse_norm = norms(r, meta['inverse_bits'])
    delta = F(min(n, 2 * meta['W'] + 1), 1 << meta['entry_bits']) + F(1, 1 << meta['Q'] + 3)
    need(epsilon <= F(1, 1 << accuracy + meta['G'] + 3), 'inverse residual')
    need(inverse_norm <= 2 * meta['B'], 'inverse norm guard')
    error = meta['B'] * (delta * inverse_norm + epsilon)
    need(error <= F(1, 1 << accuracy), 'full-cell inverse error')
    return dict(reference_error=str(delta), residual=str(epsilon), inverse_norm=str(inverse_norm), inverse_error=str(error))

def prepare(p, alpha, theta, accuracy):
    a, meta = reference(p, alpha, theta, accuracy)
    method = 'certified Decimal proposal'
    try:
        r = inverse_candidate(a, meta['entry_bits'], meta['inverse_bits'], 60)
        certificate = certify(a, r, meta, accuracy)
    except (ValueError, ArithmeticError):
        r = exact_candidate(a, meta['entry_bits'], meta['inverse_bits'])
        certificate = certify(a, r, meta, accuracy)
        method = 'exact rational elimination'
    receipt = dict(parameters=meta, accuracy_bits=accuracy, method=method, certificate=certificate, reference_sha256=sha256(json.dumps(a, separators=(',', ':')).encode()).hexdigest(), inverse_sha256=sha256(json.dumps(r, separators=(',', ':')).encode()).hexdigest())
    return (a, r, receipt)
