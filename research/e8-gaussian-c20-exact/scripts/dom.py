"""Dominance reduction of the miss-set type catalog: t is dominated if some t' has g' >= g and m' subset of m (t' != t).
Orbits under the line group (acting on cliques) are used to test one representative per orbit."""
import pickle, numpy as np
from collections import Counter
T=pickle.load(open('types_e256.pkl','rb'))
G=np.array(pickle.load(open('orbits.pkl','rb'))['G'])
C=pickle.load(open('hits_table.pkl','rb'))['C']
ci={frozenset(c):k for k,c in enumerate(C)}
Cperm=np.array([[ci[frozenset(int(g[t]) for t in c)] for c in C] for g in G])   # (|G|,640)
mis=np.array([t[4] for t in T]); g=np.array([4-t[2] for t in T]); e=np.array([t[3] for t in T])
key={ (int(g[i]),mis[i].tobytes()):i for i in range(len(T))}
orb=-np.ones(len(T),int); reps=[]
for i in range(len(T)):
    if orb[i]>=0: continue
    reps.append(i)
    idx=np.nonzero(mis[i])[0]
    for p in Cperm:
        m2=np.zeros(640,bool); m2[p[idx]]=True
        j=key.get((int(g[i]),m2.tobytes()))
        assert j is not None
        orb[j]=len(reps)-1
print('types',len(T),'orbits',len(reps))
size=mis.sum(1)
dominated=[]
for r in reps:
    # t' with g'>=g, m' subset m, t' != r
    sub=~(mis[:, ~mis[r]].any(1))   # m' within m_r
    cand=np.nonzero(sub & (g>=g[r]) & (np.arange(len(T))!=r))[0]
    dominated.append(len(cand)>0)
keep=np.array([not dominated[orb[i]] for i in range(len(T))])
print('orbit reps non-dominated',sum(not d for d in dominated))
for k,r in enumerate(reps):
    print(k,'R',T[r][2],'e',T[r][3],'|m|',int(size[r]),'orbit',int((orb==k).sum()),'dominated' if dominated[k] else 'KEEP')
pickle.dump({'orb':orb,'reps':reps,'keep':keep,'Cperm':Cperm},open('dom.pkl','wb'))
