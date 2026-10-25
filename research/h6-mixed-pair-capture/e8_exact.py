"""Independent recursive enumeration of doubled E8, exact integers only."""
from collections import defaultdict
from math import isqrt


def need(ok,message):
    if not ok:raise ValueError(message)


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def shell(norm):
    result=[]
    def visit(prefix,left,parity):
        if len(prefix)==8:
            if left==0 and sum(prefix)%4==0 and next((v for v in prefix if v),0)>0:
                result.append(tuple(prefix))
            return
        for v in range(-isqrt(left),isqrt(left)+1):
            if v%2==parity:visit(prefix+(v,),left-v*v,parity)
    for parity in (0,1):visit((),norm,parity)
    answer=sorted(result)
    need(len(answer)==len(set(answer)),'unique recursive lattice shell')
    return answer


def signature(vector,roots):
    result=0
    for i,r in enumerate(roots):
        p=dot(vector,r)
        need(p%4==0,'integral E8 lattice pairing')
        result|=((p//4)&1)<<i
    return result


def geometry():
    roots,pure=shell(8),shell(16)
    need((len(roots),len(pure))==(120,1080),'complete projective E8 shell sizes')
    root_sig=[signature(r,roots) for r in roots]
    buckets=defaultdict(list)
    for i,v in enumerate(pure):buckets[signature(v,roots)].append(i)
    need(len(set(root_sig))==120 and 0 not in root_sig,'distinct root cosets')
    need(len(buckets)==135 and all(len(v)==8 for v in buckets.values()),'135 complete pure-label fibers')
    need(not(set(root_sig)&set(buckets)) and 0 not in buckets,'disjoint nonzero E8 cosets')
    # All256 cosets represented; the pairing-signature span is exactly8.
    values=[0,*root_sig,*buckets]
    from pair_factor import binary_rank
    need(len(set(values))==256 and binary_rank(values)==8,'full E8 mod-two quotient')
    return roots,pure,root_sig,dict(sorted(buckets.items()))


def mixed_port(i,j,negative=False):
    return 2160+2*(120*i+j)+int(negative)


def vector(index,roots,pure):
    z=(0,)*8
    if index<1080:return pure[index]+z
    if index<2160:return z+pure[index-1080]
    value=index-2160;ij,sign=divmod(value,2);i,j=divmod(ij,120)
    return roots[i]+tuple((-1 if sign else 1)*x for x in roots[j])


def label(index,roots,pure,root_sig,buckets):
    # The unchanged source's affine binary isometry is injective on this pair
    # of pairing signatures; exact native label values are not changed here.
    if index<1080:return (signature(pure[index],roots),0)
    if index<2160:return (0,signature(pure[index-1080],roots))
    ij=(index-2160)//2;i,j=divmod(ij,120)
    return root_sig[i],root_sig[j]
