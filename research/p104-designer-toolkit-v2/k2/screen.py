"""k2.screen -- the `k2sa` screen: s2s event compaction + bounded multi-seed k2net SA + exact validation (+ `tk accept --native-ref` on a gain).  Scope [toolkit, unified k2net search engine + automation].
Registered as pscreen set 'k2sa' (so `tk pscreen WORD --set k2sa`, `tk eval --screens ...,k2sa`, FRONTAUTO SCREENS, tests/screen_smoke.py all run it).
run(w, tl, steps, window, topq, log, seeds, native_ref) -> (word, chain).  Returns the INPUT word and an empty chain when nothing better (and nothing illegal) was found; the compacted word is only
returned together with a gain (s2s compaction is kappa-neutral; it only frees events, so it is an internal pre-pass).  No side effects at import."""
import os,sys,json,gzip,time,subprocess,tempfile,shutil
HERE=os.path.dirname(os.path.abspath(__file__)); TK=os.path.dirname(HERE)
for p in (TK,os.path.join(TK,'synth')):
    if p not in sys.path: sys.path.insert(0,p)
RECIPE=dict(t0=0.3,t1=0.01,peel=2,cap=26000,evpen=1.0,evt=23000,
            weights=dict(shift=1,mshift=.5,ret=1,cadd=.5,cdel=1,kill=3,ins=.3,split=0,rehost=3,hop=1.5))
def _log(*a): print(*a,flush=True)
def compact(w,log=_log):
    """exact s2s window re-synthesis of the whole word (kappa-neutral, frees events: the 26000 cap starves the SA otherwise).  -> (word, info)"""
    import s2s,movekit
    from incr import IncrWord
    t=time.time(); iw=IncrWord(movekit.pin(w)); w0=iw.to_word(); edit,st=s2s.resynth(w0)
    if not edit: return w,dict(compacted=False,events=len(w['program']),seconds=round(time.time()-t,1))
    r=iw.try_edit(edit)
    if not r.legal: return w,dict(compacted=False,why='try_edit '+str(r.reason)[:100],events=len(w['program']))
    w1=s2s.apply(w0,edit); log('  s2s: %d -> %d events (%.1fs, dk %s)'%(len(w['program']),len(w1['program']),time.time()-t,r.dk))
    return w1,dict(compacted=True,events_before=len(w['program']),events=len(w1['program']),seconds=round(time.time()-t,1))
def native_accept(path,timeout=1200,log=_log):
    r=subprocess.run([sys.executable,'-B',os.path.join(TK,'tk.py'),'accept',path,'--native-ref','--json'],capture_output=True,text=True,timeout=timeout)
    try: j=json.loads(r.stdout[r.stdout.index('{'):])
    except Exception: return dict(ok=False,error='unparseable: '+(r.stdout+r.stderr)[-300:])
    return dict(ok=bool(j.get('ok')),error=j.get('error'),crossing_lo=j.get('crossing_lo'),crossing_hi=j.get('crossing_hi'),native_pairs=j.get('native_pairs'))
def inventory_only(na):
    """True when a `tk accept --native-ref` refusal is ONLY the public/owned inventory literal (a package convention, not a rule)."""
    return (not na.get('ok')) and 'inventory bound' in str(na.get('error','')).lower()
def native_check_free(path,timeout=1800):
    """GEN2POLISH review of the convention fallback: `tk check --native` under TK_FREE_BOUNDS=1 (env for the child only).  Judged by the exit code (0 iff legal AND 0 bad native pairs) AND the printed
    verdict lines; a bare substring test 'LEGAL' in stdout also matches 'ILLEGAL'."""
    import re
    c=subprocess.run([sys.executable,'-B',os.path.join(TK,'tk.py'),'check',path,'--native'],capture_output=True,text=True,timeout=timeout,env=dict(os.environ,TK_FREE_BOUNDS='1'))
    return c.returncode==0 and re.search(r': LEGAL \(',c.stdout) is not None and re.search(r'\b0 bad\b',c.stdout) is not None and 'ILLEGAL' not in c.stdout
def run(w,tl=60,steps=1,window=None,topq=None,log=_log,seeds=(1,2),native_ref=True,compact_first=True,recipe=None,eps=1e-13,keep=None,fixed_iters=None,capfree=False):
    from k2 import engine
    import kernel2net as KN,k2search_validate as V,movekit as M
    rc=dict(RECIPE); rc.update(recipe or {})
    if capfree: rc.update(cap=10**9,evpen=0)      # CAPFREE: no event cap, no event pressure (default False = unchanged)
    t0=time.time(); tmp=tempfile.mkdtemp(prefix='k2sa_')
    try:
        try: KN.check_rendezvous(w)
        except Exception as e: log('k2sa: word not encodable (%s)'%e); return w,[]
        w1,cinfo=compact(w,log) if compact_first else (w,dict(compacted=False))
        bw=os.path.join(tmp,'base.json.gz'); json.dump(w1,gzip.open(bw,'wt')); net=os.path.join(tmp,'in.net'); KN.dump_net(w1,net)
        k0=M.evaluate(M.pin(w1))
        if not k0.get('legal'): log('k2sa: input illegal'); return w,[]
        kap0=float(k0['kappa']); left=max(2.0,tl-(time.time()-t0)); per=max(2.0,left*0.85/max(1,len(seeds))); best=None
        for sd in seeds:
            out=os.path.join(tmp,'s%d.net'%sd)
            r=engine.run(net,'sa',dict(rc,seed=sd,out=out,**(dict(iters=fixed_iters) if fixed_iters else dict(secs=per,iters=10**9))),timeout=(per if not fixed_iters else 600)+120)
            log('  seed %d: C++ %.14f -> best %s (nev %s, %.0fs)'%(sd,r.get('input',{}).get('kappa',0),r.get('best_kappa'),r.get('nev'),r['sec']))
            if r.get('best_kappa') and os.path.exists(out) and (best is None or r['best_kappa']>best[0]): best=(r['best_kappa'],out,sd)
        if best is None or best[0]<=kap0+eps: log('k2sa: no gain (best %s vs %.14f)'%(best and best[0],kap0)); return w,[]
        res=V.validate(best[1],bw,os.path.join(tmp,'best.json.gz'),exact=True)
        ok=res['legal_ok'] and res['kappa_match'] and res.get('exact_ok') and res['rendezvous_viol']==0
        log('  validate: legal %s kappa_match %s exact %s kappa %.14f'%(res['legal_ok'],res['kappa_match'],res.get('exact_ok'),res['kappa']))
        if not ok or res['kappa']<=kap0+eps: log('k2sa: candidate failed validation'); return w,[]
        w2=json.load(gzip.open(res['word'],'rt'))
        ft=next((type(e[4]) for e in w['program'] if e[0]=='MOVE' and len(e)>4),int)          # MOVE 'private' flag: same JSON type as the input word (realise writes 0/1)
        if ft is bool:
            for e in w2['program']:
                if e[0]=='MOVE' and len(e)>4: e[4]=bool(e[4])
            json.dump(w2,gzip.open(res['word'],'wt'))
        info=dict(screen='k2sa',seed=best[2],kappa=res['kappa'],gain=res['kappa']-kap0,events=res['events'],compact=cinfo)
        if native_ref:
            info['native_ref']=na=native_accept(res['word'],log=log); log('  tk accept --native-ref: %s'%na)
            if inventory_only(na):      # convention-only refusal (public/owned inventory literal): fall back to the native legality check
                info['native_check_fallback']=nc=native_check_free(res['word']); log('  inventory-literal refusal; tk check --native (free bounds): %s'%('LEGAL, 0 bad' if nc else 'FAIL'))
                if not nc: return w,[]
            elif not na['ok']: return w,[]
        if keep: shutil.copy(res['word'],keep)
        return w2,[info]
    finally: shutil.rmtree(tmp,ignore_errors=True)
