"""Independent exact VVV/MMM triad census by group-wise reader closure unions.

Standard library only. Reads pinned sources, prints JSON, writes no files.
No primary census or predecessor executable is imported.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parents[1]
LABEL_PATH = 'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json'
COVER_PATH = 'research/p112-rational-decoder-gate/CANDIDATE.json'
LABEL_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
COVER_SHA = 'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b'
VVV = ((7, 12, 11), (7, 10, 13), (7, 9, 14))
MMM = ((3, 12), (5, 10), (6, 9))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pinned(path, digest):
    with path.open('rb') as stream:
        raw = stream.read(2_097_153)
    need(len(raw) <= 2_097_152, 'source input capacity')
    need(sha256(raw).hexdigest() == digest, 'source SHA256: ' + str(path))
    return json.loads(raw)


def load(root):
    data = pinned(root / LABEL_PATH, LABEL_SHA)
    candidate = pinned(root / COVER_PATH, COVER_SHA)
    labels = [row['q'] for row in sorted(data['recipes'], key=lambda row: row['port'])]
    groups = candidate['groups']
    targets = candidate['factor_supports']
    need(len(labels) == 112 and len(set(labels)) == 112, '112 labels')
    need(len(groups) == 38 and len(groups[0]) == 1, '38 physical groups')
    need(all(len(g) == 3 for g in groups[1:]), '37 triads')
    need(sorted(p for g in groups for p in g) == list(range(112)), 'group partition')
    need(len(targets) == 57 and sorted(p for s in targets for p in s) == list(range(112)),
         '57 disjoint canonical targets')
    for group in groups:
        need(all(((labels[x] & labels[y]).bit_count() % 2) == int(i == j)
                 for i, x in enumerate(group) for j, y in enumerate(group)),
             'physical group Gram identity')
    owner = {p: i for i, group in enumerate(groups) for p in group}
    signatures = [tuple(sorted(owner[p] for p in target)) for target in targets]
    for signature in signatures:
        need(len(signature) == len(set(signature)), 'one target port per physical group')
        need(all((labels[p] & labels[q]).bit_count() % 2 == 0
                 for i, j in combinations(signature, 2)
                 for p in groups[i] for q in groups[j]), 'orthogonal target groups')
    return labels, groups, targets, signatures


def binary_rank(columns):
    """Column elimination on the raw rectangular Gram matrix, without source reduction."""
    pivots = {}
    for original in columns:
        column = original
        while column:
            leading = column.bit_length() - 1
            if leading in pivots:
                column ^= pivots[leading]
            else:
                pivots[leading] = column
                break
    return len(pivots)


def rank_table(source, active, labels, groups):
    source_ports = [p for g in source for p in groups[g]]
    columns = [tuple(sum(((labels[p] & labels[q]).bit_count() % 2) << i
                         for i, p in enumerate(source_ports)) for q in groups[g])
               for g in active]
    need(len(active) <= 7 and len(source_ports) <= 19, 'triple geometry capacities')
    return [binary_rank(col for i, block in enumerate(columns) if mask >> i & 1
                        for col in block) for mask in range(1 << len(active))]


def local_choices(target_types, choices):
    """Count reader-term unions generated within ONE complete physical group."""
    states = {0: (1, ())}
    for target_type in target_types:
        update = {}
        for old, (count, witness) in states.items():
            for value, added in enumerate(choices[target_type]):
                union = old | added
                if union not in update:
                    update[union] = (count, witness + (value,))
                else:
                    previous, kept = update[union]
                    update[union] = (previous + count, kept)
        states = update
    need(sum(count for count, _ in states.values()) == len(choices[0]) ** len(target_types),
         'group choice partition')
    return states


def solve(signature, family, labels, groups):
    active = sorted(set().union(*map(set, signature)))
    terms = [tuple(t for t, s in enumerate(signature) if g in s) for g in active]
    choices = VVV if family == 'VVV' else MMM
    local = [local_choices(types, choices) for types in terms]
    a, b, c = map(set, signature)
    sources = [a | b, a | c, b | c, a | b | c] if family == 'VVV' else [a | b | c] * 4
    tables = [rank_table(sorted(source), active, labels, groups) for source in sources]
    best = None
    minimizer_count = states_checked = weighted_assignments = 0
    first_patterns = None
    for patterns in product(*(tuple(state) for state in local)):
        reader_masks = [sum((1 << j) for j, value in enumerate(patterns) if value >> i & 1)
                        for i in range(4)]
        invoice = sum(table[mask] for table, mask in zip(tables, reader_masks))
        ways = 1
        for state, pattern in zip(local, patterns):
            ways *= state[pattern][0]
        weighted_assignments += ways
        states_checked += 1
        if best is None or invoice < best:
            best, minimizer_count, first_patterns = invoice, ways, patterns
        elif invoice == best:
            minimizer_count += ways
    raw_assignments = len(choices[0]) ** sum(map(len, signature))
    need(weighted_assignments == raw_assignments, 'full assignment coverage')
    witness = [[] for _ in range(3)]
    for g, types, state, pattern in zip(active, terms, local, first_patterns):
        for target_type, value in zip(types, state[pattern][1]):
            witness[target_type].append([g, value])
    return {'minimum': best, 'assignments': raw_assignments, 'closure_states': states_checked,
            'minimizer_assignments': minimizer_count, 'witness': witness}


def collect(signatures):
    classes = {}
    for triple in combinations(range(57), 3):
        key = tuple(sorted(signatures[t] for t in triple))
        if key not in classes:
            classes[key] = {'multiplicity': 0, 'first_triple': triple}
        classes[key]['multiplicity'] += 1
    need(sum(item['multiplicity'] for item in classes.values()) == 29260, 'all literal triples')
    need(len(classes) == 1519, 'complete physical signature classes')
    return classes


def controls():
    need(binary_rank([1, 2, 3]) == 2, 'rank dependence control')
    need(binary_rank([1, 2, 4]) == 3, 'rank independence control')
    need(local_choices((0,), VVV)[12][0] == 1, 'VVV positive source type')
    need(set(local_choices((0,), MMM)) == {3, 12}, 'MMM complementary choices')
    for family in (VVV, MMM):
        for types in ((0, 1), (0, 1, 2), (0,), (2,)):
            direct = Counter()
            for pattern in product(*(family[t] for t in types)):
                result = 0
                for item in pattern:
                    result |= item
                direct[result] += 1
            need(direct == Counter({key: value[0] for key, value in local_choices(types, family).items()}),
                 'independent tiny group powerset control')


def operator_fixture(row, family, targets, signatures, labels, groups):
    ordered = sorted(row['first_literal_triple'], key=lambda t: (signatures[t], t))
    basis = [[int(p in targets[t]) for p in range(112)] for t in ordered]
    owner = {p: g for g, members in enumerate(groups) for p in members}
    chosen = row[family]['witness']
    w = [0] * 112
    for t, target in enumerate(ordered):
        values = dict(chosen[t])
        for port in targets[target]:
            index = values[owner[port]]
            w[port] = (0, 1, -1)[index] if family == 'VVV' else index
    a, b, c = basis
    if family == 'VVV':
        q = [[a[p]+b[p], a[p]+c[p], b[p]+c[p], a[p]+b[p]+c[p]] for p in range(112)]
        twice_u = [[a[p]+b[p]-c[p]-w[p], a[p]-b[p]+c[p]-w[p],
                    -a[p]+b[p]+c[p]-w[p], 2*w[p]] for p in range(112)]
    else:
        q = [[a[p]+b[p]-c[p], a[p]-b[p]+c[p], -a[p]+b[p]+c[p],
              a[p]+b[p]+c[p]] for p in range(112)]
        twice_u = [[a[p]+b[p]-w[p], a[p]+c[p]-w[p], b[p]+c[p]-w[p], w[p]]
                   for p in range(112)]
    for p in range(112):
        for r in range(112):
            expected = 2*sum(v[p]*v[r] for v in basis)
            need(sum(twice_u[p][i]*q[r][i] for i in range(4)) == expected,
                 'full literal doubled operator')
    costs = []
    for term in range(4):
        source = sorted({owner[p] for p in range(112) if q[p][term]})
        reader = sorted({owner[p] for p in range(112) if twice_u[p][term]})
        source_ports = [p for g in source for p in groups[g]]
        reader_ports = [p for g in reader for p in groups[g]]
        costs.append(binary_rank(sum(((labels[p]&labels[r]).bit_count()%2) << k
                                     for k,p in enumerate(source_ports)) for r in reader_ports))
    need(sum(costs) == row[family]['minimum'], 'literal witness actual reader tariff')
    return {'family': family, 'targets': ordered, 'operator_entries': 12544,
            'term_costs': costs, 'total': sum(costs)}


def run(root, summary_only):
    authenticate_inputs(root)
    controls()
    labels, groups, targets, signatures = load(root)
    classes = collect(signatures)
    hist = {name: Counter() for name in ('VVV', 'MMM')}
    class_hist = {name: Counter() for name in ('VVV', 'MMM')}
    assignment_totals = Counter()
    state_totals = Counter()
    rows = []
    for signature, record in sorted(classes.items()):
        baseline = sum(len(groups[g]) for s in signature for g in s)
        solved = {name: solve(signature, name, labels, groups) for name in ('VVV', 'MMM')}
        for name, value in solved.items():
            excess = value['minimum'] - baseline
            hist[name][excess] += record['multiplicity']
            class_hist[name][excess] += 1
            assignment_totals[name] += value['assignments']
            state_totals[name] += value['closure_states']
        rows.append({'signature': signature, 'multiplicity': record['multiplicity'],
                     'first_literal_triple': record['first_triple'], 'baseline': baseline,
                     **solved})
    fixtures = []
    for family in ('VVV', 'MMM'):
        tied = next(row for row in rows if row[family]['minimum'] == row['baseline'])
        for row in (rows[0], tied):
            fixtures.append(operator_fixture(row, family, targets, signatures, labels, groups))
    result = {'source_main': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
              'source_pins': {LABEL_PATH: LABEL_SHA, COVER_PATH: COVER_SHA},
              'method': 'Complete physical-group reader union states with assignment multiplicities',
              'signatures': len(classes), 'literal_triples': sum(v['multiplicity'] for v in classes.values()),
              'assignments_per_family': dict(assignment_totals),
              'closure_states_per_family': dict(state_totals),
              'literal_excess_histograms': {name: dict(sorted(value.items())) for name, value in hist.items()},
              'signature_excess_histograms': {name: dict(sorted(value.items())) for name, value in class_hist.items()},
              'literal_operator_fixtures': fixtures,
              'per_signature_sha256': sha256(json.dumps(rows, separators=(',', ':')).encode()).hexdigest(),
              'status': 'PASS' if all(min(v) >= 0 for v in hist.values()) else 'CHEAPER_WITNESS'}
    check_receipt(rows, result)
    if not summary_only:
        result['per_signature'] = rows
    print(json.dumps(result, separators=(',', ':')))



def authenticate_inputs(root):
    manifest = json.loads((HERE / 'SOURCES.json').read_bytes())
    for entry in manifest['files']:
        if entry['usage'] == 'input':
            with (root / entry['path']).open('rb') as stream:
                raw = stream.read(2_097_153)
            need(len(raw) <= 2_097_152, 'proof input capacity')
            need(sha256(raw).hexdigest() == entry['sha256'], 'proof input hash: ' + entry['path'])
    for entry in manifest['retained_sources']:
        raw = (HERE / entry['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == entry['sha256'], 'retained proof hash')


def check_receipt(rows, result):
    with (HERE / 'RESULT.json').open('rb') as stream:
        raw = stream.read(2_097_153)
    need(len(raw) <= 2_097_152, 'receipt capacity')
    receipt = json.loads(raw)
    expected = receipt['classes']
    projected = [{'signature': [list(s) for s in r['signature']],
                  'multiplicity': r['multiplicity'], 'baseline': r['baseline'],
                  'VVV_minimum': r['VVV']['minimum'], 'MMM_minimum': r['MMM']['minimum']}
                 for r in rows]
    need(projected == expected, 'complete per-signature minima and multiplicities')
    need(result['status'] == 'PASS', 'no literal triple saving')
    for name in ('signatures', 'literal_triples', 'assignments_per_family',
                 'closure_states_per_family', 'literal_excess_histograms',
                 'signature_excess_histograms', 'per_signature_sha256'):
        actual = json.loads(json.dumps(result[name]))
        need(actual == receipt[name], 'exact result field: ' + name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--emit', action='store_true', help='emit the complete reconstructed census')
    args = parser.parse_args()
    run(args.repo.resolve(), not args.emit)
