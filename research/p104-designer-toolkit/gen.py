"""tk gen [PRESET] [--realise] [--wait] [--tag T] [--env K=V ...]
Whole-window schedule generator for realise6 (S4GEN/GENX): from the CHAINS of a host word (#4610, window B = ops [11600,15273)) alone, with NO layout input, rebuild the hub partition
(event DAG, class-merge by (frame, reverse depth), cycle-checked) and score it: hub count, chain cost, forward/backward monomial-support misses.
Preset full0 (S4GEN GENFULL2, CLASSMERGE=1 NEGD=1 RDIM=0 LMIN=99 KEEP0=0 SUCC=0): published 921 hubs (native 929), chain cost = native 4010.092015 (d 0.000000), filter miss fw 0 bw 0.
Default is the partition-only check (about 1 s).  --realise additionally runs realise6 (published REALISE OK, 0 backtracks, ~220 s) through hq.
Workspace-only (TK_WORKSPACE): it drives cards/WILD/S4GEN (gen_run3.py, dagen2.py + FULLCALL/BCOMP/realise6/recheck and the #4610 word), which are not part of the package."""
import sys,os,re,subprocess
from tkcommon import *
S4=W+'/cards/WILD/S4GEN'
PRESETS={'full0':dict(CLASSMERGE='1',NEGD='1',RDIM='0',LMIN='99',KEEP0='0',SUCC='0')}
def main(a):
    if PACKAGE or not os.path.isdir(S4): raise SystemExit('tk gen: needs the workspace S4GEN tree (#4610 window-B inputs); not available in package mode')
    if a.preset not in PRESETS: raise SystemExit('tk gen: unknown preset %r (%s)'%(a.preset,', '.join(PRESETS)))
    env=dict(os.environ,**PRESETS[a.preset],REALISE='1' if a.realise else '0')
    for kv in a.env: k,v=kv.split('=',1); env[k]=v
    tag=a.tag or 'tk_'+a.preset
    argv=[W+'/venv/bin/python','-I',S4+'/gen_run3.py','g1',tag]
    if a.realise:
        name='tk_gen_'+tag; env_prefix=['env']+['%s=%s'%(k,env[k]) for k in PRESETS[a.preset]]+['REALISE=1']+a.env
        ok=submit(name,1800,['bash','-c','cd %s && %s'%(S4,' '.join(env_prefix+argv))],a.wait,threads=2)
        print('log: %s/jobs/%s.log   (S4GEN/out/%s.json.gz on success)'%(W,name,tag)); return 0
    r=subprocess.run(argv,capture_output=True,text=True,env=env,cwd=S4); o=r.stdout+r.stderr; print(o.rstrip())
    return r.returncode
