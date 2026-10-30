#!/usr/bin/env python3
"""Search changed R437 covector graphs with joint rational-frame assignment.

Fixed source/target/COPY/end interfaces and the existing frame catalogue are
retained.  F2 semantics and rational transport are checked on every candidate.
This is a finite discovery search, not a native or hosted supplier admission.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import time
from bit_pair_search import (read, canonical, load_checker, flatten, transpose,
                             pair_catalog, clusters, build, actual_profile,
                             DEFAULT_SOURCE, FROZEN)
from bit_joint_frames import Optimizer


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word', type=Path, default=DEFAULT_SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz')
    ap.add_argument('--checker', type=Path, default=DEFAULT_SOURCE/'vendor/xcheck_p.py')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--section', choices=('A','B'), required=True)
    ap.add_argument('--transpose', action='store_true')
    ap.add_argument('--max-gap', type=int, default=100000)
    ap.add_argument('--start', type=int, default=0)
    ap.add_argument('--limit', type=int, default=1000000)
    ap.add_argument('--max-bucket', type=int, default=100000)
    args = ap.parse_args()
    word = read(args.word)
    checker_module = load_checker(args.checker)
    checker = checker_module.Word(word)
    checker.full()
    assert all(checker.interface()[0].values())
    optimizer = Optimizer(word, checker)
    _, baseline = optimizer.optimize(word, args.max_bucket)
    assert not baseline['delta'], baseline
    sections = flatten(word)
    ces = transpose(sections[args.section]) if args.transpose else sections[args.section]
    groups, reads, writes = pair_catalog(ces, args.max_gap)
    indexed = [(ar,br,chosen,lo,hi)
               for (ar,br,q,ae,be),pairs in groups.items()
               for chosen,lo,hi in clusters(pairs,ar,br,reads,writes)]
    args.out.mkdir(parents=True, exist_ok=True)
    stats, found = Counter(), []
    t0 = time.monotonic()
    print('INDEXED',len(indexed),'BASELINE',json.dumps(baseline,sort_keys=True),flush=True)
    for index,(ar,br,chosen,clo,chi) in enumerate(indexed):
        if not args.start <= index < args.start+args.limit:
            continue
        stats['attempted'] += 1
        if args.transpose:
            lo,hi = len(ces)-chi,len(ces)-clo
            drops = {len(ces)-1-p['drop'] for p in chosen}
            dst,src = br,ar
        else:
            lo,hi = clo,chi
            drops = {p['drop'] for p in chosen}
            dst,src = ar,br
        if not word['v'] <= dst < 2*word['v'] and word['v'] <= src < 2*word['v']:
            stats['target_to_nontarget_rejected'] += 1
            continue
        candidate = build(word,sections,args.section,drops,lo,hi,dst,src,0,0)
        try:
            candidate, result = optimizer.optimize(candidate,args.max_bucket)
        except ValueError as exc:
            label=exc.args[0][0] if isinstance(exc.args[0],tuple) else str(exc)
            stats[label] += 1
            continue
        stats['feasible'] += 1
        if result['saving'] > 1e-10:
            actual = checker_module.Word(candidate)
            native_columns = actual.full()
            interface, conclusion, _ = actual.interface()
            assert all(interface.values())
            actual_paid = actual_profile(candidate,actual)
            assert dict(actual_paid) == result['local_profile']
            assert sum(r*n for r,n in result['delta'].items()) == 0
            ident=f"{args.section}-{'receiver' if args.transpose else 'source'}-{index}"
            payload=canonical(candidate)
            path=args.out/(ident+'.json.gz')
            path.write_bytes(gzip.compress(payload,mtime=0))
            rec=dict(id=ident,index=index,section=args.section,transpose=args.transpose,
                     ar=ar,br=br,dst=dst,src=src,lo=lo,hi=hi,drops=sorted(drops),
                     chosen=chosen,optimization=result,word=path.name,
                     canonical_sha256=sha256(payload).hexdigest(),
                     arbitrary_columns=native_columns,interface=interface,
                     scope='EXACT_LOCAL_CANDIDATE_REQUIRES_NATIVE_AND_FULL_HOSTED_INVOICE')
            found.append(rec)
            (args.out/(ident+'.json')).write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n')
            print('FOUND',json.dumps(rec,sort_keys=True),flush=True)
        if stats['attempted'] % 50 == 0:
            print('PROGRESS',index,dict(stats),'seconds',round(time.monotonic()-t0,2),flush=True)
    sources = {str(p):sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),
               Path(__file__).with_name('bit_joint_frames.py'),
               Path(__file__).with_name('bit_pair_search.py'),
               FROZEN/'fanout_search.py',args.word,args.checker]}
    receipt=dict(status='BOUNDED_BIT_CHANGED_GRAPH_JOINT_EXISTING_FRAME_SEARCH',
                 section=args.section,transpose=args.transpose,max_gap=args.max_gap,
                 start=args.start,limit=args.limit,max_bucket=args.max_bucket,
                 total_indexed=len(indexed),stats=dict(stats),candidates=found,
                 cache_stats=dict(optimizer.stats),baseline=baseline,sources=sources,
                 elapsed_seconds=time.monotonic()-t0)
    (args.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('DONE',dict(stats),'positive',len(found),'cache',dict(optimizer.stats),flush=True)


if __name__=='__main__':
    main()
