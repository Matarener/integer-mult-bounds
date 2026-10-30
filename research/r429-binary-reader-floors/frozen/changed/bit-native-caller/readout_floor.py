#!/usr/bin/env python3
"""Exact R429 row-code diagnostics and an overcomplete E8 flat-reader floor.

No predecessor producer is run. Only frozen JSON/gzip inputs are read.
Apache-2.0. Prepared with substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
BASE = Path('/Users/ross/git/math')
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
COMP = BASE / '.research-automation/runs/kappa-major-20261018T1330Z/bit-endpoint/BIT-FULL-COMPENSATION.json'
WORD = COMP.with_name('BIT-FULL-COMPENSATION-WORD.json.gz')
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
# Universal E8 root-line capacities, proved in READOUT-FLOOR.md by parabolic
# reduction. Using the unpunctured 120 at dimension8 is a relaxation.
CAP = (0, 1, 3, 6, 12, 20, 36, 63, 120)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def rank2(rows):
    basis = {}
    for row in rows:
        while row:
            k = row.bit_length()-1
            if k in basis:
                row ^= basis[k]
            else:
                basis[k] = row
                break
    return len(basis)

def bits(row):
    while row:
        k = row & -row
        yield k.bit_length()-1
        row ^= k

def span2(rows):
    out = [0]
    for row in rows:
        out += [old ^ row for old in out]
    return out

def rankq(rows):
    basis = {}
    for row in rows:
        row = list(map(Q, row))
        for k, old in sorted(basis.items()):
            c = row[k]
            row = [x-c*y for x, y in zip(row, old)]
        k = next((i for i, x in enumerate(row) if x), None)
        if k is not None:
            basis[k] = [x/row[k] for x in row]
    return len(basis)

def inverse(a):
    n = len(a)
    a = [[Q(x) for x in row]+[Q(i == j) for j in range(n)]
        for i, row in enumerate(a)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i][j])
        a[j], a[k] = a[k], a[j]
        c = a[j][j]
        a[j] = [x/c for x in a[j]]
        for i in range(n):
            if i != j:
                c = a[i][j]
                a[i] = [x-c*y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]

def profiles(budget, cap=CAP):
    inspected = 0
    survivors = []
    def rec(d, left, counts):
        nonlocal inspected
        if d == 9:
            inspected += 1
            t = sum(counts)
            if t < 9:
                return
            cost = sum((j+1)*c for j, c in enumerate(counts))
            wanted = t-8
            mass = 0
            for j, c in enumerate(counts):
                take = min(c, wanted)
                mass += cap[j+1]*take
                wanted -= take
                if wanted == 0:
                    break
            if mass >= 48:
                survivors.append({'cost':cost, 'readouts':t,
                    'rank_counts':{str(j+1):c for j,c in enumerate(counts) if c},
                    'smallest_t_minus_8_capacity':mass})
            return
        for c in range(left//d+1):
            rec(d+1, left-c*d, counts+[c])
    rec(1, budget, [])
    return inspected, sorted(survivors, key=lambda x:(x['cost'],x['readouts']))

def receipt():
    need(sha256(RAW.read_bytes()).hexdigest() ==
        'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022', 'raw pin')
    need(sha256(WORD.read_bytes()).hexdigest() ==
        '0f461dbc7e82a02faedb4a5129103963507c9f063a0a3679ba5d20ad94df160e', 'full word pin')
    w = json.loads(gzip.decompress(RAW.read_bytes()))
    comp = json.loads(COMP.read_bytes())
    need(comp['word_canonical_sha256'] == sha256(gzip.decompress(WORD.read_bytes())).hexdigest(),
        'full word canonical binding')
    roots = w['lines']
    # Reconstruct R and K independently from the raw source; the JSON matrices
    # are compared only after the reconstruction.
    rows = [1 << i for i in range(660)]
    for phase in ('D', 'A'):
        for _, dst, sources in w[phase]:
            for source in sources:
                rows[dst] ^= rows[source]
    R = [rows[h] & ((1 << 111)-1) for h in w['ret']]
    K = [sum(1 << j for j in indices) for indices in w['scatter']]
    need(R == comp['R'] and K == comp['K'], 'actual R/K matrices')
    need(rank2(R) == rank2(K) == 9, 'actual factor rank9')
    code = span2(R)
    need(len(set(code)) == 512, 'all nine independent code directions')
    distance = Counter(x.bit_count() for x in code[1:])
    need(min(distance) == 48, 'actual minimum distance48')
    need(all(any(row >> p & 1 for row in R) for p in range(111)),
        'all111 source columns nonzero')
    ranks = Counter()
    rank7 = []
    for mask, row in enumerate(code[1:], 1):
        d = rankq(roots[p] for p in bits(row))
        ranks[d] += 1
        if d == 7:
            rank7.append(mask)
    need(ranks == Counter({7:9,8:502}), 'complete rowspace support-span census')
    need(rank7 == [1 << j for j in range(9)], 'only the nine original directions have span7')
    # An explicit integral E8-lattice basis. Every retained root is checked
    # to have integer coordinates in it before reducing those coordinates mod2.
    basis = [[1,0,1,0,1,0,1,0], [0,1,1,0,1,0,0,1],
        [0,0,-1,1,-2,0,-1,-1], [0,0,0,-2,2,0,0,2],
        [0,0,0,0,1,1,1,-1], [0,0,0,0,0,2,0,-2],
        [0,0,0,0,0,0,2,-2], [0,0,0,0,0,0,0,-2]]
    bi = inverse(basis)
    U = [[sum(q[i]*bi[i][j] for i in range(8)) for j in range(8)] for q in roots]
    need(all(x.denominator == 1 for u in U for x in u), 'integral lattice coordinates')
    u = [[int(x) & 1 for x in row] for row in U]
    lift = [sum(((R[j] >> p & 1)*u[p][a]) << p for p in range(111))
        for j in range(9) for a in range(8)]
    need(rank2(lift) == 36, 'independent tensor-lift lower certificate36')
    inspected, survivors = profiles(48)
    need([x['rank_counts'] for x in survivors] == [{'4':12},{'3':16},{'2':24}],
        'complete cost<=48 profile survivors')
    # Explicit equality-case contradictions: rank2/3 total supports too small;
    # the any-four condition for rank4 forces12 full disjoint supports.
    need(16*CAP[3] < 111 and 24*CAP[2] < 111 and 12*CAP[4] > 111,
        'all three equality profile contradictions')
    # Defect controls affect proof-relevant premises, not just receipt strings.
    mutated = R[:]
    mutated[0] ^= 1
    need(mutated != R and span2(mutated) != code, 'mutated actual reader changes code')
    weakened = list(CAP)
    weakened[4] = 13
    _, bad_survivors = profiles(48, weakened)
    need(bad_survivors != survivors, 'wrong flat capacity changes finite screen')
    return {'status':'PASS_R429_ARBITRARY_OVERCOMPLETE_E8_FLAT_READOUT_COST_AT_LEAST49',
        'scientific_pin':PIN, 'no_new_kappa':True,
        'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in (RAW,COMP,WORD)},
        'R':R, 'K':K, 'root_lines':roots,
        'minimum_distance':48, 'code_distance_histogram':dict(sorted(distance.items())),
        'all511_reader_support_span_histogram':dict(sorted(ranks.items())),
        'span7_code_masks':rank7, 'minimum_9_direction_basis_rank_sum':63,
        'integer_lattice_basis':basis, 'tensor_lift_rank':36,
        'flat_capacity_upper_bounds':list(CAP),
        'cost_at_most48_sorted_rank_profiles_checked':inspected,
        'capacity_survivors':survivors,
        'equality_case_rejections':[
            '16 rank3 readouts cover at most96 source coordinates, fewer than111.',
            '24 rank2 readouts cover at most72 source coordinates, fewer than111.',
            '12 rank4 readouts: every four have disjoint full12 supports; hence all12 are pairwise disjoint and cover144>111 coordinates.'],
        'model':'Binary linear R=B C, arbitrary number of readouts; each nonzero C_j is supported on E8 root lines in a rational flat of dimension d_j, charged at least d_j. Readouts may lie outside rowspace(R).',
        'boundary':'The >=49 is a support-span cost floor, not an unrestricted native-circuit or rounded supplier lower bound. The cost relation requires each readout to be materialized by a native COPY at its containing frame. Shared native queries, nonlinear readouts, operator-valued coefficients and changed R are outside the factorization model.',
        'controls':['actual R mutation changes its code','weakening rank4 capacity changes surviving profiles']}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = json.loads(json.dumps(receipt()))
    path = HERE / 'READOUT-FLOOR.json'
    if args.write:
        path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == out, 'stored exact receipt differs')
    print(out['status'])
    print('511 reader combinations; distance48; tensor36; cost<=48 profiles',
        out['cost_at_most48_sorted_rank_profiles_checked'])

if __name__ == '__main__':
    main()
