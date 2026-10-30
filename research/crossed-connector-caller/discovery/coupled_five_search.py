"""Search five rank-two connectors with coupled four-channel stages.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import random
import time
import z3
import cycle_search as C

def setup():
    d=4;n=16;solver=z3.Solver();calls=[]
    for stage in range(3):
        a=[[z3.Bool(f'a{stage}_{i}_{j}') for j in range(d)] for i in range(d)]
        b=[[z3.Bool(f'b{stage}_{i}_{j}') for j in range(d)] for i in range(d)]
        square=C.product(a,a);relation=C.plus(C.product(a,b),C.product(b,a))
        for i,j in itertools.product(range(d),repeat=2):solver.add(square[i][j]==a[i][j],relation[i][j]==b[i][j])
        solver.add(z3.Not(C.xor(*(a[i][i] for i in range(d)))))
        solver.add(z3.Or(*[a[i][j] for i,j in itertools.product(range(d),repeat=2)]))
        solver.add(z3.Or(*[z3.Xor(a[i][j],z3.BoolVal(i==j)) for i,j in itertools.product(range(d),repeat=2)]))
        for half in range(2):
            p=C.zero(n);r=C.zero(n)
            for row,col in itertools.product((0,stage+1),repeat=2):
                for i,j in itertools.product(range(d),repeat=2):
                    value=z3.Xor(a[i][j],b[i][j]) if row==col else b[i][j]
                    if half and row==col and i==j:value=z3.Not(value)
                    p[row*d+i][col*d+j]=value
                    r[row*d+i][col*d+j]=z3.Xor(a[i][j],z3.BoolVal(bool(half and i==j)))
            calls.append((stage,p,r))
    for k in range(5):
        u=[[z3.Bool(f'u{k}_{i}_{j}') for j in range(2)] for i in range(n)]
        v=[[z3.Bool(f'v{k}_{i}_{j}') for j in range(n)] for i in range(2)]
        for j in range(2):solver.add(z3.Or(*(u[i][j] for i in range(n))),z3.Or(*v[j]))
        solver.add(z3.Or(*(z3.Xor(u[i][0],u[i][1]) for i in range(n))),z3.Or(*(z3.Xor(v[0][i],v[1][i]) for i in range(n))))
        for row in C.product(v,u):
            for x in row:solver.add(z3.Not(x))
        calls.append((3,C.zero(n),C.product(u,v)))
    total=C.zero(n)
    for _,_,r in calls:total=C.plus(total,r)
    for i,j in itertools.product(range(n),repeat=2):solver.add(total[i][j]==(i==j))
    return solver,calls

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--cases',type=int,default=8);parser.add_argument('--timeout',type=int,default=10000);args=parser.parse_args();rng=random.Random(271828);rows=[];start=time.monotonic()
    for case in range(args.cases):
        solver,calls=setup();solver.set(timeout=args.timeout);order=list(range(11));rng.shuffle(order);C.constraints(solver,calls,order,3);status=solver.check();row={'case':case,'order':order,'status':str(status)}
        if status==z3.sat:
            model=solver.model();row['calls']=[{'stage':j,'p':[sum(int(z3.is_true(model.eval(x,model_completion=True)))<<i for i,x in enumerate(r)) for r in p],'r':[sum(int(z3.is_true(model.eval(x,model_completion=True)))<<i for i,x in enumerate(row)) for row in r]} for j,p,r in calls]
            import sys
            sys.path.insert(0,str(Path(__file__).resolve().parents[1]));from word_replay import replay
            row['word']=replay(row['calls'],order)
        rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='calls'})+' '+str(round(time.monotonic()-start,2)),flush=True)
        Path(__file__).with_name('COUPLED-FIVE.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
