"""REAL verifier stack on a candidate word (unmodified PR5544/5545 local.py replay + reverse_columns + native, physical caller, PR5551's pricing.py with
census/claim literals patched).  Generalises infra/realcheck.py: word with N public registers != 735 gets the literal-only local.py patch
that #5553 shipped (735->N, 743->N+8).   usage: real.py WORD [--out RESULT.json] [--stages]   (heavy: run via hq.sh; ~3-6 min)
Result JSON: stage -> ok/err; on failure `error` = the rejecting need() message (rule string) of the real code and the stage that raised it."""
import sys,os,json,gzip,time,re,types,traceback
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
from fractions import Fraction as Q
from tkcommon import closure_root,INFRA,CACHE
ROOT=closure_root()
CTRL=ROOT+'/research/p104-productive-controller'
def local_for(n):
    import importlib.util
    src=open(CTRL+'/local.py').read()
    if n!=735:
        d=n-735
        tab=[("'public':735","'public':%d"%n),('range(743)','range(%d)'%(n+8)),('0 <= r < 743','0 <= r < %d'%(n+8)),('r >= 735 and r not in live_owned','r >= %d and r not in live_owned'%n),
             ('0 <= s < 743','0 <= s < %d'%(n+8)),('current[:735]','current[:%d]'%n),('if r < 735 else','if r < %d else'%n),('All 743 public','All %d public'%(n+8)),
             ('for r in range(735) if r not in main','for r in range(%d) if r not in main'%n),("'public_inputs':735","'public_inputs':%d"%n),('743*743','%d*%d'%(n+8,n+8)),
             ('n = 743','n = %d'%(n+8)),('if r < 735:','if r < %d:'%n),('for r in range(735):','for r in range(%d):'%n)]
        for a,b in tab:
            if a not in src: raise SystemExit('local.py literal missing: '+a)
            src=src.replace(a,b)
    tmp=CACHE+'/local_%d_%d.py'%(n,os.getpid()); os.makedirs(CACHE,exist_ok=True); open(tmp,'w').write(src)
    spec=importlib.util.spec_from_file_location('local',tmp); L=importlib.util.module_from_spec(spec); sys.modules['local']=L; spec.loader.exec_module(L)
    L.ROOT=__import__('pathlib').Path(ROOT); return L
def patched_price(L,kappa_str,sumT,sumP,surplus,tested):
    src=open(HERE+('/inputs/pr5551-pricing.py' if os.path.exists(HERE+'/inputs/pr5551-pricing.py') else '/real/pr5551-pricing.py')).read()
    for pat,rep in((r"KAPPA, TESTED = Q\('[^']*'\), Q\('[^']*'\)","KAPPA, TESTED = Q('%s'), Q('%s')"%(kappa_str,tested)),
                   (r"sum\(targets.values\(\)\) == \d+ and sum\(paid.values\(\)\) == \d+","sum(targets.values()) == %d and sum(paid.values()) == %d"%(sumT,sumP)),
                   (r"== 760,","== %d,"%surplus)):
        src,k=re.subn(pat,rep,src)
        if k!=1: raise SystemExit('pricing template literal count %d for %s'%(k,pat))
    m=types.ModuleType('price_patched'); m.__dict__['__file__']=HERE+'/real/pricing_patched.py'; exec(compile(src,'price_patched','exec'),m.__dict__); return m
def stages(path,upto='price',out=None):
    sys.path.insert(0,INFRA_DIR)
    import legal,price_exact as X
    w=legal.load(path); n=len(w['initial']); res=dict(word=os.path.basename(path),public=n,stages={}); t0=time.time()
    def done(): 
        if out: json.dump(res,open(out,'w'),indent=1,default=str)
    def stage(name,fn):
        try: v=fn(); res['stages'][name]=dict(ok=True,seconds=round(time.time()-t0)); done(); return v
        except BaseException as e:
            res['stages'][name]=dict(ok=False,error=str(e)[:400] or repr(e)); res['error']='%s: %s'%(name,str(e)[:400]); done(); return None
    L=local_for(n)
    local=stage('replay',lambda:L.replay(w))
    if local is None: return res
    res['paid']=local['paid']; res['helpers']=local['helpers']
    if upto=='replay': return res
    if stage('reverse_columns',lambda:L.reverse_columns(w)) is None: return res
    native=stage('native',lambda:L.native(w))
    if native is None: return res
    res['native_maps']=native['distinct_maps']
    if upto=='native': return res
    import caller as C
    ctl=stage('controller',lambda:C.construct()); 
    if ctl is None: return res
    phys=stage('physical',lambda:C.physical(ctl,w))
    if phys is None: return res
    rep=legal.check(w); T,Pp=X.invoice(rep); k=X.kappa(T,Pp)
    kstr='%.9f'%(k-5e-9-2e-9); tested=str(Q(kstr)+Q(5,10**9)) if False else '%.10f'%(float(kstr)+5e-9)
    sumP=sum(Pp.values()); surplus=sum(r*c for r,c in T.items())-sum(r*c for r,c in Pp.items())
    res['claim']=dict(KAPPA=kstr,TESTED=tested,sumT=sum(T.values()),sumP=sumP,surplus=surplus)
    def price():
        P=patched_price(L,kstr,sum(T.values()),sumP,surplus,tested); r=P.run(local,native,ctl,phys)
        lo,hi=r['raw_root_interval']; res['interval']=[lo,hi]; res['crossing_lo']='%.14f'%float(Q(lo)); res['crossing_hi']='%.14f'%float(Q(hi))
        res['outer_checks']=(len(r['outer']['strict_checks']),len(r['outer']['functional_checks'])); res['productive_fields']=r['productive_fields']; res['paid_calls']=r['paid_calls']
        return r
    stage('price.run',price); done(); return res
INFRA_DIR=INFRA
if __name__=='__main__':
    a=sys.argv; path=os.path.abspath(a[1]); out=a[a.index('--out')+1] if '--out' in a else None
    sys.path.insert(0,CTRL)
    upto=a[a.index('--upto')+1] if '--upto' in a else 'price'
    r=stages(path,upto=upto,out=out); print(json.dumps(r,indent=1,default=str))
