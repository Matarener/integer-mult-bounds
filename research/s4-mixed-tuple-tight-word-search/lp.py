# Exact simplex: max sum a_H Phi_H(T') s.t. sum a_H c_s(H) <= (2,1,2), a>=0, over all regular S4-set cuts.
from fractions import Fraction as F
import sys
rows=[list(map(int,l.split())) for l in open(sys.argv[1] if len(sys.argv)>1 else 'cuts.txt')]
def lp(w, price=(2,1,2)):
    best={}
    for r in rows:
        c=tuple(r[:3]); phi=w[0]*r[3]+w[1]*r[4]+w[2]*r[5]
        if phi>best.get(c,-1): best[c]=phi
    cols=[(c,phi) for c,phi in best.items() if phi>0]
    n=len(cols); m=3
    # tableau: rows m constraints + objective; variables n structural + m slack
    A=[[F(cols[j][0][i]) for j in range(n)]+[F(int(i==k)) for k in range(m)]+[F(price[i])] for i in range(m)]
    z=[F(-cols[j][1]) for j in range(n)]+[F(0)]*m+[F(0)]
    basis=[n+i for i in range(m)]
    while True:
        e=next((j for j in range(n+m) if z[j]<0),None)  # Bland
        if e is None: break
        ratios=[(A[i][-1]/A[i][e],basis[i],i) for i in range(m) if A[i][e]>0]
        if not ratios: return None
        _,_,l=min(ratios)
        piv=A[l][e]; A[l]=[x/piv for x in A[l]]
        for i in range(m):
            if i!=l and A[i][e]!=0:
                f=A[i][e]; A[i]=[x-f*y for x,y in zip(A[i],A[l])]
        f=z[e]; z=[x-f*y for x,y in zip(z,A[l])]
        basis[l]=e
    sol={cols[basis[i]][0]:(A[i][-1],cols[basis[i]][1]) for i in range(m) if basis[i]<n}
    return z[-1], sol, [z[n+i] for i in range(m)]
cases={'full (2143,3142,4231,2143)':(2,1,1),'(4231,2143)':(1,0,1),'(4231,3142)':(0,1,1),'(4231,2143,2143)':(2,0,1),
 '(2143,3142,4231)':(1,1,1),'(2143,3142)':(1,1,0),'(2143,2143,3142)':(2,1,0),'(4231)':(0,0,1),'(3142)':(0,1,0),'(2143)':(1,0,0)}
sep={(1,0,0):4,(0,1,0):5,(0,0,1):8}
for name,w in cases.items():
    val,sol,dual=lp(w)
    s=4*w[0]+5*w[1]+8*w[2]
    print(f"{name:28s} LP={val} separate={s} gap={s-val} dual_y={tuple(str(d) for d in dual)} basis={sol}")
