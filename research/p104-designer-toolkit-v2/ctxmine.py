"""ctxmine -- CONTEXT-AWARE window superoptimiser (CTXMINE.

Why: PRIMMINE mined rewrite rules on TOY configurations and concluded "owned-Steinberg is never needed", but the real frontier step #5827 (RSPLIT) is exactly such a move.  Here the search runs ON THE REAL WORD:
a window of consecutive events keeps its real registers (public/owned/helper), real frames, real owned lifetimes (INIT..CLEAR) and the real later readers (the rest of the word is untouched, so every later read sees
the same values -- each move below is value-exact for the whole register file).  Search = bounded, tolerance-pruned closure of the GENERALISED local move set (every guard of prims lifted):
  H   hoist an ADD (any operands, OWNED allowed) to another gap with automatic Steinberg corrections, optionally re-framed  (= P1/P1c with the `pub` guard lifted)
  T   retime one event's frame (P2)
  SH  ADD hop over a SCALE of its source/target (coefficient change)            (value-exact, new)
  CH  ADD hop over a COPY that reads its target (correction into the copy)      (value-exact, new)
  CC  COPY(o<-x) hop over an ADD writing x (correction ADD(o<-v,b))             (= N2 of PRIMMINE)
Every child is priced by movekit.quick (trajectory-exact census, delta cache) and, for improvements, by evaluate().  A path is tagged LIFT when it uses an owned-operand hoist / SCALE / COPY hop, i.e. a move the
guarded basis (prims.p1_apply pub=nown) refuses; improving paths with no LIFT tag are re-derivations of the existing basis (beam artefacts), the others are candidate NEW families.
API:  import ctxmine as CM;  CM.search(v,lo,hi,...) -> list of results;  CM.window_list(w,kind,...) ;  CLI: python3 -B ctxmine.py WORD --window LO HI | --around I | --scan KIND ..."""
import os,sys,json,gzip,time,collections,itertools,random
from fractions import Fraction as Q
import movekit as M
from movekit import qs
import prims
from prims import Block

# ------------------------------------------------------------------ extra hop semantics
def _hop(S,i,g,pub,f=None):
    """move the ADD S[i] to gap g with corrections, incl. SCALE / COPY hops.  -> (S2,(lo,hi),tags set).  Values are re-verified by equiv() before a node is kept."""
    A=S[i]
    if A[0]!='ADD': raise Block('not add')
    t,s=A[1],A[2]; a=Q(A[3]); tags=set()
    if g==i or g==i+1: raise Block('noop')
    if t>=pub or s>=pub: tags.add('own')
    fa=A[4] if f is None else f
    cur=a
    if g>i+1:                      # move right: A ; B...  ->  B' ... ; A'
        out=[]
        for k in range(i+1,g):
            B=S[k]; op=B[0]
            if op=='SCALE' and B[1]==s: cur=cur/Q(B[2]); tags.add('SH'); out.append(B); continue            # ADD(a);SCALE(s,k) == SCALE(s,k);ADD(a/k)
            if op=='SCALE' and B[1]==t: cur=cur*Q(B[2]); tags.add('SH'); out.append(B); continue            # ADD(a);SCALE(t,k) == SCALE(t,k);ADD(a k)
            if op=='COPY' and B[2]==t and B[1] not in(t,s): out.append(B); out.append(['ADD',B[1],s,qs(cur),B[4]]); tags.add('CH'); continue   # ADD;COPY(o<-t) == COPY;ADD(o<-s,a)
            if op=='COPY' and (B[1] in(t,s) or B[2] in(t,s)) and not (B[2]==s and B[1] not in(t,s)): raise Block('copy')
            if op=='COPY': out.append(B); continue
            for (u,v,c,fb) in prims._corr(t,s,cur,B,+1): out.append(['ADD',u,v,qs(c),fb])
            out.append(B)
        S2=S[:i]+out+[['ADD',t,s,qs(cur),fa]]+S[g:]; lo,hi=i,i+len(out)
    else:                          # move left
        tail=[]
        for k in range(i-1,g-1,-1):
            B=S[k]; op=B[0]
            if op=='SCALE' and B[1]==s: cur=cur*Q(B[2]); tags.add('SH'); tail=[B]+tail; continue
            if op=='SCALE' and B[1]==t: cur=cur/Q(B[2]); tags.add('SH'); tail=[B]+tail; continue
            if op=='COPY' and B[2]==t and B[1] not in(t,s): tail=[B,['ADD',B[1],s,qs(-cur),B[4]]]+tail; tags.add('CH'); continue
            if op=='COPY' and (B[1] in(t,s) or B[2] in(t,s)) and not (B[2]==s and B[1] not in(t,s)): raise Block('copy')
            if op=='COPY': tail=[B]+tail; continue
            tail=[B]+[['ADD',u,v,qs(c),fb] for (u,v,c,fb) in prims._corr(t,s,cur,B,-1)]+tail
        S2=S[:g]+[['ADD',t,s,qs(cur),fa]]+tail+S[i+1:]; lo,hi=g,g+len(tail)
    return S2,(lo,hi),tags
def _copyhop(S,i,g,pub):
    """COPY(o<-x) at i moves to gap g across ADDs that write x (N2): COPY later needs ADD(o<-v,-b) after it, earlier +b.  Anything else touching o/x is a barrier (value re-verified by equiv)."""
    C=S[i]; o,x=C[1],C[2]
    if C[0]!='COPY' or g in(i,i+1): raise Block('x')
    if g>i+1:
        mid=[]; cor=[]
        for k in range(i+1,g):
            B=S[k]
            if B[0]=='ADD' and B[1]==x and B[2]!=o: cor.append(['ADD',o,B[2],qs(-Q(B[3])),B[4]])
            elif B[0] in('INIT','CLEAR','SCALE') and B[1] in(o,x): raise Block('copyhop')
            elif B[0] in('ADD','COPY') and (B[1]==o or B[2]==o or B[1]==x or B[2]==x) and not(B[0]=='ADD' and B[2]==x and B[1]!=o): raise Block('copyhop')
            mid.append(B)
        if not cor: raise Block('nothing')
        return S[:i]+mid+[list(C)]+cor+S[g:],(i,i+len(mid)+1+len(cor)),{'CC','own'}
    tail=[]; cor=[]
    for k in range(i-1,g-1,-1):
        B=S[k]
        if B[0]=='ADD' and B[1]==x and B[2]!=o: cor.insert(0,['ADD',o,B[2],qs(Q(B[3])),B[4]])
        elif B[0] in('INIT','CLEAR','SCALE') and B[1] in(o,x): raise Block('copyhop')
        elif B[0] in('ADD','COPY') and (B[1]==o or B[2]==o or B[1]==x or B[2]==x) and not(B[0]=='ADD' and B[2]==x and B[1]!=o): raise Block('copyhop')
        tail=[B]+tail
    if not cor: raise Block('nothing')
    return S[:g]+[list(C)]+cor+tail+S[i+1:],(g,g+len(tail)+1+len(cor)),{'CC','own'}

def equiv(Sa,Sb):
    """value-exact check of two scalar programs differing in one window: common prefix/suffix stripped, the rest executed symbolically on linear forms; all registers touched and not CLEARed in the window must agree"""
    n=min(len(Sa),len(Sb)); p=0
    while p<n and Sa[p]==Sb[p]: p+=1
    q=0
    while q<n-p and Sa[len(Sa)-1-q]==Sb[len(Sb)-1-q]: q+=1
    A=Sa[p:len(Sa)-q]; B=Sb[p:len(Sb)-q]
    def run(ev):
        st={}; dead=set()
        def get(r): return st.setdefault(r,{r:Q(1)})
        for e in ev:
            op=e[0]; r=e[1]
            if op=='INIT': st[r]={}; dead.discard(r)
            elif op=='CLEAR': dead.add(r)
            elif op=='SCALE':
                k=Q(e[2]); st[r]={z:c*k for z,c in get(r).items()}
            else:
                c=Q(e[3]) if op=='ADD' else Q(1); src=get(e[2]); d=dict(get(r)) if op=='ADD' else {}
                for z,x in src.items():
                    d[z]=d.get(z,0)+c*x
                    if d[z]==0: del d[z]
                st[r]=d
        return {r:{z:c for z,c in d.items() if c!=0} for r,d in st.items()},dead
    sa,da=run(A); sb,db=run(B)
    dead=da|db
    for r in set(sa)|set(sb):
        if r in dead: continue
        x=sa.get(r,{r:Q(1)}); y=sb.get(r,{r:Q(1)})
        if {z:c for z,c in x.items() if c}!={z:c for z,c in y.items() if c}: return False
    return True

# ------------------------------------------------------------------ frame candidates (local scans)
def near_frames(S,pos,regs,K=70,extra=(3,)):
    """frames at which the registers `regs` sit just before / after position pos (scan +-K), plus the frames of the 2 neighbouring events, plus extra"""
    out=[]
    for r in regs:
        for rng in (range(pos-1,max(-1,pos-K),-1),range(pos,min(len(S),pos+K))):
            for k in rng:
                e=S[k]
                if e[0] in('ADD','COPY'): hit=(e[1]==r or e[2]==r)
                else: hit=(e[1]==r)
                if hit:
                    f=e[2] if e[0] in('INIT','CLEAR') else e[-1]
                    if f not in out: out.append(f)
                    break
    for k in (pos-1,pos):
        if 0<=k<len(S) and S[k][0] in('ADD','COPY','SCALE'):
            f=S[k][-1]
            if f not in out: out.append(f)
    for f in extra:
        if f not in out: out.append(f)
    return out

# ------------------------------------------------------------------ move generator
def children(S,lo,hi,pub,D=5,fmax=4,kinds=('H','T','SH','CC')):
    """-> iterate (desc, S2, (lo2,hi2), tags).  events with lo<=i<hi may move to gaps in [lo-1,hi+1]; INIT/CLEAR are never moved"""
    n=len(S); gl=max(0,lo-1); gh=min(n,hi+1)
    for i in range(lo,min(hi,n)):
        e=S[i]; op=e[0]
        if op in('INIT','CLEAR'):
            if 'T' in kinds:       # owned start / end frame (INIT frame is free; CLEAR happens at its declared frame)
                for f in near_frames(S,i,[e[1]])[:fmax+2]:
                    if f!=e[2]: yield ('T',i,f),S[:i]+[[op,e[1],f]+list(e[3:])]+S[i+1:],(lo,hi),set()
            continue
        if 'T' in kinds:
            fs=near_frames(S,i,[e[1]] if op=='SCALE' else [e[1],e[2]])
            for f in fs[:fmax+2]:
                if f!=e[-1]:
                    S2=S[:i]+[e[:-1]+[f]]+S[i+1:]
                    yield ('T',i,f),S2,(lo,hi),set()
        if op=='ADD':
            for g in range(max(gl,i-D),min(gh,i+D)+1):
                if g in(i,i+1): continue
                gg=g
                fs=[None]+[f for f in near_frames(S,min(g,n-1),[e[1],e[2]])[:fmax] if f!=e[4]]
                for f in fs:
                    try: S2,(l2,h2),tg=_hop(S,i,gg,pub,f)
                    except (Block,ValueError,ZeroDivisionError,KeyError,IndexError): break
                    if len(S2)-len(S)>1: continue
                    tags=set(tg)|({'LIFT'} if tg else set())
                    yield ('H',i,g,f),S2,(min(lo,l2),max(hi+len(S2)-len(S),h2+1)),tags
        elif op=='COPY' and 'CC' in kinds:
            for g in range(max(gl,i-D),min(gh,i+D)+1):
                if g in(i,i+1): continue
                try: S2,(l2,h2),tg=_copyhop(S,i,g,pub)
                except (Block,ValueError,KeyError,IndexError): continue
                yield ('CC',i,g),S2,(min(lo,l2),max(hi+len(S2)-len(S),h2+1)),{'LIFT'}|tg

# ------------------------------------------------------------------ the search
def _key(S,lo,hi,pad=4):
    return hash(tuple(tuple(e) for e in S[max(0,lo-pad):hi+pad]))
def search(v,lo,hi,depth=3,tol=1e-5,beam=150,k0=None,must_lift=False,log=None,tl=60,fmax=3,D=5,kinds=('H','T','SH','CC'),stats=None,eps=1e-15):
    """bounded closure from the window [lo,hi) of v.S.  -> list of dict(kappa,gain,path,tags,lo,hi) for every priced node with kappa > k0+eps (and, if must_lift, a LIFT tag), best first.
    nodes with kappa < k0-tol are not expanded (RSPLIT's first step is exactly neutral); equal programs are visited once."""
    S0=v.S; pub=v.n; t0=time.time()
    k0=k0 if k0 is not None else M.quick(v,S0)[0]
    seen={_key(S0,lo,hi)}; front=[(k0,S0,(lo,hi),(),frozenset())]; found=[]; cnt=collections.Counter()
    for d in range(1,depth+1):
        nxt=[]
        for (k,S,(l,h),path,tags) in front:
            for desc,S2,(l2,h2),tg in children(S,l,h,pub,D=D,fmax=fmax,kinds=kinds):
                if time.time()-t0>tl: break
                key=_key(S2,l2,h2)
                if key in seen: continue
                seen.add(key); cnt['children']+=1
                try: k2,_=M.quick(v,S2)
                except Exception: k2=None
                if k2 is None: cnt['illegal']+=1; continue
                cnt['legal']+=1
                if not equiv(S0,S2): cnt['NOTEQUIV']+=1; continue
                tags2=tags|frozenset(tg); path2=path+(desc,)
                if k2>k0+eps and (not must_lift or 'LIFT' in tags2): found.append(dict(kappa=k2,gain=k2-k0,path=path2,tags=sorted(tags2),lo=l2,hi=h2,S=S2))
                if k2>=k0-tol: nxt.append((k2,S2,(l2,h2),path2,tags2))
        nxt.sort(key=lambda x:-x[0]); front=nxt[:beam]
        if log: log('   depth %d: %d legal children so far, frontier %d, improving %d [%.1fs]'%(d,cnt['legal'],len(front),len(found),time.time()-t0))
        if time.time()-t0>tl or not front: break
    found.sort(key=lambda x:-x['gain'])
    if stats is not None: stats.update(cnt)
    return found

def window_events(S,lo,hi): return [tuple(e) for e in S[lo:hi]]

# ------------------------------------------------------------------ window selection
def owned_windows(v,W=8,half=None):
    """windows centred on events with an owned operand (merge overlaps)"""
    S=v.S; n=v.n; half=half if half is not None else W//2; ids=[i for i,e in enumerate(S) if (e[0] in('ADD','COPY') and (e[1]>=n or e[2]>=n)) or (e[0] in('SCALE','INIT','CLEAR') and e[1]>=n)]
    return [(max(0,i-half),min(len(S),i-half+W)) for i in ids]
def hub_windows(v,W=8,topn=8,per=40,seed=1):
    from tkcommon import roles
    S=v.S; n=v.n; rl=roles(v.w); cnt=collections.Counter()
    for e in S:
        if e[0]=='ADD':
            for r in (e[1],e[2]):
                if r<n and rl(r)=='helper': cnt[r]+=1
    hubs=[r for r,_ in cnt.most_common(topn)]; rnd=random.Random(seed); out=[]
    for r in hubs:
        ids=[i for i,e in enumerate(S) if e[0]=='ADD' and r in(e[1],e[2])]
        for i in rnd.sample(ids,min(per,len(ids))): out.append((max(0,i-W//2),min(len(S),i-W//2+W)))
    return out
def random_windows(v,W=8,m=200,seed=2):
    rnd=random.Random(seed); n=len(v.S); return [(i,i+W) for i in sorted(rnd.sample(range(n-W),m))]

def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('word'); ap.add_argument('--window',nargs=2,type=int); ap.add_argument('--around',type=int)
    ap.add_argument('--W',type=int,default=8); ap.add_argument('--depth',type=int,default=3); ap.add_argument('--tol',type=float,default=1e-5); ap.add_argument('--beam',type=int,default=150)
    ap.add_argument('--tl',type=float,default=120); ap.add_argument('--must-lift',action='store_true'); ap.add_argument('--out'); a=ap.parse_args()
    from tkcommon import load
    p,w=load(a.word); w=M.pin(w); v=M.View(w)
    lo,hi=(a.window if a.window else (a.around-a.W//2,a.around-a.W//2+a.W))
    for _ in range(6): M.quick(v,v.S)
    log=lambda *x:print(*x,flush=True); st=collections.Counter()
    res=search(v,lo,hi,depth=a.depth,tol=a.tol,beam=a.beam,tl=a.tl,must_lift=a.must_lift,log=log,stats=st)
    k0=M.quick(v,v.S)[0]; log('base %.15f; %d improving nodes; stats %s'%(k0,len(res),dict(st)))
    for r in res[:10]: log('  %+.3e %s tags=%s'%(r['gain'],r['path'],r['tags']))
if __name__=='__main__': main()
