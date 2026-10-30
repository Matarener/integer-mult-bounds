"""dq -- DELTA QUICK (FASTSITES.  Exact incremental form of movekit.quick_full.

quick() decomposes over registers: the paid multiset is the sum over registers of the MOVEs of that register's own trajectory (its events in program order, each event naming the frame the
register must be resident in), the helper census depends only on initial/final, and kappa is a function of (helpers, paid).  A candidate scalar program S2 that differs from the base S in
the window S[p:|S|-q] / S2[p:|S2|-q] (common prefix p, common suffix q) changes only the registers occurring in that window (plus those whose initial/final changed).  For such a register r
with base events L (positions), the base trajectory has per-event transition costs TC[k] (cost key / -1 free) and a final move FC; the new trajectory keeps L[:a] and L[b:] (a,b = window
boundaries in L), so only (i) the transitions of the replaced events L[a:b] and the transition into L[b] (or the final move) are subtracted and (ii) the window events of S2 are walked
from the state left by L[a-1], plus the transition into L[b] / the final move, are added.  Cost per candidate ~ window size, not program size.  Result == quick_full exactly (same
kappa function on the same (helpers, paid)); shapes the delta does not model (frames changed, odd initial/final, base not legal, out-of-range register) fall back to quick_full."""
import collections
from bisect import bisect_left
OPS_TWO=('ADD','COPY')
BLOCK=512
def _lcp(A,B,n):
    i=0
    while i<n:
        j=min(n,i+BLOCK)
        if A[i:j]==B[i:j]: i=j; continue
        while A[i]==B[i]: i+=1
        return i
    return n
def _lcs(A,B,m):
    """longest common suffix length, at most m"""
    la,lb=len(A),len(B); k=0
    while k<m:
        j=min(m,k+BLOCK)
        if A[la-j:la-k]==B[lb-j:lb-k]: k=j; continue
        while A[la-1-k]==B[lb-1-k]: k+=1
        return k
    return m
class Illegal(Exception): pass
_MISS=object()
class DQBase:
    """per-View cache: per-register event positions, frame after each event, transition cost of each event, final-move cost"""
    def __init__(s,view,fr,dim):
        import movekit as M
        w=view.w; s.S=S=view.S; s.ini=w['initial']; s.fin=w['final']; s.own=view.own; s.NR=view.NR; s.n=len(s.ini); s.fr=fr; s.dim=dim
        s.memo={}; pos=collections.defaultdict(list)
        for i,e in enumerate(S):
            r=e[1]; pos[r].append(i)
            if e[0] in OPS_TWO and e[2]!=r: pos[e[2]].append(i)
        s.pos=pos
        s.main=set(w['live'])|{r+112 for r in w['live']}; s.ret=set(M.legal.retired_of(w))
        s.tot=collections.Counter(); s.F={}; s.TC={}; s.FC={}; s.contrib={}
        for r in range(s.NR):
            L=pos.get(r,())
            if not L and r>=s.n: continue
            owned=r in s.own; cur=s.ini[r] if r<s.n else None; F=[]; TC=[]; paid=collections.Counter()
            for j in L:
                e=S[j]; c=-1
                for f in s.targets(e,r):
                    if cur!=f:
                        k=s.cost(owned,cur,f)
                        if k is None: raise Illegal(r)
                        c=k; cur=f
                if e[0]=='INIT' and e[1]==r: cur=e[2]
                elif e[0]=='CLEAR' and e[1]==r: cur=None
                F.append(cur); TC.append(c)
                if c>=0: paid[c]+=1
            fc=-1
            if r<s.n and not owned and cur!=s.fin[r]:
                fc=s.cost(owned,cur,s.fin[r])
                if fc is None: raise Illegal(r)
                paid[fc]+=1
            s.F[r]=F; s.TC[r]=TC; s.FC[r]=fc; s.contrib[r]=paid; s.tot.update(paid)
        s.hel=s.helpers(s.ini,s.fin)
    @staticmethod
    def targets(e,r):
        """frames register r must be resident in for event e, in order (target move, then source move); INIT -> none"""
        op=e[0]; out=[]
        if e[1]==r:
            if op=='INIT': return out
            out.append(e[2] if op=='CLEAR' else e[-1])
        if op in OPS_TWO and e[2]==r: out.append(e[-1])
        return out
    def helpers(s,ini,fin):
        d=s.dim; main=s.main; ret=s.ret
        return dict(collections.Counter(d[fin[r]]-d[ini[r]] for r in range(s.n) if r not in main and r not in ret))
    def cost(s,owned,a,f):
        """-> paid key, or None (illegal; also a is None)"""
        if a is None: return None
        k=(owned,a,f); c=s.memo.get(k,-2)
        if c==-2:
            fr=s.fr
            if (fr[f]<fr[a]) if owned else (fr[a]<fr[f]): c=abs(s.dim[f]-s.dim[a])
            else: c=None
            s.memo[k]=c
        return c
    def run(s,r,evs,cur,add):
        """walk events evs of register r from state cur, calling add(key) per paid MOVE -> end state; raises Illegal"""
        owned=r in s.own; cost=s.cost
        for e in evs:
            op=e[0]
            if e[1]==r:
                if op=='INIT': cur=e[2]; continue
                f=e[2] if op=='CLEAR' else e[-1]
                if cur!=f:
                    c=cost(owned,cur,f)
                    if c is None: raise Illegal(r)
                    add(c); cur=f
                if op=='CLEAR': cur=None; continue
            if op in OPS_TWO and e[2]==r:
                f=e[-1]
                if cur!=f:
                    c=cost(owned,cur,f)
                    if c is None: raise Illegal(r)
                    add(c); cur=f
        return cur
    def delta(s,S2,ini2,fin2):
        """-> (helpers dict, paid Counter) or None (illegal); NotImplementedError when the delta does not apply"""
        S=s.S
        if S2 is S: p=len(S); q=0
        else:
            n=min(len(S),len(S2)); p=_lcp(S,S2,n); q=_lcs(S,S2,n-p)
        return s._delta_win(p,len(S)-q,S2[p:len(S2)-q],ini2,fin2)
    def delta_edit(s,se):
        """REALISEFIX: as delta() for an explicit window edit (sedit.SEdit): S2 = S[:p]+new+S[hi:]; no S2, no lcp/lcs.  Same result as delta(se.materialise(S))."""
        return s._delta_win(se.p,se.hi,se.new,se.ini if se.ini is not None else s.ini,se.fin if se.fin is not None else s.fin)
    def _delta_win(s,p,lo_end,newwin,ini2,fin2):
        S=s.S; NR=s.NR
        win=collections.defaultdict(list)
        for e in newwin:
            r=e[1]; win[r].append(e)
            if e[0] in OPS_TWO and e[2]!=r: win[e[2]].append(e)
        aff=set(win)
        for e in S[p:lo_end]:
            aff.add(e[1])
            if e[0] in OPS_TWO: aff.add(e[2])
        hel=s.hel; ends=()
        if ini2 is not s.ini or fin2 is not s.fin:
            if len(ini2)!=s.n or len(fin2)!=s.n: raise NotImplementedError
            ends=[r for r in range(s.n) if ini2[r]!=s.ini[r] or fin2[r]!=s.fin[r]]
            aff.update(ends); hel=s.helpers(ini2,fin2)
        tot=dict(s.tot); pos=s.pos; cost=s.cost; S_=S; run=s.run
        def sub(c): tot[c]=tot.get(c,0)-1
        def addk(c): tot[c]=tot.get(c,0)+1
        try:
            for r in aff:
                if r>=NR or r<0: raise NotImplementedError
                L=pos.get(r,()); a=bisect_left(L,p); b=bisect_left(L,lo_end); owned=r in s.own
                if r in ends or r not in s.F:
                    # endpoints changed (or no base record): re-walk this register entirely, subtract its whole base contribution
                    if r in s.F:
                        for c,m in s.contrib[r].items(): tot[c]=tot.get(c,0)-m
                    cur=ini2[r] if r<s.n else None
                    def evs(L=L,a=a,b=b,r=r):
                        for j in L[:a]: yield S_[j]
                        yield from win.get(r,())
                        for j in L[b:]: yield S_[j]
                    cur=run(r,evs(),cur,addk)
                    if r<s.n and not owned and cur!=fin2[r]:
                        c=cost(owned,cur,fin2[r])
                        if c is None: raise Illegal(r)
                        addk(c)
                    continue
                TC=s.TC[r]; F=s.F[r]
                for k in range(a,b):
                    c=TC[k]
                    if c>=0: sub(c)
                cur=F[a-1] if a>0 else (s.ini[r] if r<s.n else None)
                cur=run(r,win.get(r,()),cur,addk)
                if b<len(L):
                    c=TC[b]
                    if c>=0: sub(c)
                    e=S_[L[b]]
                    for f in s.targets(e,r):
                        if cur!=f:
                            c=cost(owned,cur,f)
                            if c is None: raise Illegal(r)
                            addk(c); cur=f
                    # (state after e is the base's F[b]: the suffix transitions are unchanged)
                else:
                    c=s.FC[r]
                    if c>=0: sub(c)
                    if r<s.n and not owned and cur!=s.fin[r]:
                        c=cost(owned,cur,s.fin[r])
                        if c is None: raise Illegal(r)
                        addk(c)
        except Illegal: return None
        return hel,collections.Counter({k:v for k,v in tot.items() if v})

    def first_order(s,hel,paid):
        """dkappa ~ CALLS*( sum_r dhel_r w_r - sum_r dpaid_r w_r ) / (sum_T n r^e ln r - sum_P n r^e ln r),  w_r=r^(1-k0): the root moves with the invoice totals (T up / P down raises kappa)"""
        fo=getattr(s,'_fo',None)
        if fo is None:
            import math, movekit as M
            X=M.X; k0=M._kappa(s.hel,s.tot); e=1-k0
            T,P=X.invoice(dict(helpers=s.hel,paid=s.tot)); den=0.0
            for r,n in T.items(): den+=n*r**e*math.log(r) if r>0 else 0.0
            for r,n in P.items(): den-=n*r**e*math.log(r) if r>0 else 0.0
            fo=s._fo=(e,den,X.CALLS)
        e,den,calls=fo; x=0.0
        for k in set(hel)|set(s.hel):
            if k>0: x+=(hel.get(k,0)-s.hel.get(k,0))*k**e
        for k in set(paid)|set(s.tot):
            if k>0: x-=(paid.get(k,0)-s.tot.get(k,0))*k**e
        return calls*x/den

# ---------------------------------------------------------------------------------------------- incremental rebuild (FASTSITES item 2)
class Traj:
    """JIT-rebuild bookkeeping of the BASE word of a View: per-register event positions pos[r], frame after each event F[r] (CLEAR -> None), position of every scalar event in the base
    program sp[k] and group start gs[k] (the MOVEs just before scalar event k are prog[gs[k]:sp[k]]; gs[len(S)] starts the final MOVEs).  canon = the base program IS rebuild(S) (checked once)."""
    def __init__(s,view):
        w=view.w; s.S=S=view.S; s.ini=w['initial']; s.fin=w['final']; s.own=view.own; s.n=len(s.ini); s.NR=view.NR; prog=w['program']; s.prog=prog
        pos=collections.defaultdict(list); F=collections.defaultdict(list)
        for k,e in enumerate(S):
            r=e[1]; op=e[0]
            if op=='INIT': f=e[2]
            elif op=='CLEAR': f=None
            else: f=e[-1]
            pos[r].append(k); F[r].append(f)
            if op in OPS_TWO and e[2]!=r: pos[e[2]].append(k); F[e[2]].append(e[-1])
        s.pos=pos; s.F=F
        sp=[]; 
        for i,e in enumerate(prog):
            if e[0]!='MOVE': sp.append(i)
        s.sp=sp; s.gs=[0]+[i+1 for i in sp]
        s.canon=(len(sp)==len(S)) and view.rebuild_ref(S)['program']==prog
    def before(s,r,k):
        """JIT state (frame or None) of register r just before scalar event k of the base program"""
        L=s.pos.get(r)
        if L:
            a=bisect_left(L,k)
            if a>0: return s.F[r][a-1]
        return s.ini[r] if r<s.n else None
def traj_of(view):
    """the base Traj of a View when its program is the canonical JIT rebuild of its scalar program (else None); built on demand and cached on the view (REALISEFIX)"""
    tj=view.__dict__.get('_tj')
    if tj is False: return None
    if tj is None or type(tj) is int:
        tj=Traj(view)
        if not tj.canon: view._tj=False; return None
        view._tj=tj
    return tj
def splice_segments(view,t,lo,hi,new,ini=None,fin=None):
    """the JIT rebuild of S[:lo]+new+S[hi:] as SEGMENTS of the base program: [(a,b,events)] ascending, non-overlapping, prog[a:b] is replaced by `events` (the window with its MOVEs, the group of
    the first suffix event of every register whose state differs after the window, the final MOVEs).  Only for unchanged initial/final (ini/fin None) -- raises NotImplementedError otherwise.
    rebuild_splice is exactly the assembly of these segments."""
    if ini is not None or fin is not None: raise NotImplementedError('initial/final changed')
    S=view.S; prog=t.prog; sp=t.sp; gs=t.gs; own=view.own; before=t.before
    win=[]; MISS=_MISS; regs=set()
    for e in new:
        regs.add(e[1])
        if e[0] in OPS_TWO: regs.add(e[2])
    cur={r:before(r,lo) for r in regs}
    app=win.append
    for e in new:          # (the hot loop of View.rebuild_ref over the window only; every register is pre-seeded)
        op=e[0]; r=e[1]
        if op=='INIT': cur[r]=e[2]
        elif op=='CLEAR':
            a=cur[r]; f=e[2]
            if a!=f:
                if a is None: raise ValueError('dead register %d'%r)
                app(['MOVE',r,a,f,r in own])
            cur[r]=None
        else:
            f=e[-1]; a=cur[r]
            if a!=f:
                if a is None: raise ValueError('dead register %d'%r)
                app(['MOVE',r,a,f,r in own]); cur[r]=f
            if op=='ADD' or op=='COPY':
                tt=e[2]; a=cur[tt]
                if a!=f:
                    if a is None: raise ValueError('dead register %d'%tt)
                    app(['MOVE',tt,a,f,tt in own]); cur[tt]=f
        app(e if type(e) is list else list(e))
    segs=[(gs[lo],gs[hi],win)]
    touched=set(cur)
    for e in S[lo:hi]:
        touched.add(e[1])
        if e[0] in OPS_TWO: touched.add(e[2])
    diff={}
    for r in touched:
        v=cur[r] if r in cur else before(r,lo)
        if v!=before(r,hi): diff[r]=v
    # suffix: the group of the first suffix event of each differing register is regenerated
    E=set(); pos=t.pos
    for r in diff:
        L=pos.get(r)
        if L:
            a=bisect_left(L,hi)
            if a<len(L): E.add(L[a])
    nS=len(S)
    for k in sorted(E):
        e=S[k]; op=e[0]; r=e[1]; loc={}; grp=[]
        def st(x):
            v=loc.get(x,MISS)
            if v is MISS:
                v=diff.pop(x) if x in diff else before(x,k)
                loc[x]=v
            return v
        def mv(x,f):
            a=st(x)
            if a!=f:
                if a is None: raise ValueError('dead register %d'%x)
                grp.append(['MOVE',x,a,f,x in own]); loc[x]=f
        if op=='INIT':
            diff.pop(r,None)
        elif op=='CLEAR': mv(r,e[2])
        else:
            f=e[-1]; mv(r,f)
            if op=='ADD' or op=='COPY': mv(e[2],f)
        if op=='ADD' or op=='COPY': diff.pop(e[2],None)
        diff.pop(r,None)
        segs.append((gs[k],sp[k],grp))
    # final MOVEs: public registers go to `final`
    ini0=t.ini; fin0=t.fin; fm=[]
    for r in range(t.n):
        if r in own: continue
        if r in diff: a=diff[r]
        else:
            L=pos.get(r); a=t.F[r][-1] if L else ini0[r]
        if a!=fin0[r]:
            if a is None: raise ValueError('dead register %d'%r)
            fm.append(['MOVE',r,a,fin0[r],False])
    segs.append((gs[nS],len(prog),fm))
    return segs,None,None
def rebuild_splice(view,t,lo,hi,new):
    """program of rebuild(S[:lo]+new+S[hi:]) built incrementally from the base program: prefix and untouched groups are copied, the window is re-derived, and only the groups of the
    first suffix event of each register whose state differs after the window (plus the final MOVEs) are regenerated.  -> program list (identical to the full rebuild)"""
    segs,_,_=splice_segments(view,t,lo,hi,new)
    prog=t.prog; out=[]; pos=0
    for a,b,ev in segs:
        if a>pos: out.extend(prog[pos:a])
        out.extend(ev); pos=b
    out.extend(prog[pos:])
    return out
