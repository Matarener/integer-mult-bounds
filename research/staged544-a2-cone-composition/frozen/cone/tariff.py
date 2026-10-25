"""Exact tariff arithmetic adapted from PR3988, Chris R with OpenAI Codex.
Dual credited to PR3815/3862/3890. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse, gzip, hashlib, importlib.util, json, math
ROOT=Path(__file__).resolve().parent
K=Q(1730663236534549309146,10**24)

def need(ok,why):
    if not ok: raise ValueError(why)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(*terms):
    out=Counter()
    for factor,v in terms:
        for r,c in v.items():out[r]+=factor*c
    return {r:c for r,c in out.items() if c and r}
def h(r):return {r:Q(1)} if r else {}
def log_ratio(x):
    z=(x-1)/(x+1);n=50
    value=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(n)),Q(0))
    tail=2*z**(2*n+1)/(Q(2*n+1)*(1-z*z))
    return value,value+tail
@lru_cache(None)
def power(r):
    if r==0:return Q(0),Q(0)
    j=r.bit_length()-1;l2,u2=log_ratio(Q(2));lr,ur=log_ratio(Q(r,2**j))
    a,b=K*(j*l2+lr),K*(j*u2+ur)
    need(0<=a<=b<1,'exponential range')
    def exp_minus(x,n):return sum(((-x)**i/Q(math.factorial(i)) for i in range(n+1)),Q(0))
    return r*exp_minus(b,19),r*exp_minus(a,20)
def interval(v):
    lo=hi=Q(0)
    for r,c in v.items():
        a,b=power(r);lo+=c*(a if c>=0 else b);hi+=c*(b if c>=0 else a)
    return lo,hi
def brief(ab):
    scale=10**24;lo,hi=ab
    return {'lower_numerator':lo.numerator*scale//lo.denominator,'upper_numerator':-((-hi.numerator*scale)//hi.denominator),'denominator':scale}
def patterns():
    for cap in (8,16,32,48):
        def rec(i,ns,left):
            if i==5:
                yield cap,tuple(ns),left;return
            for n in range(left//(i+5)+1):yield from rec(i+1,ns+[n],left-n*(i+5))
        yield from rec(0,[],cap)
def dual():
    q={48:Q(1,20),3:Q(-1,20),5:Q(-1,4)}
    pi={w:add((-1,h(5)),(-(w-5),q)) for w in range(5,10)}
    mu={8:add((-1,pi[8])),16:add((-2,pi[8])),32:add((-4,pi[8])),48:h(48)}
    return q,pi,mu
def reduced(cap,ns,left,pi,mu):return add((1,h(left)),(-1,mu[cap]),*((-n,pi[w]) for w,n in zip(range(5,10),ns)))
def dual_check():
    q,pi,mu=dual();tight=[];strict=[]
    for cap,ns,left in patterns():
        v=reduced(cap,ns,left,pi,mu)
        if not v:tight.append([cap,list(ns),left])
        else:
            ab=interval(v);need(ab[0]>0,'dual infeasibility');strict.append(ab)
    gap=interval(add((1,h(9)),(-1,h(8)),(-1,q)));need(gap[0]>Q(6,1000),'terminal budget gap')
    # Independently test every discrete marginal, not only the analytic minimum.
    for r in range(1,10):need(interval(add((1,h(r)),(-1,h(r-1)),(-1,q)))[0]>0,'marginal budget')
    return {'patterns':len(tight)+len(strict),'tight_patterns':tight,'strict_patterns':len(strict),
      'minimum_strict_reduced_cost':brief((min(x[0] for x in strict),min(x[1] for x in strict))),
      'idle_credit_per_dimension':brief(interval(q)),
      'minimum_terminal_charge_per_dimension':brief(interval(add((1,h(9)),(-1,h(8))))),
      'mandatory_interior_saving_per_dimension':brief(gap)}
