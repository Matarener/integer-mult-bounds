"""synth.flaggen -- FLAGS lane (see ../module docstring).  Scope [toolkit synth, X flag-plan design from principles].

Generates X flag plans (kernel format: one line per X_i, 7 (or L) vectors, first = p_i) from the problem data only
(ports, root normals u_k, root lines l_k, readers' feeder lines LN[j]); no swarm word is read.

Principles (module docstring s4, measured on #5811):
  G1 LOW PHASE (dims 2..h): X_i descends the intersection lattice of ITS OWN root hyperplanes: frame f_d lies in the
     intersection of H_k over S_d, S_d = K_i minus the first (d-1) roots of a drop order (K_i = roots with p_i in H_k),
     vectors preferably ports (port-spanned frames), ties broken toward frames another X already uses (X-X meetings).
  G2 HIGH PHASE (optional, gene `hi`=(k,j)): the next vector is the root line l_k, then the chain stays inside Q_j and inside
     as many Q_j' as possible of readers j' that also own a feeder line l_k (frames are line-holding Q-flats).
  G3 without a high phase the chain keeps climbing inside the remaining root hyperplanes.
genes: per X  {'drop': permutation of K_i, 'hi': None | [k, j], 'seed': int}.
"""
import random,itertools
par=lambda a,b:bin(a&b).count('1')%2

class Geo:
    def __init__(self,ports,U,LN,lines):
        self.P=list(ports); self.n=len(ports); self.U=list(U); self.LN=[list(x) for x in LN]; self.PS=set(ports)
        self.LK={k:[l for l in lines if par(l,u)==0][0] for k,u in enumerate(U)}
        self.K=[[k for k in range(len(U)) if par(p,U[k])==0] for p in ports]
        self.O=[[j for j in range(self.n) if par(ports[i],ports[j])==0] for i in range(self.n)]

def _ext(S,v): return S|{s^v for s in S}

def random_genes(g,seed,phigh=0.65):
    rng=random.Random(seed); G=[]
    for i in range(g.n):
        dr=g.K[i][:]; rng.shuffle(dr)
        hi=None
        if rng.random()<phigh:
            c=[(k,j) for j in g.O[i] for k in range(len(g.U)) if g.LK[k] in g.LN[j] and par(g.LK[k],g.P[j])==0]
            if c: hi=list(rng.choice(c))
        G.append({'drop':dr,'hi':hi,'seed':rng.randrange(1<<30),'h':rng.choice([3,4,4])})
    return G

def gen(g,G,L=7,meet=1.0):
    """genes -> list of flags (L vectors each).  Sequential over X: frames already used by earlier X are preferred (meetings)."""
    used={}   # frozenset frame -> count
    out=[]
    for i in range(g.n):
        ge=G[i]; rng=random.Random(ge['seed']); p=g.P[i]; fl=[p]; S={0,p}
        drop=ge['drop']; hi=ge['hi']; h=ge['h'] if hi else L
        def pick(cands):
            best=None; bs=None
            for v in cands:
                T=frozenset(_ext(S,v))
                sc=(meet*min(used.get(T,0),3), v in g.PS, len(g.PS&T), rng.random())
                if bs is None or sc>bs: bs=sc; best=v
            return best
        d=1
        while len(fl)<L and d<h:
            d+=1; keep=drop[d-1:] if len(drop)>d-1 else drop[-1:]
            cands=[v for v in range(1,512) if v not in S and all(par(v,g.U[k])==0 for k in keep)]
            if not cands: cands=[v for v in range(1,512) if v not in S]
            if hi:
                cq=[v for v in cands if par(v,g.P[hi[1]])==0]
                if cq: cands=cq
            v=pick(cands); fl.append(v); S=_ext(S,v); used[frozenset(S)]=used.get(frozenset(S),0)+1
        if hi and len(fl)<L:
            k,j=hi; l=g.LK[k]
            if l not in S: fl.append(l); S=_ext(S,l); used[frozenset(S)]=used.get(frozenset(S),0)+1
            co=[j2 for j2 in range(g.n) if l in g.LN[j2]]
            while len(fl)<L:
                cands=[v for v in range(1,512) if v not in S and par(v,g.P[j])==0 and all(par(x,g.P[j])==0 for x in S)]
                if not cands: cands=[v for v in range(1,512) if v not in S]
                # stay inside as many co-reader hyperplanes Q_j' as possible
                def qn(v): T=_ext(S,v); return sum(1 for j2 in co if all(par(x,g.P[j2])==0 for x in T))
                m=max(qn(v) for v in cands); cands=[v for v in cands if qn(v)==m]
                v=pick(cands); fl.append(v); S=_ext(S,v); used[frozenset(S)]=used.get(frozenset(S),0)+1
        while len(fl)<L:
            cands=[v for v in range(1,512) if v not in S]
            v=pick(cands); fl.append(v); S=_ext(S,v)
        out.append(fl)
    return out

def mutate(g,G,rng):
    G=[dict(x) for x in G]; i=rng.randrange(g.n); x=G[i]; r=rng.random()
    if r<0.3 and len(x['drop'])>1:
        dr=x['drop'][:]; a,b=rng.sample(range(len(dr)),2); dr[a],dr[b]=dr[b],dr[a]; x['drop']=dr
    elif r<0.55:
        c=[(k,j) for j in g.O[i] for k in range(len(g.U)) if g.LK[k] in g.LN[j] and par(g.LK[k],g.P[j])==0]
        x['hi']=None if (x['hi'] and rng.random()<0.4) or not c else list(rng.choice(c))
    elif r<0.7: x['h']=rng.choice([2,3,4,5])
    else: x['seed']=rng.randrange(1<<30)
    G[i]=x; return G,i

def write(flags,path):
    open(path,'w').write(''.join(' '.join(map(str,f))+'\n' for f in flags))

def load_problem(d):
    """d = a kernel work dir with ports.txt, roots_signs.txt, lines.txt (problem data written by the JOINTFEED/PARTIALTRIE glue)"""
    import os
    P=[int(x) for x in open(os.path.join(d,'ports.txt')).read().split()[1:]]
    U=[int(l.split()[0]) for l in open(os.path.join(d,'roots_signs.txt'))]
    LN=[list(map(int,l.split()[1:])) for l in open(os.path.join(d,'lines.txt'))]
    lines=sorted({l for x in LN for l in x})
    return Geo(P,U,LN,lines)

# ---------------- v2: BUTTERFLY low phase (G0, measured on #5811: 91/104 X have f2 = <p_i,p_j>, 23 mutual pairs; dim-3 meetings = the same pair, frames with 3-4 ports
# (zero-sum quads p_a+p_b+p_c+p_d = 0); dim-4 meetings = 3-5 X in frames with 7-8 ports).  Pairs are matched inside common root hyperplanes.
def pairing(g,seed,nonorth=True):
    """G0: mutual X pairs.  #5811: every pair is NON-orthogonal (p_i.p_j = 1: neither port is in the other's Q) with ~2.8 common roots and reader signs balanced
    (half agree: Haar atoms x_i +- x_j); weight = #common roots, restricted to non-orthogonal pairs when nonorth."""
    rng=random.Random(seed); free=set(range(g.n)); part={}
    E=sorted(((len(set(g.K[i])&set(g.K[j])),rng.random(),i,j) for i in range(g.n) for j in range(i+1,g.n) if not nonorth or par(g.P[i],g.P[j])==1),reverse=True)
    for w,_,i,j in E:
        if i in free and j in free: part[i]=j; part[j]=i; free-={i,j}
    return part

QUAD=0
def gen_bfly(g,G,seed=0,L=7,meet=1.0,part=None):
    part=part if part is not None else pairing(g,seed)
    used={}; out=[None]*g.n; pv={}   # pair -> shared low vectors (dims 3,4)
    def bump(S): used[frozenset(S)]=used.get(frozenset(S),0)+1
    for i in range(g.n):
        ge=G[i]; rng=random.Random(ge['seed']); j=part.get(i); p=g.P[i]; fl=[p]; S={0,p}
        hi=ge['hi']; h=ge['h'] if hi else L
        if j is not None:
            fl.append(g.P[j]); S=_ext(S,g.P[j]); bump(S)
            C=[k for k in g.K[i] if k in g.K[j]]
            key=(min(i,j),max(i,j))
            if key not in pv:
                low=[]; T=set(S)
                for d in (3,4):
                    if d>h: break
                    keep=C[:max(1,len(C)-(d-2))] if C else []
                    cands=([v for v in g.P if v not in T] if QUAD else []) or [v for v in g.P if v not in T and all(par(v,g.U[k])==0 for k in keep)] or [v for v in range(1,512) if v not in T and all(par(v,g.U[k])==0 for k in keep)] or [v for v in range(1,512) if v not in T]
                    if QUAD:   # G1 v3 (#5811: 66/86 f3 frames hold 4 ports = a zero-sum quad, f4 frames hold 7-8 ports): ports in span first, then common roots, then meetings
                        def cr(v): T2=_ext(T,v); return sum(1 for k in g.K[i] if all(par(x,g.U[k])==0 for x in T2))
                        best=max(cands,key=lambda v:(len(g.PS&_ext(T,v)),cr(v),meet*min(used.get(frozenset(_ext(T,v)),0),3),rng.random()))
                    else: best=max(cands,key=lambda v:(meet*min(used.get(frozenset(_ext(T,v)),0),3),len(g.PS&_ext(T,v)),rng.random()))
                    low.append(best); T=_ext(T,best); bump(T)
                pv[key]=low
            for v in pv[key]:
                if len(fl)<L and v not in S: fl.append(v); S=_ext(S,v)
        if hi and len(fl)<L:
            k,jj=hi; l=g.LK[k]
            if l not in S: fl.append(l); S=_ext(S,l); bump(S)
            co=[j2 for j2 in range(g.n) if l in g.LN[j2]]
            while len(fl)<L:
                inq=all(par(x,g.P[jj])==0 for x in S)
                cands=[v for v in range(1,512) if v not in S and (not inq or par(v,g.P[jj])==0)]
                def qn(v): T=_ext(S,v); return sum(1 for j2 in co if all(par(x,g.P[j2])==0 for x in T))
                m=max(qn(v) for v in cands); cands=[v for v in cands if qn(v)==m]
                v=max(cands,key=lambda v:(meet*min(used.get(frozenset(_ext(S,v)),0),3),v in g.PS,len(g.PS&_ext(S,v)),rng.random()))
                fl.append(v); S=_ext(S,v); bump(S)
        while len(fl)<L:
            keep=[k for k in g.K[i] if all(par(x,g.U[k])==0 for x in S)]
            cands=[v for v in range(1,512) if v not in S and all(par(v,g.U[k])==0 for k in keep[:1])] or [v for v in range(1,512) if v not in S]
            v=max(cands,key=lambda v:(meet*min(used.get(frozenset(_ext(S,v)),0),3),len(g.PS&_ext(S,v)),rng.random()))
            fl.append(v); S=_ext(S,v); bump(S)
        out[i]=fl
    return out
