"""plateau -- neutral-network walks (PLATEAU; notes: toolkit/module docstring).

Hypothesis: improving moves hide behind exactly-neutral plateau steps that no greedy climb or beam crosses.  `tk plateau WORD` drifts over EXACTLY kappa-neutral legal edits
(primitive plugins P1/P2/P3 + a2x/ibase/blockmove/split2 pools), keeps a canonical-hash visited set (wsearch/canon.py), and every `--screen-every` accepted steps runs the screens from the
current point: a LOCAL level (P1/P2 in the windows the walk touched) and, every `--full-every` steps, the full `tk pscreen` sets (prims_extra handover alias macros prims_role prims).
Any state with exact kappa > the plateau level is adopted, re-validated (tk accept --native-ref, the profile's PR stack) and, above --frontier, written as ext/PLATEAU/CANDIDATE-*.json.gz.
Moves are SILENT when the canonical hash is unchanged (pure commutation / relabel: same trace) and REAL otherwise; the walk prefers REAL moves (silent accepted with probability --p-silent).
Determinism: every random choice comes from random.Random(seed); state (rng, counters, visited, cur word) is checkpointed to ext/PLATEAU/runs/RUN/ and a rerun with the same --run-id resumes.
  tk plateau 5811 --measure [--n 300]              neutral census per move class (single core, minutes)
  tk plateau 5811 --budget 1.5 --seed 1 [--cpuq NAME]   walk (CPU hours)
"""
import sys,os,json,gzip,time,random,math,collections,subprocess
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
if TK not in sys.path: sys.path.insert(0,TK)
W=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); PDIR=W + '/ext/PLATEAU'
EPS=1e-15; QTOL=1e-13
def cpu():
    t=os.times(); return t.user+t.system+t.children_user+t.children_system
def log(*a): print(time.strftime('%H:%M:%S'),*a,flush=True)
CLASSES=('P1','P2','P3','a2x','ibase','blockmove','split2','P7')
WINDOWED=('P1','P2')
class Walker:
    def __init__(s,a):
        import tkcommon,movekit as M,prims
        from . import canon,drive
        s.a=a; s.M=M; s.prims=prims; s.canon=canon; s.drive=drive; s.tkc=tkcommon
        s.src=a.src; s.pr=s.src if (s.src.isdigit() and os.path.exists(TK+'/profiles/%s.json'%s.src)) else None
        if getattr(a,'profile',None): os.environ['TK_PROFILE']=a.profile
        elif s.pr: os.environ['TK_PROFILE']=s.pr
        if not a.no_relax: drive.install_relax()
        from .evalincr import IncrEvaluator
        s.ev=IncrEvaluator(resync=a.resync,log=log)
        s.rng=random.Random(a.seed); s.run_id=a.run_id or 'plat-%s-s%d'%(s.src,a.seed)
        s.dir=PDIR+'/runs/'+s.run_id; os.makedirs(s.dir,exist_ok=True)
        s.classes=[c for c in a.classes.split(',') if c]
        s.plug={c:(prims.PLUGIN if c in('P1','P2','P3') else None if c=='P7' else M.plugin(c)) for c in s.classes}
        s.pools={}; s.stats={c:[0,0] for c in s.classes}; s.cpu0=cpu(); s.cpu_prev=0.0
        s.cnt=collections.Counter(); s.hist=[0]*64; s.visited=set(); s.canon_seen=set(); s.recent=[]
        s.step=0; s.t0=time.time()
    def used(s): return s.cpu_prev+cpu()-s.cpu0
    # ---------------- state
    def load_start(s):
        sp=s.dir+'/state.json'
        if os.path.exists(sp):
            st=json.load(open(sp)); s.cur=s.M.pin(s.tkc.load(s.dir+'/cur.json.gz')[1]); s.start=s.M.pin(s.tkc.load(s.dir+'/start.json.gz')[1])
            r=st['rng']; s.rng.setstate((r[0],tuple(r[1]),r[2])); s.cnt=collections.Counter(st['cnt']); s.hist=st['hist']; s.visited=set(st['visited']); s.canon_seen=set(st['canon_seen'])
            s.step=st['step']; s.cpu_prev=st['cpu']; s.k0=st['k0']; s.kstart=st['kstart']; s.hcur=st['hcur']; s.kcur=st['kcur']; s.base_events=st.get('base_events'); s.archive=st.get('archive',[])
            s.stats=st.get('stats') or s.stats; s.nrestart=st.get('nrestart',0); s.since_screen=st.get('since_screen',0); s.screen_wins=st.get('screen_wins',[]); s.since_full=st.get('since_full',0)
            log('RESUME %s step %d cpu %.0fs steps(accepted) %d kappa %.15f'%(s.run_id,s.step,s.cpu_prev,s.cnt['neutral'],s.kcur)); return
        p,w=s.tkc.load(s.src); w=s.M.pin(w); o=s.M.evaluate(w)
        if not o.get('legal'): raise SystemExit('start word illegal: %s'%o.get('why'))
        s.cur=s.start=w; s.k0=s.kstart=s.kcur=o['kappa']; s.hcur=s.canon.canon_hash(w); s.canon_seen={s.hcur}; s.visited={s.pk(w)}; s.archive=[]; s.nrestart=0; s.since_screen=0; s.since_full=0; s.screen_wins=[]
        json.dump(w,gzip.open(s.dir+'/start.json.gz','wt')); s.checkpoint(True)
        log('START %s (%s): kappa %.15f, %d events, canon %s'%(s.src,os.path.basename(p),s.kcur,len(w['program']),s.hcur[:12]))
    def checkpoint(s,force=False):
        if not force and time.time()-getattr(s,'_lastck',0)<60: return
        s._lastck=time.time(); json.dump(s.cur,gzip.open(s.dir+'/cur.json.gz.tmp','wt')); os.replace(s.dir+'/cur.json.gz.tmp',s.dir+'/cur.json.gz')
        stt=s.rng.getstate(); d=dict(rng=[stt[0],list(stt[1]),stt[2]],cnt=dict(s.cnt),hist=s.hist,visited=sorted(s.visited),canon_seen=sorted(s.canon_seen),step=s.step,cpu=s.used(),k0=s.k0,kstart=s.kstart,hcur=s.hcur,kcur=s.kcur,
                 base_events=getattr(s,'base_events',None),archive=s.archive,stats=s.stats,nrestart=s.nrestart,since_screen=s.since_screen,screen_wins=s.screen_wins,since_full=s.since_full)
        json.dump(d,open(s.dir+'/state.json.tmp','w')); os.replace(s.dir+'/state.json.tmp',s.dir+'/state.json')
    @staticmethod
    def pk(w):
        import hashlib
        return int.from_bytes(hashlib.blake2b(repr(w['program']).encode(),digest_size=7).digest(),'big')
    def dist(s,w,ref=None):
        """structural distance from the start word: size of the symmetric difference of the event multisets (invariant under pure commutation)"""
        A=collections.Counter(map(tuple,w['program'])); B=collections.Counter(map(tuple,(ref or s.start)['program']))
        return sum(((A-B)+(B-A)).values())
    # ---------------- candidates
    def build_pool(s,c,view):
        pl=s.plug[c]; cap=s.a.pool_cap; t=time.time(); L=[]
        if c=='P7':
            import prims_role as PR
            try: L=[dict(prim='P7',r=x['r'],plan=x['plan']) for x in PR.find_sites(view.w)]
            except Exception: L=[]
            s.rng.shuffle(L); s.pools[c]=dict(L=L,n0=s.cnt['neutral'],t=time.time()-t); return L
        if c=='P3': ctx=s.prims.PLUGIN.prepare(view); it=pl.sites(view,ctx,prims=('P3',))
        else: it=pl.sites(view,pl.prepare(view))
        for ed in it:
            L.append(ed)
            if len(L)>=cap: break
        s.rng.shuffle(L); s.pools[c]=dict(L=L,n0=s.cnt['neutral'],t=time.time()-t); return L
    def sample_sites(s,c,view,ctx,m):
        """up to m candidate edits of class c on view"""
        if c in WINDOWED:
            n=len(view.S); out=[]
            for _ in range(4):
                lo=s.rng.randrange(0,max(1,n-s.a.window)); hi=min(n,lo+s.a.window)
                L=list(s.prims.PLUGIN.sites(view,ctx,prims=(c,),window=(lo,hi)))
                if L: s.rng.shuffle(L); return [(ed,(lo,hi)) for ed in L[:m]]
            return []
        P=s.pools.get(c)
        if P is None or s.cnt['neutral']-P['n0']>=s.a.pool_refresh: P=dict(L=s.build_pool(c,view),n0=s.cnt['neutral']); s.pools[c]=dict(s.pools[c],n0=s.cnt['neutral'])
        L=s.pools[c]['L']
        if not L: return []
        return [(L[s.rng.randrange(len(L))],None) for _ in range(m)]
    def silent_pred(s,view,w2):
        """cheap prediction of 'canonical hash unchanged': the scalar program differs only by a permutation of a window and the header is the same (a strict commutation).  Validated against canon in --measure."""
        from .evalincr import _lcp,_lcs
        try:
            if w2['initial']!=view.w['initial'] or w2['final']!=view.w['final'] or w2['frames']!=view.w['frames']: return False
            A=view.S; B=[e for e in w2['program'] if e[0]!='MOVE']
            if len(A)!=len(B): return False
            n=len(A); i=_lcp(A,B,n); j=_lcs(A,B,n-i); wa=A[i:n-j]; wb=B[i:n-j]
            return collections.Counter(map(tuple,wa))==collections.Counter(map(tuple,wb))
        except TypeError: return False
    def apply(s,c,view,ed):
        if c=='P7':
            import prims_role as PR
            return PR.apply_retire(view.w,ed['r'],ed['plan'])
        return s.plug[c].apply(view,ed)
    def quick_k(s,c,view,ed):
        """trajectory-exact quick kappa or None (no quick price)"""
        pl=s.plug[c]
        if c=='P7': return 1.0
        try:
            if c in('P1','P2','P3'): return pl.fast(view,ed)
            if pl.quick: return s.M.quick(view,pl.scalars(view,ed))[0]
        except (ValueError,KeyError,AssertionError,IndexError,TypeError,ZeroDivisionError,s.prims.Block): return None
        return 1.0
    def exact(s,c,view,ed,base,skip_silent=False):
        try: w2=s.apply(c,view,ed)
        except (ValueError,KeyError,AssertionError,IndexError,TypeError,ZeroDivisionError,s.prims.Block): s.cnt['err_apply']+=1; return None,None
        if skip_silent and c in('P1','P2') and s.silent_pred(view,w2):
            if s.rng.random()>=s.a.p_silent: s.cnt['silent_skipped']+=1; return None,None
        if len(w2['initial'])!=len(base['initial']):      # register-adding / retiring edits: full path
            return w2,s.M.evaluate(w2)
        o=s.ev.evaluate(w2,ed,base=base); s.cnt['exact']+=1; return w2,o
    # ---------------- census
    def measure(s):
        """neutral census: per class n sampled sites -> quick-legal / exact-legal / neutral / improving / worse, and of the neutral ones how many are REAL (canon changes)"""
        s.load_start(); w=s.cur; view=s.M.View(w); ctx=s.prims.PLUGIN.prepare(view); k0=s.kcur; n=s.a.n; rows=[]
        for c in s.classes:
            t=time.time(); R=collections.Counter(); ex=[]
            if c in WINDOWED: cand=[]; tries=0
            if c in WINDOWED:
                m=len(view.S); allc=[]
                for _ in range(max(10,n//5)):
                    lo=s.rng.randrange(0,max(1,m-s.a.window)); allc+=[e for e in list(s.prims.PLUGIN.sites(view,ctx,prims=(c,),window=(lo,lo+s.a.window)))]
                s.rng.shuffle(allc); cand=allc[:n]; R['pool']=len(allc)
            else:
                L=s.build_pool(c,view); s.rng.shuffle(L); cand=L[:n]; R['pool']=len(L)
            R['sampled']=len(cand)
            for ed in cand:
                qk=s.quick_k(c,view,ed)
                if qk is None: R['quick_illegal']+=1; continue
                if qk<k0-0.5*k0 and qk!=1.0: R['quick_bad']+=1; continue
                w2,o=s.exact(c,view,ed,w)
                if w2 is None: R['apply_err']+=1; continue
                if not o.get('legal'): R['illegal']+=1; continue
                if not o.get('ok'): R['budget_bad']+=1; continue
                d=o['kappa']-k0
                if d>EPS: R['improving']+=1; ex.append((d,ed))
                elif d>=-EPS:
                    R['neutral']+=1
                    if R['neutral']<=s.a.canon_sample:
                        h=s.canon.canon_hash(w2); R['neutral_real' if h!=s.hcur else 'neutral_silent']+=1
                        if s.silent_pred(view,w2)!=(h==s.hcur): R['silent_pred_wrong']+=1
                else: R['worse']+=1
                if c=='P1' and abs(d)<=EPS: R['tag_'+('ends' if ed.get('ends') else 'f' if ed.get('f') is not None else 'fc' if ed.get('fc') is not None else 'plain')]+=1
            R['sec']=round(time.time()-t,1); rows.append((c,dict(R)))
            log('CENSUS %-9s %s'%(c,dict(R)))
            for d,ed in ex[:3]: log('  IMPROVING +%.3e %s'%(d,json.dumps(ed,default=str)[:160]))
        json.dump(dict(word=s.src,kappa=k0,rows=rows),open(s.dir+'/census.json','w'),indent=1)
        return 0
    # ---------------- the walk
    def edit_pos(s,ed,n):
        p=ed.get('i',ed.get('i0',ed.get('p',0)))
        try: return min(63,int(p)*64//max(1,n))
        except Exception: return 0
    def edit_win(s,ed):
        if 'g' in ed and 'i' in ed: return (min(ed['i'],ed['g']),max(ed['i'],ed['g']))
        if 'i0' in ed: return (ed['i0'],ed.get('i1',ed['i0']))
        if 'i' in ed: return (ed['i'],ed['i'])
        return None
    def adopt(s,w2,o,h,c,ed,real):
        n=len(s.cur['program']); s.cur=w2; s.kcur=o['kappa']; s.hcur=h; s.ev.adopt(w2); s.visited.add(s.pk(w2)); s.canon_seen.add(h)
        s.hist[s.edit_pos(ed,n)]+=1; s.cnt['neutral']+=1; s.cnt['real' if real else 'silent']+=1; s.cnt['cls_'+c]+=1
        s.since_screen+=1; s.since_full+=1
        for x in ((ed.get('i'),ed.get('g')) if 'g' in ed else (ed.get('i0'),ed.get('i1')) if 'i0' in ed else (ed.get('i'),)):
            if x is not None: s.screen_wins.append((x,x))
    def run(s):
        s.load_start(); a=s.a; budget=a.budget*3600; stats=s.stats; view=None; ctx=None; t_log=time.time()
        while s.used()<budget and (not a.max_steps or s.step<a.max_steps):
            s.step+=1
            if view is None or view.w is not s.cur:
                view=s.M.View(s.cur); ctx=s.prims.PLUGIN.prepare(view); self_dist=None
            cs=s.classes; wts=[(stats[c][1]+1.0)/(stats[c][0]+2.0)+0.02 for c in cs]; c=s.rng.choices(cs,wts)[0]
            cand=s.sample_sites(c,view,ctx,a.tries); stats[c][0]+=len(cand); got=[]
            for ed,_ in cand:
                qk=s.quick_k(c,view,ed)
                if qk is None: s.cnt['q_illegal']+=1; continue
                if qk!=1.0 and qk<s.k0-a.dip-QTOL: s.cnt['q_worse']+=1; continue
                w2,o=s.exact(c,view,ed,s.cur,skip_silent=True)
                if w2 is None and o is None: continue
                if w2 is None or not o.get('legal') or not o.get('ok'): s.cnt['x_illegal']+=1; continue
                d=o['kappa']-s.kcur
                if d>EPS and o['kappa']>s.k0+QTOL: s.improved(w2,o,'%s %s'%(c,json.dumps(ed,default=str)[:100])); view=None; got=[]; break
                if abs(d)<=EPS or o['kappa']>=s.k0-a.dip-EPS: got.append((s.hist[s.edit_pos(ed,len(view.S))],s.rng.random(),c,ed,w2,o))
            if not got: continue
            got.sort(key=lambda x:(x[0],x[1]))       # novelty: least-visited region of the program first
            for _,_,c2,ed,w2,o in got:
                pk=s.pk(w2)
                if pk in s.visited: s.cnt['cycle_exact']+=1; continue
                real=not s.silent_pred(view,w2)
                h=s.hcur
                s.adopt(w2,o,h,c2,ed,real); stats[c2][1]+=1
                if a.canon_every and s.cnt['neutral']%a.canon_every==0:
                    h2=s.canon.canon_hash(s.cur); s.cnt['canon']+=1
                    if h2 in s.canon_seen: s.cnt['cycle_canon']+=1
                    s.hcur=h2; s.canon_seen.add(h2)
                break
            if s.since_screen>=a.screen_every: s.local_screen(); view=None
            if a.full_every and s.since_full>=a.full_every: s.full_screen(); view=None
            if a.restart_every and s.cnt['neutral'] and s.cnt['neutral']%a.restart_every==0 and s.cnt['last_restart']!=s.cnt['neutral']: s.cnt['last_restart']=s.cnt['neutral']; s.restart(); view=None
            if time.time()-t_log>=60 or s.step%200==0:
                t_log=time.time(); s.checkpoint()
                log('step %d neutral %d (real %d silent %d) dist %d kappa %.15f canon %d cycl %d/%d exact %d cpu %.0fs cls %s'%(s.step,s.cnt['neutral'],s.cnt['real'],s.cnt['silent'],s.dist(s.cur),s.kcur,len(s.canon_seen),s.cnt['cycle_exact'],s.cnt['cycle_canon'],s.cnt['exact'],s.used(),{k[4:]:v for k,v in s.cnt.items() if k.startswith('cls_')}))
        s.checkpoint(True); log('DONE steps %d neutral %d (real %d) improving %d kappa %.15f (start %.15f) cpu %.0fs'%(s.step,s.cnt['neutral'],s.cnt['real'],s.cnt['improved'],s.kcur,s.kstart,s.used())); return 0
    def local_screen(s):
        """screens from the current point: P1/P2 levels in the windows the walk touched since the last screen (merged, <=6 windows)"""
        W=sorted(set(s.screen_wins)); s.screen_wins=[]; s.since_screen=0; s.cnt['screens']+=1
        if not W: return
        mer=[]
        for lo,hi in W:
            lo=max(0,lo-60); hi=hi+60
            if mer and lo<=mer[-1][1]+200 and hi-mer[-1][0]<=s.a.screen_span: mer[-1][1]=max(mer[-1][1],hi)
            else: mer.append([lo,hi])
        mer=sorted(mer,key=lambda x:x[0]-x[1])[:s.a.screen_windows]; t=time.time()
        for lo,hi in mer:
            try: res=s.prims.level(s.cur,('P1','P2'),window=(lo,hi),topq=12,log=None,tl=s.a.screen_wtl)
            except Exception as ex: s.cnt['screen_err']+=1; log('local screen error',repr(ex)[:120]); continue
            if res and res[0][0]>s.k0+QTOL: s.improved(res[0][1],dict(kappa=res[0][0],ok=True,legal=True),'localP1P2 %s'%json.dumps(res[0][2],default=str)[:100]); return
        s.cnt['screen_sec']+=int(time.time()-t); s.cnt['screen_w']+=len(mer)
    def full_screen(s):
        """the big screens from the current point, IN PROCESS (inherits --relax): pscreen.run_set(name, w, tl) per set; a crash of one set does not stop the walk"""
        s.since_full=0; s.cnt['fullscreens']+=1; import pscreen
        for name in [x for x in s.a.sets.split(',') if x]:
            t=time.time()
            try: w2,chain=pscreen.run_set(name,s.M.pin(s.cur),s.a.screen_tl,3)
            except BaseException as ex:
                if isinstance(ex,KeyboardInterrupt): raise
                s.cnt['fs_err_'+name]+=1; log('FULL screen %s failed: %r'%(name,ex)[:200]); continue
            o=s.M.evaluate(w2) if chain else None
            log('FULL screen %s (%.0fs): %d step(s)%s'%(name,time.time()-t,len(chain),' kappa %.15f'%o['kappa'] if o else '')); s.cnt['fs_'+name]+=1
            if o and o.get('legal') and o['kappa']>s.k0+QTOL: s.improved(w2,o,'pscreen '+name); return
    def restart(s):
        s.nrestart+=1; arch=s.dir+'/arch_%d.json.gz'%s.nrestart; json.dump(s.cur,gzip.open(arch,'wt')); s.archive.append(dict(file=arch,dist=s.dist(s.cur),canon=len(s.canon_seen),step=s.step))
        log('RESTART %d: dist %d from start, canon classes %d'%(s.nrestart,s.dist(s.cur),len(s.canon_seen)))
        s.cur=s.start; s.kcur=s.k0; s.hcur=s.canon.canon_hash(s.cur); s.ev.adopt(s.cur); s.visited.add(s.pk(s.cur)); s.screen_wins=[]
    def improved(s,w2,o,how):
        k=o['kappa']; s.cnt['improved']+=1; log('IMPROVING %.15f (+%.3e vs plateau %.15f, +%.3e vs start) via %s'%(k,k-s.kcur,s.kcur,k-s.kstart,how))
        if getattr(s.ev,'word',None) is w2:
            try: s.ev.check_sync()
            except RuntimeError as ex: log('RESYNC FAIL',ex); s.cnt['resync_fail']+=1; return
        full=s.M.evaluate(w2)
        if not full.get('legal') or abs(full['kappa']-k)>1e-13: log('  full evaluate disagrees: legal=%s kappa=%r -> discarded'%(full.get('legal'),full.get('kappa'))); s.cnt['improve_discard']+=1; return
        h=s.canon.canon_hash(w2); out=PDIR+'/CANDIDATE-%s.json.gz'%h[:12]
        if k>s.a.frontier or k>s.kstart+1e-12:
            os.makedirs(PDIR,exist_ok=True); json.dump(w2,gzip.open(out,'wt'))
            fb=os.environ.pop('TK_FREE_BOUNDS',None)      # the PR checker must run with the real inventory bounds
            try: res=s.drive.validate_file(out,os.environ.get('TK_PROFILE'))
            finally:
                if fb is not None: os.environ['TK_FREE_BOUNDS']=fb
            ok=res['accept_ok'] and res['native_ref']['ok']
            log('  %s %s kappa %.15f interval %s native_ref=%s'%('CANDIDATE-VALIDATED' if ok else 'UNCONFIRMED',h[:12],k,res.get('interval'),res['native_ref']))
            with open(PDIR+'/hits.jsonl','a') as f: f.write(json.dumps(dict(ts=time.time(),run=s.run_id,hash=h,kappa=k,how=how,ok=ok,file=out,res=res),default=str)+'\n')
            if not ok: return
        s.cur=s.start=w2; s.k0=s.kcur=k; s.hcur=h; s.visited={s.pk(w2)}; s.canon_seen={h}; s.ev.adopt(w2); s.screen_wins=[]; s.since_screen=0; json.dump(w2,gzip.open(s.dir+'/start.json.gz','wt')); s.checkpoint(True)

def measure_sets(s):
    """neutral census of the big screens: how many of their LEGAL outputs are exactly kappa-neutral (they usually return only improving moves, so this counts what the level functions expose)"""
    s.load_start(); M=s.M; w=M.pin(s.cur); k0=s.kcur; out={}
    def rec(name,res,t):
        ks=[r[0] for r in res]; n=len(ks); neu=sum(1 for k in ks if abs(k-k0)<=EPS); imp=sum(1 for k in ks if k>k0+EPS)
        out[name]=dict(legal_outputs=n,neutral=neu,improving=imp,best=max(ks) if ks else None,sec=round(t,1)); log('CENSUS-SET %-12s %s'%(name,out[name]))
    import prims_role as PR, prims_extra as PE, handover as H, prims_alias as PA
    t=time.time(); res=[]
    for st in PR.find_sites(w)[:40]:
        try: w2=PR.apply_retire(w,st['r'],st['plan'])
        except Exception: continue
        o=M.evaluate(w2)
        if o.get('legal'): res.append((o['kappa'],w2,st))
    rec('prims_role',res,time.time()-t)
    t=time.time()
    try: res=PE.level(w,('acc','ret'),topq=200,tl=s.a.screen_tl,WR=400,log=lambda *x:None)
    except Exception as ex: res=[]; log('prims_extra P8 failed',repr(ex)[:100])
    rec('prims_extra_P8',res,time.time()-t)
    t=time.time()
    try: res=H.level(w,tl=s.a.screen_tl,log=lambda *x:None)
    except Exception as ex: res=[]; log('handover failed',repr(ex)[:100])
    rec('handover',res,time.time()-t)
    t=time.time()
    try: b=PA.base(w); kb=M.evaluate(b)['kappa']; res=PA.level(b,tl=s.a.screen_tl,log=lambda *x:None); out['alias_base_kappa']=kb; log('alias base kappa %.15f (start %.15f)'%(kb,k0))
    except Exception as ex: res=[]; log('alias failed',repr(ex)[:100])
    rec('alias',res,time.time()-t)
    json.dump(out,open(s.dir+'/census_sets.json','w'),indent=1); return 0
def add_parsers(sp):
    p=sp.add_parser('plateau',help='neutral-network plateau walks + screens from each point (PLATEAU): tk plateau WORD [--measure] [--budget CPUH --seed S]')
    p.add_argument('src'); p.add_argument('--measure',action='store_true'); p.add_argument('--measure-sets',action='store_true'); p.add_argument('--n',type=int,default=300); p.add_argument('--canon-sample',type=int,default=40)
    p.add_argument('--classes',default=','.join(CLASSES)); p.add_argument('--budget',type=float,default=0.05,help='CPU hours'); p.add_argument('--seed',type=int,default=0); p.add_argument('--run-id')
    p.add_argument('--window',type=int,default=400); p.add_argument('--pool-cap',type=int,default=6000); p.add_argument('--pool-refresh',type=int,default=150); p.add_argument('--resync',type=int,default=200)
    p.add_argument('--no-relax',action='store_true'); p.add_argument('--frontier',type=float,default=0.0031241863); p.add_argument('--tries',type=int,default=6,help='candidates tried per step')
    p.add_argument('--canon-every',type=int,default=20,help='canonical hash of the walk position every N accepted steps (cycle statistics; the per-step visited test is the exact program hash)'); p.add_argument('--p-silent',type=float,default=0.05); p.add_argument('--dip',type=float,default=0.0,help='allow states down to plateau level minus dip (0 = strict plateau)')
    p.add_argument('--screen-every',type=int,default=100); p.add_argument('--full-every',type=int,default=0,help='run the pscreen sets every N accepted steps (0 = never)'); p.add_argument('--sets',default='prims_extra,handover,prims_role')
    p.add_argument('--screen-windows',type=int,default=3); p.add_argument('--screen-span',type=int,default=200); p.add_argument('--screen-wtl',type=float,default=20); p.add_argument('--screen-tl',type=float,default=120); p.add_argument('--restart-every',type=int,default=0,help='restart from the start word (or the most distant archived word) every N accepted steps'); p.add_argument('--max-steps',type=int,default=0)
    p.add_argument('--cpuq',help='write W/jobs/pending/NAME.sh running this walk (resumable)')
def main(a):
    os.environ.setdefault('TK_NATIVE_CORE','1'); os.environ.setdefault('TK_FREE_BOUNDS','1')      # search-driver entry only (never at import: tk.py imports wsearch for the parsers)
    if a.cpuq:
        argv=list(sys.argv[1:]); i=argv.index('--cpuq'); del argv[i:i+2]
        run_id=a.run_id or 'plat-%s-s%d'%(a.src,a.seed)
        if '--run-id' not in argv: argv+=['--run-id',run_id]
        sec=int(a.budget*3600*1.2+900); os.makedirs(PDIR+'/logs',exist_ok=True); pth=W+'/jobs/pending/%s.sh'%a.cpuq
        open(pth,'w').write('#!/bin/bash\n# timeout: %d\n# threads: 1\ncd %s\nTK_NATIVE_CORE=1 %s/python3 -B %s/tk.py %s >> %s/logs/%s.log 2>&1\necho "%s: tk plateau -> see %s/runs/%s" >> %s/the results log\n'%(sec,W,W,TK,' '.join(argv),PDIR,a.cpuq,a.cpuq,PDIR,run_id,W))
        os.chmod(pth,0o755); print('wrote',pth); return 0
    w=Walker(a)
    if a.measure: return w.measure()
    if a.measure_sets: return measure_sets(w)
    return w.run()
if __name__=='__main__':
    import argparse; ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd'); add_parsers(sp); a=ap.parse_args(['plateau']+sys.argv[1:]); sys.exit(main(a) or 0)
