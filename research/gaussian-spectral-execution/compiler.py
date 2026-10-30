"""Exact pruned Gaussian residuals with explicit source and precision binding."""
from collections import Counter
from dataclasses import dataclass
from math import comb
from source import gaussian as G


def binomial(b,h):
    return comb(b,h) if b>=h else (0 if b>=0 else (-1)**h*comb(h-b-1,h))


def valuation(z):
    if z==G.ZERO:
        return None
    result=0
    while (z[0]+z[1])%2==0:
        z=G.exact_divide(z,1)
        result+=1
    return result


def prepare(n,a,R,p):
    G.need(type(n) is int and n>=1 and 0<=R<n and 0<=a<=n-R and p>=0,'Spectral parameters')
    Q=p+2*n-R-1
    coefficients=[]
    for j in range(n+1):
        value=G.ZERO
        for h in range(R+1):
            value=G.add(value,G.mul((binomial(j-a,h),0),G.phase(G.pi_power(h),h)))
        d=G.add(G.phase(G.ONE,j),G.neg(G.phase(value,a)))
        e=G.exact_divide(d,R+1)
        beta=valuation(e)
        q=0 if beta is None else max(Q-beta,0)
        unit=G.ZERO if beta is None else G.exact_divide(e,beta)
        coefficients.append(dict(d=d,e=e,beta=beta,q=q,unit=unit))
    demands={r:coefficients[r.bit_count()]['q'] for r in range(1<<n) if coefficients[r.bit_count()]['q']}
    return dict(n=n,a=a,R=R,p=p,Q=Q,m=n-R-1,coefficients=coefficients,demands=demands,
                preparation=dict(coefficients=n+1,binomial_terms=(n+1)*(R+1),
                    maximum_coefficient_bits=max(abs(v).bit_length() for c in coefficients for v in c['e']),
                    exact_pi_quotients=sum(c['e']!=G.ZERO for c in coefficients)))


def profile(n,demands):
    nodes={}
    for r,q in demands.items():
        for depth in range(n+1):
            prefix=r>>(n-depth)
            nodes[depth,prefix]=max(q,nodes.get((depth,prefix),0))
    return nodes


@dataclass
class Bank:
    n: int
    source: tuple
    values: tuple
    demands: tuple
    invoice: tuple
    closed: bool = False


def gather(source,plans):
    G.need(plans,'At least one response')
    n=plans[0]['n'];N=1<<n
    G.need(len(source)==N and all(p['n']==n for p in plans),'Shared cube dimensions')
    snapshot=tuple(tuple(z) for z in source)
    G.need(all(len(z)==2 and all(type(v) is int for v in z) for z in snapshot),'Integral source')
    demands={}
    for p in plans:
        for r,q in p['demands'].items():
            demands[r]=max(q,demands.get(r,0))
    nodes=profile(n,demands);values={};bill=Counter(SOURCE_READ=N,SNAPSHOT_COPY=N,ADD=0,ADD_MASS=0,
                                                  INIT=0,CLEAR=0,LEAF_WRITE=0)
    def visit(data,depth,prefix):
        if depth==n:
            values[prefix]=data[0];bill['LEAF_WRITE']+=1
            return
        half=len(data)//2
        for bit in (0,1):
            child=(depth+1,2*prefix+bit)
            if child not in nodes:
                continue
            q=nodes[child]
            v=[G.residue(G.add(data[i],G.phase(data[i+half],2*bit)),q) for i in range(half)]
            bill.update(ADD=half,ADD_MASS=half*q,INIT=half)
            visit(v,depth+1,2*prefix+bit)
            for i in range(half):v[i]=G.ZERO
            bill['CLEAR']+=half
    if nodes:
        visit(snapshot,0,0)
    expected=sum((N>>depth)*q for (depth,prefix),q in nodes.items() if depth)
    G.need(bill['ADD_MASS']==expected,'Literal gather precision invoice')
    return Bank(n,snapshot,tuple(sorted(values.items())),tuple(sorted(demands.items())),tuple(sorted(bill.items())))


def multiply_constant(value,c,q,bill):
    """Use explicit binary doubling and signed accumulation at the declared modulus."""
    parts=[]
    for component,k in ((c[0],0),(c[1],1)):
        if not component:
            continue
        rotation=k if component>0 else k+2
        base=G.phase(value,rotation)
        if rotation:bill['PHASE']+=1
        accumulator=base
        bill['MULT_COPY']+=1
        for bit in bin(abs(component))[3:]:
            accumulator=G.residue(G.add(accumulator,accumulator),q)
            bill.update(MULT_ADD=1,MULT_ADD_MASS=q)
            if bit=='1':
                accumulator=G.residue(G.add(accumulator,base),q)
                bill.update(MULT_ADD=1,MULT_ADD_MASS=q)
        parts.append(accumulator)
    if len(parts)==2:
        bill.update(MULT_ADD=1,MULT_ADD_MASS=q)
        return G.residue(G.add(*parts),q)
    return parts[0] if parts else G.ZERO


def deliver(bank,plan,source):
    G.need(not bank.closed and bank.n==plan['n'] and tuple(tuple(z) for z in source)==bank.source,'Actual immutable source version')
    available=dict(bank.demands);values=dict(bank.values)
    G.need(all(available.get(r,0)>=q for r,q in plan['demands'].items()),'Creation precision covers every leaf')
    n=bank.n;N=1<<n;Q=plan['Q'];nodes=profile(n,plan['demands'])
    bill=Counter(VERSION_READ=N,ADD=0,ADD_MASS=0,MULT_ADD=0,MULT_ADD_MASS=0,
                 PI_SCALE=0,SCALE_MASS=0,PHASE=0,COPY=0,INIT=0,CLEAR=0,QUOTIENT=N,OUTPUT_WRITE=N)
    def synth(depth,prefix):
        q=nodes[depth,prefix]
        if depth==n:
            c=plan['coefficients'][prefix.bit_count()]
            bill['INIT']+=1
            return [multiply_constant(G.residue(values[prefix],q),c['unit'],q,bill)]
        child=[];size=N>>(depth+1)
        for bit in (0,1):
            key=(depth+1,2*prefix+bit)
            if key not in nodes:
                child.append(None);continue
            v=synth(*key);scale=q-nodes[key]
            if scale:
                factor=G.pi_power(scale)
                for i,z in enumerate(v):v[i]=G.residue(G.mul(z,factor),q)
                bill.update(PI_SCALE=size,SCALE_MASS=size*q)
            child.append(v)
        out=[]
        for sign in (1,-1):
            for i in range(size):
                a=G.ZERO if child[0] is None else child[0][i]
                b=G.ZERO if child[1] is None else child[1][i]
                out.append(G.residue(G.add(a,b if sign==1 else G.neg(b)),q))
                if child[0] is not None and child[1] is not None:
                    bill.update(ADD=1,ADD_MASS=q)
                else:
                    bill['COPY']+=1
                    if sign==-1 and child[1] is not None:bill['PHASE']+=1
        bill['INIT']+=len(out)
        for v in child:
            if v is not None:
                for i in range(len(v)):v[i]=G.ZERO
                bill['CLEAR']+=len(v)
        return out
    if nodes:
        z=synth(0,0)
        root_factor=Q-nodes[0,0]
        if root_factor:
            factor=G.pi_power(root_factor)
            for i,v in enumerate(z):z[i]=G.residue(G.mul(v,factor),Q)
            bill.update(PI_SCALE=N,SCALE_MASS=N*Q)
    else:
        z=[G.ZERO]*N;bill['INIT']+=N
    output=[G.residue(G.phase(G.exact_divide(v,plan['m']),n),plan['p']+n) for v in z]
    bill.update(PHASE=N,INIT=N)
    for i in range(N):z[i]=G.ZERO
    bill['CLEAR']+=N
    return output,dict(bill)


def close(bank):
    G.need(not bank.closed,'Live bank retirement')
    cells=len(bank.values)+len(bank.source)
    bank.values=()
    bank.source=()
    bank.demands=()
    bank.closed=True
    return dict(CLEAR=cells,RETIRED=True)


def r0_gather_mass(n,a,p):
    Q=p+2*n-1;N=1<<n
    c0=sum(comb(n,j) for j in range(n+1) if (j-a)%4==0)
    c2=sum(comb(n,j) for j in range(n+1) if (j-a)%4==2)
    return N*(n-1)*Q+(N-c0)*Q-c2
