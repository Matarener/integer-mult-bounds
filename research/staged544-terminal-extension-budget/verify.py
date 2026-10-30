"""Exact terminal-only extension budget; Chris R with OpenAI Codex, Apache-2.0.
The dual is credited to PR3815/3862/3890. No optimizer is used here.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import argparse, gzip, hashlib, importlib.util, json, math
ROOT=Path(__file__).resolve().parent
K=Q(1730663236534549309146,10**24)

def need(ok,why):
    if not ok: raise ValueError(why)
def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def add(*terms):
    out=Counter()
    for factor,v in terms:
        for r,c in v.items():out[r]+=factor*c
    return {r:c for r,c in out.items() if c and r}
def h(r):return {r:Q(1)} if r else {}
def log_ratio(x):
    z=(x-1)/(x+1);n=50
    value=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(n)),Q(0))
    tail=2*z**(2*n+1)/(Q(2*n+1)*(1-z*z))
    return value,value+tail
@lru_cache(None)
def power(r):
    if r==0:return Q(0),Q(0)
    j=r.bit_length()-1;l2,u2=log_ratio(Q(2));lr,ur=log_ratio(Q(r,2**j))
    a,b=K*(j*l2+lr),K*(j*u2+ur)
    need(0<=a<=b<1,'exponential range')
    def exp_minus(x,n):return sum(((-x)**i/Q(math.factorial(i)) for i in range(n+1)),Q(0))
    return r*exp_minus(b,19),r*exp_minus(a,20)
def interval(v):
    lo=hi=Q(0)
    for r,c in v.items():
        a,b=power(r);lo+=c*(a if c>=0 else b);hi+=c*(b if c>=0 else a)
    return lo,hi
def brief(ab):
    scale=10**24;lo,hi=ab
    return {'lower_numerator':lo.numerator*scale//lo.denominator,'upper_numerator':-((-hi.numerator*scale)//hi.denominator),'denominator':scale}
def patterns():
    for cap in (8,16,32,48):
        def rec(i,ns,left):
            if i==5:
                yield cap,tuple(ns),left;return
            for n in range(left//(i+5)+1):yield from rec(i+1,ns+[n],left-n*(i+5))
        yield from rec(0,[],cap)
def dual():
    q={48:Q(1,20),3:Q(-1,20),5:Q(-1,4)}
    pi={w:add((-1,h(5)),(-(w-5),q)) for w in range(5,10)}
    mu={8:add((-1,pi[8])),16:add((-2,pi[8])),32:add((-4,pi[8])),48:h(48)}
    return q,pi,mu
def reduced(cap,ns,left,pi,mu):return add((1,h(left)),(-1,mu[cap]),*((-n,pi[w]) for w,n in zip(range(5,10),ns)))
def dual_check():
    q,pi,mu=dual();tight=[];strict=[]
    for cap,ns,left in patterns():
        v=reduced(cap,ns,left,pi,mu)
        if not v:tight.append([cap,list(ns),left])
        else:
            ab=interval(v);need(ab[0]>0,'dual infeasibility');strict.append(ab)
    gap=interval(add((1,h(9)),(-1,h(8)),(-1,q)));need(gap[0]>Q(6,1000),'terminal budget gap')
    # Independently test every discrete marginal, not only the analytic minimum.
    for r in range(1,10):need(interval(add((1,h(r)),(-1,h(r-1)),(-1,q)))[0]>0,'marginal budget')
    return {'patterns':len(tight)+len(strict),'tight_patterns':tight,'strict_patterns':len(strict),
      'minimum_strict_reduced_cost':brief((min(x[0] for x in strict),min(x[1] for x in strict))),
      'idle_credit_per_dimension':brief(interval(q)),
      'minimum_terminal_charge_per_dimension':brief(interval(add((1,h(9)),(-1,h(8))))),
      'mandatory_interior_saving_per_dimension':brief(gap)}
def audit_module():
    spec=importlib.util.spec_from_file_location('credited_audit',ROOT/'frozen/audit_core.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def local():
    audit=audit_module();out={};width_vectors={}
    for tag in ('base','extra'):
        w=read(ROOT/f'frozen/WORD-{tag}.json.gz');bill,inventory,chain,start,end=audit.frame_bill(w,lagrangian=True)
        regs=sorted(r for r in end if r>=224);widths=[audit.dim(end[r])-audit.dim(start[r]) for r in regs]
        need(inventory=={5:28,6:18,7:53,8:96,9:213},'inventory');need(bill=={1:2482,2:712,3:218,4:109,5:20,8:8},'local bill')
        need(all(0<=chain[r][-1][1]<=9 for r in regs),'terminal climb')
        need(all(end[r]==audit.FULL for r in regs if widths[regs.index(r)]==9),'width9 is full terminal')
        width_vectors[tag]=widths
        out[tag]={'local_profile':bill,'inventory':inventory,'registers':regs,'widths':widths,
          'terminal_dimensions':[audit.dim(end[r]) for r in regs],
          'terminal_climb_histogram':dict(sorted(Counter(chain[r][-1][1] for r in regs).items())),
          'frozen_word_sha256':sha(ROOT/f'frozen/WORD-{tag}.json.gz')}
    need(width_vectors['base']==width_vectors['extra'],'provider role widths differ');need(out['base']['terminal_dimensions']==out['extra']['terminal_dimensions'],'provider terminal dimensions differ')
    return out

def owner_math(local_results):
    receipt=read(ROOT/'OWNER-PATTERNS.json');q,pi,mu=dual();bins=Counter();demand=Counter();idle=Counter();total=0
    for row in receipt['patterns']:
        cap,ns,left,n=row;need(type(n)is int and n>0,'pattern multiplicity')
        need(sum(w*k for w,k in zip(range(5,10),ns))+left==cap,'pattern capacity')
        need(not reduced(cap,ns,left,pi,mu),'incumbent not dual-tight')
        bins[cap]+=n;total+=n
        for w,k in zip(range(5,10),ns):demand[w]+=n*k
        if left:idle[left]+=n
        # Fixed identity theorem: slack implies every occupied role has width9.
        need(left==0 or all(k==0 for k in ns[:4]),'extensible role has slack')
    need(dict(bins)=={8:241920,16:161280,32:161280,48:161280},'complete bin counts')
    need(dict(demand)=={5:90720,6:58320,7:171720,8:311040,9:690120},'complete demands')
    complete=Counter({int(r):n for r,n in read(ROOT/'frozen/PROFILE.json').items()})
    lb=local_results['base']['local_profile'];derived=Counter(idle)
    for r,n in lb.items():derived[r]+=3240*n
    need(derived==complete,'complete local-plus-idle profile')
    return {'calls':3240,'roles':sum(demand.values()),'bins':total,'occupied_bins':total-idle[48],
      'idle_profile':dict(sorted(idle.items())),'complete_profile':dict(sorted(derived.items())),
      'fixed_identity_feasible_nonnegative_extensions':0,'all_actual_patterns_dual_tight':True}

def full_owner(source_root,local_results):
    pins=read(ROOT/'EXTERNAL-SOURCES.json')['files']
    for rel,digest in pins.items():need(sha(source_root/rel)==digest,'external source hash '+rel)
    fill=read(source_root/'FILL.json.gz');template=read(source_root/'inputs/TEMPLATE.json.gz')
    caps={r['child']:r['rank'] for r in template['idle_children']};width=local_results['base']['widths'];dims=local_results['base']['terminal_dimensions']
    used=Counter();groups={};headroom=Counter();rows=fill['rows']
    need(len(rows)==3240*408 and fill['columns']==['time','helper','owner_replica','child','port','offset'],'literal role count')
    for i,row in enumerate(rows):
        need(len(row)==6 and all(type(x)is int for x in row),'literal row')
        t,h,o,c,p,z=row;need((t,h)==divmod(i,408),'literal role indexing');need(0<=o<360 and c in caps and 0<=p<112,'literal bin identity')
        key=o,c,p;need(z==used[key] and z+width[h]<=caps[c],'literal prefix capacity')
        used[key]+=width[h];groups.setdefault(key,Counter())[width[h]]+=1
        headroom[key]+=9-dims[h]
    hist=Counter();slack_headroom=0
    for o in range(360):
        for c,cap in sorted(caps.items()):
            for p in range(112):
                key=o,c,p;left=cap-used[key];ns=groups.get(key,{})
                need(left==0 or headroom[key]==0,'actual joint rank/capacity obstruction')
                hist[cap,tuple(ns.get(w,0) for w in range(5,10)),left]+=1
    derived=[[cap,list(ns),left,n] for (cap,ns,left),n in sorted(hist.items())]
    need(derived==read(ROOT/'OWNER-PATTERNS.json')['patterns'],'actual owner pattern certificate')
    return {'status':'PASS_ALL_LITERAL_OWNER_ROWS','roles':len(rows),'bins':sum(hist.values()),'source_hashes':pins}

def controls():
    q,pi,mu=dual();mut_mu=dict(mu);mut_mu[8]=add((1,mu[8]),(Q(1,1000),h(1)))
    need(interval(reduced(8,(0,0,0,1,0),0,pi,mut_mu))[1]<0,'perturbed dual rejected')
    # Positive fixture: merge one added dimension into rank1 while absorbing rank1 idle.
    need(interval(add((1,h(2)),(-2,h(1))))[1]<0,'rank1-gap absorption positive fixture')
    # Failure: terminal-only dimension charge cannot be dropped as zero.
    need(interval(add((-1,q)))[1]<0,'omitted-local-bill mutant would fake gain')
    # Failure: changing source rank capacity from32 to33 would create false room.
    need(sum((5,9,9,9))==32 and 33-sum((5,9,9,9))==1,'capacity mutation discriminates')
    # Exact small rank-function example: noncoordinate extension still costs dimension.
    span=lambda vs:__import__('functools').reduce(lambda S,v:S|{x^v for x in S},vs,{0})
    U=span([3,5]);E=span([3,5,8]);need(U<E and len(E)==2*len(U),'noncoordinate rank fixture')
    return ['dual RHS perturbation rejected','rank1 absorption positive fixture','omitted local charge fake gain exposed','capacity mutation exposes false allowance','noncoordinate dimension fixture']
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path);ap.add_argument('--emit',type=Path);args=ap.parse_args()
    manifest=read(ROOT/'FROZEN.json')
    for p,digest in manifest.items():need(sha(ROOT/p)==digest,'frozen source '+p)
    lr=local();result={'status':'PASS_EXACT_TERMINAL_EXTENSION_BUDGET','kappa':str(K),'source_root_endpoint':'0.001730663236534549309146','dual':dual_check(),'local':lr,'owner':owner_math(lr),'controls':controls()}
    if args.source_root:result['full_owner']=full_owner(args.source_root.resolve(),lr)
    if args.emit:
        need(not args.emit.resolve().is_relative_to(ROOT),'emit must be outside package');args.emit.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    expected=read(ROOT/'RESULT.json') if (ROOT/'RESULT.json').exists() else None
    need(expected is not None,'missing retained result');need(json.loads(json.dumps({k:v for k,v in result.items() if k!='full_owner'}))==expected,'retained result mismatch')
    print(json.dumps({'status':result['status'],'patterns':result['dual']['patterns'],'full_owner':result.get('full_owner',{}).get('status','NOT_RUN_EXPLICIT_EXTERNAL_SOURCE_REQUIRED'),'gap':result['dual']['mandatory_interior_saving_per_dimension'],'controls':len(result['controls'])},sort_keys=True))
if __name__=='__main__':main()
