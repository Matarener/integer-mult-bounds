"""Verify exact words, cost, precision bounds and finite shortest paths."""
import hashlib
import importlib.util
import itertools
import json
from math import lcm
from pathlib import Path
import random

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('borrowed_compile',HERE/'compile.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


def require(ok,message):
    if not ok:
        raise RuntimeError(message)


def fixture(r,seed,denominator=1):
    rng=random.Random(seed)
    n=2*r+1
    change=c.eye(n)
    for _ in range(3*n):
        i,j=rng.sample(range(n),2)
        a=c.Q(rng.choice([-1,1]),denominator)
        change[i]=[x+a*y for x,y in zip(change[i],change[j])]
    inv=c.inverse(change)
    v=[row[:r] for row in change]
    l=inv[r:2*r]
    require(c.mm(l,v)==c.zero(r,r),'fixture cross-products')
    return v,l


def target(v,l,q):
    n=len(v)
    out=c.eye(n+q)
    a=c.mm(v,l) if l else c.zero(n,n)
    for i in range(n):
        for j in range(n):out[i][j]+=a[i][j]
    return out


def binary_generators(n,q):
    # A packed row is the image coefficient row, over F2.
    d=n+q
    eye=tuple(1<<i for i in range(d))
    out=[]
    for mask in range(1,1<<(n*q)):
        a=list(eye)
        for i in range(q):
            for j in range(n):
                if mask>>(i*n+j)&1:a[n+i]^=1<<j
        out.append(tuple(a))
        a=list(eye)
        for i in range(n):
            for j in range(q):
                if mask>>(i*q+j)&1:a[i]^=1<<(n+j)
        out.append(tuple(a))
    return out


def binary_mul(a,b):
    out=[]
    for row in a:
        value=0
        for j in range(len(b)):
            if row>>j&1:value^=b[j]
        out.append(value)
    return tuple(out)


def binary_inverse(a):
    n=len(a)
    rows=[x | (1<<(n+i)) for i,x in enumerate(a)]
    for j in range(n):
        k=next(i for i in range(j,n) if rows[i]>>j&1)
        rows[j],rows[k]=rows[k],rows[j]
        for i in range(n):
            if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
    return tuple(row>>n for row in rows)


def ball(n,q,depth):
    eye=tuple(1<<i for i in range(n+q))
    seen={eye:0};front=[eye]
    generators=binary_generators(n,q)
    for k in range(depth):
        following=[]
        for a in front:
            for g in generators:
                b=binary_mul(g,a)
                if b not in seen:seen[b]=k+1;following.append(b)
        front=following
    return seen


def shortest_controls():
    complete=ball(2,1,10)
    require(len(complete)==168,'GL3 binary census')
    distances=[]
    for values in itertools.product(range(2),repeat=4):
        n=[list(values[:2]),list(values[2:])]
        if not any(values) or any(sum(n[i][k]*n[k][j] for k in range(2))%2 for i in range(2) for j in range(2)):
            continue
        t=tuple((1<<i)^sum(n[i][j]<<j for j in range(2)) for i in range(2))+(4,)
        distances.append(complete[t])
    require(distances==[4,4,4],'rank-one dirty minimum')
    b3=ball(4,1,3)
    b2={a:d for a,d in b3.items() if d<=2}
    t=(1^4,2^8,4,8,16)
    for a in b2:
        require(binary_mul(t,binary_inverse(a)) not in b3,'rank-two word of length at most five')
    return {'binary_GL3_states':len(complete),'rank_one_targets':len(distances),
            'rank_two_ball_depth2':len(b2),'rank_two_ball_depth3':len(b3),'rank_two_minimum':6}


def kernel_checks():
    receipts=[]
    for h in (1,2):
        m=1<<h;n=4
        values=[]
        for chi in range(m):
            a=c.zero(n,n)
            if chi==0:
                a[0][2]=1;a[1][3]=1
            elif chi==2:
                a[2][0]=1;a[3][1]=1
            elif chi==1:
                a[3][0]=1
            else:
                a[1][2]=1
            values.append(a)
        kernel=c.from_characters(values)
        for q in (1,2):
            word,ranks=c.compile_kernel(kernel,q)
            require(max(ranks)==2 and len(word)==2*((2+q-1)//q)+2,'character maximum tariff')
            ops=c.kernel_scalar_ops(word,n,q)
            for width in (1,2):
                volume=m**width
                def shift(g):return sum(g<<(h*j) for j in range(width))
                expanded=[(d*volume+y,s*volume+(y^shift(g)),a) for d,s,a,g in ops for y in range(volume)]
                actual,prefix,suffix=c.replay(expanded,(n+q)*volume)
                expected=c.eye((n+q)*volume)
                for g,mat in kernel.items():
                    for i,row in enumerate(mat):
                        for j,a in enumerate(row):
                            for y in range(volume):expected[i*volume+y][j*volume+(y^shift(g))]+=a
                require(actual==expected,'all-column tensor-lift kernel endpoint')
                # Independent endpoint evaluation uses the coefficient permutation directly.
                receipts.append(dict(group_order=m,width=width,borrowed=q,ranks=ranks,
                                     shears=len(word),coefficient_ADDs=len(ops),
                                     denominator_lcm=lcm(*(a.denominator for _,_,a,_ in ops)),
                                     prefix_norm=str(prefix),suffix_norm=str(suffix)))
    return receipts


def main():
    for item in json.loads((HERE/'SOURCE-CONTEXT.json').read_text())['files']:
        require(hashlib.sha256((HERE/item['local']).read_bytes()).hexdigest()==item['sha256'],'source bytes changed')
    cases=ops_count=controls=0
    for r in range(1,7):
        for denominator in (1,2):
            v,l=fixture(r,100+r,denominator)
            n=len(v)
            a=c.mm(v,l)
            vf,lf=c.factor_square_zero(a)
            require(c.mm(vf,lf)==a and len(lf)==r,'rank factorization')
            for q in sorted({1,2,r,r+1}):
                word=c.compile_factors(v,l,q)
                ops=c.scalar_ops(word,n,q)
                result,prefix,suffix=c.replay(ops,n+q)
                require(result==target(v,l,q),'complete dirty endpoint')
                require(len(word)==2*((r+q-1)//q)+2,'sharp shear count')
                require(sum(k=='G' for k,_ in word)==sum(k=='S' for k,_ in word),'direction counts')
                old=2*(sum(x!=0 for row in v for x in row)+sum(x!=0 for row in l for x in row))
                require(len(ops)<=old,'scalar ADD count grew')
                bp,bs=c.bounds(v,l,q)
                require(prefix<=bp and suffix<=bs,'primitive interval bound')
                inverse=[(d,s,-a) for d,s,a in reversed(ops)]
                back,_,_=c.replay(ops+inverse,n+q)
                require(back==c.eye(n+q),'inverse word')
                clean=c.compile_factors(v,l,q,clean=True)
                require(len(clean)==2*((r+q-1)//q)+1,'clean shear count')
                clean_result,_,_=c.replay(c.scalar_ops(clean,n,q),n+q)
                require(all(clean_result[i][:n]==target(v,l,q)[i][:n] for i in range(n+q)),'clean-input endpoint')
                require(clean_result!=result,'clean centre mistaken for dirty centre')
                controls+=1
                require(c.replay(ops[:-1],n+q)[0]!=result,'deleted ADD accepted')
                controls+=1
                cases+=1;ops_count+=len(ops)
    # Literal source-format sections: D0 J = D1 J = I.
    v,l=fixture(3,987)
    n=len(v)
    _,rows=c.rref(c.transpose(v))
    left=c.mm(c.inverse([v[i] for i in rows]),[[int(j==i) for j in range(n)] for i in rows])
    require(c.mm(left,v)==c.eye(3),'section left inverse')
    right=c.add(left,l)
    def section(d):
        out=c.zero(n+3,n+3);data=c.add(c.eye(n),c.mm(v,d),-1)
        for i in range(n):out[i]=data[i]+v[i]
        for i in range(3):out[n+i]=d[i]+[c.Q(0)]*3
        return out
    k=target(v,l,3);ki=c.inverse(k)
    require(c.mm(c.mm(ki,section(left)),k)==section(right),'full section conjugacy')
    controls+=1
    # Thirty modes give the full storage tradeoff without an extra paid call.
    v=[ [c.Q(i==j) for j in range(30)] for i in range(60)]
    l=[ [c.Q(j==30+i) for j in range(60)] for i in range(30)]
    tradeoff=[]
    for q in (1,2,3,5,6,10,15,30):
        word=c.compile_factors(v,l,q);ops=c.scalar_ops(word,60,q)
        result,prefix,suffix=c.replay(ops,60+q)
        require(result==target(v,l,q),'thirty-mode endpoint')
        require(len(ops)==120,'thirty-mode scalar bill')
        tradeoff.append({'borrowed':q,'shears':len(word),'scalar_ADDs':len(ops),
                         'prefix_norm':str(prefix),'suffix_norm':str(suffix)})
    require(c.compile_factors(c.zero(3,0),[],1)==[],'zero update')
    try:c.factor_square_zero(c.eye(2))
    except ValueError:controls+=1
    else:raise RuntimeError('nonsquare-zero input accepted')
    try:c.compile_factors([[1]],[[1]],1)
    except ValueError:controls+=1
    else:raise RuntimeError('nonzero cross-product accepted')
    for bad,q in [({0:c.eye(2)},1),({0:c.zero(2,2)},0),({0:[[0],[0,0]]},1)]:
        try:c.compile_kernel(bad,q)
        except ValueError:controls+=1
        else:raise RuntimeError('invalid kernel accepted')
    print(json.dumps({'rational_cases':cases,'scalar_ADDs_replayed':ops_count,'controls':controls,
                      'shortest_paths':shortest_controls(),'thirty_mode_tradeoff':tradeoff,
                      'translation_kernel_cases':kernel_checks()},sort_keys=True))
    print('PASS_BORROWED_SPACE_SHEAR_TARIFF')


if __name__=='__main__':main()
