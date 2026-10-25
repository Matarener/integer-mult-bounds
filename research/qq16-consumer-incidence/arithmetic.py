#!/usr/bin/env python3
"""Exact arithmetic adapted from Clear1nsight PR3963, independently derived
atanh-series implementation. No predecessor module imported. Apache-2.0.
"""
from fractions import Fraction as F
from functools import lru_cache
M=73
def require(ok,msg):
    if not ok:raise ValueError(msg)

@lru_cache(None)
def log_unit(x, n=40):
    """ln x from the positive atanh series, with an exact geometric remainder."""
    require(1 <= x <= 2, 'failed: 1 <= x <= 2')
    z=(x-1)/(x+1)
    s=sum((2*z**(2*k+1)/F(2*k+1) for k in range(n)),F(0))
    tail=2*z**(2*n+1)/(F(2*n+1)*(1-z*z))
    return s,s+tail

@lru_cache(None)
def logarithm(x):
    require(x >= 1, 'failed: x >= 1')
    k=0
    while x>2:
        x/=2; k+=1
    lo,hi=log_unit(x)
    a,b=log_unit(F(2))
    return lo+k*a,hi+k*b

def exp_interval(lo,hi,n=14):
    require(0<=lo<=hi<F(1,2), 'failed: 0<=lo<=hi<F(1,2)')
    lower=upper=tl=tu=F(1)
    for k in range(1,n+1):
        tl*=lo/k;tu*=hi/k
        lower+=tl;upper+=tu
    first=tu*hi/(n+1)
    return lower,upper+first/(1-hi/(n+2))

@lru_cache(None)
def child(r,a):
    lo,hi=logarithm(F(M,r))
    lo,hi=exp_interval(a*lo,a*hi)
    return F(r,M)*lo,F(r,M)*hi


def enclosing(profile,a,live,total):
    mass=sum(r*n for r,n in profile.items());idle=total-mass
    require(idle>=0,'nonnegative idle mass');require(2*51**2<73**2<2*52**2,'idle cap')
    lo=sum(n*child(r,a)[0] for r,n in profile.items())+F(idle,51)*child(51,a)[0]
    hi=sum(n*child(r,a)[1] for r,n in profile.items())+F(idle,51)*child(51,a)[1]
    return lo/live,hi/live

def view(bounds):
    lo,hi=bounds;s=10**18
    l=lo.numerator*s//lo.denominator;u=-((-hi.numerator*s)//hi.denominator)
    return {'lower':f'{l//s}.{l%s:018d}','upper':f'{u//s}.{u%s:018d}',
            'decision':'strict_pass' if hi<1 else 'strict_fail' if lo>1 else 'undecided'}

def screens(producer,a,calls,live,sites):
    require((calls,live,sites)==(144,14336,16),'source-bound global incidence')
    total=72*live+64*calls
    def at(d):
        p=dict(producer);p[1]+=sites*d
        return enclosing(p,a,live,total)
    cases={str(d):view(at(d)) for d in [0,112,208,224,304,336,553,554]}
    require(at(553)[1]<1<at(554)[0],'one-stage1 module553/554 threshold')
    pair={1:2420+2436+336,2:836,3:864,4:284,5:164}
    pair_bounds=enclosing(pair,a,F(1792,9),F(14464))
    require(pair_bounds[0]>1 and at(336)[1]<1,'pair-rate failure must not transport')
    return {'selected_a':str(a),'family_count_assumed':live,'total_mass_assumed':total,
        'module_invocations_per_proposal':sites,'native_module_parameter_cases':cases,
        'strict_integer_native_H1_cap_per_stage1_module':553,
        'paired336_reference':view(pair_bounds),
        'scope':'All screens conditionally retain W=896/9,centre64 and ideal rank51 idle completion. Source cut counts are exact; a consumer, coverage, displaced remainder map and physical completion are not supplied.208/224/304 are parameter values, not certified sibling candidates.'}
