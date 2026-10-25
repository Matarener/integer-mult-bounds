#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Separate row-matrix and modular-minor audit, with no primary code imports.

Clear1nsight, substantial OpenAI assistance. A separately coded check in this
same session, not an independent human review or a native execution proof.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBERS = {
    'candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz':
        '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def sparse_add(destination, source, multiplier):
    for key, value in source.items():
        destination[key] = destination.get(key, Fraction(0)) + multiplier*value
        if destination[key] == 0:
            del destination[key]


def push_source_rows(word, backwards=False):
    events = word['precondition'] + word['compensation'] + word['A']
    extent = 1+max(max(e[1:3]) if e[0] == 'add' else e[1] for e in events + word['cut'])
    state = [{i: Fraction(1)} if i < 112 else {} for i in range(extent)]
    if backwards:
        for i in range(112):
            state[112+i] = {i: Fraction(1)}
    for event in events:
        if event[0] == 'scale':
            target = event[1]
            value = Fraction(event[2], event[3])
            need(value != 0, 'invertible scale')
            multiplier = 1/value if backwards else value
            state[target] = {i: x*multiplier for i,x in state[target].items()}
        else:
            need(event[0] == 'add', 'canonical elementary event')
            target, source = event[1:3]
            value = Fraction(event[3], event[4])
            if backwards:
                target, source, value = source, target, -value
            need(target != source, 'distinct elementary roles')
            sparse_add(state[target], state[source], value)
    if not backwards:
        return [[state[c].get(i, Fraction(0)) for i in range(112)] for c in word['centers']]
    rows = []
    for centre in word['centers']:
        out = {}
        for event in word['cut']:
            need(event[0] == 'add', 'canonical cut')
            if event[2] == centre:
                sparse_add(out, state[event[1]], Fraction(event[3], event[4]))
        rows.append([out.get(i, Fraction(0)) for i in range(112)])
    return rows


def transpose(rows):
    n = len(rows)
    return tuple(sum(((rows[i] >> j)&1) << i for i in range(n)) for j in range(n))


def multiply(a,b):
    """Binary row-matrix product, using parity dot products."""
    columns = transpose(b)
    return tuple(sum(((row & col).bit_count()&1) << j for j,col in enumerate(columns)) for row in a)


def own_extract(root):
    path = root / ARCHIVE
    need(path.is_file() and not path.is_symlink(), 'archive regular file')
    need(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA, 'archive SHA256')
    data = []
    with tarfile.open(path) as archive:
        for name,expected in MEMBERS.items():
            matches = [item for item in archive.getmembers() if item.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular member')
            raw = archive.extractfile(matches[0]).read()
            need(sha256(raw).hexdigest() == expected, 'member SHA256')
            data.append(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw))
    word,phases = data
    rows = push_source_rows(word)
    later = push_source_rows(word, True)
    need(later == [[x/4 for x in row] for row in rows], 'independent later query')
    need(phases['m'] == 73 and len(phases['recipes']) == 112, 'source dimensions')
    routes = []
    for index,record in enumerate(phases['recipes']):
        q = record['q']
        axes = record['idle_children'][0]['orthogonal_axes'][:8]
        need(q == word['ports'][index], 'source port ordering')
        basis = [q] + axes
        need(len(basis) == 9 and all(0 < v < 512 for v in basis), 'chart dimensions')
        need(all(((a&b).bit_count()&1) == int(i==j)
                 for i,a in enumerate(basis) for j,b in enumerate(basis)), 'orthonormal chart')
        upper = tuple((q if (q>>i)&1 else 0) |
                      sum(((axis>>i)&1) << (9+j) for j,axis in enumerate(axes)) for i in range(9))
        route = upper+tuple(axes)
        identity = tuple(1<<i for i in range(17))
        need(multiply(route,route) == identity, 'independent involution')
        routes.append(route)
    return rows,routes


def group_from_left(generators):
    identity = tuple(1<<i for i in range(len(generators[0])))
    seen,frontier = {identity},deque([identity])
    while frontier:
        right = frontier.popleft()
        for left in generators:
            item = multiply(left,right)
            if item not in seen:
                need(len(seen) < 10000, 'declared closure bound')
                seen.add(item)
                frontier.append(item)
    return seen


def mod_rank(matrix, prime=101):
    work = [[int(x)%prime for x in row] for row in matrix]
    n = len(work[0])
    rank = 0
    for col in range(n):
        pivot = next((i for i in range(rank,len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank],work[pivot] = work[pivot],work[rank]
        inverse = pow(work[rank][col], -1, prime)
        work[rank] = [(x*inverse)%prime for x in work[rank]]
        for i in range(rank+1,len(work)):
            factor = work[i][col]
            work[i] = [(a-factor*b)%prime for a,b in zip(work[i],work[rank])]
        rank += 1
        if rank == len(work):
            break
    return rank


def audit(rows,routes):
    need(digest({'rows':[[str(x) for x in row] for row in rows], 'routes':[transpose(r) for r in routes]}) ==
         '79515573d8231a59ece664a2ec421983989c9925e1ccab1ca4c71c7cfa3ea2be', 'independent geometry matches source export')
    need(len(rows)==8 and all(len(row)==112 for row in rows), 'eight by112 R')
    need(all(x.denominator==1 for row in rows for x in row), 'integral query coefficients')
    need(mod_rank(rows)==8, 'old rank by finite-field minor')
    a,b,c = (0,6,85)
    need(all(row[a]-row[b]-row[c]==0 for row in rows), 'exact primitive relation')
    need(mod_rank([[row[p] for p in (a,b,c)] for row in rows]) == 2, 'triple exact rank')
    generators = [multiply(routes[a],routes[b]),multiply(routes[b],routes[c])]
    group = group_from_left(generators)
    need(len(group)==4080, 'independent subgroup order')
    unused = set(range(112))
    classes=[]
    while unused:
        p=min(unused)
        block=[q for q in sorted(unused) if multiply(routes[p],routes[q]) in group]
        need(bool(block),'nonempty coset')
        for q in block:
            for r in block:
                need(multiply(routes[q],routes[r]) in group,'pairwise equivalence')
        unused.difference_update(block)
        classes.append(block)
    for block in classes:
        r=mod_rank([[row[p] for p in block] for row in rows])
        need(r==(2 if block==[0,6,85] else len(block)), 'independent coset minor')
    # A separate forward residual check, not just constancy or a receipt hash.
    outputs={}
    for g in group:
        for port,coefficient in ((a,1),(b,-1),(c,-1)):
            d=multiply(g,routes[port])
            out=outputs.setdefault(d,[0]*8)
            for k in range(8):
                out[k] += coefficient*int(rows[k][port])
    need(len(outputs)==4080 and all(not any(v) for v in outputs.values()), 'all later residuals vanish')
    # Drop one owner. Involutions are distinct, hence exactly three failures.
    identity=tuple(1<<i for i in range(17))
    for port,coefficient in ((a,1),(b,-1),(c,-1)):
        d=multiply(identity,routes[port])
        for k in range(8):
            outputs[d][k] -= coefficient*int(rows[k][port])
    need(sum(any(v) for v in outputs.values())==3,'dropped owner has three outputs')
    # Union-find connectivity, using the two different generators above.
    parents={g:g for g in group}
    def find(g):
        while parents[g]!=g:
            parents[g]=parents[parents[g]]
            g=parents[g]
        return g
    joins=0
    for g in sorted(group):
        for generator in generators:
            left,right=find(g),find(multiply(g,generator))
            if left!=right:
                parents[left]=right
                joins+=1
    need(joins==4079,'independent graph rank4079')
    geometry={'rows':[[str(x)for x in row]for row in rows], 'routes':[transpose(r)for r in routes]}
    return {'status':'PASS_INDEPENDENT_CENTRE_SHEAF','geometry_sha256':digest(geometry),
            'owners':4080,'old_rank_mod101':8,'right_coset_classes':classes,
            'class_size_histogram':{str(k):v for k,v in Counter(map(len,classes)).items()},
            'compatibility_rank':joins,'nonzero_later_residuals':0,
            'dropped_owner_nonzero_outputs':3,'joint_kernel_dimension':1,
            'additional_linear_observations':424319,
            'method':'Independent sparse forward source propagation, row matrices, left closure, mod101 minors, direct residuals and union-find.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geometry',type=Path)
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    if args.geometry:
        raw=json.loads(args.geometry.read_bytes())
        rows=[[Fraction(x) for x in row] for row in raw['rows']]
        routes=[transpose(tuple(row)) for row in raw['routes']]
        mode='derived geometry only; archive not read'
    else:
        rows,routes=own_extract(args.root)
        mode='independently parsed pinned archive'
    result=audit(rows,routes)
    result['source_mode']=mode
    print('INDEPENDENT_JSON='+json.dumps(result,sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
