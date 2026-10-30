"""tk accept: the REAL price.run acceptance (PR5551 pricing.py with census/claim literals patched, exactly as real.py) with the word-independent and
memoisable parts of the real stack cached, so one accept costs seconds once warm instead of ~200 s.

What is real: local.replay, local.reverse_columns, the live-register adapter part of local.native (run on a pair-free copy of the word), and price.run
(Strict rational crossing enclosure, tail ratios alpha/gamma/delta, compiler grid, scalar/route budgets, outer inventory ...).
What is cached/substituted (and cross-checked against the full real stack on the public words, see tests/regress.py --accept-real):
  * native MOVE / helper-boundary pairs: native_pair.ok (the same Gaussian-recipe check as local.native check()) with a persistent cross-word cache
    keyed by the frame bases (CACHE/nativepairs/*.json, one file per process, merged on load);
  * controller + physical (caller.construct, caller.physical): word-independent except through w['ports']; pickled once per port tuple.
usage: accept.py WORD [--json]      exit 0 = accepted"""
import sys,os,json,time,pickle,glob,re
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from fractions import Fraction as Q
from tkcommon import *
import real as R
_LOCALS={}
def _local(n):
    if n not in _LOCALS: _LOCALS[n]=R.local_for(n)
    sys.modules['local']=_LOCALS[n]
    if R.CTRL not in sys.path: sys.path.insert(0,R.CTRL)
    return _LOCALS[n]
# ---- persistent native pair cache
_PAIRS=None;_NEW={}
def _pairdir(): d=CACHE+'/nativepairs'; os.makedirs(d,exist_ok=True); return d
def _key(a,b): return ','.join(map(str,a))+'|'+','.join(map(str,b))
def _load_pairs():
    global _PAIRS
    if _PAIRS is None:
        _PAIRS={}
        for f in glob.glob(_pairdir()+'/*.json'):
            try: _PAIRS.update(json.load(open(f)))
            except Exception: pass
    return _PAIRS
def flush_pairs():
    if _NEW:
        f='%s/%d_%d.json'%(_pairdir(),os.getpid(),int(time.time()*1000)); json.dump(_NEW,open(f+'.tmp','w')); os.replace(f+'.tmp',f); _NEW.clear()
def _paircache_on(): return not native_is_ref() and os.environ.get('TK_NATIVE_PAIRCACHE','1')!='0'      # SPEED: TK_NATIVE_PAIRCACHE=0 = cold run (no read, no write)
def _par_jobs(n):
    """SPEED: worker processes for n uncomputed pairs: serial below 150 pairs; else TK_NATIVE_JOBS, or min(4, HEAVY_THREADS) inside an hq job, or 4"""
    if n<150: return 1
    e=os.environ.get('TK_NATIVE_JOBS') or os.environ.get('HEAVY_THREADS')
    try: j=int(e) if e else 4
    except ValueError: j=1
    return max(1,min(4,j,n//100))
def compute_pairs(items):
    """verdicts of the native pair check for items [(key, baseA, baseB)] -> {key: [ok, rank_or_reason]}, exactly N.ok of tkcommon.native_mod().
    SPEED: independent pairs are split over _par_jobs() worker processes (nativepar.py, same interpreter flags, inherited env incl. TK_NATIVE_REF);
    any worker failure falls back to the serial in-process computation of the missing keys."""
    out={}; items=sorted(items); j=_par_jobs(len(items))
    if j>1:
        import subprocess
        flags=['-I'] if sys.flags.isolated else []
        procs=[subprocess.Popen([sys.executable]+flags+['-B',HERE+'/nativepar.py'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for c in range(j)]
        for c,p in enumerate(procs):      # all workers start first (imports overlap); each reads all of stdin before it writes anything, so they run concurrently
            try: p.stdin.write(json.dumps([[k,list(a),list(b)] for k,a,b in items[c::j]])); p.stdin.close()
            except Exception: pass
        for p in procs:
            try:
                o=p.stdout.read(); p.stderr.read(); p.wait()
                if p.returncode==0: out.update({k:[bool(v[0]),v[1]] for k,v in json.loads(o).items()})
            except Exception: pass
    miss=[(k,a,b) for k,a,b in items if k not in out]
    if miss:
        N=native_mod()
        for k,a,b in miss:
            ok,v=N.ok(tuple(a),tuple(b)); out[k]=[bool(ok),v]
    return out
def pair_verdicts(fr,pairs):
    """{key: [ok, rank_or_reason]} for the frame-index pairs (key = _key of the two bases), from the persistent cache (fast mode) + compute_pairs for the rest.
    Returns (verdicts, number computed).  New fast-mode verdicts are persisted (one file per process, as before)."""
    C=_load_pairs() if _paircache_on() else {}
    need={}
    for a,b in pairs:
        k=_key(fr[a],fr[b])
        if k not in C and k not in need: need[k]=(k,tuple(fr[a]),tuple(fr[b]))
    if need:
        got=compute_pairs(list(need.values())); C.update(got)
        if _paircache_on(): _NEW.update(got); flush_pairs()
    return C,len(need)
def native_pairs(w,pairs=None):
    """verify every distinct MOVE frame pair and helper boundary (rank == dim gap).  Returns dict(distinct,bad=[(a,b,reason)],seconds,computed)"""
    fr=w['frames']; t=time.time(); bad=[]
    if pairs is None:
        main=set(w['live'])|{r+112 for r in w['live']}
        pairs={(e[2],e[3]) for e in w['program'] if e[0]=='MOVE'}|{(w['initial'][r],w['final'][r]) for r in range(len(w['initial'])) if r not in main}
    C,comp=pair_verdicts(fr,pairs)
    for a,b in sorted(pairs):
        k=_key(fr[a],fr[b])
        if not C[k][0]: bad.append((a,b,C[k][1]))
    return dict(distinct=len(pairs),bad=bad,computed=comp,seconds=round(time.time()-t,1))
def native_light(L,w):
    """the dict price.run needs from local.native(w), without the per-pair Gaussian work (done by native_pairs, cached)"""
    n=len(w['initial']); main=set(w['live'])|{r+112 for r in w['live']}
    rep=native_pairs(w)
    if rep['bad']: raise ValueError('Native boundary rank / phase: %d bad pairs, first %s'%(len(rep['bad']),rep['bad'][0]))
    prof={}
    for r in range(n):
        if r not in main:
            rk=abs(len(w['frames'][w['initial'][r]])-len(w['frames'][w['final'][r]])); prof[rk]=prof.get(rk,0)+1
    w2=json.loads(json.dumps(w)); w2['program']=[e for e in w2['program'] if e[0]!='MOVE']
    for r in range(n):
        if r not in main: w2['final'][r]=w2['initial'][r]     # keep the real adapter / literal-port code, drop the pair work
    nat2=L.native(w2)
    return {'distinct_maps':rep['distinct'],'main_adapters':nat2['main_adapters'],'helper_normalizers':2*sum(prof.values()),'helpers':prof,'light':True,'pairs':rep}
def ctl_phys(L,w):
    f=CACHE+'/ctlphys_%s.pkl'%hashlib_sha(repr(tuple(w['ports'])))
    if os.path.exists(f):
        try: return pickle.load(open(f,'rb'))
        except Exception: pass
    import caller as C
    ctl=C.construct(); phys=C.physical(ctl,w)
    os.makedirs(CACHE,exist_ok=True); pickle.dump((ctl,phys),open(f+'.tmp','wb')); os.replace(f+'.tmp',f); return ctl,phys
def hashlib_sha(s):
    import hashlib; return hashlib.sha256(s.encode()).hexdigest()[:16]
def _prepared_mods():
    """the vendored PR5612 checker stack (real/p5612: prepared573_local.py, pricing.py, pr5599-local.py from the pinned #5608 export): -> (R prepared573_local, L pr5599 local registered as `local`, pricing source)"""
    import importlib.util,pathlib
    d=HERE+'/real/p5612'
    def mod(name,fn):
        sp=importlib.util.spec_from_file_location(name,d+'/'+fn); m=importlib.util.module_from_spec(sp); sys.modules[name]=m; sp.loader.exec_module(m); return m
    L=mod('local','pr5599-local.py'); L.ROOT=pathlib.Path(R.ROOT); R_=mod('prepared573_local','prepared573_local.py')
    if R.CTRL not in sys.path: sys.path.insert(0,R.CTRL)
    return R_,L,open(d+'/pricing.py').read()
def accept_prepared(path,w=None):
    """acceptance for the prepared573 profile (PR5612): its own prepared573_local.replay + reverse_columns, the 5599 native() adapters, native pairs (cached; the retired role's
    boundary pair IS checked, as chain5612 does, but its helper credit is withdrawn), caller/physical, and PR5612's pricing.py with only the census/claim literals patched."""
    import re,types
    t0=time.time(); w=w or legal.load(path); res=dict(ok=False,stage=None,error=None,public=len(w['initial']),profile='p5612'); st='load'
    try:
        R_,L,psrc=_prepared_mods(); ret=legal.retired_of(w)
        st='replay'; local=R_.replay(w)
        st='reverse_columns'; R_.reverse_columns(w)
        st='native'
        rep=native_pairs(w); res['native_pairs']=rep['distinct']; res['native_computed']=rep['computed']; res['native_ref']=bool(native_is_ref())
        if rep['bad']: raise ValueError('Native boundary rank / phase: %d bad pairs, first %s'%(len(rep['bad']),rep['bad'][0]))
        main=set(w['live'])|{r+112 for r in w['live']}; prof={}
        for r in range(len(w['initial'])):
            if r not in main and r not in ret:
                rk=abs(len(w['frames'][w['initial'][r]])-len(w['frames'][w['final'][r]])); prof[rk]=prof.get(rk,0)+1
        w2=json.loads(json.dumps(w)); w2['program']=[e for e in w2['program'] if e[0]!='MOVE']
        for r in range(len(w['initial'])):
            if r not in main: w2['final'][r]=w2['initial'][r]
        nat2=L.native(w2)
        native={'distinct_maps':rep['distinct'],'main_adapters':nat2['main_adapters'],'helper_normalizers':2*sum(prof.values()),'helpers':prof,'retired_helper':ret[0] if ret else None}
        st='controller/physical'; ctl,phys=ctl_phys(L,w)
        st='claim'; lg=legal.check(w)
        if not lg['ok']: raise ValueError('illegal: %s'%(lg['violations'][:1],))
        T,Pp=X.invoice(lg); k=X.kappa(T,Pp)
        kstr='%.9f'%(k-5e-9-2e-9); tested='%.10f'%(float(kstr)+5e-9)
        sumT=sum(T.values()); sumP=sum(Pp.values()); surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in Pp.items())
        res['claim']=dict(KAPPA=kstr,TESTED=tested,sumT=sumT,sumP=sumP,surplus=surplus)
        for pat,rep_ in((r"KAPPA, TESTED = Q\('[^']*'\), Q\('[^']*'\)","KAPPA, TESTED = Q('%s'), Q('%s')"%(kstr,tested)),
                        (r"sum\(targets.values\(\)\) == \d+ and sum\(paid.values\(\)\) == \d+","sum(targets.values()) == %d and sum(paid.values()) == %d"%(sumT,sumP)),
                        (r"== 760,","== %d,"%surplus),(r"PREVIOUS = Q\('[^']*'\)","PREVIOUS = Q('.00310184')")):
            psrc,n_=re.subn(pat,rep_,psrc)
            if n_!=1: raise SystemExit('pricing template literal count %d for %s'%(n_,pat))
        st='price.run'; m=types.ModuleType('price_patched_p5612'); m.__dict__['__file__']=HERE+'/real/p5612/pricing.py'; exec(compile(psrc,'price_patched_p5612','exec'),m.__dict__)
        r=m.run(local,native,ctl,phys)
        lo,hi=r['raw_root_interval']; res['crossing_lo']='%.14f'%float(Q(lo)); res['crossing_hi']='%.14f'%float(Q(hi))
        res['outer_checks']=(len(r['outer']['strict_checks']),len(r['outer']['functional_checks'])); res['paid_calls']=r['paid_calls']; res['productive_fields']=r['productive_fields']
        res['ok']=True; st='done'
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        res['error']=(str(e) or repr(e))[:400]
    res['stage']=st; res['seconds']=round(time.time()-t0,1); return res
def accept_owned9(path,w=None):
    """acceptance for the p5660 profile (#5644/#5650/#5660): PR5627's local.py (owned_fields) replay + reverse_columns, its native() adapters, native pairs (cached), caller/physical and the
    #5660 pricing.py (reserve 1/10^12) with only the census/claim literals patched.  Same cached/real split as accept_prepared."""
    import re,types,importlib.util,pathlib
    t0=time.time(); w=w or legal.load(path); res=dict(ok=False,stage=None,error=None,public=len(w['initial']),profile='p5660'); st='load'
    try:
        d=HERE+'/real/p5660'
        sp=importlib.util.spec_from_file_location('local',d+'/pr5627-local.py'); L=importlib.util.module_from_spec(sp); sys.modules['local']=L; sp.loader.exec_module(L); L.ROOT=pathlib.Path(R.ROOT)
        if R.CTRL not in sys.path: sys.path.insert(0,R.CTRL)
        psrc=open(d+'/pricing.py').read()
        st='replay'; local=L.replay(w)
        st='reverse_columns'; L.reverse_columns(w)
        st='native'; native=native_light(L,w); res['native_pairs']=native['pairs']['distinct']; res['native_computed']=native['pairs']['computed']; res['native_ref']=bool(native_is_ref())
        st='controller/physical'; ctl,phys=ctl_phys(L,w)
        st='claim'; lg=legal.check(w)
        if not lg['ok']: raise ValueError('illegal: %s'%(lg['violations'][:1],))
        T,Pp=X.invoice(lg); k=X.kappa(T,Pp)
        kstr='%.9f'%(k-5e-9-2e-9); tested='%.10f'%(float(kstr)+5e-9)
        sumT=sum(T.values()); sumP=sum(Pp.values()); surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in Pp.items())
        res['claim']=dict(KAPPA=kstr,TESTED=tested,sumT=sumT,sumP=sumP,surplus=surplus)
        for pat,rep_ in((r"KAPPA, TESTED = Q\('[^']*'\), Q\('[^']*'\)","KAPPA, TESTED = Q('%s'), Q('%s')"%(kstr,tested)),
                        (r"sum\(targets.values\(\)\) == \d+ and sum\(paid.values\(\)\) == \d+","sum(targets.values()) == %d and sum(paid.values()) == %d"%(sumT,sumP)),
                        (r"== 760,","== %d,"%surplus),(r"PREVIOUS = Q\('[^']*'\)","PREVIOUS = Q('.00310184')")):
            psrc,n_=re.subn(pat,rep_,psrc)
            if n_!=1: raise SystemExit('pricing template literal count %d for %s'%(n_,pat))
        st='price.run'; m=types.ModuleType('price_patched_p5660'); m.__dict__['__file__']=d+'/pricing.py'; exec(compile(psrc,'price_patched_p5660','exec'),m.__dict__)
        r=m.run(local,native,ctl,phys)
        lo,hi=r['raw_root_interval']; res['crossing_lo']='%.14f'%float(Q(lo)); res['crossing_hi']='%.14f'%float(Q(hi))
        res['outer_checks']=(len(r['outer']['strict_checks']),len(r['outer']['functional_checks'])); res['paid_calls']=r['paid_calls']; res['productive_fields']=r['productive_fields']
        res['ok']=True; st='done'
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        res['error']=(str(e) or repr(e))[:400]
    res['stage']=st; res['seconds']=round(time.time()-t0,1); return res
# ---- SPEED (Oct 28): memo of whole stack-profile acceptances, keyed by the word CONTENT (sha256 of the decompressed JSON, so gzip mtimes do not matter),
# the resolved profile + sha256 of its JSON (stack pins), the sources of every module on the acceptance path, and the env switches that can change a verdict.
# Only terminal deterministic outcomes are stored (stage 'done', or a need()/ValueError rejection inside replay..price.run); never worker crashes or timeouts.
# Off under --native-ref / TK_NATIVE_REF=1 and with TK_ACCEPT_CACHE=0.  A hit returns the stored dict plus cached=True.
_MEMO_STAGES={'done','replay','reverse_columns','native','claim','price.run'}
_MEMO_ENV=('TK_NATIVE_REF','TK_PROFILE','TK_FREE_BOUNDS','TK_VERIFIER_PROFILE','TK_NATIVE_PAIRCACHE','TK_FAST_ADAPTERS','TK_PRICERUN_CACHE')
def _memo_key(path,pn):
    if os.environ.get('TK_NATIVE_REF')=='1' or os.environ.get('TK_ACCEPT_CACHE','1')=='0': return None
    try:
        import hashlib,gzip
        raw=open(path,'rb').read()
        if raw[:2]==b'\x1f\x8b': raw=gzip.decompress(raw)
        code=b''.join(open(os.path.join(HERE,f),'rb').read() for f in ('accept.py','tkstack.py','fastnative.py','nativepar.py','real.py','tkcommon.py'))
        code+=open(legal.__file__,'rb').read()+open(X.__file__,'rb').read()
        pj=open(DATA_PROFILES[pn]['_file'],'rb').read()
        h=hashlib.sha256(); [h.update(hashlib.sha256(b).digest()) for b in (raw,code,pj,repr((pn,[(k,os.environ.get(k)) for k in _MEMO_ENV])).encode())]
        return h.hexdigest()
    except Exception: return None
def _memo_get(k):
    if not k: return None
    try: return json.load(open(CACHE+'/acceptmemo/%s.json'%k))
    except Exception: return None
def _memo_put(k,r):
    if not k or r.get('stage') not in _MEMO_STAGES or (r.get('stage')!='done' and not r.get('error')): return
    try:
        d=CACHE+'/acceptmemo'; os.makedirs(d,exist_ok=True); f='%s/%s.json'%(d,k); json.dump(r,open(f+'.%d.tmp'%os.getpid(),'w'),default=str); os.replace(f+'.%d.tmp'%os.getpid(),f)
    except Exception: pass
def accept(path,w=None):
    """-> dict(ok, stage, error, crossing_lo/hi (14 d.p.), claim, seconds, native pairs info).  Never raises for a rejection."""
    t0=time.time(); w=w or legal.load(path); n=len(w['initial']); res=dict(ok=False,stage=None,error=None,public=n)
    pn,pr=profile_of(w)
    if pr.get('verifier')=='stack' and pn in DATA_PROFILES and DATA_PROFILES[pn].get('stack'):      # adopted profile: the PR's own vendored local.py / pricing.py (sandboxed worker)
        import tkstack
        mk=_memo_key(path,pn); r=_memo_get(mk)
        if r is not None and not tkstack.check_pins(tkstack.profile(pn)): r['cached']=True; return r      # a memo hit is honoured only while the vendored stack files still match their pins
        r=tkstack.run_isolated(tkstack.profile(pn),path,patched=True); r.pop('result',None); _memo_put(mk,r); return r
    if pr.get('verifier')=='prepared573': return accept_prepared(path,w)
    if pr.get('verifier')=='owned9': return accept_owned9(path,w)
    if not pr['real_stack']: res.update(stage='profile',error='profile %s has its own verifier; real price.run of this stack not applicable (use fast acceptance)'%pn,unsupported=True); return res
    try:
        L=_local(n)
        st='replay'; local=L.replay(w)
        st='reverse_columns'; L.reverse_columns(w)
        st='native'; native=native_light(L,w); res['native_pairs']=native['pairs']['distinct']; res['native_computed']=native['pairs']['computed']; res['native_ref']=bool(native_is_ref())
        st='controller/physical'; ctl,phys=ctl_phys(L,w)
        st='claim'; rep=legal.check(w)
        if not rep['ok']: raise ValueError('illegal: %s'%(rep['violations'][:1],))
        T,Pp=X.invoice(rep); k=X.kappa(T,Pp)
        kstr='%.9f'%(k-5e-9-2e-9); tested='%.10f'%(float(kstr)+5e-9)
        sumP=sum(Pp.values()); surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in Pp.items())
        res['claim']=dict(KAPPA=kstr,TESTED=tested,sumT=sum(T.values()),sumP=sumP,surplus=surplus)
        st='price.run'; P=R.patched_price(L,kstr,sum(T.values()),sumP,surplus,tested); r=P.run(local,native,ctl,phys)
        lo,hi=r['raw_root_interval']; res['crossing_lo']='%.14f'%float(Q(lo)); res['crossing_hi']='%.14f'%float(Q(hi))
        res['outer_checks']=(len(r['outer']['strict_checks']),len(r['outer']['functional_checks'])); res['paid_calls']=r['paid_calls']; res['productive_fields']=r['productive_fields']
        res['ok']=True; st='done'
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        res['error']=(str(e) or repr(e))[:400]
    res['stage']=st; res['seconds']=round(time.time()-t0,1); return res
def main(argv=None):
    a=[argv.word] if hasattr(argv,'word') else (argv or sys.argv[1:]); path=resolve(a[0]); r=accept(path)
    print(json.dumps(r,indent=1,default=str)); return 0 if r['ok'] else 1
if __name__=='__main__': sys.exit(main())
