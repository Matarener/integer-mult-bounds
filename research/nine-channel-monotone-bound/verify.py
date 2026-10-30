"""Exact certificate for the at-most-nine canonical-channel lower bound.

Prepared for Nicholas with substantial OpenAI Codex assistance, 2026-10-27.
Apache-2.0. Predecessor code and attribution are retained in source/.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import io
import json
import sys
import tarfile
import types

import independent as direct

ROOT = Path(__file__).resolve().parent


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def load_sources():
    manifest = json.loads((ROOT / 'SOURCES.json').read_text())
    for entry in manifest['source_files']:
        raw = (ROOT / entry['path']).read_bytes()
        require(sha256(raw).hexdigest() == entry['sha256'], 'Pinned source: ' + entry['path'])
    raw = (ROOT / 'source/original-packet.tar.gz').read_bytes()
    require(sha256(raw).hexdigest() == '595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7', 'Original archive')
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        word_bytes = archive.extractfile(manifest['archive_word_member']).read()
        r_bytes = archive.extractfile(manifest['archive_modes_member']).read()
    require(sha256(word_bytes).hexdigest() == '934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775', 'Original word')
    word = json.loads(gzip.decompress(word_bytes))
    modes = [[Q(x) for x in row] for row in json.loads(r_bytes)]
    require(len(modes) == 8 and all(len(r) == 112 for r in modes), 'Mode shape')
    require(all(sum(x*y for x,y in zip(a,b)) == (56 if i==j else 0)
                for i,a in enumerate(modes) for j,b in enumerate(modes)), 'RR^T = 56 I')
    events = word['programs']['backward']
    tail = []
    for j, row in enumerate(modes):
        for i,a in enumerate(row):
            if a:
                tail.append(['physical_add', ['L',i], ['C',j+1], -a.numerator, a.denominator, 1, 0, []])
        tail.append(['scalar', ['clear', ['C',j+1]], 0])
    require(events[-len(tail):] == tail, 'Exact relaxed tail')
    require(all(e[0] != 'physical_add' for e in events[:-len(tail)]), 'No earlier relaxed operation')
    require(len(events) == 22585, 'Source event count')
    return word, modes


def predecessor_scan(word, modes):
    """Expose existing local bases without changing any arithmetic or traversal."""
    old_inputs = sys.modules.get('inputs')
    inputs = types.ModuleType('inputs')
    exec(compile((ROOT/'source/inputs.py').read_text(), str(ROOT/'source/inputs.py'), 'exec'),
         dict_for_module(inputs, ROOT/'source/inputs.py'))
    sys.modules['inputs'] = inputs
    try:
        code = (ROOT/'source/cuts.py').read_text()
        marker = 'return dict(contexts=tested,'
        require(code.count(marker) == 1, 'Single instrumentation site')
        code = code.replace(marker, 'return dict(temporal_bases=temporal, contexts=tested,')
        module = types.ModuleType('predecessor_cuts')
        exec(compile(code, str(ROOT/'source/cuts.py'), 'exec'), dict_for_module(module, ROOT/'source/cuts.py'))
        result = module.scan(word, modes)
    finally:
        if old_inputs is None:
            sys.modules.pop('inputs', None)
        else:
            sys.modules['inputs'] = old_inputs
    expected = json.loads((ROOT/'source/RESULT.json').read_text())['scan']
    actual = {k:result[k] for k in expected}
    require(json.loads(json.dumps(actual)) == expected, 'Complete predecessor census')
    return module, result


def dict_for_module(module, path):
    module.__file__ = str(path)
    return module.__dict__


def primary_pairs(module, scan, word):
    all_bases = scan['temporal_bases']
    frames = [f for f in all_bases if len(word['canonical']['frames'][f]) < 8]
    require(all(not all_bases[f][1] for f in frames), 'Every low frame has zero clean subspace')
    by_pivot = defaultdict(list)
    for f in frames:
        for p in all_bases[f][0]:
            by_pivot[p].append(f)
    candidates = set()
    for group in by_pivot.values():
        for i,f in enumerate(group):
            for g in group[:i]:
                candidates.add(tuple(sorted((f,g))))
    intersections = 0
    for f,g in sorted(candidates):
        b = {p:(dict(row),list(mode),{}) for p,(row,mode,_) in all_bases[f][0].items()}
        clean = {}
        for row,mode,_ in all_bases[g][0].values():
            module.extend(row, mode, {}, b, clean)
        require(not clean, 'Two-frame clean response: ' + str((f,g)))
        if len(b) < len(all_bases[f][0]) + len(all_bases[g][0]):
            intersections += 1
    total = len(frames)*(len(frames)-1)//2
    return {
        'frames':len(frames), 'frames_by_rank':dict(sorted(Counter(len(word['canonical']['frames'][f]) for f in frames).items())),
        'distinct_pairs':total, 'same_frame_cases':len(frames),
        'explicit_eliminations':len(candidates), 'disjoint_pivot_pairs':total-len(candidates),
        'nontrivial_nuisance_intersections':intersections, 'clean_pairs':0,
    }


def compare_raw_spaces(scan, other, modes, word):
    """Undo each projector and compare the actual output-quotient subspaces."""
    for f, b in other.items():
        raw_basis = {}
        for row in b.values():
            raw = {i:x for i,x in row.items() if i<632}
            for j,r in enumerate(modes):
                a = row.get(632+j,Q(0))
                if a:
                    direct.add(raw,{i:x for i,x in enumerate(r) if x},a)
            direct.insert(raw_basis,raw)
        ref = scan['temporal_bases'][f][0]
        require(len(raw_basis) == len(ref), 'Same response dimension: ' + str(f))
        for nuisance,mode,_ in ref.values():
            raw = dict(nuisance)
            for r,a in zip(modes,mode):
                if a:
                    direct.add(raw,{i:x for i,x in enumerate(r) if x},a)
            require(direct.insert(raw_basis,raw) is None, 'Same output subspace: ' + str(f))
    expected_frames = {f for f in scan['temporal_bases']
                       if len(word['canonical']['frames'][f]) < 8}
    require(set(other) == expected_frames, 'All low frames compared')
    return len(other)


def clean_rank(rows):
    b = {}
    for r in rows:
        direct.insert(b,r)
    return sum(p>=632 for p in b)


def controls():
    # Two noisy responses cancel; independent nuisance coordinates do not.
    noisy = [{0:Q(1),632:Q(1)}, {0:Q(1)}]
    require(clean_rank(noisy)==1, 'Two-channel cancellation control')
    require(clean_rank([{0:Q(1),632:Q(1)},{1:Q(1),632:Q(1)}])==0,
            'Independent nuisance control')
    # Temporal accumulation has to retain both observations of one frame.
    b = {}; direct.insert(b,noisy[0]); p = direct.insert(b,noisy[1])
    require(p==632, 'Cross-time cancellation control')
    # Pair exclusion alone does not exclude three low channels with rank-2 noise.
    triple = [{0:Q(1)},{1:Q(1)},{0:Q(1),1:Q(1),632:Q(1)}]
    require(all(clean_rank([triple[i],triple[j]])==0 for i in range(3) for j in range(i)),
            'Every two of the three have zero clean response')
    require(clean_rank(triple)==1, 'Triple control creates a clean mode')
    # Add seven clean channels. The ten-channel example has an explicit payload
    # matrix with target I8, restored nuisance, and sum of costs 3H1+7H8.
    responses = triple + [{632+j:Q(1)} for j in range(1,8)]
    payloads = [[Q(0)]*8 for _ in responses]
    payloads[0][0] = payloads[1][0] = -1; payloads[2][0] = 1
    for j in range(1,8): payloads[j+2][j] = 1
    for j in range(8):
        out = {}
        for response,payload in zip(responses,payloads): direct.add(out,response,payload[j])
        require(out=={632+j:Q(1)}, 'Explicit abstract ten-channel endpoint')
    return {'two_channel_cancellation':True, 'independent_nuisance':True,
            'temporal_cancellation':True, 'three_low_pairwise_exclusion':True,
            'abstract_ten_channel_completion':True}


def run():
    checks = controls()
    word,modes = load_sources()
    module,scan = predecessor_scan(word,modes)
    first = primary_pairs(module,scan,word)
    print('Primary exact pair certificate passed.', flush=True)
    other,second = direct.census(word,modes)
    compared = compare_raw_spaces(scan,other,modes,word)
    second.update(direct.paircheck(other))
    require(first['frames']==second['frames']==879, 'Low frame count')
    require(first['distinct_pairs']==second['total_distinct_pairs']==385881, 'Pair coverage')
    require(first['nontrivial_nuisance_intersections']==second['nontrivial_nuisance_intersections']==3782, 'Intersection count')
    return {
        'claim':'No sum of two rank-below-eight temporal response spaces contains a nonzero clean mode; hence canonical delivery with at most nine channels costs at least 8 H8.',
        'scope':'Fixed PR5745 source and canonical immutable one-frame payload contract; necessary scalar quotient; arbitrary same-frame temporal reuse.',
        'predecessor_census':{k:scan[k] for k in ('contexts','projected_columns','temporal_observations')},
        'primary':first, 'independent':second, 'equal_low_frame_subspaces':compared,
        'controls':checks, 'independent_human_review':False,
        'not_covered_by_this_proof':'Ten or more jointly noisy channels; changed frame, payload or source contracts.',
        'related_work':'PR5823 separately proposes an any-finite-channel floor for concave power tariffs; that entire certificate is not independently replayed here.'
    }


if __name__ == '__main__':
    require(sys.argv[1:] in ([], ['--write-result']), 'Use no arguments or --write-result')
    result = json.loads(json.dumps(run()))
    path = ROOT/'RESULT.json'
    if sys.argv[1:]: path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: require(result==json.loads(path.read_text()), 'Complete semantic receipt')
    print(json.dumps(result,indent=2,sort_keys=True))
    print('PASS_NINE_CHANNEL_DELIVERY_BOUND')
