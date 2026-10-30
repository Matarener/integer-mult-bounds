"""gensearch.space -- the SPEC space of the from-scratch generator (FRONTGEN + backgen + helpershare + compact).
A spec is a flat JSON dict; `normalize` zeroes the fields that are inactive for the chosen back end so equal behaviour = equal id (lineage key).
Fields (active when):
  back      star|gray|dilworth|grouped           back-end method (synth/backgen.py)
  helpers   star|shared                          residual-carrier mode (synth/helpershare.py); only with back in star/gray/dilworth (grouped has its own shared carriers)
  compact   none|cse|all                         value-preserving compaction (synth/compact.py): none, cse only, adds+cse+scale
  root_flip 0..255                               negate roots (S row k, C column k): a SIGN knob; kappa-neutral by design (control dimension)
  dil_seed, dil_iters                            (dilworth) annealing seed / iterations of backgen.optimise_steps
  grp_beta, grp_noise, grp_prune, grp_seed       (grouped) agglomerative merge key = popcount - beta*(|A|+|B|) + noise*U(0,1) [beta<=.009, noise 0 = backgen's key]; prune order of the selected-node set (sorted|reverse|random)
  hs_seed, hs_iters, hs_T0                       (shared) simulated annealing of the Y chains (helpershare.solve)
"""
import random,math,json,hashlib
BACKS=['star','gray','dilworth','grouped']; HELPERS=['star','shared']; COMPACTS=['none','cse','all']; PRUNES=['sorted','reverse','random']
DEFAULT=dict(back='grouped',helpers='star',compact='all',root_flip=0,dil_seed=1,dil_iters=30000,grp_beta=.005,grp_noise=0.0,grp_prune='sorted',grp_seed=0,hs_seed=1,hs_iters=200000,hs_T0=25.0)
ORDER=list(DEFAULT)
def normalize(s):
    s=dict(DEFAULT,**{k:v for k,v in s.items() if k in DEFAULT})
    if s['back']=='grouped': s['helpers']='star'
    if s['back']!='dilworth': s['dil_seed']=DEFAULT['dil_seed']; s['dil_iters']=DEFAULT['dil_iters']
    if s['back']!='grouped': s.update(grp_beta=DEFAULT['grp_beta'],grp_noise=0.0,grp_prune='sorted',grp_seed=0)
    elif s['grp_noise']==0 and s['grp_prune']!='random': s['grp_seed']=0
    if s['helpers']!='shared': s.update(hs_seed=DEFAULT['hs_seed'],hs_iters=DEFAULT['hs_iters'],hs_T0=DEFAULT['hs_T0'])
    s['dil_iters']=int(s['dil_iters']); s['hs_iters']=int(s['hs_iters']); s['root_flip']=int(s['root_flip'])%256
    s['grp_beta']=round(float(s['grp_beta']),4); s['grp_noise']=round(float(s['grp_noise']),3); s['hs_T0']=round(float(s['hs_T0']),2)
    return {k:s[k] for k in ORDER}
def sid(s): return hashlib.sha1(json.dumps(normalize(s),sort_keys=True).encode()).hexdigest()[:12]
def logu(rng,a,b): return math.exp(rng.uniform(math.log(a),math.log(b)))
def sample(rng):
    """prior: uniform over methods; numeric fields log-uniform / uniform; root_flip 0 half of the time"""
    s=dict(back=rng.choice(BACKS),helpers=rng.choice(HELPERS),compact=rng.choice(COMPACTS),root_flip=0 if rng.random()<.5 else rng.randrange(256),
           dil_seed=rng.randrange(10**4),dil_iters=int(logu(rng,2000,60000)),grp_beta=rng.choice([0.002,0.005,0.009,0.02,0.1,0.5,1.0,2.0]),grp_noise=0.0 if rng.random()<.4 else round(logu(rng,.3,12),3),
           grp_prune=rng.choice(PRUNES),grp_seed=rng.randrange(10**4),hs_seed=rng.randrange(10**4),hs_iters=int(logu(rng,20000,400000)),hs_T0=round(rng.uniform(4,40),2))
    return normalize(s)
def mutate(rng,s,sigma=1.0):
    """ES mutation: every active field changes with p~.35 (at least one); categorical = resample, numeric = gaussian in (log) space with step sigma"""
    s=dict(normalize(s)); act=[k for k in ORDER if k in active(s)]; ch=[k for k in act if rng.random()<.35] or [rng.choice(act)]
    for k in ch:
        if k=='back': s[k]=rng.choice(BACKS)
        elif k=='helpers': s[k]=rng.choice(HELPERS)
        elif k=='compact': s[k]=rng.choice(COMPACTS)
        elif k=='grp_prune': s[k]=rng.choice(PRUNES)
        elif k=='root_flip': s[k]=s[k]^(1<<rng.randrange(8))
        elif k in('dil_seed','grp_seed','hs_seed'): s[k]=rng.randrange(10**4)
        elif k=='dil_iters': s[k]=int(min(80000,max(1000,s[k]*math.exp(rng.gauss(0,.7*sigma)))))
        elif k=='hs_iters': s[k]=int(min(600000,max(10000,s[k]*math.exp(rng.gauss(0,.7*sigma)))))
        elif k=='hs_T0': s[k]=min(60,max(1,s[k]+rng.gauss(0,6*sigma)))
        elif k=='grp_beta': s[k]=min(3.0,max(.0005,s[k]*math.exp(rng.gauss(0,1.0*sigma))))
        elif k=='grp_noise': s[k]=max(0.0,(s[k] if s[k]>0 else .5)*math.exp(rng.gauss(0,.8*sigma))) if rng.random()>.15 else 0.0
    return normalize(s)
def active(s):
    a={'back','compact','root_flip'}
    if s['back']=='dilworth': a|={'dil_seed','dil_iters'}
    if s['back']=='grouped': a|={'grp_beta','grp_noise','grp_prune','grp_seed'}
    else: a|={'helpers'}
    if s['helpers']=='shared' and s['back']!='grouped': a|={'hs_seed','hs_iters','hs_T0'}
    return a
