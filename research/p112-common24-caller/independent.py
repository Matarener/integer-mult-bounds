#!/usr/bin/env python3
"""Separate finite-core check: Cramer's rule, affine generator spaces, subset joins.

No primary or predecessor executable is imported. Same author/assistant context;
this is computational corroboration, not independent human or kernel acceptance.
Chris R / Clear1nsight with substantial OpenAI Codex assistance; Apache-2.0.
"""
import ast
from collections import Counter, defaultdict
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST_SHA = '4d49389e8131d6ec139722f60e12d697e4d0d31eba205b5e6d11543d22b4afd3'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key,value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def sources():
    raw = (HERE/'SOURCES.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest identity')
    result = {}
    for row in json.loads(raw,object_pairs_hook=unique)['files']:
        if row['usage'] != 'input':
            continue
        p = ROOT/row['path']
        need(not any(x.is_symlink() for x in [p,*p.parents]), 'input symlink')
        data = p.read_bytes()
        need(len(data)<=2_000_000 and hashlib.sha256(data).hexdigest()==row['sha256'], 'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'], 'Git blob')
        result[row['path']] = data
    return result


def determinant(matrix):
    a = [list(row) for row in matrix]
    previous,sign = 1,1
    for k in range(len(a)-1):
        pivot = next((i for i in range(k,len(a)) if a[i][k]),None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k],a[pivot] = a[pivot],a[k]
            sign = -sign
        p = a[k][k]
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                value = p*a[i][j]-a[i][k]*a[k][j]
                need(value%previous == 0, 'Bareiss exact division')
                a[i][j] = value//previous
            a[i][k] = 0
        previous = p
    return sign*a[-1][-1]


def reconstruct(payloads):
    text = payloads['research/one-sided-six-multisets/data/data.txt'].decode().splitlines()
    live_rows = [tuple(map(int,line.split())) for line in text[2:114]]
    geometry = ast.parse(payloads['research/p112-root-simplex-exclusion/geometry.py'])
    simple = next(ast.literal_eval(n.value) for n in geometry.body if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=='SIMPLE' for t in n.targets))
    frame = {tuple((2 if k==i else 2*s if k==i+1 else 0) for k in range(8))
             for i in range(0,8,2) for s in [-1,1]}
    all_rows = set()
    for i,j in combinations(range(8),2):
        for sign in [-1,1]:
            all_rows.add(tuple(2 if k==i else 2*sign if k==j else 0 for k in range(8)))
    for tail in product([-1,1],repeat=7):
        if sum(x<0 for x in tail)%2 == 0:
            all_rows.add((1,*tail))
    roots = sorted(all_rows)
    need(len(roots)==120 and sorted(all_rows-frame)==live_rows, 'literal E8 shell/frame')
    matrix = [list(row) for row in zip(*simple)]
    det = determinant(matrix)
    need(det != 0, 'simple system invertible')
    labels = []
    for r in roots:
        coords = []
        for j in range(8):
            modified = [row[:] for row in matrix]
            for i in range(8):
                modified[i][j] = r[i]
            numerator = determinant(modified)
            need(numerator%det==0, 'integral Cramer coordinates')
            coords.append(numerator//det)
        need(all(sum(coords[j]*simple[j][i] for j in range(8))==r[i] for i in range(8)), 'Cramer reconstruction')
        labels.append(1+sum((x%2)<<(j+1) for j,x in enumerate(coords)))
    live = sum(1<<i for i,r in enumerate(roots) if r not in frame)
    need([x for i,x in enumerate(labels) if live>>i&1] == list(map(int,text[0].split())), 'original label binding')
    return roots,labels,live


def affine_inventory(labels):
    point = {x>>1:1<<i for i,x in enumerate(labels)}
    inventory = Counter({0:255})  # seven-spaces contained in the leading-zero hyperplane
    spaces = 0
    for pivots in combinations(range(8),6):
        free = [j for j in range(8) if j not in pivots]
        entries = [(i,j) for i,p in enumerate(pivots) for j in free if j>p]
        for word in range(1<<len(entries)):
            rows = [1<<p for p in pivots]
            for bit,(i,j) in enumerate(entries):
                if word>>bit&1:
                    rows[i] |= 1<<j
            values = [0]
            for row in rows:
                values += [x^row for x in values]
            spaces += 1
            for bits in range(4):
                offset = sum((bits>>i&1)<<j for i,j in enumerate(free))
                mask = 0
                for x in values:
                    mask |= point.get(x^offset,0)
                inventory[mask] += 1
    need(spaces==10795 and sum(inventory.values())==43435, 'affine subspace domain')
    return inventory


def core(roots,labels,live,inventory):
    records, traces = [], Counter()
    for a,normal in enumerate(roots):
        word = sum(1<<i for i,r in enumerate(roots) if live>>i&1 and sum(x*y for x,y in zip(r,normal)))
        for mask,multiplicity in inventory.items():
            traces[(word&mask).bit_count()] += multiplicity
            cut = word&~mask
            if cut.bit_count()<=24:
                records.extend([(a,mask,cut)]*multiplicity)
    records.sort()
    owners = defaultdict(set)
    for a,_,cut in records:
        owners[cut].add(a)
    small = [c for c in owners if c.bit_count()==21]
    medium = [c for c in owners if c.bit_count()==23]
    candidates = {c for c in owners if c.bit_count()>=23}
    joins20,joins22 = defaultdict(list),defaultdict(list)
    for s in small:
        for bit in range(120):
            if s>>bit&1:
                joins20[s^(1<<bit)].append(s)
    for s in medium:
        positions = [1<<i for i in range(120) if s>>i&1]
        for bit in positions:
            joins22[s^bit].append(s)
        for x,y,z in combinations(positions,3):
            for t in joins20.get(s^x^y^z,()):
                candidates.add(s|t)
    for group in joins22.values():
        for s,t in combinations(group,2):
            candidates.add(s|t)
    edges = [(s,t) for s,t in combinations(small,2) if (s|t).bit_count()<=24]
    degrees = Counter(c for pair in edges for c in pair)
    need(len(small)==336 and len(edges)==168 and set(degrees.values())=={1}, 'small-cut matching')
    admitted,counts = [],Counter()
    for p in sorted(candidates):
        normals = set(owners.get(p,()))
        positions = [1<<i for i in range(120) if p>>i&1]
        if len(positions)==24:
            for bit in positions:
                normals.update(owners.get(p^bit,()))
        for deleted in combinations(positions,len(positions)-21):
            q = p
            for bit in deleted:
                q ^= bit
            normals.update(owners.get(q,()))
        need(len(normals)<=2, 'independent common24 upper bound')
        ns = sorted(normals)
        counts[(p.bit_count(),len(ns))] += 1
        admitted.append((p,ns))
    return {'spaces7':sum(inventory.values()),
            'full_trace7_histogram':{str(k):v for k,v in sorted(Counter({s:sum(n for m,n in inventory.items() if m.bit_count()==s) for s in set(m.bit_count() for m in inventory)}).items())},
            'flat_inventory_digest':digest(sorted(inventory.items())),
            'root_trace_histogram':{str(k):v for k,v in sorted(traces.items())},
            'critical_records':len(records), 'critical_record_digest':digest(records),
            'unique_cuts':len(owners), 'small_cut_matching_edges':len(edges),
            'analysis':{'candidate_sizes':{str(s):sum(p.bit_count()==s for p in candidates) for s in [23,24]},
                        'candidate_direction_histogram':{f'{s}:{n}':v for (s,n),v in sorted(counts.items())},
                        'candidate_admission_digest':digest(admitted),'maximum_directions':2}}


def compute():
    roots,labels,live = reconstruct(sources())
    return core(roots,labels,live,affine_inventory(labels))


def main():
    need(not sys.argv[1:], 'no arguments accepted')
    observed = compute()
    expected = json.loads((HERE/'RESULT.json').read_bytes(),object_pairs_hook=unique)
    for key,value in observed.items():
        target = {k:expected[key][k] for k in value} if key=='analysis' else expected[key]
        need(json.dumps(value,sort_keys=True)==json.dumps(target,sort_keys=True), 'independent receipt mismatch: '+key)
    print('PASS_COMMON24_INDEPENDENT affine_spaces=43180 leading_zero=255 Cramer_roots=120 subset_join_candidates=8540')


if __name__ == '__main__':
    main()
