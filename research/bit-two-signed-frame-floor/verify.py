"""Source binding and elementary sign-reduction checks (standard library).

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
The mathematical dependencies are PR6111 and PR6079, not executed here.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
A, B, P, Q = ((F(1),F(0),F(0)), (F(0),F(1),F(0)),
              (F(1,2),F(1,2),F(1,2)), (F(1,2),F(1,2),F(-1,2)))
OLD = (A,B,P,Q)  # Physical entries (m11,m22,m12), independent of census basis.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(x,y):
    return tuple(a+b for a,b in zip(x,y))


def scale(c,x):
    return tuple(c*a for a in x)


def det(x):
    return x[0]*x[1]-x[2]*x[2]


def rank_one(c,x,y):
    return (c*x*x,c*y*y,c*x*y)


TARGETS = tuple(add(x,y) for x in (A,B) for y in (P,Q))


def bind_sources():
    manifest = json.loads((PACKAGE/'SOURCES.json').read_text())
    declared = set(json.loads((PACKAGE/'VERIFY.json').read_text())['inputs'])
    rows = [r for r in manifest['files'] if r['usage']=='input']
    require(len(rows)==2 and {r['path'] for r in rows}==declared, 'two theorem source pins')
    for row in rows:
        data = (ROOT/row['path']).read_bytes()
        require(sha256(data).hexdigest()==row['sha256'], 'changed theorem source: '+row['path'])
    return len(rows)


def elementary_counts():
    counts = Counter()
    for old in product(range(6),repeat=4):
        n=sum(old)
        if n>5:
            continue
        M=(F(4),F(4),F(0))
        for c,frame in zip(old,OLD):
            M=add(M,scale(-c,frame))
        d,e=old[0]-old[1],old[2]-old[3]
        require(4*det(M)==(8-n)**2-d*d-e*e,'residual determinant identity')
        require(M[0]+M[1]==8-n,'positive residual trace')
        multiplicities=sum(1 for r in range(1,8-n) for s in range(1,8-n-r))
        if det(M)>0:
            counts['definite']+=multiplicities
        elif det(M)<0:
            require(n==5 and abs(d)+abs(e)==5,'indefinite two-direction reduction')
            require(not(old[0] and old[1]) and not(old[2] and old[3]),'no opposite old directions')
            E=OLD[0 if old[0] else 1]
            G=OLD[2 if old[2] else 3]
            # Solve ell(E)=ell(G)=0, ell(I)=1 in physical coordinates.
            c11=F(0) if E==A else F(1)
            c22=1-c11
            c12=-F(1,2)/G[2]
            ell=lambda x:c11*x[0]+c22*x[1]+c12*x[2]
            require(ell(E)==ell(G)==0 and ell(add(A,B))==1,'projected-support functional')
            require(sorted(ell(t) for t in TARGETS)==[0,1,1,2],'projected targets')
            for rho in (F(1),F(3)):
                require(F(2) not in {F(0),rho,4-rho,F(4)},'all possible rho admitting one')
            counts['indefinite']+=multiplicities
        else:
            matched=False
            for i,E in enumerate(OLD):
                perpendicular=i^1
                other=(2,3) if i<2 else (0,1)
                patterns=[]
                for kind in range(3):
                    c=[0]*4
                    c[i]=4 if kind<2 else 3
                    if kind==1:c[perpendicular]=1
                    if kind==2:
                        c[other[0]]=c[other[1]]=1
                    patterns.append(tuple(c))
                if old not in patterns:
                    continue
                require(not matched,'unique singular profile classification')
                matched=True
                character=(lambda x:2*x[2]) if i<2 else (lambda x:x[0]-x[1])
                require(character(E)==character(OLD[perpendicular])==0,'kill whole added line')
                require(all(abs(character(t))==1 for t in TARGETS),'four detected targets')
                if old==patterns[2]:
                    require(sum(c for c,x in zip(old,OLD) if character(x))==2,'two detected calls')
                    counts['singular_character']+=multiplicities
                else:
                    require(all(character(x)==0 for c,x in zip(old,OLD) if c),'span control')
                    counts['singular_span']+=multiplicities
            require(matched,'unclassified singular profile')
    require(dict(counts)=={'definite':422,'indefinite':20,'singular_span':16,'singular_character':4},
            'complete elementary partition')
    return dict(counts)


def geometry_controls():
    checked=0
    vectors=((1,0),(0,1),(1,1),(1,-1),(1,2),(2,-3))
    for u,v,c,t in product(vectors,vectors,(F(-2),F(-1,3),F(2,5),F(3)),(F(-3),F(-1,5),F(1,2),F(4))):
        X=rank_one(c,*u);Y=rank_one(t,*v);M=add(X,Y)
        require(det(M)==c*t*(u[0]*v[1]-u[1]*v[0])**2,'rank-one sum determinant')
        if det(M)>0 and M[0]+M[1]>0:
            require(c>0 and t>0,'positive-definite sum forces signs')
        if det(M)==0:
            require(u[0]*v[1]==u[1]*v[0],'singular sum forces common line')
        checked+=1
    # Three summands do not obey the two-summand sign lemma.
    require(add(add(scale(-1,A),scale(2,A)),B)==add(A,B),'three-frame boundary')
    return checked


def main():
    sources=bind_sources()
    partition=elementary_counts()
    geometry=geometry_controls()
    path=PACKAGE/'independent.py'
    namespace={'__name__':'independent_signed_support'}
    # Execute current local source, never a stale .pyc.
    exec(compile(path.read_bytes(),str(path),'exec'),namespace)
    result=namespace['run']()
    require(result['profiles']==sum(partition.values()),'independent total agrees')
    print('PASS_TWO_SIGNED_FRAME_REDUCTION '+json.dumps({
        'sources':sources,'partition':partition,'rank_one_sum_controls':geometry,
        'three_frame_boundary':1,'scope':'signed reduction; positive theorem inherited; no new kappa'},sort_keys=True))


if __name__=='__main__':
    main()
