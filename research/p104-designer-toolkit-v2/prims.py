"""prims -- the universal rewrite basis of the designer toolkit (PRIMITIVES.

Every swarm trick is hypothesised to be a short composition of a few generic, value-preserving rewrite PRIMITIVES.  One movekit plugin (`prims`) exposes them:
  P1  move an ADD event to another gap.  Strict commute (P1s: independent events / reads of one source / additive writes) is free; passing a conflicting ADD uses the
      Steinberg relation [A,B] = [C,B,A] and inserts the correction automatically (P1c):   A=ADD(t<-s,a), B=ADD(u<-t,b) -> C=ADD(u<-s,ab);   B=ADD(s<-v,b) -> C=ADD(t<-v,-ab).
      SCALE/COPY/INIT/CLEAR of t or s and the mutually-conflicting pair (v==t and u==s) are barriers.  Optional frame labels: f (moved event), fc (corrections).  P0 (merge of
      same-frame duplicate ADDs, cancellation of inverse pairs) is applied around the touched region.
  P2  re-time / re-frame the free variables: kind ev (one event's chart), blk (a block's chart), start / final (helper endpoint frame).  MOVEs are derived (View.rebuild).
  P3  conjugate a window by a transvection R=I+qE_ab: insert a+=q*b, rewrite the window (own derivation from the matrix identity T E T^-1), insert a-=q*b.
      Sites come from ibase (proxy screen); the rewrite is independent code (tests/prims_test.py checks it event for event against ibase.conj_events).
  P4  register split (rank split with distinct bases, #5718): delegated to split2.   (hand-off P4t = tk handoff, copy chains P4c, merge: not implemented here, see notes)
  P5  move a block to another chart: delegated to blockmove.
  P6  inject + undo with the undo SOLVED (spansolve/relaycomp.absorb): compensated relay, #5605 / #5644 / #5713 (P3x = the exact-equality subcase).
Every application is checked and priced EXACTLY with incr.IncrWord (see `search`); sites are ranked with movekit.quick (trajectory-exact census).

    tk-style:   python3 prims.py WORD --prims P1,P2 [--window LO HI] [--list N]
    python:     import prims; P=prims.PLUGIN; v=M.View(w); sites=list(P.sites(v,P.prepare(v),prims=('P1',)))
"""
import sys,os,json,gzip,time,collections,itertools,random,argparse
from bisect import bisect_left,bisect_right
from fractions import Fraction as Q
import movekit as M
from movekit import qs
import ibase,blockmove,split2,relay
import tkcommon as _TC
for _a in ('5627','5666','5684','5643','5605','5608','5795'):          # words without a shipped alias (runtime only; no shared file touched)
    for _d in (_TC.HERE+'/words', os.path.dirname(os.path.abspath(__file__)) + '/ext/TKMOVES/words',os.path.dirname(os.path.abspath(__file__)) + '/ext/RELAYGEN/words'):
        _f='%s/%s.json.gz'%(_d,_a)
        if os.path.exists(_f) and _a not in _TC.ALIASES: _TC.ALIASES[_a]=_f

class Block(Exception): pass
EDITS=os.environ.get('TK_EDITS','1')!='0'       # REALISEFIX: edit-emitting fast/score path on/off (reads the environment, never sets it)

# ---------------------------------------------------------------- P1
def _corr(t,s,a,B,side):
    """corrections for the ADD A=(t<-s,a) passing the event B.  side=+1: A moves right ([A,B] -> [C,B,A], C before B); side=-1: A moves left ([B,A] -> [A,B,C], C after B).
    -> list of (target,source,coef Fraction, frame_of_B) ; Block if the pair does not commute even up to a correction"""
    op=B[0]
    if op=='ADD':
        u,v=B[1],B[2]; x1=(v==t); x2=(u==s)
        if x1 and x2: raise Block('mutual')
        if not x1 and not x2: return []
        b=Q(B[3])
        if x1: return [(u,s,side*a*b,B[4])]            # B reads what A writes: u += ab*s
        return [(t,v,-side*a*b,B[4])]                  # B writes what A reads: t += -ab*v
    if op=='SCALE':
        if B[1] in(t,s): raise Block('scale')
        return []
    if op=='COPY':
        if B[1] in(t,s) or B[2] in(t,s): raise Block('copy')
        return []
    if op in('INIT','CLEAR'):
        if B[1] in(t,s): raise Block('life')
        return []
    raise Block('op')
def p1_apply(S,i,g,f=None,fc=None,pub=None):
    """move ADD S[i] to gap g (g<=i: before original S[g]; g>i: after original S[g-1]).  -> (S2, (lo,hi)) with the touched region of S2"""
    A=S[i]
    if A[0]!='ADD': raise Block('not add')
    t,s,a=A[1],A[2],Q(A[3])
    if pub is not None and (t>=pub or s>=pub): raise Block('owned')
    An=['ADD',t,s,A[3],A[4] if f is None else f]
    if g==i or g==i+1: raise Block('noop')
    if g>i+1:
        mid=[]
        for k in range(i+1,g):
            B=S[k]; cs=_corr(t,s,a,B,+1)
            for (u,v,c,fb) in cs: mid.append(['ADD',u,v,qs(c),fb if fc is None else fc])
            mid.append(B)
        S2=S[:i]+mid+[An]+S[g:]; lo,hi=i,i+len(mid)
    else:
        tail=[]
        for k in range(i-1,g-1,-1):
            B=S[k]; cs=_corr(t,s,a,B,-1)
            tail=[B]+[['ADD',u,v,qs(c),fb if fc is None else fc] for (u,v,c,fb) in cs]+tail
        S2=S[:g]+[An]+tail+S[i+1:]; lo,hi=g,g+len(tail)
    return S2,(lo,hi)
def p0_merge(S,lo,hi,pad=24):
    """P0 on the region [lo-pad,hi+pad] of S (ibase.merge: duplicate ADD(t,s) of one frame, cancelling inverse pairs).  -> S2"""
    a=max(0,lo-pad); b=min(len(S),hi+pad+1)
    mid=ibase.merge([list(e) for e in S[a:b]])
    return S[:a]+mid+S[b:]

# ---------------------------------------------------------------- P3 (own derivation)
def conj_window(evs,a,b,q,pub):
    """T E T^-1 for T=I+qE_ab (state update  x_a += q x_b) applied to each ADD E=I+c E_uv of the window:
    (I+qE_ab)(I+cE_uv)(I-qE_ab) = I + cE_uv + qc[b==u]E_av - qc[v==a]E_ub - q^2c[b==u][v==a]E_ab
    b==u only: extra ADD(a<-v, qc);  v==a only: extra ADD(u<-b, -qc);  both: not elementary (Block).  SCALE/COPY of a,b are barriers."""
    out=[]
    for e in evs:
        op=e[0]
        if op=='SCALE' and e[1] in(a,b): raise Block('scale')
        if op=='COPY' and (e[1] in(a,b) or e[2] in(a,b)): raise Block('copy')
        if op=='ADD':
            u,v,f=e[1],e[2],e[4]; wa=(b==u); rd=(v==a)
            if wa and rd: raise Block('ba')
            if wa or rd:
                if (wa and v>=pub) or (rd and u>=pub): raise Block('owned')
                c=ibase.Qm(e[3])          # (FASTSITES: parse the coefficient only for the events that change; memoised)
                out.append(list(e))
                if wa: out.append(['ADD',a,v,qs(q*c),f])
                else: out.append(['ADD',u,b,qs(-q*c),f])
                continue
        out.append(list(e))
    return out
def p3_apply(S,i0,i1,a,b,q,ef,xf,pub):
    mid=ibase.merge(conj_window(S[i0:i1+1],a,b,q,pub))
    return S[:i0]+[['ADD',a,b,qs(q),ef]]+mid+[['ADD',a,b,qs(-q),xf]]+S[i1+1:]

# ---------------------------------------------------------------- P2
def p2_event(S,i,f):
    e=list(S[i])
    if e[0] in('INIT','CLEAR'): e[2]=f
    else: e[-1]=f
    return S[:i]+[e]+S[i+1:]

# ---------------------------------------------------------------- the plugin
class Prims(M.Plugin):
    """dispatcher plugin: edit = dict(prim='P1'|'P2'|'P3'|'P4'|'P5', ...)"""
    name='prims'; quick=False; doc=__doc__; site_fields=('prim','i','g','kind','r','f')
    P1_TOUCH=3          # nearest touching events per register and side that define candidate gaps
    P1_MAXDIST=20000    # max events a moved ADD may pass
    def prepare(self,v):
        S=v.S; touch=collections.defaultdict(list)
        for i,e in enumerate(S):
            op=e[0]
            if op=='ADD': touch[e[1]].append(i); touch[e[2]].append(i)
            elif op=='COPY': touch[e[1]].append(i); touch[e[2]].append(i)
            else: touch[e[1]].append(i)
        fr=[(e[2] if e[0] in('INIT','CLEAR') else e[-1]) for e in S]
        bm=[0]*len(v.w['frames'])
        for k,sp in enumerate(v.spans):
            m=0
            for x in sp: m|=1<<x
            bm[k]=m
        return dict(touch=touch,fr=fr,bm=bm)
    @staticmethod
    def le(bm,a,b):
        """a -> b is a legal MOVE (or no move): same frame id, or span(a) strictly inside span(b)"""
        return a==b or (bm[a]!=bm[b] and (bm[a]|bm[b])==bm[b])
    def chain_ok(self,v,ctx,r,p,f,skip,ini=None,fin=None):
        """register r at frame f at (fractional) position p keeps a nested chain with its neighbouring touches (event `skip` ignored); cheap static legality filter of P1 sites"""
        L=ctx['touch'][r]; fr=ctx['fr']; bm=ctx['bm']; k=bisect_left(L,p); j=k-1
        if j>=0 and L[j]==skip: j-=1
        pf=fr[L[j]] if j>=0 else (ini if ini is not None else v.w['initial'][r])
        m=k
        if m<len(L) and L[m]==skip: m+=1
        if m<len(L): nf=fr[L[m]]
        else: nf=(fin if fin is not None else v.w['final'][r]) if r<v.n else None
        return self.le(bm,pf,f) and (nf is None or self.le(bm,f,nf))
    # ---- site generators
    def sites(self,v,ctx,prims=('P1','P2'),window=None,focus=None,max_f=None):
        """window=(lo,hi): only events with lo<=i<hi are moved/relabelled;  focus=set of registers: only edits touching them"""
        for p in prims:
            g=getattr(self,'sites_'+p)
            yield from (g(v,ctx,window=window,focus=focus) if max_f is None else g(v,ctx,window=window,focus=focus,max_f=max_f))
    def sites_P1(self,v,ctx,window=None,focus=None,max_f=6,ends=True):
        S=v.S; pub=v.n; touch=ctx['touch']; fr=ctx['fr']; n=len(S); K=self.P1_TOUCH
        from tkcommon import roles as _roles
        rl=_roles(v.w); helpers={r for r in range(pub) if rl(r)=='helper'} if ends else set()
        lo,hi=window or (0,n)
        for i in range(lo,hi):
            e=S[i]
            if e[0]!='ADD' or e[1]>=pub or e[2]>=pub: continue
            t,s=e[1],e[2]
            if focus is not None and t not in focus and s not in focus: continue
            gaps=set()
            for r in (t,s):
                L=touch[r]; k=bisect_left(L,i)
                for j in L[max(0,k-K):k]: gaps.update((j,j+1))              # left: before / after an earlier touch
                for j in L[k+1:k+1+K]: gaps.update((j,j+1))                 # right
            for g in sorted(gaps):
                if g==i or g==i+1 or g<0 or g>n or abs(g-i)>self.P1_MAXDIST: continue
                fs=[None]
                for r in (t,s):        # residence frame of the operand just before the gap, frame of its next touch, then the neighbouring events' frames
                    L=touch[r]; k=bisect_left(L,g)
                    cand=[]
                    if k>0 and L[k-1]!=i: cand.append(fr[L[k-1]])
                    elif k>1: cand.append(fr[L[k-2]])
                    else: cand.append(v.w['initial'][r])
                    if k<len(L) and L[k]!=i: cand.append(fr[L[k]])
                    elif k+1<len(L): cand.append(fr[L[k+1]])
                    for f in cand:
                        if f!=e[4] and f not in fs: fs.append(f)
                for j in (g-1,g):
                    if 0<=j<n and j!=i and fr[j]!=e[4] and fr[j] not in fs: fs.append(fr[j])
                # corrections: the conflicting events passed (only events touching t or s can conflict) -> their registers' residence frames are the candidate correction charts
                fcs=[None]; a_=Q(e[3]); side=1 if g>i else -1
                lo_,hi_=(i+1,g) if g>i else (g,i)
                cpos=None; creg=set(); cors=[]
                try:
                    for r in (t,s):
                        L=touch[r]
                        for k in range(bisect_left(L,lo_),bisect_left(L,hi_)):
                            j=L[k]
                            for (u_,v_,c_,fb_) in _corr(t,s,a_,S[j],side):
                                creg.add(u_); creg.add(v_); cpos=j if cpos is None else min(cpos,j); cors.append((u_,v_,fb_,j))
                except Block: continue
                if creg:
                    for r in creg:
                        L=touch[r]; k=bisect_left(L,cpos)
                        for kk in (k-1,k):
                            if 0<=kk<len(L) and L[kk]!=i and fr[L[kk]] not in fcs: fcs.append(fr[L[kk]])
                        if not L and v.w['initial'][r] not in fcs: fcs.append(v.w['initial'][r])
                    fcs=fcs[:4]
                else: fcs=[None]
                for f in fs[:max_f]:
                    fe=e[4] if f is None else f
                    if not(self.chain_ok(v,ctx,t,g-.5,fe,i) and self.chain_ok(v,ctx,s,g-.5,fe,i)): continue
                    for fc_ in fcs:
                        if cors and not all(self.chain_ok(v,ctx,x_,j+(-.25 if g>i else .25),(fc_ if fc_ is not None else fb_),i) for (u_,v_,fb_,j) in cors for x_ in (u_,v_)): continue
                        yield dict(prim='P1',i=i,g=g,f=f,fc=fc_)
                for f in fs[:max_f]:
                    if f is None or not ends: continue
                    en=[]          # fused P2 companion: a helper whose first/last touch becomes this ADD follows it (start/final frame = f)
                    for r in (t,s):
                        if r not in helpers: continue
                        L=touch[r]
                        mx=L[-1] if L[-1]!=i else (L[-2] if len(L)>1 else -1); mn=L[0] if L[0]!=i else (L[1] if len(L)>1 else n)
                        if mx<g: en.append(['final',r,f])
                        if mn>=g: en.append(['start',r,f])
                    for x in en: yield dict(prim='P1',i=i,g=g,f=f,fc=None,ends=[x])
    def sites_P2(self,v,ctx,window=None,focus=None,max_f=4,kinds=('ev','start','final')):
        S=v.S; pub=v.n; touch=ctx['touch']; fr=ctx['fr']; n=len(S); w=v.w
        lo,hi=window or (0,n)
        if 'ev' in kinds:
            for i in range(lo,hi):
                e=S[i]
                if e[0]!='ADD' or e[1]>=pub or e[2]>=pub: continue
                t,s=e[1],e[2]
                if focus is not None and t not in focus and s not in focus: continue
                cand=[]
                for r in (t,s):
                    L=touch[r]; k=bisect_left(L,i)
                    for j in (L[k-1] if k>0 else None, L[k+1] if k+1<len(L) else None):
                        if j is not None and fr[j]!=e[4] and fr[j] not in cand: cand.append(fr[j])
                for f in cand[:max_f]: yield dict(prim='P2',kind='ev',i=i,f=f)
        if 'start' in kinds or 'final' in kinds:
            from tkcommon import roles as _roles
            rl=_roles(w)
            for r in range(pub):
                if rl(r)!='helper': continue
                if focus is not None and r not in focus: continue
                L=touch[r]
                if not L: continue
                if 'start' in kinds:
                    for f in dict.fromkeys(fr[j] for j in L[:3]):
                        if f!=w['initial'][r]: yield dict(prim='P2',kind='start',r=r,f=f)
                if 'final' in kinds:
                    for f in dict.fromkeys(fr[j] for j in L[-3:]):
                        if f!=w['final'][r]: yield dict(prim='P2',kind='final',r=r,f=f)
    def sites_P3(self,v,ctx,window=None,focus=None,max_f=3):
        ictx=ibase.PLUGIN.prepare(v); bl=v.blocks
        for ed in ibase.PLUGIN.sites(v,ictx,regs=focus):
            i0=bl[ed['s0']][0]; i1=bl[ed['s1']][-1]
            if window and not(window[0]<=i0 and i1<window[1]): continue
            yield dict(prim='P3',a=ed['a'],b=ed['b'],q=ed['q'],i0=i0,i1=i1,ef=ed['ef'],xf=ed['xf'])
    def sites_P3x(self,v,ctx,window=None,focus=None,max_f=3):
        """P3' = inject-and-undo with the undo SOLVED in values available elsewhere in time (spansolve): the relay family (#5713 / #5605 / #5644 / ...).  Delegated to relay."""
        rctx=relay.PLUGIN.prepare(v)
        for ed in relay.PLUGIN.sites(v,rctx):
            if window and not(window[0]<=ed['i']<window[1]): continue
            yield dict(ed,prim='P3x')
    def sites_P6(self,v,ctx,window=None,focus=None,max_f=3,jmax=60,modes=('joint','single','exact'),ids=None):
        """P6 = inject + undo with the undo SOLVED (compensated relay): the contact(s) are replaced by an injection whose residual on the endpoint map is repaired by free
        PRE ADDs (frame-3 helpers) and POST ADDs (gather_post, full-frame registers) -- #5605 (joint) / #5644 (single, exact or compensated) / #5713.  Sites = relay.joint_edits +
        relay.comp_single_edits (spansolve modulo the zero-frame columns, then relaycomp.absorb); apply = relay.scalars.  `ids`: restrict to contacts (op indices)."""
        import relaycomp as RC
        tl=relay.PLUGIN.prepare(v); old=dict(relay.OPT)
        try:
            relay.OPT['jmax']=str(jmax); out=[]
            if 'joint' in modes: out+=relay.PLUGIN.joint_edits(v,tl,log=lambda *a:None)
            if ids: relay.OPT['ids']=','.join(map(str,ids))
            if 'single' in modes: out+=relay.PLUGIN.comp_single_edits(v,tl,log=lambda *a:None)
            if 'exact' in modes: out+=list(relay.PLUGIN.sites(v,tl))
        finally: relay.OPT.clear(); relay.OPT.update(old)
        for ed in out[:jmax]:
            if ids and not (set(ed.get('remove',[ed.get('i')]))&set(ids)): continue
            yield dict(ed,prim='P6')
    def sites_P4(self,v,ctx,window=None,focus=None,max_f=3):
        for ed in split2.PLUGIN.sites(v,split2.PLUGIN.prepare(v)): yield dict(ed,prim='P4')
    def sites_P5(self,v,ctx,window=None,focus=None,max_f=3):
        for ed in blockmove.PLUGIN.sites(v,blockmove.PLUGIN.prepare(v)):
            if window and not(window[0]<=ed['i0'] and ed['i1']<window[1]): continue
            yield dict(ed,prim='P5')
    # ---- apply: edit -> (S2, initial, final, lo, hi)  or a full word (P4,P5)
    def parts(self,v,ed):
        p=ed['prim']; S=v.S; w=v.w
        if p=='P1':
            S2,(lo,hi)=p1_apply(S,ed['i'],ed['g'],f=ed.get('f'),fc=ed.get('fc'),pub=v.n)
            S2=p0_merge(S2,lo,hi); ini=fin=None
            for (k,r,f) in ed.get('ends',()):
                if k=='start': ini=ini or list(w['initial']); ini[r]=f
                else: fin=fin or list(w['final']); fin[r]=f
            return S2,ini,fin
        if p=='P2':
            k=ed['kind']
            if k=='ev': return p2_event(S,ed['i'],ed['f']),None,None
            if k=='start':
                ini=list(w['initial']); ini[ed['r']]=ed['f']; return S,ini,None
            if k=='final':
                fin=list(w['final']); fin[ed['r']]=ed['f']; return S,None,fin
            raise ValueError(k)
        if p=='P3':
            return p3_apply(S,ed['i0'],ed['i1'],ed['a'],ed['b'],Q(ed['q']),ed['ef'],ed['xf'],v.n),None,None
        if p in('P3x','P6'):
            sub=dict(ed); sub.pop('prim'); sub.pop('qgain',None); return relay.PLUGIN.scalars(v,sub),None,None
        return None
    def apply(self,v,ed):
        pr=self.parts(v,ed)
        if pr is not None:
            S2,ini,fin=pr; return v.rebuild(S2,initial=ini,final=fin)
        sub=dict(ed); p=sub.pop('prim')
        if p=='P4': return split2.PLUGIN.apply(v,sub)
        if p=='P5': return blockmove.PLUGIN.apply(v,sub)
        raise ValueError(p)
    # REALISEFIX: edit-emitting path (sedit.py): the window is named by the primitive, no full candidate program, no prefix/suffix recovery.  TK_EDITS=0 -> the old list route.
    SEDIT_PRIMS=('P1','P2','P3','P8')
    def sedit(self,v,ed):
        import sedit as SE
        se=SE.prims_sedit(self,v,ed); se.meta=ed; se.view=v; return se
    def fast(self,v,ed):
        """quick kappa (trajectory-exact census) or None"""
        if EDITS and ed.get('prim') in self.SEDIT_PRIMS:
            return M.quick(v,self.sedit(v,ed))[0]
        pr=self.parts(v,ed)
        if pr is None:
            sub=dict(ed); p=sub.pop('prim')
            if p=='P5': return blockmove.PLUGIN.fast(v,sub)
            return 1.0           # P4 (split2): no trajectory-exact quick price here -> always confirmed exactly
        S2,ini,fin=pr; return M.quick(v,S2,initial=ini,final=fin)[0]
    def score(self,v,ed):
        """first-order dkappa estimate (movekit.quick_score) or None (not scorable: price exactly)"""
        if EDITS and ed.get('prim') in self.SEDIT_PRIMS:
            return M.quick_score(v,self.sedit(v,ed))
        pr=self.parts(v,ed)
        if pr is None: return None
        S2,ini,fin=pr; return M.quick_score(v,S2,initial=ini,final=fin)
    def span(self,v,ed):
        p=ed['prim']
        if p=='P1': return min(ed['i'],ed['g']),max(ed['i'],ed['g'])
        if p=='P2': return (ed['i'],ed['i']+1) if ed['kind']=='ev' else (0,len(v.S))
        if p=='P3': return ed['i0'],ed['i1']
        return ed.get('i0',0),ed.get('i1',len(v.S))
PLUGIN=Prims()

def edit_regs(v,ed):
    """registers an edit touched (the focus for the next primitive of a sequence)"""
    S=v.S; p=ed['prim']; r=set()
    if p=='P1':
        for e in S[ed['i']:ed['i']+1]: r|={e[1],e[2]}
    elif p=='P2':
        if ed['kind']=='ev': e=S[ed['i']]; r|={e[1],e[2]}
        else: r.add(ed['r'])
    elif p=='P3': r|={ed['a'],ed['b']}
    return r

# ---------------------------------------------------------------- search over primitive sequences
class Stats:
    def __init__(s): s.sites=0; s.quick=0; s.exact=0; s.legal=0; s.t0=time.time(); s.cpu0=time.process_time()
    def cpu_min(s): return (time.process_time()-s.cpu0)/60
    def line(s): return 'sites %d quick %d exact %d  wall %.1fs cpu %.2f min'%(s.sites,s.quick,s.exact,time.time()-s.t0,s.cpu_min())
_EV=[None]
def evaluator():
    if _EV[0] is None:
        import wsearch.evalincr as EV
        _EV[0]=EV.IncrEvaluator()
    return _EV[0]
SCREEN=dict(k=0,audit=False,log=[])        # first-order screening (FASTSITES): k>0 -> exact quick only for the top-k sites by estimated dkappa; audit -> price all and record the recall
def prog_to_S_window(w,window):
    """SCREENSMOKE: a window (lo,hi) in w['program'] indices -> the same span in the View's scalar program S (MOVE events removed): S index = number of non-MOVE events before the program index."""
    if not window: return window
    pre=[0]
    for e in w['program']: pre.append(pre[-1]+(e[0]!='MOVE'))
    n=len(pre)-1; lo,hi=window
    return (pre[max(0,min(lo,n))],pre[max(0,min(hi,n))])
def clamp_S_window(w,window):
    """SCREENSMOKE: clamp an S-index window to [0,len(S)] (an over-long window used to raise IndexError in sites_P1/P2)"""
    if not window: return window
    nS=sum(1 for e in w['program'] if e[0]!='MOVE'); return (max(0,min(window[0],nS)),max(0,min(window[1],nS)))
def level(w,prims=('P1',),window=None,focus=None,topq=30,sample=None,shard=(0,1),st=None,log=None,tl=1e9,minq=None,results=None,screen_k=None,screen_audit=None,wspace='S'):
    """one application level: enumerate the sites of `prims` on word w (inside `window`, touching `focus`), price all with quick() (trajectory-exact), confirm the topq exactly with IncrWord
    (legal + kappa + side + budgets).  -> list of (kappa, word, edit) sorted by exact kappa, best first.   `minq`: only edits whose quick kappa >= minq are confirmed (e.g. start - delta).
    screen_k>0: rank the sites by the first-order dkappa of the invoice-total delta (movekit.quick_score) and give only the top screen_k the exact quick price."""
    st=st or Stats(); ev=evaluator(); v=M.View(w); ctx=PLUGIN.prepare(v); priced=[]; n=0
    window=prog_to_S_window(w,window) if wspace=='program' else clamp_S_window(w,window)      # SCREENSMOKE: wspace='program' = indices of w['program']; default 'S' = View.S indices (legacy callers/tests), clamped
    sk=SCREEN['k'] if screen_k is None else screen_k; audit=SCREEN['audit'] if screen_audit is None else screen_audit; scr=[]
    if sk:
        for _ in range(M.DQ_AFTER+1): M.quick(v,v.S)
    for ed in PLUGIN.sites(v,ctx,prims=prims,window=window,focus=focus):
        n+=1; st.sites+=1
        if sample and n%sample: continue
        if n%shard[1]!=shard[0]: continue
        if sk:
            try: sc=PLUGIN.score(v,ed)
            except (Block,ValueError,KeyError,IndexError,AssertionError): sc=float('-inf')
            if sc!=float('-inf'): scr.append((sc,ed))
            continue
        try: k=PLUGIN.fast(v,ed)
        except (Block,ValueError,KeyError,IndexError,AssertionError): k=None
        st.quick+=1
        if k is not None:
            priced.append((k,ed))
            if results: results.write(json.dumps(dict(k=k,ed=ed))+'\n')
        if time.time()-st.t0>tl: break
    if sk:
        scr.sort(key=lambda x:-(x[0] if x[0] is not None else 1e9)); full=[]
        for rank,(sc,ed) in enumerate(scr):
            if rank>=sk and not audit: break
            try: k=PLUGIN.fast(v,ed)
            except (Block,ValueError,KeyError,IndexError,AssertionError): k=None
            st.quick+=1
            if k is not None:
                full.append((k,ed,rank))
                if rank<sk: priced.append((k,ed))
        if audit and full:
            ex=sorted(full,key=lambda x:-x[0])[:topq]; hit=sum(1 for x in ex if x[2]<sk); SCREEN['log'].append(dict(sites=len(scr),screened=sk,topq=topq,recall=hit/max(1,len(ex))))
            log and log('    screen: %d of the top-%d exact sites inside the first-order top-%d (recall %.2f)'%(hit,len(ex),sk,hit/max(1,len(ex))))
    priced.sort(key=lambda x:-x[0]); out=[]
    for k,ed in priced[:topq]:
        if minq is not None and k<minq: break
        try: w2=PLUGIN.apply(v,ed)
        except (Block,ValueError,KeyError,IndexError,AssertionError): continue
        o=M.evaluate(w2) if ed['prim']=='P4' else ev.evaluate(w2,base=w); st.exact+=1      # P4 adds a register: IncrWord edits keep the register count
        if o.get('legal') and o.get('ok'): out.append((o['kappa'],w2,ed)); st.legal+=1
    out.sort(key=lambda x:-x[0])
    if log: log('    level %s: %d sites, %d quick-legal, top quick %.12f, %d exact-legal  [%s]'%(','.join(prims),n,len(priced),priced[0][0] if priced else float('nan'),len(out),st.line()))
    return out
def edit_focus(w,ed):
    v=M.View(w); r=edit_regs(v,ed)
    for (k,rr,f) in ed.get('ends',()): r.add(rr)
    return r
def greedy(w,prims=('P1',),steps=10,window=None,topq=30,sample=None,st=None,log=print,tl=1e9,target=None,wspace='S'):
    """adopt the best exact improving edit, repeat (a monotone chain of primitive applications).  -> (kappa, word, chain, stats)
    wspace: 'S' (default, legacy) = window indexes the View's scalar program S (MOVEs removed; clamped); 'program' = window indexes w['program'] (MOVEs included), translated afresh every step"""
    st=st or Stats(); w=M.pin(w); k=M.evaluate(w)['kappa']; chain=[]
    for step in range(steps):
        ch=level(w,prims,window=window,topq=topq,sample=sample,st=st,log=log,tl=tl,wspace=wspace)
        if not ch or ch[0][0]<=k+1e-15: break
        k,w,ed=ch[0]; chain.append(ed); log('  step %d: %s -> %.15f  [%s]'%(step+1,json.dumps(ed),k,st.line()))
        if window: pass
        if target is not None and k>=target-1e-13: break
        if time.time()-st.t0>tl: break
    return k,w,chain,st
def beam(w,prims=('P1','P2'),depth=2,width=4,topq=30,window=None,sample=None,st=None,log=print,tl=1e9,target=None,slack=2e-6):
    """beam over sequences up to `depth`: level 1 on the whole word (window), later levels only edits touching the registers of the previous application (chain locality);
    children within `slack` of the parent's kappa are kept (plateau and dips allowed).  -> (best kappa, word, chain, stats)"""
    st=st or Stats(); w=M.pin(w); K0=M.evaluate(w)['kappa']; nodes=[(K0,w,[],None)]; best=(K0,w,[])
    for d in range(1,depth+1):
        kids=[]
        for (kp,wp,chain,foc) in nodes:
            ch=level(wp,prims,window=window if d==1 else None,focus=foc if d>1 else None,topq=topq,sample=sample if d==1 else None,st=st,log=log,tl=tl,minq=kp-slack)
            for k,w2,ed in ch: kids.append((k,w2,chain+[ed],edit_focus(wp,ed)))
        kids.sort(key=lambda x:-x[0]); nodes=kids[:width]
        if not nodes: break
        if nodes[0][0]>best[0]+1e-15: best=(nodes[0][0],nodes[0][1],nodes[0][2])
        log('depth %d: best %.15f (start %.15f, %+.3e)  [%s]'%(d,nodes[0][0],K0,nodes[0][0]-K0,st.line()))
        if target is not None and best[0]>=target-1e-13: break
        if time.time()-st.t0>tl: break
    return best[0],best[1],best[2],st

def main():
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--mode',default='greedy',choices=['greedy','beam','sweep'])
    ap.add_argument('--prims',default='P1'); ap.add_argument('--depth',type=int,default=2); ap.add_argument('--steps',type=int,default=10); ap.add_argument('--width',type=int,default=4)
    ap.add_argument('--topq',type=int,default=30); ap.add_argument('--window',nargs=2,type=int); ap.add_argument('--window-space',default='S',choices=['S','program']); ap.add_argument('--sample',type=int,default=0); ap.add_argument('--target',type=float)
    ap.add_argument('--tl',type=float,default=1e9); ap.add_argument('--out'); ap.add_argument('--results'); ap.add_argument('--slack',type=float,default=2e-6); ap.add_argument('--relay-ids',default='')
    ap.add_argument('--screen',type=int,default=0,help='first-order screening: exact-quick only the top-K sites by estimated dkappa'); ap.add_argument('--screen-audit',action='store_true'); a=ap.parse_args(); SCREEN['k']=a.screen; SCREEN['audit']=a.screen_audit
    if a.relay_ids: relay.OPT['ids']=a.relay_ids
    os.environ.setdefault('TK_FREE_BOUNDS','1')
    from tkcommon import load
    p,w=load(a.word); pr=tuple(a.prims.split(',')); win=tuple(a.window) if a.window else None; log=lambda *x:print(*x,flush=True)
    if a.mode=='greedy': k,w2,chain,st=greedy(w,pr,steps=a.steps,window=win,topq=a.topq,sample=a.sample or None,tl=a.tl,target=a.target,log=log,wspace=a.window_space)
    elif a.mode=='beam': k,w2,chain,st=beam(w,pr,depth=a.depth,width=a.width,topq=a.topq,window=win,sample=a.sample or None,tl=a.tl,target=a.target,log=log,slack=a.slack)
    else:
        st=Stats(); res=open(a.results,'a') if a.results else None; ch=level(M.pin(w),pr,window=win,topq=a.topq,sample=a.sample or None,st=st,log=log,tl=a.tl,results=res)
        k,w2,chain=(ch[0][0],ch[0][1],[ch[0][2]]) if ch else (None,None,[])
    print('RESULT kappa',k,'chain',json.dumps(chain)[:700],'|',st.line())
    if a.out and chain: json.dump(w2,gzip.open(a.out,'wt'))
if __name__=='__main__': main()
