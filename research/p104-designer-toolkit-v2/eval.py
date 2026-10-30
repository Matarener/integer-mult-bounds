"""tk eval WORD... [--jobs N] [--out DIR] [--summary] [--force] [--no-pipeline] [--screens LIST] [--rounds N] [--k K --maxm M --tl S] [--accept full|fast|none]

Bulk evaluator: one command per word.  Per word (each in its own worker process, so a crash/timeout becomes an error record):
  1. legality: `check` (all localised violations) + native pair check (cached across words);
  2. acceptance: the REAL price.run (accept.py), cross-checked against the fast exact price (crossing interval must agree);
  3. exact price (kappa_before);
  4. improvement pipeline: screens run in order and repeat until a full round gains nothing (fixed point) or --rounds is exhausted.
     Every screen output is re-checked (legal + native + accept) and adopted only if legal, accepted and kappa >= current;
  5. a JSON record  OUT/records/NAME.json  (legality, kappa before/after, moves applied, seconds, errors); best word OUT/words/NAME.best.json.gz.
Deterministic (fixed solver params; single thread unless HEAVY_THREADS) and resumable: finished records are skipped, every screen output is cached in OUT/work/NAME/.
`--summary` prints a table sorted by final kappa.   SCREENS is the pluggable screen registry (name -> function); register more with eval.register(name, fn)."""
import sys,os,json,gzip,time,subprocess,shutil,traceback,hashlib
sys.dont_write_bytecode=True
from tkcommon import *
DEFAULT_OUT=OUT+'/eval'
EPS=1e-15
SCREENS={}                  # name -> fn(ctx, cur_path, outbase) -> (new_path_or_None, info_dict)
def register(name,fn): SCREENS[name]=fn
def wname(spec):
    if spec in ALIASES: return spec
    p=os.path.abspath(spec); b=os.path.basename(p).split('.')[0]; return '%s_%s'%(b,hashlib.sha256(p.encode()).hexdigest()[:6])
def kap(path):
    """-> (legal, kappa Decimal-string or None, price.fast dict)"""
    import price as PR
    w=legal.load(path); o=PR.fast(path,w,use_cache=True)
    return o['legal'],(o['kappa'] if o['legal'] else None),o
def nmoves(path): return sum(1 for e in legal.load(path)['program'] if e[0]=='MOVE')
# ---- screens (each runs as a subprocess of tk.py --inline: crash isolation + determinism; cwd-independent)
def _run(argv,logf,tl,ctx,threads=None):
    th=threads or ctx['threads']; env=dict(os.environ,HEAVY_THREADS=str(th),THREADS=str(th),PYTHONHASHSEED='0')
    with open(logf,'w') as f: return subprocess.run([PY,'-B',HERE+'/tk.py']+argv,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=tl+600).returncode
def screen_handoff(ctx,cur,base):
    o=base+'.json.gz'; cands=base+'.cands.json'
    big=len(legal.load(cur)['program'])>=8000      # GEN2POLISH: exact screen is ~2 h on a 20k-event word (14400 S + 14400 C candidates x 0.23 s) per round -> positive-only incremental prefilter
    rc=_run(['handoff',cur,'--apply','--inline','--tl',str(ctx['tl']),'--out',cands]+(['--fast'] if big else []),base+'.log',ctx['tl'],ctx)
    a=cands+'.applied.json.gz'
    if os.path.exists(a): shutil.copy(a,o); return o,dict(rc=rc)
    return None,dict(rc=rc,note='no applied word (no positive hand-off, or error)')
def screen_evretime(ctx,cur,base):
    o=base+'.json.gz'
    rc=_run(['evretime',cur,'--k',str(ctx['k']),'--maxm',str(ctx['maxm']),'--tl',str(ctx['tl']),'--inline','--out',o],base+'.log',ctx['tl'],ctx,threads=ctx['ev_threads'])
    return (o if os.path.exists(o) else None),dict(rc=rc)
def screen_retime(ctx,cur,base):
    if legal.is_prepared(legal.load(cur)): return None,dict(note='retime is not prepared573-aware; skipped')
    if legal.nown(legal.load(cur))!=8 and os.environ.get('TK_RETIME_ANYOWNED')!='1': return None,dict(note='retime is not owned_fields-aware; skipped (LEVERBANK: TK_RETIME_ANYOWNED=1 runs it anyway; its output is legal-checked and exactly re-priced, so a bad model result is rejected; whether the CP-SAT model prices owned staging correctly is unverified; one own-lever word: +8.0e-6, legal)')
    o=base+'.json.gz'
    rc=_run(['retime',cur,'--free','starts,finals,stops','--tl',str(ctx['tl']),'--inline','--out',o],base+'.log',ctx['tl'],ctx)
    return (o if os.path.exists(o) else None),dict(rc=rc)
def screen_reorder(ctx,cur,base):
    o=base+'.json.gz'
    rc=_run(['reorder',cur,'--k',str(ctx['k']),'--maxm',str(ctx['maxm']),'--tl',str(ctx['tl']),'--inline','--out',o],base+'.log',ctx['tl'],ctx,threads=ctx['ev_threads'])
    return (o if os.path.exists(o) else None),dict(rc=rc)
def screen_split(ctx,cur,base):
    o=base+'.json.gz'
    rc=_run(['split',cur,'--apply','--out',o],base+'.log',ctx['tl'],ctx)
    return (o if os.path.exists(o) else None),dict(rc=rc)
register('handoff',screen_handoff); register('evretime',screen_evretime); register('retime',screen_retime); register('reorder',screen_reorder); register('split',screen_split)   # FRONTAUTO: reorder + split screens
DEFAULT_SCREENS=['handoff','evretime','retime']
# ---- one word
def verify(path,mode,native_only_ok=True):
    """legality + native + acceptance of a word.  -> dict(legal, native_bad, accept{...}, kappa, ok)"""
    import check as CK, accept as AC, price as PR
    w=legal.load(path); activate(w); rep=legal.check(w,maxviol=20); v=dict(legal=rep['ok'])
    if not rep['ok']:
        v['violations']=[(i,r,str(d)[:120]) for i,r,d in rep['violations'][:5]]; v['ok']=False; return v
    o=PR.fast(path,w,use_cache=True); v['kappa']=o['kappa']; v['crossing_lo']=o['crossing_lo']; v['crossing_hi']=o['crossing_hi']
    v['side_ok']=o['side']['ok']
    try:      # GENBUDGET: exact profile-literal admissibility (tail with the PR's own c,b,u,D; event/scalar/inventory); replaces the c=17,b=18,u=.2 legacy side test for adopted data profiles
        import admit as AD
        if profile_of(w)[0] in DATA_PROFILES:
            ad=AD.check(w); v['admit_ok']=ad['ok']; v['admit_fail']=[x['name'] for x in ad['constraints'] if not x['ok']]
            v['side_ok_legacy']=v['side_ok']; v['side_ok']=all(x['ok'] for x in ad['constraints'] if x['name'] in('alpha<1-eps','gamma<D','delta<D','D^(v/8)<1/16','theorem tail <1','field cap (sum T)'))
            if not v['side_ok'] and os.environ.get('TK_FREE_BOUNDS')=='1':      # B0POLISH: generated words need new-value literals (tail c,b,u etc.); user opted in via TK_FREE_BOUNDS => side test = admissible at the best free literals
                bt=AD.best(w); v['side_ok']=bool(bt.get('admits_any')) and not bt.get('blockers'); v['free_literals']=dict(changes={k:str(x) for k,x in bt.get('changes',{}).items()},blockers=bt.get('blockers'))
    except Exception as ex: v['admit_error']=str(ex)[:120]
    v['event_slack']=o['budgets']['event_slack']; v['scalar_slack']=o['budgets']['scalar_budget_slack']
    w_prof=profile_of(w)[0]; v['profile']=w_prof
    if mode=='full' and not profile_of(w)[1]['real_stack']: mode='fast'; v['accept_kind']='fast (profile %s: own verifier)'%w_prof
    if mode=='full':
        a=AC.accept(path,w); v['accept']=a
        v['accept_ok']=a['ok']
        # cross-check: real price.run crossing interval == fast exact price interval (14 d.p.)
        import decimal as _d; D=_d.Decimal; v['crosscheck']=bool(a['ok'] and D(a['crossing_lo'])==D(o['crossing_lo']) and D(a['crossing_hi'])==D(o['crossing_hi']))
        v['native_bad']=0 if a['ok'] or (a.get('stage') not in('native',)) else 1
        v['ok']=bool(a['ok'] and v['crosscheck'] and v['side_ok'])
    else:
        nb=AC.native_pairs(w); v['native_bad']=len(nb['bad']); v['native_pairs']=nb['distinct']
        D=__import__('decimal').Decimal; v['crosscheck']=None
        v['ok']=bool(v['native_bad']==0 and v['side_ok'] and v['event_slack']>=0 and v['scalar_slack']>=0)
    return v
def evaluate(spec,out,cfg):
    """in-process evaluation of one word -> record dict (written by the caller)"""
    t0=time.time(); name=wname(spec); rec=dict(word=spec,name=name,status='running',config=cfg,steps=[],errors=[])
    work='%s/work/%s/%s'%(out,name,hashlib.sha256(json.dumps([cfg['screens'],cfg['k'],cfg['maxm'],cfg['tl'],cfg['threads'],cfg['ev_threads']]).encode()).hexdigest()[:8]); os.makedirs(work,exist_ok=True); os.makedirs(out+'/words',exist_ok=True); os.makedirs(out+'/records',exist_ok=True)
    try:
        path=resolve(spec); rec['sha']=sha(path)[:16]; w=legal.load(path); rec['public']=len(w['initial']); rec['events']=len(w['program'])
        v0=verify(path,cfg['accept']); rec['initial']=v0; rec['legal']=v0['legal']
        if not v0['legal']: rec['status']='illegal'; rec['kappa_before']=rec['kappa_after']=None; return rec
        rec['kappa_before']=v0['kappa']; rec['accepted_before']=v0.get('ok')
        if not v0['ok']: rec['errors'].append('initial word not accepted: %s'%(v0.get('accept',{}).get('error') or ('side/native/crosscheck failed')))
        exp=EXPECT.get(spec)
        if exp:
            import price as PR; rec['expected']=exp; rec['expected_match']=PR.matches(exp,dict(kappa=v0['kappa'],crossing_lo=v0['crossing_lo'],crossing_hi=v0['crossing_hi']))
        cur=path; kcur=float(v0['kappa']); moves=[]
        if cfg['pipeline'] and v0['ok']:
            screens=cfg['screens']; ctx=dict(threads=cfg['threads'],ev_threads=cfg['ev_threads'],tl=cfg['tl'],k=cfg['k'],maxm=cfg['maxm'])
            for rd in range(cfg['rounds']):
                k_start=kcur
                for sn in screens:
                    if sn not in SCREENS: rec['errors'].append('unknown screen '+sn); continue
                    base='%s/r%d_%s'%(work,rd,sn); ts=time.time(); st=dict(round=rd,screen=sn)
                    try:
                        cached=os.path.exists(base+'.done')
                        if cached: newp=json.load(open(base+'.done')).get('path'); info=dict(cached=True)
                        else:
                            newp,info=SCREENS[sn](ctx,cur,base)
                            json.dump(dict(path=newp),open(base+'.done','w'))
                        st['info']=info
                        if newp is None or not os.path.exists(newp): st['result']='no output'
                        else:
                            v=verify(newp,cfg['accept'] if cfg['accept_each'] else 'fast'); kn=float(v['kappa']) if v.get('kappa') else None
                            st['kappa']=v.get('kappa'); st['legal']=v['legal']; st['ok']=v.get('ok')
                            if not v['legal']: st['result']='REJECTED illegal'
                            elif not v['ok']: st['result']='REJECTED check/accept: %s'%(v.get('accept',{}).get('error') or 'side/native')
                            elif kn>=kcur-EPS:
                                gain=kn-kcur; mv_before=nmoves(cur); mv_after=nmoves(newp)
                                st['result']='adopted'; st['gain']=gain; st['moves_delta']=mv_after-mv_before
                                moves.append(dict(round=rd,screen=sn,gain=gain,kappa=v['kappa'],moves_delta=mv_after-mv_before))
                                cur,kcur=newp,kn
                            else: st['result']='REJECTED lower kappa (%.3e)'%(kn-kcur)
                    except Exception as e:
                        st['result']='ERROR'; st['error']=''.join(traceback.format_exception_only(type(e),e)).strip()[:300]; rec['errors'].append('%s r%d: %s'%(sn,rd,st['error']))
                    st['seconds']=round(time.time()-ts,1); rec['steps'].append(st)
                    json.dump(rec,open('%s/records/%s.partial.json'%(out,name),'w'),indent=1,default=str) if os.path.isdir(out+'/records') else None
                if kcur<=k_start+EPS: rec['fixed_point']=True; break
            else: rec['fixed_point']=False
        rec['moves_applied']=[m for m in moves if m['gain']>EPS]; rec['steps_adopted']=len(moves)
        best=out+'/words/%s.best.json.gz'%name
        if cur!=path: shutil.copy(cur,best)
        else: shutil.copy(path,best)
        vf=verify(best,cfg['accept']) if cur!=path else v0
        if cur!=path: rec['final']=vf
        rec['kappa_after']=vf['kappa']; rec['accepted_after']=vf.get('ok'); rec['best_word']=best
        rec['status']='done'
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        rec['status']='error'; rec['errors'].append(''.join(traceback.format_exception_only(type(e),e)).strip()[:400]); rec['traceback']=traceback.format_exc()[-1500:]
    finally: rec['seconds']=round(time.time()-t0,1)
    return rec
def write_rec(out,rec):
    d=out+'/records'; os.makedirs(d,exist_ok=True); f='%s/%s.json'%(d,rec['name']); json.dump(rec,open(f+'.tmp','w'),indent=1,default=str); os.replace(f+'.tmp',f)
    p='%s/%s.partial.json'%(d,rec['name'])
    if os.path.exists(p): os.remove(p)
def cfg_of(a):
    return dict(accept=a.accept,pipeline=not a.no_pipeline,screens=[s for s in a.screens.split(',') if s],rounds=a.rounds,k=a.k,maxm=a.maxm,tl=a.tl,threads=a.threads,ev_threads=a.ev_threads or a.threads,accept_each=not a.no_accept_each)
def rec_ok(out,name,cfg):
    f='%s/records/%s.json'%(out,name)
    if not os.path.exists(f): return None
    try: r=json.load(open(f))
    except Exception: return None
    return r if r.get('status') in('done','illegal') and r.get('config')==cfg else None
def post(a,rec):
    """results line + CANDIDATE export (pipeline-improved word above the threshold, legal and accepted)"""
    try:
        if a.results:
            os.makedirs(os.path.dirname(os.path.abspath(a.results)),exist_ok=True)
            open(a.results,'a').write(json.dumps(dict(word=rec['name'],status=rec['status'],legal=rec.get('legal'),kappa_before=rec.get('kappa_before'),kappa_after=rec.get('kappa_after'),accepted=rec.get('accepted_after'),steps=rec.get('steps_adopted'),seconds=rec.get('seconds'),errors=rec.get('errors')))+'\n')
        if a.candidates and rec['status']=='done' and rec.get('accepted_after') and float(rec['kappa_after'])>float(a.threshold) and float(rec['kappa_after'])>float(rec['kappa_before'])+EPS:
            os.makedirs(a.candidates,exist_ok=True); c='%s/CANDIDATE-%s.json.gz'%(a.candidates,rec['name']); shutil.copy(rec['best_word'],c)
            for sub in('price','check'):
                r=subprocess.run([PY,'-B',HERE+'/tk.py',sub,c]+(['--native'] if sub=='check' else []),capture_output=True,text=True); open(c+'.'+sub+'.txt','w').write(r.stdout+r.stderr)
            print('CANDIDATE %s kappa %s -> %s'%(rec['name'],rec['kappa_after'],c),flush=True)
    except Exception as e: print('post() failed: %r'%e,flush=True)
def worker_cmd(spec,out,a):
    return [PY,'-B',HERE+'/tk.py','eval','--worker',spec,'--out',out,'--accept',a.accept,'--screens',a.screens,'--rounds',str(a.rounds),'--k',str(a.k),'--maxm',str(a.maxm),'--tl',str(a.tl),'--threads',str(a.threads)]+(['--ev-threads',str(a.ev_threads)] if a.ev_threads else [])+(['--no-pipeline'] if a.no_pipeline else [])+(['--candidates',a.candidates] if a.candidates else [])+['--threshold',a.threshold]+(['--results',a.results] if a.results else [])+(['--no-accept-each'] if a.no_accept_each else [])
def summary(out,names=None):
    import glob
    rows=[]
    for f in sorted(glob.glob(out+'/records/*.json')):
        if f.endswith('.partial.json'): continue
        try: r=json.load(open(f))
        except Exception: continue
        if names is not None and r.get('name') not in names: continue
        rows.append(r)
    def kf(r):
        try: return float(r.get('kappa_after') or 0)
        except Exception: return 0
    rows.sort(key=lambda r:-kf(r))
    L=['%-16s %-8s %-6s %-6s %-17s %-17s %-10s %-5s %-7s %s'%('word','status','legal','accept','kappa_before','kappa_after','gain','steps','secs','errors/notes')]
    for r in rows:
        kb,ka=r.get('kappa_before'),r.get('kappa_after'); g=(float(ka)-float(kb)) if kb and ka else None
        note=('; '.join(r['errors'])[:70] if r.get('errors') else '')+('' if r.get('expected_match') in(None,True) else ' EXPECT-MISMATCH')
        L.append('%-16s %-8s %-6s %-6s %-17s %-17s %-10s %-5s %-7s %s'%(r['name'][:16],r['status'],'Y' if r.get('legal') else 'N','Y' if r.get('accepted_after') else ('N' if r.get('accepted_after') is False else '-'),(kb or '-')[:17],(ka or '-')[:17],('%+.3e'%g) if g is not None else '-',r.get('steps_adopted','-'),r.get('seconds','-'),note))
    return '\n'.join(L)
def main(a):
    out=os.path.abspath(a.out or DEFAULT_OUT); os.makedirs(out,exist_ok=True); cfg=cfg_of(a)
    if a.worker:
        rec=evaluate(a.worker,out,cfg); write_rec(out,rec); post(a,rec); print('%s: %s kappa %s -> %s (%.0fs)'%(rec['name'],rec['status'],rec.get('kappa_before'),rec.get('kappa_after'),rec['seconds'])); return 0
    names=[wname(x) for x in a.words]
    if a.summary and not a.words: print(summary(out)); return 0
    todo=[]
    for spec in a.words:
        n=wname(spec)
        if not a.force and rec_ok(out,n,cfg): print('skip %s (record exists)'%n); continue
        todo.append(spec)
    from concurrent.futures import ThreadPoolExecutor
    tmo=a.word_timeout
    def go(spec):
        n=wname(spec); t=time.time()
        try:
            r=subprocess.run(worker_cmd(spec,out,a),capture_output=True,text=True,timeout=tmo,env=dict(os.environ,PYTHONHASHSEED='0'))
            if rec_ok(out,n,cfg) is None and not os.path.exists('%s/records/%s.json'%(out,n)) :
                write_rec(out,dict(word=spec,name=n,status='error',config=cfg,errors=['worker rc=%d: %s'%(r.returncode,(r.stderr or r.stdout)[-400:])],seconds=round(time.time()-t,1)))
            elif r.returncode!=0:
                pass
            return r.stdout.strip().splitlines()[-1:] or ['%s: rc=%d'%(n,r.returncode)]
        except subprocess.TimeoutExpired:
            write_rec(out,dict(word=spec,name=n,status='error',config=cfg,errors=['word timeout %ds'%tmo],seconds=round(time.time()-t,1))); return ['%s: TIMEOUT'%n]
        except BaseException as e:
            write_rec(out,dict(word=spec,name=n,status='error',config=cfg,errors=[repr(e)[:300]],seconds=round(time.time()-t,1))); return ['%s: ERROR %r'%(n,e)]
    with ThreadPoolExecutor(max_workers=max(1,a.jobs)) as ex:
        for res in ex.map(go,todo): print(*res,flush=True)
    s=summary(out,set(names)); print(s)
    if a.summary or True: open(out+'/SUMMARY.txt','w').write(summary(out)+'\n')
    return 0
