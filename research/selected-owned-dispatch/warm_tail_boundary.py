"""Diagnostic: virtual-blank codes are active extents, not free warm capacity.

Usage: python warm_tail_boundary.py --package /path/to/selected-owned-dispatch
This imports a prototype but never changes its code, inputs, or receipts.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load(package):
    sys.path.insert(0, str(package))
    spec = importlib.util.spec_from_file_location('warm_tail_prototype', package/'prototype.py')
    p = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = p
    spec.loader.exec_module(p)
    return p


def case(p, depth_count, tail):
    s,q = p.s,p.q
    counts=s.Counts()
    payloads=[s.Tape(counts=counts) for _ in range(16)]
    control=s.Tape(marker=s.BASE,counts=counts)
    descriptor=s.Tape(marker=s.BASE,counts=counts)
    relays=[s.Tape(marker=s.BASE,counts=counts) for _ in range(4)]
    depth=s.Tape(marker=s.BASE,counts=counts)
    # Valid p=9,M=1 descriptors. Added virtual BLANKs after RIGHT do not
    # change the query ABI, but their physical codes remain nonblank.
    words=[p.bits([2,-1],9), p.bits([-2,1],9), [],
           [1,0,0,1,q.RIGHT]+[q.BLANK]*tail,
           [1,q.RIGHT]+[q.BLANK]*tail, [], [], []]
    for tape,word in zip(payloads,words):
        for bit in p.code([q.LEFT]+word):
            s.emit(tape,bit)
        p.query_origin(tape)
    for _ in range(depth_count):
        s.emit(depth,1)
    p.at_start(depth,s.BASE)
    tapes=payloads+[control,descriptor,depth]+relays
    entry=sum(len(t.cells) for t in tapes)
    before=counts.total
    p.Dispatcher(payloads,control,descriptor,relays,depth).run()
    result=payloads[q.Y].cells[1:1+3*(1+18)]
    expected=[-2+2*(depth_count+1), 1-(depth_count+1)]
    s.need(result==p.code([q.LEFT]+p.bits(expected,9)), 'warm-tail result semantics')
    return dict(depth=depth_count, logical_blanks_per_descriptor=tail,
                entry_backing=entry,
                final_backing=sum(len(t.cells) for t in tapes),
                physical_actions=counts.total-before)


def run(package):
    p=load(package)
    rows=[]
    for depth in (1,2,4,16):
        ordinary=case(p,depth,0)
        for tail in (7,1000):
            warmed=case(p,depth,tail)
            # Two descriptors, three physical bits per coded virtual blank.
            # The two staging relays also retain one copy when depth>=1.
            p.s.need(warmed['entry_backing']-ordinary['entry_backing']==6*tail,
                     'entry backing delta')
            p.s.need(warmed['final_backing']-ordinary['final_backing']==6*tail*(depth+2),
                     'depth-multiplied coded-tail backing')
            p.s.need(warmed['physical_actions']-ordinary['physical_actions']==180*tail*depth,
                     'actual paid scans of coded blank tails')
            rows.append(dict(ordinary=ordinary,warmed=warmed))
    return dict(status='PASS_CODED_BLANK_TAIL_BOUNDARY', cases=rows,
                meaning='Exact history and semantics remain valid. A uniform O(K0+(d+1)N) corollary needs bounded encoded entry extents; physical blank backing is different.',
                scope='Finite diagnostic plus a literal descriptor-copy scaling identity, not a production dispatcher admission.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--package',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.package.resolve()),indent=2,sort_keys=True))
