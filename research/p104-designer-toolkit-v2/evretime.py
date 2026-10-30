"""tk evretime WORD [--k K] [--maxm M] [--tl S] [--out F] [--wait] [--inline]
Event-level exact lattice retime with FREE ADD PLACEMENT (MODELERR2/ev_lat.py): every ADD/COPY event gets its own frame variable (not one per stage cluster), MOVEs are re-inserted
wherever consecutive frames differ.  Candidate frames per event = native frames of the nodes within +-K on its partners' timelines plus the L/U anchor bounds; with MAXM > 0 all subspaces
between L and U are enumerated when dim(U/L) <= MAXM.  CP-SAT maximises the linearised kappa; the realised word is re-checked with legal.check and re-priced exactly.
Published (on #5561): K=2 MAXM=0 OPTIMAL, exact kappa .003081500768 (+7.6e-8, the stop-placement gain is real but tiny); K=2 MAXM=3 FEASIBLE .003081518091 (+9.4e-8)."""
import sys,os,re
from tkcommon import *
def main(a):
    path,w=load(a.word)
    out=a.out or '%s/%s__evlat_k%d_m%d.json.gz'%(OUT,a.word if a.word in ALIASES else os.path.basename(path).split('.')[0],a.k,a.maxm)
    os.makedirs(os.path.dirname(out),exist_ok=True)
    argv=[PY,'-B',HERE+'/evlat.py',path,out,str(a.tl),str(a.k),str(a.maxm)]
    name=a.name or 'tk_evlat_%s_k%d_m%d'%(sha(path)[:8],a.k,a.maxm)
    if a.inline:
        import subprocess; return subprocess.run(argv).returncode
    ok=submit(name,a.tl+900,argv,a.wait,threads=4)
    print('log: %s/jobs/%s.log   output: %s'%(W,name,out))
    if a.wait: print(open(W+'/jobs/%s.log'%name).read()[-1500:])
    return 0
