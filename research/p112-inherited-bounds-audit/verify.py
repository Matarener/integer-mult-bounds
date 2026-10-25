#!/usr/bin/env python3
"""Independent finite audit of inherited support, incidence and chamber facts.

Chris R / Clear1nsight, substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported; theorem credit stays with its authors.
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
import model as m  # noqa: E402

MANIFEST_SHA = '70ad6c294240e166689287973ce5e0c8cf8c2d3936e7aab17e62175fafb937ee'
TABLE = 'research/one-sided-six-multisets/data/data.txt'
GEOMETRY = 'research/p112-root-simplex-exclusion/geometry.py'


def unique(pairs):
    m.require(len(pairs) == len({key for key, _ in pairs}), 'duplicate JSON key')
    return dict(pairs)


def load(raw):
    return json.loads(raw, object_pairs_hook=unique)


def authenticate(root=ROOT, package=HERE):
    raw = (package / 'SOURCES.json').read_bytes()
    m.require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest identity')
    payloads = {}
    for row in load(raw)['files']:
        if row['usage'] != 'input':
            continue
        path = root / row['path']
        m.require(path.resolve().is_relative_to(root.resolve()), 'input escaped root')
        m.require(not any(p.is_symlink() for p in [path, *path.parents]), 'input symlink')
        raw = path.read_bytes()
        m.require(len(raw) <= 2_000_000, 'source size bound')
        m.require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
        blob = b'blob ' + str(len(raw)).encode() + b'\0' + raw
        m.require(hashlib.sha1(blob).hexdigest() == row['git_blob'], 'source Git blob')
        payloads[row['path']] = raw
    return payloads


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def global_census(labels, live_mask):
    ker = m.kernels(labels, [1 << j for j in range(9)])
    result = {}
    for d, expected, cap in [(5, 3_309_747, 12), (6, 788_035, 20)]:
        hist, live_hist = Counter(), Counter()
        witness = None
        for mask in m.masks(ker, m.annihilators(9, d)):
            size, live = mask.bit_count(), (mask & live_mask).bit_count()
            hist[size] += 1
            live_hist[live] += 1
            if live == cap and witness is None:
                witness = [x for i, x in enumerate(labels) if mask & live_mask & (1 << i)]
        m.require(sum(hist.values()) == expected and max(hist) == max(live_hist) == cap,
                  'complete global capacity census')
        m.require(witness is not None and len(m.basis(witness)) == d, 'sharp live support')
        result[str(d)] = {'spaces': expected, 'full_maximum': cap, 'live_maximum': cap,
                          'full_histogram': {str(k): n for k, n in sorted(hist.items())},
                          'live_histogram': {str(k): n for k, n in sorted(live_hist.items())},
                          'live_witness': witness}
    return result


def quadratic_model(labels):
    gram = [[m.dot(a, b) // 4 for b in m.SIMPLE] for a in m.SIMPLE]
    q = [((x.bit_count() + sum(gram[i][j] * (x >> i & 1) * (x >> j & 1)
                              for i, j in combinations(range(8), 2))) % 2) for x in range(256)]
    polar = [[q[x ^ y] ^ q[x] ^ q[y] for y in range(256)] for x in range(256)]
    rows = [sum(polar[1 << i][1 << j] << j for j in range(8)) for i in range(8)]
    m.require(len(m.basis(rows, 8)) == 8, 'nondegenerate ambient polar form')
    m.require({x >> 1 for x in labels} == {x for x in range(256) if q[x]}, 'quadratic root model')
    m.require(sum(1 - 2 * x for x in q) == 16, 'positive ambient Gauss sign')
    for x in range(256):
        for y in range(256):
            m.require(polar[x][y] == sum(gram[i][j] * (x >> i & 1) * (y >> j & 1)
                                       for i in range(8) for j in range(8)) % 2,
                      'quadratic polarization')
    return q, polar


def fiber_binding(labels, fiber, q, polar):
    selected = [x for i, x in enumerate(labels) if fiber >> i & 1]
    base = m.basis(selected)
    m.require(len(base) == 7, 'A2 fiber span dimension')
    affine = [x >> 1 for x in m.span(base) if x & 1]
    m.require(len(affine) == 64, 'fiber affine six-space')
    directions = m.basis([x ^ affine[0] for x in affine], 8)
    rows = [sum(polar[x][y] << j for j, y in enumerate(directions)) for x in directions]
    m.require(len(m.basis(rows, 6)) == 6 and sum(1 - 2 * q[x] for x in affine) == 8,
              'positive nondegenerate fiber quadratic restriction')
    ker = m.kernels(labels, base)
    m.require(ker[0].bit_count() == 28 and (ker[0] & ~fiber).bit_count() == 1,
              'fiber closure and unique extra root')
    return ker


def fiber_census(labels, fibers, live_mask, q, polar):
    rows5, rows6 = list(m.annihilators(7, 5)), list(m.annihilators(7, 6))
    m.require(len(rows5) == 2667 and len(rows6) == 127, 'fiber-space domains')
    expected6 = {(0, 0): 1, (12, 11): 27, (12, 12): 36, (16, 15): 36, (16, 16): 27}
    records, total5, total6, witnesses = [], Counter(), Counter(), {}
    for fiber in fibers:
        ker = fiber_binding(labels, fiber, q, polar)
        hist5, hist6 = Counter(), Counter()
        for d, rows, hist, cap in [(5, rows5, hist5, 20), (6, rows6, hist6, 32)]:
            for mask in m.masks(ker, rows):
                a, b = mask.bit_count(), (mask & fiber).bit_count()
                hist[a, b] += 1
                if a + b == cap and mask & ~live_mask == 0 and str(d) not in witnesses:
                    witnesses[str(d)] = {'labels': [x for i, x in enumerate(labels) if mask >> i & 1],
                                         'fiber_labels': [x for i, x in enumerate(labels) if fiber >> i & 1]}
            m.require(max(a for a, _ in hist) == (10 if d == 5 else 16), 'inside root capacity')
            m.require(max(a + b for a, b in hist) == cap, 'inside joint incidence')
        m.require(dict(hist6) == expected6, 'every fiber hyperplane/equality table')
        total5.update(hist5)
        total6.update(hist6)
        records.append([str(fiber), sorted((a, b, n) for (a, b), n in hist5.items()),
                        sorted((a, b, n) for (a, b), n in hist6.items())])
    m.require(set(witnesses) == {'5', '6'}, 'both sharp joint bounds attained on live roots')
    for d, witness in witnesses.items():
        m.require(len(m.basis(witness['labels'])) == int(d), 'joint witness binary rank')
    return {'fibers': len(fibers), 'rank5_space_tests': sum(total5.values()),
            'rank6_space_tests': sum(total6.values()), 'rank5_inside_root_maximum': 10,
            'rank6_inside_root_maximum': 16, 'joint_rank5_bound': 20, 'joint_rank6_bound': 32,
            'outside_rank6_bound': 30, 'per_fiber_digest': digest(records),
            'rank5_joint_histogram': {f'{a},{b}': n for (a, b), n in sorted(total5.items())},
            'rank6_joint_histogram': {f'{a},{b}': n for (a, b), n in sorted(total6.items())},
            'live_witnesses': witnesses}


def chamber(roots, coordinates):
    signed = set(roots) | {tuple(-x for x in r) for r in roots}
    m.require(all(alpha in signed for alpha in m.SIMPLE), 'simple roots belong to full root set')
    for alpha in m.SIMPLE:
        m.require(m.dot(alpha, alpha) == 8, 'simple-root norm')
        for root in signed:
            p = m.dot(alpha, root)
            m.require(p % 4 == 0, 'reflection integrality')
            m.require(tuple(x - p // 4 * y for x, y in zip(root, alpha)) in signed,
                      'signed root reflection closure')
    rho = m.solve(m.SIMPLE, [[1] * 8])[0]
    m.require(all(m.dot(rho, a) == 1 for a in m.SIMPLE), 'strict chamber functional')
    faces = [[r for r, c in zip(roots, coordinates) if all(c[j] == 0 for j in range(8)
               if not mask >> j & 1)] for mask in range(256)]
    m.require(max(len(faces[x]) for x in range(256) if x.bit_count() <= 5) == 20,
              'rank-at-most-five face cap')
    m.require(max(len(faces[x]) for x in range(256) if x.bit_count() <= 6) == 36,
              'rank-at-most-six face cap')
    seven = [len(faces[255 ^ (1 << j)]) for j in range(8)]
    m.require(seven == [42, 28, 22, 14, 16, 23, 37, 63], 'all seven-node faces')
    types = []
    for mask in range(256):
        if mask.bit_count() != 6 or len(faces[mask]) < 28:
            continue
        normal = [r for r in roots if all(m.dot(r, z) == 0 for z in faces[mask])]
        kind = (len(faces[mask]), len(normal), abs(m.dot(normal[0], normal[1])))
        m.require(kind in [(30, 2, 0), (36, 3, 4)], 'normal-plane finite types')
        types.append({'face': mask, 'root_lines': kind[0], 'normal_roots': normal})
    m.require(len(types) == 2, 'complete qualifying six-node faces')
    normal = [r for r in roots if all(m.dot(r, z) == 0 for z in faces[127])]
    m.require(len(normal) == 1, 'E7 root normal')
    return {'signed_root_reflection_tests': 1920, 'rho': [str(x) for x in rho],
            'rank5_face_maximum': 20, 'rank6_face_maximum': 36,
            'seven_node_counts': seven, 'six_node_types': types, 'E7_normal': normal[0]}


def compute(payloads):
    roots, labels, coords, live = m.reconstruct(payloads[TABLE], payloads[GEOMETRY])
    global_result = global_census(labels, live)
    q, polar = quadratic_model(labels)
    planes, fibers = m.all_a2(roots)
    off = [sum(1 << i for i, r in enumerate(roots) if live >> i & 1 and m.dot(h, r))
           for h in roots]
    distances = Counter(x.bit_count() for x in off)
    m.require(dict(distances) == {53: 112, 56: 8}, 'root-normal live support sizes')
    a2_unions, d6_unions = Counter(), Counter()
    for plane in planes:
        a, b = plane[:2]
        a2_unions[(off[a] | off[b]).bit_count()] += 1
    m.require(dict(a2_unions) == {78: 896, 80: 224}, 'actual A2 union lower bound')
    for a, b in combinations(range(120), 2):
        if m.dot(roots[a], roots[b]) == 0:
            d6_unions[(off[a] | off[b]).bit_count()] += 1
    m.require(dict(d6_unions) == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28},
              'actual orthogonal normal-plane union inventory')
    return {'schema': 'p112-inherited-bounds-audit/v1', 'global': global_result,
            'a2': fiber_census(labels, fibers, live, q, polar),
            'A2_live_union_histogram': {str(k): n for k, n in sorted(a2_unions.items())},
            'D6_live_union_histogram': {str(k): n for k, n in sorted(d6_unions.items())},
            'root_normal_live_support_histogram': {str(k): n for k, n in sorted(distances.items())},
            'chamber': chamber(roots, coords),
            'scope': 'Exact declared model and written scalar-extension proof; no full C5 or supplier.'}


def main():
    m.require(not sys.argv[1:], 'no arguments accepted')
    observed = compute(authenticate())
    expected = load((HERE / 'RESULT.json').read_bytes())
    m.require(json.dumps(observed, sort_keys=True) == json.dumps(expected, sort_keys=True),
              'audit result receipt mismatch')
    print('PASS_INHERITED_BOUNDS_AUDIT global4097782 fibers3360 inside5=8961120 '
          'inside6=426720 signed_reflections1920 bounds12/20/20/32')


if __name__ == '__main__':
    main()
