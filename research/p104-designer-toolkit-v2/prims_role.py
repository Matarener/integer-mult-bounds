"""prims_role -- P7, the ROLE-CHANGE primitive (P7ROLE.

P7 RETIRE(r): a PUBLIC helper register r becomes an OWNED scratch role (the interface change of PR5612 'delayed shared preparation', prepared573_local.py).
Mechanism (prepare.py of #5612 generalised): the input x_r is declared zero (the verifier's 'retired public role': endpoint row {} instead of e_r, final frame not checked).
Setting x_r := 0 is a linear substitution; every other endpoint row has no e_r term (they are identity rows), so they survive.  What changes:
  * r is no longer carried by upward (public) transports.  Every public MOVE of r (a -> b, ascending) is replaced by   CLEAR r @a ; INIT r @b ; COPY r <- s1 ; ADD r += c2 s2 ...
    where, with e_r struck from all rows,   row_r  ==  sum_j c_j row_sj   and every s_j is already at chart b (co-framed) at that moment.   (zero relation: just CLEAR+INIT.)
  * a MOVE after the last touch of r is simply dropped (the lifetime ends with CLEAR);  the first lifetime starts (INIT) at the first touch.
  * price: the paid ranks of r's MOVEs leave the paid census; r's helper credit (dim final - dim initial) leaves the helper census; owned lifetimes +k (budget/routes only).
Layout: the word is emitted in plain owned_fields form so that the whole toolkit (legal, incr, evaluate, accept) can read it WITHOUT infra changes: r is swapped with the last public
register m=n-1 (a helper), public := n-1, owned_fields := NO+1 (the retired role is the FIRST owned id), `verifier_profile` carries the new pins (public, owned_fields, lifetimes, peak).
kappa depends only on the paid + helper census, not on index layout (price_exact.invoice).  Conventions touched (not SPEC): owned inventory bound (<=NO+1), peak<=pin, lifetimes pin.

API:   import prims_role as PR
       sites=PR.find_sites(w)                      -> list of dict(prim='P7', r, plan, drank, dhelp, kappa_est) sorted by kappa_est
       w2=PR.apply_retire(w, r, plan)              -> legal word (owned_fields form), verifier_profile stamped
       PR.PLUGIN                                   movekit plugin: sites(view,ctx) / apply(view,edit)
       PR.register()                               attaches sites_P7 / apply('P7') to prims.Prims (done on import when prims is importable)
CLI:   python3 -B prims_role.py WORD [--list N] [--apply R OUT.json.gz] [--max-terms 3]"""
import sys,os,json,gzip,time,collections,copy
from fractions import Fraction as Q
import tkcommon as T
import legal,price_exact as X
import movekit as M
from movekit import qs

def _dy(q):
    d=q.denominator
    return d&(d-1)==0 and abs(q)+1<2**16

# ------------------------------------------------------------------ relation solver (exact, sparse)
def _norm(z):
    """canonical projective key of a sparse row z (dict col->Q): (tuple sorted items scaled so the first coefficient is 1, scale)"""
    it=sorted(z.items()); c=it[0][1]
    return tuple((k,v/c) for k,v in it),c
def solve_relation(y,rows,cofr,maxk=3,cap=16,ratios=3):
    """express the sparse row y (struck) as sum c_j rows[s_j], s_j in cofr (co-framed, rows struck).  Iterative deepening on the number of terms.  -> list of (s,Q) or None"""
    if not y: return []
    idx=collections.defaultdict(list); keyed={}
    for s in cofr:
        z=rows[s]
        if not z: continue
        for k in z: idx[k].append(s)
        kk,c=_norm(z); keyed.setdefault(kk,(s,c))
    def rec(z,k,used):
        if not z: return []
        kk,c=_norm(z)
        hit=keyed.get(kk)
        if hit and hit[0] not in used:
            q=c/hit[1]
            if _dy(q): return [(hit[0],q)]
        if k<=1: return None
        j=None;best=10**9
        for col in z:
            n=len(idx.get(col,()))
            if n==0: return None
            if n<best: best=n;j=col
        for s1 in idx[j][:cap]:
            if s1 in used: continue
            r1=rows[s1]; tried=set()
            for col in list(r1)[:12]:
                if col not in z: continue
                a=z[col]/r1[col]
                if a in tried or not _dy(a): continue
                tried.add(a)
                if len(tried)>ratios: break
                z2=dict(z)
                for cc,v in r1.items():
                    x=z2.get(cc,0)-a*v
                    if x: z2[cc]=x
                    else: z2.pop(cc,None)
                res=rec(z2,k-1,used|{s1})
                if res is not None: return [(s1,a)]+res
        return None
    for k in range(1,maxk+1):
        res=rec(y,k,frozenset())
        if res is not None: return res
    return None

# ------------------------------------------------------------------ the trace: exact rows, relation at every public MOVE of a helper
def replay_moves(w,regs=None):
    """exact-row replay; yields (i,r,a,b,later,rows,cur,byf) at every ascending public MOVE of a candidate helper (state AFTER the move; consume immediately) ; first yield is the info dict"""
    P=w['program']; n=len(w['initial']); NO=legal.nown(w); NR=n+NO
    live=set(w['live']); main=live|{x+112 for x in live}; RET=set(legal.retired_of(w))
    cand=set(r for r in range(n) if r not in main and r not in RET) if regs is None else set(regs)
    rows=[{r:Q(1)} for r in range(NR)]
    cur=list(w['initial'])+[None]*NO
    for r in RET: cur[r]=None
    byf=collections.defaultdict(set)
    for r in range(NR):
        if cur[r] is not None: byf[cur[r]].add(r)
    last={}; first={}
    for i,e in enumerate(P):
        if e[0]=='MOVE': continue
        for r in ((e[1],) if e[0] in('SCALE','INIT','CLEAR') else (e[1],e[2])):
            if r in cand:
                last[r]=i; first.setdefault(r,i)
    yield dict(cand=cand,last=last,first=first)
    for i,e in enumerate(P):
        op=e[0]; r=e[1]
        if op=='MOVE':
            _,r,a,b,pv=e
            byf[a].discard(r); byf[b].add(r); cur[r]=b
            if r in cand and not pv: yield (i,r,a,b,last.get(r,-1)>i,rows,cur,byf)
            continue
        if op=='INIT':
            rows[r]={}
            if cur[r] is not None: byf[cur[r]].discard(r)
            cur[r]=e[2]; byf[e[2]].add(r)
        elif op=='CLEAR': rows[r]={}; byf[cur[r]].discard(r); cur[r]=None
        elif op=='SCALE':
            c=Q(e[-2]); rows[r]={k:c*v for k,v in rows[r].items()}
        elif op=='COPY':
            c=Q(e[-2]); rows[r]={k:c*v for k,v in rows[e[2]].items()}
        else:
            c=Q(e[-2]); d=rows[r]
            for k,v in rows[e[2]].items():
                x=d.get(k,0)+c*v
                if x: d[k]=x
                else: d.pop(k,None)
def strike(rows,r,s): 
    z=rows[s]; return z if r not in z else {k:v for k,v in z.items() if k!=r}
def trace(w,regs=None,maxk=3,cap=16,log=None,delay=True):
    """-> dict r -> dict(moves=[(i,a,b,later,plan|None,t)], first, last).  plan = list of (s,Q) valid for the struck rows at insertion time t (reconstruct INIT goes BEFORE event t, i<t<=next touch of r).
    delay=True (G1): a hop without a relation at the MOVE is retried whenever another register arrives at its chart b (MOVE/INIT into b) and just before the next touch of r."""
    P=w['program']; t0=time.time(); nmv=0; g=replay_moves(w,regs)
    info=next(g); cand=info['cand']; last=info['last']
    out={r:dict(moves=[],first=info['first'].get(r),last=last.get(r)) for r in cand}
    # next non-MOVE touch of r after i
    touch=collections.defaultdict(list); reads=collections.defaultdict(list)
    for i,e in enumerate(P):
        if e[0]=='MOVE': continue
        for r in ((e[1],) if e[0] in('SCALE','INIT','CLEAR') else (e[1],e[2])):
            if r in cand: touch[r].append(i)
        if e[0] in('ADD','COPY') and e[2] in cand: reads[e[2]].append(i)
    from bisect import bisect_right
    movepos=collections.defaultdict(list)
    for i,e in enumerate(P):
        if e[0]=='MOVE' and e[1] in cand and not e[4]: movepos[e[1]].append(i)
    pend={}        # r -> [rec, deadline]
    rows=cur=byf=None
    def attempt(rec,r):
        nonlocal nmv
        i,a,b=rec[0],rec[1],rec[2]
        y=strike(rows,r,r); cofr=[s for s in byf[b] if s!=r]
        nmv+=1
        return solve_relation(y,{s:strike(rows,r,s) for s in cofr},cofr,maxk=maxk,cap=cap)
    # custom replay loop (needs per-event hooks)
    n=len(w['initial']); NO=legal.nown(w); NR=n+NO; RET=set(legal.retired_of(w))
    rows=[{r:Q(1)} for r in range(NR)]; cur=list(w['initial'])+[None]*NO
    for r in RET: cur[r]=None
    byf=collections.defaultdict(set)
    for r in range(NR):
        if cur[r] is not None: byf[cur[r]].add(r)
    for j,e in enumerate(P):
        op=e[0]
        # retry pending hops before executing event j when j is the deadline (next touch of r)
        if pend:
            for r in [r for r,(rec,dl) in pend.items() if dl==j]:
                rec,dl=pend.pop(r); pl=attempt(rec,r)
                rec[4]=pl; rec[5]=j if pl is not None else None
        if op=='MOVE':
            _,r,a,b,pv=e
            byf[a].discard(r); byf[b].add(r); cur[r]=b
            if r in cand and not pv:
                tl=touch[r]; k=bisect_right(tl,j); mp=movepos[r]; km=bisect_right(mp,j); rd=reads[r]; kr=bisect_right(rd,j)
                later=kr<len(rd) and (km>=len(mp) or rd[kr]<mp[km])       # NEEDED hop: r is READ before its next transport (otherwise the reconstructed content would be dead)
                rec=[j,a,b,later,None,None]; out[r]['moves'].append(rec)
                if later:
                    pl=attempt(rec,r)
                    if pl is not None: rec[4]=pl; rec[5]=j+1
                    elif delay: pend[r]=[rec,tl[k]]
            elif delay and pend:
                # arrival of register r into chart b: retry pending hops waiting at chart b
                for r2,(rec,dl) in list(pend.items()):
                    if rec[2]==b and r2!=r and dl>j+1:
                        pl=attempt(rec,r2)
                        if pl is not None: rec[4]=pl; rec[5]=j+1; pend.pop(r2)
            continue
        if op=='INIT':
            rows[e[1]]={}
            if cur[e[1]] is not None: byf[cur[e[1]]].discard(e[1])
            cur[e[1]]=e[2]; byf[e[2]].add(e[1])
            if delay and pend:
                for r2,(rec,dl) in list(pend.items()):
                    if rec[2]==e[2] and r2!=e[1] and dl>j+1:
                        pl=attempt(rec,r2)
                        if pl is not None: rec[4]=pl; rec[5]=j+1; pend.pop(r2)
            continue
        r=e[1]
        if op=='CLEAR': rows[r]={}; byf[cur[r]].discard(r); cur[r]=None
        elif op=='SCALE':
            c=Q(e[-2]); rows[r]={k:c*v for k,v in rows[r].items()}
        elif op=='COPY':
            c=Q(e[-2]); rows[r]={k:c*v for k,v in rows[e[2]].items()}
        else:
            c=Q(e[-2]); d=rows[r]
            for k,v in rows[e[2]].items():
                x=d.get(k,0)+c*v
                if x: d[k]=x
                else: d.pop(k,None)
    # hops still pending at the end (deadline passed handled above); convert to tuples
    for r in out: out[r]['moves']=[tuple(m) for m in out[r]['moves']]
    if log: log('trace: %d relation searches, %.1fs'%(nmv,time.time()-t0))
    return out

# ------------------------------------------------------------------ census pricing (exact: nothing else in the paid multiset changes)
def census(w):
    rep=legal.check(w,maxviol=5)
    return rep
def kappa_of(paid,hel):
    T_,P_=X.invoice(dict(paid=dict(sorted((k,v) for k,v in paid.items() if v)),helpers=dict(sorted((k,v) for k,v in hel.items() if v))))
    return X.kappa(T_,P_)
def find_sites(w,regs=None,maxk=3,cap=16,log=None,base=None,partial=False):
    """all fully reconstructible retirements, priced by census.  -> list of edits sorted by estimated kappa (best first)"""
    tr=trace(w,regs,maxk,cap,log)
    rep=base or legal.check(w,maxviol=5)
    paid=collections.Counter(rep['paid']); hel=collections.Counter(rep['helpers'])
    k0=kappa_of(paid,hel); dim=[len(b) for b in w['frames']]
    res=[]
    for r,t in tr.items():
        mv=t['moves']
        if not mv: continue
        # the register must be touched at all; every MOVE with a later touch needs a relation
        missing=sum(1 for (_,_,_,later,plan,_t) in mv if later and plan is None)
        if missing and not partial: continue
        dp=collections.Counter(abs(dim[b]-dim[a]) for (_,a,b,_,_,_) in mv)
        credit=dim[w['final'][r]]-dim[w['initial'][r]]
        p2=paid.copy(); p2.subtract(dp); h2=hel.copy()
        if credit in h2: h2[credit]-=1
        k1=kappa_of(p2,h2)
        res.append(dict(prim='P7',r=r,plan=[[i,[[s,qs(c)] for s,c in (plan or [])],t] for (i,a,b,later,plan,t) in mv if later],
                        drank=dict(dp),credit=credit,nterm=max([len(p) for (_,_,_,l,p,_t) in mv if l and p is not None] or [0]),kappa_est=k1,gain_est=k1-k0,
                        missing=missing,nmoves=len(mv),delayed=sum(1 for m in mv if m[3] and m[5] is not None and m[5]>m[0]+1),nlifetimes=sum(1 for m in mv if m[3])+1))
    res.sort(key=lambda d:-d['kappa_est'])
    return res

# ------------------------------------------------------------------ apply
def apply_retire(w,r,plan,swap=True):
    """retire public helper r.  plan = [[move_index, [[s,'c'],...], t], ...] for the NEEDED hops (those followed by a read of r before the next hop; as in find_sites; t = insertion
    position of the reconstruct, default move_index+1).  Phases between hops without a read are dead: their writes into r are dropped.  -> new word (owned_fields form)"""
    P=w['program']; n=len(w['initial']); NO=legal.nown(w); live=set(w['live']); main=live|{x+112 for x in live}
    assert r<n and r not in main and r not in legal.retired_of(w)
    pl={}
    for item in plan:
        i,terms=int(item[0]),item[1]; t=int(item[2]) if len(item)>2 and item[2] is not None else i+1
        pl[i]=(t,[(s,Q(c)) for s,c in terms])
    hops=[i for i,e in enumerate(P) if e[0]=='MOVE' and e[1]==r]
    phase_of=lambda i: sum(1 for h in hops if h<i)
    reads=[i for i,e in enumerate(P) if e[0] in('ADD','COPY') and e[2]==r]
    nph=len(hops)+1; lastread={}; needed=set()
    for i in reads: k=phase_of(i); needed.add(k); lastread[k]=max(lastread.get(k,-1),i)
    for k in range(1,nph):
        assert (k in needed)==(hops[k-1] in pl),'plan must cover exactly the needed hops (hop %d)'%hops[k-1]
    ins=collections.defaultdict(list)
    for h,(t,terms) in pl.items(): ins[t].append((h,terms))
    out=[]; alive=False
    if not reads and not any(e[0]!='MOVE' and e[1]==r for e in P): out+=[['INIT',r,w['initial'][r]],['CLEAR',r,w['initial'][r]]]
    for i,e in enumerate(P):
        for (h,terms) in ins.get(i,()):
            b_=P[h][3]; out.append(['INIT',r,b_]); alive=True
            for k,(s_,c) in enumerate(terms): out.append(['COPY' if k==0 else 'ADD',r,s_,qs(c),b_])
        op=e[0]
        if op=='MOVE':
            if e[1]==r and alive: pass            # the phase's CLEAR was issued at its last read
            if e[1]!=r: out.append(e)
            continue
        wr=(e[1]==r); rd=(op in('ADD','COPY') and e[2]==r)
        if not(wr or rd): out.append(e); continue
        k=phase_of(i)
        if k not in needed: continue                              # dead phase: the content is never read
        if i>lastread[k]: continue                                # writes after the last read of the phase are dead
        if not alive:
            assert k==0 or any(t_<=i for t_,_ in [(x[0],0) for x in pl.values()]),'phase %d touched before its reconstruct'%k
            out.append(['INIT',r,e[-1]]); alive=True
        out.append(e)
        if i==lastread[k]: out.append(['CLEAR',r,e[-1]]); alive=False
    assert not alive
    w2=dict(w); w2['program']=out
    m=n-1
    if swap and r!=m:
        assert m not in main
        sw=lambda x: m if x==r else (r if x==m else x)
        prog=[]
        for e in out:
            e=list(e)
            if e[0]=='MOVE': e[1]=sw(e[1])
            elif e[0] in('INIT','CLEAR','SCALE'): e[1]=sw(e[1])
            else: e[1]=sw(e[1]); e[2]=sw(e[2])
            prog.append(e)
        w2['program']=prog
        ini=list(w['initial']); fin=list(w['final']); ini[r]=ini[m]; fin[r]=fin[m]
    else:
        ini=list(w['initial']); fin=list(w['final']); assert r==m
    w2['initial']=ini[:m]; w2['final']=fin[:m]
    w2['public']=m; w2['owned_fields']=NO+1
    w2.pop('verifier_profile',None)
    # stamp the pins from the word's own census
    w2['verifier_profile']=dict(legal.profile_params(w),public=m,owned_fields=NO+1,lifetimes=0,peak=0)
    rep=legal.check(w2,contract=False)
    vp=dict(w2['verifier_profile']); vp.update(lifetimes=rep['lifetimes'],peak=rep['owned_peak']); w2['verifier_profile']=vp
    w2['role_change']=dict(retired=r,swapped_with=m if swap else None,moves=len(plan))
    return w2

# ------------------------------------------------------------------ movekit / prims plugin
class P7(M.Plugin):
    name='prims_role'; quick=False; doc=__doc__; site_fields=('prim','r')
    def prepare(self,view): return None
    def sites(self,view,ctx=None,regs=None,maxk=3):
        for ed in find_sites(view.w,regs=regs,maxk=maxk): yield ed
    def apply(self,view,ed): return apply_retire(view.w,ed['r'],ed['plan'])
PLUGIN=P7()
def register():
    try: import prims
    except Exception: return False
    def sites_P7(self,v,ctx,window=None,focus=None,max_f=3,regs=None): return PLUGIN.sites(v,ctx,regs=regs)
    prims.Prims.sites_P7=sites_P7
    old=prims.Prims.apply
    def apply(self,v,ed):
        if ed.get('prim')=='P7': return PLUGIN.apply(v,ed)
        return old(self,v,ed)
    prims.Prims.apply=apply
    return True
register()

def exact(w2,profile=None):
    import incr
    iw=incr.IncrWord(w2,profile=profile)
    return iw

if __name__=='__main__':
    import argparse; os.environ.setdefault('TK_FREE_BOUNDS','1')
    ap=argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('--list',type=int,default=15); ap.add_argument('--apply',nargs=2,metavar=('R','OUT'))
    ap.add_argument('--regs',default=None); ap.add_argument('--max-terms',type=int,default=3); ap.add_argument('--profile',default=None)
    a=ap.parse_args()
    p,w=T.load(a.word); t0=time.time()
    regs=[int(x) for x in a.regs.split(',')] if a.regs else None
    S=find_sites(w,regs=regs,maxk=a.max_terms,log=print)
    print('%d fully reconstructible retirements (%.1fs)'%(len(S),time.time()-t0))
    for s in S[:a.list]: print({k:v for k,v in s.items() if k!='plan'}, 'plan', s['plan'][:3])
    if a.apply:
        r=int(a.apply[0]); s=[x for x in S if x['r']==r][0]; w2=apply_retire(w,r,s['plan'])
        json.dump(w2,gzip.open(a.apply[1],'wt')); iw=exact(w2,a.profile); print('exact:',iw.kappa, getattr(iw,'violations',None))
