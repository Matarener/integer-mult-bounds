"""Independent recomputation of a G20 package's ordinary-admission arithmetic (stdlib Decimal, 60 digits).

Recomputes from INVOICE.json alone: the raw crossing root of sum_T k^(1-c) = sum_P k^(1-c),
the margin at the package's tested saving, the charged tail ratios alpha/gamma/delta,
uniform tail guards on [C_min, .00351] for several seeds (incl. the SELECTED admitted ordinary
backend), the compiler cutoffs H0/H1 from their defining inequalities, and rank-mass tails.
Imports no package code. Usage: python3 audit_admission.py PACKAGE_DIR
"""
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from pathlib import Path
import json, sys

getcontext().prec = 60


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def dec(q):
    q = F(q); return D(q.numerator) / D(q.denominator)


def main(pkg):
    pkg = Path(pkg)
    inv = json.load(open(pkg / 'INVOICE.json'))
    ordres = json.load(open(pkg / 'ORDINARY-RESULT.json'))
    T = {int(k): v for k, v in inv['targets'].items()}; P = {int(k): v for k, v in inv['paid'].items()}
    ln = {k: D(k).ln() for k in set(T) | set(P) | {17}}
    M = lambda H, t: sum(n * (ln[k] * t).exp() for k, n in H.items())
    f = lambda c: M(T, 1 - c) - M(P, 1 - c)
    lo, hi = D('0.0034'), D('0.0036')
    need(f(lo) > 0 > f(hi), 'root bracket')
    for _ in range(140):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    root = lo
    tested, uniform = F(ordres['params']['tested']), F(ordres['params']['uniform'])
    admitted = F(ordres['admitted'])
    need(admitted < uniform < tested < F(str(root)), 'admitted < uniform < tested < raw root')
    t = 1 - dec(tested); u = D(1) / 5
    MT = M(T, t)
    alpha = M(P, t) / MT
    gamma = M(P, t + u) / ((ln[17] * u).exp() * MT)
    delta = D(11022 * 18) / ((ln[17] * dec(tested)).exp() * MT)
    need(alpha < 1 - D(2) ** -48 and gamma < D(31) / 32 and delta < D(19) / 20, 'charged tails')
    guards = {}
    for name, cmin in [('package_backend', F(ordres['comparator'])), ('selected_admitted_ordinary', F('.0034363538396')), ('selected_admitted_BIT', F('.0034'))]:
        cm = dec(cmin); MTx = M(T, 1 - D('0.00351'))
        g = M(P, 1 - cm + u) / ((ln[17] * u).exp() * MTx); d = D(11022 * 18) / ((ln[17] * cm).exp() * MTx)
        need(g < D(31) / 32 and d < D(19) / 20, 'uniform guards from ' + name)
        guards[name] = dict(C_min=str(cmin), gamma='%.12f' % g, delta='%.12f' % d)
    v = 1024; res = F(1, 2 ** 48)
    while not (1 - F(1) / (1 + v * res) - F(4, 2 ** (v // 32)) > 0): v *= 2
    tz, z = 1 - tested, 1 - uniform; z0 = (tz + z) / 2; gap = z0 - tz; h = F(1, 64)
    rhs = gap * (5 + 8 * h) * v + 1 + 8 * v * (1 - z0)
    H0 = (rhs / (h * gap)).__floor__() + 1; H1 = (H0 * (1 - z0) / (z - z0)).__floor__() + 1
    need(v == ordres['params']['v'] and H0 == int(ordres['tail']['H0']) and H1 == int(ordres['tail']['H1']), 'compiler cutoffs')
    tails = [sum(k * n for k, n in T.items() if k >= a) - sum(k * n for k, n in P.items() if k >= a) for a in range(1, 129)]
    need(min(tails) >= 0 and tails[0] == inv['rank_surplus'], 'rank-mass tails')
    out = dict(package=pkg.name, raw_root=str(root)[:22], tested=str(tested), admitted=str(admitted),
               one_minus_alpha='%.6E' % (1 - alpha), gamma='%.10f' % gamma, delta='%.10f' % delta,
               guards=guards, v=v, H0=H0, H1=str(H1))
    print('PASS_ADMISSION', json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    main(sys.argv[1])
