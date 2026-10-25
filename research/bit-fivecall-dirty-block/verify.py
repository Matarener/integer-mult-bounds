#!/usr/bin/env python3
"""Exact diagnostics for the written conic proof; no word-search theorem claim.
JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def need(value, message):
    if not value:
        raise ValueError(message)


def rank(rows):
    a = [list(map(Q, row)) for row in rows]
    k = 0
    for j in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(k, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[k], a[pivot] = a[pivot], a[k]
        c = a[k][j]
        a[k] = [x / c for x in a[k]]
        for i in range(len(a)):
            if i != k:
                c = a[i][j]
                a[i] = [x - c*y for x, y in zip(a[i], a[k])]
        k += 1
    return k


def det(a):
    return a[0]*a[3] - a[1]*a[2]


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2],
            a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def frame(a):
    return (a[0], a[1], a[2], -a[0])


def matchings(n):
    edges = tuple(combinations(range(n), 2))
    return [frozenset(s) for k in range(n//2+1)
            for s in combinations(edges, k)
            if len({v for e in s for v in e}) == 2*k]


def graph_check():
    edges = frozenset(combinations(range(5), 2))
    ms = matchings(5)
    counts = [0, 0]
    for triple in product(ms, repeat=3):
        bad = frozenset.union(*triple)
        need(len(bad) <= 6, 'three targets exceed six bad secants')
        good = edges-bad
        covered = set().union(*(set(range(5))-set(e) for e in good))
        uncovered = 5-len(covered)
        need(uncovered <= 1, 'two scalar images can escape the active space')
        counts[uncovered] += 1
    # Dropping the six-edge premise really permits two uncovered indices.
    bad = frozenset(e for e in edges if 0 not in e or 1 not in e)
    covered = set().union(*(set(range(5))-set(e) for e in edges-bad))
    need(5-len(covered) == 2 and len(bad) == 9, 'edge-budget control')
    return {'matchings': len(ms), 'triple_cases': sum(counts),
            'zero_or_one_uncovered': counts, 'nine_edge_control': True}


def conic_check():
    points = [(t, 1, -t*t) for t in range(-3, 4)] + [(0, 0, 1)]
    need(all(det(frame(p)) == 0 and any(p) for p in points), 'conic points')
    triples = list(combinations(points, 3))
    need(all(rank(t) == 3 for t in triples), 'three points collinear')
    targets = [t for t in product(range(-2, 3), repeat=3) if det(frame(t))]
    checked = 0
    for subset in combinations(points, 5):
        for target in targets:
            bad = [e for e in combinations(range(5), 2)
                   if dot(cross(subset[e[0]], subset[e[1]]), target) == 0]
            need(len({v for e in bad for v in e}) == 2*len(bad), 'secants not matching')
            checked += 1
    p, *qs = [points[-1], points[2], points[3], points[4]]
    four_targets = []
    for i in range(3):
        others = [qs[j] for j in range(3) if j != i]
        c = cross(cross(p, qs[i]), cross(*others))
        need(det(frame(c)) != 0, 'four-point diagonal intersection singular')
        four_targets.append(c)
    for j in range(3):
        masks = [sum(1 << k for k in range(3) if k != i) for i in range(3) if i != j]
        need(masks[0] & masks[1] == 1 << j, 'singleton image intersection')
    # A singular target at a conic point violates the matching premise.
    bad = [e for e in combinations(range(5), 2)
           if dot(cross(points[e[0]], points[e[1]]), points[0]) == 0]
    need(len(bad) == 4, 'singular-target control')
    # In the degenerate plane A22=0 no rank-one frame has both b,c nonzero.
    degenerate = [(a,b,c,0) for a,b,c in product(range(-3,4), repeat=3)]
    need(all(not (a[1] and a[2]) for a in degenerate if det(a) == 0), 'degenerate partition')
    return {'conic_triples':len(triples), 'five_point_target_cases':checked,
            'four_point_targets':four_targets, 'controls':['singular target', 'degenerate conic']}


def xor_term(row, key, value):
    row[key] = row.get(key, 0) ^ value
    if not row[key]:
        del row[key]


def propagate(word, n):
    zero = (0,0,0,0)
    columns = []
    for source in range(n):
        v = {zero:1 << source}
        for addr, x, y in word:
            delta = {}
            for key, value in v.items():
                if (value & y).bit_count() % 2:
                    xor_term(delta, key, x)
                    xor_term(delta, tuple(a+b for a,b in zip(key,addr)), x)
            for key, value in delta.items():
                xor_term(v, key, value)
        columns.append(v)
    return columns


def polynomial_matrix(word, n):
    # Independent row-polynomial multiplication, not symbolic-vector propagation.
    z = (0,0,0,0)
    matrix = [[{z} if i == j else set() for j in range(n)] for i in range(n)]
    for addr, x, y in word:
        old = [[set(e) for e in row] for row in matrix]
        for i in range(n):
            if not (x >> i & 1):
                continue
            for j in range(n):
                for k in range(n):
                    if y >> k & 1:
                        matrix[i][j] ^= old[k][j]
                        matrix[i][j] ^= {tuple(a+b for a,b in zip(key,addr)) for key in old[k][j]}
    columns = []
    for j in range(n):
        col = {}
        for i in range(n):
            for key in matrix[i][j]:
                col[key] = col.get(key, 0) | (1 << i)
        columns.append(col)
    return columns


def formal_check():
    targets = [(1,0,0,1), (1,1,0,1), (0,1,-1,0)]
    word = []
    for i, (a,b,c,d) in enumerate(targets):
        word += [((a,0,c,0),1<<i,1<<i), ((0,b,0,d),1<<i,1<<i)]
    expected = [{a:1<<i} for i,a in enumerate(targets)] + [{(0,0,0,0):8}]
    need(all(rank([a[:2],a[2:]]) == 1 for a,_,_ in word), 'paid frame rank')
    need(propagate(word,4) == polynomial_matrix(word,4) == expected, 'six-call positive')
    for j in range(6):
        mutant = word[:j]+word[j+1:]
        need(propagate(mutant,4) == polynomial_matrix(mutant,4) != expected, 'deleted call')
    mutant = list(word)
    mutant[0] = ((2,0,0,0),1,1)
    need(propagate(mutant,4) == polynomial_matrix(mutant,4) != expected, 'address mutation')
    # Dirty non-coordinate cancelling factors, before and after the positive word.
    a = (1,1,0,0)
    pair = [(a,9,1), (tuple(-v for v in a),9,1)]
    need(propagate(pair+word,4) == polynomial_matrix(pair+word,4) == expected, 'dirty cancellation')
    need(propagate(pair[:1]+word,4) != expected, 'unrestored dirty image')
    restricted = 0
    for x,y in product(range(1,16), repeat=2):
        if (x&y).bit_count()%2 and x < 8:
            need((x & (y&7)).bit_count()%2 == 1, 'active restriction loses idempotence')
            restricted += 1
    return {'six_call_targets':targets, 'deletion_controls':6, 'address_control':True,
            'dirty_cancellation_control':True, 'active_idempotents_checked':restricted}


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source hash mismatch: '+row['path'])
    result = {'schema_version':1, 'claim':'written proof; finite diagnostics are not exhaustive word search',
              'graph':graph_check(), 'conic':conic_check(), 'formal':formal_check()}
    result['proof_sha256'] = hashlib.sha256((HERE/'PROOF.md').read_bytes()).hexdigest()
    result['verifier_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if sys.argv[1:] == ['--write-result']:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        need(not sys.argv[1:], 'unknown arguments')
        need((HERE/'RESULT.json').read_text() == json.dumps(result,indent=2,sort_keys=True)+'\n', 'receipt differs')
    print('PASS_FIVECALL_DIRTY_BLOCK six_call_floor arbitrary_diagonal_auxiliary_outputs')


if __name__ == '__main__':
    main()
