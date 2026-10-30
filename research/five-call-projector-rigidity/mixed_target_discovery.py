"""Test q full calls with q-1 central-query and one ordinary target.

All q inputs are arbitrary and independent. The proposed stage endpoint
is z^2 on every field. The last field has no central query at return.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path
import time
import exact_replay as e


def construct(q,coupling=1):
    r=q-1
    oldus,oldvs,_=e.canonical(r)
    us=[u+[0] for u in oldus]
    vs=[v+[coupling] for v in oldvs]
    names,ps,qs,ts=[],[],[],[]
    def var(name):
        index=len(names);names.append(name);return {(index,):F(1)}
    for i,(u,v) in enumerate(zip(us,vs)):
        pivot=next(j for j in range(q) if v[j])
        drop=next(j for j in range(q) if u[j] and j!=pivot)
        h=[F(int(j==pivot),v[pivot]) for j in range(q)]
        cols=[u,h]+[[int(k==j)-v[j]*h[k] for k in range(q)]
                    for j in range(q) if j not in (pivot,drop)]
        basis=list(map(list,zip(*cols)))
        av=[var(f'a{i}_{j}') for j in range(q-2)]
        bv=[var(f'b{i}_{j}') for j in range(q-2)]
        c=var(f'c{i}')
        core=e.zero(q);core[0][0]=core[1][1]=e.const(1);core[0][1]=c
        for j in range(q-2):core[j+2][1],core[0][j+2]=av[j],bv[j]
        ps.append(e.mm(e.mm(e.numeric(basis),core),e.numeric(e.inverse(basis))))
        qs.append(e.add(c,*(e.mul(a,b) for a,b in zip(av,bv))))
        ts.append(e.numeric([[int(a==b)-2*u[a]*v[b] for b in range(q)] for a in range(q)]))
    target=e.numeric([[(-1 if i<r else 1)*int(i==j) for j in range(q)] for i in range(q)])
    return names,ps,qs,ts,target


def equations(ps,ts,target,degree):
    n=len(ps[0]);words=[[e.eye(n)],[e.eye(n)]]
    for p,t in zip(ps,ts):
        for channel,query in enumerate([e.eye(n),t]):
            old=[e.mm(query,x) for x in words[channel]]
            word=[old[0]]+[e.ma(old[i],e.mm(p,old[i-1])) for i in range(1,len(old))]
            if len(old)<=degree:word.append(e.mm(p,old[-1]))
            words[channel]=word
    coefficient=2 if degree==1 else (1 if degree==2 else 0)
    out=[]
    for word,want in zip(words,[e.eye(n),target]):
        error=e.ma(word[degree],[[e.scale(x,coefficient) for x in row] for row in want],-1)
        out.extend(x for row in error for x in row)
    return out


def check(q,coupling=1):
    started=time.monotonic();names,ps,qs,ts,target=construct(q,coupling)
    word=e.eye(q)
    for t in ts:word=e.mm(t,word)
    if word!=target:raise ValueError('The mixed query control fails')
    values=e.linear_solution(equations(ps,ts,target,1));steps=[]
    if values is None:
        status='EXACT_MIXED_FIRST_COEFFICIENT_CONTRADICTION'
    else:
        ps=[e.ms(p,values) for p in ps];qs=[e.substitute(x,values) for x in qs]
        system=qs+equations(ps,ts,target,2)
        while True:
            reduced=e.row_reduce(system);affine=[p for p in reduced if all(len(m)<=1 for m in p)]
            row={'variables':len({v for p in system for m in p for v in m}),'affine_consequences':len(affine)}
            steps.append(row);print(json.dumps(row),flush=True)
            if any(set(p)=={()} for p in affine):status='EXACT_MIXED_SECOND_COEFFICIENT_CONTRADICTION';break
            if not affine:status='UNRESOLVED_MIXED_SYSTEM';break
            values=e.linear_solution(affine);system=[e.substitute(p,values) for p in system]
    return {'q':q,'query_extension':coupling,'central_targets':q-1,'ordinary_targets':1,'stage_degree':2,
            'status':status,'steps':steps,'seconds':time.monotonic()-started,'new_kappa':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--q',type=int,default=7)
    p.add_argument('--coupling',type=int,choices=(0,1),default=1)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();result=check(args.q,args.coupling)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
