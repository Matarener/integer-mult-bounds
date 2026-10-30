"""Declared finite coverage; seed4 chooses nonunit spectator witnesses."""
from random import Random
def cases():
    out=[];rng=Random(4)
    for precision in (1,3):
        n=193;f=3
        for name,a,b,c in (
            ('good',0,(128-14)*f,14*f),
            ('unit-across',2*f,70*f,f),
            ('pair-head',2*f,6*f,f),
            ('pair-tail',66*f,70*f,f),
            ('half-head',4*f,5*f-1,1),
            ('half-tail',68*f,69*f-1,1)):
            out.append(dict(name=name,q=3,w=precision,n=n,first=a,second=b,width=c,spectators=rng.sample([3,5,7,11,13,17],3)))
    out.extend([
        dict(name='recursive-good-width70',q=3,w=2,n=321,first=0,second=570,width=70,spectators=[1,3,5]),
        dict(name='q5-even-columns',q=5,w=2,n=129,first=4,second=140,width=2,spectators=[7,11,13]),
        dict(name='no-remainder-rank42',q=3,w=1,n=64,first=0,second=86,width=42,spectators=[1,1,1]),
    ])
    return out
