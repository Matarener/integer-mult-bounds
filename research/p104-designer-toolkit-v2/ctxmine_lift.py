"""ctxmine_lift -- plugin of the CTXMINE lane: real-context window search with the guards lifted (owned-operand hoist, SCALE/COPY hops; see ctxmine.py, module docstring).
pscreen set `ctxmine`:  windows around events with an owned operand + helper-hub samples; depth-3 closure per window; best exact-confirmed improving rewrite is applied, repeated.
API: run(w,tl,steps,log,window,topq) -> (word, chain)"""
import time,json
import movekit as M
import ctxmine as CM
def run(w,tl=300,steps=3,log=print,window=None,topq=3,W=8,per_tl=10,**kw):
    w=M.pin(w); chain=[]; t0=time.time(); k=M.evaluate(w)['kappa']
    for s in range(steps):
        v=M.View(w)
        for _ in range(6): M.quick(v,v.S)
        wins=CM.owned_windows(v,W)+CM.hub_windows(v,W,per=10)
        if window: wins=[x for x in wins if window[0]<=x[0]<window[1]]
        best=None; k0=M.quick(v,v.S)[0]
        for lo,hi in wins:
            if time.time()-t0>tl: break
            seen=set(); rs=[]
            for r in CM.search(v,lo,hi,depth=3,beam=100,tl=per_tl,k0=k0):
                kk=tuple(sorted(tuple(e) for e in r['S'][r['lo']:r['hi']]))
                if kk not in seen: seen.add(kk); rs.append(r)
            for r in rs[:topq]:
                try: w2=v.rebuild(r['S']); o=M.evaluate(w2)
                except Exception: continue
                if o.get('legal') and o['kappa']>k+1e-15 and (best is None or o['kappa']>best[0]): best=(o['kappa'],w2,r['path'],r['tags'])
        log('    ctxmine: %d windows, best %s'%(len(wins),None if best is None else '%.15f'%best[0]))
        if best is None: break
        k,w=best[0],best[1]; chain.append(dict(prim='CTX',path=[list(map(str,x)) for x in best[2]],tags=best[3]))
    return w,chain
