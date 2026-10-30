"""relaycomp -- the COMPENSATED layer of tk relay (TKRELAY): value-changing edits whose endpoint-map error E is repaired by free pre/post ADDs.

MODEL.  A word computes the linear map x_out = M x_in (rows = final registers, columns = input rows).  An edit changes it to M' = Req + E (Req = required endpoint rows:
e_y, plus e_{y-112} for a Y register).  If E can be absorbed the word stays legal and only the MOVE multiset (price) changes.  (RELAYGEN theory, all re-derived here.)
  * INJECTION calculus.  Adding the form D to register x at insertion gap g changes the final map by  S_x(g) (x) D  where S_x(g) is the SENSITIVITY covector of x at gap g
    (S_x(g)[y] = d final_y / d x_x: one backward pass, `Sens`).   Deleting a contact `x += c*s` is the injection (x, -c*f_s).  A single-target edit (spansolve in relay.py) has E = 0.
    JOINT edits trade S against D:  sum_j c_j S_{t_j} (x) f_s  ==  a S_x (x) f_u  (mod free rows / free columns).
  * ABSORB.  PRE:  rows r in Zpre (helpers whose initial frame is the common zero frame), E[r] supported on other Zpre columns  ->  ADD r += -E[r][c]*c at the start (precompose I-E,
    exact since the row and column sets are disjoint).  POST:  rows y in Zpost (final frame = the common full frame), E[y] in the span of the clean required rows Req[z] (z in Zpost)  ->
    ADD y += k*z at the end (spansolve finds k).  Pre is applied first, E is recomputed by exact replay, then post.
API
    final_forms(view,S2)            -> {y: form} final symbolic value of every register of the scalar program S2
    residual(view,S2)               -> {y: E[y]} (sparse, only rows with E != 0)
    zsets(view)                     -> (Fpre,Zpre,Fpost,Zpost)
    absorb(view,S2)                 -> (S3, info) with pre/post ADDs added, or (None, why)
    Sens(view).at(gaps)             -> {gap: {x: covector}} sensitivity covectors by one backward pass
"""
import collections
from fractions import Fraction as Q
import spansolve as SS
import dag as D

def _ops(view):
    ops=[]
    for e in view.S:
        if e[0] in('ADD','COPY'): ops.append([e[0],e[1],e[2],e[3],e[4],None])
        elif e[0]=='SCALE': ops.append(['SCALE',e[1],None,e[2],e[3],None])
        else: ops.append([e[0],e[1],None,None,e[2],None])
    return ops
def final_forms(view,S2):
    """symbolic execution of the scalar program S2 (list of events) -> final form of every register"""
    n=view.n; meta=dict(npub=n,nowned=view.NR-n,live=list(view.w['live']))
    ops=[]
    for e in S2:
        if e[0] in('ADD','COPY'): ops.append([e[0],e[1],e[2],e[3],e[4],None])
        elif e[0]=='SCALE': ops.append(['SCALE',e[1],None,e[2],e[3],None])
        else: ops.append([e[0],e[1],None,None,e[2],None])
    F,_=D.apply_forms(ops,meta)
    return F
def required(view):
    n=view.n; live=set(view.w['live']); req={}
    for y in range(n):
        f={y:Q(1)}
        if y-112 in live: f[y-112]=Q(1)
        req[y]=f
    return req
def residual(view,S2):
    F=final_forms(view,S2); req=required(view); E={}
    for y in range(view.n):
        d=dict(F[y])
        for k,x in req[y].items():
            v=d.get(k,0)-x
            if v: d[k]=v
            else: d.pop(k,None)
        if d: E[y]=d
    for r in range(view.n,view.NR):
        if F[r]: E[r]=dict(F[r])           # owned must end empty
    return E
def zsets(view):
    """Fpre/Zpre: the most common initial frame among helper registers; Fpost/Zpost: the most common final frame (public registers)"""
    w=view.w; n=view.n; live=set(w['live']); main=live|{r+112 for r in live}
    helpers=[r for r in range(n) if r not in main]
    Fpre=collections.Counter(w['initial'][r] for r in helpers).most_common(1)[0][0]
    Fpost=collections.Counter(w['final'][r] for r in range(n)).most_common(1)[0][0]
    return Fpre,{r for r in helpers if w['initial'][r]==Fpre},Fpost,{r for r in range(n) if w['final'][r]==Fpost}
def _apply(F,e):
    op=e[0]; r=e[1]
    if op=='ADD':
        c=Q(e[3]); d=dict(F[r])
        for k,x in F[e[2]].items():
            t=d.get(k,0)+c*x
            if t: d[k]=t
            else: d.pop(k,None)
        F[r]=d
    elif op=='COPY':
        c=Q(e[3]); F[r]={k:c*x for k,x in F[e[2]].items()}
    elif op=='SCALE':
        q=Q(e[2]); F[r]={k:q*x for k,x in F[r].items()}
    else: F[r]={}
def _stream(S,S2):
    """lock-step merge of the original scalar program S and the edited S2: list of ('both'|'orig'|'edit', event)"""
    import difflib
    ka=[tuple(map(str,e)) for e in S]; kb=[tuple(map(str,e)) for e in S2]
    sm=difflib.SequenceMatcher(None,ka,kb,autojunk=False); out=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag=='equal':
            for j in range(j1,j2): out.append(('both',S2[j]))
        else:
            for i in range(i1,i2): out.append(('orig',S[i]))
            for j in range(j1,j2): out.append(('edit',S2[j]))
    return out
def gather_post(view,S2,Fpost,maxdiff=16,max_terms=6,log=None):
    """earliest gap of the edited program at which every register that differs from the ORIGINAL program's state sits at the full frame and its difference is a combination of
    clean full-frame registers (PR5605: 'compare the two words immediately before event 24461: exactly six public rows differ').  -> (gap, [ADD events]) or None"""
    v=view; n=v.n; NR=v.NR; w=v.w
    Fe=[{r:Q(1)} for r in range(n)]+[{} for _ in range(NR-n)]; Fo=[dict(f) for f in Fe]
    frame=list(w['initial'])+[None]*(NR-n); diff=set(); gap=0; tried=None
    for kind,e in _stream(v.S,S2):
        if kind!='orig':
            frame[e[1]]=e[-1] if e[0] not in('INIT','CLEAR') else e[2]
            if e[0] in('ADD','COPY'): frame[e[2]]=e[-1]
        if kind in('both','orig'): _apply(Fo,e)
        if kind in('both','edit'): _apply(Fe,e)
        if kind!='orig': gap+=1
        r=e[1]
        if Fe[r]!=Fo[r]: diff.add(r)
        else: diff.discard(r)
        if diff and len(diff)<=maxdiff and all(x<n and frame[x]==Fpost for x in diff):
            key=(frozenset(diff),gap)
            if tried==frozenset(diff): continue
            tried=frozenset(diff)
            cands=[SS.Cand(z,Fe[z]) for z in range(n) if z not in diff and frame[z]==Fpost and Fe[z]]
            ops=[]; ok=True
            for y in sorted(diff):
                dv={k:Fo[y].get(k,0)-Fe[y].get(k,0) for k in set(Fo[y])|set(Fe[y])}; dv={k:x for k,x in dv.items() if x}
                sols=SS.solve(dv,cands,max_terms=max_terms,nbest=1)
                if not sols: ok=False; break
                for c,a_ in sols[0].terms: ops.append(['ADD',y,c.key,SS_qs(a_),Fpost])
            if log: log('   gather gap %d diff %d ok %s'%(gap,len(diff),ok))
            if ok: return gap,ops
    return None
def absorb(view,S2,max_pre=400,max_post=400,log=None):
    """pre/post compensation of the residual of S2.  -> (S3, info) or (None, reason).   PRE: rows y of E that are initial-frame-Fpre registers (not X) whose error columns are other
    Fpre registers, disjoint from the rows -> ADD y += -E[y][c]*c at the start.   POST: gather_post at the earliest gap with a small, full-frame, absorbable difference."""
    n=view.n; Fpre,Zpre,Fpost,Zpost=zsets(view); w=view.w; live=set(w['live'])
    E=residual(view,S2)
    if not E: return list(S2),dict(pre=0,post=0)
    if any(y>=n for y in E): return None,'owned register not empty at the end'
    cand=[y for y in E if w['initial'][y]==Fpre and y not in live and all(c<n and w['initial'][c]==Fpre for c in E[y])]
    R=set(cand); pre=[]
    for y in sorted(cand):
        if any(c in R for c in E[y]): R.discard(y); continue
    pre=[['ADD',y,c,SS_qs(-E[y][c]),Fpre] for y in sorted(R) for c in sorted(E[y])]
    if len(pre)>max_pre: return None,'too many pre ADDs'
    S2b=pre+list(S2)
    E2=residual(view,S2b) if pre else E
    if not E2: return S2b,dict(pre=len(pre),post=0,pre_rows=sorted(R))
    g=gather_post(view,S2b,Fpost,log=log)
    if g is None: return None,'no absorbable post gap (residual rows %s)'%sorted(E2)[:8]
    gap,ops=g
    if len(ops)>max_post: return None,'too many post ADDs'
    return S2b[:gap]+ops+S2b[gap:],dict(pre=len(pre),post=len(ops),pre_rows=sorted(R),post_gap=gap,post_rows=sorted({o[1] for o in ops}))
def SS_qs(x):
    x=Q(x); return str(x.numerator) if x.denominator==1 else '%d/%d'%(x.numerator,x.denominator)
class Sens:
    """backward sensitivity pass over the scalar program: S_x(g)[y] = d final_y / d (value of x at insertion gap g)"""
    def __init__(s,view): s.view=view
    def at(s,gaps,regs=None):
        """-> {gap: {x: {y: coef}}} for the requested gaps (all registers, or only `regs`)"""
        v=s.view; S=v.S; N=len(S); n=v.n; gaps=sorted(set(gaps),reverse=True)
        Sv=[dict() for _ in range(v.NR)]
        for y in range(n): Sv[y]={y:Q(1)}
        out={}; gi=0
        def snap(g):
            out[g]={x:dict(Sv[x]) for x in (regs if regs is not None else range(v.NR)) if Sv[x]}
        while gi<len(gaps) and gaps[gi]>=N:
            snap(gaps[gi]); gi+=1
        for i in range(N-1,-1,-1):
            e=S[i]; op=e[0]; r=e[1]
            if op=='ADD':
                c=Q(e[3]); sr=Sv[r]
                if sr:
                    d=Sv[e[2]]
                    for y,x in sr.items():
                        t=d.get(y,0)+c*x
                        if t: d[y]=t
                        else: d.pop(y,None)
            elif op=='COPY':
                c=Q(e[3]); sr=Sv[r]
                if sr:
                    d=Sv[e[2]]
                    for y,x in sr.items():
                        t=d.get(y,0)+c*x
                        if t: d[y]=t
                        else: d.pop(y,None)
                Sv[r]={}
            elif op=='SCALE':
                q=Q(e[2]); Sv[r]={y:q*x for y,x in Sv[r].items()}
            else: Sv[r]={}
            while gi<len(gaps) and gaps[gi]==i:
                snap(i); gi+=1
        return out
# ======================================================================================================== JOINT relays (S-span x D-span)
def _norm(vec,free):
    """(key, scale) of vec restricted to coordinates not in `free`, normalised by its first coefficient; (None,None) if the restriction is empty"""
    ks=sorted(k for k,x in vec.items() if k not in free and x)
    if not ks: return None,None
    sc=vec[ks[0]]
    return hash(tuple((k,vec[k]/sc) for k in ks)),sc
class SensPass:
    """ONE backward pass over the scalar program: keyed S-intervals + exact S vectors at requested (gap,reg) pairs and at requested contact ops.
    intervals: list of (x, lo, hi, key, scale): for gaps lo..hi the sensitivity covector of register x restricted to rows not in `free_rows` has normalised key `key`."""
    def __init__(s,view,free_rows,want_ops=(),want=None):
        v=view; S=v.S; N=len(S); n=v.n; NR=v.NR; free=free_rows
        Sv=[dict() for _ in range(NR)]
        for y in range(n): Sv[y]={y:Q(1)}
        s.contact={}; s.vec={}; s.intervals=[]; want_ops=set(want_ops); want=want or {}
        keys=[_norm(Sv[x],free) for x in range(NR)]; hi=[N]*NR
        def touch(x,i):
            k=keys[x]
            if k[0] is not None: s.intervals.append((x,i+1,hi[x],k[0],k[1]))
            keys[x]=_norm(Sv[x],free); hi[x]=i
        for g,xs in want.items():
            if g>=N: s.vec[g]={x:dict(Sv[x]) for x in xs}
        for i in range(N-1,-1,-1):
            e=S[i]; op=e[0]; r=e[1]
            if op in('ADD','COPY'):
                c=Q(e[3]); sr=Sv[r]; sidx=e[2]
                if sr:
                    d=dict(Sv[sidx])
                    for y,x in sr.items():
                        t=d.get(y,0)+c*x
                        if t: d[y]=t
                        else: d.pop(y,None)
                    Sv[sidx]=d; touch(sidx,i)
                if op=='COPY':
                    if Sv[r]: Sv[r]={}; touch(r,i)
                elif i in want_ops: s.contact[i]=dict(Sv[r])
            elif op=='SCALE':
                q=Q(e[2])
                if Sv[r]: Sv[r]={y:q*x for y,x in Sv[r].items()}; touch(r,i)
            else:
                if Sv[r]: Sv[r]={}; touch(r,i)
            if i in want: s.vec[i]={x:dict(Sv[x]) for x in want[i]}
        for x in range(NR):
            k=keys[x]
            if k[0] is not None: s.intervals.append((x,0,hi[x],k[0],k[1]))
class Joint:
    """joint relay proposals: remove a SET of contacts reading one owned value, add ONE contact x += a*u elsewhere.  Matching is on the free-coordinate quotient:
    S side modulo Zpost rows (post-repairable), value side modulo Zpre columns (pre-repairable)."""
    def __init__(s,view,tl):
        s.v=view; s.tl=tl; s.Fpre,s.Zpre,s.Fpost,s.Zpost=zsets(view)
    def reader_groups(s,owned_only=True):
        v=s.v; g={}
        for i,e in enumerate(v.S):
            if e[0]=='ADD' and (not owned_only or e[2]>=v.n): g.setdefault((e[2],s.tl.version(e[2],i)),[]).append(i)
        return g
    def value_index(s,hoist=True):
        """key -> [(u,vid,lo,hi,hoistop,scale)]: every register version and (hoist=True) the versions reachable by moving an ADD(u<-v) back over a gap where u is untouched/unread and v unchanged"""
        tl=s.tl; v=s.v; S=v.S; idx={}
        def add(u,vid,lo,hi,h,vec):
            k,sc=_norm(vec,s.Zpre)
            if k is not None and lo<=hi: idx.setdefault(k,[]).append((u,vid,lo,hi,h,sc))
        for u in range(v.NR):
            ws=[i for i,f,k in tl.ev[u] if k=='w']
            if u<v.n: 
                nxt=ws[0] if ws else len(S)
                add(u,-1,0,nxt,None,tl.form(u,-1))
            for a,w_ in enumerate(ws):
                nxt=ws[a+1] if a+1<len(ws) else len(S)
                add(u,w_,w_+1,nxt,None,tl.form_after[w_])
        if hoist:
            lastw={}   # last write index of every register before op j: computed on the fly
            lw=[-1]*v.NR; prevev=[-1]*v.NR
            for j,e in enumerate(S):
                if e[0]=='ADD':
                    u,src=e[1],e[2]
                    lo=max(prevev[u]+1,lw[src]+1)
                    if lo<j and tl.form_after[j]:
                        add(u,j,lo,j,j,tl.form_after[j])
                if e[0] in('ADD','COPY'):
                    lw[e[1]]=j; prevev[e[1]]=j; prevev[e[2]]=j
                elif e[0]=='SCALE': lw[e[1]]=j; prevev[e[1]]=j
                else: lw[e[1]]=j; prevev[e[1]]=j
        return idx
    def propose(s,maxsub=3,hoist=True,groups=None,log=print,sole_ops=None,maxcomb=3000):
        v=s.v; tl=s.tl; S=v.S
        groups=groups or s.reader_groups()
        want_ops={i for ops in groups.values() for i in ops}
        sp=SensPass(v,s.Zpost,want_ops=want_ops)
        Sidx={}
        for x,lo,hi,k,sc in sp.intervals: Sidx.setdefault(k,[]).append((x,lo,hi,sc))
        Didx=s.value_index(hoist)
        log('  joint: %d S-classes, %d value-classes, %d groups'%(len(Sidx),len(Didx),len(groups)))
        out=[]
        import itertools
        for (src,vid),ops in groups.items():
            fs=tl.form(src,vid)
            kF,scF=_norm(fs,s.Zpre)
            if kF is None: continue
            import math
            for r_ in range(1,min(maxsub,len(ops))+1):
                if r_>1 and math.comb(len(ops),r_)>maxcomb: break
                for sub in itertools.combinations(ops,r_):
                    if sole_ops is not None and not any(i in sole_ops for i in sub): continue
                    T={}
                    for i in sub:
                        c=Q(S[i][3])
                        for y,x in sp.contact[i].items():
                            t=T.get(y,0)+c*x
                            if t: T[y]=t
                            else: T.pop(y,None)
                    kT,scT=_norm(T,s.Zpost)
                    if kT is None: continue
                    for (x,slo,shi,scx) in Sidx.get(kT,[]):
                        for (u,uvid,ulo,uhi,hop,scu) in Didx.get(kF,[]):
                            if u==x: continue
                            lo=max(slo,ulo); hi=min(shi,uhi)
                            if lo>hi: continue
                            a=scT*scF/(scx*scu)
                            if not SS.is_dyadic(a): continue
                            for F,fl,fh,_v,st in tl.intervals(x,set(sub)):
                                g=max(fl,lo); g2=min(fh,hi)
                                if g>g2: continue
                                out.append(dict(kind='joint',remove=list(sub),x=x,u=u,uvid=uvid,a=SS_qs(a),gap=g,gap_hi=g2,F=F,stage=st,hoist=hop,src=src,svid=vid))
        return out
def joint_scalars(view,ed):
    """scalar program of a joint edit WITHOUT compensation"""
    S=view.S; rm=set(ed['remove']); hop=ed.get('hoist'); h=ed['gap']
    if hop is not None: rm.add(hop)
    ins=[]
    if hop is not None: ins.append(list(S[hop]))
    ins.append(['ADD',ed['x'],ed['u'],ed['a'],ed['F']])
    out=[]
    for k,e in enumerate(S):
        if k==h: out+=ins
        if k not in rm: out.append(list(e))
    if h>=len(S): out+=ins
    return out
def algebraic_filter(view,tl,J,props,max_post_rows=24,log=print):
    """exact tensor residual E = a S_x (x) f_u - T (x) f_s of every proposal (S vectors from a second backward pass); keep those whose rows are pre/post absorbable"""
    v=view; S=v.S; n=v.n; w=v.w; live=set(w['live']); Fpre,Zpre,Fpost,Zpost=J.Fpre,J.Zpre,J.Fpost,J.Zpost
    want={}
    for p in props: want.setdefault(p['gap'],set()).add(p['x'])
    allops={i for p in props for i in p['remove']}
    sp=SensPass(v,Zpost,want_ops=allops,want=want)
    keep=[]
    for p in props:
        a=Q(p['a']); Sx=sp.vec[p['gap']][p['x']]
        T={}
        for i in p['remove']:
            c=Q(S[i][3])
            for y,x in sp.contact[i].items():
                t=T.get(y,0)+c*x
                if t: T[y]=t
                else: T.pop(y,None)
        fu=tl.form_after[p['uvid']] if p['uvid']>=0 else tl.form(p['u'],-1)
        fs=tl.form(p['src'],p['svid'])
        E={}
        for y in set(Sx)|set(T):
            row={}
            sy=Sx.get(y,0)*a; ty=T.get(y,0)
            if sy:
                for c,x in fu.items(): row[c]=row.get(c,0)+sy*x
            if ty:
                for c,x in fs.items():
                    t=row.get(c,0)-ty*x
                    if t: row[c]=t
                    else: row.pop(c,None)
            row={c:x for c,x in row.items() if x}
            if row: E[y]=row
        if not E: p['E']=0; keep.append(p); continue
        pre=[y for y in E if w['initial'][y]==Fpre and y not in live and all(c<n and w['initial'][c]==Fpre for c in E[y])]
        R=set(pre)
        pre=[y for y in pre if not any(c in R for c in E[y])]
        rest=[y for y in E if y not in set(pre)]
        if all(y in Zpost for y in rest) and len(rest)<=max_post_rows:
            p['E']=dict(pre_rows=sorted(pre),post_rows=sorted(rest)); keep.append(p)
    log('  joint: %d proposals, %d algebraically absorbable'%(len(props),len(keep)))
    return keep
