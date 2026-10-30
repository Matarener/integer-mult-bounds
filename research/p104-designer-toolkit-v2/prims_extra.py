"""prims_extra -- primitives P8.. beyond P1-P7 (MOREPRIMS.  Registers on prims.Prims (sites_P8.. / apply) like prims_role; prims.py/macros.py are untouched.

  P8  OWNED BRIDGE (descent bridge).  A public register r only ever ASCENDS (MOVE to a larger span); an owned register only DESCENDS and is erased for free (CLEAR).  So a public
      register that must visit a high chart A just to read/write operands that live there can instead leave its own chart B (span B strictly inside A) untouched and let an
      owned scratch carry the operands down.
        kind 'acc' (write side, #5802):   t += a1 s1; ...; t += ak sk   ->   INIT o; o += a1 s1; ...; o += ak sk; t += o @B; CLEAR o     (o descends A -> B, delivery at B)
        kind 'ret' (read side,  #5774):   t1 += a1 s; ...; tk += ak s   ->   INIT o; COPY o<-s; t1 += a1 o @B1; ...; tk += ak o @Bk; CLEAR o      (reads at lower charts)
      Value preserving by linearity; costs +3 events and one owned lifetime per application.  The convention pins (owned lifetimes, peak, owned_fields, event cap) belong to the
      package, not to the rules: `stamp()` writes the new census into word['verifier_profile'] and `price()` reports the pins a candidate would need.
  P9  SCALE HOP (move an ADD across a SCALE with the coefficient rescaled; COPY+SCALE fusion).  Steinberg relation h(c) x_ij(a) h(c)^-1 = x_ij(a c^{+-1}).
  P10 RE-FRAME THE REST OF THE FREE VARIABLES: frame label of owned-lifetime events (INIT/COPY/SCALE/CLEAR) and the free endpoints of MAIN registers (X final, Y initial).

    python:   import prims_extra as PE; PE.register(); ed=dict(prim='P8',kind='acc',idx=[...],fp=F); w2=PE.apply_edit(w,ed); PE.price(w,w2)
"""
import sys,os,json,gzip,time,collections
from fractions import Fraction as Q
from bisect import bisect_left,bisect_right
import movekit as M
from movekit import qs
import prims
from prims import Block

# ------------------------------------------------------------------ helpers
def fr_of(e): return e[2] if e[0] in('INIT','CLEAR') else e[-1]
def with_frame(e,f):
    e=list(e)
    if e[0] in('INIT','CLEAR'): e[2]=f
    else: e[-1]=f
    return e
def intervals(S,n):
    """owned id -> sorted list of (init index, clear index) of its lifetimes in S"""
    op={}; iv=collections.defaultdict(list)
    for i,e in enumerate(S):
        if e[0]=='INIT': op[e[1]]=i
        elif e[0]=='CLEAR': iv[e[1]].append((op.pop(e[1]),i))
    return iv
def free_owned(S,v,lo,hi,iv=None,avoid=(),grow=True):
    """smallest owned id with no lifetime overlapping the index range [lo,hi]"""
    iv=iv or intervals(S,v.n)
    for o in range(v.n,v.NR):
        if o in avoid: continue
        if all(b<lo or a>hi for (a,b) in iv.get(o,())): return o
    if grow: return v.NR            # a NEW owned role: owned_fields+1 (package convention: owned inventory)
    raise Block('no free owned role')
def census(S,n):
    """(lifetimes, peak) of a scalar program"""
    live=0; peak=0; life=0
    for e in S:
        if e[0]=='INIT': live+=1; life+=1; peak=max(peak,live)
        elif e[0]=='CLEAR': live-=1
    return life,peak
def touches(e):
    op=e[0]
    if op in('ADD','COPY'): return (e[1],e[2])
    return (e[1],)

# ------------------------------------------------------------------ P8 apply
def acc_apply(S,idx,fp,o,n):
    """INIT o at the first group event; each ADD t+=a s becomes o+=a s at its own place; after the last: t += o @fp, CLEAR o @fp.  Needs: t untouched by non-group events in between"""
    t=S[idx[0]][1]; st=set(idx); lo,hi=idx[0],idx[-1]
    for k in range(lo,hi+1):
        e=S[k]
        if k in st:
            if e[0]!='ADD' or e[1]!=t or e[2]==t or e[2]==o: raise Block('group')
        elif t in touches(e) or o in touches(e): raise Block('t touched between')
    new=[]
    for k in range(lo,hi+1):
        e=S[k]
        if k==lo: new.append(['INIT',o,fr_of(e)])
        new.append(['ADD',o,e[2],e[3],e[4]] if k in st else e)
    new.append(['ADD',t,o,'1',fp]); new.append(['CLEAR',o,fp])
    return S[:lo]+new+S[hi+1:]
def ret_apply(S,idx,fps,o,n):
    """INIT o; COPY o<-s at the first read (frame of that read); read k becomes t_k += a_k o @fps[k]; CLEAR o after the last read.  Needs: s not written in between"""
    s=S[idx[0]][2]; st=set(idx); lo,hi=idx[0],idx[-1]
    for k in range(lo,hi+1):
        e=S[k]
        if k in st:
            if e[0] not in('ADD','COPY') or e[2]!=s or e[1]==s or e[1]==o: raise Block('group')
        elif o in touches(e): raise Block('o touched')
        elif s in touches(e) and not (e[0] in('ADD','COPY') and e[2]==s): raise Block('s written between')
    f0=fr_of(S[lo]); new=[]; j=0
    for k in range(lo,hi+1):
        e=S[k]
        if k==lo: new+= [['INIT',o,f0],['COPY',o,s,'1',f0]]
        if k in st: new.append([e[0],e[1],o,e[3],fps[j]]); j+=1
        else: new.append(e)
    new.append(['CLEAR',o,fps[-1]])
    return S[:lo]+new+S[hi+1:]


def descend(S,ctx,v,seeds,cap=80,fwd=True,group=(),tregs=(),real=False,backs=()):
    """DESCENT CLOSURE after a bridge.  seeds = [(pos, fo, fp)]: register t(pos) now sits at fp instead of fo from index pos on.  Every later touch of t that is still at fo is lowered to fp
    (forward pull, the stop collapse that pays for the bridge) and every operand of a lowered event is lowered backwards the same way: its previous touch (frame fo) must come down to fp
    (mandatory for public registers: they only ascend; taken for owned ones: saves their pre-descent) -- up to the register's first touch, whose declared start follows.
    -> (relabel {index: fp}, initial {r: fp}, final {r: fp});  Block when a public register cannot nest under fp."""
    touch=ctx['touch']; fr=ctx['fr']; bm=ctx['bm']; n=v.n; w=v.w
    def nest(a,b): return a==b or (bm[a]!=bm[b] and (bm[a]|bm[b])==bm[b])
    F={}; ini={}; fin={}; queue=[]
    def getf(i): return F.get(i,fr[i])
    def lower(i,fo,fp):
        f=getf(i)
        if f==fp: return
        if f!=fo: raise Block('frame %s != %s at %d'%(f,fo,i))
        if i in group: raise Block('group event')
        F[i]=fp; queue.append((i,fo,fp,None))
        if len(F)>cap: raise Block('closure cap')
    def forward(r,pos,fo,fp):
        L=touch[r]
        for j in L[bisect_right(L,pos):]:
            f=getf(j)
            if f==fp: continue
            if f!=fo: break
            lower(j,fo,fp)
    for (pos,fo,fp) in seeds:
        r=S[pos][1]
        if real and fo!=fp:
            F[pos]=fp; queue.append((pos,fo,fp,(r,)))     # the read event itself is lowered; only its TARGET register matters (the source is read through the owned copy)
        if fwd: forward(r,pos,fo,fp)
    # P8GAP: the bridged register t only ASCENDS, so its touch BEFORE the group must not sit above the new chart either (backward pull of the target; on #5802 the previous touch of t=92
    # still sat at the group's chart, which the #5796 retime had already lowered on the stack word -> without this the #5811 bridge was illegal on #5802 itself)
    for (pos,fo,fp,r) in backs:
        if fo!=fp: queue.append((pos,fo,fp,(r,)))
    k=0
    while k<len(queue):
        i,fo,fp,regs=queue[k]; k+=1
        for u in (regs or touches(S[i])):
            L=touch[u]; j=bisect_left(L,i)
            isown=u>=n
            if j>0:
                p=L[j-1]; f=getf(p)
                if f==fp: pass
                elif f==fo:
                    if p in group:
                        if u in tregs: continue
                        raise Block('operand lives in the group')
                    lower(p,fo,fp)
                elif isown: pass
                elif not nest(f,fp): raise Block('operand %d cannot nest'%u)
            if isown:
                for jj in L[j+1:]:
                    f=getf(jj)
                    if f==fp: continue
                    if f!=fo: break
                    lower(jj,fo,fp)
            if j==0 and not isown:
                if ini.get(u,w['initial'][u])==fo: ini[u]=fp
                elif not nest(ini.get(u,w['initial'][u]),fp): raise Block('start')
            # last touch -> final follows
            if not isown and j==len(L)-1 and fin.get(u,w['final'][u])==fo: fin[u]=fp
    return F,ini,fin

def stamp(w,S2):
    life,peak=census(S2,len(w['initial']))
    pp=prims.M.legal.profile_params(w); vp=dict(w.get('verifier_profile') or {})
    vp.update(public=len(w['initial']),owned_fields=M.legal.nown(w),lifetimes=life,peak=max(peak,pp.get('peak') or 0) if pp.get('peak') else peak)
    w=dict(w); w['verifier_profile']=vp; return w

_CTX={}
def prims_fr(S,i): return fr_of(S[i])
def parts(v,ed):
    """edit -> (S2, initial, final)"""
    S=v.S; w=v.w; p=ed['prim']; ini=fin=None
    if p=='P8':
        o=ed.get('o')
        iv=intervals(S,v.n)
        idx=ed['idx']
        if o is None: o=free_owned(S,v,idx[0],idx[-1],iv)
        Sb=S
        if ed.get('pull'):
            ctx=getattr(v,'_pe_ctx',None)
            if ctx is None: ctx=v._pe_ctx=prims.PLUGIN.prepare(v)
            if ed['kind']=='acc': seeds=[(idx[-1],prims_fr(S,idx[-1]),ed['fp'])]
            else: seeds=[(g,prims_fr(S,g),fp) for g,fp in zip(idx,ed['fps'])]
            backs=[(idx[0],prims_fr(S,idx[0]),ed['fp'],S[idx[0]][1])] if ed['kind']=='acc' else ()
            F,i2,f2=descend(S,ctx,v,seeds,group=set(idx),fwd=True,tregs={S[g][1] for g in idx} if ed['kind']=='ret' else {S[idx[0]][1]},real=(ed['kind']=='ret'),backs=backs,cap=ed.get('cap',300))
            Sb=list(S)
            if ed['kind']=='ret':
                for g in idx: F.pop(g,None)
            for i,f in F.items(): Sb[i]=with_frame(S[i],f)
            ini=list(w['initial']) if i2 else None; fin=list(w['final']) if f2 else None
            for r,f in i2.items(): ini[r]=f
            for r,f in f2.items(): fin[r]=f
        if ed['kind']=='acc': S2=acc_apply(Sb,idx,ed['fp'],o,v.n)
        else: S2=ret_apply(Sb,idx,ed['fps'],o,v.n)
    elif p=='P9':
        if ed.get('kind')=='fuse': S2=fuse_apply(S,ed['copy'],ed['scale'])
        else:
            S2,(lo_,hi_)=p9_apply(S,ed['i'],ed['g'],f=ed.get('f'),fc=ed.get('fc'),pub=v.n); S2=prims.p0_merge(S2,lo_,hi_)
    elif p=='P11':
        S2,(lo_,hi_)=p11_apply(S,ed['i'],ed['g'],ed.get('f'),ed.get('fc'),ed['frac'],v.n); S2=prims.p0_merge(S2,lo_,hi_)
    elif p=='P12':
        S2=p12_apply(S,ed['i'],ed['j'],ed['a'],ed['b'],ed['f'],ed.get('f2'),v.n)
    elif p=='P10':
        S2=S
        if ed['kind']=='ev':
            S2=list(S); S2[ed['i']]=with_frame(S[ed['i']],ed['f'])
        elif ed['kind']=='start': ini=list(w['initial']); ini[ed['r']]=ed['f']
        elif ed['kind']=='final': fin=list(w['final']); fin[ed['r']]=ed['f']
        else: raise ValueError(ed['kind'])
    else: raise ValueError(p)
    for (k,r,f) in ed.get('ends',()):
        if k=='start': ini=ini or list(w['initial']); ini[r]=f
        else: fin=fin or list(w['final']); fin[r]=f
    for (i,f) in ed.get('relabel',()):       # extra frame relabels of scalar events (indices of S2)
        if S2 is S: S2=list(S)
        S2[i]=with_frame(S2[i],f)
    return S2,ini,fin
# ------------------------------------------------------------------ P9: P1 through SCALE barriers (Steinberg diagonal relation) + COPY/SCALE fusion
def _corr9(t,s,a,B,side):
    """like prims._corr, but a SCALE of t or s is passable with a coefficient factor.  -> (corrections, factor Fraction)"""
    if B[0]=='SCALE' and B[1] in(t,s):
        c=Q(B[2])
        if B[1]==t: return [],(c if side>0 else 1/c)        # A then SCALE t c  ==  SCALE t c then ADD(c a)
        return [],(1/c if side>0 else c)                    # A then SCALE s c  ==  SCALE s c then ADD(a/c)
    return prims._corr(t,s,a,B,side),Q(1)
def p9_apply(S,i,g,f=None,fc=None,pub=None):
    A=S[i]
    if A[0]!='ADD': raise Block('not add')
    t,s,a=A[1],A[2],Q(A[3])
    if pub is not None and (t>=pub or s>=pub): raise Block('owned')
    if g==i or g==i+1: raise Block('noop')
    nscale=0; fac=Q(1)
    if g>i+1:
        mid=[]
        for k in range(i+1,g):
            B=S[k]; cs,x=_corr9(t,s,a,B,+1)
            if x!=1: nscale+=1; fac*=x
            for (u,vv,c,fb) in cs: mid.append(['ADD',u,vv,qs(c),fb if fc is None else fc])
            mid.append(B)
        a2=a*fac
        if not a2 or abs(a2)+1>=2**16: raise Block('growth')
        S2=S[:i]+mid+[['ADD',t,s,qs(a2),A[4] if f is None else f]]+S[g:]; lo,hi=i,i+len(mid)
    else:
        tail=[]
        for k in range(i-1,g-1,-1):
            B=S[k]; cs,x=_corr9(t,s,a,B,-1)
            if x!=1: nscale+=1; fac*=x
            tail=[B]+[['ADD',u,vv,qs(c),fb if fc is None else fc] for (u,vv,c,fb) in cs]+tail
        a2=a*fac
        if not a2 or abs(a2)+1>=2**16: raise Block('growth')
        S2=S[:g]+[['ADD',t,s,qs(a2),A[4] if f is None else f]]+tail+S[i+1:]; lo,hi=g,g+len(tail)
    if not nscale: raise Block('no scale passed')
    return S2,(lo,hi)
def sites9(v,ctx=None,window=None,focus=None,max_f=4):
    """P1 sites that pass at least one SCALE of an operand (the sites plain P1 refuses)"""
    ctx=ctx or _ctx(v); S=v.S; old=prims._corr
    def patched(t,s,a,B,side):
        if B[0]=='SCALE' and B[1] in(t,s): return []
        return old(t,s,a,B,side)
    prims._corr=patched
    try:
        for ed in prims.PLUGIN.sites_P1(v,ctx,window=window,focus=focus,max_f=max_f,ends=True):
            i,g=ed['i'],ed['g']; lo,hi=(i+1,g) if g>i else (g,i)
            e=S[i]; t,s=e[1],e[2]
            if any(S[k][0]=='SCALE' and S[k][1] in(t,s) for k in range(lo,hi)): yield dict(ed,prim='P9')
    finally: prims._corr=old
def fuse_sites(v):
    """COPY o<-s,a ; ... ; SCALE o,c with nothing else touching o in between -> COPY o<-s,a*c (saves one event; kappa-neutral; slack maker)"""
    S=v.S; last={}
    for i,e in enumerate(S):
        if e[0]=='COPY': last[e[1]]=i
        elif e[0]=='SCALE' and last.get(e[1]) is not None:
            j=last[e[1]]
            if all(e[1]!=x[1] and not(x[0] in('ADD','COPY') and x[2]==e[1]) for x in S[j+1:i]): yield dict(prim='P9',kind='fuse',copy=j,scale=i)
            last[e[1]]=None
        elif e[1] in last and e[0] in('ADD','CLEAR','INIT'): last[e[1]]=None
        elif e[0] in('ADD','COPY') and e[2] in last: last[e[2]]=None
def fuse_apply(S,j,i):
    c=S[j]; sc=S[i]; a=Q(c[3])*Q(sc[2])
    if abs(a)+1>=2**16: raise Block('growth')
    return S[:j]+[['COPY',c[1],c[2],qs(a),c[4]]]+S[j+1:i]+S[i+1:]

# ------------------------------------------------------------------ P11: ADD SPLIT (the inverse of P0's additivity x_ij(a)x_ij(b)=x_ij(a+b)): one ADD becomes two halves placed independently
def p11_apply(S,i,g,f,fc,frac,pub):
    A=S[i]
    if A[0]!='ADD': raise Block('not add')
    a=Q(A[3]); a1=a*Q(frac); a2=a-a1
    if not a1 or not a2: raise Block('degenerate')
    S1=S[:i]+[['ADD',A[1],A[2],qs(a2),A[4]],['ADD',A[1],A[2],qs(a1),A[4]]]+S[i+1:]
    # the moved half is S1[i+1]; positions after it shift by one
    g1=g+1 if g>i else g
    S2,(lo,hi)=prims.p1_apply(S1,i+1,g1,f=f,fc=fc,pub=pub)
    return S2,(lo,hi)
def sites11(v,ctx=None,window=None,focus=None,fracs=('1/2',),max_f=3):
    ctx=ctx or _ctx(v)
    for ed in prims.PLUGIN.sites_P1(v,ctx,window=window,focus=focus,max_f=max_f,ends=False):
        for fr_ in fracs: yield dict(ed,prim='P11',frac=fr_)

def _grow(w,v,S2):
    mx=max([e[1] for e in S2 if e[0]=='INIT']+[v.NR-1])
    if mx>=v.NR:
        w=dict(w); w['owned_fields']=mx+1-v.n; vp=dict(w.get('verifier_profile') or {}); vp['owned_fields']=w['owned_fields']; w['verifier_profile']=vp; v=M.View(w)
    return w,v
def apply_edit(w,ed,v=None):
    v=v or M.View(w); S2,ini,fin=parts(v,ed)
    w,v=_grow(w,v,S2)
    w2=v.rebuild(S2,initial=ini,final=fin)
    if ed['prim']=='P8': w2=stamp(w2,S2)
    return w2
def fast(v,ed):
    S2,ini,fin=parts(v,ed); _,v=_grow(v.w,v,S2); return M.quick(v,S2,initial=ini,final=fin)[0]

# ------------------------------------------------------------------ pricing with the pins reported separately
def price(w,w2,ev=None):
    """exact: legal (pins stamped in w2 are honoured by M.evaluate), kappa, event slack, and the pins (lifetimes, peak) w2 would need.
    IncrWord keeps the BASE pins, so the exact price is IncrWord with the pin violation filtered out when it is the only one"""
    ev=ev or prims.evaluator()
    o=ev.evaluate(w2,base=w)
    return o

# ------------------------------------------------------------------ registration
def register():
    if getattr(prims.Prims,'_pe_registered',False): return
    P=prims.Prims
    def sites_P8(self,v,ctx,window=None,focus=None,max_f=3,**kw): return sites8(v,ctx,window=window,focus=focus,**kw)
    def sites_P10(self,v,ctx,window=None,focus=None,max_f=3,**kw): return sites10(v,ctx,window=window,focus=focus,**kw)
    def sites_P9(self,v,ctx,window=None,focus=None,max_f=3,**kw): return sites9(v,ctx,window=window,focus=focus)
    def sites_P11(self,v,ctx,window=None,focus=None,max_f=3,**kw): return sites11(v,ctx,window=window,focus=focus)
    def sites_P12(self,v,ctx,window=None,focus=None,max_f=3,**kw): return sites12(v,ctx,window=window,focus=focus)
    P.sites_P12=sites_P12; P.sites_P8=sites_P8; P.sites_P9=sites_P9; P.sites_P10=sites_P10; P.sites_P11=sites_P11
    old_parts=P.parts
    def parts_(self,v,ed):
        if ed.get('prim') in('P8','P9','P10','P11','P12'): return parts(v,ed)
        return old_parts(self,v,ed)
    P.parts=parts_
    old_apply=P.apply
    def apply_(self,v,ed):
        if ed.get('prim') in('P8','P9','P10','P11','P12'): return apply_edit(v.w,ed,v)
        return old_apply(self,v,ed)
    P.apply=apply_
    old_span=P.span
    def span_(self,v,ed):
        if ed.get('prim')=='P8': return ed['idx'][0],ed['idx'][-1]+1
        if ed.get('prim')=='P12': return ed['i'],ed['j']+8
        if ed.get('prim')=='P10': return (ed['i'],ed['i']+1) if ed['kind']=='ev' else (0,len(v.S))
        return old_span(self,v,ed)
    P.span=span_
    P._pe_registered=True

# ------------------------------------------------------------------ site enumeration
def _ctx(v):
    ctx=prims.PLUGIN.prepare(v)
    return ctx
def sites8(v,ctx=None,window=None,focus=None,kinds=('acc','ret'),KMAX=3,W=60,WR=60,ends=True,GMAX=64,WG=400):
    """P8 sites.  acc groups: every prefix of length <= KMAX of the run of consecutive touches of t, PLUS the whole maximal run (up to GMAX events within WG indices).
    (P8GAP: the old fixed cap KMAX=3 hid #5811, a 6-event accumulation; the maximal run is now always a site, so any group size is reachable in one application.)"""
    S=v.S; n=v.n; ctx=ctx or _ctx(v); touch=ctx['touch']; fr=ctx['fr']; bm=ctx['bm']; N=len(S)
    from tkcommon import roles as _roles
    rl=_roles(v.w); lo,hi=window or (0,N)
    def sub(a,b): return a!=b and (bm[a]|bm[b])==bm[b]      # span(a) strictly inside span(b)
    def nest(a,b): return a==b or sub(a,b)
    def cand_frames(r,pos_lo,pos_hi,fmax):
        """frames for register r delivered between touches before pos_lo and after pos_hi: prev/next touch frame (and endpoints), strictly inside fmax"""
        L=touch[r]; k=bisect_left(L,pos_lo); out=[]
        pf=fr[L[k-1]] if k>0 else v.w['initial'][r]
        j=bisect_right(L,pos_hi); nf=fr[L[j]] if j<len(L) else v.w['final'][r]
        for f in (pf,nf):
            if f not in out and sub(f,fmax) and nest(pf,f) and nest(f,nf): out.append(f)
        return out,pf,nf
    for i in range(lo,hi):
        e=S[i]
        if e[0] not in('ADD','COPY'): continue
        t,s=e[1],e[2]
        if focus is not None and t not in focus and s not in focus: continue
        if 'acc' in kinds and e[0]=='ADD' and t<n:
            L=touch[t]; k=bisect_left(L,i); grp=[i]; ok=True
            for j in L[k+1:]:
                if j-i>WG or len(grp)>=GMAX: break
                x=S[j]
                if x[0]=='ADD' and x[1]==t and x[2]!=t: grp.append(j)
                else: break
            for kk in sorted(set(range(1,min(len(grp),KMAX)+1))|{len(grp)}):
                if grp[kk-1]-i>(WG if kk==len(grp) else W): continue
                idx=grp[:kk]; fl=fr[idx[-1]]
                chain=[fr[g] for g in idx]
                if not all(nest(chain[a+1],chain[a]) for a in range(len(chain)-1)): break
                cf,pf,nf=cand_frames(t,idx[0],idx[-1],fl)
                for fp in cf:
                    yield dict(prim='P8',kind='acc',idx=idx,fp=fp,pull=1)
        if 'ret' in kinds:
            L=touch[s]; k=bisect_left(L,i); grp=[i]
            for j in L[k+1:]:
                if j-i>WR or len(grp)>=KMAX: break
                x=S[j]
                if x[0] in('ADD','COPY') and x[2]==s and x[1]!=s: grp.append(j)
                elif x[0] in('ADD','COPY') and x[1]!=s: pass
                else: break
            for kk in range(1,len(grp)+1):
                idx=grp[:kk]; f0=fr[idx[0]]
                # per-read delivery frames: candidates of each target (its prev/next touch frame inside f0; owned COPY targets: their next touch), or the read's own frame
                cl=[]
                for g in idx:
                    tg=S[g][1]
                    if tg>=n:
                        L2=touch[tg]; kq=bisect_right(L2,g); nfq=fr[L2[kq]] if kq<len(L2) else None
                        cf=[nfq] if nfq is not None and sub(nfq,f0) else []
                    else: cf,_,_=cand_frames(tg,g,g,f0)
                    cl.append(list(dict.fromkeys(cf+[fr[g]])))
                pool=list(dict.fromkeys(f for c in cl for f in c if f!=f0 and sub(f,f0)))[:3]
                cl=[list(dict.fromkeys(c+pool)) for c in cl]
                import itertools
                nprod=0
                for combo in itertools.product(*cl):
                    if all(c==fr[g] for c,g in zip(combo,idx)): continue
                    if not all(nest(combo[a+1],combo[a]) for a in range(len(combo)-1)): continue
                    if not nest(combo[0],f0): continue
                    nprod+=1
                    if nprod>12: break
                    yield dict(prim='P8',kind='ret',idx=idx,fps=list(combo),pull=1)
def sites10(v,ctx=None,window=None,focus=None,kinds=('owned','main')):
    """P10: frame labels of owned-lifetime events (INIT/COPY/SCALE/CLEAR of owned registers) and free endpoints of MAIN registers (X final / Y initial)"""
    S=v.S; n=v.n; ctx=ctx or _ctx(v); touch=ctx['touch']; fr=ctx['fr']; N=len(S); lo,hi=window or (0,N)
    from tkcommon import roles as _roles
    rl=_roles(v.w)
    if 'owned' in kinds:
        for i in range(lo,hi):
            e=S[i]; op=e[0]
            if op in('INIT','CLEAR') or (op in('COPY','SCALE') and e[1]>=n):
                cand=[]
                for r in touches(e):
                    if r<n and op=='COPY': pass
                    L=touch[r]; k=bisect_left(L,i)
                    for j in (L[k-1] if k>0 else None, L[k+1] if k+1<len(L) else None):
                        if j is not None and fr[j]!=fr[i] and fr[j] not in cand: cand.append(fr[j])
                for f in cand[:4]: yield dict(prim='P10',kind='ev',i=i,f=f)
    if 'main' in kinds:
        for r in range(n):
            if rl(r) not in('X','Y'): continue
            L=touch[r]
            if not L: continue
            if rl(r)=='X':
                for f in dict.fromkeys(fr[j] for j in L[-3:]):
                    if f!=v.w['final'][r]: yield dict(prim='P10',kind='final',r=r,f=f)
            else:
                for f in dict.fromkeys(fr[j] for j in L[:3]):
                    if f!=v.w['initial'][r]: yield dict(prim='P10',kind='start',r=r,f=f)

# ------------------------------------------------------------------ P12: WEYL EXCHANGE (register identity by exchange; freedom #15)
# Steinberg Weyl element w = x_ab(1) x_ba(-1) x_ab(1) maps (A,B) -> (A+B... ): a+=b; b-=a; a+=b gives (B,-A); one SCALE b,-1 (public SCALE is legal) makes it the exact EXCHANGE (A,B)->(B,A).  4 events.
# P12 = exchange two co-framed PUBLIC registers at index i, run the window S[i:j] with the roles a<->b renamed, exchange back at j.  Values are unchanged (exact); what changes is WHICH register
# carries which chart trajectory over the window (a rests where b would have been): a re-routing of the MOVE paths for 8 extra scalar events.  #5786's hub hand-over (owned 793/792 gadget) uses
# the same Weyl identity as a copy-in (o := H via 5 events, then (f,o) exchanged) for what was and was not reproduced.
def sim_rows(S,n,extra=()):
    """exact (Fraction) final rows of the scalar program S: register r (< n public, or in `extra`) -> {input index: coefficient}.  The value-level oracle for P12 / hand-over constructions (independent of the verifier)."""
    st={}
    def get(r): return st.setdefault(r,{r:Q(1)} if (r<n or r in extra) else {})
    for e in S:
        if e[0]=='ADD':
            a=Q(e[3]); d=get(e[1])
            for k,c in list(get(e[2]).items()):
                x=d.get(k,0)+a*c
                if x==0: d.pop(k,None)
                else: d[k]=x
        elif e[0]=='SCALE':
            c=Q(e[2]); d=get(e[1])
            for k in d: d[k]*=c
        elif e[0]=='COPY': a=Q(e[3]); st[e[1]]={k:a*c for k,c in get(e[2]).items()}
        elif e[0]=='INIT': st[e[1]]={}
        elif e[0]=='CLEAR': st.pop(e[1],None)
    return {r:st.get(r,{r:Q(1)}) for r in list(range(n))+list(extra)}
def weyl_exchange(a,b,f):
    """the 4 events exchanging the contents of a and b (both at chart f)"""
    return [['ADD',a,b,'1',f],['ADD',b,a,'-1',f],['ADD',a,b,'1',f],['SCALE',b,'-1',f]]
def weyl_load(o,h,f_reg,f):
    """#5786 gadget (frame f): o:=H via 4 transvections + SCALE (o was empty), then (f_reg,o) exchanged -> h=H, f_reg=H, o=old f_reg.  9 events."""
    return [['ADD',o,h,'1',f],['ADD',h,o,'1',f],['ADD',o,h,'-1',f],['ADD',h,o,'1',f],['SCALE',o,'-1',f]]+weyl_exchange(f_reg,o,f)
def _swap_ab(e,a,b):
    e=list(e); m={a:b,b:a}
    if e[0] in('ADD','COPY'): e[1]=m.get(e[1],e[1]); e[2]=m.get(e[2],e[2])
    elif e[0] in('SCALE','INIT','CLEAR'): e[1]=m.get(e[1],e[1])
    return e
def p12_apply(S,i,j,a,b,f,f2,pub):
    if not(a<pub and b<pub) or a==b: raise Block('public pair')
    if not(0<=i<=j<=len(S)): raise Block('window')
    if any(e[0] in('INIT','CLEAR') and e[1] in(a,b) for e in S[i:j]): raise Block('lifetime')
    f2=f if f2 is None else f2
    return S[:i]+weyl_exchange(a,b,f)+[_swap_ab(e,a,b) for e in S[i:j]]+weyl_exchange(a,b,f2)+S[j:]
def sites12(v,ctx=None,window=None,focus=None,W=300,per=2):
    """candidate exchanges: an ADD event k between two public registers t,s at chart F; the exchange is inserted before k and undone at the first later touch of t or s at another chart (<=W events)"""
    S=v.S; n=v.n; lo,hi=window or (0,len(S)); touch=(ctx or _ctx(v))['touch']
    for k in range(lo,hi):
        e=S[k]
        if e[0]!='ADD' or e[1]>=n or e[2]>=n: continue
        t,s=e[1],e[2]
        if focus is not None and t not in focus and s not in focus: continue
        F=e[-1]; cnt=0
        for r in (t,s):
            L=touch[r]; q=bisect_right(L,k)
            for x in L[q:q+W]:
                if x-k>W: break
                if S[x][-1]!=F and S[x][0] not in('INIT','CLEAR'):
                    yield dict(prim='P12',i=k,j=x,a=t,b=s,f=F,f2=S[x][-1]); cnt+=1; break
            if cnt>=per: break
register()

# ------------------------------------------------------------------ search driver (own level: pins are conventions, so the exact price ignores the inventory pins)
def exact(w,w2,ev=None):
    """exact price of w2: legality + kappa with the stamped pins (M.evaluate honours word['verifier_profile'])"""
    o=M.evaluate(w2); return o
def level(w,kinds=('acc','ret'),window=None,focus=None,topq=20,sample=None,st=None,log=print,tl=1e9,KMAX=3,minq=None,WR=60):
    st=st or prims.Stats(); v=M.View(w); ctx=_ctx(v); v._pe_ctx=ctx; priced=[]; n=0
    for ed in sites8(v,ctx,window=window,focus=focus,kinds=kinds,KMAX=KMAX,WR=WR):
        n+=1; st.sites+=1
        if sample and n%sample: continue
        try: k=fast(v,ed)
        except (Block,ValueError,KeyError,IndexError,AssertionError): k=None
        st.quick+=1
        if k is not None: priced.append((k,ed))
        if time.time()-st.t0>tl: break
    priced.sort(key=lambda x:-x[0]); out=[]
    for k,ed in priced[:topq]:
        if minq is not None and k<minq: break
        try: w2=apply_edit(w,ed,v)
        except (Block,ValueError,KeyError,IndexError,AssertionError): continue
        o=M.evaluate(w2); st.exact+=1
        if o.get('legal'): out.append((o['kappa'],w2,ed,o)); st.legal+=1
    out.sort(key=lambda x:-x[0])
    log('    P8 level: %d sites, %d quick-legal, top quick %.12f, %d exact-legal [%s]'%(n,len(priced),priced[0][0] if priced else float('nan'),len(out),st.line()))
    return out

# ------------------------------------------------------------------ P0': SIBLING MERGE (transplant a sibling PR's edit onto a word that already carries another sibling's edit)
# Edits of disjoint support commute (they are P1/P2 applications on disjoint registers/events).  merge3 = diff3 of the scalar programs on the event keys; transplant_frames = replay the pure
# frame relabels (P2) of word A over its base B onto a third word C aligned with B (used for the #5796 retime on #5802).  Found by MOREPRIMS: #5795 and #5796 stack on #5802 exactly additively.
def _key(e): return tuple(map(str,e))
def _kf(e): return tuple(e[:-1]) if e[0] not in('INIT','CLEAR') else tuple(e[:2])
def merge3(Wb,Wa,Wc):
    """base word Wb, word Wa = Wb + edit_a, word Wc = Wb + edit_c (disjoint regions) -> (scalar program of Wb+edit_a+edit_c, overlap list).  Endpoints: caller merges initial/final"""
    import difflib
    S=lambda w:[e for e in w['program'] if e[0]!='MOVE']
    B=S(Wb); Bk=[_key(e) for e in B]; ops=[]
    for who,Wx in(('a',Wa),('c',Wc)):
        X=S(Wx); sm=difflib.SequenceMatcher(None,Bk,[_key(e) for e in X],autojunk=False)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag!='equal': ops.append((i1,i2,[list(e) for e in X[j1:j2]],who))
    ops.sort(key=lambda o:(o[0],o[1])); ov=[(x[:2],y[:2]) for x,y in zip(ops,ops[1:]) if y[0]<x[1] or y[0]==x[0]]
    out=[list(e) for e in B]
    for (i1,i2,new,who) in sorted(ops,key=lambda o:-o[0]): out[i1:i2]=new
    return out,ov
def transplant_frames(Wb,Wa,Wc):
    """frame relabels of Wa over Wb (same scalar program) replayed on Wc when Wc's event still carries Wb's frame there.  -> (S2 of Wc, applied, skipped)"""
    import difflib
    S=lambda w:[e for e in w['program'] if e[0]!='MOVE']
    Sb,Sa,Sc=S(Wb),S(Wa),S(Wc)
    assert [_kf(e) for e in Sb]==[_kf(e) for e in Sa]
    rel={i:fr_of(Sa[i]) for i in range(len(Sb)) if fr_of(Sa[i])!=fr_of(Sb[i])}
    sm=difflib.SequenceMatcher(None,[_kf(e) for e in Sb],[_kf(e) for e in Sc],autojunk=False); mp={}
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for k in range(i2-i1): mp[i1+k]=j1+k
    S2=[list(e) for e in Sc]; ap=sk=0
    for i,f in rel.items():
        j=mp.get(i)
        if j is None or fr_of(Sc[j])!=fr_of(Sb[i]): sk+=1; continue
        S2[j]=with_frame(S2[j],f); ap+=1
    return S2,ap,sk

# ------------------------------------------------------------------ REALISEFIX: edit-emitting P8 (sedit.py); same S2 as parts(), only the window is built
def _iv(v):
    iv=v.__dict__.get('_pe_iv')
    if iv is None or v.__dict__.get('_pe_iv_S') is not v.S:
        iv=intervals(v.S,v.n); v._pe_iv=iv; v._pe_iv_S=v.S
    return iv
def p8_sedit(v,ed):
    """P8 as a window edit of v.S: identical program to parts(v,ed)[0]; initial/final overrides as in parts.  Falls back to the generic recovery for edits with 'relabel' (S2-indexed)."""
    import sedit as SE
    S=v.S; w=v.w; ini=fin=None
    if ed.get('relabel'):
        S2,ini,fin=parts(v,ed); return SE.from_lists(S,S2,ini,fin)
    idx=ed['idx']; o=ed.get('o')
    if o is None: o=free_owned(S,v,idx[0],idx[-1],_iv(v))
    F={}
    if ed.get('pull'):
        ctx=getattr(v,'_pe_ctx',None)
        if ctx is None: ctx=v._pe_ctx=prims.PLUGIN.prepare(v)
        if ed['kind']=='acc': seeds=[(idx[-1],prims_fr(S,idx[-1]),ed['fp'])]
        else: seeds=[(g,prims_fr(S,g),fp) for g,fp in zip(idx,ed['fps'])]
        backs=[(idx[0],prims_fr(S,idx[0]),ed['fp'],S[idx[0]][1])] if ed['kind']=='acc' else ()
        F,i2,f2=descend(S,ctx,v,seeds,group=set(idx),fwd=True,tregs={S[g][1] for g in idx} if ed['kind']=='ret' else {S[idx[0]][1]},real=(ed['kind']=='ret'),backs=backs,cap=ed.get('cap',300))
        if ed['kind']=='ret':
            for g in idx: F.pop(g,None)
        ini=list(w['initial']) if i2 else None; fin=list(w['final']) if f2 else None
        for r,f in i2.items(): ini[r]=f
        for r,f in f2.items(): fin[r]=f
    lo,hi=idx[0],idx[-1]
    a=min([lo]+list(F)); b=max([hi]+list(F))+1
    Sl=[with_frame(S[i],F[i]) if i in F else S[i] for i in range(a,b)]
    ix=[i-a for i in idx]
    if ed['kind']=='acc': new=acc_apply(Sl,ix,ed['fp'],o,v.n)
    else: new=ret_apply(Sl,ix,ed['fps'],o,v.n)
    for (k,r,f) in ed.get('ends',()):
        if k=='start': ini=ini or list(w['initial']); ini[r]=f
        else: fin=fin or list(w['final']); fin[r]=f
    return SE.SEdit(a,b,new,ini,fin)
