#!/usr/bin/env python3
"""Check the connector proof identities and sharp static constructions.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)

def eye(n):
    return tuple(1 << i for i in range(n))

def zero(n):
    return (0,) * n

def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))

def mul(a, b):
    out = []
    for row in a:
        v = 0
        while row:
            low = row & -row
            v ^= b[low.bit_length()-1]
            row ^= low
        out.append(v)
    return tuple(out)

def rank(rows):
    basis = {}
    for v in rows:
        while v:
            k = v.bit_length()-1
            if k not in basis:
                basis[k] = v
                break
            v ^= basis[k]
    return len(basis)

def transpose(a):
    n = len(a)
    return tuple(sum(((a[j] >> i) & 1) << j for j in range(n)) for i in range(n))

def inverse(a):
    n = len(a)
    rows = [a[i] | (1 << (n+i)) for i in range(n)]
    for j in range(n):
        k = next(i for i in range(j, n) if rows[i] >> j & 1)
        rows[k], rows[j] = rows[j], rows[k]
        for i in range(n):
            if i != j and rows[i] >> j & 1:
                rows[i] ^= rows[j]
    return tuple(r >> n for r in rows)

def random_gl(n, rng):
    a = list(eye(n))
    for _ in range(5*n):
        i,j = rng.sample(range(n),2)
        a[i] ^= a[j]
    return tuple(a)

def outer(u,v,n):
    return tuple(v if u >> i & 1 else 0 for i in range(n))

def local(a,b,j,g,d):
    n=(g+1)*d
    out=[0]*n
    for i in range(d):
        out[i]=(a[i]^b[i]) | b[i] << (j*d)
        out[j*d+i]=b[i] | (a[i]^b[i]) << (j*d)
    return tuple(out)

def block(a,r,c,d):
    return tuple((a[r*d+i] >> (c*d)) & ((1<<d)-1) for i in range(d))

def sum_mats(items,n):
    out=zero(n)
    for a in items:
        out=add(out,a)
    return out

def split_census():
    flags=[]
    for a in itertools.product(range(4),repeat=2):
        if rank(a)==2:
            p=mul(mul(a,(1,0)),inverse(a))
            flags.append((p,add(p,eye(2))))
    require(len(set(flags))==6,'GL2 flags')
    words=set(itertools.permutations((0,0,1,1,2,2)))
    hist=[0]*6
    digest=hashlib.sha256()
    for fs in itertools.product(flags,repeat=3):
        for word in sorted(words):
            seen=[0,0,0];prefix=[zero(2)]*3
            failed=None
            for index,j in enumerate(word):
                a=fs[j][seen[j]];seen[j]+=1
                others=[k for k in range(3) if k!=j]
                defect=mul(a,add(prefix[others[0]],prefix[others[1]]))
                if defect!=zero(2) and failed is None:failed=index
                prefix[j]=add(prefix[j],a)
            require(failed is not None,'forbidden prefix flag')
            hist[failed]+=1;digest.update(bytes(word)+bytes([failed]))
    return {'ordered_flag_words':sum(hist),'first_failure_histogram':hist,'digest':digest.hexdigest()}

def coefficient_audit():
    rng=random.Random(527193)
    cases=0;extractions=0;noncommuting=0;distinct_external=0
    for d in (2,3,4):
      for g in (3,4,5):
       n=(g+1)*d
       for trial in range(8):
        calls=[];all_a=[]
        for j in range(1,g+1):
            h=random_gl(d,rng);hi=inverse(h)
            shear=tuple(rng.randrange(1<<d) for _ in range(d))
            aps=[]
            for z in range(d):
                diagonal=tuple(1<<z if i==z else 0 for i in range(d))
                a=mul(mul(h,diagonal),hi)
                b=add(mul(shear,a),mul(a,shear))
                p=local(a,b,j,g,d)
                r=local(zero(d),a,j,g,d)
                require(mul(p,p)==p and mul(p,r)==r and mul(r,p)==r,'projector/query')
                require(mul(r,r)==zero(n),'full query square')
                calls.append((j,p,r,a));aps.append(a)
            all_a.append(aps)
        if mul(all_a[0][0],all_a[1][0])!=mul(all_a[1][0],all_a[0][0]):noncommuting+=1
        chosen=tuple(rng.sample(range(1,g+1),3))
        z=list(tuple(rng.randrange(1<<n) for _ in range(n)))
        mask=(1<<d)-1
        for i in range(n):
            value=(z[i] >> (chosen[0]*d)) & mask
            for leaf in chosen[1:]:
                z[i]=(z[i] & ~(mask << (leaf*d))) | value << (leaf*d)
        z=tuple(z)
        calls.append((0,zero(n),z,zero(d)))
        rng.shuffle(calls)
        repair=add(eye(n),sum_mats((r for _,_,r,_ in calls),n))
        calls.insert(rng.randrange(len(calls)+1),(0,zero(n),repair,zero(d)))
        for _,_,zz,_ in (c for c in calls if c[0]==0):
            require(all(block(zz,r,chosen[0],d)==block(zz,r,k,d) for r in range(g+1) for k in chosen),'equal columns')
        for j in chosen:
            # Direct literal multiplication in F2[e,x]/(e^2,x^2).
            ce=zero(n);cx=zero(n);cex=zero(n)
            for stage,p,r,a in calls:
                px=p if stage==j else zero(n)
                cex=add(add(add(cex,mul(r,cx)),mul(px,ce)),mul(px,r))
                ce=add(ce,r);cx=add(cx,px)
            require(ce==eye(n),'query sum')
            later=zero(n);comm=zero(n)
            for stage,p,r,a in reversed(calls):
                if stage==j:comm=add(comm,add(mul(p,later),mul(later,p)))
                later=add(later,r)
            require(add(cex,cx)==comm,'literal mixed coefficient')
            other=[k for k in chosen if k!=j]
            s={k:zero(d) for k in other};thin={k:zero(d) for k in other}
            for i,(stage,p,r,a) in enumerate(calls):
                if stage!=j:continue
                for st2,p2,r2,a2 in calls[i+1:]:
                    for k in other:
                        if st2==k:s[k]=add(s[k],mul(a,a2))
                        if st2==0:thin[k]=add(thin[k],mul(a,add(block(r2,0,k,d),block(r2,j,k,d))))
            for k in other:
                got=add(block(comm,0,k,d),block(comm,j,k,d))
                require(got==add(s[k],thin[k]),'three-leaf extraction')
                extractions+=1
            require(thin[other[0]]==thin[other[1]],'common thin term')
        if g>3:distinct_external+=1
        cases+=1
    require(noncommuting>0 and distinct_external>0,'control coverage')
    return {'literal_words':cases,'off_support_extractions':extractions,'noncommuting_flags':noncommuting,'words_with_external_stages':distinct_external}

def poly_mul(a,b):
    out=0
    while b:
        if b&1:out^=a
        a<<=1;b>>=1
    return out

def poly_det(a):
    n=len(a);out=0
    for order in itertools.permutations(range(n)):
        term=1
        for i,j in enumerate(order):term=poly_mul(term,a[i][j])
        out^=term
    return out

def prefix_audit():
    rng=random.Random(51973);factors=0;products=0;defects=0
    for d in (2,3,4):
      for trial in range(12):
        calls=[]
        for j in range(3):
            h=random_gl(d,rng);hi=inverse(h)
            for i in range(d):
                a=mul(mul(h,tuple(1<<i if z==i else 0 for z in range(d))),hi)
                calls.append(a)
        rng.shuffle(calls)
        product=[[int(i==j) for j in range(d)] for i in range(d)]
        prefix=zero(d)
        for a in calls:
            factor=[[int(i==j) ^ (((a[i]>>j)&1)<<1) for j in range(d)] for i in range(d)]
            require(poly_det(factor)==3,'rank-one determinant')
            next_product=[[0]*d for _ in range(d)]
            for i in range(d):
              for j in range(d):
               for k in range(d):next_product[i][j]^=poly_mul(factor[i][k],product[k][j])
            product=next_product
            if mul(a,prefix)!=zero(d):defects+=1
            prefix=add(prefix,a);factors+=1
        require(prefix==eye(d),'final prefix')
        expected=1
        for _ in range(3*d):expected=poly_mul(expected,3)
        require(poly_det(product)==expected,'product determinant')
        target=1
        for _ in range(d):target=poly_mul(target,3)
        require(expected!=target,'determinant contradiction')
        products+=1
    return {'formal_polynomial_products':products,'projection_determinants':factors,'nonzero_prefix_defects':defects}

def static_witness(d,h,field_bits=1):
    # Multiplication matrices embed F4 in Mat_2(F2), when field_bits is two.
    require(field_bits in (1,2),'field')
    q=1<<field_bits
    signatures=list(itertools.product(range(q),repeat=d*h))
    labels=[signatures[0]]+[s for s in signatures[1:] for _ in range(2)]
    g=len(labels);D=d*field_bits;n=(g+1)*D
    def coefficient(a):
        if field_bits==1:return (a,)
        return ((a&1)|((a>>1)<<1),(a>>1)|(((a&1)^(a>>1))<<1))
    def fmap(axis,forward):
        m=[0]*n
        for leaf in range(1,g+1):
            for bit in range(field_bits):
                r,c=(axis*field_bits+bit,leaf*D+axis*field_bits+bit)
                if not forward:r,c=c,r
                m[r]|=1<<c
        return tuple(m)
    fs=[fmap(i,True) for i in range(d)];gs=[fmap(i,False) for i in range(d)]
    # Each U_a and V_a is field-linear; build their product from its entries.
    es=[]
    for a in range(h):
        rows=[]
        for leaf in range(g+1):
            for i in range(d):
                for bit in range(field_bits):
                    row=0
                    if leaf:
                        u=labels[leaf-1][a*d+i]
                        for other in range(1,g+1):
                            for j in range(d):
                                v=labels[other-1][a*d+j]
                                if field_bits==1:uv=u*v
                                else:
                                    uv=0
                                    for k in range(2):
                                        if v>>k&1:uv^=u<<k
                                    if uv&4:uv^=7
                                row |= coefficient(uv)[bit] << (other*D+j*field_bits)
                    rows.append(row)
        es.append(tuple(rows))
    queries=fs+gs+[e for e in es for _ in range(2)]
    k=sum_mats(fs+gs,n)
    def check_queries(qs,expected_rank):
        require(sum_mats(qs,n)==k,'thin sum')
        require(all(mul(z,z)==zero(n) for z in qs),'thin square-zero')
        r=sum(rank(z) for z in qs)
        require(r==expected_rank*field_bits,'thin rank sum')
        u=rank([r for z in qs for r in transpose(z)])
        v=rank([r for z in qs for r in z])
        require(u==v==(2*d+h)*field_bits,'image and row spans')
        require(rank(k)==2*d*field_bits and r==u+v-rank(k),'sharp Sylvester cut')
        cols=[];rows=[]
        for leaf in range(1,g+1):
            cols.append(tuple((row >> (leaf*D)) & ((1<<D)-1) for z in qs for row in z))
            rows.append(tuple(row for z in qs for row in z[leaf*D:(leaf+1)*D]))
        require(max(cols.count(s) for s in set(cols))==2,'column signatures')
        require(max(rows.count(s) for s in set(rows))==2,'row signatures')
        require(len(set(cols))==len(set(rows))==q**(d*h),'signature count')
    check_queries(queries,2*d+2*h)
    paired=None
    if h==1 and d>=2:
        paired=[add(fs[0],es[0]),add(gs[1],es[0])]
        paired += [add(fs[i],gs[(i+1)%d]) for i in range(1,d)]
        check_queries(paired,2*d+2)
        require(all(rank(z)==2*field_bits for z in paired),'rank-two pairing')
    # The static conditions must reject actual damage.
    controls=0
    for broken in (queries[:-1], [add(queries[0],eye(n))]+queries[1:]):
        try:check_queries(broken,2*d+2*h)
        except ValueError:controls+=1
        else:raise ValueError('damaged witness accepted')
    return {'field_size':q,'d':d,'h':h,'leaves':g,'field_dimension':n//field_bits,'thin_rank':2*d+2*h,'rank_one_queries':len(queries),'rank_two_queries':None if paired is None else len(paired),'rejected_controls':controls}

def main():
    source=ROOT/'vendor/PR5673-PROOF.md'
    manifest=json.loads((ROOT/'SOURCES.json').read_text())
    pin=next(x for x in manifest['files'] if x['path'].endswith('vendor/PR5673-PROOF.md'))
    require(hashlib.sha256(source.read_bytes()).hexdigest()==pin['sha256'],'source hash')
    result={'status':'PASS_ONE_SIDED_AUDIT_AND_STATIC_SHARPNESS','split_census':split_census(),'prefix_audit':prefix_audit(),'mixed_coefficient_audit':coefficient_audit(),'static_witnesses':[static_witness(*args) for args in [(2,1),(3,1),(4,1),(2,2),(2,3),(2,1,2)]],'limits':['Written universal proof; no proof-assistant or human acceptance','Static witnesses are not chronological words','No native lift, complete physical invoice or new kappa']}
    saved=ROOT/'RESULT.json'
    if saved.exists():require(json.loads(saved.read_text())==result,'saved result mismatch')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
