"""admit -- exact ADMISSIBILITY oracle for P104-family words (GENBUDGET.

`tk check` says a word is LEGAL.  A word is ADMISSIBLE when, in addition, the package's pricing.py would accept it:
  events    len(program) < event_cap                          (local.py 'Fixed operation bound'; package literal, 26000)
  inventory (public, owned_fields, lifetimes, peak) pins      (local.py 'Complete public and owned inventories'; package literals)
  scalar    local_scalar + routes < scalar_cap                (pricing.py; routes = (sum paid + 2*helpers + 208 + 4*104 + 4*lifetimes)*1000; cap 10^7)
  raw       18*cap + 15*1664 + 32*104*(phys+boundary+1026) < 1e9   (pricing.py 'Complete nonrecursive raw bound'; word independent, couples to the scalar cap)
  tail      alpha < 1-eps, gamma < D, delta < D, D^(v/8) < 1/16, 1/(1+v eps)+4/2^32 < 1, c^64 < b^63           (pricing.py literals c,b,u,v,D,eps)
  theorem   1/(1+v eps) + 2 gamma^v + 2 delta^v < 1     (higher-moment-strictification README sec. 2: the REAL inequality; pricing's D-test is only a sufficient form)
  compiler  theta^power < t*145^(-vT), 145^(vT) < 2^power, 2 (c^v)^64 <= (145^v)^63, H > 8v with (step j+1)^power < 2^j   (pricing.py; theta, power literals)

API
  check(src, lit=None, tested=None)  src = IncrWord | word dict | path/alias.  -> dict(constraints=[{name,kind,value,limit,slack,ok,note}], ok, counts, lit, tested)
        lit=None -> the word's adopted profile literals.  slack > 0 means admitted (all slacks are 'limit - value', >0 good).
  best(src)       -> choose the best legal FREE literals for this word (tail c,b,u,v,D,eps,power; event/scalar caps needed) and say whether ANY choice admits it:
                     dict(admits_any=bool, blockers=[...], lit=<chosen>, needs=dict(event_cap,scalar_cap,...), report=check(src, chosen))
  fmt(rep)        -> text.    CLI: python admit.py WORD [--profile P] [--best] [--json]
Exactness: moments are Decimal(60) evaluations of sum n r^s (pricing.py uses certified intervals; verdicts agree unless |slack| < 1e-25, which `borderline` flags).
"""
import sys,os,json,re,math,decimal,collections
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from tkcommon import *
decimal.getcontext().prec=60
D=decimal.Decimal
MAXRANK=145                       # ambient rank m in pricing.py (max target)
PHYS_RAW_CONST=15*1664+32*104*(363+1026)   # pricing.py raw = 18*10**7 + 15*1664 + 32*104*(events_phys+boundary+1026); events_phys+boundary = 363 calibrated on #5756 (raw_scalar_upper 184647552), word independent
RAW_BUDGET=10**9
_LN={}
def ln(r):
    if r not in _LN: _LN[r]=D(r).ln()
    return _LN[r]
def pw(r,e): return (ln(r)*e).exp()
def moment(H,e): return sum(n*pw(r,e) for r,n in H.items() if n)
def qd(x): return D(x.numerator)/D(x.denominator) if isinstance(x,Q) else D(x)
def dq(x,den=10**12): return Q(int((D(x)*den).to_integral_value(rounding=decimal.ROUND_CEILING)),den)

# ---------------------------------------------------------------------------------------------- literals
def lits_of(profile,w=None):
    """literal set of an adopted/legacy profile name (the pricing.py literals the PR ships)"""
    dp=DATA_PROFILES.get(profile); pr=PROFILES.get(profile) or {}
    c=(dp or {}).get('compiler') or {}
    tail=c.get('tail') or dict(u='1/5',v=1024,c=17,b=18)
    L=dict(profile=profile,
           decay=Q(c['decay']) if c.get('decay') else Q(pr.get('decay',0.97)).limit_denominator(1000),
           power=c.get('power') or pr.get('power',1000), v=tail['v'], c=tail['c'], b=tail['b'], u=Q(tail['u']),
           reserve=Q(c['reserve'].replace('10^','10**')) if False else _q(c.get('reserve'),pr.get('reserve',1e-10)),
           theta=Q(c['theta']) if c.get('theta') else Q(63,64),
           event_cap=(10**9 if os.environ.get('TK_EVENT_CAP')=='0' else (int(os.environ['TK_EVENT_CAP']) if os.environ.get('TK_EVENT_CAP') else (c.get('event_cap') or 26000))), scalar_cap=c.get('scalar_cap') or 10**7)
    if dp: L['pins']=dict(public=dp['public'],owned_fields=dp['owned_fields'],lifetimes=dp['lifetimes'],peak=dp['peak'],public_range=tuple((dp.get('interface') or {}).get('public_bound') or (dp['public'],dp['public'])),owned_range=tuple((dp.get('interface') or {}).get('owned_bound') or (dp['owned_fields'],)*2),peak_rule=(dp.get('interface') or {}).get('peak_rule'))
    return L
def _q(s,default):
    if not s: return Q(default).limit_denominator(10**13)
    m=re.match(r'^(\d+)/10\^(\d+)$',s)
    return Q(int(m.group(1)),10**int(m.group(2))) if m else Q(s)
def tested_of(profile):
    """(KAPPA, TESTED) claim literals of the profile's pricing.py, or None"""
    p=os.path.join(HERE,'profiles',str(profile),'pricing.py')
    if not os.path.exists(p): return None
    m=re.search(r"KAPPA, TESTED = Q\('([^']*)'\), Q\('([^']*)'\)",open(p).read())
    return (Q(m.group(1)),Q(m.group(2))) if m else None

# ---------------------------------------------------------------------------------------------- counts
def counts(src,profile=None):
    """-> dict(n, scalar, paid, helpers, lifetimes, peak, public, owned, live, T, P, profile, pp, kappa)"""
    if hasattr(src,'ledger') and hasattr(src,'chs'):          # IncrWord
        T,P=src.ledger()
        return dict(n=sum(len(c.evs) for c in src.chs),scalar=sum(c.scalar for c in src.chs),paid=dict(src.paid),helpers=dict(src.hel),lifetimes=sum(c.life for c in src.chs),
                    peak=max((c.peak for c in src.chs),default=0),public=src.NPUB,owned=src.NO,live=len(src.live),T=T,P=P,profile=src.profile,pp=src.PP,legal=src.legal_all)
    if isinstance(src,str): path,w=load(src)
    else: w=src; activate(w)
    name=profile or profile_of(w)[0]
    with use_profile(name):
        rep=legal.check(w); pp=legal.profile_params(w)
    T,P=X.invoice(rep)
    return dict(n=rep['nevents'],scalar=rep['scalar'],paid=rep['paid'],helpers=rep['helpers'],lifetimes=rep.get('lifetimes') or 0,peak=rep['owned_peak'],public=len(w['initial']),
                owned=legal.nown(w),live=len(w['live']),T=T,P=P,profile=name,pp=pp,legal=rep['ok'])
def routes_units(c):
    """pricing.py local_routes/1000 = sum(paid)+helper_normalizers(2*H)+main_adapters(2*live)+4*104+4*lifetimes"""
    return sum(c['paid'].values())+2*sum(c['helpers'].values())+2*c['live']+4*104+4*c['lifetimes']
def kappa_crossing(c):
    return X.kappa_dec(c['T'],c['P'],50)

# ---------------------------------------------------------------------------------------------- tail / compiler pieces
def ratios(T,P,tested,cc,bb,u):
    """alpha,gamma,delta exactly as pricing.py (tested = TESTED, t = 1-TESTED)"""
    t=1-tested
    mt=moment(T,t); mp=moment(P,t); mpu=moment(P,t+u)
    cu=pw(cc,u) if cc>0 else D(1)
    alpha=mp/mt; gamma=mpu/(cu*mt); delta=D(bb)*sum(T.values())/(pw(cc,tested)*mt)
    return alpha,gamma,delta
def theorem(alpha,gamma,delta,v,eps):
    """README sec.2 bound 1/(1+v eps)+2 gamma^v+2 delta^v ; <1 required.  pricing.py replaces the two tail terms by 4/2^32 (= 4 D^v at D^(v/8)=1/16), so adding 4/2^32 here would double count"""
    return D(1)/(1+D(v)*eps)+2*gamma**v+2*delta**v
def wins_H(step,power):
    """pricing.py: minimal right with (step*right+1)^power < 2^right (doubling+bisect), H = step*right.  Decimal-log comparison."""
    ln2=D(2).ln()
    wins=lambda j: D(power)*(D(step*j+1)).ln() < D(j)*ln2
    left,right=1,2
    while not wins(right): left,right=right,2*right
    while right-left>1:
        m=(left+right)//2
        if wins(m): right=m
        else: left=m
    return step*right,right,wins(right) and not wins(right-1)
def compiler_checks(tq,lit,kappa_claim):
    """-> list of (name, kind, value, limit, slack) for the compiler block; slack>0 ok.  Values in log10 units where sensible"""
    tested=qd(tq); t=1-tested; v=lit['v']; power=lit['power']; th=lit['theta']
    out=[]
    # eta = t*145^(-v T) > theta^power
    leta=t.ln()-D(v)*tested*ln(MAXRANK); lth=D(power)*qd(th).ln()
    out.append(('compiler eta>theta^power','real',float(leta),float(lth),float(leta-lth)))
    # 145^(v T) < 2^power
    a=D(v)*tested*ln(MAXRANK); b=D(power)*D(2).ln(); out.append(('compiler 145^(vT)<2^power','real',float(a),float(b),float(b-a)))
    # 2 (c^v)^64 <= (145^v)^63
    a=D(2).ln()+D(v)*64*ln(lit['c']); b=D(v)*63*ln(MAXRANK); out.append(('compiler 2(c^v)^64<=(145^v)^63','real',float(a),float(b),float(b-a)))
    # c^64<b^63 (integers)
    out.append(('tail c^64<b^63','real',lit['c']**64,lit['b']**63,lit['b']**63-lit['c']**64))
    gap=(tq-kappa_claim)/7
    if gap.numerator!=1: out.append(('compiler gap numerator 1','literal',gap,'1/N',-1)); return out
    H,right,ok=wins_H(gap.denominator,power)
    out.append(('compiler H>8v (finite threshold)','literal',float(H.bit_length()),float((8*v).bit_length()),1 if (H>8*v and ok) else -1))
    return out

# ---------------------------------------------------------------------------------------------- main oracle
def con(name,kind,value,limit,slack,note=''): return dict(name=name,kind=kind,value=value,limit=limit,slack=slack,ok=bool(slack>0),note=note)
def check(src,lit=None,tested=None,claim=None,profile=None,_c=None):
    """exact admissibility of `src` at literals `lit` (default: adopted profile literals).  tested/claim = (TESTED, KAPPA) pricing literals (Fractions); default: the profile's pricing.py literals
    else TESTED = crossing - 1e-10, KAPPA = TESTED - 7e-12 (documented rule."""
    c=_c or counts(src,profile)
    lit=dict(lit or lits_of(c['profile'])); lit.setdefault('pins',lits_of(c['profile']).get('pins'))
    kd=kappa_crossing(c)
    if tested is None:
        tk=tested_of(c['profile']) if lit.get('use_profile_tested',True) else None
        if tk and abs(D(tk[1].numerator)/D(tk[1].denominator)-kd)<D('1e-6'): claim,tested=tk
        else: tested=dq(kd-D('1e-10')); claim=tested-Q(7,10**12)
    td=qd(tested)
    CS=[]
    # --- events
    CS.append(con('events','literal',c['n'],lit['event_cap'],lit['event_cap']-c['n'],'local.py "Fixed operation bound" len(program)<cap (package convention A41)'))
    # --- inventory pins
    pins=lit.get('pins')
    if pins:
        okp=(pins['public_range'][0]<=c['public']<=pins['public_range'][1] and pins['owned_range'][0]<=c['owned']<=pins['owned_range'][1] and c['lifetimes']==pins['lifetimes'] and 0<c['peak']<=pins['peak'])
        CS.append(con('inventory','literal',(c['public'],c['owned'],c['lifetimes'],c['peak']),(pins['public'],pins['owned_fields'],pins['lifetimes'],pins['peak']),1 if okp else -1,'public,owned_fields,lifetimes,peak pins (verifier_profile of the word)'))
    # --- scalar
    ru=routes_units(c); used=c['scalar']+ru*1000
    CS.append(con('scalar','literal',used,lit['scalar_cap'],lit['scalar_cap']-used,'local_scalar %d + routes %d*1000 (paid MOVEs %d, 2H %d, adapters %d, outer 416, 4*lifetimes %d) < cap'%(c['scalar'],ru,sum(c['paid'].values()),2*sum(c['helpers'].values()),2*c['live'],4*c['lifetimes'])))
    # raw bound coupled to the cap: 18*cap + const < 1e9 (const unknown to the word; pricing 18*10**7 literal) -> report the cap ceiling
    smax=(RAW_BUDGET-PHYS_RAW_CONST)//18      # word independent: 363 calibrated on #5756 RESULT (raw_scalar_upper)
    CS.append(con('raw cap coupling','literal',lit['scalar_cap'],smax,smax-lit['scalar_cap'],'raw=18*cap+...<1e9 => cap <= ~%d (363 phys+boundary events calibrated on #5756; word independent)'%smax))
    # --- tail at the literals
    T,P=c['T'],c['P']
    al,ga,de=ratios(T,P,td,lit['c'],lit['b'],qd(lit['u']))
    eps=qd(lit['reserve']); Dd=qd(lit['decay']); v=lit['v']
    CS.append(con('alpha<1-eps','real',float(al),float(1-eps),float(1-eps-al),'alpha=P_t/T_t at TESTED'))
    CS.append(con('gamma<D','literal-D',float(ga),float(Dd),float(Dd-ga),'gamma=P_(t+u)/(c^u T_t), c=%d u=%s'%(lit['c'],lit['u'])))
    CS.append(con('delta<D','literal-D',float(de),float(Dd),float(Dd-de),'delta=b*sumT/(c^T T_t), b=%d sumT=%d (field cap)'%(lit['b'],sum(T.values()))))
    CS.append(con('D^(v/8)<1/16','literal',float(Dd**(v//8)),1/16,float(D(1)/16-Dd**(v//8)),'pricing "Both tail decay blocks" (D^128<1/16 at v=1024)'))
    th=theorem(al,ga,de,v,eps)
    CS.append(con('theorem tail <1','real',float(th),1.0,float(1-th),'1/(1+v eps)+2g^v+2d^v (README sec.2); pricing.py bounds the two tail terms by 4/2^32 via the D-test'))
    nrm=D(1)/(1+D(v)*eps)+D(4)/D(2**32)
    CS.append(con('normalized paid <1','literal',float(nrm),1.0,float(1-nrm),'pricing.py normalized = 1/(1+v eps)+4/2^32 (tail terms charged as 4/2^32 given D^(v/8)<1/16)'))
    for nm,kind,val,lim,sl in compiler_checks(tested,lit,claim): CS.append(con(nm,kind,val,lim,sl))
    # --- field cap: how many fields delta allows at these literals (productive fields, sum T)
    mt=moment(T,1-td); cap_fields=int((Dd*pw(lit['c'],td)*mt/lit['b']).to_integral_value(rounding=decimal.ROUND_FLOOR))
    CS.append(con('field cap (sum T)','derived',sum(T.values()),cap_fields,cap_fields-sum(T.values()),'delta<D  <=>  sumT < D c^T T_t / b'))
    return dict(constraints=CS,ok=all(x['ok'] for x in CS),counts={k:(v if not isinstance(v,(dict,collections.Counter)) or k in('paid','helpers') else '..') for k,v in c.items() if k not in('T','P','pp')},
                lit={k:(str(v) if isinstance(v,Q) else v) for k,v in lit.items() if k!='pins'},tested=str(tested),claim=str(claim),kappa=str(kd)[:18],profile=c['profile'])

# ---------------------------------------------------------------------------------------------- free-literal search
def best(src,profile=None,_c=None):
    """choose the best legal free literals; decide whether ANY literal choice admits the word.
    Free: event_cap, scalar_cap (<= raw ceiling), tail (c,b,u), v, D, eps, power.  Fixed by the word: counts, paid/helpers invoice, pins (the word must carry its own inventory)."""
    c=_c or counts(src,profile); base=lits_of(c['profile'])
    ap=check(src,None,_c=c)
    if ap['ok']:      # the adopted literals already admit it: no change
        return dict(admits_any=True,strict_ok=True,changes={},blockers=[],lit=ap['lit'],needs={},report=ap,tail_best=None,plan=plan(src,profile,_c=c),at_profile=ap)
    kd=kappa_crossing(c); tested=dq(kd-D('1e-10')); claim=tested-Q(7,10**12); td=qd(tested)
    T,P=c['T'],c['P']; t=1-td; mt=moment(T,t); sT=sum(T.values())
    alpha=moment(P,t)/mt; eps=dq((1-alpha)/2,10**13)             # eps just below 1-alpha
    blockers=[]
    # tail search over integer c in [2,m), b = least integer with c^64<b^63 (b<m), u on a grid >= TESTED (sigma>=1)
    best_t=None
    for cc in range(2,MAXRANK):
        bb=int(round(cc**(64/63)))-2
        bb=max(bb,cc+1)
        while cc**64>=bb**63: bb+=1
        if bb>=MAXRANK: continue
        delta=D(bb)*sT/(pw(cc,td)*mt)
        for uu in [Q(i,64) for i in range(1,129) if Q(i,64)>=tested]:
            gamma=moment(P,t+qd(uu))/(pw(cc,qd(uu))*mt)
            m=max(gamma,delta)
            if best_t is None or m<best_t[0]: best_t=(m,cc,bb,uu,gamma,delta)
    m,cc,bb,uu,gamma,delta=best_t
    tail_ok=m<1
    lit=dict(base); lit.update(c=cc,b=bb,u=uu,reserve=eps,event_cap=max(base['event_cap'],c['n']+1),scalar_cap=base['scalar_cap'])
    needs=dict(event_cap=c['n']+1)
    # scalar: needed cap and raw ceiling
    used=c['scalar']+routes_units(c)*1000; needs['scalar_cap']=used+1
    smax=(RAW_BUDGET-PHYS_RAW_CONST)//18
    needs['scalar_cap_ceiling_raw']=smax
    lit['scalar_cap']=max(base['scalar_cap'],used+1)
    lit['pins']=dict(public=c['public'],owned_fields=c['owned'],lifetimes=c['lifetimes'],peak=c['peak'],public_range=(c['public'],c['public']),owned_range=(c['owned'],c['owned']))   # the word carries its own inventory literals (verifier_profile)
    if used+1>smax: blockers.append('scalar: need cap %d > raw ceiling ~%d (routes %d*1000 alone; helpers %d, MOVEs %d)'%(used+1,smax,routes_units(c),sum(c['helpers'].values()),sum(c['paid'].values())))
    if not tail_ok: blockers.append('tail: best max(gamma,delta)=%.4f >= 1 at c=%d b=%d u=%s (fields %d)'%(float(m),cc,bb,uu,sT))
    if alpha>=1: blockers.append('alpha>=1 at TESTED')
    if c['peak']<=0: blockers.append('no owned lifetime')
    if tail_ok and alpha<1:
        # v, D, power: least v (multiple of 8) satisfying the theorem and the pricing D-test
        Dq=dq(m*D('1.0000001'),10**9) if m>D('0.5') else Q(1,2)
        Dd=qd(Dq)
        def good(v): return theorem(alpha,gamma,delta,v,qd(eps))<1 and Dd**(v//8)<D(1)/16 and D(1)/(1+D(v)*qd(eps))+D(4)/D(2**32)<1
        v=8
        while not good(v) and v<10**9: v*=2
        lo,hi=v//2,v
        while hi-lo>8:
            mid=(lo+hi)//16*8
            if mid<=lo: break
            if good(mid): hi=mid
            else: lo=mid
        v=hi if good(hi) else v
        lit.update(v=v,decay=Dq)
        # power: smallest multiple of 128 passing both compiler inequalities
        lth=qd(lit['theta']).ln(); leta=t.ln()-D(v)*td*ln(MAXRANK)
        pmin=max(math.ceil(float(leta/lth)),math.ceil(float(D(v)*td*ln(MAXRANK)/D(2).ln())))+1
        lit['power']=((pmin+127)//128)*128
    rep=check(src,lit,tested=tested,claim=claim,_c=c)
    ok_lit_all=rep['ok']
    # which constraints need literal changes relative to the adopted profile, and which are impossible
    changes={k:(str(lit[k]),str(base[k])) for k in ('event_cap','scalar_cap','decay','v','c','b','u','reserve','power','theta') if lit.get(k)!=base.get(k)}
    if lit.get('pins')!=base.get('pins'): changes['pins']=(lit['pins'],base.get('pins'))
    return dict(admits_any=(not blockers) and ok_lit_all,strict_ok=ap['ok'],changes=changes,blockers=blockers,lit={k:(str(x) if isinstance(x,Q) else x) for k,x in lit.items() if k!='pins'},needs=needs,report=rep,
                tail_best=dict(c=cc,b=bb,u=str(uu),gamma=float(gamma),delta=float(delta),margin=float(1-m)),plan=plan(src,profile,_c=c),
                at_profile=ap)

def plan(src,profile=None,_c=None,lit=None):
    """budget-aware generator targets at the ADOPTED literals (or `lit`): per resource, how many more 'unit helpers' (a helper with its own MOVE hops and ADD events) the budgets allow,
    using THIS word's average per-helper cost.  -> dict(per_helper=dict(events,scalar_units), max_helpers=dict(events,scalar,delta), binding=name, now=H)"""
    c=_c or counts(src,profile); lit=lit or lits_of(c['profile']); H=max(1,sum(c['helpers'].values()))
    ev_ph=c['n']/H; sc_ph=(c['scalar']+routes_units(c)*1000)/H; fixed_ev=0; fixed_sc=0
    kd=kappa_crossing(c); tested=dq(kd-D('1e-10')); td=qd(tested); mt=moment(c['T'],1-td); sT=sum(c['T'].values())
    dcap=int((qd(lit['decay'])*pw(lit['c'],td)*mt/lit['b']).to_integral_value(rounding=decimal.ROUND_FLOOR))
    # fields per helper: 18 calls each
    fields_ph=18.0
    out=dict(events=int((lit['event_cap']-1)/ev_ph),scalar=int(lit['scalar_cap']/sc_ph),delta=int(H+(dcap-sT)/fields_ph) if dcap>sT else int(dcap/fields_ph))
    return dict(now=H,per_helper=dict(events=round(ev_ph,2),scalar_units=round(sc_ph,1),moves=round(sum(c['paid'].values())/H,2)),max_helpers=out,binding=min(out,key=out.get),note='linear extrapolation at this word\'s own per-helper cost; delta cap uses 18 fields per helper')

def fmt(rep):
    L=['profile %s  kappa %s  TESTED %s  literals %s'%(rep['profile'],rep['kappa'],rep['tested'],{k:rep['lit'][k] for k in ('event_cap','scalar_cap','decay','v','c','b','u','reserve','power') if k in rep['lit']})]
    for x in rep['constraints']:
        f=lambda y:('%.6g'%y) if isinstance(y,float) else str(y)
        L.append('  %-4s %-30s %-9s value %-22s limit %-22s slack %-12s %s'%('ok' if x['ok'] else 'FAIL',x['name'],x['kind'],f(x['value']),f(x['limit']),f(x['slack']),x['note'][:70]))
    L.append('ADMISSIBLE' if rep['ok'] else 'NOT ADMISSIBLE: '+', '.join(x['name'] for x in rep['constraints'] if not x['ok']))
    return '\n'.join(L)

def main(argv=None):
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--profile'); ap.add_argument('--best',action='store_true'); ap.add_argument('--json',action='store_true')
    a=ap.parse_args(argv)
    c=counts(a.word,a.profile)
    if not a.best:
        r=check(a.word,profile=a.profile,_c=c); print(json.dumps(r,indent=1,default=str) if a.json else fmt(r)); return 0 if r['ok'] else 1
    b=best(a.word,a.profile,_c=c)
    if a.json: print(json.dumps(b,indent=1,default=str))
    else:
        print('AT ADOPTED LITERALS:'); print(fmt(b['at_profile'])); print('\nWITH BEST FREE LITERALS (admits_any=%s):'%b['admits_any']); print(fmt(b['report']))
        print('blockers:',b['blockers'] or 'none'); print('literal changes needed (new, adopted):',b['changes']); print('needs:',b['needs']); print('tail best:',b['tail_best']); print('strict-literal helper plan:',b['plan'])
    return 0 if b['admits_any'] else 1
if __name__=='__main__': sys.exit(main())
