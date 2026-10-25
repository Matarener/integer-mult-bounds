#!/usr/bin/env python3
"""Separate symbolic/physical check; imports no primary or predecessor code."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[1]

def require(x, why):
    if not x:
        raise ValueError(why)

def norm(word):
    word=list(word)
    changed=True
    while changed:
        changed=False
        for i in range(len(word)-1):
            a,b=word[i:i+2]
            if (a,b) in [('D','d'),('d','D'),('T','t'),('t','T')]:
                word[i:i+2]=[]; changed=True; break
            if (a,b)==('H','H'):
                word[i:i+2]=['H'];changed=True;break
            if a in ('T','t') and b=='H':
                word[i:i+2]=['H',a];changed=True;break
            if a in ('D','d','H','T','t') and b=='F':
                word[i:i+2]=['F',a];changed=True;break
    return tuple(word)

def plus(*xs):
    out=Counter()
    for x in xs:
        for k,v in x.items():
            out[k]+=v
    return {k:v for k,v in out.items() if v}

def times(a,b):
    out=Counter()
    for k,v in a.items():
        for l,w in b.items():
            out[norm(k+l)]+=v*w
    return {k:v for k,v in out.items() if v}

def scale(a,k):
    return {w:k*v for w,v in a.items() if k*v}

def mm(a,b):
    return [[plus(*(times(a[i][k],b[k][j]) for k in range(2))) for j in range(2)] for i in range(2)]

def atom(*w):
    return {tuple(w):1}

def algebra():
    one,zero=atom(),{}
    D,d,H,T,t=(atom(v) for v in ['D','d','H','T','t'])
    ht=times(H,T)
    e=[[D,ht],[zero,one]]
    ei=[[d,scale(times(d,ht),-1)],[zero,one]]
    p=[[one,zero],[t,one]]
    require(mm(e,ei)==[[one,zero],[zero,one]],'symbolic inverse')
    hd=times(H,d)
    want=[[plus(one,hd),scale(times(hd,ht),-1)],
          [times(t,d),plus(one,scale(times(times(t,d),ht),-1))]]
    require(mm(mm(e,p),ei)==want,'noncommutative physical correction')
    e0=[[D,H],[zero,one]]
    ei0=[[d,scale(times(d,H),-1)],[zero,one]]
    shear=[[one,scale(one,-1)],[zero,one]]
    require(mm(mm(e0,shear),ei0)==[[one,scale(D,-1)],[zero,one]],'encoded inverse shear')
    F=atom('F')
    common=[[F,zero],[zero,F]]
    require(mm(e0,common)==mm(common,e0),'completed common-axis positive control')
    forward=[[one,zero],[one,one]]
    entrance=[[t,zero],[zero,one]]
    G=[[F,zero],[zero,times(F,t)]]
    physical=mm(mm(mm(G,shear),forward),entrance)
    require(physical==[[zero,scale(F,-1)],[atom('F','t','t'),atom('F','t')]],'retained physical endpoint')
    require(mm(p,physical)==[[zero,scale(F,-1)],[atom('F','t','t'),zero]],'paid endpoint correction')
    comm=[[scale(H,-1),zero],[times(t,plus(D,scale(one,-1))),H]]
    diff=[[plus(mm(p,e)[i][j],scale(mm(e,p)[i][j],-1)) for j in range(2)] for i in range(2)]
    require(diff==comm,'blind correction defect')
    J0=plus(one,scale(H,-1))
    Pi=[[J0,H],[H,J0]]
    require(mm(Pi,Pi)==[[one,zero],[zero,one]],'literal slot permutation')
    actual=mm(Pi,e)
    actual_inverse=mm(ei,Pi)
    require(mm(mm(actual,p),actual_inverse)==mm(mm(Pi,want),Pi),'literal encoded correction')
    actual_defect=[[scale(times(H,t),-1),zero],
                   [plus(times(times(t,J0),plus(D,scale(one,-1))),scale(H,-1)),times(t,H)]]
    defect=[[plus(mm(p,actual)[i][j],scale(mm(actual,p)[i][j],-1)) for j in range(2)] for i in range(2)]
    require(defect==actual_defect,'literal slot blind-correction defect')
    # Nonzero Hd cannot be suppressed merely because it is a residual output.
    require(hd!=zero,'residual update control')
    return want

def rankq(a):
    a=[[Fraction(v) for v in row] for row in a]
    r=0
    for c in range(len(a[0])):
        i=next((i for i in range(r,len(a)) if a[i][c]),None)
        if i is None:
            continue
        a[r],a[i]=a[i],a[r]
        q=a[r][c];a[r]=[v/q for v in a[r]]
        for i in range(len(a)):
            if i!=r and a[i][c]:
                q=a[i][c];a[i]=[v-q*w for v,w in zip(a[i],a[r])]
        r+=1
    return r

def check():
    receipt=json.loads((P/'RESULT.json').read_text())
    require(type(receipt['schema_version']) is int and receipt['schema_version']==1,'typed receipt')
    sources=json.loads((P/'SOURCES.json').read_text())
    for x in sources['files']:
        if x['usage']=='input':
            require(hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256'],'input SHA')
    algebra()
    # Enumerate all 240 E8 roots, then quotient signs by first nonzero entry.
    rr=[]
    for i in range(8):
        for j in range(i+1,8):
            for s,t in itertools.product((-2,2),repeat=2):
                v=[0]*8;v[i]=s;v[j]=t;rr.append(tuple(v))
    rr += [v for v in itertools.product((-1,1),repeat=8) if sum(x<0 for x in v)%2==0]
    lines=sorted({v if next(x for x in v if x)>0 else tuple(-x for x in v) for v in rr})
    require(len(rr)==240 and len(lines)==120,'separate root enumeration')
    f=json.loads((R/'research/p104-native-channel/inputs/P104-FIXTURE.json').read_text())['section4_explicit_P104']
    removed=set(map(tuple,f['F0']+f['C']))
    ports=[v for v in lines if v not in removed]
    pivot=[0,1,3,6,22,31,93,103]
    order=pivot+[i for i in range(104) if i not in pivot]
    ports=[ports[i] for i in order]
    ip=lambda u,v:sum(a*b for a,b in zip(u,v))
    A=[[ip(u,v)//4 for v in ports] for u in ports]
    D=[[2*(i==j) if i<8 and j<8 else A[i][j]-2*(i==j) for j in range(104)] for i in range(104)]
    inv=[[-22*(i==j) if i<8 and j<8 else -2*(i==j) if i>=8 and j>=8 else A[i][j] for j in range(104)] for i in range(104)]
    require(rankq(D)==104 and rankq(inv[8:])==96,'independent rational ranks')
    labels=receipt['physical_labels']
    require(len(labels)==104 and len(set(labels))==104,'physical labels')
    require(all(((labels[i]&labels[j]).bit_count()%2)==((A[i][j]+1)%2) for i in range(104) for j in range(104)),'independent label Gram')
    commute=[]
    for z in range(512):
        signs=[(u&z).bit_count()%2 for u in labels]
        if all(not D[i][j] or signs[i]==signs[j] for i in range(104) for j in range(104)):
            commute.append(z)
    require(commute==[0,511],'all phase patterns')
    # Literal four-address translation matrices. 2*(C_u^-1-C_v^-1)
    # equals (1+i)*(X_u-X_v); its rank is two, with nonzero global phase.
    X=lambda u:[[int(i==(j^u)) for j in range(4)] for i in range(4)]
    xu,xv=X(1),X(2)
    diff=[[xu[i][j]-xv[i][j] for j in range(4)] for i in range(4)]
    require(rankq(diff)==2 and [diff[i][0] for i in range(4)]==[0,1,-1,0],'literal physical witness')
    weights=Counter((a.bit_count()*b.bit_count())%4 for a in labels for b in labels)
    require({str(k):v for k,v in weights.items()}==receipt['tensor_weights_mod_four'],'normalization phase census')
    require(weights[3]>0 and (9-3)%4==2,'fixed weight-nine phase counterexample')
    profile=Counter(e[4] for e in json.loads((R/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json').read_text())['program'] if e[0]=='transport')
    require(sum(k*v for k,v in profile.items())==2368,'inherited mass recount')
    # Recount occupied roles from explicit row/column owner names.
    data={(bank,i,j) for bank in ['X','Y'] for i in range(104) for j in range(104)}
    helper={(axis,fiber,h) for axis in [0,1] for fiber in range(104) for h in range(72)}
    W=len(data)+len(helper)
    progress=W*81-104**2
    bill=208*(2368+208)+progress-208*2312
    require((W,progress,bill,bill-W*81)==(36608,2954432,3009344,44096),'independent complete gate')
    require(receipt['gate']['lower_mass']==bill and receipt['gate']['excess']==44096,'gate receipt')
    print('PASS_SEPARATE_TWO_AXIS_SYMBOLIC physical_patterns=512 residual_rank=96 deficit=44096')

if __name__=='__main__':
    check()
