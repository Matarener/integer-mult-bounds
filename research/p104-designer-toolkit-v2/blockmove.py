"""tk blockmove -- block reframe screen (PR5739, GamingPuzzled; R22 'reorder + reframe' large-neighbourhood step).  Move class: a block of scalar ops that all run on one chart X
(e.g. 96 ops on a dim-8 chart) is re-run on a NEW lower-dimensional chart F = span(union of the entry frames of the registers that use F); an UP-CLOSED subset G of the block
(ops that depend, through non-commuting pairs, on the chosen seed ops) is re-ordered behind the F ops and run on a later chart (the registers' common next frame, or X).
Registers whose first op is in the block and whose initial chart is X get a free helper start on F; helpers that end in the block and end on X get a free final chart.
Exact trace-equivalent reorder (every dependent pair keeps its order); the MOVEs are re-derived (View.rebuild); the frame set gains F when it is new.
sites(): per block (8..1500 ops, no owned registers) a greedy forward selection of seeds (each step adds the seed whose up-closure helps the exact paid/helper price most)
and yields the best prefix as ONE edit  {i0,i1,F:[basis],G:[window idx],Gf}.  The search prices with movekit.quick (trajectory-exact), the screen re-checks with evaluate().
Back-test: PR5713 word -> PR5739 (.00310927387521) = the block of 96 ops on chart 477, seeds {79,80,90,91,92}.   Does not cover multi-block windows or per-op charts (R22 MIP)."""
import collections
from bisect import bisect_left,bisect_right
import movekit as M

def rw(e):
    op=e[0]
    if op=='ADD': return {e[2]},{e[1]},True
    if op=='SCALE': return {e[1]},{e[1]},False
    if op=='COPY': return {e[2]},{e[1]},False
    return set(),{e[1]},False
def dep(a,b):
    ra,wa,aa=a; rb,wb,ab=b
    return bool(wa&rb or ra&wb or (wa&wb and not(aa and ab)))
def upclosure(R,seed):
    G={seed}; n=len(R)
    for k in range(seed+1,n):
        rk=R[k]
        if any(dep(R[g],rk) for g in G): G.add(k)
    return G
def reduce_basis(vecs):
    """independent subset spanning the same F2 space (ints)"""
    b=[]
    for x in vecs:
        y=x
        for z in b: y=min(y,y^z)
        if y: b.append(y)
    return b
def vecspan(basis):
    s={0}
    for x in basis: s|={t^x for t in s}
    return frozenset(s)

class BlockMove(M.Plugin):
    name='blockmove'; doc=__doc__; minlen=8; maxlen=1500; maxsteps=10; site_fields=('i0','i1')
    def prepare(self,v):
        ev=collections.defaultdict(list)       # reg -> sorted S indices touching it (read or write)
        for i,e in enumerate(v.S):
            ev[e[1]].append(i)
            if e[0] in('ADD','COPY'): ev[e[2]].append(i)
        for r in ev: ev[r].sort()
        return dict(ev=ev)
    # frame of register r at S index i (its own last event before i, else initial)
    def _prev(self,v,ctx,r,i0):
        L=ctx['ev'][r]; k=bisect_left(L,i0)
        if k==0: return None
        e=v.S[L[k-1]]; return e[2] if e[0] in('INIT','CLEAR') else e[-1]
    def _next(self,v,ctx,r,i1):
        L=ctx['ev'][r]; k=bisect_right(L,i1)
        if k>=len(L): return None
        e=v.S[L[k]]; return e[2] if e[0] in('INIT','CLEAR') else e[-1]
    def plan(self,v,ctx,i0,i1,G):
        """-> (S2, initial, final, frames, Fid) or None.  G = set of window-relative indices (up-closed)."""
        S=v.S; w=v.w; X=S[i0][-1]; ops=S[i0:i1+1]; Fops=[k for k in range(len(ops)) if k not in G]; Gops=sorted(G)
        regs={}
        for k,e in enumerate(ops):
            for r in ({e[1]}|({e[2]} if e[0] in('ADD','COPY') else set())):
                regs.setdefault(r,[]).append(k)
        if any(r>=v.n for r in regs): return None
        Fregs={r for r,ks in regs.items() if any(k not in G for k in ks)}
        prevs={}
        for r in Fregs:
            p=self._prev(v,ctx,r,i0)
            if p is None:
                if w['initial'][r]!=X: p=w['initial'][r]       # first event in the block, initial elsewhere: the register moves in
                else: continue                                   # helper starts on X: retargeted to F below
            prevs[r]=p
        if not Fregs: return None
        vecs=[x for p in prevs.values() for x in w['frames'][p]]
        Fb=reduce_basis(vecs)
        # free-start helpers on X contribute nothing; F must lie strictly below X
        Fs=vecspan(Fb)
        if not(Fs<v.spans[X]): return None
        Fid=v.frame_of(Fs); frames=w['frames']
        if Fid is None: Fid=len(frames); frames=frames+[Fb]
        if Fid==X: return None
        nxt=collections.Counter()
        for r,ks in regs.items():
            if any(k in G for k in ks):
                nf=self._next(v,ctx,r,i1); nxt[nf if nf is not None else w['final'][r]]+=1
        Gf=nxt.most_common(1)[0][0] if nxt else X
        new=[ops[k][:-1]+[Fid] for k in Fops]+[ops[k][:-1]+[Gf] for k in Gops]
        # re-frame (copy events: last element is the frame for ADD/SCALE/COPY alike)
        S2=S[:i0]+new+S[i1+1:]
        initial=list(w['initial']); final=list(w['final'])
        for r,ks in regs.items():
            L=ctx['ev'][r]
            if initial[r]==X and bisect_left(L,i0)==0:               # first event of r is in the block, r starts on X
                # first event in the NEW order: an F-op if r has any, else a G-op
                initial[r]=Fid if r in Fregs else Gf
            if final[r]==X and bisect_right(L,i1)==len(L):           # last event of r is in the block, r ends on X
                final[r]=Gf if any(k in G for k in ks) else Fid
        return S2,initial,final,frames,Fid
    def fast(self,v,ed,ctx=None):
        ctx=ctx or self.prepare(v); p=self.plan(v,ctx,ed['i0'],ed['i1'],set(ed['G']))
        if p is None: return None
        S2,ini,fin,frames,_=p; return M.quick(v,S2,initial=ini,final=fin,frames=frames)[0]
    def sites(self,v,ctx,only=None):
        S=v.S; k0=M.quick(v,S)[0]
        for b in v.blocks:
            i0,i1=b[0],b[-1]
            if only is not None and (i0,i1) not in only: continue
            if not(self.minlen<=len(b)<=self.maxlen) or S[i0][0] in('INIT','CLEAR'): continue
            R=[rw(e) for e in S[i0:i1+1]]; n=len(R); clos={}
            def cl(k):
                if k not in clos: clos[k]=upclosure(R,k)
                return clos[k]
            def price(G):
                p=self.plan(v,ctx,i0,i1,G)
                if p is None: return None
                S2,ini,fin,frames,_=p; return M.quick(v,S2,initial=ini,final=fin,frames=frames)[0]
            G=set(); cur=price(G); best=(cur,set(G)); prev=cur if cur is not None else -1
            for step in range(self.maxsteps):
                cand=None
                for k in range(n):
                    if k in G: continue
                    G2=G|cl(k)
                    if len(G2)==n: continue
                    kk=price(G2)
                    if kk is not None and (cand is None or kk>cand[0]): cand=(kk,G2)
                if cand is None: break
                G=cand[1]; cur=cand[0]
                if best[0] is None or cur>best[0]: best=(cur,set(G))
                if prev is not None and cur<=prev+1e-16 and step>=2: break
                prev=cur
            if best[0] is not None and best[0]>k0+1e-15:
                p=self.plan(v,ctx,i0,i1,best[1]); yield dict(i0=i0,i1=i1,G=sorted(best[1]),F=p[3][p[4]],Fid=p[4],ops=n,quick=best[0])
    # ---- incremental site pool (SEARCHPERF)
    def span(self,v,ed): return ed['i0'],ed['i1']
    def update_sites(self,v_old,v_new,delta,pool,regen=True):
        """blocks (i0,i1) are independent sites: a block whose events and registers are untouched by the edit keeps its pooled edits (remapped through the position map);
        every other block of v_new is re-enumerated (sites(only=...))"""
        S=v_new.S; ob_new={}; dirty=set(); keep={}
        for b in v_new.blocks:
            i0,i1=b[0],b[-1]
            if not(self.minlen<=len(b)<=self.maxlen) or S[i0][0] in('INIT','CLEAR'): continue
            regs=set()
            for e in S[i0:i1+1]:
                regs.add(e[1])
                if e[0] in('ADD','COPY'): regs.add(e[2])
            ob_new[(i0,i1)]=regs
        for ed in pool:
            i0=delta.map(ed['i0']); i1=delta.map(ed['i1'])
            if i0 is None or i1 is None or (i0,i1) not in ob_new: continue
            keep.setdefault((i0,i1),[]).append(dict(ed,i0=i0,i1=i1))      # touched registers do not drop a site: plan() re-derives everything from the block at apply time, the exact check decides
        # a block with no pooled edit is either a block without sites (clean) or new/changed: re-enumerate those whose old image is not a clean block
        old_blocks={(b[0],b[-1]) for b in v_old.blocks}; inv_map={}
        for (a0,a1) in old_blocks:
            m0=delta.map(a0); m1=delta.map(a1)
            if m0 is not None and m1 is not None: inv_map[(m0,m1)]=(a0,a1)
        for blk,regs in ob_new.items():
            if blk in keep: continue
            if blk in inv_map: continue        # block present before (same events): no new enumeration (a block that merely shares a register with the edit is refreshed by the periodic full rebuild)
            dirty.add(blk)
        out=[e for L in keep.values() for e in L]
        if dirty: out+=list(self.sites(v_new,self.prepare(v_new),only=dirty))
        return out
    def apply(self,v,ed):
        ctx=self.prepare(v); S2,ini,fin,frames,_=self.plan(v,ctx,ed['i0'],ed['i1'],set(ed['G']))
        return v.rebuild(S2,frames=frames,initial=ini,final=fin)
    def scalars(self,v,ed): raise NotImplementedError
    quick=False
PLUGIN=BlockMove()
def main(a): return M.cli(PLUGIN,a)
