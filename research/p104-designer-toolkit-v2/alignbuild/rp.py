"""SURGERY replanner core (exact linear-algebra cleanup re-planning, numeric mod p=2^31-1 probe; final truth = legal.check).
State = R x R matrix (row r = value of register r over the R initial-value symbols); every event is a row operation.  No env at import."""
import sys, collections, numpy as np
from fractions import Fraction as Q
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'surgery'))
import swlib as S
P=2147483647
_QM={}
def qm(s):
    r=_QM.get(s)    # REBUILDSPEED: memo (pure function of the string)
    if r is None:
        q=Q(s); r=_QM[s]=q.numerator%P*pow(q.denominator%P,P-2,P)%P
    return r
def nreg(w): return len(w['initial'])+S.C.legal.nown(w)
def target(w):
    n=len(w['initial']); R=nreg(w); T=np.zeros((R,R),dtype=np.int64)
    live=set(w['live'])
    for r in range(n):
        T[r,r]=1
        if r-112 in live: T[r,r-112]=1
    return T
def step(A,e):
    o=e[0]
    if o=='MOVE': return
    if o in('INIT','CLEAR'): A[e[1],:]=0; return
    if o=='SCALE': A[e[1],:]=A[e[1],:]*qm(e[2])%P; return
    d,s,c=e[1],e[2],qm(e[3])
    if o=='COPY': A[d,:]=A[s,:]*c%P
    else: A[d,:]=(A[d,:]+A[s,:]*c)%P
def replay(w,prog=None,snap=None):
    """forward replay; snap = dict t -> list of regs: returns rows of those regs just BEFORE event t"""
    R=nreg(w); A=np.eye(R,dtype=np.int64); out={}
    prog=prog if prog is not None else w['program']
    for t,e in enumerate(prog):
        if snap and t in snap: out[t]={r:A[r].copy() for r in snap[t]}
        step(A,e)
    return A,out
def timelines(w,prog=None):
    """r -> list of [t_from, t_to, frame]; t_from = index of the MOVE (frame valid AFTER it), t_to = index of next MOVE (exclusive) or len"""
    prog=prog if prog is not None else w['program']; n=len(w['initial']); R=nreg(w); T=len(prog)
    tl={r:[[-1,None,w['initial'][r]]] for r in range(n)}
    for r in range(n,R): tl[r]=[]
    for t,e in enumerate(prog):
        if e[0]=='MOVE':
            r=e[1]
            if tl[r]: tl[r][-1][1]=t
            tl[r].append([t,None,e[3]])
        elif e[0]=='INIT':
            tl[e[1]].append([t,None,e[2]])
        elif e[0]=='CLEAR':
            tl[e[1]][-1][1]=t
    for r in tl:
        if tl[r] and tl[r][-1][1] is None: tl[r][-1][1]=T
    return tl
def end_at(w,h,f):
    """program with helper h ending at its stop at frame f: drop h's MOVEs after its arrival at f and every ADD/COPY/SCALE touching h after it leaves f.
    returns (prog', t_leave) ; final[h] must be set to f by the caller"""
    prog=w['program']; tarr=None; tlv=None
    if w['initial'][h]==f: tarr=-1
    for t,e in enumerate(prog):
        if e[0]=='MOVE' and e[1]==h:
            if tarr is not None and tlv is None: tlv=t
            if e[3]==f: tarr=t
    assert tarr is not None and tlv is not None
    out=[]; dropped=[]
    for t,e in enumerate(prog):
        if t>=tlv and ((e[0]=='MOVE' and e[1]==h) or (e[0] in('ADD','COPY') and h in(e[1],e[2])) or (e[0]=='SCALE' and e[1]==h)):
            dropped.append((t,e)); continue
        out.append(e)
    return out,tlv,dropped

# ------------------------------------------------------------------ copresence + candidate insertions
def frame_intervals(w,prog):
    tl=timelines(w,prog); byf=collections.defaultdict(list)
    for r,L in tl.items():
        for lo,hi,f in L: byf[f].append((r,lo,hi))
    return tl,byf
def touches(prog):
    """r -> sorted list of event indices touching r (any role)"""
    tc=collections.defaultdict(list)
    for t,e in enumerate(prog):
        if e[0] in('ADD','COPY'): tc[e[1]].append(t); tc[e[2]].append(t)
        else: tc[e[1]].append(t)
    return tc
def candidates(w,prog,dests,maxslots=6,srcfilter=None,owned_src=True):
    """(a,b,t,g): insert 'ADD a b c g' before index t of prog (both at frame g on [t-1 .. t)).  a in dests, b any co-present (b!=a).
    slots: overlap start and just after each event touching a or b inside the overlap (at most maxslots, spread)"""
    import bisect
    n=len(w['initial']); tl,byf=frame_intervals(w,prog); tc=touches(prog); out=[]
    for a in dests:
        for lo,hi,g in tl[a]:
            for (b,blo,bhi) in byf[g]:
                if b==a: continue
                if not owned_src and b>=n: continue
                if a>=n: continue          # never write owned scratch
                if srcfilter and not srcfilter(b): continue
                L=max(lo,blo)+1; H=min(hi,bhi)   # insertion index t in [L, H]  (state after event L-1, before event t)
                if L>H: continue
                br=sorted(set([L]+[x+1 for x in tc[a]+tc[b] if L<=x+1<=H]))
                if len(br)>maxslots:
                    idx=np.linspace(0,len(br)-1,maxslots).round().astype(int); br=[br[i] for i in sorted(set(idx))]
                for t in br: out.append((a,b,t,g))
    return out
def phi_cols(w,prog,req):
    """req: list of (t,a) -> dict (t,a) -> Phi_t[:,a] (map: state before event t -> final), numpy vector"""
    R=nreg(w); PT=np.eye(R,dtype=np.int64)    # PT[a] = column a of Phi
    need=collections.defaultdict(set)
    for t,a in req: need[t].add(a)
    out={}; T=len(prog)
    for a in need.get(T,()): out[(T,a)]=PT[a].copy()
    for t in range(T-1,-1,-1):
        e=prog[t]; o=e[0]
        if o=='MOVE': pass
        elif o in('INIT','CLEAR'): PT[e[1]]=0
        elif o=='SCALE': PT[e[1]]=PT[e[1]]*qm(e[2])%P
        else:
            d,s,c=e[1],e[2],qm(e[3])
            if o=='COPY': PT[s]=(PT[s]+PT[d]*c)%P; PT[d]=0
            else: PT[s]=(PT[s]+PT[d]*c)%P
        for a in need.get(t,()): out[(t,a)]=PT[a].copy()
    return out
def row_snaps(w,prog,req):
    need=collections.defaultdict(set)
    for t,b in req: need[t].add(b)
    R=nreg(w); A=np.eye(R,dtype=np.int64); out={}
    for t,e in enumerate(prog):
        for b in need.get(t,()): out[(t,b)]=A[b].copy()
        step(A,e)
    for b in need.get(len(prog),()): out[(len(prog),b)]=A[b].copy()
    return out
def taint_ok(prog,cands,n_iter=1):
    """exactness filter: a candidate's SOURCE b must be unperturbed at its slot by any candidate destination (perturbation starts at the
    earliest slot of each destination and spreads forward through prog' reads)."""
    first={}
    for a,b,t,g in cands: first[a]=min(first.get(a,10**9),t)
    ev=collections.defaultdict(list)
    for a,t in first.items(): ev[t].append(a)
    tainted={}   # r -> time tainted
    T=len(prog)
    for t in range(T+1):
        for a in ev.get(t,()): tainted.setdefault(a,t)
        if t<T:
            e=prog[t]
            if e[0] in('ADD','COPY') and e[2] in tainted and e[1] not in tainted: tainted[e[1]]=t+1
    return [c for c in cands if not (c[1] in tainted and tainted[c[1]]<=c[2])], tainted

# ------------------------------------------------------------------ mod-p linear algebra
def rref(M):
    """row-reduce M (k x n int64 mod P) -> (pivot rows matrix E (r x n, unit pivots, fully reduced), pivot cols list).  Works on nonzero columns only."""
    M=np.asarray(M)%P
    if M.size==0: return M[:0],[]
    k,n=M.shape; nzc=np.nonzero(M.any(0))[0]; Mc=M[:,nzc].copy(); piv=[]; r=0
    for ci in range(Mc.shape[1]):
        if r>=k: break
        col=Mc[r:,ci]; nz=np.flatnonzero(col)
        if len(nz)==0: continue
        i=r+nz[0]
        if i!=r: Mc[[r,i]]=Mc[[i,r]]
        inv=pow(int(Mc[r,ci]),P-2,P); Mc[r]=Mc[r]*inv%P
        cc=Mc[:,ci].copy(); cc[r]=0; nzr=np.flatnonzero(cc)
        if len(nzr): Mc[nzr]=(Mc[nzr]-(cc[nzr,None]*Mc[r][None,:])%P)%P
        piv.append(int(nzc[ci])); r+=1
    E=np.zeros((r,n),dtype=np.int64); E[:,nzc]=Mc[:r]
    return E,piv
def solve(Aeq,b):
    """solve Aeq x = b mod P (Aeq m x U).  -> x (U,) or None.  Basic solution (free vars 0)."""
    m,U=Aeq.shape; Mx=np.concatenate([Aeq%P,(b%P).reshape(-1,1)],axis=1)
    E,piv=rref(Mx)
    if U in piv: return None
    x=np.zeros(U,dtype=np.int64)
    for i,c in enumerate(piv): x[c]=E[i,U]
    return x
def ratrec(a,bound=1<<14):
    """rational reconstruction of a mod P with |num|,den <= bound -> Fraction or None"""
    from fractions import Fraction
    a=int(a)%P
    r0,r1=P,a; s0,s1=0,1
    while r1>bound:
        q=r0//r1; r0,r1=r1,r0-q*r1; s0,s1=s1,s0-q*s1
    if s1==0 or abs(s1)>bound: return None
    fr=Fraction(r1,s1)
    if (fr.numerator%P*pow(fr.denominator%P,P-2,P))%P!=a: return None
    return fr

def zmask(w):
    """registers (X or helper) whose FINAL frame is the 9-dim frame: at the end of the program their rows are unit rows e_b, and they share that frame
    with every row ending there -> insertion 'a += c b' at the end absorbs coordinate b of row a.  returns (Z list, 0/1 mask over symbols keeping NON-Z coords, dims)"""
    n=len(w['initial']); R=nreg(w); dimf=[len(b) for b in w['frames']]; live=set(w['live'])
    Z=[b for b in range(n) if dimf[w['final'][b]]==9 and not (b-112 in live)]
    m=np.ones(R,dtype=np.int64); m[Z]=0
    return Z,m,dimf
def _dedupe(B):
    seen={}
    for v in B:
        k=v.tobytes()
        if k not in seen and v.any(): seen[k]=v
    return np.array(list(seen.values())) if seen else []
_QC={}
_RNG=np.random.default_rng(12345)
def compress(B):
    """span-preserving (w.h.p.) compression of many rows: m = #nonzero cols + 8 random combinations with 20-bit coefficients (exact int64, chunked)"""
    B=np.asarray(B)%P; k=B.shape[0]; nzc=np.nonzero(B.any(0))[0]; m=len(nzc)+8
    if k<=m: return B
    Bc=B[:,nzc]; out=np.zeros((m,len(nzc)),dtype=np.int64)
    for i in range(0,k,2048):
        G=_RNG.integers(0,1<<20,size=(m,min(2048,k-i)),dtype=np.int64)
        out=(out+(G@Bc[i:i+2048])%P)%P
    full=np.zeros((m,B.shape[1]),dtype=np.int64); full[:,nzc]=out; return full
def quotient(B,v_list):
    """reduce vectors modulo span(B) (rows); returns reduced vectors (numpy)"""
    if len(B)==0: return [v%P for v in v_list]
    E,piv=rref(np.array(B))
    out=[]
    for v in v_list:
        v=v%P
        for i,c in enumerate(piv):
            if v[c]: v=(v-v[c]*E[i])%P
        out.append(v)
    return out
def joint(w,prog,h,f,maxslots=12,extra_dests=()):
    """quotient solve: unknown x = insertions INTO h (all slots at f); every other affected row a absorbs its residual with PURE insertions
    (slots after a's last read in prog').  returns dict(ok, x, rows, info)"""
    T=target(w); R=nreg(w); A2,_=replay(w,prog); D=(T-A2)%P
    Cx=[c for c in candidates(w,prog,[h],maxslots=50) if c[3]==f]
    phx=phi_cols(w,prog,[(t,a) for a,b,t,g in Cx]); rsx=row_snaps(w,prog,[(t,b) for a,b,t,g in Cx])
    rows=set(int(r) for r in np.nonzero(D.any(1))[0])|{h}|set(extra_dests)
    for c in Cx: rows|=set(int(r) for r in np.nonzero(phx[(c[2],c[0])])[0])
    rows=sorted(rows)
    Cp=candidates(w,prog,[r for r in rows if r!=h],maxslots=maxslots)
    php=phi_cols(w,prog,[(t,a) for a,b,t,g in Cp])
    pure=[c for c in Cp if php[(c[2],c[0])][c[0]]==1 and np.count_nonzero(php[(c[2],c[0])])==1]
    rsp=row_snaps(w,prog,[(t,b) for a,b,t,g in pure])
    Bp=collections.defaultdict(list)
    for a,b,t,g in pure: Bp[a].append(rsp[(t,b)])
    # x pure for h itself too: slots after h's last read
    eqs=[]; rhs=[]
    for a in rows:
        B=[v for v in Bp.get(a,[])] if a!=h else []
        cols=[D[a]]+[phx[(c[2],c[0])][a]*rsx[(c[2],c[1])]%P for c in Cx]
        red=quotient(np.unique(np.array(B),axis=0) if B else [],cols)
        eqs.append(np.array(red[1:]).T if Cx else np.zeros((R,0),dtype=np.int64)); rhs.append(red[0])
    Aeq=np.concatenate(eqs,axis=0); b=np.concatenate(rhs)
    keep=np.nonzero(Aeq.any(1)|(b!=0))[0]; Aeq=Aeq[keep]; b=b[keep]
    if len(b)==0: return dict(ok=True,x=[],nx=len(Cx),rows=rows,neq=0)
    x=solve(Aeq,b) if Aeq.shape[1] else None
    return dict(ok=x is not None,x=None if x is None else [(Cx[i],int(x[i])) for i in np.nonzero(x)[0]],nx=len(Cx),rows=rows,neq=len(b),
                rank_info=(Aeq.shape))

def kill_stop(w,r,j,mode='late'):
    """register r, timeline index j (0 = initial frame; middle stops only): delete the stop.  mode 'late': r stays at prev frame until the MOVE out of g,
    then jumps prev->next;  'early': jumps prev->next at the MOVE into g.  events of r at g are dropped.  -> (prog', dropped, info) or None"""
    tl=timelines(w)[r]
    if not (1<=j<len(tl)-1): return None
    p=tl[j-1][2]; g=tl[j][2]; nx=tl[j+1][2]; tin=tl[j][0]; tout=tl[j][1]
    prog=w['program']; out=[]; dropped=[]
    for t,e in enumerate(prog):
        if t==tin: 
            if mode=='early': out.append(['MOVE',r,p,nx,e[4]])
            continue
        if t==tout:
            if mode=='late': out.append(['MOVE',r,p,nx,e[4]])
            continue
        if tin<t<tout and ((e[0] in('ADD','COPY') and r in(e[1],e[2])) or (e[0]=='SCALE' and e[1]==r)):
            dropped.append((t,e)); continue
        out.append(e)
    return out,dropped,dict(p=p,g=g,nx=nx,tin=tin,tout=tout)
def joint2(w,prog,xdests,maxslots_x=8,maxslots=4,frames_x=None,win=None,xcap=3000):
    """generalised quotient solve: unknown x = ALL insertions into registers xdests (optionally restricted to frames_x / time window win=(lo,hi));
    every other affected row absorbs its residual with PURE insertions.  Effects deduped.  returns dict(ok, x, ...)"""
    T=target(w); R=nreg(w); A2,_=replay(w,prog); D=(T-A2)%P
    Cx=candidates(w,prog,list(xdests),maxslots=maxslots_x)
    if frames_x is not None: Cx=[c for c in Cx if c[3] in frames_x]
    if win is not None: Cx=[c for c in Cx if win[0]<=c[2]<=win[1]]
    if len(Cx)>xcap: return dict(ok=None,err='xcap %d'%len(Cx),nx=len(Cx))
    phx=phi_cols(w,prog,[(t,a) for a,b,t,g in Cx]); rsx=row_snaps(w,prog,[(t,b) for a,b,t,g in Cx])
    # dedupe x effects
    seen={}; Cu=[]
    for c in Cx:
        k=(phx[(c[2],c[0])].tobytes(),rsx[(c[2],c[1])].tobytes())
        if k in seen: continue
        seen[k]=1; Cu.append(c)
    Cx=Cu
    rows=set(int(x) for x in np.nonzero(D.any(1))[0])|set(xdests)
    for c in Cx: rows|=set(int(x) for x in np.nonzero(phx[(c[2],c[0])])[0])
    rows=sorted(rows)
    Cp=candidates(w,prog,rows,maxslots=maxslots)
    php=phi_cols(w,prog,[(t,a) for a,b,t,g in Cp])
    pure=[c for c in Cp if php[(c[2],c[0])][c[0]]==1 and np.count_nonzero(php[(c[2],c[0])])==1]
    rsp=row_snaps(w,prog,[(t,b) for a,b,t,g in pure])
    Bp=collections.defaultdict(list)
    for a,b,t,g in pure: Bp[a].append(rsp[(t,b)])
    Z,Zm,dimf=zmask(w)
    eqs=[]; rhs=[]; nd=0; RL=[]
    for a in rows:
        coef=[phx[(c[2],c[0])][a] for c in Cx]
        if not D[a].any() and not any(coef): continue
        cols=[D[a]]+[cf*rsx[(c[2],c[1])]%P for cf,c in zip(coef,Cx)]
        if Z is not None and dimf[w['final'][a]]==9 and a<len(w['initial']):
            # end-of-program slots: every register ending at the full frame holds exactly its unit row, so those coordinates are free (EXACT)
            B=[v*Zm for v in Bp.get(a,[])]; cols=[v*Zm for v in cols]
        else: B=Bp.get(a,[])
        red=quotient(_dedupe(B),cols)
        if red[0].any(): nd+=1; RL.append((a,int(np.count_nonzero(red[0])),sum(1 for v in red[1:] if v.any()),np.nonzero(red[0])[0]))
        eqs.append(np.array(red[1:]).T if Cx else np.zeros((R,0),dtype=np.int64)); rhs.append(red[0])
    Aeq=np.concatenate(eqs,axis=0); b=np.concatenate(rhs)
    keep=np.nonzero(Aeq.any(1)|(b!=0))[0]; Aeq=Aeq[keep]; b=b[keep]
    info=dict(nx=len(Cx),rows=len(rows),neq=len(b),resid_rows=nd,resid_list=RL)
    if not b.any(): return dict(ok=True,x=[],**info)
    if Aeq.shape[1]==0: return dict(ok=False,x=None,**info)
    x=solve(Aeq,b)
    return dict(ok=x is not None,x=None if x is None else [(Cx[i],int(x[i])) for i in np.nonzero(x)[0]],**info)

# ------------------------------------------------------------------ realisation (exact: apply, re-replay, verify with legal.check)
def fstr(fr):
    return str(fr.numerator) if fr.denominator==1 else '%d/%d'%(fr.numerator,fr.denominator)
def dyadic(fr): return fr is not None and fr!=0 and (fr.denominator&(fr.denominator-1))==0 and abs(fr)+1<2**16
def insert(prog,ins):
    """ins: list of (t, event) meaning 'insert before original index t' (stable for equal t in list order)"""
    by=collections.defaultdict(list)
    for t,e in ins: by[t].append(e)
    out=[]
    for t,e in enumerate(prog):
        out+=by.get(t,[]); out.append(e)
    out+=by.get(len(prog),[])
    return out
def absorb_pure1(w,prog,maxslots=12,rows=None):
    """after x is applied: every defect row a gets pure insertions (slots after a's last read) solving D[a] in span; returns (prog', n_ins) or (None, failing rows)"""
    T=target(w); A2,_=replay(w,prog); D=(T-A2)%P
    rows=[int(r) for r in np.nonzero(D.any(1))[0]] if rows is None else rows
    if not rows: return prog,0
    Cp=candidates(w,prog,rows,maxslots=maxslots)
    php=phi_cols(w,prog,[(t,a) for a,b,t,g in Cp])
    pure=[c for c in Cp if php[(c[2],c[0])][c[0]]==1 and np.count_nonzero(php[(c[2],c[0])])==1]
    # a pure insertion's source b must not itself receive pure insertions BEFORE this slot: use slots of b before b's own insertions -> handled by
    # inserting all row fixes at their slots and re-verifying; failures are reported
    rsp=row_snaps(w,prog,[(t,b) for a,b,t,g in pure])
    ins=[]; bad=[]
    for a in rows:
        C=[c for c in pure if c[0]==a]
        if not C: bad.append(a); continue
        M=np.array([rsp[(c[2],c[1])] for c in C]); cols=np.nonzero(M.any(0)|(D[a]!=0))[0]
        x=solve(M[:,cols].T,D[a][cols])
        if x is None: bad.append(a); continue
        for i in np.nonzero(x)[0]:
            fr=ratrec(x[i])
            if not dyadic(fr): bad.append((a,'nondyadic',int(x[i]))); break
            c=C[i]; ins.append((c[2],['ADD',a,c[1],fstr(fr),c[3]]))
    if bad: return None,bad
    return insert(prog,ins),len(ins)

def variant(w,r,j,kind):
    """-> (w' (shallow copy with program/initial/final replaced), dropped, info) for deleting stop j of register r.
    kind: 'late'/'early' (middle stop), 'end' (helper's LAST stop j=len-1 removed: final = previous frame), 'birth' (helper's FIRST stop j=0 removed: initial = next frame)"""
    tl=timelines(w)[r]; prog=w['program']; n=len(w['initial'])
    w2=dict(w); w2['initial']=list(w['initial']); w2['final']=list(w['final'])
    if kind in('late','early'):
        res=kill_stop(w,r,j,kind)
        if res is None: return None
        p2,dr,inf=res; w2['program']=p2; return w2,dr,inf
    if kind=='end':
        if j!=len(tl)-1 or j<1: return None
        f=tl[j-1][2]; p2,tlv,dr=end_at(w,r,f); w2['program']=p2; w2['final'][r]=f
        return w2,dr,dict(p=f,g=tl[j][2],nx=f,tin=tl[j][0],tout=len(prog))
    if kind=='birth':
        if j!=0 or len(tl)<3: return None
        t1=tl[1][0]; f1=tl[1][2]; out=[]; dr=[]
        for t,e in enumerate(prog):
            if t==t1: continue
            if t<t1 and ((e[0] in('ADD','COPY') and r in(e[1],e[2])) or (e[0]=='SCALE' and e[1]==r)): dr.append((t,e)); continue
            out.append(e)
        w2['program']=out; w2['initial'][r]=f1
        return w2,dr,dict(p=f1,g=tl[0][2],nx=f1,tin=0,tout=t1)
    return None
def try_kill(w,r,j,kind,win=1500,realise=True):
    v=variant(w,r,j,kind)
    if v is None: return dict(ok=None)
    w2,dr,inf=v; prog=w2['program']
    xd=[r]+sorted({e[1] for t,e in dr if e[0] in('ADD','COPY') and e[1]!=r})
    J=joint2(w2,prog,xd,frames_x={inf['p'],inf['nx'],inf['g']},win=(inf['tin']-win,inf['tout']+win))
    J['ndrop']=len(dr); J['info']=inf
    if not J['ok'] or not realise: return J
    ins=[]
    for c,v in J['x']:
        fr=ratrec(v)
        if not dyadic(fr): J['real']='nondyadic x'; return J
        ins.append((c[2],['ADD',c[0],c[1],fstr(fr),c[3]]))
    p2=insert(prog,ins); p3,nb=absorb_pure(w2,p2)
    if p3 is None: J['real']='absorb fail %s'%(nb[:5],); return J
    w3=dict(w2); w3['program']=p3; S.C.activate(w3); rep=S.C.legal.check(w3)
    J['real']='legal' if rep['ok'] else 'ILLEGAL %s'%(rep['violations'][:2],); J['word']=w3 if rep['ok'] else None
    if rep['ok']:
        T_,P_=S.C.X.invoice(rep); J['kappa']=S.C.X.kappa(T_,P_); J['events']=len(p3)
    return J

def joint3(w,prog,specs,maxslots_x=8,maxslots=4,xcap=4000,need=None,exact=False):
    """like joint2 but x candidates given per destination: specs = list of (a, set_of_frames or None, (lo,hi) or None[, symbol index array]);
    a 4th spec field keeps only sources whose row (at the slot) touches those symbols"""
    T=target(w); R=nreg(w); A2,_=replay(w,prog); D=(T-A2)%P
    Cx=[]
    allc=candidates(w,prog,sorted({s[0] for s in specs}),maxslots=maxslots_x)
    tag={}
    for c in allc:
        for sp in specs:
            a,fs,win=sp[:3]
            if c[0]==a and (fs is None or c[3] in fs) and (win is None or win[0]<=c[2]<=win[1]): Cx.append(c); tag[c]=sp[3] if len(sp)>3 else None; break
    if len(Cx)>6*xcap: return dict(ok=None,err='xcap0 %d'%len(Cx),nx=len(Cx))
    rsx=row_snaps(w,prog,[(t,b) for a,b,t,g in Cx])
    Cx=[c for c in Cx if tag[c] is None or rsx[(c[2],c[1])][tag[c]].any()]
    if exact: Cx,_=taint_ok(prog,Cx)
    if len(Cx)>xcap: return dict(ok=None,err='xcap %d'%len(Cx),nx=len(Cx))
    phx=phi_cols(w,prog,[(t,a) for a,b,t,g in Cx])
    seen={}; Cu=[]
    for c in Cx:
        k=(phx[(c[2],c[0])].tobytes(),rsx[(c[2],c[1])].tobytes())
        if k in seen or not rsx[(c[2],c[1])].any(): continue
        seen[k]=1; Cu.append(c)
    Cx=Cu
    if len(Cx)>xcap: return dict(ok=None,err='xcap %d'%len(Cx),nx=len(Cx))
    rows=set(int(x) for x in np.nonzero(D.any(1))[0])|{s[0] for s in specs}
    for c in Cx: rows|=set(int(x) for x in np.nonzero(phx[(c[2],c[0])])[0])
    rows=sorted(rows)
    Cp=candidates(w,prog,rows,maxslots=maxslots)
    php=phi_cols(w,prog,[(t,a) for a,b,t,g in Cp])
    pure=[c for c in Cp if php[(c[2],c[0])][c[0]]==1 and np.count_nonzero(php[(c[2],c[0])])==1]
    rsp=row_snaps(w,prog,[(t,b) for a,b,t,g in pure])
    Bp=collections.defaultdict(list)
    for a,b,t,g in pure: Bp[a].append(rsp[(t,b)])
    Z,Zm,dimf=zmask(w)
    eqs=[]; rhs=[]; nd=0; RL=[]
    for a in rows:
        coef=[phx[(c[2],c[0])][a] for c in Cx]
        if not D[a].any() and not any(coef): continue
        cols=[D[a]]+[cf*rsx[(c[2],c[1])]%P for cf,c in zip(coef,Cx)]
        if Z is not None and dimf[w['final'][a]]==9 and a<len(w['initial']):
            # end-of-program slots: every register ending at the full frame holds exactly its unit row, so those coordinates are free (EXACT)
            B=[v*Zm for v in Bp.get(a,[])]; cols=[v*Zm for v in cols]
        else: B=Bp.get(a,[])
        red=quotient(_dedupe(B),cols)
        if red[0].any(): nd+=1; RL.append((a,int(np.count_nonzero(red[0])),sum(1 for v in red[1:] if v.any()),np.nonzero(red[0])[0]))
        eqs.append(np.array(red[1:]).T if Cx else np.zeros((R,0),dtype=np.int64)); rhs.append(red[0])
    Aeq=np.concatenate(eqs,axis=0); b=np.concatenate(rhs)
    keep=np.nonzero(Aeq.any(1)|(b!=0))[0]; Aeq=Aeq[keep]; b=b[keep]
    info=dict(nx=len(Cx),rows=len(rows),neq=len(b),resid_rows=nd,resid_list=RL)
    if not b.any(): return dict(ok=True,x=[],**info)
    if Aeq.shape[1]==0: return dict(ok=False,x=None,**info)
    # cheap pre-test: drop columns, rank test via rref on [Aeq|b] restricted to nonzero cols
    x=solve(Aeq,b)
    return dict(ok=x is not None,x=None if x is None else [(Cx[i],int(x[i])) for i in np.nonzero(x)[0]],**info)
def helper_kill(w,r):
    """drop every event of helper r, chain -> one MOVE initial->final at its first MOVE time (tax 0)."""
    prog=w['program']; out=[]; dr=[]; first=True
    for t,e in enumerate(prog):
        if e[0]=='MOVE' and e[1]==r:
            if first: out.append(['MOVE',r,w['initial'][r],w['final'][r],e[4]]); first=False
            continue
        if (e[0] in('ADD','COPY') and r in(e[1],e[2])) or (e[0]=='SCALE' and e[1]==r): dr.append((t,e)); continue
        out.append(e)
    w2=dict(w); w2['program']=out; return w2,dr
def realise_x(w2,J):
    prog=w2['program']; ins=[]
    for c,v in J['x']:
        fr=ratrec(v)
        if not dyadic(fr): return None,'nondyadic x %s'%v
        ins.append((c[2],['ADD',c[0],c[1],fstr(fr),c[3]]))
    p2=insert(prog,ins); p3,nb=absorb_pure(w2,p2)
    if p3 is None: return None,'absorb fail %s'%(nb[:5],)
    w3=dict(w2); w3['program']=p3; S.C.activate(w3); rep=S.C.legal.check(w3)
    if not rep['ok']: return None,'ILLEGAL %s'%(rep['violations'][:2],)
    T_,P_=S.C.X.invoice(rep); return w3,S.C.X.kappa(T_,P_)

def try_kill2(w,r,j,kind,win=1500,yfree=True,realise=True):
    """try_kill + second round: rows still blocked that are Y mains (or early-ending helpers) become x destinations with ALL their slots."""
    J=try_kill(w,r,j,kind,win=win,realise=realise)
    if J.get('ok') is not False or not yfree: return J
    v=variant(w,r,j,kind); w2,dr,inf=v; prog=w2['program']; n=len(w['initial'])
    blk=[(a,sy) for a,nz,nxa,sy in J.get('resid_list',[]) if a<n and a!=r]
    if not blk or len(blk)>12: J['round2']='skip %d'%len(blk); return J
    specs=[(r,{inf['p'],inf['nx'],inf['g']},(inf['tin']-win,inf['tout']+win))]
    specs+=[(e[1],{inf['p'],inf['nx'],inf['g']},(inf['tin']-win,inf['tout']+win)) for t,e in dr if e[0] in('ADD','COPY') and e[1]!=r]
    dimf=[len(b) for b in w['frames']]
    specs+=[(a,{f for f in range(len(w['frames'])) if dimf[f]>0},None,sy) for a,sy in blk]
    J2=joint3(w2,prog,specs,maxslots_x=4)
    J2['round2']='blk %d'%len(blk); J2['ndrop']=len(dr); J2['info']=inf
    if J2.get('ok') and realise:
        w3,res=realise_x(w2,J2)
        J2['real']='legal' if w3 is not None else res
        if w3 is not None: J2['kappa']=res; J2['word']=w3; J2['events']=len(w3['program'])
    return J2

def rehost_prog(w,prog,s,js,F):
    """move register s's stop js (frame g) to frame F (caller checks nesting). events of s at g: relabelled to F if the partner is at F then, else dropped."""
    tl=timelines(w,prog)[s]; lo,hi,g=tl[js]
    fr=S.C.legal.spans(w)
    prv=tl[js-1][2] if js>0 else None; nxt=tl[js+1][2] if js+1<len(tl) else None
    if prv is not None and not fr[prv]<fr[F]: return None
    if nxt is not None and not fr[F]<fr[nxt]: return None
    n=len(w['initial']); cur=list(w['initial'])+[None]*(nreg(w)-n); out=[]; dropped=[]
    for t,e in enumerate(prog):
        o=e[0]
        if o=='MOVE':
            e=list(e)
            if e[1]==s and t==lo: e[3]=F
            if e[1]==s and t==hi: e[2]=F
            cur[e[1]]=e[3]; out.append(e); continue
        if o=='INIT': cur[e[1]]=e[2]; out.append(e); continue
        if o=='CLEAR': cur[e[1]]=None; out.append(e); continue
        if lo<t<hi and ((o in('ADD','COPY') and s in(e[1],e[2])) or (o=='SCALE' and e[1]==s)):
            if o=='SCALE': out.append(e[:-1]+[F]); continue
            other=e[2] if e[1]==s else e[1]
            if cur[other]==F: out.append(e[:-1]+[F])
            else: dropped.append((t,e))
            continue
        out.append(e)
    if js==0:   # initial frame
        return None
    return out,dropped,dict(g=g,F=F,lo=lo,hi=hi)
def try_combo(w,r,j,s,js,F,win=1500,realise=True,exact=True):
    """rehost partner s's stop js to frame F, then delete stop j of r ('late'); joint re-plan with x = r, s and all dropped partners near both windows."""
    rh=rehost_prog(w,w['program'],s,js,F)
    if rh is None: return dict(ok=None,err='nest')
    p1,dr1,i1=rh; w1=dict(w); w1['program']=p1
    v=variant(w1,r,j,'late')
    if v is None: return dict(ok=None,err='variant')
    w2,dr2,i2=v; prog=w2['program']
    specs=[(r,{i2['p'],i2['nx'],i2['g']},(i2['tin']-win,i2['tout']+win)),(s,{F,i1['g']},(i1['lo']-win,i1['hi']+win))]
    for t,e in dr1+dr2:
        if e[0] in('ADD','COPY'):
            for x in (e[1],e[2]):
                if x not in(r,s) and x<len(w['initial']): specs.append((x,{e[-1],F,i2['p'],i2['nx']},(t-win,t+win)))
    # intermediaries: registers sharing a frame with s or r inside the windows (they can relay the content to the dropped destinations)
    tl2,byf=frame_intervals(w2,prog)
    for (reg,fs,(lo,hi)) in [(s,{F},(i1['lo']-win,i1['hi']+win)),(r,{i2['p'],i2['nx']},(i2['tin']-win,i2['tout']+win))]:
        for f in fs:
            for q,qlo,qhi in byf[f]:
                if q in(r,s) or q>=len(w['initial']) or qhi<lo or qlo>hi or len(byf[f])>40: continue
                specs.append((q,{f},(lo,hi)))
    J=joint3(w2,prog,specs,maxslots_x=6,exact=exact)
    J['ndrop']=len(dr1)+len(dr2)
    if J.get('ok') and realise:
        w3,res=realise_x(w2,J)
        J['real']='legal' if w3 is not None else res
        if w3 is not None: J['kappa']=res; J['word']=w3; J['events']=len(w3['program'])
    return J

def apply_x(w2,J):
    ins=[]
    for c,v in J['x']:
        fr=ratrec(v)
        if not dyadic(fr): return None
        ins.append((c[2],['ADD',c[0],c[1],fstr(fr),c[3]]))
    w3=dict(w2); w3['program']=insert(w2['program'],ins); return w3
def newton(w2,specs,rounds=4,maxslots_x=6):
    """iterated linear re-plan (handles bilinear interactions between inserted events): solve, apply x, recompute, until only pure absorption is left."""
    cur=w2; hist=[]
    for k in range(rounds):
        J=joint3(cur,cur['program'],specs,maxslots_x=maxslots_x)
        hist.append((J.get('ok'),J.get('nx'),len(J.get('x') or [])))
        if not J.get('ok'): return None,dict(J,hist=hist)
        if not J['x']:
            p3,nb=absorb_pure(cur,cur['program'])
            if p3 is None: return None,dict(J,hist=hist,real='absorb fail %s'%(nb[:4],))
            w3=dict(cur); w3['program']=p3; S.C.activate(w3); rep=S.C.legal.check(w3)
            if rep['ok']:
                T_,P_=S.C.X.invoice(rep); return w3,dict(J,hist=hist,real='legal',kappa=S.C.X.kappa(T_,P_),events=len(p3))
            return None,dict(J,hist=hist,real='ILLEGAL %s'%(rep['violations'][:2],))
        nxt=apply_x(cur,J)
        if nxt is None: return None,dict(J,hist=hist,real='nondyadic')
        cur=nxt
    return None,dict(hist=hist,real='no convergence')

def absorb_pure(w,prog,maxslots=12,rows=None,rounds=6):
    """iterated pure absorption (a pure insertion's source may itself be fixed later; re-solve the remaining defect)"""
    tot=0
    for k in range(rounds):
        T=target(w); A2,_=replay(w,prog); D=(T-A2)%P
        if not D.any(): return prog,tot
        p2,n=absorb_pure1(w,prog,maxslots=maxslots)
        if p2 is None: return None,n
        prog=p2; tot+=n
    T=target(w); A2,_=replay(w,prog); D=(T-A2)%P
    return (prog,tot) if not D.any() else (None,['no convergence',[int(r) for r in np.nonzero(D.any(1))[0]][:6]])

def combo_specs(w,r,j,s,js,F,win=1500):
    rh=rehost_prog(w,w['program'],s,js,F)
    if rh is None: return None
    p1,dr1,i1=rh; w1=dict(w); w1['program']=p1
    v=variant(w1,r,j,'late')
    if v is None: return None
    w2,dr2,i2=v; prog=w2['program']; n=len(w['initial'])
    specs=[(r,{i2['p'],i2['nx'],i2['g']},(i2['tin']-win,i2['tout']+win)),(s,{F,i1['g']},(i1['lo']-win,i1['hi']+win))]
    for t,e in dr1+dr2:
        if e[0] in('ADD','COPY'):
            for x in (e[1],e[2]):
                if x not in(r,s) and x<n: specs.append((x,{e[-1],F,i2['p'],i2['nx']},(t-win,t+win)))
    tl2,byf=frame_intervals(w2,prog)
    for (reg,fs,(lo,hi)) in [(s,{F},(i1['lo']-win,i1['hi']+win)),(r,{i2['p'],i2['nx']},(i2['tin']-win,i2['tout']+win))]:
        for f in fs:
            for q,qlo,qhi in byf[f]:
                if q in(r,s) or q>=n or qhi<lo or qlo>hi or len(byf[f])>40: continue
                specs.append((q,{f},(lo,hi)))
    return w2,specs,len(dr1)+len(dr2)
