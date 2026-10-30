"""Re-seed a G20 package's finite ordinary backend levels from other completed backends.

Recursion transcribed from the package statement: a = (1-rho)*C1 + rho*backend, admitted = strict
lower 1e-15 grid point below a, requiring backend < admitted < a < C1 < rho < 1-a.
Usage: python3 chain_levels.py PACKAGE_DIR"""
from fractions import Fraction as F
from pathlib import Path
import json, sys


def below(v, d):
    return F(-((-v.numerator * d) // v.denominator) - 1, d)


def main(pkg):
    o = json.load(open(Path(pkg) / 'ORDINARY-RESULT.json'))
    C1, rho, goal, grid = F(o['C1']), F(o['params']['rho']), F(o['admitted']), o['params']['grid_denominator']
    out = {}
    for name, s in [('package_backend', F(o['comparator'])), ('selected_admitted_ordinary', F('.0034363538396')), ('selected_admitted_BIT', F('.0034'))]:
        b, n = s, 0
        while b < goal:
            a = (1 - rho) * C1 + rho * b; nb = below(a, grid)
            if not (b < nb < a < C1 < rho < 1 - a): raise SystemExit('FAIL: level condition from ' + name)
            b, n = nb, n + 1
            if n > 50: raise SystemExit('FAIL: no convergence from ' + name)
        if b != goal: raise SystemExit('FAIL: overshoot from ' + name)
        out[name] = dict(seed=str(s), levels=n)
    if out['package_backend']['levels'] != len(o['finite_backend_levels']): raise SystemExit('FAIL: package level count')
    print('PASS_CHAIN_LEVELS', json.dumps(dict(package=Path(pkg).name, admitted=str(goal), seeds=out)), flush=True)


if __name__ == '__main__':
    main(sys.argv[1])
