"""Portable complete whole-triad cost stage. Standard library; no search/network.

Regenerates all oriented geometry cases, authenticates compact expected minima,
and exhaustively proves those minima by carry-free packed integer arithmetic.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
PINS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}

def need(value, message):
    if not value:
        raise ValueError(message)

def digest(value):
    return sha256(json.dumps(value, separators=(',', ':'), sort_keys=True).encode()).hexdigest()

def read(path, expected=None):
    raw = path.read_bytes()
    need(len(raw) <= 2_097_152, 'bounded cost-stage input')
    if expected is not None:
        need(sha256(raw).hexdigest() == expected, 'source hash: ' + path.name)
    return json.loads(raw)

def basis(values):
    pivots = [0] * 9
    for value in values:
        for p in range(8, -1, -1):
            if value >> p & 1:
                if pivots[p]:
                    value ^= pivots[p]
                else:
                    pivots[p] = value
                    break
    for p in range(9):
        if pivots[p]:
            for q in range(p + 1, 9):
                if pivots[q] >> p & 1:
                    pivots[q] ^= pivots[p]
    return tuple(x for x in pivots if x)

def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)

def geometry(root, orientations=None):
    candidate = read(root / next(iter(PINS)), PINS[next(iter(PINS))])
    data = read(root / list(PINS)[1], PINS[list(PINS)[1]])
    labels = {r['port']: r['q'] for r in data['recipes']}
    groups, targets = candidate['groups'], candidate['factor_supports']
    need(len(labels) == 112 and set(labels) == set(range(112)), 'literal112 labels')
    need(len(groups) == 38 and len(groups[0]) == 1 and all(len(g) == 3 for g in groups[1:]), 'line and37 triads')
    need(sorted(sum(groups, [])) == list(range(112)), 'complete physical partition')
    need(len(targets) == 57 and sorted(sum(targets, [])) == list(range(112)), '57 canonical indicators')
    owner = {p: g for g, ports in enumerate(groups) for p in ports}
    E = [[labels[p] for p in g] for g in groups]
    need(all(((x & y).bit_count() & 1) == int(i == j) for g in E for i, x in enumerate(g) for j, y in enumerate(g)), 'own group Gram')
    signatures = [tuple(sorted(owner[p] for p in t)) for t in targets]
    for sig in signatures:
        need(len(sig) == len(set(sig)), 'distinct physical groups in target')
        need(all((x & y).bit_count() % 2 == 0 for a, b in combinations(sig, 2) for x in E[a] for y in E[b]), 'mutually orthogonal target groups')
    need(sum(len(E[g]) for sig in signatures for g in sig) == 334, 'original334 invoice')
    classes = Counter(tuple(sorted(signatures[i] for i in t)) for t in combinations(range(57), 3))
    prices, spaces = {}, set()
    def charge(A, B):
        key = (A, B) if A <= B else (B, A)
        if key not in prices:
            prices[key] = rank(sum(((x & y).bit_count() & 1) << j for j, y in enumerate(B)) for x in A)
        return prices[key]
    envelopes, actual = {}, {}
    orders = list(permutations(range(3))) if orientations is None else orientations
    oriented_count = literal_orders = 0
    for sigs, multiplicity in classes.items():
        gs = sorted(set(sum(map(list, sigs), [])))
        unions = [basis(x for i, g in enumerate(gs) if mask >> i & 1 for x in E[g]) for mask in range(1 << len(gs))]
        spaces.update(unions)
        n = len(unions)
        table = bytes(charge(a, b) for a in unions for b in unions)
        for order in orders:
            names, shape = [], []
            for j in order:
                row = []
                for g in sigs[j]:
                    if g not in names:
                        names.append(g)
                    row.append(names.index(g))
                shape.append(tuple(row))
            dims = tuple(len(E[g]) for g in names)
            key = (tuple(shape), dims)
            ix = [sum(1 << gs.index(g) for i, g in enumerate(names) if s >> i & 1) for s in range(n)]
            oriented = bytes(table[a * n + b] for a in ix for b in ix)
            if key not in envelopes:
                envelopes[key] = [oriented, 0, 0]
            else:
                envelopes[key][0] = bytes(map(min, zip(envelopes[key][0], oriented)))
            envelopes[key][1] += 1
            envelopes[key][2] += multiplicity
            actual[(key, oriented)] = actual.get((key, oriented), 0) + 1
            oriented_count += 1
            literal_orders += multiplicity
    shape_list = []
    for key, (table, count, literal) in sorted(envelopes.items()):
        shape, dims = key
        shape_list.append({'shape': shape, 'dimensions': dims, 'table': table,
                           'geometries': count, 'literal_orders': literal,
                           'original': sum(dims[g] for s in shape for g in s)})
    metadata = {'signature_classes': len(classes), 'literal_triples': sum(classes.values()),
                'orientations': oriented_count, 'literal_orders': literal_orders,
                'spaces': len(spaces), 'shapes': len(shape_list)}
    return shape_list, actual, metadata

def raw_states(shape, families):
    states = {(0, 0, 0, 0, 0)}
    for a, gs in enumerate(shape):
        for g in gs:
            options = [tuple((1 << g) if mask >> t & 1 else 0 for t in range(5)) for mask in families[a]]
            states = {tuple(x | y for x, y in zip(old, option)) for old in states for option in options}
    return states

def row_classes(table, n):
    groups, ids = {}, []
    for i in range(n):
        row = table[i * n:(i + 1) * n]
        groups.setdefault(row, i)
        ids.append(groups[row])
    need(all(table[i * n + j] == table[j * n + i] for i in range(n) for j in range(n)), 'symmetric tariff quotient')
    return ids

def reduce_states(states, ids):
    return sorted({tuple(ids[s] for s in row) for row in states})

def exact_minimum(table, n, left, right, expected):
    """Certify every pair >=expected, and at least one pair ==expected."""
    need(left and right and 0 <= expected <= 45 and all(0 <= x <= 9 for x in table), 'packed cost ranges')
    if len(left) < len(right):
        left, right = right, left
    count = len(right)
    one = ((1 << (8 * count)) - 1) // 255
    high = one * 128
    below, upto = (127 + expected) * one, (128 + expected) * one
    costs = []
    for term in range(5):
        categories = {}
        for i, row in enumerate(right):
            value = row[term]
            if value not in categories:
                categories[value] = bytearray(count)
            categories[value][i] = 1
        packed = [(value, int.from_bytes(slots, 'little')) for value, slots in categories.items()]
        costs.append({s: sum(code * table[s * n + v] for v, code in packed) for s in {r[term] for r in left}})
    attained = False
    for row in left:
        invoice = sum(costs[t][row[t]] for t in range(5))
        need(((below - invoice) & high) == 0, 'cheaper support assignment than certified minimum')
        attained |= bool((upto - invoice) & high)
    need(attained, 'certified minimum has an attaining support assignment')

def validate_metadata(shapes, metadata, receipt):
    need(metadata == receipt['geometry'], 'complete geometry coverage and orientations')
    need(len(shapes) == len(receipt['envelopes']), 'no missing incidence shape')
    for i, (actual, stored) in enumerate(zip(shapes, receipt['envelopes'])):
        need(stored['index'] == i and list(map(list, actual['shape'])) == stored['shape'] and list(actual['dimensions']) == stored['dimensions'], 'ordered shape/dimension identity')
        need(actual['geometries'] == stored['geometries'] and actual['literal_orders'] == stored['literal_orders'], 'all incidence multiplicities')
        need(actual['original'] == stored['original'], 'correct original physical invoice')
        need(sha256(actual['table']).hexdigest() == stored['tariff_sha256'], 'all regenerated envelope tariff entries')

def run(root=HERE.parents[1], receipt=None):
    receipt = read(HERE / 'COSTS.json') if receipt is None else receipt
    support = read(HERE / 'SUPPORT-TRANSFER.json', receipt['support_sha256'])['remaining_classes']
    need([r['index'] for r in support] == receipt['class_indices'] and len(support) == 135, 'exact support frontier ordering')
    shapes, actual, metadata = geometry(root)
    validate_metadata(shapes, metadata, receipt)
    raw_cache = {}
    def states(shape, r, side, ids):
        families = tuple(map(tuple, r[side + '_minimal_masks']))
        key = (shape, families)
        if key not in raw_cache:
            raw_cache[key] = raw_states(shape, families)
        return reduce_states(raw_cache[key], ids)
    open_cells, closed, total = {}, 0, 0
    for i, e in enumerate(shapes):
        raw_cache.clear()
        n = 1 << len(e['dimensions'])
        ids = row_classes(e['table'], n)
        minima = receipt['envelopes'][i]['minima']
        need(len(minima) == len(support), 'complete envelope class list')
        for r, minimum in zip(support, minima):
            L = states(e['shape'], r, 'source', ids)
            R = states(e['shape'], r, 'reader', ids)
            exact_minimum(e['table'], n, L, R, minimum)
            total += 1
            if minimum < e['original']:
                open_cells.setdefault(i, []).append(r)
            else:
                closed += 1
    need((total, closed, total - closed) == (6075, 6015, 60), 'all exact envelope minima')
    by_shape = {(e['shape'], e['dimensions']): i for i, e in enumerate(shapes)}
    actual_cases = [(by_shape[key], table, count) for (key, table), count in actual.items() if by_shape[key] in open_cells]
    actual_cases.sort(key=lambda item: (item[0], sha256(item[1]).hexdigest()))
    coverage = [[i, sha256(table).hexdigest(), count] for i, table, count in actual_cases]
    need(len(actual_cases) == 7542 and sum(c for i, t, c in actual_cases) == 8466, 'complete actual geometry quotient')
    need(digest(coverage) == receipt['actual_coverage_sha256'], 'all actual tables and multiplicities')
    jobs = []
    previous_shape = None
    for i, table, count in actual_cases:
        if i != previous_shape:
            raw_cache.clear()
            previous_shape = i
        e = shapes[i]
        n = 1 << len(e['dimensions'])
        ids = row_classes(table, n)
        for r in open_cells[i]:
            L = states(e['shape'], r, 'source', ids)
            R = states(e['shape'], r, 'reader', ids)
            exact_minimum(table, n, L, R, e['original'])
            jobs.append([i, sha256(table).hexdigest(), r['index'], e['original']])
    jobs.sort()
    need(len(jobs) == 27304 and digest(jobs) == receipt['actual_minima_sha256'], 'complete actual cost-job receipt')
    return {'status': 'passed', **metadata, 'envelope_entries': sum(len(e['table']) for e in shapes),
            'envelope_jobs': total, 'closed_envelope_jobs': closed, 'open_envelope_jobs': total - closed,
            'actual_tables': len(actual_cases), 'actual_jobs': len(jobs), 'saving_patterns': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    print(json.dumps(run(args.root), sort_keys=True))
