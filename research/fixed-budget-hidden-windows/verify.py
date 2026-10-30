#!/usr/bin/env python3
"""Exact, bounded corroboration of the theorem in PROOF.md. Python 3.10+ stdlib.

No networking, subprocesses, imports from upstream, or writes. The uniform
theorem is a written proof; this program checks arithmetic certificates and
finite examples, including every interior quadratic in a declared call budget.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import hashlib
import json


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def integer(value, name, minimum=None):
    require(type(value) is int, name + ' must be an integer, not bool/float')
    require(minimum is None or value >= minimum, name + ' is below its minimum')
    return value


def multiply(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i + j] += ai * bj
    return out


def divide_root(coefficients, root):
    """Exact division by monic x-root; low-degree coefficient order."""
    require(len(coefficients) >= 2, 'insufficient degree')
    quotient = [0] * (len(coefficients) - 1)
    quotient[-1] = coefficients[-1]
    for j in range(len(quotient) - 2, -1, -1):
        quotient[j] = coefficients[j + 1] + root * quotient[j + 1]
    require(coefficients[0] + root * quotient[0] == 0, 'endpoint multiplicity fails')
    return quotient


def build(h, a, b, c):
    """Orient the residual a*x^2+b*x+c to be positive in its inner window."""
    integer(h, 'h', 1)
    require(h <= 32, 'bounded checker supports h <= 32')
    q = [c, b, a]
    for _ in range(h):
        q = multiply(multiply(q, [-1, 1]), [-2, 1])
    q = [(-1) ** (h + 1) * x for x in q]
    return [max(-x, 0) for x in q], [max(x, 0) for x in q]


def certify(h, profile_a, profile_b, budget):
    """Certify the theorem's domain using integer arithmetic only.

    This certifies neither a legal supplier nor arbitrary rank alphabets.
    The two arrays index exactly ranks 2^j; the budget is PER PROFILE.
    """
    integer(h, 'h', 1)
    require(h <= 32, 'bounded checker supports h <= 32')
    integer(budget, 'budget', 1)
    require(type(profile_a) in (list, tuple) and type(profile_b) in (list, tuple), 'profiles must be sequences')
    degree = 2 * h + 2
    require(len(profile_a) == degree + 1 and len(profile_b) == degree + 1, 'rank alphabet/degree mismatch')
    for x in (*profile_a, *profile_b):
        integer(x, 'call multiplicity', 0)
    na, nb = sum(profile_a), sum(profile_b)
    require(na == nb and na <= budget, 'equal per-profile count/budget fails')
    ma = sum(x * (1 << j) for j, x in enumerate(profile_a))
    mb = sum(x * (1 << j) for j, x in enumerate(profile_b))
    require(ma == mb, 'rank mass differs')
    q = [b - a for a, b in zip(profile_a, profile_b)]
    require(q[-1] != 0, 'degree is not saturated')
    residual = q[:]
    for _ in range(h):
        residual = divide_root(residual, 1)
        residual = divide_root(residual, 2)
    sign = (-1) ** (h + 1)
    c, b, a = [sign * x for x in residual]
    require(a > 0, 'orientation is not a positive losing inner window')
    delta = b * b - 4 * a * c
    require(delta > 0, 'interior roots are not distinct')
    # Positive endpoint values, negative minimum and interior vertex place
    # both roots strictly inside (1,2), without floating-point square roots.
    require(2 * a < -b < 4 * a, 'vertex is outside (1,2)')
    require(a + b + c > 0 and 4 * a + 2 * b + c > 0, 'roots are not strictly inside (1,2)')
    require(all(q[j] * q[j + 1] < 0 for j in range(degree)), 'coefficient alternation fails')
    positive, negative = sum(max(x, 0) for x in q), sum(max(-x, 0) for x in q)
    w = positive
    require(w == negative, 'uncancelled counts differ')
    require(2 * w == 6 ** h * (a - b + c), 'half-L1 formula fails')
    common = sum(min(x, y) for x, y in zip(profile_a, profile_b))
    require(na == w + common and w <= budget, 'common-padding identity fails')
    # All roots positive gives |Q(-1)|=sum|q_j|. Check independently.
    require(abs(sum(x * (-1) ** j for j, x in enumerate(q))) == 2 * w, 'evaluation at -1 fails')
    count_scale, trace, endpoint_value = 6 ** h // 2, -b, a + b + c
    require(w % count_scale == 0 and w // count_scale == 2 * trace + endpoint_value,
            'discrete trace/count identity fails')
    trace_cap = (budget // count_scale - 1) // 2
    require(trace_cap >= trace > 1 and endpoint_value >= 1, 'trace budget bound fails')
    # (z+sqrt(Delta))/(z-sqrt(Delta)) >= (Z+1)/(Z-1)
    # is equivalent, after positive cross multiplication, to Z*sqrt(Delta)>=z.
    require(trace_cap * trace_cap * delta >= trace * trace, 'exact discrete width bound fails')
    return {'h': h, 'quadratic': [c, b, a], 'discriminant': delta,
            'uncancelled_calls_per_profile': w, 'actual_calls_per_profile': na,
            'common_calls': common, 'budget_per_profile': budget,
            'rank_mass_per_profile': ma, 'support_size': degree + 1,
            'bound_numerator': 2 * 6 ** h,
            'count_scale': count_scale, 'endpoint_residual_value': endpoint_value,
            'trace': trace, 'budget_trace_cap': trace_cap,
            'discrete_width_ratio_lower': str(F(trace_cap + 1, trace_cap - 1)),
            'discrete_bound_attained': delta == 1 and trace == trace_cap,
            'stronger_continuous_bound_denominator': budget - count_scale,
            'rational_roots': isqrt(delta) ** 2 == delta}


def sqrt_bounds(n, bits=160):
    integer(n, 'radicand', 0)
    integer(bits, 'bits', 1)
    scale = 1 << bits
    floor = isqrt(n << (2 * bits))
    lo = F(floor, scale)
    return lo, lo if floor * floor == n * scale * scale else F(floor + 1, scale)


def log_bounds(x, terms=48):
    """For 1<=x<=2, use 2*atanh(z) and an explicit positive tail bound."""
    require(type(x) in (int, F), 'log argument must be exact')
    x = F(x)
    require(1 <= x <= 2, 'log interval outside bounded domain')
    integer(terms, 'terms', 1)
    z = (x - 1) / (x + 1)
    z2 = z * z
    power, total = z, F(0)
    for j in range(terms):
        total += 2 * power / (2 * j + 1)
        power *= z2
    tail = 2 * power / ((2 * terms + 1) * (1 - z2))
    return total, total + tail


def ratio_bounds(certificate):
    c, b, a = certificate['quadratic']
    slo, shi = sqrt_bounds(certificate['discriminant'])
    rlo, rhi = F(-b - shi, 2 * a), F(-b - slo, 2 * a)
    slo_root, shi_root = F(-b + slo, 2 * a), F(-b + shi, 2 * a)
    require(1 < rlo <= rhi < slo_root <= shi_root < 2, 'root enclosure unresolved')
    return slo_root / rhi, shi_root / rlo


def interval_check(certificate):
    """Independently enclose W*ln(s/r)/(2*6^h), which must exceed 1."""
    lo, hi = ratio_bounds(certificate)
    lower = log_bounds(lo)[0]
    upper = log_bounds(hi)[1]
    scale = F(certificate['uncancelled_calls_per_profile'], certificate['bound_numerator'])
    lower, upper = scale * lower, scale * upper
    require(lower > 1, 'numerical enclosure does not certify strict universal bound')
    delta_hi = sqrt_bounds(certificate['discriminant'])[1]
    require(lower > delta_hi, 'numerical enclosure does not certify discriminant bound')
    # Outward rounding keeps the public receipt small; it never determines
    # whether the unrounded proof interval passed. Recheck the rounded bounds.
    scale_out = 1 << 128
    lower = F((lower * scale_out).__floor__(), scale_out)
    upper = F((upper * scale_out).__ceil__(), scale_out)
    require(lower > delta_hi, 'rounded receipt does not retain the strict bound')
    return {'normalized_ratio_lower': str(lower), 'normalized_ratio_upper': str(upper),
            'strict_bound_certified': True}


def enumerate_quadratics(budget):
    """Exhaust every oriented integer quadratic with roots in (1,2), h=1.

    W=3*(a+z+c) and W>12*a imply a<budget/12. Endpoint and
    discriminant inequalities give the exact inclusive integer c range.
    """
    integer(budget, 'budget', 1)
    for a in range(1, (budget - 1) // 12 + 1):
        for z in range(2 * a + 1, 4 * a):
            low = max(z - a + 1, 2 * z - 4 * a + 1)
            high = min((z * z - 1) // (4 * a), budget // 3 - a - z)
            for c in range(low, high + 1):
                yield a, -z, c


def source_check():
    root = Path(__file__).resolve().parent
    manifest_bytes = (root / 'SOURCES.json').read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() ==
            '6aa53019414d71decdf9afffba3c2fa23d7aa5fa64785073c9c80b4c581560aa',
            'source provenance manifest mismatch')
    manifest = json.loads(manifest_bytes)
    require(manifest['source_commit'] == '2646b6d67ceb74b9868e632f3a27312d8be62a0e', 'unexpected source commit')
    pins = {'sources/pr6049-README.md.txt': '71bebc3aacc14bce229f56b3c3315bc704985877',
            'sources/pr6049-verify.py.txt': 'fe4adcc950f44e53a304d42dd7bf139b7b53a71e'}
    require(len(manifest['files']) == 2 and {r['file']: r['git_blob_sha1'] for r in manifest['files']} == pins,
            'source manifest differs from fixed Git blob pins')
    for record in manifest['files']:
        data = (root / record['file']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == record['sha256'], 'source SHA256 mismatch')
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == record['git_blob_sha1'], 'source Git blob mismatch')
        require(len(data) == record['bytes'], 'source size mismatch')
    # The proposed public subset retains exact source bytes and blob hashes.
    # Commit/path attribution is recorded in SOURCES.json; a full offline
    # commit-to-tree proof is deliberately not bundled here.
    return len(manifest['files'])


def main():
    sources = source_check()
    example_a, example_b = build(1, 8, -22, 15)
    require(example_a == [0, 89, 0, 46, 0] and example_b == [30, 0, 97, 0, 8], 'PR6049 fixture differs')
    source_example = certify(1, example_a, example_b, 135)
    source_example['interval_check'] = interval_check(source_example)
    census, rational, irrational = 0, 0, 0
    best_root_ratio_square, optimizers = None, []
    digest = hashlib.sha256()
    irrational_examples = []
    for a, b, c in enumerate_quadratics(1000):
        pa, pb = build(1, a, b, c)
        cert = certify(1, pa, pb, 1000)
        census += 1
        rational += cert['rational_roots']
        irrational += not cert['rational_roots']
        digest.update((json.dumps(cert, sort_keys=True, separators=(',', ':')) + '\n').encode())
        root_ratio_square = F(cert['discriminant'], b * b)
        if best_root_ratio_square is None or root_ratio_square < best_root_ratio_square:
            best_root_ratio_square, optimizers = root_ratio_square, [cert.copy()]
        elif root_ratio_square == best_root_ratio_square:
            optimizers.append(cert.copy())
        if not cert['rational_roots'] and len(irrational_examples) < 12:
            cert['interval_check'] = interval_check(cert)
            irrational_examples.append(cert)
    sharpness = []
    for h in (1, 2, 3, 8, 16):
        for n in (3, 4, 10, 100, 10000, 10 ** 9):
            a, b, c = n * (n - 1), -(2 * n * n - 1), n * (n + 1)
            pa, pb = build(h, a, b, c)
            expected_w = 6 ** h * (4 * n * n - 1) // 2
            cert = certify(h, pa, pb, expected_w)
            require(cert['discriminant'] == 1, 'Farey discriminant fails')
            require(cert['uncancelled_calls_per_profile'] == expected_w, 'sharpness count formula fails')
            require(cert['endpoint_residual_value'] == 1 and cert['discrete_bound_attained'],
                    'exact finite-budget equality fails at family budget')
            interval = interval_check(cert)
            upper_squeeze = 1 + F(3, 4 * (n * n - 1))
            require(F(interval['normalized_ratio_upper']) < upper_squeeze, 'sharpness upper squeeze unresolved')
            sharpness.append({'h': h, 'n': n, 'calls_per_profile': expected_w,
                              'discriminant': 1, 'normalized_ratio_upper_squeeze': str(upper_squeeze),
                              'discrete_bound_attained': True,
                              'exact_width': 'log2(' + str(F(n*n, n*n-1)) + ')',
                              'strict_bound_certified': True})
    # Exact rational safe-mesh constant: composite trapezoidal upper bound
    # for integral_1^2 1/x dx, using strict convexity of 1/x.
    trapezoid = F(1, 4) * (F(1, 2) + F(4, 5) + F(2, 3) + F(4, 7) + F(1, 4))
    require(trapezoid == F(1171, 1680) < F(7, 10), 'log(2) rational upper bound fails')
    result = {'status': 'pass', 'claim_type': 'scoped theorem with finite exact corroboration',
              'source_files_verified': sources,
              'source_authentication': 'SHA256 and Git blob checks; commit/path provenance recorded in SOURCES.json',
              'source_example': source_example,
              'census': {'h': 1, 'budget_per_profile': 1000, 'quadratics': census,
                         'rational_root_pairs': rational, 'irrational_root_pairs': irrational,
                         'objective': 'minimize Delta/trace^2; width is strictly increasing in this quantity',
                         'minimum_Delta_over_trace_squared': str(best_root_ratio_square),
                         'all_minimizing_quadratics': optimizers,
                         'ordered_certificate_sha256': digest.hexdigest()},
              'irrational_examples': irrational_examples, 'sharpness_fixtures': sharpness,
              'log2_upper_rational': str(trapezoid),
              'limitations': ['minimal power-of-two alphabet only', 'integer multiplicities',
                              'not an exact optimum for each finite budget',
                              'no legal supplier construction or new kappa',
                              'finite checks do not replace the written uniform proof']}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
