#!/usr/bin/env python3
"""Finite three-call rolling search with distinct actual-code stage labels.

Only universal free-product identities are accepted. Negative output is a
bounded search result, not an actual-C511 or all-word obstruction.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import itertools
import json
import time

HERE=Path(__file__).resolve().parent

def word(a,b):
    x=list(a)
    for c in b:
        same=x and ((x[-1]==0 and c==0)or(x[-1]!=0 and c!=0 and(x[-1]-1)//510==(c-1)//510))
        if same:
            d=x.pop()
            if c:
                k=((c-1)%510+1+(d-1)%510+1)%511
                if k:x.append(((c-1)//510)*510+k)
        else:x.append(c)
    return tuple(x)

def add(a,b):return a^b
def mul(a,b):
    r=set()
    for x in a:
        for y in b:
            z=word(x,y)
            if z in r:r.remove(z)
            else:r.add(z)
    return frozenset(r)

Z=frozenset();I=frozenset([()]);N=frozenset([(0,)])
ID=(I,Z,Z,I)
def c(i,e=1):return frozenset([(i*510+e%511,)])if e%511 else I
def mm(A,B):return tuple(add(mul(A[2*i],B[j]),mul(A[2*i+1],B[j+2]))for i in range(2)for j in range(2))
def ng(p):return mul(N,mul(p,N))
def free(A):return all(all(0 not in w for w in p)for p in A)
def good(A):return free(tuple(mul(N,p)for p in A))
def flip(A):return A[3],A[2],A[1],A[0]
def show(A):return [[list(map(list,sorted(A[2*i+j])))for j in range(2)]for i in range(2)]

def library(cut,depth):
    gens=[('U(1)',(I,I,Z,I)),('L(1)',(I,Z,I,I))]
    for i in range(3):
        for e in [1,510]:
            p=c(i,e);p=ng(p)if i<cut else p
            lab=('a'if i<cut else 'C')+str(i)+('^-1'if e==510 else '')
            gens.extend([(f'U({lab}+1)',(I,add(p,I),Z,I)),(f'L({lab}+1)',(I,Z,add(p,I),I)),
                         (f'D0({lab})',(p,Z,Z,I)),(f'D1({lab})',(I,Z,Z,p))])
    gates={ID:()};front=[ID]
    for d in range(depth):
        nxt=[]
        for a in front:
            for lab,g in gens:
                b=mm(g,a)
                if b not in gates:gates[b]=gates[a]+(lab,);nxt.append(b)
        front=nxt
    return gates

def run(depth,write):
    t=time.monotonic();g1=library(1,depth);g2=library(2,depth)
    census=[];finds=[]
    for directions in itertools.product(['forward','inverse'],repeat=3):
        calls=[]
        for i,d in enumerate(directions):
            A=(ng(c(i)),Z,mul(c(i),N),I)if d=='forward'else(c(i,510),Z,N,I)
            calls.append(flip(A)if i==1 else A)
        right=[(mm(calls[1],mm(g,calls[0])),lab)for g,lab in g1.items()]
        left=[(mm(calls[2],g),lab)for g,lab in g2.items()]
        found=None;tried=0
        for a,la in right:
            for b,lb in left:
                r=mm(b,a);tried+=1
                if good(r):
                    found={'directions':directions,'cut1':la,'cut2':lb,'residual':show(r),
                           'terminal_free_code':show(tuple(mul(N,p)for p in r))};break
            if found:break
        census.append({'directions':directions,'pairs_tested':tried,'found':found is not None})
        print('case',','.join(directions),'pairs',tried,'found',found is not None,flush=True)
        if found:finds.append(found)
    out={'status':'PASS_BOUNDED_THREE_CODE_ROLLING_SEARCH','no_new_kappa':not bool(finds),
         'cut_gate_depth':depth,'cut1_gate_count':len(g1),'cut2_gate_count':len(g2),
         'census':census,'findings':finds,'ring':'Universal F2[C2*C511*C511*C511]',
         'native_premise':'Each actual C_i commutes every G_j,j!=i, and the full parent. The physical cut gate for stage i is C_i before i and a_i=N*C_i*N afterward.',
         'inputs':'Both public banks arbitrary. No zero target or restored source assumed.',
         'criterion':'N left-times the whole normalized residual is head/tail-separate, allowing a full-parent terminal free code inverse.',
         'limits':['Only three alternating F/B/F calls, the stated free gate library/depth and universal identities are searched.','The exact routed C_i may have further relations not represented by the free-product ring.','No all-word or caller impossibility follows from failure.'],
         'elapsed_seconds':round(time.monotonic()-t,3),'producer_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    if write:(HERE/f'MUTABLE-ROLLING-SEARCH-d{depth}.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'],'pairs',sum(x['pairs_tested']for x in census),'found',len(finds),'seconds',out['elapsed_seconds'],flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--depth',type=int,default=1);ap.add_argument('--write',action='store_true');a=ap.parse_args();run(a.depth,a.write)
