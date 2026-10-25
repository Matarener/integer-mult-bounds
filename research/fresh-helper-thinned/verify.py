"""Combine the exact helper retiming with audited PR4440 query thinning.

Apache-2.0; substantial OpenAI Codex assistance. Source notices retained.
Normal replay freshly executes both source verifiers, then this new ledger.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA, TESTED = Q('.00300105'), Q('.003001052')
ROOT_LOW, ROOT_HIGH = Q('.0030010541830'), Q('.0030010541834')

def need(ok, why):
    if not ok: raise ValueError(why)

def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)

def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def encode(x):
    if isinstance(x,Q): return str(x)
    if isinstance(x,dict): return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [encode(v) for v in x]
    return x

def authenticate():
    seen=set()
    for row in read(HERE/'SOURCES.json')['files']:
        if row['usage']!='input': continue
        p=Path(row['path']);need(not p.is_absolute() and '..' not in p.parts and str(p) not in seen,'Canonical input')
        seen.add(str(p));actual=ROOT
        for part in p.parts:
            actual/=part;need(not actual.is_symlink(),'No source aliases')
        b=actual.read_bytes()
        need(sha256(b).hexdigest()==row['sha256'],'Changed source: '+str(p))
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Changed Git source blob')
    return len(seen)

def ceiling(E,T,P):
    signed={r:T[r]-P[r] for r in T.keys()|P.keys()}
    def margin(c):
        a,b=E.moment(T,1-c),E.moment(P,1-c)
        return a[0]-b[1],a[1]-b[0]
    need(margin(ROOT_LOW)[0]>0 and margin(ROOT_HIGH)[1]<0,'New complete profile root bracket')
    derivative=None
    for i in range(16):
        l,r=Q(i,320),Q(i+1,320);low=Q(0)
        for rank,n in signed.items():
            term=E.mul(E.power(rank,1-r if n>0 else 1-l),E.log_bounds(rank))
            low+=n*term[0 if n>0 else 1]
        derivative=low if derivative is None else min(derivative,low)
    upper=None
    for i in range(128):
        l,r=Q(1,20)+Q(19*i,2560),Q(1,20)+Q(19*(i+1),2560)
        hi=sum(n*E.power(rank,1-l if n>0 else 1-r)[1 if n>0 else 0] for rank,n in signed.items())
        upper=hi if upper is None else max(hi,upper)
    need(derivative>0 and upper<0,'Fixed-profile ceiling for every real 0<C<1')
    return {'root':[ROOT_LOW,ROOT_HIGH],'headroom':[ROOT_LOW-KAPPA,ROOT_HIGH-KAPPA],
            'decreasing_through_C':Q(1,20),'negative_derivative_upper':E.display((-derivative,)*2),
            'remaining_interval_moment_upper':E.display((upper,)*2)}

def run(execute_sources=True):
    count=authenticate()
    fresh=ROOT/'research/fresh-helper-boundary'
    query=ROOT/'research/query-thinned-controllers'
    sys.path.insert(0,str(fresh));F=load(fresh/'verify.py','audited_fresh_boundary_package')
    sys.path.insert(0,str(query));S=load(query/'verify.py','audited_query_thinning_package')
    source_query=read(query/'RESULT.json')
    if execute_sources:
        need(F.verify()==read(fresh/'RESULT.json'),'Fresh helper complete source replay')
        need(encode(S.run())==source_query,'PR4440 complete source replay')
    local=read(fresh/'NATIVE-RESULT.json.gz')
    H={int(k):v for k,v in local['helpers'].items()};N={int(k):v for k,v in local['paid'].items()}
    word=read(query/'COMPLEX-CONTROLLER.json')
    T,P=Counter(),Counter();full=thin=idle=0
    for event in word['physical_events']:
        if event[0]=='LOCAL':
            full+=1;T.update(H);P.update(N)
        elif event[0]=='QUERY_SHEAR':thin+=1;P[1]+=112
        elif event[0]=='IDLE':
            rank=8*len(event[2]);need(rank>0,'No nonzero charge for erased idle stage')
            P[rank]+=224;idle+=224
    for term in word['diagonal']:
        need(term[0] in (-1,1) and all(x in (0,1) for x in term[1:]),'Actual normalized main target')
        T[1+8*sum(term[1:])]+=112
    need((full,thin,idle)==(19,16,3584),'Every full, copied-query and whole-idle event')
    need(sum(T.values())==11560 and sum(P.values())==69273,'Complete new productive/call counts')
    need((sum(r*n for r,n in T.items()),sum(r*n for r,n in P.items()))==(260798,259998),'Preserve the exact surplus 800')
    # Independent substitution into the source invoice must give the same ledger.
    oldH={5:28,6:18,7:56,8:93,9:213};oldP={1:2487,2:713,3:224,4:102,5:20,8:8}
    ref=source_query['complex_invoice']
    for key,new,old_unit,new_unit in [('targets',T,oldH,H),('paid',P,oldP,N)]:
        check=Counter({int(k):v for k,v in ref[key].items()})
        check.subtract({k:19*v for k,v in old_unit.items()});check.update({k:19*v for k,v in new_unit.items()})
        need(+check==new,'Literal event count equals whole-call substitution: '+key)
    E=S.C.load(ROOT/'research/higher-moment-strictification/verify.py','combined_exact_intervals')
    root=ceiling(E,T,P)
    t,u,v,c,b=1-TESTED,Q(1,5),1024,20,21
    target=E.moment(T,t);alpha=E.divide(E.moment(P,t),target)
    other=S.C.load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','combined_separate_intervals')
    tl,th=other.moment(T,TESTED);pl,ph=other.moment(P,TESTED)
    need(tl>ph and max(tl,target[0])<=min(th,target[1]),'Independent exact raw-moment engine')
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))
    delta=E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,TESTED),target))
    alpha_gap=Q(1,1000000000);g,d=Q(97,100),Q(19,20)
    need(alpha[1]<1-alpha_gap and gamma[1]<g and delta[1]<d,'All three completely charged tail bounds')
    need(g**128<Q(1,16) and d**128<Q(1,16),'Both exact decay blocks')
    bound=1/(1+v*alpha_gap)+Q(4,2**32)
    need(bound<1 and c**64<b**63,'Strict paid completion and splitting')
    need(gamma[0]>Q(31,32),'The previous gamma limit fails and is explicitly replaced')
    # Apply PR4433's general logarithmic majorant at the actual new ambient rank.
    theta,power=Q(63,64),1000
    eta=E.scale(E.power(153,-v*TESTED),t)
    need(2*(20**v)**64<=(153**v)**63 and eta[0]>theta**power,'Shifted exit and complement capacity')
    need(E.power(153,v*TESTED)[1]<2**power,'Initial compiler range')
    gap=(TESTED-KAPPA)/7;need(gap.numerator==1,'Integer compiler grid')
    step=gap.denominator
    def passes(j):return (step*j+1)**power<2**j
    lo,hi=1,2
    while not passes(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if passes(mid):hi=mid
        else:lo=mid
    height=step*hi
    need(height>8*v and passes(hi) and not passes(hi-1),'Effective uniform rank integer inequality')
    # The changed local list is charged under an explicit larger fixed bound.
    local_scalar=max(x['real_scalar_allowance'] for x in local['native'].values())
    local_routes=(sum(N.values())+2*408)*1000
    need(local_scalar+local_routes<10**7,'Every new local scalar and monomial route fits')
    scalar_upper=19*10**7+16*1792+32*112*(len(word['physical_events'])+sum(len(word['boundaries'][k+'_program']) for k in ('left','right')))
    need(scalar_upper<10**9,'Retain the complete raw nonrecursive bound')
    bit=source_query['ordinary_BIT'];atom=Q(bit['atom']);ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599')
    admitted=Q(bit['admitted']);need(atom==Q('.004') and atom>ordinary>admitted>TESTED and atom<1-ordinary,'Complete stronger source BIT admission')
    L=S.C.load(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','combined_outer_ledger')
    params={'kappa':KAPPA,'tested_saving':TESTED,'complex_uniform_saving':KAPPA+6*gap,
            'b':KAPPA+5*gap,'a':KAPPA+4*gap,'q':KAPPA+3*gap,'bit_saving':admitted,
            'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
    outer=L.ledger(params);outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
    need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4,'Complete outer predicate inventory')
    need(all(x>0 for key in ('strict_checks','functional_checks') for x in outer[key].values()),'Every complete outer inequality')
    controls={}
    for name,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('unfunded_endpoint',{'kappa':TESTED}),('closed_epsilon',{'epsilon':Q(1)})]:
        bad=L.ledger(dict(params,**patch));failed=[k for k,x in bad['strict_checks'].items() if x<=0]
        need(failed,'Reject '+name);controls[name]=failed
    return encode({'status':'PASS_CONDITIONAL_FRESH_HELPER_QUERY_THINNED_KAPPA', 'kappa':KAPPA,'kappa_decimal':'0.00300105',
        'source_inputs':count,'source_heads':{'PR4440':'40e22a83ed660d3d6074c4f2dbf14bfb621eee51','helper_retiming':'ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9'},
        'gain_over_PR4440':KAPPA-Q('.00296'),'gain_over_PR4416':KAPPA-Q('.00268647'),
        'targets':dict(sorted(T.items())),'paid':dict(sorted(P.items())),'full_calls':full,'query_shears':thin,
        'paid_calls':sum(P.values()),'productive_fields':sum(T.values()),'fixed_profile_ceiling':root,
        'strictification':{'tested':TESTED,'power':v,'cutoff':c,'floor':b,'tail_offset':u,
            'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),
            'limits':[1-alpha_gap,g,d],'normalized_paid_upper':bound},
        'compiler':{'theta':theta,'logarithm_power':power,'eta':E.display(eta),'uniform_saving':params['complex_uniform_saving'],
            'gap':gap,'H':height,'N':'2^'+str(height),'integer_test_exponent':hi,'word_materialized':False},
        'nonrecursive':{'local_scalar_allowance':local_scalar,'local_route_bound':local_routes,'raw_upper':scalar_upper,'raw_budget':10**9},
        'ordinary_BIT':bit,'outer':outer,'negative_controls':controls,
        'scope':'Author-checked conditional construction; retained native/all-column, owned-erasure, whole-job, analytic, precision, tape, prime and recovery contracts. No selected promotion or formal/human acceptance.'})

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='Author the new arithmetic receipt from already-audited dependency receipts; normal replay freshly reruns both dependencies.')
    args=parser.parse_args();result=run(execute_sources=not args.write)
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==read(HERE/'RESULT.json'),'Exact combined receipt replay')
    print(json.dumps({k:result[k] for k in ('status','kappa_decimal','gain_over_PR4440','compiler')},sort_keys=True))
