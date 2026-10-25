#!/usr/bin/env python3
"""Seek a rank-seven return of a copied R437 center before full cleanup.

The nine centers are never scalar sources in A/B. A legal exact reset to their
independent dirty input after COPY permits deleting all their C writes and
retaining a rank-seven final frame. This search covers direct common-frame
linear resets at every B cut, using all compatible existing registers.
No helper input is assumed clean. Apache-2.0; substantial OpenAI assistance.
"""
from __future__ import annotations
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json
from entrance_closure import load_engine, require, SOURCE

HERE = Path(__file__).resolve().parent


def span_solve(columns, target):
    pivots = {}
    for role, value in columns:
        mask = 1 << role
        while value:
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value, mask
                break
            old, expr = pivots[pivot]
            value ^= old
            mask ^= expr
    result = 0
    residual = target
    while residual:
        pivot = residual.bit_length()-1
        if pivot not in pivots:
            return None, len(pivots), residual
        old, expr = pivots[pivot]
        residual ^= old
        result ^= expr
    return result, len(pivots), 0


def separation_witness(columns, target, residual):
    """Return an explicit dual bit row separating target from all donor rows."""
    pivots = {}
    for _, value in columns:
        while value:
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
    require(residual != 0, 'nonzero failed-solve residual')
    free = residual.bit_length()-1
    require(free not in pivots, 'chosen dual coordinate is free')
    dual = 1 << free
    for pivot, row in sorted(pivots.items()):
        if (row & dual).bit_count() % 2:
            dual ^= 1 << pivot
    # These literal pairings certify the exclusion without trusting elimination.
    require((target & dual).bit_count() % 2 == 1, 'dual detects reset target')
    require(all((row & dual).bit_count() % 2 == 0 for _, row in columns),
            'dual annihilates every compatible donor')
    return dual


def profile(word, dims, masks):
    current = word['start'][:]
    bill = Counter()
    def raise_role(role, frame):
        before = current[role]
        require(masks[before] & ~masks[frame] == 0, 'nonmonotone frame')
        if before != frame:
            bill[dims[frame]-dims[before]] += 1
            current[role] = frame
    for section in ('D', 'A', 'B', 'C'):
        if section == 'B':
            for role in word['ret']:
                require(dims[current[role]] == 7, 'retained rank-seven capture')
                bill[7] += 1
        for frame, target, sources in word[section]:
            for role in [target]+sources:
                raise_role(role, frame)
    for role, frame in enumerate(word['final']):
        raise_role(role, frame)
    return dict(sorted(bill.items()))


def whole(word):
    v = word['v']; rows = [1 << r for r in range(2*v+word['R'])]
    for section in ('D','A','B','C'):
        if section == 'B':
            captures = [rows[r] for r in word['ret']]
            for target, terms in enumerate(word['scatter']):
                for term in terms:
                    rows[v+target] ^= captures[term]
        for _, target, sources in word[section]:
            for source in sources:
                rows[target] ^= rows[source]
    return rows


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'center-return')
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    path = SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz'
    raw = path.read_bytes(); word = json.loads(gzip.decompress(raw))
    canonical = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    expected = json.loads((SOURCE/'EXPECTED.json').read_text())
    require(sha256(canonical).hexdigest() == expected['word_content_sha256'], 'canonical source pin')
    engine = load_engine()
    dims = [len(engine.rref([word['lines'][j] for j in frame])) for frame in word['frames']]
    masks = [sum(1 << j for j in frame) for frame in word['frames']]
    n = 2*word['v']+word['R']
    centers = word['ret']
    require(not any(set(sources)&set(centers) for _,_,sources in word['A']+word['B']),
            'centers are not scalar sources before cleanup')
    current = word['start'][:]; rows = [1 << r for r in range(n)]
    for frame, target, sources in word['A']:
        for role in [target]+sources:
            current[role] = frame
        for source in sources:
            rows[target] ^= rows[source]
    center_frames = {h: current[h] for h in centers}
    require(all(dims[f] == 7 for f in center_frames.values()), 'actual capture ranks')
    baseline = profile(word, dims, masks)
    require(baseline == {1:1320,2:1344,3:77,4:43,5:102,6:11,7:18}, 'independent baseline complete local bill')
    all_next = []
    nexts = word['final'][:]
    all_next.append(nexts.copy())
    for frame, target, sources in reversed(word['B']):
        for role in [target]+sources:
            nexts[role] = frame
        all_next.append(nexts.copy())
    all_next.reverse()
    records = []; found = []
    exponent = 0.001736738651088946052684
    power = lambda r: r**(1-exponent) if r else 0.0
    for cut in range(len(word['B'])+1):
        nexts = all_next[cut]
        for center, frame in center_frames.items():
            target = rows[center] ^ (1 << center)
            require(target != 0, 'source has no already-returned center')
            eligible = [r for r in range(n) if not 111 <= r < 222 and r != center
                        and masks[current[r]] & ~masks[frame] == 0
                        and masks[frame] & ~masks[nexts[r]] == 0]
            def donor_cost(role):
                return (power(dims[frame]-dims[current[role]])
                        +power(dims[nexts[role]]-dims[frame])
                        -power(dims[nexts[role]]-dims[current[role]]))
            eligible.sort(key=lambda r: (donor_cost(r), rows[r].bit_count(), r))
            columns = [(r, rows[r]) for r in eligible]
            solution, rank, residual = span_solve(columns, target)
            dual = separation_witness(columns, target, residual) if solution is None else None
            records.append(dict(center=center, cut=cut, frame=frame, eligible=eligible,
                                eligible_rank=rank, solved=solution is not None,
                                residual_hex=hex(residual),
                                separating_covector_hex=hex(dual) if dual is not None else None))
            if solution is None:
                continue
            support = [r for r in eligible if solution >> r & 1]
            check = 0
            for role in support:
                check ^= rows[role]
            require(check == target, 'independent literal reset equality')
            candidate = deepcopy(word)
            candidate['B'].insert(cut, [frame, center, support])
            candidate['C'] = [gate for gate in candidate['C'] if gate[1] != center]
            require(not any(center in sources for _,_,sources in candidate['C']), 'no remaining C read of lowered center')
            candidate['final'][center] = frame
            actual = whole(candidate)
            want = [(1 << r) ^ ((1 << (r-111)) if 111 <= r < 222 else 0) for r in range(n)]
            require(actual == want, 'all659 arbitrary dirty scalar columns')
            price = profile(candidate, dims, masks)
            delta = Counter(price); delta.subtract(baseline)
            delta = {r:c for r,c in sorted(delta.items()) if c}
            info = dict(center=center, cut=cut, frame=frame, support=support,
                        local_profile=price, local_delta=delta,
                        approximate_local_saving=-sum(c*power(r) for r,c in delta.items()),
                        status='EXACT_LOCAL_RETURN_CANDIDATE_REQUIRES_NATIVE_AND_COMPLETE_OWNER_ADMISSION')
            stem = f'CENTER-{center}-CUT-{cut}'
            payload = json.dumps(candidate, sort_keys=True, separators=(',', ':')).encode()
            (args.out/(stem+'.json.gz')).write_bytes(gzip.compress(payload, mtime=0))
            info['word_canonical_sha256'] = sha256(payload).hexdigest()
            (args.out/(stem+'.json')).write_text(json.dumps(info, sort_keys=True, indent=2)+'\n')
            found.append(info)
            print('FOUND', info, flush=True)
        if cut < len(word['B']):
            frame, target, sources = word['B'][cut]
            for role in [target]+sources:
                current[role] = frame
            for source in sources:
                rows[target] ^= rows[source]
    result = dict(status='PASS_COMPLETE_DIRECT_CENTER_RETURN_SPAN_SCREEN',
                  source_sha256=sha256(raw).hexdigest(), source_canonical_sha256=sha256(canonical).hexdigest(),
                  script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  support_implementation_sha256=sha256((HERE/'entrance_closure.py').read_bytes()).hexdigest(),
                  frame_engine_sha256=sha256((HERE.parents[2]/'research/r439-kernel-entrance-closure/verify.py').read_bytes()).hexdigest(),
                  centers=centers, cuts_per_center=len(word['B'])+1, cases=len(records),
                  candidates=found, cases_checked=records,
                  scope='One exact linear reset of one copied center, after all prescribed COPYs at any existing B cut, at its unchanged rank-seven capture frame, using any compatible existing non-target registers; fixed A/B donor chronology. Arbitrary-length reset circuits, coordinated multiple centers, shifted COPY timing and changed scalar graphs remain outside this span test.')
    (args.out/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(result['status'], 'cases', len(records), 'candidates', len(found), flush=True)


if __name__ == '__main__':
    main()
