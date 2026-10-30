#!/usr/bin/env python3
"""New multi-donor covectors and whole-helper quotient graphs on current R437.

Only the current three-covector production word is used.  Frozen prior code
supplies exact frame assignment machinery and the independent native checker;
none of the prior pair-search results is re-counted.  New geometry/ownership
admission remains separate from a positive finite local graph.
Apache-2.0; substantial OpenAI assistance under the user's direction.
"""
from collections import Counter,defaultdict
from copy import deepcopy
from hashlib import sha256
from itertools import combinations,permutations
from pathlib import Path
import argparse,gzip,json,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=ROOT/'research/kappa-next-regime/word-search'
SOURCE=OLD/'candidate/WORD.json.gz'
EXPECTED='3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'
CHECKER=ROOT/'research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/vendor/xcheck_p.py'
sys.path.insert(0,str(OLD))
from bit_pair_search import read,canonical,flatten,pair_catalog,clusters,load_checker,actual_profile
from bit_joint_frames import Optimizer


def cleanup(word):
    v=word['v']
    word['C']=[[1,d,list(ss)] for sec in ('A','B') for _,d,ss in word[sec]
               if not v<=d<2*v][::-1]


def scalar(word):
    v=word['v'];n=2*v+word['R'];values=[1<<r for r in range(n)]
    for sec in ('D','A','scatter','B','C'):
        if sec=='scatter':
            captures=[values[r] for r in word['ret']]
            for t,row in enumerate(word['scatter']):
                for k in row:values[v+t]^=captures[k]
        else:
            for f,d,ss in word[sec]:
                if d in ss or len(ss)!=len(set(ss)):raise ValueError('noninvertible emitted gate')
                for s in ss:values[d]^=values[s]
    expected=[(1<<r)^((1<<(r-v)) if v<=r<2*v else 0) for r in range(n)]
    if values!=expected:raise ValueError(('arbitrary-column identity failed',[r for r in range(n) if values[r]!=expected[r]][:12]))


def terminal_bundles(word,section,max_donors,all_orders):
    sections=flatten(word);es=sections[section]
    groups,reads,writes=pair_catalog(es,100000)
    batches=defaultdict(list);v=word['v']
    for (a,b,q,ae,be),pairs in groups.items():
        if v<=a<2*v or (section=='A' and (a in word['ret'] or any(e[2]==a for e in sections['B']))):continue
        for chosen,lo,hi in clusters(pairs,a,b,reads,writes):
            keeps={p['keep'] for p in chosen}
            if any(i>=lo and i not in keeps for i in reads[a]):continue
            batches[a,tuple(sorted(keeps))].append((b,lo,hi,chosen))
    for (a,keeps),rows in sorted(batches.items()):
        for count in range(2,min(max_donors,len(rows))+1):
            for selected in combinations(rows,count):
                donors=tuple(x[0] for x in selected)
                if len(set(donors))!=len(donors):continue
                lo=min(x[1] for x in selected);hi=max(x[2] for x in selected)
                if any(lo<=i<hi for r in (a,)+donors for i in writes[r]):continue
                if any(i>=lo and i not in keeps for i in reads[a]):continue
                drops={p['drop'] for x in selected for p in x[3]}
                if len(drops)!=len(keeps)*len(donors) or drops.intersection(keeps):continue
                orders=permutations(donors) if all_orders else sorted({donors,donors[::-1]})
                for ordered in orders:
                    out=deepcopy(word);out[section]=[]
                    for i,e in enumerate(es):
                        if i==lo:
                            out[section].extend([0,a,[b]] for b in ordered)
                        if i not in drops:out[section].append([e[-1],e[1],[e[2]]])
                    cleanup(out)
                    yield out,{'kind':'terminal_multidonor','section':section,'carrier':a,
                               'donors':list(ordered),'keeps':list(keeps),'drops':sorted(drops),'lo':lo,'hi':hi}


def quotient(word,helper):
    """Maintain helper = XOR(relation) in the surviving register coordinates.

    The removed helper starts at zero, which is correct for the new input
    domain; every surviving dirty coordinate remains symbolic. A read whose
    destination belongs to the relation would lose a coordinate and is
    rejected rather than treated as a reversible operation.
    """
    out=deepcopy(word);relation=0;notes=[]
    for sec in ('A','B'):
        out[sec]=[]
        for index,(f,d,ss) in enumerate(word[sec]):
            for s in ss:
                if d==helper:
                    relation^=1<<s
                    notes.append([sec,index,'elided_write',d,s,relation.bit_count()])
                elif s==helper:
                    if relation>>d&1:raise ValueError(('coordinate_loss',sec,index,d))
                    support=[r for r in range(2*word['v']+word['R']) if relation>>r&1]
                    if support:out[sec].append([f,d,support])
                    notes.append([sec,index,'expanded_read',d,s,support])
                else:
                    out[sec].append([f,d,[s]])
                    if relation>>d&1:relation^=1<<s
    out['D']=[[f,d,[s for s in ss if s!=helper]] for f,d,ss in word['D']]
    out['D']=[g for g in out['D'] if g[2]]
    out['final'][helper]=0
    cleanup(out)
    return out,{'kind':'helper_zero_input_quotient','helper':helper,'edits':notes,
                'final_relation':[r for r in range(2*word['v']+word['R']) if relation>>r&1]}


def compact(word,helper):
    out=deepcopy(word);out['R']-=1
    rename=lambda r:r-int(r>helper)
    for sec in ('D','A','B','C'):
        assert all(d!=helper and helper not in ss for f,d,ss in out[sec])
        out[sec]=[[f,rename(d),[rename(s) for s in ss]] for f,d,ss in out[sec]]
    out['ret']=[rename(r) for r in out['ret']]
    for key in ('start','final'):out[key].pop(helper)
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=('multidonor','quotient'),required=True)
    ap.add_argument('--section',choices=('A','B'),default='B')
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--max-donors',type=int,default=6)
    ap.add_argument('--all-orders',action='store_true')
    ap.add_argument('--limit',type=int,default=1000000)
    ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--endpoint',type=float,default=.001745)
    args=ap.parse_args()
    raw=gzip.decompress(SOURCE.read_bytes());assert sha256(raw).hexdigest()==EXPECTED
    word=json.loads(raw);word['frames']=read(OLD/'enriched-frames/CATALOGUE-WORD.json.gz')['frames']
    checker_module=load_checker(CHECKER);checker=checker_module.Word(word);checker.full()
    optimizer=Optimizer(word,checker,args.endpoint)
    args.out.mkdir(parents=True,exist_ok=True);stats=Counter();candidates=[];rejects=[]
    t0=time.monotonic()
    if args.mode=='multidonor':
        iterator=terminal_bundles(word,args.section,args.max_donors,args.all_orders)
    else:
        def generate():
            for helper in range(2*word['v'],2*word['v']+word['R']):
                if helper in word['ret'] or helper==469:continue
                try:yield quotient(word,helper)
                except ValueError as exc:
                    stats[str(exc.args[0][0])]+=1
                    rejects.append({'helper':helper,'reason':exc.args[0]})
        iterator=generate()
    for index,(candidate,identity) in enumerate(iterator):
        if not args.start<=index<args.start+args.limit:continue
        stats['indexed']+=1
        try:
            scalar(candidate);stats['all_arbitrary_columns_pass']+=1
            changed,info=optimizer.optimize(candidate)
        except ValueError as exc:
            reason=exc.args[0];label=str(reason[0]) if isinstance(reason,tuple) else str(reason)
            stats[label]+=1
            if len(rejects)<1000:rejects.append({'index':index,'identity':identity,'reason':reason})
            continue
        stats['geometry_feasible']+=1
        if info['saving']>1e-9:
            if args.mode=='quotient':changed=compact(changed,identity['helper'])
            independent=checker_module.Word(changed);columns=independent.full()
            hypotheses,conclusion,_=independent.interface()
            assert all(hypotheses.values()) and all(conclusion.values())
            assert dict(actual_profile(changed,independent))==info['local_profile']
            payload=canonical(changed);name=f'{args.mode}-{args.section}-{index}'
            (args.out/(name+'.json.gz')).write_bytes(gzip.compress(payload,mtime=0))
            row={'id':name,'index':index,'identity':identity,'optimization':info,
                 'content_sha256':sha256(payload).hexdigest(),'hypotheses':hypotheses,'conclusion':conclusion,
                 'arbitrary_columns':columns,'word':name+'.json.gz'}
            (args.out/(name+'.json')).write_text(json.dumps(row,sort_keys=True,indent=2)+'\n')
            candidates.append(row);print('FOUND',name,'saving',info['saving'],'delta',info['delta'],flush=True)
        if stats['indexed']%100==0:print('PROGRESS',dict(stats),'elapsed',time.monotonic()-t0,flush=True)
    pins=[SOURCE,CHECKER,OLD/'enriched-frames/CATALOGUE-WORD.json.gz',OLD/'bit_pair_search.py',OLD/'bit_joint_frames.py',Path(__file__)]
    result={'status':'FINITE_CURRENT_WORD_NETWORK_SEARCH','mode':args.mode,'section':args.section,
            'source_word_content_sha256':EXPECTED,'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in pins},
            'stats':dict(stats),'candidates':candidates,'rejections':rejects,'seconds':time.monotonic()-t0,
            'scope':'Constructive local word/profile candidates only. The domain is the retained758 root-closed rational frames. Helper quotient candidates change width/inventory and need a new complete owner invoice. Coordinate-loss cases are rejected; no dynamic logical/physical renaming is claimed. Known public fixed-boundary helper469 deletion is skipped.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(candidates),'elapsed',time.monotonic()-t0,flush=True)


if __name__=='__main__':main()
