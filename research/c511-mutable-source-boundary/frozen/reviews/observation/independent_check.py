#!/usr/bin/env python3
"""Independent exact C511 rolling observation reconstruction, no producer imports.

Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
from collections import deque
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/Users/ross/git/math')
OLD = BASE / '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z/bit-native-caller'
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
FULL = BASE / 'integer-mult-bounds/research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
CODE = BASE / '.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier/recursive/BIT-THREE-COPY-INPUT-WORD.json.gz'
PIN = OLD / 'MUTABLE-SOURCE-FIVE.json'
BOUNDARY = OLD / 'MUTABLE-ROLLING-BOUNDARY.json'
QUOTIENT = OLD / 'MUTABLE-ROLLING-QUOTIENT.json'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(value):
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def mv(a, v):
    return tuple(sum(x * y for x, y in zip(row, v)) % 101 for row in a)


def modular(a):
    return [[x.numerator * pow(x.denominator, -1, 101) % 101 for x in row] for row in a]


def bits(row):
    while row:
        bit = row & -row
        yield bit.bit_length() - 1
        row ^= bit


def binary_product(a, b):
    out = []
    for row in a:
        value = 0
        for j in bits(row):
            value ^= b[j]
        out.append(value)
    return out


def binary_power(a, n):
    result = [1 << i for i in range(len(a))]
    while n:
        if n & 1:
            result = binary_product(result, a)
        a = binary_product(a, a)
        n >>= 1
    return result


def rank(rows):
    # Low-bit pivots, deliberately distinct from the saved high-bit echelon engine.
    pivots = {}
    for row in rows:
        while row:
            bit = row & -row
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def routes(raw, full, pin):
    roots = full['lines']
    maps = {0: eye(8)}
    queue = deque([0])
    while queue:
        parent = queue.popleft()
        for child, root in enumerate(roots):
            dot = sum(x * y for x, y in zip(roots[parent], root))
            if child in maps or abs(dot) != 2:
                continue
            sign = 1 if dot == 2 else -1
            d = [Q(x - sign * y) for x, y in zip(roots[parent], root)]
            norm = sum(x * x for x in d)
            # Rank-one Householder update, without the producer's dense reflection product.
            projection = [sum(d[k] * maps[parent][k][j] for k in range(8)) for j in range(8)]
            maps[child] = [[maps[parent][i][j] - 2 * d[i] * projection[j] / norm
                            for j in range(8)] for i in range(8)]
            queue.append(child)
    need(len(maps) == 120, 'all upstream BFS root routes')
    rhos, projectors, hashes = [], [], []
    for p, label in enumerate(raw['ports_geom']):
        g = maps[label]
        q = raw['lines'][p]
        proj = [[Q(x * y, 4) for y in q] for x in q]
        a = [row[1:] for row in g]
        rho = [proj[i] + a[i] for i in range(8)]
        rho += [[a[i][j] for i in range(8)] + [Q(0)] * 7 for j in range(7)]
        h = digest([[str(x) for x in row] for row in rho])
        need(h == pin['actual_native_geometry']['ports'][p]['rho_sha256'], 'actual rho exact bytes')
        need(matmul(rho, rho) == eye(15), 'actual rho involution')
        rhos.append(rho)
        projectors.append(proj)
        hashes.append(h)
    return rhos, projectors, hashes


# Free noncommutative polynomials; only adjacent N*N is reduced.
def multiply(a, b):
    answer = set()
    for x in a:
        for y in b:
            word = []
            for letter in x + y:
                if letter == 'N' and word and word[-1] == 'N':
                    word.pop()
                else:
                    word.append(letter)
            word = tuple(word)
            answer.symmetric_difference_update({word})
    return frozenset(answer)


def multiply_blocks(a, b):
    return [[multiply(a[i][0], b[0][j]) ^ multiply(a[i][1], b[1][j])
             for j in range(2)] for i in range(2)]


def formal_residual(saved):
    one, zero = frozenset({()}), frozenset()
    n = frozenset({('N',)})
    c = [frozenset({('C' + str(j),)}) for j in range(3)]
    lower = lambda j: [[one, zero], [multiply(n, c[j]), one]]
    upper = [[one, multiply(n, c[1])], [zero, one]]
    result = multiply_blocks(lower(2), multiply_blocks(upper, lower(0)))
    a1 = multiply(n, multiply(c[1], n))
    a2 = multiply(n, multiply(c[2], n))
    expected = [[one ^ multiply(a1, c[0]), multiply(n, c[1])],
                [multiply(n, c[2] ^ multiply(c[2], multiply(a1, c[0])) ^ c[0]),
                 one ^ multiply(a2, c[1])]]
    need(result == expected, 'free noncommutative three-call expansion')
    phi = multiply(n, result[0][0])
    need(phi == n ^ multiply(c[1], multiply(n, c[0])), 'Phi=N+C1*N*C0')
    token = {0: 'N', 1: 'C0', 511: 'C1', 1021: 'C2'}
    decoded = [[frozenset(tuple(token[x] for x in word) for word in item)
                for item in row] for row in saved['normalized_three_call_residual']]
    need(result == decoded, 'all saved residual coefficients')
    return [[sorted(map(list, entry)) for entry in row] for row in result]


def main():
    pins = {
        RAW: 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
        FULL: '1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55',
        CODE: 'ac8a6dcd5957f49eefd6fc945332b1c31afa26c48fc301d37bfb1338beea6847',
        PIN: 'ccd6d8386223878c3a34307715ebf7236de25eeabbeaca36f9fd77d0eb1fda95'}
    sources = {str(p): sha256(p.read_bytes()).hexdigest() for p in (*pins, BOUNDARY, QUOTIENT)}
    for p, expected in pins.items():
        need(sources[str(p)] == expected, 'exact scientific input ' + p.name)
    raw = json.loads(gzip.decompress(RAW.read_bytes()))
    full = json.loads(gzip.decompress(FULL.read_bytes()))
    program = json.loads(gzip.decompress(CODE.read_bytes()))
    pin, boundary, quotient = [json.loads(p.read_bytes()) for p in (PIN, BOUNDARY, QUOTIENT)]
    instructions = [r for r in program['records'] if r[0] == 1 and r[-1] in (21, 22, 23, 24)]
    need(len(instructions) == 1487, 'source code literal ADD count')
    need(all(d < 111 and s < 111 and f == 1 for _, d, s, coef, f, phase in instructions), 'literal code domain')
    # Execute each input column separately, then transpose back to comparison rows.
    C = [0] * 111
    for source in range(111):
        column = [int(i == source) for i in range(111)]
        for _, dst, src, coef, frame, phase in instructions:
            column[dst] ^= (coef % 2) * column[src]
        for dst, bit in enumerate(column):
            C[dst] |= bit << source
    identity = [1 << i for i in range(111)]
    need(C == pin['C_binary_rows'] and rank(C) == 111, 'actual C511 rows')
    need(rank([x ^ y for x, y in zip(C, identity)]) == 9, 'scalar C-I rank9')
    need(binary_power(C, 511) == identity and binary_power(C, 7) != identity
         and binary_power(C, 73) != identity, 'exact order511')
    rhos, projectors, rho_hashes = routes(raw, full, pin)
    r, P = list(map(modular, rhos)), list(map(modular, projectors))
    formal = formal_residual(boundary)
    columns = [[dst for dst in range(111) if C[dst] >> source & 1] for source in range(111)]
    records, sample_summaries, original_rows = [], [], []
    all_maps = []
    identity_checks = 0
    first_boundary = None
    for j in range(8):
        v = tuple(int(i == j) for i in range(15))
        direct = []
        intermediate = []
        for k in range(111):
            tail = mv(P[k], v[:8]) + (0,) * 7
            head = tuple((x - y) % 101 for x, y in zip(v, tail))
            direct.append(head + tail)
            intermediate.append((mv(r[k], head), mv(r[k], tail)))
            hh, tt = intermediate[-1]
            need(mv(r[k], hh) + mv(r[k], tt) == direct[-1], 'identity-code Phi cancellation')
            identity_checks += 1
        # Construct each elementary input column, using C's column adjacency.
        # Route addresses once per (middle port,destination), then XOR that
        # path independently for each entering input coefficient.
        routed = {}
        for middle in range(111):
            hh, tt = intermediate[middle]
            for dst in columns[middle]:
                routed[middle, dst] = mv(r[dst], hh) + mv(r[dst], tt)
        maps = [dict() for _ in range(111)]
        for source in range(111):
            maps[source][direct[source]] = maps[source].get(direct[source], 0) ^ (1 << source)
            for middle in columns[source]:
                for dst in columns[middle]:
                    at = routed[middle, dst]
                    maps[dst][at] = maps[dst].get(at, 0) ^ (1 << source)
        all_maps.append(maps)
        count, support = 0, 0
        for dst, values in enumerate(maps):
            for at, row in sorted(values.items()):
                if row and any(at[15:]):
                    records.append([j, dst, list(at), row])
                    original_rows.append(row)
                    count += 1
                    support |= row
        sample_summaries.append({'input_HEAD_basis': j, 'nonfree_coefficient_rows': count,
                                 'nonzero_SOURCE_columns': support.bit_count(),
                                 'accumulated_rank': rank(original_rows)})
        if j == 0:
            outputs = [[list(at) for at, row in sorted(values.items()) if row & 1] for values in maps]
            bad = [(dst, at) for dst, values in enumerate(outputs) for at in values if any(at[15:])]
            first_boundary = {'outputs': sum(map(len, outputs)), 'nonzero_tail_outputs': len(bad),
                              'digest': digest(outputs), 'first': [bad[0][0], bad[0][1]]}
    need(sample_summaries == quotient['per_sample'], 'every exact sample summary')
    need(len(records) == quotient['all_nonzero_coefficient_rows'] == 24898, 'complete row count')
    need(digest(records) == quotient['complete_coefficient_rows_sha256'], 'complete coefficient-row digest')
    need(rank(original_rows) == 111, 'independent full observation rank')
    original_witnesses = []
    reduced_witnesses = []
    for cert in quotient['row_echelon_certificate']:
        w = cert['original_row_witness']
        at = tuple(w['output_HEAD'] + w['output_TAIL'])
        row = all_maps[w['input_HEAD_basis']][w['output_port']].get(at, 0)
        need(row == w['coefficient_SOURCE_row'] and row and any(at[15:]), 'exact saved witness row')
        original_witnesses.append(row)
        reduced_witnesses.append(cert['reduced_row'])
        need(cert['reduced_row'].bit_length() - 1 == cert['pivot'], 'saved pivot')
    need(len(original_witnesses) == rank(original_witnesses) == rank(reduced_witnesses) == 111,
         'all111 saved original rows independently span the source')
    old_impulse = boundary['actual_raw_word_control']
    need(first_boundary['outputs'] == old_impulse['nonzero_output_impulses'] == 3131,
         'source port0 head e0 impulse output count')
    need(first_boundary['digest'] == old_impulse['complete_output_sha256'] and first_boundary['nonzero_tail_outputs'] == 1,
         'complete original impulse and unique nonfree output')
    need(first_boundary['first'] == [0, [0]*15 + [1] + [0]*14], 'actual destructive tail witness')
    boundary_at = tuple([0]*15 + [1] + [0]*14)
    boundary_row = all_maps[0][0][boundary_at]
    without_n_row = boundary_row ^ 1
    need(boundary_row & 1 and not (without_n_row & 1), 'omitting N flips actual nonfree impulse coefficient')

    # Actual code mutation: toggle C0[0,1], holding C1 and every route fixed.
    # Its difference is precisely C1*N applied to middle-port0's delta.
    need(C[0] >> 1 & 1, 'actual coefficient being removed')
    j = 0
    tail = mv(P[0], (1,) + (0,)*7) + (0,)*7
    head = tuple((int(i == 0) - tail[i]) % 101 for i in range(15))
    hh, tt = mv(r[0], head), mv(r[0], tail)
    mutated = [{at: row for at, row in values.items()} for values in all_maps[0]]
    mutation_witness = None
    for dst in columns[0]:
        at = mv(r[dst], hh) + mv(r[dst], tt)
        before = mutated[dst].get(at, 0)
        mutated[dst][at] = before ^ 2
        if any(at[15:]) and mutation_witness is None:
            mutation_witness = {'output_port': dst, 'ADDRESS': list(at),
                                'old_source_coefficient_row': before, 'new_source_coefficient_row': before ^ 2}
    need(mutation_witness is not None, 'actual code mutation changes projected observation')
    mutated_records = [[0, dst, list(at), row] for dst, values in enumerate(mutated)
                       for at, row in sorted(values.items()) if row and any(at[15:])]
    original_first = [row for row in records if row[0] == 0]
    need(digest(mutated_records) != digest(original_first), 'actual mutation changes full sampled coefficient digest')

    # A rational routed coefficient proves noncommutation with N independently.
    p, q = 0, 1
    need(C[p] >> q & 1, 'noncommuting coefficient present')
    route = matmul(rhos[p], rhos[q])
    def padded(proj):
        return [[proj[i][j] if i < 8 and j < 8 else Q(0) for j in range(15)] for i in range(15)]
    left, right = matmul(padded(projectors[p]), route), matmul(route, padded(projectors[q]))
    comm = next((i, j, left[i][j], right[i][j]) for i in range(15) for j in range(15)
                if left[i][j] != right[i][j])
    result = {'status': 'PASS_INDEPENDENT_B09_ACTUAL_OBSERVATION_RANK111',
              'scientific_pin': '20ecf2891d80b5acf18d980b2164fb44ea7faa90', 'source_sha256': sources,
              'VALUE_coefficient_field': 'F2', 'ADDRESS_field': 101, 'C_order': 511,
              'source_code_ADDs': 1487, 'C_rank': 111, 'C_minus_I_rank': 9,
              'actual_rho_count': len(rhos), 'actual_rho_hashes': rho_hashes,
              'formal_three_call_residual': formal, 'impulse': first_boundary,
              'per_sample': sample_summaries, 'complete_coefficient_rows': len(records),
              'complete_coefficient_rows_sha256': digest(records), 'observation_rank': 111,
              'saved_original_witnesses_checked': len(original_witnesses),
              'saved_original_witness_rank': rank(original_witnesses),
              'identity_code_cancellations': identity_checks,
              'actual_C0_bit_mutation_witness': mutation_witness,
              'mutated_sample0_coefficient_digest': digest(mutated_records),
              'omitted_N_control': {'output_port': 0, 'ADDRESS': list(boundary_at),
                  'source0_coefficient_before': boundary_row & 1,
                  'source0_coefficient_after': without_n_row & 1},
              'noncommuting_routed_coefficient': {'edge': [p,q], 'entry': list(comm[:2]),
                  'left': str(comm[2]), 'right': str(comm[3])},
              'scope': 'At least111 ADDRESS-independent common scalar source rows modulo tail-zero-preserving free maps; no native tariff or routed-reader bound.'}
    (HERE/'INDEPENDENT-RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(result['status'])
    print('3131 impulse outputs;24898 coefficient rows;111 witnessed independent rows;888 identity-code cancellations; actual code mutation changes output')


if __name__ == '__main__':
    main()
