#!/usr/bin/env python3
"""Recompute the exact entrance closure on the final changed covector word.

The old fixed-graph exclusion is not assumed to survive a word rewrite. This
reruns all rational intersection classes and both binary nullity engines.
The theorem and Q engine retain mightyOil's r439-kernel-entrance-closure credit.
Apache-2.0; substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json

from entrance_closure import load_engine,extract,independent_nullity,require,ENGINE,SOURCE

HERE = Path(__file__).resolve().parent
WORD = HERE.parent/'word-search/candidate/WORD.json.gz'
PIN = '3f7de7e1d8a6ff9da8ab7650209b559062da4cc053de2b2566b306eb4fbeffd0'


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,default=HERE/'COMPOSED-ENTRANCE-CLOSURE.json')
    args = ap.parse_args()
    raw = WORD.read_bytes(); word = json.loads(gzip.decompress(raw))
    canonical = json.dumps(word,sort_keys=True,separators=(',',':')).encode()
    require(sha256(canonical).hexdigest() == PIN, 'exact final covector word')
    engine = load_engine()
    response,first,frames = extract(word,engine)
    source_path = SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz'
    source = json.loads(gzip.decompress(source_path.read_bytes()))
    old_response,old_first,old_frames = extract(source,engine)
    require(response == old_response, 'independently recomputed full response K remains identical')
    changed_contacts = {r:{'before':old_first[r],'after':first[r]}
                        for r in first if first[r] != old_first[r]}
    require(changed_contacts == {469:{'before':94,'after':184}}, 'sole changed first-contact frame')
    spaces = set(frames.values())
    closure,pairs = engine.geometry_closure(spaces)
    normals = {space:engine.orthogonal(space) for space in spaces}
    classes = []
    for space in closure:
        eligible = [h for h in sorted(first)
                    if all(sum(x*y for x,y in zip(row,normal)) == 0
                           for row in space for normal in normals[frames[first[h]]])]
        rank,kernel = engine.kernel(response,eligible)
        nullity = len(eligible)-rank
        require(nullity == len(kernel) == independent_nullity([response[h-222] for h in eligible]),
                'independent row and column exact binary nullities agree')
        for support in kernel:
            value = 0
            for h in support:
                require(h in eligible,'reported support geometrically eligible')
                value ^= response[h-222]
            require(value == 0,'literal reported compensation-kernel direction')
        classes.append({'frame':[[str(x) for x in row] for row in space],
                        'eligible_helpers':eligible,'response_rank':rank,'nullity':nullity,'kernel_basis':kernel})
    result = {'status':'PASS_FINAL_COVECTOR_WORD_ALL_SUPPORT_FIRST_CONTACT_CLASSIFICATION',
              'word_archive_sha256':sha256(raw).hexdigest(),'word_canonical_sha256':PIN,
              'source_word_sha256':sha256(source_path.read_bytes()).hexdigest(),
              'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
              'support_script_sha256':sha256((HERE/'entrance_closure.py').read_bytes()).hexdigest(),
              'engine_sha256':sha256(ENGINE.read_bytes()).hexdigest(),
              'arbitrary_dirty_columns':659,'helpers':437,
              'changed_first_contacts':changed_contacts,'K_unchanged':True,
              'first_distinct_rowspaces':len(spaces),
              'first_dimensions':dict(Counter(len(frames[first[h]]) for h in first)),
              'closure_dimensions':dict(Counter(map(len,closure))),
              'intersecting_distinct_plane_pairs':pairs,
              'classes':classes,'nullity_histogram':dict(Counter(row['nullity'] for row in classes)),
              'viable_classes':[row for row in classes if row['nullity']],
              'controls':engine.controls(),
              'scope':'All binary helper-response kernel supports and all nonzero rational common first-contact entrances for the exact final three-covector word. This is a fresh rerun after changing A and the first frame of helper469; no transfer of the old graph obstruction is presumed. SOURCE donors, later cuts, further word changes, shifted captures and other controllers remain outside the classification.'}
    with args.out.open('x') as handle:
        json.dump(result,handle,sort_keys=True,indent=2); handle.write('\n')
    print(result['status'],'classes',len(classes),'nullity',result['nullity_histogram'],flush=True)


if __name__ == '__main__':
    main()
