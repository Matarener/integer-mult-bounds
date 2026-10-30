#!/usr/bin/env python3
"""Fresh complete first-contact kernel census on the final changed BIT word.

The old negative result is not transferred. We independently rederive the
new raw dirty response and recompute every nonzero rational first-contact
intersection class. Credit mightyOil's r439-kernel-entrance-closure theorem
and engine, and the preceding independent R437 response extractor.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXTRACTOR = REPO/'research/kappa-next-regime/width-search/entrance_closure.py'
WORD = HERE.parent/'bit-word/early-birth-prefixes/WORD.json.gz'
EXPECTED = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'


def main():
    spec = importlib.util.spec_from_file_location('independent_response_extractor',EXTRACTOR)
    extractor = importlib.util.module_from_spec(spec); spec.loader.exec_module(extractor)
    engine = extractor.load_engine()
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    assert sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest() == EXPECTED
    columns,first,frames = extractor.extract(word,engine)
    assert all(columns), 'no individual zero-response helper exists'
    first_dims = Counter(len(frames[first[h]]) for h in first)
    assert first_dims == {1:282,2:155}
    # The credited intersection-closure theorem is complete for lines and
    # planes. Its explicit dimension gate prevents a higher-flat overclaim.
    spaces = set(frames.values())
    closure,pairs = engine.geometry_closure(spaces)
    normals = {space:engine.orthogonal(space) for space in spaces}
    classes = []
    for space in closure:
        allowed = [h for h in sorted(first)
                   if all(sum(x*y for x,y in zip(row,n)) == 0
                          for row in space for n in normals[frames[first[h]]])]
        rank,basis = engine.kernel(columns,allowed)
        nullity = len(allowed)-rank
        assert nullity == len(basis) == extractor.independent_nullity([columns[h-222] for h in allowed])
        for direction in basis:
            response = 0
            for h in direction:
                assert h in allowed; response ^= columns[h-222]
            assert response == 0
        classes.append({'rational_frame':[[str(x) for x in row] for row in space],
                        'eligible_helpers':allowed,'response_rank':rank,'nullity':nullity,'kernel_basis':basis})
    assert not any(row['nullity'] for row in classes)
    inputs = [Path(__file__),EXTRACTOR,extractor.ENGINE,WORD,HERE/'BIT-FINAL-INDEPENDENT-REVIEW.json']
    result = {'status':'FINAL_CHANGED_WORD_ALL_SUPPORT_FIRST_CONTACT_KERNELS_ZERO',
              'word_canonical_sha256':EXPECTED,'complete_arbitrary_input_columns':659,
              'helper_count':437,'zero_D_columns':[],
              'first_frame_ids':len(frames),'first_rational_spaces':len(spaces),
              'first_dimensions':dict(first_dims),'closure_dimensions':dict(Counter(map(len,closure))),
              'intersecting_distinct_plane_pairs':pairs,'class_count':len(classes),
              'nullity_histogram':dict(Counter(row['nullity'] for row in classes)),
              'classes':classes,'controls':engine.controls(),
              'scope':'All binary helper-response kernel supports sharing a nonzero rational first-contact subspace of the final fixed A/scatter/B/C word. This is a freshly recomputed necessary-condition obstruction, including nonroot lines and arbitrary support sizes. Later basis changes, changed scalar words, SOURCE donors, changed target interfaces and different controller/flag laws remain outside.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in inputs}}
    (HERE/'FINAL-ENTRANCE-CLOSURE.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'classes',len(classes),'nullity',result['nullity_histogram'],flush=True)


if __name__ == '__main__':
    main()
