"""bitprims: the primitive library on BIT words (G20 local words, profile bitN).  [BITPRIMS]  `python bitprims.py ALIAS CLASS [--max N]`
Does NOT go through movekit.View (that is bound to the P104 schema); it implements the same Plugin protocol (prepare/sites/scalars) over the BIT scalar program:
  view.scal = non-Q events (ADD d s f | ERASE d f | INIT d f), view.rebuild(S2) = bitword.emit (Q/ZERO_Q re-derived from PATHS = the MOVE re-derivation of the complex side).
Legality = bitword.check (fast oracle) and the authority is `tk accept bitN` (bitadapt.accept).  Price = bitword.price (exact raw crossing + admitted).
Classes: zrel (P6/P8: zero-row relation inject+undo), p1c (P1 with Steinberg correction), p0 (cancel), pairrel (P2 pair relabel domain count), p1s (move, = bitscreen.move_screen).
Candidates (exact raw crossing > base) -> ext/BITPRIMS/CANDIDATE-<alias>-<class>-<ts>.json.gz; NOT counted until `tk accept`."""
import sys,os,json,time,bisect,copy
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import bitword,bitscreen,bitval
from collections import defaultdict,Counter
OUT=os.path.dirname(os.path.abspath(__file__)) + '/ext/BITPRIMS'
INF=float('inf')
class BitView:
    def __init__(s,alias='bit5708',w=None):
        s.ctx=bitword.Ctx(alias); s.w=w or s.ctx.baseword; s.alias=alias
        s.owned=set(s.w['owned']); s.scal=bitword.scalars(s.w); s.n=len(s.scal)
        s.S=bitscreen.Screen(s.w,s.ctx); s.W=s.S.W
        s.base_raw=None
    def rebuild(s,S2): return bitword.emit(s.w,S2,s.ctx)
    def paid_cost(s,w2): return sum(s.W[e[4]] for e in w2['records'] if e[0]=='Q')
    def exact(s,S2,label=''):
        """-> (word, raw_crossing, legal) or None if no route"""
        try: w2=s.rebuild(S2)
        except Exception: return None
        V=bitword.check(w2,s.ctx,2)
        if s.base_raw is None: s.base_raw=bitword.price(s.w,s.ctx)['raw']
        p=bitword.price(w2,s.ctx); return w2,p['raw'],not V
    def c(s,a,b): return s.S.c(a,b)
    def chain_cost(s,S2,regs):
        """linear (W-weighted) route cost of the registers `regs` (all non-owned) under program S2; None if an owned register is involved"""
        regs=set(regs)
        if regs&s.owned: return None
        seq={r:[s.w['start'][r]] for r in regs}
        for e in S2:
            if e[0]=='ADD':
                if e[1] in regs: seq[e[1]].append(e[3])
                if e[2] in regs: seq[e[2]].append(e[3])
            elif e[1] in regs: return None
        tot=0.0
        for r in regs:
            q=seq[r]+[s.w['final'][r]]
            for a,b in zip(q,q[1:]):
                v=s.c(a,b)
                if v==INF: return INF
                tot+=v
        return tot
    def commute_window(s,i):
        e=s.scal[i]; d,sr=e[1],e[2]; n=s.n; lo=i
        while lo>0 and not bitscreen._blocks(s.scal[lo-1],d,sr): lo-=1
        hi=i
        while hi<n-1 and not bitscreen._blocks(s.scal[hi+1],d,sr): hi+=1
        return lo,hi
def save_candidate(v,w2,cls,raw):
    os.makedirs(OUT,exist_ok=True); p=OUT+'/CANDIDATE-%s-%s-%d.json.gz'%(v.alias,cls,int(time.time())); bitword.save(w2,p); return p
# ------------------------------------------------------------------ zrel
class ZRel:
    """P6/P8 zero-row relation inject+undo.  For a paid segment of non-owned register d (frames a -> b between its consecutive ADD nodes, R = rows[d] constant in between)
    find times t1<t2 inside the window with R in span(rows of OTHER registers at frame a at t1) and R in span(rows of others at frame b at t2); then
      ADD d<-s (s in S, frame a) at t1  [d now zero: a->b is ZERO_Q],  ADD d<-s' (s' in S', frame b) at t2  [d restored]."""
    name='zrel'
    def prepare(s,v): return None
    def sites(s,v,ctx=None,step=3,census=None):
        scal=v.scal; W=v.ctx.width; rows=[1<<i for i in range(W)]; st=v.w['start'][:]
        # per-register timeline of ADD indices, frame after node
        tl=v.S.tl; nxt={}
        # window of paid segments: (d, k, t_lo, t_hi, a, b) with t_lo=index of node k (or -1), t_hi=index of node k+1 (or n)
        segs=[]
        for d,L in tl.items():
            if d in v.owned: continue
            seq=[(-1,v.w['start'][d])]+[(i,scal[i][3]) for i in L]+[(v.n,v.w['final'][d])]
            for (i0,a),(i1,b) in zip(seq,seq[1:]):
                if a==b or a is None or b is None: continue
                segs.append((d,i0,i1,a,b))
        # sample times; at each, per-frame cycle-space supports: noncoloop[f] = {reg: relation mask containing reg}
        samples=set(range(0,v.n,step))|{v.n-1}
        bytime={}   # t -> {frame: {reg: mask}}
        # events time sweep: apply scal[i] then sample after event i. rows/st (st = frame of last node) maintained
        stt=v.w['start'][:]
        def snapshot():
            byf=defaultdict(list)
            for r in range(W):
                if rows[r] and stt[r] is not None: byf[stt[r]].append(r)
            out={}
            for f,g in byf.items():
                if len(g)<2: continue
                basis={}; rel=[]
                for r in g:
                    x=rows[r]; c=1<<r
                    while x:
                        p=x.bit_length()-1
                        if p in basis: x^=basis[p][0]; c^=basis[p][1]
                        else: basis[p]=(x,c); break
                    if x==0: rel.append(c)
                if rel:
                    nc={}
                    for c in rel:
                        for r in g:
                            if c>>r&1 and r not in nc: nc[r]=c
                    out[f]=nc
            return out
        snaps={}
        for i,e in enumerate(scal):
            if e[0]=='ADD': rows[e[1]]^=rows[e[2]]; stt[e[1]]=e[3]; stt[e[2]]=e[3]
            else: rows[e[1]]=0; stt[e[1]]=e[2]
            if i in samples:
                sn=snapshot()
                if sn: snaps[i]=sn
        times=sorted(snaps); census=census if census is not None else Counter()
        census['segments']=len(segs); census['snapshots_with_relations']=len(times)
        for d,i0,i1,a,b in segs:
            j0=bisect.bisect_left(times,i0); j1=bisect.bisect_left(times,i1)
            t1s=[t for t in times[j0:j1] if d in snaps[t].get(a,{}) ]
            if not t1s: continue
            census['seg_with_relation_at_a']+=1
            t2s=[t for t in times[j0:j1] if d in snaps[t].get(b,{})]
            if not t2s: continue
            census['seg_with_both']+=1
            for t1 in t1s:
                for t2 in t2s:
                    if t2>t1:
                        census['site']+=1
                        yield dict(d=d,t1=t1,t2=t2,a=a,b=b,S=[r for r in range(W) if snaps[t1][a][d]>>r&1 and r!=d],S2=[r for r in range(W) if snaps[t2][b][d]>>r&1 and r!=d])
                        break
                else: continue
                break
    def scalars(s,v,ed):
        S=[e[:] for e in v.scal]; ins=[]
        ins.append((ed['t1']+1,[['ADD',ed['d'],r,ed['a']] for r in ed['S']]))
        ins.append((ed['t2']+1,[['ADD',ed['d'],r,ed['b']] for r in ed['S2']]))
        for pos,evs in sorted(ins,reverse=True): S[pos:pos]=evs
        return S
def run_zrel(alias='bit5708',step=3,maxsites=0):
    v=BitView(alias); pl=ZRel(); census=Counter(); t0=time.time(); res=[]
    base=bitword.price(v.w,v.ctx)['raw']; n=0
    for ed in pl.sites(v,step=step,census=census):
        n+=1
        if maxsites and n>maxsites: break
        S2=pl.scalars(v,ed); r=v.exact(S2)
        if r is None: census['no_route']+=1; continue
        w2,raw,ok=r
        if not ok: census['illegal']+=1; continue
        census['legal']+=1
        if raw>base: census['improving']+=1; res.append((float(raw-base),ed)); p=save_candidate(v,w2,'zrel',raw); print('IMPROVING',float(raw-base),ed['d'],p,flush=True)
        else: census['worse']+=1
    print('zrel',dict(census),'time %.0fs'%(time.time()-t0)); return res
# ------------------------------------------------------------------ p0 cancel + pair relabel
def cancel_sites(v):
    sc=v.scal; byp={}
    for i,e in enumerate(sc):
        if e[0]=='ADD': byp.setdefault((e[1],e[2]),[]).append(i)
    for k,L in byp.items():
        for a,b in zip(L,L[1:]):
            lo,hi=v.commute_window(a)
            if b<=hi: yield dict(cls='p0',i=a,j=b)
def run_p0(alias='bit5708'):
    v=BitView(alias); base=bitword.price(v.w,v.ctx)['raw']; out=[]
    for ed in cancel_sites(v):
        S2=[e for k,e in enumerate(v.scal) if k not in(ed['i'],ed['j'])]; r=v.exact(S2)
        if r is None: print('p0 no route',ed); continue
        w2,raw,ok=r; print('p0',ed,'legal',ok,'dRaw %.3e'%float(raw-base)); out.append((raw-base,ed,ok))
        if ok and raw>base: print('  CANDIDATE',save_candidate(v,w2,'p0',raw))
    return out
def pair_sites(v,cap=0):
    """adjacent ADDs (a<b, consecutive on one non-owned register r, all four registers non-owned) with a joint frame domain (ga,gb), ga != fa or gb != fb"""
    sc=v.scal; paths=v.ctx.paths; out={};inn={}
    for k in paths:
        a,b=map(int,k.split(':')); out.setdefault(a,set()).add(b); inn.setdefault(b,set()).add(a)
    def fr(rr,L2,jj):
        if jj<0: return v.w['start'][rr]
        if jj>=len(L2): return v.w['final'][rr]
        return sc[L2[jj]][3]
    def dom(i,skip):
        e=sc[i]; D=None
        for rr in (e[1],e[2]):
            L2=v.S.tl[rr]; j=bisect.bisect_left(L2,i)
            for off,t in((-1,'p'),(1,'n')):
                jj=j+off
                if 0<=jj<len(L2) and L2[jj]==skip: continue
                f=fr(rr,L2,jj)
                if f is None: continue
                s=(out.get(f,set())|{f}) if t=='p' else (inn.get(f,set())|{f})
                D=s if D is None else D&s
        return D
    n=0
    for r,L in v.S.tl.items():
        if r in v.owned: continue
        for a,b in zip(L,L[1:]):
            ea,eb=sc[a],sc[b]
            if any(x in v.owned for x in (ea[1],ea[2],eb[1],eb[2])): continue
            Da=dom(a,b);Db=dom(b,a)
            if not Da or not Db: continue
            for ga in Da:
                for gb in Db:
                    if (ga,gb)==(ea[3],eb[3]): continue
                    if gb==ga or gb in out.get(ga,()): yield dict(cls='pair',a=a,b=b,ga=ga,gb=gb)
def run_pair(alias='bit5708',topq=0):
    v=BitView(alias); base=bitword.price(v.w,v.ctx)['raw']; c=Counter(); t0=time.time()
    for ed in pair_sites(v):
        S2=copy.copy(v.scal); S2[ed['a']]=v.scal[ed['a']][:3]+[ed['ga']]; S2[ed['b']]=v.scal[ed['b']][:3]+[ed['gb']]
        c['sites']+=1; r=v.exact(S2)
        if r is None: c['no_route']+=1; continue
        w2,raw,ok=r
        if not ok: c['illegal']+=1; continue
        c['legal']+=1
        if raw>base: c['improving']+=1; print('IMPROVING',ed,float(raw-base),save_candidate(v,w2,'pair',raw),flush=True)
    print('pair',dict(c),'time %.0fs'%(time.time()-t0))

# ------------------------------------------------------------------ p1c  (P1 with Steinberg correction over GF(2))
def conflict(A,B):
    """A=ADD(t<-s) passes B=ADD(u<-v): None=commute, 'bar'=barrier, ('R',C)/( 'W',C) with the correction ADD (d,s)"""
    if B[0]!='ADD': return 'bar' if (B[1] in (A[1],A[2])) else None
    t,s=A[1],A[2]; u,vv=B[1],B[2]
    if u==s and vv==t: return 'bar'
    if u==s: return ('W',(t,vv))          # B writes s: correction t += v
    if vv==t: return ('R',(u,s))          # B reads t: correction u += s
    return None
def p1c_sites_i(v,i,maxc=2,span=400,dirs=(1,-1)):
    sc=v.scal; A=sc[i]
    if A[0]!='ADD' or A[1] in v.owned or A[2] in v.owned: return
    for dr in dirs:
        cor=[]; j=i+dr; n=0
        while 0<=j<v.n and n<span:
            B=sc[j]; c=conflict(A,B); n+=1
            if c=='bar': break
            if c is not None:
                if len(cor)>=maxc or any(x in v.owned for x in c[1]): break
                cor.append((j,c[1]))
            if B[0]=='ADD' and (B[1] in(A[1],A[2]) or B[2] in(A[1],A[2]) or (cor and cor[-1][0]==j) or any(B[1] in cc[1] or B[2] in cc[1] for cc in cor)):
                yield dict(i=i,dr=dr,j=j,cor=list(cor))
            j+=dr
def p1c_sites(v,maxc=2,span=400):
    for i in range(v.n): yield from p1c_sites_i(v,i,maxc,span)
def eval_p1c(v,ed,maxcombo=60):
    """linear gain of the best frame assignment for the edit; -> (gain, g1, [g2..]) or None"""
    sc=v.scal; i,dr,j,cor=ed['i'],ed['dr'],ed['j'],ed['cor']; A=sc[i]; t,s=A[1],A[2]
    keyA=(j+0.75) if dr==1 else (j-0.75)
    corE=[(cj+0.25,cd,cs) for cj,(cd,cs) in cor]
    if dr==-1: corE=[(cj+0.25,cd,cs) for cj,(cd,cs) in cor]
    regs={t,s}|{cd for _,cd,_ in corE}|{cs for _,_,cs in corE}
    if regs&v.owned: return None
    def chains(frames):
        g1=frames[0]; ch={}
        for r in regs:
            L=[(float(k),sc[k][3]) for k in v.S.tl[r] if k!=i]
            if r in (t,s): L.append((keyA,g1))
            for (k,cd,cs),g in zip(corE,frames[1:]):
                if r in(cd,cs): L.append((k,g))
            L.sort(); ch[r]=[f for _,f in L]
        return ch
    def cost(ch):
        tot=0.0
        for r,L in ch.items():
            q=[v.w['start'][r]]+L+[v.w['final'][r]]
            for a,b in zip(q,q[1:]):
                x=v.c(a,b)
                if x==INF: return INF
                tot+=x
        return tot
    base=0.0
    for r in regs:
        q=[v.w['start'][r]]+[sc[k][3] for k in v.S.tl[r]]+[v.w['final'][r]]
        for a,b in zip(q,q[1:]):
            x=v.c(a,b); base+=x
    # candidate frames: neighbour frames of the involved registers' base timelines around the move span
    lo,hi=min(i,j),max(i,j); cand=set()
    for r in regs:
        L=v.S.tl[r]; a=bisect.bisect_left(L,lo); b=bisect.bisect_right(L,hi)
        for k in L[max(0,a-1):b+1]: cand.add(sc[k][3])
        cand.add(v.w['start'][r]); cand.add(v.w['final'][r])
    cand.discard(None); cand=sorted(cand)
    best=None; import itertools
    nf=1+len(corE)
    for combo in itertools.product(cand,repeat=nf):
        if len(cand)**nf>4000 and combo[0]!=A[3] and nf>1: continue
        ch=chains(list(combo)); c=cost(ch)
        if c<INF and (best is None or c<best[0]): best=(c,combo)
    if best is None: return None
    return base-best[0],best[1]
def build_p1c(v,ed,frames):
    sc=[e[:] for e in v.scal]; i,dr,j,cor=ed['i'],ed['dr'],ed['j'],ed['cor']; A=sc[i][:]; A[3]=frames[0]
    items=[(float(k),e) for k,e in enumerate(sc) if k!=i]
    items.append(((j+0.75) if dr==1 else (j-0.75),A))
    for (cj,(cd,cs)),g in zip(cor,frames[1:]): items.append((cj+0.25,['ADD',cd,cs,g]))
    items.sort(key=lambda x:x[0]); return [e for _,e in items]
def run_p1c(alias='bit5708',maxc=2,topn=60,maxsites=0):
    v=BitView(alias); base=bitword.price(v.w,v.ctx)['raw']; c=Counter(); t0=time.time(); pos=[]
    for ed in p1c_sites(v,maxc):
        c['sites']+=1
        if ed['cor']: c['with_corr']+=1
        if maxsites and c['sites']>maxsites: break
        r=eval_p1c(v,ed)
        if r is None: c['skip']+=1; continue
        if r[0]>1e-12: pos.append((r[0],ed,r[1])); c['linear_positive']+=1
        if r[0]>1e-12 and not ed['cor']: c['pos_nocor']+=1
    pos.sort(key=lambda x:-x[0])
    print('p1c screen',dict(c),'%.0fs'%(time.time()-t0),flush=True)
    for g,ed,fr in pos[:topn]:
        S2=build_p1c(v,ed,fr); r=v.exact(S2)
        if r is None: c['exact_noroute']+=1; continue
        w2,raw,ok=r
        print('  linear %.3e exact d %.3e legal %s %s'%(g,float(raw-base),ok,{k:ed[k] for k in('i','dr','j')}),flush=True)
        if ok and raw>base: print('IMPROVING',save_candidate(v,w2,'p1c',raw),flush=True)
    return pos

# ------------------------------------------------------------------ walk: simulated-annealing plateau walk over P1/P1c moves (frames re-chosen locally per move)
import random,math
def rebuild_tl(v):
    from collections import defaultdict
    tl=defaultdict(list)
    for i,e in enumerate(v.scal):
        if e[0]=='ADD': tl[e[1]].append(i); tl[e[2]].append(i)
    v.S.tl=tl; v.n=len(v.scal)
def walk(alias='bit5708',seed=1,T=2e-7,minutes=20,maxc=1,tag='walk'):
    rnd=random.Random(seed); v=BitView(alias); base=bitword.price(v.w,v.ctx)['raw']; cum=0.0; best=0.0; c=Counter(); t0=time.time(); lastchk=0
    ids=[i for i,e in enumerate(v.scal) if e[0]=='ADD' and e[1] not in v.owned and e[2] not in v.owned]
    while time.time()-t0<minutes*60:
        i=rnd.randrange(v.n)
        if v.scal[i][0]!='ADD': continue
        sts=list(p1c_sites_i(v,i,maxc,dirs=(rnd.choice((1,-1)),)))
        if not sts: continue
        ed=rnd.choice(sts); r=eval_p1c(v,ed)
        if r is None: c['skip']+=1; continue
        g,fr=r; c['prop']+=1
        if g<0 and rnd.random()>=math.exp(g/T): continue
        v.scal=build_p1c(v,ed,fr); rebuild_tl(v); cum+=g; c['acc']+=1
        if g>1e-12: c['up']+=1
        if cum>best+1e-9:
            best=cum; x=v.exact(v.scal)
            if x is None or not x[2]: c['best_illegal']+=1; print('best-state illegal/noroute cum %.3e'%cum,flush=True); continue
            w2,raw,ok=x; print('NEWBEST linear %.3e exact %.3e'%(cum,float(raw-base)),flush=True)
            if raw>base: print('IMPROVING',save_candidate(v,w2,tag+str(seed),raw),flush=True)
        if c['acc']-lastchk>=3000:
            lastchk=c['acc']; x=v.exact(v.scal)
            print('chk acc %d cum %.3e exact %s legal %s t=%.0fs'%(c['acc'],cum,None if x is None else '%.3e'%float(x[1]-base),None if x is None else x[2],time.time()-t0),flush=True)
    print('walk done',dict(c),'cum %.3e best %.3e'%(cum,best))

# ------------------------------------------------------------------ plugin registry (movekit protocol: name, prepare(view), sites(view,ctx), scalars(view,edit)); view = BitView
class P1C:
    name='p1c'
    def prepare(s,v): return None
    def sites(s,v,ctx=None):
        for ed in p1c_sites(v,1):
            r=eval_p1c(v,ed)
            if r: yield dict(ed,frames=list(r[1]),gain=r[0])
    def scalars(s,v,ed): return build_p1c(v,ed,ed['frames'])
class P0:
    name='p0'
    def prepare(s,v): return None
    def sites(s,v,ctx=None): return cancel_sites(v)
    def scalars(s,v,ed): return [e for k,e in enumerate(v.scal) if k not in(ed['i'],ed['j'])]
class PAIR:
    name='pair'
    def prepare(s,v): return None
    def sites(s,v,ctx=None): return pair_sites(v)
    def scalars(s,v,ed):
        S2=copy.copy(v.scal); S2[ed['a']]=v.scal[ed['a']][:3]+[ed['ga']]; S2[ed['b']]=v.scal[ed['b']][:3]+[ed['gb']]; return S2
PLUGINS={'zrel':ZRel(),'p1c':P1C(),'p0':P0(),'pair':PAIR()}


def main(a):
    alias=a[1] if len(a)>1 else 'bit5708'; cls=a[2] if len(a)>2 else 'zrel'
    if cls=='zrel': run_zrel(alias,step=int(a[3]) if len(a)>3 else 3)
    elif cls=='p0': run_p0(alias)
    elif cls=='pair': run_pair(alias)
    elif cls=='walk': walk(alias,int(a[3]),float(a[4]),float(a[5]),int(a[6]) if len(a)>6 else 1)
    elif cls=='p1c': run_p1c(alias,*[int(x) for x in a[3:]])
if __name__=='__main__': main(sys.argv)