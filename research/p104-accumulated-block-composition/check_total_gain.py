#!/usr/bin/env python3
"""Exact bounded-exponent certificate for the blocks plus role92 charged gain.

Standard library only. The two block rewrites are from PR5795/PR5796 and role92 is the new accumulated update;
this independently checks their complete signed invoice against PR5802.
No endpoint, native, precision or all-size admission claim is made here.
Mason Hale with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse
import json
from pathlib import Path

PARENT_P = {1:2229,2:456,3:498,4:98,5:159,6:9,7:6}
PARENT_T = {1:24,2:7,3:4,4:105,5:8,7:9,8:20,9:385}
COMPOSED_P = {1:2226,2:456,3:498,4:99,5:162,6:9,7:6}
COMPOSED_T = {1:18,2:7,3:4,4:107,5:14,7:9,8:18,9:385}


def need(x, message):
    if not x:
        raise ValueError(message)


def log_interval(n, terms=80):
    # log n = 2 atanh((n-1)/(n+1)); remaining denominators >= 2M+1.
    # Hence the positive remaining tail is bounded by a geometric series.
    need(n > 1 and terms > 0, 'Positive logarithm input and finite series')
    z = Q(n-1,n+1)
    low = 2*sum((z**(2*j+1)/Q(2*j+1) for j in range(terms)),Q(0))
    tail = 2*z**(2*terms+1)/(Q(2*terms+1)*(1-z*z))
    return low, low+tail


def difference(after,before):
    c=Counter(after);c.subtract(before)
    return {r:n for r,n in c.items() if n}


def check(paid=COMPOSED_P,targets=COMPOSED_T):
    dp=difference(paid,PARENT_P);dt=difference(targets,PARENT_T)
    need(dp=={1:-3,4:1,5:3}, 'Exact paid block change')
    need(dt=={1:-6,4:2,5:6,8:-2}, 'Exact productive block change')
    signed=Counter(dt);signed.subtract(dp)
    signed={r:n for r,n in signed.items() if n}
    need(signed=={1:-3,4:1,5:3,8:-2}, 'Complete signed gain after all costs')
    need(sum(r*n for r,n in signed.items())==0, 'Gain equals zero at exponent one')
    epsilon=Q(17,5000)
    l4,h4=log_interval(4);l5,h5=log_interval(5);l8,h8=log_interval(8)
    # For .9966<=t<=1, 4^t<=4,5^t<=5 and 8^t>=8*exp(-epsilon*log8).
    # exp(-x)>=1-x; replacing log8 by its upper bound lowers that factor.
    factor=1-epsilon*h8
    need(factor>0 and l8>0, 'Both lower product factors positive')
    derivative_upper=4*h4+15*h5-16*factor*l8
    need(derivative_upper<0, 'Strictly negative derivative over whole interval')
    # Integrating g'(s)<=derivative_upper from t to1 gives
    # g(t)>=(-derivative_upper)*(1-t)>0 for every t<1 in the interval.
    claim=Q('.00312418633064')
    full_gain_lower=18*(-derivative_upper)*claim
    need(full_gain_lower>0,'Strict complete gain at published exponent')
    return {'status':'PASS_EXACT_BLOCK_GAIN_INTERVAL',
            'local_delta_paid':dp,'local_delta_targets':dt,'local_signed_gain':signed,
            'full_forward_calls':18,'unchanged_other_caller_costs_required':True,
            'exponent_interval':[1-epsilon,Q(1)],'strict_at_right_endpoint':False,
            'gain_at_right_endpoint':Q(0),'log4_interval':[l4,h4],'log5_interval':[l5,h5],
            'log8_interval':[l8,h8],'lower_exp_factor':factor,
            'derivative_upper':derivative_upper,
            'uniform_gain_lower_formula':'(-derivative_upper)*(1-t)',
            'complete_gain_lower_at_claim':full_gain_lower,'claim':claim,
            'method':'Positive atanh series with explicit geometric tail; exp(-x)>=1-x; monotonicity; exact Fraction arithmetic.',
            'scope':'This charged gain is certified only for .9966<=t<1, not all 0<t<1.'}


def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x


HEADS = {'accumulated':'9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62',
         'blocks':'206cb717c0c07737d61637b93f7502ca48850348'}


def profile(x):
    need(isinstance(x,dict), 'Histogram object')
    out={int(k):v for k,v in x.items()}
    need(len(out)==len(x) and all(type(r) is int and type(n) is int and r>0 and n>0 for r,n in out.items()), 'Positive integral histogram')
    return out


def source_binding(package):
    from hashlib import sha1,sha256
    from pathlib import PurePosixPath
    raw=(package/'SOURCES.json').read_bytes()
    sources=json.loads(raw)
    retained_commit='b83ff89de649be3bd2dc2d885da254bae00c8836'
    need(sources['retained_commit']==retained_commit,'Exact retained source ancestor')
    rows=sources['vendored']
    names=set()
    for row in rows:
        name=row['local_path'];parts=PurePosixPath(name).parts
        need(len(parts)>=3 and parts[0]=='vendor' and parts[1] in HEADS
             and '..' not in parts and '\\' not in name and ':' not in name,
             'Safe exact source name')
        need(name not in names,'Unique runtime origin')
        matching=[r for r in sources['files'] if r.get('local_path')==name]
        need(len(matching)==1,'One retained source pin')
        retained=matching[0]
        need(retained['origin']==row and retained['path']=='research/p104-accumulated-block-composition/'+name
             and retained['pin']=='head:'+retained_commit+':'+retained['path']
             and retained['sha256']==row['sha256'] and retained['git_blob']==row['git_blob'],'Exact retained source and origin mapping')
        names.add(name)
        need(row['pin']=='head:'+HEADS[parts[1]]+':'+row['path'],'Exact predecessor head')
        path=package
        for part in parts:
            path=path/part
            need(not path.is_symlink(),'No source symlink')
        data=path.read_bytes()
        need(sha256(data).hexdigest()==row['sha256'],'Source SHA256')
        need(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'Source Git blob')
    actual={p.relative_to(package).as_posix() for p in (package/'vendor').rglob('*') if p.is_file() or p.is_symlink()}
    need(actual==names,'Complete source inventory')
    return {'files':len(names),'source_manifest_sha256':sha256(raw).hexdigest()}


def check_receipt(result,word,old):
    from hashlib import sha256
    need(result['status']=='PASS_P104_ACCUMULATED_BLOCK_COMPOSITION','Successful complete receipt')
    need(result['source_commits']==HEADS,'Actual exact predecessor heads')
    digest=sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(result['canonical_word_sha256']==digest,'Actual emitted word bound to result')
    need(result['source_local']==old['local'],'Actual source local receipt')
    need(profile(old['local']['paid'])==PARENT_P and profile(old['local']['helpers'])==PARENT_T,'Authenticated source histograms')
    need(word['public']==770 and word['owned_fields']==29 and len(word['program'])==25984,'Actual final event and label counts')
    need(result['instructions']==len(word['program']),'Receipt instruction count')
    widths=[len(x) for x in word['frames']]
    paid=Counter();live=set();lifetimes=peak=scalar=0;maps=set()
    for event in word['program']:
        op,r=event[:2]
        need(type(r) is int and 0<=r<799,'Actual event role range')
        if op=='MOVE':
            _,r,a,b,owned=event
            need((r in live)==owned,'Actual owned move status')
            rank=abs(widths[a]-widths[b]);need(rank>0,'Positive paid rank')
            paid[rank]+=1;maps.add((a,b))
        elif op=='INIT':
            need(r>=770 and r not in live,'Owned lifetime starts once')
            live.add(r);lifetimes+=1;peak=max(peak,len(live));scalar+=2
        elif op=='CLEAR':
            need(r in live,'Owned lifetime ends once')
            live.remove(r);scalar+=2
        else:
            need(op in ('SCALE','ADD','COPY'),'Known scalar operation')
            q=Q(event[-2]);n,d=abs(q.numerator),q.denominator
            need(q and d&(d-1)==0 and abs(q)+1<2**16,'Actual scalar growth and dyadic bounds')
            if op=='SCALE':
                scalar+=2*(abs(n.bit_length()-d.bit_length())+int(q<0))
            else:
                scalar+=2*(2+n.bit_length()+n.bit_count()+d.bit_length()-1)
    need(not live and lifetimes==31 and peak==13,'Actual31 owned lifetimes and peak13')
    main=set(word['live'])|{r+112 for r in word['live']}
    need(len(main)==208,'Actual208 main roles')
    helpers=Counter()
    for r in range(770):
        if r not in main:
            a,b=word['initial'][r],word['final'][r]
            helpers[widths[b]-widths[a]]+=1;maps.add((a,b))
    need(dict(paid)==COMPOSED_P and dict(helpers)==COMPOSED_T,'Fresh paid and productive invoice from word')
    local=result['local'];native=result['native'];price=result['complete_cost']
    need(profile(local['paid'])==dict(paid) and profile(local['helpers'])==dict(helpers),'Actual local invoice receipt')
    mass=sum(r*n for r,n in paid.items())
    need(mass==5934==local['paid_rank_mass'],'New5934 paid rank mass')
    need(scalar==225038==local['real_scalar_allowance'],'All extra real scalars charged')
    need((local['public_inputs'],local['owned_fields'],local['owned_lifetimes'],local['peak_owned_fields'],local['endpoint_coefficients'])==(770,29,31,13,799**2),'Actual final local envelope')
    need(result['separate_columns']['columns']==799 and result['separate_columns']['coefficients']==799**2,'Complete reverse receipt dimensions')
    need(native['distinct_maps']==len(maps) and native['helper_normalizers']==2*sum(helpers.values()) and native['main_adapters']==208,'Actual native map and normalizer census')
    need(profile(native['helpers'])==dict(helpers) and native['wrong_phase_rejected'] is True,'Native receipt matches productive invoice')
    P=Counter({r:18*n for r,n in paid.items()});T=Counter({r:18*n for r,n in helpers.items()})
    P[1]+=15*104;T[145]+=208
    main_targets=Counter({145:208});idles=Counter()
    for length in (7,8):
        for j in range(1,length+1):
            P[8*(j+1)]+=208;idles[8*(j+1)]+=208
            T[1+8*(j+1)]+=208;main_targets[1+8*(j+1)]+=208
    need(profile(price['paid'])==dict(P) and profile(price['targets'])==dict(T),'Independently rebuilt complete caller bill')
    physical=result['physical_caller']
    need(profile(physical['main_targets'])==dict(main_targets) and profile(physical['whole_idle_jobs'])==dict(idles),'Physical caller inventory agrees')
    need(physical['ports']==104 and physical['full_calls']==18 and physical['physical_contacts']==7488 and physical['central_square_columns']==53248 and physical['new_paid_jobs']==0,'Complete physical receipt coverage')
    need((sum(P.values()),sum(T.values()),sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()))==(66888,13444,760),'Complete counts and rank surplus')
    need((price['paid_calls'],price['productive_fields'],price['rank_mass_surplus'],price['full_forward_calls'],price['query_shears'],price['whole_idle_jobs'])==(66888,13444,760,18,15,3120),'Complete invoice receipt census')
    routes=(sum(paid.values())+2*sum(helpers.values())+208+4*104+4*lifetimes)*1000
    n=price['nonrecursive']
    need(routes==5328000==n['local_routes'] and n['local_scalar']==scalar and scalar+routes<10**7,'Complete ordinary local allowance')
    need(n['local_paid_rank_mass']==mass and n['peak_owned_fields']==peak,'New owned and rank-mass precision envelope')
    need(n['raw_scalar_upper']==184647552 and n['raw_budget']==10**9 and n['raw_scalar_upper']<n['raw_budget'],'Retained full caller allowance')
    need(len(word['program'])<26000 and word['public']+word['owned_fields']<1000,'Unchanged coarse growth and slot caps apply')
    k=Q(price['kappa']);tested=Q(price['strictification']['tested'])
    need(k==Q('.00312418633064') and tested==Q('.00312418633564'),'Exact certified claim and tested point')
    need(Q(price['previous_pr5802'])==Q(old['complete_cost']['kappa'])==Q('.00312336057'),'Actual strongest source claim')
    need(Q(price['gain'])==k-Q(price['previous_pr5802']),'Actual improvement amount')
    grid=result['fixed_contract_grid_optimum']
    need(Q(grid['largest_published_grid'])==k and Q(grid['largest_tested_grid'])==tested and Q(grid['next_tested_grid'])==tested+Q(1,10**14),'Bound actual fixed-contract grid')
    need(Q(grid['accepted_margin'][0])>0 and Q(grid['rejected_margin'][1])<0 and Q(grid['derivative_upper'])<0,'Strict fixed-contract ceiling signs')
    return {'canonical_word_sha256':digest,'paid_calls':sum(P.values()),'productive_fields':sum(T.values()),'paid_rank_mass':mass,'native_distinct_maps':len(maps),'real_scalar_allowance':scalar,'local_routes':routes,'owned_fields':29,'owned_lifetimes':lifetimes,'peak_owned_fields':peak,'kappa':k,'tested':tested}


def main():
    from copy import deepcopy
    import gzip
    from hashlib import sha256
    parser=argparse.ArgumentParser(description='Independently recount the actual word, authenticate sources, bind its complete receipt, and prove the total moment gain. Full endpoint/native checks remain in verify.py.')
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args();package=args.package.resolve()
    binding=source_binding(package)
    raw=(package/'RESULT.json').read_bytes();result=json.loads(raw)
    word=json.loads(gzip.decompress((package/'WORD.json.gz').read_bytes()))
    old=json.loads((package/'vendor/accumulated/RESULT.json').read_bytes())
    need(result['source_authentication']==binding,'Actual authenticated source receipt')
    receipt=check_receipt(result,word,old)
    gain=check(profile(result['local']['paid']),profile(result['local']['helpers']))
    controls={}
    for label in ['omit_paid_call','old_rank_mass','wrong_source_head','missing_lifetime']:
        bad=deepcopy(result)
        if label=='omit_paid_call':bad['complete_cost']['paid']['1']-=1
        elif label=='old_rank_mass':bad['complete_cost']['nonrecursive']['local_paid_rank_mass']=5918
        elif label=='wrong_source_head':bad['source_commits']['blocks']='0'*40
        else:bad['local']['owned_lifetimes']=30
        try:check_receipt(bad,word,old)
        except ValueError as error:controls[label]=str(error)
        else:raise ValueError('Invalid receipt mutation accepted: '+label)
    payload={'status':'PASS_INDEPENDENT_TOTAL_GAIN_AND_INVOICE','source_heads':HEADS,'source_authentication':binding,'result_sha256':sha256(raw).hexdigest(),'recount':receipt,'gain_certificate':gain,'negative_controls':controls,'scope':'Independent source/word/invoice/growth-envelope check and exact interval-wide gain proof. The full registered verify.py separately checks scalar endpoints, native phase identities, physical geometry and exact root/compiler arithmetic.'}
    text=json.dumps(encode(payload),indent=2)+'\n'
    if args.out:args.out.write_text(text)
    else:
        retained=json.loads((package/'TOTAL-GAIN.json').read_bytes())
        need(json.dumps(retained,sort_keys=True)==json.dumps(encode(payload),sort_keys=True), 'Complete retained independent receipt')
    print(payload['status'])


if __name__=='__main__':main()
