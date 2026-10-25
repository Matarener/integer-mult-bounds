#!/usr/bin/env python3
"""Delete one zero-initialized logical helper while exchanging physical roles.

A coordinate is never discarded. When the unique relation loses its omitted
pivot, one actual XOR computes the old omitted value into the surviving slot
and the logical labels exchange. Literal inverse cleanup restores every dirty
physical input. This is a changed scalar network, not the fixed-role quotient.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,time
from search_networks import ROOT,HERE,OLD,SOURCE,CHECKER,EXPECTED,read,canonical,cleanup,scalar,compact,load_checker,actual_profile,Optimizer


def build(word,removed,choice='helper_first'):
    n=2*word['v']+word['R'];relation=1<<removed;pivot=removed
    physical={r:r for r in range(n) if r!=removed}
    out=deepcopy(word);notes=[];new_ret=None

    def members(mask):return [r for r in range(n) if mask>>r&1]

    def exchange(section,index,new_pivot,frame):
        nonlocal pivot
        assert relation>>new_pivot&1 and new_pivot in physical
        slot=physical.pop(new_pivot)
        support=[physical[r] for r in members(relation^(1<<pivot)^(1<<new_pivot))]
        if support:out[section].append([frame,slot,support])
        physical[pivot]=slot
        notes.append([section,index,'logical_pivot_exchange',pivot,new_pivot,slot,support])
        pivot=new_pivot

    for section in ('A','B'):
        out[section]=[]
        for index,(f,d,ss) in enumerate(word[section]):
            for s in ss:
                if d==pivot:
                    notes.append([section,index,'omitted_destination',d,s])
                elif s==pivot:
                    if relation>>d&1:
                        # Under d<-d+p, new p's coefficient becomes zero.
                        # First place old p in d's physical slot, then omit d.
                        old_pivot=pivot
                        exchange(section,index,d,f)
                        relation^=1<<old_pivot
                        continue
                    support=[physical[r] for r in members(relation^(1<<pivot))]
                    if support:out[section].append([f,physical[d],support])
                    notes.append([section,index,'expanded_source',d,s,support])
                else:out[section].append([f,physical[d],[physical[s]]])
                if relation>>d&1:relation^=1<<s
        if section=='A':
            if pivot in word['ret']:
                choices=[r for r in members(relation^(1<<pivot)) if r not in word['ret']]
                if not choices:raise ValueError('COPY has no surviving relation pivot')
                if choice=='helper_first':choices.sort(key=lambda r:(physical[r]<2*word['v'],r))
                elif choice=='source_first':choices.sort(key=lambda r:(physical[r]>=2*word['v'],r))
                else:choices.sort(reverse=True)
                exchange(section,len(word[section]),choices[0],0)
            new_ret=[physical[r] for r in word['ret']]
            assert len(new_ret)==len(set(new_ret))
    out['ret']=new_ret
    out['D']=[[f,d,[s for s in ss if s!=removed]] for f,d,ss in word['D']]
    out['D']=[g for g in out['D'] if g[2]]
    out['final'][removed]=0;cleanup(out)
    return out,{'removed_helper':removed,'choice':choice,'exchanges_and_expansions':notes,
                'logical_ret':word['ret'],'physical_ret':new_ret,'final_pivot':pivot,
                'final_logical_to_physical':physical}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--choice',choices=('helper_first','source_first','last'),default='helper_first')
    ap.add_argument('--limit',type=int,default=100000)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raw=gzip.decompress(SOURCE.read_bytes());assert sha256(raw).hexdigest()==EXPECTED
    word=json.loads(raw);word['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    module=load_checker(CHECKER);checker=module.Word(word);checker.full()
    optimizer=Optimizer(word,checker,.001745);original_captures=optimizer.captures.copy()
    pins=[SOURCE,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',HERE/'search_networks.py',Path(__file__)]
    sources={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins}
    stats=Counter();candidates=[];obstructions=[];t0=time.monotonic()
    for removed in range(2*word['v'],2*word['v']+word['R']):
        if removed in word['ret'] or removed==469:continue
        if stats['attempted']>=args.limit:break
        stats['attempted']+=1
        try:
            candidate,identity=build(word,removed,args.choice)
            scalar(candidate);stats['arbitrary_columns_pass']+=1
            optimizer.captures={new:original_captures[old] for old,new in zip(word['ret'],candidate['ret'])}
            changed,info=optimizer.optimize(candidate)
        except ValueError as exc:
            reason=exc.args[0];label=str(reason[0]) if isinstance(reason,tuple) else str(reason)
            stats[label]+=1;obstructions.append({'removed':removed,'reason':reason})
            continue
        stats['geometry_feasible']+=1
        native_type=all(r>=2*word['v'] for r in changed['ret'])
        if info['saving']>1e-9:
            changed=compact(changed,removed);payload=canonical(changed)
            native=None
            if native_type:
                independent=module.Word(changed);columns=independent.full()
                hypotheses,conclusion,_=independent.interface()
                assert all(hypotheses.values()) and all(conclusion.values())
                assert dict(actual_profile(changed,independent))==info['local_profile']
                native={'columns':columns,'hypotheses':hypotheses,'conclusion':conclusion}
            row={'removed':removed,'identity':identity,'optimization':info,'native_helper_COPY_types':native_type,
                 'native_check':native,'content_sha256':sha256(payload).hexdigest(),'word':f'R436-{removed}.json.gz'}
            (args.out/row['word']).write_bytes(gzip.compress(payload,mtime=0))
            (args.out/f'R436-{removed}.json').write_text(json.dumps(row,sort_keys=True,indent=2)+'\n')
            candidates.append(row);print('FOUND',removed,'saving',info['saving'],'profile',info['local_profile'],'native_type',native_type,flush=True)
        if stats['attempted']%50==0:print('PROGRESS',dict(stats),'seconds',time.monotonic()-t0,flush=True)
    result={'status':'FINITE_DYNAMIC_LOGICAL_PHYSICAL_QUOTIENT_SEARCH','source_word_content_sha256':EXPECTED,
            'source_sha256':sources,'choice':args.choice,'stats':dict(stats),'candidates':candidates,'obstructions':obstructions,
            'seconds':time.monotonic()-t0,'scope':'One removed zero-input helper; arbitrary surviving dirty columns preserved. Logical pivots exchange via literal reversible gates. Existing758 rational root flats and fixed original capture spaces. A candidate with SOURCE-role COPY requires a separate generalized native typing proof and is not admitted by this search.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(candidates),'seconds',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
