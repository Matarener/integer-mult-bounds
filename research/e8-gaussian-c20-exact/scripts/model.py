"""Shared exact integer data of one case of the S9 lifted relaxation (identical to s9 branch1.py).
Columns: 60 lines (gain 1), then deficient types t with e_t <= min(e1, slack-e1) (gain g_t = 4-R_t).
Rows: 640 cliques (M mu + sum n_t m_t <= cap - m_t1), e-budget (sum n_t e_t <= slack - e1).
Exclusion iff max gain < target = need - g_t1."""
import pickle, numpy as np
from scipy.sparse import csr_matrix, hstack, vstack
_D={}
def data():
    if not _D:
        _D['C']=pickle.load(open('hits_table.pkl','rb'))['C']; _D['T']=pickle.load(open('types_e256.pkl','rb'))
        _D['L']=pickle.load(open('lift.pkl','rb')); _D['dom']=pickle.load(open('dom.pkl','rb'))
    return _D
def build(c,cm,case):
    D=data(); C,T,L,dom=D['C'],D['T'],D['L'],D['dom']
    cap=c-12; slack=128*(cm+c)-7680; need=4*c-cm
    M=np.zeros((640,60),np.int64)
    for k,cl in enumerate(C): M[k,cl]=1
    if case>=0:
        r=dom['reps'][case]; e1=int(T[r][3]); base=4-int(T[r][2]); fixed=T[r][4].astype(np.int64)
        assert L[r][1]>0 and e1<=slack
        cols=[i for i in range(len(T)) if L[i][1]>0 and T[i][3]<=min(e1,slack-e1)]
    else: e1=0; base=0; fixed=np.zeros(640,np.int64); cols=[]
    Y=np.array([T[i][4] for i in cols],np.int64).T if cols else np.zeros((640,0),np.int64)
    e=np.array([T[i][3] for i in cols],np.int64); g=np.concatenate([np.ones(60,np.int64),np.array([4-T[i][2] for i in cols],np.int64)])
    A=vstack([hstack([csr_matrix(M),csr_matrix(Y)]),csr_matrix(np.concatenate([np.zeros(60,np.int64),e])[None])]).tocsr().astype(np.int64)
    b=np.concatenate([cap-fixed,[slack-e1]]).astype(np.int64)
    up=np.concatenate([np.full(60,cap),[min(cap,(slack-e1)//max(int(x),1)) for x in e]]).astype(np.int64)
    meta=dict(c=c,cm=cm,case=case,cap=cap,slack=slack,need=need,base=base,e1=e1,cols=cols)
    return A,b,g,up,need-base,meta
