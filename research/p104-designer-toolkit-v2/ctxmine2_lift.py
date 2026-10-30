"""ctxmine2_lift -- plugin of the CTXMINE2 lane: ctxmine's real-context window search + P3 conjugation, equal-value read redirect, coefficient split/merge (ctxmine2.py).
pscreen set `ctxmine2`.  API: run(w,tl,steps,log,window,topq) -> (word, chain)"""
import time
import movekit as M, ctxmine as CM, ctxmine2 as C2
def run(w,tl=300,steps=3,log=print,window=None,topq=3,W=8,per_tl=8,**kw):
    w=M.pin(w); chain=[]; t0=time.time(); k=M.evaluate(w)['kappa']
    for s in range(steps):
        v=M.View(w)
        for _ in range(6): M.quick(v,v.S)
        num=C2.Num(v.S,v.n)
        wins=CM.owned_windows(v,W)+CM.hub_windows(v,W,per=10)
        if window: wins=[x for x in wins if window[0]<=x[0]<window[1]]
        best=None; k0=M.quick(v,v.S)[0]
        for lo,hi in wins:
            if time.time()-t0>tl: break
            seen=set(); rs=[]
            for r in C2.search2(v,num,lo,hi,depth=3,beam=40,tl=per_tl,k0=k0):
                kk=tuple(sorted(tuple(e) for e in r['S'][r['lo']:r['hi']]))
                if kk not in seen: seen.add(kk); rs.append(r)
            for r in rs[:topq]:
                try: w2=v.rebuild(r['S']); o=M.evaluate(w2)
                except Exception: continue
                if o.get('legal') and o['kappa']>k+1e-15 and (best is None or o['kappa']>best[0]): best=(o['kappa'],w2,r['path'],r['tags'])
        log('    ctxmine2: %d windows, best %s'%(len(wins),None if best is None else '%.15f'%best[0]))
        if best is None: break
        k,w=best[0],best[1]; chain.append(dict(prim='CTX2',path=[list(map(str,x)) for x in best[2]],tags=best[3]))
    return w,chain
