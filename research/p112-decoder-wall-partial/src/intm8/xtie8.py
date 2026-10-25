# INDEPENDENT cross-check of tie8.py (NEARMISS=1): own E8 roots, own P112, own frames (numpy, no base.py), no symmetry breaking.
# Claim: no two disjoint nonempty sets X1, X2 of P112 lines such that each X meets every frame and, for every line t and frame F not
# containing t, with w = lines of F not orthogonal to t:  t in X => X meets w;  t not in X => |X cap w| != 1.
# usage: xtie8.py out.cnf [nodisjoint]
import sys, itertools, numpy as np
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (1,-1):
        v=[0]*8; v[i]=2; v[j]=2*s; R.append(v)
for signs in itertools.product((1,-1),repeat=8):
    if signs[0]==1 and signs.count(-1)%2==0: R.append(list(signs))
R=np.array(R); assert len(R)==120
G=R@R.T
fr=[k for k in range(120) if (R[k]!=0).sum()==2 and set(np.nonzero(R[k])[0]) in ({0,1},{2,3},{4,5},{6,7})]
assert len(fr)==8 and all(G[a,b]==0 for a in fr for b in fr if a!=b)
L=[k for k in range(120) if k not in fr]; n=len(L); Cm=R[L]; O=(Cm@Cm.T==0)
frames=[]
def ext(cl,cand):
    if len(cl)==8: frames.append(cl); return
    for k,x in enumerate(cand):
        ext(cl+[x],[y for y in cand[k+1:] if O[x,y]])
ext([],list(range(n)))
assert len(frames)==1260, len(frames)
x1=lambda t:2*t+1; x2=lambda t:2*t+2
cl=[]
nod = len(sys.argv)>2
if not nod:
    for t in range(n): cl.append([-x1(t),-x2(t)])
for F in frames:
    cl.append([x1(f) for f in F]); cl.append([x2(f) for f in F])
    Fs=set(F)
    for t in range(n):
        if t in Fs: continue
        w=[g for g in F if not O[t,g]]; assert len(w)==4
        for v in (x1,x2):
            cl.append([-v(t)]+[v(g) for g in w])
            for g in w: cl.append([v(t),-v(g)]+[v(h) for h in w if h!=g])
# dedupe
cl=sorted(set(tuple(sorted(c)) for c in cl))
with open(sys.argv[1],'w') as f:
    f.write('p cnf %d %d\n'%(2*n,len(cl)))
    for c in cl: f.write(' '.join(map(str,c))+' 0\n')
print('XTIE8 frames',len(frames),'clauses',len(cl),'nodisjoint' if nod else '')
