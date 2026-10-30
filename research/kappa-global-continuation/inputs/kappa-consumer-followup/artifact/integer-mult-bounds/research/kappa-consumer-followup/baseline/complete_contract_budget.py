#!/usr/bin/env python3
"""Exact complete-invoice tests for original and zero-repair changed contracts.

All prices are conditional on retaining the stated m=73 productive denominator
and all inherited PR3734 costs. This file supplies no missing global consumer.
SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under user direction.
"""
from fractions import Fraction as F
from decimal import Decimal, localcontext
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("baseline_price",HERE/"audit.py")
a=importlib.util.module_from_spec(s);s.loader.exec_module(a)


def budget(endpoint,repairs):
    profile=dict(a.BASE)
    profile[8]-=8*a.CALLS
    profile[1]+=repairs*a.CALLS
    c=a.weighted(profile,a.M,endpoint)
    allowance=((a.W-c[1])/a.T,(a.W-c[0])/a.T)
    out={"a":a.decimal(endpoint),"per_call_rank_one_repairs":repairs,
        "conditional_existing_profile":profile,
        "budget_in_normalized_C73_families":a.interval(*allowance),
        "assumptions":"Original m=73,W=322560 and all inherited costs remain; only eight centre children per call are removed, with the stated repair count. Additional productive fields count only after a correct complete endpoint is proved.",
        "general_test":"added normalized child cost per replica minus added correctly productive families per replica must be less than budget_in_normalized_C73_families",
        "max_fields_by_tariff":{},"controls":{}}
    for r in [1,7,8,9,73]:
        out["max_fields_by_tariff"][str(r)]=a.interval(*a.quotient_positive(allowance,a.cost(r,a.M,endpoint)))
    for n,r in [(70,8),(71,8),(72,8),(8,73),(896,1)]:
        q=dict(profile);q[r]=q.get(r,0)+n*a.T
        v=a.moment(q,a.M,a.W,endpoint)
        out["controls"][f"add_{n}_H{r}"]={"M_minus_one":a.interval(v[0]-1,v[1]-1),"passes":v[1]<1}
    for n in [6,7,8]:
        v=a.moment(profile,a.M,a.W-n*a.T,endpoint)
        out["controls"][f"reserve_{n}_formerly_productive_families"]={"M_minus_one":a.interval(v[0]-1,v[1]-1),"passes":v[1]<1,
            "scope":"No added child cost, but these outputs are unavailable as correctly transformed productive inputs, so their count is removed from W."}
    return out


def mixed_zero_label_screen(fields):
    """An optimistic lower invoice under explicitly unconstructed hypotheses."""
    m,w=81,1024
    profile={r:9*n for r,n in a.LOCAL.items() if r!=8}
    remaining=36418
    profile[57]=F(remaining,57)
    assert sum(r*n for r,n in profile.items())==82048
    profile[8]=fields
    with localcontext() as ctx:
        ctx.prec=85
        terms=[]
        for r,n in profile.items():
            q=F(r*n,m*w)
            terms.append((Decimal(q.numerator)/q.denominator,(Decimal(m)/r).ln()))
        lo,hi=Decimal(0),Decimal("0.01")
        for _ in range(220):
            x=(lo+hi)/2
            if sum(p*(x*l).exp() for p,l in terms)<1:lo=x
            else:hi=x
        d=int(lo*10**24)
    lower,upper=F(d,10**24),F(d+1,10**24)
    ml=a.moment(profile,m,w,lower);mu=a.moment(profile,m,w,upper)
    assert ml[1]<1<mu[0]
    target=a.moment(profile,m,w,a.TARGET)
    return {"terminal_H8_fields":fields,"optimistic_root_bracket":[a.decimal(lower),a.decimal(upper)],
        "lower_endpoint_residual":a.interval(ml[0]-1,ml[1]-1),"upper_endpoint_residual":a.interval(mu[0]-1,mu[1]-1),
        "target_residual":a.interval(target[0]-1,target[1]-1),"target_passes_optimistic_price":target[1]<1,
        "profile_with_fractional_idle_multiplicity":{str(r):str(n) for r,n in profile.items()},
        "assumptions":"Unconstructed mixed112 norm-one +16 zero-label geometry: m81,W1024,N9,coverage mass82048 before consumer; local profile5070, remaining mass36418; every idle child has rank at most57. Charge all remaining mass at the cheapest allowed fractional H57 tariff. No integral allocation, native controller, decoder, or kappa claim.",
        "bound_direction":"Conditional optimistic lower bound on cost: for a>0, r^(1-a)/r=r^(-a) decreases with r, so all idle mass at rank57 is cheapest under the stated cap."}


def main():
    out={"status":"PASS_EXACT_CONDITIONAL_CONSUMER_BUDGETS","cases":{}}
    for name,v in [("user_target",a.TARGET),("retained_bit_cap",a.BIT_LO),("reported_R437_cap",a.R437_REPORTED)]:
        out["cases"][name]={str(r):budget(v,r) for r in [0,8]}
    p=dict(a.BASE);p[8]-=8*a.CALLS;p[1]+=896*a.T
    assert sum(r*n for r,n in p.items())==a.M*a.W
    assert all(0<r<a.M for r,n in p.items() if n)
    assert a.moment(p,a.M,a.W,F(0))[0]<=1<=a.moment(p,a.M,a.W,F(0))[1]
    assert a.moment(p,a.M,a.W,a.TARGET)[0]>1
    out["whole_bank_H1_flatten"]={"rank_mass":sum(r*n for r,n in p.items()),"normalizer_rank_mass":a.M*a.W,
        "M_at_zero":"exactly 1","positive_endpoint_result":"strictly fails every a>0",
        "proof":"The 896 H1 consumer adds 320 rank units beyond the deleted 576 centre units per replica, exactly exhausting the original 320-unit deficit. Every nonzero remaining child has rank r<m, so (r/m)^(1-a) is strictly increasing in a.",
        "scope":"This excludes only the fully charged 896-H1 flatten consumer for the zero-repair local deletion on the unchanged m73 invoice."}
    out["unconstructed_m81_zero_label_screen"]={str(n):mixed_zero_label_screen(n) for n in [70,71,72]}
    (HERE/"COMPLETE-CONTRACT-BUDGET.json").write_text(json.dumps(out,indent=2)+"\n")
    print(out["status"])
    for name,row in out["cases"].items():
        print(name,"zero-repair H8 budget",row["0"]["max_fields_by_tariff"]["8"]["decimal"][0])
    print("whole-bank H1 flatten: exact root 0, every positive a fails")


if __name__=="__main__":main()
