"""bitscreen: BIT-side move screens on the scalar-program view (the analogue of prims P1/P2 + retime/evretime).  [BITADAPT]
Objective = linearised BIT value: every Q of rank k costs W[k] (exact marginal of the raw crossing per LOCAL Q, = 18 global queries); candidates are re-priced EXACTLY (emit + fast oracle + crossing).
Registers that are owned are frozen (their moves are free ZERO_Q when the row is zero; ADDs touching them keep their frame)."""
import sys,os,json,time
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import bitword,bitval
from collections import defaultdict,Counter
def weights(w,ctx):
    T,P=bitword.invoice(w,ctx); k0=bitval.crossing(T,P,bitval.mpf('0.001'),bitval.mpf('0.02')); W={}
    for k in range(1,8):
        P2=dict(P); P2[k]=P2.get(k,0)-ctx.calls; W[k]=float(bitval.crossing(T,P2,bitval.mpf('0.001'),bitval.mpf('0.02'))-k0)
    return W,k0
class Screen:
    def __init__(s,w,ctx):
        s.w=w;s.ctx=ctx; s.owned=set(w['owned']); s.W,s.k0=weights(w,ctx)
        s.scal=bitword.scalars(w); s.n=len(s.scal)
        s._cost={}
        # timelines for non-owned registers: list of (scalar index, frame, role)
        tl=defaultdict(list)
        for i,e in enumerate(s.scal):
            if e[0]=='ADD':
                tl[e[1]].append(i); tl[e[2]].append(i)
        s.tl=tl
        # zero flags: z[(r,k)] = rows[r]==0 after the k-th timeline node of r (segment k..k+1 is free iff flag); segment 0 (from start) never free
        rows=[1<<i for i in range(ctx.width)]; z={}; pos={r:0 for r in tl}
        for i,e in enumerate(s.scal):
            if e[0]=='ADD':
                rows[e[1]]^=rows[e[2]]
                for r in (e[1],e[2]):
                    z[(r,i)]=(rows[r]==0)
            elif e[0] in('ERASE','INIT'): rows[e[1]]=0
        s.z=z
    def c(s,a,b):
        if a==b: return 0.0
        key=(a,b)
        v=s._cost.get(key)
        if v is None:
            p=s.ctx.paths.get('%s:%s'%(a,b))
            v=float('inf') if not p else sum(s.W[r] for _,_,r in p)
            s._cost[key]=v
        return v
    def reg_cost(s,r,frame_of):
        """total route cost of register r under frame_of(i) (None = default label)"""
        L=s.tl[r]; seq=[s.w['start'][r]]+[frame_of(i) for i in L]+[s.w['final'][r]]; tot=0.0
        for k,(a,b) in enumerate(zip(seq,seq[1:])):
            if k>0 and s.z.get((r,L[k-1])): continue        # free ZERO_Q
            tot+=s.c(a,b)
        return tot
    def seg(s,r,k,L,a,b):
        """cost of the segment a->b of register r that follows timeline node index k-1 (k=0: from start)"""
        if k>0 and s.z.get((r,L[k-1])): return 0.0
        return s.c(a,b)
    def relabel_screen(s,topk=40,frames=None,allf=False):
        """all single ADD frame relabels (non-owned both ends): gain = -(delta cost); zero-row segments are free"""
        import bisect
        out=[]; fl=frames or sorted(s.ctx.dims); t0=time.time()
        for i,e in enumerate(s.scal):
            if e[0]!='ADD' or e[1] in s.owned or e[2] in s.owned: continue
            f=e[3]; parts=[]
            for r in (e[1],e[2]):
                L=s.tl[r]; j=bisect.bisect_left(L,i)
                pf=s.scal[L[j-1]][3] if j>0 else s.w['start'][r]; nf=s.scal[L[j+1]][3] if j+1<len(L) else s.w['final'][r]
                parts.append((r,j,L,pf,nf))
            def tot(g): return sum(s.seg(r,j,L,pf,g)+s.seg(r,j+1,L,g,nf) for r,j,L,pf,nf in parts)
            base=tot(f)
            if base==float('inf'): continue
            cand=set(x for p in parts for x in p[3:]) if not allf else set(fl)
            for g in cand:
                if g==f or g is None: continue
                new=tot(g)
                if new<base-1e-15: out.append((base-new,i,g,f))
        out.sort(reverse=True); s.relabel_time=time.time()-t0
        return out[:topk],len(out)
def apply_relabels(w,ctx,edits):
    scal=bitword.scalars(w)
    for i,g in edits: scal[i][3]=g
    return bitword.emit(w,scal,ctx)
if __name__=='__main__':
    alias=sys.argv[1] if len(sys.argv)>1 else 'bit5708'
    ctx=bitword.Ctx(alias); w=ctx.baseword; S=Screen(w,ctx)
    print('weights per local Q (raw crossing):',{k:'%.3e'%v for k,v in S.W.items()})
    top,n=S.relabel_screen(); print('single relabels with positive linear gain:',n,'(%.1fs)'%S.relabel_time)
    for g,i,gf,f in top[:10]: print('  gain %.3e  scalar %d  %s -> frame %s (was %s)'%(g,i,S.scal[i][:3],gf,f))

def _blocks(e,d,s):
    """does scalar event e block moving ADD(d<-s) past it?  (independent = commute)"""
    if e[0]=='ADD':
        return e[2]==d or e[1]==s          # reads d / writes s
    return e[1] in (d,s)                    # ERASE / INIT on an operand
def move_screen(S,topk=40,cap=4000):
    """P1s-type screen: move one ADD past commuting events to another timeline slot, with a re-chosen frame. Linear gain; returns sorted [(gain,i,p,g)]."""
    import bisect
    scal=S.scal; out=[]; n=S.n; t0=time.time()
    nodes={r:L for r,L in S.tl.items()}                      # sorted scalar indices of ADDs touching r
    def frame_at(r,i):
        return scal[i][3]
    def nb(r,pos,skip):
        """frames of the timeline neighbours of register r around insertion position pos (events < pos go before), ignoring scalar index skip"""
        L=nodes[r]; j=bisect.bisect_left(L,pos)
        a=j-1
        if a>=0 and L[a]==skip: a-=1
        b=j
        if b<len(L) and L[b]==skip: b+=1
        u=scal[L[a]][3] if a>=0 else S.w['start'][r]
        v=scal[L[b]][3] if b<len(L) else S.w['final'][r]
        return u,v
    for i,e in enumerate(scal):
        if e[0]!='ADD' or e[1] in S.owned or e[2] in S.owned: continue
        d,sr,f=e[1],e[2],e[3]
        lo=i
        while lo>0 and i-lo<cap and not _blocks(scal[lo-1],d,sr): lo-=1
        hi=i
        while hi<n-1 and hi-i<cap and not _blocks(scal[hi+1],d,sr): hi+=1
        if lo==i and hi==i: continue
        ud0,vd0=nb(d,i,i); us0,vs0=nb(sr,i,i)
        old=S.c(ud0,f)+S.c(f,vd0)+S.c(us0,f)+S.c(f,vs0)-S.c(ud0,vd0)-S.c(us0,vs0)
        # candidate positions: just before each node of d or s inside [lo,hi], plus lo and hi+1 edges
        pts=set([lo,hi+1])
        for r in (d,sr):
            L=nodes[r]; a=bisect.bisect_left(L,lo); b=bisect.bisect_right(L,hi)
            for j in range(a,b): pts.add(L[j]); pts.add(L[j]+1)
        best=None
        for p in pts:
            if p==i or p==i+1: continue
            ud,vd=nb(d,p,i); us,vs=nb(sr,p,i)
            cb=S.c(ud,vd)+S.c(us,vs)
            for g in {ud,vd,us,vs,f}:
                if g is None: continue
                new=S.c(ud,g)+S.c(g,vd)+S.c(us,g)+S.c(g,vs)-cb
                if new<old-1e-15 and (best is None or old-new>best[0]): best=(old-new,i,p,g)
        if best: out.append(best)
    out.sort(reverse=True); S.move_time=time.time()-t0
    return out[:topk],len(out)
def apply_move(w,ctx,i,p,g):
    scal=bitword.scalars(w); e=scal.pop(i); e[3]=g
    scal.insert(p-1 if p>i else p,e); return bitword.emit(w,scal,ctx)
