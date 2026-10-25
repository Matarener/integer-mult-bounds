#!/usr/bin/env python3
"""Common24 rank-seven theorem and two literal C5 callers.

Chris R / Clear1nsight with substantial OpenAI Codex assistance; Apache-2.0.
Credit Nick Petalas, DreamingOfClouds/3154, David Arias and E8/P112 lineage.
"""
from collections import Counter
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import model as m

MANIFEST_SHA = '4d49389e8131d6ec139722f60e12d697e4d0d31eba205b5e6d11543d22b4afd3'
TABLE = 'research/one-sided-six-multisets/data/data.txt'
GEOMETRY = 'research/p112-root-simplex-exclusion/geometry.py'
FILTER = 'research/p112-b6-t4-reconciliation/vendor/bk2b.py'


def unique(pairs):
    m.require(len(pairs) == len({k for k, _ in pairs}), 'duplicate JSON key')
    return dict(pairs)


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def histogram(values):
    return {str(k): n for k, n in sorted(Counter(values).items())}


def authenticate(root=ROOT, package=HERE):
    raw = (package / 'SOURCES.json').read_bytes()
    m.require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest identity')
    result = {}
    for row in load(raw)['files']:
        if row['usage'] != 'input':
            continue
        path = root / row['path']
        m.require(path.resolve().is_relative_to(root.resolve()), 'input escaped root')
        m.require(not any(p.is_symlink() for p in [path, *path.parents]), 'input symlink')
        data = path.read_bytes()
        m.require(len(data) <= 2_000_000, 'source size limit')
        m.require(hashlib.sha256(data).hexdigest() == row['sha256'], 'source SHA256')
        m.require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
                  == row['git_blob'], 'source Git blob')
        result[row['path']] = data
    return result


def chamber(roots, coordinates):
    signed = set(roots) | {tuple(-x for x in r) for r in roots}
    for alpha in m.SIMPLE:
        for r in signed:
            p = m.dot(alpha, r)
            m.require(p % 4 == 0, 'reflection integrality')
            m.require(tuple(x-p//4*y for x, y in zip(r, alpha)) in signed,
                      'signed reflection closure')
    rho = m.solve(m.SIMPLE, [[1]*8])[0]
    m.require(all(m.dot(rho, a) == 1 for a in m.SIMPLE), 'strict chamber functional')
    faces = [[r for r, c in zip(roots, coordinates) if all(c[j] == 0 for j in range(8)
              if not mask >> j & 1)] for mask in range(256)]
    cap6 = max(len(faces[x]) for x in range(256) if x.bit_count() <= 6)
    seven = [len(faces[255 ^ (1 << j)]) for j in range(8)]
    m.require(cap6 == 36 and seven == [42,28,22,14,16,23,37,63], 'face bounds')
    normal = [r for r in roots if all(m.dot(r, z) == 0 for z in faces[127])]
    m.require(len(normal) == 1, 'E7 root normal')
    return {'signed_reflections': 1920, 'rho': [str(x) for x in rho],
            'rank6_face_maximum': cap6, 'seven_node_counts': seven,
            'E7_normal': normal[0]}


def cut_records(roots, live, flats):
    off = [sum(1 << i for i, r in enumerate(roots) if live >> i & 1 and m.dot(r, a))
           for a in roots]
    m.require(histogram(x.bit_count() for x in off) == {'53':112,'56':8}, 'root distances')
    records, trace_hist = [], Counter()
    for a, word in enumerate(off):
        for flat in flats:
            trace = (flat & word).bit_count()
            trace_hist[trace] += 1
            cut = word & ~flat
            if cut.bit_count() <= 24:
                records.append((a, flat, cut))
    m.require(max(trace_hist) == 32, 'root-word rank-seven trace cap')
    records.sort()
    counts = Counter(('live' if live >> a & 1 else 'frame', cut.bit_count())
                     for a, _, cut in records)
    m.require(counts == {('live',21):336,('live',23):5376,('frame',24):504},
              'critical cut classes')
    return records, off, {str(k):v for k,v in sorted(trace_hist.items())}


def candidate_cuts(records):
    cuts = sorted({c for _, _, c in records})
    small = [c for c in cuts if c.bit_count() == 21]
    edges = [(i,j) for i,j in combinations(range(len(small)),2)
             if (small[i] | small[j]).bit_count() <= 24]
    degrees = Counter(i for pair in edges for i in pair)
    m.require(len(small) == 336 and len(edges) == 168 and set(degrees.values()) == {1},
              '21-cut compatibility is a matching')
    candidates = {c for c in cuts if c.bit_count() >= 23}
    for s in cuts:
        if s.bit_count() != 23:
            continue
        for t in cuts:
            union = s | t
            if union.bit_count() <= 24:
                candidates.add(union)
    return sorted(candidates), len(edges)


def analyze(roots, labels, live, records, candidates):
    by_normal = [[] for _ in roots]
    for a, _, cut in records:
        by_normal[a].append(cut)
    counts, witness = Counter(), None
    admitted_rows = []
    for p in candidates:
        normals = [a for a, cuts in enumerate(by_normal) if any(c & ~p == 0 for c in cuts)]
        m.require(len(normals) <= 2, 'common24 direction limit exceeded')
        counts[(p.bit_count(),len(normals))] += 1
        admitted_rows.append((p, normals))
        if len(normals) == 2 and p.bit_count() == 24 and witness is None:
            a,b = normals
            determinant = m.dot(roots[a], roots[a])*m.dot(roots[b], roots[b])-m.dot(roots[a],roots[b])**2
            m.require(determinant > 0, 'independent attaining pair')
            completions = [next((flat,cut) for n,flat,cut in records
                                if n == normal and cut & ~p == 0) for normal in normals]
            for normal,(flat,_) in zip(normals,completions):
                residual = [label for i,label in enumerate(labels)
                            if live>>i&1 and m.dot(roots[normal],roots[i]) and not p>>i&1]
                m.require(all(flat>>i&1 for i in range(120) if live>>i&1
                              and m.dot(roots[normal],roots[i]) and not p>>i&1),
                          'witness completion containment')
                m.require(len(m.basis(residual)) <= 7, 'witness residual rank')
            witness = {'cut_labels':[x for i,x in enumerate(labels) if p>>i&1],
                       'normal_indices':normals, 'normals':[roots[a],roots[b]],
                       'completion_masks':[flat for flat,_ in completions],
                       'Gram_determinant':determinant}
    m.require(witness is not None, 'two-direction attainment missing')
    m.require(sum(counts.values()) == 8540, 'candidate domain size')
    return {'candidate_sizes':histogram(p.bit_count() for p in candidates),
            'candidate_direction_histogram':{f'{s}:{n}':v for (s,n),v in sorted(counts.items())},
            'candidate_admission_digest':digest(admitted_rows), 'maximum_directions':2,
            'attaining_pair':witness}


def historical(weights, b):
    caps = {2:2,3:4,4:8,5:12,6:20,7:36}
    distance = [0,53,78,92,100,106,109,111,112]
    if sum(w-2 for w in weights) >= 6*b:
        return False
    for level in range(1,b+1):
        kept = weights[:len(weights)-b+level]
        total = sum(caps[w] for w in kept)
        target = sum(32 if w == 7 else caps[w] for w in kept)
        if level == 1 and target < 53 and total < 73:
            return False
        if level == 2 and target < 78 and total < 82:
            return False
        if level >= 3 and total < distance[level]:
            return False
    base = weights[:len(weights)-b]
    return not (sum(caps[w] for w in base) < 53 and
                (sum(base) <= 7 or any(sum(x)<=6 and sum(base)-sum(x)<=6
                 for n in range(len(base)+1) for x in combinations(base,n))))


def callers():
    result = []
    for weights in [(2,2,2,2,3,5,7,7,7,7,7),(2,2,2,2,4,4,7,7,7,7,7)]:
        m.require(historical(weights,5), 'literal historical caller not a survivor')
        base = weights[:6]
        cap = sum({2:2,3:4,4:8,5:12}[w] for w in base)
        m.require(cap == 24 and cap < 53, 'quotient independence cap')
        all_caps = [sum({2:2,3:4,4:8,5:12,7:36}[weights[i]] for i in indices)
                    for indices in combinations(range(11),6)]
        m.require(len(all_caps)==462 and min(all_caps)==24, 'all quotient-basis cap tests')
        m.require(len(weights)-6 == 5 and all(w == 7 for w in weights[6:]), 'five endpoints')
        result.append({'weights':weights, 'cell':[5,6], 'required_code_dimension':5,
                       'quotient_dimension':6, 'basis_indices':list(range(6)),
                       'basis_support_cap':cap, 'minimum_six_piece_capacity_sum':min(all_caps),
                       'six_piece_subsets_checked':len(all_caps), 'independent_directions_required':5,
                       'proved_direction_limit':2, 'strict_excess_deficit':30-sum(w-2 for w in weights)})
    return result


def compute(payloads):
    roots, labels, coordinates, live = m.reconstruct(payloads[TABLE],payloads[GEOMETRY])
    ker = m.kernels(labels,[1 << j for j in range(9)])
    flats = list(m.masks(ker,m.annihilators(9,7)))
    m.require(len(flats) == 43435 and max(x.bit_count() for x in flats) == 36,
              'complete rank-seven capacity')
    full5 = Counter(x.bit_count() for x in m.masks(ker,m.annihilators(9,5)))
    m.require(sum(full5.values()) == 3309747 and max(full5) == 12, 'caller rank-five capacity')
    records, _, traces = cut_records(roots,live,flats)
    candidates, edges = candidate_cuts(records)
    analysis = analyze(roots,labels,live,records,candidates)
    return {'schema':'p112-common24-caller/v1', 'spaces7':len(flats),
            'full_trace7_histogram':histogram(x.bit_count() for x in flats),
            'full_trace5_histogram':{str(k):v for k,v in sorted(full5.items())},
            'flat_inventory_digest':digest(sorted(Counter(flats).items())),
            'root_trace_histogram':traces, 'critical_records':len(records),
            'critical_record_digest':digest(records), 'unique_cuts':len({c for _,_,c in records}),
            'small_cut_matching_edges':edges, 'chamber':chamber(roots,coordinates),
            'analysis':analysis, 'callers':callers()}


def main():
    m.require(not sys.argv[1:], 'no arguments accepted')
    observed = compute(authenticate())
    expected = load((HERE/'RESULT.json').read_bytes())
    m.require(json.dumps(observed,sort_keys=True) == json.dumps(expected,sort_keys=True),
              'result receipt mismatch')
    print('PASS_COMMON24_CALLER spaces7=43435 cuts=6188 candidates=8540 directions<=2 callers=2')


if __name__ == '__main__':
    main()
