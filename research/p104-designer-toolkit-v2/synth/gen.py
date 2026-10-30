"""synth.gen -- spec -> value DAG -> word.
generate(spec, knobs=None, seed=None) -> (dag, info)   dag is a dag.py DAG (tk-dag/1) ready for dag.realise; info has value_ok (delivered outputs == contract, symbolic Fraction replay), knob log.
build_word(spec, knobs=None)  -> (word, info)           realise with the spec's hop policy.
The value check (dag.apply_forms vs dag.required) is run before any legality question: a spec whose knobs break a value is rejected with the first bad registers (value-illegal), it is NOT
sent to the legaliser.  Knobs (spec['knobs'], see spec.DEFAULT_KNOBS):
  owned_perm {old:new}   permutation of the root owned register ids        root_order [perm]  order of the 8 root lifetimes in time (units of spec.body.units)
  sign_flip [reg]        negate a root (COPY q and all consumer q)           root_scale {reg:2^k}  root*c, consumers/c   (dyadic; scalar cost only)
  event_order 'anchor'|'swap'  order_swaps N, order_window W: N random commuting-neighbour moves (only ops with NO shared register, or both additive into one dst at one frame)
  helper_init/helper_final 'anchor'|'rand', helper_frac p, helper_seed s: with prob p per helper, initial -> random sub-basis of the anchor initial (credit up), final -> anchor final + random extra vectors (credit up)
  hop_policy 'exact'|'lazy'|'split', hop_frac p, hop_seed s: 'split' inserts a random intermediate stop into a fraction p of the MOVEs that span >= 2 dims
"""
import sys,os,random,copy,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from fractions import Fraction as Q
from tkcommon import *
import dag as D
from synth.spec import DEFAULT_KNOBS
def _span(b):
    s={0}
    for v in b: s|={x^v for x in s}
    return s
def _commutes(a,b):
    """neighbour events commute iff they share no register, or are two ADDs into one dst at one frame whose sources are not that dst (additive writes commute)"""
    ra={a[1],a[2]}-{None}; rb={b[1],b[2]}-{None}
    if not(ra&rb): return True
    return a[0]=='ADD' and b[0]=='ADD' and a[1]==b[1] and a[4]==b[4] and a[2]!=a[1] and b[2]!=b[1]
def generate(spec,knobs=None,verify=None):
    if spec.get('front')=='generated':        # FRONTGEN: unhinted front end + dim-0 junk loads (synth/frontgen.py); knobs do not apply to a generated body
        from synth import frontgen as FG
        dag,info=FG.build_dag(spec); info=dict(info,log=[('front','generated')],lazy=True); return dag,info
    K=dict(DEFAULT_KNOBS); K.update(spec.get('knobs',{})); K.update(knobs or {})
    B=spec['body']; ops0=B['ops']; N=len(ops0); meta=spec['family']['meta']; n=meta['npub']
    fr=[list(b) for b in B['frames']]; regs={int(k):list(v) for k,v in B['regs'].items()}
    log=[]
    _idx={}
    def fid(b):
        """basis -> frame table index (existing frame with the same span, else appended)"""
        if not _idx:
            for i,x in enumerate(fr): _idx[frozenset(_span(x))]=i
        k=frozenset(_span(b))
        if k not in _idx: fr.append(list(b)); _idx[k]=len(fr)-1
        return _idx[k]
    # ---- 1. event order: root lifetimes (movable units) then neighbour swaps
    units=B['units']; slots=[k for k,u in enumerate(units) if u['kind']=='root']; perm=list(range(len(units)))
    if K['root_order']:
        ro=K['root_order']
        for s,k in enumerate(slots): perm[k]=slots[ro[s]]
        log.append(('root_order',ro))
    order=[]
    for k in perm: u=units[k]; order+=range(u['lo'],u['hi'])
    if K['event_order']=='swap' and K['order_swaps']:
        rng=random.Random(K['order_seed']); done=0; unsafe=K.get('order_unsafe',False)
        for _ in range(K['order_swaps']):
            p=rng.randrange(len(order)-1); d=rng.randint(1,K['order_window']); a=ops0[order[p]]
            if a[0]!='ADD': continue
            q=p
            while q+1<len(order) and q-p<d:
                b=ops0[order[q+1]]
                if not(_commutes(a,b) or (unsafe and b[0]=='ADD')): break
                q+=1
            if q>p: order.insert(q,order.pop(p)); done+=1
        log.append(('order_swaps',done))
    inv={o:i for i,o in enumerate(order)}; inv[N]=N
    # ---- 2. owned relabel, sign, scale
    om={int(k):int(v) for k,v in (K['owned_perm'] or {}).items()}
    if om: log.append(('owned_perm',om))
    n0=n; kx=len(K['extra_helpers']); mp0=lambda r:om.get(r,r)
    mp=(lambda r:(lambda x:x+kx if x>=n0 else x)(mp0(r))) if kx else mp0
    flip=set(mp(r) for r in K['sign_flip']); scl={mp(int(r)):Q(c) for r,c in K['root_scale'].items()}
    ops=[]
    for i in order:
        op,r,s,q,f=ops0[i]; r=mp(r); s=mp(s) if s is not None else None
        if op in('ADD','COPY'):
            qq=Q(q)
            for x,inv_ in ((r,1),(s,-1)):
                if x in flip: qq=-qq
                if x in scl: qq=qq*scl[x] if x==r else qq/scl[x]
            q=str(qq)
        ops.append([op,r,s,q,f,None])
    if flip: log.append(('sign_flip',sorted(flip)))
    if scl: log.append(('root_scale',{k:str(v) for k,v in scl.items()}))
    if kx:
        regs={(r if r<n0 else r+kx):v for r,v in regs.items()}
        for t,(idim,fdim) in enumerate(K['extra_helpers']):
            rr=random.Random(K['helper_seed']*1000+t); fb=[]; sp={0}
            while len(fb)<fdim:
                v=rr.randrange(1,512)
                if v not in sp: fb.append(v); sp|={x^v for x in sp}
            regs[n+t]=['helper',fid(fb[:idim]),fid(fb)]
        n+=kx; meta=dict(meta,npub=n,public=n); log.append(('extra_helpers',K['extra_helpers']))
    # owned regs table entries are interchangeable ([owned,None,None]); permutation needs nothing there
    # ---- 3. helper start/final frames
    rng=random.Random(K['helper_seed']); nh=0
    if K['helper_init']!='anchor' or K['helper_final']!='anchor':
        for r in range(n):
            if regs[r][0]!='helper' or rng.random()>=K['helper_frac']: continue
            role,i0,f0=regs[r]; b0=fr[i0] if isinstance(i0,int) else i0; bf=fr[f0] if isinstance(f0,int) else f0
            if K['helper_init']=='rand' and len(b0)>0:
                keep=[v for v in b0 if rng.random()<0.5]; regs[r][1]=fid(keep); nh+=1
            if K['helper_final']=='rand' and len(bf)<9:
                s=_span(bf); ex=[]
                for _ in range(rng.randint(1,3)):
                    v=rng.randrange(1,512)
                    if v not in s and len(bf)+len(ex)<9: ex.append(v); s|={x^v for x in s}
                regs[r][2]=fid(list(bf)+ex) if ex else f0; nh+=1
        log.append(('helper_frames',nh))
    # ---- 4. hops (remapped to the new order) and the split knob
    hops=[]
    if K['hop_policy']!='lazy':
        for i,r,fs in B['hops']: hops.append([inv[i],mp(r),list(fs)])
    if K['hop_policy']=='split':
        rng2=random.Random(K['hop_seed']); added=0
        basis=lambda f: fr[f] if isinstance(f,int) else f
        hmap=collections.defaultdict(list)
        for i,r,fs in hops: hmap[(i,r)]=[x if isinstance(x,int) else fid(x) for x in fs]
        cur={r:regs[r][1] for r in range(n)}; newh=[]
        owned_cur={}
        for j,o in enumerate(ops):
            for r in ([o[1],o[2]] if o[0] in('ADD','COPY') else [o[1]]):
                if r is None or r>=n: continue
                chain=list(hmap.pop((j,r),[])); target=o[4]
                if not chain or chain[-1]!=target: chain.append(target)
                a=cur[r]; out=[]
                for b in chain:
                    if a!=b:
                        ba,bb=basis(a),basis(b); sa,sb=_span(ba),_span(bb)
                        if sa<sb and len(bb)-len(ba)>=2 and rng2.random()<K['hop_frac']:
                            k=rng2.randint(1,len(bb)-len(ba)-1); cand=list(bb); rng2.shuffle(cand); m=list(ba); sm=set(sa)
                            for v in cand:
                                if len(m)-len(ba)>=k: break
                                if v not in sm: m.append(v); sm|={x^v for x in sm}
                            out.append(fid(m)); added+=1
                    out.append(b); a=b
                cur[r]=a
                if out and out[-1]==target: out=out[:-1]      # realise inserts the final direct MOVE itself
                if out: newh.append([j,r,out])
        for (j,r),fs in hmap.items(): newh.append([j,r,fs])
        hops=newh
        log.append(('hop_split',added))
    # ---- 5. value check
    meta2=dict(meta)
    ok=True; bad=[]
    if verify is None: verify=bool(K['root_order'] or K['sign_flip'] or K['root_scale'] or K['event_order']!='anchor' or K['owned_perm'])
    if verify:
        F,_=D.apply_forms(ops,meta2); req=D.required(meta2)
        bad=[r for r in range(n+meta['nowned']) if F[r]!=req[r]]; ok=not bad
    dag=dict(schema=D.SCHEMA,meta=meta2,frames=fr,regs={str(k):v for k,v in regs.items()},ops=ops,values=[],schedule=dict(hops=hops),delivered_ok=ok,bad_regs=bad)
    return dag,dict(value_ok=ok,bad_regs=bad[:12],n_bad=len(bad),log=log,lazy=K['hop_policy']=='lazy')
def build_word(spec,knobs=None,verify=None):
    dag,info=generate(spec,knobs,verify)
    if not info['value_ok']: return None,info
    if spec.get('modes'):       # GENLEARN: `helpers: learned` / `schedule: learned` (synth/learned.py); value-neutral transforms of regs/hops, rng seeded by modes.seed
        from synth import learned as LN
        info['learned']=LN.postprocess(dag,spec,random.Random(spec['modes'].get('seed',0)))
    w,rep=D.realise(dag,'lazy' if info['lazy'] else None,(),verify=False)
    if spec.get('front')=='generated':
        n=dag['meta']['npub']; w['verifier_profile']=dict(public=n,owned_fields=dag['meta']['nowned'],lifetimes=sum(1 for o in dag['ops'] if o[0]=='INIT'),peak=1)
    return w,info
