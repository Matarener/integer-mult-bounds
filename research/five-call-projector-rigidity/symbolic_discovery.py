"""Seek a characteristic-zero certificate for the five-call query test.

This discovery script uses SymPy. Its output must pass a separate exact
polynomial check before it can support a proof.
"""
import json
from pathlib import Path
import time
import sympy as s


def construct():
    n, ident = 4, s.eye(4)
    us = [ident[:, j] for j in range(4)] + [s.Matrix([-1, 1, -1, 1])]
    vs = [s.Matrix([[0 if i == j else (1 if i > j else -1) for j in range(n)]]) for i in range(5)]
    ts = [ident-2*u*v for u, v in zip(us, vs)]
    variables, projectors, quadratic = [], [], []
    for site in range(1, 4):
        u, v = us[site], vs[site]
        pivot = next(j for j in range(4) if v[j])
        a = ident[:, pivot]/v[pivot]
        basis = s.Matrix.hstack(u, a, *[ident[:, j]-v[j]*a for j in range(4) if j not in (site, pivot)])
        a0, a1, b0, b1, c = s.symbols(f'a{site}0 a{site}1 b{site}0 b{site}1 c{site}')
        variables.extend((a0, a1, b0, b1, c))
        core = s.Matrix([[1, c, b0, b1], [0, 1, 0, 0], [0, a0, 0, 0], [0, a1, 0, 0]])
        projectors.append(basis*core*basis.inv())
        quadratic.append(c+a0*b0+a1*b1)
    plus, minus = [ident], [ts[0]]
    for site, p in enumerate(projectors, 1):
        for word, query in ((plus, ident), (minus, ts[site])):
            old = [query*m for m in word]
            word[:] = [old[0]] + [old[j]+p*old[j-1] for j in range(1, len(old))] + [p*old[-1]]
    errors = [s.expand(x) for i in range(1, 4) for x in ts[4]*minus[i]+plus[i]]
    linear = errors[:16]
    solution = next(iter(s.linsolve(linear, variables)))
    substitution = dict(zip(variables, solution))
    free = sorted(set().union(*(v.free_symbols for v in solution)), key=str)
    reduced = list(dict.fromkeys(s.expand(e.subs(substitution, simultaneous=True)) for e in quadratic+errors[16:]))
    reduced = [p for p in reduced if p]
    return variables, projectors, quadratic, errors, solution, free, reduced


if __name__ == '__main__':
    start = time.monotonic()
    variables, ps, qs, errors, solution, free, reduced = construct()
    print(json.dumps({'variables':len(variables), 'linear_free':list(map(str, free)),
                      'reduced_equations':len(reduced), 'seconds':time.monotonic()-start}), flush=True)
    out = {'variables':list(map(str, variables)), 'linear_solution':list(map(str, solution)),
           'free_variables':list(map(str, free)), 'reduced_equations':list(map(str, reduced))}
    Path('/tmp/imb-five-symbolic-system.json').write_text(json.dumps(out, indent=2)+'\n')
    basis = s.groebner(reduced, *free, order='grevlex', method='f5b')
    out['groebner_basis'] = [str(p.as_expr()) for p in basis.polys]
    out['seconds'] = time.monotonic()-start
    Path('/tmp/imb-five-symbolic-result.json').write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'basis':out['groebner_basis'], 'seconds':out['seconds']}), flush=True)
