#!/usr/bin/env python3
"""Bounded seeded certificate construction; no exhaustive partition claim."""
import argparse
import json
from pathlib import Path
import random
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from phase_gram import rank,canonical
from query_frame_sources import need


def find(receipt,seed=47,max_restarts=1000):
    directions={r[0]:r[2] for r in receipt['records']}
    ports=sorted(directions);rng=random.Random(seed)
    for trial in range(1,max_restarts+1):
        order=ports[:];rng.shuffle(order);groups=[[] for _ in range(12)]
        for p in order:
            legal=[i for i,g in enumerate(groups) if len(g)<9 and rank([directions[q] for q in g]+[directions[p]])==len(g)+1]
            if not legal:break
            smallest=min(len(groups[i]) for i in legal)
            i=rng.choice([i for i in legal if len(groups[i])==smallest])
            groups[i].append(p)
        else:
            return {'seed':seed,'method':'seeded balanced greedy partition, 12 bins of capacity 9, independent-direction entrance',
                    'stop_rule':'first complete partition or '+str(max_restarts)+' shuffled restarts',
                    'completed_trials':trial,'groups':groups,
                    'group_ranks':[rank(directions[p] for p in g) for g in groups],
                    'ambient_span_rank':rank(directions.values()),'exhaustive':False}
    raise ValueError('no partition in the declared bounded construction; not an impossibility result')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=find(json.loads((HERE/'CERTIFICATE.json').read_text()))
    if args.check:
        need(canonical(result)==canonical(json.loads((HERE/'PARTITION.json').read_text())),'reproduced exact independent partition')
        print('PASS_QQ16_FRAME_PARTITION seed=47 restarts=1 groups=12 optimal_by_span_rank=9')
    else:print(json.dumps(result,indent=2))
