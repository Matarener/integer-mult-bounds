"""Add a pair of leaves while keeping the eight thin query factors.

The old call order is retained. New calls can enter any gap.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import itertools
import gzip
import json
from pathlib import Path
import sys
import time
import z3
import cycle_search as C
import leaf_echo_search as L

PARENT=Path(__file__).resolve().parents[1]

def embed(a,indices,n):
    out=C.zero(n)
    for i,row in enumerate(a):
        for j in range(4):out[indices[i]][indices[j]]=z3.BoolVal(bool(row>>j&1))
    return out

def build(case,distinct):
    if case==11:original=json.loads((PARENT/'ESCAPE-WORD.json').read_text())
    else:
        corpus=json.load(gzip.open(Path(__file__).with_name('RESULTS.json.gz'),'rt'))
        original=corpus['LEAF-THIN8-SEED3.json'][case]
    sys.path.insert(0,str(PARENT));from word_replay import replay
    if original['status']!='sat' or not replay(original['calls'],original['order'])['passed']:raise ValueError('The source must be a complete positive word')
    n=12;solver=z3.Solver();calls=[]
    for c in original['calls'][:6]:
        p=C.zero(n);r=C.zero(n)
        for i,j in itertools.product(range(8),repeat=2):p[i][j]=z3.BoolVal(bool(c['p'][i]>>j&1));r[i][j]=z3.BoolVal(bool(c['r'][i]>>j&1))
        calls.append((c['stage'],p,r))
    new_u=[[z3.Bool(f'u{k}_{i}') for i in range(4 if distinct else 2)] for k in range(8)]
    new_v=[[z3.Bool(f'v{k}_{i}') for i in range(4 if distinct else 2)] for k in range(8)]
    old_u=[];old_v=[]
    for k,c in enumerate(original['calls'][6:]):
        v=next(row for row in c['r'] if row);u=sum(1<<i for i,row in enumerate(c['r']) if row);old_u.append(u);old_v.append(v)
        uu=[z3.BoolVal(bool(u>>i&1)) for i in range(8)]+(new_u[k] if distinct else new_u[k]*2)
        vv=[z3.BoolVal(bool(v>>i&1)) for i in range(8)]+(new_v[k] if distinct else new_v[k]*2)
        solver.add(z3.Not(C.xor(*(z3.And(a,b) for a,b in zip(uu,vv)))))
        calls.append((5,C.zero(n),[[z3.And(a,b) for b in vv] for a in uu]))
    # Reject three equal signatures among the new leaves and an old leaf.
    for leaf in range(3):
        solver.add(z3.Or(*[z3.Xor(new_u[k][i],z3.BoolVal(bool(old_u[k]>>(2+2*leaf+(i%2))&1))) for k in range(8) for i in range(4 if distinct else 2)]))
        solver.add(z3.Or(*[z3.Xor(new_v[k][i],z3.BoolVal(bool(old_v[k]>>(2+2*leaf+(i%2))&1))) for k in range(8) for i in range(4 if distinct else 2)]))
    local=(5,10,5,10);unit=(1,2,4,8);options=[]
    for p in sorted(set(p for p,_ in L.source.FULL)):
        if L.mul(p,local)!=L.mul(local,p):continue
        r=L.mul(p,local)
        if L.source.rank(r)!=1:continue
        options.append(((p,r),(L.add(p,unit),L.add(r,local))))
    choices=[]
    for leaf in (3,4):
        chosen=[z3.Bool(f'c{leaf}_{k}') for k in range(24)];choices.extend(chosen);solver.add(z3.PbEq([(c,1) for c in chosen],1));indices=(0,1,2+2*leaf,3+2*leaf)
        for half in range(2):
            matrices=[]
            for kind in range(2):
                vals=[embed(o[half][kind],indices,n) for o in options]
                matrices.append([[z3.Or(*[chosen[k] for k,a in enumerate(vals) if z3.is_true(a[i][j])]) for j in range(n)] for i in range(n)])
            calls.append((leaf,*matrices))
    positions=[z3.Int(f'pos{i}') for i in range(18)];solver.add(z3.Distinct(*positions))
    for p in positions:solver.add(p>=0,p<18)
    for a,b in zip(original['order'],original['order'][1:]):solver.add(positions[a]<positions[b])
    solver.add(positions[14]<positions[15],positions[16]<positions[17])
    total=C.zero(n)
    for _,_,r in calls:total=C.plus(total,r)
    for i,j in itertools.product(range(n),repeat=2):solver.add(total[i][j]==(i==j))
    for stage in range(5):
        out=C.zero(n)
        for i,(s,p,_) in enumerate(calls):
            if s!=stage:continue
            for j,(_,_,r) in enumerate(calls):
                if i==j:continue
                comm=C.plus(C.product(p,r),C.product(r,p));later=positions[i]<positions[j]
                out=C.plus(out,[[z3.And(later,v) for v in row] for row in comm])
        for row in out:
            for v in row:solver.add(z3.Not(v))
    pairs=[]
    for stage in range(3):pairs.append(sorted((2*stage,2*stage+1),key=original['order'].index))
    pairs.extend(((14,15),(16,17)))
    for j,k in itertools.permutations(range(5),2):
        a,b=pairs[j];c,d=pairs[k]
        nested=z3.And(positions[a]<positions[c],positions[d]<positions[b])
        crossing=z3.And(positions[a]<positions[c],positions[c]<positions[b],positions[b]<positions[d])
        e=C.plus(calls[c][1],calls[d][1])
        for condition,left,right in ((nested,calls[a][1],e),(crossing,calls[b][1],calls[c][1])):
            for row in C.plus(C.product(left,right),C.product(right,left)):
                for v in row:solver.add(z3.Implies(condition,z3.Not(v)))
    return solver,calls,positions,choices+[x for row in new_u+new_v for x in row],original

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--timeout',type=int,default=60000);ap.add_argument('--case',type=int,default=11);ap.add_argument('--distinct',action='store_true');args=ap.parse_args();start=time.monotonic();solver,calls,positions,variables,original=build(args.case,args.distinct);solver.set(timeout=args.timeout);status=solver.check();result={'status':str(status),'old_case':original['case'],'new_leaves':2,'thin_queries':8,'new_signature_contract':'independent' if args.distinct else 'identical'}
    if status==z3.sat:
        model=solver.model();order=sorted(range(18),key=lambda i:model.eval(positions[i]).as_long());result['order']=order
        result['calls']=[{'stage':stage,'p':[sum(int(z3.is_true(model.eval(x,model_completion=True)))<<j for j,x in enumerate(row)) for row in p],'r':[sum(int(z3.is_true(model.eval(x,model_completion=True)))<<j for j,x in enumerate(row)) for row in r]} for stage,p,r in calls]
        sys.path.insert(0,str(PARENT));from word_replay import replay
        result['word']=replay(result['calls'],order)
    result['seconds']=round(time.monotonic()-start,3);Path(__file__).with_name(f'GROW-CASE{args.case}-DISTINCT{args.distinct}.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='calls'}),flush=True)
if __name__=='__main__':main()
