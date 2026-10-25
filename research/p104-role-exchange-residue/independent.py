#!/usr/bin/env python3
"""Separate quarter-integer endpoint reconstruction, without importing verify.py.
Apache-2.0. This is a second implementation, not independent human review.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
from fractions import Fraction

P = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--algebra-only', action='store_true')
    args = parser.parse_args()
    extract = json.loads((P/'geometry.json').read_text())
    if not args.algebra_only:
        raw = (P.parents[1]/extract['source_path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == extract['source_sha256'], 'source hash')
        f = json.loads(raw)['section4_explicit_P104']
        require(f['F0'] == extract['F0'] and f['C'] == extract['C'], 'extraction')
    roots = set()
    for v in itertools.product((-2,0,2), repeat=8):
        if sum(t != 0 for t in v) == 2:
            first = next(t for t in v if t)
            roots.add(tuple(t if first > 0 else -t for t in v))
    for v in itertools.product((-1,1), repeat=8):
        if sum(t < 0 for t in v) % 2 == 0:
            roots.add(tuple(t*v[0] for t in v))
    deleted = {tuple(v) for v in extract['F0']+extract['C']}
    roots = sorted(roots-deleted)
    require(len(roots) == 104, 'port count')
    # Choose the frame by the supports, rather than constructing its vectors.
    supports = {(0,2),(1,3),(4,6),(5,7)}
    J = [i for i,r in enumerate(roots) if tuple(j for j,t in enumerate(r) if t) in supports]
    N = [i for i in range(104) if i not in J]
    require(len(J) == 8, 'pivot frame')
    dot = [[sum(a*b for a,b in zip(r,s)) for s in roots] for r in roots]
    require(all(dot[i][j] == 8*(i == j) for i in J for j in J), 'orthogonal pivots')
    sign = [[dot[j][i]//4 for i in N] for j in J]
    require(all(dot[j][i] in (-4,0,4) for j in J for i in N), 'coefficient alphabet')
    # Every row stores four times its exact coefficient on 280 independent inputs.
    rows = [[4*int(i == k) for k in range(280)] for i in range(280)]
    for i in range(104):
        require(all(v%2 == 0 for v in dot[i]), 'quarter grid at channel exit')
        rows[104+i][:104] = [v//2 for v in dot[i]]
    saved = [r[:] for r in rows]
    # This reconstruction uses block ordering distinct from the primary word.
    for b,j in enumerate(J):
        for a,i in enumerate(N):
            s = sign[b][a]
            if s:
                require(all(v%2 == 0 for v in saved[i]), 'source half')
                inc = [s*(v//2) for v in saved[i]]
                rows[j] = [x+y for x,y in zip(rows[j],inc)]
                rows[104+j] = [x-y for x,y in zip(rows[104+j],inc)]
    for a,i in enumerate(N):
        rows[i] = [x+y for x,y in zip(saved[i],saved[104+i])]
        for b,j in enumerate(J):
            s = sign[b][a]
            if s:
                require(all(v%2 == 0 for v in rows[j]), 'query half')
                rows[i] = [x-s*(y//2) for x,y in zip(rows[i],rows[j])]
    for i in range(104):
        t = 104+i if i in J else i
        require(rows[t] == [4*int(k in (i,104+i)) for k in range(280)], 'sum row')
    require(rows[208:] == saved[208:], 'arbitrary dirty restoration')
    data = [[str(Fraction(v,4)) for v in row] for row in rows]
    raw = (json.dumps(data, sort_keys=True, separators=(',',':'))+'\n').encode()
    result = json.loads((P/'RESULT.json').read_text())
    require(hashlib.sha256(raw).hexdigest() == result['endpoint_sha256'], 'endpoint digest')
    require(J == result['pivots'], 'pivot order')
    # Check signed dense inputs through the independently obtained boundary.
    for seed in range(16):
        values = [((k+3)*(seed+11)*17 % 101)-50 for k in range(280)]
        output = [sum(c*v for c,v in zip(row,values)) for row in rows]
        for i in range(104):
            t = 104+i if i in J else i
            require(output[t] == 4*(values[i]+values[104+i]), 'signed fixture')
    marker = 'ALGEBRA_ONLY' if args.algebra_only else 'SOURCE_BOUND'
    print(f'PASS_P104_ROLE_EXCHANGE_INDEPENDENT_{marker} rows=280 columns=280 signed_fixtures=16')

if __name__ == '__main__':
    main()
