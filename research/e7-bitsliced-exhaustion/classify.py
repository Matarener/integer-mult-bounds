#!/usr/bin/env python3
"""Classify minimum E7 supports. Ali Romman with OpenAI Codex. Apache-2.0."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from runpy import run_path
import json

HERE = Path(__file__).resolve().parent / 'source'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def geometry():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for row in manifest['external_inputs']:
        need(sha256((HERE / row['local_path']).read_bytes()).hexdigest()
             == row['sha256'], 'retained source changed')
    return run_path(str(HERE / 'vendor/PR5238.py'), run_name='retained_geometry')


def rank(rows):
    basis = {}
    for row in rows:
        row = list(map(F, row))
        for p, b in basis.items():
            c = row[p]
            if c:
                row = [x-c*y for x, y in zip(row, b)]
        p = next((i for i, x in enumerate(row) if x), None)
        if p is not None:
            c = row[p]
            basis[p] = [x/c for x in row]
    return len(basis)


def minimum_supports(basis):
    engine = run_path(str(HERE.parent / 'binary.py'))
    words = set(engine['low_weight_words'](basis, 63, 12))
    need(0 in words, 'zero word retained')
    supports = words - {0}
    need(len(supports) == 1638 and all(word.bit_count() == 12 for word in supports),
         'complete minimum census')
    return supports


def reflections(roots, frames, dot):
    lookup = {r: i for i, r in enumerate(roots)}
    frame_set = set(frames)
    out = []
    for normal in roots:
        p = []
        for r in roots:
            inner = dot(r, normal)
            need(inner % 4 == 0, 'integral reflection')
            image = tuple(r[i]-inner//4*normal[i] for i in range(8))
            if next(x for x in image if x) < 0:
                image = tuple(-x for x in image)
            need(image in lookup, 'root reflection closure')
            p.append(lookup[image])
        need(sorted(p) == list(range(63)), 'root permutation')
        need(all(tuple(sorted(p[j] for j in frame)) in frame_set
                 for frame in frames), 'frame reflection closure')
        out.append(tuple(p))
    return out


def transport(mask, permutation):
    image = 0
    while mask:
        bit = mask & -mask
        image |= 1 << permutation[bit.bit_length()-1]
        mask ^= bit
    return image


def orbit(mask, permutations):
    seen, queue = {mask}, [mask]
    for current in queue:
        for p in permutations:
            image = transport(current, p)
            if image not in seen:
                seen.add(image)
                queue.append(image)
    return seen


def form_a(x):
    return sum(x[i]*x[i] for i in range(4))-sum(x[i]*x[i] for i in range(4, 8))


def form_b(x):
    return (x[0]-x[1])*(x[2]-x[3])


def quadratic_matrix(form):
    vectors = []
    for i in (1, 2, 3, 5, 6, 7):
        x = [0]*8
        x[i] = 1
        vectors.append(x)
    vectors.append([1, 0, 0, 0, -1, 0, 0, 0])
    matrix = [[F(form([x+y for x, y in zip(a, b)])-form(a)-form(b), 2)
               for b in vectors] for a in vectors]
    need(sum(matrix[i][i] for i in range(6))+matrix[6][6]/2 == 0,
         'restricted trace zero')
    return matrix


def supported_rank(frames, support):
    return rank([[int(j in frame) for j in support] for frame in frames])


def check_relation(frames, values):
    need(sum(x != 0 for x in values) == 12, 'twelve nonzero values')
    need(all(sum(values[j] for j in frame) == 0 for frame in frames),
         'literal rational frame sums')


def partition(supports, orbits):
    need(not orbits[0] & orbits[1], 'disjoint equality orbits')
    need(orbits[0] | orbits[1] == supports, 'every minimum support classified')


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('invalid control accepted')


def check():
    g = geometry()
    roots = g['intrinsic_e7']()
    g['validate_domain'](roots)
    need(roots == tuple(r for r in g['e8_lines']() if g['dot'](r, g['PIVOT']) == 0),
         'ambient and intrinsic domains agree')
    need(g['check_root_transitivity']() == 120, 'every ambient root slice')
    frames = g['orthogonal_frames'](roots)
    rows = tuple(sum(1 << j for j in frame) for frame in frames)
    basis, free = g['binary_kernel'](rows)
    supports = minimum_supports(basis)
    permutations = reflections(roots, frames, g['dot'])
    orbits, records, controls = [], [], 0
    for name, form, size, qrank, scale in (
            ('diagonal', form_a, 630, 6, 8), ('product', form_b, 1008, 2, 4)):
        values = tuple(form(r) for r in roots)
        check_relation(frames, values)
        need(set(values) == {-scale, 0, scale}, 'constant nonzero magnitudes')
        need(values.count(scale) == values.count(-scale) == 6, 'six values of each sign')
        support = [j for j, x in enumerate(values) if x]
        mask = sum(1 << j for j in support)
        current = orbit(mask, permutations)
        need(len(current) == size and current <= supports, 'complete attained orbit')
        need(supported_rank(frames, support) == 11, 'one-dimensional rational lift')
        need(rank(quadratic_matrix(form)) == qrank, 'quadratic rank')
        for omitted in support:
            need(supported_rank(frames, [j for j in support if j != omitted]) == 11,
                 'every single omission has zero kernel')
            controls += 1
        changed = list(values)
        changed[support[0]] += 1
        reject(lambda: check_relation(frames, changed))
        controls += 1
        orbits.append(current)
        records.append(dict(type=name, supports=size, representative_support=support,
                            representative_values=list(values), quadratic_rank=qrank,
                            restricted_frame_rank=11, rational_lift_dimension=1,
                            orbit_sha256=sha256(json.dumps(sorted(current)).encode()).hexdigest()))
    partition(supports, orbits)
    reject(lambda: partition(supports-{next(iter(supports))}, orbits))
    reject(lambda: partition(supports, [orbits[0], orbits[1] | orbits[0]]))
    controls += 2
    return dict(status='PASS_E7_MINIMUM_SUPPORT_CLASSIFICATION', root_lines=63,
                frames=135, binary_rank=36, binary_dimension=27,
                nonzero_codewords=(1 << 27)-1, minimum_support=12,
                minimum_supports=len(supports), reflection_generators=len(permutations),
                ambient_root_slices=120, characteristic='zero', orbits=records,
                rejecting_or_omission_controls=controls)


def main():
    result = check()
    need(result == json.loads((HERE / 'RESULT.json').read_text()), 'fixed result receipt')
    print(result['status'])
    print('1638 minimum supports = 630 rank-six + 1008 rank-two; one scalar family per support')


if __name__ == '__main__':
    main()
