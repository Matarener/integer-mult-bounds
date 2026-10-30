#!/usr/bin/env python3
"""PR3538's MMM affine family on the PR2757 whole-triad geometry.

Reuses only this author's adjacent geometry helper, never upstream producer code.
The mathematical reduction/classification is credited in the companion note.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, permutations, product
from pathlib import Path
from types import ModuleType
import json
import time

HELPER = Path(__file__).with_name('independent_vvv.py')
# Execute the adjacent source bytes directly: -B alone still permits reading
# an old bytecode cache, including in a direct Git-free replay.
own = ModuleType('own_geometry')
own.__file__ = str(HELPER)
exec(compile(HELPER.read_bytes(), str(HELPER), 'exec'), own.__dict__)
need, rankq, rank2 = own.need, own.rankq, own.rank2


def values(target, twice_w):
    a, b, c = [int(target == j) for j in range(3)]
    return tuple(F(x, 2) for x in (a+b-twice_w, a+c-twice_w,
                                   b+c-twice_w, twice_w))


def minimize(signatures, geom):
    groups = sorted(set(sum((list(s) for s in signatures), [])))
    group_index = {g: i for i, g in enumerate(groups)}
    ports = [(t, 1 << group_index[g]) for t, ss in enumerate(signatures) for g in ss]
    price = [geom.charge(groups, [g for i, g in enumerate(groups) if mask >> i & 1])
             for mask in range(1 << len(groups))]
    patterns = ((3, 12), (5, 10), (6, 9))
    options = [[tuple(bit if patterns[t][s] >> k & 1 else 0 for k in range(4))
                for s in range(2)] for t, bit in ports]
    best = 1000
    for choice in product(range(2), repeat=len(ports)):
        masks = [0]*4
        for option, state in zip(options, choice):
            for k, bit in enumerate(option[state]):
                masks[k] |= bit
        charges = [price[mask] for mask in masks]
        cost = sum(charges)
        if cost < best:
            best, saved, invoice = cost, list(choice), charges
    return best, saved, invoice, 2**len(ports)


def witness(geom, triple, choice):
    ports = [p for j in triple for p in sorted(geom.cols[j], key=geom.owner.get)]
    states = dict(zip(ports, choice))
    owner = {p: i for i, j in enumerate(triple) for p in geom.cols[j]}
    coordinates = ((1, 1, -1), (1, -1, 1), (-1, 1, 1), (1, 1, 1))
    U = [[F(c[owner[p]]) if p in owner else F(0) for c in coordinates]
         for p in range(112)]
    V = [list(values(owner.get(p, -1), states.get(p, 0))) for p in range(112)]
    for p in range(112):
        for q in range(112):
            got = sum(U[p][t]*V[q][t] for t in range(4))
            want = int(p in owner and q in owner and owner[p] == owner[q])
            need(got == want, 'literal MMM endpoint')
    invoice = [geom.charge([geom.owner[p] for p in range(112) if U[p][t]],
                           [geom.owner[p] for p in range(112) if V[p][t]])
               for t in range(4)]
    return {'triple': list(triple), 'twice_w': choice, 'charges': invoice,
            'local_cost': sum(invoice),
            'global_cost': 334-sum(geom.baseline[j] for j in triple)+sum(invoice),
            'endpoint_entries_checked': 112**2,
            'U': [[str(x) for x in row] for row in U],
            'V': [[str(x) for x in row] for row in V]}


def classification_controls():
    # Check only the new non-Fano orbit/selective-template part of PR3538.
    # The complete23 rank-three line-system classification remains an inherited premise.
    P = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0),
         (1, 0, 1), (0, 1, 1), (1, 1, 1)]
    lines = {frozenset(t) for t in combinations(range(7), 3)
             if rankq([P[i] for i in t]) == 2}
    need(lines == {frozenset(t) for t in ((0,1,3), (0,2,4), (0,5,6),
                                        (1,2,5), (1,4,6), (2,3,6))}, 'six non-Fano lines')
    automorphisms = [p for p in permutations(range(7))
                     if {frozenset(p[i] for i in t) for t in lines} == lines]
    reps = ((0,1,2), (0,1,4), (0,3,4), (3,4,5))
    orbits = [{tuple(sorted(p[i] for i in t)) for p in automorphisms} for t in reps]
    need(len(automorphisms) == 24 and list(map(len, orbits)) == [4,12,12,1],
         'four independent marked-triple orbits')
    need(len(set.union(*orbits)) == 29, 'all independent triples classified')
    templates = [
        ([(-1,0,1),(1,1,0),(-1,1,1),(0,1,1)],
         [(1,0,1),(1,1,0),(1,1,1),(0,1,1)]),
        ([(-1,1,0),(-1,0,1),(-2,1,1),(-1,1,1)],
         [(1,1,0),(1,0,1),(0,1,1),(1,1,1)])]
    true_counts = []
    for rational, binary in templates:
        need(all(not y or x for a, b in zip(rational, binary) for x, y in zip(a,b)),
             'selective query support inclusion')
        count = 0
        for j in range(3):
            target = tuple(int(j == k) for k in range(3))
            for mask in range(16):
                old = [q for t,q in enumerate(rational) if mask >> t & 1]
                if rankq(old) == rankq(old+[target]):
                    new = [sum(x << k for k,x in enumerate(q))
                           for t,q in enumerate(binary) if mask >> t & 1]
                    need(rank2(new) == rank2(new+[1 << j]), 'selective span implication')
                    count += 1
        true_counts.append(count)
    need(true_counts == [14, 15], 'both selective-map counts')
    patterns = ((3,12),(5,10),(6,9))
    for target in range(3):
        for w in (0,1):
            need(sum((x != 0) << k for k,x in enumerate(values(target,w))) == patterns[target][w],
                 'MMM critical support pattern')
        need(all(values(target, 2)), 'other MMM state has all four entries')
    return {'automorphisms': 24, 'marked_orbits': [4,12,12,1],
            'selective_span_requests': true_counts,
            'classification_scope': '23-type rank-three classification inherited, not rerun'}


def run():
    start = time.perf_counter()
    geom = own.Geometry()
    classes = {}
    for triple in combinations(range(57), 3):
        rep = tuple(sorted(triple, key=lambda j: (geom.signatures[j], j)))
        key = tuple(geom.signatures[j] for j in rep)
        if key not in classes:
            classes[key] = [rep, 0]
        classes[key][1] += 1
    rows = []
    histogram = Counter()
    best = None
    for signatures, (triple, multiplicity) in sorted(classes.items()):
        minimum, w, charges, count = minimize(signatures, geom)
        original = sum(geom.baseline[j] for j in triple)
        row = {'signature': [list(s) for s in signatures], 'triple': list(triple), 'multiplicity': multiplicity,
               'original': original, 'minimum': minimum, 'twice_w': w,
               'charges': charges, 'assignments': count}
        rows.append(row)
        histogram[minimum-original] += multiplicity
        if best is None or minimum-original < best['minimum']-best['original']:
            best = row
    need(sum(histogram.values()) == 29260, 'complete literal triple coverage')
    literal = witness(geom, best['triple'], best['twice_w'])
    need(literal['charges'] == best['charges'], 'literal repricing')
    return {'source_pins': own.PINS,
            'scope': 'Dense MMM four-query rays, all rational ambient readers, all57choose3 target triples',
            'credit': 'PR3538 e63a7635da461ae14e562ed4bb26be26a0fdb5f4, PROOF blob ee0665716883b28072db137ea86a837e568f3520',
            'triples': 29260, 'classes': len(rows),
            'assignments': sum(row['assignments'] for row in rows),
            'excess_histogram': dict(sorted(histogram.items())),
            'classification_controls': classification_controls(),
            'classes_results': rows, 'best_literal_witness': literal,
            'geometry_helper_sha256': sha256(HELPER.read_bytes()).hexdigest(),
            'elapsed_seconds': time.perf_counter()-start}



def check_result(result):
    receipt = json.loads(Path(__file__).with_name('RESULT.json').read_bytes())
    expected = receipt['classes']
    actual = result['classes_results']
    need(len(actual) == len(expected), 'independent complete class count')
    for got, want in zip(actual, expected):
        need(got['signature'] == want['signature'], 'independent signature order')
        need(got['multiplicity'] == want['multiplicity'], 'independent literal multiplicity')
        need(got['original'] == want['baseline'], 'independent original bill')
        need(got['minimum'] == want['MMM_minimum'], 'independent actual-reader minimum')
    need(json.loads(json.dumps(result['excess_histogram'])) == receipt['literal_excess_histograms']['MMM'],
         'independent excess histogram')
    need(result['assignments'] == receipt['assignments_per_family']['MMM'], 'independent assignment count')
    need(min(result['excess_histogram']) >= 0, 'no cheaper literal triple')
    return {'family': 'MMM', 'classes': len(actual), 'triples': result['triples'],
            'assignments': result['assignments'], 'excess_histogram': result['excess_histogram'],
            'status': 'PASS_INDEPENDENT_MMM'}


if __name__ == '__main__':
    print(json.dumps(check_result(run()), sort_keys=True))
