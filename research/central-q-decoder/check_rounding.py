"""Exact finite corroboration of the unitary rounding theorem, separate toy cells.
These are small noncommuting code fixtures, not a rounded whole native caller.
"""
from fractions import Fraction as F
import json

def need(ok,msg):
    if not ok:raise ValueError(msg)
def energy(v):return sum(a*a+b*b for a,b in v)
def qlayer(v,f,bit):
    size=1<<(2*f);out=[]
    for i,(a,b) in enumerate(v):
        owner,x=divmod(i,size);c,d=v[owner*size+(x^(1<<bit))]
        out.append(((a-b+c+d)/2,(b+a+d-c)/2))
    return out
H=[[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]]
def recode(v,f,stage):
    size=1<<(2*f);mask=(1<<f)-1
    def perm(owner,x):
        a=x&mask;b=x>>f
        if (owner+stage)&1:a,b=b,a
        return a|(b<<f)
    aligned=[v[owner*size+perm(owner,x)] for owner in range(4)for x in range(size)]
    w=[]
    for owner in range(4):
        for x in range(size):
            w.append(tuple(sum(H[owner][j]*aligned[j*size+x][part]for j in range(4))/2 for part in range(2)))
    return [w[owner*size+perm(owner,x)] for owner in range(4)for x in range(size)]
def rnd(x,B):
    value=x*(1<<B);q,r=divmod(value.numerator,value.denominator)
    if 2*r>value.denominator or (2*r==value.denominator and q&1):q+=1
    return F(q,1<<B)
def run():
    cases=0
    for f in (1,2,3):
        N=4*(1<<(2*f));v=[(F((j*7)%23-11,8),F((j*11)%19-9,8))for j in range(N)]
        need(qlayer(recode(v,f,0),f,0)!=recode(qlayer(v,f,0),f,0),'Fixture must not commute with Q')
        for m in (1,3,9):
            layers=[lambda v,j=j:qlayer(v,f,j)for j in range(f)]+[lambda v,s=s:recode(v,f,s)for s in reversed(range(m))]+[lambda v,j=j:qlayer(v,f,j)for j in range(f)]
            exact=v
            for U in layers:
                old=energy(exact);exact=U(exact);need(energy(exact)==old,'Every exact layer unitary')
            for B in (0,2,5):
                rounded=v
                for U in layers:
                    raw=U(rounded);rounded=[(rnd(a,B),rnd(b,B))for a,b in raw]
                    need(all(abs(a-c)<=F(1,2<<B) and abs(b-d)<=F(1,2<<B)for (a,b),(c,d)in zip(raw,rounded)),'Local nearest-round bound')
                err=energy([(a-c,b-d)for (a,b),(c,d)in zip(rounded,exact)])
                need(err<=F(len(layers)**2*N,1<<(2*B)),'Global squared-error bound')
                cases+=1
    need(rnd(F(1,2),0)==0 and rnd(F(3,2),0)==2 and rnd(F(-1,2),0)==0,'Signed tie-to-even controls')
    return {'status':'PASS_UNITARY_ROUNDING_CORROBORATION','dense_fixture_cases':cases,'max_cells':N,'rounding':'nearest ties to even','scope':'Generic small unitary-code fixtures; no rounded physical p19 caller is asserted.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
