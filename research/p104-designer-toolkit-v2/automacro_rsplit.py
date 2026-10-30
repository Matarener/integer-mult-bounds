"""automacro_rsplit -- NEW primitive found by AUTOMACRO from PR #5827.  Registered through pscreen set `automacro` (`tk pscreen WORD --set automacro`).

RSPLIT  = remote Steinberg split of a READ across its writer.   Base:    ... B=ADD(s<-v,b) ... A=ADD(t<-s,a) ...      (A reads the sum s+b*v)
        ->   A'=ADD(t<-s,a) at an EARLIER gap (frame fA)  and  C=ADD(t<-v,a*b) delivered at ANY gap where v still holds its value at B (frame fC), B unchanged.
  This is P1c (A moves left past B, correction C appears behind B) followed by P1 re-timing of A' and of C.  Plain `prims` cannot reach it: (i) step 1 is exactly neutral (greedy/level-1 never takes
  it), (ii) prims.p1_apply refuses owned operands (C reads the OWNED v in #5827), so C cannot be re-timed (`pub=None` here lifts that for the correction ONLY, the moved ADD stays public).
  #5827 (aliromman, +5.8048e-7): A=ADD(695<-733) frame 597 -> frame 3 before the writer ADD(733<-773); C=ADD(695<-773) frame 1031 inside owned 773's life; 695 loses its two dim-597 visits.
API:  import automacro_rsplit as RS;  RS.sites(v,ctx,window,focus) -> edits dict(prim='RS',i,gA,fA,gC,fC);  RS.apply_edit(w,ed,v);  RS.fast(v,ed);  RS.level(w,...);  RS.run(w,tl,steps)"""
import os,sys,json,gzip,time
os.environ.setdefault('TK_FREE_BOUNDS','1') if __name__=='__main__' else None       # CLI only: never set env at import
import movekit as M
import prims
from prims import Block
def _frames_near(fr,S,g,extra=()):
    out=[]
    for k in (g-2,g-1,g,g+1):
        if 0<=k<len(S):
            f=S[k][-1] if S[k][0] in('ADD','COPY','SCALE') else None
            if f is not None and f not in out: out.append(f)
    for f in extra:
        if f is not None and f not in out: out.append(f)
    return out
def _find_corr(S,S1,A,lo,hi):
    old=set(tuple(e) for e in S[lo:hi+1]); ic=None
    for k in range(lo,hi+1):
        e=S1[k]
        if e[0]=='ADD' and (e[1],e[2])!=(A[1],A[2]) and tuple(e) not in old: ic=k
    return ic
def _build(S,ed,pub):
    i,gA,fA,gC,fC=ed['i'],ed['gA'],ed['fA'],ed['gC'],ed['fC']
    A=S[i]
    S1,(lo,hi)=prims.p1_apply(S,i,gA,f=fA,pub=pub)
    if len(S1)!=len(S)+1: raise Block('not a single correction')
    ic=_find_corr(S,S1,A,lo,hi)
    if ic is None: raise Block('no correction')
    gc=gC
    if gc in(ic,ic+1): gc=None
    S2=S1
    if gc is not None or fC is not None:
        if gc is None: gc=ic
        if gc not in(ic,ic+1):
            S2,_=prims.p1_apply(S1,ic,gc,f=fC,pub=None)
        elif fC is not None:
            S2=prims.p2_event(S1,ic,fC)
    if len(S2)!=len(S)+1: raise Block('extra events')
    return S2
def sites(v,ctx,window=None,focus=None,W=40,max_f=3,max_gA=3,max_gC=6):
    S=v.S; n=len(S); pub=v.n; fr=ctx['fr']; touch=ctx['touch']; lo,hi=window or (0,n)
    for i in range(lo,min(hi,n)):
        A=S[i]
        if A[0]!='ADD' or A[1]>=pub or A[2]>=pub: continue
        t,s=A[1],A[2]
        if focus is not None and t not in focus and s not in focus: continue
        for mode in ('L','R'):
            j=None
            if mode=='L':
                for k in range(i-1,max(-1,i-W),-1):
                    e=S[k]
                    if e[0]=='ADD' and e[1]==s and e[2]!=t: j=k; break
                    if s in((e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])): break
            else:
                for k in range(i+1,min(n,i+W)):
                    e=S[k]
                    if e[0]=='ADD' and e[2]==t and e[1]!=s: j=k; break
                    if t in((e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])): break
            if j is None: continue
            gAs=range(j,max(-1,j-max_gA-1),-1) if mode=='L' else range(j+1,min(n+1,j+2+max_gA))
            for gA in gAs:
                fAs=[None]
                for f in _frames_near(fr,S,gA,extra=(3,)):
                    if f!=A[4]: fAs.append(f)
                for fA in fAs[:max_f+1]:
                    try: S1,(lo1,hi1)=prims.p1_apply(S,i,gA,f=fA,pub=pub)
                    except (Block,ValueError,KeyError,IndexError): break
                    if len(S1)!=len(S)+1: break
                    ic=_find_corr(S,S1,A,lo1,hi1)
                    if ic is None: continue
                    cs=S1[ic]; fCs=[None]
                    for f in _frames_near(fr,S1,min(gA,ic)+1,extra=[fr[x] for x in touch[cs[2]][-3:] if x<len(fr)]):
                        if f!=cs[4] and f not in fCs: fCs.append(f)
                    gCs=[ic]+[g for g in range(max(0,min(gA,ic)-2),min(len(S1),max(gA,ic)+3)) if g not in(ic,ic+1)]
                    for gC in gCs[:max_gC+1]:
                        for fC in fCs[:max_f+1]:
                            if gC==ic and fC is None and fA is None and gA==(j if mode=='L' else j+1): continue          # = plain P1c
                            yield dict(prim='RS',mode=mode,i=i,gA=gA,fA=fA,gC=gC,fC=fC)
def apply_edit(w,ed,v=None):
    v=v or M.View(w); return v.rebuild(_build(v.S,ed,v.n))
def fast(v,ed):
    return M.quick(v,_build(v.S,ed,v.n))[0]
class Stats:
    def __init__(s): s.sites=0; s.quick=0; s.exact=0; s.legal=0; s.t0=time.time()
    def line(s): return 'sites %d quick %d exact %d legal %d wall %.1fs'%(s.sites,s.quick,s.exact,s.legal,time.time()-s.t0)
def level(w,window=None,focus=None,topq=12,st=None,log=None,tl=1e9,k0=None,**kw):
    st=st or Stats(); v=M.View(w); ctx=prims.PLUGIN.prepare(v); priced=[]
    base=k0 if k0 is not None else M.quick(v,v.S)[0]
    for ed in sites(v,ctx,window=window,focus=focus,**kw):
        st.sites+=1
        try: k=fast(v,ed)
        except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): k=None
        st.quick+=1
        if k is not None: priced.append((k,ed))
        if time.time()-st.t0>tl: break
    priced.sort(key=lambda x:-x[0]); out=[]
    for k,ed in priced[:topq]:
        try: w2=apply_edit(w,ed,v)
        except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError): continue
        o=M.evaluate(w2); st.exact+=1
        if o.get('legal'): out.append((o['kappa'],w2,ed,k)); st.legal+=1
    out.sort(key=lambda x:-x[0])
    if log:
        for k,ed in priced[:6]:
            if k>base+1e-15: log('      improving quick %.15f (%+.3e) %s'%(k,k-base,json.dumps(ed)))
    if log: log('    RS level: %d sites, %d quick-legal, improving %d, top quick %.15f (base %.15f), %d exact-legal [%s]'%(st.sites,len(priced),sum(1 for k,_ in priced if k>base+1e-15),priced[0][0] if priced else float('nan'),base,len(out),st.line()))
    return out
def run(w,tl=300,steps=3,log=print,window=None,focus=None,**kw):
    w=M.pin(w); k=M.evaluate(w)['kappa']; chain=[]; st=Stats()
    for s in range(steps):
        left=tl-(time.time()-st.t0)
        if left<=0: break
        ch=level(w,window=window,focus=focus,st=st,log=log,tl=left,**kw)
        if not ch or ch[0][0]<=k+1e-15: break
        k,w,ed,_=ch[0]; chain.append(ed); log('  step %d: %.15f %s'%(s+1,k,json.dumps(ed)[:200]))
    return w,chain
def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--window',nargs=2,type=int); ap.add_argument('--steps',type=int,default=1)
    ap.add_argument('--tl',type=float,default=1e9); ap.add_argument('--topq',type=int,default=12); ap.add_argument('--out'); a=ap.parse_args()
    from tkcommon import load
    p,w=load(a.word); log=lambda *x:print(*x,flush=True)
    w2,chain=run(w,tl=a.tl,steps=a.steps,log=log,window=tuple(a.window) if a.window else None,topq=a.topq)
    k0=M.evaluate(M.pin(w))['kappa']; k1=M.evaluate(w2)['kappa']
    log('RESULT %s kappa %.15f -> %.15f (%+.3e) steps %d'%(a.word,k0,k1,k1-k0,len(chain)))
    if a.out and chain and k1>k0+1e-15: json.dump(w2,gzip.open(a.out,'wt')); log('wrote',a.out)
if __name__=='__main__': main()
