"""Independent rational moment certificate for the source-bound final profile.

The old clock/profile is PR3815 (Erwan Secousses), built on PR3734;
the comparison endpoint is PR3875. This checker imports no price evaluator.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from decimal import Decimal as D,localcontext
from pathlib import Path
import math,json,sys

OLD_PRICE_SHA256='f989112add9b51d3a9d8be458defafadc85d84add9a4f476ec0f81d7a72f1be0'
OLD_PROFILE={1:7989840,2:2349000,3:749088,4:330480,5:69120,8:25920,48:137952}
FULL_PROFILE={1:8041680,2:2306880,3:729648,4:353160,5:69120,8:25920,48:137952}
LOCAL_DELTA={1:42,2:-13,3:-6,4:7}
COPIES=3240
IDLE_CREDIT=84240
REPLICAS=360
LOWER=Q('0.001730663236534549309146')
UPPER=Q('0.001730663236534549309147')
OUTER_LOWER=LOWER-Q(1,10**46)-Q(1,10**70)
PREDECESSOR_UPPER=Q('0.001730578437266246818741')
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

def uniform_gain():
    l2,u2=logs(2);_,u3=logs(3)
    a,b,c=Q(6931,10000),Q(6932,10000),Q(10987,10000)
    need(a<l2 and u2<b and u3<c,'elementary logarithm bounds')
    derivative=56*a*(1-2*b/Q(500))-26*b-18*c
    need(derivative==Q(707951289,781250000)>Q(9,10),'uniform positive derivative')
    lo2,hi2=power_bounds(2,PREDECESSOR_UPPER)
    lo3,hi3=power_bounds(3,PREDECESSOR_UPPER)
    lo4,hi4=power_bounds(4,PREDECESSOR_UPPER)
    gain=outward(13*lo2+6*lo3-7*hi4-16,13*hi2+6*hi3-7*lo4-16)
    need(gain[0]>0,'strict predecessor gain')
    return derivative,gain

def controls():
    outcomes=[]
    def reject(label,fn):
        try:fn()
        except ValueError:outcomes.append(label);return
        raise ValueError('mutation was accepted: '+label)
    wrong=dict(FULL_PROFILE);wrong[1]+=1
    reject('one wrong aggregate rank1 count',lambda:certify_bracket(wrong))
    wrong=dict(FULL_PROFILE);wrong[1]+=IDLE_CREDIT
    reject('missing literal idle credit',lambda:certify_bracket(wrong))
    shift=Q(1,10**12)
    reject('unsupported larger endpoint',lambda:certify_bracket(FULL_PROFILE,LOWER+shift,UPPER+shift))
    return outcomes

def main():
    owner={int(rank):n for rank,n in json.loads((PACKAGE/'owner/PROFILE.json').read_text(encoding='utf8')).items()}
    need(owner==FULL_PROFILE,'owner profile and independent exact profile differ')
    expected=dict(OLD_PROFILE)
    for rank,n in LOCAL_DELTA.items():expected[rank]+=COPIES*n
    expected[1]-=IDLE_CREDIT
    need(expected==FULL_PROFILE,'literal aggregate profile assembly')
    need(COPIES==9*REPLICAS and IDLE_CREDIT==26*COPIES,'call and promoted-cell multiplicities')
    need(OUTER_LOWER>PREDECESSOR_UPPER,'strict endpoint improvement after inherited padding')
    old_upper_moment=moment(signed(OLD_PROFILE),PREDECESSOR_UPPER)
    need(old_upper_moment[0]>0,'certified conservative predecessor root upper bound')
    old_upper_with_margin=PREDECESSOR_UPPER-Q(1,10**46)-Q(1,10**70)
    need(moment(signed(OLD_PROFILE),old_upper_with_margin)[0]>0,'predecessor upper remains strict after margin comparison')
    ml,mh=certify_bracket(FULL_PROFILE);derivative,gain=uniform_gain()
    padded_moment=moment(signed(FULL_PROFILE),OUTER_LOWER)
    need(padded_moment[1]<0,'padded lower endpoint moment')
    with localcontext() as ctx:
        ctx.prec=100
        decimal_lower=format(D(LOWER.numerator)/D(LOWER.denominator),'.24f')
        decimal_upper=format(D(UPPER.numerator)/D(UPPER.denominator),'.24f')
    print(json.dumps({'status':'PASS_EXACT_PROFILE_ROOT','old_price_source_sha256':OLD_PRICE_SHA256,'full_profile':FULL_PROFILE,'owner_profile_matches':True,'comparison_count':896*REPLICAS,'comparison_rank':73,'root_lower':str(LOWER),'root_upper':str(UPPER),'lower_decimal':decimal_lower,'upper_decimal':decimal_upper,'outer_lower':str(OUTER_LOWER),'predecessor_root_upper':str(PREDECESSOR_UPPER),'predecessor_upper_moment_interval':list(map(str,old_upper_moment)),'strict_improvement_threshold':str(LOWER-PREDECESSOR_UPPER),'lower_moment_interval':list(map(str,ml)),'upper_moment_interval':list(map(str,mh)),'strict_uniform_derivative_lower':str(derivative),'per_local_call_gain_at_predecessor_interval':list(map(str,gain)),'rejected_controls':controls() if '--controls' in sys.argv else [],'scope':'Exact paid-profile comparison. Native phases, literal owner fill and inherited outer theorem hypotheses must be checked by the package replay.'},sort_keys=True))

if __name__=='__main__':main()
