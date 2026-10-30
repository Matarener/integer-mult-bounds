#!/usr/bin/env python3
"""Separate finite-core check: Cramer's rule, affine generator spaces, all compatible quadruples.

Shell/Cramer/affine routines adapted with credit from PR3960; new graph and
quadruple check here. No primary or predecessor executable is imported. Same author/assistant context;
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



def compute():
    roots,labels,live = reconstruct(sources())
    inventory = affine_inventory(labels)
    records = []
    for a,h in enumerate(roots):
        word = sum(1<<i for i,r in enumerate(roots) if live>>i&1 and sum(x*y for x,y in zip(r,h)))
        for flat,multiplicity in inventory.items():
            cut = word & ~flat
            if cut.bit_count() <= 30:
                records.extend([(a,flat,cut)]*multiplicity)
    records.sort()
    nodes = sorted({(a,c) for a,f,c in records})
    adjacent = [set() for _ in nodes]
    # A different pair traversal and a direct all-quadruple test, without prefix pruning.
    grouped = [[i for i,(a,c) in enumerate(nodes) if a==normal] for normal in range(120)]
    edges = []
    for left,right in combinations(grouped,2):
        for i in left:
            cut = nodes[i][1]
            for j in right:
                if (cut | nodes[j][1]).bit_count() <= 30:
                    adjacent[i].add(j); adjacent[j].add(i); edges.append((i,j))
    triangles,quadruples = Counter(),Counter()
    for i,j in edges:
        for k in adjacent[i] & adjacent[j]:
            if k<=j:
                continue
            cut = nodes[i][1] | nodes[j][1] | nodes[k][1]
            if cut.bit_count()>30:
                continue
            normals = [roots[nodes[q][0]] for q in [i,j,k]]
            gram = [[sum(x*y for x,y in zip(a,b)) for b in normals] for a in normals]
            det = determinant(gram)
            need(det>=0 and cut.bit_count()==30, 'all triples require common30')
            triangles[(cut.bit_count(),det>0)] += 1
            for q in adjacent[i] & adjacent[j] & adjacent[k]:
                if q<=k:
                    continue
                joined = cut | nodes[q][1]
                if joined.bit_count()>30:
                    continue
                four = normals+[roots[nodes[q][0]]]
                gram4 = [[sum(x*y for x,y in zip(a,b)) for b in four] for a in four]
                need(determinant(gram4)==0, 'independent compatible quadruple')
                quadruples[joined.bit_count()] += 1
    need(triangles[(30,True)]>0, 'independent triple exists')
    return {'spaces7':sum(inventory.values()),'flat_inventory_digest':digest(sorted(inventory.items())),
            'critical_records':len(records),'critical_record_digest':digest(records),
            'nodes':len(nodes),'node_digest':digest(nodes),'edges':len(edges),'edge_digest':digest(sorted(edges))},triangles,quadruples


def main():
    need(not sys.argv[1:], 'no arguments accepted')
    observed,triangles,quadruples = compute()
    expected = json.loads((HERE/'RESULT.json').read_bytes(),object_pairs_hook=unique)
    for key,value in observed.items():
        need(json.dumps(value,sort_keys=True)==json.dumps(expected[key],sort_keys=True),'independent receipt mismatch '+key)
    need(triangles=={(30,False):896,(30,True):3584},'complete triangle histogram')
    # This includes quadruples whose first three directions are dependent.
    need(quadruples=={30:3360},'complete quadruple histogram')
    print('PASS_COMMON30_INDEPENDENT Cramer_roots=120 affine_spaces=43435 triangles=4480 all_quadruples=3360 span=3')


if __name__=='__main__':
    main()
