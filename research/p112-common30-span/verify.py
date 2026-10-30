#!/usr/bin/env python3
"""Common30 rank-seven span theorem and literal C5 caller.

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



def rank_q(rows):
    from fractions import Fraction
    a = [[Fraction(x) for x in row] for row in rows]
    rank = 0
    for j in range(8):
        pivot = next((i for i in range(rank,len(a)) if a[i][j]),None)
        if pivot is None:
            continue
        a[rank],a[pivot] = a[pivot],a[rank]
        scale = a[rank][j]
        a[rank] = [x/scale for x in a[rank]]
        for i in range(rank+1,len(a)):
            scale = a[i][j]
            a[i] = [x-scale*y for x,y in zip(a[i],a[rank])]
        rank += 1
    return rank


def completion_records(roots,live,flats):
    records = []
    for a,h in enumerate(roots):
        word = sum(1<<i for i,r in enumerate(roots) if live>>i&1 and m.dot(r,h))
        m.require(word.bit_count() == (53 if live>>a&1 else 56), 'root support')
        for flat in flats:
            cut = word & ~flat
            if cut.bit_count() <= 30:
                records.append((a,flat,cut))
    return sorted(records)


def compatible_graph(nodes):
    adjacent = [set() for _ in nodes]
    edges = []
    owners = [a for a,c in nodes]
    cuts = [c for a,c in nodes]
    for i,(owner,cut) in enumerate(nodes):
        for j in (j for j in range(i) if owner != owners[j]
                  and (cut|cuts[j]).bit_count() <= 30):
            adjacent[i].add(j)
            adjacent[j].add(i)
            edges.append((j,i))
    return adjacent,sorted(edges)


def independent_prefixes(roots,nodes,adjacent):
    counts = Counter()
    maximum = 0
    witness = None
    def visit(chosen,union,candidates):
        nonlocal maximum,witness
        if chosen:
            rank = rank_q([roots[nodes[i][0]] for i in chosen])
            counts[(len(chosen),union.bit_count(),rank)] += 1
            if rank > maximum:
                maximum,witness = rank,(chosen,union)
            if rank < len(chosen):
                return
        for i in sorted(candidates):
            joined = union | nodes[i][1]
            if joined.bit_count() <= 30:
                visit(chosen+[i],joined,{j for j in candidates & adjacent[i] if j>i})
    visit([],0,set(range(len(nodes))))
    m.require(maximum == 3, 'common30 span bound and attainment')
    m.require(all(size==30 for (n,size,rank) in counts if n>=3), 'common29 at most two directions')
    return counts,witness


def literal_caller(payloads):
    import ast
    weights = (2,2,2,2,2,6,7,7,7,7,7)
    tree = ast.parse(payloads[FILTER])
    nodes = [n for n in tree.body if isinstance(n,(ast.ImportFrom,ast.Assign,ast.FunctionDef))]
    namespace = {}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<authenticated PR3154 filter>','exec'),namespace)
    m.require(namespace['feasible'](weights,5) and not namespace['killed'](weights,5),
              'literal historical survivor')
    capacity = {2:2,6:20,7:36}
    sums = [sum(capacity[weights[i]] for i in chosen) for chosen in combinations(range(11),6)]
    m.require(min(sums)==30 and sums.count(30)==1, 'six-piece capacity minimum')
    m.require(sum(w-2 for w in weights)==29, 'strict excess')
    return {'weights':weights,'b':5,'t':6,'required_intersection_dimension':5,
            'quotient_dimension':6,'minimum_six_piece_capacity_sum':30,
            'minimum_basis_choices':1,'six_piece_subsets':len(sums),'strict_excess_deficit':1,
            'required_independent_directions':5,'uniform_available_span_dimension':3}


def compute():
    payloads = authenticate()
    roots,labels,coordinates,live = m.reconstruct(payloads[TABLE],payloads[GEOMETRY])
    kernel = m.kernels(labels,[1<<i for i in range(9)])
    flats = list(m.masks(kernel,m.annihilators(9,7)))
    m.require(len(flats)==43435 and max(x.bit_count() for x in flats)==36, 'seven-space domain and cap')
    six_count,six_max = 0,0
    for flat in m.masks(kernel,m.annihilators(9,6)):
        six_count += 1
        six_max = max(six_max,flat.bit_count())
    m.require(six_count==788035 and six_max==20, 'global rank-six capacity')
    records = completion_records(roots,live,flats)
    nodes = sorted({(a,c) for a,_,c in records})
    adjacent,edges = compatible_graph(nodes)
    counts,witness = independent_prefixes(roots,nodes,adjacent)
    indices,cut = witness
    normals = [roots[nodes[i][0]] for i in indices]
    m.require(rank_q(normals)==3 and cut.bit_count()==30, 'sharp rank-three witness')
    for normal in normals:
        residual = [labels[i] for i,r in enumerate(roots) if live>>i&1 and not cut>>i&1 and m.dot(r,normal)]
        m.require(len(m.basis(residual))==7, 'attaining triple residual rank')
    return {'spaces7':len(flats),'flat_inventory_digest':digest(sorted(Counter(flats).items())),
            'maximum_rank7_trace':36,'spaces6':six_count,'maximum_rank6_trace':six_max,
            'chamber':chamber(roots,coordinates),'critical_records':len(records),
            'critical_record_digest':digest(records),'nodes':len(nodes),'node_digest':digest(nodes),
            'cut_size_histogram':histogram(c.bit_count() for a,c in nodes),
            'edges':len(edges),'edge_digest':digest(edges),
            'prefix_histogram':[[list(k),v] for k,v in sorted(counts.items())],
            'maximum_span_common30':3,'maximum_directions_common29':2,
            'attaining_triple':{'normal_indices':[nodes[i][0] for i in indices],
                 'normals':normals,'cut_labels':[label for i,label in enumerate(labels) if cut>>i&1]},
            'caller':literal_caller(payloads)}


def main():
    m.require(not sys.argv[1:], 'no arguments accepted')
    observed = compute()
    expected = load((HERE/'RESULT.json').read_bytes())
    m.require(json.dumps(observed,sort_keys=True)==json.dumps(expected,sort_keys=True), 'result receipt mismatch')
    print('PASS_COMMON30_SPAN nodes=24264 edges=9828 maximum_span=3 common29_directions=2 caller=2^5,6,7^5 excluded')


if __name__ == '__main__':
    main()
