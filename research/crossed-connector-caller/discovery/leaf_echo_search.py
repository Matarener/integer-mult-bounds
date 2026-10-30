"""Search general rank-one thin queries outside the aggregate space.

This is a finite necessary-condition search. It is not a native caller.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import importlib.util
import itertools
import json
from pathlib import Path
import random
import time
import z3

spec=importlib.util.spec_from_file_location('source',Path(__file__).resolve().parents[1]/'vendor/algebra.py')
source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
N=8;F=z3.BoolVal(False);T=z3.BoolVal(True)

def xor(*args):
    v=F
    for a in args:v=z3.Xor(v,a)
    return v

def matxor(a,b):return [[z3.Xor(x,y) for x,y in zip(ra,rb)] for ra,rb in zip(a,b)]
def product(a,b):return [[xor(*(z3.And(a[i][k],b[k][j]) for k in range(N))) for j in range(N)] for i in range(N)]
def zero():return [[F]*N for _ in range(N)]
def bits(a):return [[z3.BoolVal(bool(row>>j&1)) for j in range(N)] for row in a]
def embed(a,indices):
    out=[0]*N
    for i,row in enumerate(a):out[indices[i]]=sum(1<<indices[j] for j in range(4) if row>>j&1)
    return tuple(out)
def add(a,b):return tuple(x^y for x,y in zip(a,b))
def mul(a,b):return tuple(sum((sum((row>>k&1)*(b[k]>>j&1) for k in range(len(a)))%2)<<j for j in range(len(a))) for row in a)

def setup(thin_count,budget=None):
    solver=z3.Solver();solver.set(timeout=10000)
    choices=[];good=[];targets=[];local=(5,10,5,10);unit=(1,2,4,8)
    options=[]
    for p in sorted(set(p for p,_ in source.FULL)):
        if mul(p,local)!=mul(local,p):continue
        r=mul(p,local)
        if source.rank(r)!=1:continue
        options.append(((p,r),(add(p,unit),add(r,local))))
    for j in range(3):
        choice=[z3.Bool(f'c{j}_{i}') for i in range(24)];choices.append(choice)
        solver.add(z3.PbEq([(x,1) for x in choice],1));indices=(0,1,2+2*j,3+2*j)
        target=embed(unit,indices);targets.append(target)
        for half in range(2):
            matrices=[]
            for kind in range(2):
                numeric=[embed(o[half][kind],indices) for o in options]
                matrices.append([[z3.Or(*[choice[k] for k,a in enumerate(numeric) if a[row]>>col&1]) for col in range(N)] for row in range(N)])
            good.append((j,*matrices))
    thin=[];active=[]
    for k in range(thin_count):
        u=[z3.Bool(f'u{k}_{i}') for i in range(N)];v=[z3.Bool(f'v{k}_{i}') for i in range(N)]
        enabled=z3.Bool(f'enabled{k}');active.append(enabled)
        solver.add(enabled==z3.And(z3.Or(*u),z3.Or(*v)),z3.Not(xor(*(z3.And(a,b) for a,b in zip(u,v)))))
        if budget is None:solver.add(enabled)
        r=[[z3.And(u[i],v[j]) for j in range(N)] for i in range(N)]
        thin.append((3,zero(),r))
    if budget is not None:solver.add(z3.PbLe([(x,1) for x in active],budget))
    calls=good+thin;total=zero()
    for _,_,r in calls:total=matxor(total,r)
    for i,j in itertools.product(range(N),repeat=2):solver.add(total[i][j]==(i==j))
    return solver,calls,choices,options

def constraints(solver,calls,order):
    tail=zero();out=[zero() for _ in range(3)]
    for index in reversed(order):
        stage,p,r=calls[index]
        if stage<3:out[stage]=matxor(out[stage],matxor(product(p,tail),product(tail,p)))
        tail=matxor(tail,r)
    for mat in out:
        for row in mat:
            for val in row:solver.add(z3.Not(val))

def stage_constraints(solver,calls,order):
    # Pairwise scalar-stage coefficients are necessary for the full word.
    places={k:order.index(k) for k in range(6)}
    for j,k in itertools.combinations(range(3),2):
        a,b=sorted((places[2*j],places[2*j+1]));c,d=sorted((places[2*k],places[2*k+1]))
        if b<c or d<a:continue
        if c<a:j,k=k,j;a,b,c,d=c,d,a,b
        pj=calls[order[a]][1]
        if d<b:
            ek=matxor(calls[2*k][1],calls[2*k+1][1]);left,right=pj,ek
        else:
            left,right=calls[order[b]][1],calls[order[c]][1]
        comm=matxor(product(left,right),product(right,left))
        for row in comm:
            for v in row:solver.add(z3.Not(v))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--thin',type=int,default=6);ap.add_argument('--cases',type=int,default=12);ap.add_argument('--timeout',type=int,default=10000);ap.add_argument('--seed',type=int,default=20261026);ap.add_argument('--budget',type=int);args=ap.parse_args()
    rng=random.Random(args.seed);records=[];start=time.monotonic()
    for case in range(args.cases):
        solver,calls,choices,options=setup(args.thin,args.budget);solver.set(timeout=args.timeout)
        if case<6:
            second=list(itertools.permutations((1,3,5)))[case]
            order=[0,2,4]+list(range(6,6+args.thin))+list(second)
        else:
            order=list(range(6+args.thin));rng.shuffle(order)
        stage_constraints(solver,calls,order);constraints(solver,calls,order);result=solver.check()
        row={'case':case,'order':order,'status':str(result)}
        if result==z3.sat:
            m=solver.model();row['calls']=[{'stage':s,'p':[sum(int(z3.is_true(m.eval(x,model_completion=True)))<<j for j,x in enumerate(r)) for r in p],'r':[sum(int(z3.is_true(m.eval(x,model_completion=True)))<<j for j,x in enumerate(row)) for row in r]} for s,p,r in calls]
            row['choices']=[next(i for i,v in enumerate(c) if z3.is_true(m.eval(v))) for c in choices]
        records.append(row);print(json.dumps(row if result!=z3.sat else {k:row[k] for k in ('case','order','status','choices')})+' '+str(round(time.monotonic()-start,2)),flush=True)
        Path(__file__).with_name(f'LEAF-THIN{args.thin}-BUDGET{args.budget}-SEED{args.seed}.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
