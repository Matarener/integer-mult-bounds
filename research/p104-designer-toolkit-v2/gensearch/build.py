"""gensearch.build -- spec -> DAG -> word, and the evaluators.
  r0(dag)              L0  (dag only, no realise)  R0 helper-line law (GENLEARN-RULEBOOK R0): tax = D ln D - sum r ln r over helper itineraries (+ same for X/Y mains)
  fast(word, spec)     L1  (realise + compaction + one pass over the program, ~1 s): invoice from MOVE ranks, kappa_hat = exact kappa of that invoice, surrogate counts, admit.py slack
                           at the ADOPTED literals (events, scalar = local + 1000*routes, tail/theorem via admit.check on a counts dict).  NO legality / native-pair check.
  exact(word, profile) L2  (IncrWord: legality incl. native pairs, exact kappa) + admit.best (free literals)
Nothing here edits synth/: the spec knobs are applied by temporarily replacing module-level hooks (backgen.load_dilworth_steps / grouped_structure, frontgen.load_code, helpershare.DATA)
for the duration of one build, never writing the shared data/*.json caches.
"""
import sys,os,json,math,random,time,contextlib,collections
HERE=os.path.dirname(os.path.abspath(__file__)); TKD=os.path.dirname(HERE); sys.path.insert(0,TKD)
from tkcommon import *
import dag as D, incr, admit as A
from synth import sample as SM, frontgen as FG, backgen as BG, helpershare as HS, compact as CP
X=incr.X
ANCHOR='5756'; GS=W + '/ext/GENSEARCH'; HSDIR=GS+'/work/hs'
_dil={}; _spec_cache={}
def anchor_spec(): 
    if 'a' not in _spec_cache: _spec_cache['a']=SM.anchor_spec(ANCHOR,ANCHOR)
    return _spec_cache['a']
def _flip_code(mask):
    S4,C2=FG.load_code.__wrapped__() if hasattr(FG.load_code,'__wrapped__') else _orig_load_code()
    S4=[list(r) for r in S4]; C2=[list(r) for r in C2]
    for k in range(len(S4)):
        if mask>>k&1:
            S4[k]=[-v for v in S4[k]]
            for j in range(len(C2)): C2[j][k]=-C2[j][k]
    return S4,C2
_orig_load_code=FG.load_code
_orig_dil=BG.load_dilworth_steps; _orig_grp=BG.grouped_structure
def _my_tree(P,beta,noise,rng):
    m=len(P); pm=sum(1<<p for p in P); mask={j:BG._pmask(P[j]) for j in range(m)}; grp={j:frozenset([j]) for j in range(m)}; live=set(range(m)); merges=[]; nid=m
    while len(live)>1:
        best=None; L=sorted(live)
        for ai in range(len(L)):
            for bi in range(ai+1,len(L)):
                a,b=L[ai],L[bi]; fm=mask[a]&mask[b]; key=BG._mpop(fm&pm)-beta*(len(grp[a])+len(grp[b]))+(noise*rng.random() if noise else 0.0)
                if best is None or key>best[0]: best=(key,a,b,fm)
        _,a,b,fm=best; mask[nid]=fm; grp[nid]=grp[a]|grp[b]; merges.append((a,b)); live-={a,b}; live.add(nid); nid+=1
    return merges,mask
def _my_grouped(beta,noise,prune,seed):
    def gs(P,line,C2):
        rng=random.Random(seed); merges,mask=_my_tree(P,beta,noise,rng); m=len(P); mask=dict(mask)
        sel={n for n in range(m,m+len(merges)) if sum(1 for p in P if (mask[n]>>p)&1)>0}; cur=BG._tree_cost(P,line,C2,merges,mask,sel); imp=True
        while imp:
            imp=False; order=sorted(sel)
            if prune=='reverse': order.reverse()
            elif prune=='random': random.Random(seed+7).shuffle(order)
            for n in order:
                sel.discard(n); c=BG._tree_cost(P,line,C2,merges,mask,sel)
                if c<cur-1e-9: cur=c; imp=True
                else: sel.add(n)
        return merges,sel
    return gs
@contextlib.contextmanager
def patched(s):
    FG.load_code=(lambda: _flip_code(s['root_flip'])) if s['root_flip'] else _orig_load_code
    if s['back']=='dilworth':
        def dil(C2):
            key=(s['dil_seed'],s['dil_iters'])
            if key not in _dil: _dil[key]=[[tuple(g) for g in st] for st in BG.optimise_steps(C2,iters=s['dil_iters'],seed=s['dil_seed'])[1]]
            return _dil[key]
        BG.load_dilworth_steps=dil
    if s['back']=='grouped' and (s['grp_noise']>0 or s['grp_prune']!='sorted' or abs(s['grp_beta']-.005)>1e-9): BG.grouped_structure=_my_grouped(s['grp_beta'],s['grp_noise'],s['grp_prune'],s['grp_seed'])
    old_data=HS.DATA
    if s['helpers']=='shared' and s['back']!='grouped':
        os.makedirs(HSDIR,exist_ok=True); p=HSDIR+'/hs_%d_%d_%s.json'%(s['hs_seed'],s['hs_iters'],s['hs_T0'])
        if not os.path.exists(p):
            ports=anchor_spec()['family']['meta']['ports']; c,res=HS.solve(ports,iters=s['hs_iters'],seed=s['hs_seed'],T0=s['hs_T0'],out=None,verbose=False)
            json.dump(res,open(p+'.tmp','w')); os.replace(p+'.tmp',p)
        HS.DATA=p
    try: yield
    finally: FG.load_code=_orig_load_code; BG.load_dilworth_steps=_orig_dil; BG.grouped_structure=_orig_grp; HS.DATA=old_data
def build_dag(s):
    fs=dict(anchor_spec(),front='generated',back='generated:'+s['back'],helpers=s['helpers']); fs.pop('body',None)
    with patched(s): dag,info=FG.build_dag(fs)
    return dag,info
def realise(dag):
    w,rep=D.realise(dag,'lazy',(),verify=False); n=dag['meta']['npub']
    w['verifier_profile']=dict(public=n,owned_fields=dag['meta']['nowned'],lifetimes=sum(1 for o in dag['ops'] if o[0]=='INIT'),peak=1); return w
def compact(w,level):
    if level=='none': return w,{}
    return CP.compact(w,('cse',) if level=='cse' else ('adds','cse','scale'),verify=False,native=False)
def build_word(s):
    dag,info=build_dag(s)
    if not info['value_ok']: return None,info,dag
    w=realise(dag); w,st=compact(w,s['compact']); info['compact']=st; return w,info,dag
# ------------------------------------------------------------------ L0: R0 surrogate from the DAG itineraries
def _tax(ranks):
    ranks=[r for r in ranks if r>0]
    if not ranks: return 0.0
    Dd=sum(ranks); return Dd*math.log(Dd)-sum(r*math.log(r) for r in ranks)
def r0(dag):
    fr=dag['frames']; dim=[len(b) for b in fr]; regs=dag['regs']; n=dag['meta']['npub']; live=set(dag['meta']['live']); mains=live|{r+112 for r in live}
    it={}
    for r in range(n):
        v=regs[str(r)]; it[r]=[dim[v[1]]]
    for o in dag['ops']:
        if o[0] in('INIT','CLEAR'): continue
        for r in (o[1],o[2]):
            if r is not None and 0<=r<n:
                d=dim[o[4]]
                if it[r][-1]!=d: it[r].append(d)
    for r in range(n):
        d=dim[regs[str(r)][2]]
        if it[r][-1]!=d: it[r].append(d)
    th=tm=0.0; nh=0; stops=0
    for r,seq in it.items():
        rk=[abs(b-a) for a,b in zip(seq,seq[1:])]
        if r in mains: tm+=_tax(rk)
        else: th+=_tax(rk); nh+=1; stops+=len(rk)
    return dict(r0_help=round(th,2),r0_main=round(tm,2),r0=round(th+tm,2),n_help=nh,help_stops=stops)
# ------------------------------------------------------------------ L1: fast invoice + admit slack
def fast(w,profile=ANCHOR):
    fr=w['frames']; dim=[len(b) for b in fr]; n=len(w['initial']); live=list(w['live']); main=set(live)|{r+112 for r in live}
    paid=collections.Counter(); scalar=0; life=0; nev=len(w['program'])
    for e in w['program']:
        op=e[0]
        if op=='MOVE': paid[abs(dim[e[3]]-dim[e[2]])]+=1
        elif op in('INIT','CLEAR'): scalar+=2; life+=(op=='INIT')
        else:
            c=incr._coef(e[-2]); scalar+=c[7] if op=='SCALE' else c[8]
    hel=collections.Counter(dim[w['final'][r]]-dim[w['initial'][r]] for r in range(n) if r not in main)
    T,Pp=X.invoice(dict(paid=dict(sorted(paid.items())),helpers=dict(sorted(hel.items()))))
    kh=X.kappa(T,Pp) if min(hel)>0 else None
    c=dict(n=nev,scalar=scalar,paid=dict(paid),helpers=dict(hel),lifetimes=life,peak=1,public=n,owned=sum(1 for r in w['regs'] if False) if False else len(w.get('owned',[])) or 8,live=len(live),T=T,P=Pp,profile=profile,pp=None,legal=None)
    out=dict(kappa_hat=kh,events=nev,scalar=scalar,helpers=sum(hel.values()),moves=sum(paid.values()),min_credit=min(hel) if hel else None)
    try:
        lit=A.lits_of(profile); out['ev_slack']=lit['event_cap']-nev; routes=A.routes_units(c); out['scalar_slack']=lit['scalar_cap']-(scalar+routes*1000)
        out['strict_events_ok']=out['ev_slack']>0; out['strict_scalar_ok']=out['scalar_slack']>0
        c['pp']=w.get('verifier_profile'); lit2=dict(lit); lit2['pins']=dict(public=n,owned_fields=8,lifetimes=life,peak=1,public_range=(n,n),owned_range=(8,8)); c['owned']=8
        rep=A.check(None,lit2,_c=c); bad=[x['name'] for x in rep['constraints'] if not x['ok']]
        out['admit_bad']=bad; out['admit_strict']=not bad
    except Exception as ex: out['admit_err']=repr(ex)[:120]
    return out
# ------------------------------------------------------------------ L2: exact
def exact(w,profile=ANCHOR):
    t=time.time(); iw=incr.IncrWord(w,profile=profile); row=dict(legal=bool(iw.legal_all),kappa=iw.kappa if iw.legal_all else None,kappa_illegal=None if iw.legal_all else iw.kappa,n_viol=len(iw.viol),bad_pairs=len(iw.bad_pairs),secs_incr=round(time.time()-t,1))
    if not iw.legal_all: row['viol']=[str(v)[:100] for v in iw.viol[:3]]
    try:
        t=time.time(); b=A.best(iw); row['admit_strict']=bool(b['strict_ok']); row['admit_any']=bool(b['admits_any']); row['admit_changes']=sorted(b['changes']); row['admit_blockers']=[x[:100] for x in b['blockers']]; row['secs_admit']=round(time.time()-t,1)
        row['scalar_exact']=sum(c.scalar for c in iw.chs)
    except Exception as ex: row['admit_err']=repr(ex)[:150]
    return row,iw
