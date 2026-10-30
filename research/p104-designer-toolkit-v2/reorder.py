"""tk reorder WORD [--k K] [--maxm M] [--tl S] [--out F] [--window LO HI] [--wait] [--inline]
Event-ORDER + frame retime (relat.py; evlat generalised).  Events that commute -- reads of one register, additive writes into one register (ADD(t,s): R on s, W on t) -- may change places
(epoch model, see relat.py docstring) while each ADD/COPY event gets its own frame, MOVEs are re-inserted, helper starts/finals are free.  Barriers: SCALE/INIT/CLEAR/COPY and every event touching an owned register.
CP-SAT maximises the linearised kappa; cyclic global orders are cut lazily; the realised word is re-checked with legal.check and re-priced exactly (then run `tk check --native`).
--window LO HI pins everything outside the touched events/registers (small, fast; acceptance tests use it).  Published/rediscovered: see COMMREAD/NOTES.md."""
import sys,os
from tkcommon import *
def main(a):
    path,w=load(a.word)
    tag=a.word if a.word in ALIASES else os.path.basename(path).split('.')[0]
    out=a.out or '%s/%s__reorder_k%d_m%d%s.json.gz'%(OUT,tag,a.k,a.maxm,('_w%d_%d'%tuple(a.window)) if a.window else '')
    os.makedirs(os.path.dirname(out),exist_ok=True)
    argv=[PY,'-B',HERE+'/relat.py',path,out,str(a.tl),str(a.k),str(a.maxm)]+([str(x) for x in a.window] if a.window else [])
    name=a.name or 'tk_reorder_%s_k%d_m%d%s'%(sha(path)[:8],a.k,a.maxm,('_w%d_%d'%tuple(a.window)) if a.window else '')
    if a.inline:
        import subprocess; return subprocess.run(argv).returncode
    ok=submit(name,a.tl*30+900,argv,a.wait,threads=4)
    print('log: %s/jobs/%s.log   output: %s'%(W,name,out))
    if a.wait: print(open(W+'/jobs/%s.log'%name).read()[-1500:])
    return 0
