"""bitadapt: BIT-side adapter for tk (adopt / price / accept / check on G20 local words).  [BITADAPT]
`tk adopt N` on a BIT package (ORDINARY-RESULT.json + WORD with start/final/records/owned) vendors the package (hash-pinned) into profiles/bitN/pkg and writes profiles/bitN.json (kind=bit).
tk price|accept|check WORD (WORD = alias bitN or a path whose JSON has records+owned) are routed here from tk.py.  accept = the PR's OWN pipeline in an isolated process (bitworker.py)."""
import sys,os,json,gzip,subprocess,tempfile,shutil,hashlib,time,re
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
PROFDIR=HERE+'/profiles'
PY12='/opt/homebrew/bin/python3.12'
SRC=os.path.dirname(os.path.abspath(__file__)) + '/ext/TKAUDIT/src/g.git'
import bitword,bitval
from fractions import Fraction as F
def git(*a,text=False):
    r=subprocess.run(['git','--git-dir='+SRC]+list(a),capture_output=True,timeout=280)
    if r.returncode: raise SystemExit('tk adopt (bit): git %s failed: %s'%(' '.join(a[:3]),r.stderr.decode()[-300:]))
    return r.stdout.decode() if text else r.stdout
def sha_tree(d):
    out={}
    for root,_,fs in os.walk(d):
        for f in sorted(fs):
            p=os.path.join(root,f)
            if '__pycache__' in p or p.endswith('.pyc'): continue
            out[os.path.relpath(p,d)]=hashlib.sha256(open(p,'rb').read()).hexdigest()
    return out
def detect_package(commit,pkg=None):
    """the research/<dir> whose WORD the head commit touched last (adopt.find_package), if it carries ORDINARY-RESULT.json and a records+owned WORD, else None"""
    import adopt
    try: c=pkg or adopt.find_package(commit)
    except SystemExit: return None
    names=git('ls-tree','-r','--name-only',commit+':'+c,text=True).splitlines()
    return c if 'ORDINARY-RESULT.json' in names and ('WORD.json.gz' in names or 'WORD.json' in names) else None
def is_bit_pr(pr,head=None):
    import adopt
    try: ref,commit=adopt.fetch(pr,head)
    except SystemExit: return None
    pkg=detect_package(commit); return (ref,commit,pkg) if pkg else None
def recipe_of(files):
    if 'global_retirement.py' in files and 'native.py' in files and 'integration.py' in files: return 'conj'
    if 'local_relations.py' in files and 'global_relations.py' in files and 'verify.py' in files: return 'nine'
    return None
def adopt_bit(pr,head=None,alias=None,say=print,do_accept=True):
    ref,commit,pkg=is_bit_pr(pr,head); alias=alias or 'bit%d'%pr
    dest=PROFDIR+'/%s'%alias; shutil.rmtree(dest,ignore_errors=True); os.makedirs(dest+'/pkg')
    tar=subprocess.run(['git','--git-dir='+SRC,'archive',commit,pkg],capture_output=True,timeout=280).stdout
    p=subprocess.run(['tar','-x','-C',dest,'-f','-'],input=tar,capture_output=True); 
    shutil.move(dest+'/'+pkg,dest+'/pkgx'); shutil.rmtree(dest+'/pkg'); os.rename(dest+'/pkgx',dest+'/pkg'); shutil.rmtree(dest+'/research',ignore_errors=True)
    pk=dest+'/pkg'; files=set(os.listdir(pk)); recipe=recipe_of(files)
    if not recipe: raise SystemExit('tk adopt (bit): package %s has no known verifier layout (got %s)'%(pkg,sorted(files)[:20]))
    inv=json.load(open(pk+'/INVOICE.json')); o=json.load(open(pk+'/ORDINARY-RESULT.json'))
    fr=None
    for root,_,fs in os.walk(pk):
        if 'FRAMES.json' in fs: fr=os.path.relpath(root+'/FRAMES.json',pk); break
    calls=len(json.load(open(pk+'/CALLS.json'))); w=bitword.load(pk+'/WORD.json.gz')
    prior=None
    if os.path.exists(pk+'/prior/ORDINARY-RESULT.json'): prior=json.load(open(pk+'/prior/ORDINARY-RESULT.json'))['admitted']
    prof=dict(schema='tk-profile/bit1',kind='bit',alias=alias,pr=pr,head=commit,ref=ref,package=pkg,recipe=recipe,calls=calls,frames_file=fr,
              word=dict(registers=len(w['start']),records=len(w['records']),owned=len(w['owned'])),
              ordinary=dict(chain=('q8x3' if recipe=='nine' else 'fine5'),grid=15,prior_admitted=prior,admitted=o['admitted'],status=o['status'],raw_lower=o['raw_crossing_independent_exact']['lower']['saving'],raw_upper=o['raw_crossing_independent_exact']['upper']['saving']),
              invoice=inv,pins=sha_tree(pk),verifier=dict(python=PY12,entry='bitworker.py'))
    json.dump(prof,open(PROFDIR+'/%s.json'%alias,'w'),indent=1,default=str)
    say('adopted %s: PR%d %s recipe=%s, %d registers, %d records, calls %d, admitted %s'%(alias,pr,pkg,recipe,prof['word']['registers'],prof['word']['records'],calls,o['admitted']))
    ctx=bitword.Ctx(alias); pr_=bitword.price(w,ctx); say('tk price: raw %s admitted %s (published %s) %s'%(bitval.mp.nstr(pr_['raw'],17),float(pr_['admitted']),o['admitted'],'MATCH' if str(pr_['admitted'])==o['admitted'] else 'MISMATCH'))
    if do_accept:
        r=accept(alias,pk+'/WORD.json.gz',patched=False); say('tk accept (unpatched PR pipeline): '+fmt(r))
    return prof
def accept(alias,wordpath,patched=True,keep=False):
    prof=json.load(open(PROFDIR+'/%s.json'%alias)); pk=PROFDIR+'/%s/pkg'%alias
    pins=bitsha=sha_tree(pk)
    if pins!=prof['pins']: return dict(ok=False,stage='pins',error='vendored package changed since adopt: %s'%[k for k in set(pins)|set(prof['pins']) if pins.get(k)!=prof['pins'].get(k)][:5])
    tmp=tempfile.mkdtemp(prefix='bitstack-'); d=tmp+'/p'
    try:
        shutil.copytree(pk,d)
        shutil.copy(wordpath,d+'/WORD.json.gz') if open(wordpath,'rb').read(2)==b'\x1f\x8b' else bitword.save(bitword.load(wordpath),d+'/WORD.json.gz')
        env={'PATH':'/usr/bin:/bin','HOME':tmp,'PYTHONDONTWRITEBYTECODE':'1','BITTK_HERE':HERE}
        r=subprocess.run([PY12,'-I','-B',HERE+'/bitworker.py',d,prof['recipe'],'1' if patched else '0'],capture_output=True,text=True,env=env,cwd=tmp,timeout=600)
        try: res=json.loads(r.stdout.split('@@RESULT@@',1)[1])
        except Exception: return dict(ok=False,stage='worker',error=(r.stderr or r.stdout)[-500:])
        if not patched and res.get('ok'):
            same=[]; 
            for fn in ('INVOICE.json','ORDINARY-RESULT.json','INDEPENDENT-RESULT.json','GLOBAL-RESULT.json'):
                if not (os.path.exists(d+'/'+fn) and os.path.exists(pk+'/'+fn)): continue
                a=json.load(open(d+'/'+fn)); b=json.load(open(pk+'/'+fn))
                if fn=='GLOBAL-RESULT.json': a.pop('CPU_seconds',None); b.pop('CPU_seconds',None)
                same.append((fn,a==b))
            res['reproduces']=same
        return res
    finally:
        if not keep: shutil.rmtree(tmp,ignore_errors=True)
def fmt(r):
    if not r.get('ok'): return 'FAIL stage=%s: %s'%(r.get('stage'),r.get('error'))
    s='OK admitted %s (%.15f) local paid %s [%ss]'%(r['admitted'],float(F(r['admitted'])),r.get('local_paid'),r.get('seconds'))
    if 'reproduces' in r: s+='  reproduces published receipts: %s'%dict(r['reproduces'])
    return s
# ---------- tk routing ----------
def alias_of(spec):
    if re.fullmatch(r'bit\d+',spec) and os.path.exists(PROFDIR+'/%s.json'%spec): return spec,PROFDIR+'/%s/pkg/WORD.json.gz'%spec
    return None,None
def sniff(spec):
    a,p=alias_of(spec)
    if a: return a,p
    if os.path.isfile(spec):
        try:
            w=bitword.load(spec)
            if bitword.is_bit(w): return os.environ.get('TK_BIT_PROFILE','bit5708'),os.path.abspath(spec)
        except Exception: pass
    return None,None
def default_profile(): return os.environ.get('TK_BIT_PROFILE','bit5708')
def dispatch(a):
    """-> exit code if handled, else None"""
    c=a.cmd
    if c=='adopt' and getattr(a,'pr',None) and not a.list:
        if is_bit_pr(a.pr,a.head):
            adopt_bit(a.pr,a.head,a.alias,do_accept=not a.no_accept); return 0
        return None
    if c in('price','accept','check') and getattr(a,'word',None):
        alias,path=sniff(a.word)
        if not alias: return None
        ctx=bitword.Ctx(alias); w=bitword.load(path)
        if c=='check':
            V=bitword.check(w,ctx,getattr(a,'max',50))
            for v in V: print('VIOLATION %s @%s: %s'%v)
            print('LEGAL (fast oracle)' if not V else '%d violation(s)'%len(V)); return 1 if V else 0
        if c=='price':
            p=bitword.price(w,ctx); V=bitword.check(w,ctx,5)
            if getattr(a,'json',False): print(json.dumps(dict(raw=str(p['raw']),admitted=str(p['admitted']),P=p['P'],T=p['T'],legal=not V),default=str))
            else:
                print('BIT word %s (%s): legal(fast)=%s'%(os.path.basename(path),alias,not V))
                print('raw crossing %s   admitted %s = %.15f   rank surplus %d'%(bitval.mp.nstr(p['raw'],17),p['admitted'],float(p['admitted']),p['surplus']))
                print('local paid %s   global paid %s'%(dict(sorted(bitword.local_paid(w).items())),dict(sorted(p['P'].items()))))
            return 0
        r=accept(alias,path,patched=(os.path.abspath(path)!=os.path.abspath(PROFDIR+'/%s/pkg/WORD.json.gz'%alias)))
        print(fmt(r)); 
        if getattr(a,'json',False): print(json.dumps(r,default=str)[:4000])
        return 0 if r.get('ok') else 1
    return None
