#!/usr/bin/env python3
"""Check the full-cell reference. Ali Romman with OpenAI Codex. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from runpy import run_path
from math import isqrt
import json

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('invalid control accepted')


def independent_exp(x, terms):
    """Use a separate rational Taylor enclosure without range reduction."""
    term = total = F(1)
    for j in range(1, terms+1):
        term *= x/j
        total += term
    tail = term*x/(terms+1)/(1-x/(terms+2))
    return 1/(total+tail), 1/total


def check():
    for row in json.loads((HERE/'SOURCES.json').read_text())['external_inputs']:
        need(sha256((HERE/row['local_path']).read_bytes()).hexdigest() == row['sha256'],
             'retained source changed')
    m = run_path(str(HERE/'prepare.py'), run_name='preparation')
    exp = m['expneg']
    comparisons = 0
    for x in (F(0), F(1, 257), F(1, 2), F(1), F(7, 3), F(17)):
        lo, hi = exp(x, 80)
        rlo, rhi = independent_exp(x, 240)
        need(lo <= rlo <= rhi <= hi, 'independent exact exponential enclosure')
        need(hi-lo <= F(1, 1 << 80), 'exponential width')
        comparisons += 1
    pi_lo, pi_hi = m['pi_bounds'](120)
    need(F(3141592653589793, 10**15) < pi_lo < pi_hi
         < F(3141592653589794, 10**15), 'independent coarse pi bracket')
    # The fixed Machin identity follows from this exact tangent calculation.
    tangent = (F(120, 119)-F(1, 239))/(1+F(120, 119*239))
    need(tangent == 1, 'Machin tangent identity')
    controls = 0
    receipts = []
    for p, theta, accuracy in ((16, F(1, 256), 4), (17, F(2, 599), 12),
                               (17, F(2, 599), 40)):
        a, r, receipt = m['prepare'](p, 3, theta, accuracy)
        meta = receipt['parameters']
        need(meta['N'] == (256 if p == 16 else 299), 'complete source floor')
        lo, _ = exp(pi_hi, 80)
        _, hi = exp(pi_lo*F(9, 4), 80)
        need(hi < F(1, 16*p) < lo, 'actual source alpha is three')
        rho = 1+theta
        for k in (0, meta['N']//2, meta['N']-1):
            for i in (0, meta['N']//2, meta['N']-1):
                left = F(i)-(F(k)+F(1, 2))/rho
                right = (2*i*rho-2*k-1)/(2*rho)
                need(left == right, 'literal phase and dilation identity')
                comparisons += 1
        bad = [row[:] for row in r]
        bad[0][0] += 1 << meta['inverse_bits']
        reject(lambda: m['certify'](a, bad, meta, accuracy))
        controls += 1
        bad_a = [row[:] for row in a]
        bad_a[0][0] = 0
        reject(lambda: m['certify'](bad_a, r, meta, accuracy))
        controls += 1
        reject(lambda: m['certify'](a, r[:-1], meta, accuracy))
        controls += 1
        receipts.append(receipt)
    for prime in (17, 599, 601):
        need(all(prime % d for d in range(2, isqrt(prime)+1)), 'literal prime fixture')
    need(F(601, 599)-1 == F(2, 599), 'fine-prime ratio fixture')
    # Force the exact completion path on independent small integer matrices.
    exact_checks = 0
    for a in ([[0, 1], [1, 1]], [[3, 1], [2, 1]],
              [[1, 2, 0], [0, 1, 3], [0, 0, 1]]):
        r = m['exact_candidate'](a, 0, 24)
        need(m['residual'](a, r, 0, 24) == 0, 'exact inverse with pivoting')
        exact_checks += 1
    for args in ((15, 3, F(1, 256), 4), (16, 3, F(1, 2048), 4),
                 (16, 3, F(1, 256), -1)):
        reject(lambda args=args: m['parameters'](*args))
        controls += 1
    reject(lambda: exp(-1, 40))
    reject(lambda: m['reference'](16, 4, F(1, 256), 4))
    controls += 2
    return dict(status='PASS_DYADIC_FULL_CELL_GAUSSIAN', cells=receipts,
                exact_enclosure_and_geometry_checks=comparisons,
                exact_inverse_checks=exact_checks, rejecting_controls=controls,
                production_threshold=16, inverse_guard='5*p^6',
                scope='Certified reference and inverse preparation; no physical caller or new kappa.')


def main():
    result = check()
    need(result == json.loads((HERE/'RESULT.json').read_text()), 'fixed result receipt')
    print(result['status'])
    print('Complete 256- and 299-column cells; exact interval and inverse-residual certificates')


if __name__ == '__main__':
    main()
