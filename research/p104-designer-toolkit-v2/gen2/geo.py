"""RELAYLAT geometry: ports, residual E, frame enumeration helpers (no side effects beyond module constants)."""
import os
import json, itertools, numpy as np, sys
TK=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
J=json.load(open(TK+'/synth/data/sign_code.json')); S4=np.array(J['S4']); C2=np.array(J['C2'])
import gzip
_w=json.load(gzip.open(TK+'/words/5827.json.gz'))
PORTS=list(_w['ports']); m=len(PORTS)
RES=(2*C2@S4)/4.0 - np.eye(m)      # res_ji : Y_j needs -res_ji x_i  (=-E)
par=lambda a,b: bin(a&b).count('1')&1
ORTH=np.array([[1-par(PORTS[i],PORTS[j]) for i in range(m)] for j in range(m)])  # ORTH[j,i]
def span(b):
    S={0}
    for v in b: S|={x^v for x in S}
    return S
def ports_in(S): return [i for i,p in enumerate(PORTS) if p in S]
def readers_of(basis): return [j for j,p in enumerate(PORTS) if all(not par(p,v) for v in basis)]
