"""Test short interval Gram constraints for a finite-order stage.

The scalar stage has every p-th root as a character. Intervals with fewer
than p interior factors cannot use the cyclic relation. This exact test
uses only their first two coefficients and all projector identities.
"""
import argparse
import json
from pathlib import Path
import time
import exact_replay as e


def sandwich(v, matrix, u):
    return e.add(*(e.scale(matrix[i][j], v[i]*u[j])
                   for i in range(len(v)) for j in range(len(u)) if v[i]*u[j]))


def equations(ps, us, vs, period, degree):
    n = len(us[0])
    out = []
    for low in range(n):
        for high in range(low+2,n+1):
            if high-low > period:
                continue
            sites = list(range(low+1,high))
            for reverse in (False,True):
                first, second = e.zero(n), e.zero(n)
                for site in sites[::(-1 if reverse else 1)]:
                    p = ps[site-1]
                    if degree == 2:
                        second = e.ma(second,e.mm(p,first))
                    first = e.ma(first,p)
                row,col,sign = (low,high,-1) if reverse else (high,low,1)
                count = len(sites) if degree == 1 else len(sites)*(len(sites)-1)//2
                value = sandwich(vs[row],first if degree == 1 else second,us[col])
                out.append(e.add(value,e.const(-sign*count)))
    return out


def check(n,period):
    started = time.monotonic()
    names,ps,qs,ts = e.chart(n)
    us,vs,_ = e.canonical(n)
    linear = equations(ps,us,vs,period,1)
    values = e.linear_solution(linear)
    steps = []
    if values is None:
        status = 'EXACT_INTERVAL_LINEAR_CONTRADICTION'
    else:
        ps = [e.ms(p,values) for p in ps]
        qs = [e.substitute(q,values) for q in qs]
        need = equations(ps,us,vs,period,1)
        if any(need):
            raise ValueError('The interval first-coefficient solution fails')
        system = qs + equations(ps,us,vs,period,2)
        while True:
            reduced = e.row_reduce(system)
            affine = [p for p in reduced if all(len(m)<=1 for m in p)]
            count = len({v for p in system for m in p for v in m})
            row = {'variables':count,'affine_consequences':len(affine)}
            steps.append(row);print(json.dumps(row),flush=True)
            if any(set(p)=={()} for p in affine):
                status = 'EXACT_INTERVAL_QUADRATIC_CONTRADICTION';break
            if not affine:
                status = 'UNRESOLVED_INTERVAL_SYSTEM';break
            values = e.linear_solution(affine)
            system = [e.substitute(p,values) for p in system]
    return {'n':n,'period':period,'status':status,'steps':steps,
            'seconds':time.monotonic()-started,'new_kappa':False}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--n',type=int,default=8)
    parser.add_argument('--period',type=int,default=7)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=check(args.n,args.period)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
