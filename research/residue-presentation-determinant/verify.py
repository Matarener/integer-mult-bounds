#!/usr/bin/env python3
"""Exhaustive check of the presentation-change determinant formula.

For monic irreducible f, g of degree d over F_p and every isomorphism
phi: F_p[u]/(f) -> F_p[v]/(g), phi(u) = alpha, the program checks:

1. det(phi) in power bases, by Gaussian elimination mod p, equals the
   Frobenius-ordered Vandermonde ratio V(alpha^(p^k)) / V(v^(p^k)),
   computed in F_p[v]/(g).
2. det(phi)^2 * disc(g) = disc(f), with disc from a Sylvester resultant.
3. The d isomorphisms have determinants (-1)^(k(d-1)) * det(phi_0).
4. det(phi tensor I_N) = det(phi)^N in coefficient-minor order.

Mutation controls must each fail at least once. Standard library only.
"""

import hashlib
import itertools
import json
import sys

DOMAINS = ((2, 2), (2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (3, 4),
           (5, 2), (5, 3), (7, 2), (7, 3), (11, 2))
TENSOR_POWERS = (2, 3, 4)


def poly_mulmod(a, b, g, p):
    """Product of coefficient lists a, b (low first) reduced mod monic g."""
    d = len(g) - 1
    prod = [0] * (2 * d - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                prod[i + j] = (prod[i + j] + x * y) % p
    for k in range(len(prod) - 1, d - 1, -1):
        c = prod[k]
        if c:
            for j in range(d + 1):
                prod[k - d + j] = (prod[k - d + j] - c * g[j]) % p
    return prod[:d]


def poly_powmod(a, e, g, p):
    d = len(g) - 1
    result = [1] + [0] * (d - 1)
    base = list(a)
    while e:
        if e & 1:
            result = poly_mulmod(result, base, g, p)
        base = poly_mulmod(base, base, g, p)
        e >>= 1
    return result


def poly_eval_in(f, alpha, g, p):
    """f(alpha) in F_p[v]/(g) by Horner."""
    d = len(g) - 1
    acc = [0] * d
    for c in reversed(f):
        acc = poly_mulmod(acc, alpha, g, p)
        acc[0] = (acc[0] + c) % p
    return acc


def is_irreducible(f, p):
    """Rabin's test: x^(p^d) = x mod f and gcd(x^(p^(d/r)) - x, f) = 1
    for each prime r dividing d (d <= 10 here).
    """
    d = len(f) - 1
    x = [0, 1] + [0] * (d - 2) if d > 1 else [0]
    if d == 1:
        return True
    if poly_powmod(x, p ** d, f, p) != x:
        return False
    for r in (2, 3, 5, 7):
        if d % r == 0:
            h = poly_powmod(x, p ** (d // r), f, p)
            h = [(h[i] - x[i]) % p for i in range(d)]
            if poly_gcd_degree(h, f, p) > 0:
                return False
    return True


def poly_trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def poly_gcd_degree(a, b, p):
    a, b = poly_trim(a), poly_trim(b)
    while a:
        inv = pow(a[-1], p - 2, p)
        while len(b) >= len(a):
            c = b[-1] * inv % p
            s = len(b) - len(a)
            for i, x in enumerate(a):
                b[s + i] = (b[s + i] - c * x) % p
            b = poly_trim(b)
            if not b:
                break
        a, b = b, a
    return len(b) - 1


def det_mod(m, p):
    m = [row[:] for row in m]
    n = len(m)
    det = 1
    for col in range(n):
        piv = next((r for r in range(col, n) if m[r][col]), None)
        if piv is None:
            return 0
        if piv != col:
            m[col], m[piv] = m[piv], m[col]
            det = -det
        det = det * m[col][col] % p
        inv = pow(m[col][col], p - 2, p)
        for r in range(col + 1, n):
            c = m[r][col] * inv % p
            if c:
                for k in range(col, n):
                    m[r][k] = (m[r][k] - c * m[col][k]) % p
    return det % p


def sylvester_disc(f, p):
    """disc(f) = (-1)^(d(d-1)/2) Res(f, f') for monic f, mod p."""
    d = len(f) - 1
    df = [(i * f[i]) % p for i in range(1, d + 1)]
    a = list(reversed(f))
    b = list(reversed(df))
    n = 2 * d - 1
    rows = []
    for i in range(d - 1):
        rows.append([0] * i + a + [0] * (n - i - len(a)))
    for i in range(d):
        rows.append([0] * i + b + [0] * (n - i - len(b)))
    res = det_mod(rows, p)
    return (-1) ** (d * (d - 1) // 2) * res % p


def vandermonde(points, g, p):
    d = len(g) - 1
    acc = [1] + [0] * (d - 1)
    for i, j in itertools.combinations(range(len(points)), 2):
        diff = [(points[j][k] - points[i][k]) % p for k in range(d)]
        acc = poly_mulmod(acc, diff, g, p)
    return acc


def field_div_scalar(a, b, g, p):
    """a / b in F_p[v]/(g), asserting the quotient is a constant."""
    d = len(g) - 1
    inv_b = poly_powmod(b, p ** d - 2, g, p)
    q = poly_mulmod(a, inv_b, g, p)
    if any(q[1:]):
        raise AssertionError("Vandermonde ratio is not in F_p")
    return q[0]


def kron_identity(m, n):
    """Matrix of phi tensor I_n in (monomial, coefficient power) order."""
    d = len(m)
    out = [[0] * (d * n) for _ in range(d * n)]
    for blk in range(n):
        for i in range(d):
            for j in range(d):
                out[blk * d + i][blk * d + j] = m[i][j]
    return out


def monic_polys(p, d):
    for coeffs in itertools.product(range(p), repeat=d):
        yield list(coeffs) + [1]


def frobenius_orbit(a, g, p):
    d = len(g) - 1
    orbit = [a]
    for _ in range(d - 1):
        orbit.append(poly_powmod(orbit[-1], p, g, p))
    return orbit


def check_domain(p, d, digest, stats, mutants):
    irr = [f for f in monic_polys(p, d) if is_irreducible(f, p)]
    expected = sum(1 for _ in irr)
    stats["irreducibles"] += expected
    disc = {tuple(f): sylvester_disc(f, p) for f in irr}
    for g in irr:
        v = [0, 1] + [0] * (d - 2)
        vg = vandermonde(frobenius_orbit(v, g, p), g, p)
        all_elems = [list(c) for c in itertools.product(range(p), repeat=d)]
        for f in irr:
            roots = [a for a in all_elems
                     if not any(poly_eval_in(f, a, g, p))]
            if len(roots) != d:
                raise AssertionError(f"root count {len(roots)} for {f} in {g}")
            alpha0 = roots[0]
            orbit = frobenius_orbit(alpha0, g, p)
            if sorted(map(tuple, orbit)) != sorted(map(tuple, roots)):
                raise AssertionError("Frobenius orbit misses a root")
            base_det = None
            seen = []
            for k, alpha in enumerate(orbit):
                powers = [[1] + [0] * (d - 1)]
                for _ in range(d - 1):
                    powers.append(poly_mulmod(powers[-1], alpha, g, p))
                mat = [[powers[j][i] for j in range(d)] for i in range(d)]
                det = det_mod(mat, p)
                if det == 0:
                    raise AssertionError("isomorphism matrix is singular")
                va = vandermonde(frobenius_orbit(alpha, g, p), g, p)
                formula = field_div_scalar(va, vg, g, p)
                if formula != det:
                    raise AssertionError(f"formula {formula} != det {det}")
                if det * det * disc[tuple(g)] % p != disc[tuple(f)]:
                    raise AssertionError("det^2 disc(g) != disc(f)")
                if base_det is None:
                    base_det = det
                sign = (-1) ** (k * (d - 1))
                if det != sign * base_det % p:
                    raise AssertionError("cyclic-shift sign rule fails")
                for n in TENSOR_POWERS:
                    if det_mod(kron_identity(mat, n), p) != pow(det, n, p):
                        raise AssertionError("tensor power rule fails")
                    stats["tensor_checks"] += 1
                # Mutation controls: each must disagree somewhere.
                sorted_roots = sorted(map(tuple, frobenius_orbit(alpha, g, p)))
                vs = vandermonde([list(r) for r in sorted_roots], g, p)
                if field_div_scalar(vs, vg, g, p) != det:
                    mutants["unordered_roots"] += 1
                if base_det != det:
                    mutants["ignore_frobenius_sign"] += 1
                if det != 1:
                    mutants["assume_determinant_one"] += 1
                if (d % 2 == 0 and p != 2 and
                        det != (-1) ** (k * d) * base_det % p):
                    mutants["sign_exponent_kd"] += 1
                seen.append(det)
                digest.update(json.dumps([p, d, f, g, k, det]).encode())
                stats["isomorphisms"] += 1
            stats["pairs"] += 1
            values = sorted(set(seen))
            if p != 2 and d % 2 == 0:
                if len(values) != 2 or seen.count(values[0]) != d // 2:
                    raise AssertionError("even degree must give +-delta d/2 times")
                stats["two_valued_pairs"] += 1
            elif len(values) != 1:
                raise AssertionError("odd degree or char 2 must give one value")


def main():
    digest = hashlib.sha256()
    stats = {"irreducibles": 0, "pairs": 0, "isomorphisms": 0,
             "tensor_checks": 0, "two_valued_pairs": 0}
    mutants = {"unordered_roots": 0, "ignore_frobenius_sign": 0,
               "assume_determinant_one": 0, "sign_exponent_kd": 0}
    for p, d in DOMAINS:
        check_domain(p, d, digest, stats, mutants)
    for name, hits in mutants.items():
        if hits == 0:
            raise AssertionError(f"mutation control {name} never detected")
    result = {"domains": [list(x) for x in DOMAINS], "stats": stats,
              "mutant_detections": mutants, "case_sha256": digest.hexdigest()}
    print("RESULT " + json.dumps(result, sort_keys=True))
    print("PASS_RESIDUE_PRESENTATION_DETERMINANT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
