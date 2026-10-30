#!/usr/bin/env python3
"""Independent H6 localized Smith and literal-row-completion review.

No producer import. All harmonic/mixed/radial polynomial actions are
rederived from degree<=6 shell moments; small feature minors use the
producer's explicit row set as certificate data only.
Substantial OpenAI Codex assistance. No physical compiler or kappa claim.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from math import factorial, prod
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE
REPO=HERE.parents[1]
PIN='20ecf2891d80b5acf18d980b2164fb44ea7faa90'


def need(ok,message):
    if not ok: raise ValueError(message)


def signed_shells():
    roots=[]
    for i,j in combinations(range(8),2):
        for a,b in product((-2,2),repeat=2):
            x=[0]*8;x[i]=a;x[j]=b;roots.append(tuple(x))
    roots += [x for x in product((-1,1),repeat=8) if sum(x)%4==0]
    fourth=[]
    for i in range(8):
        for a in (-4,4):
            x=[0]*8;x[i]=a;fourth.append(tuple(x))
    for inds in combinations(range(8),4):
        for signs in product((-2,2),repeat=4):
            x=[0]*8
            for i,a in zip(inds,signs): x[i]=a
            fourth.append(tuple(x))
    for i in range(8):
        for signs in product((-1,1),repeat=8):
            x=list(signs);x[i]*=3
            if sum(x)%4==0: fourth.append(tuple(x))
    need(len(roots)==len(set(roots))==240,'full root shell')
    need(len(fourth)==len(set(fourth))==2160,'full norm-four shell')
    need(all(sum(a*a for a in x)==8 for x in roots),'doubled root norms')
    need(all(sum(a*a for a in x)==16 for x in fourth),'doubled norm-four norms')
    return sorted(roots),sorted(fourth)


@lru_cache(None)
def spherical(indices,fourth=False):
    counts=Counter(indices)
    if any(n%2 for n in counts.values()): return 0
    degree=len(indices);radius2=16 if fourth else 8;number=2160 if fourth else 240
    wick=prod(prod(range(1,n,2)) for n in counts.values())
    out=F(number*radius2**(degree//2)*wick,
          prod(8+2*j for j in range(degree//2)))
    need(out.denominator==1,'integer shell moment')
    return out.numerator


@lru_cache(None)
def h6_moment(indices):
    # All products in this audit have even total degree<=6. Their canonical
    # shell sum is half the full simultaneous-antipodal sum.
    a=tuple(i for i in indices if i<8)
    b=tuple(i-8 for i in indices if i>=8)
    n=spherical(a)*spherical(b)
    if not b: n+=spherical(a,True)
    if not a: n+=spherical(b,True)
    need(n%2==0,'canonical half-shell moment integrality')
    return n//2


TRIPLES=list(combinations_with_replacement(range(16),3))
MULTI={t:6//prod(factorial(n) for n in Counter(t).values()) for t in TRIPLES}


def add(poly,monomial,coefficient):
    t=tuple(sorted(monomial));poly[t]=poly.get(t,0)+coefficient
    if not poly[t]: del poly[t]


def action(poly):
    # 3072*K(p,z)=(p.z)^3-64*(p.z), in doubled coordinates.
    cubic={t:MULTI[t]*sum(c*h6_moment(tuple(sorted(t+s)))
                          for s,c in poly.items()) for t in TRIPLES}
    linear={i:-64*sum(c*h6_moment(tuple(sorted((i,)+s)))
                     for s,c in poly.items()) for i in range(16)}
    return {t:c for t,c in cubic.items() if c},{i:c for i,c in linear.items() if c}


def harmonic_polynomial(t,offset):
    p={};add(p,tuple(i+offset for i in t),10)
    counts=Counter(t)
    if len(counts)==1: trace=t[0];scale=3
    elif len(counts)==2: trace=next(i for i,n in counts.items() if n==1);scale=1
    else: return p
    for j in range(8): add(p,(j+offset,j+offset,trace+offset),-scale)
    return p


def check_actions():
    harmonic=[];mixed=[]
    for offset in (0,8):
        for t in combinations_with_replacement(range(8),3):
            p=harmonic_polynomial(t,offset);a,b=action(p)
            need(not b and a=={t:3072*39*c for t,c in p.items()},
                 'all harmonic polynomial coefficient actions')
            harmonic.append(p)
        for i in range(8):
            for j,k in combinations(range(8),2):
                mixed.append({tuple(sorted((i+offset,j+8-offset,k+8-offset))):1})
            for j in range(7):
                p={};add(p,(i+offset,j+8-offset,j+8-offset),1)
                add(p,(i+offset,15-offset,15-offset),-1);mixed.append(p)
    for p in mixed:
        a,b=action(p)
        need(not b and a=={t:3072*45*c for t,c in p.items()},
             'all mixed polynomial coefficient actions')
    M=((9,-240),(-18,-195))
    for offset in (0,8):
        for i in range(8):
            # Both columns are twice the same-scale indicator basis8R:
            # 2F1=x_i*(r_x^2-r_y^2),2F2=2*x_i*r_y^2 on norm16.
            fs=[{},{}]
            for j in range(8):
                add(fs[0],(i+offset,j+offset,j+offset),1)
                add(fs[0],(i+offset,j+8-offset,j+8-offset),-1)
                add(fs[1],(i+offset,j+8-offset,j+8-offset),2)
            for col,p in enumerate(fs):
                a,b=action(p);hom={t:16*c for t,c in a.items()}
                for j,c in b.items():
                    for k in range(16): add(hom,(j,k,k),c)
                expected={}
                for row,f in enumerate(fs):
                    for t,c in f.items(): add(expected,t,16*3072*M[row][col]*c)
                need(hom==expected,'all radial actions on actual norm16 shell')
    return harmonic,mixed,M


def rank_and_det(matrix,p):
    a=[[x%p for x in row] for row in matrix]
    rows=len(a);cols=len(a[0]);r=0;det=1
    for j in range(cols):
        q=next((i for i in range(r,rows) if a[i][j]),None)
        if q is None: continue
        if q!=r: a[r],a[q]=a[q],a[r];det=-det
        v=a[r][j];det=det*v%p;iv=pow(v,-1,p)
        a[r]=[(x*iv)%p for x in a[r]]
        for i in range(r+1,rows):
            v=a[i][j]
            if v: a[i]=[(x-v*y)%p for x,y in zip(a[i],a[r])]
        r+=1
        if r==rows: break
    return r,det%p if r==rows==cols else None


def value(poly,x):
    return sum(c*prod(x[i] for i in t) for t,c in poly.items())


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--producer',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();roots,fourth=signed_shells()
    checks=0
    for shell,isfourth in ((roots,False),(fourth,True)):
        for powers in ((2,),(4,),(2,2),(6,),(4,2),(2,2,2)):
            inds=tuple(i for i,p in enumerate(powers) for _ in range(p))
            need(sum(prod(x[i] for i in inds) for x in shell)==spherical(inds,isfourth),
                 'independent full-shell moment representatives')
            checks+=1
    harmonic,mixed,M=check_actions()
    canonical=[x for x in roots if next(t for t in x if t)>0]
    claimed=json.loads(args.producer.read_bytes())
    cert=claimed['physical_row_certificate'];pairs=[tuple(x) for x in cert['root_pairs']]
    need(len(pairs)==len(set(pairs))==280 and set(pairs)=={(b,a) for a,b in pairs},
         'same literal symmetric280 root pairs')
    need(all((i,i) in pairs for i in range(120)),'all physical diagonal pairs included')
    Q=lambda x:[x[i]*x[j] for i,j in combinations(range(8),2)]+[x[i]**2-x[7]**2 for i in range(7)]
    z=[[a*b for a in canonical[i] for b in Q(canonical[j])] for i,j in pairs]
    mr,md=rank_and_det(z,11);need(mr==280 and md==6,'independent mixed mod11 minor')
    h=[[value(p,x+(0,)*8) for p in harmonic[:120]] for x in canonical]
    hr,_=rank_and_det(h,19);need(hr==112,'independent harmonic mod19 rank')
    lr,_=rank_and_det(canonical,23);need(lr==8,'independent linear mod23 rank')
    need([sum(M[i][j]*(1,10)[j] for j in range(2))%23 for i in range(2)]==[1,10],
         'radial eigenvector orientation')
    physical=sorted(2160+240*i+2*j+s for i,j in pairs for s in (0,1))
    need(physical==cert['physical_rows'] and len(set(physical))==560,'all560 literal row IDs')
    # The exact characteristic/annihilator identities are inherited from the
    # byte-pinned source; new sector identities above do not use projectors.
    factors=((0,30144),(39,224),(45,560))
    radical=lambda x:x*x+186*x-6075
    nullities={11:560,19:224,23:16}
    derivative_at_one=(1-39)*(1-45)*radical(1)+(1)*(1-45)*radical(1)+(1)*(1-39)*radical(1)+(1)*(1-39)*(1-45)*188
    for p,n in nullities.items():
        need(derivative_at_one%p!=0,'simple eigenvalue1 in reduced annihilator')
        algebraic=sum(m for l,m in factors if (1-l)%p==0)+(16 if radical(1)%p==0 else 0)
        need(algebraic==n,'reduced characteristic multiplicity')
    smith=((1,30400),(11,336),(209,208),(4807,16))
    need(sum(n for d,n in smith)==30960,'Smith dimension')
    for p,n in nullities.items(): need(sum(k for d,k in smith if d%p==0)==n,'all elementary valuations1')
    need(224+2*560+8*16==1472 and -radical(1)==2**8*23,'exact determinant valuations')
    control=z[:];control[-1]=control[0]
    need(rank_and_det(control,11)[0]<280,'duplicate selected mixed row control')
    raw=[[prod(x[i] for i in t) for t in combinations_with_replacement(range(8),3)] for x in canonical]
    need(rank_and_det(raw,19)[0]==120,'unprojected cubics control')
    need([sum(M[i][j]*(1,9)[j] for j in range(2))%23 for i in range(2)]!=[1,9],
         'wrong radial eigenvector control')
    sources={}
    for path in ('research/h6-independent-audit/spectral/results.json',
                 'research/h6-independent-audit/spectral/README.md',
                 'research/niemeier-lattices/code/e8_cubed.py'):
        data=(REPO/path).read_bytes()
        sources[path]=sha256(data).hexdigest()
    receipt={'status':'PASS_INDEPENDENT_H6_SMITH_AND560_ROW_PRIMITIVITY_NO_COMPILER',
             'source_pin':PIN,'source_sha256':sources,
             'producer_source_sha256':sha256((HERE/'derive.py').read_bytes()).hexdigest(),
             'certificate_data_sha256':sha256(args.producer.read_bytes()).hexdigest(),
             'full_shell_moment_representatives':checks,'all_harmonic_polynomial_actions':240,
             'all_mixed_polynomial_actions':560,'all_radial_polynomial_actions':32,
             'coefficient_rows_per_cubic_identity':816,'moment_identity_ring':'Z[1/30], safe at11/19/23',
             'mixed_mod11_rank_and_det':[mr,md],'harmonic_mod19_rank':hr,'radial_mod23_rank':lr,
             'physical_rows':physical,'localized_smith':smith,'prime_nullities':nullities,
             'negative_controls':['duplicate selected mixed row','unprojected cubics','wrong radial eigenvector'],
             'limits':['complete characteristic polynomial inherited from pinned exact spectrum/moment proof',
                       'all-coordinate sector eigenidentities independently rederived, not rational projector reduction',
                       'literal560 rows give abstract dyadic unimodular completion; no completion coefficients or paid circuit',
                       'stable560 auxiliary completion changes helper outputs and permits helper dirt in data',
                       'restored-helper exact(Cx,h) map impossible over dyadic unimodular model',
                       'no physical transport, rounding precision, owner/controller or kappa admission']}
    args.out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(receipt['status'])


if __name__=='__main__': main()
