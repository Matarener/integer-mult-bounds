"""Every donor set of size <= 3 giving an exact identity for helper 472 at its producer cut; each one is
built, frame-repaired, locally optimised and priced on the ideal packing ceiling."""
import itertools,sys
import numpy as np
from fractions import Fraction as Q
from timeline import *
from construct import exact_fixed
from construct2 import assemble
from repair import repair
from frameopt import Frames
from ideal import ideal
w=load('base'); ev=events(w); b0,w0,*_=C.frame_bill(w); a0=ideal(b0,w0)
h=472; c=10759; P=C.span((429,51))
rest=set(map(int,w['helper_final'])); removed=set(w['removed'])
D=[r for r in range(224,704) if r not in removed and r not in rest and r!=h]
X=np.eye(704); cons=[]
for cc in w['initial_corrections']:
    row=np.zeros(704); row[cc['source']]=1; cons.append(row)
for e in ev[:c]:
    g=e['g']; k=e['kind']
    if k in ('warp','awarp'): cons.append(X[g[1]].copy())
    elif k=='corr': pass
    elif g[0]=='add': X[g[1]]+=g[3]/g[4]*X[g[2]]
    elif g[0]=='scale': X[g[1]]*=g[2]/g[3]
A=np.vstack([X-np.eye(704)]+[np.array(cons)]); ah=A[:,h]
act=[d for d in D if np.any(np.abs(A[:,d])>1e-12)]
print('active donors',len(act))
sols=[]
for k in (1,2,3):
    for S in itertools.combinations(act,k):
        M=A[:,list(S)]; s,*_=np.linalg.lstsq(M,-ah,rcond=None)
        if np.linalg.norm(M@s+ah)<1e-9 and np.all(np.abs(s)>1e-9):
            sols.append({h:Q(1),**{d:Q(x).limit_denominator(1<<20) for d,x in zip(S,s)}})
    if sols: print('size',k,':',len(sols),'sets'); 
print('sets found',len(sols))
for v in sols[:40]:
    ok,_=exact_fixed(w,ev,c,v)
    if not ok: print('inexact',v); continue
    ins=[(c,['add',d,h,q.numerator,q.denominator]) for d,q in v.items() if d!=h]
    best=None
    for mode in (False,True):
        try:
            x,mark=assemble(w,ev,h,P,c,ins); x,_=repair(x,mark,minimal_B=mode,cleanup=False); C.frame_bill(x)
            f=Frames(x); f.optimize(); x=f.write(); b,wd,*_=C.frame_bill(x)
            an=ideal(b,wd)
            if best is None or an>best[0]: best=(an,b)
        except Exception as ex: pass
    print({d:str(q) for d,q in v.items() if d!=h},'d_ideal',f'{best[0]-a0:+.3e}' if best else 'infeasible')
