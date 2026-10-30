"""sedit -- EDIT OBJECTS for the movekit plugin interface (REALISEFIX.

FASTSITES left one structural cost: every plugin site builds the FULL candidate scalar program S2 (list copies of ~38k events), then dq.delta / View.rebuild re-discover the window by
prefix/suffix comparison (lcp/lcs).  An SEdit names the window directly:

    SEdit(p, hi, new, ini=None, fin=None, meta=None, view=None)
        S2 == S[:p] + new + S[hi:]        (S = view.S, the non-MOVE program of the base word; positions are base positions)
        ini / fin : replacement `initial` / `final` lists or None (unchanged)

Consumers (all exact, same results as the list route):
    dq.DQBase.delta_edit(se)          trajectory-exact delta quick, no S2, no lcp/lcs
    movekit.quick(view, se) / quick_score(view, se)    accept an SEdit wherever they accepted S2 (initial/final come from the edit)
    movekit.View.rebuild_edit(se)     word with just-in-time MOVEs (incremental splice when the base is canonical)
    incr.IncrWord.try_edit(se)        converted by se.to_incr() = ordinary splice ops on the program with MOVEs (dq.splice_segments), no full word, no diff
Producers: plugin.sedit(view, edit) -> SEdit, and plugin.edits(view, ctx, **kw) -> iterator of (site_edit, SEdit).  Plugins that do not define sedit() get the generic fallback
(scalars() + prefix/suffix recovery), so the old interface keeps working untouched.

LazySeq(S, se) is the program S2 as a read-only sequence (int / slice indexing, len, iteration) without materialising it: multi-step macros (carry: P1c o P1c o P1) read the intermediate
programs through it.  SEdit.slice / replace / then compose edits (a step edit expressed against the intermediate program is folded back onto the base)."""
import collections
from fractions import Fraction as Q

class SEdit:
    __slots__=('p','hi','new','ini','fin','meta','view')
    def __init__(s,p,hi,new,ini=None,fin=None,meta=None,view=None):
        s.p=p; s.hi=hi; s.new=new; s.ini=ini; s.fin=fin; s.meta=meta; s.view=view
    @property
    def delta(s): return len(s.new)-(s.hi-s.p)
    def length(s,S): return len(S)+s.delta
    def materialise(s,S): return S[:s.p]+s.new+S[s.hi:]
    def noop(s,S): return s.ini is None and s.fin is None and s.new==S[s.p:s.hi]
    def __getitem__(s,i): raise TypeError('use LazySeq(S, se)')
    def slice(s,S,a,b):
        """S2[a:b] (0<=a<=b<=len(S2)) without building S2"""
        p=s.p; e=p+len(s.new); d=len(s.new)-(s.hi-p); out=[]
        if a<p: out+=S[a:min(b,p)]
        lo=max(a,p); hi_=min(b,e)
        if lo<hi_: out+=s.new[lo-p:hi_-p]
        if b>e: out+=S[max(a,e)-d:b-d]
        return out
    def item(s,S,i):
        p=s.p; e=p+len(s.new)
        if i<p: return S[i]
        if i<e: return s.new[i-p]
        return S[i-(len(s.new)-(s.hi-p))]
    def replace(s,S,a,b,mid,ini=None,fin=None):
        """edit of S that equals this edit followed by `S2[a:b] := mid` (a<=b in S2 coordinates)"""
        p=s.p; e=p+len(s.new); d=len(s.new)-(s.hi-p)
        P=min(p,a); E=max(e,b)
        head=s.slice(S,P,a) if P<a else []
        tail=s.slice(S,b,E) if b<E else []
        return SEdit(P,E-d,head+list(mid)+tail,ini if ini is not None else s.ini,fin if fin is not None else s.fin,s.meta,s.view)
    def then(s,S,step):
        """`step` is an SEdit defined on S2 (this edit applied to S): the composite as an edit of S"""
        return s.replace(S,step.p,step.hi,step.new,step.ini,step.fin)
    def to_incr(s,view=None):
        """IncrWord edit (ordinary splice ops on the program with MOVEs) -- needs the canonical base trajectory of the view"""
        import dq as DQM
        v=view or s.view
        if v is None: raise ValueError('SEdit.to_incr: no view')
        t=DQM.traj_of(v)
        if t is None: raise ValueError('SEdit.to_incr: base program is not the canonical rebuild of its scalar program')
        segs,ini,fin=DQM.splice_segments(v,t,s.p,s.hi,s.new,s.ini,s.fin)
        ops=[['splice',a,b,[tuple(e) for e in ev]] for a,b,ev in reversed(segs) if not (b-a==len(ev) and t.prog[a:b]==ev)]
        w=v.w
        if s.ini is not None:
            for r in range(len(s.ini)):
                if s.ini[r]!=w['initial'][r]: ops.append(['initial',r,s.ini[r]])
        if s.fin is not None:
            for r in range(len(s.fin)):
                if s.fin[r]!=w['final'][r]: ops.append(['final',r,s.fin[r]])
        return dict(ops=ops)

class LazySeq:
    """S2 = S with the window replaced, as a read-only sequence (no copy)"""
    __slots__=('S','se','n')
    def __init__(s,S,se): s.S=S; s.se=se; s.n=len(S)+se.delta
    def __len__(s): return s.n
    def __getitem__(s,i):
        if isinstance(i,slice):
            a,b,st=i.indices(s.n)
            if st!=1: return [s[k] for k in range(a,b,st)]
            return s.se.slice(s.S,a,max(a,b))
        if i<0: i+=s.n
        if i<0 or i>=s.n: raise IndexError(i)
        return s.se.item(s.S,i)
    def __iter__(s):
        for k in range(s.n): yield s.se.item(s.S,k)

def from_lists(S,S2,ini=None,fin=None,meta=None,view=None):
    """generic fallback: recover the window of S2 against S by prefix/suffix comparison"""
    import dq as DQM
    if S2 is S: return SEdit(len(S),len(S),[],ini,fin,meta,view)
    n=min(len(S),len(S2)); p=DQM._lcp(S,S2,n); q=DQM._lcs(S,S2,n-p)
    return SEdit(p,len(S)-q,S2[p:len(S2)-q],ini,fin,meta,view)

# ---------------------------------------------------------------- primitive ports (identical semantics to prims.py; no full-program copies)
def _qs(x):
    import prims
    return prims.qs(x)
def p1_edit(S,i,g,f=None,fc=None,pub=None):
    """prims.p1_apply as an edit: -> (SEdit relative to S, (lo,hi)) with (lo,hi) the touched region of S2 (same numbers as p1_apply).  S may be a LazySeq."""
    import prims
    qs=prims.qs; Block=prims.Block; _corr=prims._corr
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
        return SEdit(i,g,mid+[An]),(i,i+len(mid))
    tail=[]
    for k in range(i-1,g-1,-1):
        B=S[k]; cs=_corr(t,s,a,B,-1)
        tail=[B]+[['ADD',u,v,qs(c),fb if fc is None else fc] for (u,v,c,fb) in cs]+tail
    return SEdit(g,i+1,[An]+tail),(g,g+len(tail))
def p0_merge_edit(S,se,lo,hi,pad=24):
    """prims.p0_merge on the region [lo-pad,hi+pad] of S2 (= S with se applied), as an edit of S"""
    import ibase
    n2=len(S)+se.delta
    a=max(0,lo-pad); b=min(n2,hi+pad+1)
    mid=ibase.merge([list(e) for e in se.slice(S,a,b)])
    return se.replace(S,a,b,mid)
def p3_edit(S,i0,i1,a,b,q,ef,xf,pub):
    import prims,ibase
    mid=ibase.merge(prims.conj_window(S[i0:i1+1],a,b,q,pub))
    return SEdit(i0,i1+1,[['ADD',a,b,prims.qs(q),ef]]+mid+[['ADD',a,b,prims.qs(-q),xf]])
def p2_edit(S,i,f):
    e=list(S[i])
    if e[0] in('INIT','CLEAR'): e[2]=f
    else: e[-1]=f
    return SEdit(i,i+1,[e])

def prims_sedit(pl,v,ed):
    """Prims.sedit: P1 / P2 / P3 ported (no full-program copy); every other primitive through the generic fallback (parts + lcp/lcs).  The view may be a movekit.View or a macros.PV (S = LazySeq)."""
    import prims
    Q_=Q; p=ed['prim']; S=v.S; w=v.w
    if p=='P1':
        se,(lo,hi)=p1_edit(S,ed['i'],ed['g'],f=ed.get('f'),fc=ed.get('fc'),pub=v.n)
        se=p0_merge_edit(S,se,lo,hi); ini=fin=None
        for (k,r,f) in ed.get('ends',()):
            if k=='start': ini=ini or list(w['initial']); ini[r]=f
            else: fin=fin or list(w['final']); fin[r]=f
        se.ini=ini; se.fin=fin; return se
    if p=='P2':
        k=ed['kind']
        if k=='ev': return p2_edit(S,ed['i'],ed['f'])
        if k=='start':
            ini=list(w['initial']); ini[ed['r']]=ed['f']; return SEdit(len(S),len(S),[],ini,None)
        if k=='final':
            fin=list(w['final']); fin[ed['r']]=ed['f']; return SEdit(len(S),len(S),[],None,fin)
        raise ValueError(k)
    if p=='P3':
        return p3_edit(S,ed['i0'],ed['i1'],ed['a'],ed['b'],Q_(ed['q']),ed['ef'],ed['xf'],v.n)
    if p=='P8':
        import prims_extra as PE
        return PE.p8_sedit(v,ed)
    pr=pl.parts(v,ed)
    if pr is None: raise NotImplementedError(p)
    S2,ini,fin=pr
    return from_lists(S,S2,ini,fin)
