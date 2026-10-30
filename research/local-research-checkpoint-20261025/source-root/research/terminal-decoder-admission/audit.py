"""Routed summary and common-frame admission screens. No new supplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('decoder_design', HERE.parent/'mechanism-design-reset/audit.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)
require, encode = D.require, D.encode
F = D.Field(False)
GRAPH = ROOT/'research/coordinated-frames-and-entrance-banks/selected/complex/graph.json.gz'


def transpose(a):
    return [list(x) for x in zip(*a)]


def basis(rows):
    pivots = {}
    for x in rows:
        for p, v in sorted(pivots.items(), reverse=True):
            if x >> p & 1:
                x ^= v
        if x:
            p = x.bit_length()-1
            for k, v in list(pivots.items()):
                if v >> p & 1:
                    pivots[k] ^= x
            pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def apply(columns, x):
    result = 0
    while x:
        bit = x & -x
        result ^= columns[bit.bit_length()-1]
        x ^= bit
    return result


def exchange(q, h, block):
    """The retained R_12,S or R_23,S on the padded 3h-dimensional space."""
    m = 3*h
    pivot = next(i for i in range(h) if not (q >> i & 1))
    v = q ^ (1 << pivot)
    local = [(1 << i) ^ (v if v >> i & 1 else 0) for i in range(h) if i != pivot]
    offset = h if block == 1 else 2*h-1
    external = [1 << (offset+i) for i in range(h-1)]
    flips = [u ^ b for u, b in zip(local, external)]
    columns = []
    for j in range(m):
        x = 1 << j
        for w in flips:
            if w >> j & 1:
                x ^= w
        columns.append(x)
    require(apply(columns, q) == q, 'source line fixed')
    for u, b in zip(local, external):
        require(apply(columns, u) == b and apply(columns, b) == u, 'active basis exchange')
    require(all(apply(columns, x) == 1 << j for j, x in enumerate(columns)), 'involution')
    require(all((x & y).bit_count() % 2 == int(i == j)
                for i, x in enumerate(columns) for j, y in enumerate(columns)), 'orthogonal map')
    require(basis(columns[:h]) == basis([q]+external), 'active image determines the source line')
    require(columns[-2:] == [1 << (m-2), 1 << (m-1)], 'padding fixed')
    return tuple(columns)


def source_control():
    blob = GRAPH.read_bytes()
    graph = json.loads(gzip.decompress(blob))
    h, ports = graph['h'], graph['inputs']
    n = len(ports)
    require((h, n) == (22, 1320), 'selected complex motif')
    expected = {sum(1 << (2*p+s) for p, s in zip(ps, ss))
                for ps in combinations(range(h//2), 3) for ss in product(range(2), repeat=3)}
    require(set(ports) == expected and len(set(ports)) == n, 'all paired-cube ports exactly once')
    roots = [r for r in graph['roots'] if r.get('kind') == 'center']
    require(len(roots) == h and {r['coordinate'] for r in roots} == set(range(h)), 'all star roots')
    @lru_cache(None)
    def value(node):
        if node < n:
            return {node: 1}
        a, b = graph['args'][node]
        result = dict(value(a))
        for source, coefficient in value(b).items():
            result[source] = result.get(source, 0)+graph['signs'][node]*coefficient
        return {s: c for s, c in result.items() if c}
    for root in roots:
        j = root['coordinate']
        require(value(root['node']) == {t: 1 for t, q in enumerate(ports) if q >> j & 1},
                'actual signed center producer equals the incidence row')
        coefficients = {t: Q(c) for t, c in zip(root['targets'], root['coefficients'])}
        require(coefficients == {t: Q(int(q >> j & 1), 2)-Q(1, 6) for t, q in enumerate(ports)},
                'actual center scatter equals the retained central matrix')
    V = [[Q(q >> i & 1) for q in ports] for i in range(h)]
    gram = F.mm(V, transpose(V))
    require(all(gram[i][j] == (180 if i == j else 0 if i//2 == j//2 else 18)
                for i in range(h) for j in range(h)), 'paired incidence Gram')
    inverse = F.inverse(gram)
    leverages = []
    for q in ports:
        support = [i for i in range(h) if q >> i & 1]
        leverages.append(sum(inverse[i][j] for i in support for j in support))
    require(set(leverages) == {Q(h, n)}, 'uniform leverage on actual columns')
    routes = [[exchange(q, h, block) for q in ports] for block in (1, 3)]
    require(all(len(set(maps)) == n for maps in routes), 'no adjacent-stage routing collisions')
    overlap = sum(x*x for x in leverages)
    require(overlap == Q(h*h, n), 'regular-cover projection overlap per group element')
    pair_lower = 2*h-overlap
    total_lower = 2*pair_lower
    return dict(h=h, ports=n, local_summary_rank=h,
                source_sha256=sha256(blob).hexdigest(), star_roots_checked=h,
                leverage=Q(h, n), projection_trace_per_group=overlap,
                pair_summary_rank_lower_per_group=pair_lower,
                both_input_summary_rank_lower_per_group=total_lower,
                aligned_summary_rank_per_group=2*h, separate_summary_rank_per_group=4*h,
                expansion_over_aligned_lower=total_lower/(2*h),
                excess_over_three_local_banks_lower=total_lower/(3*h),
                route_maps_checked=2*n, distinct_maps_per_stage=[len(set(x)) for x in routes],
                route_inventory_sha256=sha256(json.dumps(routes, separators=(',', ':')).encode()).hexdigest(),
                scope='Full regular cover trace formula; no enumeration of O(66,2). '
                      'Bound on this factorization input summaries, not all decoder algorithms.')


def regular_cover_control(collision=False):
    a = [[Q(1), Q(0), Q(1)], [Q(0), Q(1), Q(1)]]
    k, v, group_size = 2, 3, 3
    routes = [0, 0, 0] if collision else [0, 1, 2]
    def lifted(twisted):
        matrix = F.zero(group_size*k, group_size*v)
        for vertex in range(group_size):
            for row in range(k):
                for port in range(v):
                    data_group = (vertex-routes[port]) % group_size if twisted else vertex
                    matrix[vertex*k+row][data_group*v+port] = a[row][port]
        return matrix
    def projector(rows):
        return F.mm(transpose(rows), F.mm(F.inverse(F.mm(rows, transpose(rows))), rows))
    left, right = lifted(False), lifted(True)
    p, q = projector(left), projector(right)
    trace = sum(F.mm(p, q)[i][i] for i in range(group_size*v))
    local = projector(a)
    full_formula = group_size*sum(local[s][t]*local[t][s]
                                  for s in range(v) for t in range(v) if routes[s] == routes[t])
    require(trace == full_formula, 'independent dense trace replay')
    diagonal_formula = group_size*sum(local[s][s]**2 for s in range(v))
    intersection = 2*group_size*k-D.H.H.rank(left+right)
    require(intersection <= trace, 'intersection dimension bounded by projection trace')
    if collision:
        require(trace != diagonal_formula, 'collision invalidates diagonal-only formula')
    else:
        require(trace == diagonal_formula, 'distinct routing reduces to diagonal terms')
    return dict(collision=collision, trace=trace, intersection=intersection,
                stacked_rank=D.H.H.rank(left+right), diagonal_formula=diagonal_formula)


def common_frame_control():
    m = 4
    normals = [q for q in range(1, 1 << m) if q.bit_count() % 2]
    caps = [basis(x for x in range(1 << m) if (x&q).bit_count() % 2 == 0) for q in normals]
    def distance(a, b):
        # dim U + dim V - 2 dim(U intersect V), the retained L_U metric.
        return 2*len(basis(a+b))-len(a)-len(b)
    require(all(distance(a, b) == 2 for i, a in enumerate(caps) for b in caps[i+1:]),
            'distinct normal caps have distance two')
    subspaces = {()}
    frontier = {()}
    while frontier:
        following = {basis(a+(x,)) for a in frontier for x in range(1, 1 << m)}-subspaces
        subspaces |= following
        frontier = following
    require(len(subspaces) == 67, 'complete small subspace catalog')
    costs = [sum(distance(cap, u) for cap in caps) for u in subspaces]
    require(min(costs) == len(normals), 'sharp common-frame alignment bill')
    h, v, ambient = 22, 1320, 66
    prefix = 2*v*(ambient-1)
    decoder = 2*v
    require(prefix+decoder == 2*v*ambient, 'common decoder exhausts data rank capacity')
    return dict(small_dimension=m, normals=len(normals), tested_subspace_frames=len(subspaces),
                minimum_one_way_sum=min(costs), selected_dimension=ambient,
                ports_per_group=v, data_prefix_rank_floor_per_group=prefix,
                terminal_alignment_rank_floor_per_group=decoder,
                total_data_rank_floor_per_group=prefix+decoder,
                scope='One common frame for all updated Y streams at entry and exit; '
                      'unchanged outer data cuts and full-volume calls. Arbitrary common '
                      'Clifford frames covered by the triangle proof, catalog is a control only.')


def audit():
    paths = [GRAPH, ROOT/'notes/three-stage-cover-complex.tex', ROOT/'notes/paired-cube-sharing.tex',
             ROOT/'notes/paired-cube-construction.tex', ROOT/'notes/general-clifford-frames.tex']
    return dict(status='No admitted terminal decoder. Routed summaries nearly double; common-frame implementation excluded.',
                selected_complex=source_control(), regular_cover_controls=[regular_cover_control(c) for c in (False, True)],
                common_frame=common_frame_control(),
                source_sha256={p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in paths})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    result = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(result == json.loads(args.check.read_text()), 'saved terminal admission receipt')
    print('Terminal decoder admission checks passed; no improved supplier or kappa.')
