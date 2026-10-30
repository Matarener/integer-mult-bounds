"""synth.spec -- word spec.  spec_from_word(word) extracts the parameters of a P104-family word; gen.generate(spec) rebuilds the value DAG from them.

A spec (schema tk-synth-spec/1, JSON) has two layers:
  PARAMETRIC layer (what a sampler draws):
    family     profile, meta (npub,nowned,live,ports,...), anchor word sha
    roots      8 root lifetimes of owned registers: reg, hyperplane H_k (normal u_k, 9-bit mask), COPY source helper, descent line l_k, targets (ADD consumers), sign pattern
    catalyst   the multi-lifetime owned register(s) that are not roots (id, INIT frame dim, lifetimes)
    owned_plan lifetimes list (reg, init_op, clear_op, kind) -- count/peak are PINNED by the verifier profile (convention)
    helpers    inventory: per helper (init_dim, final_dim, n_ops, first/last dim visited)
    sign_net   per Y_j: pattern L_j = {k : l_k perp p_j}, n delivery ops, delivery sources by frame dim (junk loads at dim 0 vs signal adds)
    schedule   hop policy ('exact'), event-order policy ('anchor')
    knobs      the values gen.py reads (defaults = identity)
    front      'anchor' (default: template layer) | 'generated' (FRONTGEN: synth/frontgen.py builds the whole value DAG from family + roots + data/sign_code.json; body/knobs ignored; word needs TK_FREE_BOUNDS=1)
  TEMPLATE layer (what is NOT yet generated from parameters; honest limit): body.ops = the value ops of the anchor in program order and body.hops its MOVE hop chains.
    The front end (collection of x's into the dim-8 hyperplanes, ~4000 ops), the Y <- helper junk loads (~7800 ops at dim 0) and the dirty-catalyst cancellations are the swarm's lineage;
    no unhinted generator exists for them (DESIGNER/NOTES: "GENX cannot yet rebuild A-rest/cleanup unhinted"; BUILD D1: negative).  Knobs re-parametrise the template (relabel, reorder, resign,
    re-frame, re-chain) rather than synthesise it.
"""
import sys,os,gzip,json,collections
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.dirname(HERE))
from tkcommon import *
import dag as D
SCHEMA='tk-synth-spec/1'
DEFAULT_KNOBS=dict(owned_perm=None,root_order=None,sign_flip=[],root_scale={},helper_init='anchor',helper_final='anchor',helper_seed=0,helper_frac=0.0,
                   extra_helpers=[],hop_policy='exact',hop_seed=0,hop_frac=0.0,descent_stage=[],event_order='anchor',order_seed=0,order_swaps=0,order_unsafe=False,order_window=400)
def _hyper_normal(basis):
    """normal vector u (9-bit mask) of a dim-8 frame: the unique nonzero u with <u,b>=0 for all basis vectors"""
    for u in range(1,512):
        if all(bin(u&b).count('1')%2==0 for b in basis): return u
def _spans_dim(basis): return len(basis)
def spec_from_word(word,profile=None,alias=None,keep_ops=True):
    path,w=load(word) if isinstance(word,str) else (None,word)
    if profile is None:
        profile=word if isinstance(word,str) and (word in DATA_PROFILES) else profile_of(w)[0]
    dg=D.decompile(w,forms=False)
    meta=dg['meta']; fr=dg['frames']; ops=dg['ops']; regs={int(k):v for k,v in dg['regs'].items()}
    n=meta['npub']; live=meta['live']; ports=meta['ports']
    dim=lambda f:len(fr[f])
    hops=collections.defaultdict(list)
    for i,r,fs in dg['schedule']['hops']: hops[r].append((i,fs))
    # ---- owned lifetimes / roots / catalyst
    lts=[];openl={}
    for i,o in enumerate(ops):
        if o[0]=='INIT': openl[o[1]]=dict(reg=o[1],init_op=i,init_frame=o[4],init_dim=dim(o[4]))
        elif o[0]=='CLEAR':
            l=openl.pop(o[1]); l['clear_op']=i; l['clear_frame']=o[4]; l['clear_dim']=dim(o[4]); lts.append(l)
    lts.sort(key=lambda l:l['init_op'])
    port_of_x={x:ports[k] for k,x in enumerate(live)}
    for l in lts:
        r=l['reg']; inner=[(i,ops[i]) for i in range(l['init_op'],l['clear_op']+1)]
        cp=[o for i,o in inner if o[0]=='COPY' and o[1]==r]
        l['copy_src']=cp[0][2] if cp else None
        l['consumers']=[i for i,o in inner if o[0]=='ADD' and o[2]==r]
        l['n_consumers']=len(l['consumers']); l['kind']='root' if l['init_dim']>=7 else 'catalyst'
        if l['kind']=='root':
            l['u']=_hyper_normal(fr[l['init_frame']]); l['line']=fr[l['clear_frame']][0] if l['clear_dim']==1 else None
            l['descent']=[(i,[dim(f) for f in fs]) for i,fs in hops.get(r,[])]
            l['n_ports_in']=sum(1 for x in live if bin(port_of_x[x]&l['u']).count('1')%2==0)
    roots=[l for l in lts if l['kind']=='root']; cats=[l for l in lts if l['kind']!='root']
    # ---- helpers
    help_=[r for r in range(n) if regs[r][0]=='helper']
    nops=collections.Counter(); dmin={};dmax={}
    for o in ops:
        for r in (o[1],o[2]):
            if r is not None and r<n and regs[r][0]=='helper':
                nops[r]+=1; d=dim(o[4]); dmin[r]=min(dmin.get(r,9),d); dmax[r]=max(dmax.get(r,0),d)
    hel={str(h):dict(init_dim=dim(regs[h][1]),final_dim=dim(regs[h][2]),n_ops=nops[h],dmin=dmin.get(h),dmax=dmax.get(h)) for h in help_}
    # ---- sign network (geometry: Y_j sees root k iff l_k perp p_j) and delivery census
    lines={l['reg']:l['line'] for l in roots}
    sn={}
    ycount=collections.Counter(); ydim=collections.defaultdict(collections.Counter)
    for o in ops:
        if o[0]=='ADD' and regs.get(o[1],[None])[0]=='Y' and o[2] is not None:
            ycount[o[1]]+=1; ydim[o[1]][dim(o[4])]+=1
    for x in live:
        y=x+112; p=port_of_x[x]
        pat=[l['reg'] for l in roots if l['line'] is not None and bin(p&l['line']).count('1')%2==0]
        sn[str(y)]=dict(port=p,pattern=pat,n_adds=ycount[y],adds_by_dim=dict(ydim[y]))
    spec=dict(schema=SCHEMA,anchor=dict(alias=alias or (word if isinstance(word,str) else None),path=path,profile=profile,sha=None),
        family=dict(meta=meta,profile=profile),
        roots=[{k:v for k,v in l.items() if k!='consumers'} for l in roots],catalyst=[{k:v for k,v in l.items() if k!='consumers'} for l in cats],
        owned_plan=[dict(reg=l['reg'],init_op=l['init_op'],clear_op=l['clear_op'],kind=l['kind']) for l in lts],
        helpers=dict(count=len(help_),hist_init={str(k):v for k,v in sorted(collections.Counter(h['init_dim'] for h in hel.values()).items())},
                     hist_final={str(k):v for k,v in sorted(collections.Counter(h['final_dim'] for h in hel.values()).items())},
                     credit_hist={str(k):v for k,v in sorted(collections.Counter(h['final_dim']-h['init_dim'] for h in hel.values()).items())},per=hel),
        sign_net=sn,schedule=dict(extra_helpers=[],hop_policy='exact',event_order='anchor',n_hop_chains=len(dg['schedule']['hops'])),
        knobs=dict(DEFAULT_KNOBS))
    if keep_ops:
        spec['body']=dict(ops=[[o[0],o[1],o[2],o[3],o[4]] for o in ops],hops=dg['schedule']['hops'],frames=dg['frames'],
                          regs={str(k):v for k,v in regs.items()},units=units_of(lts,len(ops)))
    return spec
def units_of(lts,nops):
    """program partition used by the reorder knob: 'gap' units (fixed) and the ROOT lifetimes (movable as a block, INIT..CLEAR inclusive).  Catalyst lifetimes stay inside gaps."""
    cuts=[(l['init_op'],l['clear_op']) for l in lts if l['kind']=='root']
    u=[];p=0
    for k,(a,b) in enumerate(cuts):
        if a>p: u.append(dict(kind='gap',lo=p,hi=a))
        u.append(dict(kind='root',lo=a,hi=b+1,reg=lts[[l['init_op'] for l in lts].index(a)]['reg'])); p=b+1
    if p<nops: u.append(dict(kind='gap',lo=p,hi=nops))
    return u
def save_spec(s,path): D.save(s,path)
def load_spec(path): return D.load(path)
