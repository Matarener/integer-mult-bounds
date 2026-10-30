"""handover -- P13: LATE-CUT HAND-OVER WITH SOLVED COMPENSATION (LATECUT.  Generalises split2 (PR5718) and reproduces the mechanism of #5786 (asynchronous helper hubs).

Move.  A public register p that is PRISTINE at a cut (row e_p; it was only read so far) and whose next event sits on chart F retires there: a NEW public register f (initial chart F, final chart G = old final of p) takes over EVERY
later occurrence of p; p keeps its row e_p and ends on F.  The cut may be anywhere (before the first run on F as in #5786, or after an F-run as in split2).  A gadget makes f a CLONE of p
(f = e_p) and parks the new input e_f in an owned scratch o:   INIT o; COPY o<-f; f -= o; f += p; o -= p   =>  f = e_p, p = e_p, o = K0 := e_f - e_p     (5 events; #5786 spends 10 with Weyl transvections).

Exact algebra (everything is linear; rows are over initial inputs).  The clone word V computes every OLD final row, except that f ends as e_p instead of e_f.  The missing -K0 on f (and any junk) is repaired by three event families,
all with sources of FIXED known rows:
    pre(T,a)   T += a p     at the start, chart Z           (T initial on Z; p is e_p there)             effect  a * Cfull(T) (x) e_p
    end(T,b)   T += b f     at the very end, chart G        (T final on G; f_end = e_f when repaired)     effect  b * e_T       (x) e_f
    win(T,c,t) T += c o     inside o's lifetime, after event t, T on chart F (or nested-detour via F)      effect  c * C(T,t)    (x) K0
with Cfull(T)/C(T,t) the exact suffix-map columns (unit in T at that time -> every final register; backward sweep).  Since e_p, e_f are independent the repair is exactly
        sum_T a_T Cfull(T)  =  -beta                       (beta = end coefficients, supported on registers whose final chart is G)
        sum_j c_j C(T_j,t_j) =  e_f - beta                 (e_f = the unit vector of the NEW register: the injection `f += o` is one of the win options)
over all public registers.  `solve` finds a sparse exact solution (LP over the candidate columns, dyadic rounding, exact Fraction check); split2 is the special case with no win options and d = push(e_p).
Compensation is therefore a SOLVED sub-step: pre/end pairs absorb the junk that reaches legal leaves, `o` events inside the window absorb the rest (the 53 illegal Y mains of #5774/623), nothing is #5786-specific.
python:  import handover as H; ed=H.sites(v) ...; w2=H.apply_edit(w,ed)       tk:  tk handover WORD [--apply]
"""
import collections,time,json,os
from fractions import Fraction as Q
import numpy as np
import movekit as M
from movekit import qs

class Block(Exception): pass

def zero_frame(w):
    z=[i for i,f in enumerate(w['frames']) if len(f)==0]; return z[0] if z else None

_FQC={}
def _fq(s):
    x=_FQC.get(s)
    if x is None: x=_FQC[s]=float(Q(s))
    return x

def shifted(S,n):
    """owned ids >= n move up by one (a new public register takes id n)"""
    out=[]
    for e in S:
        e=list(e)
        if e[0] in('ADD','COPY'):
            if e[1]>=n: e[1]+=1
            if e[2]>=n: e[2]+=1
        else:
            if e[1]>=n: e[1]+=1
        out.append(e)
    return out

def gadget(o,f,p,F):
    return [['INIT',o,F],['COPY',o,f,'1',F],['ADD',f,o,'-1',F],['ADD',f,p,'1',F],['ADD',o,p,'-1',F]]

def rename_from(S,i0,p,f):
    out=[list(e) for e in S]
    for i in range(i0,len(out)):
        e=out[i]
        if e[0] in('ADD','COPY'):
            if e[1]==p: e[1]=f
            if e[2]==p: e[2]=f
        elif e[1]==p: e[1]=f
    return out

def rows_prefix(S,NR,own,stop):
    rows=np.eye(NR)
    for r in own: rows[r]=0
    for i,e in enumerate(S):
        if i>=stop: break
        op,r=e[0],e[1]
        if op=='ADD': rows[r]+=_fq(e[3])*rows[e[2]]
        elif op=='SCALE': rows[r]*=_fq(e[2])
        elif op=='COPY': rows[r]=_fq(e[3])*rows[e[2]]
        else: rows[r]=0
    return rows

def suffix_columns(B,NR,want):
    """want: {t: [T,...]} (columns of the suffix map B[t+1:], i.e. insertion AFTER event t; t=-1 = full map) -> {(T,t): vector over registers}.  Backward sweep M := M E_i, O(len*NR)."""
    M_=np.eye(NR); out={}
    for i in range(len(B)-1,-2,-1):
        if i in want:
            for T in want[i]: out[(T,i)]=M_[:,T].copy()
        if i<0: break
        e=B[i]; op,r=e[0],e[1]
        if op=='ADD': M_[:,e[2]]+=_fq(e[3])*M_[:,r]
        elif op=='SCALE': M_[:,r]*=_fq(e[2])
        elif op=='COPY': M_[:,e[2]]+=_fq(e[3])*M_[:,r]; M_[:,r]=0
        else: M_[:,r]=0
    return out

def chart_tracks(B,initial,NR,final):
    """per register the list of (event index, chart after the event) + initial chart"""
    tr=collections.defaultdict(list)
    for i,e in enumerate(B):
        op=e[0]
        if op in('ADD','COPY'): tr[e[1]].append((i,e[-1])); tr[e[2]].append((i,e[-1]))
        elif op in('INIT','CLEAR'): tr[e[1]].append((i,e[2]))
        else: tr[e[1]].append((i,e[-1]))
    return tr

def rows_all(S,NR,own):
    """float64 matrix: register r after S as a linear function of the initial values (owned start empty)"""
    rows=np.eye(NR)
    for r in own: rows[r]=0
    for e in S:
        op,r=e[0],e[1]
        if op=='ADD': rows[r]+=_fq(e[3])*rows[e[2]]
        elif op=='SCALE': rows[r]*=_fq(e[2])
        elif op=='COPY': rows[r]=_fq(e[3])*rows[e[2]]
        else: rows[r]=0
    return rows

def _nextchart(S,c,q,w,n):
    for e in S[c:]:
        if e[0] in('ADD','COPY') and q in e[1:3]: return e[-1]
        if e[0]=='SCALE' and e[1]==q: return e[-1]
    return w['final'][q] if q<n else None

def _undo_replay(S,c,p,h,rows,n,w,Z,F,sp,chart):
    """undo p's pre-cut writes whose (non-Z) sources are unchanged since: p -= a r @F"""
    undo=[]; lastt={}
    for i,e2 in enumerate(S[:c]):
        if e2[0] in('ADD','COPY'): lastt[e2[1]]=i
        elif e2[0]=='SCALE': lastt[e2[1]]=i
    for i,e2 in enumerate(S[:c]):
        if e2[0]=='ADD' and e2[1]==p and e2[2]!=p and (e2[2]>=n or w['initial'][e2[2]]!=Z):
            r=e2[2]
            if lastt.get(r,-1)>i: raise Block('undo source changed after the write')
            if not(r<n and sp[chart(r)]<=sp[F] and sp[F]<=sp[_nextchart(S,c,r,w,n)]): raise Block('undo source cannot reach F')
            undo.append(['ADD',p,r,qs(-Q(e2[3])),F]); h=h-_fq(e2[3])*rows[r]
    return undo,h
def _undo_lp(S,c,p,h,rows,n,w,Z,F,sp,chart):
    """sparse exact combination of the registers currently on a chart <= F whose rows cancel the non-Z part of h (p -= sum a_q q @F)"""
    import scipy.sparse as sp_
    from scipy.optimize import linprog
    NRr=rows.shape[0]
    nzc=[r for r in range(NRr) if r!=p and (r>=n or w['initial'][r]!=Z)]
    cands=[q for q in range(n) if q!=p and sp[chart(q)]<=sp[F] and np.any(rows[q][nzc]!=0) and sp[F]<=sp[_nextchart(S,c,q,w,n)]]
    if not cands: raise Block('no undo sources')
    A=sp_.csr_matrix(rows[np.ix_(cands,nzc)].T)
    b=-h[nzc]
    A2=sp_.hstack([A,-A]).tocsr()
    res=linprog(np.ones(2*len(cands)),A_eq=A2,b_eq=b,bounds=(0,None),method='highs')
    if res.status!=0: raise Block('undo LP infeasible')
    x=res.x[:len(cands)]-res.x[len(cands):]
    undo=[]
    for q,xv in zip(cands,x):
        if abs(xv)>1e-9:
            d=_dy(xv); undo.append(['ADD',p,q,qs(d),F]); h=h+float(d)*rows[q]
    return undo,h

def build(v,p,c,F=None):
    """clone word V (before compensation).  -> dict(B, ...)  B = pre_k + S[:c] + gadget + S[c:] with p -> f; ids: f=n, owned shifted +1, scratch o = NR+1 (placeholder)
    p's row at the cut is h = e_p + k.  The part of k supported on Z-initial registers is cancelled at t=0 (pre_k: `p -= k_r r @Z`, split2's closed-form correction); the part written by registers that
    are NOT Z-initial (e.g. #5786's hub 696 accumulates packets 698/700/702 that start on 1031) is UNDONE at the cut on chart F (`p -= a r @F`, re-reading the same sources), after f has cloned the current value.
    gadget:  INIT o; COPY o<-f; f -= o; f += p; [undo events]; o -= p        => f = h, p = e_p, o = e_f - e_p"""
    w=v.w; S=v.S; n=v.n; NR=v.NR; Z=zero_frame(w)
    if Z is None or p>=n or w['initial'][p]!=Z: raise Block('p must be public, initial on Z')
    if F is None:
        e=S[c]
        if p not in(e[1:3] if e[0] in('ADD','COPY') else (e[1],)): raise Block('event c must touch p')
        F=e[-1] if e[0] not in('INIT','CLEAR') else e[2]
    if F==Z: raise Block('F==Z')
    rows=rows_prefix(S,NR,v.own,c)
    h=rows[p].copy(); h[p]-=1                      # k = h - e_p
    sp=v.spans
    # chart of every register at the cut
    cur={}
    for i,e2 in enumerate(S[:c]):
        if e2[0] in('ADD','COPY'): cur[e2[1]]=e2[-1]; cur[e2[2]]=e2[-1]
        elif e2[0]=='SCALE': cur[e2[1]]=e2[-1]
    def chart(r): return cur.get(r,w['initial'][r] if r<n else None)
    if not(sp[chart(p)]<=sp[F]): raise Block('p above F')
    undo=[]
    nonZ=[r for r in range(len(h)) if h[r]!=0 and r!=p and (r>=n or w['initial'][r]!=Z)]
    if nonZ:
        try:
            undo,h=_undo_replay(S,c,p,h,rows,n,w,Z,F,sp,chart)
        except Block:
            undo,h=_undo_lp(S,c,p,h,rows,n,w,Z,F,sp,chart)
    kk={int(r):float(h[r]) for r in np.nonzero(h)[0]}
    for r in kk:
        if r>=n or r==p or w['initial'][r]!=Z: raise Block('p not pristine: k not supported on Z-initial registers')
    Gp=w['final'][p]; f=n
    S1=shifted(S,n); o=NR+1
    pre_k=[['ADD',p,r,qs(-Q(kv)),Z] for r,kv in sorted(kk.items())]
    gad=[['INIT',o,F],['COPY',o,f,'1',F],['ADD',f,o,'-1',F],['ADD',f,p,'1',F]]+undo+[['ADD',o,p,'-1',F]]
    B=pre_k+S1[:c]+gad+rename_from(S1,c,p,f)[c:]
    return dict(B=B,np_=len(pre_k),c=c+len(pre_k),F=F,Z=Z,Gp=Gp,f=f,p=p,o=o,k=kk,ng=len(gad))

def plan(v,p,c,W=3000,detour=True,log=None,diag=False,F=None):
    """-> dict with the clone word, the compensation solved from the exact error matrix (or raises Block)"""
    import scipy.sparse as sp_, bisect
    from scipy.optimize import linprog
    b=build(v,p,c,F); w=v.w; n=v.n; NR=v.NR; f=b['f']; F=b['F']; Z=b['Z']; Gp=b['Gp']; o=b['o']; B=b['B']
    NRp=NR+2; pub=list(range(n+1)); g=b['c']+b['ng']
    initial=list(w['initial'])+[F]; final=list(w['final'])+[Gp]; final[p]=F
    spans=v.spans; own=set(range(n+1,NRp))
    # exact error matrix of the clone word (public x public)
    R=rows_all(B,NRp,own)[:n+1,:n+1]
    R0=getattr(v,'_ho_R0',None)
    if R0 is None: R0=v._ho_R0=rows_all(v.S,NR,v.own)[:n,:n]
    tgt=np.zeros((n+1,n+1)); tgt[:n,:n]=R0; tgt[f,f]=1
    Err=R-tgt
    rowo=rows_all(B[:g],NRp,own)[o,:n+1]                       # o's row once the gadget has run (constant while o lives)
    touch=collections.defaultdict(list)
    for i,e in enumerate(B):
        if e[0] in('ADD','COPY'): touch[e[1]].append(i); touch[e[2]].append(i)
        else: touch[e[1]].append(i)
    def chart_of_event(e): return e[2] if e[0] in('INIT','CLEAR') else e[-1]
    cand=[]; hi=min(len(B)-1,g+W)
    # alive foreign owned sources (scratch of earlier hand-overs / P8 bridges): intervals [INIT, CLEAR) in B
    op_={}; alive=[]
    for i,e in enumerate(B):
        if e[0]=='INIT': op_[e[1]]=i
        elif e[0]=='CLEAR' and e[1] in op_:
            i0=op_.pop(e[1])
            if e[1]!=o and i>g-1 and i0<hi: alive.append((e[1],i0,i))
    def chart_at(r,t):
        L=touch[r]; k=bisect.bisect_right(L,t)
        return chart_of_event(B[L[k-1]]) if k>0 else initial[r] if r<len(initial) else None
    def tgt_gaps(T):
        L=touch[T]; k=bisect.bisect_right(L,g-1)
        prev=L[k-1] if k>0 else None
        X=chart_of_event(B[prev]) if prev is not None else initial[T]
        t=g-1; out=[]
        while True:
            nxt=L[k] if k<len(L) else None
            Y=chart_of_event(B[nxt]) if nxt is not None else final[T]
            if X==F or Y==F: cost=1
            elif detour and spans[X]<spans[F]<spans[Y]: cost=3
            else: cost=None
            if cost is not None and B[t][0]!='CLEAR': out.append((t,cost))
            if nxt is None or nxt>hi: break
            t=nxt; X=chart_of_event(B[nxt]); k+=1
        return out
    gaps={T:tgt_gaps(T) for T in pub}
    # owned scratch registers alive in the window as TARGETS (they descend: current chart >= F >= next chart); their content reaches the public rows through later events (#5786: 773 -> 709, 733)
    intervals_=[]; op2={}
    for i,e in enumerate(B):
        if e[0]=='INIT': op2[e[1]]=i
        elif e[0]=='CLEAR' and e[1] in op2:
            i0=op2.pop(e[1]); i1=i
            if e[1]!=o and i1>g-1 and i0<hi: intervals_.append((e[1],i0,i1))
    for (q,i0,i1) in intervals_:
        L=touch[q]
        for a_,b_ in zip(L,L[1:]):
            if b_>hi or a_<g-1 and b_<g-1: continue
            t=max(a_,g-1)
            if t<i0 or t>=i1: continue
            X=chart_of_event(B[a_]); Y=chart_of_event(B[b_])
            if t==g-1 and a_<g-1: pass
            if X==F or Y==F or (spans[F]<spans[X] and spans[Y]<=spans[F]): cand.append((q,t,2,'o'))
    for T in pub:
        if T==p: continue
        for t,cost in gaps[T]: cand.append((T,t,cost,'o'))
    # public sources sitting on F with a sparse known row (the frozen hubs themselves, earlier hand-overs' registers): window options only, no detours
    srcrows={}
    W2=int(os.environ.get('LATECUT_W2','400')) if True else 400
    TT=[g-1]+[i for i in range(g,min(len(B),g+W2)) if B[i][0]!='INIT' and B[i][0]!='CLEAR' and B[i][-1]==F]
    TTs=set(TT); lastT=max(TT)
    rr=np.eye(NRp)
    for r_ in own: rr[r_]=0
    ch=list(initial)+[None]*(NRp-len(initial))
    for i,e in enumerate(B[:lastT+1]):
        op,r_=e[0],e[1]
        if op=='ADD': rr[r_]+=_fq(e[3])*rr[e[2]]; ch[r_]=e[-1]; ch[e[2]]=e[-1]
        elif op=='SCALE': rr[r_]*=_fq(e[2]); ch[r_]=e[-1]
        elif op=='COPY': rr[r_]=_fq(e[3])*rr[e[2]]; ch[r_]=e[-1]; ch[e[2]]=e[-1]
        elif op=='INIT': rr[r_]=0; ch[r_]=e[2]
        else: rr[r_]=0; ch[r_]=None
        if i in TTs:
            for q in range(NRp):
                if ch[q]!=F or q==f and False: continue
                rv=rr[q,:n+1]; nzq=np.count_nonzero(rv)
                if nzq==0 or nzq>4: continue
                if q==o or q>n and q not in [a_[0] for a_ in alive]: continue
                srcrows[(q,i)]=rv.copy()
    for (q,t),rv in srcrows.items():
        if q==o: continue
        for T in pub:
            if T==q: continue
            L=touch[T]; k=bisect.bisect_right(L,t)
            X=chart_of_event(B[L[k-1]]) if k>0 else initial[T]
            Y=chart_of_event(B[L[k]]) if k<len(L) else final[T]
            if (X==F or Y==F) and B[t][0]!='CLEAR': cand.append((T,t,2,q))
    cand=list({(T,t,c_,sr):1 for (T,t,c_,sr) in cand}.keys())
    def rowof(sr,t): return rowo if sr=='o' else srcrows[(sr,t)]
    src=[p]+sorted(b['k'])                                      # pre sources (rows e_s at t=0)
    pre=[T for T in pub if T not in src and T!=f and initial[T]==Z]
    want=collections.defaultdict(list)
    for T in pre: want[-1].append(T)
    for T,t,cost,sr in cand: want[t].append(T)
    cols=suffix_columns(B,NRp,want)
    E=[r for r in pub if r!=p and r!=f and final[r]==Gp]
    Q_=set(np.nonzero(np.abs(Err).sum(axis=0))[0].tolist())|set(src)|{f}|set(np.nonzero(rowo)[0].tolist())
    for (q_,t_),rv in srcrows.items(): Q_|=set(np.nonzero(rv)[0].tolist())
    Q_=sorted(Q_)
    qi={q:i for i,q in enumerate(Q_)}
    nv_a=len(pre)*len(src); nv_c=len(cand); nv_b=len(E); nv=nv_a+nv_c+nv_b
    Ar=[];Ac=[];Av=[]; npub=n+1
    for j,T in enumerate(pre):
        col=cols[(T,-1)][:npub]; nz=np.nonzero(col)[0]
        for si,s in enumerate(src):
            jj=j*len(src)+si; qq=qi[s]
            for r in nz: Ar.append(qq*npub+int(r)); Ac.append(jj); Av.append(col[r])
    for j,(T,t,cost,sr) in enumerate(cand):
        col=cols[(T,t)][:npub]; nz=np.nonzero(col)[0]; rv=rowof(sr,t)
        for q in np.nonzero(rv)[0]:
            qq=qi[int(q)]
            for r in nz: Ar.append(qq*npub+int(r)); Ac.append(nv_a+j); Av.append(col[r]*rv[q])
    for j,r in enumerate(E):
        Ar.append(qi[f]*npub+r); Ac.append(nv_a+nv_c+j); Av.append(1.0)
    A=sp_.csr_matrix((Av,(Ar,Ac)),shape=(len(Q_)*npub,nv))
    rhs=np.concatenate([-Err[:,q] for q in Q_])
    A2=sp_.hstack([A,-A]).tocsr()
    cost_=np.array([1.0]*nv_a+[cc for (_,_,cc,_) in cand]+[1.0]*nv_b)
    if diag:       # slack LP: what cannot be repaired at all
        nr=A.shape[0]; I=sp_.identity(nr,format='csr')
        A3=sp_.hstack([A2,I,-I]).tocsr(); c3=np.concatenate([cost_,cost_,np.full(2*nr,100.0)])
        r3=linprog(c3,A_eq=A3,b_eq=rhs,bounds=(0,None),method='highs')
        sl=r3.x[2*nv:2*nv+nr]-r3.x[2*nv+nr:]
        bad=[(Q_[i//npub],i%npub,float(sl[i])) for i in np.nonzero(np.abs(sl)>1e-9)[0]]
        return dict(resid=bad,Err=Err,Q=Q_,E=E,nz_err=[(q,[int(r) for r in np.nonzero(Err[:,q])[0]][:10]) for q in Q_[:6]])
    res=linprog(np.concatenate([cost_,cost_]),A_eq=A2,b_eq=rhs,bounds=(0,None),method='highs')
    if res.status!=0:
        raise Block('no compensation (LP %s); err coords %s'%(res.message[:50],Q_[:8]))
    x=res.x[:nv]-res.x[nv:]
    sol=dict(pre=[(pre[j//len(src)],src[j%len(src)],x[j]) for j in range(nv_a) if abs(x[j])>1e-9],
             win=[(cand[j][0],cand[j][1],x[nv_a+j],cand[j][3]) for j in range(nv_c) if abs(x[nv_a+j])>1e-9],
             end=[(E[j],x[nv_a+nv_c+j]) for j in range(nv_b) if abs(x[nv_a+nv_c+j])>1e-9])
    return dict(b=b,B=B,g=g,o=o,initial=initial,final=final,sol=sol,ncand=(nv_a,nv_c,nv_b),obj=res.fun,Err=Err)

# ------------------------------------------------------------------ emit / apply
def _dy(x,den=64):
    q=Q(float(x)).limit_denominator(den)
    if abs(float(q)-float(x))>1e-9: raise Block('non-dyadic coefficient %r'%x)
    if q.denominator&(q.denominator-1): raise Block('non-dyadic coefficient %r'%x)
    return q

def free_owned_id(Sx,n1,NRp,lo,hi,o_placeholder):
    """smallest owned id (>= n1) with no lifetime overlapping [lo,hi] in the program Sx (which may use o_placeholder for the scratch)"""
    iv=collections.defaultdict(list); op={}
    for i,e in enumerate(Sx):
        if e[0]=='INIT': op[e[1]]=i
        elif e[0]=='CLEAR' and e[1] in op: iv[e[1]].append((op.pop(e[1]),i))
    for o in range(n1,o_placeholder):
        if all(b<lo or a>hi for (a,b) in iv.get(o,())): return o
    return o_placeholder

def emit(v,pl,reuse=True):
    """-> (S2, initial, final) for the planned hand-over"""
    B=[list(e) for e in pl['B']]; b=pl['b']; p=b['p']; f=b['f']; F=b['F']; Z=b['Z']; Gp=b['Gp']; c=b['c']; o=pl['o']; g=pl['g']; n=v.n
    sol=pl['sol']
    pre=[['ADD',T,s,qs(_dy(a)),Z] for T,s,a in sol['pre']]+B[:b['np_']]
    end=[['ADD',T,f,qs(_dy(bb)),Gp] for T,bb in sol['end']]
    ins=collections.defaultdict(list)
    for T,t,cc,sr in sol['win']: ins[t].append(['ADD',T,o if sr=='o' else sr,qs(_dy(cc)),F])
    last=max([t for T,t,cc,sr in sol['win'] if sr=='o']+[g-1])
    out=[]
    for i,e in enumerate(B):
        if i<b['np_']: continue
        out.append(e)
        if i in ins: out.extend(ins[i])
        if i==last: out.append(['CLEAR',o,F])
    S2=pre+out+end
    lo=len(pre)+c-b['np_']; hi=len(pre)+(last-b['np_'])+sum(len(x) for k,x in ins.items() if k<=last)+1
    if reuse:
        o2=free_owned_id(S2,n+1,pl['o']+1,lo,hi,pl['o'])
        if o2!=o:
            S2=[[ (o2 if (j in(1,2) and x==o and (e[0] in('ADD','COPY') or j==1)) else x) for j,x in enumerate(e)] for e in S2]
    return S2,pl['initial'],pl['final']

def verify_rows(v,S2,n1,tv=None):
    """exact (Fraction) value check: public rows of S2 == public rows of the target word (default v), every new register identity"""
    import prims_extra as PE
    tv=tv or v
    base=PE.sim_rows(tv.S,tv.n); got=PE.sim_rows(S2,n1)
    bad=[r for r in range(tv.n) if got[r]!=base[r]]
    for r in range(tv.n,n1):
        if got[r]!={r:Q(1)}: bad.append(r)
    return bad

def rebuild_shifted(v,S2,initial,final):
    from tkcommon import legal
    mx=max([e[1] for e in S2 if e[0]=='INIT']+[len(initial)-1])
    nown=max(legal.nown(v.w),mx+1-len(initial))
    w=dict(v.w); w['initial']=initial; w['final']=final; w['public']=len(initial); w['owned_fields']=nown
    w['verifier_profile']=dict(legal.profile_params(v.w),public=len(initial),owned_fields=nown)
    v2=M.View(w); return v2.rebuild(S2)


# ------------------------------------------------------------------ JOINT (multi-hub) hand-over: several new hubs, optionally re-solving the compensation of hand-overs that are already in the word
def hub_info(v,p,c,F=None):
    """pre-cut analysis of one hub on the ORIGINAL scalar program: -> dict(p,c,F,Gp,undo,k)"""
    w=v.w; S=v.S; n=v.n; NR=v.NR; Z=zero_frame(w)
    if Z is None or p>=n or w['initial'][p]!=Z: raise Block('p must be public, initial on Z')
    if F is None:
        e=S[c]
        if p not in(e[1:3] if e[0] in('ADD','COPY') else (e[1],)): raise Block('event c must touch p')
        F=e[-1] if e[0] not in('INIT','CLEAR') else e[2]
    if F==Z: raise Block('F==Z')
    rows=rows_prefix(S,NR,v.own,c)
    h=rows[p].copy(); h[p]-=1
    sp=v.spans; cur={}
    for e2 in S[:c]:
        if e2[0] in('ADD','COPY'): cur[e2[1]]=e2[-1]; cur[e2[2]]=e2[-1]
        elif e2[0]=='SCALE': cur[e2[1]]=e2[-1]
    def chart(r): return cur.get(r,w['initial'][r] if r<n else None)
    if not(sp[chart(p)]<=sp[F]): raise Block('p above F')
    undo=[]
    nonZ=[r for r in range(len(h)) if h[r]!=0 and r!=p and (r>=n or w['initial'][r]!=Z)]
    if nonZ:
        try: undo,h=_undo_replay(S,c,p,h,rows,n,w,Z,F,sp,chart)
        except Block: undo,h=_undo_lp(S,c,p,h,rows,n,w,Z,F,sp,chart)
    kk={int(r):float(h[r]) for r in np.nonzero(h)[0]}
    for r in kk:
        if r>=n or r==p or w['initial'][r]!=Z: raise Block('p not pristine: k not supported on Z-initial registers')
    return dict(p=p,c=c,F=F,Z=Z,Gp=w['final'][p],undo=undo,k=kk)

def build_multi(v,hubs):
    """clone word for several NEW hubs (sorted by cut): B = pre_k(all) + S with every gadget inserted at its cut and p_i -> f_i from the cut on.  f_i = n+i, owned ids shift by m, scratch o_i = NR+m+i (placeholder)"""
    S=v.S; n=v.n; NR=v.NR; m=len(hubs)
    infos=[hub_info(v,h['p'],h['c'],h.get('F')) for h in hubs]
    order=sorted(range(m),key=lambda i:(infos[i]['c'],i)); infos=[infos[i] for i in order]
    ps=[x['p'] for x in infos]
    if len(set(ps))<m: raise Block('duplicate hub')
    S1=S
    def sh(e):
        e=list(e)
        if e[0] in('ADD','COPY'):
            if e[1]>=n: e[1]+=m
            if e[2]>=n: e[2]+=m
        elif e[1]>=n: e[1]+=m
        return e
    S1=[sh(e) for e in S]
    pre_k=[]
    for i,x in enumerate(infos):
        x['f']=n+i; x['o']=NR+m+i
        for r,kv in sorted(x['k'].items()): pre_k.append(['ADD',x['p'],r,qs(-Q(kv)),x['Z']])
    for j,x in enumerate(infos):            # undo sources must not be an earlier hub's renamed p
        for ev in x['undo']:
            if ev[2] in ps[:j]: raise Block('undo source is a renamed hub')
    body=[]; gidx={}
    ren={}
    for idx,e in enumerate(S1):
        for i,x in enumerate(infos):
            if x['c']==idx:
                p,f,o,F=x['p'],x['f'],x['o'],x['F']
                gad=[['INIT',o,F],['COPY',o,f,'1',F],['ADD',f,o,'-1',F],['ADD',f,p,'1',F]]+x['undo']+[['ADD',o,p,'-1',F]]
                body.extend(gad); gidx[i]=len(pre_k)+len(body); ren[p]=f
        e=list(e)
        if ren:
            if e[0] in('ADD','COPY'):
                e[1]=ren.get(e[1],e[1]); e[2]=ren.get(e[2],e[2])
            else: e[1]=ren.get(e[1],e[1])
        body.append(e)
    for i,x in enumerate(infos): x['g']=gidx[i]
    return dict(B=pre_k+body,np_=len(pre_k),infos=infos,m=m)

def plan_multi(v,hubs,old=(),target=None,W=3000,detour=True,exclude=(),log=None,diag=False):
    """joint LP.  hubs: new hand-overs [{p,c,F}] on v.S; old: hand-overs already present in v (dicts p,f,F,G) whose compensation events were stripped (their f are public ids < v.n);
    target: View whose rows are the TARGET (default v).  -> plan dict"""
    import scipy.sparse as sp_, bisect
    from scipy.optimize import linprog
    w=v.w; n=v.n; NR=v.NR
    bm=build_multi(v,hubs); B=bm['B']; infos=bm['infos']; m=bm['m']
    n2=n+m; NRp=NR+2*m; npub=n2
    tv=target or v
    Z=infos[0]['Z']
    initial=list(w['initial'])+[x['F'] for x in infos]; final=list(w['final'])+[x['Gp'] for x in infos]
    for x in infos: final[x['p']]=x['F']
    spans=v.spans; own=set(range(n2,NRp))
    R=rows_all(B,NRp,own)[:n2,:n2]
    R0=getattr(tv,'_ho_R0',None)
    if R0 is None: R0=tv._ho_R0=rows_all(tv.S,tv.NR,tv.own)[:tv.n,:tv.n]
    tgt=np.zeros((n2,n2)); tgt[:tv.n,:tv.n]=R0
    for x in infos: tgt[x['f'],x['f']]=1
    Err=R-tgt
    hubs_all=[dict(p=o_['p'],f=o_['f'],F=o_['F'],G=o_['G'],new=False) for o_ in old]+[dict(p=x['p'],f=x['f'],F=x['F'],G=x['Gp'],new=True,k=x['k']) for x in infos]
    hp=[h_['p'] for h_ in hubs_all]; hf=[h_['f'] for h_ in hubs_all]
    rank={p_:i for i,p_ in enumerate(hp)}
    ksrc=sorted({r for x in infos for r in x['k']})
    srcs=hp+[r for r in ksrc if r not in hp]
    touch=collections.defaultdict(list)
    for i,e in enumerate(B):
        if e[0] in('ADD','COPY'): touch[e[1]].append(i); touch[e[2]].append(i)
        else: touch[e[1]].append(i)
    def chart_of_event(e): return e[2] if e[0] in('INIT','CLEAR') else e[-1]
    # alive owned sources: lifetime, last target event, row after it, chart
    life=[]; op_={}
    for i,e in enumerate(B):
        if e[0]=='INIT': op_[e[1]]=i
        elif e[0]=='CLEAR' and e[1] in op_: life.append((e[1],op_.pop(e[1]),i))
    for q_,i0_ in op_.items(): life.append((q_,i0_,len(B)))      # (new scratch: CLEAR is placed after planning)
    newo={x['o']:i for i,x in enumerate(infos)}
    # forward pass: rows of owned sources after their last target event
    tl_={}
    for (q_,i0_,i1_) in life:
        if q_ not in newo and not any(hh['F'] for hh in hubs_all): pass
        L=[t for t in touch[q_] if i0_<=t<i1_ and (B[t][0]=='INIT' or (B[t][0] in('ADD','COPY') and B[t][1]==q_) or B[t][0]=='SCALE')]
        tl_[q_]=max(L) if L else i0_
    need=collections.defaultdict(list)
    for (q_,i0_,i1_) in life: need[tl_[q_]].append(q_)
    srow={}
    rr=np.eye(NRp)
    for r_ in own: rr[r_]=0
    lastneed=max(need) if need else -1
    chq={}
    chv=list(initial)+[None]*(NRp-len(initial))
    for i,e in enumerate(B[:lastneed+1]):
        op,r_=e[0],e[1]
        if op=='ADD': rr[r_]+=_fq(e[3])*rr[e[2]]; chv[r_]=e[-1]; chv[e[2]]=e[-1]
        elif op=='SCALE': rr[r_]*=_fq(e[2]); chv[r_]=e[-1]
        elif op=='COPY': rr[r_]=_fq(e[3])*rr[e[2]]; chv[r_]=e[-1]; chv[e[2]]=e[-1]
        elif op=='INIT': rr[r_]=0; chv[r_]=e[2]
        else: rr[r_]=0; chv[r_]=None
        if i in need:
            for q_ in need[i]:
                rv=rr[q_,:n2].copy()
                if 0<np.count_nonzero(rv)<=4: srow[q_]=(i,rv,chv[q_])
    hi_all=len(B)-1
    cand=[]; pubsrc={}; pubF={}
    def gaps_for(T,tlo,thi,Fq,detour_ok):
        L=touch[T]; k=bisect.bisect_right(L,tlo)
        prev=L[k-1] if k>0 else None
        X=chart_of_event(B[prev]) if prev is not None else initial[T] if T<len(initial) else None
        t=tlo; out=[]
        while True:
            nxt=L[k] if k<len(L) else None
            Y=chart_of_event(B[nxt]) if nxt is not None else (final[T] if T<len(final) else None)
            if X is None: cost=None
            elif X==Fq or Y==Fq: cost=1
            elif detour_ok and Y is not None and spans[X]<spans[Fq]<spans[Y]: cost=3
            else: cost=None
            if cost is not None and B[t][0]!='CLEAR' and t<=thi: out.append((t,cost))
            if nxt is None or nxt>thi: break
            t=nxt; X=chart_of_event(B[nxt]); k+=1
        return out
    # window options with every alive sparse owned source
    for (q_,i0_,i1_) in life:
        if q_ not in srow: continue
        ts,rv,Fq=srow[q_]
        if Fq is None: continue
        thi=min(i1_-1,ts+W,hi_all)
        if q_ in newo:
            thi=min(ts+W,hi_all)
        for T in range(n2):
            if T==q_ or T in exclude: continue
            if T in hp and not new_ok(T,q_): continue
            for t,cost in gaps_for(T,ts,thi,Fq,detour):
                cand.append((T,t,cost,q_))
        # owned scratch as targets (they descend)
        for (q2,j0,j1) in life:
            if q2==q_ or q2 in newo: continue
            L=touch[q2]
            for a_,b_ in zip(L,L[1:]):
                t=max(a_,ts)
                if t<j0 or t>=j1 or t>thi or b_>thi+1: continue
                X=chart_of_event(B[a_]); Y=chart_of_event(B[b_])
                if X==Fq or Y==Fq or (spans[Fq]<spans[X] and spans[Y]<=spans[Fq]): cand.append((q2,t,2,q_))
    # public registers sitting on a hub's F with a sparse known row (frozen hubs, x_623 ...): window options near that hub's gadget, no detours
    W2=int(os.environ.get('LATECUT_W2','400'))
    for x in infos:
        F=x['F']; g=x['g']
        TT=[g-1]+[i for i in range(g,min(len(B),g+W2)) if B[i][0] not in('INIT','CLEAR') and B[i][-1]==F]
        TTs=set(TT); last=max(TT)
        rr2=np.eye(NRp)
        for r_ in own: rr2[r_]=0
        ch2=list(initial)+[None]*(NRp-len(initial))
        for i,e in enumerate(B[:last+1]):
            op,r_=e[0],e[1]
            if op=='ADD': rr2[r_]+=_fq(e[3])*rr2[e[2]]; ch2[r_]=e[-1]; ch2[e[2]]=e[-1]
            elif op=='SCALE': rr2[r_]*=_fq(e[2]); ch2[r_]=e[-1]
            elif op=='COPY': rr2[r_]=_fq(e[3])*rr2[e[2]]; ch2[r_]=e[-1]; ch2[e[2]]=e[-1]
            elif op=='INIT': rr2[r_]=0; ch2[r_]=e[2]
            else: rr2[r_]=0; ch2[r_]=None
            if i in TTs:
                for q in range(n2):
                    if ch2[q]!=F: continue
                    rv=rr2[q,:n2]; nzq=np.count_nonzero(rv)
                    if nzq==0 or nzq>4: continue
                    pubsrc[(q,i)]=rv.copy(); pubF[(q,i)]=F
    for (q,t),rv in pubsrc.items():
        Fq=None
        for x in infos:
            pass
        for T in range(n2):
            if T==q or T in exclude: continue
            L=touch[T]; k=bisect.bisect_right(L,t)
            X=chart_of_event(B[L[k-1]]) if k>0 else initial[T]
            Y=chart_of_event(B[L[k]]) if k<len(L) else final[T]
            Fq=pubF[(q,t)]
            if (X==Fq or Y==Fq) and B[t][0]!='CLEAR': cand.append((T,t,2,(q,t)))
    cand=list({c_:1 for c_ in cand}.keys())
    pre=[T for T in range(n2) if initial[T]==Z and T not in srcs and T not in hf and T not in exclude]
    preT=[(T,s) for T in pre for s in srcs]
    # hub targets: allowed as pre targets of an earlier-ranked hub source
    for T in hp:
        if initial[T]==Z:
            for s in hp:
                if rank[s]<rank[T]: preT.append((T,s))
    want=collections.defaultdict(list)
    for T,s in preT: want[-1].append(T)
    for T,t,cost,q_ in cand: want[t].append(T)
    cols=suffix_columns(B,NRp,want)
    Eend=[]
    for hi_,hh in enumerate(hubs_all):
        for r in range(n2):
            if r in hp or r in hf or final[r]!=hh['G'] or r in exclude: continue
            Eend.append((r,hi_))
    Q_=set(np.nonzero(np.abs(Err).sum(axis=0))[0].tolist())|set(srcs)|set(hf)
    for q_,(ts,rv,Fq) in srow.items(): Q_|=set(np.nonzero(rv)[0].tolist())
    for k_,rv in pubsrc.items(): Q_|=set(np.nonzero(rv)[0].tolist())
    Q_=sorted(Q_); qi={q:i for i,q in enumerate(Q_)}
    nv_a=len(preT); nv_c=len(cand); nv_b=len(Eend); nv=nv_a+nv_c+nv_b
    Ar=[];Ac=[];Av=[]
    for j,(T,s) in enumerate(preT):
        col=cols[(T,-1)][:npub]; nz=np.nonzero(col)[0]; qq=qi[s]
        for r in nz: Ar.append(qq*npub+int(r)); Ac.append(j); Av.append(col[r])
    for j,(T,t,cost,q_) in enumerate(cand):
        col=cols[(T,t)][:npub]; nz=np.nonzero(col)[0]; rv=srow[q_][1] if not isinstance(q_,tuple) else pubsrc[q_]
        for q in np.nonzero(rv)[0]:
            qq=qi[int(q)]
            for r in nz: Ar.append(qq*npub+int(r)); Ac.append(nv_a+j); Av.append(col[r]*rv[q])
    for j,(r,hi_) in enumerate(Eend):
        Ar.append(qi[hf[hi_]]*npub+r); Ac.append(nv_a+nv_c+j); Av.append(1.0)
    A=sp_.csr_matrix((Av,(Ar,Ac)),shape=(len(Q_)*npub,nv))
    rhs=np.concatenate([-Err[:,q] for q in Q_])
    A2=sp_.hstack([A,-A]).tocsr()
    cost_=np.array([1.0]*nv_a+[cc for (_,_,cc,_) in cand]+[1.0]*nv_b)
    if diag:
        nr=A.shape[0]; I=sp_.identity(nr,format='csr')
        A3=sp_.hstack([A2,I,-I]).tocsr(); c3=np.concatenate([cost_,cost_,np.full(2*nr,100.0)])
        r3=linprog(c3,A_eq=A3,b_eq=rhs,bounds=(0,None),method='highs')
        sl=r3.x[2*nv:2*nv+nr]-r3.x[2*nv+nr:]
        return dict(resid=[(Q_[i//npub],i%npub,float(sl[i])) for i in np.nonzero(np.abs(sl)>1e-9)[0]],Err=Err,Q=Q_)
    res=linprog(np.concatenate([cost_,cost_]),A_eq=A2,b_eq=rhs,bounds=(0,None),method='highs')
    if res.status!=0: raise Block('no joint compensation (LP %s)'%res.message[:50])
    x=res.x[:nv]-res.x[nv:]
    sol=dict(pre=[(preT[j][0],preT[j][1],x[j]) for j in range(nv_a) if abs(x[j])>1e-9],
             win=[(cand[j][0],cand[j][1],x[nv_a+j],cand[j][3]) for j in range(nv_c) if abs(x[nv_a+j])>1e-9],
             end=[(Eend[j][0],hf[Eend[j][1]],x[nv_a+nv_c+j]) for j in range(nv_b) if abs(x[nv_a+nv_c+j])>1e-9])
    return dict(bm=bm,B=B,infos=infos,hubs_all=hubs_all,initial=initial,final=final,sol=sol,obj=res.fun,life=life,Err=Err,n2=n2,NRp=NRp,m=m,hp=hp,pubF=pubF)

def new_ok(T,q_): return True

def emit_multi(v,pl,reuse=True):
    B=[list(e) for e in pl['B']]; bm=pl['bm']; infos=pl['infos']; sol=pl['sol']; n=v.n; m=pl['m']; hp=pl['hp']; rank={p_:i for i,p_ in enumerate(hp)}
    Z=infos[0]['Z']
    pre=[['ADD',T,s,qs(_dy(a)),Z] for T,s,a in sorted(sol['pre'],key=lambda t:-rank.get(t[1],-1))]
    npk=bm['np_']
    end=[['ADD',T,f,qs(_dy(bb)),next(h_['G'] for h_ in pl['hubs_all'] if h_['f']==f)] for T,f,bb in sol['end']]
    ins=collections.defaultdict(list)
    Fof={}
    for x in infos: Fof[x['o']]=x['F']
    for q_,i0_,i1_ in pl['life']:
        pass
    # chart of each source at insertion: owned sources keep their chart
    chart_src={}
    for (q_,i0_,i1_) in pl['life']:
        chart_src[q_]=None
    # chart per source from the plan: srow holds it; recompute from B (last event chart of q before insertion)
    def chart_at(q_,t):
        c_=None
        for i in range(t,-1,-1):
            e=B[i]
            if e[0] in('ADD','COPY') and q_ in e[1:3]: return e[-1]
            if e[0] in('SCALE',) and e[1]==q_: return e[-1]
            if e[0]=='INIT' and e[1]==q_: return e[2]
        return None
    lastuse={}
    for T,t,cc,sr in sol['win']:
        if isinstance(sr,tuple): ins[t].append(['ADD',T,sr[0],qs(_dy(cc)),pl['pubF'][sr]]); continue
        ins[t].append(['ADD',T,sr,qs(_dy(cc)),chart_at(sr,t)])
        lastuse[sr]=max(lastuse.get(sr,-1),t)
    out=[]
    clear_after={}
    for x in infos:
        o=x['o']; clear_after[max(lastuse.get(o,-1),x['g']-1)]=clear_after.get(max(lastuse.get(o,-1),x['g']-1),[])+[(o,x['F'])]
    for i,e in enumerate(B):
        if i<npk: continue
        out.append(e)
        if i in ins: out.extend(ins[i])
        if i in clear_after:
            for o,F in clear_after[i]: out.append(['CLEAR',o,F])
    S2=pre+B[:npk]+out+end
    if reuse:
        n1=n+m; phs=sorted(x['o'] for x in infos)
        for x in infos:
            o=x['o']
            # lifetime in S2
            ia=next(i for i,e in enumerate(S2) if e[0]=='INIT' and e[1]==o); ib=next(i for i,e in enumerate(S2) if e[0]=='CLEAR' and e[1]==o and i>ia)
            o2=free_owned_id(S2,n1,phs[0],ia,ib,o)
            if o2!=o:
                S2=[[ (o2 if (j in(1,2) and x_==o and (e[0] in('ADD','COPY') or j==1)) else x_) for j,x_ in enumerate(e)] for e in S2]
    return S2,pl['initial'],pl['final']

# ------------------------------------------------------------------ site enumeration
def _H(r,kappa=0.0031): return r**(1-kappa) if r>0 else 0.0
_BT={}
def _between(v,X,Fr):
    """frames f with span(X) <= span(f) < span(Fr) (cached per word)"""
    key=(id(v.w),X,Fr); r=_BT.get(key)
    if r is None:
        sp=v.spans; sx=sp[X]; sf=sp[Fr]
        r=_BT[key]=[f for f in range(len(sp)) if sx<=sp[f] and sp[f]<sf]
    return r
def sites(v,variants=('A','B','C'),only=None,topC=2):
    """handover sites (edit dicts {p,c,F}): public p initial on Z, a run of p's events on an intermediate chart F (Z < F < final, nested spans).
    variant A: cut before the first event of the run (f starts on F, p moves there: #5786 hub 623); variant B: cut after the last event of the run (p rests on F: split2 / #5786 hub 696).
    ranked by the field gain H(dF-dZ)+H(dG-dF)-H(dG).  Feasibility (a legal compensation exists) is decided by `plan`."""
    w=v.w; S=v.S; n=v.n; Z=zero_frame(w); dim=v.dim; sp=v.spans; cand=[]
    if Z is None: return
    ev=collections.defaultdict(list)
    for i,e in enumerate(S):
        if e[0] in('ADD','COPY'):
            if e[1]<n: ev[e[1]].append(i)
            if e[2]<n: ev[e[2]].append(i)
        elif e[0]=='SCALE' and e[1]<n: ev[e[1]].append(i)
    for p in (only if only is not None else range(n)):
        if w['initial'][p]!=Z: continue
        G=w['final'][p]
        if dim[G]-dim[Z]<2: continue
        L=ev[p]; j=0
        while j<len(L):
            F=S[L[j]][-1]; k=j
            while k+1<len(L) and S[L[k+1]][-1]==F: k+=1
            if F!=Z and F!=G and dim[Z]<dim[F]<dim[G] and sp[Z]<sp[F]<sp[G]:
                gain=_H(dim[F]-dim[Z])+_H(dim[G]-dim[F])-_H(dim[G])
                if 'A' in variants: cand.append((gain,dict(p=p,c=L[j],F=F,var='A')))
                if 'B' in variants and k+1<len(L): cand.append((gain,dict(p=p,c=L[k]+1,F=F,var='B')))
            if 'C' in variants and F!=Z and sp[Z]<sp[F] and dim[Z]<dim[G]:
                # variant C: F strictly BETWEEN p's resting chart and the chart of its next run (#5786 hub 585: F=245 below 127); p ascends Z..X -> F, f goes F -> F_run
                X=S[L[j-1]][-1] if j>0 else Z
                best=[]
                for fr in _between(v,X,F):
                    if fr==Z or fr==G or not(dim[Z]<dim[fr]<dim[G]): continue
                    best.append((_H(dim[fr]-dim[Z])+_H(dim[G]-dim[fr])-_H(dim[G]),fr))
                best.sort(reverse=True)
                for gain,fr in best[:topC]: cand.append((gain,dict(p=p,c=L[j],F=fr,var='C')))
            j=k+1
    cand.sort(key=lambda t:-t[0])
    for g,ed in cand: yield ed

# ------------------------------------------------------------------ apply
def apply_parts(v,ed,W=3000,detour=True):
    if 'hubs' in ed:
        pl=plan_multi(v,ed['hubs'],old=ed.get('old',()),target=ed.get('target'),W=ed.get('W',W),detour=ed.get('detour',detour),exclude=ed.get('exclude',()))
        S2,ini,fin=emit_multi(v,pl); return S2,ini,fin,pl
    pl=plan(v,ed['p'],ed['c'],W=ed.get('W',W),detour=ed.get('detour',detour),F=ed.get('F'))
    S2,ini,fin=emit(v,pl)
    return S2,ini,fin,pl
def apply_edit(w,ed,v=None,check=True):
    """word with the hand-over applied (pins stamped: lifetimes/peak/owned_fields/public are package conventions).  check: exact Fraction value check of the public rows"""
    import prims_extra as PE
    v=v or M.View(w); S2,ini,fin,pl=apply_parts(v,ed)
    if check:
        bad=verify_rows(v,S2,len(ini),ed.get('target'))
        if bad: raise Block('value check failed on %s'%bad[:5])
    w2=rebuild_shifted(v,S2,ini,fin)
    return PE.stamp(w2,S2)

# ------------------------------------------------------------------ search level (pscreen / tk handover)
def level(w,tl=1e9,topq=10,only=None,variants=('A','B'),log=print,shard=(0,1),maxsites=None,results=None):
    """price every handover site exactly (plan + exact value check + M.evaluate with stamped pins).  -> [(kappa, word, edit, verdict)] best first (legal ones only)"""
    t0=time.time(); v=M.View(w); out=[]; n=nb=0
    for idx,ed in enumerate(sites(v,variants,only)):
        if idx%shard[1]!=shard[0]: continue
        if maxsites and n>=maxsites: break
        n+=1
        try: w2=apply_edit(w,ed,v)
        except (Block,ValueError,KeyError,AssertionError,IndexError): nb+=1; continue
        o=M.evaluate(w2)
        if not o.get('legal') and 'transport' in str(o.get('why')):       # chart-legality retry: no nested detours through F, shorter window
            for alt in (dict(detour=False),dict(detour=False,W=600)):
                try: w3=apply_edit(w,dict(ed,**alt),v)
                except (Block,ValueError,KeyError,AssertionError,IndexError): continue
                o3=M.evaluate(w3)
                if o3.get('legal'): w2,o,ed=w3,o3,dict(ed,**alt); break
        if results is not None: results.write(json.dumps(dict(ed=ed,legal=bool(o.get('legal')),kappa=o.get('kappa'),why=str(o.get('why'))[:120]))+'\n'); results.flush()
        if o.get('legal'): out.append((o['kappa'],w2,dict(ed,prim='P13'),o))
        if time.time()-t0>tl: break
    out.sort(key=lambda x:-x[0])
    log('    P13 level: %d sites tried, %d blocked, %d legal, top %s [%.0fs]'%(n,nb,len(out),'%.12f'%out[0][0] if out else None,time.time()-t0))
    return out[:topq]
