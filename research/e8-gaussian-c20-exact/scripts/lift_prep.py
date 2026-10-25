"""Per type: Z_t (lines all of whose cliques are missed), x_t max pairwise-orthogonal subset, delta, y_t. Cached to lift.pkl"""
import pickle, numpy as np
from f2check import NO
C=pickle.load(open('hits_table.pkl','rb'))['C']
M=np.zeros((640,60),bool)
for k,cl in enumerate(C): M[k,cl]=True
T=pickle.load(open('types_e256.pkl','rb'))
orth=~NO; np.fill_diagonal(orth,False)
cache={}
def maxorth(Z):
    k=tuple(Z)
    if k in cache: return cache[k]
    best=[]
    def ext(cl,cand):
        nonlocal best
        if len(cl)>len(best): best=cl
        for i,v in enumerate(cand): ext(cl+[v],[w for w in cand[i+1:] if orth[v,w]])
    ext([],list(Z)); cache[k]=best; return best
mis=np.array([t[4] for t in T])
Zall=~((~mis[:,:,None])&M[None,:,:]).any(1)   # (n,60): no hit clique through line
out=[]
for i,(a,b,R,e,m) in enumerate(T):
    x=maxorth(list(np.nonzero(Zall[i])[0])); d=(4-R)-len(x)
    out.append((x,d))
pickle.dump(out,open('lift.pkl','wb'))
from collections import Counter
print(Counter((T[i][2],T[i][3],len(x),d) for i,(x,d) in enumerate(out)))
