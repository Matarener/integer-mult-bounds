"""alias_core -- P14 ALIAS machinery (ALIAS; module docstring): anchor poset feasibility, edit/DCE, frame closure (hybrid|minimal), exact junk re-solve, relabel, greedy rounds."""
"""ALIAS lane library: timelines, full symbolic values, dup groups."""
import sys,os,collections,pickle,time
TK=__import__('os').path.dirname(__import__('os').path.abspath(__file__))
for p in (TK,TK+'/infra'): sys.path.insert(0,p)
from fractions import Fraction as F
import tkcommon, movekit as M
from ledger import load,lines
def loadw(spec):
    p,w=tkcommon.load(spec) if not os.path.exists(spec) else (spec,tkcommon.legal.load(spec))
    tkcommon.activate(w)
    return M.pin(w)
class Info:
    def __init__(s,w):
        s.w=w; s.role,s.mv,s.cred,s.dim=lines(w); s.n=len(w['initial']); s.v=M.View(w); s.sp=[frozenset(x) for x in s.v.spans]; s.S=s.v.S
        S=s.S; n=s.n
        # full values: val[r] = dict col->Fraction ; columns = initial register ids
        val=[None]*(n+64)
        for r in range(n): val[r]={r:F(1)}
        for r in range(n,n+64): val[r]={}
        s.reads=[]   # (i, d, src, coef, frame, content_full_of_src (copy))
        s.cont={}    # i -> (X-content tuple normalized, scale, junkpart dict) for dirty reads
        s.dirty=collections.defaultdict(list)
        role=s.role
        for i,e in enumerate(S):
            if e[0]=='ADD':
                d,t,c,f=e[1],e[2],F(e[3]),e[4]
                vs=val[t]
                if role.get(t)=='H' and 0<s.dim[f]<=9:
                    xs={k:x for k,x in vs.items() if role.get(k)!='H'}
                    if xs:
                        k0=min(xs); sc=xs[k0]
                        key=tuple(sorted((k,x/sc) for k,x in xs.items()))
                        s.dirty[key].append((i,d,t,c,f,sc))
                vd=val[d]
                for k,x in vs.items():
                    nx=vd.get(k,0)+c*x
                    if nx==0: vd.pop(k,None)
                    else: vd[k]=nx
            elif e[0]=='INIT': val[e[1]]={}
            elif e[0]=='CLEAR': val[e[1]]={}
        s.final=val

def span_join(a,b):
    """span of union of two subspaces (frozensets of ints)"""
    if a<=b: return b
    if b<=a: return a
    s=set(a)
    for x in b:
        if x not in s: s|={y^x for y in s}
    return frozenset(s)
class TL:
    """per-register timeline: sorted list of (event index, frame) over ADD events (dest and source), + initial/final"""
    def __init__(s,I):
        w=I.w; s.t=collections.defaultdict(list)
        for i,e in enumerate(I.S):
            if e[0]=='ADD': s.t[e[1]].append((i,e[4])); s.t[e[2]].append((i,e[4]))
            elif e[0] in('INIT','CLEAR'): s.t[e[1]].append((i,e[2]))
        s.idx={r:[x[0] for x in L] for r,L in s.t.items()}
        s.ini=w['initial']; s.fin=w['final']
    def around(s,r,tau):
        """(frame before tau, frame after tau) of register r for an event inserted at position tau (before current event tau)"""
        from bisect import bisect_left
        L=s.t.get(r,[]); ix=s.idx.get(r,[]); k=bisect_left(ix,tau)
        a=L[k-1][1] if k>0 else (s.ini[r] if r<len(s.ini) else None)
        b=L[k][1] if k<len(L) else (s.fin[r] if r<len(s.fin) else None)
        return a,b

class Poset:
    """vector clocks over anchors.  lower anchors: X initial lines, pinned frames of events with an owned register; upper anchors: Y final hyperplanes and the same owned frames.
    anc[e]: lower-anchor mask in the past of e; desc[e]: upper-anchor mask in its future.  allowed[a] = mask of upper anchors b with span(a) <= span(b)."""
    def __init__(s,I):
        S=I.S; role=I.role; n=I.n; w=I.w; own=I.v.own
        s.xs=sorted(w['live']); nx=len(s.xs)
        s.xi={r:k for k,r in enumerate(s.xs)}; s.yi={r+112:k for k,r in enumerate(s.xs)}
        ports=dict(zip(w['live'],w['ports']))
        lines=[frozenset([0,ports[r]]) for r in s.xs]
        hyp=[frozenset(x for x in range(512) if not bin(x&ports[r]).count('1')&1) for r in s.xs]
        of={}   # owned pinned frame id -> bit
        for e in S:
            if e[0] in('ADD','COPY') and (e[1] in own or e[2] in own): of.setdefault(e[-1],len(of))
            elif e[0]=='SCALE' and e[1] in own: of.setdefault(e[-1],len(of))
        s.obit=of
        spl=[I.sp[f] for f in of]
        s.lowspan=lines+spl      # lower bit k -> span ; owned bits at nx+k
        s.upspan=hyp+spl         # upper bit k -> span
        s.nx=nx
        # lower bits: X line k -> k ; owned o -> nx+o.  upper bits: Y k -> k ; owned o -> nx+o
        s.allowed=[0]*len(s.lowspan)
        for a,sa in enumerate(s.lowspan):
            m=0
            for b,sb in enumerate(s.upspan):
                if sa<=sb: m|=1<<b
            s.allowed[a]=m
        reg=[0]*(n+64)
        for r,k in s.xi.items(): reg[r]=1<<k
        s.anc=[0]*len(S)
        for i,e in enumerate(S):
            if e[0]=='ADD':
                d,t=e[1],e[2]; m=(reg[d] if d<n else 0)|(reg[t] if t<n else 0)
                if d in own or t in own: m|=1<<(nx+of[e[-1]])
                s.anc[i]=m
                if d<n: reg[d]=m
                if t<n: reg[t]=m
        s.ancfinal=reg
        reg=[0]*(n+64)
        for r,k in s.yi.items(): reg[r]=1<<k
        s.desc=[0]*len(S)
        for i in range(len(S)-1,-1,-1):
            e=S[i]
            if e[0]=='ADD':
                d,t=e[1],e[2]; m=(reg[d] if d<n else 0)|(reg[t] if t<n else 0)
                if d in own or t in own: m|=1<<(nx+of[e[-1]])
                s.desc[i]=m
                if d<n: reg[d]=m
                if t<n: reg[t]=m
        s.descini=reg
    def bad(s,anc,desc):
        a=anc
        while a:
            lb=a&-a; i=lb.bit_length()-1; a^=lb
            if desc & ~s.allowed[i]: return True
        return False

def windows(I):
    """win[key] -> [(h,i0,i1,scale)] intervals (S positions) during which helper h's X-content (up to scale) == key"""
    S=I.S; role=I.role; n=I.n
    val=[None]*(n+64)
    for r in range(n): val[r]={r:F(1)}
    for r in range(n,n+64): val[r]={}
    snap=collections.defaultdict(list)
    for i,e in enumerate(S):
        if e[0]!='ADD': continue
        d,t,c,f=e[1],e[2],F(e[3]),e[4]; vd=val[d]
        for k,x in val[t].items():
            nx=vd.get(k,0)+c*x
            if nx==0: vd.pop(k,None)
            else: vd[k]=nx
        if role.get(d)=='H':
            xs={k:x for k,x in vd.items() if role.get(k)!='H'}
            if xs:
                k0=min(xs); sc=xs[k0]; snap[d].append((i,(tuple(sorted((k,x/sc) for k,x in xs.items())),sc)))
            else: snap[d].append((i,None))
    win=collections.defaultdict(list)
    for h,L in snap.items():
        for a in range(len(L)):
            i0,kk=L[a]; i1=L[a+1][0] if a+1<len(L) else len(S)
            if kk: win[kk[0]].append((h,i0,i1,kk[1]))
    return win
def movable(I,T,d2,tau):
    """d2's events before position tau that may be moved after the new read: dim>0 ADDs with d2 as DEST after d2's last source-use/dim0/INIT event.  -> (indices ascending, last non-movable index or -1)"""
    S=I.S; L=[j for (j,fr) in T.t[d2] if j<tau]
    mv=[]
    for j in reversed(L):
        e=S[j]
        ok=e[0]=='ADD' and e[1]==d2 and I.dim[e[4]]>0 and e[2]!=d2
        if ok:
            src=e[2]
            if any(jj>j and jj<tau and S[jj][0]=='ADD' and S[jj][1]==src for (jj,_) in T.t.get(src,[])): ok=False
        if ok: mv.append(j)
        else: return mv[::-1],j
    return mv[::-1],-1
def feas(I,P,T,win,recut):
    """per dirty read (i2,d2,h2): set of keepers h1 feasible at the anchor level.  recut: reader's past ignored (new read first in its chain)"""
    from bisect import bisect_left
    S=I.S
    def anc_at(r,tau):
        ix=T.idx.get(r,[]); k=bisect_left(ix,tau); return P.anc[ix[k-1]] if k>0 else ((1<<P.xi[r]) if r in P.xi else 0)
    def desc_at(r,tau):
        ix=T.idx.get(r,[]); k=bisect_left(ix,tau); return P.desc[ix[k]] if k<len(ix) else ((1<<P.yi[r]) if r in P.yi else 0)
    out={}
    for key,L in I.dirty.items():
        if len({x[2] for x in L})<2: continue
        for (i2,d2,h2,a2,f2,sc2) in L:
            ok=set()
            for (h1,i0,i1,sc1) in win[key]:
                if h1==h2 or h1==d2: continue
                for tau in {i0+1}|{j+1 for (j,fr) in T.t[h1] if i0<j<i1}:
                    ob=(1<<(P.nx+P.obit[f2])) if d2 in I.v.own else 0
                    if recut:
                        lo,hi=min(tau,i2),max(tau,i2)
                        if any(lo<=j<=hi and S[j][0]=='ADD' and S[j][2]==d2 for (j,_) in T.t[d2]): continue
                        mv,nm=movable(I,T,d2,tau)
                        if i2<tau and i2 not in mv: pass
                        pa=P.anc[nm] if nm>=0 else ((1<<P.xi[d2]) if d2 in P.xi else 0)
                        fd=desc_at(d2,(mv[0] if mv else tau)) | (desc_at(d2,tau))
                        if i2>=tau or i2 in mv: pass
                        good=not P.bad(anc_at(h1,tau)|pa|ob,fd|desc_at(h1,tau)|ob)
                        if good: ok.add((h1,tau,sc1,tuple(mv))); break
                        continue
                    else:
                        lo,hi=min(tau,i2),max(tau,i2)
                        if any(lo<=j<=hi and S[j][0]=='ADD' and S[j][2]==d2 for (j,_) in T.t[d2]): continue
                        t2=tau if tau<=i2 else tau-1
                        good=not P.bad(anc_at(h1,tau)|anc_at(d2,tau)|ob,desc_at(h1,tau)|desc_at(d2,tau)|ob)
                    if good: ok.add((h1,tau,sc1)); break
            out[(h2,i2)]=ok
    return out
def victims(I,F):
    nread=collections.Counter()
    for key,L in I.dirty.items():
        for x in L: nread[x[2]]+=1
    got=collections.Counter(h for (h,i),ok in F.items() if ok)
    return [h for h in nread if got[h]==nread[h]], len(nread)

def simulate(S,n,nreg):
    """exact final matrix rows (dict col->Fraction) of the scalar program S (public registers 0..n-1; owned n..)"""
    val=[None]*nreg
    for r in range(n): val[r]={r:F(1)}
    for r in range(n,nreg): val[r]={}
    for e in S:
        op=e[0]
        if op=='ADD':
            d,t,c=e[1],e[2],F(e[3]); vd=val[d]
            for k,x in val[t].items():
                nx=vd.get(k,0)+c*x
                if nx==0: vd.pop(k,None)
                else: vd[k]=nx
        elif op=='COPY':
            c=F(e[3]); val[e[1]]={k:c*x for k,x in val[e[2]].items()}
        elif op=='SCALE':
            c=F(e[2]); val[e[1]]={k:c*x for k,x in val[e[1]].items()}
        elif op in('INIT','CLEAR'): val[e[1]]={}
    return val
def target(w):
    n=len(w['initial']); live=set(w['live']); T=[]
    for r in range(n):
        row={r:F(1)}
        if r-112 in live: row[r-112]=F(1)
        T.append(row)
    return T

# ---- p14
"""P14 ALIAS: redirect all dirty reads of a victim helper to an equal-content keeper helper (anchor-level feasibility), realise frames by forward closure,
solve the junk with start loads, relabel registers, price exactly."""
import sys,os,collections,copy,time
Fr=F
from movekit import qs
def basis_of(s):
    b=[];sp={0}
    for v in sorted(s):
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
class Ctx:
    def __init__(s,w):
        s.w=w; s.I=Info(w); s.P=Poset(s.I); s.T=TL(s.I); s.win=windows(s.I); s.n=s.I.n
        s.nown=w.get('owned_fields',8)
        s.k0=M.evaluate(w)['kappa']
        s.rd={}
        for key,L in s.I.dirty.items():
            for (i,d,t,c,f,sc) in L: s.rd[(t,i)]=(key,d,Fr(c),f,sc)
    def feas(s,recut=False): return feas(s.I,s.P,s.T,s.win,recut)
def dce(S,role,n,protect=()):
    """drop helpers with no reader (as source of another register); returns S',removed set"""
    removed=set()
    while True:
        rd=collections.Counter()
        for e in S:
            if e[0]=='ADD' and e[2]!=e[1]: rd[e[2]]+=1
        dead={e[1] for e in S if e[0]=='ADD' and e[1]<n and role.get(e[1])=='H' and rd[e[1]]==0 and e[1] not in protect}
        # helpers that appear only as dest are dead
        if not dead: break
        S=[e for e in S if not(e[1] in dead or (e[0] in('ADD','COPY') and e[2] in dead))]; removed|=dead
    return S,removed
def edit(C,victims,choice,do_dce=True):
    """returns (S2, removed helper set)"""
    I=C.I; S=I.S; role=I.role; n=I.n; vs=set(victims)
    ins=collections.defaultdict(list)
    moved=set()
    for (h2,i2),x in choice.items():
        h1,tau,sc1=x[:3]; mv=x[3] if len(x)>3 else ()
        key,d2,a2,f2,sc2=C.rd[(h2,i2)]
        ins[tau].append(['ADD',d2,h1,qs(a2*sc2/sc1),f2])
        for j in mv:
            if j in moved: continue
            if S[j][2] in vs or S[j][1] in vs: continue
            moved.add(j); ins[tau].append(list(S[j]))
    out=[]
    for i,e in enumerate(S):
        for ne in ins.get(i,()): out.append(ne)
        if i in moved: continue
        if e[1] in vs or (e[0] in('ADD','COPY') and e[2] in vs): continue
        out.append(list(e))
    for ne in ins.get(len(S),()): out.append(ne)
    removed=set(vs)
    if do_dce:
        out,r2=dce(out,role,n); removed|=r2
    return out,removed
def upper_frames(C,S2,removed):
    """U[e]: meet of the frames of all upper anchors (Y final hyperplanes, owned-pinned events) in the future of event e of S2 (backward pass over non-owned register chains)"""
    I=C.I; w=C.w; n=I.n; sp=I.sp; own=I.v.own; full=frozenset(range(512))
    U={}
    for r in I.role:
        if I.role[r]=='Y': U[r]=sp[w['final'][r]]
    out=[None]*len(S2)
    for i in range(len(S2)-1,-1,-1):
        e=S2[i]
        if e[0] not in('ADD','COPY','SCALE'): out[i]=full; continue
        regs=[e[1]]+([e[2]] if e[0] in('ADD','COPY') else [])
        m=full
        for r in regs:
            if r<n and r not in own: m=m&U.get(r,full)
        if any(r in own for r in regs): m=m&sp[e[-1]]
        out[i]=m
        for r in regs:
            if r<n and r not in own and m is not full: U[r]=m
    return out
def closure(C,S2,removed,minimal=False):
    """forward closure of frames: each event frame := join(own, cur[d], cur[s]); returns S3 frames as spans list per event, final spans, or None"""
    I=C.I; w=C.w; n=I.n; sp=I.sp; own=I.v.own
    zero=sp[0] if len(sp[0])==1 else frozenset([0])
    zero=[x for x in sp if len(x)==1][0]
    hybrid=(minimal=='hybrid'); minimal=bool(minimal) and not hybrid
    Uf=upper_frames(C,S2,removed) if hybrid else None
    cur={r:(sp[w['initial'][r]] if (not minimal or I.role[r]!='H') else zero) for r in range(n) if r not in removed}
    first={}
    ei=-1
    spans=[]; S3=[]
    for e in S2:
        ei+=1
        op=e[0]
        if op in('INIT',): cur[e[1]]=sp[e[2]]; spans.append(sp[e[2]]); continue
        if op=='CLEAR': spans.append(sp[e[2]]); cur.pop(e[1],None); continue
        fr=sp[e[-1]]
        regs=[e[1]]+([e[2]] if op in('ADD','COPY') else [])
        if any(r in own for r in regs):
            spans.append(fr); 
            for r in regs:
                if r not in own: 
                    if not cur[r]<=fr: return 'owned-event frame %d dim %d'%(r,len(fr))
                    cur[r]=fr
            continue
        nf=zero if minimal else (fr&Uf[ei] if hybrid else fr)
        for r in regs: nf=span_join(nf,cur[r])
        for r in regs: first.setdefault(r,nf)
        for r in regs: cur[r]=nf
        spans.append(nf)
    fin={}
    for r in range(n):
        if r in removed: continue
        f=sp[w['final'][r]] if not (minimal and I.role[r]=='H') else cur[r]
        if not cur[r]<=f:
            if I.role[r]=='Y': return 'Y final %d'%r
            f=span_join(f,cur[r])
        fin[r]=f
    ini={r:(first.get(r,cur[r]) if (minimal and I.role[r]=='H') else sp[w['initial'][r]]) for r in range(n) if r not in removed}
    return spans,fin,ini
def relabel(C,removed):
    n=C.n; nn=n-len(removed)
    surv=[r for r in range(n) if r not in removed]
    mp={}
    free=[r for r in sorted(removed) if r<nn]
    movers=[r for r in surv if r>=nn]
    assert len(free)==len(movers)
    for r in surv:
        if r<nn: mp[r]=r
    for a,b in zip(movers,free): mp[a]=b
    for k in range(C.nown+8): mp[n+k]=nn+k
    return mp,nn
def realise(C,victims,choice,do_dce=True,junk=True,log=None,minimal=False,reframe=None):
    """minimal: False/'hybrid'/True('minimal')/'best' (REALISEFIX: both completions, keep the higher exact kappa).  reframe: None or dict(tl=,K=,maxm=,threads=) -> afterwards frames.assign
    (exact CP-SAT frame re-assignment, never worse; heavy: only inside an hq job)."""
    if minimal=='best':
        import frames as FR
        cands=[(m,realise(C,victims,choice,do_dce,junk,log,m)) for m in ('hybrid',True)]
        ok=[(m,r[0]) for m,r in cands if r[0] is not None]
        if not ok: return cands[0][1]
        b=FR.best_closure(ok)
        w3=b[1] if b else ok[0][1]
        if reframe: w3,_=FR.assign(w3,**reframe)
        return w3,'ok'
    w3,why=_realise(C,victims,choice,do_dce,junk,log,minimal)
    if w3 is not None and reframe:
        import frames as FR
        w3,_=FR.assign(w3,**reframe)
    return w3,why
def _realise(C,victims,choice,do_dce=True,junk=True,log=None,minimal=False):
    I=C.I; w=C.w; n=I.n
    S2,removed=edit(C,victims,choice,do_dce)
    cl=closure(C,S2,removed,minimal)
    if isinstance(cl,str): return None,'closure:'+cl.split()[0]
    spans,fin,ini0=cl
    mp,nn=relabel(C,removed)
    frames=[list(b) for b in w['frames']]; fidx={x:i for i,x in enumerate(I.sp)}
    def fid(span):
        i=fidx.get(span)
        if i is None: frames.append(basis_of(span)); i=len(frames)-1; fidx[span]=i
        return i
    S3=[]
    for e,spn in zip(S2,spans):
        e=list(e); f=fid(spn)
        if e[0]=='INIT': e=['INIT',mp[e[1]],f]
        elif e[0]=='CLEAR': e=['CLEAR',mp[e[1]],f]
        elif e[0] in('ADD','COPY'): e=[e[0],mp[e[1]],mp[e[2]],e[3],f]
        else: e=[e[0],mp[e[1]]]+e[2:-1]+[f]
        S3.append(e)
    ini=[None]*nn; fn=[None]*nn
    for r in range(n):
        if r in removed: continue
        ini[mp[r]]=fid(ini0[r]); fn[mp[r]]=fid(fin[r])
    w2=dict(w); w2['frames']=frames; w2['initial']=ini; w2['final']=fn
    vp=dict(w.get('verifier_profile') or {}); vp['public']=nn; w2['verifier_profile']=vp
    w2['live']=[mp[r] for r in w['live']]
    assert w2['live']==w['live']
    if junk:
        r=solve_junk(w2,S3,nn)
        if isinstance(r,str): return None,'junk:'+r
        S3=r
    v2=M.View(w2); 
    w3=v2.rebuild_ref(S3)
    return w3,'ok'
def solve_junk(w2,S3,nn):
    nreg=nn+w2.get('owned_fields',8)+8
    V=simulate(S3,nn,nreg); T=target(w2)
    eps=[]  # list of (row, col, val)
    cols=collections.defaultdict(dict)
    for r in range(nn):
        d={}
        for k in set(V[r])|set(T[r]):
            x=T[r].get(k,0)-V[r].get(k,0)
            if x: d[k]=x
        if d: eps.append((r,d))
    if not eps: return S3
    live=set(w2['live']); role=lambda r:'X' if r in live else 'Y' if r-112 in live and r<nn else 'H'
    bcols=collections.defaultdict(dict)   # k -> {row: val}
    for r,d in eps:
        for k,x in d.items(): bcols[k][r]=x
    for k in bcols:
        if role(k)!='H' or len(w2['frames'][w2['initial'][k]])!=0: return 'col %d role %s inidim %d'%(k,role(k),len(w2['frames'][w2['initial'][k]]))
    # unknown x_{j,k}: sum_j x_j * V[r][j] = eps[r][k]   (columns of the CURRENT map V)
    Ys=[r for r in range(nn) if role(r)=='Y' or (role(r)=='H' and len(w2['frames'][w2['initial'][r]])==0)]
    colJ={j:{} for j in Ys}
    for r in range(nn):
        for j,x in V[r].items():
            if j in colJ: colJ[j][r]=x
    # gaussian elimination on rows r with matrix A[r][j]=V[r][j] (j in Ys); rhs per k
    rows=collections.defaultdict(dict)
    for j in Ys:
        for r,x in colJ[j].items(): rows[r][j]=x
    ks=list(bcols)
    # build augmented rows
    aug={}
    for r in rows|{r:None for r in set(r for k in bcols for r in bcols[k])}.keys() if False else set(rows)|{r for k in bcols for r in bcols[k]}:
        aug[r]=(dict(rows.get(r,{})),{k:bcols[k][r] for k in bcols if r in bcols[k]})
    piv={}
    sol_rows=[]
    for r,(A,B) in aug.items():
        A=dict(A); B=dict(B)
        # reduce by existing pivots
        changed=True
        while True:
            js=[j for j in A if j in piv]
            if not js: break
            j=js[0]; pa,pb=piv[j]; f=A[j]
            for jj,x in pa.items():
                nx=A.get(jj,0)-f*x
                if nx==0: A.pop(jj,None)
                else: A[jj]=nx
            for kk,x in pb.items():
                nx=B.get(kk,0)-f*x
                if nx==0: B.pop(kk,None)
                else: B[kk]=nx
        if not A:
            if B: return 'inconsistent'
            continue
        j=min(A); f=A[j]
        A={jj:x/f for jj,x in A.items()}; B={kk:x/f for kk,x in B.items()}
        # eliminate j from existing pivots
        for jj,(pa,pb) in list(piv.items()):
            if j in pa:
                g=pa[j]
                for a,x in A.items():
                    nx=pa.get(a,0)-g*x
                    if nx==0: pa.pop(a,None)
                    else: pa[a]=nx
                for kk,x in B.items():
                    nx=pb.get(kk,0)-g*x
                    if nx==0: pb.pop(kk,None)
                    else: pb[kk]=nx
        piv[j]=(A,B)
    # solution: free unknowns = 0 ; x_j for pivot j = B (rhs) ; x_{j,k}=piv[j][1][k]
    f0=None; loads=[]
    for j,(A,B) in piv.items():
        # pivot row: x_j + sum_free A * x_free = B  with free=0
        for k,x in B.items():
            loads.append(['ADD',j,k,qs(x),w2['initial'][j]])
    if any(w2['initial'][e[1]]!=w2['initial'][e[2]] for e in loads): return 'frame0 mismatch'
    return loads+S3

# ---- greedy
MODE=__import__('os').environ.get('FRAMES','hybrid')
RECUT=bool(int(__import__('os').environ.get('RECUT','0')))
def round_(w,batch,log):
    C=Ctx(w); F=C.feas(RECUT); v,nh=victims(C.I,F)
    byv=collections.defaultdict(dict)
    for (h,i),ok in F.items(): byv[h][i]=ok
    log('  victims',len(v),'k',C.k0)
    V=set(); K=set(); R=set(); sel=[]; ch={}
    for h in v:
        c=pick(byv,h); ks={x[0] for x in c.values()}; rs={C.rd[(h,i)][1] for i in c}
        if h in K or h in R or (ks&V) or (rs&V): continue
        cc={(h,i):x for i,x in c.items()}
        S2,removed=edit(C,sel+[h],{**ch,**cc})
        if isinstance(closure(C,S2,removed,MODE),str): continue
        sel.append(h); V.add(h); K|=ks; R|=rs; ch.update(cc)
        if len(sel)>=batch: break
    return C,sel,ch
def attempt(C,sel,ch,log):
    """realise; on failure bisect"""
    if not sel: return None,0
    cc={k:v for k,v in ch.items() if k[0] in set(sel)}
    w3,why=realise(C,sel,cc,minimal=MODE)
    if w3 is not None:
        o=M.evaluate(w3)
        if o.get('legal'): return w3,len(sel)
        why='illegal:'+str(o.get('why'))[:80]
    log('   fail',len(sel),why[:100])
    if len(sel)==1: return None,0
    m=len(sel)//2
    a,na=attempt(C,sel[:m],ch,log)
    return (a,na) if a is not None else attempt(C,sel[m:],ch,log)

def pick(byv,h):
    """for victim h: per reader slot choose one feasible (twin, ...) option, preferring a twin common to all slots (from ALIAS/greedy.py; was missing here -> pscreen 'alias' NameError)"""
    rs=byv[h]; common=None
    for i,ok in rs.items():
        ks={x[0] for x in ok}; common=ks if common is None else common&ks
    return {i:sorted(ok,key=lambda x:(x[0] not in (common or ()),x[1]))[0] for i,ok in rs.items()}
