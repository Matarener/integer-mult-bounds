"""shipcheck -- ADMITGEN: is a (generated) word SHIPPABLE as a package, which literals must change, and do those changes have precedent?
usage: tk shipcheck WORD [--base 5827] [--json] [--real] [--wait]

Verdicts
  SHIPPABLE AS-IS            admitted at the base package literals (only the per-word inventory pins are rewritten, which every PR does)
  SHIPPABLE, PRECEDENTED     needs only literal changes whose KIND and VALUE an adopted PR already used
  NEEDS NEW-VALUE LITERALS   admissible, but a literal moves to a value no PR used (kind has precedent)
  NEEDS BEYOND-PRECEDENT     admissible only with a literal no adopted PR ever changed (event cap, scalar cap, v, theta ...)
  NOT SHIPPABLE              a REAL blocker (no literal choice admits it)
The literal chooser keeps v=1024, power=1024, theta=63/64, reserve=1/10^12 and D=125/128 whenever the tail allows it, moves (c,b,u) only as far as needed
(closest b to the precedent 17), and sets the two caps to the least value the word needs (reported together with a rounded proposal).
`--real` builds a DERIVED stack (the base profile's local.py / pricing.py with ONLY those literals edited, the three PR-specific negative controls dropped)
and runs the PR's own replay / native / price.run on it (hq job unless --wait)."""
import sys,os,json,glob,re,math,hashlib,shutil,decimal
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fractions import Fraction as Q
import admit as A
D=decimal.Decimal
PROFDIR=HERE+'/profiles'
LITKEYS=('event_cap','scalar_cap','decay','power','v','theta','reserve','c','b','u')

# ------------------------------------------------------------------------------------------ precedent (derived from the adopted profiles + external notes)
def history():
    """-> {literal: [(value, first_pr, [all prs])]} over toolkit/profiles/<pr>.json (adopted PR packages, chronological by PR number)"""
    rows=[]
    for f in sorted(glob.glob(PROFDIR+'/*.json')):
        nm=os.path.basename(f)[:-5]
        if not re.match(r'^\d+$',nm): continue
        d=json.load(open(f)); c=d.get('compiler') or {}
        if not c.get('decay'): continue
        t=c.get('tail') or dict(u='1/5',v=1024,c=17,b=18)
        rows.append((int(nm),dict(event_cap=c.get('event_cap') or 26000,scalar_cap=c.get('scalar_cap') or 10**7,decay=c['decay'],power=c['power'],v=t['v'],theta=c['theta'],reserve=c['reserve'],
                    tail='c=%d,b=%d,u=%s'%(t['c'],t['b'],t['u']),public=d['public'],owned=d['owned_fields'],lifetimes=d['lifetimes'],peak=d['peak'])))
    H={}
    for pr,r in rows:
        for k,v in r.items():
            L=H.setdefault(k,[])
            for e in L:
                if e[0]==v: e[2].append(pr); break
            else: L.append((v,pr,[pr]))
    return H
# external (not in profiles): pending swarm PRs that touch the same literals.  Marked UNADOPTED: no maintainer acceptance known.
EXTERNAL={'event_cap':'PR5830 (pending, Ali Romman): 26351-instruction word; adds a declared operation-bound parameter to local.py (strict bound 27504), all other source checks byte-identical; hosted CI red on an unrelated suite, NOT adopted/merged'}
INV_NOTE='inventory pins (public/owned/lifetimes/peak) were widened by #5599 (735->750), #5612 (lifetimes 8->11, peak 1->2), #5644 (owned 9), #5751 (767), #5774 (owned 22, lifetimes 24, peak 12), #5786 (770, owned 25), #5802/#5811 (owned 28/29); user-cited #5627 not adopted here'

def fq(x): return str(Q(x))

# ------------------------------------------------------------------------------------------ literal chooser
def base_lits(base='5827'):
    L=A.lits_of(base); return L
def tail_candidates(c,tested,L0,vfix=1024):
    """all (b,c,u) with b<=17 and gamma/delta at TESTED; -> sorted list closest to the precedent"""
    T,P=c['T'],c['P']; td=A.qd(tested); t=1-td; mt=A.moment(T,t); sT=sum(T.values()); out=[]
    ugrid=sorted({Q(i,64) for i in range(1,129) if Q(i,64)>=tested}|{Q(1,7),Q(1,5),Q(1,4),Q(1,8),Q(1,6)})
    for bb in range(A.MAXRANK-1,2,-1):
        cc=bb-1
        while cc>1 and cc**64>=bb**63: cc-=1
        if cc<2: continue
        delta=D(bb)*sT/(A.pw(cc,td)*mt)
        if delta>=D('0.9786'): continue
        best=None
        for uu in ugrid:
            if uu<tested: continue
            g=A.moment(P,t+A.qd(uu))/(A.pw(cc,A.qd(uu))*mt)
            if best is None or g<best[0]: best=(g,uu)
        out.append(dict(b=bb,c=cc,u=best[1],gamma=best[0],delta=delta,m=max(best[0],delta)))
    return out
def choose(src,base='5827',c=None):
    """-> dict(lit, changes, report, blockers, tier)"""
    c=c or A.counts(src); L0=base_lits(base)
    pins=dict(public=c['public'],owned_fields=c['owned'],lifetimes=c['lifetimes'],peak=c['peak'],public_range=(c['public'],c['public']),owned_range=(c['owned'],c['owned']))
    L0=dict(L0); L0['pins']=pins
    rep0=A.check(src,L0,_c=c)
    if rep0['ok']: return dict(lit=L0,report=rep0,blockers=[],at_base=rep0,tier='base')
    kd=A.kappa_crossing(c); tested=A.dq(kd-D('1e-10')); claim=tested-Q(7,10**12)
    L=dict(L0); L['event_cap']=max(L0['event_cap'],c['n']+1)
    used=c['scalar']+A.routes_units(c)*1000; L['scalar_cap']=max(L0['scalar_cap'],used+1)
    blockers=[]
    smax=(A.RAW_BUDGET-A.PHYS_RAW_CONST)//18
    if L['scalar_cap']>smax: blockers.append('scalar cap %d above raw ceiling %d'%(L['scalar_cap'],smax))
    # tail at base literals first
    rep1=A.check(src,L,tested=tested,claim=claim,_c=c)
    tailnames=('gamma<D','delta<D','theorem tail <1','field cap (sum T)','D^(v/8)<1/16','alpha<1-eps','normalized paid <1')
    if all(x['ok'] for x in rep1['constraints'] if x['name'] in tailnames):
        rep=rep1
    else:
        cands=sorted(tail_candidates(c,tested,L0),key=lambda r:(-r['b'],-r['c']))
        rep=None
        Dprec=Q(125,128)
        for r in cands:
            if r['m']<A.qd(Dprec)*D('0.9999'): Dd=Dprec
            else: Dd=Q(math.ceil(float(r['m'])*128+1e-9),128) if r['m']<D('0.97') else A.dq(r['m']*D('1.0000001'),10**6)
            if A.qd(Dd)**128>=D(1)/16: continue
            L2=dict(L); L2.update(c=r['c'],b=r['b'],u=r['u'],decay=Dd)
            rp=A.check(src,L2,tested=tested,claim=claim,_c=c)
            if rp['ok']: L,rep=L2,rp; break
        if rep is None:
            # fall back to the free-v chooser of admit.best
            b=A.best(src,_c=c); L=dict(b['lit']); L['pins']=pins
            for k in ('decay','u','reserve'): L[k]=Q(L[k]) if isinstance(L[k],str) else L[k]
            rep=A.check(src,L,tested=tested,claim=claim,_c=c); blockers+=b['blockers']
            if not rep['ok'] and not blockers: blockers.append('no literal choice found')
    return dict(lit=L,report=rep,blockers=blockers,at_base=rep0,tier='changed',tested=str(tested))

def classify(L,L0,c,H):
    """per changed literal: (literal, new, base, class, citation).  class in PRECEDENT / NEW-VALUE / BEYOND"""
    rows=[]
    def vals(k): return [e for e in H.get(k,[])]
    def row(name,new,old,cls,cite): rows.append(dict(literal=name,new=new,base=old,cls=cls,cite=cite))
    for k in ('event_cap','scalar_cap','v','theta','power'):
        if str(L[k])!=str(L0[k]):
            seen=[e for e in H.get(k,[]) if str(e[0])==str(L[k])]
            if seen: row(k,str(L[k]),str(L0[k]),'PRECEDENT','adopted value, first #%d'%seen[0][1])
            elif len(H.get(k,[]))>1: row(k,str(L[k]),str(L0[k]),'NEW-VALUE','kind changed before: %s'%[(e[0],e[1]) for e in H[k]])
            else: row(k,str(L[k]),str(L0[k]),'BEYOND','never changed in any adopted PR (constant %s in all %d profiles)'%(H[k][0][0],len(H[k][0][2]))+('; '+EXTERNAL[k] if k in EXTERNAL else ''))
    tl='c=%d,b=%d,u=%s'%(L['c'],L['b'],L['u']); tl0='c=%d,b=%d,u=%s'%(L0['c'],L0['b'],L0['u'])
    dec=str(L['decay']); dec0=str(L0['decay'])
    if tl!=tl0 or dec!=dec0:
        seen=[e for e in H.get('tail',[]) if e[0]==tl]; sd=[e for e in H.get('decay',[]) if e[0]==dec]
        if seen and sd: row('tail (c,b,u) + decay',tl+' D='+dec,tl0+' D='+dec0,'PRECEDENT','tail first #%d, decay first #%d'%(seen[0][1],sd[0][1]))
        else: row('tail (c,b,u) + decay',tl+' D='+dec,tl0+' D='+dec0,'NEW-VALUE','kind changed by #%s (tail 17/18,1/5 -> 16/17,1/7 and decay .97 -> 39/40 -> 125/128 incl. power 1000->1024 at #5599); this (c,b,u) not used before'%(','.join(str(e[1]) for e in H['tail'][1:]) or '?'))
    if str(L['reserve'])!=str(L0['reserve']):
        row('reserve',str(L['reserve']),str(L0['reserve']),'NEW-VALUE' if len(H['reserve'])>1 else 'BEYOND','reserve 1e-10 -> 1e-12 at #5644')
    p=L['pins']; ch=[]
    if p['public']>770: ch.append('public %d (adopted max 770, #5786/#5802..#5827)'%p['public'])
    if p['owned_fields']>29: ch.append('owned_fields %d (max 29)'%p['owned_fields'])
    if p['lifetimes']>31: ch.append('lifetimes %d (max 31)'%p['lifetimes'])
    if p['peak']>13: ch.append('peak %d (max 13)'%p['peak'])
    if ch: row('inventory pins',', '.join(ch),'767..770/8..29/31/13','NEW-VALUE','kind: '+INV_NOTE)
    else: row('inventory pins','public %d owned %d life %d peak %d'%(p['public'],p['owned_fields'],p['lifetimes'],p['peak']),'(per word)','PRECEDENT','kind: '+INV_NOTE) if (p['public'],p['owned_fields'],p['lifetimes'],p['peak'])!=(770,29,31,13) else None
    return rows

def verdict(rows,blockers,ok_strict):
    if blockers: return 'NOT SHIPPABLE'
    if ok_strict: return 'SHIPPABLE AS-IS'
    cl={r['cls'] for r in rows}
    if 'BEYOND' in cl: return 'NEEDS BEYOND-PRECEDENT LITERALS'
    if 'NEW-VALUE' in cl: return 'NEEDS NEW-VALUE LITERALS (kind has precedent)'
    return 'SHIPPABLE, PRECEDENTED'

def analyse(src,base='5827'):
    c=A.counts(src); H=history(); L0=base_lits(base)
    ch=choose(src,base,c); L=ch['lit']
    rows=classify(L,dict(L0,pins=None),c,H) if ch['tier']!='base' else []
    # at-base failures
    fails=[x['name'] for x in ch['at_base']['constraints'] if not x['ok']]
    v=verdict(rows,ch['blockers'],ch['tier']=='base' or (ch['at_base']['ok']))
    # constraint slack at the chosen literals
    sl=[(x['name'],x['kind'],x['value'],x['limit'],x['slack']) for x in ch['report']['constraints']]
    need=dict(events=c['n'],scalar=c['scalar']+A.routes_units(c)*1000,public=c['public'],helpers=sum(c['helpers'].values()),moves=sum(c['paid'].values()),sumT=sum(c['T'].values()))
    rounded=dict(event_cap=int(math.ceil((c['n']+1)/1000.0)*1000),scalar_cap=int(math.ceil((need['scalar']+1)/10**6.0)*10**6))
    # digit screen
    dg=digit_screen(src,c)
    return dict(owned=c['owned'],peak=c['peak'],verdict=v,kappa=ch['at_base']['kappa'],base=base,counts=need,fails_at_base=fails,literals=({k:(str(L[k]) if k in L else None) for k in LITKEYS}),rows=rows,blockers=ch['blockers'],
                admissible_after=ch['report']['ok'],rounded_caps=rounded,digits=dg,constraints=sl,raw_ceiling=(A.RAW_BUDGET-A.PHYS_RAW_CONST)//18)

def digit_screen(src,c=None):
    """Python 4300-digit int<->str limit: where can a word reach it?  Exact quantities that get str()-ed or json-ed in the PR pipelines are small for P104-family words
    (dyadic coefficients, integer census); the large integers (c^v)^64, 145^(vT), (step j+1)^power are only compared.  Returns the numbers."""
    w=src if isinstance(src,dict) else None
    if w is None:
        try: _,w=A.load(src) if isinstance(src,str) else (None,None)
        except Exception: w=None
    out=dict()
    if w:
        mx=0;bits=0.0
        for e in w['program']:
            for x in e[1:]:
                if isinstance(x,str) and ('/' in x or x.lstrip('-').isdigit()) and e[0] in('ADD','SCALE'):
                    try:
                        f=Q(x); mx=max(mx,len(str(f.numerator)),len(str(f.denominator))); bits+=math.log2(1+abs(float(f)))
                    except Exception: pass
        out.update(max_coef_digits=mx,sum_log2_growth_bits=round(bits),growth_digits_if_materialised=round(bits*0.30103),note='informational only: the accepted #5827-based K2SEARCH candidate shows ~5.8k and passes the real stack (nothing str()s these); the P104 local/pricing stack never hit the 4300 limit on generated words (tk shipcheck --real); the limit bit only the BIT global_retirement majorant str (K2BIT reroute walks)')
    return out

def fmt(r):
    L=['SHIPCHECK  verdict: %s'%r['verdict'],'  kappa %s  base package profile %s'%(r['kappa'],r['base']),'  counts: '+', '.join('%s %s'%kv for kv in r['counts'].items()),
       '  fails at the base literals: %s'%(', '.join(r['fails_at_base']) or 'none')]
    if r['rows']:
        L.append('  literal changes (class, citation):')
        for x in r['rows']: L.append('    %-22s %-34s <- %-26s [%s] %s'%(x['literal'],x['new'],x['base'],x['cls'],x['cite'][:230]))
    L.append('  rounded cap proposal: events < %d, scalar < %d (raw ceiling %d)'%(r['rounded_caps']['event_cap'],r['rounded_caps']['scalar_cap'],r['raw_ceiling']))
    L.append('  admissible after those changes: %s%s'%(r['admissible_after'],('; blockers: '+'; '.join(r['blockers'])) if r['blockers'] else ''))
    L.append('  int-str (4300 digit) screen: %s'%r['digits'])
    L.append('  slack at the chosen literals:')
    for n,k,v,l,s in r['constraints']: L.append('    %-34s %-9s value %-14s limit %-14s slack %s'%(n,k,('%.5g'%v) if isinstance(v,float) else str(v)[:14],('%.5g'%l) if isinstance(l,float) else str(l)[:14],('%.4g'%s) if isinstance(s,float) else str(s)[:14]))
    return '\n'.join(L)

def main(a):
    word=a.word; r=analyse(word,getattr(a,'base','5827') or '5827')
    if getattr(a,'json',False): print(json.dumps(r,indent=1,default=str))
    else: print(fmt(r))
    if getattr(a,'real',False):
        import shipreal; return shipreal.launch(word,r,wait=getattr(a,'wait',False))
    return 0 if r['verdict'].startswith('SHIPPABLE') else 1
def add_parsers(sp):
    p=sp.add_parser('shipcheck',help='is a generated word shippable as a package? literals to change + precedent'); p.add_argument('word'); p.add_argument('--base',default='5827'); p.add_argument('--json',action='store_true'); p.add_argument('--real',action='store_true',help='run the PR\'s own stack on a derived literal-patched copy (hq job)'); p.add_argument('--wait',action='store_true')
if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--base',default='5827'); ap.add_argument('--json',action='store_true'); ap.add_argument('--real',action='store_true'); ap.add_argument('--wait',action='store_true')
    sys.exit(main(ap.parse_args()))
