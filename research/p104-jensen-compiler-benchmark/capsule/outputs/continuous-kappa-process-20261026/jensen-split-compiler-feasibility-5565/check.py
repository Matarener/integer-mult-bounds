#!/usr/bin/env python3
"""One hypothetical145-split compiler gate; root's single bounded pair only.

No construction, source interpreter, parameter sweep, outer/BIT or cost replay.
Apache-2.0; substantial OpenAI Codex assistance. See CONTRACT.md.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
HEAD='9af814164b9dfc21f19ec737959d67cb71488c95'
GOALS=(Q(33,10000),Q(6600001,2000000000))
U=GOALS[1]
V=32768
LOG_POWER=22000
RESERVE=Q(1,10**6)
RHO=Q(19997,20000)
THETA=Q(39,40)
SOURCE_P={1:2203,2:459,3:493,4:92,5:168,6:18,7:14}
SOURCE_H={4:83,5:5,8:14,9:425}
HELPERS={4:228,5:150,8:14,9:280}
MESH=10**320


def need(ok,message):
    if not ok:
        raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def hist(h):return {int(r):int(n) for r,n in h.items() if n}
def mass(h):return sum(r*n for r,n in h.items())


def mesh(a):
    lo=Q((a[0]*MESH).__floor__(),MESH)
    hi=Q(-((-a[1]*MESH).__floor__()),MESH)
    need(lo<=a[0]<=a[1]<=hi,'exact outward1e-320 mesh')
    return lo,hi


def multiply(a,b):
    need(0<=a[0]<=a[1] and 0<=b[0]<=b[1],'positive multiplication domain')
    return mesh((a[0]*b[0],a[1]*b[1]))


def divide(a,b):
    need(0<=a[0]<=a[1] and 0<b[0]<=b[1],'positive ratio domain')
    return mesh((a[0]/b[1],a[1]/b[0]))


def ipower(a,n):
    need(type(n) is int and n>=0 and 0<=a[0]<=a[1],'nonnegative interval integer power')
    result=(Q(1),Q(1))
    while n:
        if n&1:result=multiply(result,a)
        n//=2
        if n:a=multiply(a,a)
    return result


def invoice(p,h):
    paid=Counter({r:18*n for r,n in p.items()})
    targets=Counter({r:18*n for r,n in h.items()})
    paid[1]+=1560
    for length in (7,8):
        for k in range(2,length+2):
            paid[8*k]+=208;targets[8*k+1]+=208
    targets[145]+=208
    return dict(paid),dict(targets)


def split_helpers(number=145,remove_parents=True,extra=0):
    need(type(number) is int and 0<=number<=425,'distinct original rank9 inventory')
    need(number==145 and extra==0,'single145 nomination; no separate13/15 existing credit')
    out=Counter(SOURCE_H)
    out[4]+=number+extra;out[5]+=number+extra
    if remove_parents:out[9]-=number+extra
    need(dict(out)==HELPERS,'one target replacement with removed parent credit')
    return dict(out)


def bind_candidate(p,h,paid,targets):
    need(p==SOURCE_P and h==HELPERS,'fixed paid side and one target hypothesis')
    a,b=invoice(p,h)
    need((a,b)==(paid,targets),'complete paid/query/idle/main/target coefficient equality')
    need(sum(paid.values())==66726 and sum(targets.values())==15424 and
         mass(paid)==241268 and mass(targets)==242028 and max(paid)==72 and max(targets)==145,
         'hypothetical complete count/rank-mass census')


def validate_parameters(c,cutoff=12,floor=13,u=U,v=V,p=LOG_POWER):
    need(c in GOALS and 0<c<1 and u>=c and 1<cutoff<floor<145 and
         type(v) is int and v>=1 and type(p) is int and p>0,'actual source theorem parameter domains')


def charged(al,ga,de,v=V,coefficients=(1,2,2)):
    need(coefficients==(1,2,2),'complete source original-paid and completion coefficients')
    terms=[ipower(pair,v) for pair in (al,ga,de)]
    return mesh((sum(k*x[0] for k,x in zip(coefficients,terms)),
                 sum(k*x[1] for k,x in zip(coefficients,terms))))


def threshold(step=14000000000,p=LOG_POWER):
    need(step==14000000000 and p==22000,'one frozen uniform grid')
    def wins(j):return (step*j+1)**p<2**j
    need(not wins(1) and wins(1500000),'declared finite bracket1..1500000')
    lo,hi=1,1500000
    while hi-lo>1:
        mid=(lo+hi)//2
        if wins(mid):hi=mid
        else:lo=mid
    need(wins(hi) and not wins(hi-1) and step*hi>8*V,'exact least-grid threshold and rejected predecessor')
    return {'step':step,'logarithm_power':p,'least_positive_passing_j':hi,'predecessor_j':hi-1,
            'H':step*hi,'N':'2^'+str(step*hi),'finite_bracket_upper_j':1500000,
            'positive_crossing_uniqueness':'README§4 strict convexity argument; not a minimum native program',
            'winning_word_materialized':False}


def rejected(action,strength):
    try:action()
    except (ValueError,KeyError):return {'outcome':'rejected','strength':strength}
    raise ValueError('accepted required control '+strength)


def main():
    pins=json.loads((B/'INPUTS.json').read_bytes())
    for name,digest in pins['files'].items():
        need(sha((ROOT/name).read_bytes())==digest,'frozen input byte '+name)
    def load(name):return json.loads((ROOT/pins[name]).read_bytes())
    nomination=load('nomination');source=load('source_raw');capture=load('capture');custody=load('custody')
    need(nomination['source']['head']==HEAD,'one exact source nomination')
    ownership=load('curator_gate')
    need(ownership['frozen_benchmark']['source_head']==HEAD and
         ownership['additional_paper_only_scope']['source']==5565 and
         ownership['additional_paper_only_scope']['overlap_observed'] is False and
         ownership['additional_paper_only_scope']['no_physical_inventory_claim'] is True and
         ownership['additional_paper_only_scope']['not_execution_authority'] is True,
         'sealed paper-only ownership boundary; root request separately governs execution')
    texts={r['path']:r for r in capture['files'] if r['pr']==5565}
    for path,row in texts.items():
        raw=row['content'].encode();record=next(r for r in custody['records'] if r['pr']==5565 and r['path']==path)
        need(row['head']==record['head']==HEAD and blob(raw)==row['sha']==record['git_blob'] and
             sha(raw)==record['sha256'],'source text Git/SHA custody '+path)
    need((ROOT/pins['source_raw']).read_bytes()==texts['research/p104-commuting-contact/RESULT.json']['content'].encode(),
         'whole source receipt serialization')
    pricing=texts['research/p104-commuting-contact/pricing.py']['content']
    for line in ['t,u,v,c,b = 1-TESTED,Q(1,5),1024,17,18','theta,power = Q(63,64),1000',
                 'raw += 32*104*(26+1000)']:
        need(line in pricing,'source constants preserved rather than silently modified '+line)
    tc=load('theorem_capture');td=load('theorem_custody')
    for row in tc['files']:
        raw=(ROOT/pins['theorem_dir']/row['file']).read_bytes()
        record=next(r for r in td['records'] if r['file']==row['file'])
        need(row['ref']==record['ref']=='5e0052ca0aa3036a3afa8b0438927377c8d97d53' and
             raw==row['content'].encode() and blob(raw)==row['sha']==record['git_blob'] and
             sha(raw)==record['sha256'],'generalized theorem source '+row['file'])
    theorem=(ROOT/pins['theorem_dir']/'README.md').read_text()
    for line in ['u >= C,  sigma = t+u >= 1','alpha^v + 2 gamma_u^v + 2 delta^v','any real p>0',
                 'theta_bar^p < eta = t m^(t−1)','m^(1−t) < 2^p']:
        need(line in theorem,'actual higher-moment/majorant premise '+line)
    word_raw=(ROOT/pins['word']).read_bytes()
    wr=next(r for r in custody['records'] if r['pr']==5565 and r['path'].endswith('/WORD.json.gz'))
    need(sha(word_raw)==wr['sha256'] and blob(word_raw)==wr['git_blob'] and wr['head']==HEAD,'source WORD bytes')
    word=json.loads(gzip.decompress(word_raw));dims=list(map(len,word['frames']));sp=Counter();sh=Counter();live=set(word['live'])
    for event in word['program']:
        if event[0]=='MOVE':
            r=abs(dims[event[3]]-dims[event[2]]);need(r>0,'positive source MOVE rank');sp[r]+=1
    for owner in range(735):
        if owner not in live and owner-112 not in live:
            r=dims[word['final'][owner]]-dims[word['initial'][owner]];need(r>0,'positive helper endpoint rank');sh[r]+=1
    need(dict(sp)==SOURCE_P==hist(source['local']['paid']) and dict(sh)==SOURCE_H==hist(source['local']['helpers']),
         'independent structural source census, not an interpreter')
    source_paid,source_targets=invoice(sp,sh)
    need(source_paid==hist(source['result']['paid']) and source_targets==hist(source['result']['targets']) and
         sum(source_paid.values())==66726 and sum(source_targets.values())==12814 and
         mass(source_paid)==241268 and mass(source_targets)==242028 and
         word['public']==735 and len(word['program'])==25133 and
         source['result']['full_forward_calls']==18 and source['result']['query_shears']==15 and
         source['result']['whole_idle_jobs']==3120,'complete source/controller bill')
    helpers=split_helpers();paid,targets=invoice(SOURCE_P,helpers);bind_candidate(SOURCE_P,helpers,paid,targets)
    one=nomination['one_profile'];cfg=nomination['fixed_parameters']
    need(hist(one['complete_paid'])==paid and hist(one['complete_targets'])==targets and
         hist(one['local_paid'])==SOURCE_P and hist(one['local_helpers'])==HELPERS and
         one['selected_splits']['number_per_FULL']==145 and one['selected_splits']['parent_rank']==9 and
         one['selected_splits']['child_ranks']==[4,5] and
         one['selected_splits']['distinct_original_parent_inventory']==425 and
         one['selected_splits']['reuse_of_produced_children'] is False and
         one['selected_splits']['physical_realization'] is None,'whole hypothetical nomination and absent physical witness')
    need(cfg['funded_C']==str(GOALS[0]) and cfg['tested_C']==str(GOALS[1]) and
         cfg['cutoff']==12 and cfg['completion_floor']==13 and cfg['tail_offset']==str(U) and
         cfg['tensor_power']==V and cfg['alpha_reserve']==str(RESERVE) and cfg['common_tail_ceiling']==str(RHO) and
         cfg['theta_bar']==str(THETA) and cfg['logarithm_power']==LOG_POWER and cfg['uniform_j_upper']==1500000 and
         cfg['gap']=='1/14000000000' and cfg['uniform_grid_step']==14000000000,
         'one nominated fixed tuple, no optimization')
    old_request=load('engine_qualified_request');old_pair=load('engine_qualified_pair')
    need(old_pair['complete_output_equal'] and old_pair['scientific_fields_excluded']==0 and
         sha((ROOT/pins['engine_qualified_request']).read_bytes())==old_pair['request_sha256'] and
         old_request['files'][pins['engine']]==sha((ROOT/pins['engine']).read_bytes()),'qualified positive-C engine custody')
    spec=importlib.util.spec_from_file_location('qualified_positive_C_engine',ROOT/pins['engine'])
    engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
    @lru_cache(None)
    def power(r,c):
        need(0<=c<1 and type(r) is int and 1<=r<=145,'positive-C engine call domain')
        return mesh(engine.power(r,c))
    def moment(h,c):
        return mesh((sum(n*power(r,c)[0] for r,n in h.items()),sum(n*power(r,c)[1] for r,n in h.items())))
    def direct_tails(c,cutoff=12,floor=13):
        validate_parameters(c,cutoff=cutoff,floor=floor)
        s=U-c;tail={r:divide((Q(r*r),Q(r*r)),power(r,s)) for r in paid}
        tailpaid=mesh((sum(n*tail[r][0] for r,n in paid.items()),sum(n*tail[r][1] for r,n in paid.items())))
        target=moment(targets,c);rawpaid=moment(paid,c)
        cutoff_u=divide((Q(cutoff),Q(cutoff)),power(cutoff,U))
        cutoff_c=divide((Q(cutoff),Q(cutoff)),power(cutoff,c))
        return (divide(rawpaid,target),divide(tailpaid,multiply(cutoff_u,target)),
                divide((Q(floor*15424),Q(floor*15424)),multiply(cutoff_c,target)),
                target,rawpaid,tailpaid,divide((Q(241268),Q(241268)),multiply(cutoff_c,target)))
    def display(pair):return engine.interval(*pair)

    logcert=nomination['paid_log_certificate'];logupper={int(r):Q(v) for r,v in logcert['rank_log_upper'].items()}
    for rank in paid:
        log=engine.ln_rank(rank)
        need(log[1]<logupper[rank] if rank>1 else log[1]==logupper[rank]==0,'exact rational log table '+str(rank))
    for rank,lower,upper in [(2,Q('0.6931'),Q('0.6932')),(3,Q('1.0986'),Q('1.0987'))]:
        ll,lh=engine.ln_rank(rank);need(lower<ll<=lh<upper,'primitive rational log bracket')
    weighted=sum(paid[r]*r*logupper[r] for r in paid)
    need(weighted==Q(logcert['weighted_log_sum_upper']),'rank-mass weighted log-sum witness')
    weights={r:Q(n*r,241268) for r,n in paid.items()}
    need(sum(weights.values())==1 and all(x>0 for x in weights.values()),'paid rank-mass probabilities')
    mu=weighted/241268;log12_lower=2*Q('0.6931')+Q('1.0986');d=log12_lower-mu
    need(engine.ln_rank(12)[0]>log12_lower and d==Q(logcert['Jensen_gap_lower'])>0,'strict Jensen geometric-mean gap')
    x=GOALS[0]*d-(U-GOALS[0])*Q('1.7919')
    need(x==Q(nomination['fixed_offset_bridge']['uniform_exponent_gap_lower'])>0 and
         1/(1+x)<RHO and Q(13*15424,241268)==Q(50128,60317)<Q(21,25)<RHO,
         'fixed-u transport and separate completion count bounds')
    rho_v=ipower((RHO,RHO),V)
    need(rho_v[1]<Q(1,128),'new finite rho^32768 tail certificate')
    paper_charge=Q(1)/(1+V*RESERVE)+Q(4,128)
    need(paper_charge==Q(516137,516384)<1,'both coefficient-two tails in complete paper upper bound')
    need(12**40<13**39 and 2*12**40<145**39,'actual theta and reduced shifted-exit certificate')
    points=[];internal=[]
    for c in GOALS:
        validate_parameters(c)
        al,ga,de,target,rawpaid,tailpaid,endpoint=direct_tails(c)
        raw=(target[0]-rawpaid[1],target[1]-rawpaid[0])
        need(raw[0]>0 and al[1]<1-RESERVE and ga[1]<RHO and de[1]<RHO,'direct raw reserve and both fixed-u tails')
        need(endpoint[1]<al[0] and ga[1]<Q(1)/(1+x) and de[1]<Q(50128,60317),
             'endpoint Jensen and fixed-u correction bounds independently agree with direct intervals')
        total=charged(al,ga,de);need(total[1]<1 and total[1]<paper_charge,'direct complete charged moment')
        base=divide(power(145,c),(Q(145),Q(145)));negative=ipower(base,V)
        eta=multiply((1-c,1-c),negative);initial=divide((Q(1),Q(1)),negative)
        theta_p=ipower((THETA,THETA),LOG_POWER)
        need(0<theta_p[0]<=theta_p[1]<eta[0] and initial[1]<2**LOG_POWER,
             'actual eta/capacity and initial range, no inherited p1000 cap')
        points.append({'C':str(c),'u':str(U),'s':str(U-c),'raw_surplus':display(raw),
          'target_moment':display(target),'raw_paid_moment':display(rawpaid),'paid_tail_moment_at1_plus_s':display(tailpaid),
          'alpha':display(al),'gamma_fixed_u':display(ga),'gamma_endpoint_u_equals_C_diagnostic':display(endpoint),
          'delta':display(de),'complete_charged_normalized_moment':display(total),
          'eta':display(eta),'theta_to_p':display(theta_p),'initial_range':display(initial),
          'direct_fixed_u_correction_checked':True})
        internal.append((c,al,ga,de,target,base,eta,tailpaid))
    grid=threshold()
    need((GOALS[1]-GOALS[0])/7==Q(1,grid['step']),'exact tested/proposed seven-step gap')
    controls={}
    controls['parents_not_removed']=rejected(lambda:split_helpers(remove_parents=False),'actual signed target accounting mutation')
    for extra in (13,15):
        controls['double_credit_existing_'+str(extra)]=rejected(lambda extra=extra:split_helpers(extra=extra),'hypothesis inventory mutation; not a numerical impossibility claim')
    controls['reuse_beyond425_original_parents']=rejected(lambda:split_helpers(number=426),'finite parent inventory mutation')
    wrong={r:Q(n,66726) for r,n in paid.items()}
    controls['call_count_Jensen_weights']=rejected(lambda:need(wrong==weights,'wrong probabilities fail exact moment identity'),
        'actual probability-identity mutation; not a converse Jensen theorem')
    for name,rank,side,amount in [('omit_query',1,'paid',104),('omit_idle',72,'paid',208),('omit_main',145,'targets',208)]:
        pp,tt=deepcopy((paid,targets));hh=pp if side=='paid' else tt;hh[rank]-=amount
        controls[name]=rejected(lambda pp=pp,tt=tt:bind_candidate(SOURCE_P,HELPERS,pp,tt),'actual complete invoice mutation')
    controls['source_word_byte_corruption']=rejected(lambda:need(sha(word_raw+b'x')==wr['sha256'],'source byte mismatch'),'actual source custody mutation')
    for i,(c,al,ga,de,target,base,eta,tailpaid) in enumerate(internal):
        old_delta=direct_tails(c,cutoff=17,floor=18)[2]
        need(old_delta[0]>1,'old cutoff17/floor18 genuinely fails completion ratio for this target invoice')
        controls['old17_18_completion_'+str(i)]={'outcome':'rejected','strength':'actual old completion delta lower bound exceeds1','delta':display(old_delta)}
        controls['u_below_C_'+str(i)]=rejected(lambda c=c:validate_parameters(c,u=c/2),'actual theorem-domain mutation')
        short=charged(al,ga,de,v=1024)
        need(short[0]>1,'source v1024 loses this complete charged sufficient expression')
        controls['source_v1024_'+str(i)]={'outcome':'rejected','strength':'actual charged sufficient expression exceeds1; no physical impossibility conclusion','charged':display(short)}
        oldtheta=ipower((THETA,THETA),1000)
        need(eta[1]<oldtheta[0],'source p1000 genuinely fails eta capacity at changed tensor')
        controls['source_p1000_'+str(i)]={'outcome':'rejected','strength':'actual eta-capacity failure at nominated v'}
        for coefficients,label in [((1,0,2),'drop_original_paid_tail'),((1,2,0),'drop_completion_tail')]:
            controls[label+'_'+str(i)]=rejected(lambda al=al,ga=ga,de=de,coefficients=coefficients:charged(al,ga,de,coefficients=coefficients),
              'complete-charge accounting mutation; omitting a positive term is not a numerical impossibility test')
    need(internal[0][-1][0]>241268,'fixed-u goal numerator is strictly above P1; it is not the exact endpoint')
    controls['pretend_endpoint_at_both_points']=rejected(lambda:need(internal[0][-1][1]<=241268,'false endpoint numerator'),
       'actual fixed-u correction mutation at goal point')
    controls['wrong_uniform_gap']=rejected(lambda:threshold(step=1400000000),'exact grid mutation before search')
    controls['inherit_ordinary_caps']=rejected(lambda:need(pins['actual_new_ordinary_cost_bound_supplied'] is True,'no supplied changed-word cost bound'),
       'scope/claim sanity only; no actual ordinary-cost counterexample supplied')
    result={'schema':'jensen-split-compiler-feasibility-5565/v1','status':'PASS_SCOPED_HYPOTHETICAL_145_SPLIT_COMPILER_FEASIBILITY',
      'source_head':HEAD,'profile_is_hypothetical':True,'distinct_original_rank9_parents_per_FULL':145,
      'independent_physical_split_ids_supplied':False,'baseline_original_parent_inventory':425,
      'source_complete_paid':source_paid,'source_complete_targets':source_targets,
      'hypothetical_local_helpers':helpers,'hypothetical_complete_paid':paid,'hypothetical_complete_targets':targets,
      'paid_count':66726,'target_count':15424,'paid_rank_mass':241268,'target_rank_mass':242028,'rank_surplus':760,
      'parameters':cfg,'Jensen_rank_mass_log_sum_upper':str(weighted),'Jensen_mu_upper':str(mu),
      'Jensen_log12_lower':str(log12_lower),'Jensen_gap_lower':str(d),'fixed_u_gap_lower':str(x),
      'rho_power':display(rho_v),'complete_paper_charge_strict_upper':str(paper_charge),
      'interval_mesh_denominator_power10':320,'points':points,'uniform_threshold':grid,'controls':controls,
      'tested_point':str(GOALS[1]),'proposed_target_label_only':str(GOALS[0]),
      'uniform_saving_if_source_native_and_compiler_hypotheses_hold':str(GOALS[1]-Q(1,grid['step'])),
      'native_hypotheses':'Distinct arbitrary productive input fields; chronological tensor substitution on actual physical owners; complete spectators and whole-job adapters; source complements, integer flow and safe owned erasure. None newly established.',
      'post_product_inventory':{'original_paid_positions':'66726^32768','productive_fields':'15424^32768','ambient_rank':'145^32768',
       'original_rank_surplus':'242028^32768-241268^32768','paid_completion':'on same owner to13^32768, at most15424^32768 completions',
       'paid_splitting':'integer12^32768 blocks plus remainder; both full coefficient-two tails charged'},
      'actual_new_ordinary_cost_bound_supplied':False,'old_1000_1100_caps_transferred':False,
      'unrun_obligations':['physical145 distinct independent target splits and literal new word','native all-width/phase/adapters/product applicability',
        'actual scalar/basis/movement/normalizer/owned-bank counts and denominator/growth bounds','new expanded U/R/W/P/G, storage, precision, tape and rowstock constants',
        'BIT and changed-consumer outer admission, including retained54strict+4functional ledger only if applicable'],
      'new_kappa':None,'funded_kappa':None,'physical_word':None,'automatic_constructive_dispatch':False,
      'engine_credit':'Qualified positive-C interval_math; new positive rational interval transport only, no negative-C engine call. Jensen source Hoeffding1963 equation1.9; generic compiler README§§1/2/4/5 and retained predecessors.'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
