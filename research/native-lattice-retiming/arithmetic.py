"""Complete changed invoice, paid tails, rank and outer consumer.
Apache-2.0. Substantial OpenAI Codex assistance. Credits: PR4359/4433,
Cinna Davis PR4440/4441, and Jacob Alan Sussman's mixed-target flow.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import ast
import json
import native

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
KAPPA,TESTED=Q('.00300120'),Q('.00300122')
LOW,HIGH=Q('.0030012390170'),Q('.0030012390173')
need=native.need

def encoded(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encoded(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encoded(v) for v in x]
    return x

def uniform(E,v,theta,power,kappa):
    t=1-TESTED
    eta=E.scale(E.power(153,-v*TESTED),t)
    need(18**16<22**15 and 2*(18**v)**16<=(153**v)**15,'Strict shifted logarithm contraction')
    need(eta[0]>theta**power and E.power(153,v*TESTED)[1]<2**power,'Both logarithmic induction conditions')
    gap=(TESTED-kappa)/7
    step=gap.denominator
    def passes(j):return (step*j+1)**power<2**(gap.numerator*j)
    lo,hi=1,2
    while not passes(hi):lo,hi=hi,2*hi
    while hi-lo>1:
        mid=(lo+hi)//2
        if passes(mid):hi=mid
        else:lo=mid
    H=step*hi
    need(H>8*v and passes(hi) and not passes(hi-1),'Effective winning integer rank and prior-grid control')
    return dict(theta=theta,logarithm_power=power,eta=E.display(eta),gap=gap,
                uniform_saving=TESTED-gap,H=H,N='2^'+str(H),integer_exponent=gap.numerator*hi,
                word_materialized=False)

def legacy(params,outer):
    source=ROOT/'research/higher-moment-strictification/vendor/check_ledger.py'
    parsed=ast.parse(source.read_bytes())
    fn=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='ledger')
    constants=[n for n in parsed.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.startswith('KAPPA_') for t in n.targets)]
    d=params['d'];eps,beta,q,a=(params[k] for k in ('epsilon','beta','q','a'))
    grid=10**10;backoff=Q((eps*q*grid).__floor__(),grid)-KAPPA
    need(backoff>0,'Positive exact legacy grid backoff')
    env={'Q':Q,'R0':params['r0'],'ZETA':Q(1,10**8),'SLACK':d,'STOP':d,'FLOOR':grid,'BACKOFF':backoff,
         'EPS':eps,'BETA':beta,'THETA_POWER':Q(2),'HALO_POWER':48,'CORE_POWER':128,'STRASSEN_TAU':Q(45,16),
         'b':params['b'],'q':q,'a':a,'bit':params['bit_saving'],
         'online':Q('0.001730970419199163702738'),'old':Q('0.001730970419199163702738')}
    exec(compile(ast.fix_missing_locations(ast.Module(body=constants+[fn],type_ignores=[])),'pinned legacy outer','exec'),env)
    result=env['ledger']('native_lattice')
    need(result['kappa']==KAPPA and result['margins']==outer['margins'],'Nine outer rows agree independently')
    need(len(result['strict_checks'])==63 and all(x>0 for x in result['strict_checks'].values()),'All 63 legacy predicates')
    return dict(checks=result['strict_checks'],grid=grid,backoff=backoff)

def run(local):
    E=native.load(ROOT/'research/higher-moment-strictification/verify.py','lattice_exact_intervals')
    C=native.load(ROOT/'research/query-thinned-controllers/controller.py','lattice_query_controller')
    word=native.read(ROOT/'research/query-thinned-controllers/COMPLEX-CONTROLLER.json')
    need(json.loads(json.dumps(C.run('complex',17,8)))==word,'Exact unchanged source physical word and Laurent boundaries')
    H={int(k):v for k,v in local['helpers'].items()};N={int(k):v for k,v in local['paid'].items()}
    T,P=Counter(),Counter();full=thin=idle=0
    for e in word['physical_events']:
        if e[0]=='LOCAL':full+=1;T.update(H);P.update(N)
        elif e[0]=='QUERY_SHEAR':thin+=1;P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224;idle+=224
    for term in word['diagonal']:T[1+8*sum(term[1:])]+=112
    need((full,thin,idle)==(19,16,3584),'Every native, query and whole idle')
    predecessor=native.read(ROOT/'research/fresh-helper-thinned/RESULT.json')
    oldT=Counter({int(k):v for k,v in predecessor['targets'].items()});oldP=Counter({int(k):v for k,v in predecessor['paid'].items()})
    need(T==oldT and P==oldP+Counter({1:19,4:19})-Counter({2:19,3:19}),'Independent complete profile substitution')
    need(sum(T.values())==11560 and sum(P.values())==69273,'Complete field and call counts')
    need((sum(r*n for r,n in T.items()),sum(r*n for r,n in P.items()))==(260798,259998),'Unchanged rank masses and surplus 800')
    def margin(c):
        a,b=E.moment(T,1-c),E.moment(P,1-c)
        return a[0]-b[1],a[1]-b[0]
    need(margin(LOW)[0]>0 and margin(HIGH)[1]<0,'Exact changed raw-root bracket')
    # Positive decreasing on [0,.01], sufficient to isolate this first root.
    derivative=sum(n*E.mul(E.power(r,Q('.99')),E.log_bounds(r))[0] for r,n in T.items())-sum(n*E.mul(E.power(r,1),E.log_bounds(r))[1] for r,n in P.items())
    need(derivative>0,'Strictly decreasing throughout C in [0,.01]')
    other=native.load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','lattice_other_intervals')
    tl,th=other.moment(T,TESTED);pl,ph=other.moment(P,TESTED)
    t=1-TESTED;target=E.moment(T,t);paid=E.moment(P,t)
    need(tl>ph and max(tl,target[0])<=min(th,target[1]),'Second exact raw moment engine')
    alpha=E.divide(paid,target);u=Q(3,25);v=675;c=18;b=22
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))
    delta=E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,TESTED),target))
    ag,g,d=Q(19,10**9),Q(491,500),Q(391,400)
    need(t+u>=1 and alpha[1]<1-ag and gamma[1]<g and delta[1]<d,'All exact charged tail limits')
    bound=1/(1+v*ag)+2*g**v+2*d**v
    need(bound<1,'Both completion tails paid at tensor power 675')
    # The same conservative limits reject a substantially shorter product.
    need(1/(1+600*ag)+2*g**600+2*d**600>1,'Short-product bound negative control')
    rank=uniform(E,v,Q(15,16),160,KAPPA)
    same=uniform(E,v,Q(15,16),160,Q('.00300105'))
    bit=native.read(ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom=Q(bit['atom']);ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599');admitted=Q(bit['admitted'])
    need(atom==Q('.004') and atom>ordinary>admitted>TESTED and atom<1-ordinary,'Retain the entire stronger ordinary BIT admission')
    gap=(TESTED-KAPPA)/7
    params=dict(kappa=KAPPA,tested_saving=TESTED,complex_uniform_saving=rank['uniform_saving'],
        b=KAPPA+5*gap,a=KAPPA+4*gap,q=KAPPA+3*gap,bit_saving=admitted,
        epsilon=1-gap,beta=1-3*gap,r0=gap/10,stop=gap,layout=gap,d=gap)
    L=native.load(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','lattice_outer')
    outer=L.ledger(params);outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
    need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4,'Full current consumer predicates')
    need(all(x>0 for group in ('strict_checks','functional_checks') for x in outer[group].values()),'Every current outer predicate')
    oldchecks=legacy(params,outer)
    source_kappa=Q('.00300105');sg=(TESTED-source_kappa)/7
    sp=dict(kappa=source_kappa,tested_saving=TESTED,complex_uniform_saving=same['uniform_saving'],
        b=source_kappa+5*sg,a=source_kappa+4*sg,q=source_kappa+3*sg,bit_saving=admitted,
        epsilon=1-sg,beta=1-3*sg,r0=sg/10,stop=sg,layout=sg,d=sg)
    same_outer=L.ledger(sp);same_outer['functional_checks']['actual_new_BIT_stock_sublinear']=sp['beta']*(1-atom)
    need(all(x>0 for group in ('strict_checks','functional_checks') for x in same_outer[group].values()),'Same-kappa full outer comparison')
    controls={}
    for name,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('unfunded_kappa',{'kappa':TESTED}),('closed_epsilon',{'epsilon':Q(1)})]:
        bad=L.ledger(dict(params,**patch));failed=[k for k,x in bad['strict_checks'].items() if x<=0];need(failed,'Reject '+name);controls[name]=failed
    local_scalar=max(x['real_scalar_allowance'] for x in local['native'].values())
    routes=(sum(N.values())+2*408)*1000
    need(local_scalar+routes<10**7,'All unchanged scalar and changed physical route costs fit')
    raw=19*10**7+16*1792+32*112*(len(word['physical_events'])+sum(len(word['boundaries'][k+'_program']) for k in ('left','right')))
    need(raw<10**9,'Complete nonrecursive raw budget')
    return encoded(dict(status='PASS_CONDITIONAL_NEW_NATIVE_PROFILE_KAPPA',kappa=KAPPA,kappa_decimal='0.00300120',
        gain_over_PR4441=KAPPA-Q('.00300105'),targets=dict(sorted(T.items())),paid=dict(sorted(P.items())),
        rank_surplus=800,raw_root=[LOW,HIGH],raw_root_scope='Unique crossing on [0,.01]; no universal or global mechanism ceiling.',
        derivative_negative_upper=-derivative,raw_moment_margin=E.display(margin(TESTED)),
        strictification=dict(tested=TESTED,power=v,cutoff=c,floor=b,u=u,alpha=E.display(alpha),gamma=E.display(gamma),delta=E.display(delta),limits=[1-ag,g,d],normalized_paid_upper=bound),
        compiler=rank,same_predecessor_kappa_compiler=same,
        rank_exponent_reduction=Q(int(predecessor['compiler']['H']),rank['H']),same_kappa_rank_exponent_reduction=Q(int(predecessor['compiler']['H']),same['H']),
        ordinary_BIT=bit,outer=outer,same_predecessor_kappa_outer=same_outer,legacy_outer=oldchecks,negative_controls=controls,
        nonrecursive=dict(local_scalar=local_scalar,route_bound=routes,raw_upper=raw,budget=10**9)))
