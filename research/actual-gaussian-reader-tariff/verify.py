#!/usr/bin/env python3
"""Check the actual reader and its basis. Ali Romman with OpenAI Codex. Apache-2.0."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/centre-code-services/frozen/'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('control did not reject')


def source(suffix):
    path = SOURCE + suffix
    pin = next(x for x in json.loads((HERE/'SOURCES.json').read_text())['files'] if x['path'] == path)
    raw = (ROOT/path).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'source bytes')
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


def add(a, b, c):
    return {k: a.get(k, 0)+c*b.get(k, 0) for k in a.keys() | b.keys()
            if a.get(k, 0)+c*b.get(k, 0)}


def fwht(a):
    a = a[:]
    h = 1
    while h < len(a):
        for b in range(0, len(a), 2*h):
            for j in range(b, b+h):
                s, t = a[j], a[j+h]
                a[j], a[j+h] = s+t, s-t
        h *= 2
    return a


def rank(a, prime=None):
    basis = {}
    for row in a:
        row = row[:]
        for p, b in basis.items():
            if row[p]:
                x, y = row[p], b[p]
                row = [y*s-x*t for s, t in zip(row, b)]
                if prime:
                    row = [s % prime for s in row]
                else:
                    g = gcd(*row)
                    if g:
                        row = [s//g for s in row]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            basis[p] = row
    return len(basis)


def inv_check(t, b):
    n = len(t)
    for i in range(n):
        for j in range(n):
            need(sum(t[i][k]*b[k][j] for k in range(n)) == 120*(i == j), 'right inverse')
            need(sum(b[i][k]*t[k][j] for k in range(n)) == 120*(i == j), 'left inverse')


def best_additions(v, d):
    positive = []
    for a in range(30):
        for b in range(30):
            if a == b:
                continue
            counts = Counter(-d[b][k]/d[a][k] for k in d[a].keys() & d[b].keys())
            counts.update(v[a][k]/v[b][k] for k in v[a].keys() & v[b].keys())
            overhead = len(d[a].keys()-d[b].keys())+len(v[b].keys()-v[a].keys())
            for c, n in counts.items():
                if c.denominator & (c.denominator-1) == 0 and n > overhead:
                    positive.append((n-overhead, a, b, str(c)))
    return positive


def word(v, d, q, directions):
    result = []
    previous, total = {}, {}
    for first in range(0, 30, q):
        gather = {(j-first, p//512, p % 512): c
                  for j in range(first, min(30, first+q)) for p, c in d[j].items()}
        scatter = {(p, j-first, directions[p]): c
                   for j in range(first, min(30, first+q)) for p, c in v[j].items()}
        result.extend([('G', add(gather, previous, -1)), ('S', scatter)])
        previous = gather
        total = add(total, scatter, 1)
    result.extend([('G', {k: -c for k, c in previous.items()}),
                   ('S', {k: -c for k, c in total.items()})])
    return result


def apply_kernel(rows, data, denominator):
    out = [[0]*512 for _ in rows]
    for i, row in enumerate(rows):
        for packed, c in row.items():
            p, g = divmod(packed, 512)
            n = c*denominator
            need(n.denominator == 1, 'kernel integer scale')
            n = int(n)
            for x in range(512):
                out[i][x] += n*data[p][x ^ g]
    return out


def physical_replay(w, q, expected, omit=False):
    data = [[((i+7)*(x+11) % 101)-50 for x in range(512)] for i in range(112)]
    bank = [[((i+13)*(x+3) % 67)-33 for x in range(512)] for i in range(q)]
    initial_bank = [row[:] for row in bank]
    scale = 1
    for step, (kind, coeffs) in enumerate(w[:-1] if omit else w):
        den = lcm(*(c.denominator for c in coeffs.values()))
        if kind == 'G':
            target, src = bank, data
        else:
            target, src = data, bank
        out = [[den*x for x in row] for row in target]
        for (i, j, g), c in coeffs.items():
            n = int(den*c)
            for x in range(512):
                out[i][x] += n*src[j][x ^ g]
        if kind == 'G':
            bank, data = out, [[den*x for x in row] for row in data]
        else:
            data, bank = out, [[den*x for x in row] for row in bank]
        scale *= den
    need(all(bank[i][x] == scale*initial_bank[i][x] for i in range(q) for x in range(512)), 'dirty restore')
    need(all(240*data[i][x] == scale*expected[i][x] for i in range(112) for x in range(512)), 'physical data endpoint')


def main():
    for item in json.loads((HERE/'SOURCE-CONTEXT.json').read_text()):
        need(sha256((HERE/item['local']).read_bytes()).hexdigest() == item['sha256'], 'frozen context')
    r = source('lanes/new-core-transfer-20261017/low-displacement-20261020/run-normal/RESPONSE-PROGRAM.json')
    directions = source('lanes/history-encoding/independent-skeleton-20261018/fresh-three-child/FRESH-THREE-CHILD-PROGRAMS.json.gz')
    certificate = source('root/RANK30-PHASE-SECTION-BLOCKS-20261020.json.gz')
    u = [{int(j): F(c) for j, c in row.items()} for row in r['correction_U']]
    v = [{int(j): F(c) for j, c in row.items()} for row in r['correction_V']]
    q = [row['q'] for row in directions['transfers']]
    need(len(u) == 112 and len(v) == 30 and len(q) == 112 and len(set(q)) == 112, 'dimensions and directions')
    need(all((2*c).denominator == 1 for row in u for c in row.values()), 'twice U integral')
    need(all(c.denominator == 1 for row in v for c in row.values()), 'V integral')
    blocks = []
    for chi, rec in enumerate(certificate['characters']):
        need(rec['chi'] == chi, 'character index')
        b = [[F(0)]*30 for _ in range(30)]
        for i in range(16):
            for j in range(16):
                b[i][j] = 60*F(rec['large_inverse'][i][j])
        for i in range(16, 30):
            b[i][i] = 60/F(rec['small_diagonal'][i-16])
        need(all(c.denominator == 1 for row in b for c in row), 'inverse scale')
        blocks.append([[int(c) for c in row] for row in b])
    need(len(blocks) == 512, 'all characters')
    bv = []
    for b in blocks:
        rows = [[0]*112 for _ in range(30)]
        for i in range(30):
            for j, c in enumerate(b[i]):
                if c:
                    for p, a in v[j].items():
                        rows[i][p] += int(c*a)
        bv.append(rows)
    deltas, ranks, modular = [], [], []
    for chi, b in enumerate(blocks):
        signs = [1-2*((chi & x).bit_count() % 2) for x in q]
        t = [[0]*30 for _ in range(30)]
        for i, row in enumerate(v):
            for p, a in row.items():
                for j, c in u[p].items():
                    t[i][j] += int(2*signs[p]*a*c)
        inv_check(t, b)
        delta = [[bv[0][i][p]*signs[p]-bv[chi][i][p] for p in range(112)] for i in range(30)]
        for row in delta:
            cross = [F(0)]*30
            for p, c in enumerate(row):
                if c:
                    for j, a in u[p].items():
                        cross[j] += c*signs[p]*a
            need(not any(cross), 'Delta J = 0')
        deltas.append(delta)
        ranks.append(rank(delta))
        modular.append(rank(delta, 1000003))
    need(ranks == modular, 'independent modular rank lower bounds')
    need(max(ranks) == 30 and ranks[92] == 30, 'actual rank maximum')
    broken_inverse = [row[:] for row in blocks[-1]]
    broken_inverse[0][0] += 1
    reject(lambda: inv_check(t, broken_inverse))
    d = []
    for i in range(30):
        row = {}
        for p in range(112):
            transformed = fwht([a[i][p] for a in deltas])
            need(fwht(transformed) == [512*a[i][p] for a in deltas], 'Walsh inverse')
            row.update({512*p+g: F(c, 30720) for g, c in enumerate(transformed) if c})
        d.append(row)
    columns = [{p: row[i] for p, row in enumerate(u) if i in row} for i in range(30)]
    original_d, original_v = [a.copy() for a in d], [a.copy() for a in columns]
    need(sum(map(len, d)) == 15628 and sum(map(len, columns)) == 176, 'source coefficient bill')
    operations = json.loads((HERE/'BASIS.json').read_text())['operations']
    for a, b, c in operations:
        c = F(c)
        need(a != b and c.denominator & (c.denominator-1) == 0, 'dyadic elementary basis')
        d[b] = add(d[b], d[a], c)
        columns[a] = add(columns[a], columns[b], -c)
    need(sum(map(len, d)) == 9968 and sum(map(len, columns)) == 208, 'new coefficient bill')
    need(not best_additions(columns, d), 'complete single dyadic ADD local minimum')
    restored_d, restored_v = [a.copy() for a in d], [a.copy() for a in columns]
    for a, b, c in reversed(operations):
        restored_d[b] = add(restored_d[b], restored_d[a], -F(c))
        restored_v[a] = add(restored_v[a], restored_v[b], F(c))
    need(restored_d == original_d and restored_v == original_v, 'inverse basis and factor product')
    bills = []
    for borrowed in range(1, 31):
        w = word(columns, d, borrowed, q)
        need(len(w) == 2*((30+borrowed-1)//borrowed)+2, 'sharp stage count')
        js, ds = [], []
        for first in range(0, 30, borrowed):
            js.append(max(sum(abs(columns[j].get(p, 0)) for j in range(first, min(30, first+borrowed))) for p in range(112)))
            ds.append(max(sum(map(abs, row.values())) for row in d[first:first+borrowed]))
        j, dmax = sum(js), max(ds)
        m = max(1+2*dmax, 1+j)
        pref = max(1+sum(x*y for x, y in zip(js, ds))+j, 1+dmax)*m
        suff = (1+j*dmax)*max(1+j*(2*dmax+1), 1+dmax)*m
        bills.append(dict(borrowed=borrowed, shears=len(w), coefficient_adds=sum(len(a) for _, a in w),
                          nonidentity_shift_adds=sum(g != 0 for _, a in w for i, k, g in a),
                          prefix_bound=str(pref), suffix_bound=str(suff)))
    data = [[((i+7)*(x+11) % 101)-50 for x in range(512)] for i in range(112)]
    dx = apply_kernel(original_d, data, 120)
    expected = [[240*x for x in row] for row in data]
    for p, row in enumerate(u):
        for i, c in row.items():
            for x in range(512):
                expected[p][x] += int(2*c)*dx[i][x ^ q[p]]
    w = word(columns, d, 30, q)
    physical_replay(w, 30, expected)
    wrong_sign = [(kind, a.copy()) for kind, a in w]
    wrong_sign[2] = ('G', {k: -c for k, c in wrong_sign[2][1].items()})
    reject(lambda: physical_replay(wrong_sign, 30, expected))
    reject(lambda: physical_replay(w, 30, expected, omit=True))
    den = lcm(*(c.denominator for a in columns+d for c in a.values()))
    odd = den
    while odd % 2 == 0:
        odd //= 2
    need(odd == 15, 'no new odd denominator')
    result = dict(status='PASS_ACTUAL_GAUSSIAN_READER_TARIFF', characters=512,
                  rank_histogram=dict(sorted(Counter(ranks).items())), maximum_rank_character=92,
                  zero_characters=[i for i, r in enumerate(ranks) if not r],
                  old_adds=31608, new_adds=20352, dyadic_basis_operations=operations,
                  common_denominator=den, physical_orbit_size=512, controls=3, bills=bills)
    path = HERE/'RESULT.json'
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if path.exists():
        need(path.read_text() == text, 'fixed result receipt')
    else:
        path.write_text(text)
    print(result['status'])
    print('rank=30; coefficient_ADDs=31608 -> 20352; all 870 dyadic row-ADD directions checked')


if __name__ == '__main__':
    main()
