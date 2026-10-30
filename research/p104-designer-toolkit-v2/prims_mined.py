"""prims_mined -- fused move plugins mined by PRIMMINE.  Registered only through pscreen (`tk pscreen WORD --set prims_mined`).

The miner (ext/PRIMMINE/mine.cpp: exact symbolic enumeration of event strings of length <= 7-8 on 3 public + 1-2 owned registers, context-priced over frame lattices)
and the classifier (cls.py: Dijkstra over local verified rewrites) found that EVERY mined rule A->B with a better price in some frame context is a composition of
P1c (Steinberg move) and P8 (owned courier) -- most often P1c o P8 of depth 2 (one Steinberg move whose correction or whose moved reader is then delivered through an owned copy), a few P1c o P1c o P8.
The greedy/beam drivers only reach such a pair when the P1c half survives the level-1 top-q cut (it normally DIPS), so the mined macros are implemented as fused direct site finders:

  PM1  STEINBERG COURIER   one P1 (a move of an ADD past a conflicting event; a correction ADD is created) followed, inside the same edit, by every P8 (acc / ret) site on the touched region
                           of the intermediate program.  The dip of the P1 half is invisible to the search; priced as a pair with the trajectory-exact quick price, confirmed with M.evaluate.
  PM2  DOUBLE STEINBERG COURIER  P1 o P1 o P8 (the second P1 moves an event created by / adjacent to the first one).

API (as prims_extra):   import prims_mined as PM;  for ed in PM.sites_pm1(v,ctx,window=(lo,hi),focus=regs): ...;   w2=PM.apply_edit(w,ed);   PM.level(w,...);   PM.run(w,tl,steps)
An edit is dict(prim='PM1', e1=<P1 edit>, e8=<P8 edit on the intermediate program>)."""
import sys,os,json,gzip,time,collections
import movekit as M
import prims
import prims_extra as PE
from prims import Block

_CACHE={}
def _inter(v,e1):
    """intermediate program after the P1 half: (S1, lo, hi, w1, v1, ctx1) cached on (id of v.S, edit)"""
    key=(id(v.S),e1['prim'],e1.get('i'),e1.get('g'),e1.get('f'),e1.get('fc'),e1.get('i0'),e1.get('i1'),e1.get('a'),e1.get('b'),e1.get('ef'),e1.get('xf'))
    c=_CACHE.get(key)
    if c is not None: return c
    if e1['prim']=='P3':
        from fractions import Fraction as Q
        S1=prims.p3_apply(v.S,e1['i0'],e1['i1'],e1['a'],e1['b'],Q(e1['q']),e1['ef'],e1['xf'],v.n); lo,hi=e1['i0'],e1['i1']+8
    else:
        S1,(lo,hi)=prims.p1_apply(v.S,e1['i'],e1['g'],f=e1.get('f'),fc=e1.get('fc'),pub=v.n)
        if len(S1)<=len(v.S): raise Block('no correction')
        S1=prims.p0_merge(S1,lo,hi)
    w1=v.rebuild(S1); v1=M.View(w1); ctx1=prims.PLUGIN.prepare(v1)
    c=(S1,lo,hi,w1,v1,ctx1)
    if len(_CACHE)>64: _CACHE.clear()
    _CACHE[key]=c; return c
def sites_pm1(v,ctx,window=None,focus=None,max_f=3,kinds=('acc','ret'),p8window=(3,10),per_p1=24,KMAX=3,only_new=True):
    """P1 (with Steinberg correction) fused with the P8 sites of the touched region.  only_new: the P8 group must contain an event created or moved by the P1 half (otherwise it is a plain P8)."""
    S=v.S; N=len(S)
    for e1 in prims.PLUGIN.sites_P1(v,ctx,window=window,focus=focus,max_f=max_f,ends=False):
        try: S1,lo,hi,w1,v1,ctx1=_inter(v,e1)
        except (Block,ValueError,KeyError,IndexError,AssertionError): continue
        n=0
        for e8 in PE.sites8(v1,ctx1,window=(max(0,lo-p8window[0]),min(len(S1),hi+p8window[1])),kinds=kinds,KMAX=KMAX):
            if only_new and not any(lo<=g<=hi for g in e8['idx']): continue
            n+=1
            if n>per_p1: break
            yield dict(prim='PM1',e1=e1,e8=e8)
def sites_pm3(v,ctx,window=None,focus=None,kinds=('acc','ret'),p8window=(3,12),per_p1=24,KMAX=3,**kw):
    """P3 (conjugation of a window by a transvection, ibase sites) fused with the P8 sites of the conjugated window (mined class P3+P8, the largest: 90 of 365 rules at 3 pub / 2 owned / L<=7)."""
    for e1 in prims.PLUGIN.sites_P3(v,ctx,window=window,focus=focus):
        try: S1,lo,hi,w1,v1,ctx1=_inter(v,e1)
        except (Block,ValueError,KeyError,IndexError,AssertionError): continue
        n=0
        for e8 in PE.sites8(v1,ctx1,window=(max(0,lo-p8window[0]),min(len(S1),hi+p8window[1])),kinds=kinds,KMAX=KMAX):
            n+=1
            if n>per_p1: break
            yield dict(prim='PM3',e1=e1,e8=e8)
def sites_pm2(v,ctx,window=None,focus=None,max_f=2,kinds=('acc','ret'),per_p1=12,per_p2=12):
    """P1 o P1 o P8: the second P1 moves an ADD touching the first one's correction (or the moved ADD); the P8 half then runs on the touched region."""
    S=v.S
    for e1 in prims.PLUGIN.sites_P1(v,ctx,window=window,focus=focus,max_f=max_f,ends=False):
        try: S1,lo,hi,w1,v1,ctx1=_inter(v,e1)
        except (Block,ValueError,KeyError,IndexError,AssertionError): continue
        regs=set()
        for g in range(lo,min(hi+1,len(S1))):
            if S1[g][0]=='ADD': regs|={S1[g][1],S1[g][2]}
        k2=0
        for e2 in prims.PLUGIN.sites_P1(v1,ctx1,window=(max(0,lo-2),min(len(S1),hi+3)),focus=regs,max_f=max_f,ends=False):
            try: S2,(lo2,hi2)=prims.p1_apply(S1,e2['i'],e2['g'],f=e2.get('f'),fc=e2.get('fc'),pub=v1.n)
            except (Block,ValueError,KeyError,IndexError,AssertionError): continue
            k2+=1
            if k2>per_p2: break
            S2=prims.p0_merge(S2,lo2,hi2)
            w2=v1.rebuild(S2); v2=M.View(w2); ctx2=prims.PLUGIN.prepare(v2)
            k8=0
            for e8 in PE.sites8(v2,ctx2,window=(max(0,min(lo,lo2)-3),min(len(S2),max(hi,hi2)+10)),kinds=kinds):
                k8+=1
                if k8>per_p1: break
                yield dict(prim='PM2',e1=e1,e2=e2,e8=e8)
def apply_edit(w,ed,v=None):
    v=v or M.View(w)
    if ed['prim']=='PM4': return v.rebuild(pm4_apply(v.S,ed))
    S1,lo,hi,w1,v1,ctx1=_inter(v,ed['e1'])
    if ed['prim'] in('PM1','PM3'):
        v1._pe_ctx=ctx1
        return PE.apply_edit(w1,ed['e8'],v1)
    S2,(lo2,hi2)=prims.p1_apply(S1,ed['e2']['i'],ed['e2']['g'],f=ed['e2'].get('f'),fc=ed['e2'].get('fc'),pub=v1.n); S2=prims.p0_merge(S2,lo2,hi2)
    w2=v1.rebuild(S2); v2=M.View(w2); v2._pe_ctx=prims.PLUGIN.prepare(v2)
    return PE.apply_edit(w2,ed['e8'],v2)
def fast(v,ed):
    if ed['prim']=='PM4': return M.quick(v,pm4_apply(v.S,ed))[0]
    S1,lo,hi,w1,v1,ctx1=_inter(v,ed['e1'])
    if ed['prim'] in('PM1','PM3'):
        v1._pe_ctx=ctx1
        return PE.fast(v1,ed['e8'])
    S2,(lo2,hi2)=prims.p1_apply(S1,ed['e2']['i'],ed['e2']['g'],f=ed['e2'].get('f'),fc=ed['e2'].get('fc'),pub=v1.n); S2=prims.p0_merge(S2,lo2,hi2)
    w2=v1.rebuild(S2); v2=M.View(w2); v2._pe_ctx=prims.PLUGIN.prepare(v2)
    return PE.fast(v2,ed['e8'])
class Stats:
    def __init__(s): s.sites=0; s.quick=0; s.exact=0; s.legal=0; s.t0=time.time(); s.cpu0=time.process_time()
    def line(s): return 'sites %d quick %d exact %d legal %d wall %.1fs cpu %.2f min'%(s.sites,s.quick,s.exact,s.legal,time.time()-s.t0,(time.process_time()-s.cpu0)/60)
def level(w,kinds_pm=('PM1',),window=None,focus=None,topq=12,st=None,log=None,tl=1e9,minq=None,k0=None,hist=None,**kw):
    """price every fused edit with the trajectory-exact quick price, confirm the topq exactly (M.evaluate honours the stamped P8 pins).  -> [(kappa, word, edit)] best first.
    hist: optional Counter collecting quick-priced gains (sites that are legal) for the report"""
    st=st or Stats(); v=M.View(w); ctx=prims.PLUGIN.prepare(v); priced=[]
    base=k0 if k0 is not None else M.quick(v,v.S)[0]
    for kind in kinds_pm:
        gen={'PM1':sites_pm1,'PM2':sites_pm2,'PM3':sites_pm3,'PM4':sites_pm4}[kind](v,ctx,window=window,focus=focus,**kw)
        for ed in gen:
            st.sites+=1
            try: k=fast(v,ed)
            except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): k=None
            st.quick+=1
            if k is not None:
                priced.append((k,ed))
                if hist is not None: hist[kind]+=1
            if time.time()-st.t0>tl: break
    priced.sort(key=lambda x:-x[0]); out=[]
    if log: log('    census: %d quick-legal; improving %d; neutral(|d|<1e-12) %d; within 5e-7 below %d; within 2e-6 below %d; best 5 d: %s'%(len(priced),sum(1 for k,_ in priced if k>base+1e-15),sum(1 for k,_ in priced if abs(k-base)<=1e-12),sum(1 for k,_ in priced if k>base-5e-7),sum(1 for k,_ in priced if k>base-2e-6),['%+.2e'%(k-base) for k,_ in priced[:5]]))
    for k,ed in priced[:topq]:
        if minq is not None and k<minq: break
        try: w2=apply_edit(w,ed,v)
        except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError): continue
        o=M.evaluate(w2); st.exact+=1
        if o.get('legal'): out.append((o['kappa'],w2,ed,k)); st.legal+=1
    out.sort(key=lambda x:-x[0])
    if log: log('    PM level %s: %d sites, %d quick-legal, top quick %.15f (base %.15f), %d exact-legal [%s]'%(','.join(kinds_pm),st.sites,len(priced),priced[0][0] if priced else float('nan'),base,len(out),st.line()))
    return out
def run(w,tl=300,steps=3,log=print,kinds_pm=('PM1',),window=None,focus=None,**kw):
    """greedy over fused edits (pscreen set `prims_mined`).  -> (word, chain)"""
    w=M.pin(w); k=M.evaluate(w)['kappa']; chain=[]; st=Stats()
    for s in range(steps):
        left=tl-(time.time()-st.t0)
        if left<=0: break
        ch=level(w,kinds_pm,window=window,focus=focus,st=st,log=log,tl=left,**kw)
        if not ch or ch[0][0]<=k+1e-15: break
        k,w,ed,_=ch[0]; chain.append(ed); log('  step %d: %.15f %s'%(s+1,k,json.dumps(ed)[:200]))
    return w,chain
def main():
    import argparse; os.environ.setdefault('TK_FREE_BOUNDS','1')
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--kinds',default='PM1'); ap.add_argument('--window',nargs=2,type=int)
    ap.add_argument('--steps',type=int,default=1); ap.add_argument('--tl',type=float,default=1e9); ap.add_argument('--topq',type=int,default=12); ap.add_argument('--out'); ap.add_argument('--hot',type=int,default=0)
    ap.add_argument('--shard',default='0/1'); a=ap.parse_args()
    from tkcommon import load
    p,w=load(a.word); log=lambda *x:print(*x,flush=True)
    foc=None
    if a.hot:
        from wsearch import guide
        foc=set(guide.hot_list(M.pin(w),a.hot))
    win=tuple(a.window) if a.window else None
    w2,chain=run(w,tl=a.tl,steps=a.steps,log=log,kinds_pm=tuple(a.kinds.split(',')),window=win,focus=foc,topq=a.topq)
    k0=M.evaluate(M.pin(w))['kappa']; k1=M.evaluate(w2)['kappa']
    log('RESULT %s kappa %.15f -> %.15f (%+.3e) steps %d'%(a.word,k0,k1,k1-k0,len(chain)))
    if a.out and chain and k1>k0+1e-15: json.dump(w2,gzip.open(a.out,'wt')); log('wrote',a.out)
if __name__=='__main__': main()

# ------------------------------------------------------------------ PM4: READ REDIRECT THROUGH A TRANSVECTION PAIR (mined, NOT decomposed by cls.py within depth 4 / 600 nodes, 4-public table)
# Mined rule  x0 -= x1 ; x1 -= x2 ; x2 += x1   ==>   x1 -= x2 ; x2 += x1 ; x0 -= x2.   In general   R=ADD(t<-x,a) ; W1=ADD(x<-y,b) ; W2=ADD(y<-x,c)  with  b*c = -1
# leaves y = c*x_old (the pair is a Weyl half: x' = x + b y, y' = c x), so the READ R can be re-issued AFTER the pair as ADD(t<-y, a/c): same value, the reader now meets y (chart / residence of y) instead of x.
# The mirror form (R after the pair reading y) moves it before the pair as ADD(t<-x, a*c).  Value-preserving by construction; frames: candidates = residence/next frames of t and y.
from fractions import Fraction as _Q
def _qq(x): return _Q(x)
def sites_pm4(v,ctx,window=None,focus=None,W=80,max_f=3):
    S=v.S; n=len(S); pub=v.n; lo,hi=window or (0,n); touch=ctx['touch']; fr=ctx['fr']
    for i in range(lo,min(hi,n)):
        R=S[i]
        if R[0]!='ADD' or R[1]>=pub or R[2]>=pub: continue
        t,x,a=R[1],R[2],_qq(R[3])
        if focus is not None and t not in focus and x not in focus: continue
        j=None
        for jj in range(i+1,min(n,i+W)):
            e=S[jj]
            if e[0]=='ADD' and e[1]==x and e[2]<pub and e[2] not in(t,x): j=jj; break
            if t in (e[1],) or (e[0] in('ADD','COPY') and e[2]==t) or x in touches_(e): break   # something else touches t or x first
        if j is None: continue
        W1=S[j]; y=W1[2]; b=_qq(W1[3])
        for k in range(j+1,min(n,j+W)):
            e=S[k]
            if e[0]=='ADD' and e[1]==y and e[2]==x and _qq(e[3])*b==-1: 
                c=_qq(e[3]); fs=[None]
                for r in (t,y):
                    L=touch[r]; from bisect import bisect_left
                    q=bisect_left(L,k)
                    for jx in (L[q-1] if q>0 else None, L[q] if q<len(L) and L[q]!=k else None):
                        if jx is not None and jx not in (i,j,k) and fr[jx] not in fs: fs.append(fr[jx])
                for f in fs[:max_f]: yield dict(prim='PM4',i=i,j=j,k=k,y=y,f=f)
                break
            if t in (e[1],) or (e[0] in('ADD','COPY') and e[2]==t) or (y in touches_(e) or x in touches_(e)): break
def touches_(e): return (e[1],) if e[0] in('INIT','CLEAR','SCALE') else (e[1],e[2])
def pm4_apply(S,ed):
    i,j,k,y,f=ed['i'],ed['j'],ed['k'],ed['y'],ed['f']
    R=S[i]; c=_qq(S[k][3]); a=_qq(R[3])
    Rn=['ADD',R[1],y,str(a/c) if (a/c).denominator==1 else str(a/c),R[4] if f is None else f]
    for z in (S[j],S[k]):
        pass
    if i<j<k:
        return S[:i]+S[i+1:k+1]+[Rn]+S[k+1:]
    raise Block('order')
def pm4_value_ok(S,S2,n):
    """exact oracle: final rows of S and S2 agree (prims_extra.sim_rows)"""
    return PE.sim_rows(S,n)==PE.sim_rows(S2,n)
