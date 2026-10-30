"""k2bit_search: SA / plateau walk on the BIT rendezvous program (synth.k2bit) with the richer move set BITPRIMS could not express.  [K2BIT]
`python k2bit_search.py ALIAS SECONDS SEED T [moves]`   state = scalar ADD program with order keys (so relocation across the whole commuting window is O(log n)); MOVEs are DERIVED (route cost c(a,b) from PATHS).
Objective (linear, exact marginal W[rank] per local Q, registers non-owned; owned chains untouched because owned-touching events are frozen); every ACCEPTED improving state and every 1500 accepts is re-verified by
bitword.emit + bitword.check (fast oracle) + exact price.  Moves (K2SEARCH vocabulary -> BIT):
  reloc   rendezvous relocation: ADD to ANY slot of its commuting window (slots next to events of d or s) with frame from the chain stops + path-interior frames   (K2SEARCH shift/ret)
  reroute 4-event commutator  d+=s  ==  [t+=s, d+=t, t+=s, d+=t]  through a third register t met at two other rendezvous                                  (K2SEARCH split / cadd+cdel)
  conj    2 ADDs on one dest (d+=a, d+=b) -> conjugation [a+=b, d+=a, a+=b]  (chain split of a fan-in)                                                      (K2SEARCH split)
  merge   consecutive [a+=b, d+=a, a+=b] -> [d+=a, d+=b]   (chain merge, inverse of conj)                                                                  (K2SEARCH kill/merge)
Candidates: CANDIDATE-<alias>-ksearch-<ts>.json.gz in ext/K2BIT ONLY if exact raw > base and fast oracle legal; then `tk accept`."""
import sys,os,time,math,random,bisect,json
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import bitword,bitscreen,bitval
from collections import Counter
OUT=os.path.dirname(os.path.abspath(__file__)) + '/ext/K2BIT'
INF=float('inf')
class S:
    def __init__(s,alias='bit5708',w=None):
        s.ctx=ctx=bitword.Ctx(alias); s.w=w or ctx.baseword; s.owned=set(s.w['owned']); s.base_w=s.w
        s.W,s.k0=bitscreen.weights(s.w,ctx); s.cc={}
        sc=bitword.scalars(s.w); s.start=s.w['start']; s.final=s.w['final']
        s.K=[];s.D=[];s.Sx=[];s.F=[];s.kind=[];s.alive=[]
        s.tk={};s.ti={}; s.gk=[]; s.gid=[]
        for i,e in enumerate(sc):
            s.new_event(e,float(i)*1024.0)
        s.nacc=0
        s.cost=sum(s.regcost(r) for r in range(len(s.start)) if r not in s.owned)
        s.paths=ctx.paths
        s.stat=Counter()
    def c(s,a,b):
        if a==b: return 0.0
        v=s.cc.get((a,b))
        if v is None:
            p=s.ctx.paths.get('%s:%s'%(a,b)); v=INF if not p else sum(s.W[r] for _,_,r in p); s.cc[(a,b)]=v
        return v
    def path_interior(s,a,b):
        if a==b or a is None or b is None: return ()
        p=s.ctx.paths.get('%s:%s'%(a,b)); return [x[1] for x in p[:-1]] if p else ()
    # ---- event store
    def new_event(s,e,key):
        i=len(s.K); s.K.append(key); s.kind.append(e[0]); s.alive.append(True)
        if e[0]=='ADD': s.D.append(e[1]); s.Sx.append(e[2]); s.F.append(e[3]); regs=(e[1],e[2])
        else: s.D.append(e[1]); s.Sx.append(-1); s.F.append(e[2]); regs=(e[1],)
        s.link(i); return i
    def link(s,i):
        key=s.K[i]
        regs=(s.D[i],s.Sx[i]) if s.kind[i]=='ADD' else (s.D[i],)
        for r in regs:
            if r not in s.tk: s.tk[r]=[]; s.ti[r]=[]
            j=bisect.bisect_left(s.tk[r],key); s.tk[r].insert(j,key); s.ti[r].insert(j,i)
        j=bisect.bisect_left(s.gk,key); s.gk.insert(j,key); s.gid.insert(j,i)
    def unlink(s,i):
        key=s.K[i]
        regs=(s.D[i],s.Sx[i]) if s.kind[i]=='ADD' else (s.D[i],)
        for r in regs:
            j=bisect.bisect_left(s.tk[r],key); assert s.ti[r][j]==i; del s.tk[r][j]; del s.ti[r][j]
        j=bisect.bisect_left(s.gk,key); assert s.gid[j]==i; del s.gk[j]; del s.gid[j]
    def kill(s,i): s.unlink(i); s.alive[i]=False
    def pfnf(s,r,key):
        j=bisect.bisect_left(s.tk[r],key) if r in s.tk else 0
        L=s.ti.get(r,[]); pf=s.F[L[j-1]] if j>0 else s.start[r]
        nf=s.F[L[j]] if j<len(L) else s.final[r]
        # note: event at exactly key (self) must be unlinked before calling
        return pf,nf
    def regcost(s,r):
        L=s.ti.get(r,[]); seq=[s.start[r]]+[s.F[i] for i in L]+[s.final[r]]
        return sum(s.c(a,b) for a,b in zip(seq,seq[1:]))
    # ---- windows / slots
    def window(s,i):
        d,sr,key=s.D[i],s.Sx[i],s.K[i]
        lo=-INF; hi=INF
        for r,test in ((d,lambda e:s.Sx[e]==d or s.kind[e]!='ADD'),(sr,lambda e:s.D[e]==sr or s.kind[e]!='ADD')):
            L=s.ti[r]; j=bisect.bisect_left(s.tk[r],key)
            a=j-1
            while a>=0 and not test(L[a]): a-=1
            if a>=0: lo=max(lo,s.K[L[a]])
            b=j+1
            while b<len(L) and not test(L[b]): b+=1
            if b<len(L): hi=min(hi,s.K[L[b]])
        return lo,hi
    def key_after(s,k):
        j=bisect.bisect_right(s.gk,k); nx=s.gk[j] if j<len(s.gk) else k+2048.0
        m=(k+nx)/2; return m if k<m<nx else None
    def key_before(s,k):
        j=bisect.bisect_left(s.gk,k); pv=s.gk[j-1] if j>0 else k-2048.0
        m=(k+pv)/2; return m if pv<m<k else None
    def slots(s,i,lo,hi,regs):
        out=[]
        for r in regs:
            L=s.ti[r]; ks=s.tk[r]; a=bisect.bisect_right(ks,lo); b=bisect.bisect_left(ks,hi)
            for j in range(a,b):
                if L[j]==i: continue
                out.append(('a',ks[j])); out.append(('b',ks[j]))
        if lo>-INF: out.append(('a',lo))
        if hi<INF: out.append(('b',hi))
        return out
    def slotkey(s,sl):
        t,k=sl; return s.key_after(k) if t=='a' else s.key_before(k)
    def frames_for(s,u,v,K,extra=()):
        pu,nu=s.pfnf(u,K); pv,nv=s.pfnf(v,K); cs={pu,nu,pv,nv}|set(extra)
        if len(cs)<12:
            cs|=set(s.path_interior(pu,nu))|set(s.path_interior(pv,nv))
        return [g for g in cs if g is not None]
    def ins_cost(s,r,K,g):
        pf,nf=s.pfnf(r,K); return s.c(pf,g)+s.c(g,nf)-s.c(pf,nf)
    # ---- moves; each returns (delta, undo) after APPLYING, or None.  delta in linear units.
    def mv_reloc(s,rng):
        i=s.rand_free_add(rng)
        if i is None: return None
        d,sr,f=s.D[i],s.Sx[i],s.F[i]; lo,hi=s.window(i)
        sl=s.slots(i,lo,hi,(d,sr)); 
        if not sl: return None
        K=None
        for _ in range(4):
            K=s.slotkey(rng.choice(sl))
            if K is not None: break
        if K is None: return None
        oldK=s.K[i]; s.unlink(i)
        jd0=bisect.bisect_left(s.tk[d],oldK); js0=bisect.bisect_left(s.tk[sr],oldK)
        pd,nd=s.pfnf(d,oldK); ps,ns=s.pfnf(sr,oldK)       # neighbours at old slot without x
        rem=s.c(pd,f)+s.c(f,nd)-s.c(pd,nd)+s.c(ps,f)+s.c(f,ns)-s.c(ps,ns)
        cands=s.frames_for(d,sr,K,extra=(f,))
        best=[]; 
        for g in cands:
            v=s.ins_cost(d,K,g)+s.ins_cost(sr,K,g)
            if v<INF: best.append((v,g))
        if not best: s.K[i]=oldK; s.link(i); return None
        best.sort(); m=best[0][0]
        pick=rng.choice([b for b in best if b[0]<=m+1e-13]) if rng.random()<0.5 else rng.choice(best[:max(1,min(len(best),3))])
        v,g=pick; delta=v-rem
        noop=(g==f and bisect.bisect_left(s.tk[d],K)==jd0 and bisect.bisect_left(s.tk[sr],K)==js0)
        if noop: s.K[i]=oldK; s.link(i); s.stat['reloc_noop']+=1; return None
        s.K[i]=K; s.F[i]=g; s.link(i)
        def undo(): s.unlink(i); s.K[i]=oldK; s.F[i]=f; s.link(i)
        return delta,undo,'reloc'
    def rand_free_add(s,rng):
        for _ in range(60):
            i=rng.randrange(len(s.K))
            if s.alive[i] and s.kind[i]=='ADD' and s.D[i] not in s.owned and s.Sx[i] not in s.owned: return i
        return None
    def near_regs(s,K,n=30):
        j=bisect.bisect_left(s.gk,K); out=set()
        for e in s.gid[max(0,j-n):j+n]:
            for r in (s.D[e],s.Sx[e]):
                if r>=0 and r not in s.owned: out.add(r)
        return list(out)
    def block_try(s,K,block,regs_cost,rng,nf=0):
        """block = list of (d,s,fset) -> pick frames (small product) minimising cost over regs_cost; returns best (cost_after, frames) for insertion at K (events not linked yet).  Greedy sequential with exact eval of final."""
        # candidate frames per event from current neighbours at K (events of block not yet inserted)
        cand=[]
        for (d,sr,_) in block:
            cs=s.frames_for(d,sr,K); cand.append(cs)
        best=None
        # greedy: insert sequentially choosing frame with minimal incremental exact cost over the registers, then 1 refinement pass
        ids=[]
        keys=[]
        # keys: strictly increasing just after K
        k=K
        for _ in block:
            nk=s.key_after(k) if not keys else (k+s.gk[min(len(s.gk)-1,bisect.bisect_right(s.gk,k))])/2
            keys.append(None)
        return None
    def mv_block(s,rng,kind):
        """generic block insertion for reroute/conj; replaces one or two events"""
        if kind=='reroute':
            i=s.rand_free_add(rng)
            if i is None: return None
            d,sr=s.D[i],s.Sx[i]; lo,hi=s.window(i); sl=s.slots(i,lo,hi,(d,sr))
            if not sl: return None
            K0=s.slotkey(rng.choice(sl))
            if K0 is None: return None
            old=[i]
            blocks=lambda t:[(t,sr),(d,t),(t,sr),(d,t)]
            tcands=[t for t in s.near_regs(K0) if t not in (d,sr)]
            if not tcands: return None
            t=rng.choice(tcands); block=blocks(t); frame_slots=[(0,2),(1,3)]
        else:
            return None
        return s.apply_block(rng,old,K0,block,frame_slots,'reroute')
    def apply_block(s,rng,old,K0,block,fslots,tag):
        # remove old events, then enumerate frame assignments per frame-slot group (events sharing a slot-group share a frame)
        saved=[(i,s.K[i],s.F[i]) for i in old]
        oldreg=set()
        for i in old: oldreg|={s.D[i],s.Sx[i]}
        regs=set(oldreg)
        for (a,b) in block: regs|={a,b}
        before=sum(s.regcost(r) for r in regs)
        for i in old: s.unlink(i)
        # keys for the 4 events right after K0
        keys=[]; k=K0
        for _ in block:
            keys.append(k); j=bisect.bisect_right(s.gk,k); nx=s.gk[j] if j<len(s.gk) else k+2048.0; k=(k+nx)/2
            if not (keys[-1]<k<nx): 
                for i,kk,ff in saved: s.link(i)
                return None
        # reorder: keys increasing; but each subsequent key computed after previous, relative to existing gk only; fine since k increases within the same gap
        # candidate frame sets per group
        groups=[]
        for grp in fslots:
            a,b=block[grp[0]]; groups.append(s.frames_for(a,b,K0))
        ids=[]
        for (a,b),kk in zip(block,keys):
            ids.append(s.new_event(['ADD',a,b,0],kk)) if False else None
        # create events (unlinked placeholder): use new_event then immediately set frames per assignment
        evid=[]
        for (a,b),kk in zip(block,keys):
            i=len(s.K); s.K.append(kk); s.kind.append('ADD'); s.alive.append(True); s.D.append(a); s.Sx.append(b); s.F.append(None); evid.append(i)
        def setframes(asg):
            for gi,grp in enumerate(fslots):
                for ei in grp: s.F[evid[ei]]=asg[gi]
        for i in evid:
            # link timelines
            pass
        best=None
        import itertools
        for asg in itertools.product(*[g[:12] for g in groups]):
            setframes(asg)
            for i in evid: s.link(i)
            c=sum(s.regcost(r) for r in regs)
            for i in evid: s.unlink(i)
            if best is None or c<best[0]-1e-13 or (abs(c-best[0])<=1e-13 and rng.random()<0.5): best=(c,asg)
        if best is None or best[0]>=INF:
            for i in evid: s.alive[i]=False
            for i,kk,ff in saved: s.link(i)
            return None
        setframes(best[1])
        for i in evid: s.link(i)
        delta=best[0]-before
        def undo():
            for i in evid: s.unlink(i); s.alive[i]=False
            for i,kk,ff in saved: s.alive[i]=True; s.K[i]=kk; s.F[i]=ff; s.link(i)
        for i in old: s.alive[i]=False
        return delta,undo,tag
    def mv_conj(s,rng):
        i=s.rand_free_add(rng)
        if i is None: return None
        d=s.D[i]; L=s.ti[d]; j=bisect.bisect_left(s.tk[d],s.K[i])
        # partner: next ADD in tl[d] with dest d, no reader of d in between
        for jj in range(j+1,min(len(L),j+6)):
            e=L[jj]
            if s.kind[e]!='ADD' or s.Sx[e]==d: break
            if s.D[e]==d and s.Sx[e] not in s.owned and s.Sx[e]!=s.Sx[i] and s.Sx[e]!=d:
                a,b=s.Sx[i],s.Sx[e]
                lo=max(s.window(i)[0],s.window(e)[0]) if False else None
                # place block at x's slot (before e's slot is fine: both commute past events between since no reader of d between)
                # require a,b not written/read in between conflicts: conj block touches a (writes) -> events between that read a or write b... be safe: slot right after the later event only if between events don't touch a,b
                ok=True
                for q in s.gid[bisect.bisect_left(s.gk,s.K[i]):bisect.bisect_right(s.gk,s.K[e])]:
                    if q in (i,e): continue
                    if s.kind[q]!='ADD' or s.D[q]==a or s.Sx[q]==a or s.D[q]==b or s.Sx[q]==b or s.D[q]==d or s.Sx[q]==d: ok=False;break
                if not ok: return None
                K0=s.key_before(s.K[e]) if rng.random()<0.5 else s.key_after(s.K[e])
                if K0 is None: return None
                block=[(a,b),(d,a),(a,b)]
                return s.apply_block(rng,[i,e],K0,block,[(0,),(1,),(2,)],'conj')
            if s.D[e]!=d: break
        return None
    def mv_merge(s,rng):
        # find consecutive triple in d's timeline: pattern events (a<-b),(d<-a),(a<-b) adjacent in global order
        for _ in range(40):
            j=rng.randrange(len(s.gid)-2); x,y,z=s.gid[j],s.gid[j+1],s.gid[j+2]
            if not(s.alive[x] and s.alive[y] and s.alive[z]): continue
            if not(s.kind[x]==s.kind[y]==s.kind[z]=='ADD'): continue
            if s.D[x]==s.D[z] and s.Sx[x]==s.Sx[z] and s.Sx[y]==s.D[x] and s.D[y]!=s.D[x] and s.D[y]!=s.Sx[x] and not({s.D[y],s.D[x],s.Sx[x]}&s.owned):
                a,b,d=s.D[x],s.Sx[x],s.D[y]
                return s.apply_block(rng,[x,y,z],s.K[x],[(d,a),(d,b)],[(0,),(1,)],'merge')
        return None
    def step(s,rng,T,moves):
        m=rng.choice(moves)
        if m=='reloc': r=s.mv_reloc(rng)
        elif m=='reroute': r=s.mv_block(rng,'reroute')
        elif m=='conj': r=s.mv_conj(rng)
        else: r=s.mv_merge(rng)
        s.stat[m+'_try']+=1
        if r is None: return None
        delta,undo,tag=r
        if delta<=1e-13 or (T>0 and rng.random()<math.exp(-delta/T)):
            s.cost+=delta; s.nacc+=1; s.stat[tag+('_neutral' if abs(delta)<=1e-13 else '_improve' if delta<0 else '_worse')]+=1; return delta
        undo(); s.stat[tag+'_rej']+=1; return None
    def scal(s):
        ids=[s.gid[j] for j in range(len(s.gid))]
        out=[]
        for i in ids:
            out.append(['ADD',s.D[i],s.Sx[i],s.F[i]] if s.kind[i]=='ADD' else [s.kind[i],s.D[i],s.F[i]])
        return out
    def verify(s):
        sc=s.scal()
        try: w2=bitword.emit(s.base_w,sc,s.ctx)
        except Exception as ex: return None,['emit:'+str(ex)[:80]]
        V=bitword.check(w2,s.ctx,3); return w2,V
def run(alias='bit5708',secs=240,seed=1,T=0.0,moves=('reloc','reroute','conj','merge'),save=None):
    st=S(alias); rng=random.Random(seed); t0=time.time(); base=bitword.price(st.base_w,st.ctx)['raw']
    base_cost=st.cost; print('start linear cost %.9f events %d'%(base_cost,len(st.gk)),flush=True)
    last=0; bestc=st.cost; log=Counter(); nver=0
    while time.time()-t0<secs:
        r=st.step(rng,T,moves)
        if r is not None and st.nacc-last>=1500:
            last=st.nacc; w2,V=st.verify(); nver+=1
            p=bitword.price(w2,st.ctx)['raw'] if w2 else None
            print('t=%.0fs acc=%d cost-base=%.3e verify=%s raw-base=%s ev=%d'%(time.time()-t0,st.nacc,st.cost-base_cost,'OK' if not V else V[:1],None if p is None else '%.3e'%float(p-base),len(st.gk)),flush=True)
            if V: print('ILLEGAL STATE: abort'); break
        if st.cost<bestc-1e-12:
            bestc=st.cost; w2,V=st.verify()
            if w2 is not None and not V:
                p=bitword.price(w2,st.ctx)
                print('IMPROVING linear %.3e exact raw-base %.3e'%(base_cost-st.cost,float(p['raw']-base)),flush=True)
                if p['raw']>base:
                    os.makedirs(OUT,exist_ok=True); path=OUT+'/CANDIDATE-%s-ksearch-%d.json.gz'%(alias,int(time.time())); bitword.save(w2,path); print('CANDIDATE',path,'raw',p['raw'],'admitted',float(p['admitted']),flush=True)
            else: print('improving linear but not legal/emit-failed',V[:1] if V else None,flush=True)
    w2,V=st.verify(); p=bitword.price(w2,st.ctx)['raw'] if w2 and not V else None
    print('DONE seed',seed,'T',T,'time %.0fs'%(time.time()-t0),'accepted',st.nacc,'legal',not V,'raw-base',None if p is None else float(p-base),'events',len(st.gk))
    print(dict(sorted(st.stat.items())))
    if save and w2 is not None and not V: bitword.save(w2,save); print('saved',save)
if __name__=='__main__':
    a=sys.argv; run(a[1] if len(a)>1 else 'bit5708',float(a[2]) if len(a)>2 else 240,int(a[3]) if len(a)>3 else 1,float(a[4]) if len(a)>4 else 0.0,tuple(a[5].split(',')) if len(a)>5 else ('reloc','reroute','conj','merge'),a[6] if len(a)>6 else None)
