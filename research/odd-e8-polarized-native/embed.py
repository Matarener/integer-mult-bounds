"""Exact minimal I20 embedding of the literal odd-E8 two-cube restriction.

Finite binary-linear algebra certificate only; no Gaussian/native/kappa claim.
Default read-only; --write authors the stable receipt.
"""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
NORMALIZERS_SHA = 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def dot(a, b):
    return (a & b).bit_count() & 1

def basis(rows):
    piv = {}
    for x in rows:
        while x:
            p = x.bit_length()-1
            if p in piv:
                x ^= piv[p]
            else:
                piv[p] = x
                break
    for p in sorted(piv):
        for q in piv:
            if q != p and piv[q] >> p & 1:
                piv[q] ^= piv[p]
    return [piv[p] for p in sorted(piv, reverse=True)]

def pairing_rank(a, b):
    return len(basis(sum(dot(x, y) << j for j, y in enumerate(b)) for x in a))

def combine(b, mask):
    value = 0
    for i, x in enumerate(b):
        if mask >> i & 1:
            value ^= x
    return value

def coordinate_solver(b):
    piv = {}
    for i, value in enumerate(b):
        label = 1 << i
        while value:
            p = value.bit_length()-1
            if p in piv:
                value ^= piv[p][0]
                label ^= piv[p][1]
            else:
                piv[p] = (value, label)
                break
        need(value != 0, 'coordinate basis must be independent')
    def solve(value):
        label = 0
        while value:
            p = value.bit_length()-1
            need(p in piv, 'vector outside declared span')
            value ^= piv[p][0]
            label ^= piv[p][1]
        return label
    return solve

def bilinear(rows, a, b):
    return dot(combine(rows, a), b)

def orthonormal_basis(rows):
    n = len(rows)
    remaining = [1 << i for i in range(n)]
    units, hyperbolic = [], []
    B = lambda a, b: bilinear(rows, a, b)
    while remaining:
        odd = next((i for i, x in enumerate(remaining) if B(x, x)), None)
        if odd is not None:
            x = remaining.pop(odd)
            remaining = [y ^ (x if B(x, y) else 0) for y in remaining]
            units.append(x)
        else:
            pair = next(((i, j) for i in range(len(remaining))
                         for j in range(i+1, len(remaining))
                         if B(remaining[i], remaining[j])), None)
            need(pair is not None, 'completion must be nondegenerate')
            i, j = pair
            e, f = remaining[i], remaining[j]
            remaining = [y ^ (e if B(y, f) else 0) ^ (f if B(y, e) else 0)
                         for k, y in enumerate(remaining) if k not in pair]
            hyperbolic.append((e, f))
    need(units, 'the supplied completion must be nonalternating')
    # I1 perpendicular H is I3: all three listed vectors have norm one
    # and pairwise zero pairing. Reuse one unit for each remaining H.
    for e, f in hyperbolic:
        o = units.pop()
        units += [o ^ e, o ^ f, o ^ e ^ f]
    need(len(units) == n and len(basis(units)) == n, 'orthonormal basis dimension')
    need(all(B(a, b) == int(i == j) for i, a in enumerate(units)
             for j, b in enumerate(units)), 'orthonormal Gram must be I')
    return units

def main():
    normal_raw = (HERE/'inputs/NORMALIZERS.json').read_bytes()
    need(sha256(normal_raw).hexdigest() == NORMALIZERS_SHA, 'normalizer pin')
    data = json.loads(normal_raw)
    channels_raw = (HERE/'POLARIZED-CHANNELS.json.gz').read_bytes()
    inherited = json.loads((HERE/'POLARIZED-CROSS-CUBE.json').read_text())
    need(sha256(channels_raw).hexdigest() == inherited['literal_channels_sha256'], 'channel pin')
    channels = json.loads(gzip.decompress(channels_raw))['channels']
    labels = [p['q'] for p in data['ports']]
    ca = inherited['base_cube_a']['ports']
    cb = inherited['base_cube_b']['ports']
    cc = inherited['fixed_other_cube']['ports']
    ports = sorted((i*112+j)*112+k for i, j, k in product(ca+cb, cc, cc))
    def raw_q(port):
        i, rest = divmod(port, 112*112)
        j, k = divmod(rest, 112)
        return labels[i] | (labels[j] << 9) | (labels[k] << 18)
    qraw = {p: raw_q(p) for p in ports}
    V = basis(qraw.values())
    need(len(ports) == len(set(qraw.values())) == 1024, '1024 distinct raw ports')
    need(len(V) == 12 and pairing_rank(V, V) == 4, 'V12 rank-four form')
    R = basis(combine(V, mask) for mask in range(1 << len(V))
              if all(not dot(combine(V, mask), y) for y in V))
    need(len(R) == 8, 'eight-dimensional radical')
    N = next([V[i] for i in chosen] for chosen in combinations(range(12), 4)
             if pairing_rank([V[i] for i in chosen], [V[i] for i in chosen]) == 4)
    need(len(basis(N+R)) == 12 and any(dot(x, x) for x in N), 'N4 perpendicular R8')
    Wraw = N+R
    solve = coordinate_solver(Wraw)
    # Abstract completion [N4,R8,D8], with B(R_i,D_j)=delta_ij.
    gram = [sum(dot(x, y) << j for j, y in enumerate(N)) for x in N]
    gram += [1 << (12+i) for i in range(8)]
    gram += [1 << (4+i) for i in range(8)]
    need(len(gram) == len(basis(gram)) == 20, 'nondegenerate dimension-20 completion')
    O = orthonormal_basis(gram)
    def embed(raw):
        coordinate = solve(raw)
        return sum(bilinear(gram, coordinate, o) << i for i, o in enumerate(O))
    q20 = {p: embed(qraw[p]) for p in ports}
    need(len(set(q20.values())) == 1024 and len(basis(q20.values())) == 12, 'injective embedding')
    checks = 0
    for p in ports:
        need(dot(q20[p], q20[p]) == 1, 'all literal q20 are odd')
        for q in ports:
            need(dot(qraw[p], qraw[q]) == dot(q20[p], q20[q]), 'all-port exact Gram identity')
            checks += 1
    need(checks == 1024**2, 'all ordered Gram pairs checked')
    groups = defaultdict(list)
    for i, ch in enumerate(channels):
        sb = basis(q20[p] for p, _, _ in ch['source'])
        rb = basis(q20[p] for p, _, _ in ch['reader'])
        need(len(sb) == len(rb) == 8 and pairing_rank(sb, rb) == 0, 'orthogonal eight-spaces')
        need(pairing_rank(sb, sb) == pairing_rank(rb, rb) == 2, 'self-pairing two')
        groups[(tuple(sb), tuple(rb))].append(i)
    need(len(groups) == 4 and sorted(map(len, groups.values())) == [16]*4, 'four space pairs')
    all_source, all_reader = [], []
    group_records = []
    for (sb, rb), ids in sorted(groups.items()):
        sp = sorted(set(p for i in ids for p, _, _ in channels[i]['source']))
        rp = sorted(set(p for i in ids for p, _, _ in channels[i]['reader']))
        need(len(sp) == len(rp) == 128, 'each space-pair has 128 literal source/read fields')
        all_source += sp
        all_reader += rp
        group_records.append({'source_basis20': sb, 'reader_basis20': rb,
                              'channel_ids': ids, 'source_ports': sp, 'reader_ports': rp})
    need(len(all_source) == len(set(all_source)) == 512, 'source groups partition b cube')
    need(len(all_reader) == len(set(all_reader)) == 512, 'reader groups partition a cube')
    # A quotient certificate: V/rad(V) is nonalternating dimension four.
    ng = gram[:4]
    NO = orthonormal_basis(ng)
    quotient = {p: sum(bilinear(ng, solve(qraw[p]) & 15, o) << i
                       for i, o in enumerate(NO)) for p in ports}
    quotient_counts = Counter(quotient.values())
    need(quotient_counts == {i: 128 for i in range(16) if i.bit_count() & 1}, 'eight balanced quotient types')
    cliques = []
    for weight in (1, 3):
        types = [i for i in range(16) if i.bit_count() == weight]
        buckets = [[p for p in ports if quotient[p] == t] for t in types]
        for i in range(128):
            clique = [bucket[i] for bucket in buckets]
            qb = [q20[p] for p in clique]
            need(len(basis(qb)) == pairing_rank(qb, qb) == 4, 'literal orthonormal four-clique')
            cliques.append(clique)
    # Two nonorthogonal quotient types give a forced identity submatrix of size 256.
    independent = [p for p in ports if quotient[p] in (1, 7)]
    need(len(independent) == 256 and all(dot(q20[p], q20[q]) for p in independent for q in independent),
         '256-port forbidden-offdiagonal lower bound')
    result = {'schema': 'odd-e8-two-cube-minimal-I20-v1',
       'normalizer_sha256': NORMALIZERS_SHA,
       'polarized_channels_sha256': sha256(channels_raw).hexdigest(),
       'raw_ambient': 27, 'span_dimension': 12, 'pairing_rank': 4,
       'radical_dimension': 8, 'minimal_nondegenerate_ambient': 20,
       'completion_decomposition': 'N4 perpendicular H^8, N4 nonalternating',
       'raw_non_degenerate_basis': N, 'raw_radical_basis': R,
       'raw_coordinate_basis': Wraw, 'completion_Gram_rows': gram,
       'orthonormal_completion_basis': O,
       'raw_basis_images20': [embed(x) for x in Wraw],
       'ports': [{'port': p, 'q27': qraw[p], 'coordinates12': solve(qraw[p]),
                  'q20': q20[p], 'quotient4': quotient[p]} for p in ports],
       'ordered_Gram_checks': checks,
       'orthogonal_eight_space_pairs': group_records,
       'quotient_orthonormal_basis4': NO,
       'quotient_type_counts': dict(sorted(quotient_counts.items())),
       'clique_fitting_matrix': {'cliques': cliques, 'rank': 256,
           'rank_lower_bound_independent_ports': independent,
           'source_copy_profile': {'4': 256}, 'copy_mass_per_port': '1',
           'compatible_physical_native_core_proved': False},
       'physical_program_emitted': False, 'complete_invoice_proved': False, 'kappa_claim': False}
    target = HERE/'EMBEDDING.json'
    encoded = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if '--write' in sys.argv:
        target.write_text(encoded)
    else:
        need(target.read_text() == encoded, 'stable embedding receipt differs')
    print(json.dumps({'status': 'PASS', 'ports': 1024, 'span': 12, 'pairing_rank': 4,
          'radical': 8, 'minimal_ambient': 20, 'Gram_pairs': checks,
          'orthogonal8_pairs': len(groups), 'fitting_rank_exact': 256,
          'native_word': False}, sort_keys=True))

if __name__ == '__main__':
    main()
