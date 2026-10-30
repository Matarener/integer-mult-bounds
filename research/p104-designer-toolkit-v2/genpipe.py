"""genpipe -- one pipeline from a generated word (or a generator spec) to the best admissible word (GENPIPE.

  tk genpipe SPEC|WORD [--stages generate,p14,p15,p2p3,frames,compact,admit] [--budget CPUH] [--run-id ID] [--cpuq NAME] [--list]

Stages (all single core; each one is a function  stage(P, w, tl) -> new word or None):
  generate  SPEC (a synth spec file -> `tk synth --gen`, or an existing generator word) -> word.  A WORD input skips it.
  p14       P14 helper alias (prims_alias, pscreen 'alias'), judged against its own hybrid-frame base word
  p15       P15 source-reorder alias (prims_alias2): UNPRICED chunks (restart on the previous realised word) until a chunk accepts < --p15-min, then ONE priced final chunk
  p2p3      P2 (re-frame) + P3 (conjugation) polish (prims.greedy, windowed sweeps of the word; windows from --p2-windows)
  frames    frame re-assignment: REALISEFIX's frames.assign (exact-optimal frames, CP-SAT 1 thread) then the closure modes (hybrid / full) on the identity edit
  compact   synth.compact (moves, adds, cse, scale) -- value preserving event/scalar compaction
  admit     admit.best: best literals + admissibility record (never changes the word); words above --frontier are validated with `tk accept --native-ref`
Safety: every stage output must pass movekit.evaluate (exact legal + invoice) AND a fresh IncrWord (native pairs) with the same kappa, and must RAISE kappa by > 1e-15, else it is REVERTED
(the stage is logged as 'revert').  `tk check --native` (fastnative) is run on every accepted word that ends a stage when --native-every N allows (default every stage with a gain), and always on the final word.
Store (wsearch/store.py, ext/SEARCH/store.sqlite): words, evals (profile), lineage (parent -> child, edit = stage record: kappa before/after, helpers, events, admit flag), validations
('native'), checkpoints(run_id).  A rerun with the same --run-id resumes at the first unfinished stage (P15 resumes at its last finished chunk).
cpuq: --cpuq NAME writes W/jobs/pending/NAME.sh (resumable).   Per-stage record JSONL: ext/GENPIPE/runs/RUN/stages.jsonl"""
import sys,os,json,gzip,time,subprocess,hashlib
HERE=os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0,HERE)
W=os.path.dirname(os.path.abspath(__file__)); GDIR=W + '/ext/GENPIPE'
STAGES=('generate','p14','p15','p2p3','frames','compact','admit')
EPS=1e-15
FRONTIER=0.0031241863
def log(*a): print(time.strftime('%H:%M:%S'),*a,flush=True)
def cpu():
    t=os.times(); return t.user+t.system+t.children_user+t.children_system

# ------------------------------------------------------------------------------ exact verification
def evaluate(w):
    import movekit as M
    return M.evaluate(w)
def incr_check(w):
    """fresh IncrWord (chunked replay + native pairs): -> (legal, kappa float, nevents, helpers)"""
    import incr
    iw=incr.IncrWord(w)
    return bool(iw.legal_all),float(iw.kappa),len(w['program']),len(w['initial'])
def native_check(path,ref=False):
    """tk check --native (fastnative) in a subprocess; -> (ok, last output line)"""
    env=dict(os.environ); env.pop('TK_FREE_BOUNDS',None)
    cmd=[sys.executable,'-B',HERE+'/tk.py','check',path,'--native']+(['--native-ref'] if ref else [])
    env['TK_FREE_BOUNDS']=os.environ.get('TK_FREE_BOUNDS','1')
    p=subprocess.run(cmd,capture_output=True,text=True,env=env)
    out=(p.stdout+p.stderr).strip().splitlines()
    return p.returncode==0,(out[-1] if out else '')
def admit_rec(w):
    import admit as A
    try:
        b=A.best(w)
        return dict(admits_any=bool(b['admits_any']),strict_ok=bool(b['strict_ok']),blockers=b['blockers'],needs=b['needs'],changes={k:[str(x) for x in v] if isinstance(v,tuple) else str(v) for k,v in b['changes'].items()})
    except Exception as ex: return dict(error=repr(ex)[:200])

# ------------------------------------------------------------------------------ the pipeline object
class Pipe:
    def __init__(s,a):
        import movekit as M, tkcommon
        from wsearch import store,canon
        s.a=a; s.M=M; s.tkc=tkcommon; s.canon=canon
        s.store=store.Store(a.store)
        s.src=a.src; s.stages=[x for x in a.stages.split(',') if x]
        bad=[x for x in s.stages if x not in STAGES]
        if bad: raise SystemExit('unknown stages %s'%bad)
        s.run_id=a.run_id or 'gp-%s'%os.path.basename(a.src).replace('.json.gz','').replace('.json','')
        s.dir=GDIR+'/runs/'+s.run_id; os.makedirs(s.dir,exist_ok=True)
        s.budget=a.budget*3600.0; s.cpu_prev=0.0; s.cpu0=cpu(); s.rec=[]; s.done=0; s.cur=None; s.hcur=None; s.kcur=None; s.sub={}; s.nacc=0
    def used(s): return s.cpu_prev+cpu()-s.cpu0
    def left(s): return s.budget-s.used()
    def hash(s,w): return s.canon.canon_hash(w)
    def profile(s,w):
        try: return s.tkc.profile_of(w)[0]
        except SystemExit: return '?'
    # ---- store
    def put(s,w,o,parent,edit,cls,step):
        h=s.hash(w); s.store.put_word(h,w)
        s.store.add_eval(h,s.profile(w),o.get('legal'),o.get('kappa'),None,o.get('ok'),'fast',relaxed=not s.a.no_relax,side_ok=o.get('side_ok'))
        s.store.add_lineage(h,parent,edit,cls,0,s.run_id,step); return h
    def checkpoint(s):
        s.store.save_ck(s.run_id,dict(done=s.done,cur=s.hcur,kcur=s.kcur,sub=s.sub,rec=s.rec,cpu=s.used(),nacc=s.nacc,src=s.src,stages=s.stages))
    def start(s):
        ck=s.store.load_ck(s.run_id)
        if ck and ck.get('stages')==s.stages and ck.get('src')==s.src:
            s.done=ck['done']; s.hcur=ck['cur']; s.kcur=ck['kcur']; s.sub=ck.get('sub') or {}; s.rec=ck['rec']; s.cpu_prev=ck['cpu']; s.nacc=ck.get('nacc',0)
            s.cur=s.M.pin(s.store.get_word(s.hcur)) if s.hcur else None
            log('RESUME %s: stages done %d/%d, cur %s kappa %s, cpu %.0fs'%(s.run_id,s.done,len(s.stages),(s.hcur or '-')[:10],s.kcur,s.cpu_prev)); return
        if s.stages and s.stages[0]=='generate' and not s.is_word(s.src):
            return
        s.load_input()
    def is_word(s,src):
        try:
            p=s.tkc.resolve(src)
            if os.path.isdir(p): return False
            w=s.tkc.legal.load(p); return isinstance(w,dict) and 'program' in w
        except BaseException: return False
    def load_input(s):
        p,w=s.tkc.load(s.src); w=s.M.pin(w); o=evaluate(w)
        if not o.get('legal'): raise SystemExit('input word illegal: %s'%o.get('why'))
        ic=incr_check(w)
        if not ic[0]: raise SystemExit('input word fails IncrWord (native) check')
        s.cur=w; s.kcur=o['kappa']; s.hcur=s.put(w,o,None,dict(stage='input',src=s.src,path=p),'genpipe:input',0)
        r=dict(stage='input',kappa=o['kappa'],helpers=len(w['initial']),events=len(w['program']),ok=bool(o.get('ok')),legal=True,cpu=s.used(),hash=s.hcur)
        r['admissible']=admit_rec(w).get('strict_ok'); s.rec.append(r); s.emit(r)
        log('INPUT %s kappa %.15f helpers %d events %d ok %s admissible %s'%(s.src,o['kappa'],r['helpers'],r['events'],r['ok'],r['admissible']))
    def emit(s,r):
        with open(s.dir+'/stages.jsonl','a') as f: f.write(json.dumps(r,default=str)+'\n')
    # ---- one stage with the never-lose guard
    def verify(s,w2):
        """-> (ok, evaluate dict, why).  exact movekit.evaluate + fresh IncrWord (native pairs) must agree on legality and kappa"""
        o=evaluate(w2)
        if not o.get('legal'): return False,o,'illegal: %s'%(o.get('why'),)
        ic=incr_check(w2)
        if not ic[0]: return False,o,'IncrWord/native rejects'
        if abs(ic[1]-o['kappa'])>1e-13: return False,o,'IncrWord kappa %.15f != evaluate %.15f'%(ic[1],o['kappa'])
        return True,o,''
    def accept(s,name,w2,info,t0):
        """apply the guard; returns True if adopted"""
        r=dict(stage=name,kappa_before=s.kcur,helpers_before=len(s.cur['initial']),events_before=len(s.cur['program']),info=info)
        if w2 is None:
            r.update(action='noop',kappa=s.kcur,helpers=r['helpers_before'],events=r['events_before'])
        else:
            ok,o,why=s.verify(w2)
            r.update(kappa=o.get('kappa'),helpers=len(w2['initial']),events=len(w2['program']),verify=why or 'ok')
            if not ok: r.update(action='revert',reason=why,kappa=s.kcur)
            elif o['kappa']<s.kcur-EPS or (o['kappa']<=s.kcur+EPS and not (r['events']<r['events_before'] or r['helpers']<r['helpers_before'])): r.update(action='revert',reason='no gain (%+.3e)'%(o['kappa']-s.kcur),kappa_rejected=o['kappa'],kappa=s.kcur)
            else:
                r['action']='accept'; r['neutral']=o['kappa']<=s.kcur+EPS; s.nacc+=1
                if s.a.native_every and s.nacc%s.a.native_every==0:
                    p=s.dir+'/%s_%s.json.gz'%(name,s.nacc); json.dump(w2,gzip.open(p,'wt')); nok,line=native_check(p)
                    r['native']=dict(ok=nok,line=line)
                    if not nok: r.update(action='revert',reason='native check failed: '+line,kappa=s.kcur)
                if r['action']=='accept':
                    h=s.put(w2,o,s.hcur,dict(stage=name,kappa_before=s.kcur,kappa=o['kappa'],helpers=r['helpers'],events=r['events'],info=info),'genpipe:'+name,s.done+1)
                    if 'native' in r: s.store.add_validation(h,'native',r['native']['ok'],r['native'])
                    s.cur=s.M.pin(w2); s.hcur=h; s.kcur=o['kappa']; r['hash']=h
                    open(s.dir+'/cur.json.gz','wb').close(); json.dump(s.cur,gzip.open(s.dir+'/cur.json.gz','wt'))
        r['cpu']=s.used(); r['sec']=round(time.time()-t0,1); s.rec.append(r); s.emit(r)
        log('STAGE %-8s %s  kappa %.15f -> %.15f (%+.3e)  helpers %d->%d events %d->%d  %s'%(name,r['action'],r['kappa_before'],r.get('kappa',r['kappa_before']),(r.get('kappa',r['kappa_before'])-r['kappa_before']),r['helpers_before'],r['helpers'],r['events_before'],r['events'],r.get('reason','')))
        return r['action']=='accept'

# ------------------------------------------------------------------------------ the stages
def st_generate(P,w,tl):
    """SPEC -> word via `tk synth --gen SPEC --out F`; (input already a word: not reached)"""
    out=P.dir+'/generated.json.gz'
    cmd=[sys.executable,'-B',HERE+'/tk.py','synth','--gen',P.src,'--out',out]
    log('generate:',' '.join(cmd)); p=subprocess.run(cmd,capture_output=True,text=True)
    log((p.stdout+p.stderr)[-600:])
    if not os.path.exists(out): raise SystemExit('generate failed')
    return out
def _pick(byv,h):
    """alias_core.pick is missing from the toolkit copy (pscreen 'alias' died with NameError); ALIAS/greedy.py's definition"""
    rs=byv[h]; common=None
    for i,ok in rs.items():
        ks={x[0] for x in ok}; common=ks if common is None else common&ks
    return {i:sorted(ok,key=lambda x:(x[0] not in (common or ()),x[1]))[0] for i,ok in rs.items()}
def st_p14(P,w,tl):
    import prims_alias as PA, alias_core as A
    if not hasattr(A,'pick'): A.pick=_pick
    w2,chain=_pin_greedy_alias(PA,w,tl)
    return w2,dict(steps=len(chain))
def _pin_greedy_alias(PA,w,tl,steps=10):
    import pscreen
    return pscreen.run_set('alias',w,tl=tl,steps=steps)
def st_p15(P,w,tl):
    """unpriced chunks then one priced final chunk (module docstring best practice); every chunk is a resumable sub-state"""
    import prims_alias2 as PA2
    a=P.a; M=P.M
    ck=P.sub.get('p15') or dict(chunk=0,hash=None,priced=False)
    cur=w
    if ck['hash'] and ck['hash']!=P.hcur:
        cur=M.pin(P.store.get_word(ck['hash']))
    kprev=M.evaluate(cur)['kappa']; tstart=time.time(); info=dict(chunks=[])
    try:
        while True:
            if P.left()<30: info['stop']='budget'; break
            priced=ck['priced']; tl_c=min(a.p15_chunk,P.left()*0.9)
            t0=time.time()
            w3,rem,acc=PA2.run(cur,tl=tl_c,maxpass=1,judge=priced,log=lambda *x:None)
            n=len(acc)
            if w3 is None:
                info['chunks'].append(dict(n=0,priced=priced,sec=round(time.time()-t0)))
                log('  p15 chunk %d%s: accepted 0'%(ck['chunk'],' (priced)' if priced else ''));
                if priced: break
                ck['priced']=True; continue
            o=M.evaluate(w3)
            if not o.get('legal') or o['kappa']<=kprev+EPS and priced:
                info['chunks'].append(dict(n=n,priced=priced,legal=bool(o.get('legal')),kappa=o.get('kappa'),dropped=True,sec=round(time.time()-t0)))
                log('  p15 chunk %d%s: %d accepted but %s -> dropped'%(ck['chunk'],' (priced)' if priced else '',n,'no gain' if o.get('legal') else 'ILLEGAL'))
                if priced: break
                ck['priced']=True; continue            # unpriced chain ended illegal/worse: finish with a priced pass from the last good word
            if not priced and o['kappa']<=kprev+EPS:
                ck['priced']=True; info['chunks'].append(dict(n=n,priced=priced,kappa=o['kappa'],dropped=True)); continue
            cur=M.pin(w3); kprev=o['kappa']; ck['chunk']+=1
            info['chunks'].append(dict(n=n,priced=priced,kappa=o['kappa'],helpers=len(w3['initial']),sec=round(time.time()-t0)))
            log('  p15 chunk %d%s: +%d victims, kappa %.15f, helpers %d, %.0fs'%(ck['chunk'],' (priced)' if priced else '',n,o['kappa'],len(w3['initial']),time.time()-t0))
            h=P.hash(cur); P.store.put_word(h,cur); ck['hash']=h; P.sub['p15']=ck; P.checkpoint()      # resumable at chunk granularity
            if priced: break
            if n<a.p15_min: ck['priced']=True
    except Exception as ex:
        import traceback; traceback.print_exc(); info['error']=repr(ex)[:200]      # keep the last good chunk word
    P.sub.pop('p15',None)
    return (cur if cur is not w else None),info
def st_p2p3(P,w,tl):
    """P2/P3 generic rewrites: windowed greedy sweeps (module docstring: P2 reframe +0.24%); windows tile the program, each with tl share"""
    import prims
    M=P.M; a=P.a; wins=a.p2_windows; k0=M.evaluate(w)['kappa']; cur=w; kc=k0; info=dict(windows=[])
    n=len(M.View(M.pin(w)).S)            # windows index the View's scalar program S (not w['program'])
    span=max(1,n//wins); t_all=min(tl,P.left()*0.9); t0=time.time(); per=t_all/wins
    for i in range(wins):
        lo=i*span; hi=min(n,lo+span)
        if time.time()-t0>t_all: break
        n_cur=len(M.View(M.pin(cur)).S); lo=min(lo,n_cur); hi=min(hi,n_cur)
        if hi<=lo: break
        kk,w2,chain,st=prims.greedy(cur,('P2','P3'),steps=a.p2_steps,window=(lo,hi),tl=per,log=lambda *x:None)
        o=M.evaluate(w2) if chain else None
        info['windows'].append(dict(lo=lo,hi=hi,steps=len(chain),kappa=(o or {}).get('kappa')))
        if chain and o.get('legal') and o['kappa']>kc+EPS:
            cur=M.pin(w2); kc=o['kappa']
            log('  p2p3 window %d [%d,%d): %d steps, kappa %.15f'%(i,lo,hi,len(chain),kc))
    return (cur if kc>k0+EPS else None),info
def st_frames(P,w,tl):
    """frame re-assignment.  REALISEFIX's exact-optimal frame routine if landed (module realisefix), else the closure modes on the identity edit"""
    M=P.M; info=dict(tried=[])
    k0=M.evaluate(w)['kappa']; best=(k0,None,None)
    try:
        import frames as FR
        t=time.time(); w2,fi=FR.assign(w,tl=min(tl,P.a.frames_tl),K=2,maxm=0,threads=1)
        o=M.evaluate(w2) if w2 is not w else {}
        info['tried'].append(dict(mode='frames.assign',info={k:fi.get(k) for k in ('status','gain','kept','nodes','seconds')},kappa=o.get('kappa'),sec=round(time.time()-t)))
        if w2 is not w and o.get('legal') and o['kappa']>best[0]+EPS: best=(o['kappa'],w2,'frames.assign')
    except Exception as ex: info['tried'].append(dict(mode='frames.assign',error=repr(ex)[:200]))
    import alias_core as A
    for mode in ('hybrid',False):
        t=time.time()
        try:
            C=A.Ctx(M.pin(w)); w2,why=A.realise(C,[],{},minimal=mode)
            if w2 is None: info['tried'].append(dict(mode=str(mode),why=why)); continue
            o=M.evaluate(w2); info['tried'].append(dict(mode=str(mode),kappa=o.get('kappa'),legal=bool(o.get('legal')),sec=round(time.time()-t)))
            if o.get('legal') and o['kappa']>best[0]+EPS: best=(o['kappa'],w2,str(mode))
        except Exception as ex: info['tried'].append(dict(mode=str(mode),error=repr(ex)[:200]))
    info['best']=best[2]
    return best[1],info
def st_compact(P,w,tl):
    from synth import compact as C
    out=C.compact(w,verify=True); w2,st=out[0],out[1]
    return w2,dict(stats={k:v for k,v in (st.items() if isinstance(st,dict) else [])})
def st_admit(P,w,tl):
    rec=admit_rec(w); P.sub['admit']=rec; return None,rec

FNS=dict(generate=st_generate,p14=st_p14,p15=st_p15,p2p3=st_p2p3,frames=st_frames,compact=st_compact,admit=st_admit)

def run(a):
    os.environ.setdefault('TK_FREE_BOUNDS','1'); os.environ.setdefault('TK_NATIVE_CORE','1')      # search-driver entry only (never at import)
    import wsearch.drive as drive
    if not a.no_relax: drive.install_relax()
    P=Pipe(a); P.start()
    for i in range(P.done,len(P.stages)):
        name=P.stages[i]
        if name=='generate':
            if P.cur is None:
                out=st_generate(P,None,0); P.src=out; P.load_input()
            P.done=i+1; P.checkpoint(); continue
        if P.cur is None: P.load_input()
        if P.left()<=0: log('budget exhausted before',name); break
        t0=time.time(); log('--- stage',name,'(cpu left %.0fs)'%P.left())
        fn=FNS[name]
        if name=='admit':
            _,rec=fn(P,P.cur,0); r=dict(stage='admit',kappa=P.kcur,helpers=len(P.cur['initial']),events=len(P.cur['program']),admit=rec,admissible=rec.get('strict_ok'),admits_any=rec.get('admits_any'),cpu=P.used(),sec=round(time.time()-t0,1))
            P.rec.append(r); P.emit(r); P.store.add_validation(P.hcur,'admit',bool(rec.get('admits_any')),rec)
            log('ADMIT strict_ok=%s admits_any=%s blockers=%s needs=%s'%(rec.get('strict_ok'),rec.get('admits_any'),rec.get('blockers'),rec.get('needs')))
        else:
            try:
                res=fn(P,P.cur,min(a.stage_tl,max(30.0,P.left())))
                w2,info=res if isinstance(res,tuple) else (res,{})
            except Exception as ex:
                import traceback; traceback.print_exc(); w2,info=None,dict(error=repr(ex)[:300])
            P.accept(name,w2,info,t0)
        P.done=i+1; P.checkpoint()
    # ---- final
    out=P.dir+'/final.json.gz'; json.dump(P.cur,gzip.open(out,'wt'))
    nok,line=native_check(out); P.store.add_validation(P.hcur,'native',nok,dict(line=line))
    fin=dict(stage='final',kappa=P.kcur,helpers=len(P.cur['initial']),events=len(P.cur['program']),native_ok=nok,native=line,path=out,hash=P.hcur,cpu=P.used())
    P.rec.append(fin); P.emit(fin); P.checkpoint()
    log('FINAL %s kappa %.15f helpers %d events %d native %s'%(out,P.kcur,fin['helpers'],fin['events'],nok))
    first=next((r for r in P.rec if r['stage']=='input'),None)
    if first: log('TOTAL gain %+.3e (%+.2f%%) over input %.15f'%(P.kcur-first['kappa'],100*(P.kcur/first['kappa']-1),first['kappa']))
    if P.kcur>a.frontier and nok:
        log('ABOVE FRONTIER %.15f: validating tk accept --native-ref'%P.kcur)
        p=subprocess.run([sys.executable,'-B',HERE+'/tk.py','accept',out,'--native-ref'],capture_output=True,text=True)
        log((p.stdout+p.stderr)[-1500:])
        cand=GDIR+'/CANDIDATE-%s.json.gz'%P.hcur[:12]; json.dump(P.cur,gzip.open(cand,'wt')); log('CANDIDATE',cand)
    return 0

def add_parsers(sp):
    p=sp.add_parser('genpipe',help='generator pipeline: generate -> P14 -> P15 -> P2/P3 -> frames -> compact -> admit, never-lose stages, store lineage, resumable (genpipe.py docstring)')
    p.add_argument('src',help='generator SPEC file or WORD alias/path'); p.add_argument('--stages',default='generate,p14,p15,p2p3,frames,compact,admit')
    p.add_argument('--budget',type=float,default=1.0,help='CPU hours for the whole pipeline'); p.add_argument('--stage-tl',type=float,default=1800,help='time limit seconds of one stage (p15: per stage total)')
    p.add_argument('--run-id'); p.add_argument('--store'); p.add_argument('--frontier',type=float,default=FRONTIER); p.add_argument('--no-relax',action='store_true',help='do not relax the public-inventory/side checks (default: relaxed like tk search for generated words)')
    p.add_argument('--native-every',type=int,default=1,help='run tk check --native on every Nth accepted stage word (0 = final only)')
    p.add_argument('--p15-chunk',type=float,default=250,help='seconds per P15 chunk'); p.add_argument('--p15-min',type=int,default=3,help='switch to the priced final chunk when an unpriced chunk accepts fewer victims')
    p.add_argument('--frames-tl',type=float,default=1200,help='CP-SAT seconds for frames.assign (1 thread)'); p.add_argument('--p2-windows',type=int,default=6); p.add_argument('--p2-steps',type=int,default=8)
    p.add_argument('--cpuq',help='write W/jobs/pending/NAME.sh running this pipeline (resumable)')
def main(a):
    if a.cpuq:
        argv=list(sys.argv[1:]); i=argv.index('--cpuq'); del argv[i:i+2]
        run_id=a.run_id or 'gp-%s'%os.path.basename(a.src).replace('.json.gz','').replace('.json','')
        if '--run-id' not in argv: argv+=['--run-id',run_id]
        sec=int(a.budget*3600*1.3+1800); os.makedirs(GDIR+'/logs',exist_ok=True); pth=W+'/jobs/pending/%s.sh'%a.cpuq
        open(pth,'w').write('#!/bin/bash\n# timeout: %d\n# threads: 1\ncd %s\nTK_NATIVE_CORE=1 %s/python3 -B %s/tk.py %s >> %s/logs/%s.log 2>&1\necho "%s: tk genpipe -> %s/runs/%s" >> %s/the results log\n'%(sec,W,W,HERE,' '.join(argv),GDIR,a.cpuq,a.cpuq,GDIR,run_id,W))
        os.chmod(pth,0o755); print('wrote',pth); return 0
    return run(a)
