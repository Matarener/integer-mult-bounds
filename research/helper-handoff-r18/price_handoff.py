"""Price successor hand-offs on the selected #5413 profile (Decimal, 50 digits; numerical screen).
A hand-off splits one rank-k productive helper target into a + (k-a) at an unchanged paid profile.
Columns: per-hand-off moment gain dM = f(a)+f(k-a)-f(k) at the selected root, and the raw root when one
such hand-off is added in each of n locals.  U = 0.00302728825 is the fixed-profile ceiling (#5409)."""
from price16 import *
U = D('0.00302728825'); base = root(); e = 1 - base
print('selected raw root', base)
f = lambda x: pw(x, e)
for k, a in [(9, 1), (9, 2), (9, 3), (9, 4), (8, 4), (7, 3), (4, 2), (5, 2)]:
    dM = f(a) + f(k - a) - f(k)
    line = f'k={k} -> {a}+{k-a}: dM per hand-off {float(dM):.6f}'
    for n in (1, 9, 18):
        r = root(add(add(T0, {k: -n, a: n}), {k - a: n}), P0)
        line += f' | n={n:2d} root {r:.17f} (beats U: {r > U})'
    print(line)
# ceilings: every rank-9 helper handed off once at 4+5; every helper split at every climb (R16 levers.py)
print('all 5724 rank-9 targets handed off once at 4+5:', f"{root(add(T0, {9: -5724, 4: 5724, 5: 5724}), P0):.10f}")
print('PASS_PRICE_HANDOFF')
