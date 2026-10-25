"""Independent cost replay: explicit annihilators and seven-bit packed lanes.

No imports from the producer or predecessor verifiers. Standard library only.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
ALL = (1 << 512) - 1

def check(ok, message):
    if not ok:
        raise ValueError(message)

def load(path, pin=None):
    raw = path.read_bytes()
    check(len(raw) <= 2_097_152, 'bounded input')
    if pin is not None:
        check(sha256(raw).hexdigest() == pin, 'pinned input: ' + path.name)
    return json.loads(raw)

def receipt_hash(rows):
    return sha256(json.dumps(rows, separators=(',', ':'), sort_keys=True).encode()).hexdigest()

def members(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b

def dimension(space):
    size = space.bit_count()
    check(size > 0 and size & (size - 1) == 0, 'vector-space cardinality')
    return size.bit_length() - 1

def build_geometry(root):
    candidate = load(root / 'research/p112-rational-decoder-gate/CANDIDATE.json',
                     'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b')
    labels = load(root / 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json',
                  'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa')
    q = {r['port']: r['q'] for r in labels['recipes']}
    groups = candidate['groups']
    check(sorted(q) == list(range(112)), '112 label domain')
    check(len(groups) == 38 and len(groups[0]) == 1 and all(len(g) == 3 for g in groups[1:]), 'one residual line and37 triads')
    check(sorted(sum(groups, [])) == list(range(112)), 'full physical partition')
    E = [[q[p] for p in ports] for ports in groups]
    check(all(((x & y).bit_count() % 2) == (i == j) for e in E for i, x in enumerate(e) for j, y in enumerate(e)), 'orthonormal groups')
    # Derive the canonical targets independently from the matched triad axes.
    columns = [[groups[g][a], groups[g + 1][a]] for g in range(1, 37, 2) for a in range(3)]
    columns.extend([[p] for p in groups[37]])
    columns[21].append(groups[0][0])
    check(sorted(map(sorted, columns)) == sorted(map(sorted, candidate['factor_supports'])), 'literal canonical projector supports')
    check(sorted(sum(columns, [])) == list(range(112)), 'target partition')
    owners = {p: g for g, ports in enumerate(groups) for p in ports}
    signatures = [tuple(sorted(owners[p] for p in c)) for c in columns]
    hyperplanes = [sum(1 << x for x in range(512) if (x & y).bit_count() % 2 == 0) for y in range(512)]
    perps = []
    for e in E:
        value = ALL
        for x in e:
            value &= hyperplanes[x]
        perps.append(value)
    spaces, pairings = {}, {}
    def space(perp):
        if perp not in spaces:
            primal = ALL
            for y in members(perp):
                primal &= hyperplanes[y]
            d = 9 - dimension(perp)
            check(dimension(primal) == d, 'double annihilator')
            spaces[perp] = (primal, d)
        return spaces[perp]
    def tariff(a, b):
        key = frozenset((a, b))
        if key not in pairings:
            A, d = space(a)
            B, e = space(b)
            value = d - dimension(A & b)
            check(value == e - dimension(B & a), 'symmetric physical pairing')
            pairings[key] = value
        return pairings[key]
    original = 0
    for sig in signatures:
        perp = ALL
        for g in sig:
            perp &= perps[g]
        baseline = sum(len(E[g]) for g in sig)
        check(tariff(perp, perp) == baseline, 'canonical whole-group invoice')
        original += baseline
    check(original == 334, 'original334')
    classes = Counter(tuple(sorted(signatures[i] for i in triple)) for triple in combinations(range(57), 3))
    envelopes, actual = {}, {}
    total_orders = total_literal = 0
    for sigs, multiplicity in classes.items():
        physical = sorted(set(g for sig in sigs for g in sig))
        n = 1 << len(physical)
        subset_perps = [ALL] * n
        for s in range(1, n):
            bit = s & -s
            subset_perps[s] = subset_perps[s ^ bit] & perps[physical[bit.bit_length() - 1]]
        matrix = tuple(tuple(tariff(a, b) for b in subset_perps) for a in subset_perps)
        for order in permutations(range(3)):
            names, incidence = [], []
            for j in order:
                row = []
                for g in sigs[j]:
                    if g not in names:
                        names.append(g)
                    row.append(names.index(g))
                incidence.append(tuple(row))
            dims = tuple(len(E[g]) for g in names)
            key = (tuple(incidence), dims)
            old_bits = [1 << physical.index(g) for g in names]
            conversion = [sum(old_bits[i] for i in members(s)) for s in range(n)]
            table = bytes(matrix[i][j] for i in conversion for j in conversion)
            if key not in envelopes:
                envelopes[key] = [bytearray(table), 0, 0]
            current = envelopes[key]
            for z, value in enumerate(table):
                if value < current[0][z]:
                    current[0][z] = value
            current[1] += 1
            current[2] += multiplicity
            identity = (key, table)
            actual[identity] = actual.get(identity, 0) + 1
            total_orders += 1
            total_literal += multiplicity
    metadata = {'signature_classes': len(classes), 'literal_triples': sum(classes.values()),
                'orientations': total_orders, 'literal_orders': total_literal,
                'spaces': len(spaces), 'shapes': len(envelopes)}
    return [(key, bytes(v[0]), v[1], v[2]) for key, v in sorted(envelopes.items())], actual, metadata

def union_configurations(incidence, alternatives):
    configurations = {(0,) * 5}
    for target, physical in enumerate(incidence):
        for group in physical:
            next_configurations = set()
            for query_mask in alternatives[target]:
                terms = tuple(members(query_mask))
                for old in configurations:
                    new = list(old)
                    for t in terms:
                        new[t] |= 1 << group
                    next_configurations.add(tuple(new))
            configurations = next_configurations
    return configurations

def equivalent_rows(table, n):
    representative = {}
    ids = []
    for i in range(n):
        row = tuple(table[i * n:i * n + n])
        representative.setdefault(row, i)
        ids.append(representative[row])
    check(all(table[i * n + j] == table[j * n + i] for i in range(n) for j in range(n)), 'symmetric table')
    return ids

def verify_minimum(table, n, left, right, minimum):
    """Seven-bit additive guards, distinct from the byte subtraction checker."""
    check(left and right and 0 <= minimum <= 45 and all(0 <= x <= 9 for x in table), 'safe lane ranges')
    if len(right) > len(left):
        left, right = right, left
    count = len(right)
    unit = ((1 << (7 * count)) - 1) // 127
    signs = unit * 64
    lower_guard = (64 - minimum) * unit
    upper_guard = (63 - minimum) * unit
    weights = []
    for t in range(5):
        positions = {}
        for i, row in enumerate(right):
            positions[row[t]] = positions.get(row[t], 0) | (1 << (7 * i))
        weights.append({a: sum(code * table[a * n + b] for b, code in positions.items()) for a in {s[t] for s in left}})
    attained = False
    for row in left:
        invoice = sum(weights[t][row[t]] for t in range(5))
        check((invoice + lower_guard) & signs == signs, 'all configurations meet minimum')
        attained |= (invoice + upper_guard) & signs != signs
    check(attained, 'minimum attained')

def run(root=HERE.parents[1]):
    receipt = load(HERE / 'COSTS.json')
    frontier = load(HERE / 'SUPPORT-TRANSFER.json', receipt['support_sha256'])['remaining_classes']
    check(len(frontier) == 135 and [r['index'] for r in frontier] == receipt['class_indices'], 'complete stable frontier')
    envelopes, actual, metadata = build_geometry(root)
    check(metadata == receipt['geometry'], 'all physical geometry cases')
    check(len(envelopes) == len(receipt['envelopes']), 'complete incidence list')
    cache = {}
    def configurations(incidence, alternatives, ids):
        key = (incidence, tuple(map(tuple, alternatives)))
        if key not in cache:
            cache[key] = union_configurations(*key)
        return sorted({tuple(ids[g] for g in row) for row in cache[key]})
    open_cells = {}
    envelope_jobs = envelope_entries = 0
    for i, ((incidence, dims), table, count, literal) in enumerate(envelopes):
        cache.clear()
        stored = receipt['envelopes'][i]
        check(stored['index'] == i and stored['shape'] == list(map(list, incidence)) and stored['dimensions'] == list(dims), 'ordered incidence and residual dimensions')
        baseline = sum(dims[g] for target in incidence for g in target)
        check((count, literal, baseline) == (stored['geometries'], stored['literal_orders'], stored['original']), 'multiplicities and original charge')
        check(sha256(table).hexdigest() == stored['tariff_sha256'], 'entire envelope matrix')
        envelope_entries += len(table)
        n = 1 << len(dims)
        ids = equivalent_rows(table, n)
        check(len(stored['minima']) == len(frontier), 'no omitted cost class')
        for row, minimum in zip(frontier, stored['minima']):
            L = configurations(incidence, row['source_minimal_masks'], ids)
            R = configurations(incidence, row['reader_minimal_masks'], ids)
            verify_minimum(table, n, L, R, minimum)
            envelope_jobs += 1
            if minimum < baseline:
                open_cells.setdefault(i, []).append(row)
    check(envelope_jobs == 6075 and sum(map(len, open_cells.values())) == 60 and envelope_entries == 93780, 'complete envelope screen')
    index = {key: i for i, (key, table, count, literal) in enumerate(envelopes)}
    cases = sorted((index[key], sha256(table).hexdigest(), table, count) for (key, table), count in actual.items() if index[key] in open_cells)
    coverage = [[i, h, count] for i, h, table, count in cases]
    check(len(cases) == 7542 and sum(v[2] for v in coverage) == 8466, 'all actual geometry cases')
    check(receipt_hash(coverage) == receipt['actual_coverage_sha256'], 'actual table coverage hash')
    jobs = []
    previous = None
    for i, h, table, count in cases:
        if i != previous:
            cache.clear()
            previous = i
        (incidence, dims), _, _, _ = envelopes[i]
        baseline = sum(dims[g] for target in incidence for g in target)
        n = 1 << len(dims)
        ids = equivalent_rows(table, n)
        for row in open_cells[i]:
            L = configurations(incidence, row['source_minimal_masks'], ids)
            R = configurations(incidence, row['reader_minimal_masks'], ids)
            verify_minimum(table, n, L, R, baseline)
            jobs.append([i, h, row['index'], baseline])
    check(len(jobs) == 27304 and receipt_hash(sorted(jobs)) == receipt['actual_minima_sha256'], 'all actual cost minima')
    return {'status': 'passed', **metadata, 'envelope_entries': envelope_entries, 'envelope_jobs': envelope_jobs,
            'open_envelope_jobs': 60, 'closed_envelope_jobs': 6015, 'actual_tables': len(cases), 'actual_jobs': len(jobs), 'saving_patterns': 0}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=HERE.parents[1])
    args = parser.parse_args()
    print(json.dumps(run(args.root), sort_keys=True))
