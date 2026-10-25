#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Chris R / Clear1nsight, with substantial OpenAI Codex assistance.
"""Exact local-ring source binding, orbit control and fixed-profile arithmetic."""
from collections import deque
from fractions import Fraction as F
import gzip, hashlib, itertools, json
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok: raise ValueError(msg)

def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def eye(n): return [[int(i==j) for j in range(n)] for i in range(n)]
def mm(a,b,M):
    out=[[0]*len(b[0]) for _ in a]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]=(out[i][j]+x*y)%M
    return out
def inv(a,M):
    from math import gcd
    n=len(a);w=[row[:]+e for row,e in zip(a,eye(n))]
    for j in range(n):
        p=next((i for i in range(j,n) if gcd(w[i][j],M)==1),None)
        need(p is not None,'unit basis pivot')
        w[j],w[p]=w[p],w[j];u=pow(w[j][j],-1,M)
        w[j]=[u*x%M for x in w[j]]
        for i in range(n):
            if i!=j:
                u=w[i][j];w[i]=[(x-u*y)%M for x,y in zip(w[i],w[j])]
    return [row[n:] for row in w]

def projector(rows):
    a=[[F(x) for x in row] for row in rows];n=len(a[0]);k=0;piv=[]
    for j in range(n):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None: continue
        a[k],a[p]=a[p],a[k];u=a[k][j];a[k]=[x/u for x in a[k]]
        for i in range(len(a)):
            if i!=k:
                u=a[i][j];a[i]=[x-u*y for x,y in zip(a[i],a[k])]
        piv.append(j);k+=1
    free=[j for j in range(n) if j not in piv]
    need(k==7 and len(free)==1,'actual rank7 hyperplane')
    z=[F(j==free[0]) for j in range(n)]
    for i,j in enumerate(piv):z[j]=-a[i][free[0]]
    norm=sum(x*x for x in z)
    return [[F(i==j)-z[i]*z[j]/norm for j in range(n)] for i in range(n)]

def authenticate():
    s=json.loads((HERE/'SOURCES.json').read_text())
    for r in s['retained']:
        p=HERE/r['path'];need(p.is_file() and not p.is_symlink(),'missing/linked retained source')
        b=p.read_bytes()
        need(hashlib.sha256(b).hexdigest()==r['sha256'],'retained SHA256 '+r['path'])
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'retained Git blob')
    return json.loads(gzip.decompress((HERE/'inputs/r437-word.json.gz').read_bytes()))

def source_conjugacies(word):
    cur=word['start'][:]
    for sec in ['D','A']:
        for frame,target,sources in word[sec]:
            for role in [target]+sources:cur[role]=frame
    need(word['ret']==list(range(470,479)),'actual nine captures')
    need([cur[i] for i in word['ret']]==list(range(510,519)),'actual capture frames')
    hashes=[]
    for capture in word['ret']:
        p=projector([word['lines'][i] for i in word['frames'][cur[capture]]])
        for prime,w in [(3,1),(3,2),(5,2),(17,2)]:
            M=prime**w;P=[[x.numerator*pow(x.denominator,-1,M)%M for x in row] for row in p]
            need(mm(P,P,M)==P,'source idempotence over local ring')
            # Pick seven image columns and one complementary kernel column.
            T=None
            for cols in itertools.combinations(range(8),7):
                for k in range(8):
                    cand=[[P[i][j] for j in cols]+[(int(i==k)-P[i][k])%M] for i in range(8)]
                    try:Ti=inv(cand,M)
                    except ValueError:continue
                    T=cand;break
                if T is not None:break
            need(T is not None,'split basis found')
            E=[[int(i==j and i<7) for j in range(8)] for i in range(8)]
            need(mm(mm(T,E,M),Ti,M)==P,'actual capture split basis')
            # g=S diag(T^-1,I56), conjugating the actual embedded capture to last7.
            bigP=[[P[i][j] if i<8 and j<8 else 0 for j in range(64)] for i in range(64)]
            G=eye(64)
            for i in range(8):G[i][:8]=Ti[i]
            for i in range(7):G[i],G[57+i]=G[57+i],G[i]
            Q=mm(mm(G,bigP,M),inv(G,M),M)
            want=[[int(i==j and i>=57) for j in range(64)] for i in range(64)]
            need(Q==want,'actual GL64 class reaches shifted projector')
            hashes.append(hashlib.sha256(canonical([capture,M,G])).hexdigest())
    return dict(captures=9,local_ring_cases=len(hashes),conjugacy_digest=hashlib.sha256(canonical(hashes)).hexdigest())

def lead(x):return next((i for i,a in enumerate(x) if a),len(x))
def swap_outer(x,k):
    y=list(x);N=len(x)
    for i in range(k):y[i],y[N-1-i]=y[N-1-i],y[i]
    return tuple(y)
def closure(seeds,M):
    seen=set(seeds);queue=deque(seeds)
    while queue:
        x=queue.popleft()
        for i in range(len(x)):
            for j in range(i):
                if not x[j]:continue
                y=list(x);y[i]=(y[i]+x[j])%M;y=tuple(y)
                if y not in seen:seen.add(y);queue.append(y)
    return seen

def orbit_checks():
    rows=[]
    for m,M in [(2,3),(2,9),(3,3)]:
        x=tuple(int(i==m) for i in range(2*m));y=tuple(int(i==m-1) for i in range(2*m))
        pre=closure([x],M)
        for k in range(1,m):
            one=closure([swap_outer(z,k) for z in pre],M)|pre
            need(y not in one,'one-child orbit misses required input')
            need(all(lead(z)<k or lead(z)==m for z in one),'whole reachable support leading flag')
            need(all(lead(tuple(a*t%M for a in y))==m-1 and tuple(a*t%M for a in y) not in one
                     for t in range(1,M) if __import__('math').gcd(t,M)==1),'every unit ancestor weight')
            two=closure([swap_outer(z,k) for z in one],M)|one
            need(y in two,'extra-child premise control exposes missing dependency')
            need(swap_outer(x,m)==y,'full-width premise control')
            # High-lift nonunit off-leading values are included in complete closures.
            rows.append(dict(m=m,modulus=M,k=k,pre=len(pre),one=len(one),two=len(two),missing=list(y)))
    return rows

def payload_control():
    # A concrete nonlinear dirty echo is tested on the complete 3^4 address cube.
    M=3;N=4;xs=list(itertools.product(range(M),repeat=N));idx={x:i for i,x in enumerate(xs)}
    x=(0,0,1,0);y=(0,2,0,0);j=idx[x]
    # Q=diag(0,1), H=diag(1,2), reflected physical tail.
    target=lambda z:(z[0],2*z[2]%M,pow(2,-1,M)*z[1]%M,z[3])
    need(target(x)==y and target(target(x))==x,'weighted target pullback orientation')
    zero=[0]*len(xs);delta=[int(z==y) for z in xs]
    helpers=[[((i*17+seed*13)%11)<5 for i in range(len(xs))] for seed in range(3)]
    def run(source):
        source=source[:];saved=source[:];h=[a[:] for a in helpers];private=source[:]
        def pull(f):
            nonlocal private
            private=[private[idx[f(z)]] for z in xs]
        # Pointwise nonlinear Boolean gates: helper bits are read-only and dirty.
        private=[a ^ (b and c) for a,b,c in zip(private,h[0],h[1])]
        pull(lambda z:(z[0],(z[1]+2*z[0])%M,z[2],(z[3]+z[2])%M))
        pull(lambda z:swap_outer(z,1))
        private=[a ^ b for a,b in zip(private,h[2])]
        pull(lambda z:(z[0],z[1],(z[2]+z[0])%M,(z[3]+2*z[1])%M))
        need(source==saved and h==helpers,'borrowed source and arbitrary helpers unchanged')
        return private
    a,b=run(zero),run(delta)
    need(a[j]==b[j],'one-child dirty Boolean echo cannot distinguish witness source bit')
    need(zero[idx[y]]!=delta[idx[y]],'required weighted COPY does distinguish it')
    need(delta[idx[y]]!=delta[idx[(0,1,0,0)]],'dropped ancestor unit changes target bit')
    return dict(addresses=len(xs),dirty_helpers=3,output_address=list(x),required_input=list(y),observed_difference=0,required_difference=1)

def budget(word):
    e=json.loads((HERE/'inputs/r437-EXPECTED.json').read_text())
    cat=json.loads((HERE/'inputs/pr3967-CATALOGUE.json').read_text())
    profile={int(k):v for k,v in e['profile'].items()};W=e['live'];m=64
    copies=len(word['ret'])*9*32
    need(copies==cat['literal_opcode_counts']['2']==cat['literal_opcode_counts']['3']==2592,'source-bound COPY and disposal census')
    mass=sum(r*n for r,n in profile.items());need(mass==e['rank_mass']==1808352,'exact source rank mass')
    need(W*m-mass==e['deficit']==10272,'exact source deficit')
    newmass=mass+copies*7;need(newmass>m*W,'fixed two-rank7 optimistic gate fails')
    c=F(e['BIT_c']);a=F(17,10000)
    gaps=[c-a*(1-a),c-a*(1-a*a)]
    need(all(g>0 for g in gaps),'both available upper-tariff gaps positive')
    return dict(profile=e['profile'],W=W,copies=copies,readers_each=63,old_mass=mass,new_mass=newmass,
        deficit=m*W-mass,extra_mass=copies*7,excess=newmass-m*W,moment_zero=str(F(newmass,m*W)),
        adaptive_fraction_zero_necessary=str(F(m*W-mass,copies*7)),tariff_gaps=list(map(str,gaps)),
        scope='fixed two rank7 children per COPY only; not an adaptive or mixed-width impossibility')

def evaluate():
    w=authenticate()
    return dict(source=source_conjugacies(w),orbits=orbit_checks(),payload=payload_control(),budget=budget(w),new_kappa=False)

def main():
    got=evaluate();want=json.loads((HERE/'RESULT.json').read_text())
    need(got==want,'committed exact result differs')
    print('PASS_COPY_ECHO_BUDGET capture_conjugacies=36 one_child_orbits=4 dirty_boolean_payload=81 fixed_two_child_excess=7872 no_new_kappa')
if __name__=='__main__':main()
