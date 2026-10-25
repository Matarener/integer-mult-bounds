#!/usr/bin/env python3
"""Persistent basis changes at direct A edges touching a warm helper.

This includes pairs with no common producer: the old inter-helper operation
can cancel against the inserted shear, while all later observations change
by conjugation. Warm dirty inputs remain protected in the full replay.
"""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from time import monotonic
import gzip,json
from network_search import ROOT,HERE,FROZEN,F,O,OLD,trace,canonical,repair
from permanent_shear import check_conjugation
from timed_shear import construct


def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--word',type=Path)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True);translator_checks=check_conjugation()
    source=args.word or OLD/'candidate/BORROW-WORD-43base.json.gz';word=F.read(source);sec=F.expand(word)
    allowed=set(range(224,704))-set(word['removed'])-set(map(int,word['helper_final']))-set(word['centers'])
    allowed-={e[1] for name in ('A','B','restore') for e in sec[name] if e[0]=='warp'}
    warm=set(map(int,word['start_extra']));pairs=defaultdict(list)
    for i,e in enumerate(word['A']):
        if i>=word['prelude_events'] and e[0]=='add' and e[1] in allowed and e[2] in allowed and ({e[1],e[2]}&warm):
            pairs[tuple(sorted(e[1:3]))].append(i)
    base=Counter({int(r):c for r,c in word['report']['local_profile'].items()});census=Counter(pairs=len(pairs))
    found=[];cases=[];hist=Counter();started=monotonic()
    for pair_index,((a,b),positions) in enumerate(sorted(pairs.items())):
        cuts=sorted({i for j in positions for i in (j,j+1)})
        values={Q(-2),Q(-1),Q(-1,2),Q(1,2),Q(1),Q(2)}
        for p,q in ((a,b),(b,a)):
            for cut in cuts:
                for t in sorted(values):
                    census['constructed']+=1;candidate=construct(word,p,q,t,cut)
                    try:O.graph(candidate)
                    except (ValueError,AssertionError) as exc:census['global_frame_infeasible']+=1;hist[str(exc)[:120]]+=1;continue
                    census['global_frame_feasible']+=1
                    try:candidate,opt=O.optimize(candidate)
                    except (ValueError,AssertionError) as exc:census['optimizer_capacity_or_reject']+=1;continue
                    census['joint_optimized']+=1;profile,_=trace(candidate);delta=profile.copy();delta.subtract(base)
                    saving=-sum(c*F.phi(r) for r,c in delta.items())
                    if saving<=1e-10:continue
                    info={'p':p,'q':q,'t':str(t),'insertion_before_A':cut,'direct_A_edges':positions,
                          'local_profile':dict(profile),'delta':{r:c for r,c in delta.items() if c},'saving':saving,'optimization':opt,
                          'warm_helpers':sorted({p,q}&warm)}
                    try:info['repair']=repair(candidate)
                    except (ValueError,AssertionError) as exc:census['full_dirty_rejected']+=1;info['rejected']=str(exc)
                    else:
                        payload=canonical(candidate);name=f'WORD-{p}-{q}-cut{cut}-t{t.numerator}over{t.denominator}.json.gz';(args.output/name).write_bytes(gzip.compress(payload,mtime=0))
                        info.update(word=name,word_content_sha256=sha256(payload).hexdigest(),native_admission=False)
                        found.append(info);census['positive_exact']+=1;print('POSITIVE',json.dumps(info,sort_keys=True),flush=True)
                    cases.append(info)
        if pair_index%5==0:print('PROGRESS',pair_index,dict(census),monotonic()-started,flush=True)
    paths=[Path(__file__),HERE/'timed_shear.py',HERE/'permanent_shear.py',HERE/'network_search.py',source,FROZEN/'exact_rows.py',OLD/'opt_frames.py',OLD/'fanout_search.py']
    result={'status':'WARM_DIRECT_A_EDGE_PERSISTENT_BASIS_SEARCH','census':dict(census),'positives':found,'cases':cases,'seconds':monotonic()-started,
            'infeasibility_histogram':dict(hist),'exact_translator_basis_checks':translator_checks,
            'source_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
            'scope':'All direct A helper pairs touching a warm full-exit helper and no warp/COPY. A permanent shear in either orientation is inserted immediately before or after their old mutual edge; t∈{±1/2,±1,±2}. Every later scalar gate is conjugated, all frames are solved jointly, and every dirty input is retained. This does not exhaust general multihelper networks or all cuts.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('DONE',dict(census),flush=True)


if __name__=='__main__':main()
