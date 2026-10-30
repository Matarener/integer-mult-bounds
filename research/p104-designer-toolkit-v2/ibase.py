"""tk ibase -- paid interior bases screen (PR5678, aliromman).  Move class: conjugate the scalar program of a block interval [s0..s1] by the basis change R=I+q*E_ab
(insert `a += q*b` before the interval and `a -= q*b` after it, rewrite the interior).  Only events that read a (ADD(t,a)) or write b (ADD(b,s)) change:
a reader gains `t += -q*c * b`, a writer gains `a += q*c * s`; a contact VANISHES when it cancels an existing ADD(t,b,qc) / ADD(a,s,-qc) of the same block.
Forbidden: SCALE/COPY touching a or b, ADD(b,a), owned a/b or owned partner.  Gain = fewer (register, frame) visits -> fewer/cheaper paid MOVEs.
sites(): proxy = net contact change over a contiguous block interval (the MOVES1026 scr4 proxy, rediscovers all four PR5678 sites), expanded over entry/exit frame
candidates (ef, xf) of the inserted pair.  Ported from MOVES1026 (scr4.py/conj.py/scan.py) on the shared View/legal (any owned count, public = len(initial))."""
import collections,itertools
from bisect import bisect_left
from fractions import Fraction as Q
import movekit as M
from movekit import qs

_QC={}
def Qm(x):
    """memoised Fraction(str): quotients repeat constantly"""
    r=_QC.get(x)
    if r is None: r=_QC[x]=Q(x)
    return r
def conj_events(evs,a,b,q,pub):
    out=[]
    for e in evs:
        op=e[0]
        if op in('SCALE','COPY') and (e[1] in(a,b) or (op=='COPY' and e[2] in (a,b))): raise ValueError('scale/copy')
        if op=='ADD':
            t,s,c,f=e[1],e[2],Qm(e[3]),e[4]
            if t==b and s==a: raise ValueError('ba')
            if s==a:
                if t>=pub: raise ValueError('owned')
                out.append(['ADD',t,a,qs(c),f]); out.append(['ADD',t,b,qs(-q*c),f]); continue
            if t==b:
                if s>=pub: raise ValueError('owned')
                out.append(['ADD',b,s,qs(c),f]); out.append(['ADD',a,s,qs(q*c),f]); continue
        out.append(e[:])
    return out
def merge(evs):
    """merge duplicate ADD(t,s) of one frame when no event in between reads t / writes s / is not an ADD on that frame (the backwards scan of merge_ref).
    FASTSITES: positions are stable ids (cancelled events become None tombstones, compacted at the end) and the run indexes keep a position LIST per key, so a cancellation removes one
    position from three lists instead of re-scanning the whole run (the old reindex was O(run) per cancellation); the run is re-indexed from scratch only when a cancellation empties it.
    Output identical to merge_old (tests/ibase_fast_test.py)."""
    out=[]; rf=None; pos={}; lw={}; lr={}; nrun=0
    def reindex():
        nonlocal rf,pos,lw,lr,nrun
        out[:]=[x for x in out if x is not None]
        pos={}; lw={}; lr={}; rf=None; nrun=0
        if out and out[-1][0]=='ADD':
            rf=out[-1][4]; j=len(out)-1
            while j>0 and out[j-1][0]=='ADD' and out[j-1][4]==rf: j-=1
            for k in range(j,len(out)):
                p=out[k]; pos.setdefault((p[1],p[2]),[]).append(k); lw.setdefault(p[1],[]).append(k); lr.setdefault(p[2],[]).append(k)
            nrun=len(out)-j
    for e in evs:
        if e[0]=='ADD':
            t,s,f=e[1],e[2],e[4]
            if rf==f:
                pl=pos.get((t,s))
                if pl:
                    j=pl[-1]; x=lw.get(s); y=lr.get(t)
                    if (x[-1] if x else -1)<=j and (y[-1] if y else -1)<=j:
                        c=Qm(out[j][3])+Qm(e[3])
                        if c==0:
                            out[j]=None; pl.pop(); lw[t].remove(j); lr[s].remove(j); nrun-=1
                            if nrun==0: reindex()
                        else: out[j]=['ADD',t,s,qs(c),f]
                        continue
            else: rf=f; pos={}; lw={}; lr={}; nrun=0
            k=len(out); out.append(e); pos.setdefault((t,s),[]).append(k); lw.setdefault(t,[]).append(k); lr.setdefault(s,[]).append(k); nrun+=1
        else: out.append(e); rf=None
    return [x for x in out if x is not None] if None in out else out
def merge_old(evs):
    """merge duplicate ADD(t,s) of one frame when no event in between reads t / writes s / is not an ADD on that frame.
    Linear: the maximal run of same-frame ADDs at the end of `out` is indexed (latest position of each (t,s); latest writer / reader of each register), so a candidate
    is merged iff its latest twin is not followed by a writer of s or a reader of t -- exactly the backwards scan of merge_ref, without the O(run) walk."""
    out=[]; rf=None; pos={}; lw={}; lr={}
    def reindex():
        nonlocal rf,pos,lw,lr
        pos={}; lw={}; lr={}; rf=None
        if out and out[-1][0]=='ADD':
            rf=out[-1][4]; j=len(out)-1
            while j>0 and out[j-1][0]=='ADD' and out[j-1][4]==rf: j-=1
            for k in range(j,len(out)):
                p=out[k]; pos[(p[1],p[2])]=k; lw[p[1]]=k; lr[p[2]]=k
    for e in evs:
        if e[0]=='ADD':
            t,s,f=e[1],e[2],e[4]
            if rf==f:
                j=pos.get((t,s))
                if j is not None and lw.get(s,-1)<=j and lr.get(t,-1)<=j:
                    c=Qm(out[j][3])+Qm(e[3])
                    if c==0: out.pop(j); reindex()
                    else: out[j]=['ADD',t,s,qs(c),f]
                    continue
            else: rf=f; pos={}; lw={}; lr={}
            k=len(out); out.append(e); pos[(t,s)]=k; lw[t]=k; lr[s]=k
        else: out.append(e); rf=None
    return out
def merge_ref(evs):
    """merge duplicate ADD(t,s) of one frame when no event in between reads t / writes s / is not an ADD on that frame"""
    out=[]
    for e in evs:
        if e[0]=='ADD':
            t,s,f=e[1],e[2],e[4]; j=len(out)-1; done=False
            while j>=0:
                p=out[j]
                if p[0]=='ADD' and p[1]==t and p[2]==s and p[4]==f:
                    c=Q(p[3])+Qm(e[3])
                    if c==0: out.pop(j)
                    else: out[j]=['ADD',t,s,qs(c),f]
                    done=True;break
                if p[0]!='ADD' or p[1]==s or p[2]==t or p[4]!=f: break
                j-=1
            if done: continue
        out.append(e)
    return out
def proxy_sites_full(v,regs=None):
    """-> list (delta, a, b, q, s0, s1, L) sorted most negative first: contiguous block intervals where conjugation by I+q*E_ab removes contacts
    regs (set) restricts to the pairs with a in regs or b in regs (incremental site pools: only the pairs an edit can have changed)
    FASTSITES: same result as proxy_sites_ref (tests/ibase_fast_test.py: list equality on real words); the per-(pair, q, block) Fraction compares `d==q*c` are replaced by the
    q-independent ratio d/c computed once per contact: a contact removes one pair at q iff its ratio == q, so the block delta is base - (#contacts whose ratio == q)."""
    pub=v.n; blocks=[[v.S[i] for i in b] for b in v.blocks]; INF=10**6
    con=[collections.defaultdict(Q) for _ in blocks]; cnt=[collections.Counter() for _ in blocks]
    readers=collections.defaultdict(list); writers=collections.defaultdict(list); bad=collections.defaultdict(set); srcev=[collections.defaultdict(list) for _ in blocks]
    for bi,b in enumerate(blocks):
        for k,e in enumerate(b):
            if e[0]=='ADD':
                t,s,c=e[1],e[2],Qm(e[3]); con[bi][(t,s)]+=c; cnt[bi][(t,s)]+=1; readers[s].append((bi,t,c)); writers[t].append((bi,s,c)); srcev[bi][s].append((k,t,c))
            else:
                bad[e[1]].add(bi)
                if e[0]=='COPY': bad[e[2]].add(bi)
    tg=[collections.defaultdict(set) for _ in blocks]; tcon=[collections.defaultdict(list) for _ in blocks]
    for bi in range(len(blocks)):
        for (t,s_) in con[bi]: tg[bi][s_].add(t); tcon[bi][t].append(s_)
    first3=[b[0][0]=='ADD' and b[0][-1] in (3,127) for b in blocks]
    res=[]
    for a in range(pub):
        byblock=collections.defaultdict(list)
        for bi,t,c in readers[a]: byblock[bi].append((t,c))
        cand=set(); ra=regs is None or a in regs
        for bi,s_,c in writers[a]:
            for t2 in (tg[bi][s_] if ra else tg[bi][s_]&regs):
                if t2!=a and t2<pub: cand.add(t2)
        for bi,l in byblock.items():
            for t in {t for t,c in l}:
                for s2 in tcon[bi].get(t,()):
                    if s2!=a and s2<pub and (ra or s2 in regs): cand.add(s2)
        contrib={}          # b -> [(bi, ratio)] in the order the reference scans them: readers of a (byblock order), then writers of b (block, event order)
        for bi,l in byblock.items():
            cb=con[bi]; nb=cnt[bi]; tc=tcon[bi]
            for t_,c in l:
                for b in tc.get(t_,()):
                    if (ra or b in regs) and nb[(t_,b)]==1: contrib.setdefault(b,[]).append((bi,cb[(t_,b)]/c))
        wc={}
        for bi in sorted({bi for bi,s_,c in writers[a]}):
            cb=con[bi]; nb=cnt[bi]; se=srcev[bi]
            for s_ in tcon[bi].get(a,()):
                if nb[(a,s_)]==1:
                    d=cb[(a,s_)]
                    for k,t2,c in se[s_]:
                        if ra or t2 in regs: wc.setdefault(t2,[]).append((bi,k,-d/c))
        for b,l in wc.items():
            l.sort(key=lambda x:(x[0],x[1]))
            contrib.setdefault(b,[]).extend((bi,r) for bi,k,r in l)
        for b in cand:
            if regs is not None and a not in regs and b not in regs: continue
            cs=contrib.get(b)
            if cs is None: continue
            qset=set(); mc={}          # mc[bi]: Counter ratio -> #contacts that vanish at q==ratio
            for bi,r in cs:
                qset.add(r); m=mc.get(bi)
                if m is None: m=mc[bi]=collections.Counter()
                m[r]+=1
            wbl=collections.defaultdict(list)
            for bi,s,c in writers[b]: wbl[bi].append((s,c))
            qset={q for q in qset if q!=0 and (q.denominator&(q.denominator-1))==0}
            if not qset: continue
            blks=sorted(set(byblock)|set(wbl))
            ba=bad[a]; bb=bad[b]; base=[]; live=[]
            for bi in blks:
                dl=0; bd=bi in ba or bi in bb; cb=con[bi]
                for t,c in byblock.get(bi,()):
                    if t==b or t>=pub: bd=True
                    if (t,b) not in cb: dl+=1
                for s,c in wbl.get(bi,()):
                    if s==a or s>=pub: bd=True
                    if (a,s) not in cb: dl+=1
                if bd: base.append(INF); live.append(False)
                elif first3[bi]: base.append(0); live.append(False)
                else: base.append(dl); live.append(True)
            pos={bi:i for i,bi in enumerate(blks)}; adj={}
            for bi,m in mc.items():
                i=pos[bi]
                if live[i]:
                    for r,k in m.items():
                        if r in qset: adj.setdefault(r,[]).append((i,k))
            for q in qset:
                xs=base
                ad=adj.get(q)
                if ad:
                    xs=base[:]
                    for i,k in ad: xs[i]-=k
                best=(0,None,None);cur=0;st=0
                for i,x in enumerate(xs):
                    if cur>0 or i==0: cur=0;st=i
                    cur+=x
                    if cur<best[0]: best=(cur,st,i)
                if best[1] is not None and best[0]<=-1: res.append((best[0],a,b,q,blks[best[1]],blks[best[2]],best[2]-best[1]+1))
    res.sort(key=lambda r:(r[0],r[6],r[1],r[2])); return res
INC=True
STATS=collections.Counter()
_LAST=[None]          # (S, blocks, result, n) of the last whole-word proxy_sites: the next call on a word that differs by one hunk updates it (exactly) instead of recomputing
def proxy_sites(v,regs=None):
    """proxy_sites_full, with an EXACT incremental update across committed edits (FASTSITES item 4).  The result of a pair (a,b) depends only on the events whose target/source is a or b and on
    the blocks (index, membership, first event) those events live in.  So for a word that differs from the previous one by one hunk [p, hi) of the scalar program, every pair with neither a nor b
    in INVALID = (registers of the hunk's old+new events) U (registers occurring in any block that touches the hunk +-1 event, old or new) keeps its old result (block indices remapped), and only the
    pairs touching INVALID are recomputed (proxy_sites_full(regs=INVALID)).  Same list, same order (tests/ibase_fast_test.py, rediscovery chain)."""
    if regs is not None or not INC: return proxy_sites_full(v,regs)
    S=v.S; L=_LAST[0]; res=None
    if L is not None and L[0] is S and L[3]==v.n: return L[2]
    if L is not None and L[3]==v.n:
        try: res=_proxy_inc(v,L)
        except Exception: res=None
        STATS['inc' if res is not None else 'inc_fallback']+=1
    if res is None: res=proxy_sites_full(v); STATS['full']+=1
    _LAST[0]=(S,v.blocks,res,v.n); return res
def _proxy_inc(v,L):
    from dq import _lcp,_lcs
    from bisect import bisect_right
    So,Bo,res_o,_=L; S=v.S; Bn=v.blocks
    n=min(len(So),len(S)); p=_lcp(So,S,n); q=_lcs(So,S,n-p); hio=len(So)-q; hin=len(S)-q
    if (hio-p)+(hin-p)>max(400,len(S)//8): return None            # big hunk: a full recompute is as cheap
    inv=set()
    for e in So[p:hio]+S[p:hin]:
        inv.add(e[1])
        if e[0] in('ADD','COPY'): inv.add(e[2])
    def touch(B,Sx,lo,hi):
        starts=[b[0] for b in B]; k=max(0,bisect_right(starts,lo)-1)
        while k<len(B) and B[k][0]<hi:
            if B[k][-1]>=lo:
                for j in B[k]:
                    e=Sx[j]; inv.add(e[1])
                    if e[0] in('ADD','COPY'): inv.add(e[2])
            k+=1
    touch(Bo,So,max(0,p-1),hio+1); touch(Bn,S,max(0,p-1),hin+1)
    shift=len(S)-len(So); nstart={b[0]:k for k,b in enumerate(Bn)}
    def remap(bi):
        j=Bo[bi][0]
        if j<p-1: return bi
        return nstart[j+shift]
    out=[]
    for r in res_o:
        if r[1] in inv or r[2] in inv: continue
        out.append((r[0],r[1],r[2],r[3],remap(r[4]),remap(r[5]),r[6]))
    out+=proxy_sites_full(v,inv)
    out.sort(key=lambda r:(r[0],r[6],r[1],r[2])); return out
def proxy_sites_ref(v,regs=None):
    """-> list (delta, a, b, q, s0, s1, L) sorted most negative first: contiguous block intervals where conjugation by I+q*E_ab removes contacts
    regs (set) restricts to the pairs with a in regs or b in regs (incremental site pools: only the pairs an edit can have changed)"""
    pub=v.n; blocks=[[v.S[i] for i in b] for b in v.blocks]
    con=[collections.defaultdict(Q) for _ in blocks]; cnt=[collections.Counter() for _ in blocks]
    readers=collections.defaultdict(list); writers=collections.defaultdict(list); bad=collections.defaultdict(set)
    for bi,b in enumerate(blocks):
        for e in b:
            if e[0]=='ADD':
                t,s,c=e[1],e[2],Qm(e[3]); con[bi][(t,s)]+=c; cnt[bi][(t,s)]+=1; readers[s].append((bi,t,c)); writers[t].append((bi,s,c))
            else:
                bad[e[1]].add(bi)
                if e[0]=='COPY': bad[e[2]].add(bi)
    tg=[collections.defaultdict(set) for _ in blocks]; tcon=[collections.defaultdict(list) for _ in blocks]
    for bi in range(len(blocks)):
        for (t,s_) in con[bi]: tg[bi][s_].add(t); tcon[bi][t].append(s_)
    res=[]
    for a in range(pub):
        byblock=collections.defaultdict(list)
        for bi,t,c in readers[a]: byblock[bi].append((t,c))
        cand=set(); ra=regs is None or a in regs
        for bi,s_,c in writers[a]:
            for t2 in (tg[bi][s_] if ra else tg[bi][s_]&regs):
                if t2!=a and t2<pub: cand.add(t2)
        for bi,l in byblock.items():
            for t in {t for t,c in l}:
                for s2 in tcon[bi].get(t,()):
                    if s2!=a and s2<pub and (ra or s2 in regs): cand.add(s2)
        for b in cand:
            if regs is not None and a not in regs and b not in regs: continue
            wbl=collections.defaultdict(list)
            for bi,s,c in writers[b]: wbl[bi].append((s,c))
            blks=sorted(set(byblock)|set(wbl)); qset=set()
            for bi,l in byblock.items():
                for t,c in l:
                    d=con[bi].get((t,b))
                    if d is not None and cnt[bi][(t,b)]==1: qset.add(d/c)
            for bi,l in wbl.items():
                for s,c in l:
                    d=con[bi].get((a,s))
                    if d is not None and cnt[bi][(a,s)]==1: qset.add(-d/c)
            qset={q for q in qset if q!=0 and (q.denominator&(q.denominator-1))==0}
            for q in qset:
                deltas=[]
                for bi in blks:
                    dl=0;bd=False
                    for t,c in byblock.get(bi,[]):
                        if t==b or t>=pub: bd=True
                        d=con[bi].get((t,b))
                        if d is None: dl+=1
                        elif cnt[bi][(t,b)]==1 and d==q*c: dl-=1
                    for s,c in wbl.get(bi,[]):
                        if s==a or s>=pub: bd=True
                        d=con[bi].get((a,s))
                        if d is None: dl+=1
                        elif cnt[bi][(a,s)]==1 and d==-q*c: dl-=1
                    if bi in bad[a] or bi in bad[b]: bd=True
                    if blocks[bi][0][-1] in (3,127) and blocks[bi][0][0]=='ADD': dl=0 if not bd else dl
                    deltas.append(dl if not bd else 10**6)
                best=(0,None,None);cur=0;st=0
                for i,dl in enumerate(deltas):
                    if cur>0 or i==0: cur=0;st=i
                    cur+=dl
                    if cur<best[0]: best=(cur,st,i)
                if best[1] is not None and best[0]<=-1: res.append((best[0],a,b,q,blks[best[1]],blks[best[2]],best[2]-best[1]+1))
    res.sort(key=lambda r:(r[0],r[6],r[1],r[2])); return res
class IBase(M.Plugin):
    name='ibase'; doc=__doc__; site_fields=('a','b','q')
    def prepare(self,v):
        touch=collections.defaultdict(list)
        for i,e in enumerate(v.S):
            if e[0]=='ADD': touch[e[1]].append(i); touch[e[2]].append(i)
            elif e[0] in('SCALE','INIT','CLEAR'): touch[e[1]].append(i)
            elif e[0]=='COPY': touch[e[1]].append(i); touch[e[2]].append(i)
        return dict(touch=touch)
    def sites(self,v,ctx,maxframes=8,regs=None):
        touch=ctx['touch']; S=v.S; w=v.w
        def fr(j): e=S[j]; return e[2] if e[0] in('INIT','CLEAR') else e[-1]
        def near(i,regs,side):
            o=[]
            for r in regs:
                L=touch[r]; k=bisect_left(L,i)
                for j in (L[max(0,k-2):k] if side<0 else L[k:k+2]): o.append(fr(j))
            return o
        for sm,a,b,q,s0,s1,L in proxy_sites(v,regs):
            i0=v.blocks[s0][0]; i1=v.blocks[s1][-1]
            EF=list(dict.fromkeys([fr(i0)]+near(i0,(a,b),-1)+near(i0,(a,b),1)+[w['initial'][a],w['initial'][b]]))[:maxframes]
            XF=list(dict.fromkeys([fr(i1)]+near(i1+1,(a,b),-1)+near(i1+1,(a,b),1)+[w['final'][a],w['final'][b]]))[:maxframes]
            for ef,xf in itertools.product(EF,XF):
                yield dict(a=a,b=b,q=qs(q),s0=s0,s1=s1,ef=ef,xf=xf,proxy=sm)
    # ---- incremental site pool (SEARCHPERF): the pool of an earlier word is updated after an edit instead of rebuilt
    def span(self,v,ed):
        """event positions (lo,hi) of S an edit of this site spans"""
        bl=v.blocks; return bl[ed['s0']][0],bl[ed['s1']][-1]
    defer_regen=True            # driver may call update_sites(regen=False): remap only; the touched registers are re-enumerated later in one go
    def update_sites(self,v_old,v_new,delta,pool,regen=True):
        """pool: edits enumerated on v_old.  -> pool for v_new (or None = rebuild): sites on pairs (a,b) with a or b a register the edit touched are dropped and re-enumerated
        (proxy_sites restricted to those registers); the others keep their blocks, remapped through the event position map (dropped if an endpoint moved into a changed hunk)."""
        ob,nb=v_old.blocks,v_new.blocks; st={b[0]:k for k,b in enumerate(nb)}; en={b[-1]:k for k,b in enumerate(nb)}; out=[]
        for ed in pool:
            if ed['a'] in delta.regs or ed['b'] in delta.regs: continue
            i0=delta.map(ob[ed['s0']][0]); i1=delta.map(ob[ed['s1']][-1])
            if i0 is None or i1 is None or i0 not in st or i1 not in en: continue
            s0,s1=st[i0],en[i1]
            if s1<s0: continue
            out.append(dict(ed,s0=s0,s1=s1))
        if regen and delta.regs:
            ctx=self.prepare(v_new); out+=list(self.sites(v_new,ctx,regs=delta.regs))
        return out
    def scalars(self,v,ed):
        S=v.S; bl=v.blocks; q=Q(ed['q']); a,b=ed['a'],ed['b']
        i0=bl[ed['s0']][0]; i1=bl[ed['s1']][-1]
        mid=merge(conj_events(S[i0:i1+1],a,b,q,v.n))
        return S[:i0]+[['ADD',a,b,qs(q),ed['ef']]]+mid+[['ADD',a,b,qs(-q),ed['xf']]]+S[i1+1:]
    def sedit(self,v,ed):
        """REALISEFIX: the same conjugation as scalars() as a window edit (no S[:i0]+..+S[i1+1:] copy)"""
        import sedit as SE
        S=v.S; bl=v.blocks; q=Q(ed['q']); a,b=ed['a'],ed['b']
        i0=bl[ed['s0']][0]; i1=bl[ed['s1']][-1]
        mid=merge(conj_events(S[i0:i1+1],a,b,q,v.n))
        return SE.SEdit(i0,i1+1,[['ADD',a,b,qs(q),ed['ef']]]+mid+[['ADD',a,b,qs(-q),ed['xf']]],meta=ed,view=v)
PLUGIN=IBase()
def main(a): return M.cli(PLUGIN,a)
