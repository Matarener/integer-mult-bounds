"""synth.backgen_measure -- measurement helpers for GENBACK: build a generated word per back method, exact kappa, cost-class ablation (diagnostic invoice arithmetic).
python -B synth/backgen_measure.py [method ...]   (TK_FREE_BOUNDS=1 is set; single core ~25 s per method)"""
import sys,os,collections,time
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE)); sys.path.insert(0,HERE)
from tkcommon import *
import dag as D, incr, price_exact as PX
from synth import sample as SM, gen as G, frontgen as FG
def build(method,anchor='5756'):
    spec=SM.anchor_spec(anchor,anchor); spec=dict(spec,front='generated',back='generated:'+method); spec.pop('body',None)
    w,info=G.build_word(spec); return w,info
def invoice_without(w,drop_regs):
    """kappa of the word's own invoice with all paid MOVEs and credits of the given registers removed"""
    n=len(w['initial']); fr=w['frames']; dim=[len(b) for b in fr]; T=collections.Counter(PX.TOUT); P=collections.Counter(PX.POUT)
    for e in w['program']:
        if e[0]=='MOVE' and e[1] not in drop_regs: P[abs(dim[e[3]]-dim[e[2]])]+=PX.CALLS
    live=set(w['live'])
    for r in range(n):
        if r in live or r-112 in live: continue
        if r not in drop_regs: T[dim[w['final'][r]]-dim[w['initial'][r]]]+=PX.CALLS
    return PX.kappa(dict(T),dict(P))
def main(methods):
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    for me in methods:
        t=time.time(); w,info=build(me)
        iw=incr.IncrWord(w,profile='5756'); roles=info['roles']
        print('%-9s legal %s viol %d badpairs %d  kappa %.12f  helpers %d  (copies %d)  %.0fs'%(me,iw.legal_all,len(iw.viol),len(iw.bad_pairs),iw.kappa,info['helpers'],info['copies'],time.time()-t),flush=True)
        # ablations are DIAGNOSTIC (the word minus these helpers is not a word)
        allh=set(sum(roles.values(),[]))
        for nm in('resid','carrier','copy','T'):
            print('   without %-8s: kappa %.10f'%(nm,invoice_without(w,set(roles[nm]))))
        print('   without ALL helpers: kappa %.10f'%invoice_without(w,allh))
if __name__=='__main__': main(sys.argv[1:] or ['star','dilworth'])
