"""Eliminate the first mixed equation for general shortest-query projectors.

The projector chart is affine with one quadratic rank constraint per site.
The endpoint projectors do not enter the query-character condition.
"""
import argparse
import json
from pathlib import Path
import time
import sympy as s


def build(n):
    ident = s.eye(n)
    us = [ident[:, j] for j in range(n)] + [s.Matrix([(-1)**(j+1) for j in range(n)])]
    vs = [s.Matrix([[0 if i == j else (1 if i > j else -1) for j in range(n)]]) for i in range(n+1)]
    ts = [ident-2*u*v for u, v in zip(us, vs)]
    variables, ps, qs = [], [], []
    for site in range(1, n):
        u, v = us[site], vs[site]
        pivot = next(j for j in range(n) if v[j])
        a = ident[:, pivot]/v[pivot]
        basis = s.Matrix.hstack(u, a, *[ident[:, j]-v[j]*a for j in range(n) if j not in (site, pivot)])
        av = s.symbols(f'a{site}_0:{n-2}')
        bv = s.symbols(f'b{site}_0:{n-2}')
        c = s.Symbol(f'c{site}')
        variables.extend((*av, *bv, c))
        core = s.zeros(n);core[0,0]=core[1,1]=1;core[0,1]=c
        for j in range(n-2):core[j+2,1]=av[j];core[0,j+2]=bv[j]
        ps.append(basis*core*basis.inv())
        qs.append(c+sum(a*b for a,b in zip(av,bv)))
    tail, tails = ident, []
    for i in range(n, 0, -1):
        tail = tail*ts[i]
        if i-1>0:tails.append(tail)
    tails.reverse()
    conjugates = [t*p*t.inv() for t,p in zip(tails,ps)]
    linear = list(sum((p-q for p,q in zip(ps,conjugates)),s.zeros(n)))
    solution = next(iter(s.linsolve(linear, variables)))
    free = sorted(set().union(*(v.free_symbols for v in solution)), key=str)
    sub = dict(zip(variables,solution))
    ps = [p.subs(sub, simultaneous=True) for p in ps]
    ps = [p.applyfunc(s.expand) for p in ps]
    qs = [s.expand(q.subs(sub, simultaneous=True)) for q in qs]
    return free, ps, qs, ts, variables, solution


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n',type=int,default=6)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    start=time.monotonic()
    free,ps,qs,ts,variables,solution=build(args.n)
    result={'n':args.n,'free':list(map(str,free)),
            'projectors':[[list(map(str,p.row(i))) for i in range(args.n)] for p in ps],
            'quadratics':list(map(str,qs)), 'queries':[t.tolist() for t in ts],
            'original_variables':list(map(str,variables)), 'linear_solution':list(map(str,solution)),
            'seconds':time.monotonic()-start}
    result['queries']=[[[int(v) for v in row] for row in t] for t in result['queries']]
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'n':args.n,'linear_variables':len(variables),'free':len(free),'seconds':result['seconds']}),flush=True)
