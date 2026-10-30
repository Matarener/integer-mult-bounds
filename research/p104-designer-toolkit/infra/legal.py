"""LEGALITY ORACLE for P104-family words (DESIGNER/infra).  Re-implements the checks of
PR5544/5545 research/p104-productive-controller/local.py replay() (+ the literal-port part of native()) as a
function that returns ALL violations (not first exception) in about a second per 25k-event word.
Endpoint (all 743 public+owned rows) is checked by random evaluation mod p=2^61-1 on K random inputs
(error <= 25311*K/p ~ 1e-14 per word; exact mode: legal_exact() delegates to the real local.replay).
API:  rep = check(word)            -> dict(ok, violations[list of (idx, rule, detail)], paid, helpers, owned, scalar, nevents)
      check(word, events=None)     word = dict(frames, initial, final, live, ports, program)
      budget(word)                 -> slack to verifier constants (26000 events, 1e7 scalar)
SPEC lines mirrored (local.py): MOVE nested (l.~'Nested chronological transport'), ADD/COPY common chart
('Common scalar chart'), dyadic ('Dyadic scalar coefficient'), COPY into cleared owned, CLEAR at declared frame
(content NOT checked, CLEAR erases dirty owned content for free), peak owned==1, min helper rank>0, 104 literal ports."""
import gzip,json,random,collections,sys
from fractions import Fraction as Q
P=(1<<61)-1
def load(path):
    return json.load(gzip.open(path)) if path.endswith('.gz') else json.load(open(path))
def spans(w):
    out=[]
    for b in w['frames']:
        s={0}
        for v in b:
            if not(type(v) is int and 0<v<512 and v not in s): raise ValueError('dependent basis '+str(b))
            s|={x^v for x in s}
        out.append(frozenset(s))
    return out
def check(w,K=2,seed=1,maxviol=50,contract=True):
    """contract=False: only the per-event rules (frame law, ownership, nesting, dyadic) -- for toy words / counterexample searches."""
    V=[];prog=w['program']
    def bad(i,rule,d=''):
        if len(V)<maxviol: V.append((i,rule,d))
    if len(prog)>=26000: bad(-1,'Fixed operation bound','%d>=26000'%len(prog))
    fr=spans(w); nf=len(fr); dim=[len(b) for b in w['frames']]
    NPUB=len(w['initial']); NR=NPUB+8   # w['public'] is stale in hand-off words
    cur=list(w['initial'])+[None]*8
    rnd=random.Random(seed); v0=[[rnd.randrange(P) for _ in range(NR)] for _ in range(K)]
    val=[list(x) for x in v0]            # K vectors of register values
    paid=collections.Counter(); owned=set(); peak=0; scalar=0
    inv2=pow(2,P-2,P)
    for i,e in enumerate(prog):
        op,r=e[0],e[1]
        if not(0<=r<NR): bad(i,'Role index',r); continue
        if op=='MOVE':
            _,r,a,b,pv=e
            if cur[r]!=a or ((r in owned)!=bool(pv)): bad(i,'Transport source and ownership',(r,cur[r],a,pv)); 
            ok=(fr[b]<fr[a]) if pv else (fr[a]<fr[b])
            if not ok: bad(i,'Nested chronological transport',(r,a,b,pv))
            paid[abs(dim[b]-dim[a])]+=1; cur[r]=b
        elif op=='INIT':
            if not(r>=NPUB and r not in owned): bad(i,'Owned initialization',r)
            owned.add(r); peak=max(peak,len(owned))
            for x in val: x[r]=0
            cur[r]=e[2]; scalar+=2
        elif op=='CLEAR':
            if not(r in owned and cur[r]==e[2]): bad(i,'Owned erasure at declared frame',r)
            for x in val: x[r]=0
            cur[r]=None; owned.discard(r); scalar+=2
        else:
            q=Q(e[-2]); f=e[-1]
            if not q or cur[r]!=f: bad(i,'Scalar destination and coefficient',(r,cur[r],f)); continue
            n,d=abs(q.numerator),q.denominator
            if d&(d-1): bad(i,'Dyadic scalar coefficient',q)
            if not abs(q)+1<2**16: bad(i,'Fixed scalar growth bound',q)
            qm=(q.numerator%P)*pow(d,P-2,P)%P
            if op=='SCALE':
                if n&(n-1): bad(i,'Dyadic unit SCALE',q)
                for x in val: x[r]=x[r]*qm%P
                scalar+=2*(abs(n.bit_length()-d.bit_length())+int(q<0))
            else:
                s=e[2]
                if not(s!=r and 0<=s<NR and cur[s]==f): bad(i,'Common scalar chart',(r,s,cur[s],f)); continue
                if op=='COPY':
                    if not(r in owned and all(x[r]==0 for x in val)): bad(i,'COPY into cleared owned field',r)
                    for x in val: x[r]=x[s]*qm%P
                elif op=='ADD':
                    for x in val: x[r]=(x[r]+qm*x[s])%P
                else: bad(i,'Scalar opcode',op); continue
                scalar+=2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    if owned or (contract and peak!=1): bad(-1,'All public and owned exits','owned=%s peak=%d'%(sorted(owned),peak))
    if cur[:NPUB]!=list(w['final']): bad(-1,'Final frames','%d registers differ: %s'%(sum(1 for a,b in zip(cur,w['final']) if a!=b),[(i,a,b) for i,(a,b) in enumerate(zip(cur,w['final'])) if a!=b][:12]))   # (reg, frame reached, frame declared)
    if not contract:
        return dict(ok=not V,violations=V,paid=dict(sorted(paid.items())),owned_peak=peak,scalar=scalar,nevents=len(prog),vals=val)
    live=set(w['live'])
    nbad=0
    for r in range(NR):
        for k in range(K):
            ex=v0[k][r] if r<NPUB else 0
            if r-112 in live and r<NPUB: ex=(ex+v0[k][r-112])%P
            if val[k][r]!=ex: nbad+=1; break
    if nbad: bad(-1,'Endpoint rows (random evaluation)','%d rows differ: %s'%(nbad,[r for r in range(NR) if any(val[k][r]!=((v0[k][r] if r<NPUB else 0)+(v0[k][r-112] if (r-112 in live and r<NPUB) else 0))%P for k in range(K))][:12]))
    main=live|{r+112 for r in live}
    hel=collections.Counter(dim[w['final'][r]]-dim[w['initial'][r]] for r in range(NPUB) if r not in main)
    if not(len(live)==len(w['ports'])==104 and len(main)==208 and (not hel or min(hel)>0)): bad(-1,'Independent productive inputs',(len(live),len(main),min(hel) if hel else None))
    for r in range(NPUB):
        if r not in main and not fr[w['initial'][r]]<=fr[w['final'][r]]: bad(-1,'Helper endpoints not nested',r)
    for r,q in zip(w['live'],w['ports']):
        if w['frames'][w['initial'][r]]!=[q]: bad(-1,'Literal central port',r)
        if fr[w['final'][r+112]]!=frozenset(x for x in range(512) if not (x&q).bit_count()%2): bad(-1,'Literal output hyperplane',r)
    return dict(ok=not V,violations=V,paid=dict(sorted(paid.items())),helpers=dict(sorted(hel.items())),
                owned_peak=peak,scalar=scalar,nevents=len(prog))
def budget(w,rep=None):
    rep=rep or check(w)
    paidsum=sum(rep['paid'].values())
    return dict(events=len(w['program']),event_cap=26000,event_slack=26000-len(w['program']),
                scalar=rep['scalar'],scalar_cap=10**7,scalar_note='price.py also adds local_routes=(sum paid+helper normalizers 2*hel+104*2*? ...)*1000; use price_exact.budget')
if __name__=='__main__':
    import time;t=time.time();w=load(sys.argv[1]);rep=check(w)
    print(rep['ok'],rep['violations'][:5],rep['paid'],rep['helpers'],rep['scalar'],rep['nevents'],'%.1fs'%(time.time()-t))
