#!/usr/bin/env python3
"""Finite n18 ABCD funding separator, for one root-owned guarded execution.

Exact Fractions throughout. Credits: source and paper authors in CONTRACT.md;
positive-C power algorithm is the retained, qualified interval_math.py engine.
The finite integer fifth-root extension is new and explicitly certified here.
Apache-2.0; substantial OpenAI Codex assistance.
"""
import base64
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
HEAD='6efa248cf456d6101d757e9d09ba29711d18a13a'
PRIOR='f0ab2ed10f91a5acd76c1c6753d970c59e51e83c3d0b96fe8a6a3a6c3f80e9de'
P0={1:2211,2:459,3:494,4:94,5:164,6:18,7:14}
H0={4:83,5:5,8:15,9:424}
C0=Q(6163781,2000000000)
GOALS=(Q(33,10000),Q(6600001,2000000000))


def need(condition,message):
    if not condition:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def hist(h):return {int(r):Q(n) for r,n in h.items() if Q(n)}
def show(h):return {str(r):str(n) for r,n in sorted(h.items()) if n}
def mass(h):return sum((r*n for r,n in h.items()),Q(0))
def bounds(h):return [str(h[0]),str(h[1])]


def outward_mesh(interval):
    # Exact rounding prevents a cross-rank denominator product in source sums.
    unit=10**24;a,b=interval
    lo=Q((a*unit).__floor__(),unit);hi=Q(-((-b*unit).__floor__()),unit)
    need(lo<=a<=b<=hi and hi-lo<Q(1,10**20),'exact outward source power mesh')
    return lo,hi


def full_invoice(p,h,n=18):
    need(n==18,'retained original n18 caller only')
    paid={r:18*Q(k) for r,k in p.items()}
    targets={r:18*Q(k) for r,k in h.items()}
    paid[1]=paid.get(1,0)+104*15
    for length in (7,8):
        for k in range(2,length+2):
            paid[8*k]=paid.get(8*k,0)+208
            targets[8*k+1]=targets.get(8*k+1,0)+208
    targets[145]=targets.get(145,0)+208
    return paid,targets


def source_scope(source,paid,targets,p,h):
    st=source['result']['strictification']
    need(p==P0 and h==H0,'exact current source local invoice, including p7')
    need(source['result']['full_forward_calls']==source['physical']['full_calls']==18 and source['physical']['ports']==104 and
         st['cutoff']==17 and st['floor']==18 and
         Q(st['tail_offset'])==Q(1,5) and Q(st['tested'])==C0,'source caller/C0/cutoff/floor/offset scope')
    ep,et=full_invoice(p,h)
    need(paid==ep==hist(source['result']['paid']) and targets==et==hist(source['result']['targets']),
         'complete source query/whole-idle/main/helper paid/target coefficient equality')
    need(sum(paid.values())==66852 and sum(targets.values())==12814 and
         mass(paid)==241250 and mass(targets)==242010 and max(paid)==72 and max(targets)==145,
         'complete source counts, masses and ranks')


def bind_formula(pricing,verify,proof,current_verify,current_common):
    snippets=("E = L.load(L.ROOT/'research/higher-moment-strictification/verify.py','p104_productive_intervals')",
      't,u,v,c,b = 1-TESTED,Q(1,5),1024,17,18',
      'target,paid = E.moment(T,t),E.moment(P,t)',
      'alpha = E.divide(paid,target)',
      'gamma = E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))',
      'delta = E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,TESTED),target))',
      'reserve,decay = Q(1,10**10),Q(97,100)',
      "L.need(alpha[1] < 1-reserve and gamma[1] < decay and delta[1] < decay")
    need(all(x in pricing for x in snippets),'literal current pricing.run formula/callsite/parameter binding')
    need('gamma = divide(moment(P, t+u), mul(power(cutoff, u), target))' in verify and
         'delta = divide((Q(sum(T.values())*floor),)*2,' in verify and
         'mul(power(cutoff, C), target))' in verify and
         "need(t+u >= 1, 'tail moment exponent at least one')" in verify,
         'retained strictification.tail_certificate gamma/delta formula and applicability')
    need('Cutoff 17, floor 18, tail offset' in proof and '1/5' in proof and
         'All completion, splitting, capacity, compiler-grid, BIT-stock and 58 outer' in proof,
         'retained source PROOF declares original charged compiler route')
    need("with closure() as root:" in current_verify and
         "L = load(root/'research/p104-productive-controller/local.py', 'local')" in current_verify and
         'L.ROOT = root' in current_verify and 'result = P.run(local, native, caller, physical)' in current_verify and
         "pins=json.loads((HERE/'SOURCES.json').read_bytes())['retained_source']" in current_common,
         'current verify.main joins exact retained closure to current pricing.run')


def affine(a,b,c,d):
    return {1:2211-a+b+c,2:459-2*b-c+d,3:494+b-2*d,4:94-c+d,5:164-a+c,6:18+a,7:14}


def inverse(p):
    return (p[6]-18,p[3]+2*p[4]+2*p[5]+2*p[6]-1046,p[5]+p[6]-182,p[4]+p[5]+p[6]-276)


def invariant(p,tag=None,rank_mass=5915,tag_mass=3458):
    if tag is None:tag={r:1+(r==6) for r in range(1,7)}
    need(set(p)==set(range(1,8)) and all(x>=0 for x in p.values()) and p[7]==14,'nonnegative six-rank profile and fixed p7')
    need(sum(r*p[r] for r in range(1,7))==rank_mass and
         sum(tag[r]*p[r] for r in range(1,7))==tag_mass,'two affine invariants with rank6 tag weight two')
    need(affine(*inverse(p))==p,'explicit signed ABCD affine inverse')


def log_rank(r):
    # Independent finite atanh sum; no real logarithm routine.
    # For u in [1,2], z in [0,1/3], ln u = 2 sum z^(2j+1)/(2j+1).
    def unit(u):
        z=(u-1)/(u+1);need(0<=z<=Q(1,3),'finite log domain')
        s=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)),Q(0))
        tail=2*z**65/(65*(1-z*z))
        return s,s+tail
    k=r.bit_length()-1
    a,b=unit(Q(r,2**k));l,u=unit(Q(2))
    return a+k*l,b+k*u


def fifth_bracket(r):
    # Integer bisection at fixed rational mesh, with explicit fifth-power proof.
    need(type(r) is int and 1<=r<=145,'finite fifth-root rank range')
    scale=10**12;low=0;high=3*scale
    while high-low>1:
        mid=(low+high)//2
        if mid**5<=r*scale**5:low=mid
        else:high=mid
    lo,hi=Q(low,scale),Q(high,scale)
    need(lo**5<=r<=hi**5 and hi-lo==Q(1,scale),'certified integer fifth-root enclosure')
    return lo,hi


def rational_goal_bounds(c,paper):
    need(c in GOALS,'two predeclared goal points only')
    result={}
    for r in range(1,7):
        l,u=map(Q,paper['log_brackets'][str(r)]);actual=log_rank(r)
        need(l<=actual[0]<=actual[1]<=u,'independently certified inherited rational log brackets')
        qlo,qhi=map(Q,paper['fifth_root_brackets'][str(r)])
        need(qlo**5<=r<=qhi**5 and 0<qlo<=qhi,'paper fifth-root bracket exact residuals')
        xlo,xhi=c*l,c*u
        need(0<=xlo<=xhi<1,'alternating Taylor domain')
        elo=1-xhi+xhi*xhi/2-xhi**3/6
        ehi=1-xlo+xlo*xlo/2
        need(0<elo<=ehi,'positive decreasing Taylor enclosures')
        raw=(r*elo,r*ehi);tail=(raw[0]*qlo,raw[1]*qhi)
        result[r]={'raw':raw,'tail':tail,'exp_neg':(elo,ehi)}
    return result


def dual_certificate(c,paper,saved,prior_point,gamma_floor=Q(193,200),lam=Q(799,10)):
    v=rational_goal_bounds(c,paper)
    need(0<lam and gamma_floor==Q(193,200),'positive lambda and independently qualified coarse gamma constant')
    mu=v[2]['tail'][0]+lam*v[2]['raw'][0]-(1+lam)
    nu=1+lam-mu
    slack={r:v[r]['tail'][0]+lam*v[r]['raw'][0]-mu*r-nu*(1+(r==6)) for r in range(1,7)}
    need(slack[1]==slack[2]==0 and all(slack[r]>0 for r in range(3,7)),
         'six dual coefficient inequalities, rank1/rank2 exact and rank6 tag2')
    sigma=sum((P0[r]*(v[r]['tail'][1]+lam*v[r]['raw'][1]) for r in range(1,7)),Q(0))-5915*mu-3458*nu
    b18=Q(prior_point['B18_current_tight'][0])
    required=lam*b18-sigma
    need(C0<c and Q(1763,1000)**5>17 and log_rank(72)[1]<Q(43177,10000),'headroom transport elementary rank/cutoff bounds')
    decay=1-(c-C0)*Q(43177,10000)
    bracket=Q(97,100)-gamma_floor*decay
    available=Q(1763,1000)*242010/18*bracket
    need(0<decay<1 and 0<bracket and available<required,'strict necessary raw/tail separation')
    need(Q(saved['C'])==c and Q(saved['lambda'])==lam and Q(saved['mu'])==mu and Q(saved['nu'])==nu,
         'independent mu/nu match paper finite fractions')
    for r in range(1,7):
        for name in ('raw','tail','exp_neg'):
            need(tuple(map(Q,saved['six_rank_power_bounds'][str(r)][name]))==v[r][name],'all asymmetric outward power endpoints')
        need(Q(saved['dual_rank_lower_slacks'][str(r)])==slack[r],'all paper coefficient slacks')
    need(Q(saved['baseline_dual_slack_strict_upper'])==sigma and Q(saved['B18_current_strict_lower'])==b18 and
         Q(saved['necessary_tail_increment_per_FULL_strict_lower'])==required and
         Q(saved['available_tail_increment_per_FULL_upper_if_source_gamma_exceeds_0965'])==available and
         Q(saved['separation_gap_even_with_0965_source_gamma_lower'])==required-available,
         'source slack, current B18, transported headroom and strict gap')
    return {'C':str(c),'lambda':str(lam),'mu':str(mu),'nu':str(nu),'six_rank_dual_lower_slacks':{str(r):str(slack[r]) for r in range(1,7)},
            'zero_slack_ranks':[1,2],'baseline_dual_slack_upper':str(sigma),'B18_current_strict_lower':str(b18),
            'necessary_tail_increment_per_FULL_strict_lower':str(required),
            'available_tail_increment_per_FULL_strict_upper':str(available),'strict_gap':str(required-available),
            'power_bounds':{str(r):{k:bounds(value) for k,value in row.items()} for r,row in v.items()}}


def rejected(action,strength):
    try:action()
    except (ValueError,KeyError):return {'outcome':'rejected','strength':strength}
    raise ValueError('mutation unexpectedly accepted: '+strength)


def main():
    pins=json.loads((B/'INPUTS.json').read_bytes())
    for name,expected in pins['files'].items():need(sha((ROOT/name).read_bytes())==expected,'pinned input bytes '+name)
    def load(name):return json.loads((ROOT/pins[name]).read_bytes())
    source=load('source_raw');derived=load('source_derived');capture=load('capture');revision=load('revision')
    prior=load('prior_result');pair=load('prior_pair');prior_req=load('prior_request')
    engine_inputs=load('engine_inputs');engine_result=load('engine_result');engine_pair=load('engine_pair')
    need(engine_pair['complete_output_equal'] and engine_pair['scientific_fields_excluded']==0 and
         engine_pair['result_sha256']==sha((ROOT/pins['engine_result']).read_bytes()) and
         engine_inputs['files']['outputs/economic-sensitivity-feasibility-20261025/interval_math.py']==sha((ROOT/pins['engine']).read_bytes()) and
         engine_inputs['reviewed_head']==engine_result['reviewed_head']=='18968423711fd902aaee1099979497d55603e1dc',
         'credited existing positive-C power engine qualification/code/result/pair joins')
    need(sha((ROOT/pins['prior_result']).read_bytes())==PRIOR==pair['result_sha256'] and
         pair['complete_output_equal'] and pair['scientific_fields_excluded']==0 and
         pair['request_sha256']==sha((ROOT/pins['prior_request']).read_bytes()),'existing 25-control root result and request/pair joins')
    need(prior['status']=='PASS_SCOPED_PR5580_SINGLE_USE_TAIL_COUNT_CERTIFICATE' and prior['reviewed_head']==HEAD and
         len(prior['mutation_controls'])==25 and all(x['outcome']=='rejected' for x in prior['mutation_controls'].values()),
         'qualified source/price transfer scope and all 25 controls')
    need(capture['head']==HEAD and capture['pr']==5580 and source==derived,'current raw/derived author receipt semantic equality')
    text={x['path']:x for x in capture['text_sources']}
    for name,row in text.items():need(blob(row['content'].encode())==row['sha'],'captured text Git object '+name)
    pricing=text['research/p104-event-contact-step/pricing.py']['content']
    current_verify=text['research/p104-event-contact-step/verify.py']['content']
    current_common=text['research/p104-event-contact-step/common.py']['content']
    declared=json.loads(text['research/p104-event-contact-step/SOURCES.json']['content'])['retained_source']
    archive=(ROOT/pins['closure']).read_bytes()
    need(sha(archive)==declared['sha256'],'actual retained strictification closure archive pin')
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tar:
        members=tar.getmembers();need(len({m.name for m in members})==len(members) and all(m.isfile() for m in members),'regular unique closure members')
        payload={m.name:tar.extractfile(m).read() for m in members}
    export=json.loads(payload['.research-export.json'])
    need(sha(payload['.research-export.json'])==declared['export_manifest_sha256'] and
         export['commit']==declared['commit'] and len(export['files'])==declared['files']==33 and
         set(payload)=={'.research-export.json'}|{row['path'] for row in export['files']},'exact source closure manifest/files/commit')
    for row in export['files']:need(sha(payload[row['path']])==row['sha256'] and len(payload[row['path']])==row['size'],'retained member custody '+row['path'])
    strict=payload['research/higher-moment-strictification/verify.py'].decode()
    proof=payload['research/p104-full-frame-contact/PROOF.md'].decode()
    bind_formula(pricing,strict,proof,current_verify,current_common)
    raw=(ROOT/pins['source_raw']).read_bytes()
    need(raw==text['research/p104-event-contact-step/RESULT.json']['content'].encode() and
         blob(raw)==text['research/p104-event-contact-step/RESULT.json']['sha'],'exact raw author RESULT serialization')
    need(revision['exact_author_serialization']['sha256']==sha(raw) and
         revision['historical_derived_serialization']['sha256']==sha((ROOT/pins['source_derived']).read_bytes()) and
         revision['exact_author_serialization']['git_blob']==blob(raw),'curator explicit immutable raw-derived custody revision')
    manifest=load('checkpoint')
    need(manifest['latest_complete_author_claim']['head']==HEAD and manifest['latest_complete_author_claim']['conclusion']=='success' and
         not manifest['stronger_complete_claim_observed'],'retained current checkpoint CI pass and no higher captured complete bill')
    wraw=(ROOT/pins['word']).read_bytes();wrow=capture['word_source']
    need(sha(wraw)==prior['word_sha256'] and blob(wraw)==prior['word_git_blob']==wrow['sha'] and
         base64.b64decode(''.join(wrow['content'].split()),validate=True)==wraw,'current exact WORD binary custody')
    word=json.loads(gzip.decompress(wraw));dims=list(map(len,word['frames']));p={};h={}
    for event in word['program']:
        if event[0]=='MOVE':
            r=abs(dims[event[3]]-dims[event[2]]);need(r>0,'positive structural MOVE rank');p[r]=p.get(r,0)+1
    live=set(word['live'])
    for owner in range(735):
        if owner not in live and owner-112 not in live:
            r=dims[word['final'][owner]]-dims[word['initial'][owner]];need(r>0,'positive structural helper rank');h[r]=h.get(r,0)+1
    need(word['public']==735 and len(word['program'])==25140 and p==hist(prior['current_local_paid']) and
         h==hist(prior['current_helpers']),'independent source structural rank census agrees with qualified current card')
    paid,targets=full_invoice(p,h);source_scope(source,paid,targets,p,h)
    paper=load('paper');need(paper['source_funding_input']['C0']==str(C0),'paper source C0')
    need(paper['two_invariants']['rank_mass_first_six']==5915 and paper['two_invariants']['tag_mass']==3458 and
         paper['two_invariants']['tag_weights']=={str(r):1+(r==6) for r in range(1,7)},'paper invariant declaration')
    invariant(P0)
    # Because these maps are affine, origin and four independent coordinate
    # directions prove the displayed inverse/invariants as coefficient identities.
    for args in ((0,0,0,0),(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)):
        v=affine(*args);need(inverse(v)==args,'affine coefficient inverse');invariant(v)
    for r in range(2,7):
        v={k:Q(0) for k in range(1,8)};v[7]=14
        # r6 has tag2, hence a distinct simplex endpoint.
        denom=r-(2 if r==6 else 1);v[r]=Q(2457,denom);v[1]=3458-(2 if r==6 else 1)*v[r]
        invariant(v)
    spec=importlib.util.spec_from_file_location('credited_positive_C_interval_math',ROOT/pins['engine'])
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    # New finite tail extension: every rank is evaluated only at positive C0;
    # multiply credited r^(1-C0) enclosures by independently certified r^(1/5).
    ranks=sorted(set(paid)|set(targets)|{17})
    need(max(ranks)<=145 and 0<C0<Q(1,100),'positive-C finite engine domain')
    need(1-C0+Q(1,5)>=1 and all(1-c+Q(1,5)>=1 for c in GOALS) and 1<17<18<145,
         'retained strictification tail-exponent/rank applicability at source and both goals')
    power={r:outward_mesh(engine.power(r,C0)) for r in ranks};roots={r:fifth_bracket(r) for r in ranks}
    p_tail=(sum((n*power[r][0]*roots[r][0] for r,n in paid.items()),Q(0)),
            sum((n*power[r][1]*roots[r][1] for r,n in paid.items()),Q(0)))
    target=(sum((n*power[r][0] for r,n in targets.items()),Q(0)),
            sum((n*power[r][1] for r,n in targets.items()),Q(0)))
    gamma=(p_tail[0]/(roots[17][1]*target[1]),p_tail[1]/(roots[17][0]*target[0]))
    need(Q(193,200)<gamma[0]<=gamma[1]<1,'independent exact source gamma0 strictly exceeds .965')
    need(target[1]<=242010,'exact source target upper below rank mass for headroom transport')
    points=[]
    for c,saved,old in zip(GOALS,paper['points'],prior['points']):
        need(Q(old['C'])==c,'qualified B18 exact same goal point')
        points.append(dual_certificate(c,paper,saved,old))
    need(len(paper['points'])==len(prior['points'])==2,'no silent extra or omitted points')
    controls={}
    def scope_mutate(name,edit):
        s,pp,tt,lp,lh=deepcopy((source,paid,targets,p,h));edit(s,pp,tt,lp,lh)
        controls[name]=rejected(lambda:source_scope(s,pp,tt,lp,lh),'real source/accounting mutation')
    scope_mutate('omit_nonlocal_query',lambda s,pp,tt,lp,lh:pp.__setitem__(1,pp[1]-104))
    scope_mutate('omit_whole_idle',lambda s,pp,tt,lp,lh:pp.__setitem__(72,pp[72]-208))
    scope_mutate('omit_main_target',lambda s,pp,tt,lp,lh:tt.__setitem__(145,tt[145]-208))
    scope_mutate('source_target_credit',lambda s,pp,tt,lp,lh:lh.__setitem__(9,lh[9]+1))
    scope_mutate('source_p7_cancellation',lambda s,pp,tt,lp,lh:lp.__setitem__(7,13))
    scope_mutate('old_transpose_comparison',lambda s,pp,tt,lp,lh:lp.__setitem__(2,458))
    scope_mutate('wrong_source_C0',lambda s,pp,tt,lp,lh:s['result']['strictification'].__setitem__('tested',str(GOALS[0])))
    scope_mutate('current_cutoff',lambda s,pp,tt,lp,lh:s['result']['strictification'].__setitem__('cutoff',16))
    scope_mutate('current_floor',lambda s,pp,tt,lp,lh:s['result']['strictification'].__setitem__('floor',17))
    scope_mutate('tail_offset',lambda s,pp,tt,lp,lh:s['result']['strictification'].__setitem__('tail_offset','1/4'))
    scope_mutate('other_caller_n17',lambda s,pp,tt,lp,lh:s['result'].__setitem__('full_forward_calls',17))
    controls['rank6_tag_weight']=rejected(lambda:invariant(P0,{r:1 for r in range(1,7)}),'real invariant coefficient mutation')
    controls['rank_mass_invariant']=rejected(lambda:invariant(P0,rank_mass=5916),'real affine constraint mutation')
    bad=deepcopy(paper);bad['fifth_root_brackets']['6']=['2','3']
    controls['bad_fifth_root']=rejected(lambda:rational_goal_bounds(GOALS[0],bad),'real power-bound certificate mutation')
    bad=deepcopy(paper);bad['log_brackets']['2']=['0','1/2']
    controls['bad_log_bound']=rejected(lambda:rational_goal_bounds(GOALS[0],bad),'real power-bound certificate mutation')
    for i,c in enumerate(GOALS):
        controls['negative_lambda_'+str(i)]=rejected(lambda i=i,c=c:dual_certificate(c,paper,paper['points'][i],prior['points'][i],lam=-Q(799,10)),
            'dual sign/domain sanity; not a source semantic mutant')
        controls['unsupported_gamma_constant_'+str(i)]=rejected(lambda i=i,c=c:dual_certificate(c,paper,paper['points'][i],prior['points'][i],gamma_floor=Q(99,100)),
            'source gamma premise sanity; no author interval substitution')
        altered=deepcopy(paper['points'][i]);altered['B18_current_strict_lower']=str(Q(altered['B18_current_strict_lower'])/18)
        controls['wrong_B18_denominator_'+str(i)]=rejected(lambda c=c,i=i,altered=altered:dual_certificate(c,paper,altered,prior['points'][i]),
            'real required raw-gain certificate mutation')
        altered=deepcopy(paper['points'][i]);altered['dual_rank_lower_slacks']['6']='0'
        controls['discard_rank6_slack_'+str(i)]=rejected(lambda c=c,i=i,altered=altered:dual_certificate(c,paper,altered,prior['points'][i]),
            'real dual certificate coefficient mutation')
        # A weakened premise may simply lose the separator. Classify that
        # outcome as inconclusive, never as a family exclusion.
        weak=Q(9,10);avail=Q(1763,1000)*242010/18*(Q(97,100)-weak*(1-(c-C0)*Q(43177,10000)))
        need(avail>=Q(points[i]['necessary_tail_increment_per_FULL_strict_lower']),'weakened-gamma boundary loses separation')
        controls['weakened_gamma_no_false_exclusion_'+str(i)]={'outcome':'inconclusive_as_required','strength':'analytic sensitivity sanity','available_headroom':str(avail)}
    controls['source_ratio_reused_at_goal']=rejected(lambda:need(C0==GOALS[0],'C0 differs from goal; transport required'),
        'analytic point-label sanity only, not a source mutant')
    controls['retained_gamma_formula_callsite']=rejected(lambda:bind_formula(pricing.replace('E.moment(P,t+u)','E.moment(P,t)'),strict,proof,current_verify,current_common),
        'real current compiler callsite formula mutation; code read only')
    result={'schema':'finite-n18-abcd-funding-separator/v1','status':'PASS_SCOPED_N18_ABCD_NECESSARY_FUNDING_OBSTRUCTION',
      'reviewed_head':HEAD,'prior_25_control_result_sha256':PRIOR,'source_C0':str(C0),
      'retained_compiler_guard_binding':{'source_archive_sha256':sha(archive),'source_archive_commit':declared['commit'],
        'current_pricing_Git_blob':text['research/p104-event-contact-step/pricing.py']['sha'],
        'strictification_module_sha256':sha(payload['research/higher-moment-strictification/verify.py']),
        'source_PROOF_sha256':sha(payload['research/p104-full-frame-contact/PROOF.md']),
        'gamma':'M_P(1-C+1/5)/(17^(1/5)*M_T(1-C))','delta':'18*|T|/(17^C*M_T(1-C))',
        'applicability':'1-C+1/5 >=1, retained cutoff17<floor18<145, current run() requires alpha<1-1e-10,gamma<.97,delta<.97; only alpha<1 and gamma<.97 used here',
        'source_modules_executed':False},
      'source_gamma_independent_interval':bounds(gamma),'source_gamma_coarse_strict_lower':'193/200',
      'source_tail_moment_interval':bounds(p_tail),'source_target_moment_interval':bounds(target),
      'source_power_intervals':{str(r):bounds(v) for r,v in power.items()},
      'source_complete_paid':show(paid),'source_complete_targets':show(targets),
      'source_local_paid':show(p),'source_local_helpers':show(h),
      'fifth_root_extension':{'method':'integer bisection at denominator 10^12; each lo^5<=r<=hi^5 checked',
        'brackets':{str(r):bounds(v) for r,v in roots.items()},'maximum_rank':145,'negative_C_calls':0},
      'power_engine_credit':'Qualified retained interval_math.py positive-C power engine reused without independent reimplementation; root-only evaluation at C0.',
      'points':points,'mutation_controls':controls,
      'scope':'All nonnegative real profiles with rank mass5915, tag mass3458 (tag6=2), fixedp7=14, fixed source helpers/nonlocal controller; original n18 cutoff17 floor18 offset1/5 decay.97, two declared C points only.',
      'analytic_premises':'Rational log/alternating exponential enclosures, fifth-root monotonicity, affine coefficient identities and Farkas multiplication by nonnegative profiles; headroom transport uses exp(-Delta log r)>=1-Delta L and target monotonicity. Not a proof-kernel theorem.',
      'source_census_scope':'Structural MOVE dimensions and declared helper endpoint dimensions only; source physical legality, caller semantics, native and compiler theorems inherited.',
      'physical_witness':False,'new_kappa':None,'selected_promotion':False,'n17_funding_claim':False,'all_n_funding_claim':False,
      'compiler_universal_claim':False,'source_gamma_author_interval_used_as_proof':False,
      'credit':'Ali Romman PR5580/A; thu-nmrc PR5551 B/C; source controller/compiler/precision/native predecessors; Astra ABCD dual paper; Clear1nsight qualification; OpenAI Codex assistance.'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
