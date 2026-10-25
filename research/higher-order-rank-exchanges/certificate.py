# SPDX-License-Identifier: Apache-2.0
"""Sufficient higher-order power-profile exchanges and paid interval credits.
Dugongue with substantial OpenAI Codex assistance. See PROOF.md.
"""
from fractions import Fraction as F
from math import comb, prod

def need(ok,message):
    if not ok:raise ValueError(message)

def stencil(order,start=1,step=1):
    need(type(order) is int and 2<=order<=12,'implementation order domain 2..12')
    need(type(start) is int and start>=1 and type(step) is int and step>=1,'positive integer grid')
    return {start+j*step:(-1)**j*comb(order,j) for j in range(order+1)}

def sum_distribution(order,boxes):
    need(type(order) is int and 2<=order<=12,'order')
    need(type(boxes) is int and 1<=boxes<=128,'bounded grid 1..128')
    coefficients=[1]
    for _ in range(order):
        out=[0]*(len(coefficients)+boxes-1)
        for i,c in enumerate(coefficients):
            for j in range(boxes):out[i+j]+=c
        coefficients=out
    need(sum(coefficients)==boxes**order,'cube-cell count')
    return coefficients

def credit(order,start,step,lower,upper,boxes=16):
    stencil(order,start,step)
    need(type(lower) is F and type(upper) is F and 0<lower<=upper<1,'exact saving interval')
    A=lower*(1-upper)*prod((lower+j for j in range(1,order-1)),start=F(1))
    coefficients=sum_distribution(order,boxes)
    total=F(0)
    for s,c in enumerate(coefficients):
        R=F(start)+F((s+order)*step,boxes)
        total+=F(c)/(R**(order-1)*(1+upper*(R-1)))
    return A*F(step,boxes)**order*total

def capped_sums(delta):
    return {k:sum(v*min(r,k) for r,v in delta.items()) for k in range(1,max(delta)+1)}

def certify(profile,dimension,moves,lower,upper,overhead=None,boxes=16):
    need(type(dimension) is int and dimension>1,'dimension')
    need(type(profile) is dict and profile and all(type(r) is int and 0<r<dimension and
         type(n) is int and n>=0 for r,n in profile.items()),'legal finite profile')
    need(type(moves) is list and moves,'nonempty positive stencil list')
    new=dict(profile);total=F(0);records=[]
    for move in moves:
        need(type(move) is dict and set(move)=={'order','start','step','copies'},'exact move schema')
        n,x,h,copies=(move[k] for k in ('order','start','step','copies'))
        need(type(copies) is int and copies>0,'positive integer copies')
        d=stencil(n,x,h)
        need(max(d)<dimension,'all recursive child ranks below dimension')
        need(sum(d.values())==0 and sum(r*v for r,v in d.items())==0,'count/mass identity')
        unit=credit(n,x,h,lower,upper,boxes)
        for r,v in d.items():new[r]=new.get(r,0)+copies*v
        total+=copies*unit
        records.append(move|{'signed_stencil':{str(r):v for r,v in d.items()},
                            'capped_sums':{str(k):v for k,v in capped_sums(d).items()},
                            'unit_raw_credit':str(unit)})
    need(all(v>=0 for v in new.values()),'insufficient aggregate source inventory')
    need(sum(r*n for r,n in new.items())==sum(r*n for r,n in profile.items()),'aggregate rank mass')
    extra={} if overhead is None else overhead
    need(type(extra) is dict and all(type(r) is int and 0<r<dimension and
         type(n) is int and n>=0 for r,n in extra.items()),'overhead profile')
    Q=sum(r*n for r,n in extra.items())
    need(Q<total,'overhead not below sufficient credit')
    for r,n in extra.items():new[r]=new.get(r,0)+n
    return {'saving_interval':[str(lower),str(upper)],'boxes':boxes,'moves':records,
            'total_raw_credit':str(total),'overhead_rank_mass':Q,
            'net_raw_credit':str(total-Q),'charged_profile':{str(r):n for r,n in sorted(new.items())}}
