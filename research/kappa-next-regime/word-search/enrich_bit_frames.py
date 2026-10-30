#!/usr/bin/env python3
"""Add exact rational root flats at chronological graph lower/upper bounds.

Frames are closed by exact integer annihilators of their generating root lines.
Adding a catalogue entry charges no work; every actually used frame transition
is still priced and checked in the optimized emitted word. This finite closure
set does not enumerate every rational intermediate subspace. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
from bit_pair_search import read,canonical,load_checker,actual_profile,DEFAULT_SOURCE
from bit_joint_frames import Optimizer


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,default=DEFAULT_SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz')
    ap.add_argument('--checker',type=Path,default=DEFAULT_SOURCE/'vendor/xcheck_p.py')
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    word=read(args.word)
    module=load_checker(args.checker)
    checker=module.Word(word)
    optimizer=Optimizer(word,checker)
    optimizer.graph(word)
    lo,hi=optimizer.last_bounds
    known={tuple(f) for f in word['frames']}
    new=deepcopy(word)
    additions=[]
    for mask in sorted(set(lo+hi)):
        labels=[i for i in range(word['v']) if mask>>i&1]
        annihilator=module.nullspace_int([word['lines'][i] for i in labels])
        closure=tuple(i for i,line in enumerate(word['lines'])
                      if all(sum(a*b for a,b in zip(line,row))==0 for row in annihilator))
        if closure in known:
            continue
        known.add(closure)
        rank=len(module.rref([word['lines'][i] for i in closure])[0])
        additions.append(dict(frame=len(new['frames']),rank=rank,labels=closure,
                              original_required_labels=labels))
        new['frames'].append(list(closure))
    checked=module.Word(new)
    checked.labels()
    checked.full()
    op=Optimizer(new,checked)
    optimized,result=op.optimize(new)
    real=module.Word(optimized)
    real.full()
    interface,conclusion,_=real.interface()
    assert all(interface.values())
    assert dict(actual_profile(optimized,real))==result['local_profile']
    args.out.mkdir(parents=True,exist_ok=True)
    payload=canonical(new)
    (args.out/'CATALOGUE-WORD.json.gz').write_bytes(gzip.compress(payload,mtime=0))
    optimized_payload=canonical(optimized)
    (args.out/'OPTIMIZED-WORD.json.gz').write_bytes(gzip.compress(optimized_payload,mtime=0))
    receipt=dict(status='PASS_EXACT_RATIONAL_GRAPH_BOUND_FRAME_ENRICHMENT',
                 source_word_sha256=sha256(args.word.read_bytes()).hexdigest(),
                 old_frames=len(word['frames']),new_frames=len(new['frames']),
                 additions=additions,added_ranks=dict(Counter(a['rank'] for a in additions)),
                 optimization=result,interface=interface,
                 catalogue_payload_sha256=sha256(payload).hexdigest(),
                 optimized_payload_sha256=sha256(optimized_payload).hexdigest(),
                 scope='FINITE_EXACT_LOCAL_WORD; NATIVE_HOSTED_INVOICE_REMAINS')
    (args.out/'RESULT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='additions'},sort_keys=True),flush=True)


if __name__=='__main__':
    main()
