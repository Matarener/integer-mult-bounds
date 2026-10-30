"""drive -- the word-search driver (SEARCHCORE): `tk search --from WORD --strategy greedy|beam|anneal|lns --classes a2x,ibase,...,reorder --budget CPUH --seed S`.
Moves: the movekit plugin classes (ibase a2x blockmove split2: sites(view)->edits, priced by quick() or apply+evaluate) and the existing screens (handoff evretime reorder split
retime) as LARGE moves (subprocess `tk <screen>`).  Evaluator interface: ev.evaluate(word, edit=None) -> dict(ok, legal, kappa, ...): FullEvaluator = legal.check + exact invoice
(~0.13 s/word on #5718); IncrEvaluator (wsearch/evalincr.py, DEFAULT: incr.IncrWord try_edit/commit with a periodic full-check resync) plugs in behind the same call (--evaluator full = old path).
Determinism: all randomness from random.Random(seed) (state checkpointed); pools are enumerated in the plugins' own order; schedules use the step index when --max-steps is given
(else the CPU fraction, so cut-off points depend on machine speed).  Resumable: state + current/best words go to the store every ~60 CPU s and on every new best; rerun the same
command (same --run-id) to continue.  Every hit above --frontier is re-validated (tk accept --native-ref, with the profile's own PR stack) before it is flagged CANDIDATE."""
import sys,os,json,gzip,time,random,math,subprocess,itertools,copy,hashlib
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); SEARCH_DIR=W + '/ext/SEARCH'
EPS=1e-15
PLUGINS=('ibase','a2x','blockmove','split2'); SCREENS=('handoff','evretime','reorder','split','retime')
POOL_CAP=dict(a2x=60000,ibase=6000,blockmove=200,split2=200)
def cpu():
    t=os.times(); return t.user+t.system+t.children_user+t.children_system
def log(*a): print(time.strftime('%H:%M:%S'),*a,flush=True)

# ---------------------------------------------------------------- evaluators
def free_bounds():
    os.environ.setdefault('TK_FREE_BOUNDS','1')
def install_relax():
    """--relax: legal.check ignores 'Public inventory bound' (toolkit legal.py caps public at 750; the #5751 stack allows 767) and X.side always passes (profile tail decay of #5751
    not modelled).  Hits are flagged RELAXED and only the PR stack (tk accept) decides."""
    import legal,price_exact as X
    if getattr(legal.check,'_relaxed',False): return
    oc=legal.check
    def check(w,*a,**k):
        r=oc(w,*a,**k); v=[x for x in r['violations'] if x[1]!='Public inventory bound']
        if len(v)!=len(r['violations']): r=dict(r,violations=v,ok=not v)
        return r
    check._relaxed=True; legal.check=check
    os_=X.side
    def side(*a,**k):
        r=os_(*a,**k); return dict(r,ok=True,orig_ok=r['ok'])
    X.side=side
class FullEvaluator:
    name='full'
    def __init__(s): import movekit; s.M=movekit
    def evaluate(s,word,edit=None,base=None): return s.M.evaluate(word)
    def adopt(s,w): pass
    def check_sync(s): return None
def make_evaluator(kind,resync=200):
    if kind=='incr':
        try:
            from .evalincr import IncrEvaluator
            return IncrEvaluator(resync=resync,log=log)
        except Exception as ex: log('incr evaluator unavailable (%r): falling back to full'%(ex,))
    return FullEvaluator()

# ---------------------------------------------------------------- the search object
class Search:
    def __init__(s,a):
        import tkcommon,movekit as M
        from . import canon,store
        s.a=a; s.M=M; s.canon=canon; s.tkc=tkcommon
        s.src=a.src; s.pr=a.src if (a.src and a.src.isdigit() and os.path.exists(TK+'/profiles/%s.json'%a.src)) else None
        if getattr(a,'profile',None): os.environ['TK_PROFILE']=a.profile
        elif s.pr: os.environ['TK_PROFILE']=s.pr
        free_bounds()
        if a.relax: install_relax()
        s.ev=make_evaluator(a.evaluator,a.resync); s.store=store.Store(a.store)
        s.seed=a.seed; s.rng=random.Random(a.seed); s.frontier=float(a.frontier)
        s.run_id=a.run_id or '%s-%s-s%d'%(a.strategy,a.src,a.seed)
        s.classes=[c for c in a.classes.split(',') if c]; s.plug=[c for c in s.classes if c in PLUGINS]; s.scr=[c for c in s.classes if c in SCREENS]
        bad=[c for c in s.classes if c not in PLUGINS+SCREENS]
        if bad: raise SystemExit('unknown classes %s'%bad)
        s.plugins={c:M.plugin(c) for c in s.plug}
        s.cnt=dict(priced=0,exact=0,accepted=0,improved=0,errors=0); s.cpu0=cpu(); s.cpu_prev=0.0; s.step=0
        s.workdir=SEARCH_DIR+'/work/'+s.run_id; os.makedirs(s.workdir,exist_ok=True)
        s.best=None; s.cur=None; s.last_ck=0
        s.tm=dict(apply=0.0,eval=0.0,pool=0.0,view=0.0); s.upd_cls={}; s.pools={}; s.view_cache=None; s.nadopt=0; s.dirty=False; s.pend=[]; s.t0=time.time()
        s.cnt.update(tries=0,pool_upd=0,pool_rebuild=0)
    # ---- bookkeeping
    def used(s): return s.cpu_prev+cpu()-s.cpu0
    def profile(s,w):
        try: return s.tkc.profile_of(w)[0]
        except SystemExit: return '?'
    def load_start(s):
        ck=s.store.load_ck(s.run_id)
        if ck:
            w=s.store.get_word(ck['cur']); b=s.store.get_word(ck['best'])
            s.cur=s.M.pin(w); s.kcur=ck['kcur']; s.hcur=ck['cur']; s.rng.setstate((ck['rng'][0],tuple(ck['rng'][1]),ck['rng'][2])); s.cnt=ck['cnt']; s.cpu_prev=ck['cpu']; s.step=ck['step']
            s.best=dict(word=s.M.pin(b),k=ck['kbest'],h=ck['best']); s.extra=ck.get('extra',{})
            for k_ in('tries','pool_upd','pool_rebuild'): s.cnt.setdefault(k_,0)
            log('RESUME run %s: step %d, cpu %.0fs, cur %.15f best %.15f'%(s.run_id,s.step,s.cpu_prev,s.kcur,s.best['k'])); return
        p,w=s.tkc.load(s.src); w=s.M.pin(w); o=s.M.evaluate(w)
        if not o.get('legal'): raise SystemExit('start word illegal: %s'%o.get('why'))
        if not o.get('ok'): log('WARNING start word legal but not ok (side/budgets) -- use --relax for words the toolkit does not model')
        s.cur=w; s.kcur=o['kappa']; s.hcur=s.canon.canon_hash(w); s.extra={}
        s.record_word(s.hcur,w,o,None,None,'start'); s.best=dict(word=w,k=s.kcur,h=s.hcur)
        log('START %s (%s) profile %s: kappa %.15f, %d events, %d public, hash %s'%(s.src,os.path.basename(p),s.profile(w),s.kcur,len(w['program']),len(w['initial']),s.hcur[:12]))
    def record_word(s,h,w,o,parent,edit,cls=None,store_blob=True):
        if store_blob: s.store.put_word(h,w)
        iv=s.M.interval(w) if o.get('legal') else None
        s.store.add_eval(h,s.profile(w),o.get('legal'),o.get('kappa'),iv,o.get('ok'),'fast',relaxed=bool(s.a.relax),side_ok=o.get('side_ok'))
        s.store.add_lineage(h,parent,edit,cls or (edit.get('cls') if isinstance(edit,dict) else str(edit)),s.seed,s.run_id,s.step)
    def checkpoint(s,force=False,extra=None):
        if not force and s.used()-s.last_ck<60: return
        s.last_ck=s.used(); s.ensure_hash(); s.store.put_word(s.hcur,s.cur)
        if extra is not None: s.extra=extra
        st=s.rng.getstate(); s.store.save_ck(s.run_id,dict(cur=s.hcur,best=s.best['h'],kcur=s.kcur,kbest=s.best['k'],rng=[st[0],list(st[1]),st[2]],cnt=s.cnt,cpu=s.used(),step=s.step,extra=s.extra,strategy=s.a.strategy,args=vars(s.a)))
    def ensure_hash(s):
        """canonical hash of the current word is computed lazily (0.36 s): non-best adoptions only append to s.pend; the lineage of the next hash covers them"""
        if not s.dirty: return s.hcur
        h=s.canon.canon_hash(s.cur); s.store.add_lineage(h,s.hcur,dict(cls='walk',n=len(s.pend),last=s.pend[-3:]),'walk',s.seed,s.run_id,s.step); s.hcur=h; s.dirty=False; s.pend=[]; return h
    def note_best(s,w,o,parent,edit,cls):
        """new global best?  store it, validate if above the frontier"""
        if o['kappa']<=s.best['k']+EPS: return False
        if s.a.evaluator=='incr' and s.ev.word is w: s.ev.check_sync()          # full legal.check + price must agree with the incremental state at every new best
        h=s.canon.canon_hash(w); s.pend=s.pend[-6:]; s.record_word(h,w,o,s.hcur if s.dirty else parent,dict(edit,walk=s.pend) if isinstance(edit,dict) and s.dirty else edit,cls); s.best=dict(word=w,k=o['kappa'],h=h); s.cnt['improved']+=1; s.dirty=False; s.pend=[]
        log('BEST %.15f (+%.3e vs start) via %s %s  [%d priced, %d exact, %.0f cpu-s]'%(o['kappa'],o['kappa']-s.k0,cls,json.dumps(edit,default=str)[:90],s.cnt['priced'],s.cnt['exact'],s.used()))
        if o['kappa']>s.frontier and o['kappa']>s.k0+EPS: s.validate(h,w,o['kappa'])
        s.checkpoint(True); return True
    # ---- validation of frontier hits
    def validate(s,h,w,k,force=False):
        out=os.path.join(SEARCH_DIR,'CANDIDATE-%s.json.gz'%h[:12]); os.makedirs(SEARCH_DIR,exist_ok=True); json.dump(w,gzip.open(out,'wt'))
        log('ABOVE FRONTIER %.15f > %.10f: %s -- validating (tk accept --native-ref, profile stack)'%(k,s.frontier,out))
        if s.a.no_validate: log('  --no-validate: UNVALIDATED'); return None
        res=validate_file(out,os.environ.get('TK_PROFILE'))
        s.store.add_validation(h,'accept',res['accept_ok'],res); s.store.add_validation(h,'prstack',res['prstack_ok'],res); s.store.add_validation(h,'native_ref',res['native_ref']['ok'],res['native_ref'])
        flag='CANDIDATE' if (res['accept_ok'] and res['prstack_ok'] and res['native_ref']['ok']) else 'UNCONFIRMED'
        log('  %s %s kappa %.15f interval %s (accept_ok=%s prstack_ok=%s native_ref=%s)'%(flag,h[:12],k,res.get('interval'),res['accept_ok'],res['prstack_ok'],res['native_ref']))
        with open(SEARCH_DIR+'/hits.jsonl','a') as f: f.write(json.dumps(dict(ts=time.time(),run=s.run_id,hash=h,kappa=k,flag=flag,validation=res,file=out),default=str)+'\n')
        return res
    # ---- pools and pricing
    refresh=25; full_every=300; regen_every=6
    def pool(s,cname,view,force=False):
        """shuffled pool of edits of one class on `view`.  An existing pool of an EARLIER word is updated incrementally when the plugin has update_sites(v_old,v_new,delta,pool)
        (only sites touching the registers / blocks the committed edits changed are re-enumerated); plugins without the hook that enumerate fast (<0.5 s) are rebuilt on every
        new word, slow ones every `refresh` adoptions (stale sites are merely poor proposals: every adoption is evaluated exactly)."""
        pl=s.plugins[cname]; P=s.pools.get(cname); cap=s.a.pool_cap or POOL_CAP[cname]
        if P is not None and not force:
            if P['v'].w is view.w: return P['L']
            upd=getattr(pl,'update_sites',None) if s.a.incremental_pools else None
            if upd is not None and s.nadopt-P['nfull']>=s.full_every: upd=None; force=True      # periodic full rebuild (drift guard)
            if upd is not None:
                t0=time.time()
                try:
                    from .pools import Delta
                    d=Delta(P['v'],view); L=None
                    if d.frames_ok and d.nhunks<=400:
                        if getattr(pl,'defer_regen',False):          # remap now, re-enumerate the accumulated touched registers every `regen_every` adoptions
                            pend=P['pend']|d.regs; regen=s.nadopt-P['n_regen']>=s.regen_every
                            if regen: d.regs=pend
                            L=upd(P['v'],view,d,P['L'],regen=regen)
                        else: regen=True; pend=set(); L=upd(P['v'],view,d,P['L'])
                except (ValueError,KeyError,AssertionError,IndexError,TypeError) as ex: L=None; s.cnt['errors']+=1
                if L is not None:
                    L=L[:cap] if len(L)>cap else L; s.rng.shuffle(L); s.pools[cname]=dict(L=L,v=view,build=P['build'],n0=s.nadopt,nfull=P['nfull'],pend=set() if regen else pend,n_regen=s.nadopt if regen else P['n_regen']); s.cnt['pool_upd']+=1
                    s.upd_t=getattr(s,'upd_t',0.0)+time.time()-t0; s.upd_cls[cname]=s.upd_cls.get(cname,0.0)+time.time()-t0; s.upd_regs=getattr(s,'upd_regs',0)+len(d.regs); s.upd_h=getattr(s,'upd_h',0)+d.nhunks; return L
            elif not force and P['build']>=0.5 and s.nadopt-P['n0']<s.refresh: return P['L']
        t0=time.time(); ctx=pl.prepare(view); L=[]
        for ed in pl.sites(view,ctx):
            L.append(ed)
            if len(L)>=cap: break
        s.rng.shuffle(L); s.pools[cname]=dict(L=L,v=view,build=time.time()-t0,n0=s.nadopt,nfull=s.nadopt,pend=set(),n_regen=s.nadopt); s.cnt['pool_rebuild']+=1; s.build_tot=getattr(s,'build_tot',0.0)+time.time()-t0; return L
    def price(s,cname,view,ed):
        """estimated kappa of the edit or None (illegal / not applicable).  quick classes: trajectory-exact census only (no legality of values) -- every adoption is re-evaluated."""
        pl=s.plugins[cname]; s.cnt['priced']+=1
        try:
            if pl.quick: k,_=s.M.quick(view,pl.scalars(view,ed)); return k
            o=s.ev.evaluate(pl.apply(view,ed),ed,base=view.w); s.cnt['exact']+=1; return o['kappa'] if o.get('ok') else None
        except (ValueError,KeyError,AssertionError,IndexError,TypeError,ZeroDivisionError): s.cnt['errors']+=1; return None
    def apply_exact(s,cname,view,ed):
        """apply the edit with the plugin and evaluate EXACTLY against the current word (incr: diff_edit + try_edit, the state is only committed by adopt)"""
        pl=s.plugins[cname]; t0=time.perf_counter()
        try: w2=pl.apply(view,ed)
        except (ValueError,KeyError,AssertionError,IndexError,TypeError,ZeroDivisionError): s.cnt['errors']+=1; s.tm['apply']+=time.perf_counter()-t0; return None,None
        t1=time.perf_counter(); o=s.ev.evaluate(w2,ed,base=view.w); s.cnt['exact']+=1; s.tm['apply']+=t1-t0; s.tm['eval']+=time.perf_counter()-t1; return (w2,o) if o.get('ok') else (None,o)
    def adopt(s,w,o,edit,cls,parent=None):
        """move the walk to word w (exact outcome o)"""
        parent=parent or s.hcur; s.cur=w; s.kcur=o['kappa']; s.cnt['accepted']+=1; s.nadopt+=1; s.view_cache=None
        s.ev.adopt(w)
        if o['kappa']>s.best['k']+EPS: s.note_best(w,o,parent,edit,cls); s.hcur=s.best['h']
        else: s.dirty=True; s.pend.append(dict(cls=cls,**{k:v for k,v in (edit if isinstance(edit,dict) else {}).items() if k in('i','j','a','b','q','s0','s1','i0','i1','window')}))
    def view(s):
        if s.view_cache is None or s.view_cache.w is not s.cur: t=time.perf_counter(); s.view_cache=s.M.View(s.cur); s.tm['view']+=time.perf_counter()-t
        return s.view_cache
    def left(s): return s.used()<s.deadline and (not s.a.max_steps or s.step<s.a.max_steps)
    # ---- screens as large moves
    def run_screen(s,name,w,window=None):
        import eval as E
        pth=os.path.join(s.workdir,'cur_%d.json.gz'%s.step); json.dump(w,gzip.open(pth,'wt')); base=os.path.join(s.workdir,'scr_%d_%s'%(s.step,name))
        ctx=dict(tl=s.a.screen_tl,threads=1,k=2,maxm=0,ev_threads=1)
        try:
            if name=='reorder' and window:
                o=base+'.json.gz'; E._run(['reorder',pth,'--k','2','--maxm','0','--tl',str(s.a.screen_tl),'--inline','--window',str(window[0]),str(window[1]),'--out',o],base+'.log',s.a.screen_tl,ctx)
                out=o if os.path.exists(o) else None
            else: out,_=E.SCREENS[name](ctx,pth,base)
        except Exception as ex: log('screen %s failed: %r'%(name,ex)); return None,None
        if not out or not os.path.exists(out): return None,None
        w2=s.M.pin(json.load(gzip.open(out))); o=s.ev.evaluate(w2); s.cnt['exact']+=1
        return (w2,o) if o.get('ok') else (None,o)
    def try_screens(s,window=None):
        for name in s.scr:
            w2,o=s.run_screen(name,s.cur,window)
            if w2 is not None and o['kappa']>s.kcur+EPS:
                log('SCREEN %s: +%.3e'%(name,o['kappa']-s.kcur)); s.adopt(w2,o,dict(cls=name,window=window),name); return True
        return False

    # ================================================================ strategies
    def sweep_plugin(s,cname,topk=20):
        """price the pool of one class on the current word; adopt improving edits best-first (re-checked exactly on the moving word).  -> number adopted"""
        view=s.M.View(s.cur); L=s.pool(cname,view,force=True); sc=[]
        for ed in L:
            if not s.left(): break
            k=s.price(cname,view,ed)
            if k is not None and k>s.kcur+EPS: sc.append((k,ed))
        sc.sort(key=lambda t:-t[0]); n=0; fails=0
        for k,ed in sc:
            if fails>=topk or not s.left(): break
            view=s.M.View(s.cur); w2,o=s.apply_exact(cname,view,ed)
            if w2 is not None and o['kappa']>s.kcur+EPS:
                s.step+=1; s.adopt(w2,o,dict(ed,cls=cname),cname); n+=1; fails=0
            else: fails+=1
        s.checkpoint(); return n
    def greedy(s):
        while s.left():
            gained=0
            for c in s.plug:
                if not s.left(): break
                gained+=s.sweep_plugin(c)
            if not gained and s.left():
                if not s.try_screens(): log('GREEDY local optimum (all classes): kappa %.15f'%s.kcur); break
        s.checkpoint(True)
    def anneal(s):
        T0,T1=[float(x) for x in s.a.temp.split(',')]; start_used=s.used(); span=max(1e-9,s.deadline-start_used)
        screen_every=400; quick_pre=(s.a.prefilter=='quick') or (s.a.prefilter=='auto' and s.a.evaluator!='incr'); empty=0
        if not s.plug: log('anneal needs plugin classes'); return
        while s.left():
            frac=(s.step/s.a.max_steps) if s.a.max_steps else min(1.0,(s.used()-start_used)/span); T=T0*(T1/T0)**frac
            view=s.view(); c=s.rng.choice(s.plug); tp=time.perf_counter(); L=s.pool(c,view); s.tm['pool']+=time.perf_counter()-tp
            if not L:
                s.step+=1; empty+=1
                if empty>50*len(s.plug): log('anneal: all pools empty'); break
                continue
            empty=0; ed=s.rng.choice(L); s.step+=1; pl=s.plugins[c]
            if quick_pre and pl.quick:             # trajectory-exact kappa first: Metropolis before the (more expensive) exact legality check
                k=s.price(c,view,ed)
                if k is None: continue
                d=k-s.kcur
                if d<0 and s.rng.random()>=math.exp(d/T): continue
            w2,o=s.apply_exact(c,view,ed)
            if w2 is None: continue
            d=o['kappa']-s.kcur
            if not(quick_pre and pl.quick) and d<0 and s.rng.random()>=math.exp(d/T): continue
            s.adopt(w2,o,dict(ed,cls=c,T=T),c)
            if s.scr and s.step%screen_every==0 and s.try_screens(): pass
            s.checkpoint()
            if s.step%500==0: log('anneal step %d T=%.2e cur %.15f best %.15f tries %d exact %d acc %d pools upd/rebuilt %d/%d'%(s.step,T,s.kcur,s.best['k'],s.cnt['priced'],s.cnt['exact'],s.cnt['accepted'],s.cnt['pool_upd'],s.cnt['pool_rebuild']))
        s.checkpoint(True)
    def beam(s):
        B=s.a.beam_width; m=s.a.beam_children; beam=[(s.kcur,s.hcur,s.cur)]; seen={s.hcur}; stale=0
        while s.left() and stale<2:
            kids=[]
            for k0,h0,w0 in beam:
                view=s.M.View(w0)
                for c in s.plug:
                    L=s.pool(c,view,force=True); sc=[]
                    for ed in L:
                        if not s.left(): break
                        k=s.price(c,view,ed)
                        if k is not None: sc.append((k,ed))
                    sc.sort(key=lambda t:-t[0])
                    for k,ed in sc[:m]:
                        w2,o=s.apply_exact(c,view,ed)
                        if w2 is not None: kids.append((o['kappa'],w2,o,ed,c,h0))
            kids.sort(key=lambda t:-t[0]); new=[]
            for kk,w2,o,ed,c,h0 in kids:
                if len(new)>=B: break
                h=s.canon.canon_hash(w2)
                if h in seen: continue
                seen.add(h); s.step+=1; s.cur=w2; s.kcur=kk; s.hcur=h
                if kk>s.best['k']+EPS: s.note_best(w2,o,h0,ed,c); s.hcur=s.best['h']
                else: s.record_word(h,w2,o,h0,dict(ed,cls=c),c,store_blob=False)
                new.append((kk,h,w2))
            if not new: break
            allb=sorted(beam+new,key=lambda t:-t[0])[:B]
            stale=stale+1 if max(t[0] for t in new)<=max(t[0] for t in beam)+EPS else 0
            beam=allb; log('BEAM level: best %.15f  width %d  (%d kids, %d priced, %d exact)'%(beam[0][0],len(beam),len(kids),s.cnt['priced'],s.cnt['exact']))
            s.cur=beam[0][2]; s.kcur=beam[0][0]; s.hcur=beam[0][1]; s.checkpoint(True)
    def s2s_repair(s,window=None):
        """GENSPLICE operator: re-synthesise the window (whole word if None) state-to-state (synth/s2s.py): exact end state, frames, MOVEs unchanged => kappa identical, events drop (the binding cap).
        Adopted when exactly legal and kappa >= current - EPS (a plateau move that regains event headroom)."""
        from synth import s2s
        n=len(s.cur['program']); t0,t1=(0,n) if window is None else (max(0,window[0]),min(n,window[1]))
        try: edit,st=s2s.resynth(s.cur,t0,t1)
        except Exception as ex: s.cnt['errors']+=1; log('s2s error %r'%(ex,)); return False
        if edit is None: return False
        w2=s2s.apply(s.cur,edit); o=s.ev.evaluate(w2); s.cnt['exact']+=1
        if not(o and o.get('ok')) or o['kappa']<s.kcur-EPS: return False
        s.adopt(w2,o,dict(cls='s2s',window=[t0,t1],saved=st['saved']),'s2s'); log('s2s window %s: -%d events (%d -> %d)'%((t0,t1),st['saved'],n,len(w2['program']))); return True
    def lns(s):
        lo,hi=[int(x) for x in s.a.lns_window.split(',')]
        import dag as D
        while s.left():
            s.step+=1; n=len(s.cur['program']); L=s.rng.randint(lo,hi); a0=s.rng.randrange(0,max(1,n-L)); window=(a0,a0+L)
            mode=s.rng.choices(['perturb','realise','window'],weights=[0.7,0.15,0.15])[0] if s.plug else 'window'
            s.ensure_hash(); base_w,base_k,base_h=s.cur,s.kcur,s.hcur
            if mode=='perturb': s.perturb(window)      # destroy: a few random legal moves inside the window (kappa may drop by at most --lns-drop in total), repair below
            if mode=='realise':       # destroy: forget the recorded MOVE hops of the ops in the window (lazy direct MOVEs), repair below
                try:
                    d=D.decompile(s.cur,forms=False); ops_lo=sum(1 for e in s.cur['program'][:a0] if e[0]!='MOVE'); ops_hi=sum(1 for e in s.cur['program'][:a0+L] if e[0]!='MOVE')
                    hops=[h for h in d['schedule']['hops'] if not(ops_lo<=h[0]<ops_hi)]; w2,_=D.realise(d,dict(hops=hops),(),verify=False); w2=s.M.pin(w2); o=s.ev.evaluate(w2); s.cnt['exact']+=1
                except Exception as ex: o=None
                if not o or not o.get('ok'): log('lns %d realise-destroy window %s: illegal (skipped)'%(s.step,window)); continue
                s.cur,s.kcur=w2,o['kappa']; s.view_cache=None; s.dirty=True; s.pend.append(dict(cls='realise',window=window))
            # repair: window-restricted plugin sweeps, then screens on the window
            s.window=window; gained=0
            for c in s.plug:
                if not s.left(): break
                gained+=s.sweep_window(c,window)
            if s.scr and s.left(): s.try_screens(window=window if 'reorder' in s.scr else None)
            if getattr(s.a,'s2s',False) and s.left(): s.s2s_repair(window)
            if s.kcur>=base_k-EPS:           # not worse: keep the walk where it is (plateau drift); the hash / lineage are computed lazily
                if s.kcur>base_k+EPS: s.ensure_hash()
            else: s.cur,s.kcur,s.hcur=base_w,base_k,base_h; s.dirty=False; s.pend=[]; s.view_cache=None
            log('lns %d %s window %s: %.15f -> %.15f (%s)  [%d priced, %d exact]'%(s.step,mode,window,base_k,s.kcur,'improved' if s.kcur>base_k+EPS else ('kept' if s.cur is not base_w else 'same'),s.cnt['priced'],s.cnt['exact']))
            s.checkpoint()
        s.checkpoint(True)
    def perturb(s,window):
        """LNS destroy step: adopt 2-6 random exactly-legal edits that overlap the window, each keeping kappa within --lns-drop of the start of the iteration"""
        npert=s.rng.randint(2,6); done=0; tries=0; floor=s.kcur-s.a.lns_drop
        while done<npert and tries<80 and s.left():
            c=s.rng.choice(s.plug); view=s.view(); L=s.pool(c,view); tries+=1
            if not L: continue
            ed=None
            for _ in range(60):
                e=s.rng.choice(L)
                try: sp=s.span_of(c,view,e)
                except (IndexError,KeyError): continue
                if sp is None or not(sp[1]<window[0] or sp[0]>window[1]): ed=e; break
            if ed is None: continue
            w2,o=s.apply_exact(c,view,ed)
            if w2 is None or o['kappa']<floor: continue
            s.adopt(w2,o,dict(ed,cls=c,perturb=1),c); done+=1
        return done
    def span_of(s,cname,view,ed):
        """event positions (lo,hi) an edit spans (plugin.span, else the integer fields of the edit)"""
        pl=s.plugins[cname]
        if hasattr(pl,'span'): return pl.span(view,ed)
        ints=[v for key,v in ed.items() if key in('i','j','P3','s0','s1','i0','i1','p','q0','q1') and isinstance(v,int)]
        return (min(ints),max(ints)) if ints else None
    def window_edits(s,cname,view,window):
        L=s.pool(cname,view); out=[]
        for ed in L:
            try: sp=s.span_of(cname,view,ed)
            except (IndexError,KeyError): continue
            if sp is None or not(sp[1]<window[0] or sp[0]>window[1]): out.append(ed)
        return out
    def sweep_window(s,cname,window,topk=10):
        """LNS repair of one class inside the window.  incr evaluator: FIRST-IMPROVEMENT with exact try_edit (up to --lns-price-cap edits tried, the window pool is refreshed after every
        adoption); full evaluator: quick() ranking of the window edits, then best-first exact adoption"""
        if s.a.evaluator=='incr':
            got=0; tried=0; cap=s.a.lns_price_cap; view=s.view(); W_=s.window_edits(cname,view,window); i=0
            while tried<cap and s.left():
                if i>=len(W_): break
                ed=W_[i]; i+=1; tried+=1
                w2,o=s.apply_exact(cname,view,ed)
                if w2 is not None and o['kappa']>s.kcur+EPS:
                    s.adopt(w2,o,dict(ed,cls=cname),cname); got+=1; view=s.view(); W_=s.window_edits(cname,view,window); i=0
            return got
        view=s.view(); L=s.pool(cname,view); sc=[]; n=0; cap=min(s.a.pool_cap or POOL_CAP[cname],s.a.lns_price_cap)
        for ed in L:
            if not s.left() or n>=cap: break
            try: sp=s.span_of(cname,view,ed)
            except (IndexError,KeyError): continue
            if sp is not None and (sp[1]<window[0] or sp[0]>window[1]): continue
            n+=1; k=s.price(cname,view,ed)
            if k is not None and k>s.kcur+EPS: sc.append((k,ed))
        sc.sort(key=lambda t:-t[0]); got=0; fails=0
        for k,ed in sc:
            if fails>=topk or not s.left(): break
            view=s.view(); w2,o=s.apply_exact(cname,view,ed)
            if w2 is not None and o['kappa']>s.kcur+EPS: s.adopt(w2,o,dict(ed,cls=cname),cname); got+=1; fails=0
            else: fails+=1
        return got
    def run(s):
        s.load_start(); s.k0=s.extra.get('k0',s.kcur); s.extra['k0']=s.k0
        s.deadline=s.used()+s.a.budget*3600 if not s.extra.get('deadline') else s.extra['deadline']
        s.ev.adopt(s.cur) if s.a.evaluator=='incr' else None
        s.extra['deadline']=s.deadline; t=time.time(); c0=dict(s.cnt)
        if getattr(s.a,'s2s',False): s.s2s_repair(None)          # --s2s: start from the event-compacted word (kappa identical)
        log('RUN %s strategy %s classes %s budget %.3f cpu-h seed %d evaluator %s'%(s.run_id,s.a.strategy,','.join(s.classes),s.a.budget,s.seed,s.ev.name))
        getattr(s,s.a.strategy)()
        el=time.time()-t; pr=s.cnt['priced']-c0['priced']; ex=s.cnt['exact']-c0['exact']
        log('DONE %s: kappa best %.15f (%+.3e vs start), cur %.15f; %d priced + %d exact in %.0fs wall = %.0f priced/min, %.1f exact/min, %d adopted, %d errors'%(s.run_id,s.best['k'],s.best['k']-s.k0,s.kcur,pr,ex,el,60*pr/max(el,1e-9),60*ex/max(el,1e-9),s.cnt['accepted'],s.cnt['errors']))
        log('pools: %d updated (%.1fs total, avg %.0f regs, %.1f hunks), %d rebuilt (%.1fs); evaluator %s: %d tries, %d binds, %d full evals, %.1fs in try_edit, %d resyncs ok; wall split: %s'%(s.cnt['pool_upd'],getattr(s,'upd_t',0.0),getattr(s,'upd_regs',0)/max(1,s.cnt['pool_upd']),getattr(s,'upd_h',0)/max(1,s.cnt['pool_upd']),s.cnt['pool_rebuild'],getattr(s,'build_tot',0.0),s.ev.name,getattr(s.ev,'ntry',0),getattr(s.ev,'nbind',0),getattr(s.ev,'nfull',0),getattr(s.ev,'t_try',0.0),getattr(s.ev,'nresync',0),' '.join('%s %.0fs'%kv for kv in s.tm.items())+'; pool update s by class '+' '.join('%s %.1f'%kv for kv in s.upd_cls.items())))
        return s.best

def native_ref_verdict(j):
    """did the reference native check run and pass?  j = the accept json.  ran = native_ref flag true, pair count > 0, every pair freshly computed (computed == pairs: cache bypassed), a verdict present"""
    nc=j.get('native_check') or {}
    ref=nc.get('ref',j.get('native_ref')); pairs=nc.get('pairs',j.get('native_pairs')); comp=nc.get('computed',j.get('native_computed')); bad=nc.get('bad',0 if j.get('ok') else None)
    verdict='ok' in j
    ran=bool(ref) and isinstance(pairs,int) and pairs>0 and comp==pairs and verdict
    return dict(requested=True,ran=ran,ref_flag=ref,pairs=pairs,computed=comp,bad=bad,verdict=j.get('ok') if verdict else None,ok=bool(ran and j.get('ok') and not bad))
def validate_file(path,profile):
    """`tk accept --native-ref` with the profile's own PR stack, the reference (clifford) native kernels EXPLICITLY requested (flag + TK_NATIVE_REF=1) and PROVED to have run:
    the accept json must report native_ref true, pair count > 0, every pair freshly computed (pair cache bypassed: computed == pairs), 0 bad pairs and carry a verdict.
    res['native_ref'] = dict(requested, ran, pairs, computed, bad, ok); accept_ok already includes it.  A hit without ok native_ref is never a CANDIDATE."""
    import tkcommon
    base=[tkcommon.PY,'-B',TK+'/tk.py']+(['--profile',profile] if profile else [])
    res=dict(accept_ok=False,prstack_ok=False,native_ref=dict(requested=True,ran=False,ok=False))
    try:
        env=dict(os.environ,TK_NATIVE_REF='1')
        r=subprocess.run(base+['accept',path,'--json','--native-ref'],capture_output=True,text=True,timeout=7200,env=env)
        try: j=json.loads(r.stdout[r.stdout.index('{'):])
        except Exception: j=dict(ok=False,error=(r.stdout+r.stderr)[-400:])
        res['native_ref']=native_ref_verdict(j)
        res['accept_ok']=bool(j.get('ok')) and res['native_ref']['ok']; res['interval']=[j.get('crossing_lo'),j.get('crossing_hi')]
        res['accept']={k:j.get(k) for k in('ok','stage','error','crossing_lo','crossing_hi','native_ref','native_pairs','native_computed','native_check','paid_calls','fields')}
        res['prstack_ok']=bool(j.get('ok')) and res['native_ref']['ok']        # `tk accept` with a stack profile IS the PR's own checker (sandboxed tkstack); without a stack profile there is no PR-stack level
        prof=tkcommon.DATA_PROFILES.get(profile) if profile else None
        res['has_pr_stack']=bool(prof and prof.get('stack'))
        if not res['has_pr_stack']: res['prstack_ok']=False; res['note']='profile has no vendored PR stack: accept is the toolkit real-stack model only'
        if j.get('ok') and not res['native_ref']['ok']: res['note']=(res.get('note','')+' reference native check NOT confirmed (ran=%s)'%res['native_ref']['ran']).strip()
    except Exception as ex: res['error']=repr(ex)[:300]
    return res

def main(a):
    from . import store
    if a.cpuq:
        argv=[x for x in sys.argv[1:]]
        # rebuild the command without --cpuq NAME
        i=argv.index('--cpuq'); del argv[i:i+2]
        run_id=a.run_id or '%s-%s-s%d'%(a.strategy,a.src,a.seed)
        if '--run-id' not in argv: argv+=['--run-id',run_id]
        name=a.cpuq; sec=int(a.budget*3600*1.15+600); sec=min(sec,14400)
        p=W+'/jobs/pending/%s.sh'%name
        open(p,'w').write('#!/bin/bash\n# timeout: %d\n# threads: 1\ncd %s\n%s/python3 -B %s/tk.py %s >> %s/ext/SEARCH/logs/%s.log 2>&1\necho "%s: tk search %s -> see store/report (%s/ext/SEARCH)" >> %s/the results log\n'%(sec,W,W,TK,' '.join(argv),W,name,name,run_id,W,W))
        os.makedirs(SEARCH_DIR+'/logs',exist_ok=True); os.chmod(p,0o755); print('wrote',p); return 0
    S=store.Store(a.store)
    if a.report: return report(S,a)
    if a.validate:
        import tkcommon
        r=S.db.execute('SELECT chash FROM words WHERE chash LIKE ?',(a.validate+'%',)).fetchone()
        if not r: print('no such hash'); return 1
        w=S.get_word(r['chash']); out=os.path.join(SEARCH_DIR,'CANDIDATE-%s.json.gz'%r['chash'][:12]); json.dump(w,gzip.open(out,'wt'))
        pr=a.src if (a.src and a.src.isdigit()) else None
        res=validate_file(out,pr or os.environ.get('TK_PROFILE')); S.add_validation(r['chash'],'accept',res['accept_ok'],res); S.add_validation(r['chash'],'prstack',res['prstack_ok'],res); S.add_validation(r['chash'],'native_ref',res['native_ref']['ok'],res['native_ref'])
        print('native_ref:',res['native_ref'])
        print(json.dumps(res,indent=1,default=str)); return 0 if res['accept_ok'] else 1
    if not a.src: raise SystemExit('tk search: --from WORD required')
    sr=Search(a); sr.run(); return 0

def report(S,a):
    rows=S.best(a.k)
    print('store %s: %s'%(S.path,S.stats()))
    fr=float(a.frontier)
    for i,r in enumerate(rows):
        v=S.validations(r['chash']); ch=S.chain(r['chash'])
        flag='CANDIDATE' if r['kappa']>fr and v.get('accept',{}).get('ok') and v.get('prstack',{}).get('ok') and v.get('native_ref',{}).get('ok') else ('ABOVE-FRONTIER-UNVALIDATED' if r['kappa']>fr else '')
        print('%2d. %s  kappa %.15f  [%s, %s]  profile %s  %s%s'%(i+1,r['chash'][:12],r['kappa'],r['lo'],r['hi'],r['profile'],'RELAXED ' if r['relaxed'] else '',flag))
        print('    validated: %s | lineage %d steps: %s'%(','.join('%s=%s'%(k,'ok' if x['ok'] else 'FAIL') for k,x in v.items()) or 'none',len(ch),' <- '.join('%s[%s]'%(c,(e or '')[:60]) for h,c,e in ch[:4])))
    return 0
