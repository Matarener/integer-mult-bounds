#!/usr/bin/env python3
"""Fresh all-annihilator-pairs / colored-completion-graph audit of PR3960.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
No executable from PR3960, PR3951 or other predecessor is imported.
"""
import ast
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REVIEWED_SHA = '65267c54c56f3e8614f3399dc810ec17b769d1085f68543ebb3fefb0d5bdfde2'
MANIFEST_SHA = '6c23d87eb2aa9a8865829ad8240e5f3b35ea2b18367bae6890b8b9877a1d3587'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    result = {}
    for k, v in items:
        require(k not in result, 'duplicate JSON key')
        result[k] = v
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sources():
    raw = (HERE/'SOURCES.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest identity')
    result = {}
    for row in json.loads(raw, object_pairs_hook=unique)['files']:
        if row['usage'] != 'input':
            continue
        p = ROOT/row['path']
        require(p.resolve().is_relative_to(ROOT.resolve()), 'source escaped root')
        require(not any(x.is_symlink() for x in (p, *p.parents)), 'source symlink')
        raw = p.read_bytes()
        require(len(raw) <= 2_000_000, 'source size')
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'], 'source Git blob')
        result[row['path']] = raw
    return result


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def inverse(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row]+[Fraction(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j]), None)
        require(pivot is not None, 'singular simple matrix')
        a[j], a[pivot] = a[pivot], a[j]
        scale = a[j][j]
        a[j] = [x/scale for x in a[j]]
        for i in range(n):
            if i != j:
                scale = a[i][j]
                a[i] = [x-scale*y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def geometry(payload):
    table = payload['research/one-sided-six-multisets/data/data.txt'].decode().splitlines()
    live = [tuple(map(int, row.split())) for row in table[2:114]]
    frame = [tuple(2 if k == i else 2*s if k == i+1 else 0 for k in range(8)) for i in range(0, 8, 2) for s in (-1, 1)]
    roots = sorted(live+frame)
    shell = {tuple(2 if k == i else 2*s if k == j else 0 for k in range(8)) for i, j in combinations(range(8), 2) for s in (-1, 1)}
    shell |= {(1, *tail) for tail in product((-1, 1), repeat=7) if sum(x < 0 for x in tail)%2 == 0}
    require(len(roots) == len(set(roots)) == 120 and set(roots) == shell, 'root shell')
    tree = ast.parse(payload['research/p112-root-simplex-exclusion/geometry.py'])
    simple = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'SIMPLE' for t in n.targets))
    inv = inverse(list(zip(*simple)))
    coords = [tuple(dot(row, r) for row in inv) for r in roots]
    require(all(x.denominator == 1 for c in coords for x in c), 'nonintegral coordinates')
    coords = [tuple(map(int, c)) for c in coords]
    require(all(tuple(sum(c[j]*simple[j][i] for j in range(8)) for i in range(8)) == r for c, r in zip(coords, roots)), 'coordinate reconstruction')
    require(all(all(x >= 0 for x in c) or all(x <= 0 for x in c) for c in coords), 'simple signs')
    labels = [1+sum((x%2) << (j+1) for j, x in enumerate(c)) for c in coords]
    require(len(set(labels)) == 120, 'label injectivity')
    live_mask = sum(1 << i for i, r in enumerate(roots) if r not in frame)
    require([x for i, x in enumerate(labels) if live_mask >> i & 1] == list(map(int, table[0].split())), 'original row-label binding')
    require([[sum(r[i]*r[j] for r in live) for j in range(8)] for i in range(8)] == [[112*(i == j) for j in range(8)] for i in range(8)], 'live Gram injectivity')
    signed = set(roots) | {tuple(-x for x in r) for r in roots}
    for alpha in simple:
        for r in signed:
            require(dot(alpha, r)%4 == 0, 'reflection integrality')
            require(tuple(x-dot(alpha, r)//4*y for x, y in zip(r, alpha)) in signed, 'reflection closure')
    rho = [sum(row) for row in inverse(simple)]
    require(all(dot(a, rho) == 1 for a in simple), 'chamber functional')
    faces = [[r for r, c in zip(roots, coords) if all(c[j] == 0 for j in range(8) if not mask >> j & 1)] for mask in range(256)]
    require(max(len(face) for mask, face in enumerate(faces) if mask.bit_count() <= 6) == 36, 'rank-six face bound')
    require([len(faces[255 ^ (1 << j)]) for j in range(8)] == [42, 28, 22, 14, 16, 23, 37, 63], 'seven-node faces')
    require(sum(all(dot(r, a) == 0 for a in faces[127]) for r in roots) == 1, 'E7 root normal')
    return roots, labels, live_mask


def all_flats(labels):
    """The unique ordered pair a<b<a^b represents each two-space once."""
    hyperplanes = [sum(1 << i for i, x in enumerate(labels) if (a & x).bit_count()%2 == 0) for a in range(512)]
    masks = [hyperplanes[a] & hyperplanes[b] for a in range(1, 512) for b in range(a+1, 512) if b < (a ^ b)]
    require(len(masks) == 511*510//6 == 43435, 'all annihilator pairs')
    require(max(x.bit_count() for x in masks) == 36, 'global seven-space trace')
    return masks


def completions(roots, live, masks):
    records = []
    off = []
    for r in roots:
        off.append(sum(1 << i for i, s in enumerate(roots) if live >> i & 1 and dot(r, s)))
    require(Counter(x.bit_count() for x in off) == {53: 112, 56: 8}, 'root word distances')
    for owner, word in enumerate(off):
        for mask in masks:
            cut = word & ~mask
            if cut.bit_count() <= 24:
                records.append((owner, mask, cut))
    records.sort()
    vertices = sorted({(owner, cut) for owner, _, cut in records})
    return records, vertices


def graph(vertices, cutoff=24):
    adjacency = [0]*len(vertices)
    edges = []
    for i, (a, s) in enumerate(vertices):
        for j in range(i+1, len(vertices)):
            b, t = vertices[j]
            if a != b and (s | t).bit_count() <= cutoff:
                adjacency[i] |= 1 << j
                adjacency[j] |= 1 << i
                edges.append((i, j))
    triangle = None
    for i, j in edges:
        common = adjacency[i] & adjacency[j]
        if common:
            triangle = (i, j, (common & -common).bit_length()-1)
            break
    degrees = Counter(x.bit_count() for x in adjacency)
    return edges, triangle, {str(k): v for k, v in sorted(degrees.items())}


def caller_arithmetic():
    caps = {2: 2, 3: 4, 4: 8, 5: 12}  # cap12 is inherited, not recertified here.
    profiles = [[2, 2, 2, 2, 3, 5, 7, 7, 7, 7, 7], [2, 2, 2, 2, 4, 4, 7, 7, 7, 7, 7]]
    output = []
    for weights in profiles:
        required_intersection = 5
        quotient_bound = len(weights)-required_intersection
        support_cap = sum(caps[w] for w in weights[:quotient_bound])
        require(support_cap == 24 < 53, 'small basis below distance')
        require(weights[quotient_bound:] == [7]*5, 'five rank-seven residual pieces')
        output.append({'weights': weights, 'required_intersection': required_intersection, 'quotient_bound': quotient_bound, 'basis_capacity_sum': support_cap, 'independent_residual_codewords': len(weights)-quotient_bound})
    return output


def compute():
    roots, labels, live = geometry(sources())
    masks = all_flats(labels)
    records, vertices = completions(roots, live, masks)
    edges, triangle, degrees = graph(vertices)
    require(triangle is None, 'three-color completion triangle')
    require(all(int(k) <= 1 for k in degrees), 'complete different-color graph is a matching')
    raw = (HERE/'REVIEWED.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA, 'reviewed target identity')
    target = json.loads(raw, object_pairs_hook=unique)['compared_fields']
    require(digest(sorted(Counter(masks).items())) == target['flat_inventory_digest'], 'target flat disagreement')
    require(digest(records) == target['critical_record_digest'] and len(records) == target['critical_records'], 'target record disagreement')
    require(edges, 'two-direction witness missing')
    i, j = edges[0]
    a, s = vertices[i]
    b, t = vertices[j]
    require(dot(roots[a], roots[a])*dot(roots[b], roots[b])-dot(roots[a], roots[b])**2 > 0, 'independent witness normals')
    return {'seven_spaces': len(masks), 'flat_multiset_sha256': digest(sorted(Counter(masks).items())), 'completion_records': len(records), 'completion_records_sha256': digest(records), 'colored_vertices': len(vertices), 'vertices_sha256': digest(vertices), 'different_color_edges': len(edges), 'edge_sha256': digest(edges), 'degree_histogram': degrees, 'triangles': 0, 'witness': {'normal_indices': [a, b], 'normals': [list(roots[a]), list(roots[b])], 'cut_labels': [label for k, label in enumerate(labels) if (s | t) >> k & 1]}, 'caller_arithmetic': caller_arithmetic()}


def main():
    require(not sys.argv[1:], 'no arguments accepted')
    observed = compute()
    require(digest(observed) == digest(read_json(HERE/'RESULT.json')), 'audit result receipt mismatch')
    print('PASS_COMMON24_GRAPH_AUDIT spaces=43435 records=6216 triangles=0 callers=2')


if __name__ == '__main__':
    main()
