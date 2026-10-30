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
# ---- prepared573 verifier profile (PR5612 'delayed shared preparation': research/p104-delayed-shared-relay/prepared573_local.py)
# A word carries `retired_public` (public role whose input row is zeroed and which is re-used as an OWNED scratch role), `owned_roles`, `independent_public`, `fields`.
# Differences from the PR5599 local.py (all cited in toolkit/module docstring via prepared573_local.py line numbers):
#   l.33-35 exact interface (fields 756, retired [573], independent_public = 747 regs, owned_roles = [573]+748..755);   l.38-40 current[573]=None, owned = set(owned_roles)
#   l.55    INIT needs r in owned_roles (not r >= public);   l.88-89 peak owned == 2, owned lifetime census == 11, finals checked on independent_public only
#   l.92    endpoint row of the retired role is {} (not e_r);   l.97 / l.136 helper census and transpose exclude the retired role
PREPARED=dict(retired=[573],peak=2,lifetimes=11)     # public count / fields are taken from the word (PR5612 pins 748/756; each prepared PR retargets those literals, like the 750/758/749 -> 748/756/747 edit of PR5606 -> PR5612)
# ---- owned_fields profile (PR5627 helper-subspace-splits/local.py, used by #5644/#5650/#5660): the word carries `owned_fields` (8 or 9 owned scratch roles after the public ones).
# Differences from the PR5599 local.py (diff of the two files is exactly this): owned inventory bound 8<=owned_fields<=9 (default 8), public bound 735<=public<=750, roles/charts range
# over public+owned, and the exit rule is 0<peak<=2 instead of peak==1.  The package verify.py of #5644/#5650/#5660 additionally pins (public,owned_fields,lifetimes,peak)==(743,9,11,2).
OWNED9=dict(public=743,owned_fields=9,lifetimes=11,peak=2)
def profile_params(w):
    """Verifier pins (public, owned_fields, lifetimes, peak) of the word under test, read from a profile OBJECT, never from constants in the screens.
    Precedence: word['verifier_profile'] (dict) > JSON file named by env TK_VERIFIER_PROFILE (TKADOPT: toolkit/profiles/<name>.json, keys public/owned_fields/lifetimes/peak) > built-in
    PR5627 (OWNED9) / PR5612 (PREPARED) defaults.  Owned count falls back to the word's own `owned_fields` key."""
    import os
    p=dict(OWNED9) if has_of(w) else dict(public=len(w['initial']),owned_fields=8,lifetimes=PREPARED['lifetimes'] if w.get('retired_public') else None,peak=PREPARED['peak'] if w.get('retired_public') else 1)
    f=os.environ.get('TK_VERIFIER_PROFILE')
    if f:
        import json; J=json.load(open(f)); I=J.get('interface') or {}; C=J.get('compiler') or {}
        if I.get('public_bound'): p['public_range']=tuple(I['public_bound'])
        if I.get('owned_bound'): p['owned_range']=tuple(I['owned_bound'])
        if C.get('event_cap'): p['event_cap']=C['event_cap']
        p.update({k:v for k,v in J.items() if k in('public','owned_fields','lifetimes','peak','public_range','owned_range','event_cap')})
    p.update({k:v for k,v in (w.get('verifier_profile') or {}).items() if k in('public','owned_fields','lifetimes','peak','public_range','owned_range','event_cap')})
    p.setdefault('public_range',(735,750)); p.setdefault('owned_range',(8,9)); p.setdefault('event_cap',26000)
    if os.environ.get('TK_FREE_BOUNDS'):   # package-literal conventions (A41 event cap, public/owned inventory): not SPEC; a shipping package sets its own literals
        p['public_range']=(0,10**9); p['owned_range']=(0,10**9); p['event_cap']=10**9
    if os.environ.get('TK_EVENT_CAP') is not None:   # CAPFREE: explicit event-cap override (tk --cap-free sets 0 = no cap; N = declare bound N); public/owned ranges untouched
        _c=int(os.environ['TK_EVENT_CAP']); p['event_cap']=_c if _c>0 else 10**9
    return p
def nown(w): return (w.get('verifier_profile') or {}).get('owned_fields',w.get('owned_fields',8))
def has_of(w): return 'owned_fields' in w
def guard8(w,tool):
    if nown(w)!=8: raise SystemExit('%s: not owned_fields-aware (word has %d owned roles); use tk check / price / accept'%(tool,nown(w)))
def retired_of(w): return list(w.get('retired_public') or [])
def is_prepared(w): return bool(w.get('retired_public'))
def owned_set(w):
    """registers that are OWNED scratch (INIT/CLEAR lifetimes): r >= public, plus the retired public roles of a prepared word"""
    n=len(w['initial']); return set(range(n,n+nown(w)))|set(retired_of(w))
def check(w,K=2,seed=1,maxviol=50,contract=True):
    """contract=False: only the per-event rules (frame law, ownership, nesting, dyadic) -- for toy words / counterexample searches."""
    V=[];prog=w['program']
    def bad(i,rule,d=''):
        if len(V)<maxviol: V.append((i,rule,d))
    PP=profile_params(w); EC=PP['event_cap']; PLO,PHI=PP['public_range']; OLO,OHI=PP['owned_range']   # bounds are profile data (package literals, A41)
    if len(prog)>=EC: bad(-1,'Fixed operation bound','%d>=%d'%(len(prog),EC))
    fr=spans(w); nf=len(fr); dim=[len(b) for b in w['frames']]
    NPUB=len(w['initial']); NO=nown(w); NR=NPUB+NO; OF=has_of(w)   # w['public'] is stale in hand-off words
    RET=set(retired_of(w)); OWN=owned_set(w); prepared=bool(RET); lifetimes=0
    if OF:
        if not(type(NO) is int and OLO<=NO<=OHI): bad(-1,'Owned inventory bound',NO)
        if not(PLO<=NPUB<=PHI): bad(-1,'Public inventory bound',NPUB)
    cur=list(w['initial'])+[None]*NO
    for r in RET:
        if 0<=r<NPUB: cur[r]=None
    if prepared:
        iface=(w.get('fields')==NR and sorted(RET)==PREPARED['retired'] and w.get('independent_public')==[r for r in range(NPUB) if r not in RET]
               and w.get('owned_roles')==sorted(RET)+list(range(NPUB,NR)) )
        if not iface: bad(-1,'Exact independent and owned interface','public %d fields %s retired %s'%(NPUB,w.get('fields'),sorted(RET)))
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
            if not(r in OWN and r not in owned): bad(i,'Owned initialization',r)
            lifetimes+=1; owned.add(r); peak=max(peak,len(owned))
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
                if not(s!=r and 0<=s<NR and cur[s]==f): bad(i,'Common scalar chart',(r,s,cur[s] if 0<=s<NR else None,f)); continue
                if op=='COPY':
                    if not(r in owned and all(x[r]==0 for x in val)): bad(i,'COPY into cleared owned field',r)
                    for x in val: x[r]=x[s]*qm%P
                elif op=='ADD':
                    for x in val: x[r]=(x[r]+qm*x[s])%P
                else: bad(i,'Scalar opcode',op); continue
                scalar+=2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    PP=profile_params(w); wantpeak=PP['peak'] if prepared else 1
    if OF and not prepared:     # local.py of PR5627: 0<peak<=2
        if owned or (contract and not(0<peak<=PP['peak'])): bad(-1,'All public and owned exits','owned=%s peak=%d (need 1..%d)'%(sorted(owned),peak,PP['peak']))
    elif owned or (contract and peak!=wantpeak): bad(-1,'All public and owned exits','owned=%s peak=%d (need %d)'%(sorted(owned),peak,wantpeak))
    if prepared and contract and lifetimes!=PP['lifetimes']: bad(-1,'Complete owned lifetime census','%d lifetimes (need %d)'%(lifetimes,PP['lifetimes']))
    if OF and contract and not prepared and (NPUB,NO,lifetimes,peak)!=(PP['public'],PP['owned_fields'],PP['lifetimes'],PP['peak']):
        bad(-1,'Complete public and owned inventories','(public,owned_fields,lifetimes,peak)=%s need %s'%((NPUB,NO,lifetimes,peak),tuple(PP.values())))
    if [cur[r] for r in range(NPUB) if r not in RET]!=[w['final'][r] for r in range(NPUB) if r not in RET]: bad(-1,'Final frames','%d registers differ: %s'%(sum(1 for r,(a,b) in enumerate(zip(cur,w['final'])) if a!=b and r not in RET),[(i,a,b) for i,(a,b) in enumerate(zip(cur,w['final'])) if a!=b and i not in RET][:12]))   # (reg, frame reached, frame declared)
    if not contract:
        return dict(ok=not V,violations=V,paid=dict(sorted(paid.items())),owned_peak=peak,scalar=scalar,nevents=len(prog),vals=val,lifetimes=lifetimes)
    live=set(w['live'])
    nbad=0
    for r in range(NR):
        for k in range(K):
            ex=v0[k][r] if (r<NPUB and r not in RET) else 0
            if r-112 in live and r<NPUB: ex=(ex+v0[k][r-112])%P
            if val[k][r]!=ex: nbad+=1; break
    if nbad: bad(-1,'Endpoint rows (random evaluation)','%d rows differ: %s'%(nbad,[r for r in range(NR) if any(val[k][r]!=((v0[k][r] if (r<NPUB and r not in RET) else 0)+(v0[k][r-112] if (r-112 in live and r<NPUB) else 0))%P for k in range(K))][:12]))
    main=live|{r+112 for r in live}
    hel=collections.Counter(dim[w['final'][r]]-dim[w['initial'][r]] for r in range(NPUB) if r not in main and r not in RET)
    if not(len(live)==len(w['ports'])==104 and len(main)==208 and (not hel or min(hel)>0)): bad(-1,'Independent productive inputs',(len(live),len(main),min(hel) if hel else None))
    for r in range(NPUB):
        if r not in main and r not in RET and not fr[w['initial'][r]]<=fr[w['final'][r]]: bad(-1,'Helper endpoints not nested',r)
    for r,q in zip(w['live'],w['ports']):
        if w['frames'][w['initial'][r]]!=[q]: bad(-1,'Literal central port',r)
        if fr[w['final'][r+112]]!=frozenset(x for x in range(512) if not (x&q).bit_count()%2): bad(-1,'Literal output hyperplane',r)
        # FRAMEGAP (Oct 27): neither the swarm local.py/native() nor the old oracle pinned the OTHER two main endpoints. PROOF.md of p104-productive-controller fixes main boundary
        # progress at 2*104*8 = 1664 (X: [q] -> full 9-dim space, Y: 0-dim -> hyperplane); pricing charges that as a constant, so a word that leaves X below dim 9 / Y above dim 0 skips the progress.
        if len(w['frames'][w['final'][r]])!=9: bad(-1,'Main X final frame (SPEC: full 9-dim space)',(r,len(w['frames'][w['final'][r]])))
        if len(w['frames'][w['initial'][r+112]])!=0: bad(-1,'Main Y initial frame (SPEC: 0-dim)',(r+112,len(w['frames'][w['initial'][r+112]])))
    return dict(ok=not V,violations=V,paid=dict(sorted(paid.items())),helpers=dict(sorted(hel.items())),
                owned_peak=peak,scalar=scalar,nevents=len(prog),lifetimes=lifetimes,prepared=prepared)
def budget(w,rep=None):
    rep=rep or check(w)
    paidsum=sum(rep['paid'].values())
    _ec=profile_params(w)['event_cap'] if os.environ.get('TK_EVENT_CAP') is not None else 26000      # CAPFREE: default unchanged
    return dict(events=len(w['program']),event_cap=_ec,event_slack=_ec-len(w['program']),
                scalar=rep['scalar'],scalar_cap=10**7,scalar_note='price.py also adds local_routes=(sum paid+helper normalizers 2*hel+104*2*? ...)*1000; use price_exact.budget')
if __name__=='__main__':
    import time;t=time.time();w=load(sys.argv[1]);rep=check(w)
    print(rep['ok'],rep['violations'][:5],rep['paid'],rep['helpers'],rep['scalar'],rep['nevents'],'%.1fs'%(time.time()-t))
