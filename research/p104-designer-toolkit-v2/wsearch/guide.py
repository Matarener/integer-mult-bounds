"""guide -- guidance hooks for multi-step word search (MACROS 3).
(a) MARGINAL-COST STEERING   heat(w): per-register sum over its paid MOVEs of the R0-law marginal kappa of removing one paid rank of that size (the `tk sens` table, per register);
    hot_regs(w, n) = the n hottest registers; hot_events(S, heat) = event hotness.  Sites touching cold registers are not priced (or priced last).
(b) PLATEAU / DIP TOLERANCE  Dip policy: a candidate whose own kappa is >= k - slack is kept as a SEED; the driver (macros.search) expands each seed one more level focused on the registers
    it touched and accepts the PAIR if the pair beats k.  anneal(): Metropolis acceptance with a geometric temperature schedule (used for the #5565 tuning)."""
import sys,os,math,random
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
from tkcommon import legal,X
import movekit as M, sens
def paid_weights(w):
    """d -> kappa gain of removing ONE paid rank-d move (R0-law marginal), for d=1..9"""
    rep=legal.check(M.pin(w),maxviol=1); T,P=X.invoice(rep); b=sens.kap(T,P); out={}
    for d in range(1,10):
        if P.get(d,0)<=0: out[d]=0.0; continue
        from collections import Counter
        P2=Counter(P); P2[d]-=1; out[d]=sens.kap(T,P2)-b
    return out
def heat(w,weights=None):
    """register -> summed marginal cost of its paid MOVEs"""
    weights=weights or paid_weights(w); fr=legal.spans(M.pin(w)); dim=[len(b) for b in w['frames']]; own=legal.owned_set(w); h={}
    for e in w['program']:
        if e[0]!='MOVE': continue
        _,r,a,b=e[:4]
        paid=(fr[b]<fr[a]) if r in own else (fr[a]<fr[b])
        if paid: h[r]=h.get(r,0.0)+weights.get(abs(dim[b]-dim[a]),0.0)
    return h
def density(w,weights=None):
    """register -> (unweighted MOVE count incl. unpaid) / (number of scalar events touching it): moves per use.  Measured on #5565/5580: helper 531 ranks 26/743 here vs 560/743 by absolute heat"""
    nev={}; mv={}
    for e in w['program']:
        if e[0]=='MOVE': mv[e[1]]=mv.get(e[1],0)+1
        elif e[0]=='ADD': nev[e[1]]=nev.get(e[1],0)+1; nev[e[2]]=nev.get(e[2],0)+1
        elif e[0]=='COPY': nev[e[1]]=nev.get(e[1],0)+1; nev[e[2]]=nev.get(e[2],0)+1
        else: nev[e[1]]=nev.get(e[1],0)+1
    return {r:mv[r]/max(1,nev.get(r,0)) for r in mv}
def hot_regs(w,n=200,h=None,mode='density'):
    h=h or (density(w) if mode=='density' else heat(w)); return {r for r,_ in sorted(h.items(),key=lambda x:-x[1])[:n]}
def hot_list(w,n=200,mode='density'):
    """the n hottest registers as a list, hottest first (macros that cap their site count walk it in order)"""
    h=density(w) if mode=='density' else heat(w); return [r for r,_ in sorted(h.items(),key=lambda x:-x[1])[:n]]
def hot_rank(w,r,h=None):
    h=h or heat(w); order=sorted(h,key=lambda x:-h[x]); return order.index(r)+1 if r in h else None
class Dip:
    """seeds = candidates within `slack` below the current kappa, best first, at most `width`"""
    def __init__(s,slack=2e-6,width=12): s.slack=slack; s.width=width
    def seeds(s,k,cands): return [c for c in sorted(cands,key=lambda c:-c[0]) if c[0]>=k-s.slack][:s.width]
def anneal(k_cur,k_new,T,rng=random):
    """Metropolis acceptance on kappa (units of 1e-7)"""
    d=(k_new-k_cur)*1e7
    return d>=0 or rng.random()<math.exp(d/max(T,1e-9))
def temp(step,T0=3.0,alpha=0.9): return T0*alpha**step
