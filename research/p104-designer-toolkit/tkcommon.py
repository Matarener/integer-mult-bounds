"""tk shared helpers: paths, word aliases, caching, role names.  Imports the infra modules (single source of truth)."""
import sys,os,gzip,json,hashlib,time
HERE=os.path.dirname(os.path.abspath(__file__))
# Workspace mode (intmult-work checkout) or package mode (research/p104-designer-toolkit: infra/ and inputs/ next to this file).
_WS=os.environ.get('TK_WORKSPACE','')      # optional research-workspace checkout (heavy-job queue, S4GEN, PRICE8 trees); unset in the package
PACKAGE=os.path.isdir(HERE+'/infra') or not _WS
W=HERE if PACKAGE else _WS
INFRA=HERE+'/infra' if PACKAGE else _WS+'/cards/WILD/DESIGNER/infra'
for p in (INFRA,HERE):
    if p not in sys.path: sys.path.insert(0,p)
sys.dont_write_bytecode=True
import legal,price_exact as X
PY=sys.executable if PACKAGE else _WS+'/venv/bin/python'
if PACKAGE:     # never write into the checkout
    import tempfile
    W=os.environ.get('TK_WORK') or os.path.join(tempfile.gettempdir(),'p104-designer-toolkit-work')
    os.makedirs(W,exist_ok=True)
CACHE=W+'/cache' if PACKAGE else HERE+'/.cache'
OUT=W+'/out' if PACKAGE else HERE+'/out'
ALIASES={a:HERE+'/words/%s.json.gz'%a for a in ('5545','5551','5553','5561','5561s')}
# published crossing intervals (lo,hi) of the shipped words, from RESULT.json / VERIFY of each package
EXPECT={'5545':'.00304117181649','5551':'.00304153116715','5553':'.0030428242','5561':'.0030814243','5561s':'.0030768800'}
def resolve(spec):
    """alias (5551, 5553, 5561, 5561s, 5545, 5553A) or a path to WORD.json[.gz]"""
    if spec in ALIASES: return ALIASES[spec]
    if os.path.exists(spec): return os.path.abspath(spec)
    raise SystemExit('tk: no such word %r (aliases: %s)'%(spec,', '.join(ALIASES)))
def sha(path):
    return hashlib.sha256(open(path,'rb').read()).hexdigest()
def load(spec):
    p=resolve(spec); return p,legal.load(p)
def cache_get(kind,path):
    f='%s/%s_%s.json'%(CACHE,kind,sha(path)[:16])
    if os.path.exists(f):
        try: return json.load(open(f)),f
        except Exception: pass
    return None,f
def cache_put(f,obj):
    os.makedirs(CACHE,exist_ok=True); json.dump(obj,open(f,'w'),indent=1,default=str)
def roles(w):
    """role(r) -> 'X' live source, 'Y' target (r+112), 'helper', 'owned' (scratch, r>=len(initial))"""
    live=set(w['live']); n=len(w['initial'])
    def role(r):
        if r in live: return 'X'
        if r-112 in live and r<n: return 'Y'
        return 'helper' if r<n else 'owned'
    return role
def dimstr(w,f): return '%s(dim %d)'%(f,len(w['frames'][f])) if f is not None else 'None'

def closure_root():
    """root holding research/p104-productive-controller/ (the byte-pinned PR5545 source capsule): the workspace tree, or the package's own tarball extracted once into .cache/"""
    if not PACKAGE: return _WS+'/cards/WILD/AUDIT5544/src/r'
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
    """queue a heavy job through W/bin/hq.sh (<=4 workers machine-wide; hq blocks until a slot is free, then returns).  wait=True polls for jobs/NAME.done (bounded by TL+120)."""
    import subprocess
    env=dict(os.environ,THREADS=str(threads),HEAVY_THREADS=str(threads))
    if PACKAGE or not os.path.exists(W+'/bin/hq.sh'):      # no job queue: run synchronously in this process tree
        os.makedirs(W+'/jobs',exist_ok=True); lg=W+'/jobs/%s.log'%name
        with open(lg,'w') as f: rc=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=TL+60).returncode
        open(W+'/jobs/%s.done'%name,'w').close(); print('job %s finished rc=%d, log %s'%(name,rc,lg)); return rc==0
    r=subprocess.run([W+'/bin/hq.sh',name,str(int(TL))]+argv,capture_output=True,text=True,env=env)
    print((r.stdout+r.stderr).strip())
    if not wait: return None
    t0=time.time(); done=W+'/jobs/%s.done'%name
    while time.time()-t0<TL+120 and not os.path.exists(done): time.sleep(poll)
    return os.path.exists(done)
