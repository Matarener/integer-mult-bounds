#!/usr/bin/env python3
"""One fixed PR5678 nearest-contact prerequisite; root-only bounded execution.

Apache-2.0. Credit Ali Romman and retained P104/source/native/caller/compiler
contributors; classical compensated-update identity; OpenAI Codex assistance.
No source imports, constructor, changed full word, numeric powers or pricing.
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
HEAD='af814f6f3c477fdd13b8f04380a33cf32004966b'
WORD_SHA='b56281a67f84832198be2f2ad36d87b75244d424f1e0a6f4dda2df74f20cc08d'
WORD_BLOB='8be2b3e1c2d02034d4579bef5d36df7761d826ff'
LIMIT=16*1024*1024
ENTRY=['ADD',438,733,'-4',794]
R=['ADD',140,438,'-1/2',794]
SPECTATOR=['ADD',160,451,'-1/2',911]
Y=['ADD',144,438,'-1/2',911]
EXIT=['ADD',438,733,'4',127]
P_PREFIX=['ADD',144,140,'1']
Q_PREFIX=['ADD',144,140,'-1']

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
    need(pin['head']==HEAD and pin['bytes']==120135 and pin['sha256']==WORD_SHA and pin['git_blob']==WORD_BLOB,
         'Exact fixed source binding')
    need(len(raw)==120135 and sha(raw)==WORD_SHA and blob(raw)==WORD_BLOB,'Compressed WORD byte/Git/SHA identity before decode')


def integer_token(s):
    need(len(s)<=11,'Bounded JSON integer token')
    n=int(s);need(abs(n)<=2**31-1,'Bounded JSON integer value');return n


def pairs_unique(pairs):
    out={}
    for k,v in pairs:
        need(k not in out,'Duplicate JSON descriptor key');out[k]=v
    return out


def bad_constant(s):raise SourceError('Unexpected JSON numeric constant '+s)


def read_capped(stream,limit):
    decoded=stream.read(limit+1)
    need(len(decoded)<=limit,'Decompressed WORD exceeds hard abort cap')
    need(stream.read(1)==b'','Decompressed WORD has excess data')
    return decoded


def decode(raw,pin):
    authenticate_word(raw,pin)
    with gzip.GzipFile(fileobj=io.BytesIO(raw),mode='rb') as stream:
        decoded=read_capped(stream,LIMIT)
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


def roles(e):return set(e[1:3]) if e[0] in ('ADD','COPY') else {e[1]}
def access(e,r):
    out=[]
    if e[0] in ('ADD','COPY'):
        if e[2]==r:out.append('read')
        if e[1]==r:out.append('write')
    elif e[0]=='SCALE' and e[1]==r:out=['read','write']
    return out

def grammar(e,n,owned,frame_count):
    need(isinstance(e,list) and e and isinstance(e[0],str),'Instruction record')
    op=e[0];width={'ADD':5,'COPY':5,'SCALE':4,'MOVE':5,'INIT':3,'CLEAR':3}
    need(op in width and len(e)==width[op],'Known opcode and exact fail-closed width')
    need(isint(e[1]) and 0<=e[1]<n+owned,'Destination role')
    def frame(f):need(isint(f) and 0<=f<frame_count,'Frame index')
    if op=='MOVE':
        frame(e[2]);frame(e[3]);need(type(e[4]) is bool,'MOVE ownership flag')
    elif op in ('INIT','CLEAR'):
        need(e[1]>=n,'Public lifetime operation is unsupported/source failure');frame(e[2])
    else:
        frame(e[-1]);need(isinstance(e[-2],str) and len(e[-2])<=128,'Bounded exact scalar coefficient')
        q=Q(e[-2]);need(q and q.numerator.bit_length()<=256 and q.denominator.bit_length()<=256 and
            q.denominator&(q.denominator-1)==0 and abs(q)+1<2**16,'Bounded nonzero dyadic scalar')
        if op=='SCALE':need(abs(q.numerator)&(abs(q.numerator)-1)==0,'Dyadic unit SCALE')
        else:
            need(isint(e[2]) and 0<=e[2]<n+owned and e[1]!=e[2],'Distinct valid scalar source')
            if op=='COPY':need(e[1]>=n,'Public COPY is not the declared grammar')


def validate(word,receipt):
    need(isinstance(word,dict) and word.get('schema')=='p104-paid-interior-bases/1','Exact emitted source schema')
    n,owned=word.get('public'),word.get('owned_fields')
    need(n==743 and isint(n) and owned==9 and isint(owned),'Retained public/owned counts')
    frames=word.get('frames');need(isinstance(frames,list) and 912<=len(frames)<=4096,'Bounded frame table')
    need(all(isinstance(b,list) and len(b)<=9 for b in frames),'Nine-axis frame cap')
    spaces=[reduced_basis(b) for b in frames]
    need([len(spaces[f]) for f in (794,911,127)]==[6,7,9] and strict(spaces[794],spaces[911]) and strict(spaces[911],spaces[127]),'Published high-pair ordered strict frame chain')
    for name in ('initial','final'):
        need(isinstance(word.get(name),list) and len(word[name])==n and all(isint(f) and 0<=f<len(frames) for f in word[name]),'Complete public boundary descriptor')
    live=word.get('live');need(isinstance(live,list) and len(live)==104 and all(isint(r) and 0<=r<n and r+112<n for r in live) and len(set(live))==104,'104 distinct live roles')
    main=set(live)|{r+112 for r in live};need(len(main)==208,'Main role convention')
    helper=Counter()
    for r in range(n):
        if r not in main:
            a,b=word['initial'][r],word['final'][r];need(strict(spaces[a],spaces[b]),'Helper productive boundary')
            helper[len(spaces[b])-len(spaces[a])]+=1
    need(shown(helper)==receipt['local']['helpers'] and receipt['local']['public_inputs']==n and receipt['local']['owned_fields']==owned,'Authenticated source descriptor/target receipt')
    program=word.get('program');need(isinstance(program,list) and 0<len(program)<=26000,'Hard instruction cap')
    current=word['initial'][:]+[None]*owned;zero=[None]*owned;life=peak=0;semantic=[];protected=[]
    for i,e in enumerate(program):
        grammar(e,n,owned,len(frames));op,r=e[:2]
        if r>=n or (op in ('ADD','COPY') and e[2]>=n):protected.append(e)
        if op=='MOVE':
            need(current[r]==e[2] and e[4] is (r>=n),'Exact MOVE source/ownership chronology')
            need(strict(spaces[e[3]],spaces[e[2]]) if r>=n else strict(spaces[e[2]],spaces[e[3]]),'Typed old MOVE nesting')
            current[r]=e[3];continue
        semantic.append({'event':i,'instruction':e})
        if op=='INIT':
            need(current[r] is None,'Fresh owned lifetime');current[r]=e[2];zero[r-n]=True;life+=1
            peak=max(peak,sum(f is not None for f in current[n:]))
        elif op=='CLEAR':
            need(current[r]==e[2] and zero[r-n] is not None,'Active owned CLEAR chart');current[r]=None;zero[r-n]=None
        else:
            need(all(current[a]==e[-1] for a in roles(e)),'Every scalar operand has its declared actual common chart')
            if op=='COPY':
                need(zero[r-n] is True,'COPY destination proven zero by conservative lifetime bookkeeping')
                zero[r-n]=zero[e[2]-n] if e[2]>=n else False
            elif op=='ADD' and r>=n:
                if e[2]<n or zero[e[2]-n] is not True:zero[r-n]=False
            # Nonzero SCALE preserves the conservative zero flag.
    need(current[:n]==word['final'] and all(f is None for f in current[n:]),'All source public/owned exits')
    need(life==receipt['local']['owned_lifetimes']==11 and peak==receipt['local']['peak_owned_fields']==2,'Owned lifetime/peak counts')
    return spaces,program,semantic,{'public_inputs':n,'helpers':535,'owned_fields':owned,'owned_lifetimes':life,'peak_owned_fields':peak,
      'protected_subsequence_sha256':sha(canonical(protected)),
      'boundary_descriptor_sha256':sha(canonical({k:word[k] for k in ('public','owned_fields','initial','final','live')})),
      'scope':'Chart/lifetime descriptors only; no endpoint rows, owned erasure-zero, native phases or physical caller admission.'}


def unique(items,label):
    need(len(items)==1,'Unique '+label+' context required');return items[0]


def bind(semantic):
    es=[x['instruction'] for x in semantic]
    start=unique([i for i in range(len(es)-1) if es[i:i+2]==[ENTRY,R]],'entry/R')
    end=unique([i for i in range(len(es)-2) if es[i:i+3]==[SPECTATOR,Y,EXIT]],'spectator/Y/exit')
    bound={'entry':semantic[start],'R':semantic[start+1],'spectator':semantic[end],'Y':semantic[end+1],'exit':semantic[end+2]}
    need(bound['entry']['event']<bound['R']['event']<bound['spectator']['event']<bound['Y']['event']<bound['exit']['event'],'Ordered published fixed contexts')
    return bound


def contact(row,r):
    return {'event':row['event'],'instruction':row['instruction'],'access':access(row['instruction'],r)}


def predicate(semantic,bound):
    ri,yi=bound['R']['event'],bound['Y']['event']
    previous=[contact(x,144) for x in semantic if x['event']<yi and 144 in roles(x['instruction'])]
    nearest=previous[-2:]
    answer={'nearest_144_contacts':nearest,'certified_R':bound['R'],'certified_Y':bound['Y']}
    if len(nearest)!=2 or nearest[0]['instruction'][:4]!=P_PREFIX or nearest[1]['instruction'][:4]!=Q_PREFIX:
        return dict(answer,status='NEAREST_MISMATCH',reason='The fixed two immediately preceding semantic contacts do not equal the nominated P/Q opcode, roles and signs.')
    p,q=nearest;pi,qi=p['event'],q['event']
    if not pi<ri<qi<yi:return dict(answer,status='CORRIDOR_MISMATCH',reason='The actual order is not P<R<Q<Y.')
    observers=[contact(x,144) for x in semantic if pi<=x['event']<=yi and 144 in roles(x['instruction'])]
    if [x['event'] for x in observers]!=[pi,qi,yi]:return dict(answer,status='CORRIDOR_MISMATCH',reason='An additional receiver observer exists.',observers=observers)
    writes=[contact(x,140) for x in semantic if pi<x['event']<qi and 'write' in access(x['instruction'],140)]
    if [x['event'] for x in writes]!=[ri]:return dict(answer,status='CORRIDOR_MISMATCH',reason='R is not the sole logical 140 write between P and Q.',writes_140=writes)
    changed=[contact(x,438) for x in semantic if ri<x['event']<yi and 'write' in access(x['instruction'],438)]
    if changed:return dict(answer,status='CORRIDOR_MISMATCH',reason='438 has another logical write between R and Y.',writes_438=changed)
    return dict(answer,status='MATCH',P=p,Q=q,observers_144=observers,writes_140=writes,writes_438=changed,
                retained_other_140_reads=[contact(x,140) for x in semantic if pi<x['event']<yi and 'read' in access(x['instruction'],140) and x['event'] not in (pi,qi)])


def semantics(events):return [{'event':i,'instruction':e} for i,e in enumerate(events) if e[0]!='MOVE']

def rejected(action):
    try:action()
    except (SourceError,ValueError,KeyError):return 'rejected'
    raise SourceError('A bounded control unexpectedly accepted')


def control_suite(raw,pin):
    valid=[['ADD',144,140,'1',794],ENTRY,R,['ADD',144,140,'-1',911],SPECTATOR,Y,EXIT]
    def status(events):
        sem=semantics(events);return predicate(sem,bind(sem))['status']
    def require_match(events):need(status(events)=='MATCH','Synthetic conditional predicate')
    positive=status(valid);need(positive=='MATCH','Exact valid synthetic conditional pattern')
    # Independent three-row exact algebra for P,R,Q,Y, not a source lookup.
    rows={140:[Q(1),Q(0),Q(0)],144:[Q(0),Q(1),Q(0)],438:[Q(0),Q(0),Q(1)]}
    for e in [valid[0],R,valid[3],Y]:rows[e[1]]=[a+Q(e[3])*b for a,b in zip(rows[e[1]],rows[e[2]])]
    need(rows[144]==[0,1,0] and rows[140]==[1,0,Q(-1,2)] and rows[438]==[0,0,1],'Exact synthetic arbitrary-input identity')
    sign=[e[:] for e in valid];sign[3][3]='1'
    role=[e[:] for e in valid];role[3][2]=141
    observer=valid[:4]+[['COPY',743,144,'1',911]]+valid[4:]
    write=valid[:3]+[['ADD',140,451,'1',794]]+valid[3:]
    hwrite=valid[:3]+[['ADD',438,451,'1',794]]+valid[3:]
    return {
      'compressed_corruption_before_decode':rejected(lambda:authenticate_word(raw[:-1]+bytes([raw[-1]^1]),pin)),
      'nearest_sign':rejected(lambda:require_match(sign)),
      'nearest_role':rejected(lambda:require_match(role)),
      'additional_owned_COPY_source_observer':rejected(lambda:require_match(observer)),
      'additional_140_write':rejected(lambda:require_match(write)),
      'additional_438_write':rejected(lambda:require_match(hwrite)),
      'nonunique_anchor_context':rejected(lambda:bind(semantics(valid+[ENTRY,R]))),
      'unexpected_opcode':rejected(lambda:grammar(['OBSERVE',144,911],743,9,4096)),
      'decompression_abort_cap':rejected(lambda:read_capped(io.BytesIO(b'ab'),1)),
      'valid_synthetic_conditional_pattern':{'outcome':'accepted','exact_identity':True,
       'scope':'Pure semantic/algebra unit case, not an actual typed source/native program.'}}


def route(word,program,semantic,r,spaces,deleted):
    all_contacts=[dict(contact(x,r),frame=x['instruction'][-1]) for x in semantic if r in roles(x['instruction'])]
    kept=[x for x in all_contacts if x['event'] not in deleted]
    def path(cs):
        required=[{'kind':'input','frame':word['initial'][r]}]+cs+[{'kind':'final','frame':word['final'][r]}]
        visits=[]
        for c in required:
            if not visits or visits[-1]!=c['frame']:visits.append(c['frame'])
        edges=[]
        for a,b in zip(visits,visits[1:]):
            need(strict(spaces[a],spaces[b]),'Direct required path is strictly increasing; no repair/intermediate search')
            edges.append({'old':a,'new':b,'rank':len(spaces[b])-len(spaces[a])})
        return {'required':required,'coalesced_frames':visits,'edges':edges,'histogram':shown(Counter(e['rank'] for e in edges))}
    old,new=path(all_contacts),path(kept)
    actual=[{'old':e[2],'new':e[3],'rank':len(spaces[e[3]])-len(spaces[e[2]])} for e in program if e[0]=='MOVE' and e[1]==r]
    need(old['edges']==actual,'Complete old required-contact path equals every actual source MOVE for affected role')
    old_h={int(k):v for k,v in old['histogram'].items()};new_h={int(k):v for k,v in new['histogram'].items()}
    delta=Counter(new_h);delta.subtract(old_h)
    return {'old':old,'new_contact_subchain':new,'actual_old_MOVE_chain':actual,'signed_local_delta':shown(delta)},set(old['coalesced_frames'])|set(new['coalesced_frames'])


def main():
    inputs=json.loads((HERE/'INPUTS.json').read_bytes())
    for name,digest in inputs['files'].items():need(sha((ROOT/name).read_bytes())==digest,'Frozen input SHA '+name)
    for name,digest in inputs['git_blobs'].items():need(blob((ROOT/name).read_bytes())==digest,'Published input Git blob '+name)
    pin=json.loads((ROOT/inputs['word_custody']).read_bytes());raw=(ROOT/inputs['word']).read_bytes();authenticate_word(raw,pin)
    nomination=json.loads((HERE/'NOMINATION.json').read_bytes())
    need(nomination['source']['head']==HEAD and nomination['fixed_anchors']['R']['instruction']==R and nomination['fixed_anchors']['Y']['instruction']==Y and
         nomination['missing_anchors']['P']['required_prefix']==P_PREFIX and nomination['missing_anchors']['Q']['required_prefix']==Q_PREFIX,'One fixed nomination binding')
    witness=json.loads((ROOT/inputs['witness']).read_bytes());high=witness[0]
    need((high['a'],high['b'],high['coefficient'],high['entry_frame'],high['exit_frame'])==(438,733,'-4',794,127) and
         high['blocks'][0]['after']==[R] and high['blocks'][1]['after']==[SPECTATOR,Y] and high['start_block']==1090 and high['end_block']==1314,'Published source witness context; stage identifiers are provenance only')
    controls=control_suite(raw,pin)
    word,length,digest=decode(raw,pin);receipt=json.loads((ROOT/inputs['source_result']).read_bytes())
    spaces,program,sem,desc=validate(word,receipt);bound=bind(sem);answer=predicate(sem,bound)
    output={'schema':'pr5678-fixed-nearest-contact-prerequisite/v1','source_head':HEAD,'source_word_sha256':WORD_SHA,'source_word_git_blob':WORD_BLOB,
      'decompressed_hard_cap':LIMIT,'decompressed_bytes_observed':length,'decompressed_source_sha256':digest,'instruction_count':len(program),
      'source_descriptor_checks':desc,'unique_published_context':bound,'nearest_predicate':answer,'controls':controls,
      'stage_indices_used_as_final_indices':False,'logical_observer_rule':'All ADD/COPY source reads and destination writes, SCALE reads+writes; owned interfaces included. MOVE excluded only from logical observation under the declared source invariant.',
      'physical_native_limitation':'MOVE charts and lifetime descriptors are checked on the source. Excluding transport from logical observers is not native/global-phase/caller equivalence for a changed word.',
      'changed_full_word_emitted':False,'source_modules_imported':False,'pricing_or_numeric_powers_evaluated':False,'new_kappa':None,'candidate_paid_invoice':None,
      'fallback_search':False,'other_contact_pairs_queried':False,'native_admission':False,'endpoint_admission':False,'ordinary_or_compiler_admission':False}
    if answer['status']=='NEAREST_MISMATCH':
        output.update(status='COMPLETED_FIXED_NEAREST_CONTACT_FALSIFIER',stop_reason=answer['reason'],complete_affected_route_extraction_performed=False)
        return output
    if answer['status']!='MATCH':
        output.update(status='COMPLETED_FIXED_CONTACT_PREDICATE_FALSIFIER',stop_reason=answer['reason'],complete_affected_route_extraction_performed=False)
        return output
    deleted={answer['P']['event'],answer['Q']['event'],bound['Y']['event']}
    need(all(e['instruction'][0]=='ADD' and max(e['instruction'][1:3])<743 for e in [answer['P'],answer['Q'],bound['Y']]),'Only three public ADD contact deletions')
    routes={};frames=set();total=Counter()
    for r in (140,144,438):
        row,used=route(word,program,sem,r,spaces,deleted);routes[str(r)]=row;frames|=used
        total.update({int(k):n for k,n in row['signed_local_delta'].items()})
    need(sum(r*n for r,n in total.items())==0,'Endpoint-fixed path deletion preserves rank mass')
    output.update(status='COMPLETED_FIXED_NEAREST_CONTACT_CONDITIONAL_PACKET',stop_reason='The one logical prerequisite matches; contact-subchain/rank packet only. Separate full native/caller/ordinary/funding validation is required.',
      complete_affected_route_extraction_performed=True,deleted_public_scalar_contact_indices=sorted(deleted),affected_role_routes=routes,
      ordered_frame_bases={str(f):word['frames'][f] for f in sorted(frames)},signed_affected_local_rank_histogram=shown(total),
      symbolic_cost='sum_r delta_r H_r(C), H_r(C)=r^(1-C); no powers or prices evaluated.',
      retained_other_140_reads=answer['retained_other_140_reads'],conditional_target_delta=0,
      target_transfer_status='Conditional only; original independent input/endpoints/targets/protected owned sequence and full caller must be realized and verified later.')
    return output


if __name__=='__main__':
    try:output=main();code=0
    except Exception as error:
        output={'schema':'pr5678-fixed-nearest-contact-prerequisite/v1','status':'SOURCE_OR_BINDING_FAILURE',
          'failure':type(error).__name__+': '+str(error),'new_kappa':None,'changed_full_word_emitted':False,
          'source_modules_imported':False,'pricing_or_numeric_powers_evaluated':False,'fallback_search':False};code=2
    print(json.dumps(output,sort_keys=True,separators=(',',':')));sys.exit(code)
