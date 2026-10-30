#!/usr/bin/env python3
"""Small exact controls for mixed two-port transfer; no quantified proof.

Standard library only. Default replay compares the saved JSON without writing;
--write-receipt writes the JSON beside this script. No coefficient search, network, or producer imports.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def gf_mul(a, b):
    # F4 = F2[w]/(w*w+w+1); 2=w and 3=w+1=w*w.
    out = 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a & 4:
            a ^= 7
    return out


def rank_q(columns):
    a = [list(map(F, row)) for row in zip(*columns)]
    p = 0
    for j in range(len(columns)):
        i = next((i for i in range(p, len(a)) if a[i][j]), None)
        if i is None:
            continue
        a[p], a[i] = a[i], a[p]
        v = a[p][j]
        a[p] = [x/v for x in a[p]]
        for i in range(len(a)):
            if i != p:
                v = a[i][j]
                a[i] = [x-v*y for x, y in zip(a[i], a[p])]
        p += 1
    return p


def rank_f4(columns):
    a = [list(row) for row in zip(*columns)]
    p = 0
    for j in range(len(columns)):
        i = next((i for i in range(p, len(a)) if a[i][j]), None)
        if i is None:
            continue
        a[p], a[i] = a[i], a[p]
        inv = gf_mul(a[p][j], a[p][j])
        a[p] = [gf_mul(x, inv) for x in a[p]]
        for i in range(len(a)):
            if i != p:
                v = a[i][j]
                a[i] = [x ^ gf_mul(v, y) for x, y in zip(a[i], a[p])]
        p += 1
    return p


def endpoint(terms, field):
    out = [[0]*3 for _ in range(3)]
    for q, r in terms:
        for i in range(3):
            for j in range(3):
                if field == 'Q':
                    out[i][j] += q[i]*r[j]
                else:
                    out[i][j] ^= gf_mul(q[i], r[j])
    return out


def square(a, b, c, characteristic_two=False):
    neg = (lambda x: x) if characteristic_two else (lambda x: -x)
    # Matrix-position vertices 00,10,11,01. Vertical gain a is replicated.
    return [[1,neg(a),0,0], [0,0,neg(a),1],
            [1,0,0,neg(b)], [0,1,neg(c),0]]


def support(terms):
    return [[sum((x != 0)<<i for i,x in enumerate(q)),
             sum((x != 0)<<i for i,x in enumerate(r))] for q,r in terms]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', action='store_true')
    args = parser.parse_args()
    identity = [[int(i == j) for j in range(3)] for i in range(3)]

    # A commuting square has holonomy 1 for the repeated horizontal/vertical
    # gains. Do not claim that all formal cycles are unbalanced.
    need(rank_q(square(5,2,2)) == 3, 'rational commuting square')
    need(rank_f4(square(2,3,3,True)) == 3, 'F4 commuting square')
    # A repeat of a still cancels, but the independent gains b and c do not.
    need(rank_q(square(5,2,3)) == 4, 'old unbalanced repeated-gain cycle')
    need(rank_f4(square(1,2,1,True)) == 4, 'new unbalanced repeated-gain cycle')

    # Exact I3 with nonuniform sparse sides and essential forbidden-entry
    # cancellation between the two orientation classes.
    mixed = [([1,1,0],[1,1,1]), ([-1,-1,1],[1,1,0]),
             ([1,0,-1],[1,0,0]), ([0,1,-1],[0,1,0]),
             ([-1,-1,1],[0,0,1])]
    need(endpoint(mixed,'Q') == identity, 'rational mixed I3')
    class_a = [term for term in mixed if sum(x != 0 for x in term[0]) <= 2]
    class_b = [term for term in mixed if term not in class_a]
    a, b = endpoint(class_a,'Q'), endpoint(class_b,'Q')
    cross = [[i,j,a[i][j],b[i][j]] for i in range(3) for j in range(3)
             if i != j and a[i][j]]
    need(len(cross) == 6 and all(x+y == 0 for i,j,x,y in cross),
         'all six forbidden positions cancel across classes')
    need(any(sum(x != 0 for x in r) == 3 for q,r in mixed), 'no uniformly sparse reader side')
    need(any(sum(x != 0 for x in q) == 3 for q,r in mixed), 'no uniformly sparse query side')
    mixed_f4 = [([x%2 for x in q],[x%2 for x in r]) for q,r in mixed]
    need(endpoint(mixed_f4,'F4') == identity, 'actual support-preserving characteristic-two mixed factors')
    need(support(mixed_f4) == support(mixed), 'mixed support envelopes')

    # A five-vertex path through matrix positions 00,01,11,12,22. Three of
    # its vertices are diagonal. Q has exact output I3 and a half coefficient.
    tree_q = [([1,0,0],[1,-1,0]), ([1,-1,0],[0,1,0]),
              ([0,2,0],[0,1,-1]), ([0,1,F(1,2)],[0,0,2])]
    need(endpoint(tree_q,'Q') == identity, 'rational three-diagonal tree I3')
    # Before row normalization, diagonal values are 1,w,w^2. The all-one
    # tree annihilator requires their sum 0; F2 has no all-nonzero solution.
    need(1 ^ 2 ^ 3 == 0 and 1 ^ 1 ^ 1 != 0, 'F4 needed for this fixed tree')
    tree_pre = [([1,0,0],[1,1,0]), ([1,1,0],[0,1,0]),
                ([0,3,0],[0,1,1]), ([0,1,1],[0,0,3])]
    need(endpoint(tree_pre,'F4') == [[1,0,0],[0,2,0],[0,0,3]], 'nonzero tree diagonal values')
    row_scales = [1,3,2]
    tree_post = [([gf_mul(row_scales[i],q[i]) for i in range(3)],r)
                 for q,r in tree_pre]
    need(endpoint(tree_post,'F4') == identity, 'consistent global row normalization')
    need(support(tree_post) == support(tree_q), 'tree support envelopes')
    # For A R=C^T with disjoint indicator marks, normalize output columns,
    # hence reader entries, rather than the query coordinates.
    tree_columns = [(q,[gf_mul(row_scales[j],r[j]) for j in range(3)])
                    for q,r in tree_pre]
    need(endpoint(tree_columns,'F4') == identity, 'consistent output column normalization')
    need(support(tree_columns) == support(tree_q), 'column-normalized support envelopes')
    # Duplicate each marked coordinate on two disjoint physical ports. This
    # gives the exact six-port endpoint CC^T, including its permitted copies.
    lifted = [([x for x in q for _ in range(2)],
               [x for x in r for _ in range(2)]) for q,r in tree_columns]
    for i in range(6):
        for j in range(6):
            value = 0
            for q,r in lifted:
                value ^= gf_mul(q[i],r[j])
            need(value == int(i//2 == j//2), 'exact duplicated-mark CC^T')
    need(max(sum(x != 0 for x in q) for q,r in lifted) == 4,
         'two coefficient marks can touch four literal ports')

    receipt = {
        'scope':'finite algebra controls only; quantified transfer is proved separately',
        'field_F4':'0,1,2=w,3=w+1, with w^2+w+1=0',
        'commuting_square':{'Q_rank':3,'F4_rank':3,'holonomy':'a*b*a^-1*b^-1=1'},
        'unbalanced_replicated_cycle':{'Q_rank':4,'F4_rank':4,'uncancelled_holonomy':'b/c'},
        'mixed_fixture':{'Q_endpoint':'I3','F4_endpoint':'I3','terms':mixed,
                         'F4_terms':mixed_f4,'supports':support(mixed),
                         'forbidden_cross_cancellations':cross,
                         'uniform_query_sparse':False,'uniform_reader_sparse':False},
        'three_diagonal_tree':{'Q_endpoint':'I3','pre_diagonal_F4':[1,2,3],
                               'F2_all_nonzero_feasible':False,
                               'row_scales_F4':row_scales,'F4_terms_after_scaling':tree_post,
                               'F4_endpoint':'I3','supports':support(tree_post)},
        'disjoint_mark_output_columns':{'column_scales_F4':row_scales,
                                        'F4_terms_after_scaling':tree_columns,
                                        'coefficient_endpoint':'I3',
                                        'duplicated_mark_endpoint':'CC^T on six ports',
                                        'literal_source_support_max':4,
                                        'exact_duplicate_mark_checks':36},
        'verdict':'PASS'}
    payload = json.dumps(receipt,indent=2)+'\n'
    receipt_path = Path(__file__).with_name('MIXED-CONTROLS.json')
    if args.write_receipt:
        receipt_path.write_text(payload,encoding='utf-8',newline='\n')
    else:
        need(receipt_path.is_file(), 'missing MIXED-CONTROLS.json receipt')
        need(json.loads(receipt_path.read_text(encoding='utf-8')) == json.loads(payload),
             'saved mixed controls receipt mismatch')
    print('PASS: repeated gains, mixed forbidden cancellation, F4 tree and shared row normalization')


if __name__ == '__main__':
    main()
