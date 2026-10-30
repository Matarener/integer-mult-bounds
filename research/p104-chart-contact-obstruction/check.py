#!/usr/bin/env python3
"""One fixed 5660 contact-chart prerequisite; root-only scientific execution.

No source imports, constructor, changed full word, endpoint/native replay or
whole pricing engine. Exact rational/bit arithmetic; Apache-2.0.
Credit Ali Romman and retained source/controller/native/compiler contributors;
OpenAI Codex assistance. See CONTRACT.md for the deliberately limited claim.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE
HEAD='3b0b4f37d5005f381ed9cfcccebfbe1ab35c71aa'
WORD_SHA='9e78864cd46fc443c6183674588c99c52cfb8e8e408c7ba09bb50cf4694463f6'
WORD_BLOB='9e68b7de6bfc23bc4fe9940c718dba350ba8a893'
LIMIT=16*1024*1024
BLOCK=[['ADD',165,586,'1/2',3],['ADD',586,733,'-4',597],
       ['ADD',21,586,'1',652],['ADD',165,21,'-1/2',652]]
POINTS=(Q(33,10000),Q(6600001,2000000000))


class SourceError(ValueError):pass


def need(ok,message):
    if not ok:raise SourceError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()
def blob(raw):return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def shown(h):return {str(r):n for r,n in sorted(h.items()) if n}
def mass(h):return sum(r*n for r,n in h.items())
def clean(h):return {r:n for r,n in h.items() if n}
def isint(x):return type(x) is int


def authenticate_word(raw,pin):
    need(pin['head']==HEAD and pin['bytes']==107909 and pin['sha256']==WORD_SHA and pin['git_blob']==WORD_BLOB,
         'Exact fixed source binding')
    need(len(raw)==107909 and sha(raw)==WORD_SHA and blob(raw)==WORD_BLOB,'Compressed WORD byte/Git/SHA identity before decode')


def integer_token(s):
    need(len(s)<=11,'Bounded JSON integer token')
    n=int(s);need(abs(n)<=2**31-1,'Bounded JSON integer value');return n


def pairs_unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,'Duplicate JSON descriptor key');out[k]=v
    return out


def bad_constant(s):raise SourceError('Unexpected JSON numeric constant '+s)


def decode(raw,pin):
    authenticate_word(raw,pin)
    with gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb') as stream:
        decoded=stream.read(LIMIT+1)
        need(len(decoded)<=LIMIT,'Decompressed WORD exceeds hard 16 MiB abort cap')
        need(stream.read(1)==b'','Decompressed WORD has excess data')
    word=json.loads(decoded,object_pairs_hook=pairs_unique,parse_int=integer_token,parse_constant=bad_constant)
    stack=[(word,0)];nodes=0
    while stack:
        x,depth=stack.pop();nodes+=1
        need(nodes<=500000 and depth<=16,'Descriptor node/depth cap')
        if isinstance(x,dict):
            need(len(x)<=64 and all(isinstance(k,str) and len(k)<=128 for k in x),'Descriptor field cap')
            stack.extend((v,depth+1) for v in x.values())
        elif isinstance(x,list):
            need(len(x)<=26000,'Descriptor array cap');stack.extend((v,depth+1) for v in x)
        elif isinstance(x,str):need(len(x)<=4096,'Descriptor string cap')
        elif isinstance(x,float):need(x==x and abs(x)!=float('inf'),'Finite unused metadata number')
        else:need(x is None or type(x) in (int,bool),'Unexpected descriptor value')
    return word,len(decoded),sha(decoded)


def reduced_basis(vectors):
    pivots={}
    for v in vectors:
        need(isint(v) and 0<v<512,'Nine-axis binary frame vector')
        x=v
        for p,b in sorted(pivots.items(),reverse=True):
            if x&(1<<p):x^=b
        need(x!=0,'Independent frame basis')
        pivots[x.bit_length()-1]=x
    return sorted(pivots.items(),reverse=True)


def included(a,b):
    for _,v in a:
        x=v
        for p,w in b:
            if x&(1<<p):x^=w
        if x:return False
    return True


def strict(a,b):return len(a)<len(b) and included(a,b)


def frame_binding(frames):
    need(frames[3]==[] and frames[597]==[82] and frames[652]==[82,268],
         'Exact pinned zero/one/two-dimensional chart labels and ordered bases')


def event_roles(e):return set(e[1:3]) if e[0] in ('ADD','COPY') else {e[1]}


def descriptor(word):
    need(isinstance(word,dict) and word.get('schema')=='p104-contact-rewrite/1','Exact emitted WORD schema')
    for name in ('frames','public','owned_fields','initial','final','live','program'):need(name in word,'Missing descriptor '+name)
    n,owned=word['public'],word['owned_fields']
    need(isint(n) and n==743 and isint(owned) and owned==9,'Exact public and owned slot counts')
    frames=word['frames'];need(isinstance(frames,list) and 653<=len(frames)<=4096,'Frame table cap')
    need(all(isinstance(b,list) and len(b)<=9 for b in frames),'Frame dimension cap')
    spaces=[reduced_basis(b) for b in frames];frame_binding(frames)
    def frame(f):need(isint(f) and 0<=f<len(frames),'Valid frame index')
    for name in ('initial','final'):
        need(isinstance(word[name],list) and len(word[name])==n,'Exact public boundary width')
        for f in word[name]:frame(f)
    live=word['live'];need(isinstance(live,list) and len(live)==len(set(live))==104 and
        all(isint(r) and 0<=r<n and r+112<n for r in live),'Exact main role descriptor')
    main=set(live)|{r+112 for r in live};need(len(main)==208,'Disjoint main input/output roles')
    helpers={r for r in range(n) if r not in main};need(len(helpers)==535 and {586,733}<=helpers,'Retained independent helpers')
    target=Counter()
    for r in helpers:
        a,b=word['initial'][r],word['final'][r]
        need(strict(spaces[a],spaces[b]),'Source helper boundary is strictly increasing')
        target[len(spaces[b])-len(spaces[a])]+=1
    program=word['program'];need(isinstance(program,list) and 0<len(program)<=26000,'Instruction hard cap')
    current={r:word['initial'][r] for r in (586,733)}
    owned_current=[None]*owned;lifetimes=peak=0
    skeleton=[];contacts={r:[] for r in current};moves={r:[] for r in current};owned_tape=[];scalar_tape=[]
    for i,e in enumerate(program):
        need(isinstance(e,list) and e and isinstance(e[0],str),'Instruction record type')
        op=e[0];need(op in ('MOVE','ADD','COPY','SCALE','INIT','CLEAR'),'Opcode covered by contact extraction')
        size={'MOVE':5,'ADD':5,'COPY':5,'SCALE':4,'INIT':3,'CLEAR':3}[op]
        need(len(e)==size,'Exact opcode width')
        need(isint(e[1]) and 0<=e[1]<n+owned,'Valid destination/owner role')
        if op in ('ADD','COPY'):need(isint(e[2]) and 0<=e[2]<n+owned,'Valid source role')
        if op=='MOVE':
            frame(e[2]);frame(e[3]);need(type(e[4]) is bool,'MOVE orientation field')
        elif op in ('INIT','CLEAR'):frame(e[2]);need(e[1]>=n,'No public lifetime creation/erasure')
        else:
            frame(e[-1]);need(isinstance(e[-2],str) and len(e[-2])<=128,'Exact bounded scalar coefficient')
            q=Q(e[-2]);need(q.numerator.bit_length()<=256 and q.denominator.bit_length()<=256 and
                q.denominator&(q.denominator-1)==0 and q and abs(q)+1<2**16,'Bounded nonzero dyadic scalar coefficient')
            if op=='SCALE':need(abs(q.numerator)&(abs(q.numerator)-1)==0,'Dyadic unit SCALE grammar')
            if op in ('ADD','COPY'):need(e[1]!=e[2],'Distinct scalar operands')
            if op=='COPY':need(e[1]>=n,'COPY destination is an owned slot')
        touched=event_roles(e)
        if op!='MOVE' or e[1]>=n:skeleton.append((i,e))
        if any(r>=n for r in touched):owned_tape.append(e)
        if op!='MOVE':scalar_tape.append(e[:-1])
        if op=='INIT':
            slot=e[1]-n;need(owned_current[slot] is None,'Fresh owned lifetime')
            owned_current[slot]=e[2];lifetimes+=1;peak=max(peak,sum(x is not None for x in owned_current))
        elif op=='CLEAR':
            slot=e[1]-n;need(owned_current[slot]==e[2],'Declared owned erasure chart');owned_current[slot]=None
        elif op=='MOVE':
            if e[1]>=n:
                slot=e[1]-n;need(owned_current[slot]==e[2] and e[4] is True and strict(spaces[e[3]],spaces[e[2]]),
                    'Existing owned MOVE chronology/orientation/reverse inclusion');owned_current[slot]=e[3]
            if e[1] in current:
                r=e[1];need(e[4] is False and current[r]==e[2] and strict(spaces[e[2]],spaces[e[3]]),
                    'Existing affected public MOVE is direct strict forward inclusion')
                moves[r].append({'event':i,'old':e[2],'new':e[3],'rank':len(spaces[e[3]])-len(spaces[e[2]])});current[r]=e[3]
        else:
            for r in touched:
                if r>=n:need(owned_current[r-n]==e[-1],'Owned scalar contact chart/activity')
                if r in current:
                    need(current[r]==e[-1],'Existing affected role contact matches its actual current chart')
                    access=[]
                    if e[1]==r:access.append('destination')
                    if op in ('ADD','COPY') and e[2]==r:access.append('source')
                    contacts[r].append({'event':i,'op':op,'instruction':e,'frame':e[-1],'access':access})
    need(lifetimes==11 and peak==2 and all(x is None for x in owned_current),'Complete declared owned chronology counts and final inactivity')
    for r in current:need(current[r]==word['final'][r],'Affected role actual final chart')
    return spaces,contacts,moves,skeleton,shown(target),{
        'owned_lifetimes':lifetimes,'peak_owned':peak,'owned_subsequence_sha256':sha(canonical(owned_tape)),
        'scalar_opcode_roles_coefficients_order_sha256':sha(canonical(scalar_tape)),
        'public_boundary_descriptor_sha256':sha(canonical({k:word[k] for k in ('public','owned_fields','initial','final','live')})),
        'unmodified_nonprogram_descriptor_sha256':sha(canonical({k:v for k,v in word.items() if k!='program'})),
        'scope':'Descriptor and chart/lifetime chronology checks only; no endpoint linear-map, erasure-zero or native phase replay.'}


def unique_site(sites):
    need(len(sites)==1,'Exactly one final four-gate skeleton occurrence');return sites[0]


def check_block(block):need(block==BLOCK,'Exact fixed four-gate scalar roles/coefficients/charts')


def route(initial,final,contacts,spaces):
    required=[{'kind':'input','frame':initial}]+[dict(c,kind='contact') for c in contacts]+[{'kind':'final','frame':final}]
    visits=[]
    for item in required:
        if not visits or visits[-1]!=item['frame']:visits.append(item['frame'])
    edges=[];failures=[]
    for a,b in zip(visits,visits[1:]):
        ok=strict(spaces[a],spaces[b]);entry={'old':a,'new':b,'rank':len(spaces[b])-len(spaces[a]),'strict_forward':ok}
        edges.append(entry)
        if not ok:failures.append(entry)
    return {'required':required,'coalesced_visits':visits,'edges':edges,'unsupported_edges':failures}


def histogram(edges):
    need(all(e['strict_forward'] and e['rank']>0 for e in edges),'Only legal forward edges earn a paid histogram')
    return dict(Counter(e['rank'] for e in edges))


def sumhist(a,b):
    x=Counter(a);x.update(b);return clean(dict(x))


def difference(new,old):
    x=Counter(new);x.subtract(old);return clean(dict(x))


def charged(old_h,old_s,new_h,new_s,supplied):
    expected=difference(sumhist(new_h,new_s),sumhist(old_h,old_s))
    need(expected==supplied,'Full recipient plus donor charges, with no omitted donor leg');return expected


def log_bounds(r):
    def unit(u):
        z=(u-1)/(u+1);need(0<=z<=Q(1,3),'Rational logarithm domain')
        low=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(32)),Q(0))
        return low,low+2*z**65/(65*(1-z*z))
    k=r.bit_length()-1;a,b=unit(Q(r,2**k));l,u=unit(Q(2));return a+k*l,b+k*u


def power(r,c):
    if r==1:return Q(1),Q(1)
    l,u=log_bounds(r)
    def exponential(x):
        need(0<=x<1,'Alternating exponential domain');term=s=Q(1);low=high=None
        for j in range(1,13):
            term*=-x/j;s+=term
            if j==11:low=s
            if j==12:high=s
        return low,high
    a,b=r*exponential(c*u)[0],r*exponential(c*l)[1];mesh=10**24
    low=Q((a*mesh).__floor__(),mesh);high=Q(-((-b*mesh).__floor__()),mesh)
    need(low<=a<=b<=high,'Exact outward rational price mesh');return low,high


def price(delta,c):
    low=high=Q(0)
    for r,n in delta.items():
        need(isint(r) and 1<=r<=9 and isint(n),'Bounded exact signed paid coefficient')
        a,b=power(r,c);low+=n*(a if n>=0 else b);high+=n*(b if n>=0 else a)
    return {'C':str(c),'local_paid_cost_difference_interval':[str(low),str(high)],
            'full18_paid_cost_difference_interval':[str(18*low),str(18*high)]},low,high


def reject(action,strength):
    try:action()
    except (SourceError,ValueError,KeyError):return {'outcome':'rejected','strength':strength}
    raise SourceError('Control unexpectedly accepted: '+strength)


def main():
    inputs=json.loads((HERE/'INPUTS.json').read_bytes())
    for name,digest in inputs['files'].items():need(sha((ROOT/name).read_bytes())==digest,'Frozen input SHA '+name)
    pin=json.loads((ROOT/inputs['word_custody']).read_bytes());raw=(ROOT/inputs['word']).read_bytes()
    authenticate_word(raw,pin)
    for name,expected in inputs['git_blobs'].items():
        need(blob((ROOT/name).read_bytes())==expected,'Authenticated published text Git blob '+name)
    receipt=json.loads((ROOT/inputs['source_result']).read_bytes())
    nominal=json.loads((ROOT/inputs['nomination']).read_bytes())
    need(nominal['single_object']['source_head']==HEAD and nominal['single_object']['edit_old']==BLOCK[1] and
         nominal['single_object']['edit_new']==['ADD',586,733,'-4',652],'Single fixed nomination')
    word,length,decoded_sha=decode(raw,pin)
    spaces,contacts,moves,skeleton,helpers,boundaries=descriptor(word)
    need(helpers=={str(k):v for k,v in receipt['local']['helpers'].items()} and
         receipt['local']['public_inputs']==743 and receipt['local']['owned_fields']==9 and
         receipt['local']['owned_lifetimes']==11 and receipt['local']['peak_owned_fields']==2,
         'Published local target/boundary/owned descriptor binding')
    simple=[e for _,e in skeleton]
    site=unique_site([i for i in range(len(simple)-3) if simple[i:i+4]==BLOCK]);check_block(simple[site:site+4])
    actual_indices=[skeleton[site+j][0] for j in range(4)];anchor=actual_indices[1]
    old={};new={};modified={};neighbor={}
    for r in (586,733):
        old[r]=route(word['initial'][r],word['final'][r],contacts[r],spaces)
        need(not old[r]['unsupported_edges'],'Existing affected contact chain is strictly forward')
        need([(e['old'],e['new'],e['rank']) for e in old[r]['edges']]==[(e['old'],e['new'],e['rank']) for e in moves[r]],
             'Complete old required-contact route equals all actual published affected MOVEs')
        hit=[i for i,c in enumerate(contacts[r]) if c['event']==anchor]
        need(len(hit)==1 and contacts[r][hit[0]]['instruction']==BLOCK[1],'Both role lists bind the same literal donor/recipient event')
        seq=[dict(c) for c in contacts[r]];i=hit[0]
        before=seq[i-1] if i else {'kind':'input','frame':word['initial'][r]}
        after=seq[i+1] if i+1<len(seq) else {'kind':'final','frame':word['final'][r]}
        neighbor[r]={'preceding':before,'succeeding':after}
        entry=dict(seq[i]);entry['frame']=652;entry['instruction']=['ADD',586,733,'-4',652];seq[i]=entry
        need(sum(a!=b for a,b in zip(contacts[r],seq))==1 and len(seq)==len(contacts[r]),'Only one chart contact changes in each affected role list')
        modified[r]=seq;new[r]=route(word['initial'][r],word['final'][r],seq,spaces)
    controls={}
    controls['compressed_byte_corruption']=reject(lambda:authenticate_word(raw[:-1]+bytes([raw[-1]^1]),pin),'Immutable byte/Git/SHA corruption; no mutated decode')
    badpin=dict(pin);badpin['head']='0'*40
    controls['wrong_source_binding']=reject(lambda:authenticate_word(raw,badpin),'Exact source-head custody mutation')
    controls['ambiguous_anchor']=reject(lambda:unique_site([site,site]),'Duplicate match-evidence cardinality; no changed full program')
    badblock=[e[:] for e in BLOCK];badblock[1][-1]=596
    controls['wrong_anchor_chart']=reject(lambda:check_block(badblock),'Actual four-gate binding field mutation')
    small={3:[],597:[82],652:[82,269]}
    controls['wrong_frame_space']=reject(lambda:frame_binding(small),'Ordered frame basis mutation')
    controls['reversed_nesting']=reject(lambda:need(strict(spaces[652],spaces[597]),'Reverse public route'), 'Actual reverse inclusion of fixed source spaces')
    oh,os=histogram(old[586]['edges']),histogram(old[733]['edges'])
    need(bool(os),'At least one actual positive donor MOVE for donor-charge control')
    donor_missing=dict(os);first=next(iter(donor_missing));donor_missing[first]-=1;donor_missing=clean(donor_missing)
    wrong=difference(sumhist(oh,os),sumhist(oh,donor_missing))
    controls['omitted_donor_charge']=reject(lambda:charged(oh,os,oh,os,wrong),'Omit one actual donor old-MOVE charge while recipient/new bill held fixed')
    result={'schema':'one-h586-chart-retag-feasibility/v1','source_head':HEAD,'source_word_sha256':WORD_SHA,
      'source_word_git_blob':WORD_BLOB,'decompressed_bytes_observed':length,'decompressed_hard_cap':LIMIT,'decompressed_source_sha256':decoded_sha,
      'source_schema':word['schema'],'instruction_count':len(word['program']),'public_inputs':743,'helpers':535,
      'unique_final_block':{'skeleton_index':site,'actual_program_indices':actual_indices,'events':BLOCK,'old_indices_transferred':False,
        'skeleton_keeps_owned_MOVEs':True},
      'source_descriptor_checks':boundaries,'source_contacts':{str(r):contacts[r] for r in contacts},
      'source_MOVE_chains':{str(r):moves[r] for r in moves},'old_routes':{str(r):old[r] for r in old},
      'counterfactual_contact_lists':{str(r):modified[r] for r in modified},'new_routes':{str(r):new[r] for r in new},
      'donor_W_Z':{'W':neighbor[733]['preceding'],'Z':neighbor[733]['succeeding'],
        'p':len(spaces[neighbor[733]['preceding']['frame']]),'r':len(spaces[neighbor[733]['succeeding']['frame']]),
        'spaces':{str(f):word['frames'][f] for f in {neighbor[733]['preceding']['frame'],597,652,neighbor[733]['succeeding']['frame']}}},
      'controls':controls,'changed_full_word_emitted':False,'source_modules_imported':False,
      'scope':'Only one chart in two required-contact lists; no chronology/basis/boundary/owned changes or route search.',
      'new_kappa':None,'physical_construction':None,'native_phase_checked':False,'arbitrary_input_endpoint_replay':False,
      'ordinary_costs_certified':False,'full_pricing_or_compiler_run':False,'fallback_search':False,
      'interpretation':'Only a necessary physical/economic prerequisite. Descriptor preservation is not independent endpoint/native admission.'}
    baseline=receipt['complete_cost'];paid={int(r):n for r,n in baseline['paid'].items()};targets={int(r):n for r,n in baseline['targets'].items()}
    need(baseline['full_forward_calls']==18 and baseline['query_shears']==15 and baseline['whole_idle_jobs']==3120 and
         sum(paid.values())==66474 and sum(targets.values())==12958 and mass(targets)-mass(paid)==760 and
         baseline['paid']==nominal['recursive_accounting']['baseline_paid'] and baseline['targets']==nominal['recursive_accounting']['baseline_targets'],
         'Authenticated fixed full 18-call baseline invoice')
    result['baseline_complete_paid']=shown(paid);result['baseline_complete_targets']=shown(targets)
    result['baseline_invoice_status']='Published authenticated receipt; no whole-source paid census or price replay.'
    unsupported={str(r):new[r]['unsupported_edges'] for r in new if new[r]['unsupported_edges']}
    if unsupported:
        result['status']='STOP_UNSUPPORTED_FORWARD_NESTING';result['stop_reason']='The one fixed new direct route is not strictly forward in the exact source spaces.'
        result['unsupported_edges']=unsupported;result['candidate_paid_invoice']=None;return result
    nh,ns=histogram(new[586]['edges']),histogram(new[733]['edges'])
    dh,ds=difference(nh,oh),difference(ns,os);delta=charged(oh,os,nh,ns,sumhist(dh,ds))
    need(dh=={1:-2,2:1},'Recipient predicted route reduction actually bound')
    need(mass(delta)==0,'Same endpoint forward paths preserve affected rank mass')
    candidate=Counter(paid);candidate.update({r:18*n for r,n in delta.items()})
    need(all(n>=0 for n in candidate.values()) and mass(targets)-mass(candidate)==760,'Complete donor-adjusted invoice and rank mass')
    result.update({'recipient_local_delta':shown(dh),'donor_local_delta':shown(ds),'complete_two_role_local_delta':shown(delta),
       'old_recipient_histogram':shown(oh),'old_donor_histogram':shown(os),'new_recipient_histogram':shown(nh),'new_donor_histogram':shown(ns),
       'candidate_paid_invoice':shown(dict(candidate)),'conditional_unchanged_targets':shown(targets),
       'candidate_paid_count':sum(candidate.values()),'candidate_target_count':sum(targets.values()),
       'target_transfer_premise':'Same public boundary/target descriptors and caller; requires later realized chart induction and native/endpoint validation.'})
    prices=[];intervals=[]
    for c in POINTS:
        row,lo,hi=price(delta,c);prices.append(row);intervals.append((lo,hi))
    result['two_point_paid_cost_differences']=prices
    if all(hi<0 for lo,hi in intervals):
        result['status']='FAVORABLE_PHYSICAL_ECONOMIC_PREREQUISITE_ONLY';result['stop_reason']='Both exact donor-adjusted paid-cost upper bounds are negative; no construction or funded result follows.'
    elif any(lo>=0 for lo,hi in intervals):
        result['status']='STOP_DONOR_ADJUSTED_NO_GAIN';result['stop_reason']='At least one required point has nonnegative exact paid-cost lower bound, including exact-zero cases.'
    else:
        result['status']='STOP_UNRESOLVED_SIGN';result['stop_reason']='The fixed rational enclosures do not certify negative cost at both points. No fallback precision/route search.'
    return result


if __name__=='__main__':
    try:output=main();code=0
    except Exception as error:
        output={'schema':'one-h586-chart-retag-feasibility/v1','status':'STOP_SOURCE_OR_BINDING_FAILURE',
          'failure':type(error).__name__+': '+str(error),'new_kappa':None,'changed_full_word_emitted':False,
          'source_modules_imported':False,'fallback_search':False};code=2
    print(json.dumps(output,sort_keys=True,separators=(',',':')))
    sys.exit(code)
