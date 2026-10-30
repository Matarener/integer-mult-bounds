#!/usr/bin/env python3
"""Complete all-Q affine readers for four fixed queries on the 57 triad columns.

The affine reduction is credited to upstream p112-nonfano-affine-reader.
This file independently applies it to the PR2757 whole-triad geometry.
No producer imports, external dependencies, or network calls.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import time

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
    'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
    'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def read_pin(path):
    raw = (ROOT / path).read_bytes()
    need(sha256(raw).hexdigest() == PINS[path], 'source hash: ' + path)
    return json.loads(raw)


def rank2(values):
    pivots = {}
    for x in values:
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return len(pivots)


def rankq(rows):
    A = [list(map(F, row)) for row in rows]
    r = 0
    for c in range(len(A[0]) if A else 0):
        p = next((p for p in range(r, len(A)) if A[p][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pivot = A[r][c]
        A[r] = [x / pivot for x in A[r]]
        for p in range(r + 1, len(A)):
            f = A[p][c]
            if f:
                A[p] = [x - f*y for x, y in zip(A[p], A[r])]
        r += 1
    return r


class Geometry:
    def __init__(self):
        C = read_pin(next(iter(PINS)))
        D = read_pin(list(PINS)[1])
        self.groups = C['groups']
        q = {r['port']: r['q'] for r in D['recipes']}
        need(len(q) == 112 and set(q) == set(range(112)), '112 labels')
        need(len(self.groups) == 38 and len(self.groups[0]) == 1,
             '38 physical groups')
        need(all(len(g) == 3 for g in self.groups[1:]), '37 triads')
        self.owner = {p: g for g, ports in enumerate(self.groups) for p in ports}
        need(len(self.owner) == 112, 'partition')
        self.E = [[q[p] for p in ports] for ports in self.groups]
        need(all(((a & b).bit_count() & 1) == (i == j)
                 for E in self.E for i, a in enumerate(E)
                 for j, b in enumerate(E)), 'own Gram identities')
        self.cache = {}
        free = [[a, b] for a, b in combinations(range(38), 2)
                if self.charge((a,), (b,)) == 0]
        need(free == C['orthogonal_group_pairs'], 'complete free graph')
        self.cols = []
        for g in range(1, 37, 2):
            for axis in range(3):
                self.cols.append([self.groups[g][axis], self.groups[g+1][axis]])
        self.cols += [[p] for p in self.groups[37]]
        self.cols[21].append(self.groups[0][0])
        need(len(self.cols) == 57 and sorted(sum(self.cols, [])) == list(range(112)),
             '57 disjoint target indicators partition112')
        self.signatures = [tuple(sorted(self.owner[p] for p in c)) for c in self.cols]
        self.baseline = [self.charge(s, s) for s in self.signatures]
        need(sum(self.baseline) == 334, 'canonical334')

    def charge(self, left, right):
        a, b = tuple(sorted(set(left))), tuple(sorted(set(right)))
        key = (a, b) if a <= b else (b, a)
        if key not in self.cache:
            X = [x for g in a for x in self.E[g]]
            Y = [y for g in b for y in self.E[g]]
            self.cache[key] = rank2(sum(((x & y).bit_count() & 1) << j
                                         for j, y in enumerate(Y)) for x in X)
        return self.cache[key]

    def expanded_identity(self):
        mark = {p: j for j, col in enumerate(self.cols) for p in col}
        slots = [(p, x) for p in range(112) for x in self.E[self.owner[p]]]
        need(len(slots) == 334, 'expanded334 slots')
        for i, (p, x) in enumerate(slots):
            for j, (r, y) in enumerate(slots):
                entry = int(mark[p] == mark[r]) * ((x & y).bit_count() & 1)
                need(entry == int(i == j), 'literal I334 expansion')
        return {'dimension': 334, 'entries': 334**2, 'rank': 334}


# Bits are term support in order ab, ac, bc, abc; choices w=0,+1,-1.
PATTERNS = ((7, 12, 11), (7, 10, 13), (7, 9, 14))
WVALUES = (0, 1, -1)


def affine_values(target, w):
    a, b, c = [int(target == j) for j in range(3)]
    return ((F(a+b-c)-w)/2, (F(a-b+c)-w)/2,
            (F(-a+b+c)-w)/2, F(w))


def minimize(signatures, geom):
    groups = sorted(set(sum((list(s) for s in signatures), [])))
    bits = {g: 1 << i for i, g in enumerate(groups)}
    source = [set(signatures[0]+signatures[1]),
              set(signatures[0]+signatures[2]),
              set(signatures[1]+signatures[2]), set(groups)]
    tariffs = [[geom.charge(s, [g for i, g in enumerate(groups) if mask >> i & 1])
                for mask in range(1 << len(groups))] for s in source]
    ports = [(t, bits[g]) for t, ss in enumerate(signatures) for g in ss]
    options = []
    for t, bit in ports:
        options.append([tuple(bit if pat >> k & 1 else 0 for k in range(4))
                        for pat in PATTERNS[t]])
    best = 1000
    best_choice = None
    best_charges = None
    for choice in product(range(3), repeat=len(ports)):
        masks = [0, 0, 0, 0]
        for option, state in zip(options, choice):
            entry = option[state]
            for k in range(4):
                masks[k] |= entry[k]
        charges = [tariffs[k][masks[k]] for k in range(4)]
        cost = sum(charges)
        if cost < best:
            best, best_choice, best_charges = cost, choice, charges
    return best, [WVALUES[i] for i in best_choice], best_charges, 3**len(ports)


def literal_witness(geom, triple, ws):
    # Match the minimizer's group-sorted port order within each target.
    ports = [p for j in triple for p in sorted(geom.cols[j], key=geom.owner.get)]
    need(len(ws) == len(ports), 'witness dimensions')
    W = dict(zip(ports, map(F, ws)))
    target = {p: t for t, j in enumerate(triple) for p in geom.cols[j]}
    query_targets = ((0, 1), (0, 2), (1, 2), (0, 1, 2))
    U = [[F(int(p in target and target[p] in ts)) for ts in query_targets]
         for p in range(112)]
    V = [list(affine_values(target.get(p, -1), W.get(p, F(0))))
         for p in range(112)]
    for p in range(112):
        for r in range(112):
            got = sum(U[p][k]*V[r][k] for k in range(4))
            expected = int(p in target and r in target and target[p] == target[r])
            need(got == expected, 'literal four-query endpoint')
    charges = [geom.charge([geom.owner[p] for p in range(112) if U[p][k]],
                           [geom.owner[p] for p in range(112) if V[p][k]])
               for k in range(4)]
    return {'triple': list(triple), 'w': ws, 'charges': charges,
            'local_cost': sum(charges), 'global_cost': 334-sum(geom.baseline[j] for j in triple)+sum(charges),
            'endpoint_entries_checked': 112**2,
            'U': [[str(x) for x in row] for row in U],
            'V': [[str(x) for x in row] for row in V]}


def controls(geom):
    for t in range(3):
        for k, w in enumerate(WVALUES):
            mask = sum((x != 0) << i for i, x in enumerate(affine_values(t, w)))
            need(mask == PATTERNS[t][k], 'all three exact reader patterns')
        need(all(affine_values(t, F(2))), 'generic w full support')
        need(all(affine_values(t, F(1, 3))), 'fractional generic w full support')
    need(affine_values(-1, 0) == (0, 0, 0, 0), 'external zero dominates')
    need(all(affine_values(-1, 2)), 'external nonzero all four')
    # Characteristic-two failure: rational pair sums are independent, binary are not.
    pair = [[1, 1, 0], [1, 0, 1], [0, 1, 1]]
    need(rankq(pair) == 3 and rank2([3, 5, 6]) == 2, 'non-Fano triangle control')
    # Missing the negative critical value loses a non-dominated pattern.
    need(not any((PATTERNS[0][i] & PATTERNS[0][2]) == PATTERNS[0][i]
                 for i in (0, 1)), 'w=-1 cannot be discarded')
    return ['three incomparable critical patterns', 'generic and external domination',
            'rational versus binary triangle rank', 'negative-critical omission rejected']


def run():
    started = time.perf_counter()
    geom = Geometry()
    expansion = geom.expanded_identity()
    checks = controls(geom)
    classes = {}
    for triple in combinations(range(57), 3):
        representative = tuple(sorted(triple, key=lambda j: (geom.signatures[j], j)))
        key = tuple(geom.signatures[j] for j in representative)
        if key not in classes:
            classes[key] = [representative, 0]
        classes[key][1] += 1
    rows = []
    histogram = Counter()
    assignments = 0
    best = None
    for signatures, (triple, multiplicity) in sorted(classes.items()):
        cost, ws, charges, count = minimize(signatures, geom)
        original = sum(geom.baseline[j] for j in triple)
        row = {'signature': [list(s) for s in signatures], 'triple': list(triple), 'multiplicity': multiplicity,
               'original': original, 'minimum': cost, 'w': ws, 'charges': charges,
               'assignments': count}
        rows.append(row)
        assignments += count
        histogram[cost-original] += multiplicity
        if best is None or cost-original < best['minimum']-best['original']:
            best = row
    need(sum(row['multiplicity'] for row in rows) == 29260, 'all57choose3 triples')
    witness = literal_witness(geom, best['triple'], best['w'])
    need(witness['charges'] == best['charges'], 'literal witness repriced')
    return {'scope': 'Fixed four non-Fano queries on any three PR2757 canonical target columns; arbitrary rational ambient readers',
            'credit': 'Affine reduction: upstream research/p112-nonfano-affine-reader/PROOF.md',
            'source_pins': PINS, 'baseline': 334, 'identity_expansion': expansion,
            'triples': 29260, 'classes': len(rows), 'assignments': assignments,
            'excess_histogram': dict(sorted(histogram.items())), 'controls': checks,
            'classes_results': rows, 'best_literal_witness': witness,
            'elapsed_seconds': time.perf_counter()-started}



def check_result(result):
    receipt = json.loads(Path(__file__).with_name('RESULT.json').read_bytes())
    expected = receipt['classes']
    actual = result['classes_results']
    need(len(actual) == len(expected), 'independent complete class count')
    for got, want in zip(actual, expected):
        need(got['signature'] == want['signature'], 'independent signature order')
        need(got['multiplicity'] == want['multiplicity'], 'independent literal multiplicity')
        need(got['original'] == want['baseline'], 'independent original bill')
        need(got['minimum'] == want['VVV_minimum'], 'independent actual-reader minimum')
    need(json.loads(json.dumps(result['excess_histogram'])) == receipt['literal_excess_histograms']['VVV'],
         'independent excess histogram')
    need(result['assignments'] == receipt['assignments_per_family']['VVV'], 'independent assignment count')
    need(min(result['excess_histogram']) >= 0, 'no cheaper literal triple')
    return {'family': 'VVV', 'classes': len(actual), 'triples': result['triples'],
            'assignments': result['assignments'], 'excess_histogram': result['excess_histogram'],
            'status': 'PASS_INDEPENDENT_VVV'}


if __name__ == '__main__':
    print(json.dumps(check_result(run()), sort_keys=True))
