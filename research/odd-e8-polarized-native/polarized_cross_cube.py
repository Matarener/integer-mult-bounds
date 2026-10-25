"""Polarized orthogonal rectangles for an unsolved #5439 cross-cube piece.

This proves no Gaussian implementation, chart schedule, or kappa bound.
Only standard-library exact rational and binary-linear algebra is used.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
PIN = 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def basis(rows):
    piv = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
    return list(piv.values())

def dot(x, y):
    return (x & y).bit_count() & 1

def pairing_rank(a, b):
    return len(basis(sum(dot(x, y) << j for j, y in enumerate(b)) for x in a))

def rank(mat):
    a = [[F(x) for x in row] for row in mat]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[p], a[r] = a[r], a[p]
        z = a[r][j]
        a[r] = [x / z for x in a[r]]
        for i in range(r+1, len(a)):
            z = a[i][j]
            if z:
                a[i] = [x-z*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r

def qtuple(labels, triple):
    return sum(labels[t] << (9*i) for i, t in enumerate(triple))

def radical(b):
    # At most nine generators in this fixture; enumerate coefficient masks.
    vectors = []
    for mask in range(1 << len(b)):
        x = 0
        for j, y in enumerate(b):
            if mask >> j & 1:
                x ^= y
        if all(not dot(x, y) for y in b):
            vectors.append(x)
    return basis(vectors)

def main():
    raw = (HERE/'inputs/NORMALIZERS.json').read_bytes()
    need(sha256(raw).hexdigest() == PIN, 'normalizer source pin')
    data = json.loads(raw)
    roots = list(zip(*data['mode_columns']))
    labels = [p['q'] for p in data['ports']]
    cubes = {}
    for i, v in enumerate(roots):
        cubes.setdefault(tuple(j for j, x in enumerate(v) if x), []).append(i)
    cubes = sorted(cubes.items())
    need(len(cubes) == 14 and all(len(x[1]) == 8 for x in cubes), 'literal cubes')
    aa, bb = next((a, b) for a in range(14) for b in range(a+1, 14)
                  if len(set(cubes[a][0]) & set(cubes[b][0])) == 2)
    ca, cb = cubes[aa][1], cubes[bb][1]
    shared = sorted(set(cubes[aa][0]) & set(cubes[bb][0]))
    # The two inactive factors are fixed to the first literal cube.
    cc = cubes[0][1]
    def gram(i, j):
        return sum(x*y for x, y in zip(roots[i], roots[j]))
    Cab = [[F(gram(i, j), 4) for j in cb] for i in ca]
    B = [[F(gram(i, j), 4) for j in cc] for i in cc]
    K = [[int(i == j)-B[i][j] for j in range(8)] for i in range(8)]
    def parity(i):
        v, support = roots[cc[i]], cubes[0][0]
        first = v[support[0]]
        return sum(v[j]*first < 0 for j in support[1:]) & 1
    selectors = list(product(range(8), repeat=2))
    T = [[K[a][c]*K[b][d] for c, d in selectors] for a, b in selectors]
    P = [[(int(i == j)-T[i][j])/2 for j in range(64)] for i in range(64)]
    J = [i for i, (a, _) in enumerate(selectors) if parity(a) == 0]
    need(len(J) == 32, 'half-selector chart')
    U = [[int(i == j)-T[i][j] for j in J] for i in range(64)]
    V = [[(int(j == k)-T[j][k])/2 for k in range(64)] for j in J]
    need(all(sum(U[i][j]*V[j][k] for j in range(32)) == P[i][k]
             for i in range(64) for k in range(64)), 'P=UV exact')
    need(all(sum(T[i][j]*T[j][k] for j in range(64)) == int(i == k)
             for i in range(64) for k in range(64)), 'T involution')
    need(rank(Cab) == 2 and rank(P) == 32, 'literal rank factors')
    def polar(i, branch):
        value = roots[i][shared[0]]+branch*roots[i][shared[1]]
        need(value in (-2, 0, 2), 'polarized root entry')
        return value//2
    need(all(Cab[i][j] == sum(F(polar(ca[i], branch)*polar(cb[j], branch), 2)
                             for branch in (-1, 1))
             for i in range(8) for j in range(8)), 'polarized rank-two root factorization')
    # Exhaustively check all 512 x 512 entries against the original F3 polynomial.
    count = 0
    for i, j, a, b in product(range(8), range(8), range(64), range(64)):
        a2, a3 = selectors[a]
        b2, b3 = selectors[b]
        f3 = Cab[i][j]*(int(a2 == b2)*B[a3][b3]
              + B[a2][b2]*int(a3 == b3)-B[a2][b2]*B[a3][b3])/2
        need(-f3 == -Cab[i][j]*P[a][b], 'cross-cube H3=-Cab tensor P')
        if f3:
            qread = qtuple(labels, (ca[i], cc[a2], cc[a3]))
            qsource = qtuple(labels, (cb[j], cc[b2], cc[b3]))
            need(not dot(qread, qsource), 'literal orthogonal H support mask')
        count += 1
    features = []
    channels = []
    hist = Counter()
    # All 64 rectangles are individually orthogonal in the literal binary labels.
    rectangle_pairs = 0
    for branch, j in product((-1, 1), range(32)):
        read = [(i, a) for i in range(8) for a in range(64)
                if polar(ca[i], branch)*U[a][j]]
        src = [(i, b) for i in range(8) for b in range(64)
               if polar(cb[i], branch)*V[j][b]]
        read_labels = [qtuple(labels, (ca[i], cc[selectors[a][0]], cc[selectors[a][1]]))
                       for i, a in read]
        source_labels = [qtuple(labels, (cb[i], cc[selectors[b][0]], cc[selectors[b][1]]))
                         for i, b in src]
        need(len(read) == len(src) == 68, 'polarized rectangle support')
        need(all(not dot(x, y) for x in read_labels for y in source_labels),
             'literal all-port orthogonal rectangle')
        rectangle_pairs += len(read_labels)*len(source_labels)
        rb, sb = basis(read_labels), basis(source_labels)
        rr, sr = radical(rb), radical(sb)
        joint = basis(rb+sb)
        common_rad = len(rr)+len(sr)-len(basis(rr+sr))
        radicals_annihilate_joint = all(not dot(x, y) for x in rr+sr for y in joint)
        key = (len(read), len(src), len(rb), len(sb), pairing_rank(rb, sb),
               pairing_rank(rb, rb), pairing_rank(sb, sb), len(joint),
               pairing_rank(joint, joint), common_rad)
        hist[key] += 1
        features.append({'polarization': branch, 'half_selector': J[j],
                         'read_ports': len(read), 'source_ports': len(src),
                         'reader_span_rank': len(rb), 'source_span_rank': len(sb),
                         'cross_pairing_rank': pairing_rank(rb, sb),
                         'reader_self_pairing_rank': pairing_rank(rb, rb),
                         'source_self_pairing_rank': pairing_rank(sb, sb),
                         'joint_span_rank': len(joint),
                         'joint_pairing_rank': pairing_rank(joint, joint),
                         'common_radical_rank': common_rad,
                         'individual_radicals_annihilate_joint': radicals_annihilate_joint,
                         'reader_radical_basis': sorted(rr),
                         'source_radical_basis': sorted(sr)})
        def packed(index, factor):
            return [index, factor.numerator, factor.denominator]
        def port_index(a, b, c):
            return (a*112+b)*112+c
        channels.append({'polarization': branch, 'half_selector': J[j],
            'reader': [packed(port_index(ca[i], cc[selectors[a][0]], cc[selectors[a][1]]),
                              F(polar(ca[i], branch))*U[a][j]) for i, a in read],
            'source': [packed(port_index(cb[i], cc[selectors[b][0]], cc[selectors[b][1]]),
                              -F(polar(cb[i], branch))*V[j][b]/2) for i, b in src]})
    # Off-diagonal reciprocal pair is [[0,H_ab],[H_ab^t,0]].
    channel_bytes = gzip.compress((json.dumps({'direction': 'a_reads_b',
        'port_index': '(i1*112+i2)*112+i3',
        'term': '[global-port-index, rational-numerator, rational-denominator]',
        'equation': 'H_ab=sum reader_column*source_row', 'channels': channels},
        sort_keys=True, separators=(',', ':'))+'\n').encode(), mtime=0)
    result = {'schema': 'odd-e8-polarized-cross-cube-scalar-abi-v1',
      'source_sha256': PIN, 'predecessor_pr': 5439,
      'predecessor_head': 'e6d50e7ebd0bb1fd4f388930df78df696e56b404',
      'base_cube_a': {'support': cubes[aa][0], 'ports': ca},
      'base_cube_b': {'support': cubes[bb][0], 'ports': cb},
      'fixed_other_cube': {'support': cubes[0][0], 'ports': cc},
      'shared_root_coordinates': shared,
      'port_count_two_cubes': 1024, 'directed_cross_block_rank': 64,
      'reciprocal_cross_block_rank': 128, 'channels_per_direction': 64,
      'exhaustive_tensor_entries': count,
      'literal_rectangle_pairings_checked': rectangle_pairs,
      'feature_profiles': [{'read_ports': k[0], 'source_ports': k[1],
          'reader_span': k[2], 'source_span': k[3], 'cross_pairing': k[4],
          'reader_self_pairing': k[5], 'source_self_pairing': k[6],
          'joint_span': k[7], 'joint_pairing': k[8], 'common_radical': k[9], 'count': n}
          for k, n in sorted(hist.items())],
      'features': features,
      'literal_channels_sha256': sha256(channel_bytes).hexdigest(),
      'exact_equations': ['K=I-B', 'T=K tensor K', 'P=(I-T)/2',
        'P=UV with U_j=e_j-T e_j, V_j=(e_j^t-e_j^t T)/2, j in even(first-selector)',
        'w_(+,i)=(M_i,u+M_i,v)/2; w_(-,i)=(M_i,u-M_i,v)/2',
        'C_ab=(w_(+,a) w_(+,b)^t+w_(-,a) w_(-,b)^t)/2',
        'H_ab=-C_ab tensor P=-sum_(branch,j) (w_(branch,a) tensor U_j) (w_(branch,b)^t tensor V_j)/2'],
      'physical_program_emitted': False, 'dirty_return_proved': False,
      'complete_invoice_proved': False, 'kappa_claim': False}
    target = HERE/'POLARIZED-CROSS-CUBE.json'
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if '--write' in __import__('sys').argv:
        target.write_text(encoded)
        (HERE/'POLARIZED-CHANNELS.json.gz').write_bytes(channel_bytes)
    else:
        saved = json.loads(target.read_text())
        scientific = lambda value: {k: v for k, v in value.items()
                                    if k != 'literal_channels_sha256'}
        need(scientific(saved) == json.loads(json.dumps(scientific(result))),
             'stable scientific receipt differs')
        saved_channels = (HERE/'POLARIZED-CHANNELS.json.gz').read_bytes()
        need(json.loads(gzip.decompress(saved_channels)) ==
             json.loads(gzip.decompress(channel_bytes)), 'literal channel payload differs')
        # Authenticate retained source bytes separately from regeneration equality.
        need(sha256(saved_channels).hexdigest() == saved['literal_channels_sha256'],
             'retained channel source digest differs')
    print(json.dumps({'status': 'PASS', 'checked_tensor_entries': count,
                      'channels_per_direction': 64, 'rectangle_pairings': rectangle_pairs,
                      'feature_profiles': result['feature_profiles'],
                      'physical_program_emitted': False}, sort_keys=True))

if __name__ == '__main__':
    main()
