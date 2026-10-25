"""Joint helper entrance/exit/contact optimization, carried through a p16 controller.

Arithmetic scaffolding adapted from PR4447; native and compiler lineage retained.

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
sys.dont_write_bytecode = True
import native_joint as J

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA, TESTED = Q('.00302015'), Q('.003020155')
ROOT_LOW, ROOT_HIGH = Q('.0030201659770'), Q('.0030201659771')

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


def controller16(C):
    """Reconstruct the word and check its supplied exact factorization."""
    row=read(HERE/'CONTROLLER.json')
    need((row['kind'],row['pairs'],row['prefix_pairs'],row['ambient_rank'])==('complex',16,7,145),'Exact controller parameters')
    need(row['keep_mask']==C.keep_mask(16,7),'Exact retained idle mask')
    B,E=C.engines()
    coefficients,events,idles=E.controller(16,C.keep_mask(16,7))
    coefficients=C.specialize_complex(coefficients,C.thick_stages(16))
    rebuilt=[]
    for event in events:
        if event[0]=='LOCAL' and event[1] not in C.thick_stages(16):
            rebuilt.append(['QUERY_SHEAR',*event[1:]])
        elif event[0]=='IDLE':
            selected=[stage for stage in event[2] if stage in C.thick_stages(16)]
            if selected:rebuilt.append(['IDLE',event[1],selected])
        else:rebuilt.append(event)
    need(rebuilt==row['physical_events'],'Every emitted event freshly reconstructed')
    need(encode(C.inventories('complex',16,7,row['diagonal'],idles))==row['invoice'],'Fresh independent controller invoice')
    left=[[Q(x) for x in r] for r in row['boundaries']['left']]
    right=[[Q(x) for x in r] for r in row['boundaries']['right']]
    diagonal=[tuple(k) for k in row['diagonal']]
    actual={k:B.matrix_multiply(B.matrix_multiply(left,m),right) for k,m in coefficients.items()}
    expected={k:[[Q(i==j and diagonal[i]==k) for j in range(32)] for i in range(32)] for k in set(diagonal)}
    need(actual==expected,'Every p16 rational Laurent coefficient and absolute central sign')
    need(C.replay_events(row['physical_events'],16,'complex')==coefficients,'Independent literal p16 physical word')
    for name,matrix in [('left',left),('right',right)]:
        need(E.scalar_program(matrix)==row['boundaries'][name+'_program'],'Exact scalar boundary programs')
    bad=json.loads(json.dumps(row['physical_events']))
    next(e for e in bad if e[0]=='QUERY_SHEAR')[3]=True
    need(C.replay_events(bad,16,'complex')!=coefficients,'Wrong query orientation rejected')
    bad=json.loads(json.dumps(row['physical_events']))
    next(e for e in bad if e[0]=='QUERY_SHEAR')[0]='LOCAL'
    need(C.replay_events(bad,16,'complex')!=coefficients,'An unpaid full stage is rejected')
    return row


def replay_dependencies():
    """Fresh checks of the inherited physical primitives and unchanged BIT side.

    The superseded p17 complex arithmetic is not a premise of the new p16 word.
    Its replacement is freshly reconstructed by controller16 below.
    """
    authenticate()
    query=ROOT/'research/query-thinned-controllers'
    sys.path.insert(0,str(query));S=load(query/'verify.py','joint_source_bit')
    C=S.C;C.engines()
    source=read(query/'RESULT.json')
    need(S.native_contacts()==source['native'],'Retained physical main contacts, binary charts and owned-query lowering')
    row=C.run('bit',16,7)
    need(encode(row)==read(query/'BIT-CONTROLLER.json'),'Fresh complete binary controller')
    B,_=C.engines();coefficients,_,_=B.physical_controller(16,C.keep_mask(16,7))
    coefficients=C.specialize_bit(coefficients,C.thick_stages(16))
    need(C.replay_events(row['physical_events'],16,'bit')==coefficients,'Independent literal binary physical word')
    need(encode(row['invoice'])==source['bit_invoice'],'Complete source-bound BIT invoice')
    E=C.load(ROOT/'research/higher-moment-strictification/verify.py','joint_bit_intervals')
    tail=S.tail(E,row['invoice'],Q('.00346'),Q('.003459'),17,18,Q(1,250000))
    need(encode(tail)==source['bit_strictification'],'Exact paid BIT tails and finite compiler')
    bit=source['ordinary_BIT'];before,after,atom=map(Q,(bit['before_cover'],bit['after_cover'],bit['atom']))
    ordinary=(1-atom)*after+atom*Q('.0000384599')
    need(before>after and 2**26>256/(before-after),'Explicit delayed-cover exponent gap and prime allowance')
    need(atom>ordinary>Q(bit['admitted']) and atom<1-ordinary,'Complete ordinary BIT conversion and stock')
    return {'status':'PASS_RETAINED_NATIVE_AND_BIT_DEPENDENCIES','native':source['native'],'ordinary_BIT':bit}

def run(execute_sources=True):
    count=authenticate()
    fresh=ROOT/'research/fresh-helper-boundary'
    query=ROOT/'research/query-thinned-controllers'
    sys.path.insert(0,str(fresh));F=load(fresh/'verify.py','audited_fresh_boundary_package')
    sys.path.insert(0,str(query));S=load(query/'verify.py','audited_query_thinning_package')
    source_query=read(query/'RESULT.json')
    if execute_sources: replay_dependencies()
    local=J.run() if execute_sources else read(HERE/'NATIVE.json.gz')
    need(json.loads(json.dumps(local))==read(HERE/'NATIVE.json.gz'),'Fresh exact missing-span native replay')
    H={int(k):v for k,v in local['helpers'].items()};N={int(k):v for k,v in local['paid'].items()}
    print('CHECK_JOINT_CONTROLLER',flush=True)
    word=controller16(S.C)
    print('PASS_JOINT_CONTROLLER',flush=True)
    need(json.loads(json.dumps(word))==read(HERE/'CONTROLLER.json'),'Fresh p16 controller and literal boundary replay')
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
    need((full,thin,idle)==(18,15,3360),'Every full, copied-query and whole-idle event')
    need(sum(T.values())==10928 and sum(P.values())==64620,'Complete new productive/call counts')
    need((sum(r*n for r,n in T.items()),sum(r*n for r,n in P.items()))==(239886,239134),'Preserve the exact surplus 752')
    # Independent substitution into the source invoice must give the same ledger.
    oldH={5:28,6:18,7:56,8:93,9:213};oldP={1:2487,2:713,3:224,4:102,5:20,8:8}
    ref=word['invoice']
    for key,new,old_unit,new_unit in [('targets',T,oldH,H),('paid',P,oldP,N)]:
        check=Counter({int(k):v for k,v in ref[key].items()})
        check.subtract({k:18*v for k,v in old_unit.items()});check.update({k:18*v for k,v in new_unit.items()})
        need(+check==new,'Literal event count equals whole-call substitution: '+key)
    E=S.C.load(ROOT/'research/higher-moment-strictification/verify.py','combined_exact_intervals')
    print('CHECK_EXACT_CEILING',flush=True)
    root=ceiling(E,T,P)
    print('PASS_EXACT_CEILING',flush=True)
    # A finite interval proof of a uniform strict local moment improvement.
    coefficients={1:17,2:126,3:-50,4:-42,5:2,7:-22,8:5,9:17}
    prior_native=read(ROOT/'research/missing-join-frame/NATIVE.json.gz')
    actual=Counter(H);actual.subtract(N)
    actual.subtract({int(k):v for k,v in prior_native['helpers'].items()})
    actual.update({int(k):v for k,v in prior_native['paid'].items()})
    need({k:v for k,v in actual.items() if v}==coefficients,'Uniform gain is the actual source-bound profile difference')
    need(sum(r*n for r,n in coefficients.items())==0,'Local gain vanishes at t=1')
    derivative_upper=None
    for i in range(128):
        l,r=Q(i,128),Q(i+1,128)
        bound=Q(0)
        for rank,n in coefficients.items():
            product=E.mul(E.power(rank,r if n>0 else l),E.log_bounds(rank))
            bound+=n*product[1 if n>0 else 0]
        derivative_upper=bound if derivative_upper is None else max(derivative_upper,bound)
    need(derivative_upper<0,'Joint local moment gain for every 0<t<1')
    print('PASS_UNIFORM_LOCAL_GAIN',flush=True)
    local_gain={'coefficients':coefficients,'vanishes_at_one':True,'derivative_upper':E.display((derivative_upper,)*2),'intervals':128}

    parent=read(ROOT/'research/missing-join-frame/RESULT.json')
    oldT={int(k):v for k,v in parent['targets'].items()};oldP={int(k):v for k,v in parent['paid'].items()}
    need(E.moment(oldT,1-KAPPA)[1]<E.moment(oldP,1-KAPPA)[0],'Predecessor invoice fails at the new saving')
    need(sum(H.values())==408 and sum(r*n for r,n in N.items())-sum(r*n for r,n in H.items())==1856,'Fixed native mass deficit')
    t,u,v,c,b=1-TESTED,Q(1,5),1024,20,21
    target=E.moment(T,t);alpha=E.divide(E.moment(P,t),target)
    other=S.C.load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','combined_separate_intervals')
    tl,th=other.moment(T,TESTED);pl,ph=other.moment(P,TESTED)
    need(tl>ph and max(tl,target[0])<=min(th,target[1]),'Independent exact raw-moment engine')
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))
    delta=E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,TESTED),target))
    alpha_gap=Q(1,1000000000);g,d=Q(97,100),Q(97,100)
    need(alpha[1]<1-alpha_gap and gamma[1]<g and delta[1]<d,'All three completely charged tail bounds')
    need(g**128<Q(1,16) and d**128<Q(1,16),'Both exact decay blocks')
    bound=1/(1+v*alpha_gap)+Q(4,2**32)
    need(bound<1 and c**64<b**63,'Strict paid completion and splitting')
    need(sum(P.values())<69273,'Paid call count below the pinned p17 predecessor')
    # Apply PR4433's general logarithmic majorant at the actual new ambient rank.
    theta,power=Q(63,64),1000
    eta=E.scale(E.power(145,-v*TESTED),t)
    need(2*(20**v)**64<=(145**v)**63 and eta[0]>theta**power,'Shifted exit and complement capacity')
    need(E.power(145,v*TESTED)[1]<2**power,'Initial compiler range')
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
    local_routes=(sum(N.values())+2*408+688)*1000
    need(local_scalar+local_routes<10**7,'Every new local scalar and monomial route fits')
    scalar_upper=18*10**7+15*1792+32*112*(len(word['physical_events'])+sum(len(word['boundaries'][k+'_program']) for k in ('left','right')))
    need(scalar_upper<10**9,'Retain the complete raw nonrecursive bound')
    print('PASS_COMPLETION_AND_COMPILER',flush=True)
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
    return encode({'status':'PASS_CONDITIONAL_JOINT_HELPER_KAPPA_00302015', 'kappa':KAPPA,'kappa_decimal':'0.00302015',
        'source_inputs':count,'uniform_local_gain':local_gain,'source_heads':{'PR4447':'322e0ec764aa7ef7801383feb1f656e460dd8bed','PR4440':'40e22a83ed660d3d6074c4f2dbf14bfb621eee51','helper_retiming':'ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9','PR4441_combination':'5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39'},
        'gain_over_PR4447':KAPPA-Q('.00300123'), 'gain_over_PR4441':KAPPA-Q('.00300105'), 'gain_over_PR4440':KAPPA-Q('.00296'),'gain_over_PR4416':KAPPA-Q('.00268647'),
        'targets':dict(sorted(T.items())),'paid':dict(sorted(P.items())),'full_calls':full,'query_shears':thin,'pairs':16,'prefix_pairs':7,'local_helpers':H,'local_paid':N,
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
    parser.add_argument('--write',action='store_true',help='Author arithmetic from pinned receipts; not a fresh native/dependency replay.')
    parser.add_argument('--part',choices=('all','dependencies','native','arithmetic'),default='all')
    args=parser.parse_args()
    need(not args.write or args.part=='all','The authoring switch is separate from partial replay modes')
    if args.part=='dependencies':
        print(json.dumps(replay_dependencies(),sort_keys=True))
    elif args.part=='native':
        authenticate();local=J.run()
        need(json.loads(json.dumps(local))==read(HERE/'NATIVE.json.gz'),'Fresh complete native receipt')
        print(json.dumps({'status':'PASS_JOINT_NATIVE_632_COLUMNS_BOTH_ORIENTATIONS','helpers':local['helpers'],'paid':local['paid'],'physical_pairs':len(local['new_physical_edges_and_boundaries'])},sort_keys=True))
    else:
        result=run(execute_sources=args.part=='all' and not args.write)
        if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        else:need(result==read(HERE/'RESULT.json'),'Exact combined arithmetic receipt')
        keys=('status','kappa_decimal','gain_over_PR4447','compiler')
        output={k:result[k] for k in keys}
        if args.part=='arithmetic':output['replay_scope']='Arithmetic and p16 controller only; the registered native and dependency gates are separate required commands.'
        print(json.dumps(output,sort_keys=True))
