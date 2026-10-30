"""synth.helpershare -- HELPER SHARING for the FRONTGEN word (HELPERSHARE, see ../module docstring).  Scope [toolkit synth, helper-sharing generator].

Used by frontgen when the spec says `front: generated, helpers: shared` (`tk synth --front-gen --helpers shared`).

WHAT IS SHARED.  The STAR design pays one private carrier r(j,i) (born at frame 0 -> L_i=<p_i> picks x_i -> Q_j=p_j^perp -> F9, shape (1,7,1)) for each of the 4992 residual pairs
(Y_j must subtract res_ji * x_i for the 48 ports orthogonal to p_j).  86% of the helper cost line.  Here Y_j gets a CHAIN of intermediate frames N_1 < N_2 < ... < Q_j (its main is fragmented, a
cheap uncredited cost) and the carrier for port i is born at 0 -> L_i -> N -> F9 where N is the FIRST frame of Y_j's chain that contains p_i.  Every Y whose chain contains N reads the SAME
carrier (the coefficient -res_ji is per ADD, free).  Carriers are keyed (N, i): the number of helpers is the number of distinct (first-containing frame, port) pairs.

THE ASSIGNMENT PROBLEM (exact cost model = entropy tax of the invoice; first-order kappa-free form, units 'r ln r'):
    choose for every Y_j a nested chain of frames inside Q_j  (dual form: A_1=<p_j> < A_2 < ... , N_t = A_t^perp, dim N_t = 9 - dim A_t)
    cost = sum over distinct carriers (N,i) of tax(1, dim N - 1, 9 - dim N)  +  sum_j tax_Y(chain)  [+ private leaf carriers at Q_j]
    tax(c_1..c_s) = R ln R - sum c ln c  (R = sum c)   -- a rank-r hop costs r^(1-kappa), the credit of the helper is R^(1-kappa); only the entropy deficit counts to first order.
`solve` is simulated annealing over the 104 Y chains with incremental (Counter-based) evaluation; the best plan is stored in data/helpershare_trie.json (like backgen_dilworth.json) and
`plan` loads it, re-derives the carriers and validates every pair.  The exact kappa is always measured on the built word (IncrWord), never on this model.

plan(ports, fixed=None) -> dict(ystops={j:[basis,...]}   Y_j intermediate frames, ascending, excluding Q_j
                               carriers=[dict(i, node=basis|None, users=[j,...])]   node None = private at Q_j (user list has one j)
                               info)
`fixed[j]` (optional) = list of frozenset-element frames Y_j already visits (other back ends); a chain not comparable with all of them is dropped for that Y (its pairs become private).
"""
import os,sys,json,math,random,collections,time
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
DATA=os.path.join(HERE,'data','helpershare_trie.json')
par=lambda a,b:bin(a&b).count('1')%2
def _H(r): return r*math.log(r) if r>0 else 0.0
def ccost(d):
    """tax of the carrier shape (1, d-1, 9-d): born 0 -> L_i -> N(dim d) -> F9"""
    return _H(9)-_H(d-1)-_H(9-d) if d>=2 else _H(9)-_H(8)
CC=[0.0]+[ccost(d) for d in range(1,10)]
def ycost(dims):
    prev=0; s=_H(8)
    for d in list(dims)+[8]: s-=_H(d-prev); prev=d
    return s
def span(basis):
    S={0}
    for v in basis:
        if v not in S: S|={x^v for x in S}
    return frozenset(S)
def perp_basis_of(vecs,nbits=9):
    """basis of {x in F2^nbits : <x,v>=0 for all v in vecs}"""
    ws=[]
    for v in vecs:                      # row-reduce vecs
        for w in ws:
            if v^w<v: v^=w
        if v: ws.append(v); ws.sort(reverse=True)
    # brute force nullspace (nbits<=9): greedy independent solutions
    sol=[]; sp={0}
    for x in range(1,1<<nbits):
        if x in sp: continue
        if all(par(x,v)==0 for v in ws): sol.append(x); sp|={y^x for y in sp}
    return sol
class _A:
    __slots__=('key','dim','om','basis','d','node')
class _Obj:
    """annealing state.  A = dual subspace (contains p_j), node = A^perp (primal frame)."""
    def __init__(s,ports):
        s.ports=ports; m=s.m=len(ports); s.cache={}
        s.orthmask=[sum(1<<i for i in range(m) if i!=j and par(ports[i],ports[j])==0) for j in range(m)]
        s.cnt=collections.defaultdict(collections.Counter); s.chain=[[] for _ in range(m)]; s.cost=0.0
        for j in range(m): s._apply(j,[],1)
    def mkA(s,basis):
        S={0}; b=[]
        for v in basis:
            if v not in S: b.append(v); S|={x^v for x in S}
        key=frozenset(S); a=s.cache.get(key)
        if a is None:
            a=_A(); a.key=key; a.basis=b; a.dim=len(b); a.d=9-a.dim
            a.om=sum(1<<i for i in range(s.m) if all(par(s.ports[i],x)==0 for x in b)); a.node=None; s.cache[key]=a
        return a
    def ycost_j(s,chain): return ycost([a.d for a in reversed(chain)])
    def _apply(s,j,chain,sign):
        d=0.0; rem=s.orthmask[j]
        for a in reversed(chain):                    # biggest A = smallest node first
            hit=rem&a.om
            if hit:
                cn=s.cnt[a.key]; w=CC[a.d]; h=hit
                while h:
                    b=h&-h; i=b.bit_length()-1; h^=b
                    if sign>0:
                        if cn[i]==0: d+=w
                        cn[i]+=1
                    else:
                        cn[i]-=1
                        if cn[i]==0: d-=w
                rem&=~hit
        d+=sign*bin(rem).count('1')*CC[8]+sign*s.ycost_j(chain); s.cost+=d
    def set_chain(s,j,chain):
        s._apply(j,s.chain[j],-1); s.chain[j]=chain; s._apply(j,chain,1)
    def rand_chain(s,j,rng):
        ports=s.ports; m=s.m; pj=ports[j]; r=rng.random()
        if r<0.5:
            j2=rng.randrange(m)
            if j2==j or not s.chain[j2]: return None
            ch2=s.chain[j2]; t=rng.randrange(len(ch2)); base=[a for a in ch2[t:] if pj in a.key]
            if not base: return None
            out=[]
            if rng.random()<0.6:
                a0=base[0]; tgt=rng.randint(2,max(2,a0.dim-1))
                if tgt<a0.dim:
                    els=list(a0.key); b=[pj]
                    for _ in range(40):
                        if len(span(b))>=2**tgt: break
                        b.append(rng.choice(els))
                    a1=s.mkA(b)
                    if a1.dim==tgt and a1.key<a0.key: out.append(a1)
            return out+base
        if r<0.8:
            dims=sorted(rng.sample([2,3,4,5,6],rng.randint(1,3))); b=[pj]; chain=[]
            for dd in dims:
                for _ in range(60):
                    if len(span(b))>=2**dd: break
                    b.append(ports[rng.randrange(m)])
                a=s.mkA(b)
                if a.dim==dd: chain.append(a)
                else: b=list(a.basis)
            return chain
        ch=list(s.chain[j])
        if not ch: return None
        if rng.random()<0.4: ch.pop(rng.randrange(len(ch))); return ch
        k=rng.randrange(len(ch)); a=ch[k]; lo=ch[k-1] if k>0 else None
        b=list(lo.basis if lo else [pj])+[ports[rng.randrange(m)]]
        for _ in range(60):
            if len(span(b))>=2**a.dim: break
            b.append(ports[rng.randrange(m)])
        na=s.mkA(b)
        if na.dim!=a.dim: return None
        if k+1<len(ch) and not na.key<ch[k+1].key: return None
        ch[k]=na; return ch
def solve(ports,iters=2000000,seed=1,T0=25.0,out=None,verbose=True):
    """simulated annealing over the Y chains; returns (cost, chains as lists of dual bases)"""
    rng=random.Random(seed); ob=_Obj(ports); m=ob.m; t0=time.time(); c0=ob.cost
    for it in range(iters):
        T=T0*(1-it/iters)+0.05; j=rng.randrange(m); ch=ob.rand_chain(j,rng)
        if ch is None: continue
        if not (all(ch[k].key<ch[k+1].key for k in range(len(ch)-1)) and all(ports[j] in a.key for a in ch)): continue
        old=ob.chain[j]; cc=ob.cost; ob.set_chain(j,ch); dc=ob.cost-cc
        if dc>0 and rng.random()>math.exp(-dc/T): ob.set_chain(j,old)
        if verbose and it%500000==0: print('helpershare SA',it,'cost %.0f (start %.0f) T %.2f %.0fs'%(ob.cost,c0,T,time.time()-t0),flush=True)
    res=dict(ports=list(ports),cost=ob.cost,start_cost=c0,iters=iters,seed=seed,T0=T0,chains={str(j):[list(a.basis) for a in ob.chain[j]] for j in range(m)})
    if out:
        old=None
        if os.path.exists(out):
            try: old=json.load(open(out))
            except Exception: old=None
        if old is None or old.get('ports')!=list(ports) or old['cost']>ob.cost:
            os.makedirs(os.path.dirname(out),exist_ok=True); json.dump(res,open(out,'w'))
            if verbose: print('wrote',out,'cost %.1f'%ob.cost)
        elif verbose: print('kept existing',out,'cost %.1f <= %.1f'%(old['cost'],ob.cost))
    return ob.cost,res
def _items(ports,chains_nodes,j,orth):
    """first node of Y_j's primal chain (ascending) that contains p_i, else None"""
    out={}
    for i in orth:
        p=ports[i]; nd=None
        for k,N in enumerate(chains_nodes):
            if p in N[1]: nd=k;break
        out[i]=nd
    return out
def plan(ports,fixed=None,data=None):
    """carriers + Y stops from the stored annealing result (data/helpershare_trie.json); falls back to PRIVATE carriers (the STAR design) if the file is missing or built for other ports"""
    m=len(ports); orth=[[i for i in range(m) if i!=j and par(ports[i],ports[j])==0] for j in range(m)]
    D=data
    if D is None and os.path.exists(DATA):
        try: D=json.load(open(DATA))
        except Exception: D=None
    if D is not None and D.get('ports')!=list(ports): D=None
    ystops={}; chains={}
    for j in range(m):
        nodes=[]
        if D is not None:
            for A in D['chains'].get(str(j),[]):
                assert all(par(x,ports[j])==0 for x in perp_basis_of(A))
                pb=perp_basis_of(A); nodes.append((tuple(pb),span(pb)))
            nodes.sort(key=lambda t:len(t[1]))      # ascending primal dim
            ok=all(nodes[k][1]<nodes[k+1][1] for k in range(len(nodes)-1))
            if ok and fixed and fixed.get(j):
                allf=[n[1] for n in nodes]+list(fixed[j]); allf.sort(key=len)
                ok=all(allf[k]<=allf[k+1] for k in range(len(allf)-1))
            if not ok: nodes=[]
        chains[j]=nodes; ystops[j]=[list(n[0]) for n in nodes]
    users=collections.defaultdict(list)           # (node key or ('Q',j), i) -> [j]
    for j in range(m):
        it=_items(ports,chains[j],j,orth[j])
        for i,k in it.items():
            key=(chains[j][k][1],i) if k is not None else (('Q',j),i)
            users[key].append(j)
    carriers=[]
    for (nk,i),us in sorted(users.items(),key=lambda t:(t[0][1],min(t[1]))):
        if isinstance(nk,tuple) and nk and nk[0]=='Q': carriers.append(dict(i=i,node=None,users=us))
        else:
            basis=None
            for j in us:
                for b,S in chains[j]:
                    if S==nk: basis=list(b);break
                if basis is not None: break
            carriers.append(dict(i=i,node=basis,users=us))
    ncost=sum(CC[len(span(c['node'])).bit_length()-1] if c['node'] else CC[8] for c in carriers)
    info=dict(carriers=len(carriers),private=sum(1 for c in carriers if c['node'] is None),shared=sum(1 for c in carriers if c['node'] is not None),
              pairs=sum(len(c['users']) for c in carriers),ystops=sum(len(v) for v in ystops.values()),model_cost=ncost+sum(ycost([len(span(b)).bit_length()-1 for b in v]) for v in ystops.values()),
              source=('stored plan' if D is not None else 'no stored plan: private carriers'))
    return dict(ystops=ystops,carriers=carriers,info=info)
def apply(bk,ctx):
    """turn a back-end plan `bk` (backgen.plan, residual = star: bk['rcar'] is None) into one with SHARED residual carriers: ctx = dict(ports, frames (list of bases), fid, Qf).
    Returns a new plan dict with rcar (one entry per distinct (node, port) carrier) and ysteps extended by the Y chain frames (merged with the steps the copies already use)."""
    assert bk['rcar'] is None,'residual carriers already shared by the back-end plan'
    ports=ctx['ports']; fid=ctx['fid']; Qf=ctx['Qf']; frames=ctx['frames']; m=len(ports)
    fixed={j:[span(frames[f]) for (f,_,_) in bk['ysteps'][j] if f!=Qf[j]] for j in range(m)}
    pl=plan(ports,fixed=fixed)
    ys={j:{f:[list(cr),list(rr)] for (f,cr,rr) in bk['ysteps'][j]} for j in range(m)}
    rcar=[]
    for c in pl['carriers']:
        rcar.append(dict(i=c['i'])); ri=len(rcar)-1
        for j in c['users']:
            f=fid(c['node']) if c['node'] else Qf[j]
            ys[j].setdefault(f,[[],[]])[1].append(ri)
    out=dict(bk); out['rcar']=rcar; out['ysteps']={j:[(f,v[0],v[1]) for f,v in ys[j].items()] for j in range(m)}
    out['info']=dict(bk['info'],helpers='shared',**{('hs_'+k):v for k,v in pl['info'].items()})
    return out
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument('--solve',action='store_true'); ap.add_argument('--iters',type=int,default=2000000); ap.add_argument('--seed',type=int,default=1); ap.add_argument('--T0',type=float,default=25.0)
    ap.add_argument('--spec',default=None); a=ap.parse_args()
    import dag as D_
    sp=D_.load(a.spec or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/ext/SYNTH/spec_5756.json.gz'); ports=sp['family']['meta']['ports']
    if a.solve: solve(ports,a.iters,a.seed,a.T0,out=DATA)
    else:
        p=plan(ports); print(p['info'])
