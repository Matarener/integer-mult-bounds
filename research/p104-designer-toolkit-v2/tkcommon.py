"""tk shared helpers: paths, word aliases, caching, role names.  Imports the infra modules (single source of truth)."""
import sys,os,gzip,json,hashlib,time
HERE=os.path.dirname(os.path.abspath(__file__))
# Everything the toolkit needs ships next to this file: infra/ (legality oracle, exact pricing, lattice tools), inputs/ (byte-pinned PR5545 verifier capsule).
# Scratch state (cache, outputs, job logs) lives under TK_WORK (default: this directory; .cache/ out/ jobs/ ext/ are git-ignored).
PACKAGE=True
W=os.environ.get('TK_WORK') or HERE
INFRA=HERE+'/infra'
for p in (INFRA,HERE):
    if p not in sys.path: sys.path.insert(0,p)
sys.dont_write_bytecode=True
import legal,price_exact as X
PY=sys.executable
os.makedirs(W,exist_ok=True)
CACHE=W+'/.cache'
OUT=W+'/out'
ALIASES={a:HERE+'/words/%s.json.gz'%a for a in ('5545','5551','5553','5553A','5561','5561s','5569','5580','5565','5565A','5565old','5599','5599n','5612','on5612','5644','5650','5660')}
# published crossing intervals (lo,hi) of the shipped words, from RESULT.json / VERIFY of each package
EXPECT={'5545':'.00304117181649','5551':'.00304153116715','5553':'.0030428242','5561':'.0030814243','5561s':'.0030768800','5569':'.0030818185','5580':'.0030818949','5565old':'.00304195140018','5565':'.00308521055201','5565A':'.00308415555080','5599':'.00309839352211','5599n':'.0031004563','5612':'.00310299359333','on5612':'.00310440547057','5644':'.00310626336369','5650':'.00310644469581','5660':'.00310676334487'}
def resolve(spec):
    """alias (5551, 5553, 5561, 5561s, 5545, 5553A) or a path to WORD.json[.gz]"""
    if spec in ALIASES: return ALIASES[spec]
    if os.path.exists(spec): return os.path.abspath(spec)
    raise SystemExit('tk: no such word %r (aliases: %s)'%(spec,', '.join(ALIASES)))
def sha(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()
_ACT=[False]
def activate(w):
    """make legal.profile_params see the pins of the data profile selected for this word (one-shot CLI process); a legacy profile clears a previous activation"""
    try: name,pr=profile_of(w)
    except SystemExit: return
    if name in DATA_PROFILES and not os.environ.get('TK_VERIFIER_PROFILE'): os.environ['TK_VERIFIER_PROFILE']=DATA_PROFILES[name]['_file']; _ACT[0]=True
    elif _ACT[0] and name not in DATA_PROFILES: os.environ.pop('TK_VERIFIER_PROFILE',None); _ACT[0]=False
def load(spec):
    p=resolve(spec); w=legal.load(p); activate(w); return p,w
def _rules_tag():
    """hash of the legality/pricing rule sources: a rule change (e.g. a new verifier profile) must never serve an older cached verdict"""
    return hashlib.sha256(b''.join(open(m.__file__,'rb').read() for m in (legal,X))).hexdigest()[:6]
def cache_get(kind,path):
    f='%s/%s_%s_%s%s.json'%(CACHE,kind,sha(path)[:16],_rules_tag(),('_'+os.environ['TK_PROFILE']) if os.environ.get('TK_PROFILE') else '')
    if os.path.exists(f):
        try: return json.load(open(f)),f
        except Exception: pass
    return None,f
def cache_put(f,obj):
    os.makedirs(CACHE,exist_ok=True); json.dump(obj,open(f,'w'),indent=1,default=str)
def roles(w):
    """role(r) -> 'X' live source, 'Y' target (r+112), 'helper', 'owned' (scratch, r>=len(initial))"""
    live=set(w['live']); n=len(w['initial']); ret=set(legal.retired_of(w))
    def role(r):
        if r in ret: return 'owned'      # prepared573: the retired public role is an owned scratch role
        if r in live: return 'X'
        if r-112 in live and r<n: return 'Y'
        return 'helper' if r<n else 'owned'
    return role
def dimstr(w,f): return '%s(dim %d)'%(f,len(w['frames'][f])) if f is not None else 'None'

def closure_root():
    """root holding research/p104-productive-controller/ (the byte-pinned PR5545 source capsule): the workspace tree, or the package's own tarball extracted once into .cache/"""
    import tarfile
    d=CACHE+'/closure'
    if not os.path.isdir(d+'/research/p104-productive-controller'):
        os.makedirs(d,exist_ok=True)
        with tarfile.open(HERE+'/inputs/pr5545-source-closure.tar.gz') as t:
            for m in t.getmembers():
                if m.name.startswith('/') or '..' in m.name.split('/'): raise SystemExit('unsafe tar member '+m.name)
            t.extractall(d)
    return d
def submit(name,TL,argv,wait=False,donefile_out=None,threads=1,poll=10):
    """run a heavy job directly (default) or through the optional queue wrapper named by $TK_HQ.  wait=True polls for jobs/NAME.done (bounded by TL+120)."""
    import subprocess
    env=dict(os.environ,THREADS=str(threads),HEAVY_THREADS=str(threads))
    HQ=os.environ.get('TK_HQ')      # optional job-queue wrapper (same calling convention: HQ NAME TIMELIMIT argv...); default = run synchronously
    if not HQ or not os.path.exists(HQ):      # no job queue: run synchronously in this process tree
        os.makedirs(W+'/jobs',exist_ok=True); lg=W+'/jobs/%s.log'%name
        with open(lg,'w') as f: rc=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=TL+60).returncode
        open(W+'/jobs/%s.done'%name,'w').close(); print('job %s finished rc=%d, log %s'%(name,rc,lg)); return rc==0
    r=subprocess.run([HQ,name,str(int(TL))]+argv,capture_output=True,text=True,env=env)
    print((r.stdout+r.stderr).strip())
    if not wait: return None
    t0=time.time(); done=W+'/jobs/%s.done'%name
    while time.time()-t0<TL+120 and not os.path.exists(done): time.sleep(poll)
    return os.path.exists(done)

# compiler-parameter profiles (tail decay of price.run's three-ratio check, log power).  Default = PR5551..5580 (decay .97, power 1000).
# #5599 (750 public regs) changes them to decay 39/40, power 1024 and ships its OWN local.py/verify.py, so the real price.run of the
# 5551-line stack (accept.py) does not apply to it: tk eval uses the fast acceptance (legal + native pairs + profile side + budgets) for that profile.
PROFILES={'default':dict(decay=0.97,power=1000,real_stack=True),'p5599':dict(decay=39/40,power=1024,real_stack=False)}
PROFILE_BY_PUBLIC={750:'p5599',748:'p5599'}
# p5612 = 'prepared573' verifier (PR5612 delayed shared preparation): #5599 compiler constants (decay 39/40, power 1024) but its OWN local.py (prepared573_local.py:
# owned initialisation by owned_roles, peak owned 2, 11 lifetimes, 747 independent inputs, retired role 573 not a helper) and its own pricing census.  Selected by the word's
# `retired_public` key (NOT by the public count: #5608-family words also have 748 registers and stay p5599).  The verifier rules live in infra/legal.py (check(): RET/OWN/PREPARED).
PROFILES['p5612']=dict(decay=39/40,power=1024,real_stack=True,verifier='prepared573',peak=2,lifetimes=11)
# p5660 = the PR5627 'owned_fields' local.py (words of #5644/#5650/#5660: 743 public + 9 owned, peak<=2, 11 lifetimes) + their pricing.py, identical to #5612's except the census/claim literals
# and `reserve = 1/10^12` (alpha < 1-reserve; #5612 and earlier 1/10^10).  Selected by the word's `owned_fields` key.
PROFILES['p5660']=dict(decay=39/40,power=1024,real_stack=True,verifier='owned9',peak=2,lifetimes=11,reserve=1e-12)
# ---- DATA profiles (toolkit/profiles/<alias>.json, written by `tk adopt`; schema in module docstring).  They extend PROFILES with the verifier constants the PR's own
# files declare (decay, log power, reserve, peak, lifetimes, owned count) and, when a stack is vendored, the authoritative checker (tkstack).
PROFDIR=HERE+'/profiles'
DATA_PROFILES={}
def _load_data_profiles():
    import glob
    for f in sorted(glob.glob(PROFDIR+'/*.json')):
        try: p=json.load(open(f))
        except Exception: continue
        if p.get('schema')!='tk-profile/1': continue
        DATA_PROFILES[p['alias']]=p; p['_file']=f
        wf=HERE+'/words/%s.json.gz'%p['alias']
        if os.path.exists(wf) and p['alias'] not in ALIASES: ALIASES[p['alias']]=wf
        if p['alias'] not in EXPECT: EXPECT[p['alias']]=p['expect']['interval'][0]
        PROFILES[p['alias']]=dict(decay=p['compiler']['decay_f'],power=p['compiler']['power'],real_stack=bool(p.get('stack')),verifier='stack' if p.get('stack') else 'data',
                                  peak=p['peak'],lifetimes=p['lifetimes'],reserve=p['compiler']['reserve_f'],data=True,owned_fields=p['owned_fields'],
                                  tail=_tail_of(p['compiler']))
def _tail_of(c):
    """(c,b,u) tail literal of an adopted compiler block as floats/ints for X.side (u may be a fraction string like '1/7'); None when the profile has no tail"""
    t=c.get('tail')
    if not t: return None
    from fractions import Fraction
    return dict(c=int(t['c']),b=int(t['b']),u=float(Fraction(str(t['u']))))
def family_of(w):
    return dict(public=len(w['initial']),owned_fields=w.get('owned_fields',8),retired_public=list(w.get('retired_public') or []),has_owned_fields_key='owned_fields' in w)
def word_fingerprint(w):
    """cheap exact identity of a word (initial, final, program length, full program hash) -- used to bind an adopted PR word to ITS OWN profile"""
    import hashlib
    h=hashlib.sha1(json.dumps([w.get('initial'),w.get('final'),w.get('program')],separators=(',',':'),default=str).encode()).hexdigest()
    return h
_FP={}
_FPLEN=set()      # SPEED: program lengths of the indexed words; a word whose length is not here cannot match any fingerprint (the fingerprint covers the program)
def _fingerprints():
    """fingerprint -> alias for every adopted data profile whose word is stored in words/<alias>.json.gz (lazy, cached).
    SPEED (Oct 28): per-alias fingerprints are memoised on disk in CACHE/fingerprints.json keyed by the sha256 of the word FILE BYTES (exact: the
    fingerprint is a function of the file content), so a command no longer decodes + re-dumps every adopted word (~0.45 s per tk command)."""
    if _FP.get('_done'): return _FP
    cf=CACHE+'/fingerprints.json'
    try: disk=json.load(open(cf))
    except Exception: disk={}
    dirty=False
    for al,p in DATA_PROFILES.items():
        wf=HERE+'/words/%s.json.gz'%al
        if os.path.exists(wf):
            try:
                raw=open(wf,'rb').read(); fs=hashlib.sha256(raw).hexdigest(); e=disk.get(al)
                if not(isinstance(e,list) and len(e)==3 and e[0]==fs):
                    w0=json.loads(gzip.decompress(raw)); e=disk[al]=[fs,word_fingerprint(w0),len(w0.get('program') or [])]; dirty=True
                _FP[e[1]]=al; _FPLEN.add(e[2])
            except Exception: pass
    if dirty:
        try:
            os.makedirs(CACHE,exist_ok=True); tmp='%s.%d.tmp'%(cf,os.getpid()); json.dump(disk,open(tmp,'w')); os.replace(tmp,cf)
        except Exception: pass
    _FP['_done']=True; return _FP
def exact_alias(w):
    """alias of the adopted PR word whose fingerprint equals w's, else None.  Same answer as _fingerprints().get(word_fingerprint(w)), but skips the
    full-program hash when no indexed word has w's program length (SPEED)."""
    fp=_fingerprints()
    if len(w.get('program') or []) not in _FPLEN: return None
    return fp.get(word_fingerprint(w))
_NOAL=object()
def data_profile_for(w,_al=_NOAL):
    """the adopted data profile OF THIS EXACT WORD if it is an adopted PR word (fingerprint match); otherwise the newest adopted profile of the word's family
    (public, owned_fields, retired roles, owned_fields key).  Exact match first so adopting a newer PR never changes how an older PR word resolves."""
    al=exact_alias(w) if _al is _NOAL else _al
    if al and al in DATA_PROFILES: return DATA_PROFILES[al]
    f=family_of(w); hit=[p for p in DATA_PROFILES.values() if all(p['family'].get(k)==v for k,v in f.items())]
    return max(hit,key=lambda p:p['pr']) if hit else None
def _legacy_auto(w):
    if legal.is_prepared(w): return 'p5612'
    if legal.has_of(w): return 'p5660'
    return PROFILE_BY_PUBLIC.get(len(w['initial']),'default')
LEGACY_FAMILIES={'default','p5599','p5612','p5660'}
def profile_of(w,override=None):
    """-> (name, params).  Order: override / TK_PROFILE; adopted data profile with `auto` set; the built-in profile of a known legacy family; the newest adopted data profile of the word's
    family; legacy 'default' (PR5545-family, public<=737) otherwise.  A word of an unknown family (e.g. public=745 with 9 owned roles) no longer silently gets 'default'."""
    name=override or os.environ.get('TK_PROFILE')
    if not name:
        ea=exact_alias(w); dp=data_profile_for(w,ea); leg=_legacy_auto(w); known_legacy=leg!='default' or len(w['initial'])<=737
        exact=bool(dp) and ea==dp['alias']
        name=dp['alias'] if dp and (exact or dp.get('auto') or not known_legacy) else leg
    if name not in PROFILES: raise SystemExit('tk: unknown profile %r (%s)'%(name,', '.join(PROFILES)))
    return name,PROFILES[name]
def side_of(T,P,pr,k=None,decay=None,reserve=None):
    """THE way to call X.side (TKHYG2): side constraints of invoice (T,P) under profile params `pr` (second element of profile_of(w)) -- decay, reserve AND the adopted (c,b,u) tail.
    Calling X.side directly with only decay/reserve silently uses the legacy 17/18/.2 tail and gives false FAIL verdicts on tail-profile words (#5907, #5827)."""
    r=X.side(T,P,k,decay=pr['decay'] if decay is None else decay,reserve=pr.get('reserve',1e-10) if reserve is None else reserve,**(pr.get('tail') or {}))
    if not r['ok'] and os.environ.get('TK_FREE_BOUNDS')=='1' and r['alpha']<1-(pr.get('reserve',1e-10) if reserve is None else reserve):
        # B0POLISH: user opted into free literals (TK_FREE_BOUNDS, set by the CLI/job env only): a word that needs a NEW tail (c,b,u) (every from-scratch word, e.g. SIGFUSE b0: tail 15/16/11/64) is judged at its best
        # free tail instead of the adopted PR's, otherwise every screen (prims/macros/k2sa/eval, which all gate on side_ok) rejects every neighbour of such a word.  Sound: tail_feasible requires c^64<b^63 and gamma,delta<D with D^128<1/16.
        m,t=X.tail_feasible(T,P,k)
        if m>0: r=dict(r,ok=True,gamma=t['gamma'],delta=t['delta'],free_tail=dict(c=t['c'],b=t['b'],u=t['u']))
    return r
@__import__('contextlib').contextmanager
def use_profile(name):
    """pin TK_PROFILE (and, for a data profile, TK_VERIFIER_PROFILE = its JSON, read by legal.profile_params) for the duration; restores the environment"""
    old={k:os.environ.get(k) for k in ('TK_PROFILE','TK_VERIFIER_PROFILE')}
    try:
        if name: os.environ['TK_PROFILE']=name
        if name in DATA_PROFILES: os.environ['TK_VERIFIER_PROFILE']=DATA_PROFILES[name]['_file']
        yield
    finally:
        for k,v in old.items():
            if v is None: os.environ.pop(k,None)
            else: os.environ[k]=v
_load_data_profiles()

def native_mod():
    """initialised native pair checker: fastnative (numpy, bit-exact vs the pinned vendor code; default) or, with TK_NATIVE_REF=1 / --native-ref,
    the reference infra/native_pair.py running the unmodified vendor kernels.  Both expose ok(a,b)."""
    if os.environ.get('TK_NATIVE_REF')=='1':
        import native_pair as N
    else:
        import fastnative as N
    N.init(closure_root()); return N
def native_is_ref(): return os.environ.get('TK_NATIVE_REF')=='1'

# ---- canonical word serialisation (HYGIENE; mirrors ext/PKGPREP/normalise.py dump): sorted keys, indent 2, trailing newline, gzip mtime 0, MOVE private flags JSON bool
def normalise_flags(w):
    """MOVE private flag int 0/1 -> bool, in place (only 0/1 allowed); returns w"""
    for e in w.get('program',()):
        if e[0]=='MOVE' and len(e)>4 and type(e[4]) is int:
            assert e[4] in (0,1),e; e[4]=bool(e[4])
    return w
def canonical_bytes(w,gz=True):
    raw=(json.dumps(normalise_flags(w),sort_keys=True,indent=2)+'\n').encode()
    return gzip.compress(raw,mtime=0) if gz else raw
def save_canonical(w,path):
    open(path,'wb').write(canonical_bytes(w,gz=str(path).endswith('.gz')))
