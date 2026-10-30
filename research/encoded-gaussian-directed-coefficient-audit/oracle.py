"""Independent rational arcsine / alternating-decay oracle. Apache-2.0.
JoyboyBrian with substantial OpenAI Codex assistance. No source imports.
"""
from fractions import Fraction as Q
from functools import lru_cache


def need(ok,why):
    if not ok:raise ValueError(why)


def down(x,T):return Q((x*(1<<T)).__floor__(),1<<T)
def up(x,T):return Q((x*(1<<T)).__ceil__(),1<<T)


@lru_cache(None)
def pi_box(T):
    # pi=6 asin(1/2). Positive successive-term ratio is <1/4.
    term=Q(1,2);total=Q();n=0
    while True:
        total+=term
        term*=Q((2*n+1)**2,8*(n+1)*(2*n+3));n+=1
        if 8*term<Q(1,1<<(T+4)):break
    return down(6*total,T),up(6*total+8*term,T)


def decay_point(x,T):
    need(0<=x<=Q(1,4),'independent alternating range')
    # Even/odd partial sums straddle exp(-x); no source positive series.
    term=Q(1);total=Q(1);n=0
    while True:
        n+=1;term*=x/n
        total+=term if n%2==0 else -term
        following=term*x/(n+1)
        other=total-following if n%2==0 else total+following
        if following<Q(1,1<<(T+4)):
            return down(min(total,other),T),up(max(total,other),T)


def interval(f,P,growth=False,sigma=0):
    need(f>=0 and type(P) is int and P>=1 and type(sigma) is int and sigma>=0,'oracle domain')
    if f==0:return Q(1,1<<sigma),Q(1,1<<sigma)
    F=max(1,f.__ceil__());T=P+16*F+48
    lo,hi=pi_box(T);xlo=f*lo;xhi=f*hi;k=0
    while xhi>Q(1,4):xlo/=2;xhi/=2;k+=1
    lower=decay_point(xhi,T)[0];upper=decay_point(xlo,T)[1]
    for _ in range(k):lower=down(lower*lower,T);upper=up(upper*upper,T)
    need(lower>0,'oracle reciprocal denominator')
    if growth:lower,upper=1/upper,1/lower
    lower/=1<<sigma;upper/=1<<sigma
    need(upper-lower<Q(1,1<<(P+10)),'independent oracle resolution')
    return lower,upper


def self_tests():
    lo,hi=pi_box(80)
    need(Q(314159,100000)<lo<hi<Q(314160,100000),'independent pi familiar rational bounds')
    cases=0
    for f in (Q(0),Q(1,1000),Q(1,4),Q(1),Q(4)):
        for P in (1,8,24):
            for sigma in (0,3):
                dec=interval(f,P,False,sigma);grow=interval(f,P,True,sigma)
                need(dec[0]<=dec[1] and grow[0]<=grow[1],'ordered independent intervals')
                need(dec[0]*grow[0]<=Q(1,1<<(2*sigma))<=dec[1]*grow[1],'growth decay reciprocal identity')
                cases+=2
    # Exact alternating tail sign and scaling controls.
    l,u=decay_point(Q(0),32);need(l==u==1,'zero alternating series')
    need(interval(Q(0),4,True,7)==(Q(1,128),Q(1,128)),'binary normalization exact')
    return {'intervals':cases,'pi_method':'positive arcsine with geometric tail','exp_method':'alternating decay with rational endpoint evaluation and outward squaring'}


if __name__=='__main__':print(self_tests())
