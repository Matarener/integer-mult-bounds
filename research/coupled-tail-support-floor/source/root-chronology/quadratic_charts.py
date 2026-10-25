#!/usr/bin/env python3
"""Exact X-character monomial algebra and bounded quadratic-chart retiming.

Apache-2.0; substantial OpenAI Codex assistance. Rank screens do not admit a
physical supplier. A saved positive word must separately lower every child.
"""
from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction
from heapq import nsmallest
from math import isqrt
import argparse, hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def need(c,m):
    if not c: raise ValueError(m)
def parity(x): return x.bit_count()&1
def linear(rows,x): return sum(parity(r&x)<<i for i,r in enumerate(rows))
def inverse(rows):
    n=len(rows);a=[r|(1<<(n+i)) for i,r in enumerate(rows)]
    for i in range(n):
        j=next((j for j in range(i,n) if a[j]>>i&1),None)
        need(j is not None,'invertible binary address');a[i],a[j]=a[j],a[i]
        for j in range(n):
            if j!=i and a[j]>>i&1:a[j]^=a[i]
    return tuple(r>>n for r in a)
@lru_cache(None)
def rank(rows):
    basis={}
    for r in rows:
        while r:
            p=r.bit_length()-1
            if p in basis:r^=basis[p]
            else:basis[p]=r;break
    return len(basis)

@dataclass(frozen=True)
class Mono:
    rows:tuple
    offset:int
    alpha:tuple
    quad:tuple
    constant:int=0
    global_phase:int=0
    # Actual all-f family: i^global_phase times the f-fold tensor power.
    def q(self,x):
        return (self.constant+sum(a for i,a in enumerate(self.alpha) if x>>i&1)
                +2*sum(parity(r&x) for i,r in enumerate(self.quad) if x>>i&1))%4
    def act(self,x):return linear(self.rows,x)^self.offset
    def __matmul__(self,b):return compose(self,b)
    def inv(self):return adjoint(self)
    def data(self):return dict(rows=list(self.rows),offset=self.offset,alpha=list(self.alpha),quad=list(self.quad),constant=self.constant,global_phase=self.global_phase)
    def polar(self):
        r=[(self.alpha[i]&1)<<i for i in range(len(self.rows))]
        for i,row in enumerate(self.quad):
            for j in range(i+1,len(r)):
                if row>>j&1:r[i]^=1<<j;r[j]^=1<<i
        return tuple(r)

def from_function(rows,offset,fn,global_phase=0):
    n=len(rows);c=fn(0)%4;alpha=tuple((fn(1<<i)-c)%4 for i in range(n));quad=[]
    for i in range(n):
        row=0
        for j in range(i+1,n):
            z=(fn((1<<i)|(1<<j))-c-alpha[i]-alpha[j])%4
            need(z%2==0,'quadratic Gaussian phase');row|=(z//2)<<j
        quad.append(row)
    return Mono(tuple(rows),offset,alpha,tuple(quad),c,global_phase%4)

@lru_cache(None)
def compose(a,b):
    n=len(a.rows);rows=tuple(sum(parity(a.rows[i]&sum(((b.rows[k]>>j)&1)<<k for k in range(n)))<<j for j in range(n)) for i in range(n))
    return from_function(rows,linear(a.rows,b.offset)^a.offset,
                         lambda x:b.q(x)+a.q(b.act(x)),a.global_phase+b.global_phase)
@lru_cache(None)
def adjoint(a):
    rows=inverse(a.rows);off=linear(rows,a.offset)
    return from_function(rows,off,lambda x:-a.q(linear(rows,x)^off),-a.global_phase)
def identity(n):return Mono(tuple(1<<i for i in range(n)),0,(0,)*n,(0,)*n)
@lru_cache(None)
def chart(rows):
    n=len(rows)
    return Mono(tuple(1<<i for i in range(n)),0,tuple((r>>i)&1 for i,r in enumerate(rows)),tuple(r&~((1<<(i+1))-1) for i,r in enumerate(rows)))
def old_operator(e,n):
    d=e['operator'];p=d['block_permutation'];rows=[0]*n
    for i,j in enumerate(p):rows[2*j]=1<<(2*i);rows[2*j+1]=1<<(2*i+1)
    out=Mono(tuple(rows),0,(0,)*n,(0,)*n)
    alpha=[0]*n;offset=0
    for i in d['native_blocks']:alpha[2*i]=3;alpha[2*i+1]=1;offset^=3<<(2*i)
    N=Mono(identity(n).rows,offset,tuple(alpha),(0,)*n,0,(len(d['native_blocks'])+(2 if d['sign']==-1 else 0))%4)
    return N@out
def decode(e,n):
    if 'x_monomial' in e:
        d=e['x_monomial'];return Mono(tuple(d['rows']),d['offset'],tuple(d['alpha']),tuple(d['quad']),d.get('constant',0),d.get('global_phase',0))
    if e['kind']=='ADDRESS_LINEAR':
        # Physical P_A acts on X characters by A^-T.
        ri=inverse(tuple(e['operator']['address_rows']))
        rows=tuple(sum(((ri[j]>>i)&1)<<j for j in range(n)) for i in range(n))
        return Mono(rows,0,(0,)*n,(0,)*n)
    return old_operator(e,n)
def xor(a,b):return tuple(x^y for x,y in zip(a,b))
@lru_cache(None)
def move(g,A):
    # g D_A = D_B h with h physically monomial (native rank zero).
    n=len(A);ri=inverse(g.rows);C=xor(g.polar(),A)
    cols=tuple(sum(((ri[i]>>j)&1)<<i for i in range(n)) for j in range(n))
    return tuple(sum(parity(u&linear(C,v))<<j for j,v in enumerate(cols)) for u in cols)

def future_charts(events,banks,n):
    gs=[identity(n)]*banks;out=[None]*(len(events)+1);out[-1]=tuple(g.polar()for g in gs)
    for k in range(len(events)-1,-1,-1):
        e=events[k]
        if e['kind']=='BANK_SWAP':i,j=e['banks'];gs[i],gs[j]=gs[j],gs[i]
        elif e['kind']not in('ADD','SCALE'):i=e['bank'];gs[i]=gs[i]@decode(e,n)
        out[k]=tuple(g.polar()for g in gs)
    return out

def search(events,banks,n,beam,heuristic_weight=1,future_hint=False):
    zero=(0,)*n;cap=isqrt((n*n-1)//2)
    future=future_charts(events,banks,n)
    states={(zero,)*banks:(0,())};sizes=[]
    for index,e in enumerate(events):
        kind=e['kind']
        if kind=='ADD':
            d,s=e['dst'],e['src'];out={}
            for state,(cost,path) in states.items():
                A,B=state[d],state[s]
                candidates={zero,A,B,xor(A,B),tuple(a&b for a,b in zip(A,B)),tuple(a|b for a,b in zip(A,B))}
                if future_hint:candidates.update((future[index+1][d],future[index+1][s]))
                for R in candidates:
                    ranks=rank(xor(A,R)),rank(xor(B,R))
                    ns=list(state);ns[d]=ns[s]=R;ns=tuple(ns);c=cost+sum(ranks)
                    if ns not in out or c<out[ns][0]:out[ns]=(c,path+(R,))
            def priority(item):
                st,(cost,path)=item
                debt=sum(rank(xor(a,b))for a,b in zip(st,future[index+1])) if future_hint else sum(map(rank,st))
                return cost+heuristic_weight*debt,cost,st
            states=dict(nsmallest(beam,out.items(),key=priority));sizes.append([index,len(out),len(states)])
        elif kind=='SCALE':pass
        elif kind=='BANK_SWAP':
            out={};i,j=e['banks']
            for state,v in states.items():ns=list(state);ns[i],ns[j]=ns[j],ns[i];out[tuple(ns)]=v
            states=out
        else:
            g=decode(e,n);i=e['bank'];out={}
            for state,v in states.items():ns=list(state);ns[i]=move(g,state[i]);out[tuple(ns)]=v
            states=out
        need(states,'nonempty bounded chart screen')
    eligible=list(states.items())
    st,(cost,path)=min(eligible,key=lambda x:(x[1][0]+sum(map(rank,x[0])),x[0]))
    return path,cost+sum(map(rank,st)),sizes

def compile_word(events,banks,n,choices):
    pending=[(0,)*n for _ in range(banks)];out=[];choices=iter(choices)
    def emit(i,g,label):
        if g!=identity(n):out.append(dict(kind='NATIVE' if rank(g.polar()) else 'ADDRESS_OR_UNIT',bank=i,x_monomial=g.data(),rank_per_f=rank(g.polar()),label=label))
    for e in events:
        if e['kind']=='ADD':
            R=next(choices)
            for i in (e['dst'],e['src']):emit(i,chart(R).inv()@chart(pending[i]),'paid quadratic chart alignment');pending[i]=R
            out.append(e)
        elif e['kind']=='SCALE':out.append(e)
        elif e['kind']=='BANK_SWAP':
            i,j=e['banks'];pending[i],pending[j]=pending[j],pending[i];out.append(e)
        else:
            g=decode(e,n);i=e['bank'];B=move(g,pending[i]);h=chart(B).inv()@g@chart(pending[i])
            need(rank(h.polar())==0,'transport adapter is physically monomial');emit(i,h,'literal free chart transport');pending[i]=B
    need(next(choices,None) is None,'one choice per ADD')
    for i,A in enumerate(pending):emit(i,chart(A),'paid final chart')
    return out

def replay(events,banks,n):
    I=identity(n);one=(Fraction(1),Fraction(0))*4;zero=(Fraction(0),)*8
    def rotate(v,c,g):
        out=[]
        for r in range(4):
            a,b=v[2*r:2*r+2]
            out.extend(((a,b),(-b,a),(-a,-b),(b,-a))[(c*r+g)%4])
        return tuple(out)
    def normalize(k,v):
        return Mono(k.rows,k.offset,k.alpha,k.quad),rotate(v,k.constant,k.global_phase)
    M=[[{I:one} if i==j else {} for j in range(banks)] for i in range(banks)]
    for e in events:
        if e['kind']=='ADD':
            d,s=e['dst'],e['src'];c=Fraction(e['coefficient'])
            for j in range(banks):
                row=dict(M[d][j])
                for k,v in M[s][j].items():row[k]=tuple(a+c*b for a,b in zip(row.get(k,zero),v))
                M[d][j]={k:v for k,v in row.items() if any(v)}
        elif e['kind']=='SCALE':
            i=e['bank'];c=Fraction(e['coefficient']);need(c!=0,'invertible scalar bank scaling');M[i]=[{k:tuple(c*x for x in v)for k,v in entry.items()}for entry in M[i]]
        elif e['kind']=='BANK_SWAP':i,j=e['banks'];M[i],M[j]=M[j],M[i]
        else:
            g=decode(e,n);i=e['bank'];M[i]=[dict(normalize(g@k,v) for k,v in entry.items()) for entry in M[i]]
    return M

def controls():
    n=6;I=identity(n);v=sum(1<<j for j in(0,1,2,4));R=Mono(tuple((1<<i)^(v if v>>i&1 else 0)for i in range(n)),0,(0,)*n,(0,)*n)
    alpha=(3,1,0,0,0,0);N=Mono(I.rows,3,alpha,(0,)*n,0,1)
    need(R@R==I and N@N==Mono(I.rows,0,(0,)*n,(0,)*n,0,2),'literal reflection and native square')
    A=N@R@N.inv();need(rank(A.polar())==2,'independent conjugated reflection rank')
    for a in (R,N,A,N@R):
        need(a@a.inv()==I==a.inv()@a,'both literal inverses')
        for b in (R,N,A):
            c=a@b
            for x in range(1<<n):need(c.act(x)==a.act(b.act(x)) and c.q(x)==(b.q(x)+a.q(b.act(x)))%4,'complete exact one-bit monomial composition')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path);p.add_argument('--beam',type=int,default=256);p.add_argument('--heuristic-weight',type=int,default=1);p.add_argument('--future-hint',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args();controls()
    if a.source is None:print('PASS_EXACT_QUADRATIC_CHART_ALGEBRA');return
    raw=a.source.read_bytes();src=json.loads(raw);events=src['events'];banks=src.get('width',src.get('banks'));n=src['ambient_arity']
    choices,mass,sizes=search(events,banks,n,a.beam,a.heuristic_weight,a.future_hint);out=compile_word(events,banks,n,choices)
    need(replay(events,banks,n)==replay(out,banks,n),'all independent input columns preserved exactly for every f')
    need(sum(e.get('rank_per_f',0)for e in out)==mass,'complete screened rank invoice')
    result=dict(status='PASS_EXACT_QUADRATIC_CHART_RETIMING',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_path=str(a.source),source_sha256=hashlib.sha256(raw).hexdigest(),beam=a.beam,heuristic_weight=a.heuristic_weight,future_hint=a.future_hint,width=banks,ambient_arity=n,native_rank_mass=mass,stock=n*banks,choices=choices,beam_sizes=sizes,events=out,limits=['Bounded search is not an optimality proof.','Rank-based child costs require explicit selected-native lowering and all-f adapters, including contracting splits of large-rank phases, before admission.','No precision, owner, COPY, tape or joint BIT contract is discharged.'])
    path=HERE/('QUADRATIC-'+a.source.stem+'-'+str(a.beam)+'-H'+str(a.heuristic_weight)+('-F'if a.future_hint else '')+'.json');result=json.loads(json.dumps(result))
    if a.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(path.read_bytes())==result,'saved exact retiming differs')
    print(result['status'],'mass',mass,'stock',n*banks)
if __name__=='__main__':main()
