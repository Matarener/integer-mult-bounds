#!/usr/bin/env python3
"""Independent rational-space entrance ceiling for each GL prefix circuit.

This backwards propagation uses exact annihilators, including rational
directions not spanned by the111 root labels.  It does not use the finite-frame
optimizer or its catalogue.  A zero ceiling excludes every nonzero entrance
for that particular scalar graph and its fixed COPY/end interfaces.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse,json
from bit_pair_search import read,load_checker,DEFAULT_SOURCE
from bit_prefix_gl import change


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--word',type=Path,required=True)
    ap.add_argument('--cases',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();w=read(args.word);module=load_checker(DEFAULT_SOURCE/'vendor/xcheck_p.py');checker=module.Word(w)
    frame_perp=[tuple(tuple(x for x in row) for row in module.rref(rows)[0]) for rows in checker.fperp]
    @lru_cache(None)
    def join(a,b):
        if a==b:return a
        return tuple(tuple(x for x in row) for row in module.rref(list(a+b))[0])
    cur=list(w['start'])
    for sec in ('D','A'):
        for f,d,ss in w[sec]:
            for r in [d]+ss:cur[r]=f
    copies={r:frame_perp[cur[r]] for r in w['ret']}
    result=[]
    for case in read(args.cases)['cases']:
        p,q,cut=case['p'],case['q'],case['cut'];nw=change(w,p,q,cut)
        upper=[frame_perp[f] for f in nw['final']]
        for name in ('B','A'):
            for f,d,ss in reversed(nw[name]):
                shared=upper[d]
                for s in ss:shared=join(shared,upper[s])
                upper[d]=shared
                for s in ss:upper[s]=shared
            if name=='B':
                for r,perp in copies.items():upper[r]=join(upper[r],perp)
        rank=len(upper[p]);dim=w['h']-rank
        out=dict(p=p,q=q,cut=cut,exact_maximum_entrance_dimension=dim,
                 annihilator_rank=rank,
                 annihilator=[[str(x) for x in row] for row in upper[p]])
        result.append(out)
    receipt=dict(status='PASS_EXACT_RATIONAL_FIXED_GRAPH_ENTRANCE_CEILINGS',
                 source_word_sha256=sha256(args.word.read_bytes()).hexdigest(),
                 cases_sha256=sha256(args.cases.read_bytes()).hexdigest(),
                 count=len(result),dimension_histogram=dict(Counter(c['exact_maximum_entrance_dimension'] for c in result)),
                 cases=result,scope='Named prefix-conjugation graphs with existing COPY/final interfaces; arbitrary rational entrance subspaces included')
    args.out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='cases'},sort_keys=True),flush=True)


if __name__=='__main__':main()
