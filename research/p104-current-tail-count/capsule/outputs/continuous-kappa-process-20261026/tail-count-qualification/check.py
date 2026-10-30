#!/usr/bin/env python3
"""Finite Fraction-only qualification of the strict single-use tail relaxation.

No source constructor, contact scan, native code, interval engine, real power,
logarithm or exponential routine. Analytic implications remain paper premises.
Chris R/Clear1nsight, OpenAI Codex assistance, Apache-2.0; lineage in CONTRACT.md.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[2]
PRICE_SHA = '6ad37711165765c2f4f3fb9690e78b3db8b1fb6e8b91ff883b2f1286129f8335'
PRICE_PAIR_SHA = '1d99144de9f6d9411baeea842fcb0d3524ac2dbdc8e946c841b57ef430ed3805'
PRICE_REQUEST_SHA = 'd85ca5055168c84ca64a6c9b37dcc52fc61028134bfc6787fafc104a0b44cbe0'
LOG_SHA = '882369dbec747ac4fe4c324501dddca7e67240e773bb6782e29bd91dde25b5a7'
HEAD = 'af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf'
WORD_SHA = '12224e9a13a49c830b304338a8d31610fb43da15d1a650537733c27f7864310f'


def need(condition,message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticated(raw,expected,label):
    need(sha(raw) == expected,'byte authentication '+label)
    return json.loads(raw)


def histogram(data):
    return {int(r):Q(n) for r,n in data.items() if n}


def combine(*terms):
    out={}
    for factor,poly in terms:
        for r,n in poly.items():
            out[r]=out.get(r,Q(0))+factor*n
    return histogram(out)


def mass(poly):
    return sum((r*n for r,n in poly.items()),Q(0))


def show(poly):
    return {str(r):str(n) for r,n in sorted(poly.items()) if n}


def interval(data):
    lo,hi=(Q(data[k]) for k in ('lower_decimal_outward','upper_decimal_outward'))
    need(lo<hi,'strict inherited interval order')
    return lo,hi


def finite_log_brackets():
    bounds={2:(Q('0.6931'),Q('0.6932')),
            3:(Q('1.0986'),Q('1.0987')),
            5:(Q('1.6094'),Q('1.6095'))}
    for n,(lo,hi) in bounds.items():
        z=Q(n-1,n+1);z2=z*z;term=z;partial=Q(0)
        for j in range(32):
            partial += 2*term/Q(2*j+1)
            term *= z2
        tail=2*term/(65*(1-z2))
        need(lo<partial<partial+tail<hi and 0<tail<Q(1,10**10),'finite log enclosure '+str(n))
    return bounds


def derivatives(bounds,aggregate):
    l2,u2=bounds[2];l3,u3=bounds[3];l5,u5=bounds[5]
    l4,u4=2*l2,2*u2;l9,u9=2*l3,2*u3
    maximum=Q(17,5000)
    need(all(1-maximum*u>0 for u in (u4,u5,u9)),'positive linear exponential lower factors')
    slope=(18*l3-8*u2-5*u5,18*u3-8*l2-5*l5)
    need(slope==(Q(61817,10000),Q(7731,1250)),'g9 slope coefficient endpoints')
    second_lower=4*(1-maximum*u4)*l4*l4+5*(1-maximum*u5)*l5*l5-9*u9*u9
    second_upper=4*u4*u4+5*u5*u5-9*(1-maximum*u9)*l9*l9
    need(-23<second_lower<second_upper<-22,'strict coarse second derivative brackets')
    need(second_lower==Q(aggregate['g9_second_derivative_rational_lower']) and
         second_upper==Q(aggregate['g9_second_derivative_rational_upper']) and
         list(map(str,slope))==aggregate['g9_derivative_at_zero'] and
         aggregate['C_domain']==['0','17/5000'] and
         aggregate['g9_second_derivative_coarse']==['-23','-22'],'static derivative arithmetic match')
    return slope,(second_lower,second_upper)


def taylor(c,slope):
    need(0<c<=Q(17,5000),'strict positive Taylor evaluation domain')
    lo=slope[0]*c-Q(23,2)*c*c
    hi=slope[1]*c-11*c*c
    need(0<lo<hi,'Taylor integrated positive gain brackets')
    return lo,hi


def canonical_bill(n,debt):
    need(type(n) is int and n>=3,'declared canonical controller branch n>=3')
    a,d=(n-3)//2,(n-2)//2
    rest={1:Q(104*(n-3)),1+8*n:Q(-208)}
    for side in (a,d):
        for k in range(2,side+2):
            rest[8*k]=rest.get(8*k,Q(0))+208
            rest[8*k+1]=rest.get(8*k+1,Q(0))-208
    return combine((n,debt),(1,rest))


def full_invoice(n,paid,helpers):
    # Separate paid and independent productive ledgers, retaining every
    # query, both prefix/suffix whole-idle sequences, and every main bank.
    need(type(n) is int and n in (17,18),'qualified controller counts only')
    sides=((n-3)//2,(n-2)//2)
    queries={1:Q(104*(n-3))}
    idles={};banks={1+8*n:Q(208)}
    for length in sides:
        for j in range(1,length+1):
            rank=8*(j+1)
            idles[rank]=idles.get(rank,Q(0))+208
            banks[rank+1]=banks.get(rank+1,Q(0))+208
    return (combine((n,paid),(1,queries),(1,idles)),
            combine((n,helpers),(1,banks)),queries,idles,banks,sides)


def validate_complete(n,local_paid,local_helpers,paid,targets,expected_census):
    need(all(r>0 and v>0 and v.denominator==1 for h in (paid,targets) for r,v in h.items()),
         'positive integral complete ledger')
    need(combine((1,paid),(-1,targets))==canonical_bill(n,combine((1,local_paid),(-1,local_helpers))),
         'complete paid-minus-target polynomial equals canonical law')
    need(sum(paid.values())==expected_census['paid'] and sum(targets.values())==expected_census['targets'] and
         mass(targets)-mass(paid)==expected_census['surplus'],'complete invoice census')


def witness_groups(m):
    return [{'count':93,'paid_rank':4,'paid_start':0,'target_rank':9,'target_start':0,'new_paid':0,'new_target':5},
            {'count':m-93,'paid_rank':5,'paid_start':0,'target_rank':9,'target_start':93,'new_paid':0,'new_target':4}]


def apply_witness(paid,helpers,groups,expected_count):
    paid_seen=set();target_seen=set();pd={};hd={};gain={}
    for g in groups:
        count,c,r=g['count'],g['paid_rank'],g['target_rank']
        cp,rp=g['new_paid'],g['new_target'];k=c-cp
        need(all(type(x) is int for x in (count,c,r,cp,rp,k,g['paid_start'],g['target_start'])) and count>0,
             'integral multiset allocation')
        need(1<=k<=min(c,r-1) and c<=r<=9 and cp>=0 and rp==r-k>0,
             'strict single-use isolated nested-tail language')
        need({c,r-c}=={4,5} and r==9 and cp==0,'balanced g9 witness ranks')
        for index in range(count):
            pslot=(c,g['paid_start']+index);hslot=(r,g['target_start']+index)
            need(0<=pslot[1]<paid.get(c,0) and 0<=hslot[1]<helpers.get(r,0),'original inventory allocation')
            need(pslot not in paid_seen,'distinct old terminal paid-job multiset slots')
            need(hslot not in target_seen,'distinct old independent helper-target multiset slots')
            paid_seen.add(pslot);target_seen.add(hslot)
        pd[c]=pd.get(c,Q(0))-count;hd[r]=hd.get(r,Q(0))-count
        if cp:pd[cp]=pd.get(cp,Q(0))+count
        hd[rp]=hd.get(rp,Q(0))+count
        gain=combine((1,gain),(count,{c:1,rp:1,r:-1}),(-count,{cp:1} if cp else {}))
    need(len(paid_seen)==len(target_seen)==expected_count,'exact single-use exchange count')
    new_p,new_h=combine((1,paid),(1,pd)),combine((1,helpers),(1,hd))
    need(all(v>0 for h in (new_p,new_h) for v in h.values()),'nonnegative resulting inventories')
    need(sum(new_h.values())==sum(helpers.values())==527,'no new or double-credited independent targets')
    need(mass(new_p)-mass(new_h)==mass(paid)-mass(helpers)==1720,'local debt conserved')
    need(gain=={4:Q(expected_count),5:Q(expected_count),9:Q(-expected_count)},'exact total balanced reward')
    need(combine((1,paid),(-1,helpers),(-1,new_p),(1,new_h))==gain,'complete signed local gain identity')
    return new_p,new_h,pd,hd


def positive_budget(n,m,gain,b17,j17,extra_global=Q(0)):
    need(n in (17,18),'controller nomination domain')
    b=b17 if n==17 else (b17[0]+j17[0]/306,b17[1]+j17[1]/306)
    per=(m*gain[0]-b[1],m*gain[1]-b[0])
    total=(n*per[0]-extra_global,n*per[1]-extra_global)
    need(0<total[0]<total[1]<1,'strict positive complete slack below one global H1')
    return b,per,total


def rejected(operation,label,strength):
    try:
        operation()
    except ValueError:
        return {'outcome':'rejected','strength':strength}
    raise ValueError('mutation accepted '+label)


def main():
    pins=json.loads((B/'INPUTS.json').read_bytes())
    for name,expected in pins['files'].items():
        need(sha((ROOT/name).read_bytes())==expected,'frozen input '+name)
    price_raw=(ROOT/pins['price_result']).read_bytes()
    price=authenticated(price_raw,PRICE_SHA,'price result')
    pair=authenticated((ROOT/pins['price_pair']).read_bytes(),PRICE_PAIR_SHA,'price pair')
    request_raw=(ROOT/pins['price_request']).read_bytes()
    request=authenticated(request_raw,PRICE_REQUEST_SHA,'price request')
    need(pair['request_sha256']==sha(request_raw) and pair['result_sha256']==PRICE_SHA and
         pair['complete_output_equal'] is True and pair['scientific_fields_excluded']==0 and pair['modes']==2,
         'inherited price result/request/pair join')
    need(request['total_seconds']==150 and request['memory_mib']==512 and request['per_child_seconds']==60,
         'inherited price resource contract')
    price_inputs=json.loads((ROOT/pins['price_inputs']).read_bytes())
    need(request['files'][pins['price_inputs']]==sha((ROOT/pins['price_inputs']).read_bytes()),'inherited price INPUTS binding')
    need(price['status']=='PASS_SCOPED_EXACT_ECONOMIC_GATE' and price['reviewed_head']==HEAD and
         price_inputs['current_head']==HEAD and price_inputs['files']['sources/WORD.json.gz']==WORD_SHA,
         'source identities inherited from exact qualified price census')
    log=authenticated((ROOT/pins['log_result']).read_bytes(),LOG_SHA,'prior log certificate')
    aggregate=json.loads((ROOT/pins['aggregate']).read_bytes())
    need(aggregate['source_result_sha256']==PRICE_SHA and aggregate['inherited_price_pair_sha256']==PRICE_PAIR_SHA and
         aggregate['inherited_log_certificate_sha256']==LOG_SHA and aggregate['current_source_head']==HEAD and
         aggregate['current_word_sha256']==WORD_SHA,'aggregate source custody identities')
    need(aggregate['physical_candidates'] is None and aggregate['contact_count'] is None and
         aggregate['independence_or_compatibility_established'] is False,'aggregate multiset-only scope')
    bounds=finite_log_brackets()
    need({str(n):list(map(str,v)) for n,v in bounds.items()}==aggregate['log_bounds']==
         log['certificate']['rational_log_brackets'],'independent finite log brackets match authenticated predecessor')
    slope,second=derivatives(bounds,aggregate)
    p,h=histogram(price['local_paid']),histogram(price['local_helpers'])
    need(p==histogram({1:2211,2:458,3:496,4:93,5:164,6:18,7:14}) and
         h==histogram({4:83,5:5,8:15,9:424}),'authentic current local P/H')
    need(sum(p.values())==3454 and sum(h.values())==527 and mass(p)==6013 and mass(h)==4293,
         'original local paid/helper census')
    old18=full_invoice(18,p,h)
    need(old18[0]==histogram(price['complete_paid']) and old18[1]==histogram(price['complete_targets']),
         'independent complete n18 baseline reconstruction')
    need(canonical_bill(17,combine((1,p),(-1,h)))==histogram(price['n17_numerator_coefficients']),
         'n17 canonical numerator coefficients match authenticated gate')
    witnesses={};internal={}
    for m,n,key,census in [(146,17,'optimistic_m146_census',{'paid':60604,'targets':12079,'surplus':712}),
                            (147,18,'optimistic_m147_fixed18_census',{'paid':64206,'targets':12814,'surplus':760})]:
        groups=witness_groups(m)
        witness_key='optimistic_m146_multiset_witness' if m==146 else 'optimistic_m147_fixed18_multiset_witness'
        need([{'count':g['count'],'old_paid_rank':g['paid_rank'],'new_paid_rank':g['new_paid'],
               'old_target_rank':g['target_rank'],'new_target_rank':g['new_target']} for g in groups]==aggregate[witness_key],
             'static declared multiset groups')
        np,nh,pd,hd=apply_witness(p,h,groups,m)
        invoice=full_invoice(n,np,nh);paid,targets,queries,idles,banks,sides=invoice
        validate_complete(n,np,nh,paid,targets,census)
        saved=aggregate[key]
        need((sum(np.values()),sum(nh.values()),mass(np),mass(nh),mass(np)-mass(nh))==
             (saved['local_paid_count'],saved['local_helper_count'],saved['local_paid_rank_mass'],
              saved['local_helper_rank_mass'],saved['local_rank_debt']),'static witness local census')
        prefix='n'+str(n)+'_complete_'
        need((sum(paid.values()),sum(targets.values()),mass(targets)-mass(paid))==
             (saved[prefix+'paid_count'],saved[prefix+'target_count'],saved[prefix+'rank_surplus']),
             'static witness complete census')
        delta_key='optimistic_m146_delta' if m==146 else 'optimistic_m147_fixed18_delta'
        need(pd==histogram(aggregate[delta_key]['local_paid']) and hd==histogram(aggregate[delta_key]['local_helpers']),
             'static witness paid/helper deltas')
        if m==146:
            need(np==histogram(aggregate['new_local_paid']) and nh==histogram(aggregate['new_local_helpers']),
                 'static optimized146 local inventories')
        need(sum(queries.values())==104*(n-3) and sum(idles.values())==208*(n-3) and
             sum(banks.values())==104*(2*n-4),'all query/idle/main multiplicities charged')
        debt=combine((1,p),(-1,h));new_debt=combine((1,np),(-1,nh))
        for k in (16,17):
            before=combine((k,canonical_bill(k+1,debt)),(-(k+1),canonical_bill(k,debt)))
            after=combine((k,canonical_bill(k+1,new_debt)),(-(k+1),canonical_bill(k,new_debt)))
            need(before==after,'J coefficients unchanged by compatible local debt shift')
        internal[m]=(n,np,nh,paid,targets,census)
        witnesses[str(m)]={'controller_FULL_count':n,'multiset_only_no_source_contact_ids':True,
            'groups':groups,'local_paid':show(np),'local_helpers':show(nh),'paid':show(paid),'targets':show(targets),
            'query_paid':show(queries),'whole_idle_paid':show(idles),'main_targets':show(banks),'side_lengths':list(sides),
            'complete_paid_count':str(sum(paid.values())),'complete_target_count':str(sum(targets.values())),
            'complete_rank_surplus':str(mass(targets)-mass(paid)),'local_rank_debt':'1720'}
    controls={};points=[]
    need(len(price['price_points'])==len(aggregate['points'])==2,'exact two-point scope')
    for point,saved in zip(price['price_points'],aggregate['points']):
        c=Q(point['C']);need(c==Q(saved['C']) and c in (Q(33,10000),Q(6600001,2000000000)),'declared exact price points')
        gain=taylor(c,slope);b17=interval(point['B_current_required_further_net_discount_per_FULL'])
        j16,j17=interval(point['J16']),interval(point['J17'])
        need(j16[1]<0<j17[0] and point['ratio_minimizing_FULL_count']==17,'inherited ratio-minimizer signs')
        need(145*gain[1]<b17[0]<b17[1]<146*gain[0],'145 fail and146 pass in all-controller relaxation')
        b18,per147,total147=positive_budget(18,147,gain,b17,j17)
        _,per146,total146=positive_budget(17,146,gain,b17,j17)
        need(146*gain[1]<b18[0]<b18[1]<147*gain[0],'146 fail and147 pass in fixed18 relaxation')
        scalar_checks={'g9_lower_rational':gain[0],'g9_lower_decimal_exact':gain[0],
          'g9_upper_rational':gain[1],'g9_upper_decimal_exact':gain[1],
          '145_ideal_changes_gain_upper_exact':145*gain[1],
          '146_ideal_changes_gain_lower_exact':146*gain[0],
          'B_lower_inherited':b17[0],'B_upper_inherited':b17[1],
          '145_ideal_changes_deficit_lower':b17[0]-145*gain[1],
          '146_ideal_changes_surplus_lower':146*gain[0]-b17[1],
          'fixed18_B_lower_rational':b18[0],'fixed18_B_upper_rational':b18[1]}
        need(all(Q(saved[k])==value for k,value in scalar_checks.items()),'all static two-point scalar arithmetic')
        for key,value in [('146_all_n_per_FULL_surplus_interval',per146),('146_n17_complete_surplus_interval',total146),
                          ('147_fixed18_per_FULL_surplus_interval',per147),('147_n18_complete_surplus_interval',total147)]:
            need(tuple(map(Q,saved[key]))==value,'static interval arithmetic '+key)
        need(saved['relaxed_minimum_count']==146 and saved['fixed18_minimum_relaxed_count']==147,
             'minimum-count labels match independently checked chains')
        label=str(c)
        controls['145_as_sufficient_'+label]=rejected(lambda:positive_budget(17,145,gain,b17,j17),label,'budget mutation: insufficient count')
        controls['146_fixed18_confusion_'+label]=rejected(lambda:positive_budget(18,146,gain,b17,j17),label,'budget mutation: controller confusion')
        controls['one_extra_global_H1_'+label]=rejected(lambda:positive_budget(17,146,gain,b17,j17,Q(1)),label,'budget mutation: charged extra global job')
        controls['one_extra_global_H1_fixed18_'+label]=rejected(lambda:positive_budget(18,147,gain,b17,j17,Q(1)),label,'budget mutation: charged extra global job')
        points.append({'C':str(c),'g9_bounds':list(map(str,gain)),'B17':list(map(str,b17)),'B18':list(map(str,b18)),
                       'J16':list(map(str,j16)),'J17':list(map(str,j17)),
                       'all_controller_count_chain':list(map(str,(145*gain[1],b17[0],b17[1],146*gain[0]))),
                       'fixed18_count_chain':list(map(str,(146*gain[1],b18[0],b18[1],147*gain[0]))),
                       '146_n17_complete_raw_slack':list(map(str,total146)),
                       '147_n18_complete_raw_slack':list(map(str,total147)),
                       'one_extra_uncompensated_global_H1_excludes_these_witnesses_only':True})
    controls['corrupted_price_result']=rejected(lambda:authenticated(price_raw+b' ',PRICE_SHA,'price result'),
        'source byte','custody mutation before science')
    reused=witness_groups(146);reused[1]['target_start']=0
    controls['reuse_helper_target']=rejected(lambda:apply_witness(p,h,reused,146),'helper reuse','accounting mutation: double-credit independent target')
    paid_reuse=witness_groups(146);paid_reuse[1].update(paid_rank=4,new_target=5)
    controls['reuse_paid_job']=rejected(lambda:apply_witness(p,h,paid_reuse,146),'paid reuse','accounting mutation: double-credit paid removal')
    free_credit=witness_groups(146);free_credit[1]['new_target']=9
    controls['omit_target_loss']=rejected(lambda:apply_witness(p,h,free_credit,146),'target debit','accounting mutation: uncharged productive loss')
    too_many=witness_groups(146);too_many[0]['count']=94;too_many[1]['count']=52;too_many[1]['target_start']=94
    controls['overdraw_rank4']=rejected(lambda:apply_witness(p,h,too_many,146),'rank4 count','accounting mutation: unavailable old paid inventory')
    for m in (146,147):
        n,np,nh,paid,targets,census=internal[m]
        for kind in ('query','idle','main'):
            bp,bt=dict(paid),dict(targets)
            if kind=='query':bp[1]-=104
            elif kind=='idle':bp[16]-=208
            else:bt[1+8*n]+=208
            controls[str(m)+'_'+kind+'_charge']=rejected(
                lambda n=n,np=np,nh=nh,bp=bp,bt=bt,census=census:validate_complete(n,np,nh,bp,bt,census),
                kind,'accounting mutation: complete polynomial/census')
    controls['physical_contact_label']=rejected(lambda:need(aggregate['contact_count']==146,'no physical contact count'),
        'contact label','label sanity only; no source mutant or physical validation')
    result={'schema':'isolated-tail-count-qualification/v1','status':'PASS_SCOPED_SINGLE_USE_TAIL_COUNT_CERTIFICATE',
      'price_result_sha256':PRICE_SHA,'price_pair_sha256':PRICE_PAIR_SHA,'price_request_sha256':PRICE_REQUEST_SHA,
      'inherited_log_result_sha256':LOG_SHA,'reviewed_head':HEAD,'word_sha256':WORD_SHA,
      'finite_log_terms':32,'rational_log_brackets':{str(n):list(map(str,v)) for n,v in bounds.items()},
      'g9_slope_bounds':list(map(str,slope)),'g9_second_derivative_rational_bounds':list(map(str,second)),
      'g9_second_derivative_coarse_bounds':['-23','-22'],'derivative_domain':['0','17/5000'],
      'points':points,'optimistic_multiset_witnesses':witnesses,'mutation_controls':controls,
      'analytic_premises':'Balanced concavity/maximal g_r and strict discrete all-controller reduction are retained paper arguments, not proof-kernel checks. Taylor bounds integrate the certified derivative premises.',
      'scope':'Two exact points only; strict single-use isolated nested tails, distinct original paid/helper slots, additive gain, no new targets/fusion/recycling, unchanged controller law and nonnegative extra debits.',
      'active_ownership_exclusions':aggregate['active_ownership_exclusions'],
      'physical_contacts_found':None,'physical_witness':False,'new_kappa':None,'selected_promotion':False,
      'not_claimed':['general P104 ceiling','larger-C exclusion','physical146/147 contacts','new funding','native or source chronology validation'],
      'credit':'zxv PR5554; GamingPuzzled PR5472/5569; DreamingOfClouds PR5561/5553; thu-nmrc PR5551; Ali Romman and P104 lineage; Clear1nsight audits; Matarener contract audit; retained native/compiler/precision predecessors. OpenAI Codex-assisted finite qualification.'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
