"""Float screen of the prefix identity for every candidate (h, P) over its whole cut window.

Strict: some v = e_h + w, w on ordinary non-restored helpers (not h), with M_c v = v and no
        nonzero value on a warp or correction (the PR3605/PR3734 form).
Relaxed: M_c v - v has components on targets only (target releases allowed).
Float arithmetic (dyadic coefficients); retained solutions are rechecked
exactly elsewhere.
"""
import sys,json,time
import numpy as np
from timeline import *
from candidates import candidates
tag=sys.argv[1]; widths=tuple(int(x) for x in sys.argv[2].split(',')) if len(sys.argv)>2 else (8,9)
w=load(tag); ev=events(w); con=contacts(ev)
bill,wd,chain,start,end=C.frame_bill(w)
cand=candidates(w,ev,con,start,end,widths)
rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
D=[r for r in range(224,704) if r not in removed and r not in rest]
Dix={r:i for i,r in enumerate(D)}
nontgt=np.array([r for r in range(704) if not (112<=r<224)])
X=np.eye(704)
cons=[]                                   # functionals that must vanish on v
for c in w['initial_corrections']:
    row=np.zeros(704); row[c['source']]=1; cons.append(row)
lo=min(c['lo'] for c in cand); hi=max(c['hi'] for c in cand)
active={}                                  # position -> candidates whose window contains it
for k,c in enumerate(cand):
    c['strict']=[]; c['relax']=[]
res_t=time.time()
def nullspace(A,tol=1e-9):
    if A.shape[0]==0: return np.eye(A.shape[1])
    u,s,vt=np.linalg.svd(A,full_matrices=True)
    r=int((s>tol*max(1.0,s[0] if len(s) else 1)).sum())
    return vt[r:].T
for pos in range(0,hi+1):
    if pos>=lo:
        here=[c for c in cand if c['lo']<=pos<=c['hi']]
        if here:
            M=X-np.eye(704)
            Wr=np.array(cons) if cons else np.zeros((0,704))
            for mode,rows in (('strict',slice(None)),('relax',nontgt)):
                A=np.vstack([M[rows][:,D],Wr[:,D]])
                cols=np.where(np.abs(A).sum(0)>0)[0]
                N=nullspace(A[:,cols])
                for c in here:
                    j=Dix[c['h']]
                    if j not in set(cols):      # h jamais lu : solution triviale v=e_h
                        c[mode].append(pos); continue
                    jj=int(np.where(cols==j)[0][0])
                    if N.shape[1] and np.abs(N[jj]).max()>1e-7: c[mode].append(pos)
    if pos==len(ev): break
    e=ev[pos]; g=e['g']; k=e['kind']
    if k=='corr': pass
    elif k in ('warp','awarp'):
        cons.append(X[g[1]].copy())
    elif g[0]=='add':
        X[g[1]]+=g[3]/g[4]*X[g[2]]
    elif g[0]=='scale':
        X[g[1]]*=g[2]/g[3]
    if pos%2000==0: print('pos',pos,round(time.time()-res_t,1),flush=True)
out=[]
for c in cand:
    out.append({k:c[k] for k in ('h','width','u','nblock','lo','hi')}|
               dict(P=C.points(c['P'])[:8],strict_n=len(c['strict']),relax_n=len(c['relax']),
                    strict_first=c['strict'][:1],strict_last=c['strict'][-1:],
                    relax_first=c['relax'][:1],relax_last=c['relax'][-1:]))
json.dump(out,open(f'scalar-{tag}.json','w'),indent=0)
from collections import Counter
cnt=Counter((o['width'],o['strict_n']>0,o['relax_n']>0) for o in out)
print('(width, strict possible, relaxed possible):',dict(cnt))
hs=Counter()
for o in out:
    if o['strict_n']: hs[('strict',o['width'],o['h'])]+=1
print('helpers with a strict solution:',sorted({(k[1],k[2]) for k in hs}))
