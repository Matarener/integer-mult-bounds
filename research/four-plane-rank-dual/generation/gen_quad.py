"""build CERTIFICATES.json.gz and CERT-INDEX.bin.gz for the four-plane package"""
import pickle, gzip, json, itertools, sys
from fractions import Fraction as Q
from multiprocessing import Pool
import numpy as np
from scipy.optimize import linprog
U=list(range(1,16)); KEYS=[(S,T) for S in U for T in U]; SINGLES=[1,2,4,8]
OFF=[(P,Q2) for P in SINGLES for Q2 in SINGLES if P!=Q2]
pop=lambda x: bin(x).count('1')
def bound(S,T,X,Z):
    rows=[P for P in SINGLES if P&S&X]; cols=[Q2 for Q2 in SINGLES if Q2&T&X]
    br={frozenset(Q2 for Q2 in cols if (P,Q2) not in Z) for P in rows}-{frozenset()}
    bc={frozenset(P for P in rows if (P,Q2) not in Z) for Q2 in cols}-{frozenset()}
    return min(len(br),len(bc))
A0=np.array([[1.0 if (S&X and T&X) else 0.0 for X in U] for S,T in KEYS]); c0=-np.array([2*pop(X) for X in U],float)
UNIONS=U
exec(open('fastcheck.py').read())
TAB=open('phitab4.bin','rb').read()
def exact_ok(tt,cert):
    if sum(2*pop(X)*w for m,X,w in cert)!=16: return False
    return cert_ok(tt,cert,TAB)
def block(tt):
    r=linprog(c0,A_ub=A0,b_ub=np.array(tt,float),bounds=(0,None),method='highs')
    for den in (6,12,60,420):
        cert=tuple((0,X,Q(x).limit_denominator(den)) for X,x in zip(U,r.x) if Q(x).limit_denominator(den)>0)
        if exact_ok(tt,cert): return tt,cert
    return tt,None
if __name__=='__main__':
    classes=pickle.load(open('quad_classes.pkl','rb')); weak=set(pickle.load(open('quad_weak.pkl','rb')))
    strong=[k for k in classes if k not in weak]
    with Pool(12) as pool:
        res=dict(pool.map(block,strong,chunksize=500))
    print('strong',len(strong),'exact certified',sum(1 for v in res.values() if v),flush=True)
    for i in range(12):
        for tt,(val,nz) in pickle.load(open(f'quad_cert_{i}.pkl','rb')).items():
            if val<16-1e-6: res[tt]=None; continue
            cert=None
            for den in (6,12,60,420):
                cand=tuple(sorted((m,X,Q(w).limit_denominator(den)) for m,X,w in nz if Q(w).limit_denominator(den)>0))
                if exact_ok(tt,cand): cert=cand; break
            res[tt]=cert
    certs={}; 
    for tt,cert in res.items():
        if cert is not None and cert not in certs: certs[cert]=len(certs)+1
    print('distinct certificates',len(certs),'certified classes',sum(1 for v in res.values() if v),'of',len(classes),flush=True)
    order=list(itertools.combinations(range(56),4)); quad2cls={}
    for tt,qs in classes.items():
        for q in qs: quad2cls[q]=tt
    idx=bytearray()
    for q in order:
        c=res.get(quad2cls[q]); ci=certs[c] if c is not None else 0
        idx+=bytes((ci&255,ci>>8))
    out=[[[m,X,str(w)] for m,X,w in cert] for cert,_ in sorted(certs.items(),key=lambda kv:kv[1])]
    open('CERTIFICATES.json.gz','wb').write(gzip.compress(json.dumps({"schema":"four-plane-rank-dual/1","certificates":out}).encode(),9))
    open('CERT-INDEX.bin.gz','wb').write(gzip.compress(bytes(idx),9))
    print('quadruples certified', sum(1 for i in range(0,len(idx),2) if idx[i] or idx[i+1]), 'of', len(order))
