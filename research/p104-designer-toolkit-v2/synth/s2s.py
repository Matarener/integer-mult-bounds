"""synth.s2s -- STATE-TO-STATE window synthesis (GENSPLICE; notes ../module docstring).

A window [t0,t1) of a word is re-synthesised so that every register ends the window in the SAME frame and with the SAME exact linear form as before (so the suffix, the
frame law, ownership, native pairs and kappa's MOVE ledger are untouched) while the events are rebuilt from the value-level requirement, not copied.
Windows can be cut anywhere: a node (register, epoch) starts at t0, at the event after its MOVE/INIT/CLEAR and ends at t1 or at its next MOVE/INIT/CLEAR.

LEVELS
  L1  meeting synthesis (this file, `resynth`): inside the window all ADD/SCALE events that touch the same set of mutated nodes at one frame form a MEETING (union-find over
      written nodes; read-only nodes are shared sources).  A meeting is a linear map M (rows = written nodes, columns = written + read-only nodes), obtained EXACTLY by running the
      meeting's own events on the node basis (no linear solve, nothing guessed).  M is re-factored: reader-before-read topological order, SCALE then ADDs for singleton strongly
      connected components, Gauss-Jordan (pivots +-2^k only) for cycles up to MAXSCC.  The new block replaces the meeting's events if it has fewer events (or `allow_equal`).
      Legal by construction (same frame, same nodes, nothing else touched) and kappa-neutral: MOVEs/frames are not touched; the saving is EVENTS (the binding cap, 26000) and scalar.
  L2  `Edit`s are plain `['splice', t0, t1, events]` so IncrWord.try_edit judges legality/kappa exactly; `repair_op` is the wsearch LNS operator.
Owned lifetimes are atomic in v1: meetings that write an owned register (INIT..CLEAR, COPY) are kept verbatim.
API
  state_at(word, t) -> (frames_cur, owned, forms)           exact Fraction forms over the input columns (the 'full register state' of a window boundary)
  analyze(prog, t0, t1, npub) -> meetings                   structure only
  resynth(word, t0, t1, allow_equal=False, stats=None) -> (edit, stats)   edit = ['splice', t0, t1, new_events] (None if nothing improves)
  apply(word, edit) -> word
CLI: python -m synth.s2s WORD [--t0 N --t1 N] [--windows SIZE:COUNT] [--out F]
"""
import sys,os,json,gzip,collections,time,copy
from fractions import Fraction as Q
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
sys.setrecursionlimit(20000)
MAXSCC=40
def qs(q): return str(q)
def dyadic(q): return q.denominator&(q.denominator-1)==0
def okcoef(q): return q!=0 and dyadic(q) and abs(q)+1<2**16
def okscale(q): return q!=0 and dyadic(q) and (abs(q.numerator)&(abs(q.numerator)-1))==0 and abs(q)+1<2**16
# ---------------------------------------------------------------------------------------------- exact state
def step(F,e):
    op=e[0]
    if op=='MOVE': return
    r=e[1]
    if op=='INIT' or op=='CLEAR': F[r]={}
    elif op=='SCALE': q=Q(e[2]); F[r]={c:v*q for c,v in F[r].items()}
    elif op=='COPY': q=Q(e[3]); F[r]={c:v*q for c,v in F[e[2]].items()}
    else:
        q=Q(e[3]); d=F[r]
        for c,v in F[e[2]].items():
            x=d.get(c,0)+q*v
            if x: d[c]=x
            else: d.pop(c,None)
def state_at(word,t,npub=None,nr=None):
    """full register state before event t: (cur frame per register, owned set, exact forms over the input columns (register ids), None frame = unborn owned)"""
    npub=npub or len(word['initial']); nr=nr or max(npub,(word.get('owned_fields') or 0)+npub)
    F=[{r:Q(1)} for r in range(npub)]+[{} for _ in range(nr-npub)]
    cur=list(word['initial'])+[None]*(nr-npub); owned=set()
    for e in word['program'][:t]:
        step(F,e)
        if e[0]=='MOVE': cur[e[1]]=e[3]
        elif e[0]=='INIT': cur[e[1]]=e[2]; owned.add(e[1])
        elif e[0]=='CLEAR': cur[e[1]]=None; owned.discard(e[1])
    return cur,owned,F
# ---------------------------------------------------------------------------------------------- structure
class Meeting:
    __slots__=('idx','W','R','lo','hi','frame','M','skip','orig','zero')
def analyze(prog,t0,t1,npub):
    """-> list of Meeting (one per union-find component of written nodes with >= 2 events), each with the insertion interval [lo,hi]"""
    ep=collections.defaultdict(int); start={}; end={}; zero=set()
    ev=[]                                              # (idx, kind, node_dst, node_src, frame)
    for i in range(t0,t1):
        e=prog[i]; op=e[0]; r=e[1]
        if op=='MOVE' or op=='INIT' or op=='CLEAR':
            n=(r,ep[r]); end[n]=i; ep[r]+=1; start[(r,ep[r])]=i+1
            if op!='MOVE': zero.add((r,ep[r]))                 # INIT/CLEAR: the new epoch starts with the ZERO form (owned register)
            continue
        if op=='SCALE': ev.append((i,'S',(r,ep[r]),None,e[3]))
        else: ev.append((i,op[0],(r,ep[r]),(e[2],ep[e[2]]),e[4]))       # 'A' ADD / 'C' COPY
    written={n for _,_,n,_,_ in ev}
    par={}
    def find(x):
        while par.setdefault(x,x)!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for _,k,nd,ns,f in ev:
        find(nd)
        if ns is not None and ns in written: par[find(nd)]=find(ns)
    comp=collections.defaultdict(list)
    for x in ev: comp[find(x[2])].append(x)
    out=[]
    for root,evs in comp.items():
        m=Meeting(); m.idx=[x[0] for x in evs]; m.skip=None; m.orig=len(evs)
        W=set(); R=set(); frames=set()
        for i,k,nd,ns,f in evs:
            W.add(nd); frames.add(f)
            if ns is not None and ns not in written: R.add(ns)
            if k=='C': m.skip='copy'
        m.zero=frozenset(n for n in W if n in zero)
        if len(frames)!=1: m.skip=m.skip or 'frames'
        m.frame=next(iter(frames)); m.W=sorted(W); m.R=sorted(R)
        nodes=W|R
        m.lo=max(start.get(n,t0) for n in nodes); m.hi=min(end.get(n,t1) for n in nodes)
        if m.lo>m.hi: m.skip=m.skip or 'interval'
        m.M=None; out.append(m)
    out.sort(key=lambda m:m.idx[0]); return out,ev
def matrix(prog,m,evbyidx):
    """exact linear map of a meeting: rows[node] = {node: Q} over written+read-only nodes, by running its events on the node basis"""
    rows={n:({} if n in m.zero else {n:Q(1)}) for n in m.W}
    for i in m.idx:
        _,k,nd,ns,f=evbyidx[i]; e=prog[i]
        if k=='S':
            q=Q(e[2]); rows[nd]={c:v*q for c,v in rows[nd].items()}
        else:
            q=Q(e[3]); src=rows.get(ns) or {ns:Q(1)}; d=rows[nd]
            for c,v in src.items():
                x=d.get(c,0)+q*v
                if x: d[c]=x
                else: d.pop(c,None)
    m.M=rows; return rows
# ---------------------------------------------------------------------------------------------- re-factoring of a map
def sccs(nodes,adj):
    index={};low={};st=[];on=set();res=[];c=[0]
    def go(v):
        index[v]=low[v]=c[0]; c[0]+=1; st.append(v); on.add(v)
        for w in adj[v]:
            if w not in index: go(w); low[v]=min(low[v],low[w])
            elif w in on: low[v]=min(low[v],index[w])
        if low[v]==index[v]:
            comp=[]
            while True:
                w=st.pop(); on.discard(w); comp.append(w)
                if w==v: break
            res.append(comp)
    for v in nodes:
        if v not in index: go(v)
    return res                                              # reverse topological order of the condensation (Tarjan): sinks first
def gauss_block(S,order):
    """ops ('A',i,j,q)/('S',i,q) that turn the identity into S (rows/cols = order); None if impossible with +-2^k pivots"""
    n=len(order); A=[[S[i].get(j,Q(0)) for j in order] for i in order]; ops=[]
    for c in range(n):
        if A[c][c]==0:
            p=next((r for r in range(c+1,n) if A[r][c]!=0),None)
            if p is None: return None
            ops.append(('A',c,p,Q(1)))
            for k in range(n): A[c][k]+=A[p][k]
        piv=A[c][c]
        if piv!=1:
            if not okscale(piv): return None
            ops.append(('S',c,1/piv))
            for k in range(n): A[c][k]=A[c][k]/piv
        for r in range(n):
            if r!=c and A[r][c]!=0:
                q=-A[r][c]; ops.append(('A',r,c,q))
                for k in range(n): A[r][k]+=q*A[c][k]
    for r in range(n):
        for k in range(n):
            if A[r][k]!=(1 if r==k else 0): return None
    # ops reduce S to I; S = inverse ops applied to I in reverse order
    inv=[]
    for o in reversed(ops):
        inv.append(('A',o[1],o[2],-o[3]) if o[0]=='A' else ('S',o[1],1/o[2]))
    return [(o[0],order[o[1]],order[o[2]],o[3]) if o[0]=='A' else ('S',order[o[1]],o[2]) for o in inv]
def lu_block(S,nodes):
    """sparse LU with symmetric Markowitz pivoting on +-2^k diagonal entries and row-add FIXUPS when no acceptable diagonal exists: ops ('A',i,j,q)/('S',i,q) that turn the identity into S
    (dict-of-dicts over `nodes`); None if stuck.  Reduction: red = row ops taking S to an upper-triangular U' (pivot order); realisation = build U' (ascending), then the inverse of red in reverse order.
    ops = nnz(U')+scales+|red|"""
    rows={i:dict(S[i]) for i in nodes}; cols={i:set() for i in nodes}
    for i in nodes:
        for j in rows[i]: cols[j].add(i)
    active=set(nodes); order=[]; U={}; red=[]
    def setrow(i,j,x):
        if x: rows[i][j]=x; cols[j].add(i)
        else:
            if j in rows[i]: del rows[i][j]
            cols[j].discard(i)
    while active:
        best=None
        for k in active:
            d=rows[k].get(k)
            if d is None or not okscale(d): continue
            c=(len(rows[k])-1)*(len(cols[k])-1)
            if best is None or c<best[0]:
                best=(c,k)
                if c==0: break
        if best is None:                                     # fixup: row_k += c row_i makes the diagonal of k acceptable
            fx=None
            for k in active:
                for i in cols[k]:
                    if i==k or i not in active: continue
                    for c in (Q(1),Q(-1),Q(2),Q(-2),Q(1,2),Q(-1,2)):
                        if okscale(rows[k].get(k,Q(0))+c*rows[i][k]):
                            key=len(rows[i])
                            if fx is None or key<fx[0]: fx=(key,k,i,c)
                            break
            if fx is None: return None
            _,k,i,c=fx
            for j,v in list(rows[i].items()): setrow(k,j,rows[k].get(j,Q(0))+c*v)
            red.append(('A',k,i,c))
            continue
        k=best[1]; pk=rows[k][k]; order.append(k); U[k]=dict(rows[k]); active.discard(k)
        for i in list(cols[k]):
            if i==k or i not in active: continue
            a=rows[i][k]; m=a/pk
            for j,v in rows[k].items(): setrow(i,j,rows[i].get(j,Q(0))-m*v)
            red.append(('A',i,k,-m))
        for j in rows[k]: cols[j].discard(k)
        cols[k]=set(); del rows[k]
    ops=[]
    for k in order:
        d=U[k][k]
        if d!=1: ops.append(('S',k,d))
        for j,v in U[k].items():
            if j!=k: ops.append(('A',k,j,v))
    for o in reversed(red): ops.append(('A',o[1],o[2],-o[3]))
    return ops
def lu_general(S,nodes,lam=3):
    """sparse elimination with GENERAL Markowitz pivots (i,j) (penalty lam for i!=j: a permutation costs ~3 ops per moved register): M = E^-1 U' P.
    ops: P (signed permutation of register contents, itself realised by lu_block), U' (triangular in pivot order), E^-1 (reverse elimination)"""
    rows={i:dict(S[i]) for i in nodes}; cols=collections.defaultdict(set)
    for i in nodes:
        for j in rows[i]: cols[j].add(i)
    active=set(nodes); piv=[]; red=[]
    while active:
        best=None
        for i in active:
            ri=len(rows[i])
            for j,v in rows[i].items():
                if not okscale(v): continue
                c=(ri-1)*(len(cols[j])-1)+(lam if i!=j else 0)
                if best is None or c<best[0]: best=(c,i,j)
            if best is not None and best[0]==0: break
        if best is None: return None
        _,i,j=best; pv=rows[i][j]; urow=dict(rows[i]); piv.append((i,j,pv,urow)); active.discard(i)
        for r in list(cols[j]):
            if r==i or r not in active: continue
            mlt=rows[r][j]/pv
            for jj,v in urow.items():
                x=rows[r].get(jj,Q(0))-mlt*v
                if x: rows[r][jj]=x; cols[jj].add(r)
                else:
                    rows[r].pop(jj,None); cols[jj].discard(r)
            red.append(('A',r,i,-mlt))
        for jj in urow: cols[jj].discard(i)
        cols[j]=set(); del rows[i]
    sigma={i:j for i,j,_,_ in piv}; inv={j:i for i,j in sigma.items()}
    ops=[]
    moved=[i for i in nodes if sigma[i]!=i]
    if moved:
        mv=set(moved); SP={i:{sigma[i]:Q(1)} for i in moved}
        o=lu_block(SP,sorted(moved))
        if o is None: return None
        ops+=o
    for i,j,pv,urow in piv:
        if pv!=1: ops.append(('S',i,pv))
        for jj,v in urow.items():
            if jj!=j: ops.append(('A',i,inv[jj],v))
    for o in reversed(red): ops.append(('A',o[1],o[2],-o[3]))
    return ops
def best_block(S,nodes):
    best=None
    for fn in (lambda: lu_block(S,nodes),lambda: lu_general(S,nodes,0),lambda: lu_general(S,nodes,3),lambda: lu_general(S,nodes,8)):
        try: o=fn()
        except RecursionError: o=None
        if o is not None and (best is None or len(o)<len(best)): best=o
    return best
def refactor(m):
    """new event list (reg-level, frame m.frame) realising m.M, or None"""
    M=m.M; W=m.W; Wset=set(W)
    adj={n:[j for j in M[n] if j!=n and j in Wset] for n in W}
    comps=sccs(W,adj)                                       # sinks first
    order=list(reversed(comps))                             # readers first
    ev=[]; f=m.frame
    for comp in order:
        if len(comp)==1:
            n=comp[0]; d=M[n].get(n,Q(0))
            if n in m.zero: d=Q(1)
            elif d==0: return None
            if d!=1:
                if not okscale(d): return None
                ev.append(['SCALE',n[0],qs(d),f])
            for j,q in sorted(M[n].items()):
                if j==n: continue
                if not okcoef(q): return None
                ev.append(['ADD',n[0],j[0],qs(q),f])
        else:
            cs=set(comp)
            S={i:{j:q for j,q in M[i].items() if j in cs} for i in comp}
            ops=best_block(S,sorted(comp))
            if ops is None and len(comp)<=MAXSCC: ops=gauss_block(S,sorted(comp))
            if ops is None: return None
            for o in ops:
                if o[0]=='A':
                    if not okcoef(o[3]): return None
                    ev.append(['ADD',o[1][0],o[2][0],qs(o[3]),f])
                else:
                    if not okscale(o[2]): return None
                    ev.append(['SCALE',o[1][0],qs(o[2]),f])
            for i in comp:
                for j,q in sorted(M[i].items()):
                    if j in comp: continue
                    if not okcoef(q): return None
                    ev.append(['ADD',i[0],j[0],qs(q),f])
    return ev
def selfcheck(m,new):
    """run the synthesised events on the node basis and compare with the meeting's exact map M (guards the factorisation itself)"""
    reg2node={n[0]:n for n in list(m.W)+list(m.R)}
    rows={n:({} if n in m.zero else {n:Q(1)}) for n in m.W}
    for e in new:
        d=reg2node[e[1]]
        if e[0]=='SCALE':
            q=Q(e[2]); rows[d]={c:v*q for c,v in rows[d].items()}
        else:
            q=Q(e[3]); s_=reg2node[e[2]]; src=rows.get(s_) or {s_:Q(1)}; r=rows[d]
            for c,v in src.items():
                x=r.get(c,0)+q*v
                if x: r[c]=x
                else: r.pop(c,None)
    return rows==m.M
def window_equal(word,edit):
    """independent exact check of an edit: frames, owned set and EVERY register's exact form at the window end are unchanged (replays the prefix twice with state_at)"""
    a,b=edit['ops'][0][1],edit['ops'][0][2]; w2=apply(word,edit); b2=b+len(edit['ops'][0][3])-(b-a)
    c1,o1,F1=state_at(word,b); c2,o2,F2=state_at(w2,b2)
    return c1==c2 and o1==o2 and F1==F2
# ---------------------------------------------------------------------------------------------- window synthesis
def resynth(word,t0=0,t1=None,allow_equal=False,min_events=2,stats=None,verify=True):
    """re-synthesise every meeting inside [t0,t1); -> (edit, stats).  edit = ['splice',t0,t1,events] or None when no meeting got cheaper."""
    prog=word['program']; npub=len(word['initial']); t1=len(prog) if t1 is None else t1
    st=stats if stats is not None else {}
    ms,ev=analyze(prog,t0,t1,npub); evb={x[0]:x for x in ev}
    remove=set(); ins=collections.defaultdict(list); saved=0; tried=0; why=collections.Counter()
    for m in ms:
        if m.orig<min_events: why['small']+=1; continue
        if m.skip: why[m.skip]+=1; continue
        tried+=1; matrix(prog,m,evb); new=refactor(m)
        if new is None: why['refactor_failed']+=1; continue
        if verify and not selfcheck(m,new): why['selfcheck_failed']+=1; continue
        if len(new)<m.orig or (allow_equal and len(new)==m.orig and new!=[prog[i] for i in m.idx]):
            remove.update(m.idx); ins[m.lo].extend(new); saved+=m.orig-len(new); why['accepted']+=1
        else: why['not_cheaper']+=1
    out=[]
    for i in range(t0,t1):
        if i in ins: out.extend(ins[i])
        if i not in remove: out.append(prog[i])
    if t1 in ins: out.extend(ins[t1])
    st.update(meetings=len(ms),tried=tried,saved=saved,why=dict(why),events_before=t1-t0,events_after=len(out))
    return ({'ops':[['splice',t0,t1,out]],'name':'s2s'} if saved or (allow_equal and remove) else None),st
def apply(word,edit):
    w=copy.copy(word); _,a,b,evs=edit['ops'][0]; w['program']=list(word['program'][:a])+[list(e) for e in evs]+list(word['program'][b:]); return w
# ---------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--t0',type=int,default=0); ap.add_argument('--t1',type=int); ap.add_argument('--out'); ap.add_argument('--equal',action='store_true')
    a=ap.parse_args(argv)
    from tkcommon import load
    from incr import IncrWord
    import movekit; p,w=load(a.word); iw=IncrWord(movekit.pin(w)); w=iw.to_word()
    t=time.time(); edit,st=resynth(w,a.t0,a.t1,allow_equal=a.equal); st['seconds']=round(time.time()-t,2)
    print(json.dumps(st))
    if edit:
        r=iw.try_edit(edit); print('try_edit legal=%s dk=%s reason=%s'%(r.legal,r.dk,str(r.reason)[:200]))
        if a.out and r.legal: json.dump(apply(w,edit),gzip.open(a.out,'wt')); print('wrote',a.out)
if __name__=='__main__': main()
