#!/usr/bin/env python3
"""One finite PR5580 price-transfer/count certificate; root execution only.

No price engine, source constructor, contact search, native/row interpreter,
real powers, logarithm or exponential routine. Standard-library exact algebra.
Apache-2.0; substantial OpenAI Codex assistance; predecessor credit in contract.
"""
import base64
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

B=Path(__file__).resolve().parent
ROOT=B.parents[2]
SPEC=importlib.util.spec_from_file_location('independent_tail_finite_helpers',B/'finite.py')
f=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(f)
HEAD='6efa248cf456d6101d757e9d09ba29711d18a13a'
WORD_SHA='b2a98c4bd0dbe86c09e9d15ee060dcf1aab09dbef90aa1e2127676f4039f406b'
WORD_BLOB='9434855e7dad0d0236d23210b3e71a2b83a9ae64'
TRANSFER_SHA='ce5012989710292c7fbd2ad25ebb1570580349ae130bcf534710fe5de64dde45'
REVISION_SHA='efe80b15d50743be5a2e0934bfb831f2eda7fde00a1362eba33d191a4089719f'


def blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def canonical(n,debt):
    f.need(type(n) is int and n>=0,'canonical nonnegative integer count')
    if n==0:return {1:Q(104)}
    if n<=2:return f.combine((n,debt),(1,{1:312-104*n,1+8*n:-208}))
    return f.canonical_bill(n,debt)


def census(word):
    # Structural dimensions only: no containment, version, endpoint row,
    # owned-erasure, chronological frame legality or native-phase inference.
    f.need(word['public']==735 and len(word['program'])==25140,'source public/event declarations')
    dims=[len(frame) for frame in word['frames']];paid={}
    for event in word['program']:
        if event[0]=='MOVE':
            rank=abs(dims[event[3]]-dims[event[2]])
            f.need(rank>0,'positive literal MOVE rank')
            paid[rank]=paid.get(rank,0)+1
    live=set(word['live']);helpers={}
    for owner in range(735):
        if owner not in live and owner-112 not in live:
            rank=dims[word['final'][owner]]-dims[word['initial'][owner]]
            f.need(rank>0,'positive declared independent helper rank')
            helpers[rank]=helpers.get(rank,0)+1
    return f.histogram(paid),f.histogram(helpers)


def source_cost(receipt,old_word,new_word,old_price):
    f.need(set(old_word)==set(new_word),'source JSON key inventory')
    for key in old_word:
        if key!='program':f.need(old_word[key]==new_word[key],'unchanged complete nonprogram field '+key)
    old_scalar=[(i,e) for i,e in enumerate(old_word['program']) if e[0]!='MOVE']
    new_scalar=[(i,e) for i,e in enumerate(new_word['program']) if e[0]!='MOVE']
    f.need(len(old_scalar)==len(new_scalar)==21686,'complete scalar/owned chronology length')
    f.need([e[:-1] for _,e in old_scalar]==[e[:-1] for _,e in new_scalar],
           'unchanged ordered scalar/owned signatures and coefficients')
    changed=[(oi,ni,oe,ne) for (oi,oe),(ni,ne) in zip(old_scalar,new_scalar) if oe!=ne]
    f.need(len(changed)==1 and changed[0][0]==12658 and
           changed[0][2:]==(['ADD',451,228,'1',262],['ADD',451,228,'1',737]),'exact source event/role/chart fingerprint')
    old_p,old_h=census(old_word);p,h=census(new_word)
    f.need(old_p==f.histogram(old_price['local_paid']) and old_h==f.histogram(old_price['local_helpers']),
           'structural old census matches authenticated root receipt')
    f.need(p==f.histogram(receipt['local']['paid']) and h==f.histogram(receipt['local']['helpers']),
           'independent structural new census matches author receipt')
    delta=f.combine((1,p),(-1,old_p))
    f.need(delta==f.histogram({2:1,3:-2,4:1}) and h==old_h,'exact new paid delta and unchanged targets')
    inv=receipt['inventory'];cost=receipt['result'];physical=receipt['physical']
    f.need(inv['all_productive_targets_fixed'] is True and inv['all_public_endpoints_fixed'] is True and
           inv['owned_lifetimes_fixed'] is True and inv['events']==inv['source_events']==25140 and
           inv['ordered_scalar_events']==21686,'author inventory declarations bound to structural fingerprints')
    f.need(f.histogram(inv['local_paid_delta'])==delta and f.histogram(inv['global_paid_delta'])==f.combine((18,delta)),
           'author local/global paid delta')
    f.need(inv['changed_contacts']==[[changed[0][2],changed[0][3]]],'author changed-contact fingerprint')
    paid,targets,queries,idles,banks,sides=f.full_invoice(18,p,h)
    f.need(paid==f.histogram(cost['paid']) and targets==f.histogram(cost['targets']),
           'complete source paid/productive coefficients')
    f.need(targets==f.histogram(old_price['complete_targets']) and
           f.combine((1,paid),(-1,f.histogram(old_price['complete_paid'])))==f.combine((18,delta)),
           'source complete delta and all productive targets fixed')
    f.need(cost['full_forward_calls']==physical['full_calls']==18 and cost['query_shears']==15 and
           cost['whole_idle_jobs']==sum(idles.values())==3120 and physical['ports']==104 and
           physical['new_paid_jobs']==0,'unchanged controller/tariff declarations')
    f.need(f.histogram(physical['whole_idle_jobs'])==idles and f.histogram(physical['main_targets'])==banks,
           'every source whole-idle and main-bank coefficient')
    f.validate_complete(18,p,h,paid,targets,{'paid':66852,'targets':12814,'surplus':760})
    f.need(sum(p.values())==3454 and sum(h.values())==527 and f.mass(p)==6013 and f.mass(h)==4293,
           'complete current local count/rank-mass census')
    return p,h,delta,changed[0][:2]


def gD_derivatives(bounds,transfer):
    l2,u2=bounds[2];l3,u3=bounds[3];l4,u4=2*l2,2*u2;maximum=Q(17,5000)
    slope=(10*l2-6*u3,10*u2-6*l3)
    lo=6*(1-maximum*u3)*l3*l3-2*u2*u2-4*u4*u4
    hi=6*u3*u3-2*(1-maximum*u2)*l2*l2-4*(1-maximum*u4)*l4*l4
    f.need(slope==(Q(847,2500),Q(851,2500)) and Q(-3,2)<lo<hi<Q(-13,10)<0,
           'near-C gD slope and strict negative second-derivative bounds')
    f.need(slope[0]-Q(3,4)*maximum>0,'uniform positivity of integrated gD lower bound on positive declared domain')
    f.need(list(map(str,slope))==transfer['gD_derivative_at_zero_strict_brackets'] and
           [str(lo),str(hi)]==transfer['gD_second_derivative_strict_bounds'] and
           transfer['gD_concavity_scope']==['0','17/5000'] and
           transfer['gD_second_derivative_coarse']==['-3/2','-13/10'],'static gD derivative arithmetic')
    at_one_lower=2*l3*l3-5*u2*u2
    f.need(at_one_lower>0,'positive gD second derivative at C=1 forbids global concavity extrapolation')
    return slope,(lo,hi),at_one_lower


def groups(m):
    return [{'count':94,'paid_rank':4,'paid_start':0,'target_rank':9,'target_start':0,'new_paid':0,'new_target':5},
            {'count':m-94,'paid_rank':5,'paid_start':0,'target_rank':9,'target_start':94,'new_paid':0,'new_target':4}]


def main():
    pins=json.loads((B/'INPUTS.json').read_bytes())
    for name,expected in pins['files'].items():f.need(f.sha((ROOT/name).read_bytes())==expected,'frozen input '+name)
    price_raw=(ROOT/pins['price_result']).read_bytes();price=f.authenticated(price_raw,f.PRICE_SHA,'old B/J result')
    pair=f.authenticated((ROOT/pins['price_pair']).read_bytes(),f.PRICE_PAIR_SHA,'old B/J pair')
    request_raw=(ROOT/pins['price_request']).read_bytes();request=f.authenticated(request_raw,f.PRICE_REQUEST_SHA,'old B/J request')
    f.need(pair['request_sha256']==f.sha(request_raw) and pair['result_sha256']==f.PRICE_SHA and
           pair['complete_output_equal'] is True and pair['scientific_fields_excluded']==0,'old B/J exact request/result pair')
    price_inputs=json.loads((ROOT/pins['price_inputs']).read_bytes())
    f.need(request['files'][pins['price_inputs']]==f.sha((ROOT/pins['price_inputs']).read_bytes()) and
           price_inputs['current_head']==price['reviewed_head']==f.HEAD,'old B/J input/source binding')
    f.need(request['files'][pins['old_word']]==f.sha((ROOT/pins['old_word']).read_bytes())==f.WORD_SHA,
           'old word request binding')
    log=f.authenticated((ROOT/pins['log_result']).read_bytes(),f.LOG_SHA,'prior finite log certificate')
    old_aggregate=json.loads((ROOT/pins['old_aggregate']).read_bytes())
    transfer=f.authenticated((ROOT/pins['transfer']).read_bytes(),TRANSFER_SHA,'new transfer arithmetic')
    f.need(transfer['head']==HEAD and transfer['prior_BJ_receipt_sha256']==f.PRICE_SHA and
           transfer['prior_tail_arithmetic_sha256']==f.sha((ROOT/pins['old_aggregate']).read_bytes()),'transfer dependency join')
    for name,expected in transfer['source_files'].items():f.need(f.sha((ROOT/name).read_bytes())==expected,'curator source '+name)
    capture=json.loads((ROOT/pins['capture']).read_bytes());custody=json.loads((ROOT/pins['custody']).read_bytes())
    f.need(capture['pr']==5580 and capture['head']==HEAD,'exact PR5580 source head')
    text={row['path']:row for row in capture['text_sources']}
    for name,expected in transfer['source_text_blobs'].items():
        row=text[name];raw=row['content'].encode()
        f.need(row['sha']==blob(raw)==expected and '/blob/'+HEAD+'/'+name in row['display_url'],
               'exact captured author text '+name)
    source=json.loads((ROOT/pins['source_result']).read_bytes())
    f.need(source==json.loads(text['research/p104-event-contact-step/RESULT.json']['content']),
           'curator parsed RESULT equals all source author JSON fields')
    f.need((ROOT/pins['source_result_raw']).read_bytes()==text['research/p104-event-contact-step/RESULT.json']['content'].encode(),
           'exact author RESULT serialization retained separately from parsed convenience fixture')
    revision=f.authenticated((ROOT/pins['custody_revision']).read_bytes(),REVISION_SHA,'explicit source custody revision')
    f.need(revision['source_head_unchanged']==HEAD and revision['parsed_JSON_equality'] is True and
           revision['word_unchanged'] is True and
           revision['historical_derived_serialization']['sha256']==f.sha((ROOT/pins['source_result']).read_bytes()) and
           revision['exact_author_serialization']['sha256']==f.sha((ROOT/pins['source_result_raw']).read_bytes()) and
           revision['exact_author_serialization']['git_blob']==text['research/p104-event-contact-step/RESULT.json']['sha'],
           'both immutable source serializations and explicit custody repair join')
    source_manifest=json.loads((ROOT/pins['source_manifest']).read_bytes())
    f.need(source_manifest==json.loads(text['research/p104-event-contact-step/SOURCES.json']['content']),
           'curator parsed SOURCES equals source author JSON')
    parent=next(row for row in source_manifest['external_inputs'] if row['local_path']=='inputs/pr5569-WORD.json.gz')
    f.need(parent['source_commit']==f.HEAD and parent['sha256']==f.WORD_SHA,'source declared exact predecessor')
    invariant=json.loads((ROOT/pins['invariant']).read_bytes());law=invariant['controller_law_code_binding']
    f.need(invariant['head']==HEAD and invariant['parent_head']==f.HEAD and
           invariant['new_word_sha256']==WORD_SHA and invariant['old_word_sha256']==f.WORD_SHA and
           law['ports_v']==104 and law['block_rank_b']==8 and
           law['query_cost']=='104 H1 per query' and law['idle_cost']=='208 H_(8*window_length) per idle' and
           law['source_closure_commit']==source_manifest['retained_source']['commit'] and
           law['source_closure_sha256']==source_manifest['retained_source']['sha256'],
           'source-bound unchanged controller law and closure premises')
    word_raw=(ROOT/pins['word']).read_bytes();row=capture['word_source']
    f.need(f.sha(word_raw)==WORD_SHA and blob(word_raw)==WORD_BLOB==row['sha']==custody['word']['git_blob'],
           'exact new source word SHA/Git blob')
    f.need(base64.b64decode(''.join(row['content'].split()),validate=True)==word_raw,'captured binary source equals frozen word')
    decompressed=gzip.decompress(word_raw)
    f.need(f.sha(decompressed)==custody['word']['decompressed_sha256'],'decompressed word custody')
    old_word=json.loads(gzip.decompress((ROOT/pins['old_word']).read_bytes()));word=json.loads(decompressed)
    p,h,delta,contact_indices=source_cost(source,old_word,word,price)
    f.need(p==f.histogram(transfer['local_paid']) and h==f.histogram(transfer['local_helpers']) and
           delta==f.histogram(transfer['delta_paid_vs_5569']) and transfer['delta_helpers_vs_5569']=={},'static source-cost transfer')
    f.need(f.combine((1,p),(-1,h))==f.histogram(transfer['local_debt']) and
           source['result']['paid']==transfer['source_complete_paid'] and
           source['result']['targets']==transfer['source_complete_targets'],'static complete source polynomial')
    bounds=f.finite_log_brackets()
    f.need({str(n):list(map(str,v)) for n,v in bounds.items()}==log['certificate']['rational_log_brackets'],
           'independent N32 rational logs and prior certificate')
    g9_slope,g9_second=f.derivatives(bounds,old_aggregate)
    d_slope,d_second,d_at_one=gD_derivatives(bounds,transfer)
    old_debt=f.combine((1,f.histogram(price['local_paid'])),(-1,f.histogram(price['local_helpers'])))
    debt=f.combine((1,p),(-1,h))
    for n in (1,2,3,16,17):
        oldj=f.combine((n,canonical(n+1,old_debt)),(-(n+1),canonical(n,old_debt)))
        newj=f.combine((n,canonical(n+1,debt)),(-(n+1),canonical(n,debt)))
        f.need(oldj==newj,'complete J geometry independent of compatible local debt including small-n junction')
        f.need(f.combine((1,canonical(n,debt)),(-1,canonical(n,old_debt)))==f.combine((n,delta)),
               'all-controller per-FULL source delta coefficient identity')
    witness_results={};internals={}
    for saved in transfer['optimistic_witnesses']:
        m,n=saved['changes_per_FULL'],saved['FULL_count'];g=groups(m)
        f.need((m,n) in ((146,17),(147,18)),'exact minimum-count witness nominations')
        f.need([{'count':x['count'],'old_paid_rank':x['paid_rank'],'new_paid_rank':x['new_paid'],
                 'old_target_rank':x['target_rank'],'new_target_rank':x['new_target']} for x in g]==saved['moves'],
               'new94-plus52/53 declared groups')
        np,nh,_,_=f.apply_witness(p,h,g,m)
        paid,targets,query,idle,banks,sides=f.full_invoice(n,np,nh)
        census_expected={'paid':60604 if n==17 else 64206,'targets':12079 if n==17 else 12814,'surplus':712 if n==17 else 760}
        f.validate_complete(n,np,nh,paid,targets,census_expected)
        c=saved['census']
        f.need(np==f.histogram(saved['new_local_paid']) and nh==f.histogram(saved['new_local_helpers']) and
               (sum(np.values()),sum(nh.values()),f.mass(np),f.mass(nh))==
               (c['local_paid_count'],c['local_helper_count'],c['local_paid_rank_mass'],c['local_helper_rank_mass']) and
               (sum(paid.values()),sum(targets.values()),f.mass(targets)-f.mass(paid))==
               (c['complete_paid_count'],c['complete_target_count'],c['complete_rank_surplus']),
               'static current witness local/full inventories and census')
        f.need(sum(query.values())==104*(n-3) and sum(idle.values())==208*(n-3) and sum(banks.values())==104*(2*n-4),
               'all source query/whole-idle/main lines charged')
        internals[m]=(n,np,nh,paid,targets,census_expected)
        witness_results[str(m)]={'FULL_count':n,'multiset_only_no_source_contact_ids':True,'groups':g,
          'local_paid':f.show(np),'local_helpers':f.show(nh),'complete_paid':f.show(paid),'complete_targets':f.show(targets),
          'queries':f.show(query),'whole_idles':f.show(idle),'main_banks':f.show(banks),'side_lengths':list(sides),
          'paid_count':str(sum(paid.values())),'target_count':str(sum(targets.values())),'rank_surplus':str(f.mass(targets)-f.mass(paid))}
    f.need(set(internals)=={146,147},'both complete current witness invoices')
    controls={};points=[]
    f.need(len(price['price_points'])==len(transfer['points'])==2,'two exact points only')
    for old,saved in zip(price['price_points'],transfer['points']):
        c=Q(old['C']);f.need(c==Q(saved['C']) and c in (Q(33,10000),Q(6600001,2000000000)),'declared exact point')
        g9=f.taylor(c,g9_slope);oldb=f.interval(old['B_current_required_further_net_discount_per_FULL'])
        j16,j17=f.interval(old['J16']),f.interval(old['J17'])
        f.need(j16[1]<0<j17[0] and old['ratio_minimizing_FULL_count']==17,'inherited ratio-minimizer signs')
        dlo=d_slope[0]*c-Q(3,4)*c*c;dup=d_slope[1]*c-Q(13,20)*c*c;coarse=d_slope[1]*c
        f.need(0<dlo<dup<coarse,'gD Taylor bounds and positive strict saving')
        tight=(oldb[0]-dup,oldb[1]-dlo);wide=(oldb[0]-coarse,oldb[1])
        f.need(wide[0]<tight[0]<tight[1]<wide[1],'coarse/tighter inherited B5580 transfer intervals')
        fixed18=(tight[0]+j17[0]/306,tight[1]+j17[1]/306)
        wide18=(wide[0]+j17[0]/306,wide[1]+j17[1]/306)
        f.need(145*g9[1]<wide[0]<wide[1]<146*g9[0] and
               146*g9[1]<wide18[0]<wide18[1]<147*g9[0],'robust coarse145/146 and146/147 chains')
        small=[]
        for key in ('special_n1_ratio','special_n2_ratio'):
            before=f.interval(old[key]);after=(before[0]-dup,before[1]-dlo)
            f.need(after[0]>tight[1],'explicit source small-n gate after same local discount')
            small.append(list(map(str,after)))
        _,_,s146=f.positive_budget(17,146,g9,tight,j17)
        _,_,s147=f.positive_budget(18,147,g9,tight,j17)
        _,_,w146=f.positive_budget(17,146,g9,wide,j17)
        _,_,w147=f.positive_budget(18,147,g9,wide,j17)
        checks={'gD_coarse_strict_upper_rational':coarse,'gD_coarse_strict_upper_decimal_exact':coarse,
          'gD_strict_lower_rational':dlo,'gD_strict_upper_rational':dup,
          'gD_strict_lower_decimal_exact':dlo,'gD_strict_upper_decimal_exact':dup,
          'B5580_lower_rational':tight[0],'B5580_upper_rational':tight[1],
          'B5580_lower_decimal_exact':tight[0],'B5580_upper_decimal_exact':tight[1],
          'B18_5580_lower_rational':fixed18[0],'B18_5580_upper_rational':fixed18[1],
          'coarse_145_vs_B_margin_rational':wide[0]-145*g9[1],
          'coarse_146_vs_B18_margin_rational':wide18[0]-146*g9[1]}
        f.need(all(Q(saved[k])==value for k,value in checks.items()),'all source-bound static transfer scalar endpoints')
        f.need(tuple(map(Q,saved['146_n17_complete_raw_surplus_rational_interval']))==s146 and
               tuple(map(Q,saved['147_n18_complete_raw_surplus_rational_interval']))==s147 and
               saved['all_controller_relaxed_minimum_count']==146 and saved['fixed18_relaxed_minimum_count']==147,
               'static current two-point witness slacks and count labels')
        label=str(c)
        for name,n,m,extra in [('insufficient145',17,145,Q(0)),('controller146_fixed18',18,146,Q(0)),
                              ('global_H1_146',17,146,Q(1)),('global_H1_147',18,147,Q(1))]:
            controls[name+'_'+label]=f.rejected(lambda n=n,m=m,extra=extra:f.positive_budget(n,m,g9,wide,j17,extra),
                 name,'budget mutation: coarse current-source accounting gate')
        points.append({'C':str(c),'g9_bounds':list(map(str,g9)),'gD_bounds':list(map(str,(dlo,dup))),
          'gD_coarse_upper':str(coarse),'B17_current_coarse':list(map(str,wide)),'B17_current_tight':list(map(str,tight)),
          'B18_current_coarse':list(map(str,wide18)),'B18_current_tight':list(map(str,fixed18)),
          'coarse_all_controller_chain':list(map(str,(145*g9[1],wide[0],wide[1],146*g9[0]))),
          'coarse_fixed18_chain':list(map(str,(146*g9[1],wide18[0],wide18[1],147*g9[0]))),
          'special_n1_n2_current_ratio_intervals':small,'J16':list(map(str,j16)),'J17':list(map(str,j17)),
          '146_n17_slack_tight':list(map(str,s146)),'147_n18_slack_tight':list(map(str,s147)),
          '146_n17_slack_coarse':list(map(str,w146)),'147_n18_slack_coarse':list(map(str,w147)),
          'one_extra_uncompensated_global_H1_excludes_these_witnesses_only':True})
    controls['corrupt_current_word']=f.rejected(lambda:f.need(f.sha(word_raw+b' ')==WORD_SHA,'word byte'),
        'word byte','custody mutation')
    altered=deepcopy(source);altered['result']['paid']['2']+=1
    controls['alter_author_complete_paid']=f.rejected(lambda:source_cost(altered,old_word,word,price),
        'author paid','source/accounting mutation: all complete coefficients')
    omitted=deepcopy(source);omitted['result']['paid']['1']-=104
    controls['omit_query_from_author_bill']=f.rejected(lambda:source_cost(omitted,old_word,word,price),
        'query bill','source/accounting mutation: charged query')
    altered_target=deepcopy(source);altered_target['local']['helpers']['9']+=1
    controls['alter_author_helper_credit']=f.rejected(lambda:source_cost(altered_target,old_word,word,price),
        'helper credit','source/accounting mutation: structural helper census')
    wrong_source=deepcopy(word)
    wrong_source['ports']=[]
    controls['change_protected_source_ports']=f.rejected(lambda:source_cost(source,old_word,wrong_source,price),
        'source ports','source structural-field mutation; no row/native inference')
    reuse=groups(146);reuse[1]['target_start']=0
    controls['reuse_helper_target']=f.rejected(lambda:f.apply_witness(p,h,reuse,146),'target reuse','accounting mutation: target double-credit')
    reuse_paid=groups(146);reuse_paid[1].update(paid_rank=4,new_target=5)
    controls['reuse_paid_job']=f.rejected(lambda:f.apply_witness(p,h,reuse_paid,146),'paid reuse','accounting mutation: paid removal double-credit')
    free_target=groups(146);free_target[1]['new_target']=9
    controls['omit_target_loss']=f.rejected(lambda:f.apply_witness(p,h,free_target,146),'target loss','accounting mutation: uncharged target loss')
    overdraw=groups(146);overdraw[0]['count']=95;overdraw[1]['count']=51;overdraw[1]['target_start']=95
    controls['overdraw_rank4']=f.rejected(lambda:f.apply_witness(p,h,overdraw,146),'rank4 overdraw','accounting mutation: unavailable old paid job')
    for m,(n,np,nh,paid,targets,cost) in internals.items():
        for kind in ('query','idle','main'):
            bp,bt=dict(paid),dict(targets)
            if kind=='query':bp[1]-=104
            elif kind=='idle':bp[16]-=208
            else:bt[1+8*n]+=208
            controls[str(m)+'_'+kind+'_charge']=f.rejected(
                lambda n=n,np=np,nh=nh,bp=bp,bt=bt,cost=cost:f.validate_complete(n,np,nh,bp,bt,cost),
                kind,'accounting mutation: complete current witness polynomial')
    controls['global_gD_concavity']=f.rejected(lambda:f.need(d_at_one<=0,'gD second derivative positive at1'),
        'global concavity','analytic-domain sanity: actual rational endpoint sign, not a source mutant')
    controls['physical_contact_label']=f.rejected(lambda:f.need(transfer['physical_candidate'] is not None,'no physical candidate'),
        'physical label','label sanity only; no physical validation')
    result={'schema':'pr5580-isolated-tail-count-qualification/v1','status':'PASS_SCOPED_PR5580_SINGLE_USE_TAIL_COUNT_CERTIFICATE',
      'reviewed_head':HEAD,'word_sha256':WORD_SHA,'word_git_blob':WORD_BLOB,'source_contact_fingerprint':{'old_event':contact_indices[0],
      'new_event':contact_indices[1],'destination':451,'source':228,'old_frame':262,'new_frame':737},
      'source_census_scope':'Every literal MOVE dimension and declared helper endpoint; unchanged nonprogram/scalar signatures. No chronological chart legality, row/native proof or complete source admission.',
      'old_root_price_result_sha256':f.PRICE_SHA,'old_root_price_pair_sha256':f.PRICE_PAIR_SHA,
      'static_transfer_sha256':TRANSFER_SHA,'finite_log_terms':32,'g9_slope_bounds':list(map(str,g9_slope)),
      'source_serialization_custody_revision_sha256':REVISION_SHA,
      'g9_second_derivative_rational_bounds':list(map(str,g9_second)),
      'gD_slope_bounds':list(map(str,d_slope)),'gD_second_derivative_rational_bounds':list(map(str,d_second)),
      'gD_second_derivative_positive_at_C1_lower':str(d_at_one),'gD_concavity_domain':['0','17/5000'],
      'current_local_paid':f.show(p),'current_helpers':f.show(h),'local_paid_delta':f.show(delta),
      'points':points,'optimistic_multiset_witnesses':witness_results,'mutation_controls':controls,
      'analytic_premises':'Balanced concavity/max-g_r and PR5554 all-controller reduction remain paper arguments; derivative/Taylor implications use finite rational coefficients and exp(-x)>=1-x. No proof-kernel acceptance.',
      'scope':'Exact PR5580 head, two declared C points, strict single-use isolated nested tails, additive gains, unchanged104-port/rank8/query/whole-idle controller law; no new targets/fusions/recycling.',
      'ownership_and_source_scope_exclusions':['5574 event-frame/event-order constructive inventory','5575 owned-scratch cancellation/retirement',
       '5576 all-holder/COPY-return constructive screen','5125 changed-input/private-COPY completion','5579 owned-holder contact inventory'],
      'physical_contacts_found':None,'physical_witness':False,'new_kappa':None,'selected_promotion':False,
      'historical_request_executed_by_this_certificate':False,'historical_outputs_modified_by_this_certificate':False,
      'credit':'Ali Romman PR5580/5544/5545 and active construction; zxv PR5554; GamingPuzzled PR5472/5569; DreamingOfClouds PR5561/5553; thu-nmrc PR5551; Matarener; Clear1nsight audits; retained native/compiler/precision predecessors. OpenAI Codex assistance.'}
    print(json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
