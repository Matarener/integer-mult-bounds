# SPDX-License-Identifier: Apache-2.0
# Exact atanh/alternating-exponential oracle retained from PR3863.
from fractions import Fraction as F
from certificate import need

def log_interval(n):
    k=0
    while n >= 2**(k+1): k+=1
    def unit(a,b):
        t=F(a-b,a+b);N=48
        s=2*sum((t**(2*j+1)/F(2*j+1) for j in range(N)),F(0))
        return s,s+2*t**(2*N+1)/(F(2*N+1)*(1-t*t))
    lo,hi=unit(n,2**k);l2,u2=unit(2,1)
    return lo+k*l2,hi+k*u2

def raw_power_interval(r,a):
    if r==0:return F(0),F(0)
    lo,hi=log_interval(r);lo*=a;hi*=a
    need(0<=lo<=hi<F(1,2),'oracle small argument')
    def alt(x,N):
        term=F(1);s=term
        for j in range(1,N+1):term*= -x/j;s+=term
        return s
    return r*alt(hi,25),r*alt(lo,26)

def gap_interval(old,new,a):
    lo=hi=F(0)
    for r,(o,n) in enumerate(zip(old,new)):
        l,u=raw_power_interval(r,a);d=o-n
        lo+=d*(l if d>=0 else u);hi+=d*(u if d>=0 else l)
    return lo,hi

