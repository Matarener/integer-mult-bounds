#!/usr/bin/env python3
"""Recheck the bounded direct-center return family after permanent A rewrites.

No old-word obstruction is transferred to the changed donor rows. The exact
GF2 span and separating covector routines retain their width-search source.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json

from center_return_search import span_solve,separation_witness,profile,whole
from entrance_closure import load_engine,require,ENGINE

HERE = Path(__file__).resolve().parent
WORD = HERE.parent/'word-search/candidate/WORD.json.gz'
PIN = '3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE/'composed-center-return')
    args = ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    raw = WORD.read_bytes(); word = json.loads(gzip.decompress(raw))
    canonical = json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    require(sha256(canonical).hexdigest() == PIN,'actual final composed word')
    engine = load_engine()
    dims = [len(engine.rref([word['lines'][j] for j in frame])) for frame in word['frames']]
    masks = [sum(1 << j for j in frame) for frame in word['frames']]
    centers = word['ret']; n = 659
    require(not any(set(ss)&set(centers) for _,_,ss in word['A']+word['B']), 'centers have no scalar A/B reads')
    current = word['start'][:]; rows = [1 << r for r in range(n)]
    for frame,target,sources in word['A']:
        for role in [target]+sources:
            current[role] = frame
        for source in sources:
            rows[target] ^= rows[source]
    center_frames = {h:current[h] for h in centers}
    require(all(dims[f] == 7 for f in center_frames.values()),'same prescribed COPY rank-seven frames')
    before_profile = profile(word,dims,masks)
    require(before_profile == {1:1322,2:1342,3:74,4:46,5:103,6:10,7:18},'full final-word baseline invoice')
    future = word['final'][:]; all_next = [future.copy()]
    for frame,target,sources in reversed(word['B']):
        for role in [target]+sources:
            future[role] = frame
        all_next.append(future.copy())
    all_next.reverse()
    cases,found = [],[]
    for cut in range(len(word['B'])+1):
        next_frames = all_next[cut]
        for center,frame in center_frames.items():
            desired = rows[center]^(1 << center)
            eligible = [r for r in range(n) if not 111 <= r < 222 and r != center
                        and masks[current[r]] & ~masks[frame] == 0
                        and masks[frame] & ~masks[next_frames[r]] == 0]
            columns = [(r,rows[r]) for r in eligible]
            support,rank,residual = span_solve(columns,desired)
            record = {'center':center,'cut':cut,'frame':frame,'eligible':eligible,
                      'eligible_rank':rank,'solved':support is not None}
            if support is None:
                record['separating_covector_hex'] = hex(separation_witness(columns,desired,residual))
            else:
                donors = [r for r in eligible if support >> r & 1]
                candidate = deepcopy(word)
                candidate['B'].insert(cut,[frame,center,donors])
                candidate['C'] = [g for g in candidate['C'] if g[1] != center]
                require(not any(center in ss for _,_,ss in candidate['C']),'lowered center has no cleanup reads')
                candidate['final'][center] = frame
                expected = [(1 << r)^((1 << (r-111)) if 111 <= r < 222 else 0) for r in range(n)]
                require(whole(candidate) == expected,'literal early-return full arbitrary dirty interface')
                price = profile(candidate,dims,masks)
                payload = json.dumps(candidate,sort_keys=True,separators=(',',':')).encode()
                name = f'CENTER-{center}-CUT-{cut}.json.gz'
                (args.out/name).write_bytes(gzip.compress(payload,mtime=0))
                record.update(donors=donors,word=name,canonical_sha256=sha256(payload).hexdigest(),profile=price,
                              scope='LOCAL_EARLY_RETURN_CANDIDATE_REQUIRES_EXACT_NATIVE_GAUGE_AND_COMPLETE_WIDTH_INVOICE')
                found.append(record)
            cases.append(record)
        if cut < len(word['B']):
            frame,target,sources = word['B'][cut]
            for role in [target]+sources:
                current[role] = frame
            for source in sources:
                rows[target] ^= rows[source]
    result = {'status':'PASS_FINAL_COVECTOR_WORD_DIRECT_CENTER_RETURN_SPAN_SCREEN',
              'source_word_sha256':sha256(raw).hexdigest(),'source_word_canonical_sha256':PIN,
              'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
              'span_engine_sha256':sha256((HERE/'center_return_search.py').read_bytes()).hexdigest(),
              'frame_engine_sha256':sha256(ENGINE.read_bytes()).hexdigest(),
              'cases':len(cases),'centers':centers,'cuts_per_center':len(word['B'])+1,
              'before_profile':before_profile,'candidates':found,'cases_checked':cases,
              'scope':'One exact common-frame linear reset of one copied center at each prescribed B cut of the FINAL composed word, at the unchanged rank-seven capture frame, using all compatible existing non-target donor rows. Every failed span has an explicitly checked binary separating covector. Multistage relays, shifted COPYs, changed later scalar graphs and coordinated centers remain outside this test.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'cases',len(cases),'candidates',len(found),flush=True)


if __name__ == '__main__':
    main()
