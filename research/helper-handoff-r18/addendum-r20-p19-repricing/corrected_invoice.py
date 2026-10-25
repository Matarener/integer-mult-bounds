#!/usr/bin/env python3
"""R20: re-price DaysSky's p19 coded-reverse invoice (#5270 / #5440) with the reviewed costs charged.

Reads the package at ~/imb-r20 (PR #5440 head c0f52b5b1). Uses the package's own `invoice()`
(p19_claim.py) and listing generator (p19_word.py) and prices with a 60-digit Decimal engine
(R16 price16.py style) plus the repository's exact concave-order comparator
(scripts/compare_recursive_invoices.py). Standard library only.

Pricing: M(C) = sum_T n k^(1-C) - sum_P n r^(1-C); the complex supplier is the raw root C*.
Frontiers: selected 0.003027288235 (605457647/200000000000), ours 0.0030272882489783, BIT 0.0034.
"""
import importlib.util, json, sys
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction
from pathlib import Path

getcontext().prec = 60
PKG = Path.home()/'imb-r20/research/coded-reverse-word-p19'
REPO = Path.home()/'imb-r20'
U_SEL = D('0.003027288235')
U_OURS = D('0.0030272882489783')
BIT = D('0.0034')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def pw(x, e): return (D(x).ln()*e).exp()


def M(T, P, C):
    e = 1-D(C)
    return sum(n*pw(k, e) for k, n in T.items() if n) - sum(n*pw(r, e) for r, n in P.items() if n)


def root(T, P):
    """Largest-sign-change bisection on (0, 0.05); returns 0 if M <= 0 on a fine grid (no break-even)."""
    grid = [D(i)/D(10000) for i in range(0, 500)]
    vals = [M(T, P, c) for c in grid]
    if all(v <= 0 for v in vals): return D(0)
    i = max(j for j, v in enumerate(vals) if v > 0)
    lo, hi = grid[i], grid[i]+D('0.0001')
    for _ in range(120):
        m = (lo+hi)/2
        if M(T, P, m) > 0: lo = m
        else: hi = m
    return lo


def concave_order_dead(T, P):
    """Exact: K(k) = sum_r (P[r]-T[r]) min(r,k) > 0 at every knot => M(C) < 0 for all C in (0,1)."""
    d = Counter(P); d.subtract(T)
    knots = sorted(set(T) | set(P))
    K = [sum(n*min(r, k) for r, n in d.items()) for k in knots]
    return all(x > 0 for x in K), min(K)


def tolerance(T, P, limit):
    """Max extra rank-1 paid jobs keeping the raw root above `limit` (M(limit) / 1)."""
    return int(M(T, P, limit) // 1)


def add(h, delta):
    out = Counter(h)
    for k, v in delta.items(): out[k] += v
    return +out


def main():
    claim = load('p19claim', PKG/'p19_claim.py')
    word = load('p19word', PKG/'p19_word.py')
    p, pat = 19, 'I'*9 + 'T'*9
    thick = frozenset(range(1, 2*p, 2))
    T0, P0 = claim.invoice(p, pat, thick, claim.P_NEW)
    out = {}
    mass = lambda h: sum(k*n for k, n in h.items())
    r0 = root(T0, P0)
    out['V0_as_claimed'] = dict(root=str(r0), mass_surplus=mass(T0)-mass(P0), T=dict(T0), P=dict(P0))
    print('V0 package invoice: root %.12f  mass surplus %d of %d' % (r0, mass(T0)-mass(P0), mass(T0)))
    for name, lim in (('BIT 0.0034', BIT), ('selected', U_SEL), ('ours', U_OURS)):
        print('   tolerance (extra rank-1 jobs) above %-10s: %d  [M = %s]' % (name, tolerance(T0, P0, lim),
                                                                            str(M(T0, P0, lim))[:14]))

    # ---- charge 1: missing Q on every letter (native call supplies D, listing applies R = D Q) ----
    g = word.listing(p, 'R')
    kinds = Counter(x[0] for x in g)
    letters = [x for x in g if x[0] == 'LETTER']
    owners = word.OWNERS
    q_letter = sum(len(x[1:3]) for x in letters)*owners
    assert len(letters) == p and len(thick) == p and q_letter == 4256, q_letter
    print('listing gate kinds', dict(kinds))
    print('charge 1: %d LETTER gates x 2 roles x %d owners = %d Q jobs (rank 1)' % (len(letters), owners, q_letter))

    # ---- charge 2: R-type idles in the invoiced fresh-block geometry ----
    # An idle over the thick stages S is prod_{s in S} R_s = (prod D_s) Q^{|S|}; Q^4 = I, Q^2 a signed
    # address swap (monomial, free); so odd |S| needs one extra Gaussian rank on the central line.
    # The invoice charges the idle as one rank-8|S| job per field; most favourable: merge -> 8|S|+1.
    idle_merge = Counter()
    for i, ch in enumerate(pat, 1):
        S = (frozenset(range(0, 2*i)) if ch == 'I' else frozenset(range(2*i+1, 2*p+1))) & thick
        if len(S) % 2: idle_merge[8*len(S)] += 224
    print('charge 2: retained idles with odd thick count:', dict(idle_merge), '->', sum(idle_merge.values()),
          'rank increments (merged into the idle job)')
    # listing check: the listing's idle powers count ALL stages (2i, 36-2j), always even -> R^even is
    # monomial in the collapsed 9-axis replay, which is why the replay never saw these costs.
    pows = [x[3] for x in g if x[0] == 'IDLE' and x[4] != 'middle']
    middle = [x for x in g if x[0] == 'IDLE' and x[4] == 'middle']
    print('   listing idle powers (non-middle):', sorted(pows), '(all even)')
    print('   middle idles in the listing: %d executing R^1 on 2x%d fields; invoice prices them at rank 0'
          % (len(middle), owners))

    variants = {}
    variants['V1 +4256 Q (separate rank-1 jobs)'] = (T0, add(P0, {1: q_letter}))
    P2 = add(P0, {1: q_letter})
    for r, n in idle_merge.items(): P2[r] -= n; P2[r+1] += n
    variants['V2 = V1 + odd-idle Q merged (8k->8k+1)'] = (T0, +P2)
    P3 = add(P2, {9: len(middle)*2*owners})
    variants['V3 = V2 + literal middle R idles (rank 9)'] = (T0, +P3)
    # terminal-gauge alternative (letter D, no letter Q): Matarener outcome B -- decode the 19 coded
    # output banks with one paid Q per owner, credit 8k instead of 1+8k
    outs_even = [1+8*len(s & thick) for s in
                 [frozenset(range(2*p+1))] + [frozenset(range(0, 2*i+1)) if ch == 'I' else
                                              frozenset(range(2*i, 2*p+1)) for i, ch in enumerate(pat, 1)]]
    TB, PB = Counter(T0), Counter(P0)
    for r in outs_even: TB[r] -= 112; TB[r-1] += 112; PB[1] += 112
    variants['VB letter D + terminal Q decoder (2128), credit 8k'] = (+TB, +PB)
    variants['VB0 terminal decoder only, credit kept (2128 rank-1)'] = (T0, add(P0, {1: 2128}))

    for name, (T, P) in variants.items():
        r = root(T, P)
        dead, kmin = concave_order_dead(T, P)
        ms = mass(T)-mass(P)
        out[name] = dict(root=str(r), mass_surplus=ms, concave_order_dead=dead, min_hinge=kmin,
                         M_at_selected=str(M(T, P, U_SEL)), M_at_ours=str(M(T, P, U_OURS)))
        print('%-55s root %.12f  mass %+6d  M(U_sel) %+.3f  dead-for-all-t %s (min hinge %d)'
              % (name, r, ms, M(T, P, U_SEL), dead, kmin))

    # ---- merge-robust bound: any placement of the 4256 Q ranks into existing jobs ----
    # Adding one Gaussian axis to a job of rank r costs (r+1)^(1-C) - r^(1-C) >= (1-C)(r+1)^(-C);
    # no job exceeds the ambient rank 153, so each Q costs >= (1-U) 153^(-U) at C = U.
    per_q = (1-U_SEL)*pw(153, -U_SEL)
    budget = M(T0, P0, U_SEL)
    print('merge-robust: each Q costs >= %.6f at U_sel; 4256 Q cost >= %.1f vs budget M0(U_sel) = %.3f'
          % (per_q, 4256*per_q, budget))
    print('   max Q ranks affordable at U_sel even with free merging: %d (need 4256; with letter Q only)'
          % int(budget/per_q))
    out['merge_robust'] = dict(per_q_lower=str(per_q), budget_at_selected=str(budget),
                               max_affordable=int(budget/per_q), needed=4256)
    (Path(__file__).resolve().parent/'corrected_invoice.json').write_text(json.dumps(out, indent=1, default=str))


if __name__ == '__main__':
    main()
