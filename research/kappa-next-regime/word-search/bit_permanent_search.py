#!/usr/bin/env python3
"""Share a last-use bit covector and absorb its undo in literal FULL cleanup.

The carrier is not a target, not an A COPY source, and has no later A/B read
except the exact replaced shared consumers.  Its arbitrary dirty value is
restored by the regenerated C word.  This changes the cleanup graph rather
than omitting restoration.  All local semantics are rechecked on positives.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,time
from bit_pair_search import read,canonical,load_checker,flatten,pair_catalog,clusters,actual_profile,DEFAULT_SOURCE
from bit_joint_frames import Optimizer


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--checker',type=Path,default=DEFAULT_SOURCE/'vendor/xcheck_p.py')
    ap.add_argument('--section',choices=('A','B'),required=True)
    args=ap.parse_args()
    w=read(args.word);module=load_checker(args.checker);checker=module.Word(w)
    checker.full();assert all(checker.interface()[0].values())
    sections=flatten(w);es=sections[args.section]
    optimizer=Optimizer(w,checker)
    groups,reads,writes=pair_catalog(es,100000)
    indexed=[]
    for (a,b,q,ae,be),pairs in groups.items():
        if w['v']<=a<2*w['v']:continue
        if args.section=='A' and a in w['ret']:continue
        for chosen,lo,hi in clusters(pairs,a,b,reads,writes):
            keeps={p['keep'] for p in chosen}
            if any(i>=lo and i not in keeps for i in reads[a]):continue
            if args.section=='A' and any(e[2]==a for e in sections['B']):continue
            indexed.append((a,b,chosen,lo,hi))
    args.out.mkdir(parents=True,exist_ok=True)
    t0=time.monotonic();stats=Counter();found=[]
    print('INDEXED',len(indexed),flush=True)
    for index,(a,b,chosen,lo,hi) in enumerate(indexed):
        drops={p['drop'] for p in chosen};nw=deepcopy(w);nw[args.section]=[]
        for i in range(len(es)+1):
            if i==lo:nw[args.section].append([0,a,[b]])
            if i<len(es) and i not in drops:
                e=es[i];nw[args.section].append([e[-1],e[1],[e[2]]])
        nw['C']=[[1,d,list(ss)] for sec in ('A','B') for _,d,ss in nw[sec] if not w['v']<=d<2*w['v']][::-1]
        stats['attempted']+=1
        try:nw,result=optimizer.optimize(nw)
        except ValueError as exc:
            label=exc.args[0][0] if isinstance(exc.args[0],tuple) else str(exc)
            stats[label]+=1;continue
        stats['feasible']+=1
        if result['saving']>1e-10:
            independent=module.Word(nw);columns=independent.full()
            interface,conclusion,_=independent.interface();assert all(interface.values())
            assert dict(actual_profile(nw,independent))==result['local_profile']
            ident=f'{args.section}-permanent-{index}';payload=canonical(nw)
            path=args.out/(ident+'.json.gz');path.write_bytes(gzip.compress(payload,mtime=0))
            info=dict(id=ident,index=index,a=a,b=b,chosen=chosen,lo=lo,hi=hi,
                      optimization=result,word=path.name,canonical_sha256=sha256(payload).hexdigest(),
                      interface=interface,arbitrary_columns=columns)
            found.append(info);(args.out/(ident+'.json')).write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
            print('FOUND',json.dumps(info,sort_keys=True),flush=True)
        if stats['attempted']%25==0:print('PROGRESS',index,dict(stats),'seconds',time.monotonic()-t0,flush=True)
    receipt=dict(status='BOUNDED_BIT_PERMANENT_LAST_USE_COVECTOR_SEARCH',section=args.section,
                 source_sha256=sha256(args.word.read_bytes()).hexdigest(),stats=dict(stats),
                 total_indexed=len(indexed),candidates=found,
                 scope='EXACT_LOCAL_CANDIDATES_REQUIRE_NATIVE_AND_HOSTED_INVOICE')
    (args.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(found),flush=True)


if __name__=='__main__':main()
