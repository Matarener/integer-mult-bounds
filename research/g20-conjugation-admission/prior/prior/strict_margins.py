"""Choose finite strict compiler margins for the retained G20 framework.

The caller supplies a certified positive first-moment reserve. The tail bounds
are checked separately on the complete profile. Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F


def need(ok,message):
    if not ok:raise ValueError(message)


def tensor_degree(reserve):
    need(F(0)<reserve<1,'positive certified reserve')
    need(F(31,32)**128<F(1,16) and F(19,20)**128<F(1,16),'retained tail blocks')
    v=1024
    while 1-F(1)/(1+v*reserve)-F(4,2**(v//32))<=0:
        v*=2
    return v


def compiler_cutoffs(tested,uniform,v):
    need(0<uniform<tested<F(1,100) and v>=1024 and v%1024==0,'strict compiler inputs')
    t,z=1-tested,1-uniform;z0=(t+z)/2;gap=z0-t;h=F(1,64)
    rhs=gap*(5+8*h)*v+1+8*v*(1-z0)
    h0=(rhs/(h*gap)).__floor__()+1
    h1=(h0*(1-z0)/(z-z0)).__floor__()+1
    need(h0>=8*v and h0*h*gap>rhs and h1*(z-z0)>h0*(1-z0),'strict finite cutoffs')
    return h0,h1


def below_grid(value,denominator):
    need(isinstance(denominator,int) and denominator>0,'positive grid denominator')
    out=F(-((-value.numerator*denominator)//value.denominator)-1,denominator)
    need(0<value-out<=F(1,denominator),'strict lower grid')
    return out


def controls():
    degrees={}
    for k in (8,39,48,96,192,384):
        reserve=F(1,2**k);v=tensor_degree(reserve)
        need(v%1024==0 and 1-F(1)/(1+v*reserve)>F(4,2**(v//32)),'positive exact contraction')
        degrees[str(k)]=v
    for value in (F(7,1000),F(701,100000),F(699,100000)):
        need(below_grid(value,1000)<value,'strict grid includes exact-grid inputs')
    try:tensor_degree(F(0))
    except ValueError:pass
    else:raise ValueError('zero reserve accepted')
    return degrees
