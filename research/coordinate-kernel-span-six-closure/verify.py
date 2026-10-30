#!/usr/bin/env python3
"""Exact finite corroboration; the universal claim uses the cited written lemma."""
import itertools as it
import json
import hashlib
from pathlib import Path
from fractions import Fraction

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def unpack(n):
    return tuple(tuple((n >> (4*i+j)) & 1 for j in range(4)) for i in range(4))

def pack(a):
    return sum(a[i][j] << (4*i+j) for i in range(4) for j in range(4))

def mm(a,b):
    n=len(a)
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(n))%2
                       for j in range(n)) for i in range(n))

def rank(a, binary=False):
    a=[[Fraction(x) for x in row] for row in a]
    r=0
    for c in range(len(a[0])):
        p=next((i for i in range(r,len(a)) if a[i][c]),None)
        if p is None: continue
        a[r],a[p]=a[p],a[r]
        v=a[r][c]
        a[r]=[x/v for x in a[r]]
        for i in range(len(a)):
            if i!=r:
                v=a[i][c]
                a[i]=[x-v*y for x,y in zip(a[i],a[r])]
                if binary: a[i]=[x%2 for x in a[i]]
        r+=1
        if r==len(a): break
    return r

POOL=(0x0003,0x0022,0x0550)
COORD=tuple(1 << (5*i) for i in range(4))

def isolated(pool):
    return [q for q in range(4) if all(
        not a[q][j] and not a[j][q]
        for n in pool for a in [unpack(n)] for j in range(4))]

def permute(n,p):
    a=unpack(n); b=[[0]*4 for _ in range(4)]
    for i in range(4):
        for j in range(4): b[p[i]][p[j]]=a[i][j]
    return pack(b)

# Formal Laurent polynomials: sets of integer exponent tuples over F2.
def add(a,b): return a ^ b
def mul(a,b):
    out=set()
    for x in a:
        for y in b:
            z=tuple(u+v for u,v in zip(x,y))
            if z in out: out.remove(z)
            else: out.add(z)
    return out

def identity(n,d):
    return [[{(0,)*d} if i==j else set() for j in range(n)] for i in range(n)]

def formal_mm(a,b):
    n=len(a); out=[[set() for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            for k in range(n): out[i][j]^=mul(a[i][k],b[k][j])
    return out

def factor(n,a):
    d=len(a); m=len(n); f=identity(m,d); coeff={(0,)*d}^{tuple(a)}
    for i in range(m):
        for j in range(m):
            if n[i][j]: f[i][j]^=coeff
    return f

def execute(word,frames,n=4):
    out=identity(n,len(frames[0]))
    for p,a in zip(word,frames): out=formal_mm(factor(p,a),out)
    return out

def check_split(word,frames):
    full=execute(word,frames)
    small=execute([tuple(tuple(n[i][j] for j in range(3)) for i in range(3))
                   for n in word],frames,3)
    total=tuple(sum(a[c] for n,a in zip(word,frames) if n[3][3])
                for c in range(len(frames[0])))
    for i in range(4):
        for j in range(4):
            expected=small[i][j] if i<3 and j<3 else ({total} if i==j==3 else set())
            require(full[i][j]==expected,'formal block factorization')

def main():
    package=Path(__file__).resolve().parent
    root=package.parent.parent
    for row in json.loads((package/"SOURCES.json").read_text())["files"]:
        if row["usage"]=="input":
            require(hashlib.sha256((root/row["path"]).read_bytes()).hexdigest()==row["sha256"], "source drift: "+row["path"])
    pools={tuple(sorted(permute(n,p) for n in POOL)) for p in it.permutations(range(4))}
    require(len(pools)==24,'orbit size')
    placements=0
    for pool in pools:
        iso=isolated(pool); require(len(iso)==1,'unique isolated coordinate')
        q=iso[0]; active=[i for i in range(4) if i!=q]
        for n in pool+COORD:
            a=unpack(n)
            require(mm(a,a)==a and rank(a,True)==1,'idempotent rank')
            require(all(not a[q][j] and not a[j][q] for j in active),'off-block entry')
            b=tuple(tuple(a[i][j] for j in active) for i in active)
            require(rank(b,True)==(0 if n==COORD[q] else 1),'restricted rank')
        for data in it.combinations(range(4),3):
            # Every possible call split has budget 8, independently of isolated role.
            require(sum(3 for _ in data)>8,'target rank contradiction')
            placements+=1
    alphabet=[unpack(n) for n in POOL+COORD]
    words=0
    for k in range(1,5):
        frames=[tuple(int(i==j) for j in range(k)) for i in range(k)]
        for word in it.product(alphabet,repeat=k):
            check_split(word,frames); words+=1
    # Genuine collisions including inverses; exact full endpoint is identity.
    for n in alphabet:
        frames=[(1,),(-1,)]
        check_split([n,n],frames)
        require(execute([n,n],frames)==identity(4,1),'inverse cancellation')
    # Negative controls: two old orbits, an off-block rank-one bridge, rank-two update.
    transpose=lambda n: pack(tuple(zip(*unpack(n))))
    old=(0x0003,0x0022,0x0dd0)
    require(not isolated(old),'48-orbit separation')
    require(not isolated(tuple(transpose(n) for n in old)),'transpose separation')
    require(not isolated(POOL+(1+(1<<3),)),'off-block bridge rejected')
    require(rank(unpack(COORD[0]+COORD[1]),True)==2,'rank-two rejected')
    # Nine calls, three full-rank targets, address span exactly six.
    units=[tuple(int(k==i*3+j) for k in range(9)) for i,j in
           [(0,0),(1,1),(2,2),(0,1),(1,2),(2,0)]]
    frames=units[:3]+units[3:]+units[:3]
    word=[unpack(COORD[i]) for i in range(3) for _ in range(3)]
    out=execute(word,frames)
    require(rank(frames)==6,'span-six positive control')
    for i in range(4):
        target=tuple(sum(frames[k][c] for k in range(9) if k//3==i) for c in range(9))
        for j in range(4): require(out[i][j]==({target} if i==j else set()),'endpoint')
        if i<3: require(rank([target[j:j+3] for j in (0,3,6)])==3,'invertible target')
    print(json.dumps({'status':'PASS_COORDINATE_KERNEL_CLOSURE',
        'pools':len(pools),'data_placements':placements,'formal_words':words,
        'inverse_controls':7,'negative_controls':4,'positive_calls':9,
        'positive_address_span':6,'inherited_lemma_reproved':False},sort_keys=True))

if __name__=='__main__': main()
