"""Exact Gaussian residue execution of the frozen Smith circuit."""
from collections import Counter
from math import comb

ZERO = (0,0)
ONE = (1,0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(x,y):
    return x[0]+y[0],x[1]+y[1]


def neg(x):
    return -x[0],-x[1]


def phase(x,k):
    a,b=x
    return ((a,b),(-b,a),(-a,-b),(b,-a))[k%4]


def mul(x,y):
    return x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0]


def pi_power(m):
    need(m>=0,'Nonnegative integral scale')
    return phase((2**(m//2),0) if m%2==0 else (2**(m//2),2**(m//2)),m//2)


def residue(x,q):
    """Return one of exactly 2**q canonical Gaussian residue pairs."""
    need(q>=0,'Nonnegative raw modulus')
    if q%2==0:
        mod=1<<(q//2)
        return x[0]%mod,x[1]%mod
    half=1<<(q//2)
    b=x[1]%half
    a=(x[0]-(x[1]-b))%(2*half)
    return a,b


def exact_divide(x,m):
    need(m>=0,'Nonnegative quotient exponent')
    a,b=x
    if m%2:
        need((a+b)%2==0,'Exact odd Gaussian quotient')
        a,b=(a+b)//2,(b-a)//2
    power=1<<(m//2)
    need(a%power==0 and b%power==0,'Exact binary quotient')
    return phase((a//power,b//power),-(m//2))


def raw_tensor(x,n):
    """Apply C tensor n without the Smith factorization or reduction."""
    need(len(x)==1<<n,'Cube size')
    y=list(x)
    for axis in range(n):
        bit=1<<axis
        for r in range(1<<n):
            if not r&bit:
                a,b=y[r],y[r+bit]
                y[r]=add(phase(a,1),b)
                y[r+bit]=add(a,phase(b,1))
    return y


def execute(x,n,P):
    """Return the full raw numerator modulo pi**P and its literal invoice."""
    need(type(n) is int and n>=0 and type(P) is int and P>=0,'Raw dimensions')
    need(len(x)==1<<n and all(len(z)==2 and all(type(v) is int for v in z) for z in x),'Integral cube')
    original=tuple(x)
    work=[ZERO for _ in x]
    for r,z in enumerate(x):
        work[r]=residue(z,P)
    counts=Counter(INIT=2*len(x),COPY=len(x),CLEAR=0,ADD=0,PHASE=0,PI2_SCALE=0,TRUNCATE=0)
    mass=Counter(INIT=2*len(x)*P,COPY=len(x)*P,CLEAR=0,ADD=0,PHASE=0,PI2_SCALE=0,TRUNCATE=0)
    stages=[]
    for axis in range(n):
        bit=1<<axis
        stage=0
        for r in range(1<<n):
            if r&bit:
                continue
            Q=max(P-2*(r&(bit-1)).bit_count(),0)
            if Q:
                a,b=work[r],work[r+bit]
                work[r]=residue(add(a,phase(b,-1)),Q)
                work[r+bit]=residue(b,max(Q-2,0))
                counts.update(ADD=1,PHASE=1,TRUNCATE=1)
                mass.update(ADD=Q,PHASE=Q,TRUNCATE=Q)
                stage+=Q
            else:
                need(work[r]==work[r+bit]==ZERO,'Pruned T branch is zero')
        stages.append(['T',axis,stage])
    diagonal_bits=sum(max(P-2*r.bit_count(),0) for r in range(1<<n))
    for axis in range(n):
        bit=1<<axis
        stage=0
        for r in range(1<<n):
            if r&bit:
                continue
            Q=max(P-2*(r>>(axis+1)).bit_count(),0)
            if Q:
                a,b=work[r],work[r+bit]
                scaled=phase((2*b[0],2*b[1]),1)
                work[r+bit]=residue(add(a,scaled),Q)
                work[r]=residue(phase(a,1),Q)
                counts.update(ADD=1,PHASE=1,PI2_SCALE=1)
                mass.update(ADD=Q,PHASE=Q,PI2_SCALE=Q)
                stage+=Q
            else:
                need(work[r]==work[r+bit]==ZERO,'Pruned S branch is zero')
        stages.append(['S',axis,stage])
    output=[ZERO for _ in x]
    for r,z in enumerate(work):
        output[r]=z
    counts.update(COPY=len(x),CLEAR=len(x))
    mass.update(COPY=len(x)*P,CLEAR=len(x)*P)
    for r in range(len(work)):
        work[r]=ZERO
    need(tuple(x)==original and all(z==ZERO for z in work),'Input and owned cleanup')
    return output,dict(counts=dict(counts),precision_mass=dict(mass),stages=stages,
                       diagonal_bits=diagonal_bits,source_preserved=True,work_zero=True)


def formula(n,P):
    stages=[(1<<(n-m-1))*sum(comb(m,j)*max(P-2*j,0) for j in range(m+1)) for m in range(n)]
    return dict(add_mass=2*sum(stages),T=stages,S=list(reversed(stages)),
                diagonal_bits=sum(comb(n,j)*max(P-2*j,0) for j in range(n+1)))


def exact(x,n,inverse=False):
    b=max((abs(v).bit_length() for z in x for v in z),default=0)
    q=b+n+2
    data=[(a,-b) for a,b in x] if inverse else x
    values,invoice=execute(data,n,2*q)
    mod=1<<q
    values=[tuple(v-mod if v>=mod//2 else v for v in z) for z in values]
    if inverse:
        values=[phase((a,-b),n) for a,b in values]
    return values,dict(raw_precision=2*q,invoice=invoice)


def install(x,n,header=0):
    """Use two exact central kernels and a literal payload swap."""
    need(type(header) is int and header>=0,'Input denominator header')
    old=list(x)
    image,forward=exact(old,n)
    public,owned=image,old
    inverse,backward=exact(public,n,inverse=True)
    restored=[exact_divide(z,2*n) for z in inverse]
    owned=[add(a,neg(b)) for a,b in zip(owned,restored)]
    need(all(z==ZERO for z in owned),'Inverse cleanup')
    return public,dict(input_header=header,output_header=header+n,
        forward=forward,inverse=backward,payload_swap_cells=2*len(x),
        header_swaps=1,alignment_divisions=len(x),cleanup_adds=len(x),owned_zero=True)
