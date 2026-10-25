#!/usr/bin/env python3
"""Exact source packet extraction, integer/GF(2) replay and rational geometry.

Apache-2.0. Substantial OpenAI Codex assistance. No producer imports. This
certifies finite scalar/frame facts, not native execution or a new bound.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent
N = 660
H = {1: 1322, 2: 1342, 3: 79, 4: 39, 5: 102, 6: 11, 7: 18}
CUTS = (23325, 23339, 23405, 23424, 23426)
WATCH = (17, 22, 33, 60, 87, 92, 271, 293, 352, 371, 413, 444,
         468, 469, 470, 605, 369)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(a, b, c):
    out = a.copy()
    for j, v in b.items():
        out[j] = out.get(j, 0) + c*v
        if out[j] == 0:
            del out[j]
    return out


def mul(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(r, c)) for c in zip(*b))
                 for r in a)


def sub(a, b):
    return tuple(tuple(x-y for x, y in zip(r, s)) for r, s in zip(a, b))


def transpose(a):
    return tuple(zip(*a))


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def projector(raw, frame):
    basis = []
    for label in raw['frames'][frame]:
        v = list(map(F, raw['lines'][label]))
        for u in basis:
            ratio = sum(x*y for x, y in zip(v, u))/sum(x*x for x in u)
            v = [x-ratio*y for x, y in zip(v, u)]
        if any(v):
            basis.append(v)
        if len(basis) == 8:
            break
    return tuple(tuple(sum((u[i]*u[j]/sum(x*x for x in u)
                            for u in basis), F(0)) for j in range(8))
                 for i in range(8))


def swap(p):
    q = sub(eye(8), p)
    return tuple(q[i]+p[i] for i in range(8))+tuple(p[i]+q[i] for i in range(8))


def replay(word, backward=False, initial=None, capture=False, expected_adds=36005):
    values = ([{i: 1} for i in range(N)]+[{}] if initial is None
              else [v.copy() for v in initial])
    frames = list(word['final'] if backward else word['start'])+[None]
    opened = None
    hist, adds, copies, snapshots = Counter(), 0, 0, {}
    records = list(enumerate(word['records']))
    if backward:
        records.reverse()
    for i, (op, d, s, c, f, section) in records:
        if capture and i in CUTS:
            snapshots[i] = {'rows': {h: values[h].copy() for h in WATCH},
                            'frames': {h: frames[h] for h in WATCH}}
        if op == 0:
            before, after = (c, s) if backward else (s, c)
            need(frames[d] == before, 'MOVE endpoint at '+str(i))
            frames[d] = after
            hist[f] += 1
        elif op == 1:
            need(d != s and frames[d] == frames[s] == f,
                 'common ADD frame at '+str(i))
            need(d != opened, 'COPY immutability at '+str(i))
            values[d] = add(values[d], values[s], -c if backward else c)
            adds += 1
        elif op == (3 if backward else 2):
            need(s == N and opened is None and values[N] == {}, 'private COPY')
            need(frames[d] == c and frames[N] is None, 'COPY frames')
            opened, values[N], frames[N] = d, values[d].copy(), f
            hist[7] += 1
            copies += 1
        else:
            need(op == (2 if backward else 3), 'known opcode')
            need(s == N and opened == d and frames[d] == c and frames[N] == f,
                 'ERASE source')
            need(values[N] == values[d], 'ERASE snapshot equality')
            opened, values[N], frames[N] = None, {}, None
    need(opened is None and values[N] == {}, 'private restoration')
    need(frames[:-1] == (word['start'] if backward else word['final']), 'end frames')
    need(dict(hist) == H and adds == expected_adds and copies == 9, 'full frozen tariff')
    return values, snapshots


def suffix_columns(records, cut, skip=()):
    cols = [[0, 0] for _ in range(N+1)]
    cols[413], cols[444] = [1, 0], [0, 1]
    for i in range(cut, len(records)):
        if i in skip:
            continue
        op, d, s, c, _, _ = records[i]
        if op == 1:
            cols[d] = [a+c*b for a, b in zip(cols[d], cols[s])]
        elif op == 2:
            cols[N] = cols[d].copy()
        elif op == 3:
            need(cols[N] == cols[d], 'suffix ERASE columns')
            cols[N] = [0, 0]
    return cols


def serialized(a):
    return [[str(x) for x in row] for row in a]


def touches(record, registers):
    op, d, s, _, _, _ = record
    return d in registers or (op == 1 and s in registers)


def main():
    pins = json.loads((PACKAGE/'inputs/PREDECESSOR-PINS.json').read_text())
    inputs = {}
    for item in pins['files']:
        data = (PACKAGE/item['path']).read_bytes()
        need(sha256(data).hexdigest() == item['sha256'],
             'source pin '+item['path'])
        inputs[item['path']] = data
    blob = gzip.decompress(inputs['inputs/WORD.json.gz'])
    need(sha256(blob).hexdigest() == pins['word_canonical_sha256'], 'canonical word pin')
    word = json.loads(blob)
    raw = json.loads(gzip.decompress(inputs['inputs/GEOMETRY.json.gz']))
    records = word['records']
    expected = {
        23318: [0, 17, 183, 509, 2, 0],
        23325: [1, 444, 17, 1, 509, 2],
        23333: [1, 413, 17, 1, 509, 2],
        23405: [0, 413, 509, 390, 2, 0],
        23406: [1, 413, 605, 1, 390, 2],
        23407: [0, 413, 390, 517, 1, 0],
        23408: [0, 469, 52, 517, 6, 0],
        23409: [1, 413, 469, 1, 517, 2],
        23424: [0, 444, 509, 392, 2, 0],
        23425: [1, 444, 369, 1, 392, 2],
        23486: [0, 444, 392, 513, 1, 0],
        23488: [1, 474, 444, 1, 513, 2],
        23515: [1, 478, 413, 1, 517, 2],
        24523: [1, 17, 33, 1, 509, 4],
        24883: [0, 17, 509, 395, 2, 0],
    }
    for i, record in expected.items():
        need(records[i] == record, 'selected record '+str(i))
    end, snapshots = replay(word, capture=True)
    identity = [{i: 1} for i in range(N)]+[{}]
    need(replay(word, backward=True, initial=end)[0] == identity, 'literal inverse')
    for j in range(N):
        want = {j: 1}
        if 111 <= j < 222:
            want[j-111] = 1
        need({k: v % 2 for k, v in end[j].items() if v % 2} == want,
             'complete GF(2) boundary '+str(j))
        if not 111 <= j < 222:
            need(end[j] == {j: 1}, 'integer spectator restoration '+str(j))
    need(end[111].get(236) == -2, 'integer target is not the Boolean clean shear')
    entry = snapshots[23339]['rows']
    common = {17: 1, 22: 1, 33: 1, 60: 1, 87: 1, 92: 1}
    residual_413 = {413: 1, 469: -1, 605: -1, 67: 1}
    residual_444 = {444: 1, 369: -1, 77: 1, 38: 1}
    need(entry[413] == add(common, residual_413, 1), 'complete payload 413')
    need(entry[444] == add(common, residual_444, 1), 'complete payload 444')
    need(entry[17] == {17: 1}, 'actual original source17')
    pivot = [[entry[h].get(j, 0) for j in (413, 444)] for h in (413, 444)]
    need(pivot == [[1, 0], [0, 1]], 'independent arbitrary dirt')
    need(not any(touches(r, {413, 444}) for r in records[23339:23405]),
         'common quiet window')
    need(not any(r[1] == 17 and r[0] in (0, 1)
                 for r in records[23339:24523]), 'unchanged source17 window')

    @lru_cache(None)
    def frame(f):
        a = projector(raw, f)
        need(mul(a, a) == a and transpose(a) == a, 'orthogonal projector')
        return a
    p0 = frame(509)
    p, q = sub(frame(390), p0), sub(frame(392), p0)
    for a in (p, q):
        need(mul(a, a) == a and transpose(a) == a, 'increment projector')
        need(sum(a[i][i] for i in range(8)) == 2, 'rank two query')
        need(mul(a, p0) == tuple((F(0),)*8 for _ in range(8)), 'orthogonal increment')
        need(all(x.denominator & (x.denominator-1) == 0 for row in a for x in row),
             'dyadic specialization')
    comm = sub(mul(p, q), mul(q, p))
    need(comm[0][1] == F(1, 8), 'noncommuting witness')
    native_comm = sub(mul(swap(p), swap(q)), mul(swap(q), swap(p)))
    need(native_comm[0][1] == F(1, 4), 'address action witness')
    source_first_departure = next(i for i in range(23339, len(records))
                                  if records[i][0] == 0 and records[i][1] == 17)
    need(source_first_departure == 24883, 'source first departure')

    # This retiming adds no gates: both query targets are untouched during
    # their earlier movement. It proves common-frame scalar legality only.
    retimed = dict(word)
    retimed['records'] = records[:23339]+[records[23405], records[23424]]+[
        r for i, r in enumerate(records[23339:], 23339) if i not in (23405, 23424)]
    retimed_end, _ = replay(retimed)
    need(retimed_end == end, 'cost-preserving local retiming')
    need(replay(retimed, backward=True, initial=retimed_end)[0] == identity,
         'retimed literal inverse')
    cols = suffix_columns(records, 23339)
    need(cols[111] == [1, 0] and cols[114] == [0, 1], 'two distinct public demands')
    need(cols == suffix_columns(records, 23426), 'later cut demand agreement')
    need(cols[413] == cols[478] == [1, 0], 'first restored helper demands')
    need(cols[444] == cols[474] == [0, 1], 'second restored helper demands')
    after = suffix_columns(records, 23516)
    need(all(v == [0, 0] for v in after[111:222]), 'both deliveries already completed')

    controls = {}
    for name, altered in (
        ('omit_second_query', records[:23424]+records[23424+1:]),
        ('borrow_source_without_reset', records[:23339]+[[0, 17, 509, 390, 2, 99]]+
         records[23339:]),
    ):
        bad = dict(word, records=altered)
        try:
            replay(bad)
        except ValueError as exc:
            controls[name] = str(exc)
        else:
            raise ValueError('negative control accepted: '+name)
    controls['drop_delivery_23488_changes_public114'] = (
        suffix_columns(records, 23339, skip=(23488,))[114] != cols[114])
    need(controls['drop_delivery_23488_changes_public114'], 'delivery defect detected')
    wrong_comm = sub(mul(p, p), mul(p, p))
    controls['replace_Q_by_P_rejects_noncommuting_witness'] = wrong_comm[0][1] != F(1, 8)
    missing_dirty = [pivot[0], [pivot[1][0], 0]]
    bad_determinant = missing_dirty[0][0]*missing_dirty[1][1]-missing_dirty[0][1]*missing_dirty[1][0]
    controls['zero_dirty_444_loses_independence'] = bad_determinant == 0
    need(all(controls[k] for k in controls if isinstance(controls[k], bool)),
         'all defect controls detected')

    # Optional exact scalar fanout seed. This changes no paid query.
    replacement = [records[23332]]+records[23333:23339]+[
        [1, 444, 413, 1, 509, 2],
        [1, 444, 468, 1, 509, 2],
        [1, 444, 371, -1, 509, 2],
    ]
    seed = dict(word, records=records[:23325]+replacement+records[23339:])
    seed_end, _ = replay(seed, expected_adds=36001)
    need(seed_end == end, '13 to 9 fanout exact integer boundary')
    need(replay(seed, backward=True, initial=seed_end, expected_adds=36001)[0] == identity,
         'fanout seed literal inverse')
    wrong_replacement = [r.copy() for r in replacement]
    wrong_replacement[-1][3] = 1
    wrong_seed = dict(word, records=records[:23325]+wrong_replacement+records[23339:])
    wrong_end, _ = replay(wrong_seed, expected_adds=36001)
    controls['wrong_compensation_sign_changes_integer_lift'] = wrong_end != end
    controls['wrong_compensation_sign_is_invisible_mod_two'] = all(
        {k: v % 2 for k, v in a.items() if v % 2} ==
        {k: v % 2 for k, v in b.items() if v % 2} for a, b in zip(wrong_end, end))
    need(controls['wrong_compensation_sign_changes_integer_lift'] and
         controls['wrong_compensation_sign_is_invisible_mod_two'], 'integer sign control')

    lifetimes = {}
    for h in (413, 444):
        uses = [(i, r) for i, r in enumerate(records) if touches(r, {h})]
        moves = [(i, r) for i, r in uses if r[0] == 0]
        lifetimes[h] = {'first_use': uses[0], 'last_use': uses[-1],
                        'moves': moves, 'terminal_frame': word['final'][h]}
    result = {
        'status': 'PASS_ACTUAL_NONCOMMUTING_SHARED_SOURCE_PACKET',
        'source_commit': pins['source_commit'],
        'word_canonical_sha256': pins['word_canonical_sha256'],
        'record_indexing': 'zero based',
        'selected_records': expected,
        'cut_snapshots_all_watched_integer_columns': snapshots,
        'entry_common_original_source_row': common,
        'entry_residual_rows': {413: residual_413, 444: residual_444},
        'independent_dirty_pivot': pivot,
        'projectors': {'P509': serialized(p0), 'P': serialized(p), 'Q': serialized(q)},
        'commutator': serialized(comm),
        'native_address_commutator_0_1': str(native_comm[0][1]),
        'common_quiet_window': [23339, 23405],
        'source17_unchanged_common_frame_until_before': 24523,
        'source17_frame509_until_before': source_first_departure,
        'next_delivery_records': {413: 23515, 444: 23488},
        'suffix_all_660_output_integer_columns': cols[:N],
        'public_independence_witness': {111: cols[111], 114: cols[114]},
        'helper_lifetimes': lifetimes,
        'baseline': {
            'minimal_query_packet': {'rank_histogram': {2: 2}, 'rank_mass': 4, 'ADDs': 0},
            'source_fanout_setup_records_half_open': [23317, 23339],
            'source_fanout_setup': {'rank_histogram': {2: 5, 3: 4}, 'rank_mass': 22, 'ADDs': 13},
            'frozen_full_word': {'rank_histogram': H, 'ADDs': 36005, 'COPY_episodes': 9},
            'retiming_added_operations': 0,
            'native_retiming_transport_cost': 'not established',
        },
        'optional_scalar_fanout_seed': {
            'replace_records_half_open': [23325, 23339],
            'replacement_records': replacement,
            'old_ADDs': 13, 'new_ADDs': 9, 'complete_new_ADDs': 36001,
            'paid_rank_histogram_change': {},
            'exact_integer_and_literal_inverse_checked': True,
            'remaining': ['forward/reverse positive-prefix guards',
                          'physical schedule admission; no recursive saving'],
        },
        'negative_controls': controls,
        'coverage': ['all 660 independent scalar entrance columns over integers',
                     'all Boolean endpoints and integer source/helper restoration',
                     'literal forward/inverse for original and retimed word',
                     'local exact dyadic projectors over Q and every odd prime field',
                     'all 660 output columns for frozen suffix perturbations'],
        'limits': ['no positive query saving', 'no faithful group algebra equality claimed',
                   'no native tape route or phase verification',
                   'no paid shared-source compensation constructed',
                   'no changed precision or recursive moment claim'],
        'no_new_kappa': True,
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write receipt to this explicit path')
    args = parser.parse_args()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.output is None:
        print(encoded, end='')
    else:
        args.output.write_text(encoded)
        print('PASS_ACTUAL_NONCOMMUTING_SHARED_SOURCE_PACKET records=23405,23424 '
              'rank_histogram={2:2} public_pivot=111,114 no_new_kappa')


if __name__ == '__main__':
    main()
