"""k2.engine -- driver for the unified k2net search engine (k2/k2.cpp + k2search.inc + k2grow.inc + k2frames.inc).  Scope [toolkit, unified k2net search engine + automation].
Every move family and option is a RUNTIME flag (env K2S_*, see OPTS below); one binary.  No side effects at import (nothing in os.environ is touched: options go to the child env only).
API: build(force=False) -> binary path; run(net, mode='sa', opts=None, timeout=None, out=None) -> dict(lines, final, best_kappa, ...)."""
import os,sys,subprocess,re,time
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=[os.path.join(HERE,f) for f in ('k2.cpp','k2net.inc','k2search.inc','k2grow.inc','k2frames.inc','k2phi.inc','k2levers.inc')]
MOVES=('shift','mshift','ret','cadd','cdel','kill','ins','split','rehost','hubsw','relab','lift','hubpl','killsw','hop','kslide','fnew','own','lbirth','eend')
# runtime options (all optional): name -> env var.  weights: dict move->weight or comma string in MOVES order.
OPTS={'seed':'K2S_SEED','iters':'K2S_ITERS','secs':'K2S_SECS','t0':'K2S_T0','t1':'K2S_T1','cap':'K2S_CAP','peel':'K2S_PEEL','peelv':'K2S_PEELV','neut':'K2S_NEUT','evpen':'K2S_EVPEN','evt':'K2S_EVT',
      'hop7':'K2S_HOP','hopkill':'K2S_HOPKILL','hopk':'K2S_HOPK','xr':'K2S_XR','rec':'K2S_REC','focus':'K2S_FOCUS','focusp':'K2S_FOCUSP','free':'K2S_FREE','cost':'K2S_COST',
      'out':'K2S_OUT','log':'K2S_LOG','dumpevery':'K2S_DUMPEVERY','ktries':'K2S_KTRIES','samples':'K2S_SAMPLES','tlist':'K2S_TLIST','ttries':'K2S_TTRIES','tmin':'K2S_TMIN',
      'fullverify':'K2S_FULLVERIFY','profile':'K2S_PROFILE','peak':'K2S_PEAK','ownnew':'K2S_OWNNEW','prel':'K2S_PREL',
      'phi':'K2S_PHI','phiw':'K2S_PHIW','phip':'K2S_PHIP','phitau':'K2S_PHITAU','phia':'K2S_PHIA','flog':'K2S_FLOG','flogn':'K2S_FLOGN','fsnap':'K2S_FSNAP'}   # HEURISTICS: potentials (default OFF)   # K2FRAMES: owned peak cap (default = input peak), new owned ids allowed, relay-instead-of-follow prob
def binpath(): return os.path.join(HERE,'bin','k2u')
def build(force=False,flags=('-O2',)):
    b=binpath(); os.makedirs(os.path.dirname(b),exist_ok=True)
    if not force and os.path.exists(b) and os.path.getmtime(b)>=max(os.path.getmtime(s) for s in SRC): return b
    tmp=b+'.%d.tmp'%os.getpid(); import shutil; cxx=os.environ.get('CXX') or shutil.which('clang++') or shutil.which('g++') or 'c++'
    r=subprocess.run([cxx,*flags,'-std=c++17','-o',tmp,SRC[0]],capture_output=True,text=True,cwd=HERE)
    if r.returncode: raise RuntimeError('k2 build failed: '+r.stderr[-2000:])
    os.replace(tmp,b); return b
def env_for(net,mode,opts):
    e=dict(os.environ); e['K2_NET']=net; e['K2_SEARCH']=mode
    for k,v in (opts or {}).items():
        if k=='weights':
            if isinstance(v,dict): v=','.join(str(v.get(m,{'shift':1,'mshift':1,'ret':1,'cadd':.5,'cdel':.5,'kill':2,'ins':.5,'split':.2,'rehost':2}.get(m,0))) for m in MOVES)
            e['K2S_W']=v
        elif k in OPTS:
            if v is False or v is None: continue
            e[OPTS[k]]=str(int(v)) if v is True else str(v)
        else: raise KeyError('unknown k2 option '+k)
    return e
_NUM=r'([-+0-9.eE]+)'
def run(net,mode='sa',opts=None,timeout=None,binary=None):
    b=binary or build(); t0=time.time()
    r=subprocess.run([b],env=env_for(net,mode,opts),capture_output=True,text=True,timeout=timeout)
    lines=r.stdout.splitlines(); res={'rc':r.returncode,'lines':lines,'sec':time.time()-t0,'stderr':r.stderr[-500:]}
    for ln in lines:
        m=re.match(r'INPUT ok=(\d) why=(\S+) .* kappa '+_NUM+' R0 '+_NUM+r'.* nev (\d+)',ln)
        if m: res['input']={'ok':bool(int(m.group(1))),'kappa':float(m.group(3)),'R0':float(m.group(4)),'nev':int(m.group(5))}
        m=re.match(r'FINAL kappa '+_NUM+' R0 '+_NUM+r' nev (\d+) \| best kappa '+_NUM+' R0 '+_NUM,ln)
        if m: res['final']=float(m.group(1)); res['nev']=int(m.group(3)); res['best_kappa']=float(m.group(4)); res['best_R0']=float(m.group(5))
    return res
if __name__=='__main__':
    print(build(force='--force' in sys.argv))
