#!/usr/bin/env python3
"""Independent reverse-covector check of C03's retained logical words.

Substantial OpenAI Codex assistance. No producer module is imported or executed.
The data are exact historical fixtures, not a physical Clifford implementation.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

PINS = {
    'MIXED-RECTANGLE-RESULT.json': 'fb78f1fe52de77105eee210331b8ba70d733251735ae4855e8c011826ee06ac8',
    'CYCLIC-MIXED-RESULT.json': 'f65323e4d86d35f1463647ad36bddcffa21dc5eefc6ac4bbcbc8cf0ef4d0c369',
    'DYNAMIC-CYCLIC-RESULT.json': '9b9c02dac51d0989148c460f53623d51c6bd1204415991f058c83b77e36e884f',
}
FULL = tuple(1 << i for i in range(16, -1, -1))


class Rejection(ValueError):
    pass


def require(ok, gate, disabled=()):
    if gate not in disabled and not ok:
        raise Rejection(gate)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def unique_object(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, 'duplicate JSON key')
        out[k] = v
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(Rejection('finite JSON')))


def echelon(vectors):
    """Full row reduction by column sweeps, independent of producer pivot insertion."""
    rows = list(vectors)
    require(all(type(v) is int and 0 < v < (1 << 17) for v in rows), '17-bit nonzero frame vectors')
    pivot = 0
    for bit in range(16, -1, -1):
        found = next((i for i in range(pivot, len(rows)) if rows[i] & (1 << bit)), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(len(rows)):
            if i != pivot and rows[i] & (1 << bit):
                rows[i] ^= rows[pivot]
        pivot += 1
    return tuple(rows[:pivot])


def subset(small, large):
    return len(echelon(tuple(small) + tuple(large))) == len(large)


def coefficient(text):
    q = Fraction(text)
    require(q != 0 and q.denominator & (q.denominator - 1) == 0, 'nonzero dyadic coefficient')
    return q


def horner_tokens(q):
    """Enumerate the stated scalar tariff, without replaying lowering temporaries."""
    bits = bin(abs(q.numerator))[2:]
    tokens = ['fixed'] * 3
    for i, bit in enumerate(bits):
        if i:
            tokens.append('double')
        if bit == '1':
            tokens.append('numerator_add')
    denominator = q.denominator
    while denominator > 1:
        tokens.append('halve')
        denominator //= 2
    return tokens


def bill(kind, r, dual):
    if kind == 'rectangle':
        return 312 if dual else 300
    return 2*r*((54*r + (2 if dual else -1)) if kind == 'dynamic'
                else (72*r + (-34 if dual else -37)))


def flatten(fixture, dual=False, disabled=()):
    """Validate frames and expand private macro algebra into ordinary shears."""
    columns = sorted(fixture['starts'])
    require(set(columns) == set(fixture['ends']), 'ordinary register coverage')
    frames = {name: tuple(fixture['starts'][name]) for name in columns}
    for frame in frames.values():
        require(frame == echelon(frame), 'canonical entrance frames')
    paths = {name: [] for name in columns}
    steps, histogram = [], Counter()
    charges = Counter()
    scalar_adds = private_count = private_rank = 0
    for event in fixture['events']:
        op = event['op']
        require(op in ('add', 'climb', 'private'), 'known event opcode')
        if op == 'climb':
            name, frame = event['register'], tuple(event['frame'])
            require(name in frames, 'declared ordinary register')
            require(frame == echelon(frame) and subset(frames[name], frame),
                    'ordinary monotone frame', disabled)
            rank = len(frame) - len(frames[name])
            if rank:
                paths[name].append(rank)
                histogram[rank] += 1
            frames[name] = frame
        elif op == 'add':
            dst, src, q = event['dst'], event['src'], coefficient(event['q'])
            require(dst in frames and src in frames and dst != src, 'distinct declared ADD registers')
            require(frames[dst] == frames[src], 'common frame equality', disabled)
            if dual:
                dst, src, q = src, dst, -q
            steps.append((dst, src, q))
            charges.update(horner_tokens(q))
            scalar_adds += 1
        else:
            center = event['center']
            targets = [(name, coefficient(q)) for name, q in event['targets']]
            U = tuple(event.get('from', FULL))
            W = tuple(event.get('to', ()))
            require(center in frames and all(name in frames and name != center for name, _ in targets),
                    'declared private interface')
            require(len({name for name, _ in targets}) == len(targets), 'distinct private targets')
            require(U == echelon(U) and W == echelon(W) and subset(W, U), 'private nested frames')
            require(frames[center] == U and all(frames[name] == W for name, _ in targets),
                    'private entrance frames', disabled)
            private_count += 1
            rank = len(U) - len(W)
            private_rank += rank
            histogram[rank] += 1
            # Forward COPY + scatter and dual gather + unit subtraction have
            # the same ordinary operator; their clean-stream tariffs differ.
            charges['private_clear'] += 2
            if dual:
                charges.update(horner_tokens(Fraction(-1)))
                scalar_adds += 1
            else:
                charges['private_copy'] += 1
            for name, q in targets:
                charges.update(horner_tokens(q))
                scalar_adds += 1
                steps.append((center, name, -q) if dual else (name, center, q))
    require(frames == {name: tuple(frame) for name, frame in fixture['ends'].items()},
            'declared final frames', disabled)
    return columns, steps, {
        'paths': paths, 'private_episodes': private_count, 'private_rank': private_rank,
        'profile': {str(k): v for k, v in sorted(histogram.items()) if v},
        'rank_mass': sum(k*v for k, v in histogram.items()),
        'scalar_adds': scalar_adds,
        'scalar_primitives_before_real_doubling': sum(charges.values()),
        'tariff_token_counts': dict(sorted(charges.items())),
        'ordinary_shears_after_private_elimination': len(steps),
    }


def reverse_rows(columns, steps):
    """Pull each final coordinate covector backwards through the chronological word."""
    rows = []
    index = {name: i for i, name in enumerate(columns)}
    for output in columns:
        covector = {output: Fraction(1)}
        for dst, src, q in reversed(steps):
            if dst in covector:
                value = covector.get(src, Fraction(0)) + q*covector[dst]
                if value:
                    covector[src] = value
                elif src in covector:
                    del covector[src]
        rows.append({index[name]: q for name, q in covector.items()})
    return rows


def integer_prefixes(fixture, dual):
    """Separate integer/power-of-two forward representation, including private rows."""
    columns = sorted(fixture['starts'])
    rows = {name: ({i: 1}, 0) for i, name in enumerate(columns)}
    peak, depth, executed_adds = Fraction(1), 0, 0

    def observe(row):
        nonlocal peak, depth
        integers, exponent = row
        peak = max(peak, Fraction(sum(abs(v) for v in integers.values()), 1 << exponent))
        depth = max(depth, exponent)

    def add(dst, src, q):
        nonlocal executed_adds
        a, ea = rows[dst]
        b, eb = rows[src]
        eb += q.denominator.bit_length()-1
        exponent = max(ea, eb)
        value = {i: n << (exponent-ea) for i, n in a.items()}
        for i, n in b.items():
            value[i] = value.get(i, 0)+(q.numerator*n << (exponent-eb))
        value = {i: n for i, n in value.items() if n}
        if not value:
            exponent = 0
        while exponent and all(n % 2 == 0 for n in value.values()):
            value = {i: n//2 for i, n in value.items()}
            exponent -= 1
        rows[dst] = value, exponent
        executed_adds += 1
        observe(rows[dst])

    for event in fixture['events']:
        if event['op'] == 'climb':
            continue
        if event['op'] == 'add':
            dst, src, q = event['dst'], event['src'], coefficient(event['q'])
            add(src, dst, -q) if dual else add(dst, src, q)
        else:
            require('__private' not in rows, 'fresh private row')
            rows['__private'] = ({}, 0)
            center = event['center']
            if dual:
                for target, q in event['targets']:
                    add('__private', target, coefficient(q))
                snapshot = rows['__private']
                add(center, '__private', Fraction(-1))
                require(rows['__private'] == snapshot, 'immutable dual readout before ERASE')
            else:
                rows['__private'] = copy.deepcopy(rows[center])
                snapshot = copy.deepcopy(rows[center])
                observe(rows['__private'])
                for target, q in event['targets']:
                    add(target, '__private', coefficient(q))
                require(rows[center] == snapshot and rows['__private'] == snapshot,
                        'immutable forward COPY before ERASE')
            del rows['__private']
    rational = [{i: Fraction(n, 1 << exponent) for i, n in value.items()}
                for value, exponent in (rows[name] for name in columns)]
    return rational, {'logical_prefix_row_l1': str(peak),
                      'logical_prefix_denominator_depth': depth, 'executed_adds': executed_adds}


def expected_rows(columns, dual, kernel=None):
    index = {name: i for i, name in enumerate(columns)}
    rows = [{i: Fraction(1)} for i in range(len(columns))]
    n = len([x for x in columns if x.startswith('x')])
    require(all('x'+str(i) in index and 'y'+str(i) in index for i in range(n)), 'complete paired data ports')
    for i in range(n):
        for j in range(n):
            q = Fraction(i == j) if kernel is None else Fraction(kernel[i][j])
            if q:
                dst, src = ('x'+str(j), 'y'+str(i)) if dual else ('y'+str(i), 'x'+str(j))
                rows[index[dst]][index[src]] = -q if dual else q
    return rows


def first_difference(columns, actual, wanted):
    for i, (a, b) in enumerate(zip(actual, wanted)):
        for j in sorted(set(a) | set(b)):
            if a.get(j, 0) != b.get(j, 0):
                return {'output': columns[i], 'input': columns[j],
                        'actual': str(a.get(j, 0)), 'expected': str(b.get(j, 0))}
    return None


def audit_fixture(fixture, kind, r, dual=False, disabled=(), kernel=None):
    columns, steps, invoice = flatten(fixture, dual, disabled)
    rows = reverse_rows(columns, steps)
    wanted = expected_rows(columns, dual, kernel)
    witness = first_difference(columns, rows, wanted)
    require(witness is None, 'complete ordinary operator', disabled)
    require(invoice['scalar_primitives_before_real_doubling'] == bill(kind, r, dual),
            'complete scalar invoice', disabled)
    require(invoice['rank_mass'] == (298 if kind == 'rectangle' else 83*2*r),
            'complete rank invoice', disabled)
    return columns, rows, invoice, witness


def require_duality(columns, forward, dual):
    # Check D F^T = I at every entry, using sparse exact dot products.
    for i, a in enumerate(dual):
        for j, b in enumerate(forward):
            require(sum(q*b.get(k, 0) for k, q in a.items()) == int(i == j),
                    'same-order dual is inverse transpose')


def dense(columns, rows):
    return [[str(row.get(j, 0)) for j in range(len(columns))] for row in rows]


def expect_rejection(call, intended):
    try:
        call()
    except Rejection as error:
        require(str(error) == intended, 'intended semantic rejection')
        return {'gate': intended, 'rejected': True}
    raise Rejection('expected rejection missing')


def with_deletion(call, deleted, intended):
    record = expect_rejection(call, intended)
    try:
        expect_rejection(deleted, intended)
    except Rejection as error:
        require(str(error) == 'expected rejection missing', 'named-check deletion exposes defect')
    else:
        raise Rejection('named-check deletion retained rejection')
    record['named_check_deletion_exposes_defect'] = True
    return record


def controls(fixture, kind, r, dual):
    out = []
    first = next(e for e in fixture['events'] if e['op'] == 'add')
    wrong = copy.deepcopy(fixture)
    changed = next(e for e in wrong['events'] if e['op'] == 'add')
    changed['q'] = str(-Fraction(changed['q']))
    call = lambda: audit_fixture(wrong, kind, r, dual)
    deleted = lambda: audit_fixture(wrong, kind, r, dual, ('complete ordinary operator',))
    record = with_deletion(call, deleted, 'complete ordinary operator')
    record.update(mutation='first_actual_ADD_sign', coefficient_witness=deleted()[3])
    out.append(record)
    paid = copy.deepcopy(fixture)
    paid['events'][:0] = [dict(first, q='1', tag='paid_pair'), dict(first, q='-1', tag='paid_pair')]
    call = lambda: audit_fixture(paid, kind, r, dual)
    deleted = lambda: audit_fixture(paid, kind, r, dual, ('complete scalar invoice',))
    record = with_deletion(call, deleted, 'complete scalar invoice')
    columns, rows, invoice, witness = deleted()
    require(witness is None and invoice['scalar_primitives_before_real_doubling'] == bill(kind, r, dual)+8,
            'paid cancelling pair preserves endpoint and costs eight')
    record.update(mutation='paid_cancelling_pair', same_operator=True, added_component_primitives=8)
    out.append(record)
    frame = copy.deepcopy(fixture)
    tag = 'source_read_arc' if kind == 'dynamic' else 'source_plane'
    frame['events'] = [e for e in frame['events'] if e['tag'] != tag]
    call = lambda: audit_fixture(frame, kind, r, dual)
    deleted = lambda: audit_fixture(frame, kind, r, dual, ('common frame equality',))
    record = with_deletion(call, deleted, 'common frame equality')
    record.update(mutation='omitted_'+tag, endpoint_and_scalar_invoice_preserved=True)
    out.append(record)
    return out


def sources(source_dir):
    reports = {}
    for name, expected in PINS.items():
        path = source_dir/name
        raw = path.read_bytes() if path.exists() else gzip.decompress((source_dir/(name+'.gz')).read_bytes())
        require(digest(raw) == expected, 'authenticated fixture receipt: '+name)
        reports[name] = decode(raw)
    return reports


def cases(reports):
    a = reports['MIXED-RECTANGLE-RESULT.json']
    yield 'rectangle', None, a['fixtures'], a['orientations']
    for kind, name in [('static', 'CYCLIC-MIXED-RESULT.json'), ('dynamic', 'DYNAMIC-CYCLIC-RESULT.json')]:
        require([x['r'] for x in reports[name]['cases']] == list(range(2, 8)), 'complete six cyclic orders')
        for case in reports[name]['cases']:
            yield kind, case['r'], case['fixture'], [case['forward'], case['dual']]


def pauli_fixture_check(fixture, dual=False, disabled=()):
    E = [[Fraction(q) for q in row] for row in fixture['E']]
    require(len(E) == 19 and all(len(row) == 8 for row in E), 'complete nineteen by eight feature matrix')
    kernel = [[sum(a*b for a, b in zip(E[i], E[j]))/8192 for j in range(19)] for i in range(19)]
    require(kernel == [[Fraction(q) for q in row] for row in fixture['K']], 'complete E E transpose kernel')
    expected_price = 8*(6 if dual else 3)
    for row in E:
        for value in row:
            if value:
                expected_price += 2*(len(horner_tokens(value))+len(horner_tokens(value/8192)))
    columns, steps, invoice = flatten(fixture, dual, disabled)
    require(len(columns) == 46, 'complete forty-six ordinary input columns')
    rows = reverse_rows(columns, steps)
    witness = first_difference(columns, rows, expected_rows(columns, dual, kernel))
    require(witness is None, 'complete ordinary operator', disabled)
    require(invoice['scalar_primitives_before_real_doubling'] == expected_price,
            'complete scalar invoice', disabled)
    return columns, rows, invoice, witness


def pauli_controls(fixture, dual):
    out = []
    bad = copy.deepcopy(fixture)
    first = next(e for e in bad['events'] if e['op'] == 'add')
    first['q'] = str(-Fraction(first['q']))
    call = lambda: pauli_fixture_check(bad, dual)
    deleted = lambda: pauli_fixture_check(bad, dual, ('complete ordinary operator',))
    record = with_deletion(call, deleted, 'complete ordinary operator')
    record.update(mutation='first_actual_dirt_ADD_sign', coefficient_witness=deleted()[3])
    out.append(record)
    paid = copy.deepcopy(fixture)
    first = next(e for e in paid['events'] if e['op'] == 'add')
    paid['events'][:0] = [dict(first, q='1', tag='paid_pair'), dict(first, q='-1', tag='paid_pair')]
    call = lambda: pauli_fixture_check(paid, dual)
    deleted = lambda: pauli_fixture_check(paid, dual, ('complete scalar invoice',))
    record = with_deletion(call, deleted, 'complete scalar invoice')
    require(deleted()[3] is None, 'Pauli paid cancelling pair preserves operator')
    record.update(mutation='paid_cancelling_pair', same_operator=True, added_component_primitives=8)
    out.append(record)
    wrong_frame = copy.deepcopy(fixture)
    wrong_frame['events'] = [e for e in wrong_frame['events'] if e['tag'] != 'source_U']
    call = lambda: pauli_fixture_check(wrong_frame, dual)
    deleted = lambda: pauli_fixture_check(wrong_frame, dual, ('common frame equality',))
    record = with_deletion(call, deleted, 'common frame equality')
    record.update(mutation='omitted_actual_source_U', endpoint_and_scalar_invoice_preserved=True)
    out.append(record)
    return out


def audit_pauli(pauli, cyclic):
    require([case['name'] for case in pauli['cases']] == ['ZERO', 'radical2'], 'complete two Pauli variants')
    roots = []
    for i, j in combinations(range(8), 2):
        for second_sign in (-2, 2):
            row = [0]*8
            row[i], row[j] = 2, second_sign
            roots.append(row)
    roots += [[1]+list(tail) for tail in product((-1, 1), repeat=7)
              if sum(value == -1 for value in tail) % 2 == 0]
    roots.sort()
    require(roots == pauli['canonical_roots'] and len(roots) == 120, 'independent canonical E8 line representatives')
    packed = pauli['packed_root_pairs']
    require(len(packed) == 120 and all(len(row) == 120 for row in packed), 'complete packed pair labels')
    require(all(type(v) is int and 0 < v < (1 << 17) for row in packed for v in row),
            'complete seventeen-bit label domain')
    base = packed[0][0]
    left = [packed[i][0] ^ base for i in range(120)]
    right = [packed[0][j] ^ base for j in range(120)]
    parity = lambda a, b: (a & b).bit_count() % 2
    gram = [[sum(a*b for a, b in zip(x, y))//4 for y in roots] for x in roots]
    require(parity(base, base) == 1, 'odd affine label origin')
    for i in range(120):
        require(parity(base, left[i]) == gram[0][i] % 2 and parity(base, right[i]) == gram[0][i] % 2,
                'affine origin Gram parity')
        for j in range(120):
            require(packed[i][j] == base ^ left[i] ^ right[j], 'complete affine product label decomposition')
            wanted = (gram[i][j]+gram[0][i]+gram[0][j]) % 2
            require(parity(left[i], left[j]) == wanted and parity(right[i], right[j]) == wanted
                    and parity(left[i], right[j]) == 0, 'all affine factor Gram parities')
    q = [sum((-1 if j % 2 else 1)*v*v for j, v in enumerate(row)) for row in roots]
    require(q == pauli['quadratic_values'], 'actual selected quadratic values')
    support = [j for j in range(120) if q[j]]
    require(len(support) == 24 and {q[j] for j in support} == {-8, 8}, 'actual quadratic support')
    U = echelon(packed[i][j] for i in range(120) for j in support)
    W = echelon(w for w in range(1, 1 << 17) if all(parity(w, u) == 0 for u in U))
    require(list(U) == pauli['source_support_U'] and list(W) == pauli['radical_U_perp']
            and len(U) == 15 and len(W) == 2 and subset(W, U), 'independent U15 radical2 geometry')
    result = []
    for case in pauli['cases']:
        fixture = case['fixture']
        expected_E = [[str(roots[a][c]*q[b]) for c in range(8)] for a, b in fixture['ports']]
        require(expected_E == fixture['E'], 'all actual diagnostic feature coefficients')
        orientations, raw_rows = [], []
        for dual in (False, True):
            columns, rows, invoice, _ = pauli_fixture_check(fixture, dual)
            integer_rows, prefixes = integer_prefixes(fixture, dual)
            require(rows == integer_rows, 'Pauli forward integer and reverse rational operators agree')
            fresh = case['dual' if dual else 'forward']
            original_order = fresh['ordinary_column_order']
            require(set(original_order) == set(columns) and len(original_order) == len(columns),
                    'Pauli producer column domain')
            reordered = [[fresh['final_rows'][a][original_order.index(b)] for b in columns] for a in columns]
            require(dense(columns, rows) == reordered, 'Pauli complete fresh operator binding')
            for key in ('paths', 'private_rank'):
                require(canonical(invoice[key]) == canonical(fresh[key]), 'Pauli complete invoice field: '+key)
            require(invoice['scalar_primitives_before_real_doubling'] == fresh['primitive_before_real_doubling'],
                    'Pauli complete scalar record binding')
            require(prefixes['executed_adds'] == invoice['scalar_adds'], 'Pauli executed ADD prefix coverage')
            for key in ('logical_prefix_row_l1', 'logical_prefix_denominator_depth'):
                require(prefixes[key] == fresh[key], 'Pauli exact prefix field: '+key)
            expected_private = 8*(15-len(case['output_frame']))
            require(invoice['private_rank'] == expected_private and invoice['rank_mass'] == 744+expected_private,
                    'Pauli complete role rank invoice')
            orientations.append({'orientation': 'dual' if dual else 'forward', 'ordinary_columns': columns,
                                 'ordinary_operator_rows': dense(columns, rows), 'invoice': invoice,
                                 'integer_dyadic_prefixes': prefixes,
                                 'production_controls': pauli_controls(fixture, dual)})
            raw_rows.append(rows)
        require_duality(columns, raw_rows[0], raw_rows[1])
        result.append({'name': case['name'], 'fixture_sha256': digest(canonical(fixture).encode()),
                       'orientations': orientations, 'same_order_inverse_transpose_entries': len(columns)**2})
    frames = pauli['tiling_frame_cases']
    require(len(frames) == 2400 and digest(canonical(frames).encode()) == pauli['tiling_frame_cases_sha256'],
            'complete Pauli frame census digest')
    require(len({(x['triple_index'], x['b_pair_index']) for x in frames}) == 2400,
            'unique complete frame census')
    for record in frames:
        labels = record['labels']
        require(len(labels) == 6, 'six frame-case labels')
        planes = [echelon(labels[2*g:2*g+2]) for g in range(3)]
        arcs = [echelon(planes[g]+planes[(g+1)%3]) for g in range(3)]
        require(canonical(planes) == canonical(record['planes']) and canonical(arcs) == canonical(record['final_arcs']),
                'independently reduced planes and arcs')
    if cyclic is not None:
        require(canonical(frames) == canonical(cyclic['complete_tiling']['frame_cases']),
                'complete independent cross-stage frame binding')
    return {'cases': result, 'ordinary_operator_coefficients': 4*46*46,
            'duality_coefficients': 2*46*46, 'rejecting_mutations': 12,
            'named_check_deletions': 12, 'independently_reduced_frame_cases': 2400,
            'cross_stage_full_frame_arrays_compared': cyclic is not None,
            'independent_affine_Gram_domain': {'factor_lines': 120, 'product_labels': 14400,
                                             'all_ordered_pair_Gram_equalities_implied': 14400**2,
                                             'physical_signed_support_ports': 5760,
                                             'U_dimension': len(U), 'W_dimension': len(W)},
            'frame_cases_sha256': digest(canonical(frames).encode())}


def audit(source_dir, cyclic=None, pauli=None):
    reports = sources(source_dir)
    fresh_cases = None if cyclic is None else list(cases(cyclic['reports']))
    records = []
    for number, (kind, r, fixture, retained) in enumerate(cases(reports)):
        if fresh_cases is not None:
            fresh_kind, fresh_r, fresh_fixture, fresh_orientations = fresh_cases[number]
            require((fresh_kind, fresh_r) == (kind, r) and canonical(fresh_fixture) == canonical(fixture),
                    'complete historical fixture binding')
        orientations = []
        raw_rows = []
        for dual in (False, True):
            columns, rows, invoice, _ = audit_fixture(fixture, kind, r, dual)
            integer_rows, prefixes = integer_prefixes(fixture, dual)
            require(integer_rows == rows, 'forward integer and reverse rational operators agree')
            require(prefixes['executed_adds'] == invoice['scalar_adds'], 'all executed prefix ADDs covered')
            for key in ('logical_prefix_row_l1', 'logical_prefix_denominator_depth'):
                require(prefixes[key] == retained[int(dual)][key], 'retained exact prefix field: '+key)
            for key in ('paths', 'private_episodes', 'private_rank', 'profile', 'rank_mass',
                        'scalar_adds', 'scalar_primitives_before_real_doubling'):
                require(canonical(invoice[key]) == canonical(retained[int(dual)][key]),
                        'complete retained invoice field: '+key)
            all_rows = dense(columns, rows)
            if fresh_cases is not None:
                fresh = fresh_orientations[int(dual)]
                fresh_index = {name: i for i, name in enumerate(fresh['ordinary_columns'])}
                require(set(fresh_index) == set(columns) and len(fresh['ordinary_columns']) == len(columns),
                        'fresh complete column coverage')
                reordered = [[fresh['ordinary_operator_rows'][fresh_index[a]][fresh_index[b]]
                              for b in columns] for a in columns]
                require(all_rows == reordered, 'fresh complete ordinary operator binding')
            orientations.append({'orientation': 'dual' if dual else 'forward',
                                 'ordinary_columns': columns, 'ordinary_operator_rows': all_rows,
                                 'invoice': invoice, 'integer_dyadic_prefixes': prefixes,
                                 'production_controls': controls(fixture, kind, r, dual)})
            raw_rows.append(rows)
        require_duality(columns, raw_rows[0], raw_rows[1])
        records.append({'kind': kind, 'r': r, 'fixture_sha256': digest(canonical(fixture).encode()),
                        'ordinary_input_columns': len(columns), 'chronological_events': len(fixture['events']),
                        'same_order_inverse_transpose_entries': len(columns)**2, 'orientations': orientations})
    if fresh_cases is not None:
        require(len(fresh_cases) == len(records), 'complete fresh case coverage')
    result = {'schema': 'c03_independent_reverse_covectors.v1', 'status': 'PASS',
            'checker_sha256': digest(Path(__file__).read_bytes()), 'authenticated_fixture_receipts': PINS,
            'fresh_cyclic_receipt_compared': cyclic is not None, 'cases': records,
            'coverage': {'fixtures': len(records), 'orientations': 2*len(records),
                         'ordinary_operator_coefficients': sum(2*x['ordinary_input_columns']**2 for x in records),
                         'duality_coefficients': sum(x['ordinary_input_columns']**2 for x in records),
                         'rejecting_mutations': 6*len(records), 'named_check_deletions': 6*len(records)},
            'premises': ['Every ordinary source, target and dirty helper has an independent input coordinate.',
                        'Frames are logical labels; helper values restore at declared final frames, not entrance frames.',
                        'Private macros assume the declared clean COPY/erase contract; their arbitrary dirty input is not asserted.',
                        'Horner charges are enumerated tariffs; numerical lowering temporaries and rounded precision are not replayed.',
                        'No physical Clifford phases, source admission, ownership, all-size supplier or exponent result is established.']}
    if pauli is not None:
        result['pauli'] = audit_pauli(pauli, cyclic)
        result['total_coverage'] = {'fixtures': 15, 'orientations': 30,
                                  'ordinary_operator_coefficients': 44440, 'duality_coefficients': 22220,
                                  'rejecting_mutations': 90, 'named_check_deletions': 90}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--cyclic-receipt', type=Path)
    parser.add_argument('--cyclic-sha256')
    parser.add_argument('--pauli-receipt', type=Path)
    parser.add_argument('--pauli-sha256')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.output.is_absolute() and not args.output.exists(), 'fresh absolute output')
    require(args.source_dir.resolve() not in args.output.resolve().parents, 'output outside source inputs')
    require((args.cyclic_receipt is None) == (args.cyclic_sha256 is None), 'paired cyclic authentication arguments')
    require((args.pauli_receipt is None) == (args.pauli_sha256 is None), 'paired Pauli authentication arguments')
    cyclic = None
    if args.cyclic_receipt is not None:
        raw = args.cyclic_receipt.read_bytes()
        require(digest(raw) == args.cyclic_sha256, 'authenticated fresh cyclic receipt')
        cyclic = decode(gzip.decompress(raw) if args.cyclic_receipt.suffix == '.gz' else raw)
    pauli = None
    if args.pauli_receipt is not None:
        raw = args.pauli_receipt.read_bytes()
        require(digest(raw) == args.pauli_sha256, 'authenticated fresh Pauli receipt')
        pauli = decode(gzip.decompress(raw) if args.pauli_receipt.suffix == '.gz' else raw)
    result = audit(args.source_dir, cyclic, pauli)
    if cyclic is not None:
        result['fresh_cyclic_receipt_sha256'] = args.cyclic_sha256
    if pauli is not None:
        result['fresh_pauli_receipt_sha256'] = args.pauli_sha256
    raw = (json.dumps(result, sort_keys=True, indent=2)+'\n').encode()
    if args.output.suffix == '.gz':
        raw = gzip.compress(raw, mtime=0)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as handle:
        handle.write(raw)
    print('PASS independent reverse covectors: '+canonical(result.get('total_coverage', result['coverage'])))


if __name__ == '__main__':
    main()
