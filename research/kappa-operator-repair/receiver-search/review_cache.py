#!/usr/bin/env python3
"""Compare cached canonical frame elimination with the unmodified solver.

This is a subsequent independent control of the new search optimization.
The original search's inline comment overstated its own baseline check:
that run checked the baseline price, not an uncached execution. This script
performs the omitted comparison on the baseline and six completed cases.
No negative census or supplier claim follows from this bounded control.
Apache-2.0. Substantial OpenAI assistance.
"""
import hashlib
import json
from pathlib import Path
import search as S

HERE = Path(__file__).resolve().parent
O,F,J = S.O,S.F,S.J

def main():
    receipt = json.loads((HERE/'transpose-A/RESULT.json').read_text())
    need = lambda ok: None if ok else (_ for _ in ()).throw(ValueError('Cached/uncached mismatch'))
    word = F.read(S.OLD/'candidate/BORROW-WORD-43base.json.gz')
    sec=F.expand(word)
    events=J.transposed(sec['A'])
    groups,reads,writes=F.pair_catalog(events,2000)
    indexed=[]
    for (a,b,q,ae,be),pairs in groups.items():
        for chosen,lo,hi in F.clusters(pairs,a,b,reads,writes):
            if len(events)-hi < word['prelude_events']:
                continue
            indexed.append((a,b,q,chosen,lo,hi))
    original=O.solve_component
    stats=S.install_cache()
    cached=O.solve_component
    indices=[None,0,199,499,899,1299,receipt['completed_indices'][-1]]
    records=[]
    for index in indices:
        candidate=word
        if index is not None:
            need(index in receipt['completed_indices'])
            a,b,q,chosen,lo,hi=indexed[index]
            candidate,_,_=J.transpose_mutation(word,'A',events,chosen,lo,hi,a,b,q)
        O.solve_component=original
        plain,plain_result=O.optimize(candidate)
        O.solve_component=cached
        fast,fast_result=O.optimize(candidate)
        need(plain==fast and plain_result==fast_result)
        records.append(dict(index=index,complete_word_and_solver_receipt_equal=True,
                            canonical_word_sha256=hashlib.sha256(json.dumps(plain,sort_keys=True,separators=(',',':')).encode()).hexdigest()))
    out=dict(status='PASS_SEVEN_CACHED_VS_UNCACHED_COMPLETE_FRAME_OPTIMIZATIONS',checks=records,cache_stats=dict(stats),
             search_result_sha256=hashlib.sha256((HERE/'transpose-A/RESULT.json').read_bytes()).hexdigest(),
             scope='Baseline and six actually completed search cases; exact word and full solver receipt equality. Corrects the search source comment: the original run did not itself perform uncached controls.',
             source_pins={str(p.relative_to(S.REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__),Path(S.__file__),S.OLD/'opt_frames.py',S.OLD/'fanout_search.py',S.OLD/'joint_fanout_search.py']})
    (HERE/'CACHE-REVIEW.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])

if __name__=='__main__':
    main()
