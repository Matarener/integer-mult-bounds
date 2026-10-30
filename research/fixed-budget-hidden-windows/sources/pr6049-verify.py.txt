"""Sharp hidden-window family: exact algebra and sign checks. Apache-2.0."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent


def need(ok,msg):
    if not ok:
        raise ValueError(msg)


def mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y
    return out


def poly(h,u,v):
    need(isinstance(h,int) and 1<=h<=8,'h domain')
    need(F(1)<u<v<F(2),'root domain')
    out=[(-1)**(h+1)]
    for _ in range(h):
        out=mul(out,[-1,1]);out=mul(out,[-2,1])
    return mul(mul(out,[-u.numerator,u.denominator]),[-v.numerator,v.denominator])


def deriv(q):
    return [i*q[i] for i in range(1,len(q))] or [0]


def ev(q,x):
    out=F(0)
    for c in reversed(q):
        out=out*x+c
    return out


def validate(q,h):
    need(len(q)==2*h+3 and all(q),'exact support')
    need(all(q[j]*q[j+1]<0 for j in range(len(q)-1)),'alternating coefficients')
    d=q
    for _ in range(h):
        need(ev(d,1)==ev(d,2)==0,'endpoint multiplicity')
        d=deriv(d)
    need(ev(d,1)!=0 and ev(d,2)!=0,'exact endpoint order')
    old={2**i:-c for i,c in enumerate(q) if c<0}
    new={2**i:c for i,c in enumerate(q) if c>0}
    need(sum(old.values())==sum(new.values()),'count')
    mass=sum(r*n for r,n in old.items())
    need(mass==sum(r*n for r,n in new.items()),'mass')
    need(mass>max(old.keys()|new.keys()),'target larger than paid')
    return old,new,mass


def pow_bounds(p,bits=40):
    need(F(0)<p<F(1),'exponent domain')
    a,b=p.numerator,p.denominator
    need(b<=2048 and bits<=100,'bounded integer-power work')
    d=1<<bits
    n=(2**a)*(d**b)
    lo,hi=d,2*d
    while lo+1<hi:
        mid=(lo+hi)//2
        if mid**b<=n:lo=mid
        else:hi=mid
    need(lo**b<=n<(lo+1)**b,'power bounds')
    return F(lo,d),F(lo+1,d)


def sign_power_minus(p,u):
    a,b=p.numerator,p.denominator
    need(b<=2048,'bounded sign work')
    delta=(2**a)*(u.denominator**b)-u.numerator**b
    return (delta>0)-(delta<0)


def sign_factored(p,u,v):
    return -sign_power_minus(p,u)*sign_power_minus(p,v)


def gap(a,b):
    need(F(0)<=a<b<=F(1),'gap domain')
    p=a+(b-a)/3
    q=a+2*(b-a)/3
    _,u=pow_bounds(p)
    v,_=pow_bounds(q)
    need(u<v,'root separation')
    need(sign_power_minus(a,u)<0 and sign_power_minus(b,v)>0,'roots inside gap')
    return u,v,(a+b)/2


def rejected(fn):
    try:fn()
    except ValueError:return
    raise ValueError('control accepted')


def expanded_sign(q,p):
    lo,hi=pow_bounds(p,100)
    lower=upper=F(0)
    for i,c in enumerate(q):
        aa,bb=lo**i,hi**i
        lower+=c*(aa if c>0 else bb)
        upper+=c*(bb if c>0 else aa)
    need(lower>0 or upper<0,'expanded sign unresolved')
    return 1 if lower>0 else -1


def main():
    root=HERE.parents[1]
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage']=='input':
            need(hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256'],'source bytes')
    witnesses=samples=0
    for n in range(2,25):
        for k in range(n):
            a,b=F(k,n),F(k+1,n)
            u,v,mid=gap(a,b)
            q=poly(1,u,v);validate(q,1)
            need(sign_factored(mid,u,v)==1,'hidden loss')
            for j in range(1,n):
                need(sign_factored(F(j,n),u,v)==-1,'sample win')
                samples+=1
            witnesses+=1
    center=F(319,320)
    for bits in (24,32,40):
        u,v=pow_bounds(center,bits)
        for h in range(1,9):
            q=poly(h,u,v);validate(q,h)
            need(sign_factored(center,u,v)==1,'narrow hidden loss')
            need(sign_factored(F(9,10),u,v)==-1,'narrow left sample')
            need(sign_factored(F(999,1000),u,v)==-1,'narrow right sample')
            witnesses+=1
    q=poly(1,F(5,4),F(3,2))
    need(q==[30,-89,97,-46,8],'literal polynomial')
    old,new,mass=validate(q,1)
    need((sum(old.values()),mass)==(135,546),'literal count/mass')
    for p,want in ((F(1,4),-1),(F(1,2),1),(F(3,4),-1)):
        need(expanded_sign(q,p)==want==sign_factored(p,F(5,4),F(3,2)),'expanded oracle')
    need(256**2>2*181**2,'exact square-root loss')
    rejected(lambda:validate(q,2))
    bad=q.copy();bad[0]+=1
    rejected(lambda:validate(bad,1))
    rejected(lambda:poly(1,F(3,2),F(5,4)))
    rejected(lambda:poly(0,F(5,4),F(3,2)))
    rejected(lambda:need(sign_factored(F(1,2),F(5,4),F(3,2))==-1,'reversed sign'))
    print(json.dumps(dict(status='PASS_HIDDEN_POWER_WINDOWS',witnesses=witnesses,
                         sampled_wins=samples,minimal_support_h1=5,
                         scope='sharp scoped proof; synthetic invoices; no new kappa'),sort_keys=True))


if __name__=='__main__':main()
