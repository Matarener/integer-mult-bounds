#!/usr/bin/env python3
"""Exact all-support first-contact entrance screen for the actual R437 word.

The intersection-closure theorem and rational rowspace engine are credited to
mightyOil's r439-kernel-entrance-closure; the changed source is ai-nanachi's
PR3647 at a24f9ff95c12fd0b6792e3f710569237efd72db2. This script rederives the
entire dirty response of the actual changed word before computing its null
directions. It supplies neither a physical entrance nor a general obstruction.
Apache-2.0. Substantial OpenAI assistance under the user's direction.
"""
from __future__ import annotations
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = HERE.parent / 'sources/PR3647/research/bit-p111-r437-gl464-470-20261018'
ENGINE = REPO / 'research/r439-kernel-entrance-closure/verify.py'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load_engine():
    spec = importlib.util.spec_from_file_location('credited_entrance_engine', ENGINE)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


def extract(word, engine):
    v, count = word['v'], word['R']
    offset, n = 2*v, 2*v+count
    require((v, count, word['h']) == (111, 437, 8), 'actual source geometry')
    require(len(word['start']) == len(word['final']) == n, 'endpoint inventory')
    require(word['start'][offset:] == [0]*count and word['final'][offset:] == [1]*count,
            'ordinary zero-to-full helper endpoints')
    response = [0]*count
    for frame, target, sources in word['D']:
        require(frame == 0 and v <= target < offset, 'compensation target/frame')
        for source in sources:
            require(offset <= source < n, 'compensation source helper')
            response[source-offset] ^= 1 << (target-v)
    first = {}
    for frame, target, sources in word['A'] + word['B']:
        for role in [target] + sources:
            if role >= offset:
                require(role < n, 'helper index')
                first.setdefault(role, frame)
    require(set(first) == set(range(offset, n)), 'complete first-contact inventory')
    frames = {frame: engine.rref([word['lines'][i] for i in word['frames'][frame]])
              for frame in set(first.values())}
    rows = [1 << i for i in range(n)]
    a_helpers = {r for _, t, ss in word['A'] for r in [t]+ss if r >= offset}
    require(set(word['ret']) <= a_helpers, 'copied helpers have earlier A contact')
    for phase in ('A', 'scatter', 'B', 'C'):
        if phase == 'scatter':
            captured = [rows[h] for h in word['ret']]
            for i, terms in enumerate(word['scatter']):
                for term in terms:
                    rows[v+i] ^= captured[term]
        else:
            for _, target, sources in word[phase]:
                for source in sources:
                    rows[target] ^= rows[source]
    for role, actual in enumerate(rows):
        expected = 1 << role
        if v <= role < offset:
            target = role-v
            expected ^= 1 << target
            for j, column in enumerate(response):
                if column >> target & 1:
                    expected ^= 1 << (offset+j)
        require(actual == expected, 'raw map/D disagreement on independent input columns')
    return response, first, frames


def independent_nullity(columns):
    """Binary row elimination, separate from the credited column-mask engine."""
    rows = [sum(((col >> bit) & 1) << j for j, col in enumerate(columns))
            for bit in range(111)]
    rank = 0
    for j in range(len(columns)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> j & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> j & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return len(columns)-rank


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=HERE/'R437-ENTRANCE-CLOSURE.json')
    args = ap.parse_args()
    path = SOURCE/'data/r0042/R437-COMPOSED-WORD.json.gz'
    raw = path.read_bytes()
    word = json.loads(gzip.decompress(raw))
    expected = json.loads((SOURCE/'EXPECTED.json').read_text())
    canonical = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
    require(sha256(canonical).hexdigest() == expected['word_content_sha256'], 'source canonical word pin')
    engine = load_engine()
    response, first, frames = extract(word, engine)
    spaces = set(frames.values())
    closure, pairs = engine.geometry_closure(spaces)
    normals = {frame: engine.orthogonal(frame) for frame in spaces}
    classes = []
    for space in closure:
        # Exact annihilator membership is equivalent to the credited RREF test.
        eligible = [h for h in sorted(first)
                    if all(sum(x*y for x, y in zip(row, normal)) == 0
                           for row in space for normal in normals[frames[first[h]]])]
        rank, nullbasis = engine.kernel(response, eligible)
        nullity = len(eligible)-rank
        require(nullity == len(nullbasis) == independent_nullity([response[h-222] for h in eligible]),
                'independent row/column nullity comparison')
        for direction in nullbasis:
            require(all(h in eligible for h in direction), 'kernel support contained')
            mask = 0
            for h in direction:
                mask ^= response[h-222]
            require(mask == 0, 'literal response of reported kernel')
        classes.append(dict(frame=[[str(x) for x in row] for row in space],
                            eligible_helpers=eligible, response_rank=rank,
                            nullity=nullity, kernel_basis=nullbasis))
    result = dict(
        status='PASS_EXACT_R437_ALL_SUPPORT_FIRST_CONTACT_CLASSIFICATION',
        word_sha256=sha256(raw).hexdigest(), word_canonical_sha256=sha256(canonical).hexdigest(),
        source_head='a24f9ff95c12fd0b6792e3f710569237efd72db2',
        engine_sha256=sha256(ENGINE.read_bytes()).hexdigest(),
        script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        arbitrary_input_columns=659, helper_count=437,
        first_frame_ids=len(frames), first_distinct_rowspaces=len(spaces),
        first_dimensions=dict(Counter(len(frames[first[h]]) for h in first)),
        closure_dimensions=dict(Counter(map(len, closure))),
        intersecting_distinct_plane_pairs=pairs,
        nullity_histogram=dict(Counter(row['nullity'] for row in classes)),
        viable_classes=[row for row in classes if row['nullity']], classes=classes,
        controls=engine.controls(),
        scope='All binary helper response-kernel supports and all nonzero rational common first-contact entrances of the fixed R437 A/scatter/B/C word. Later cuts, changed A, source donors, altered target interfaces and different physical controllers are outside this classification. No new kappa or native supplier is inferred.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as handle:
        json.dump(result, handle, sort_keys=True, indent=2)
        handle.write('\n')
    print(result['status'], 'classes', len(classes), 'nullity', result['nullity_histogram'], flush=True)


if __name__ == '__main__':
    main()
