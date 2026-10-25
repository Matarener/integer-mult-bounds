"""Free-warp relaxation of the chart problem with FIXED scalar order.
Keep every L-L ADD and its time order on each register, endpoints' dims;
let every frame be any subspace of the right dim (free warps). Minimize paid
concave cost. Gives a ceiling for chart/warp-gauge levers at fixed order."""
import sys,gzip,json,time; sys.path.insert(0,str(__import__('pathlib').Path.home()/'imb-harness/r12/tools'))
from moment import *
from collections import Counter,defaultdict
import numpy as np, scipy.sparse as sp
from scipy.optimize import milp,LinearConstraint,Bounds
side=sys.argv[1] if len(sys.argv)>1 else 'forward'
Cc=float(sys.argv[2]) if len(sys.argv)>2 else 0.00302
w=json.loads(gzip.decompress(open(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','rb').read()))
c=w['canonical'];fr=c['frames'];dim=lambda i:len(fr[i])
s={i:dim(c['start'][i]) for i in range(632)}; fn={i:dim(c['final'][i]) for i in range(632)}
seq=defaultdict(list); edges=[]
for op in w['programs'][side]:
    if op[0]=='scalar' and op[1][0]=='add':
        a,b=tuple(op[1][1]),tuple(op[1][2])
        if a[0]=='L' and b[0]=='L':
            A,B=a[1],b[1]; e=len(edges); edges.append((A,B,max(s[A],s[B]),min(fn[A],fn[B]))); seq[A].append(e); seq[B].append(e)
nv=0; W={}
for e,(A,B,lo,hi) in enumerate(edges):
    for l in range(lo,hi+1): W[e,l]=nv; nv+=1
U={}; cost=[]
for r in range(632):
    for a in range(s[r],fn[r]+1):
        for b in range(a+1,fn[r]+1): U[r,a,b]=nv; nv+=1
obj=np.zeros(nv)
for (r,a,b),j in U.items(): obj[j]=(b-a)**(1-Cc)
rows=[];cols=[];vals=[];lb=[];ub=[];m=0
def row(entries,l,u):
    global m
    for j,v in entries: rows.append(m);cols.append(j);vals.append(v)
    lb.append(l);ub.append(u);m+=1
for e,(A,B,lo,hi) in enumerate(edges): row([(W[e,l],1) for l in range(lo,hi+1)],1,1)
for r in range(632):
    S,F=s[r],fn[r]
    if S==F: continue
    for l in range(S,F+1):
        out=[(U[r,l,b],1) for b in range(l+1,F+1)]; inn=[(U[r,a,l],-1) for a in range(S,l)]
        rhs=1 if l==S else (-1 if l==F else 0)
        row(out+inn,rhs,rhs)
    for e in set(seq[r]):
        lo,hi=edges[e][2],edges[e][3]
        for l in range(max(lo,S+1),min(hi,F-1)+1):
            row([(W[e,l],1)]+[(U[r,a,l],-1) for a in range(S,l)],-np.inf,0)
    q=seq[r]
    for e1,e2 in zip(q,q[1:]):
        if e1==e2: continue
        L1,H1=edges[e1][2],edges[e1][3];L2,H2=edges[e2][2],edges[e2][3]
        for l in range(min(L1,L2),max(H1,H2)):
            ent=[(W[e1,x],1) for x in range(L1,min(H1,l)+1)]+[(W[e2,x],-1) for x in range(L2,min(H2,l)+1)]
            row(ent,0,np.inf)
A=sp.csr_matrix((vals,(rows,cols)),shape=(m,nv))
print('vars',nv,'rows',m,flush=True)
t=time.time()
LPMODE=len(sys.argv)>4 and sys.argv[4]=="lp"
res=milp(obj,constraints=LinearConstraint(A,lb,ub),integrality=np.zeros(nv) if LPMODE else np.ones(nv),bounds=Bounds(0,1),options={"time_limit":float(sys.argv[3]) if len(sys.argv)>3 else 600,"disp":False,"mip_rel_gap":1e-6})
print("dual bound",getattr(res,"mip_dual_bound",None),"fun",res.fun,"(+centres",8*8**(1-Cc),")",flush=True)
if LPMODE:
    lbcost=res.fun+8*8**(1-Cc); cur=sum(n*r**(1-Cc) for r,n in LOCAL["paid"].items()); print("LP local cost lower bound",lbcost,"current",cur,"saving per local",cur-lbcost); sys.exit()
print(res.status,res.message,'obj',res.fun,'t',time.time()-t,flush=True)
x=res.x; P=Counter()
for (r,a,b),j in U.items():
    if x[j]>0.5: P[b-a]+=1
P[8]+=8
print('paid',dict(sorted(P.items())),'mass',sum(k*v for k,v in P.items()))
H,_,T,PP,_=invoice({'helpers':{4:28,7:7,8:47,9:326},'paid':dict(P)}); print('ceiling root (fixed order, free warps)',root(T,PP))
cur=sum(n*r**(1-Cc) for r,n in LOCAL['paid'].items()); print('current local cost',cur,'relaxed',sum(n*r**(1-Cc) for r,n in P.items()))
