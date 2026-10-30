"""GAPMAP ledger: per-register exact invoice lines.  usage: ledger.py WORD   (pickles lines)"""
import sys,os,json,gzip,collections,math
TK=__import__('os').path.dirname(__import__('os').path.abspath(__file__)); sys.path.insert(0,TK); sys.path.insert(0,TK+'/infra')
import price_exact as X
def load(p):
    if not os.path.exists(p): p=TK+'/words/%s.json.gz'%p
    return json.load(gzip.open(p))
def lines(w):
    n=len(w['initial']); dim=[len(b) for b in w['frames']]
    live=set(w['live']); Xs=live; Ys={r+112 for r in live}
    cur=list(w['initial'])+[None]*10000
    mv=collections.defaultdict(list)   # reg -> [(rank, owned_flag)]
    for e in w['program']:
        if e[0]=='MOVE':
            _,r,a,b,pv=e; mv[r].append(abs(dim[b]-dim[a]))
        elif e[0]=='INIT': cur[e[1]]=e[2]
    role={}
    for r in range(n): role[r]='X' if r in Xs else ('Y' if r in Ys else 'H')
    for r in mv:
        if r>=n: role[r]='O'
    cred={r:dim[w['final'][r]]-dim[w['initial'][r]] for r in range(n) if role[r]=='H'}
    return role,mv,cred,dim
def invoice_parts(role,mv,cred,sel=None):
    """T,P counters of the register lines in sel (set of roles), without outer"""
    T=collections.Counter(); P=collections.Counter()
    for r,l in mv.items():
        if sel is None or role[r] in sel:
            for x in l: P[x]+=18
    for r,c in cred.items():
        if sel is None or 'H' in sel: T[c]+=18
    return T,P
OUT_T=collections.Counter(X.TOUT); OUT_P=collections.Counter(X.POUT)
def kap(T,P):
    TT=collections.Counter(OUT_T); PP=collections.Counter(OUT_P)
    TT.update(T); PP.update(P); return X.kappa(dict(TT),dict(PP))
def wt(C,k): return sum(n*r**(1-k) for r,n in C.items())
if __name__=='__main__':
    w=load(sys.argv[1]); role,mv,cred,dim=lines(w)
    T,P=invoice_parts(role,mv,cred); k=kap(T,P); print('kappa',k)
