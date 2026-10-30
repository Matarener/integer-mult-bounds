"""Apply exact linear consequences of the quadratic endpoint equations."""
import argparse
import json
from pathlib import Path
import time
import sympy as s


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chart',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();start=time.monotonic()
    data=json.loads(args.chart.read_text());n=data['n']
    variables=list(s.symbols(data['free']))
    ps=[s.Matrix([[s.sympify(x) for x in row] for row in p]) for p in data['projectors']]
    ts=[s.Matrix(t) for t in data['queries']]
    tail=s.eye(n);tails=[]
    for i in range(n,0,-1):
        tail=tail*ts[i]
        if i-1>0:tails.append(tail)
    tails.reverse();cs=[t*p*t.inv() for t,p in zip(tails,ps)]
    second=sum((ps[j]*ps[i]-cs[j]*cs[i] for j in range(n-1) for i in range(j)),s.zeros(n))
    equations=list(dict.fromkeys(s.expand(q) for q in [*map(s.sympify,data['quadratics']),*second]))
    equations=[q for q in equations if q]
    original=list(map(str,equations));steps=[]
    while True:
        polys=[s.Poly(q,*variables) for q in equations]
        monomials=sorted(set().union(*(set(p.monoms()) for p in polys)),key=lambda m:(sum(m),m),reverse=True)
        matrix=s.Matrix([[p.coeff_monomial(m) for m in monomials] for p in polys])
        reduced,_=matrix.rref()
        linear=[]
        for row in reduced.tolist():
            if any(a for a,m in zip(row,monomials) if sum(m)>1):continue
            q=sum(a*s.prod(v**e for v,e in zip(variables,m)) for a,m in zip(row,monomials))
            if q:linear.append(q)
        step={'variables':list(map(str,variables)), 'equations':len(equations),
              'monomials':len(monomials),'linear_consequences':list(map(str,linear))}
        steps.append(step);print(json.dumps(step),flush=True)
        if any(not q.free_symbols for q in linear):
            status='EXACT_QUADRATIC_CONTRADICTION';break
        if not linear:
            status='UNRESOLVED_QUADRATIC_SYSTEM';break
        solution=next(iter(s.linsolve(linear,variables)))
        substitution=dict(zip(variables,solution))
        equations=list(dict.fromkeys(s.expand(q.subs(substitution,simultaneous=True)) for q in equations))
        equations=[q for q in equations if q]
        variables=sorted(set().union(*(q.free_symbols for q in equations)),key=str)
    result={'status':status,'n':n,'original_equations':original,'steps':steps,
            'remaining_equations':list(map(str,equations)), 'seconds':time.monotonic()-start}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':status,'seconds':result['seconds']}),flush=True)
