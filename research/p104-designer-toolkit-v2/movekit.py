"""movekit -- the move-class plugin framework of the designer toolkit (TKMOVES lane).

A MOVE CLASS is one family of word edits (A2 exchange, paid interior bases, block reframe, two-boundary split, ...).  A plugin implements
    sites(view, ctx)     -> iterable of EDITS (JSON-able dicts, each a complete concrete edit: sites already expanded to their free parameters)
    scalars(view, edit)  -> new scalar program S2 (list of non-MOVE events)       [scalar-only classes: MOVEs are re-derived by View.rebuild]
 or apply(view, edit)    -> new WORD (dict)                                       [classes that also change frames / endpoints / registers]
and optionally prepare(view) -> ctx (indexes shared by sites()).  Everything else is shared here:
    View            word + scalar program + blocks + frame spans; rebuild(S2) re-derives the MOVEs (just-in-time, paid multiset reproduced)
    evaluate(w)     the EXACT check and price: tk legality oracle + exact invoice + side constraints + budgets  (kappa float, Decimal-50 interval on request)
    quick(view,S2)  exact paid/helper census from register trajectories only (nesting + ownership direction, no endpoint-value replay): ~10x cheaper than evaluate.
                    Ranking only -- every adopted word is re-checked with evaluate().
    screen / greedy / fixed_point   drivers;   cli(plugin, args) = `tk <class> WORD [--apply] ...`;   register_screens() puts every class in `tk eval --screens`.
Verifier pin: legal.profile_params pins public==743 for the PR5627-line owned_fields words; words with another public count (the #5718 word has 744) get
`verifier_profile` injected IN MEMORY (pin()) and stamped on emitted words, so no profiles/*.json is touched (a package verify.py must retarget its pin, like PR5606->PR5612)."""
import sys,os,json,gzip,copy,time,collections,decimal,importlib
from fractions import Fraction as Q
from tkcommon import *

CLASSES=['ibase','a2x','blockmove','split2','relay']      # module names; each defines PLUGIN
def plugin(name): return importlib.import_module(name).PLUGIN

def pin(w):
    """word with the verifier pins (public, owned_fields, lifetimes, peak) of the profile, public retargeted to len(initial); same object if nothing to change"""
    if not legal.has_of(w): return w
    pp=legal.profile_params(w); n=len(w['initial'])
    if pp.get('public')==n and 'verifier_profile' not in w: return w
    w2=dict(w); w2['verifier_profile']=dict(pp,public=n,owned_fields=legal.nown(w)); return w2
def qs(x):
    x=Q(x); return str(x.numerator) if x.denominator==1 else '%d/%d'%(x.numerator,x.denominator)

class View:
    """a word seen as (scalar program S, blocks, spans).  S = non-MOVE events in order; a BLOCK is a maximal run of scalar events on one frame (INIT/CLEAR are singleton blocks)."""
    def __init__(s,w):
        if legal.is_prepared(w): raise SystemExit('movekit: prepared573 words are not supported')
        s.w=w; s.n=len(w['initial']); s.own=legal.owned_set(w); s.NR=s.n+legal.nown(w)
        s.S=[e for e in w['program'] if e[0]!='MOVE']; s._bl=None; s._sp=None
    @property
    def spans(s):
        if s._sp is None: s._sp=legal.spans(s.w)
        return s._sp
    @property
    def dim(s): return [len(b) for b in s.w['frames']]
    @property
    def blocks(s):
        if s._bl is None: s._bl=blocks_of(s.S)
        return s._bl
    def frame_of(s,span):
        """frame id whose span equals the set `span` (frozenset of ints), or None"""
        if not hasattr(s,'_idx'): s._idx={sp:i for i,sp in enumerate(s.spans)}
        return s._idx.get(frozenset(span))
    def rebuild(s,S2,frames=None,initial=None,final=None,extra=None):
        """as rebuild_ref; FASTSITES: from the second call on a View (and while the base program is the canonical rebuild of its S) the program is built INCREMENTALLY from the base program
        (dq.rebuild_splice: only the window and the groups it perturbs are re-derived) -- identical output, tests/rebuild_diff.py"""
        if RB and frames is None and initial is None and final is None and not extra:
            tj=s.__dict__.get('_tj',0)
            if type(tj) is int and tj<RB_AFTER: s._tj=tj+1
            elif tj is not False:
                try:
                    if type(tj) is int:
                        import dq as DQM
                        tj=s._tj=DQM.Traj(s)
                        if not tj.canon: s._tj=False; tj=False
                    if tj is not False:
                        import dq as DQM
                        S=s.S; n=min(len(S),len(S2)); p=DQM._lcp(S,S2,n); q=DQM._lcs(S,S2,n-p)
                        prog=DQM.rebuild_splice(s,tj,p,len(S)-q,S2[p:len(S2)-q])
                        res=dict(s.w); res['program']=prog; STATS['rebuild_inc']+=1; return res
                except ValueError: raise
                except Exception: STATS['rebuild_err']+=1
        return s.rebuild_ref(S2,frames,initial,final,extra)
    def rebuild_edit(s,se):
        """word of an explicit window edit (sedit.SEdit): incremental splice from the canonical base trajectory (no S2, no lcp/lcs), else the full JIT rebuild"""
        if RB and se.ini is None and se.fin is None:
            try:
                import dq as DQM
                tj=DQM.traj_of(s)
                if tj is not None:
                    prog=DQM.rebuild_splice(s,tj,se.p,se.hi,se.new)
                    res=dict(s.w); res['program']=prog; STATS['rebuild_edit']+=1; return res
            except ValueError: raise
            except Exception: STATS['rebuild_err']+=1
        return s.rebuild_ref(se.materialise(s.S),initial=se.ini,final=se.fin)
    def rebuild_ref(s,S2,frames=None,initial=None,final=None,extra=None):
        """word with scalar program S2 and just-in-time MOVEs (a register moves to the frame of its next event; public registers end at `final`; owned move before CLEAR)"""
        w=s.w; n=s.n; own=s.own
        ini=initial if initial is not None else w['initial']; fin=final if final is not None else w['final']
        cur=list(ini)+[None]*(s.NR-len(ini)); prog=[]
        def move(r,f):
            if cur[r]!=f:
                if cur[r] is None: raise ValueError('dead register %d'%r)
                prog.append(['MOVE',r,cur[r],f,r in own]); cur[r]=f
        app=prog.append
        for e in S2:        # (hot loop of every plugin apply: the checks are inlined, move() is only called for the actual MOVEs)
            op=e[0]; r=e[1]
            if op=='INIT': cur[r]=e[2]
            elif op=='CLEAR': move(r,e[2]); cur[r]=None
            else:
                f=e[-1]
                if cur[r]!=f: move(r,f)
                if op=='ADD' or op=='COPY':
                    t=e[2]
                    if cur[t]!=f: move(t,f)
            app(e if type(e) is list else list(e))
        for r in range(len(ini)):
            if r not in own: move(r,fin[r])
        res=dict(w); res['program']=prog
        if frames is not None: res['frames']=frames
        if initial is not None: res['initial']=ini
        if final is not None: res['final']=fin
        if extra: res.update(extra)
        return res
def blocks_of(S):
    bl=[];cur=[];fr=None
    for i,e in enumerate(S):
        if e[0] in('INIT','CLEAR'):
            if cur: bl.append(cur)
            bl.append([i]);cur=[];fr=None
        elif fr!=e[-1]:
            if cur: bl.append(cur)
            cur=[i];fr=e[-1]
        else: cur.append(i)
    if cur: bl.append(cur)
    return bl

# ---- shared exact check + price
def evaluate(w):
    """EXACT: legality (all rules incl. endpoint rows), invoice, kappa (float root 1e-15), side constraints with the word's profile decay/reserve, budgets.
    -> dict(ok [= legal and side and budgets], legal, kappa, side_ok, ev_slack, sc_slack, paid_calls, fields, why)"""
    w=pin(w); rep=legal.check(w,maxviol=3)
    if not rep['ok']: return dict(ok=False,legal=False,why=[(i,r,str(d)[:90]) for i,r,d in rep['violations'][:2]])
    T,P=X.invoice(rep); pr=profile_of(w)[1]
    sd=side_of(T,P,pr); b=X.budgets(rep)
    o=dict(ok=bool(sd['ok'] and b['event_slack']>=0 and b['scalar_budget_slack']>=0),legal=True,kappa=X.kappa(T,P),side_ok=sd['ok'],ev_slack=b['event_slack'],sc_slack=b['scalar_budget_slack'],
           paid_calls=sum(P.values()),fields=sum(T.values()),paid=rep['paid'],helpers=rep['helpers'])
    return o
def interval(w):
    """Decimal-50 root and the 1e-14 crossing interval (strings)"""
    rep=legal.check(pin(w)); T,P=X.invoice(rep); D=decimal.Decimal; kd=X.kappa_dec(T,P,50)
    lo=(kd*10**14).to_integral_value(rounding=decimal.ROUND_FLOOR)/D(10**14)
    return dict(kappa=str(kd)[:22],lo=format(lo,'.14f'),hi=format(lo+D(1)/D(10**14),'.14f'))
def _kappa(hel,paid,_c={}):
    """kappa of (helpers, paid) through the invoice, built in CANONICAL (sorted) key order so every route (full / delta quick) gives the same float; memoised"""
    key=(tuple(sorted(hel.items())),tuple(sorted(paid.items())))
    k=_c.get(key)
    if k is None:
        T,P=X.invoice(dict(helpers=dict(key[0]),paid=dict(key[1]))); k=X.kappa(T,P)
        if len(_c)>200000: _c.clear()
        _c[key]=k
    return k
STATS=collections.Counter()
DQ_AFTER=4; RB_AFTER=4          # calls on one View before its delta cache / trajectory table is built
RB=os.environ.get('TK_RB','1')!='0'          # incremental rebuild on/off
EDITS=os.environ.get('TK_EDITS','1')!='0'      # REALISEFIX: edit-emitting plugin path (sedit.py) on/off
DQ=os.environ.get('TK_DQ','1')!='0'        # delta quick (dq.py) on/off; quick_full is the reference
def quick(view,S2,initial=None,final=None,frames=None):
    """paid multiset + helper census from trajectories of the rebuilt word (no value replay).  -> (kappa or None if a MOVE is not strictly nested / illegal, paid Counter)
    helpers are read from the base word's endpoints unless initial/final given.  Incremental (dq.DQBase, exact == quick_full) when the frames are unchanged; the first call on a View is full."""
    se=None
    if type(S2) is not list and hasattr(S2,'materialise'):          # REALISEFIX: an explicit window edit (sedit.SEdit) instead of the full candidate program
        se=S2
        if frames is None and (initial is None and final is None):
            initial=se.ini; final=se.fin
        S2=None
    if DQ and frames is None:
        st=view.__dict__.get('_dq',0)
        if type(st) is int and st<DQ_AFTER: view._dq=st+1; st=-1          # the cache costs ~4 full quicks to build: only views priced more than that often get it
        elif st is not False:
            try:
                if type(st) is int:
                    import dq as DQM
                    st=view._dq=DQM.DQBase(view,view.spans,[len(b) for b in view.w['frames']])
                w=view.w
                if st.S is view.S and st.ini is w['initial'] and st.fin is w['final']:
                    if se is not None: r=st.delta_edit(se) if (initial is None and final is None) else st.delta(se.materialise(view.S),initial or w['initial'],final or w['final'])
                    else: r=st.delta(S2,initial or w['initial'],final or w['final'])
                    if r is None: return None,collections.Counter()
                    STATS['delta']+=1; return _kappa(*r),r[1]
            except NotImplementedError: STATS['fallback']+=1
            except Exception:
                STATS['error']+=1
                if type(st) is int: view._dq=False
    if se is not None: S2=se.materialise(view.S)
    return quick_full(view,S2,initial,final,frames)
def quick_score(view,S2,initial=None,final=None):
    """FIRST-ORDER screen (FASTSITES): estimated dkappa of the candidate from the invoice-total delta (dkappa/dT, dkappa/dP at the base root), without solving for kappa.
    -> float, or None when the candidate is illegal or the delta route does not apply (callers then price it exactly with quick())."""
    st=view.__dict__.get('_dq',0)
    if not DQ or st is False or (type(st) is int and st<DQ_AFTER): return None
    try:
        if type(st) is int:
            import dq as DQM
            st=view._dq=DQM.DQBase(view,view.spans,[len(b) for b in view.w['frames']])
        w=view.w
        if st.S is not view.S or st.ini is not w['initial'] or st.fin is not w['final']: return None
        if type(S2) is not list and hasattr(S2,'materialise'):
            se=S2; r=st.delta_edit(se) if (initial is None and final is None) else st.delta(se.materialise(view.S),initial or w['initial'],final or w['final'])
        else: r=st.delta(S2,initial or w['initial'],final or w['final'])
        if r is None: return float('-inf')          # illegal under the trajectory census
        return st.first_order(r[0],r[1])
    except NotImplementedError: return None
    except Exception: return None
def quick_full(view,S2,initial=None,final=None,frames=None):
    """REFERENCE quick: the full walk of S2 (see quick)."""
    w=view.w; fr=view.spans if frames is None else [frozenset(_span(b)) for b in frames]; fb=w['frames'] if frames is None else frames; dim=[len(b) for b in fb]
    ini=initial or w['initial']; fin=final or w['final']; own=view.own; cur=list(ini)+[None]*(view.NR-len(ini)); paid=collections.Counter()
    def move(r,f):
        a=cur[r]
        if a!=f:
            if a is None: return False
            if (fr[f]<fr[a]) if r in own else (fr[a]<fr[f]): paid[abs(dim[f]-dim[a])]+=1; cur[r]=f; return True
            return False
        return True
    for e in S2:
        op,r=e[:2]
        if op=='INIT': cur[r]=e[2]
        elif op=='CLEAR':
            if not move(r,e[2]): return None,paid
            cur[r]=None
        else:
            if not move(r,e[-1]): return None,paid
            if op in('ADD','COPY') and not move(e[2],e[-1]): return None,paid
    for r in range(len(ini)):
        if r not in own and not move(r,fin[r]): return None,paid
    hel=helpers_of(w,fr,dim,ini,fin)
    return _kappa(hel,paid),paid
def _span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
def helpers_of(w,fr,dim,ini,fin):
    main=set(w['live'])|{r+112 for r in w['live']}; ret=set(legal.retired_of(w))
    return dict(collections.Counter(dim[fin[r]]-dim[ini[r]] for r in range(len(ini)) if r not in main and r not in ret))

# ---- plugin base + drivers
class Plugin:
    name='?'; doc=''
    def prepare(self,view): return None
    def sites(self,view,ctx): raise NotImplementedError
    def scalars(self,view,edit): raise NotImplementedError          # scalar-only classes
    def apply(self,view,edit): return view.rebuild(self.scalars(view,edit))
    # REALISEFIX: edit-emitting path.  sedit() returns a sedit.SEdit (explicit window, consumable by dq / quick / rebuild_edit / IncrWord.try_edit); plugins that do not implement it get the
    # generic recovery from scalars() (correct, no faster).  edits() yields (site, SEdit) pairs; sites whose edit is illegal/blocked are skipped.
    def sedit(self,view,edit):
        import sedit as SE
        return SE.from_lists(view.S,self.scalars(view,edit),meta=edit,view=view)
    def edits(self,view,ctx,**kw):
        for ed in self.sites(view,ctx,**kw):
            try: se=self.sedit(view,ed)
            except (ValueError,KeyError,IndexError,AssertionError): continue
            se.meta=ed; se.view=view; yield ed,se
    quick=True       # True: scalar-only class, screen with quick(); False: always evaluate()
    site_fields=()          # edit fields that identify a SITE (the rest are free parameters of the site); used to re-price only previously improving sites
    def site_key(self,edit): return tuple(str(edit.get(f)) for f in self.site_fields) if self.site_fields else None
REG={}
def screen(pl,w,max_sites=None,shard=(0,1),log=print,positive_only=True,exact_top=8,results=None,base_k=None,keys=None):
    """price every edit of the class: -> list of dict(edit, gain, kappa) sorted by gain; the best `exact_top` positive ones are confirmed by evaluate()"""
    w=pin(w); v=View(w); k0=base_k if base_k is not None else evaluate(w)['kappa']; ctx=pl.prepare(v); out=[]; n=0; t0=time.time()
    for i,ed in enumerate(pl.sites(v,ctx)):
        if keys is not None and pl.site_key(ed) not in keys: continue
        if i%shard[1]!=shard[0]: continue
        if max_sites and n>=max_sites: break
        n+=1
        try:
            if pl.quick:
                k,_=quick(v,pl.sedit(v,ed) if EDITS else pl.scalars(v,ed))
            else:
                o=evaluate(pl.apply(v,ed)); k=o['kappa'] if o.get('ok') else None
        except (ValueError,KeyError,AssertionError,IndexError) as ex: k=None
        rec=dict(edit=ed,kappa=k,gain=None if k is None else k-k0)
        if results: results.write(json.dumps(rec,default=str)+'\n'); results.flush()
        if k is not None and (k>k0+1e-15 or not positive_only): out.append(rec)
    out.sort(key=lambda r:-r['gain']); log('  %s: %d edits priced in %.0fs, %d improving'%(pl.name,n,time.time()-t0,len(out)))
    for r in out[:exact_top]:
        try:
            w2=pl.apply(v,r['edit']); o=evaluate(w2); r['exact']=o.get('kappa') if o.get('ok') else None; r['word']=w2 if o.get('ok') else None
        except Exception as ex: r['exact']=None; r['word']=None; r['err']=repr(ex)[:80]
    out=[r for r in out if r.get('exact') is not None or 'word' not in r] ; return out,k0
def greedy(pl,w,steps=1,log=print,**kw):
    """apply the best exact-confirmed improving edit, rescan, repeat.  -> (word, applied list)"""
    cur=pin(w); applied=[]; keys=None; kw.pop('base_k',None)
    for st in range(steps):
        out,k0=screen(pl,cur,log=log,keys=keys,**kw)
        best=[r for r in out if r.get('word') is not None and r['exact']>k0+1e-15]
        if not best:
            if keys is None or not pl.site_fields: break
            keys=None; continue          # restricted rescan (previously improving sites) found nothing: one full rescan decides
        if pl.site_fields: keys={pl.site_key(r['edit']) for r in out if r['gain']>0}
        b=max(best,key=lambda r:r['exact']); cur=b['word']; applied.append(dict(edit=b['edit'],gain=b['exact']-k0,kappa=b['exact']))
        log('  APPLY %s %s: +%.3e -> kappa %.15f'%(pl.name,json.dumps(b['edit'])[:100],b['exact']-k0,b['exact']))
    return cur,applied
def fixed_point(pls,w,rounds=6,log=print,**kw):
    """cycle the classes (greedy, up to 40 steps each) until a full round gains nothing"""
    cur=pin(w); allapplied=[]
    for rd in range(rounds):
        k_start=evaluate(cur)['kappa']
        for pl in pls:
            cur,ap=greedy(pl,cur,steps=40,log=log,**kw); allapplied+=[dict(a,cls=pl.name) for a in ap]
        if evaluate(cur)['kappa']<=k_start+1e-15: break
    return cur,allapplied

# ---- CLI:  tk <class> WORD [--apply] [--steps N] [--max-sites N] [--shard i/n] [--out F] [--results F.jsonl] [--edit JSON] [--list N]
def add_parsers(sp):
    for name in CLASSES:
        pl=plugin(name) if False else None
        p=sp.add_parser(name,help=DOCS[name]); p.add_argument('word'); p.add_argument('--apply',action='store_true',help='greedy: apply the best improving edit(s) and write --out')
        p.add_argument('--steps',type=int,default=40); p.add_argument('--max-sites',type=int,default=0); p.add_argument('--shard',default='0/1',help='i/n: price only edits i mod n (parallel shards)')
        p.add_argument('--out'); p.add_argument('--results',help='append one JSON line per priced edit'); p.add_argument('--edit',help='JSON edit: apply exactly this edit, print exact kappa (and write --out)'); p.add_argument('--list',type=int,default=10)
        p.add_argument('--exact-top',type=int,default=8); p.add_argument('--opt',action='append',help='class option k=v (relay: terms=4 sole=1 nbest=2 engine=dfs|cpsat ids=i,j)')
DOCS=dict(ibase='paid interior bases screen (#5678): conjugate a block interval by R=I+qE_ab',a2x='A2 paid rank exchange screen (#5643/#5650): move a scalar chain contact',
          blockmove='block reframe screen (#5739): move a same-chart block to a new lower-dimensional chart',split2='two-boundary helper split screen (#5718): distinct input/output bases',
          relay='relay/temporal screen (#5713/#5605/#5612): replace a sole contact by an exact span of existing values at other times (spansolve)')
def cli(pl,a):
    path,w=load(a.word); w=pin(w); sh=tuple(int(x) for x in a.shard.split('/')); log=lambda *x:print(*x,flush=True)
    k0=evaluate(w)
    if not k0.get('legal'): log('ILLEGAL', k0.get('why')); return 1
    log('%s on %s: kappa %.15f (%d events)'%(pl.name,os.path.basename(path),k0['kappa'],len(w['program'])))
    if a.edit:
        v=View(w); w2=pl.apply(v,json.loads(a.edit)); o=evaluate(w2); log('edit ->',{k:o.get(k) for k in('ok','legal','kappa','side_ok','why')},'gain %+.3e'%(o['kappa']-k0['kappa']) if o.get('legal') else '')
        if a.out and o.get('ok'): json.dump(w2,gzip.open(a.out,'wt')); log('wrote',a.out)
        return 0 if o.get('ok') else 1
    res=open(a.results,'a') if a.results else None
    if a.apply:
        cur,ap=greedy(pl,w,steps=a.steps,log=log,max_sites=a.max_sites or None,shard=sh,results=res,exact_top=a.exact_top,base_k=k0['kappa'])
        if ap and a.out:
            json.dump(cur,gzip.open(a.out,'wt')); log('wrote %s: %d edits, kappa %.15f'%(a.out,len(ap),ap[-1]['kappa']))
        elif not ap: log('no improving edit')
        return 0
    out,_=screen(pl,w,max_sites=a.max_sites or None,shard=sh,results=res,exact_top=a.exact_top,base_k=k0['kappa'],log=log)
    for r in out[:a.list]: log('  gain %+.3e exact %s %s'%(r['gain'],r.get('exact'),json.dumps(r['edit'])[:160]))
    best=[r for r in out if r.get('word') is not None and r.get('exact') and r['exact']>k0['kappa']+1e-15]
    if best and a.out:
        b=max(best,key=lambda r:r['exact']); json.dump(b['word'],gzip.open(a.out,'wt')); log('wrote best single edit %s: kappa %.15f (+%.3e)'%(a.out,b['exact'],b['exact']-k0['kappa']))
    return 0
# ---- eval registration
def screen_fn(name):
    def fn(ctx,cur,base):
        import eval as E
        o=base+'.json.gz'; rc=E._run([name,cur,'--apply','--out',o],base+'.log',ctx['tl'],ctx)
        return (o if os.path.exists(o) else None),dict(rc=rc)
    return fn
def register_screens():
    import eval as E
    for n in CLASSES:
        if n not in E.SCREENS: E.register(n,screen_fn(n))
