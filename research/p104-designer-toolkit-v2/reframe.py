"""tk reframe WORD [--k K] [--maxm M] [--tl S] [--out F] [--wait] [--inline]
Exact frame re-assignment of a legal word (frames.assign: event-level lattice CP-SAT, never worse than the input; module docstring).  Queued through hq (2 threads) unless --inline."""
import os
from tkcommon import *
def main(a):
    path,w=load(a.word)
    out=a.out or '%s/%s__reframe.json.gz'%(OUT,a.word if a.word in ALIASES else os.path.basename(path).split('.')[0])
    os.makedirs(os.path.dirname(out),exist_ok=True)
    argv=[PY,'-B',HERE+'/frames.py',path,out,str(a.tl),str(a.k),str(a.maxm)]
    if a.inline:
        import subprocess; return subprocess.run(argv).returncode
    name=a.name or 'tk_reframe_%s'%sha(path)[:8]
    submit(name,a.tl+900,argv,a.wait,threads=2)
    print('log: %s/jobs/%s.log   output: %s'%(W,name,out))
    if a.wait: print(open(W+'/jobs/%s.log'%name).read()[-1500:])
    return 0
