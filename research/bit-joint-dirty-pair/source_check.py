#!/usr/bin/env python3
"""Focused exact binding of the PR4068 common-cut query pair.

Apache-2.0; substantial OpenAI Codex assistance. No producer imports.
Default execution writes deterministic JSON only to stdout.
"""
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parent
HEAD = '5a34918402ae2c0c683d8820ad832970e77f6382'
CANONICAL_WORD = '3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a'
PINS = {
    'inputs/WORD.json.gz': 'c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c',
    'inputs/GEOMETRY.json.gz': 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
    'inputs/PREDECESSOR-PINS.json': '4d03736c497eae94c4e98d33ac10ecacba9e914f9d604787237ff71075dc4e94',
}
N, CUT, END = 660, 23339, 23426
QUERY_RECORDS = {23405: [0, 413, 509, 390, 2, 0],
                 23424: [0, 444, 509, 392, 2, 0]}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def identity_rows():
    return [{i: 1} for i in range(N)]+[{}]


def add(a, b, coefficient):
    out = a.copy()
    for j, v in b.items():
        out[j] = out.get(j, 0)+coefficient*v
        if not out[j]:
            del out[j]
    return out


def replay(records, values, frames, inverse=False):
    values, frames = [x.copy() for x in values], frames[:]
    opened = None
    copies = 0
    ordered = list(reversed(records)) if inverse else records
    for op, d, s, c, f, section in ordered:
        if op == 0:
            before, after = (c, s) if inverse else (s, c)
            require(frames[d] == before, 'MOVE entrance frame')
            frames[d] = after
        elif op == 1:
            require(d != s and d < N and 0 <= s <= N, 'ordinary ADD operands')
            require(frames[d] == frames[s] == f, 'ADD common frame')
            require(d != opened, 'COPY source immutability')
            values[d] = add(values[d], values[s], -c if inverse else c)
        elif op == (3 if inverse else 2):
            require(s == N and opened is None and not values[N], 'COPY zero slot')
            require(frames[d] == c and frames[N] is None, 'COPY frame')
            opened, values[N], frames[N] = d, values[d].copy(), f
            copies += 1
        else:
            require(op == (2 if inverse else 3), 'known opcode')
            require(s == N and opened == d and frames[d] == c and frames[N] == f,
                    'ERASE matching source')
            require(values[N] == values[d], 'ERASE equality')
            opened, values[N], frames[N] = None, {}, None
    require(opened is None, 'no live private copy at selected endpoint')
    return values, frames, copies


def multiply(a, b):
    return tuple(tuple(sum(x*y for x, y in zip(row, col)) for col in zip(*b))
                 for row in a)


def subtract(a, b):
    return tuple(tuple(x-y for x, y in zip(row, other)) for row, other in zip(a, b))


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def matrix_rank(a):
    a = [list(row) for row in a]
    rank = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        value = a[rank][j]
        a[rank] = [x/value for x in a[rank]]
        for i in range(rank+1, len(a)):
            value = a[i][j]
            a[i] = [x-value*y for x, y in zip(a[i], a[rank])]
        rank += 1
        if rank == len(a):
            break
    return rank


def determinant(a):
    a = [list(row) for row in a]
    result = F(1)
    for j in range(len(a)):
        pivot = next((i for i in range(j, len(a)) if a[i][j]), None)
        if pivot is None:
            return F(0)
        if pivot != j:
            result = -result
            a[j], a[pivot] = a[pivot], a[j]
        value = a[j][j]
        result *= value
        a[j] = [x/value for x in a[j]]
        for i in range(j+1, len(a)):
            value = a[i][j]
            a[i] = [x-value*y for x, y in zip(a[i], a[j])]
    return result


def projector(raw, f):
    basis = []
    for label in raw['frames'][f]:
        v = list(map(F, raw['lines'][label]))
        for u in basis:
            coefficient = sum(x*y for x, y in zip(v, u))/sum(x*x for x in u)
            v = [x-coefficient*y for x, y in zip(v, u)]
        if any(v):
            basis.append(v)
        if len(basis) == 8:
            break
    out = tuple(tuple(sum((u[i]*u[j]/sum(x*x for x in u)
                            for u in basis), F(0)) for j in range(8))
                for i in range(8))
    require(multiply(out, out) == out and tuple(zip(*out)) == out,
            'orthogonal frame projector')
    return out


def swap(p):
    q = subtract(eye(8), p)
    return tuple(q[i]+p[i] for i in range(8))+tuple(p[i]+q[i] for i in range(8))


def same_frame_pair(record):
    return record[1] in (413, 444) or (record[0] == 1 and record[2] in (413, 444))


def row_digest(rows):
    canonical = [[[j, row[j]] for j in sorted(row)] for row in rows]
    return sha256(json.dumps(canonical, separators=(',', ':')).encode()).hexdigest()


def rejected(call, expected_reason=None):
    try:
        call()
    except ValueError as exc:
        return expected_reason is None or str(exc) == expected_reason
    return False


def check_source():
    sources = json.loads((ROOT/'INPUT-SOURCES.json').read_text())
    require(sources['predecessor_head'] == HEAD, 'predecessor head')
    manifest_files = {entry['path']: entry for entry in sources['files']}
    blobs = {}
    for path, digest in PINS.items():
        blobs[path] = (ROOT/path).read_bytes()
        require(sha256(blobs[path]).hexdigest() == digest, 'immutable source '+path)
        entry = manifest_files[path]
        require(entry['sha256'] == digest and entry['source_commit'] == HEAD,
                'manifest source binding '+path)
    pins = json.loads(blobs['inputs/PREDECESSOR-PINS.json'])
    word_bytes = gzip.decompress(blobs['inputs/WORD.json.gz'])
    require(sha256(word_bytes).hexdigest() == CANONICAL_WORD == pins['word_canonical_sha256'],
            'canonical word binding')
    word = json.loads(word_bytes)
    raw = json.loads(gzip.decompress(blobs['inputs/GEOMETRY.json.gz']))
    require(len(word['start']) == len(word['final']) == N and raw['h'] == 8,
            'source dimensions')
    records = word['records']
    for i, record in QUERY_RECORDS.items():
        require(records[i] == record, 'actual query record '+str(i))
    require(records[23325] == [1, 444, 17, 1, 509, 2] and
            records[23333] == [1, 413, 17, 1, 509, 2], 'actual common source reads')

    start_frames = word['start']+[None]
    rows, frames, copies = replay(records[:CUT], identity_rows(), start_frames)
    require(copies == 0 and rows[N] == {} and frames[N] is None,
            'private slot inactive at cut')
    restored, old_frames, back_copies = replay(records[:CUT], rows, frames, inverse=True)
    require(restored == identity_rows() and old_frames == start_frames and back_copies == 0,
            'all 660 cut rows unrestricted by exact inverse prefix')
    expected_rows = {
        17: {17: 1},
        413: {413: 1, 469: -1, 605: -1, 87: 1, 17: 1, 22: 1,
              33: 1, 60: 1, 67: 1, 92: 1},
        444: {444: 1, 369: -1, 77: 1, 17: 1, 22: 1, 33: 1,
              60: 1, 87: 1, 38: 1, 92: 1},
    }
    require(all(rows[h] == v and frames[h] == 509 for h, v in expected_rows.items()),
            'full shared source payload rows')
    dirty_pivot = [[rows[h].get(j, 0) for j in (413, 444)] for h in (413, 444)]
    require(dirty_pivot == [[1, 0], [0, 1]], 'independent dirty pivot')
    require(all(word['start'][h] == 0 and word['final'][h] == 1 for h in (413, 444)),
            'selected helpers ZERO to FULL')
    require(not any(same_frame_pair(r) for r in records[CUT:23405]), 'common quiet window')
    require(not any(r[1] == 444 or (r[0] == 1 and r[2] == 444) for r in records[CUT:23424]),
            'second target has no earlier touch')
    require(not any(r[0] in (0, 1) and r[1] == 17 for r in records[CUT:24523]),
            'source17 unchanged through window')

    old_local = records[CUT:END]
    new_local = [records[23405], records[23424]]+[
        r for i, r in enumerate(old_local, CUT) if i not in QUERY_RECORDS]
    old_end, old_end_frames, _ = replay(old_local, rows, frames)
    new_end, new_end_frames, _ = replay(new_local, rows, frames)
    require(old_end == new_end and old_end_frames == new_end_frames,
            'retiming preserves every relevant column and frame')
    back, back_frames, _ = replay(new_local, new_end, new_end_frames, inverse=True)
    require(back == rows and back_frames == frames, 'retimed local literal inverse')

    @lru_cache(None)
    def p(f):
        return projector(raw, f)
    common = p(509)
    P, Q = subtract(p(390), common), subtract(p(392), common)
    zero8 = tuple((F(0),)*8 for _ in range(8))
    for delta in (P, Q):
        require(multiply(delta, delta) == delta and tuple(zip(*delta)) == delta,
                'orthogonal query increment')
        require(matrix_rank(delta) == 2 and multiply(delta, common) == zero8,
                'rank2 and nested query increment')
        require(all(x.denominator & (x.denominator-1) == 0 for row in delta for x in row),
                'dyadic increment')
    comm = subtract(multiply(P, Q), multiply(Q, P))
    require(comm[0][1] == F(1, 8), 'distinct noncommuting address labels')
    require(sum(comm[i][j]*comm[j][i] for i in range(8) for j in range(8)) == -1,
            'no common characteristic-zero flag')
    concat = tuple(P[i]+Q[i] for i in range(8))
    require(matrix_rank(concat) == 4, 'address span dimension4')
    minor_rows, minor_cols = [0, 1, 2, 4], [0, 1, 8, 9]
    minor = tuple(tuple(concat[i][j] for j in minor_cols) for i in minor_rows)
    require(determinant(minor) == F(1, 256), 'dyadic address span minor')
    S, T = swap(P), swap(Q)
    require(multiply(S, S) == eye(16) and multiply(T, T) == eye(16), 'query involutions')
    sdisp, tdisp = subtract(S, eye(16)), subtract(T, eye(16))
    require(matrix_rank(tuple(sdisp[i]+tdisp[i] for i in range(16))) == 4,
            'address displacement span dimension4')
    require(subtract(multiply(S, T), multiply(T, S))[0][1] == F(1, 4),
            'address action noncommutation')

    first_copy_index = next(i for i in range(CUT, len(records)) if records[i][0] == 2)
    first_copy = records[first_copy_index]
    copy_frames = [None]*(N+1)
    copy_frames[first_copy[1]] = first_copy[3]
    dirty_zero_port = identity_rows()
    dirty_zero_port[N] = {N: 1}
    zero_port_rejected = rejected(
        lambda: replay([first_copy], dirty_zero_port, copy_frames), 'COPY zero slot')
    matching_erase = [3]+first_copy[1:]
    clean_copy_rows, clean_copy_frames, clean_copy_count = replay(
        [first_copy, matching_erase], identity_rows(), copy_frames)
    clean_copy_accepted = (clean_copy_rows == identity_rows() and
                           clean_copy_frames == copy_frames and clean_copy_count == 1)
    missing_query = [r for i, r in enumerate(old_local, CUT) if i != 23424]
    controls = {
        'dirty_private_port_rejected_by_original_COPY': zero_port_rejected,
        'clean_private_COPY_ERASE_control_accepted': clean_copy_accepted,
        'Q_replaced_by_P_fails_noncommutation':
            subtract(multiply(P, P), multiply(P, P))[0][1] != F(1, 8),
        'Q_replaced_by_P_collapses_concat_rank': matrix_rank(tuple(row+row for row in P)) == 2,
        'omitted_second_query_fails_frame_contract': rejected(lambda: replay(missing_query, rows, frames)),
    }
    bad_rows = [r.copy() for r in rows]
    bad_rows[444].pop(444)
    bad_pivot = [[F(bad_rows[h].get(j, 0)) for j in (413, 444)] for h in (413, 444)]
    controls['discarding_independent_dirty_input_loses_rank'] = matrix_rank(bad_pivot) == 1
    require(all(controls.values()), 'all semantic defect controls detected')

    def strings(a):
        return [[str(x) for x in row] for row in a]
    return {
        'status': 'PASS_ACTUAL_JOINT_DIRTY_SOURCE_BINDING',
        'predecessor_head': HEAD, 'word_canonical_sha256': CANONICAL_WORD,
        'source_hashes': PINS, 'record_indexing': 'zero based original WORD',
        'entrance_cut': CUT, 'query_records': QUERY_RECORDS,
        'ordinary_independent_input_columns': N,
        'prefix_columns_sha256': row_digest(rows),
        'prefix_inverse_returns_all_660_columns': True,
        'selected_rows': expected_rows, 'independent_dirty_pivot': dirty_pivot,
        'selected_common_frame': 509,
        'private_port': {'index': N, 'value': 'zero', 'frame': None,
                         'prior_COPY_count': copies, 'first_future_COPY_record': first_copy_index,
                         'contract': 'inactive private zero, not a free active arbitrary-dirty role'},
        'quiet_window_half_open': [CUT, 23405],
        'source17_unchanged_until_before': 24523,
        'retimed_window_half_open': [CUT, END],
        'retimed_all_columns_and_frames_equal': True,
        'retimed_local_inverse_checked': True,
        'retimed_end_columns_sha256': row_digest(new_end),
        'query_rank_profile': {'2': 2},
        'projectors': {'common_frame': strings(common), 'P': strings(P), 'Q': strings(Q)},
        'commutator_0_1': '1/8', 'address_swap_commutator_0_1': '1/4',
        'trace_commutator_squared': '-1',
        'geometric_concat_rank_over_Q': 4,
        'address_displacement_concat_rank_over_Q': 4,
        'geometric_minor': {'rows': minor_rows, 'columns': minor_cols, 'determinant': '1/256'},
        'negative_controls': controls,
        'limits': ['prefix and local retiming only; no repeated full-word metric audit',
                   'address geometry over Q is not a representation of payload F2[G]',
                   'formal common-cut diagonal endpoint requires its own algebra theorem',
                   'no changed-tail or source-compensation lower bound',
                   'no native physical execution, recursive moment improvement or new kappa'],
        'no_new_kappa': True,
    }


def main():
    print(json.dumps(check_source(), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
