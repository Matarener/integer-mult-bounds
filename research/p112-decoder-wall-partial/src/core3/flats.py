# CORE3 flats.py: all flats of the P112 line matroid (over Q) up to Aut, by rank; per-flat label statistics.
# Output flats.pkl: list of dicts {rank, mask, nlines, orbit}.  Also checks: Aut generators are signed-linear (so Aut acts on the
# Q-matroid), labels all have bit 0 set, m(d) = max #lines with labels in a d-dim F2 subspace for d = 6,7,8.
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fullwall'))
from base import *
import numpy as np, pickle, time, pynauty, itertools
from fractions import Fraction as Fr
HERE3=os.path.dirname(os.path.abspath(__file__)); t0=time.time()
MAXR=int(sys.argv[1]) if len(sys.argv)>1 else 8
# ---------- Aut: pynauty generators, signed-linear check
ADJ={i:[j for j in range(n) if j!=i and Bd[i,j]] for i in range(n)}
gens,a_,b_,_,_=pynauty.autgrp(pynauty.Graph(n,adjacency_dict=ADJ)); AUT=round(a_*10**b_)
Ci=C.astype(np.int64)
basis=[];
for t in range(n):
    if np.linalg.matrix_rank(Ci[basis+[t]])>len(basis): basis.append(t)
    if len(basis)==8: break
Binv=np.linalg.inv(Ci[basis].T.astype(float))
def linear_ok(g):
    for signs in itertools.product((1,-1),repeat=8):
        Tg=(Ci[[g[t] for t in basis]].T*np.array(signs))@Binv   # T c_basis = signs * c_g(basis)
        img=(Tg@Ci.T).T
        ok=all(np.allclose(img[t],Ci[g[t]]) or np.allclose(img[t],-Ci[g[t]]) for t in range(n))
        if ok: return True
    return False
assert all(linear_ok(g) for g in gens); print('Aut',AUT,'#gens',len(gens),'all generators signed-linear: OK',flush=True)
G=np.load(os.path.join(HERE3,'G.npy')).astype(np.int64)
assert len(G)==AUT and len({r.tobytes() for r in G[:2000]})==2000
for g in G[::9973]: assert (Bd[np.ix_(g,g)]==Bd).all()
# G.npy is the closure of the same pynauty generators (SUBST/gen.py BFS); spot-check that each sampled element is signed-linear too
for g in G[::17203]: assert linear_ok(list(g))
GINV=np.argsort(G,axis=1)
def canon(mask):
    v=np.array([(mask>>t)&1 for t in range(n)],dtype=bool)
    img=v[GINV]                       # img[g,j] = v[g^-1 j]  (image set g(D))
    pk=np.packbits(img,axis=1,bitorder='little')
    pk=np.concatenate([pk,np.zeros((len(pk),2),np.uint8)],1).view(np.uint64)   # (N,2) lo,hi
    hi=pk[:,1]; m=hi.min(); sel=pk[hi==m,0].min()
    return int(sel)|(int(m)<<64)
# ---------- closure
def closure(lines):
    M=Ci[list(lines)].astype(float)
    if len(lines)==0: return 0,0
    U,S,Vt=np.linalg.svd(M); r=int((S>1e-8).sum()); B=Vt[:r]
    res=Ci-(Ci@B.T)@B
    inn=np.where(np.abs(res).max(1)<1e-7)[0]
    return r,sum(1<<int(t) for t in inn)
def lines_of(m): return [t for t in range(n) if m>>t&1]
reps={0:{0:1}}
for r in range(0,min(MAXR,8)):
    nxt={}
    for F in reps[r]:
        seen=set(); Fl=lines_of(F)
        for t in range(n):
            if F>>t&1: continue
            rr,cl=closure(Fl+[t])
            if cl in seen: continue
            seen.add(cl); assert rr==r+1
            c=canon(cl)
            nxt[c]=1
    reps[r+1]=nxt
    print('rank',r+1,'flat orbits',len(nxt),'%.0fs'%(time.time()-t0),flush=True)
# orbit sizes
def orbit_size(mask):
    v=np.array([(mask>>t)&1 for t in range(n)],dtype=bool)
    pk=np.packbits(v[GINV],axis=1,bitorder='little')
    return len(np.unique(pk,axis=0))
out=[]
for r in sorted(reps):
    for F in reps[r]:
        out.append(dict(rank=r,mask=F,nlines=bin(F).count('1'),orbit=orbit_size(F)))
    print('rank',r,'orbits',len(reps[r]),'total flats',sum(o['orbit'] for o in out if o['rank']==r),flush=True)
pickle.dump(out,open(HERE3+'/flats.pkl','wb'))
# ---------- exact re-verification of every representative (Fractions): rank and closedness
def frank(rows):
    rows=[[Fr(int(x)) for x in r] for r in rows]; rk=0; cols=len(rows[0]) if rows else 0
    for c in range(cols):
        p=next((i for i in range(rk,len(rows)) if rows[i][c]!=0),None)
        if p is None: continue
        rows[rk],rows[p]=rows[p],rows[rk]
        for i in range(len(rows)):
            if i!=rk and rows[i][c]!=0:
                f=rows[i][c]/rows[rk][c]; rows[i]=[x-f*y for x,y in zip(rows[i],rows[rk])]
        rk+=1
    return rk
bad=0
for o in out:
    Fl=lines_of(o['mask'])
    r=frank([Ci[t] for t in Fl]) if Fl else 0
    if r!=o['rank']: bad+=1; continue
    for t in range(n):
        if not o['mask']>>t&1 and frank([Ci[s] for s in Fl]+[Ci[t]])==r: bad+=1; break
print('exact flat re-verification: bad =',bad,flush=True)
# ---------- label facts
hd=[h for h in range(1,512) if all(bin(h&l).count('1')%2==1 for l in LAB)]; assert hd; print('functional h with h.lab=1 on all labels:',hd,'OK (so a d-dim subspace holds <= 2^(d-1) labels)')
Z=[sum(1<<t for t in range(n) if bin(h&LAB[t]).count('1')%2==0) for h in range(512)]
m8=max(bin(Z[h]).count('1') for h in range(1,512))
m7=0
for h1 in range(1,512):
    for h2 in range(h1+1,512):
        m7=max(m7,bin(Z[h1]&Z[h2]).count('1'))
m6=0
Za=np.array([[z&((1<<64)-1),z>>64] for z in Z],dtype=np.uint64)
def pc(x):
    x=x.copy(); c=np.zeros(x.shape,np.int64)
    while x.any(): c+=(x&np.uint64(1)).astype(np.int64); x>>=np.uint64(1)
    return c
for h1 in range(1,512):
    for h2 in range(h1+1,512):
        z12=Za[h1]&Za[h2]
        if bin(int(z12[0])).count('1')+bin(int(z12[1])).count('1')<=m6: continue
        cnt=[bin(int(z12[0]&Za[h3,0])).count('1')+bin(int(z12[1]&Za[h3,1])).count('1') for h3 in range(1,512) if h3 not in (h1,h2,h1^h2)]
        m6=max(m6,max(cnt))
print('m8 (codim-1 max lines)',m8,' m7 (codim-2)',m7,' m6 (codim-3)',m6,'%.0fs'%(time.time()-t0),flush=True)
