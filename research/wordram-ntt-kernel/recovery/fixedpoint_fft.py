"""Certified fixed-point FFT application. Python standard library only.
Not a Word RAM cost certificate: products below may require multiword arithmetic.
"""
from fractions import Fraction as F
from math import factorial
import argparse, hashlib, json, random
from pathlib import Path


def nearest(x):
    """Nearest integer; exact ties go toward positive infinity."""
    return (2*x.numerator + x.denominator)//(2*x.denominator)


def atan_interval(q, terms=100):
    z=F(1,q)
    total=sum(((-1)**j*z**(2*j+1)/ (2*j+1) for j in range(terms)),F(0))
    nxt=(-1)**terms*z**(2*terms+1)/(2*terms+1)
    return min(total,total+nxt),max(total,total+nxt)


def pi_interval():
    a,b=atan_interval(5); c,d=atan_interval(239)
    return 16*a-4*d,16*b-4*c


def certified_twiddles(n,bits):
    """Each coordinate is within 1/(2*Q) of its true root coordinate.
    Machin's formula and Taylor's theorem give rational certificates.
    True forward twiddle is exp(-2*pi*i*k/n).
    """
    q=1<<bits; lo,hi=pi_interval(); mid=F(nearest((lo+hi)/2*(1<<96)),1<<96)
    result=[]; maxrad=F(0)
    for k in range(n//2):
        if k==0: result.append((q,0)); continue
        if 4*k==n: result.append((0,-q)); continue
        kk=min(k,n//2-k)
        x=2*mid*kk/n
        c=sum(((-1)**j*x**(2*j)/factorial(2*j) for j in range(16)),F(0))
        s=sum(((-1)**j*x**(2*j+1)/factorial(2*j+1) for j in range(16)),F(0))
        # Taylor polynomial degrees 30 and 31; derivative magnitude <= 1.
        perturb=F(2*kk,n)*max(abs(mid-lo),abs(hi-mid))
        ec=abs(x)**31/factorial(31)+perturb
        es=abs(x)**32/factorial(32)+perturb
        if k>n//4: c=-c
        a=nearest(c*q); b=nearest(-s*q)
        assert abs(F(a,q)-c)+ec < F(1,2*q)
        assert abs(F(b,q)+s)+es < F(1,2*q)
        result.append((a,b)); maxrad=max(maxrad,ec,es)
    return result, {'pi_lower':str(lo),'pi_upper':str(hi),
       'max_taylor_and_argument_radius':str(maxrad),
       'component_error_upper':str(F(1,2*q)),
       'euclidean_error_upper':str(F(1,q))}


def cmul(a,b,q,counter):
    counter['complex_products']+=1
    return nearest(F(a[0]*b[0]-a[1]*b[1],q)),nearest(F(a[0]*b[1]+a[1]*b[0],q))


def fft(data,twiddles,q,inverse,counter):
    n=len(data); out=list(data); j=0
    for i in range(1,n):
        bit=n>>1
        while j&bit: j^=bit; bit>>=1
        j^=bit
        if i<j: out[i],out[j]=out[j],out[i]
    length=2
    while length<=n:
        for offset in range(0,n,length):
            for j in range(length//2):
                w=twiddles[j*n//length]
                if inverse: w=(w[0],-w[1])
                u=out[offset+j]; v=out[offset+j+length//2]
                t=cmul(v,w,q,counter) # exactly one shared product
                out[offset+j]=(u[0]+t[0],u[1]+t[1])
                out[offset+j+length//2]=(u[0]-t[0],u[1]-t[1])
                counter['butterflies']+=1
        length*=2
    return out


def budget(n,d,bits):
    """Uniform Euclidean norm error bound, all admissible input digits.
    Additions are exact integer additions; only complex products round.
    """
    delta=F(1,1<<bits); werr=delta
    def stages(m,e):
        ledger=[]
        for stage in range(n.bit_length()-1):
            # E + |w|E + W(M+E) + delta; |w|=1.
            e=(2+werr)*e+werr*m+delta
            m*=2
            ledger.append({'stage':stage+1,'magnitude_upper':str(m),'error_upper':str(e)})
        return m,e,ledger
    m,e,fwd=stages(F(d),F(0))
    ep=2*m*e+e*e+delta
    mi,ei,inv=stages(m*m,ep)
    # No rounding in normalization: interpreted output is integer/(Q*N).
    return {'forward':fwd,'product_error':str(ep),'inverse':inv,
      'coefficient_error_upper':str(ei/n),'strict_half':ei/n<F(1,2)}


def schoolbook(a,b,n):
    out=[0]*n
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return out


def run(n=512,bits=40,cases=12):
    assert n>=2 and n&(n-1)==0
    q=1<<bits; d=15; width=n//2
    tw,tc=certified_twiddles(n,bits)
    bound=budget(n,d,bits); assert bound['strict_half']
    if n==512 and bits==40: assert F(bound['coefficient_error_upper'])<F(1,1000)
    if n==512: assert not budget(n,d,30)['strict_half']
    rng=random.Random(20261024)
    tests=[([0]*width,[0]*width),([d]*width,[d]*width),
      ([d]+[0]*(width-1),[0]*(width-1)+[d]),
      ([0]*(width-1)+[d],[0]*(width-1)+[d]),
      ([d if i%2 else 0 for i in range(width)],[d if i%2 else 0 for i in range(width)])]
    tests += [([-d]*width,[d]*width),([(-1)**i*d for i in range(width)],[d]*width),
      ([rng.randrange(-15,16) for _ in range(width)],[rng.randrange(-15,16) for _ in range(width)])]
    tests += [([rng.randrange(16) for _ in range(width)],[rng.randrange(16) for _ in range(width)]) for _ in range(cases)]
    max_observed=F(0); counts=None
    for a,b in tests:
        counter={'complex_products':0,'butterflies':0}
        aa=fft([(x*q,0) for x in a]+[(0,0)]*width,tw,q,False,counter)
        bb=fft([(x*q,0) for x in b]+[(0,0)]*width,tw,q,False,counter)
        prod=[cmul(x,y,q,counter) for x,y in zip(aa,bb)]
        out=fft(prod,tw,q,True,counter)
        actual=schoolbook(a,b,n)
        recovered=[nearest(F(x,n*q)) for x,y in out]
        assert recovered==actual
        # Stronger than only comparing packed product: each coefficient exact.
        for (x,y),z in zip(out,actual):
            err=abs(F(x,n*q)-z)+abs(F(y,n*q))
            max_observed=max(max_observed,err)
        av=sum(v*16**i for i,v in enumerate(a)); bv=sum(v*16**i for i,v in enumerate(b))
        assert sum(v*16**i for i,v in enumerate(recovered))==av*bv
        assert counter['complex_products']==3*(n//2)*(n.bit_length()-1)+n
        counts=counter
    # Essential controls: equality at a half-step does not force recovery.
    assert nearest(F(1,2))!=0
    assert nearest(F(0))!=F(1,4) # missing integer-lattice membership
    # Minimal accepted bit count for THIS conservative sufficient bound.
    minbits=next(b for b in range(1,bits+1) if budget(n,d,b)['strict_half'])
    return {'status':'PASS','n':n,'digit_base':16,'max_operand_digits':width,
      'bits':bits,'tested_pairs':len(tests),'certificate':tc,'budget':bound,
      'smallest_bits_satisfying_this_bound':minbits,
      'max_observed_l1_coefficient_error':str(max_observed),
      'literal_counts':counts,'unshared_complex_products':6*(n//2)*(n.bit_length()-1)+n,
      'controls':{'half_step_boundary_rejects_universal_recovery':True,'lattice_membership_required':True},
      'evidence':'Exact rational executable checks plus paper all-input proof; not Lean kernel verification; not RAM64 or kappa certificate.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--n',type=int,default=512)
    ap.add_argument('--bits',type=int,default=40); ap.add_argument('--cases',type=int,default=12)
    ap.add_argument('--output'); args=ap.parse_args()
    result=run(args.n,args.bits,args.cases)
    output=json.dumps(result,indent=2)
    if args.output: Path(args.output).write_text(output+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('certificate','budget')},indent=2))



