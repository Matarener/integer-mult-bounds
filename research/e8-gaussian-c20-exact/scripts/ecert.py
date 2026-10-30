"""Exact verifier for ebb.py certificates (pure Python integers, no floating point).
A certificate is a list of leaves (path, y).  A path is a sequence of steps from the root box [0, up]:
  (j,'<=',v) / (j,'>=',v+1)   branching (both children must be present: checked as a complete binary tree);
  ('T', y, ((j,lo,hi),...))   reduced-cost tightening certified by the dual y (one child);
At a leaf, the dyadic dual y >= 0 (scaled by SC = 2^24) must give
  S(y, box) := y.b + sum_j max(d_j lo_j, d_j hi_j) < target*SC,   d = SC*g - A^T y,
which proves every integer x in the box with A x <= b has g.x < target.  A tightening step with S = S(y, box) >= target*SC
may set hi_j = lo_j + floor((S - target*SC)/(-d_j)) for d_j < 0 and lo_j = hi_j - floor((S - target*SC)/d_j) for d_j > 0:
any x in the box with g.x >= target satisfies target*SC <= S + d_j (x_j - lo_j) (resp. - d_j (hi_j - x_j)).
The root box is checked to contain every feasible x (A >= 0, b >= 0, x >= 0  =>  x_j <= min_i floor(b_i / A_ij)).
argv: cert.pkl ..."""
import pickle, sys, numpy as np
from model import build
SC=1<<24
class Ctx: pass
def S_and_d(cx,y,lo,hi):
    """exact S(y,box) and d; int64 numpy when an a-priori magnitude bound guarantees no overflow, else Python ints"""
    y=np.asarray(y,dtype=np.int64); assert len(y)==cx.nr and y.min()>=0
    lo=np.asarray(lo,dtype=np.int64); hi=np.asarray(hi,dtype=np.int64)
    ym=int(y.max()); hm=int(max(np.abs(lo).max(),np.abs(hi).max(),1))
    dmax=cx.gmax+ym*cx.colsum            # |d_j| <= SC*g_j + y_max * sum_i A_ij
    if ym*cx.bsum+cx.nc*dmax*hm < 2**62:
        s=int(y.dot(cx.bn)); d=cx.gSn-cx.AT.dot(y)
        s+=int(np.maximum(d*lo,d*hi).sum()); return s,d
    yl=[int(v) for v in y]; s=sum(yi*bi for yi,bi in zip(yl,cx.b) if yi)
    d=[cx.gS[j]-sum(yl[cx.Ai[k]]*cx.Ad[k] for k in range(cx.Ap[j],cx.Ap[j+1])) for j in range(cx.nc)]
    s+=sum(max(dj*int(l),dj*int(h)) for dj,l,h in zip(d,lo,hi)); return s,d
def walk(cx,leaves,depth,lo,hi):
    """leaves: list of (path,y) sharing the prefix path[:depth]; returns number of leaves verified"""
    ends=[L for L in leaves if len(L[0])==depth]
    if ends:
        assert len(leaves)==1, 'leaf with descendants'
        if any(l>h for l,h in zip(lo,hi)): return 1          # empty box
        s,_=S_and_d(cx,ends[0][1],lo,hi); assert s<cx.target*SC, 'leaf bound fails'
        cx.worst=max(cx.worst,s); return 1
    steps={}
    for L in leaves: steps.setdefault(id(L[0][depth]) if L[0][depth][0]=='T' else L[0][depth],[]).append(L)
    first=leaves[0][0][depth]
    if first[0]=='T':
        assert len(steps)==1, 'tightening node with several children'
        _,y,ch=first
        if any(l>h for l,h in zip(lo,hi)): return len(leaves)
        s,d=S_and_d(cx,y,lo,hi); gap=s-cx.target*SC; assert gap>=0
        lo=list(lo); hi=list(hi); d=[int(v) for v in d]
        for j,nl,nh in ch:
            if d[j]<0: assert nl==lo[j] and nh==lo[j]+gap//(-d[j]) and nh<hi[j]; hi[j]=nh
            elif d[j]>0: assert nh==hi[j] and nl==hi[j]-gap//d[j] and nl>lo[j]; lo[j]=nl
            else: raise AssertionError('zero reduced cost tightening')
        cx.ntight+=len(ch)
        return walk(cx,leaves,depth+1,lo,hi)
    assert len(steps)==2, 'branch node without exactly two children'
    h1,h2=sorted(steps,key=lambda h:h[1])
    assert h1[1]=='<=' and h2[1]=='>=' and h1[0]==h2[0] and h2[2]==h1[2]+1, 'bad split'
    j=h1[0]; hi1=list(hi); hi1[j]=min(hi[j],h1[2]); lo2=list(lo); lo2[j]=max(lo[j],h2[2])
    return walk(cx,steps[h1],depth+1,lo,hi1)+walk(cx,steps[h2],depth+1,lo2,hi)
def verify(fn):
    R=pickle.load(open(fn,'rb')); meta=R['meta']
    A,b,g,up,target,meta2=build(meta['c'],meta['cm'],meta['case'])
    assert meta2['cols']==meta['cols']
    A=A.tocsc(); nr,nc=A.shape
    assert (A.data>0).all() and (b>=0).all()
    imp=np.array([min(int(b[A.indices[k]])//int(A.data[k]) for k in range(A.indptr[j],A.indptr[j+1])) for j in range(nc)])
    assert (imp<=up).all(), 'box does not contain all feasible points'
    if R['status']=='FEASIBLE':
        x=[int(v) for v in R['x']]; Ad=A.toarray()
        ok=min(x)>=0 and all(int(sum(int(Ad[i,j])*x[j] for j in range(nc) if x[j]))<=int(b[i]) for i in range(nr))
        gain=sum(int(g[j])*x[j] for j in range(nc))
        return ('FEASIBLE (verified integer point, gain %d >= target %d)'%(gain,target)) if ok and gain>=target else 'BAD POINT'
    cx=Ctx(); cx.nr,cx.nc=nr,nc; cx.b=[int(v) for v in b]; cx.gS=[int(v)*SC for v in g]; cx.Ai=A.indices.tolist(); cx.Ad=[int(v) for v in A.data]
    cx.Ap=A.indptr.tolist(); cx.bn=b.astype(np.int64); cx.gSn=g.astype(np.int64)*SC; cx.AT=A.T.tocsr().astype(np.int64)
    cx.colsum=int(A.sum(0).max()); cx.gmax=int(g.max())*SC; cx.bsum=int(b.sum()); cx.target=int(target); cx.worst=-10**30; cx.ntight=0
    sys.setrecursionlimit(100000)
    n=walk(cx,R['leaves'],0,[0]*nc,[int(v) for v in up]); assert n==len(R['leaves'])
    return 'EXCLUDED (exact: %d leaves, %d tightenings, max leaf bound %.6f < target %d)'%(n,cx.ntight,cx.worst/SC,target)
if __name__=='__main__':
    for fn in sys.argv[1:]: print(fn,verify(fn),flush=True)
