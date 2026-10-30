"""macros -- the macro library of the designer toolkit (MACROS.

A MACRO is a parameterised sequence of prims.py primitives with an ELIGIBILITY predicate learned from the swarm's tricks (module docstring sec. 2: roles, dims, residence frames,
dependencies -- never absolute indices).  Each macro is a movekit-style plugin:  sites(v,ctx,window,hot) -> edits,  apply(v,ed) -> word,  fast(v,ed) -> quick kappa,  and the driver
`search` prices with M.quick then confirms exactly with the INCR evaluator.  An edit is dict(macro=NAME, steps=[prims edits...]) (composites are applied on the scalar program in order,
MOVEs re-derived once at the end), so a dip inside a macro is invisible to the search.
  cofrm    CO-FRAME P1 (#5569, #5565 x5, #5660 last step, #5643): move one ADD to a gap where its operands' frames coincide:  f = common RESIDENCE frame of t,s at the gap (dim f < dim old),
           f = common NEXT-touch frame (exchange, with Steinberg correction), or f = partner's residence frame + helper endpoint companion (hand-off).
  carry    TRANSPORT-CANCEL (#5660 gate rotation): P1c of A creates a correction C; C is carried to a gap where ITS corrections cancel an existing ADD (P0 reduction).  Depth 2, dip hidden.
  rehome   helper start/final change followed by a focused descent on P2 event relabels of the events around it (#5565 tail: start dip, then +; #5569 final).  Dip hidden.
  conj     P3 conjugation of a block interval (#5678), sites from ibase.            inject   P6 compensated relay (#5605 / #5644 / #5713).
  split    P4 two-boundary split (#5718).                                           block    P5 block move (#5739).
CLI:  python3 -B macros.py WORD [--macros cofrm,carry,rehome] [--steps N] [--hot N] [--window LO HI] [--slack S] [--topq K] [--target KAPPA] [--tl SEC] [--out F]"""
import sys,os,json,gzip,time,collections,argparse
from bisect import bisect_left,bisect_right
from fractions import Fraction as Q
import movekit as M
import prims
from prims import PLUGIN as P, Block
from wsearch import guide

class PV:
    """pseudo view: lets prims.parts chain several primitive edits on the scalar program without re-deriving MOVEs in between"""
    def __init__(s,v): s.S=v.S; s.w=dict(v.w); s.n=v.n; s.spans=v.spans
def run_steps(v,steps):
    pv=PV(v); ini=fin=None
    for ed in steps:
        S2,i2,f2=P.parts(pv,ed); pv.S=S2
        if i2: pv.w['initial']=i2; ini=i2
        if f2: pv.w['final']=f2; fin=f2
    return pv.S,ini,fin

def run_steps_edit(v,steps):
    """run_steps as ONE window edit of v.S (REALISEFIX): every step is an SEdit against the intermediate program, read through LazySeq; no intermediate program is built"""
    import sedit as SE
    S0=v.S; pv=PV(v); se=None
    for ed in steps:
        st=P.sedit(pv,ed)
        se=st if se is None else se.then(S0,st)
        pv.S=SE.LazySeq(S0,se)
        if st.ini: pv.w['initial']=st.ini
        if st.fin: pv.w['final']=st.fin
    if se is None: se=SE.SEdit(len(S0),len(S0),[])
    se.view=v; return se
EDITS=prims.EDITS
class Win:
    """read-only sequence = seq, with the window [a,b) materialised once (bounded random access without paying LazySeq per element)"""
    __slots__=('seq','a','b','d')
    def __init__(s,seq,a,b): s.seq=seq; s.a=a; s.b=b; s.d=seq[a:b]
    def __len__(s): return len(s.seq)
    def __getitem__(s,k):
        if isinstance(k,slice): return s.seq[k]
        if s.a<=k<s.b: return s.d[k-s.a]
        return s.seq[k]
class Macro:
    name='?'; doc=''
    def sites(self,v,ctx,window=None,hot=None): raise NotImplementedError
    def scalars(self,v,ed): return run_steps(v,ed['steps'])
    def sedit(self,v,ed): return run_steps_edit(v,ed['steps'])
    def apply(self,v,ed):
        S2,ini,fin=self.scalars(v,ed); return v.rebuild(S2,initial=ini,final=fin)
    def fast(self,v,ed):
        if EDITS: return M.quick(v,self.sedit(v,ed))[0]
        S2,ini,fin=self.scalars(v,ed); return M.quick(v,S2,initial=ini,final=fin)[0]
    def score(self,v,ed):
        """first-order dkappa estimate or None (= price exactly)"""
        if EDITS: return M.quick_score(v,self.sedit(v,ed))
        S2,ini,fin=self.scalars(v,ed); return M.quick_score(v,S2,initial=ini,final=fin)

def _fr(ctx,v):
    return ctx['fr'],[len(b) for b in v.w['frames']]
def frames_at(ctx,v,r,g,skip):
    """(residence frame just before gap g, next-touch frame after it) of register r, ignoring event `skip`"""
    L=ctx['touch'][r]; fr=ctx['fr']; k=bisect_left(L,g)
    j=L[k-1] if k>0 and L[k-1]!=skip else (L[k-2] if k>1 else None)
    res=fr[j] if j is not None else v.w['initial'][r]
    m=k
    if m<len(L) and L[m]==skip: m+=1
    nxt=fr[L[m]] if m<len(L) else (v.w['final'][r] if r<v.n else None)
    return res,nxt

# ------------------------------------------------------------------ cofrm
class CoFrame(Macro):
    name='cofrm'; doc=__doc__
    def sites(self,v,ctx,window=None,hot=None):
        S=v.S; dim=[len(b) for b in v.w['frames']]; hot=set(hot) if hot is not None else None
        for ed in P.sites_P1(v,ctx,window=window,focus=hot):
            i,g,f=ed['i'],ed['g'],ed['f']
            if f is None: continue
            e=S[i]; t,s,fo=e[1],e[2],e[4]
            rt,nt=frames_at(ctx,v,t,g,i); rs,ns=frames_at(ctx,v,s,g,i)
            if 'ends' in ed: tag='part'
            elif rt==rs==f and dim[f]<dim[fo]: tag='cores'
            elif nt==ns==f and f!=fo: tag='conext'
            else: continue
            yield dict(macro=self.name,tag=tag,i=i,steps=[ed])

# ------------------------------------------------------------------ carry
def _new_events(S,S1,lo,hi):
    """events of S1[lo:hi] not present in S[lo:hi] (multiset difference) -> indices in S1"""
    c=collections.Counter(tuple(e) for e in S[lo:hi]); out=[]
    for k in range(lo,hi):
        t=tuple(S1[k])
        if c[t]>0: c[t]-=1
        else: out.append(k)
    return out
from dq import _lcp,_lcs          # FASTSITES: block-compared (C-speed slices), no reversed copies of the whole program
def _lcp_ref(A,B,n):
    if A[:n]==B[:n]: return n
    lo,hi=0,n
    while hi-lo>64:
        mid=(lo+hi)//2
        if A[:mid]==B[:mid]: lo=mid
        else: hi=mid
    while lo<hi and A[lo]==B[lo]: lo+=1
    return lo
def _shift_map(S,S2):
    """-> (p,q): S[:p]==S2[:p], S[-q:]==S2[-q:] (q may be 0); original index j maps to j (j<p) or j+len(S2)-len(S) (j>=len(S)-q), else None"""
    n=min(len(S),len(S2)); p=_lcp(S,S2,n); m=n-p
    q=_lcs(S,S2,m) if m>0 else 0
    return p,q
class Carry(Macro):
    """TRANSPORT-CANCEL.  A (ADD t<-s) passes a conflicting event B: P1c creates the correction C (step 1).  C is carried to a gap near its own operands (step 2), where ITS correction Z
    is the inverse of an existing ADD D (found by a hash on (target,source,-coef), anywhere within MAXD events): step 3 brings Z next to D (P1), P0 cancels the pair.
    Eligible = the composite does not lengthen the program (len <= original) and contains >= 1 cancellation.  #5660: A=`c-=x/2`, B=`x+=h`, C=`c+=h/2`, Z=`c-=2s`, D=`c+=2s`."""
    name='carry'
    MAXRANGE=400; K=3; MAXD=600
    def _gaps(self,S,i,regs,lo_lim,hi_lim):
        gaps=set(); left={r:0 for r in regs}; right={r:0 for r in regs}
        k=i-1
        while k>=lo_lim and any(c<self.K for c in left.values()):
            e=S[k]
            for r in regs:
                if left[r]<self.K and (e[1]==r or (e[0] in('ADD','COPY') and e[2]==r)): left[r]+=1; gaps.update((k,k+1))
            k-=1
        k=i+1
        while k<hi_lim and any(c<self.K for c in right.values()):
            e=S[k]
            for r in regs:
                if right[r]<self.K and (e[1]==r or (e[0] in('ADD','COPY') and e[2]==r)): right[r]+=1; gaps.update((k,k+1))
            k+=1
        gaps.discard(i); gaps.discard(i+1); return sorted(gaps)
    def _res(self,S1,r,g,v):
        k=g-1; lim=max(-1,g-self.MAXRANGE)
        while k>lim:
            e=S1[k]
            if e[1]==r or (e[0] in('ADD','COPY') and e[2]==r): return e[-1] if e[0] not in('INIT','CLEAR') else e[2]
            k-=1
        return None
    def _gaps2(self,S1,c,C,v):
        """(gap, frame) candidates of the carried correction: frame = the keep-frame (None) and the operands' RESIDENCE frames at the gap (the lower common chart, frame 3 in #5660)"""
        for g in self._gaps(S1,c,(C[1],C[2]),max(0,c-self.MAXRANGE),min(len(S1),c+self.MAXRANGE)):
            fs=[None]
            for r in (C[1],C[2]):
                f=self._res(S1,r,g,v)
                if f is not None and f!=C[4] and f not in fs: fs.append(f)
            for f in fs: yield g,f
    def sites(self,v,ctx,window=None,hot=None):
        if not EDITS: yield from self.sites_ref(v,ctx,window,hot); return
        import sedit as SE
        S=v.S; n=len(S); pub=v.n; lo,hi=window or (0,n); hot=set(hot) if hot is not None else None
        H=collections.defaultdict(list)
        for j,e in enumerate(S):
            if e[0]=='ADD': H[(e[1],e[2])].append(j)
        for i in range(lo,hi):
            e=S[i]
            if e[0]!='ADD' or e[1]>=pub or e[2]>=pub: continue
            if hot is not None and e[1] not in hot and e[2] not in hot: continue
            for g1 in self._gaps(S,i,(e[1],e[2]),max(0,i-self.MAXRANGE),min(n,i+self.MAXRANGE)):
                ed1=dict(prim='P1',i=i,g=g1,f=None,fc=None)
                try:
                    pv0=PV(v); se1=P.sedit(pv0,ed1)              # (REALISEFIX: edits against LazySeq views; no S1/S2/S3 lists)
                except (Block,ValueError,IndexError): continue
                S1=SE.LazySeq(S,se1)
                if len(S1)<=n: continue                       # no correction created: a plain commute (cofrm territory)
                a=min(i,g1); b=max(i,g1); d=len(S1)-n
                for c in _new_events(S,Win(S1,a,min(len(S1),b+d+1)),a,min(len(S1),b+d+1)):
                    C=S1[c]
                    if C[0]!='ADD' or C[1]>=pub or C[2]>=pub: continue
                    S1w=Win(S1,max(0,c-2*self.MAXRANGE-2),min(len(S1),c+self.MAXRANGE+2))
                    for g2,f2 in self._gaps2(S1w,c,C,v):
                        ed2=dict(prim='P1',i=c,g=g2,f=f2,fc=None)
                        try:
                            pv=PV(v); pv.S=S1; st2=P.sedit(pv,ed2)
                        except (Block,ValueError,IndexError): continue
                        if st2.ini is None and st2.fin is None and st2.new==S1[st2.p:st2.hi]: continue       # S2==S1
                        se2=se1.then(S,st2); S2=SE.LazySeq(S,se2)
                        if len(S2)<len(S1) and len(S2)<=n: yield dict(macro=self.name,i=i,steps=[ed1,ed2]); continue
                        # step 3: a new correction Z of step 2 meets its inverse D anywhere
                        dl=len(S2)-len(S1)
                        zlo=max(0,min(c,g2)-1); zhi=min(len(S2),max(c,g2)+dl+2)
                        for z in _new_events(S1,Win(S2,zlo,zhi),zlo,zhi):
                            Z=S2[z]
                            if Z[0]!='ADD' or Z[1]>=pub or Z[2]>=pub: continue
                            zc=-Q(Z[3])
                            j0=max(0,z-self.MAXD); j1=min(len(S2),z+self.MAXD); Wn=S2[j0:j1]
                            for jj in range(j0,j1):
                                D=Wn[jj-j0]
                                if jj==z or D[0]!='ADD' or D[1]!=Z[1] or D[2]!=Z[2] or Q(D[3])!=zc: continue
                                ed3=dict(prim='P1',i=z,g=(jj if jj>z else jj+1),f=D[4],fc=None)
                                if ed3['g'] in(z,z+1): continue
                                try:
                                    pv3=PV(v); pv3.S=S2; st3=P.sedit(pv3,ed3)
                                except (Block,ValueError,IndexError): continue
                                if len(S2)+st3.delta<=n and len(S2)+st3.delta<len(S2) : yield dict(macro=self.name,i=i,steps=[ed1,ed2,ed3])
    def sites_ref(self,v,ctx,window=None,hot=None):
        S=v.S; n=len(S); pub=v.n; lo,hi=window or (0,n); hot=set(hot) if hot is not None else None
        H=collections.defaultdict(list)
        for j,e in enumerate(S):
            if e[0]=='ADD': H[(e[1],e[2])].append(j)
        for i in range(lo,hi):
            e=S[i]
            if e[0]!='ADD' or e[1]>=pub or e[2]>=pub: continue
            if hot is not None and e[1] not in hot and e[2] not in hot: continue
            for g1 in self._gaps(S,i,(e[1],e[2]),max(0,i-self.MAXRANGE),min(n,i+self.MAXRANGE)):
                ed1=dict(prim='P1',i=i,g=g1,f=None,fc=None)
                try: S1,_,_=run_steps(v,[ed1])
                except (Block,ValueError,IndexError): continue
                if len(S1)<=n: continue                       # no correction created: a plain commute (cofrm territory)
                a=min(i,g1); b=max(i,g1); d=len(S1)-n
                for c in _new_events(S,S1,a,min(len(S1),b+d+1)):
                    C=S1[c]
                    if C[0]!='ADD' or C[1]>=pub or C[2]>=pub: continue
                    for g2,f2 in self._gaps2(S1,c,C,v):
                        ed2=dict(prim='P1',i=c,g=g2,f=f2,fc=None)
                        try:
                            pv=PV(v); pv.S=S1; S2,_,_=P.parts(pv,ed2)
                        except (Block,ValueError,IndexError): continue
                        if S2==S1: continue
                        if len(S2)<len(S1) and len(S2)<=n: yield dict(macro=self.name,i=i,steps=[ed1,ed2]); continue
                        # step 3: a new correction Z of step 2 meets its inverse D anywhere
                        p,q=_shift_map(S1,S2); m1=len(S1)-q; dl=len(S2)-len(S1)
                        for z in _new_events(S1,S2,max(0,min(c,g2)-1),min(len(S2),max(c,g2)+dl+2)):
                            Z=S2[z]
                            if Z[0]!='ADD' or Z[1]>=pub or Z[2]>=pub: continue
                            zc=-Q(Z[3])
                            for jj in range(max(0,z-self.MAXD),min(len(S2),z+self.MAXD)):
                                D=S2[jj]
                                if jj==z or D[0]!='ADD' or D[1]!=Z[1] or D[2]!=Z[2] or Q(D[3])!=zc: continue
                                ed3=dict(prim='P1',i=z,g=(jj if jj>z else jj+1),f=S2[jj][4],fc=None)
                                if ed3['g'] in(z,z+1): continue
                                try:
                                    pv=PV(v); pv.S=S2; S3,_,_=P.parts(pv,ed3)
                                except (Block,ValueError,IndexError): continue
                                if len(S3)<=n and len(S3)<len(S2) : yield dict(macro=self.name,i=i,steps=[ed1,ed2,ed3])

# ------------------------------------------------------------------ rehome
class Rehome(Macro):
    name='rehome'; DESC=8; NF=3; MAXEXP=40; DIPMAX=2e-6; STONES=12; KT=10; NT=8; RAD=1
    def sites(self,v,ctx,window=None,hot=None):
        """every helper start/final candidate is priced at the ENDPOINT-ONLY level (quick, ~7 ms); only the MAXEXP least-dipping legal ones are expanded by the descent (30 s each)"""
        from tkcommon import roles
        rl=roles(v.w); fr=ctx['fr']; touch=ctx['touch']; w=v.w; cand=[]
        order=list(hot) if isinstance(hot,list) else [r for r in range(v.n) if hot is None or r in hot]
        k0=M.quick(v,v.S)[0]
        for r in order:
            if r>=v.n or rl(r)!='helper' or not touch[r]: continue
            L=touch[r]
            for kind,Ls in (('start',L[:self.NF]),('final',L[-self.NF:])):
                fl=[fr[j] for j in Ls]               # frames of its own first/last touches ...
                for j in Ls:                           # ... and the PARTNERS' residence frames at those touches (the co-residence chart: frame 3 in #5565)
                    e=v.S[j]
                    if e[0]=='ADD':
                        p=e[2] if e[1]==r else e[1]
                        if p<v.n: fl.append(frames_at(ctx,v,p,j,j)[0])
                for f in dict.fromkeys(fl):
                    if f==w['initial' if kind=='start' else 'final'][r]: continue
                    ed=dict(macro=self.name,kind=kind,r=r,f=f,steps=[dict(prim='P2',kind=kind,r=r,f=f)])
                    try: S2,ini,fin=run_steps(v,ed['steps']); k=M.quick(v,S2,initial=ini,final=fin)[0]
                    except (ValueError,KeyError,IndexError,Block): continue
                    if k is None or (k0 is not None and k<k0-self.DIPMAX): continue
                    cand.append((k,ed))
        cand.sort(key=lambda x:-x[0])
        for k,ed in cand[:self.MAXEXP]: yield ed
    def _children(self,v,ctx,S2,ini,fin,near,r):
        """single-step children of the CURRENT scalar program (S2 with the endpoints ini/fin): P2 ev relabels around the helper's chain + P1 moves of ADDs touching the helper"""
        pv=PV(v); pv.S=S2; pv.spans=v.spans; w=dict(v.w)
        if ini: w['initial']=ini
        if fin: w['final']=fin
        pv.w=w; c2=P.prepare(pv)
        T=c2['touch'][r]; foc=set()
        for j in T[:self.NT]+T[-4:]:
            for jj in range(max(0,j-self.RAD),min(len(S2),j+self.RAD+1)):
                if S2[jj][0]=='ADD': foc|={S2[jj][1],S2[jj][2]}
        yield from list(P.sites_P2(pv,c2,focus=foc,kinds=('ev',)))
        old=P.P1_TOUCH; P.P1_TOUCH=self.KT
        try:
            for ed2 in list(P.sites_P1(pv,c2,focus={r},ends=False)):
                if ed2.get('f') is not None: yield ed2
        finally: P.P1_TOUCH=old
    def _price(self,v,S2,ed2,ini,fin):
        pv=PV(v); pv.S=S2; w=dict(v.w)
        if ini: w['initial']=ini
        if fin: w['final']=fin
        pv.w=w
        S3,i3,f3=P.parts(pv,ed2); return S3,(i3 or ini),(f3 or fin),M.quick(v,S3,initial=i3 or ini,final=f3 or fin)[0]
    def _expand(self,v,ed):
        """the descent (dip hidden): after the endpoint change, greedily apply P2 ev relabels / P1 co-frame moves around the helper while the quick price improves; a NEUTRAL child (|dk|<1e-12)
        is allowed as a stepping stone when one of ITS children improves (the Y113 hoist of #5565).  cached in ed['_exp'] = (steps, kappa)"""
        if '_exp' in ed: return ed['_exp']
        ctx=P.prepare(v); r=ed['r']; S=v.S; steps=list(ed['steps'])
        S2,ini,fin=run_steps(v,steps); k=M.quick(v,S2,initial=ini,final=fin)[0]
        if k is None: ed['_exp']=(steps,-1.0); return ed['_exp']
        T=ctx['touch'][r]; near=set()
        for j in T[:self.NT]+T[-4:]:
            for jj in range(max(0,j-self.RAD),min(len(S),j+self.RAD+1)):
                if S[jj][0]=='ADD': near|={S[jj][1],S[jj][2]}
        for it in range(self.DESC):
            ch=[]
            for ed2 in self._children(v,ctx,S2,ini,fin,near,r):
                try: S3,i3,f3,k3=self._price(v,S2,ed2,ini,fin)
                except (ValueError,KeyError,IndexError,Block): continue
                if k3 is not None: ch.append((k3,ed2,S3,i3,f3))
            ch.sort(key=lambda x:-x[0])
            if ch and ch[0][0]>k+1e-15:
                k,ed2,S2,ini,fin=ch[0]; steps.append(ed2); continue
            stepped=False
            for k3,ed2,S3,i3,f3 in [c for c in ch if c[0]>=k-1e-12 and c[1]['prim']=='P1'][:self.STONES]:
                sub=[]
                for ed3 in self._children(v,ctx,S3,i3,f3,near,r):
                    try: S4,i4,f4,k4=self._price(v,S3,ed3,i3,f3)
                    except (ValueError,KeyError,IndexError,Block): continue
                    if k4 is not None and k4>k+1e-15: sub.append((k4,ed3,S4,i4,f4))
                if sub:
                    sub.sort(key=lambda x:-x[0]); k4,ed3,S4,i4,f4=sub[0]; steps+=[ed2,ed3]; k,S2,ini,fin=k4,S4,i4,f4; stepped=True; break
            if not stepped: break
        ed['_exp']=(steps,k); return ed['_exp']
    def scalars(self,v,ed): return run_steps(v,self._expand(v,ed)[0])
    def sedit(self,v,ed): return run_steps_edit(v,self._expand(v,ed)[0])
    def fast(self,v,ed):
        k=self._expand(v,ed)[1]; return k if k>0 else None
    def apply(self,v,ed):
        S2,ini,fin=self.scalars(v,ed); return v.rebuild(S2,initial=ini,final=fin)

# ------------------------------------------------------------------ wrappers on the delegated primitives
class Wrap(Macro):
    prim='?'; kw={}
    def sites(self,v,ctx,window=None,hot=None):
        for ed in getattr(P,'sites_'+self.prim)(v,ctx,window=window,focus=None,**self.kw): yield dict(macro=self.name,steps=[ed])
    def scalars(self,v,ed): raise ValueError('delegated')
    def apply(self,v,ed): return P.apply(v,ed['steps'][0])
    def fast(self,v,ed): return P.fast(v,ed['steps'][0])
    def score(self,v,ed): return P.score(v,ed['steps'][0]) if ed['steps'][0].get('prim') in('P1','P2','P3') else None
class Conj(Wrap): name='conj'; prim='P3'
class Inject(Wrap): name='inject'; prim='P6'
class Split(Wrap): name='split'; prim='P4'
class Block_(Wrap): name='block'; prim='P5'
LIB={m.name:m for m in (CoFrame(),Carry(),Rehome(),Conj(),Inject(),Split(),Block_())}

# ------------------------------------------------------------------ guided search driver
class Stats:
    def __init__(s): s.sites=0; s.quick=0; s.exact=0; s.t0=time.time(); s.cpu0=time.process_time(); s.macro=collections.Counter()
    def cpu_min(s): return (time.process_time()-s.cpu0)/60
    def line(s): return 'sites %d quick %d exact %d  wall %.1fs cpu %.2f min'%(s.sites,s.quick,s.exact,time.time()-s.t0,s.cpu_min())
SCREEN=dict(k=0,audit=False,log=[])           # first-order screening (FASTSITES item 3): k>0: price exactly only the top-k sites by first-order dkappa; audit: also price all exactly and record the recall
def level(w,macros,window=None,hot=None,topq=20,st=None,log=None,tl=1e9,minq=None,focus=None,exact_floor=None,screen_k=None,screen_audit=None):
    """one macro level on word w: enumerate every macro's sites (touching `hot`), price with quick, confirm the best topq exactly.  -> sorted [(kappa, word, edit)] (legal+ok)
    screen_k>0: sites are first ranked by the first-order dkappa of the invoice-total delta (movekit.quick_score); only the top screen_k (and every site the screen cannot score) get the exact quick price"""
    st=st or Stats(); ev=prims.evaluator(); v=M.View(w); ctx=P.prepare(v); priced=[]
    sk=SCREEN['k'] if screen_k is None else screen_k; audit=SCREEN['audit'] if screen_audit is None else screen_audit; scr=[]
    if sk:
        for _ in range(M.DQ_AFTER+1): M.quick(v,v.S)          # make the delta base before scoring
    for m in macros:
        n0=st.sites
        try: gen=m.sites(v,ctx,window=window,hot=hot)
        except Exception as ex: log and log('   %s sites error %r'%(m.name,ex)); continue
        for ed in gen:
            st.sites+=1
            if focus is not None and not (edit_focus(v,ed)&focus): continue
            if sk:
                try: sc=m.score(v,ed)
                except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): sc=float('-inf')
                if sc==float('-inf'): continue          # illegal under the trajectory census (exact quick would be None too)
                scr.append((sc,m,ed))
                if time.time()-st.t0>tl: break
                continue
            try: k=m.fast(v,ed)
            except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): k=None
            st.quick+=1
            if k is not None: priced.append((k,m,ed))
            if time.time()-st.t0>tl: break
        st.macro[m.name]+=st.sites-n0
    if sk:
        scr.sort(key=lambda x:-(x[0] if x[0] is not None else 1e9))          # unscorable sites first (exact), then by estimated gain
        full=[]
        for rank,(sc,m,ed) in enumerate(scr):
            if rank>=sk and not audit: break
            try: k=m.fast(v,ed)
            except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError,ZeroDivisionError): k=None
            st.quick+=1
            if k is not None:
                full.append((k,m,ed,rank))
                if rank<sk: priced.append((k,m,ed))
        if audit and full:
            ex=sorted(full,key=lambda x:-x[0])[:topq]; hit=sum(1 for x in ex if x[3]<sk)
            SCREEN['log'].append(dict(sites=len(scr),screened=sk,topq=topq,recall=hit/max(1,len(ex)),worst_rank=max(x[3] for x in ex)))
            log and log('    screen: top-%d exact sites, %d inside the first-order top-%d (recall %.2f, worst rank %d of %d)'%(len(ex),hit,sk,hit/max(1,len(ex)),max(x[3] for x in ex),len(scr)))
    priced.sort(key=lambda x:-x[0]); out=[]
    for k,m,ed in priced[:topq]:
        if minq is not None and k<minq: break
        try: w2=m.apply(v,ed)
        except (Block,ValueError,KeyError,IndexError,AssertionError,TypeError): continue
        o=M.evaluate(w2) if ed['steps'][0].get('prim')=='P4' else ev.evaluate(w2,base=w); st.exact+=1
        if o.get('legal') and o.get('ok'): out.append((o['kappa'],w2,ed))
    out.sort(key=lambda x:-x[0])
    if log: log('    level %s: %d sites, %d quick-priced, top quick %.12f, %d exact-legal  [%s]'%(','.join(m.name for m in macros),st.sites,len(priced),priced[0][0] if priced else float('nan'),len(out),st.line()))
    return out
def edit_focus(v,ed):
    r=set()
    for s_ in ed['steps'][:1]:          # later steps index the intermediate program
        if s_.get('prim')=='P1': e=v.S[s_['i']] if s_['i']<len(v.S) else None; r|={e[1],e[2]} if e else set()
        if 'r' in s_: r.add(s_['r'])
    for k_ in('r',):
        if k_ in ed: r.add(ed[k_])
    return r
def search(w,macros,steps=10,hot_n=0,window=None,topq=20,slack=0.0,dip_width=8,target=None,tl=1e9,log=print,st=None):
    """greedy macro search with dip tolerance.  hot_n>0: only ADDs touching the hot_n hottest registers (marginal-cost steering).  slack>0: when no macro improves, the best candidates
    within `slack` below the current kappa are expanded one more macro level (focused on the registers they touched); the PAIR is adopted if it beats the current kappa.
    -> (kappa, word, chain, stats)"""
    st=st or Stats(); w=M.pin(w); k=M.evaluate(w)['kappa']; k0=k; chain=[]
    stages=macros if macros and isinstance(macros[0],list) else [macros]
    for step in range(steps):
        hot=guide.hot_list(w,hot_n) if hot_n else None
        imp=[]; ch=[]
        for stage in stages:
            ch=level(w,stage,window=window,hot=hot,topq=topq,st=st,log=log,tl=tl,minq=k-slack if slack else None)
            imp=[c for c in ch if c[0]>k+1e-15]
            if imp: break
        macros=[m for stg in stages for m in stg]
        if imp:
            k,w,ed=imp[0]; chain.append(dict(ed,_exp=None)); log('  step %d: %s -> %.15f (%+.3e)  [%s]'%(step+1,json.dumps({a:b for a,b in ed.items() if a!='_exp'})[:160],k,k-k0,st.line()))
        elif slack:
            done=False; seeds=guide.Dip(slack,dip_width).seeds(k,[(c[0],c[1],c[2]) for c in ch])
            for ks,ws,eds in seeds:
                v=M.View(w); fr_=edit_focus(v,eds); foc=fr_|guide_neighbors(M.View(ws),fr_)
                ch2=level(ws,macros,window=None,hot=None,topq=topq,st=st,log=None,tl=tl,focus=foc)
                if ch2 and ch2[0][0]>k+1e-15:
                    k2,w2,ed2=ch2[0]; chain.append(dict(eds,_exp=None)); chain.append(dict(ed2,_exp=None)); log('  step %d: DIP PAIR %.3e then %.15f (%+.3e)  [%s]'%(step+1,ks-k,k2,k2-k0,st.line())); k,w=k2,w2; done=True; break
            if not done: break
        else: break
        if target is not None and k>=target-1e-13: break
        if time.time()-st.t0>tl: break
    return k,w,chain,st
def guide_neighbors(v,regs,radius=3):
    """registers sharing an ADD within `radius` events of a touch of regs (the chain the dip step opened)"""
    S=v.S; out=set(); idx=[i for i,e in enumerate(S) if e[1] in regs or (e[0] in('ADD','COPY') and e[2] in regs)]
    for i in idx[:400]:
        for j in range(max(0,i-radius),min(len(S),i+radius+1)):
            if S[j][0]=='ADD': out|={S[j][1],S[j][2]}
    return out

def main():
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--macros',default='cofrm,carry,rehome'); ap.add_argument('--steps',type=int,default=10)
    ap.add_argument('--hot',type=int,default=0); ap.add_argument('--window',nargs=2,type=int); ap.add_argument('--slack',type=float,default=0.0); ap.add_argument('--topq',type=int,default=20)
    ap.add_argument('--target',type=float); ap.add_argument('--tl',type=float,default=1e9); ap.add_argument('--out'); ap.add_argument('--dip-width',type=int,default=8)
    ap.add_argument('--screen',type=int,default=0,help='first-order screening: exact-quick only the top-K sites by estimated dkappa (0 = off, price every site exactly)'); ap.add_argument('--screen-audit',action='store_true',help='also price every site exactly and report the screen recall'); a=ap.parse_args()
    SCREEN['k']=a.screen; SCREEN['audit']=a.screen_audit
    from tkcommon import load
    p,w=load(a.word); ms=[[LIB[x] for x in stg.split(',') if x] for stg in a.macros.split(';')]; log=lambda *x:print(*x,flush=True)
    k,w2,chain,st=search(w,ms,steps=a.steps,hot_n=a.hot,window=tuple(a.window) if a.window else None,topq=a.topq,slack=a.slack,dip_width=a.dip_width,target=a.target,tl=a.tl,log=log)
    print('RESULT kappa %.15f chain %d |'%(k,len(chain)),st.line(),dict(st.macro))
    if a.out and chain: json.dump(w2,gzip.open(a.out,'wt'))
if __name__=='__main__': main()
