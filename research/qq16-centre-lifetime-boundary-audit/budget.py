#!/usr/bin/env python3
"""Independent rational audit of PR3952's conditional centre-budget screen.

No predecessor arithmetic is imported. This is a conditional numerical lemma,
not an admission of a changed caller, family count, coverage or native schedule.
Chris R / Clear1nsight with OpenAI assistance. Apache-2.0.
"""
import json
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

A = F(836330098538459, 499163669901461541)
M = 73
W = F(896,9)
R = 51
BASE = {1:F(2428), 2:F(418), 3:F(432), 4:F(142), 5:F(82)}

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
def child(r):
    lo,hi=logarithm(F(M,r))
    lo,hi=exp_interval(A*lo,A*hi)
    return F(r,M)*lo,F(r,M)*hi

def moment(decoder_pair=112, retained_h8_pair=16, centre=64, w=W):
    """Fixed-total-mass relaxation, with all physical overhead set to zero."""
    require(decoder_pair>=0 and retained_h8_pair>=0 and centre>=0, 'failed: decoder_pair>=0 and retained_h8_pair>=0 and centre>=0')
    n=dict(BASE);n[1]+=F(decoder_pair,2);n[8]=F(retained_h8_pair,2)
    total=72*w+centre
    local=sum(r*v for r,v in n.items())
    idle=total-local
    require(idle>=0 and 2*R*R<M*M<2*(R+1)**2, 'failed: idle>=0 and 2*R*R<M*M<2*(R+1)**2')
    lo=sum(v*child(r)[0] for r,v in n.items())+idle/R*child(R)[0]
    hi=sum(v*child(r)[1] for r,v in n.items())+idle/R*child(R)[1]
    return lo/w,hi/w

def show(x,digits=18):
    lo,hi=x; s=10**digits
    l=lo.numerator*s//lo.denominator
    u=-((-hi.numerator*s)//hi.denominator)
    return {'lower':f'{l//s}.{l%s:0{digits}d}','upper':f'{u//s}.{u%s:0{digits}d}',
            'decision':'strict_pass' if hi<1 else 'strict_fail' if lo>1 else 'undecided'}

def calculate():
    fixed={str(h):show(moment(retained_h8_pair=h)) for h in [0,1,2,3,8,16]}
    require(moment(retained_h8_pair=2)[1]<1<moment(retained_h8_pair=3)[0], 'failed: moment(retained_h8_pair=2)[1]<1<moment(retained_h8_pair=3)[0]')
    require(moment(decoder_pair=61)[1]<1<moment(decoder_pair=62)[0], 'failed: moment(decoder_pair=61)[1]<1<moment(decoder_pair=62)[0]')
    require(moment(decoder_pair=336,retained_h8_pair=0)[0]>1, 'failed: moment(decoder_pair=336,retained_h8_pair=0)[0]>1')
    require(moment(decoder_pair=121,retained_h8_pair=0)[1]<1<moment(decoder_pair=122,retained_h8_pair=0)[0], 'failed: moment(decoder_pair=121,retained_h8_pair=0)[1]<1<moment(decoder_pair=122,retained_h8_pair=0)[0]')
    # Literal deletion of a pair H8 removes mean rank mass four. If all other
    # children and W were unchanged, centre decreases by exactly four as well.
    # This example is deliberately conditional: it has no schedule admission.
    literal={str(h):show(moment(retained_h8_pair=h,centre=4*h)) for h in [0,2,3,15,16]}
    # Incidence table: 112 children per decoder invocation; d/N=1/2 only for
    # the hypothetical pair model. A nine-call controller must supply integer d.
    incidence={str(d):show(moment(decoder_pair=F(224*d,9),retained_h8_pair=0)) for d in range(1,6)}
    # Sensitivity when one fewer productive family per nine-call replica is
    # retained but the local bill is held fixed; not a claim this is legal.
    changed_w={str(v):show(moment(retained_h8_pair=0,w=F(v,9))) for v in [896,895,880,768]}
    out={
        'status':'PASS_INDEPENDENT_CONDITIONAL_BUDGET',
        'arithmetic':'exact Fraction atanh logarithm,40 terms;exp14 with geometric tail',
        'a':str(A),'W':str(W),'fixed_centre':64,
        'fixed_total_h8_pair':fixed,
        'restored_full_consumer336_pair_h8_waived':show(moment(decoder_pair=336,retained_h8_pair=0)),
        'decoder_pair_integer_threshold_with16H8':{'61':show(moment(decoder_pair=61)),'62':show(moment(decoder_pair=62))},
        'decoder_pair_integer_threshold_with0H8':{'121':show(moment(decoder_pair=121,retained_h8_pair=0)),'122':show(moment(decoder_pair=122,retained_h8_pair=0))},
        'literal_deletion_hypothetical_total_changes':literal,
        'nine_call_hypothetical_decoder_incidence_rank8_waived':incidence,
        'changed_family_stock_hypothetical_fixed_local':changed_w,
        'scope':'Conditional arithmetic only. No continuation, family count, coverage, centre deletion, hosting, child placement or physical bill is admitted.'}
    return out

if __name__=='__main__':print(json.dumps(calculate(),indent=2,sort_keys=True))
