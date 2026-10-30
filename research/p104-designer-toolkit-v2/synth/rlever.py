"""RLEVER: exact-pricer cost model for the signal count r (root descent cost vs residual saving).
Usage: W/python3 -B synth/rlever.py   (single core, seconds).  Base word #5786 invoice (cached tk price)."""
import sys,os,json,glob
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE+'/..')
from tkcommon import *
n=104
def frame_bound(r): return n*n/r-n          # ||E||_F^2 >= n^2/r - n  (RESIDUAL tight-frame theorem)
def base(word='5786'):
    p,w=load(word); rep=legal.check(w)
    T,P=X.invoice(rep); return rep,dict(T),dict(P)
CAR=dict(T={9:1},P={1:2,7:1})   # (1,7,1) carrier per call: credit 9, paid 1+7+1  (tax 6.154)
def kappa_cfg(T,P,root_costs,tax_removed=0.0,calls=18,base_roots=8,base_cost=7):
    T=dict(T);P=dict(P)
    P[base_cost]=P.get(base_cost,0)-calls*base_roots
    for c in root_costs: P[c]=P.get(c,0)+calls
    # remove tax_removed/6.154 (1,7,1) carriers (R0 law), fractional ok
    nc=tax_removed/6.154
    for r,m in CAR['T'].items(): T[r]=T.get(r,0)-calls*nc*m
    for r,m in CAR['P'].items(): P[r]=P.get(r,0)-calls*nc*m
    return X.kappa(T,P)
def table(T,P,resid_tax=3700.0,eff=1.0):
    k0=kappa_cfg(T,P,[7]*8)
    out=[]
    for r in (8,9,10,12,13,16,20,26):
        sav=resid_tax*eff*(1-frame_bound(r)/frame_bound(8))
        ks={c:kappa_cfg(T,P,[c]*r,sav)/k0-1 for c in (7,6,5,4,3,2)}
        # break-even average root cost
        lo,hi=0.0,8.0
        for _ in range(40):
            m=(lo+hi)/2
            # fractional cost: interpolate P between floor/ceil ranks
            f=int(m); fr=m-f
            Pm=dict(P); Pm[7]=Pm.get(7,0)-18*8
            Pm[f]=Pm.get(f,0)+18*r*(1-fr)
            if fr>0: Pm[f+1]=Pm.get(f+1,0)+18*r*fr
            Tm=dict(T); nc=sav/6.154
            Tm[9]=Tm.get(9,0)-18*nc; Pm[1]=Pm.get(1,0)-18*nc*2; Pm[7]=Pm.get(7,0)-18*nc
            if X.kappa(Tm,Pm)>=k0: lo=m
            else: hi=m
        out.append((r,round(frame_bound(r)),round(sav),ks,lo))
    return k0,out
if __name__=='__main__':
    rep,T,P=base(sys.argv[1] if len(sys.argv)>1 else '5786')
    print('base kappa',X.kappa(T,P),'paid',rep['paid'])
    for rt,eff in ((3700,1.0),(3700,0.5),(5900,1.0)):
        k0,out=table(T,P,rt,eff)
        print('\nresid tax %d efficiency %.1f (saving = tax*eff*(1-FB(r)/FB(8)))  base kappa %.10f'%(rt,eff,k0))
        print(' r  frameLB  saved_tax | rel kappa gain at uniform root cost 7,6,5,4,3,2 | break-even mean root cost (total owned rank)')
        for r,fb,sav,ks,be in out:
            print('%2d %6d %8d | '%(r,fb,sav)+' '.join('%+6.1f%%'%(100*ks[c]) for c in (7,6,5,4,3,2))+' | %.2f (%.1f)'%(be,be*r))
