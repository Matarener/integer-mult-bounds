"""tkstack: run a PR's OWN verifier stack (vendored local.py / pricing.py from the fetched blob, hash-pinned) as the authoritative checker for any word.
Driven entirely by a data profile (toolkit/profiles/<alias>.json, section `stack`; written by `tk adopt`), so a new swarm verifier variant needs no new code here.

Pipeline (what every PR's verify.py does, minus the construction):  base local (module `local`: need/load/ROOT/native)  ->  replay + reverse_columns of the replay module
-> native (cached pair checks via fastnative; `L.native` itself on a pair-free copy for the adapters; named native edits)  ->  controller/physical caller  ->  the PR's pricing.py
(`run(local,native,caller,physical)`), with its claim literals patched to the candidate's own invoice (regexes recorded in the profile) or run unpatched on the PR's own word.

Sandbox: `run_isolated()` executes in `python -I -B` with a scrubbed environment, a temp cwd and network access disabled (best effort: socket module replaced);
the code that runs is only the vendored, sha256-pinned PR files."""
import sys,os,json,time,re,types,importlib.util,hashlib,subprocess,tempfile
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__))
PROFDIR=HERE+'/profiles'
from fractions import Fraction as Q
def sha256_file(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def norm(x):
    """JSON-normal form of a replay / native / result dict (Fractions -> str, int keys -> str), comparable with RESULT.json"""
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):norm(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [norm(v) for v in x]
    return x
def dict_diff(a,b,path='',out=None,limit=12):
    """precise diff of two JSON-normal objects: [(path, a_value, b_value)]"""
    out=[] if out is None else out
    if len(out)>=limit: return out
    if isinstance(a,dict) and isinstance(b,dict):
        for k in sorted(set(a)|set(b),key=str):
            if k not in a: out.append((path+'/'+str(k),'<absent>',str(b[k])[:60]))
            elif k not in b: out.append((path+'/'+str(k),str(a[k])[:60],'<absent>'))
            else: dict_diff(a[k],b[k],path+'/'+str(k),out,limit)
    elif a!=b: out.append((path or '/',str(a)[:60],str(b)[:60]))
    return out
def load_module(path,name,root):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m)
    if hasattr(m,'ROOT') or name=='local':
        import pathlib; m.ROOT=pathlib.Path(root)
    return m
def sandbox():
    import socket
    def deny(*a,**k): raise OSError('tk sandbox: network disabled')
    for n in ('socket','create_connection','getaddrinfo','gethostbyname'): setattr(socket,n,deny)
def pdir(prof): return PROFDIR+'/'+prof['alias']+'/'
def check_pins(prof):
    """vendored stack files must still hash to the pins recorded at adopt time (a blob from the fetched PR head)"""
    bad=[]
    for fn,pin in (prof['stack'].get('files') or {}).items():
        p=pdir(prof)+fn
        if not os.path.exists(p) or sha256_file(p)!=pin['sha256']: bad.append(fn)
    return bad
NATIVE_REPORT={}
def _fast_adapters(base,pairs_mod):
    """SPEED (Oct 28): in the default (fast) native mode, the PR's own native() on the pair-free copy (main adapters + identity helper charts) runs with the
    fastnative kernels -- the same bit-identical numpy replacements of clifford_exact.Op.zero_state / native_verify.state / tableau that the pair checks
    already use (module docstring).  Done by wrapping the module's own `load` so the vendor modules it loads get those kernels; everything else (lower_child,
    recipes, need(), exception text) is the pinned code.  --native-ref / TK_NATIVE_REF=1: untouched.  TK_FAST_ADAPTERS=0 disables.  Returns an undo function."""
    if pairs_mod.native_is_ref() or os.environ.get('TK_FAST_ADAPTERS','1')=='0' or not callable(getattr(base,'load',None)): return lambda:None
    import fastnative as F
    N=pairs_mod.native_mod()
    if N is not F or F.REF or F.V is None: return lambda:None
    orig=base.load; vdir=os.path.realpath(F.ROOT+F._SUB)
    def load(path,name):
        m=orig(path,name); pp=os.path.realpath(str(path))
        if os.path.dirname(pp)==vdir:
            if os.path.basename(pp)=='clifford_exact.py' and hasattr(m,'Op'): m.Op.zero_state=F.make_zero_state(m.Op.zero_state)
            elif os.path.basename(pp)=='native_verify.py' and hasattr(m,'state') and hasattr(m,'tableau'): m.state=F.make_state(m.state); m.tableau=F.make_tableau(m.tableau)
        return m
    base.load=load
    def undo(): base.load=orig
    return undo
def native_generic(base,w,nat,pairs_mod):
    """native(): pairs through the cached fast checker, adapters from the PR's own L.native on a pair-free copy; named edits from the profile."""
    import legal
    main=set(w['live'])|{r+112 for r in w['live']}; ret=set(legal.retired_of(w)); n=len(w['initial'])
    rep=pairs_mod.native_pairs(w)
    NATIVE_REPORT.clear(); NATIVE_REPORT.update(ref=bool(pairs_mod.native_is_ref()),pairs=rep['distinct'],computed=rep['computed'],bad=len(rep['bad']),seconds=rep.get('seconds'))     # SEARCHPERF: evidence for validation
    if rep['bad']: raise ValueError('Native boundary rank / phase: %d bad pairs, first %s'%(len(rep['bad']),rep['bad'][0]))
    prof={}
    for r in range(n):
        if r not in main and r not in ret:
            rk=abs(len(w['frames'][w['initial'][r]])-len(w['frames'][w['final'][r]])); prof[rk]=prof.get(rk,0)+1
    w2=json.loads(json.dumps(w)); w2['program']=[e for e in w2['program'] if e[0]!='MOVE']
    for r in range(n):
        if r not in main: w2['final'][r]=w2['initial'][r]
    restore=_fast_adapters(base,pairs_mod)
    try: nat2=base.native(w2)
    finally: restore()
    out={'distinct_maps':rep['distinct'],'main_adapters':nat2['main_adapters'],'helper_normalizers':2*sum(prof.values()),'helpers':prof}
    for e in (nat.get('edits') or []):
        if e=='retired_helper' and ret: out['retired_helper']=sorted(ret)[0]
        elif e not in ('retired_helper',): raise ValueError('unknown native edit %r'%e)
    return out
def patched_source(prof,path,w,local,native):
    """the PR's pricing.py with claim literals set to the candidate's own invoice (same regexes the profile recorded at adopt time)"""
    import price_exact as X
    S=prof['stack']['pricing']; src=open(pdir(prof)+S['file']).read()
    T,P=X.invoice(dict(helpers=native['helpers'],paid=local['paid']))
    k=X.kappa(T,P); kstr='%.9f'%(k-5e-9-2e-9); tested='%.10f'%(float(kstr)+5e-9)
    sumT=sum(T.values()); sumP=sum(P.values()); surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in P.items())
    vals=dict(KAPPA=kstr,TESTED=tested,sumT=sumT,sumP=sumP,surplus=surplus,**{'PREV_%d'%i:'0.000%d'%(i+1) for i in range(9)})
    class _D(dict):
        def __missing__(s,k): return '0.0001'        # unknown template field (older profile): any value below the candidate's kappa
    skipped=[]
    for name,pat,tmpl in S['patch']:      # tolerant: patch only the literals that exist exactly once in this pricing.py; the rest are left as the PR wrote them
        src,c=re.subn(pat,lambda m:tmpl.format_map(_D(vals)),src) if len(re.findall(pat,src))==1 else (src,0)
        if c!=1: skipped.append(name)
    vals['skipped_patches']=skipped
    return src,vals
# ---- SPEED (Oct 28): memo of the PR's price.run result.  run(local,native,controller,physical) is a deterministic function of: the (patched) pricing source,
# the replay dict `local`, the native dict, the controller/physical pair (a function of w['ports'] -- the same assumption as accept.ctl_phys's cache), the
# profile (its JSON carries the sha256 pins of every vendored stack file, enforced by check_pins) and the pinned closure root.  The key hashes all of them
# with a type-preserving canonical form, so a hit returns the identical object.  Words with the same invoice (plateau / neutral moves) skip the ~9 s Fraction
# bisection.  Only successful runs are stored.  Off under --native-ref / TK_NATIVE_REF=1 (ship convention: everything really runs) or TK_PRICERUN_CACHE=0.
def _canon(x):
    if isinstance(x,dict): return ('d',tuple(sorted(((_canon(k),_canon(v)) for k,v in x.items()),key=repr)))
    if isinstance(x,(list,tuple)): return (type(x).__name__,tuple(_canon(v) for v in x))
    return x
def _pricerun_on(): return os.environ.get('TK_NATIVE_REF','0')!='1' and os.environ.get('TK_PRICERUN_CACHE','1')!='0'
def _pricerun_key(prof,src,local,native,w,root):
    if not _pricerun_on(): return None
    try:
        pj=sha256_file(PROFDIR+'/%s.json'%prof['alias'])
        return hashlib.sha256(repr(('pricerun/1',prof['alias'],pj,str(root),src,_canon(local),_canon(native),tuple(w.get('ports') or ()))).encode()).hexdigest()
    except Exception: return None
def _pricerun_file(k):
    from tkcommon import CACHE
    return CACHE+'/pricerun/%s.pkl'%k
def _pricerun_get(k):
    if not k: return None
    import pickle
    try: return pickle.load(open(_pricerun_file(k),'rb'))
    except Exception: return None
def _pricerun_put(k,r):
    if not k: return
    import pickle
    try:
        f=_pricerun_file(k); os.makedirs(os.path.dirname(f),exist_ok=True); tmp='%s.%d.tmp'%(f,os.getpid())
        pickle.dump(r,open(tmp,'wb')); os.replace(tmp,f)
    except Exception: pass
def stack_accept(prof,path,w=None,patched=True):
    """-> dict(ok, stage, error, crossing_lo/hi (14 d.p.), claim, seconds, ...) using the profile's vendored stack"""
    import legal,accept as A
    from tkcommon import closure_root,CACHE
    t0=time.time(); w=w or legal.load(path); res=dict(ok=False,stage=None,error=None,public=len(w['initial']),profile=prof['alias'],stack=True); st='pins'
    try:
        bad=check_pins(prof)
        if bad: raise ValueError('vendored stack files changed since adopt: %s'%bad)
        S=prof['stack']; root=closure_root(); d=pdir(prof)
        st='load'; base=load_module(d+S['base']['file'],'local',root)
        rp=S['replay']['file']; rep=base if rp==S['base']['file'] else load_module(d+rp,'tk_replay_'+prof['alias'],root)
        if A.R.CTRL not in sys.path: sys.path.insert(0,A.R.CTRL)
        st='replay'; local=rep.replay(w)
        st='reverse_columns'; rep.reverse_columns(w)
        st='native'; native=native_generic(base,w,S['native'],A)
        st='controller/physical'; ctl,phys=A.ctl_phys(base,w)
        st='claim'
        if patched: src,vals=patched_source(prof,path,w,local,native); res['claim']=vals
        else: src=open(d+S['pricing']['file']).read()
        st='price.run'; mk=_pricerun_key(prof,src,local,native,w,root); r=_pricerun_get(mk)
        if r is None:
            m=types.ModuleType('price_'+prof['alias']); m.__dict__['__file__']=d+S['pricing']['file']; exec(compile(src,'price_'+prof['alias'],'exec'),m.__dict__)
            r=m.run(local,native,ctl,phys); _pricerun_put(mk,r)
        else: res['pricerun_cached']=True
        lo,hi=r['raw_root_interval']; res['crossing_lo']='%.14f'%float(Q(lo)); res['crossing_hi']='%.14f'%float(Q(hi)); res['raw_root_interval']=[str(lo),str(hi)]
        res['outer_checks']=(len(r['outer']['strict_checks']),len(r['outer']['functional_checks'])); res['paid_calls']=r['paid_calls']; res['productive_fields']=r['productive_fields']
        res['local']=norm(local); res['native']=norm(native); res['result']=r; res['native_check']=dict(NATIVE_REPORT)
        res['ok']=True; st='done'
    except BaseException as e:
        if isinstance(e,KeyboardInterrupt): raise
        res['error']=(str(e) or repr(e))[:400]
    res['stage']=st; res['seconds']=round(time.time()-t0,1); return res
def run_isolated(prof,path,patched=True,timeout=1500):
    """stack_accept in a fresh `python -I -B` process (scrubbed env, temp cwd, no network).  -> same dict (without the bulky `result`)"""
    env={'PATH':'/usr/bin:/bin','HOME':tempfile.gettempdir(),'PYTHONDONTWRITEBYTECODE':'1','TK_NATIVE_REF':os.environ.get('TK_NATIVE_REF','0')}
    env.update({k:os.environ[k] for k in ('TK_NATIVE_PAIRCACHE','TK_FAST_ADAPTERS','TK_PRICERUN_CACHE','TK_NATIVE_JOBS','HEAVY_THREADS') if k in os.environ})      # SPEED switches reach the sandbox
    cwd=tempfile.mkdtemp(prefix='tkstack-')
    cmd=[sys.executable,'-I','-B',HERE+'/tkstack.py','--worker',prof['alias'],os.path.abspath(path),'1' if patched else '0']
    r=subprocess.run(cmd,capture_output=True,text=True,env=env,cwd=cwd,timeout=timeout)
    try: return json.loads(r.stdout.split('@@RESULT@@',1)[1])
    except Exception: return dict(ok=False,stage='worker',error=(r.stderr or r.stdout)[-400:])
def profile(alias):
    return json.load(open(PROFDIR+'/%s.json'%alias))
def probe(cand,wordpath,edits=()):
    """what does this candidate local.py produce on the word?  -> dict(replay=norm|None, native=norm|None, errors)"""
    import legal,accept as A
    from tkcommon import closure_root
    w=legal.load(wordpath); root=closure_root(); out={}
    if A.R.CTRL not in sys.path: sys.path.insert(0,A.R.CTRL)
    try:
        L=load_module(cand,'local',root)
    except BaseException as e: return dict(error='import: '+repr(e)[:200])
    try: out['replay']=norm(L.replay(w))
    except BaseException as e: out['replay_error']=repr(e)[:200]
    try:
        out['cols']=norm(L.reverse_columns(w))
    except BaseException as e: out['cols_error']=repr(e)[:200]
    try: out['native']=norm(native_generic(L,w,dict(edits=list(edits)),A))
    except BaseException as e: out['native_error']=repr(e)[:200]
    return out
def run_probe(cand,wordpath,edits=(),timeout=900):
    env={'PATH':'/usr/bin:/bin','HOME':tempfile.gettempdir(),'PYTHONDONTWRITEBYTECODE':'1'}
    r=subprocess.run([sys.executable,'-I','-B',HERE+'/tkstack.py','--probe',cand,wordpath,','.join(edits)],capture_output=True,text=True,env=env,cwd=tempfile.mkdtemp(prefix='tkprobe-'),timeout=timeout)
    try: return json.loads(r.stdout.split('@@RESULT@@',1)[1])
    except Exception: return dict(error=(r.stderr or r.stdout)[-300:])
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='--probe':
    sandbox(); sys.path.insert(0,HERE); import tkcommon
    print('@@RESULT@@'+json.dumps(probe(sys.argv[2],sys.argv[3],[e for e in sys.argv[4].split(',') if e]),default=str))
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='--worker':
    sandbox(); sys.path.insert(0,HERE); import tkcommon
    alias,path,pat=sys.argv[2],sys.argv[3],sys.argv[4]=='1'
    r=stack_accept(profile(alias),path,patched=pat); r.pop('result',None)
    print('@@RESULT@@'+json.dumps(r,default=str))
