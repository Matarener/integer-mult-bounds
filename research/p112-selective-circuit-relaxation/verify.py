#!/usr/bin/env python3
"""One fixed six-query Dowling dictionary: exact selective F4 transfer.

No geometry or coefficient search. Read-only receipt replay by default.
"""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import argparse
import json
from hashlib import sha256
from collections import Counter

Q = [[1,1,-1],[1,-1,1],[-1,1,1],
     [0,1,-1],[1,0,-1],[1,-1,0]]
B = [[1,1,1],[2,1,1],[1,3,1],
     [0,1,1],[1,0,1],[2,1,0]]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def mul(a,b):
    out=0
    while b:
        if b&1:
            out ^= a
        a <<= 1
        if a&4:
            a ^= 7
        b >>= 1
    return out


def rank(columns,field):
    a = [list(map(F,row)) if field=='Q' else list(row)
         for row in zip(*columns)]
    p=0
    for j in range(len(columns)):
        i=next((i for i in range(p,len(a)) if a[i][j]),None)
        if i is None:
            continue
        a[p],a[i]=a[i],a[p]
        v=a[p][j]
        a[p]=[x/v for x in a[p]] if field=='Q' else [mul(x,mul(v,v)) for x in a[p]]
        for i in range(len(a)):
            if i != p:
                v=a[i][j]
                a[i]=([x-v*y for x,y in zip(a[i],a[p])] if field=='Q'
                      else [x^mul(v,y) for x,y in zip(a[i],a[p])])
        p+=1
    return p



PINS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def binary_rank(rows):
    basis = {}
    for v in rows:
        while v:
            p = v.bit_length()-1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
    return len(basis)


def geometry():
    root = Path(__file__).resolve().parents[2]
    inputs = []
    for path,digest in PINS.items():
        payload = (root/path).read_bytes()
        need(sha256(payload).hexdigest() == digest, 'pinned input: '+path)
        inputs.append(json.loads(payload))
    candidate,data = inputs
    groups,marks = candidate['groups'],candidate['factor_supports']
    labels = {r['port']:r['q'] for r in data['recipes']}
    owner = {p:g for g,ps in enumerate(groups) for p in ps}
    marked = {p:j for j,ps in enumerate(marks) for p in ps}
    ports = set(range(112))
    need(set(owner) == ports and sum(map(len,groups)) == 112,
         'groups partition exactly the 112 ports')
    need(set(marked) == ports and sum(map(len,marks)) == 112,
         'disjoint canonical marks partition exactly the 112 ports')
    need(set(labels) == ports, 'all binary labels present exactly once')
    need(len(data['recipes']) == 112, 'no duplicate recipe ports')
    need(Counter(map(len,groups)) == {1:1,3:37}, 'physical group dimensions')
    need(Counter(map(len,marks)) == {1:3,2:53,3:1}, 'canonical copy counts')
    pairing = {(a,b):(labels[a]&labels[b]).bit_count()%2 for a in ports for b in ports}
    for ps in groups:
        need(all(pairing[a,b] == int(a == b) for a in ps for b in ps),
             'each full physical group is orthonormal')
    expanded = [(p,a) for p in range(112) for a in groups[owner[p]]]
    need(len(expanded) == 334, '334 expanded coordinates')
    for i,(p,a) in enumerate(expanded):
        for j,(q,b) in enumerate(expanded):
            need(int(marked[p] == marked[q])*pairing[a,b] == int(i == j),
                 'canonical full-group expansion equals I334')
    def invoice(ps):
        closure = sorted({a for p in ps for a in groups[owner[p]]})
        rows = [sum(pairing[a,b] << j for j,b in enumerate(closure)) for a in closure]
        return binary_rank(rows)
    costs = [invoice(ps) for ps in marks]
    dimensions = [sum(len(groups[owner[p]]) for p in ps) for ps in marks]
    need(costs == dimensions, 'each canonical mark attains its expanded identity rank')
    need(Counter(costs) == {3:3,6:53,7:1} and sum(costs) == 334,
         'all canonical invoices, with residual and singleton charges')
    ordinary = [j for j,ps in enumerate(marks) if len(ps) == 2]
    chosen = ordinary[:3]
    local = [(p,a) for p,a in expanded if marked[p] in chosen]
    need(len(local) == 18, 'three ordinary marks have 18 expanded coordinates')
    for i,(p,a) in enumerate(local):
        for j,(q,b) in enumerate(local):
            need(int(marked[p] == marked[q])*pairing[a,b] == int(i == j),
                 'three-mark endpoint expands to I18')
    return {'physical_groups':len(groups),'ports':112,'canonical_marks':len(marks),
            'group_size_counts':dict(sorted(Counter(map(len,groups)).items())),
            'mark_size_counts':dict(sorted(Counter(map(len,marks)).items())),
            'expanded_dimension':334,'expanded_entries_checked':334**2,
            'canonical_mark_invoices':costs,'canonical_mark_expanded_dimensions':dimensions,
            'canonical_invoice':sum(costs),'ordinary_mark_count':len(ordinary),
            'local_three_mark_indices':chosen,'local_expanded_dimension':18,
            'local_expanded_entries_checked':18**2,'local_invoice':sum(costs[j] for j in chosen)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt',action='store_true')
    args=parser.parse_args()
    need([[x!=0 for x in q] for q in Q] == [[x!=0 for x in b] for b in B],
         'identical source patterns')
    requests=[]
    for j in range(3):
        target=[int(i==j) for i in range(3)]
        recover_q=[]; recover_f4=[]
        for mask in range(64):
            q=[Q[k] for k in range(6) if mask>>k&1]
            b=[B[k] for k in range(6) if mask>>k&1]
            if rank(q,'Q') == rank(q+[target],'Q'):
                recover_q.append(mask)
                need(rank(b,'F4') == rank(b+[target],'F4'),
                     'every old recovery survives: target %s mask %s'%(j,mask))
            if rank(b,'F4') == rank(b+[target],'F4'):
                recover_f4.append(mask)
        minimal=[m for m in recover_q if not any(n != m and n&m==n for n in recover_q)]
        requests.append({'target':j,'Q_recoverable_masks':recover_q,
                         'F4_recoverable_masks':recover_f4,
                         'Q_minimal_masks':minimal})
    need(rank(Q[3:],'Q') == 2, 'old difference triangle is dependent')
    need(rank(B[3:],'F4') == 3, 'new difference triangle becomes independent')
    old_lines = [list(ids) for ids in combinations(range(6),3)
                 if rank([Q[i] for i in ids],'Q') == 2]
    new_lines = [list(ids) for ids in combinations(range(6),3)
                 if rank([B[i] for i in ids],'F4') == 2]
    need(old_lines == [[0,1,3],[0,2,4],[1,2,5],[3,4,5]], 'four old query lines')
    need(new_lines == old_lines[:3], 'only the target-free line is released')
    need(all(rank([Q[i] for i in ids],'Q') == 2 and
             rank([B[i] for i in ids],'F4') == 2
             for ids in combinations(range(6),2)), 'all query pairs independent')
    axes = [[int(i==j) for i in range(3)] for j in range(3)]
    augmented_q,augmented_b = axes+Q,axes+B
    changed = []
    for mask in range(512):
        rq=rank([augmented_q[i] for i in range(9) if mask>>i&1],'Q')
        rb=rank([augmented_b[i] for i in range(9) if mask>>i&1],'F4')
        if rq != rb:
            changed.append([mask,rq,rb])
    need(changed == [[448,2,3]], 'exactly one query-only circuit-hyperplane relaxation')
    receipt={'geometry':geometry(),'source_sha256':PINS,'scope':'one exact dictionary, all supports; arbitrary physical embedding and actual readers follow in proof',
             'Q_columns':Q,'F4_columns':B,'F4_encoding':'2=w, 3=w+1, w^2+w+1=0',
             'checked_target_support_requests':192,'requests':requests,
             'Q_dependent_triples':old_lines,'F4_dependent_triples':new_lines,
             'checked_augmented_subset_ranks':512,'changed_augmented_ranks':changed,
             'difference_triangle_ranks':{'Q':2,'F4':3},
             'verdict':'PASS'}
    payload=json.dumps(receipt,indent=2)+'\n'
    path=Path(__file__).with_name('RESULT.json')
    if args.write_receipt:
        path.write_text(payload,encoding='utf-8',newline='\n')
    else:
        need(path.is_file(),'missing receipt')
        need(path.read_text(encoding='utf-8')==payload,'receipt mismatch')
    print('PASS_SELECTIVE_CIRCUIT_RELAXATION: 192 recoveries, 512 augmented subsets, I334 and local I18')


if __name__=='__main__':
    main()
