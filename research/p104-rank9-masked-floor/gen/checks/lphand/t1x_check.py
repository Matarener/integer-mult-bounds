# Independent Python check of the Lean table t1xOK (LPHand.lean) and evOK, exact mirror of the Lean Bool.
# Data: portBits and r8 copied from the Lean sources (data.json, sha256 printed).  Apache-2.0.
import json, hashlib, time, itertools
T0=time.time()
raw=open('data.json','rb').read(); print('data.json sha256', hashlib.sha256(raw).hexdigest())
d=json.loads(raw); PB=d['portBits']; R8=d['r8']
par=lambda t,n: bin(PB[t]&n).count('1')&1
pm=[sum(1<<t for t in range(104) if par(t,n)) for n in range(512)]
popc=lambda m: bin(m).count('1')
dotZ=lambda x,z: sum(a*b for a,b in zip(R8[x],R8[z]))
bits=lambda m: [t for t in range(104) if m>>t&1]
def clq(L): return all(x==z or dotZ(x,z)!=0 for x in L for z in L)
def t1At(nu,na):
    Y=pm[na]^(pm[na]&pm[nu])
    if popc(Y)>24: return True
    for nc in range(512):
        if nc==0 or nc==nu or popc(Y&pm[nc])>4: continue
        for nd in range(512):
            if nd in (0,nu,nc,nc^nu) or popc(Y&pm[nd])>4: continue
            U=Y&(pm[nc]|pm[nd])
            if popc(U)>4: continue
            if clq(bits(U)): return False
    return True
bad=[]; npass=0
for nu in range(512):
    if bin(nu).count('1')%2==0 or nu==511: continue
    for na in range(512):
        if na==0 or na==nu: continue
        if popc(pm[na]^(pm[na]&pm[nu]))<=24: npass+=1
        if not t1At(nu,na): bad.append((nu,na))
print('t1xOK (odd nu != 511):', 'TRUE' if not bad else 'FALSE', 'pairs passing |Y|<=24:', npass, 'bad', bad[:10])
ev=[s for s in range(1,512) if bin(s).count('1')%2==0 and popc(pm[s])<48]
print('evOK (nOdd>=48 for even s!=0):', 'TRUE' if not ev else 'FALSE', ev[:5])
print('min nOdd over even s!=0', min(popc(pm[s]) for s in range(1,512) if bin(s).count('1')%2==0))
print('time %.0fs'%(time.time()-T0))
