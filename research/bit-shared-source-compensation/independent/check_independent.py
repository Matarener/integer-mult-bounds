#!/usr/bin/env python3
"""Independent dense-column and address audit of the source17 repair.

Apache-2.0; substantial OpenAI Codex assistance. No producer imports or caches.
This proves finite literal-model identities, not native execution or kappa.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import platform
import sys

ROOT = Path(__file__).resolve().parent.parent
N = 660
ZERO = [0] * N
BASE_H = {1: 1322, 2: 1342, 3: 79, 4: 39, 5: 102, 6: 11, 7: 18}


class Failure(ValueError):
    pass


def need(value, label):
    if not value:
        raise Failure(label)


def equal(a, b, label, disabled=()):
    if label not in disabled:
        need(a == b, label)


def rejection(label, action):
    try:
        action()
    except Failure as error:
        need(str(error) == label, "wrong rejection for " + label)
    else:
        raise Failure("unexpected acceptance: " + label)


def eye(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def transpose(a):
    return tuple(zip(*a))


def product(a, b):
    columns = transpose(b)
    return tuple(tuple(sum(x*y for x, y in zip(r, c)) for c in columns) for r in a)


def difference(a, b):
    return tuple(tuple(x-y for x, y in zip(r, s)) for r, s in zip(a, b))


def row_basis(rows):
    """Pivot elimination; intentionally independent of Gram-Schmidt construction."""
    pivots = {}
    for raw in rows:
        row = list(map(Q, raw))
        for j, old in sorted(pivots.items()):
            a = row[j]
            if a:
                row = [x-a*y for x, y in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            a = row[pivot]
            pivots[pivot] = [x/a for x in row]
    return tuple(tuple(v) for _, v in sorted(pivots.items()))


def inverse(a):
    n = len(a)
    rows = [list(r)+list(e) for r, e in zip(a, eye(n))]
    for j in range(n):
        k = next(k for k in range(j, n) if rows[k][j])
        rows[j], rows[k] = rows[k], rows[j]
        q = rows[j][j]
        rows[j] = [x/q for x in rows[j]]
        for k in range(n):
            if k != j:
                q = rows[k][j]
                rows[k] = [x-q*y for x, y in zip(rows[k], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def projector(geometry, frame):
    rows = row_basis(geometry['lines'][k] for k in geometry['frames'][frame])
    if not rows:
        p = tuple((Q(0),)*8 for _ in range(8))
    else:
        # Orthogonal projection R^T (R R^T)^-1 R.
        p = product(product(transpose(rows), inverse(product(rows, transpose(rows)))), rows)
    need(product(p, p) == p and transpose(p) == p, 'projector identity')
    need(all(x.denominator & (x.denominator-1) == 0 for r in p for x in r),
         'dyadic projector')
    return p, len(rows)


def swap(p):
    other = difference(eye(8), p)
    return tuple(other[i]+p[i] for i in range(8))+tuple(p[i]+other[i] for i in range(8))


def literal_inverse(records):
    out = []
    for op, d, s, c, f, tag in reversed(records):
        if op == 0:
            out.append([op, d, c, s, f, tag])
        elif op == 1:
            out.append([op, d, s, -c, f, tag])
        else:
            out.append([5-op, d, s, c, f, tag])
    return out


def replay(records, start, finish, initial=None, cuts=()):
    """Every integer input coefficient, including all independent dirty rows."""
    values = [[int(i == j) for j in range(N)] for i in range(N)]+[ZERO.copy()]
    if initial is not None:
        values = [row.copy() for row in initial]
    frames = list(start)+[None]
    opened = None
    hist = Counter()
    adds = copies = erases = 0
    snapshots = {}
    majorant = [sum(map(abs, row)) for row in values]
    maximum = max(max(map(abs, row)) for row in values)
    max_l1 = max(majorant)
    max_l1_at = {'record': -1, 'row': majorant.index(max_l1)}
    max_majorant = max_l1
    max_majorant_at = max_l1_at.copy()
    for index, (op, d, s, c, f, _) in enumerate(records):
        if op == 0:
            need(frames[d] == s, 'MOVE entrance')
            frames[d] = c
            hist[f] += 1
        elif op == 1:
            need(d != s and frames[d] == frames[s] == f, 'common ADD frame')
            need(d != opened, 'COPY source immutable')
            values[d] = [a+c*b for a, b in zip(values[d], values[s])]
            maximum = max(maximum, max(map(abs, values[d])))
            norm = sum(map(abs, values[d]))
            if norm > max_l1:
                max_l1 = norm
                max_l1_at = {'record': index, 'row': d}
            majorant[d] += abs(c)*majorant[s]
            if majorant[d] > max_majorant:
                max_majorant = majorant[d]
                max_majorant_at = {'record': index, 'row': d}
            adds += 1
        elif op == 2:
            need(s == N and opened is None and values[N] == ZERO, 'fresh COPY')
            need(frames[d] == c and frames[N] is None, 'COPY frame')
            values[N] = values[d].copy()
            majorant[N] = majorant[d]
            frames[N] = f
            opened = d
            hist[7] += 1
            copies += 1
        elif op == 3:
            need(s == N and opened == d and frames[d] == c and frames[N] == f,
                 'ERASE frame')
            need(values[N] == values[d], 'ERASE exact equality')
            values[N] = ZERO.copy()
            majorant[N] = 0
            frames[N] = None
            opened = None
            erases += 1
        else:
            raise Failure('unknown opcode')
        if index in cuts:
            snapshots[index] = {
                str(i): {'row': {str(j): x for j, x in enumerate(values[i]) if x},
                         'frame': frames[i]}
                for i in (17, 413, 444)
            }
    need(frames == list(finish)+[None] and opened is None and values[N] == ZERO,
         'final frames and private zero')
    return values, {'H': dict(sorted(hist.items())), 'ADD': adds, 'COPY': copies,
                    'ERASE': erases, 'max_absolute_integer_coefficient': maximum,
                    'max_prefix_row_l1': max_l1, 'max_prefix_row_l1_at': max_l1_at,
                    'positive_majorant_peak': max_majorant,
                    'positive_majorant_peak_at': max_majorant_at}, snapshots


def build_repair(records, omit_return=False, late=False):
    result = []
    original_cuts = {}
    for index, record in enumerate(records):
        if index in (23325, 23333):
            continue
        result.append(record)
        if index in (23405, 23424):
            helper, frame = (413, 390) if index == 23405 else (444, 392)
            if late and index == 23405:
                continue
            result.extend([[0, 17, 509, frame, 2, 40], [1, helper, 17, 1, frame, 40]])
            if not omit_return:
                result.append([0, 17, frame, 509, 2, 40])
            if late and index == 23424:
                result.extend([[0, 17, 509, 390, 2, 0], [1, 413, 17, 1, 390, 2],
                               [0, 17, 390, 509, 2, 0]])
        original_cuts[index] = len(result)-1
    return result, original_cuts


def scalar_rewrite(records):
    """Independently derived9-ADD prefix; keep original expanded cleanup."""
    expected = [
        [1, 444, s, 1, 509, 2] for s in (17, 271, 293, 352, 413, 468, 470)
    ]+[[0, 371, 193, 509, 2, 0]]+[
        [1, 413, s, 1, 509, 2] for s in (17, 271, 293, 352, 371, 470)
    ]
    need(records[23325:23339] == expected, 'exact scalar rewrite interval')
    changed = [records[23332]]+[[1, 413, s, 1, 509, 2]
                              for s in (17, 271, 293, 352, 371, 470)]+[
        [1, 444, 413, 1, 509, 2], [1, 444, 468, 1, 509, 2],
        [1, 444, 371, -1, 509, 2],
    ]
    return records[:23325]+changed+records[23339:]


def reduced(word):
    result = []
    for letter in word:
        if result and result[-1] == letter:
            result.pop()
        else:
            result.append(letter)
    return ''.join(result)


def formal_program(events, n):
    """Complete F2 free-product coefficients, with right-appended pullback words."""
    rows = [{(i, '')} for i in range(n)]
    for event in events:
        if len(event) == 2:
            d, letter = event
            rows[d] = {(i, reduced(w+letter)) for i, w in rows[d]}
        else:
            d, s, _ = event
            rows[d] ^= rows[s]
    return rows


def formal_inverse(events):
    return list(reversed(events))  # XOR additions and each query are involutions.


def field3(a):
    return tuple(tuple(int(x.numerator * pow(x.denominator, -1, 3)) % 3 for x in r) for r in a)


def act(a, x):
    return tuple(sum(v*w for v, w in zip(r, x)) % 3 for r in a)


def main():
    pins = json.loads((ROOT/'inputs/PREDECESSOR-PINS.json').read_bytes())
    hashes = {}
    authenticated_inputs = {}
    for item in pins['files']:
        data = (ROOT/item['path']).read_bytes()
        h = sha256(data).hexdigest()
        need(h == item['sha256'], 'input pin '+item['path'])
        hashes[item['path']] = h
        authenticated_inputs[item['path']] = data
    word_bytes = gzip.decompress(authenticated_inputs['inputs/WORD.json.gz'])
    need(sha256(word_bytes).hexdigest() == pins['word_canonical_sha256'], 'WORD payload pin')
    word = json.loads(word_bytes)
    geometry = json.loads(gzip.decompress(authenticated_inputs['inputs/GEOMETRY.json.gz']))
    records = word['records']
    need(len(records) == 38927 and len(word['start']) == N, 'source dimensions')
    actual = {23325: [1, 444, 17, 1, 509, 2], 23333: [1, 413, 17, 1, 509, 2],
              23405: [0, 413, 509, 390, 2, 0], 23424: [0, 444, 509, 392, 2, 0]}
    for k, record in actual.items():
        need(records[k] == record, 'selected record '+str(k))

    cache = {}
    def frame(k):
        if k not in cache:
            cache[k] = projector(geometry, k)
        return cache[k]
    pairs = set()
    for op, _, s, c, f, _ in records:
        if op == 0:
            pair = (s, c, f)
        elif op in (2, 3):
            pair = (f, c, 7)
        else:
            continue
        if pair in pairs:
            continue
        pairs.add(pair)
        a, ar = frame(pair[0])
        b, br = frame(pair[1])
        need(br-ar == pair[2] and product(a, b) == a, 'native nested rank tariff')
    f0, _ = frame(509)
    p = difference(frame(390)[0], f0)
    q = difference(frame(392)[0], f0)
    need(product(p, p) == p and product(q, q) == q, 'actual query projectors')
    comm = difference(product(p, q), product(q, p))
    need(comm[0][1] == Q(1, 8), 'actual noncommutator entry')
    dp, dq = swap(p), swap(q)
    need(product(dp, dp) == eye(16) and product(dq, dq) == eye(16), 'actual involutions')

    baseline, invoice, snapshots = replay(records, word['start'], word['final'], cuts=(23338, 23405, 23424))
    need(invoice['H'] == BASE_H and invoice['ADD'] == 36005 and invoice['COPY'] == 9,
         'complete original invoice')
    cut = snapshots[23338]
    expected = {
        17: {17: 1},
        413: {413: 1, 469: -1, 605: -1, 87: 1, 17: 1, 22: 1, 33: 1, 60: 1, 67: 1, 92: 1},
        444: {444: 1, 369: -1, 77: 1, 17: 1, 22: 1, 33: 1, 60: 1, 87: 1, 38: 1, 92: 1},
    }
    for h, wanted in expected.items():
        need(cut[str(h)] == {'row': {str(j): x for j, x in wanted.items()}, 'frame': 509},
             'independent original-input row '+str(h))
    # Unchanged records are a dependency certificate, not a guess from endpoints.
    consumers = {}
    for h, omitted, delivery in [(413, 23333, 23405), (444, 23325, 23424)]:
        need(not any(r[0] == 1 and r[2] == h for r in records[omitted+1:delivery]),
             'no omitted contribution escapes before repair')
        consumers[h] = next(i for i in range(delivery+1, len(records))
                            if records[i][0] == 1 and records[i][2] == h)
    need(consumers == {413: 23515, 444: 23488}, 'actual first consumers')
    first_source_change = next(i for i in range(23339, len(records)) if records[i][1] == 17)
    need(first_source_change == 24523, 'source immutable across both tours')
    need(records[23318] == [0, 17, 183, 509, 2, 0], 'source frame509 entrance')

    repaired, mapped = build_repair(records)
    repair_bytes = (ROOT/'REPAIR.json').read_bytes()
    certificate = json.loads(repair_bytes)
    need(certificate['word_canonical_sha256'] == pins['word_canonical_sha256'], 'repair source pin')
    remove = {item['index']: item['expected'] for item in certificate['remove']}
    insert = {item['index']: item for item in certificate['insert_after']}
    certified = []
    for i, record in enumerate(records):
        if i in remove:
            need(record == remove[i], 'repair removal guard')
        else:
            certified.append(record)
        if i in insert:
            need(record == insert[i]['expected'], 'repair insertion guard')
            certified.extend(insert[i]['records'])
    need(certified == repaired, 'fixed repair matches independent construction')
    result, repaired_invoice, repaired_cuts = replay(
        repaired, word['start'], word['final'], cuts=(mapped[23405], mapped[23424]))
    need(result == baseline, 'full integer endpoint equality')
    for old in (23405, 23424):
        relevant = (17, 413) if old == 23405 else (17, 413, 444)
        for h in relevant:
            need(repaired_cuts[mapped[old]][str(h)] == snapshots[old][str(h)],
                 'exact repaired delivery and source return')
    wanted_h = dict(BASE_H)
    wanted_h[2] += 4
    need(repaired_invoice['H'] == wanted_h and repaired_invoice['ADD'] == invoice['ADD']
         and repaired_invoice['COPY'] == invoice['COPY']
         and repaired_invoice['ERASE'] == invoice['ERASE'], 'complete repaired invoice')
    tariff_lo = Q('8.055644400453750470661584')
    tariff_hi = Q('8.055644400453750470661592')
    need((tariff_lo/8)**500 < 32 < (tariff_hi/8)**500, 'independent exact tariff enclosure')
    identity = [[int(i == j) for j in range(N)] for i in range(N)]+[ZERO.copy()]
    # A supplied initial map can contain the largest coefficient before any gate.
    initial_metric_input = [row.copy() for row in identity]
    initial_metric_input[7][7], initial_metric_input[7][8] = 23, -5
    _, initial_invoice, _ = replay([], word['start'], word['start'], initial_metric_input)
    initial_metric_expected = {
        'max_absolute_integer_coefficient': 23,
        'max_prefix_row_l1': 28,
        'max_prefix_row_l1_at': {'record': -1, 'row': 7},
        'positive_majorant_peak': 28,
        'positive_majorant_peak_at': {'record': -1, 'row': 7},
    }
    initial_metric_observed = {k: initial_invoice[k] for k in initial_metric_expected}
    need(initial_metric_observed == initial_metric_expected, 'nonidentity initial prefix metrics')
    undo = literal_inverse(repaired)
    roundtrip = replay(undo, word['final'], word['start'], result)[0]
    need(roundtrip == identity, 'forward then literal inverse')
    backward = replay(undo, word['final'], word['start'])[0]
    need(replay(repaired, word['start'], word['final'], backward)[0] == identity,
         'literal inverse then forward')
    for i in list(range(111))+list(range(222, N)):
        need(result[i] == identity[i], 'integer source and helper restoration')
    for i, row in enumerate(result[:N]):
        target = identity[i].copy()
        if 111 <= i < 222:
            target[i-111] = 1
        need([x % 2 for x in row] == target, 'all Boolean endpoints')
    need(result[111][236] == -2, 'retained even integer target defect')

    # Changed scalar choice: independent chronological reconstruction and all columns.
    scalar_records = scalar_rewrite(records)
    scalar_source_bytes = (ROOT/'source-audit/SOURCE-AUDIT.json').read_bytes()
    scalar_certificate = json.loads(scalar_source_bytes)['optional_scalar_fanout_seed']
    need(scalar_certificate['replace_records_half_open'] == [23325, 23339], 'scalar certificate interval')
    need(scalar_records[23325:23335] == scalar_certificate['replacement_records'],
         'fixed scalar recipe matches independent construction')
    scalar_result, scalar_invoice, scalar_cuts = replay(
        scalar_records, word['start'], word['final'], cuts=(23334, 23401, 23420))
    need(scalar_result == baseline, 'scalar rewrite full integer endpoint')
    for before, after in [(23338, 23334), (23405, 23401), (23424, 23420)]:
        need(snapshots[before] == scalar_cuts[after], 'scalar rewrite boundary equality')
    need(scalar_records[23335:] == records[23339:], 'unchanged expanded forward cleanup')
    need(scalar_invoice['H'] == invoice['H'] and scalar_invoice['ADD'] == 36001
         and scalar_invoice['COPY'] == 9 and scalar_invoice['ERASE'] == 9,
         'scalar rewrite full invoice')
    scalar_undo = literal_inverse(scalar_records)
    need(replay(scalar_undo, word['final'], word['start'], scalar_result)[0] == identity,
         'scalar forward then literal inverse')
    scalar_back, scalar_inverse_invoice, _ = replay(scalar_undo, word['final'], word['start'])
    need(replay(scalar_records, word['start'], word['final'], scalar_back)[0] == identity,
         'scalar literal inverse then forward')
    baseline_undo = literal_inverse(records)
    need(replay(baseline_undo, word['final'], word['start'], baseline)[0] == identity,
         'baseline forward then literal inverse')
    baseline_back, baseline_inverse_invoice, _ = replay(baseline_undo, word['final'], word['start'])
    need(replay(records, word['start'], word['final'], baseline_back)[0] == identity,
         'baseline literal inverse then forward')
    no_compensation = scalar_records[:23334]+scalar_records[23335:]
    incomplete_scalar = replay(no_compensation, word['start'], word['final'])[0]
    rejection('missing scalar compensation',
              lambda: equal(incomplete_scalar, baseline, 'missing scalar compensation'))
    equal(incomplete_scalar, baseline, 'missing scalar compensation', ('missing scalar compensation',))
    wrong_sign = [r.copy() for r in scalar_records]
    wrong_sign[23334][3] = 1
    wrong_sign_result = replay(wrong_sign, word['start'], word['final'])[0]
    need(all([x % 2 for x in a] == [x % 2 for x in b]
             for a, b in zip(wrong_sign_result, baseline)), 'wrong sign defeats Boolean-only oracle')
    dirty_ids = list(range(111))+list(range(222, N))
    rejection('scalar signed dirty restoration',
              lambda: equal([wrong_sign_result[i] for i in dirty_ids],
                            [baseline[i] for i in dirty_ids], 'scalar signed dirty restoration'))
    equal([wrong_sign_result[i] for i in dirty_ids], [baseline[i] for i in dirty_ids],
          'scalar signed dirty restoration', ('scalar signed dirty restoration',))
    rejection('common ADD frame',
              lambda: replay(scalar_records[:23325]+scalar_records[23326:],
                             word['start'], word['final']))

    # Two independent fresh perturbations at the actual cut, propagated exactly.
    response = [[0, 0] for _ in range(N+1)]
    response[413] = [1, 0]
    response[444] = [0, 1]
    for op, d, s, c, f, tag in records[23339:]:
        if op == 1:
            response[d] = [a+c*b for a, b in zip(response[d], response[s])]
        elif op == 2:
            response[N] = response[d].copy()
        elif op == 3:
            need(response[N] == response[d], 'suffix response ERASE guard')
            response[N] = [0, 0]
    need(response[111] == [1, 0] and response[114] == [0, 1], 'distinct public responses')

    # Universal positive control, in a faithful free-product formal algebra.
    # Here words encode precomposition, so chronological p then q is the word pq.
    tour = [(0, 'p'), (1, 0, '+'), (0, 'q'), (2, 0, '+'), (0, 'q'), (0, 'p')]
    target = [{(0, '')}, {(1, ''), (0, 'p')}, {(2, ''), (0, 'pq')}]
    need(formal_program(tour, 3) == target, 'formal shared-source positive control')
    need(formal_program(tour+formal_inverse(tour), 3) == [{(i, '')} for i in range(3)],
         'formal literal inverse')
    wrong_tour = tour[:-2]+[(0, 'p'), (0, 'q')]
    wrong = formal_program(wrong_tour, 3)
    rejection('noncommuting inverse order', lambda: equal(wrong, target, 'noncommuting inverse order'))
    equal(wrong, target, 'noncommuting inverse order', ('noncommuting inverse order',))
    actual_wrong = product(product(product(dp, dq), dp), dq)
    need(actual_wrong != eye(16), 'actual wrong-order witness survives quotient')

    # Actual-address delta-function defects: no assumption of faithful small matrices.
    defects = {}
    for name, delta in [('p', dp), ('q', dq)]:
        native = field3(delta)
        axis = next(j for j in range(16) if any(native[i][j] != int(i == j) for i in range(16)))
        address = tuple(int(j == axis) for j in range(16))
        moved = act(native, address)
        need(moved != address, 'moved address')
        # At z=address, d(z)=1 but d(D z)=0 for d=indicator_address.
        obtained = int(address == address)
        required = int(moved == address)
        rejection('omitted independent dirt '+name,
                  lambda name=name: equal(obtained, required, 'omitted independent dirt '+name))
        equal(obtained, required, 'omitted independent dirt '+name,
              ('omitted independent dirt '+name,))
        defects[name] = {'field': 3, 'input_delta_address': address,
                         'query_moved_address': moved, 'source_input': 0,
                         'source_only_output_at_input_address': obtained,
                         'required_output_at_input_address': required}

    rejection('MOVE entrance', lambda: replay(build_repair(records, omit_return=True)[0],
                                               word['start'], word['final']))
    rejection('common ADD frame', lambda: replay(build_repair(records, late=True)[0],
                                                 word['start'], word['final']))
    # Delete an inverse scalar step; frames stay legal, but complete arbitrary-input cleanup fails.
    cut_inverse = next(i for i, r in enumerate(undo) if r[:4] == [1, 444, 17, -1])
    broken_undo = undo[:cut_inverse]+undo[cut_inverse+1:]
    broken_endpoint = replay(broken_undo, word['final'], word['start'], result)[0]
    rejection('missing literal inverse ADD',
              lambda: equal(broken_endpoint, identity, 'missing literal inverse ADD'))
    equal(broken_endpoint, identity, 'missing literal inverse ADD', ('missing literal inverse ADD',))
    rejection('omitted source return charge',
              lambda: equal(repaired_invoice['H'][2]-invoice['H'][2], 2, 'omitted source return charge'))
    equal(repaired_invoice['H'][2]-invoice['H'][2], 2, 'omitted source return charge',
          ('omitted source return charge',))
    # Replay an equivalent ordering of all independent integer input coordinates.
    permuted_identity = [list(reversed(row)) for row in identity]
    permuted_result = replay(repaired, word['start'], word['final'], permuted_identity)[0]
    need(permuted_result == [list(reversed(row)) for row in baseline],
         'positive input-coordinate permutation')

    output = {
        'status': 'PASS_SCOPED_SHARED_SOURCE_REVIEW', 'no_new_kappa': True,
        'inputs_sha256': hashes, 'word_payload_sha256': sha256(word_bytes).hexdigest(),
        'repair_recipe_sha256': sha256(repair_bytes).hexdigest(),
        'repaired_records_sha256': sha256(json.dumps(repaired, separators=(',', ':')).encode()).hexdigest(),
        'scalar_source_receipt_sha256': sha256(scalar_source_bytes).hexdigest(),
        'scalar_records_sha256': sha256(json.dumps(scalar_records, separators=(',', ':')).encode()).hexdigest(),
        'python': platform.python_version(), 'optimized': bool(sys.flags.optimize),
        'geometry_method': 'pivot basis, inverse Gram matrix, full rational identities',
        'frame_projectors_checked': len(cache), 'nested_move_copy_pairs_checked': len(pairs),
        'independent_integer_columns': N, 'all_word_records': len(records),
        'literal_orientations': 'forward/inverse and inverse/forward',
        'literal_words_checked': ['baseline', 'repair', 'scalar_rewrite'],
        'nonidentity_initial_prefix_control': initial_metric_observed,
        'rows_at_cut23339': cut, 'first_consumers': consumers,
        'source17_first_change_after_cut': first_source_change,
        'projector_commutator_0_1': str(comm[0][1]),
        'public_response_111': response[111], 'public_response_114': response[114],
        'baseline_invoice': invoice, 'repaired_invoice': repaired_invoice,
        'scalar_rewrite': {'invoice': scalar_invoice,
                           'inverse_invoice': scalar_inverse_invoice,
                           'baseline_inverse_invoice': baseline_inverse_invoice,
                           'ADD_delta_forward': -4, 'query_histogram_delta': {},
                           'expanded_forward_cleanup_changed': False,
                           'claim': 'Exact scalar-only saving; no paid-query saving or native price admission'},
        'query_histogram_delta': {'2': 4}, 'ADD_delta': 0,
        'tariff_delta_m64_b1over500': {'exact': '8 * 32^(1/500)',
                                     'strict_lower': str(tariff_lo),
                                     'strict_upper': str(tariff_hi)},
        'native_dirt_defects': defects,
        'controls': ['noncommuting inverse order', 'omitted independent dirt p',
                     'omitted independent dirt q', 'missing source return',
                     'delayed stale compensation', 'missing literal inverse ADD',
                     'omitted source return charge', 'missing scalar compensation',
                     'scalar signed dirty restoration', 'missing scalar transport'],
        'sensitivity': 'equality controls accepted only when their named checks are disabled',
        'claim': 'Exact full-word repair in inherited literal frame model; strict surcharge +4 H2.',
        'limits': ['Boolean public contract; integer target lift retains even defect',
                   'downward excursions charged as literal inverse queries',
                   'no native compiler, all-size precision, owners or recursive moment admission',
                   'no universal noncommuting cost obstruction or optimal repair claim'],
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
