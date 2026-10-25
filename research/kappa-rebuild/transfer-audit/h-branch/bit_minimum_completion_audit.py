#!/usr/bin/env python3
"""Independent minimum-row PR589 completion and literal native replay.

Only previously independent audit helpers are imported. The producer's
rank, inverse, geometry, factoring and replay functions are not used.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import json

import bit_h_completion_audit as A
from outer_transfer_audit import moment_margin

HERE=Path(__file__).resolve().parent
BIT=A.BIT
ROOT=A.ROOT


def scalar_word(program,offset,frame):
    out=[]
    for op,d,s in program:
        d+=offset;s+=offset
        if op=='ADD':
            out.append(['ADD',d,s,frame])
        else:
            A.need(op=='SWAP' and d!=s,'Only literal ADD and three-ADD SWAP lowering')
            out.extend([['ADD',d,s,frame],['ADD',s,d,frame],['ADD',d,s,frame]])
    return out


def geometry(word,artifact):
    h=A.read(BIT/'PR589-H-NATIVE.json.gz')
    actual,dirt=A.native_geometry(word,h['geometry'])
    J=actual['J_rows'];basis=[];selected=[]
    for i,row in enumerate(J):
        if A.rank(basis+[row])>len(basis):
            basis.append(row)
        else:
            selected.append(i)
    A.need(len(basis)==108 and selected==[106,109,110],'Independent exact corank and dependent-row selection')
    G=list(J);choices=[];corrections=[]
    for i in selected:
        col=next(j for j in range(111) if A.rank(basis+[1<<j])>len(basis))
        basis.append(1<<col);choices.append(col);corrections.append(J[i]^(1<<col));G[i]=1<<col
    inverse=A.inv(G)
    A.need(A.rank(G)==111 and choices==[0,1,2],'Independent minimum three-row invertible completion')
    A.need(A.rank(corrections)==3,'Literal correction has rank three')
    A.need(A.mm(G,inverse)==A.mm(inverse,G)==[1<<i for i in range(111)],'Exact two-sided inverse')
    claimed=artifact['geometry']
    expected={'J_rows':J,'G_rows':G,'G_inverse_rows':inverse,'selected':selected,
              'replacement_source_columns':choices,'correction_rows':corrections}
    A.need(all(claimed[k]==v for k,v in expected.items()),'New artifact geometry equals independently reconstructed matrices')
    programs=[]
    for name,wanted,adds in [('forward_constant_program',G,6166),('inverse_constant_program',inverse,6222)]:
        current=[1<<i for i in range(111)]
        for _,d,s,_ in scalar_word(claimed[name],0,0):
            A.need(0<=d<111 and 0<=s<111 and d!=s,'Invertible scalar gate operands')
            current[d]^=current[s]
        count=len(scalar_word(claimed[name],0,0))
        A.need(current==wanted and count==adds,'Literal scalar factor and full three-ADD swap charge')
        programs.append({'name':name,'unit_ADDs':count})
    controls=[]
    for i in selected:
        broken=list(G);broken[i]=J[i];r=A.rank(broken)
        A.need(r==110,'Omitting any displayed completion row loses invertibility')
        controls.append({'omitted_row':i,'rank':r})
    return expected,dirt,programs,controls


def replay(word,artifact,geo,projectors,dims,key):
    forward=key.endswith('forward');wrapped=key.startswith('wrapped')
    n=661;v=111;current=list(word['start'] if forward else word['final'])+[None]
    values=[1<<i for i in range(n)]+[0];paid=Counter();counts=Counter();active=None;episodes=0
    for event in artifact[key]:
        op=event[0];counts[op]+=1
        if op=='MOVE':
            _,role,old,new,cost=event
            A.need(current[role]==old,'Actual native frame entrance')
            low,high=(old,new) if dims[old]<dims[new] else (new,old)
            a,b=projectors[low],projectors[high]
            A.need(dims[high]-dims[low]==cost and A.mul(a,b)==a and A.mul(b,a)==a,
                   'Every paid transition has its actual rational nested projector and rank')
            current[role]=new;paid[cost]+=1
            if role==n:
                A.need(active is not None and active['moved'] is False and old==1 and cost==1,
                       'Only one paid rank-one full-to-hole correction descent')
                active['moved']=True
        elif op=='ADD':
            _,d,s,frame=event
            A.need(d!=s and current[d]==current[s]==frame,'All scalar gates occur at literal equal physical frames')
            if active is not None:
                A.need(not 0<=d<v,'Original completed sources immutable during owned gather/use/discard')
                if d==n:
                    A.need(not active['moved'] and 0<=s<v and frame==1,'Gather uses only completed source operands')
                    active['gather'].append(s)
                else:
                    A.need(s==n and active['moved'] and v<=d<2*v,'Only target reads the owned transformed stream')
                    active['reads'].append(d-v)
            values[d]^=values[s]
        elif op=='OWNED_CLEAR':
            _,r,f=event
            A.need(r==n and values[r]==0 and current[r] is None and active is None and f==1,
                   'Fresh private zero stream is uncredited')
            current[r]=f;active={'moved':False,'gather':[],'reads':[]}
        else:
            A.need(op=='OWNED_ERASE','Known native operation')
            _,r,f=event
            A.need(r==n and active is not None and active['moved'] and current[r]==f and len(active['reads'])==1,
                   'Complete private use before charged erase')
            port=active['reads'][0];j=geo['selected'].index(port)
            A.need(sum(1<<s for s in active['gather'])==geo['correction_rows'][j] and f==word['final'][v+port],
                   'Actual correction row and native hole contact')
            A.need(values[n]!=0,'The permitted erasure really exercises nonzero private data')
            values[r]=0;current[r]=None;active=None;episodes+=1
    expected=[1<<i for i in range(n)]+[0]
    if wrapped:
        matrix=geo['G_rows'] if forward else geo['G_inverse_rows']
        for i,row in enumerate(matrix):
            expected[i]=row;expected[v+i]=row^(row<<v)
    else:
        for i,row in enumerate(geo['G_rows']):
            expected[v+i]^=row
    A.need(values==expected,'All661 independent input columns, including all439 arbitrary helpers')
    A.need(current==list(word['final'] if forward else word['start'])+[None] and active is None and episodes==3,
           'Every native endpoint and all three owned episodes close')
    A.need(paid==Counter({1:1326,2:1342,3:79,4:44,5:102,6:11,7:10}),'Complete literal native invoice')
    adds=11625+(2*(6166 if forward else 6222) if wrapped else 0)
    A.need(counts==Counter(ADD=adds,MOVE=2914,OWNED_CLEAR=3,OWNED_ERASE=3),'All primitive operations, including wrapper swaps')
    return {'variant':key,'all_arbitrary_columns':661,'arbitrary_helpers_restored':439,
            'paid':dict(sorted(paid.items())),'paid_rank_mass':sum(r*c for r,c in paid.items()),
            'primitive_counts':dict(counts),'owned_fields':1,'owned_episodes':episodes}


def main():
    artifact_path=BIT/'PR589-MINIMUM-COMPLETION-NATIVE.json.gz'
    receipt_path=BIT/'PR589-MINIMUM-COMPLETION.json'
    original_path=BIT/'sources/pr589-regenerated/WORD.json.gz'
    artifact,receipt,word=A.read(artifact_path),A.read(receipt_path),A.read(original_path)
    A.need(A.digest(artifact_path)==receipt['artifact_sha256'],'Exact new native artifact')
    A.need(A.digest(original_path)==receipt['source_word_sha256']==artifact['source_word_sha256'],'Exact retained source')
    geo,dirt,programs,controls=geometry(word,artifact)
    A.need(dirt==artifact['new_D'],'Exact dirty compensation reconstructed from original raw A/B')
    projectors,dims=A.frame_geometry(word)
    cut=next(i for i,e in enumerate(artifact['forward']) if e[0]=='OWNED_CLEAR')
    body=artifact['forward'][:cut];correction=artifact['forward'][cut:]
    A.need([A.strip_rank(e) for e in body]==A.expected_body(word,dirt),'Literal no-COPY native body preserved')
    reversed_body=[['MOVE',e[1],e[3],e[2],e[4]] if e[0]=='MOVE' else e for e in reversed(body)]
    A.need(artifact['reverse']==correction+reversed_body,'Reverse chronological native body and early completed gather')
    claimed=artifact['geometry']
    A.need(artifact['wrapped_forward']==scalar_word(claimed['forward_constant_program'],111,0)+artifact['forward']+
           scalar_word(claimed['forward_constant_program'],0,1),'Forward G at legal pretarget and postsource common frames')
    A.need(artifact['wrapped_reverse']==scalar_word(claimed['inverse_constant_program'],0,1)+artifact['reverse']+
           scalar_word(claimed['inverse_constant_program'],111,0),'Reverse G inverse at legal common frames')
    checks=[replay(word,artifact,geo,projectors,dims,key) for key in ('forward','reverse','wrapped_forward','wrapped_reverse')]
    contacts=A.physical_completions(word,geo,projectors)
    body_receipt=A.read(BIT/'MIXED-PRODUCTIVE-BIT.json')
    case=next(x for x in body_receipt['candidates'] if x['pairs']==3 and x['keep_idle_mask']==43)
    paid=Counter({int(r):7*n for r,n in checks[0]['paid'].items()})
    idle=sum(2*111*(e[2]>>1).bit_count() for e in case['physical_events'] if e[0]=='IDLE')
    A.need(idle==1332,'Actual retained idle-stage requests')
    paid[7]+=idle;targets=Counter({8:3073,22:444,50:222})
    A.need(dict(sorted(paid.items()))=={int(k):v for k,v in receipt['global_raw_paid'].items()},'Complete proposed raw p3 bill')
    repaired=paid.copy();repaired[1]+=666
    mass=lambda p:sum(r*c for r,c in p.items())
    A.need(mass(targets)-mass(paid)==645 and mass(targets)-mass(repaired)==-21,'Direct complete repair is still unfunded at rank potential')
    raw_interval=moment_margin(targets,paid,F(1,250));fixed_interval=moment_margin(targets,repaired,F(1,250))
    A.need(raw_interval[0]>0 and fixed_interval[1]<0,'Independent directed-rational .004 controls')
    sources=[Path(__file__),HERE/'bit_h_completion_audit.py',HERE/'BIT-H-COMPLETION-AUDIT.json',
             artifact_path,receipt_path,BIT/'pr589_minimum_completion.py',original_path,
             BIT/'MIXED-PRODUCTIVE-BIT.json',A.AUDIT/'outer_transfer_audit.py']
    result={'schema':'independent-minimum-row-PR589-native-completion-audit/1',
            'status':'PASS_MINIMUM_THREE_ROWS_ALL_NATIVE_COLUMNS_BUT_DIRECT_GLOBAL_BILL_FAILS',
            'sources_sha256':{str(p.relative_to(ROOT)):A.digest(p) for p in sources},
            'geometry':{'J_rank':108,'G_rank':111,'selected_rows':geo['selected'],'replacement_columns':geo['replacement_source_columns'],
                        'correction_rank':3,'minimum_modified_rows':3,
                        'proof':'rank(J+E)<=rank(J)+rank(E)<=108+number_of_modified_rows; three displayed changes attain111.'},
            'common_frame_scalar_programs':programs,'full_native_checks':checks,
            'physical_line_contacts':contacts,'omitted_row_controls':controls,
            'p3':{'targets':dict(sorted(targets.items())),'raw_paid':dict(sorted(paid.items())),
                  'direct_repaired_paid':dict(sorted(repaired.items())),'raw_rank_margin':645,'direct_repaired_rank_margin':-21,
                  'raw_margin_at_004':[str(v) for v in raw_interval],'direct_repaired_margin_at_004':[str(v) for v in fixed_interval]},
            'not_claimed':['A new full global H/G supplier.','A lower bound on unrestricted coupled boundary decoding.','A new kappa.']}
    out=HERE/'BIT-MINIMUM-COMPLETION-AUDIT.json';out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'rank_J':108,'rank_G':111,'selected':[106,109,110],
                      'all_columns':661,'native_variants':4,'local_rank_mass':checks[0]['paid_rank_mass'],
                      'direct_repaired_global_rank_margin':-21}))


if __name__=='__main__':
    main()
