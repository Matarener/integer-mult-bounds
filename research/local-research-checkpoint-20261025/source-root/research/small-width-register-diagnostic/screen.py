#!/usr/bin/env python3
"""Bounded necessary-condition screens, NOT a supplier verifier.

Requires z3-solver. Every timeout is reported as unknown, never as exclusion.
Bit: exact degree-two augmentation equations over F2 for dyadic shear frames.
Complex: exact f=1 specialization over F5 of Gaussian-dyadic Hadamards.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

import z3 as z


def xor(xs):
    xs = list(xs)
    if not xs:
        return z.BoolVal(False)
    out = xs[0]
    for x in xs[1:]:
        out = z.Xor(out, x)
    return out


def choose(k, values):
    out = values[-1]
    for i in reversed(range(len(values) - 1)):
        out = z.If(k == i, values[i], out)
    return out


def dyadic_catalog():
    lines = []
    for v in itertools.product((-1, 0, 1), repeat=3):
        support = [x for x in v if x]
        if len(support) in (1, 2) and support[0] == 1:
            lines.append(v)
    # Matrices B=2A are integral. A=alpha vv^T/(v^T v), rank one.
    return sorted(set(tuple(2 * alpha * v[i] * v[j] // sum(x*x for x in v)
                            for i in range(3) for j in range(3))
                      for v in lines for alpha in (-2, -1, 1, 2)))


def bit_screen(timeout_ms, control=None, structured=False):
    W, E = 4, 12 if control == 'positive' else 11
    cat = dyadic_catalog()
    solver = z.SolverFor('QF_BV')
    solver.set(timeout=timeout_ms, random_seed=0)
    frame = [z.BitVec(f'f{t}', 6) for t in range(E)]
    u = [[z.Bool(f'u{t}_{i}') for i in range(W)] for t in range(E)]
    v = [[z.Bool(f'v{t}_{i}') for i in range(W)] for t in range(E)]
    for t in range(E):
        solver.add(z.ULT(frame[t], len(cat)),
                   xor(z.And(u[t][i], v[t][i]) for i in range(W)))
    # Common target is invariant under scalar conjugacy: normalize first N.
    if not structured:
        for i in range(W):
            solver.add(u[0][i] == (i == 0), v[0][i] == (i == 0))
    if control:
        for t in range(E):
            role, axis = divmod(t, 3)
            B = tuple(2*int(j == 3*axis+axis) for j in range(9))
            solver.add(frame[t] == cat.index(B))
            for i in range(W):
                solver.add(u[t][i] == (i == role), v[t][i] == (i == role))
    elif structured:
        # Five signed coordinate-pair projector pairs plus 2 E00.
        # Their sum is 4 I exactly. Cyclic target roles; all 2^33 feedback
        # choices remain available through the unrestricted off-diagonal v.
        pairs=[(0,1),(1,2),(0,2),(1,2),(1,2)]
        word=[]
        for a,b in pairs:
            q=[0]*3;q[a]=q[b]=1
            word.append(tuple(q[i]*q[j] for i in range(3) for j in range(3)))
        word.append((4,0,0,0,0,0,0,0,0))
        for a,b in reversed(pairs):
            q=[0]*3;q[a]=1;q[b]=-1
            word.append(tuple(q[i]*q[j] for i in range(3) for j in range(3)))
        assert tuple(sum(B[j] for B in word) for j in range(9))==(8,0,0,0,8,0,0,0,8)
        for t,B in enumerate(word):
            solver.add(frame[t]==cat.index(B))
            for i in range(W):
                solver.add(u[t][i]==(i==t%W))
    # Determinant in the commutative group ring: sum A_t = W I.
    for j in range(9):
        solver.add(sum((choose(frame[t], [z.BitVecVal(a[j],8) for a in cat]) for t in range(E)), z.BitVecVal(0,8))
                   == (2 * W if j in (0, 4, 8) else 0))
    # All 511 nonzero binary linear functionals; degree-two equations only
    # need matrix units and pair sums, by the quadratic polarization law.
    units = [tuple(int(i == j) for i in range(9)) for j in range(9)]
    queries = units + [tuple(a+b for a,b in zip(units[i], units[j]))
                       for i in range(9) for j in range(i+1, 9)]
    for q, weights in enumerate(queries):
        exponents = [sum(x*y for x,y in zip(a, weights)) for a in cat]
        b1 = [bool(b % 2) for b in exponents]
        b2 = [bool((b*(b-1)//2) % 2) for b in exponents]
        S1 = [[z.BoolVal(False) for j in range(W)] for i in range(W)]
        S2 = [[z.BoolVal(False) for j in range(W)] for i in range(W)]
        for t in range(E):
            c1 = choose(frame[t], b1)
            c2 = choose(frame[t], b2)
            dot = [xor(z.And(v[t][k], S1[k][j]) for k in range(W))
                   for j in range(W)]
            T1 = [[z.Bool(f'q{q}_t{t}_s1_{i}_{j}') for j in range(W)] for i in range(W)]
            T2 = [[z.Bool(f'q{q}_t{t}_s2_{i}_{j}') for j in range(W)] for i in range(W)]
            for i in range(W):
                for j in range(W):
                    nij = z.And(u[t][i], v[t][j])
                    solver.add(T1[i][j] == z.Xor(S1[i][j], z.And(c1, nij)))
                    solver.add(T2[i][j] == xor((S2[i][j], z.And(c1,u[t][i],dot[j]), z.And(c2,nij))))
            S1, S2 = T1, T2
        trace = sum(weights[j] for j in (0,4,8)) % 2
        for i in range(W):
            for j in range(W):
                solver.add(z.Not(S1[i][j]), S2[i][j] == bool(trace and i == j))
    started = time.monotonic()
    result = solver.check()
    out = dict(side='bit', control=control, structured=structured, m=3, W=W, paid_rank=E, catalog_size=len(cat),
               queries=len(queries), result=str(result), seconds=time.monotonic()-started,
               timeout_ms=timeout_ms,
               scope='Necessary determinant and augmentation-through-degree-two conditions only; dyadic coordinate/pair-projector catalog.')
    if result == z.sat:
        model = solver.model()
        out['candidate'] = [dict(B=list(cat[model.eval(frame[t]).as_long()]),
                                 u=[int(z.is_true(model.eval(x))) for x in u[t]],
                                 v=[int(z.is_true(model.eval(x))) for x in v[t]]) for t in range(E)]
    if result == z.unknown:
        out['reason'] = solver.reason_unknown()
    return out


def hadamard_catalog():
    # H_(v,w), w.v=1: Fourier on pairs x,x+v, using w.x as their bit.
    return [(v,w) for v in range(1,8) for w in range(1,8)
            if (v&w).bit_count() % 2]


def complex_screen(timeout_ms, control=None, structured=False):
    # Gaussian i -> 2 in F5; (1+i)/2 -> 4 = -1. No field divisions.
    W,E,p = 3,9 if control == 'positive' else 8,5
    solver = z.SolverFor('QF_BV')
    solver.set(random_seed=0)
    u = [[z.BitVec(f'cu{t}_{i}',3) for i in range(W)] for t in range(E)]
    v = [[z.BitVec(f'cv{t}_{i}',3) for i in range(W)] for t in range(E)]
    direction=[z.BitVec(f'dir{t}',3) for t in range(E)]
    covector=[z.BitVec(f'cov{t}',3) for t in range(E)]
    def parity(b):
        return xor(z.Extract(i,i,b)==1 for i in range(3))
    def plus(a,b):
        total=z.ZeroExt(1,a)+z.ZeroExt(1,b)
        return z.Extract(2,0,z.If(z.UGE(total,5),total-5,total))
    def negative(a):
        return z.If(a==0,z.BitVecVal(0,3),5-a)
    def signed(a,c):
        return z.If(c==0,z.BitVecVal(0,3),z.If(c==1,a,negative(a)))
    for t in range(E):
        solver.add(direction[t]!=0,covector[t]!=0,parity(direction[t]&covector[t]))
        for x in u[t]+v[t]:
            solver.add(z.Or(x==0,x==1,x==4))
        # Enforce dot=1 over the integers, not just modulo 5. The possible
        # dot products are -3..3, so residue 1 already uniquely means 1.
        prod=[signed(u[t][i],v[t][i]) for i in range(W)]
        solver.add(plus(plus(prod[0],prod[1]),prod[2])==1)
        if control:
            role,axis=divmod(t,3)
            solver.add(direction[t]==1<<axis,covector[t]==1<<axis)
            for i in range(W):
                solver.add(u[t][i]==int(i==role),v[t][i]==int(i==role))
        elif structured:
            role,axis=t%W,t//W
            solver.add(direction[t]==1<<axis,covector[t]==1<<axis)
            for i in range(W):
                solver.add(u[t][i]==int(i==role))
    insertions={} if control else {2:(0,0,1),5:(1,1,2)}
    def wanted(column):
        return [0 if i//8!=column//8 else (4*(-1 if ((i%8)&(column%8)).bit_count()%2 else 1))%p for i in range(24)]
    def add_column(column):
        S=[z.BitVecVal(int(i==column),3) for i in range(24)]
        for t in range(E):
            if t in insertions:
                role,cb,tb=insertions[t]
                prior=list(S)
                for x in range(8):
                    S[8*role+x]=prior[8*role+(x^(((x>>cb)&1)<<tb))]
            dot=[z.BitVec(f'dot{column}_{t}_{x}',3) for x in range(8)]
            for x in range(8):
                terms=[signed(S[8*k+x],v[t][k]) for k in range(W)]
                solver.add(dot[x]==plus(plus(terms[0],terms[1]),terms[2]))
            delta=[z.BitVec(f'delta{column}_{t}_{x}',3) for x in range(8)]
            for x in range(8):
                other=choose(direction[t],[dot[x^d] for d in range(8)])
                same=z.If(parity(covector[t]&x),negative(dot[x]),dot[x])
                solver.add(delta[x]==plus(negative(plus(same,other)),negative(dot[x])))
            T=[z.BitVec(f'cs{column}_{t}_{i}',3) for i in range(24)]
            for role in range(W):
                for x in range(8):
                    solver.add(T[8*role+x]==plus(S[8*role+x],signed(delta[x],u[t][role])))
            S=T
        for actual,target in zip(S,wanted(column)):
            solver.add(actual==target)
    def read_candidate():
        model=solver.model()
        return [dict(frame=[model.eval(direction[t]).as_long(),model.eval(covector[t]).as_long()],
                     u=[-1 if model.eval(x).as_long()==4 else model.eval(x).as_long() for x in u[t]],
                     v=[-1 if model.eval(x).as_long()==4 else model.eval(x).as_long() for x in v[t]]) for t in range(E)]
    def first_failure(word):
        for column in range(24):
            S=[int(i==column) for i in range(24)]
            for t,move in enumerate(word):
                if t in insertions:
                    role,cb,tb=insertions[t]
                    old=list(S)
                    for x in range(8):
                        S[8*role+x]=old[8*role+(x^(((x>>cb)&1)<<tb))]
                dot=[sum(move['v'][r]*S[8*r+x] for r in range(W))%p for x in range(8)]
                d,c=move['frame']
                delta=[(-(-1 if (x&c).bit_count()%2 else 1)*dot[x]-dot[x^d]-dot[x])%p for x in range(8)]
                S=[(S[8*r+x]+move['u'][r]*delta[x])%p for r in range(W) for x in range(8)]
            if S!=wanted(column):
                return column
        return None
    started=time.monotonic()
    columns=[0]
    add_column(0)
    iterations=0
    candidate=None
    reason=None
    while True:
        remaining=timeout_ms-int(1000*(time.monotonic()-started))
        if remaining<=0:
            result='unknown';reason='overall budget';break
        solver.set(timeout=remaining)
        result=str(solver.check())
        iterations+=1
        if result!='sat':
            reason=solver.reason_unknown() if result=='unknown' else None
            break
        candidate=read_candidate()
        failed=first_failure(candidate)
        if failed is None:
            break
        assert failed not in columns, 'independent specialization disagrees with encoding'
        columns.append(failed)
        add_column(failed)
        candidate=None
    out=dict(side='complex',control=control,structured=structured,m=3,W=W,paid_rank=E,catalog_size=28,
             insertions={str(k):list(v) for k,v in insertions.items()},result=result,
             seconds=time.monotonic()-started,timeout_ms=timeout_ms,columns=columns,iterations=iterations,
             scope='Necessary f=1 reduction over F5 only; 28 directional Gaussian Hadamards, signed ternary scalar vectors, two specified free CNOT insertions.')
    if result=='sat':
        out['candidate']=candidate
    if reason:
        out['reason']=reason
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('side',choices=['bit','complex'])
    ap.add_argument('--timeout-ms',type=int,default=60000)
    ap.add_argument('--control',choices=['positive','negative'])
    ap.add_argument('--structured',action='store_true')
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    z.set_param('memory_max_size',1500)
    answer=(bit_screen if args.side=='bit' else complex_screen)(args.timeout_ms,args.control,args.structured)
    answer.update(z3_version=z.get_version_string(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(answer,indent=2)+'\n')
    print(json.dumps({k:v for k,v in answer.items() if k!='candidate'},indent=2))
