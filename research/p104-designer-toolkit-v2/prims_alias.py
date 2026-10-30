"""prims_alias -- P14 ALIAS primitive (ALIAS.  Replace a helper H (the VICTIM) by an existing helper H' (the KEEPER) of identical X-content (up to a scalar) as the source of every
read of H; the reader chains are RE-PLANNED by letting every frame float (forward closure from the minimal frame lattice) -- feasibility is the exact anchor-poset test (vector clocks over X initial
lines, Y final hyperplanes and owned-pinned frames), the junk (helper initial values in Y/H rows) is re-solved exactly by head-of-program loads, orphaned kids are DCE'd, indices are re-packed.
API:  sites(w)  -> list of dict(victim, choice)   (candidate groups, anchor-feasible);   apply(w, sites)  -> new word (minimal frames) or None
      level(w, tl, log) -> [(kappa, word, edit)] for pscreen ('alias' set): one greedy batch, exact M.evaluate is the judge.
NB the realised word has the MINIMAL frame assignment (identity edit on mh_I prices -2.5%); compare against `apply(w, [])` (the same word without edits), then `tk retime` it."""
import time,collections
import alias_core as A
import movekit as M
def base(w):
    C=A.Ctx(M.pin(w)); w0,_=A.realise(C,[],{},minimal='hybrid'); return w0
def sites(w,recut=False):
    C=A.Ctx(M.pin(w)); F=C.feas(recut); v,nh=A.victims(C.I,F)
    byv=collections.defaultdict(dict)
    for (h,i),ok in F.items(): byv[h][i]=ok
    return [dict(prim='P14',victim=h,choice={str(i):list(x) for i,x in A.pick(byv,h).items()}) for h in v]
def apply(w,ss):
    C=A.Ctx(M.pin(w)); vs=[s['victim'] for s in ss]; ch={}
    for s in ss:
        for i,x in s['choice'].items(): ch[(s['victim'],int(i))]=(x[0],x[1],A.Fr(x[2]) if not isinstance(x[2],A.Fr) else x[2])
    w2,why=A.realise(C,vs,ch,minimal='hybrid'); return w2
def level(w,tl=300,log=print,batch=40):
    t0=time.time(); w=M.pin(w)
    C,sel,ch=A.round_(w,batch,log)
    w2,na=A.attempt(C,sel,ch,log)
    if w2 is None: return []
    o=M.evaluate(w2)
    return [(o['kappa'],w2,dict(prim='P14',removed=na))] if o.get('legal') else []
