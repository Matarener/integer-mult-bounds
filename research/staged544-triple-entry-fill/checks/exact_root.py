"""Independent rational moment certificate for the staged-entry final profile.

Comparison: PR3945 (Dugongue), root bracket [0.001730663236534549309146, 0.001730663236534549309147].
Rational log/exp enclosures are PR3945's checks/exact_root.py, unchanged (Dugongue, OpenAI Codex assisted).
Adaptation: Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from decimal import Decimal as D,localcontext
from pathlib import Path
import math,json,sys

OLD_PROFILE={1:8041680,2:2306880,3:729648,4:353160,5:69120,8:25920,48:137952}
FULL_PROFILE={1:8061120,2:2313360,3:745362,4:330480,5:66690,8:25920,48:138438}
LOCAL_DELTA={1:6,2:2,3:5,4:-7}
IDLE_DELTA={3:-486,5:-2430,48:486}
COPIES=3240
REPLICAS=360
LOWER=Q('0.001730809033576552081734')
UPPER=Q('0.001730809033576552081735')
OUTER_LOWER=LOWER-Q(1,10**46)-Q(1,10**70)
PREDECESSOR_LOWER=Q('0.001730663236534549309146')
PREDECESSOR_UPPER=Q('0.001730663236534549309147')
PACKAGE=Path(__file__).resolve().parent.parent

def need(ok,why):
    if not ok:raise ValueError(why)

def outward(lo,hi,digits=60):
    scale=10**digits
    lower=(lo.numerator*scale)//lo.denominator
    upper=-((-hi.numerator*scale)//hi.denominator)
    return Q(lower,scale),Q(upper,scale)

@lru_cache(None)
def logs(rank):
    need(type(rank) is int and 1<=rank<=73,'rank range')
    def small(x):
        z=(x-1)/(x+1);N=120
        S=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(N)),Q())
        tail=2*z**(2*N+1)/(Q(2*N+1)*(1-z*z))
        return S,S+tail
    e=rank.bit_length()-1;a,b=small(Q(rank,1<<e));c,d=small(Q(2))
    return outward(a+e*c,b+e*d,80)

def exp_minus_interval(lo,hi):
    need(0<=lo<=hi<1,'Taylor alternating range')
    def partial(x,n):return sum(((-x)**j/Q(math.factorial(j)) for j in range(n+1)),Q())
    return partial(hi,25),partial(lo,24)

def power_bounds(rank,k):
    lo,hi=logs(rank);el,eh=exp_minus_interval(k*lo,k*hi)
    return rank*el,rank*eh

def moment(profile,k):
    need(0<k<Q(1,100),'exponent range')
    lo=hi=Q()
    for rank,n in profile.items():
        need(type(n) is int,'integer coefficient')
        l,u=power_bounds(rank,k)
        lo+=n*(l if n>=0 else u);hi+=n*(u if n>=0 else l)
    return outward(lo,hi)

def signed(profile):return {**profile,73:-896*REPLICAS}

def certify_bracket(profile,lower=LOWER,upper=UPPER):
    need(lower<upper,'ordered bracket')
    ml,mh=moment(signed(profile),lower),moment(signed(profile),upper)
    need(ml[1]<0<mh[0],'strict opposite moment signs')
    # Dividing the moment by 73^(1-k) leaves a strictly increasing function:
    # each positive term is count*(rank/73)^(1-k), with rank<73.
    need(all(n>0 and rank<73 for rank,n in profile.items()),'positive normalized monotonicity')
    return ml,mh

def controls():
    outcomes=[]
    def reject(label,fn):
        try:fn()
        except ValueError:outcomes.append(label);return
        raise ValueError('mutation was accepted: '+label)
    wrong=dict(FULL_PROFILE);wrong[1]+=1
    reject('one wrong aggregate rank1 count',lambda:certify_bracket(wrong))
    wrong=dict(FULL_PROFILE)
    for r,n in IDLE_DELTA.items():wrong[r]-=n
    wrong[1]+=sum(r*n for r,n in IDLE_DELTA.items())
    reject('idle change replaced by rank-1 cells',lambda:certify_bracket(wrong))
    shift=Q(1,10**12)
    reject('unsupported larger endpoint',lambda:certify_bracket(FULL_PROFILE,LOWER+shift,UPPER+shift))
    reject('PR3945 profile at the new bracket',lambda:certify_bracket(OLD_PROFILE))
    return outcomes

def main():
    owner={int(rank):n for rank,n in json.loads((PACKAGE/'owner/PROFILE.json').read_text(encoding='utf8')).items()}
    need(owner==FULL_PROFILE,'owner profile and independent exact profile differ')
    expected=dict(OLD_PROFILE)
    for rank,n in LOCAL_DELTA.items():expected[rank]+=COPIES*n
    for rank,n in IDLE_DELTA.items():expected[rank]+=n
    need(expected==FULL_PROFILE,'literal aggregate profile assembly')
    need(sum(r*n for r,n in LOCAL_DELTA.items())==-3 and sum(r*n for r,n in IDLE_DELTA.items())==3*COPIES,'three width units move from paid local cells to idle')
    need(COPIES==9*REPLICAS,'call multiplicity')
    old_lo,old_hi=moment(signed(OLD_PROFILE),PREDECESSOR_LOWER),moment(signed(OLD_PROFILE),PREDECESSOR_UPPER)
    need(old_lo[1]<0<old_hi[0],'certified PR3945 root bracket')
    need(OUTER_LOWER>PREDECESSOR_UPPER,'strict endpoint improvement after inherited padding')
    ml,mh=certify_bracket(FULL_PROFILE)
    padded_moment=moment(signed(FULL_PROFILE),OUTER_LOWER)
    need(padded_moment[1]<0,'padded lower endpoint moment')
    with localcontext() as ctx:
        ctx.prec=100
        decimal_lower=format(D(LOWER.numerator)/D(LOWER.denominator),'.24f')
        decimal_upper=format(D(UPPER.numerator)/D(UPPER.denominator),'.24f')
        outer=format(D(OUTER_LOWER.numerator)/D(OUTER_LOWER.denominator),'.70f')
    print(json.dumps({'status':'PASS_EXACT_PROFILE_ROOT','full_profile':FULL_PROFILE,'owner_profile_matches':True,'comparison_count':896*REPLICAS,'comparison_rank':73,
                      'root_lower':str(LOWER),'root_upper':str(UPPER),'lower_decimal':decimal_lower,'upper_decimal':decimal_upper,'outer_lower':str(OUTER_LOWER),'outer_lower_decimal':outer,
                      'pr3945_root_bracket':[str(PREDECESSOR_LOWER),str(PREDECESSOR_UPPER)],'pr3945_bracket_moments':[list(map(str,old_lo)),list(map(str,old_hi))],
                      'gain_over_pr3945_upper_at_least':str(OUTER_LOWER-PREDECESSOR_UPPER),'lower_moment_interval':list(map(str,ml)),'upper_moment_interval':list(map(str,mh)),
                      'rejected_controls':controls() if '--controls' in sys.argv else [],
                      'scope':'Exact paid-profile comparison. Native phases, literal owner fill and inherited outer theorem hypotheses are checked by the package replay.'},sort_keys=True))

if __name__=='__main__':main()
