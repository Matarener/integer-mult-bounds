#!/usr/bin/env python3
"""Check code witnesses, affine coset sums and the retained upper construction.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
import hashlib
from itertools import combinations
import json
from math import comb, prod, gcd
from pathlib import Path
import random
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(c, message):
    if not c: raise ValueError(message)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            k = value.bit_length()-1
            if k not in pivots:
                pivots[k] = value; break
            value ^= pivots[k]
    return len(pivots)


def code_rows(n):
    need(n >= 5 and n % 4 == 1, 'axis family')
    rows = []
    for block in range((n-1)//4):
        rows.extend(x << (8*block) for x in [255,170,204,240])
    rows.append(15 << (2*n-2))
    return rows, 2*n+3


def points_from_rows(rows, length):
    return [sum(((r >> j) & 1) << i for i,r in enumerate(rows)) for j in range(length)]


def check_tuple(points, n, residue):
    need(len(points) % 4 == residue, 'constant character')
    need(rank(x ^ points[0] for x in points) == n, 'full affine span')
    rows = [sum(((x >> i) & 1) << j for j,x in enumerate(points)) for i in range(n)]
    need(all(r.bit_count() % 4 == 0 for r in rows), 'linear phase character')
    need(all((x & y).bit_count() % 2 == 0 for x,y in combinations(rows,2)), 'quadratic phase character')


def gl(n):
    def extend(columns, span):
        if len(columns) == n:
            table = [0]*(1 << n)
            for x in range(1,1 << n):
                bit = x & -x; table[x] = table[x ^ bit] ^ columns[bit.bit_length()-1]
            yield tuple(table); return
        for x in range(1,1 << n):
            if x not in span:
                yield from extend(columns+[x],span | {x ^ y for y in span})
    return list(extend([], {0}))


def character(g, n):
    identity = tuple(range(1 << n)); power = g; order = 1
    while power != identity:
        power = tuple(g[x] for x in power); order += 1
        need(order <= (1 << n), 'group order control')
    r = rank(g[1 << j] ^ (1 << j) for j in range(n))
    if n == 3: return {1:6,2:-2,3:0,4:2,7:-1}[order]
    if order == 1: return 42
    if order == 2: return -6 if r == 1 else 2
    if order == 4: return 2 if r == 2 else -2
    if order == 3: return -6 if r == 4 else 0
    if order == 6: return 2 if r == 4 else 0
    if order == 5: return 2
    if order == 7: return 0
    if order == 15: return -1
    raise ValueError('unclassified element')


def coset_checks(n):
    group = gl(n); weights = [character(g,n) for g in group]
    need(sum(x*x for x in weights) % len(group) == 0, 'character norm')
    count = 0
    for normal in range(1,1 << n):
        basis = []
        for x in range(1,1 << n):
            if not (x & normal).bit_count() % 2 and rank(basis+[x]) > len(basis): basis.append(x)
        need(len(basis) == n-1, 'hyperplane')
        sums = defaultdict(int)
        for g,w in zip(group,weights): sums[tuple(g[x] for x in basis)] += w
        need(set(sums.values()) == {0}, 'every hyperplane coset sum')
        count += len(sums)
    need(any(weights) and sum(weights) == 0, 'nonzero cancellation character')
    # An identity coefficient corruption leaves a nonzero coset sum.
    normal = 1; basis = [1 << j for j in range(1,n)]
    bad = defaultdict(int)
    for g,w in zip(group,weights): bad[tuple(g[x] for x in basis)] += w+int(g == tuple(range(1 << n)))
    need(any(bad.values()), 'character corruption detected')
    return {'dimension':n,'group_order':len(group),'cosets':count,'coefficient_counts':dict(Counter(weights)),'character_norm':sum(x*x for x in weights)//len(group)}


def run():
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    for s in pins:
        if s['usage'] == 'input': need(hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest() == s['sha256'],'source bytes')
    witnesses = []
    for n in range(5,130,4):
        rows,length = code_rows(n)
        need(rank(rows) == n and rank(rows+[(1 << length)-1]) == n+1, 'code and affine ranks')
        base = points_from_rows(rows,length)
        record = {'axes':n,'cutoff':length,'thresholds':[length+(r-length)%4 for r in range(4)]}
        for r in range(4): check_tuple(base+[0]*((r-length)%4),n,r)
        if n == 9: record['shortest_points'] = base
        # Direct binomial Gauss sum at the forbidden self-dual length.
        N = 2*n+2
        real = sum((-1)**(j//2)*comb(N,j) for j in range(0,N+1,2))
        imag = sum((-1)**((j-1)//2)*comb(N,j) for j in range(1,N+1,2))
        need((real,imag) == (-(1 << (N//2)),0), 'length-four-mod-eight Gauss contradiction')
        record['forbidden_self_dual_length'] = N
        record['gauss_sum'] = real
        witnesses.append(record)
    row8 = [255,170,204,240]
    words = [0]
    for r in row8: words += [r ^ x for x in words]
    need(len(set(words)) == 16 and all(x.bit_count()%4 == 0 for x in words), 'E8 code control')
    need(sum((-1)**(j//2)*comb(8,j) for j in range(0,9,2)) == 16, 'length-eight positive Gauss control')
    smallest,_ = code_rows(5)
    short = points_from_rows(smallest,12)
    need(rank(x ^ short[0] for x in short) == 4, 'deleted zero loses affine span')
    bad = points_from_rows(*code_rows(9));bad[0] ^= 1
    try: check_tuple(bad,9,len(bad)%4)
    except ValueError: pass
    else: raise ValueError('phase mutation accepted')
    groups = [coset_checks(3),coset_checks(4)]
    upper = runpy.run_path(str(ROOT/'research/shorter-native-phase-witness/verify.py'))
    rng = random.Random(562233); cases = 0
    for n in [5,9,13,17,21,25,29,33]:
        for _ in range(64):
            u = tuple(rng.randrange(4) for j in range(n));v = tuple(rng.randrange(2) for j in range(n*(n-1)//2));f = 2*n+3+rng.randrange(4)
            pts = upper['witness'](n,u,v,f)
            rows = [sum(((x >> i)&1) << j for j,x in enumerate(pts)) for i in range(n)]
            need(len(pts) == f and rank(x ^ pts[0] for x in pts) == n, 'upper affine witness')
            need(tuple(x.bit_count()%4 for x in rows) == u, 'upper linear statistics')
            need(tuple((rows[i]&rows[j]).bit_count()%2 for i,j in combinations(range(n),2)) == v, 'upper quadratic statistics')
            cases += 1
    n = 9; N = (1 << n)-1; phi = sum(gcd(k,N) == 1 for k in range(N)); copies = phi//n
    degree = prod((1 << j)-1 for j in range(1,n));transvection = -degree//((1 << (n-1))-1)
    need(phi % n == 0 and copies*degree+((1 << (n-1))-1)*copies*transvection == 0, 'cuspidal fixed-space dimension')
    return {'status':'PASS_NINE_AXIS_CUTOFF_SHARPNESS','scope':'n=1 mod 4, n>=5; fixed affine-quadratic input-phase grammar','witnesses':witnesses,'small_group_controls':groups,'upper_witness_controls':cases,'nine_axis':{'cutoff':21,'thresholds':[24,21,22,23],'primitive_cuspidal_count':copies,'irreducible_degree':degree,'integer_character_identity':copies*degree,'integer_character_transvection':copies*transvection},'rejection_controls':4,'limits':['Green character theory is a cited theorem, not kernel-checked or enumerated at n=9.','The general upper proof is retained from PR5529; finite controls do not prove it.','No physical supplier, efficient group-algebra expansion or kappa improvement.']}


if __name__ == '__main__':
    result = json.loads(json.dumps(run(),sort_keys=True))
    if '--write' in sys.argv: (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else: need(result == json.loads((HERE/'RESULT.json').read_text()),'receipt differs')
    print(result['status'])
