"""Search paired native stages on a cycle with free local query frames.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import json
from pathlib import Path
import random
import time
import z3

F=z3.BoolVal(False);T=z3.BoolVal(True)
def xor(*args):
    out=F
    for a in args:out=z3.Xor(out,a)
    return out

def plus(a,b):return [[z3.Xor(x,y) for x,y in zip(aa,bb)] for aa,bb in zip(a,b)]
def zero(n):return [[F]*n for _ in range(n)]
def product(a,b):return [[xor(*(z3.And(a[i][k],b[k][j]) for k in range(len(b)))) for j in range(len(b[0]))] for i in range(len(a))]
def embed(a,indices,n):
    out=zero(n)
    for i,j in itertools.product(range(4),repeat=2):out[indices[i]][indices[j]]=a[i][j]
    return out

def setup(g,thin_count):
    n=2*g;s=z3.Solver();calls=[]
    for j in range(g):
        p=[[z3.Bool(f'p{j}_{r}_{c}') for c in range(4)] for r in range(4)]
        for r,row in enumerate(product(p,p)):
            for c,x in enumerate(row):s.add(x==p[r][c])
        indices=(2*j,2*j+1,2*((j+1)%g),2*((j+1)%g)+1)
        for half in range(2):
            u=[z3.Bool(f'gu{j}_{half}_{i}') for i in range(4)]
            v=[z3.Bool(f'gv{j}_{half}_{i}') for i in range(4)]
            s.add(z3.Or(*u),z3.Or(*v),z3.Not(xor(*(z3.And(a,b) for a,b in zip(u,v)))))
            for i in range(4):
                s.add(xor(*(z3.And(p[i][k],u[k]) for k in range(4)))==(u[i] if half==0 else F))
                s.add(xor(*(z3.And(v[k],p[k][i]) for k in range(4)))==(v[i] if half==0 else F))
            ph=p if half==0 else [[z3.Xor(p[r][c],z3.BoolVal(r==c)) for c in range(4)] for r in range(4)]
            q=[[z3.And(a,b) for b in v] for a in u]
            calls.append((j,embed(ph,indices,n),embed(q,indices,n)))
    for k in range(thin_count):
        u=[z3.Bool(f'u{k}_{i}') for i in range(n)];v=[z3.Bool(f'v{k}_{i}') for i in range(n)]
        s.add(z3.Or(*u),z3.Or(*v),z3.Not(xor(*(z3.And(a,b) for a,b in zip(u,v)))))
        calls.append((g,zero(n),[[z3.And(a,b) for b in v] for a in u]))
    total=zero(n)
    for _,_,r in calls:total=plus(total,r)
    for i,row in enumerate(total):
        for j,x in enumerate(row):s.add(x==(i==j))
    return s,calls

def constraints(s,calls,order,g):
    n=len(calls[0][1]);tail=zero(n);out=[zero(n) for _ in range(g)]
    for i in reversed(order):
        j,p,r=calls[i]
        if j<g:out[j]=plus(out[j],plus(product(p,tail),product(tail,p)))
        tail=plus(tail,r)
    for m in out:
        for row in m:
            for x in row:s.add(z3.Not(x))
    places={k:order.index(k) for k in range(2*g)}
    for j,k in itertools.combinations(range(g),2):
        a,b=sorted((places[2*j],places[2*j+1]));c,d=sorted((places[2*k],places[2*k+1]))
        if b<c or d<a:continue
        if c<a:j,k=k,j;a,b,c,d=c,d,a,b
        if d<b:left,right=calls[order[a]][1],plus(calls[2*k][1],calls[2*k+1][1])
        else:left,right=calls[order[b]][1],calls[order[c]][1]
        for row in plus(product(left,right),product(right,left)):
            for x in row:s.add(z3.Not(x))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--g',type=int,default=3);ap.add_argument('--thin',type=int,default=2);ap.add_argument('--cases',type=int,default=40);ap.add_argument('--timeout',type=int,default=10000);ap.add_argument('--seed',type=int,default=20261026);args=ap.parse_args()
    rng=random.Random(args.seed);out=[];start=time.monotonic()
    for case in range(args.cases):
        s,calls=setup(args.g,args.thin);s.set(timeout=args.timeout)
        order=list(range(2*args.g+args.thin));rng.shuffle(order)
        constraints(s,calls,order,args.g);result=s.check();row={'case':case,'order':order,'status':str(result)}
        if result==z3.sat:
            m=s.model();row['calls']=[{'stage':j,'p':[sum(int(z3.is_true(m.eval(x,model_completion=True)))<<i for i,x in enumerate(r)) for r in p],'r':[sum(int(z3.is_true(m.eval(x,model_completion=True)))<<i for i,x in enumerate(row)) for row in r]} for j,p,r in calls]
            import sys
            sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
            from word_replay import replay
            row['word']=replay(row['calls'],order)
        out.append(row);print(json.dumps({k:v for k,v in row.items() if k!='calls'})+' '+str(round(time.monotonic()-start,2)),flush=True)
        Path(__file__).with_name(f'CYCLE-DIRECT-G{args.g}-THIN{args.thin}-SEED{args.seed}.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
