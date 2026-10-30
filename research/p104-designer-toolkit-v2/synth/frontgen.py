"""synth.frontgen -- UNHINTED generator for the front end + dim-0 junk loads (FRONTGEN lane).  See ../module docstring.

build_dag(spec, opts=None) -> (dag, info)   dag = dag.py tk-dag/1 (MOVE-free value ops, lazy hops), info = counts + symbolic value check.
Nothing is copied from an anchor word's ops: the inputs are the literal ports/live ids, the spec's root family (u_k -> hyperplane H_k, descent line l_k) and the sign code
(data/sign_code.json = BOTTLENECK8 S,C, validated here against the geometry).  The construction is the 'STAR' design (each consumer gets PRIVATE carriers; no sharing yet):

 carrier c(k,i)  helper born at frame 0 -> MOVE to L_i=<p_i> -> c += X_i (equal frame) -> MOVE to H_k -> root_k += (S_ki/4) c ...        (front end: 8 x 52 carriers)
 root_k          owned, INIT at H_k (dim 8), 52 carrier ADDs, MOVE (owned, descending) to the line <l_k>, ADD into one private copy u(j,k) per reader j (C_jk != 0), CLEAR
 u(j,k)          helper born at 0 -> <l_k> -> u += 2*C2_jk*root_k -> MOVE to Q_j = p_j^perp (Y_j's final hyperplane); Y_j reads it there           (back end: templated-simple)
 residual r(j,i) Y_j needs -res_ji x_i for the 48 orthogonal i (res = C S - I = +-1/2 on all 48): private carrier born at 0 -> L_i -> += X_i -> Q_j, Y_j -= res_ji r
 Y_j             0 -> Q_j in ONE MOVE (rank 8, as the anchor's mains); X_i  L_i -> F9 in ONE MOVE (rank 8)
 junk (dim 0)    every helper holds its own initial value h for ever (never zero).  After all signal events Y_j holds y_j + x_j + sum_h J_jh h.  Because every helper is born at frame 0,
                 Y_j (frame 0) is co-present with every h at the very start: Y_j += -J_jh * h  (free ADDs) cancels ALL junk.  J is read off an exact symbolic dry run (solve, not copy).
 restore (F9)    T_k (one helper per root, born 0 -> F9 in one MOVE) accumulates the root content R_k = sum_i S_ki/4 c(k,i); u(j,k) -= C T_k, T_k -= R_k (T clean), u(j,k) += C T_k: u restored with
                 52+52+2 events per root instead of 52 per u.  c(k,i) -= X_i, r(j,i) -= X_i (X at F9).  Every helper ends at F9, X_i at F9, Y_j at Q_j.
Events are free but numerous (about 45k): run with TK_FREE_BOUNDS=1 (event cap 26000 is a package convention).
"""
import sys,os,json,collections,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from fractions import Fraction as Q
from tkcommon import *
import dag as D
par=lambda a,b:bin(a&b).count('1')%2
def _basis(vs):
    b=[]; sp={0}
    for v in vs:
        if v not in sp: b.append(v); sp|={x^v for x in sp}
    return b
def perp_basis(q,nbits=9):
    """basis of {x : <x,q>=0} (dim nbits-1), greedy over 1..511"""
    return _perp_vectors(q,nbits)
def _perp_vectors(q,nbits):
    t=(q&-q).bit_length()-1      # pivot bit
    return [ (1<<b) | ((1<<t) if (q>>b)&1 else 0) for b in range(nbits) if b!=t ]
def load_code():
    J=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','sign_code.json'))); return J['S4'],J['C2']
def _dimof(basis): return len(basis)
def build_dag(spec,opts=None):
    opts=opts or {}
    meta0=spec['family']['meta']; live=list(meta0['live']); ports=list(meta0['ports']); m=len(live)
    S4,C2=load_code(); K=len(S4)
    keep=opts.get('keep') or spec.get('keep')      # UNITGEN hook: sub-unit = subset of the sign code's 104 live indices (rows of C2, columns of S4); spec meta must list exactly those live/ports
    if keep: S4=[[row[i] for i in keep] for row in S4]; C2=[C2[j] for j in keep]
    # ---- root family from the spec (u_k, l_k); match each to its sign-code row by support
    sup=lambda k:{i for i in range(m) if S4[k][i]}
    roots=[]
    for r in spec['roots']:
        u=r['u']; H={i for i in range(m) if par(u,ports[i])==0}
        kk=[k for k in range(K) if sup(k)==H]
        assert len(kk)==1,'root %s: no unique sign-code row'%r['reg']
        roots.append(dict(k=kk[0],u=u,line=r['line'],reg=r['reg']))
    assert sorted(r['k'] for r in roots)==list(range(K))
    roots.sort(key=lambda r:r['k']); line=[r['line'] for r in roots]; U=[r['u'] for r in roots]
    # geometry law the sign code relies on: Y_j reads root k iff l_k perp p_j  (BOTTLENECK8, Lemma H)
    for j in range(m):
        assert {k for k in range(K) if C2[j][k]}=={k for k in range(K) if par(line[k],ports[j])==0},'sign code vs lines mismatch at %d'%j
    # residual res = C S - I (units of 1/4 * 2 = 1/2): res_ji = sum_k 2*C2[j][k] * S4[k][i]/4
    res=[[Q(sum(2*C2[j][k]*S4[k][i] for k in range(K)),4)-(1 if i==j else 0) for i in range(m)] for j in range(m)]
    TP=None
    if (opts.get('residual') or spec.get('residual'))=='taps':     # RESIDUAL lane: reverse-accumulating root descent absorbs part of the residual at the source (synth/residual.py)
        from synth import residual as RS
        TP=RS.plan(dict(ports=ports,U=U,line=line,S4=S4,C2=C2)); res=TP['res']
    usec=lambda k,i:bool(S4[k][i]) and (TP is None or TP['stage'][(k,i)] is not None)
    for j in range(m):
        for i in range(m):
            if par(ports[i],ports[j]) and res[j][i]!=0: raise AssertionError('sign code does not reproduce e_j on N_j')
    # ---- frames (interned by span) and register ids
    frames=[]; idx={}
    def fid(basis):
        b=_basis(basis); sp={0}
        for v in b: sp|={x^v for x in sp}
        key=frozenset(sp)
        if key not in idx: frames.append(list(b)); idx[key]=len(frames)-1
        return idx[key]
    F0=fid([]); L=[fid([p]) for p in ports]; H=[fid(perp_basis(u)) for u in U]
    Ln=[fid([line[k]]) for k in range(K)]; Qf=[fid(perp_basis(p)) for p in ports]; F9=fid([1<<b for b in range(9)])
    for k in range(K): assert par(U[k],line[k])==0
    X=list(live); Y=[x+112 for x in live]; used=set(X)|set(Y)
    free=[r for r in range(max(Y)+1) if r not in used]; nxt=[max(Y)+1]
    def newh():
        if free: return free.pop(0)
        r=nxt[0]; nxt[0]+=1; return r
    # allocate helpers
    carrier={(k,i):newh() for k in range(K) for i in range(m) if usec(k,i)}
    readers=[[(j,k) for k in range(K) if C2[j][k]] for j in range(m)]
    from synth import backgen as BG
    backname=(opts.get('back') or spec.get('back') or 'star').replace('generated:','')
    bk=BG.plan(backname,dict(C2=C2,fid=fid,line=line,Qf=Qf,ports=ports))       # back-end plan (copies + Y steps); 'star' = the original private-copy design
    hmode=(opts.get('helpers') or spec.get('helpers') or 'star')
    if hmode=='shared' and bk['rcar'] is None:  # HELPERSHARE: Y chains + shared residual carriers (synth/helpershare.py)
        from synth import helpershare as HS
        bk=HS.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf))
    if hmode=='hub' and bk['rcar'] is None:     # HUBGEN: annealed X flags + aggregated private hubs (synth/hubgen.py)
        from synth import hubgen as HG
        bk=HG.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf))
    if hmode=='ladder' and bk['rcar'] is None:  # HUBLADDER: hub-hub merge ladders with shared hubs (synth/hubladder.py)
        from synth import hubladder as HL
        bk=dict(bk); bk['rcar']=[]; bk['hub']=HL.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res))
    if hmode=='mainhub' and bk['rcar'] is None:  # MAINHUB: mains as hubs (X packets, Y-Y pairs, root copies as carriers), synth/mainhub.py
        from synth import mainhub as MHB
        bk=dict(bk); bk['rcar']=[]; bk['hub']=MHB.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res,line=line,F0=F0,F9=fid([1<<b for b in range(9)])))
        if bk['hub'].get('rootreads'):          # roots read shared S_k-signed trees: no star signal carriers (registers returned to the pool)
            free.extend(carrier.values()); free.sort(); carrier={}; usec=lambda k,i:False
    if hmode=='cse' and bk['rcar'] is None:      # SHAREDSUM: mainhub residual/root trees + shared signal relays (synth/sharedsum.py)
        from synth import sharedsum as SSM
        bk=SSM.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res,line=line,F0=F0,F9=fid([1<<b for b in range(9)]),C2=C2))
        if bk['hub'].get('rootreads'):
            free.extend(carrier.values()); free.sort(); carrier={}; usec=lambda k,i:False
    if hmode=='joint' and bk['rcar'] is None:    # JOINTFEED: mainhub residual/root trees + root copies as joint signal+residual feeders + SHAREDSUM relays (synth/jointfeed.py)
        from synth import jointfeed as JF
        bk=JF.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res,line=line,F0=F0,F9=fid([1<<b for b in range(9)]),C2=C2))
        free.extend(carrier.values()); free.sort(); carrier={}; usec=lambda k,i:False
    if hmode=='ptrie' and bk['rcar'] is None:    # PARTIALTRIE: JOINTFEED network + S_k-signed partial roots (trie pieces / root-tree hubs) read by Y-side registers (synth/partialtrie.py)
        from synth import partialtrie as PTR
        bk=PTR.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res,line=line,F0=F0,F9=fid([1<<b for b in range(9)]),C2=C2))
        free.extend(carrier.values()); free.sort(); carrier={}; usec=lambda k,i:False
    if hmode=='k2' and bk['rcar'] is None:       # KERNEL2: unified kernel k2 (plan format = JOINTFEED/PARTIALTRIE; synth/kernel2.py)
        from synth import kernel2 as K2
        bk=K2.apply(bk,dict(ports=ports,frames=frames,fid=fid,Qf=Qf,res=res,line=line,F0=F0,F9=fid([1<<b for b in range(9)]),C2=C2))
        free.extend(carrier.values()); free.sort(); carrier={}; usec=lambda k,i:False
    if bk['rcar'] is None:                      # star residual: one private carrier per (j,i) read at Q_j
        keys=[(j,i) for j in range(m) for i in range(m) if res[j][i]!=0]; bk['rcar']=[dict(i=i) for (j,i) in keys]
        for ri,(j,i) in enumerate(keys):
            st=bk['ysteps'][j]
            if st[-1][0]!=Qf[j]: st.append((Qf[j],[],[]))
            st[-1][2].append(ri)
    rc_j=collections.defaultdict(dict)           # residual carrier -> {j: frame} (every reader must have a nonzero residual on that port)
    for j,st in bk['ysteps'].items():
        for (f,cr,rr) in st:
            for ri in rr: assert res[j][bk['rcar'][ri]['i']]!=0; rc_j[ri][j]=f
    copy_reg=[newh() for _ in bk['copies']]; rc_reg=[newh() for _ in bk['rcar']]; by_k=collections.defaultdict(list)
    for ci,c in enumerate(bk['copies']): by_k[c['k']].append(ci)
    hubd=bk.get('hub') or dict(hubs=[],ops=[]); hub_reg=[newh() for _ in hubd['hubs']]
    T=[newh() for k in range(K)] if TP is None else []
    npub=nxt[0]; nown=K; OW=[npub+k for k in range(K)]
    ops=[]
    def add(dst,src,q,f): ops.append(['ADD',dst,src,str(Q(q)),f,None])
    def RG(t):   # MAINHUB generic register ref (kind, index)
        return {'Y':Y,'X':X,'H':hub_reg,'C':copy_reg}[t[0]][t[1]]
    for o in hubd.get('pre',[]): add(RG(o['dst']),RG(o['src']),o['coef'],o['frame'])
    RT=hubd.get('rootreads')
    if RT:    # MAINHUB root trees: every hub/X/Y op (ascending dim) BEFORE the roots, so X chains stay monotone; copies only after
        for o in sorted(hubd.get('seq',[]),key=lambda o:(o['dim'],o['h'])): add(RG(o['dst']),RG(o['src']),o['coef'],o['frame'])
    # ---- 1. front end + roots
    if TP is not None:
        assert backname=='star','residual taps: star back end only'
        copy_j={ci:j for j,st in bk['ysteps'].items() for (f_,cr,rr) in st for ci,cf in cr}
    for k in range(K):
        for i in range(m):
            if usec(k,i): add(carrier[(k,i)],X[i],1,L[i])
        ops.append(['INIT',OW[k],None,None,H[k],None])
        if TP is not None:
            nst=sum(1 for (kk,t) in TP['frames'] if kk==k)
            for i in range(m):
                if usec(k,i) and TP['stage'][(k,i)]==nst: add(OW[k],carrier[(k,i)],Q(S4[k][i],4),H[k])
            for t in range(nst-1,-1,-1):
                Ft=fid(TP['frames'][(k,t)])
                for ci in by_k[k]:
                    if TP['tap'][(copy_j[ci],k)]==t: add(copy_reg[ci],OW[k],bk['copies'][ci]['cin'],Ft)
                for i in range(m):
                    if usec(k,i) and TP['stage'][(k,i)]==t: add(OW[k],carrier[(k,i)],Q(S4[k][i],4),Ft)
            ops.append(['CLEAR',OW[k],None,None,fid(TP['frames'][(k,0)]),None])
            continue
        if RT:
            for src,q in RT[k]: add(OW[k],RG(src),q,H[k])
        else:
            for i in range(m):
                if S4[k][i]: add(OW[k],carrier[(k,i)],Q(S4[k][i],4),H[k])
        for ci in by_k[k]: add(copy_reg[ci],OW[k],bk['copies'][ci]['cin'],Ln[k])
        ops.append(['CLEAR',OW[k],None,None,Ln[k],None])
    for o in sorted(hubd.get('post',[]),key=lambda o:(o['dim'],o.get('h',0))): add(RG(o['dst']),RG(o['src']),o['coef'],o['frame'])   # SHAREDSUM: post-root ops (relay reads)
    # ---- 2. Y reads (back end, simple) + residual carriers
    for ri,c in enumerate(bk['rcar']): add(rc_reg[ri],X[c['i']],1,L[c['i']])
    # HUBGEN picks: Y_j / hub += -res_ji X_i at the X stop (ascending dimension keeps every chain monotone), restored at F9 below
    for o in sorted((o for o in hubd['ops'] if o['kind']=='pick'),key=lambda o:o['dim']):
        add(Y[o['j']] if o['hub'] is None else hub_reg[o['hub']],X[o['i']],-res[o['j']][o['i']],o['frame'])
    for o in ([] if RT else sorted(hubd.get('seq',[]),key=lambda o:(o['dim'],o['h']))):      # HUBLADDER: picks and child reads in one order (dim, height)
        if o['kind']=='g': add(RG(o['dst']),RG(o['src']),o['coef'],o['frame']); continue
        dst=Y[o['j']] if o['dst'] is None else hub_reg[o['dst']]
        if o['kind']=='pick': add(dst,X[o['i']],o['coef'],o['frame'])
        else: add(dst,hub_reg[o['child']],o['coef'],o['frame'])
    allst=sorted(((_dimof(frames[fr_]),j,fr_,cr,rr) for j in range(m) for (fr_,cr,rr) in bk['ysteps'][j]),key=lambda t:(t[0],t[1]))   # nested chains: ascending dimension is a valid global order
    for _,j,fr_,cr,rr in allst:
        for ci,cf in cr: add(Y[j],copy_reg[ci],cf,fr_)
        for ri in rr: add(Y[j],rc_reg[ri],-res[j][bk['rcar'][ri]['i']],fr_)
    # ---- 3. restore at F9 (T trick for u, X for carriers)
    for o in hubd['ops']:
        if o['kind']=='read': add(Y[o['j']],hub_reg[o['hub']],1,o['frame'])
    for k in (range(K) if TP is not None else ()):          # taps: restore each copy directly (it holds cin * the ports with stage > its tap)
        for ci in by_k[k]:
            t=TP['tap'][(copy_j[ci],k)]
            for i in range(m):
                if usec(k,i) and TP['stage'][(k,i)]>t: add(copy_reg[ci],carrier[(k,i)],-bk['copies'][ci]['cin']*Q(S4[k][i],4),F9)
    for o in hubd.get('prerestore',[]): add(RG(o['dst']),RG(o['src']),o['coef'],o['frame'])   # SHAREDSUM: undo relay reads while relays are still dirty (before the T trick)
    for k in (range(K) if TP is None else ()):
        if RT:
            for src,q in RT[k]: add(T[k],RG(src),q,F9)                      # T = h_T + root content (root-tree hubs still dirty)
        for i in (range(m) if not RT else ()):
            if S4[k][i]: add(T[k],carrier[(k,i)],Q(S4[k][i],4),F9)           # T = h_T + R_k   (carriers still dirty = h_c + x_i)
        for ci in by_k[k]: add(copy_reg[ci],T[k],-bk['copies'][ci]['cin'],F9)               # u = h_u - C h_T
        if RT:
            for src,q in RT[k]: add(T[k],RG(src),-q,F9)
        for i in (range(m) if not RT else ()):
            if S4[k][i]: add(T[k],carrier[(k,i)],-Q(S4[k][i],4),F9)          # T = h_T
        for ci in by_k[k]: add(copy_reg[ci],T[k],bk['copies'][ci]['cin'],F9)                # u = h_u
    for o in hubd.get('restore',[]): add(RG(o['dst']),RG(o['src']),o['coef'],o['frame'])   # MAINHUB: X undo, hub reads (parents first), picks; after the T trick (root-tree hubs dirty there)
    for (k,i),c in carrier.items(): add(c,X[i],-1,F9)
    for ri,c in enumerate(bk['rcar']): add(rc_reg[ri],X[c['i']],-1,F9)
    for o in sorted((o for o in hubd.get('seq',[]) if o['kind']=='rd' and o['dst'] is not None),key=lambda o:-o['h']):   # parents first: child still dirty
        add(hub_reg[o['dst']],hub_reg[o['child']],-o['coef'],F9)
    for o in hubd['ops']:
        if o['kind']=='pick' and o['hub'] is not None: add(hub_reg[o['hub']],X[o['i']],res[o['j']][o['i']],F9)
    for o in hubd.get('seq',[]):
        if o['kind']=='pick' and o['dst'] is not None: add(hub_reg[o['dst']],X[o['i']],-o['coef'],F9)
    # ---- 4. dim-0 junk loads: exact symbolic dry run, then Y_j += -J_jh * h at frame 0 (all helpers are born at frame 0)
    meta=dict(npub=npub,nowned=nown,live=live,ports=ports,public=npub,schema=meta0.get('schema'),owned_fields=nown)
    Fm,_=D.apply_forms(ops,meta); req=D.required(meta)
    helpers=set(range(npub))-set(X)-set(Y); pre=[]; nj=0; nonh=0
    for j in range(m):
        d={c:Fm[Y[j]].get(c,0)-req[Y[j]].get(c,0) for c in set(Fm[Y[j]])|set(req[Y[j]])}; d={c:v for c,v in d.items() if v}
        for c,v in sorted(d.items()):
            if c in helpers: pre.append(['ADD',Y[j],c,str(-v),F0,None]); nj+=1
            else: nonh+=1
    ops=pre+ops
    regs={}
    for r in range(npub):
        if r in X: regs[str(r)]=['X',L[X.index(r)],F9]
        elif r in set(Y): regs[str(r)]=['Y',F0,Qf[Y.index(r)]]
        else: regs[str(r)]=['helper',F0,F9]
    for o in OW: regs[str(o)]=['owned',None,None]
    for r in range(npub+K,npub+nown): regs[str(r)]=['owned',None,None]
    dag=dict(schema=D.SCHEMA,meta=meta,frames=frames,regs=regs,ops=ops,values=[],schedule=dict(hops=[]))
    Fm,_=D.apply_forms(ops,meta); req=D.required(meta)
    bad=[r for r in range(npub+nown) if Fm[r]!=req[r]]
    dag['delivered_ok']=not bad; dag['bad_regs']=bad[:20]
    info=dict(value_ok=not bad,n_bad=len(bad),bad_regs=bad[:12],npub=npub,helpers=len(helpers),carriers=len(carrier),copies=len(copy_reg),resid=len(rc_reg),junk_loads=nj,nonhelper_residue=nonh,
              n_ops=len(ops),design=backname,back=bk['info'],hub=len(hub_reg),hubinfo=hubd.get('info'),roles=dict(carrier=sorted(carrier.values()),copy=sorted(copy_reg),resid=sorted(rc_reg),T=sorted(T)))
    dag['delivered_ok']=info['value_ok']
    return dag,info
def build_word(spec,opts=None):
    dag,info=build_dag(spec,opts)
    if not info['value_ok']: return None,info
    w,rep=D.realise(dag,'lazy',(),verify=False)
    n=dag['meta']['npub']; w['verifier_profile']=dict(public=n,owned_fields=dag['meta']['nowned'],lifetimes=sum(1 for o in dag['ops'] if o[0]=='INIT'),peak=1)
    return w,info
def cost_lines(w):
    """invoice broken down by cost line: paid MOVE ranks by register ROLE (X mains / Y mains / helper climbs / owned descent), helper credits, stops, events.
    Weighted with the exact kappa weights r^(1-k) at k=kappa(w)."""
    import legal,price_exact as PX
    n=len(w['initial']); live=set(w['live']); fr=w['frames']; dim=[len(b) for b in fr]
    role=lambda r:'owned' if r>=n else ('X' if r in live else ('Y' if r-112 in live else 'helper'))
    paid=collections.defaultdict(collections.Counter); cred=collections.Counter(); ev=collections.Counter(); stops=collections.Counter()
    for e in w['program']:
        ev[e[0]]+=1
        if e[0]=='MOVE':
            ro=role(e[1]); paid[ro][abs(dim[e[3]]-dim[e[2]])]+=1; stops[ro]+=1
    for r in range(n):
        if role(r)=='helper': cred[dim[w['final'][r]]-dim[w['initial'][r]]]+=1
    return dict(paid={k:dict(v) for k,v in paid.items()},credit=dict(cred),stops=dict(stops),events=dict(ev))
def gap_report(wa,wg,profile=None,out=print,ig=None):
    """anchor wa vs generated wg: invoice lines at the anchor's kappa (kappa as the root of sum (T-P) r^(1-k); each line's contribution to the root = weight/|df/dk|)"""
    import price_exact as PX, legal
    ia=incr_eval(wa,profile); ig=ig or incr_eval(wg,profile)
    Ta,Pa=PX.invoice(dict(helpers=ia.hel,paid=ia.paid)); Tg,Pg=PX.invoice(dict(helpers=ig.hel,paid=ig.paid))
    k=PX.kappa(Ta,Pa); e=1-k
    wgt=lambda r:r**e
    dfdk=-(sum(n*r**e*math.log(r) for r,n in Ta.items())-sum(n*r**e*math.log(r) for r,n in Pa.items()))
    out('kappa anchor %.10f  generated %.10f  gap %.3e (%.1f%%)'%(ia.kappa,ig.kappa,ig.kappa-ia.kappa,100*(ig.kappa/ia.kappa-1)))
    out('per rank class r (credits T / paid P, counts x18 calls + outer part; weights r^(1-k) at the anchor kappa); dkappa = LINEARISED at the anchor (overshoots: the gap is large)')
    tot=0
    rows=[]
    for r in sorted(set(Ta)|set(Pa)|set(Tg)|set(Pg)):
        dT=(Tg.get(r,0)-Ta.get(r,0))*wgt(r); dP=(Pg.get(r,0)-Pa.get(r,0))*wgt(r)
        rows.append((r,Ta.get(r,0),Tg.get(r,0),Pa.get(r,0),Pg.get(r,0),dT,dP))
    for r,ta,tg,pa,pg,dT,dP in rows:
        if abs(dT)+abs(dP)<1e-9: continue
        out('rank %-3d credit(T) %7d -> %7d   paid(P) %7d -> %7d   dT %+12.1f dP %+12.1f  net %+12.1f  dkappa %+.3e'%(r,ta,tg,pa,pg,dT,dP,dT-dP,(dT-dP)/dfdk*-1 if False else (dT-dP)/(-dfdk)))
        tot+=dT-dP
    out('first-order total dkappa %+.3e (exact gap %+.3e)'%(tot/(-dfdk)*-1 if False else tot/(-dfdk),ig.kappa-ia.kappa))
    ca,cg=cost_lines(wa),cost_lines(wg)
    out('paid MOVEs by role (rank:count)\n  anchor   %s\n  generated %s'%(ca['paid'],cg['paid']))
    out('stops (MOVE count) by role  anchor %s  generated %s'%(ca['stops'],cg['stops']))
    out('helper credit histogram  anchor %s  generated %s'%(dict(sorted(ca['credit'].items())),dict(sorted(cg['credit'].items()))))
    out('events anchor %s  generated %s'%(ca['events'],cg['events']))
    line_swaps(wa,wg,out)
def incr_eval(w,profile=None):
    import incr
    return incr.IncrWord(w,profile=profile) if profile else incr.IncrWord(w)
def line_swaps(wa,wg,out=print):
    """exact kappa of the ANCHOR invoice with ONE cost line replaced by the generated word's (X mains, Y mains, helper stops (paid), helper credits, owned descent), and the cumulative chain.
    Lines are the invoice entries per rank class: T = outer + 18*credits, P = outer + 18*paid MOVE ranks."""
    import price_exact as PX
    ca,cg=cost_lines(wa),cost_lines(wg)
    def inv(paid_by_role,credit):
        T=collections.Counter(PX.TOUT); P=collections.Counter(PX.POUT)
        for r,n in credit.items(): T[r]+=PX.CALLS*n
        for ro,d in paid_by_role.items():
            for r,n in d.items(): P[r]+=PX.CALLS*n
        return dict(T),dict(P)
    base=PX.kappa(*inv(ca['paid'],ca['credit']))
    lines=[('X mains paid','paid','X'),('Y mains paid','paid','Y'),('helpers (stops paid + credits)','both','helper'),('owned descent paid','paid','owned')]
    out('line swapped into the anchor invoice (exact kappa)           kappa        d vs anchor')
    out('  anchor                                                     %.10f'%base)
    cur_p={k:dict(v) for k,v in ca['paid'].items()}; cur_c=dict(ca['credit'])
    for name,kind,ro in lines:
        p={k:dict(v) for k,v in ca['paid'].items()}; c=dict(ca['credit'])
        if kind in('paid','both'): p[ro]=cg['paid'].get(ro,{})
        if kind=='both': c=cg['credit']
        k1=PX.kappa(*inv(p,c))
        if kind in('paid','both'): cur_p[ro]=cg['paid'].get(ro,{})
        if kind=='both': cur_c=cg['credit']
        k2=PX.kappa(*inv(cur_p,cur_c))
        out('  %-24s alone %.10f (%+.3e)   cumulative %.10f (%+.3e)'%(name,k1,k1-base,k2,k2-base))
