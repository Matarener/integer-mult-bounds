"""EXACT-INVOICE PRICER for P104-family words, callable inside search loops (DESIGNER/infra).
Replaces the *marginal* weights of stage3/model2.py (cw[d] = kappa(P+18 e_d) linearised at base) by the real invoice:
  kappa = root of  sum_r (T_r - P_r) r^(1-k) = 0   with  T = 18*helpers + outer_T,  P = 18*paid + outer_P
(price.py: assemble() + run()); the outer part is word-independent for the P104 controller (constants below, verified
against stage3/inv.json).  Also the SIDE CONSTRAINTS of price.py that a root-only model never sees:
  alpha = Mom(P,1-k)/Mom(T,1-k) < 1-1e-10 ; gamma = Mom(P,1-k+.2)/(17^.2 Mom(T,1-k)) < .97 ;
  delta = 18*sum(T)/(17^k Mom(T,1-k)) < .97  (completion tail, c=17,b=18)   -> these bound the NUMBER of fields.
and the verifier budgets: events < 26000, local_scalar + 1000*(paid jobs + 2*helpers + 2*104 + 4*104 + 4*8) < 1e7.
API:  inv=invoice(rep)  (rep from legal.check)  -> (T,P)
      kappa(T,P)  float root (1e-15);  kappa_dec(T,P) Decimal-50 root;  Pricer(T,P).delta(dT,dP) -> new kappa in O(#ranks)
      side(T,P,k=None) -> dict(alpha,gamma,delta,ok);  budgets(rep) -> dict
CLI: python price_exact.py WORD.json.gz"""
import math,sys,collections,decimal
sys.path.insert(0,__file__.rsplit('/',1)[0])
CALLS=18
TOUT={145:208,73:208, **{r:416 for r in range(17,66,8)}}
POUT={1:15*104,72:208, **{r:416 for r in range(16,65,8)}}
def invoice(rep):
    T=collections.Counter(TOUT); P=collections.Counter(POUT)
    for r,n in rep['helpers'].items(): T[r]+=CALLS*n
    for r,n in rep['paid'].items(): P[r]+=CALLS*n
    return dict(T),dict(P)
def f(T,P,k):
    e=1-k; return sum(n*r**e for r,n in T.items())-sum(n*r**e for r,n in P.items())
def kappa(T,P,lo=1e-5,hi=0.02):
    for _ in range(100):
        m=(lo+hi)/2
        if f(T,P,m)>0: lo=m
        else: hi=m
    return lo
def kappa_dec(T,P,prec=50):
    decimal.getcontext().prec=prec; D=decimal.Decimal
    def g(k):
        e=1-k
        return sum(n*(D(r).ln()*e).exp() for r,n in T.items())-sum(n*(D(r).ln()*e).exp() for r,n in P.items())
    lo,hi=D('0.00001'),D('0.02')
    for _ in range(150):
        m=(lo+hi)/2
        if g(m)>0: lo=m
        else: hi=m
    return lo
class Pricer:
    """Newton on k with the (T,P) tables held as dicts; delta() is O(#distinct ranks)*3 iterations (microseconds)."""
    def __init__(s,T,P): s.T=dict(T); s.P=dict(P); s.k=kappa(s.T,s.P)
    def _newton(s,k):
        for _ in range(8):
            e=1-k
            F=sum(n*r**e for r,n in s.T.items())-sum(n*r**e for r,n in s.P.items())
            dF=-sum(n*r**e*math.log(r) for r,n in s.T.items())+sum(n*r**e*math.log(r) for r,n in s.P.items())
            nk=k-F/dF
            if abs(nk-k)<1e-16: return nk
            k=nk
        return k
    def delta(s,dT=None,dP=None,commit=False):
        T=dict(s.T); P=dict(s.P)
        for r,n in (dT or {}).items(): T[r]=T.get(r,0)+n
        for r,n in (dP or {}).items(): P[r]=P.get(r,0)+n
        k=s._newton(s.k)
        # newton on modified tables
        s2=Pricer.__new__(Pricer); s2.T=T; s2.P=P; k=s2._newton(s.k)
        if commit: s.T,s.P,s.k=T,P,k
        return k
def side(T,P,k=None,c=17,b=18,u=0.2,decay=0.97):
    k=kappa(T,P)-1e-9 if k is None else k
    t=1-k; mt=sum(n*r**t for r,n in T.items()); mp=sum(n*r**t for r,n in P.items())
    mpu=sum(n*r**(t+u) for r,n in P.items())
    a=mp/mt; g=mpu/(c**u*mt); d=b*sum(T.values())/(c**k*mt)
    return dict(alpha=a,gamma=g,delta=d,ok=(a<1-1e-10 and g<decay and d<decay),sumT=sum(T.values()),momT=mt)
def budgets(rep,helpers=None):
    n=rep['nevents']; H=sum(rep['helpers'].values()); pj=sum(rep['paid'].values())
    routes=(pj+2*H+2*104+4*104+4*8)*1000
    return dict(events=n,event_slack=26000-n,scalar=rep['scalar'],routes=routes,scalar_budget_used=rep['scalar']+routes,
                scalar_budget_slack=10**7-rep['scalar']-routes,jobs_units=pj+2*H+2*104+4*104+4*8)
def maxextra(T,P,r,kind='T',decay=0.97):
    """how many extra rank-r fields in T (kind T) can be added before delta>=decay at fixed kappa (hard constraint headroom)"""
    n=0;TT=dict(T)
    while True:
        TT[r]=TT.get(r,0)+1
        if side(TT,P,kappa(T,P)-1e-9)['delta']>=decay: return n
        n+=1
        if n>5000: return n
if __name__=='__main__':
    import legal
    w=legal.load(sys.argv[1]); rep=legal.check(w); T,P=invoice(rep)
    print('legal',rep['ok'],rep['violations'][:3]); print('kappa %.13f'%kappa(T,P),'dec',str(kappa_dec(T,P))[:16])
    print(side(T,P)); print(budgets(rep))

def tail_feasible(T,P,k=None,cs=range(2,40),us=(0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5,0.7,1.0)):
    """Best (c,b,u) for price.py's tail block: need  c^64<b^63 (integers), alpha<1-reserve, gamma<D, delta<D,
    D^128<1/16 (so D<0.97857).  Returns (margin, dict) with margin = D_max - max(gamma,delta) (>0 feasible).
    NB u and the exponent power 1024/ 'wins' arithmetic of price.py are NOT re-derived here (u=.2 is the shipped value)."""
    k=kappa(T,P)-1e-9 if k is None else k
    D=(1/16)**(1/128)-1e-6; t=1-k
    mt=sum(n*r**t for r,n in T.items()); sT=sum(T.values()); best=None
    for c in cs:
        b=c+1
        while c**64>=b**63: b+=1
        # smallest b with c^64<b^63 is best for delta
        for u in us:
            mpu=sum(n*r**(t+u) for r,n in P.items())
            g=mpu/(c**u*mt); d=b*sT/(c**k*mt); m=D-max(g,d)
            if best is None or m>best[0]: best=(m,dict(c=c,b=b,u=u,gamma=g,delta=d,D=D))
    return best
def maxextra_best(T,P,r,limit=3000):
    k=kappa(T,P)-1e-9; n=0; TT=dict(T)
    lo,hi=0,limit
    while lo<hi:
        m=(lo+hi+1)//2; TT=dict(T); TT[r]=TT.get(r,0)+m
        if tail_feasible(TT,P,k)[0]>0: lo=m
        else: hi=m-1
    return lo
