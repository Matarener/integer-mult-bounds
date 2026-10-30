#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound finite algebra/event checks; no physical supplier admission."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parabolic import (require, identity, multiply, inverse, row_add, word_matrix,
                       compile_banks, complete_model, inverse_groups, route_groups,
                       invoice, direct_residual, diagonal_word)
HERE = Path(__file__).resolve().parent
WORD_SHA = 'e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e'


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    sources = json.loads((HERE/'SOURCES.json').read_bytes())
    for row in sources['retained']:
        p = HERE/row['path']
        require(p.is_file() and not p.is_symlink(), 'retained source missing or linked')
        b = p.read_bytes()
        require(hashlib.sha256(b).hexdigest() == row['sha256'], 'retained source hash')
        require(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest() == row['git_blob'], 'retained source blob')
    raw = (HERE/'inputs/r437-word.json.gz').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == WORD_SHA, 'R437 exact word pin')
    return json.loads(gzip.decompress(raw))


def rational_projector(rows):
    # Reconstruct the one-dimensional orthogonal complement; no predecessor imports.
    a = [[Fraction(x) for x in row] for row in rows]
    pivots, k, n = [], 0, len(a[0])
    for j in range(n):
        p = next((i for i in range(k, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[k], a[p] = a[p], a[k]
        scalar = a[k][j]
        a[k] = [x/scalar for x in a[k]]
        for i in range(len(a)):
            if i != k:
                scalar = a[i][j]
                a[i] = [x-scalar*y for x, y in zip(a[i], a[k])]
        pivots.append(j)
        k += 1
    free = [j for j in range(n) if j not in pivots]
    require(len(free) == 1 and len(pivots) == 7, 'literal rank-seven hyperplane')
    v = [Fraction(int(j == free[0])) for j in range(n)]
    for i, j in enumerate(pivots):
        v[j] = -a[i][free[0]]
    norm = sum(x*x for x in v)
    return [[Fraction(i == j)-v[i]*v[j]/norm for j in range(n)] for i in range(n)]


def modular(a, modulus):
    return [[x.numerator*pow(x.denominator, -1, modulus) % modulus for x in row] for row in a]


def generated_unit(n, modulus, seed):
    rng = random.Random(seed)
    ans = identity(n)
    for _ in range(4*n):
        i, j = rng.sample(range(n), 2)
        row_add(ans, i, j, rng.randrange(modulus), modulus)
    return ans


def reject(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('accepted negative control: '+label)


def finite_payload():
    n, rank, modulus = 2, 1, 3
    q = [[0, 0], [1, 1]]
    weights = [2, 1]
    banks = compile_banks(q, rank, weights, modulus)
    vector_events = []
    for backwards in (True, False):
        if not backwards:
            vector_events.append(('swap', 0, n, 0))
        for bank in ('head', 'tail'):
            groups = inverse_groups(banks[bank]) if backwards else banks[bank]
            offset = n if bank == 'tail' else 0
            vector_events += [(op, i+offset, j+offset, a) for op,i,j,a in route_groups(groups,n,rank,bank=='tail')]
    addresses = list(product(range(modulus), repeat=2*n))
    index = {a:i for i,a in enumerate(addresses)}
    source = tuple(random.Random(17000+i).randrange(2) for i in range(3*2*len(addresses)))
    # All distinct physical prefixes, including equal field-header labels, survive.
    current = source
    for op,i,j,a in reversed(vector_events):
        transformed = []
        for prefix in range(3):
            for spectator in range(2):
                base = (2*prefix+spectator)*len(addresses)
                for x in addresses:
                    y = list(x)
                    if op == 'swap':
                        y[i],y[j] = y[j],y[i]
                    else:
                        y[i] = (y[i]+a*y[j]) % modulus
                    transformed.append(current[base+index[tuple(y)]])
        current = tuple(transformed)
    matrix = direct_residual(q,weights,modulus)
    expected = []
    for prefix in range(3):
        for spectator in range(2):
            base = (2*prefix+spectator)*len(addresses)
            for x in addresses:
                y = tuple(sum(a*b for a,b in zip(row,x)) % modulus for row in matrix)
                expected.append(source[base+index[y]])
    require(current == tuple(expected), 'actual event pullback on every payload cell')
    dirty_targets = [[(i+target)%2 for i in range(len(source))] for target in range(63)]
    original_targets = [row[:] for row in dirty_targets]
    private = list(current)
    for row in dirty_targets:
        row[:] = [a^b for a,b in zip(row,private)]
    require(all(row == [a^b for a,b in zip(old,private)] for row,old in zip(dirty_targets,original_targets)), 'all 63 dirty readers')
    # Model-only cleanup of the actual private buffer after its last reader.
    # Physical erasure, head restoration and scan cost remain backend premises.
    completed_targets = [row[:] for row in dirty_targets]
    require(any(private), 'nonzero private-buffer disposal control')
    for i in range(len(private)):
        private[i] = 0
    require(not any(private), 'model private buffer erased in place')
    require(dirty_targets == completed_targets, 'cleanup preserves completed dirty targets')
    require(source == tuple(random.Random(17000+i).randrange(2) for i in range(len(source))), 'cleanup preserves borrowed source')
    return {'addresses':len(addresses),'physical_prefixes':3,'spectators':2,'payload_bits':len(source),'dirty_readers':63,'primitive_events':len(vector_events)}


def calculate():
    word = authenticate()
    require(word['R'] == 437 and word['ret'] == list(range(470,479)), 'current R437 captures')
    current = word['start'][:]
    for section in ('D','A'):
        for frame,target,sources in word[section]:
            for role in [target]+sources:
                current[role] = frame
    require([current[c] for c in word['ret']] == list(range(510,519)), 'capture frames')
    contexts, support_hashes, projector_hashes = 0,set(),[]
    for centre in word['ret']:
        p = rational_projector([word['lines'][i] for i in word['frames'][current[centre]]])
        projector_hashes.append(hashlib.sha256(canonical([[str(x) for x in row] for row in p])).hexdigest())
        for prime,w in [(3,1),(3,2),(5,2),(7,2),(11,1)]:
            modulus=prime**w
            g=generated_unit(8,modulus,centre*prime+w)
            q=multiply(multiply(g,modular(p,modulus),modulus),inverse(g,modulus),modulus)
            units=[i for i in range(1,modulus) if i%prime]
            weights=[units[i%len(units)] for i in range(8)]
            result=complete_model(q,7,weights,modulus)
            support_hashes.add(hashlib.sha256(canonical(result['supports'])).hexdigest())
            contexts+=1
    require(len(support_hashes)==1,'one ordered operation support across every tested low/high/weight class')
    # Entire GL2(F3), all rank-one conjugates and all diagonal unit weights.
    exhaustive=0
    for values in product(range(3),repeat=4):
        g=[list(values[:2]),list(values[2:])]
        if (g[0][0]*g[1][1]-g[0][1]*g[1][0])%3 == 0:
            continue
        q=multiply(multiply(g,[[1,0],[0,0]],3),inverse(g,3),3)
        for weights in product((1,2),repeat=2):
            complete_model(q,1,list(weights),3)
            exhaustive+=1
    # Bad leading minor in full ambient64, with nonzero graph factors and weights.
    n,r,modulus=64,7,9
    rng=random.Random(5348)
    upper=[(i,r+k,rng.randrange(modulus)) for i in range(r) for k in range(n-r)]
    lower=[(r+k,i,rng.randrange(modulus)) for k in range(n-r) for i in range(r)]
    # Multiples of3 in the graph ensure the last7 principal block stays a unit.
    graph=word_matrix([(i,j,3*(a%3)) for i,j,a in upper+lower],n,modulus)
    perm=identity(n)
    for i in range(r): perm[i],perm[n-r+i]=perm[n-r+i],perm[i]
    t=multiply(perm,graph,modulus)
    e=[[int(i==j and i<r) for j in range(n)] for i in range(n)]
    q=multiply(multiply(t,e,modulus),inverse(t,modulus),modulus)
    require(all(q[i][j]%3==0 for i in range(r) for j in range(r)), 'bad leading chart is truly singular')
    weights=[1+3*(i%3) for i in range(n)]
    ambient=complete_model(q,r,weights,modulus,list(range(n-r,n)))
    controls=[]
    interleaved=[(0,1,1),(1,0,-1),(0,1,1),(0,2,1),(2,0,-1),(0,2,1)]
    grouped=[(0,1,1),(0,2,1),(1,0,-1),(2,0,-1),(0,1,1),(0,2,1)]
    controls.append(reject(lambda: require(word_matrix(interleaved,3,3)==word_matrix(grouped,3,3),'one-hot flags required'), 'two active pivot flags'))
    controls.append(reject(lambda: complete_model(q,r,weights,modulus,list(range(r))), 'force bad leading chart'))
    controls.append(reject(lambda: complete_model(q,r,[3]+weights[1:],modulus,list(range(n-r,n))), 'nonunit ancestor weight'))
    controls.append(reject(lambda: complete_model(q,6,weights,modulus,list(range(n-6,n))), 'wrong rank'))
    small=[[0,0],[1,1]]
    bb=compile_banks(small,1,[2,1],3)
    correct=complete_model(small,1,[2,1],3)['matrix']
    controls.append(reject(lambda: require(correct==direct_residual(small,[1,1],3),'weights matter'), 'drop ancestor weights'))
    events=route_groups(bb['head'],2,1)
    from parabolic import execute
    trimmed=events[:]
    first=next(i for i,x in enumerate(trimmed) if x[0]=='swap')
    del trimmed[first]
    controls.append(reject(lambda: require(execute(trimmed,2,3)==execute(events,2,3),'routing restoration matters'), 'omit one router swap'))
    controls.append(reject(lambda: require(invoice()['swap']==0,'ordinary bill nonzero'), 'free ordinary adapters'))
    b=Fraction(17,10000)
    target=Fraction(1736646042038446578551,10**24)
    gaps={name:str((1+target)*(1-rate)-1) for name,rate in [('B1',b*(1-b)),('B2',b*(1-b*b))]}
    require(all(Fraction(g)>0 for g in gaps.values()),'same positive exponent gap')
    return {'status':'PASS_PARABOLIC_COPY_RELATIVE_CONSTRUCTION','source_capture_projector_hashes':projector_hashes,
            'literal_contexts':contexts,'full_GL2_weighted_contexts':exhaustive,'full_ambient64_cases':1,
            'fixed_support_hash_8':next(iter(support_hashes)),'ambient64_invoice':ambient['counts'],
            'one_reversed_child_width':'7f','old_alternate_add_per_column':41832,'old_alternate_ordinary_calls':41832,
            'power_gaps':gaps,'finite_payload':finite_payload(),'semantic_controls':controls,
            'physical_backend_implemented':False,'inherited_cheap_tariff_proved':False,'supplier_admitted':False}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=calculate()
    if args.write:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        expected=json.loads((HERE/'RESULT.json').read_bytes())
        require(canonical(expected)==canonical(result),'exact result receipt')
    print(result['status'],json.dumps(result['ambient64_invoice'],sort_keys=True), 'contexts=45+192+1')

if __name__=='__main__': main()
