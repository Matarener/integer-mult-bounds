#!/usr/bin/env python3
"""Finite Fraction-only qualification of the strict single-use tail relaxation.

No source constructor, contact scan, native code, interval engine, real power,
logarithm or exponential routine. Analytic implications remain paper premises.
Chris R/Clear1nsight, OpenAI Codex assistance, Apache-2.0; lineage in CONTRACT.md.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
PRICE_SHA = '6ad37711165765c2f4f3fb9690e78b3db8b1fb6e8b91ff883b2f1286129f8335'
PRICE_PAIR_SHA = '1d99144de9f6d9411baeea842fcb0d3524ac2dbdc8e946c841b57ef430ed3805'
PRICE_REQUEST_SHA = 'd85ca5055168c84ca64a6c9b37dcc52fc61028134bfc6787fafc104a0b44cbe0'
LOG_SHA = '882369dbec747ac4fe4c324501dddca7e67240e773bb6782e29bd91dde25b5a7'
HEAD = 'af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf'
WORD_SHA = '12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticated(raw,expected,label):
    need(sha(raw) == expected,'byte authentication '+label)
    return json.loads(raw)


def histogram(data):
    return {int(r):Q(n) for r,n in data.items() if n}


def combine(*terms):
    out={}
    for factor,poly in terms:
        for r,n in poly.items():
            out[r]=out.get(r,Q(0))+factor*n
    return histogram(out)


def mass(poly):
    return sum((r*n for r,n in poly.items()),Q(0))


def show(poly):
    return {str(r):str(n) for r,n in sorted(poly.items()) if n}


def interval(data):
    lo,hi=(Q(data[k]) for k in ('lower_decimal_outward','upper_decimal_outward'))
    need(lo<hi,'strict inherited interval order')
    return lo,hi


def finite_log_brackets():
    bounds={2:(Q('0.6931'),Q('0.6932')),
            3:(Q('1.0986'),Q('1.0987')),
            5:(Q('1.6094'),Q('1.6095'))}
    for n,(lo,hi) in bounds.items():
        z=Q(n-1,n+1);z2=z*z;term=z;partial=Q(0)
        for j in range(32):
            partial += 2*term/Q(2*j+1)
            term *= z2
        tail=2*term/(65*(1-z2))
        need(lo<partial<partial+tail<hi and 0<tail<Q(1,10**10),'finite log enclosure '+str(n))
    return bounds


def derivatives(bounds,aggregate):
    l2,u2=bounds[2];l3,u3=bounds[3];l5,u5=bounds[5]
    l4,u4=2*l2,2*u2;l9,u9=2*l3,2*u3
    maximum=Q(17,5000)
    need(all(1-maximum*u>0 for u in (u4,u5,u9)),'positive linear exponential lower factors')
    slope=(18*l3-8*u2-5*u5,18*u3-8*l2-5*l5)
    need(slope==(Q(61817,10000),Q(7731,1250)),'g9 slope coefficient endpoints')
    second_lower=4*(1-maximum*u4)*l4*l4+5*(1-maximum*u5)*l5*l5-9*u9*u9
    second_upper=4*u4*u4+5*u5*u5-9*(1-maximum*u9)*l9*l9
    need(-23<second_lower<second_upper<-22,'strict coarse second derivative brackets')
    need(second_lower==Q(aggregate['g9_second_derivative_rational_lower']) and
         second_upper==Q(aggregate['g9_second_derivative_rational_upper']) and
         list(map(str,slope))==aggregate['g9_derivative_at_zero'] and
         aggregate['C_domain']==['0','17/5000'] and
         aggregate['g9_second_derivative_coarse']==['-23','-22'],'static derivative arithmetic match')
    return slope,(second_lower,second_upper)


def taylor(c,slope):
    need(0<c<=Q(17,5000),'strict positive Taylor evaluation domain')
    lo=slope[0]*c-Q(23,2)*c*c
    hi=slope[1]*c-11*c*c
    need(0<lo<hi,'Taylor integrated positive gain brackets')
    return lo,hi


def canonical_bill(n,debt):
    need(type(n) is int and n>=3,'declared canonical controller branch n>=3')
    a,d=(n-3)//2,(n-2)//2
    rest={1:Q(104*(n-3)),1+8*n:Q(-208)}
    for side in (a,d):
        for k in range(2,side+2):
            rest[8*k]=rest.get(8*k,Q(0))+208
            rest[8*k+1]=rest.get(8*k+1,Q(0))-208
    return combine((n,debt),(1,rest))


def full_invoice(n,paid,helpers):
    # Separate paid and independent productive ledgers, retaining every
    # query, both prefix/suffix whole-idle sequences, and every main bank.
    need(type(n) is int and n in (17,18),'qualified controller counts only')
    sides=((n-3)//2,(n-2)//2)
    queries={1:Q(104*(n-3))}
    idles={};banks={1+8*n:Q(208)}
    for length in sides:
        for j in range(1,length+1):
            rank=8*(j+1)
            idles[rank]=idles.get(rank,Q(0))+208
            banks[rank+1]=banks.get(rank+1,Q(0))+208
    return (combine((n,paid),(1,queries),(1,idles)),
            combine((n,helpers),(1,banks)),queries,idles,banks,sides)


def validate_complete(n,local_paid,local_helpers,paid,targets,expected_census):
    need(all(r>0 and v>0 and v.denominator==1 for h in (paid,targets) for r,v in h.items()),
         'positive integral complete ledger')
    need(combine((1,paid),(-1,targets))==canonical_bill(n,combine((1,local_paid),(-1,local_helpers))),
         'complete paid-minus-target polynomial equals canonical law')
    need(sum(paid.values())==expected_census['paid'] and sum(targets.values())==expected_census['targets'] and
         mass(targets)-mass(paid)==expected_census['surplus'],'complete invoice census')


def witness_groups(m):
    return [{'count':93,'paid_rank':4,'paid_start':0,'target_rank':9,'target_start':0,'new_paid':0,'new_target':5},
            {'count':m-93,'paid_rank':5,'paid_start':0,'target_rank':9,'target_start':93,'new_paid':0,'new_target':4}]


def apply_witness(paid,helpers,groups,expected_count):
    paid_seen=set();target_seen=set();pd={};hd={};gain={}
    for g in groups:
        count,c,r=g['count'],g['paid_rank'],g['target_rank']
        cp,rp=g['new_paid'],g['new_target'];k=c-cp
        need(all(type(x) is int for x in (count,c,r,cp,rp,k,g['paid_start'],g['target_start'])) and count>0,
             'integral multiset allocation')
        need(1<=k<=min(c,r-1) and c<=r<=9 and cp>=0 and rp==r-k>0,
             'strict single-use isolated nested-tail language')
        need({c,r-c}=={4,5} and r==9 and cp==0,'balanced g9 witness ranks')
        for index in range(count):
            pslot=(c,g['paid_start']+index);hslot=(r,g['target_start']+index)
            need(0<=pslot[1]<paid.get(c,0) and 0<=hslot[1]<helpers.get(r,0),'original inventory allocation')
            need(pslot not in paid_seen,'distinct old terminal paid-job multiset slots')
            need(hslot not in target_seen,'distinct old independent helper-target multiset slots')
            paid_seen.add(pslot);target_seen.add(hslot)
        pd[c]=pd.get(c,Q(0))-count;hd[r]=hd.get(r,Q(0))-count
        if cp:pd[cp]=pd.get(cp,Q(0))+count
        hd[rp]=hd.get(rp,Q(0))+count
        gain=combine((1,gain),(count,{c:1,rp:1,r:-1}),(-count,{cp:1} if cp else {}))
    need(len(paid_seen)==len(target_seen)==expected_count,'exact single-use exchange count')
    new_p,new_h=combine((1,paid),(1,pd)),combine((1,helpers),(1,hd))
    need(all(v>0 for h in (new_p,new_h) for v in h.values()),'nonnegative resulting inventories')
    need(sum(new_h.values())==sum(helpers.values())==527,'no new or double-credited independent targets')
    need(mass(new_p)-mass(new_h)==mass(paid)-mass(helpers)==1720,'local debt conserved')
    need(gain=={4:Q(expected_count),5:Q(expected_count),9:Q(-expected_count)},'exact total balanced reward')
    need(combine((1,paid),(-1,helpers),(-1,new_p),(1,new_h))==gain,'complete signed local gain identity')
    return new_p,new_h,pd,hd


def positive_budget(n,m,gain,b17,j17,extra_global=Q(0)):
    need(n in (17,18),'controller nomination domain')
    b=b17 if n==17 else (b17[0]+j17[0]/306,b17[1]+j17[1]/306)
    per=(m*gain[0]-b[1],m*gain[1]-b[0])
    total=(n*per[0]-extra_global,n*per[1]-extra_global)
    need(0<total[0]<total[1]<1,'strict positive complete slack below one global H1')
    return b,per,total


def rejected(operation,label,strength):
    try:
        operation()
    except ValueError:
        return {'outcome':'rejected','strength':strength}
    raise ValueError('mutation accepted '+label)


# Pure helpers reused from the frozen historical preparatory checker.
# Its main() and historical execution path are deliberately absent.
