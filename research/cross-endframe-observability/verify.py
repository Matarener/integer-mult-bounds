#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact census of pooled rank-seven/rank-eight terminal observations.

This checker is independent of the PR2979 producer and its verifier. It reads
only the two pinned word JSONs, expands their non-target linear maps backwards
as formal warp-word polynomials over Q, and tests exact nuisance cancellation.
"""
from collections import defaultdict
from fractions import Fraction as F
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'rank7-joint-endframes' / 'data'
HASHES = {
    'base': 'abaf67bfcb257528658c906b612f57025617592bd7889828f92b97a5f4f4300d',
    'extra': 'e0eaf64c4d5d324693d43889bce1b9e53e8da00402105c8c978fd102f208bed7',
}
TARGET = set(range(112, 224))
EXPECTED_FORM = {
    (224, ()): F(-1, 2), (227, ()): F(1, 2),
    (229, ()): F(-1, 2), (231, ()): F(-1, 2),
    (232, ()): F(-1, 2), (233, ()): F(1, 2),
    (234, ()): F(-1, 2), (235, ()): F(1, 2),
    (236, ()): F(1, 2), (237, ()): F(-1, 2),
    (238, ()): F(1, 2), (239, ()): F(-1, 2),
    (276, ()): F(-1, 2), (292, ()): F(-1, 2),
}
EXPECTED_READOUT = {7: F(-1), 232: F(-1), 236: F(1), 238: F(1)}
EXPECTED_RANK9 = (
    ({224: 1, 229: 1, 235: -1, 237: 1, 238: -1, 239: 1},
     {7: 2, 87: -2, 238: -2}),
    ({227: 1, 231: -1, 233: 1, 236: 1, 237: -1, 239: -1},
     {7: -2, 236: 2, 239: 2}),
    ({229: 1, 231: 1, 236: 1, 237: -1, 238: 1, 239: -1},
     {7: -2, 76: -1, 231: 1}),
    ({232: 1, 234: 1, 237: -1, 239: -1, 276: 1, 292: 1},
     {7: -2, 87: 2, 232: 2, 239: 2}),
    ({232: 1, 234: 1, 237: 1, 239: 1, 276: 1, 292: 1},
     {7: 2, 76: 1, 232: 2, 233: -1}),
    ({224: 1, 227: -1, 229: 1, 231: 1, 233: -1, 235: -1, 236: -1, 238: -1},
     {76: -1, 233: 1, 236: -2, 238: -2}),
    ({224: 1, 227: 1, 229: 1, 231: -1, 233: 1, 235: -1, 236: 1, 238: -1},
     {87: -2, 236: 2, 238: -2, 239: 2}),
    ({224: 1, 229: 1, 232: 1, 234: 1, 235: -1, 238: -1, 276: 1, 292: 1},
     {232: 2, 238: -2, 239: 2}),
    ({227: 1, 231: -1, 232: -1, 233: 1, 234: -1, 236: 1, 276: -1, 292: -1},
     {87: -2, 232: -2, 236: 2}),
    ({229: 1, 231: 1, 232: 1, 234: 1, 236: 1, 238: 1, 276: 1, 292: 1},
     {231: 1, 232: 2, 233: -1}),
    ({224: 1, 227: -1, 229: 1, 231: 1, 232: 1, 233: -1, 234: 1,
      235: -1, 236: -1, 237: 1, 238: -1, 239: 1, 276: 1, 292: 1},
     {7: 2, 232: 2, 236: -2, 238: -2}),
)
EXPECTED_RANK9_QUARTET = (
    ({224: 1, 229: 2, 231: 1, 235: -1, 236: 1},
     {76: -1, 87: -2, 231: 1, 238: -2}),
    ({224: 1, 231: -1, 235: -1, 236: -1, 238: -2},
     {231: -1, 233: 1, 238: -2, 239: 2}),
    ({227: 1, 229: -1, 231: -2, 233: 1, 238: -1},
     {76: 1, 231: -1, 236: 2, 239: 2}),
    ({227: 1, 229: 1, 233: 1, 236: 2, 238: 1},
     {87: -2, 231: 1, 233: -1, 236: 2}),
    ({224: 1, 227: -1, 233: -1, 235: -1, 236: -2,
      237: 1, 238: -2, 239: 1},
     {7: 2, 231: -1, 233: 1, 236: -2, 238: -2}),
    ({224: 1, 227: -1, 229: 2, 231: 2, 232: 1, 233: -1,
      234: 1, 235: -1, 276: 1, 292: 1},
     {76: -1, 231: 1, 232: 2, 236: -2, 238: -2}),
)


def require(ok, why):
    if not ok:
        raise ValueError(why)


def span(basis):
    values = {0}
    for v in basis:
        require(isinstance(v, int) and 0 <= v < 512, 'frame outside GF(2)^9')
        values |= {x ^ v for x in tuple(values)}
    return frozenset(values)


def dimension_union(spaces):
    pivots = {}
    for space in spaces:
        for value in space:
            x = value
            while x:
                pivot = x.bit_length() - 1
                if pivot in pivots:
                    x ^= pivots[pivot]
                else:
                    pivots[pivot] = x
                    break
    return len(pivots)


def load_provider(name):
    raw = (DATA / f'WORD-{name}.json.gz').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == HASHES[name], f'{name} source bytes changed')
    p = json.loads(gzip.decompress(raw))
    require(len(p['ports']) == 112 and len(p['warps']) == 72, f'{name} provider shape')

    live = set(range(704)) - set(p['removed'])
    frames = [span([p['ports'][r]]) if r < 112 else span([]) for r in range(704)]
    for r, basis in p['start_extra'].items():
        frames[int(r)] = span(basis)

    warps_at = defaultdict(list)
    for i, warp in enumerate(p['warps']):
        require(0 <= warp[0] <= len(p['B']), f'{name} warp position')
        warps_at[warp[0]].append(['warp', warp[1], i + 1, warp[3], warp[4]])
    events = list(p['A'])
    for i in range(len(p['B']) + 1):
        events.extend(warps_at.get(i, []))
        if i < len(p['B']):
            events.append(p['B'][i])
    events.extend(p['restore'])

    for g in events:
        kind, dest = g[:2]
        nxt = span(g[4]) if kind == 'warp' else span(g[-1])
        regs = [dest] if kind in ('warp', 'scale') else [dest, g[2]]
        for r in regs:
            require(r in live, f'{name} event touches removed register')
            frames[r] = nxt

    ops = []
    for g in events[p['prelude_events']:]:
        if g[1] in TARGET:
            continue
        require(g[0] != 'add' or g[2] not in TARGET, f'{name} non-target reads target')
        ops.append(g)
    eligible = (set(range(224, 704)) & live) - (
        set(map(int, p['helper_final'])) | set(map(int, p['start_extra']))
        | {c['source'] for c in p['initial_corrections']}
    )
    require(len(ops) == 5207, f'{name} non-target operator count')
    require(len(eligible) == 207, f'{name} eligible-input count')
    active = live - TARGET
    require(len(active) == 520, f'{name} tracked terminal count')

    groups = {7: defaultdict(list), 8: defaultdict(list)}
    for r in sorted(active):
        size = len(frames[r])
        if size == 128:
            groups[7][frames[r]].append(r)
        elif size == 256:
            groups[8][frames[r]].append(r)
    require((len(groups[7]), sum(map(len, groups[7].values()))) == (49, 104),
            f'{name} rank-seven endpoint census')
    require((len(groups[8]), sum(map(len, groups[8].values()))) == (126, 336),
            f'{name} rank-eight endpoint census')
    return raw, ops, eligible, groups


def add(dst, src, q):
    for key, c in list(src.items()):
        value = dst.get(key, F(0)) + q * c
        if value:
            dst[key] = value
        else:
            dst.pop(key, None)


def terminal_rows(ops, terminals):
    """Return exact formal-polynomial rows: terminal registers -> initial state."""
    state = [{} for _ in range(704)]
    for r in terminals:
        state[r][(r, ())] = F(1)
    for g in reversed(ops):
        kind, dest = g[:2]
        if kind == 'add':
            add(state[g[2]], state[dest], F(g[3], g[4]))
        elif kind == 'scale':
            q = F(g[2], g[3])
            state[dest] = {key: q * c for key, c in state[dest].items()}
        else:
            t = g[2]
            state[dest] = {
                (r, word[:-1] if word and word[-1] == -t else word + (t,)): c
                for (r, word), c in state[dest].items()
            }
    rows = {r: {} for r in terminals}
    for initial, poly in enumerate(state):
        for (terminal, word), c in poly.items():
            rows[terminal][(initial, word)] = c
    return rows


def nuisance_kernel(channels, rows, eligible):
    """Basis for readouts whose every protected coefficient polynomial vanishes."""
    basis = {}
    keys = set().union(*(rows[r].keys() for r in channels))
    for key in sorted(keys):
        if key[0] in eligible:
            continue
        v = [rows[r].get(key, F(0)) for r in channels]
        for pivot, row in sorted(basis.items()):
            q = v[pivot]
            if q:
                v = [x - q * y for x, y in zip(v, row)]
        pivot = next((j for j, value in enumerate(v) if value), None)
        if pivot is not None:
            q = v[pivot]
            basis[pivot] = [value / q for value in v]

    free = [j for j in range(len(channels)) if j not in basis]
    kernel = []
    for f in free:
        v = [F(0)] * len(channels)
        v[f] = F(1)
        for pivot in sorted(basis, reverse=True):
            v[pivot] = -sum(basis[pivot][j] * v[j]
                            for j in range(pivot + 1, len(channels)))
        kernel.append(v)
    return kernel


def eligible_forms(channels, kernel, rows, eligible):
    forms = []
    for readout in kernel:
        form = {}
        for r, q in zip(channels, readout):
            if not q:
                continue
            for key, c in rows[r].items():
                if key[0] in eligible:
                    value = form.get(key, F(0)) + q * c
                    if value:
                        form[key] = value
                    else:
                        form.pop(key, None)
        forms.append(form)
    return forms


def sparse_rank(vectors):
    basis = {}
    rank = 0
    for vector in vectors:
        v = dict(vector)
        while v:
            pivot = min(v)
            if pivot not in basis:
                q = v[pivot]
                basis[pivot] = {j: c / q for j, c in v.items()}
                rank += 1
                break
            q = v[pivot]
            for j, c in basis[pivot].items():
                value = v.get(j, F(0)) - q * c
                if value:
                    v[j] = value
                else:
                    v.pop(j, None)
    return rank


def scan_join_rank(groups, rows, eligible, arity, join_rank):
    spaces = sorted(groups, key=lambda s: tuple(sorted(s)))
    join_count = 0
    positive = []
    for selected in combinations(spaces, arity):
        if dimension_union(selected) != join_rank:
            continue
        join_count += 1
        channels = [r for space in selected for r in groups[space]]
        kernel = nuisance_kernel(channels, rows, eligible)
        forms = eligible_forms(channels, kernel, rows, eligible)
        rank = sparse_rank(forms)
        if rank:
            positive.append((channels, kernel, forms, rank))
    return join_count, positive


def canonical_rank9_witness(channels, readout, form):
    pivot = min(form)
    scale = F(1) / form[pivot]
    normalized_form = tuple(sorted((key, q * scale) for key, q in form.items()))
    normalized_readout = tuple(sorted((r, q * scale)
                                      for r, q in zip(channels, readout) if q))
    return normalized_form, normalized_readout


def expected_rank9_signatures():
    return {
        (
            tuple(sorted(((r, ()), F(q)) for r, q in form.items())),
            tuple(sorted((r, F(q)) for r, q in readout.items())),
        )
        for form, readout in EXPECTED_RANK9
    }


def expected_rank9_quartet_signatures():
    return {
        (
            tuple(sorted(((r, ()), F(q)) for r, q in form.items())),
            tuple(sorted((r, F(q)) for r, q in readout.items())),
        )
        for form, readout in EXPECTED_RANK9_QUARTET
    }


def mod_three(q):
    """Reduce a rational with denominator prime to 3 into GF(3)."""
    q = F(q)
    denominator = q.denominator % 3
    require(denominator != 0, 'GF(3) screen encountered a denominator divisible by 3')
    return q.numerator * pow(denominator, -1, 3) % 3


def add_mod_three(basis, row):
    """Insert one short vector into a normalized row basis over GF(3)."""
    value = list(row)
    for pivot in sorted(basis):
        if value[pivot]:
            q = value[pivot]
            value = [(x - q * y) % 3 for x, y in zip(value, basis[pivot])]
    pivot = next((j for j, q in enumerate(value) if q), None)
    if pivot is not None:
        q = pow(value[pivot], -1, 3)
        basis[pivot] = [q * x % 3 for x in value]


def scan_rank9_quartets(rank7, rows, eligible):
    """Screen every four-class support over GF(3), then recheck candidates over Q."""
    spaces = sorted(rank7, key=lambda s: tuple(sorted(s)))
    channels = sorted(r for space in spaces for r in rank7[space])
    global_kernel = nuisance_kernel(channels, rows, eligible)
    width = len(global_kernel)
    require(width == 9, 'global rank-seven protected kernel dimension changed')
    index = {r: i for i, r in enumerate(channels)}

    # A rational rank drop forces the same drop modulo 3 because these exact
    # kernel coordinates have denominators coprime to 3. Thus this is a
    # complete candidate screen; every candidate is subsequently checked over Q.
    local_rows = []
    global_mod_three_basis = {}
    for space in spaces:
        basis = {}
        for terminal in rank7[space]:
            row = [mod_three(global_kernel[j][index[terminal]]) for j in range(width)]
            add_mod_three(global_mod_three_basis, row)
            add_mod_three(
                basis,
                row,
            )
        local_rows.append(tuple(basis[j] for j in sorted(basis)))
    require(len(global_mod_three_basis) == width,
            'global protected-kernel basis loses rank modulo 3')

    outside_rank_histogram = defaultdict(int)
    exact_rank_histogram = defaultdict(int)
    join_rank_histogram = defaultdict(int)
    observed_forms = set()
    observed_witnesses = set()
    candidate_count = 0
    total = 0
    for selected_indices in combinations(range(len(spaces)), 4):
        total += 1
        omitted = set(selected_indices)
        outside_basis = {}
        for i, local in enumerate(local_rows):
            if i not in omitted:
                for row in local:
                    add_mod_three(outside_basis, row)
                if len(outside_basis) == width:
                    break
        outside_rank_histogram[len(outside_basis)] += 1
        if len(outside_basis) == width:
            continue

        candidate_count += 1
        selected = [spaces[i] for i in selected_indices]
        join_rank = dimension_union(selected)
        join_rank_histogram[join_rank] += 1
        require(join_rank == 9, 'four-class rank-defect candidate has non-nine join')
        selected_channels = [r for space in selected for r in rank7[space]]
        kernel = nuisance_kernel(selected_channels, rows, eligible)
        forms = eligible_forms(selected_channels, kernel, rows, eligible)
        eligible_rank = sparse_rank(forms)
        require(eligible_rank > 0, 'screened quartet has no exact eligible signal')
        exact_rank_histogram[eligible_rank] += 1
        for readout, form in zip(kernel, forms):
            if not form:
                continue
            require(all(not word for _, word in form),
                    'quartet signal has a non-scalar formal-warp term')
            signature = canonical_rank9_witness(selected_channels, readout, form)
            observed_forms.add(signature[0])
            observed_witnesses.add(signature)

    expected_old = expected_rank9_signatures()
    expected_new = expected_rank9_quartet_signatures()
    expected_forms = {form for form, _ in expected_old | expected_new}
    new_forms = {form for form, _ in expected_new}
    require(total == 211876, f'four-class support count changed: {total}')
    require(dict(outside_rank_histogram) == {6: 1, 7: 94, 8: 1258, 9: 210523},
            f'four-class GF(3) screen histogram changed: {dict(outside_rank_histogram)}')
    require(candidate_count == 1353, f'four-class candidate count changed: {candidate_count}')
    require(dict(join_rank_histogram) == {9: 1353},
            f'four-class candidate join histogram changed: {dict(join_rank_histogram)}')
    require(dict(exact_rank_histogram) == {1: 1258, 2: 94, 3: 1},
            f'four-class exact eligible-rank histogram changed: {dict(exact_rank_histogram)}')
    require(observed_forms == expected_forms,
            f'four-class normalized input-form set changed: {len(observed_forms)}')
    require(expected_new <= observed_witnesses,
            'one or more sparse quartet readout identities were not reproduced')
    require(sparse_rank([dict(form) for form in new_forms]) == 5,
            'six additional quartet forms do not span a five-space')
    five_term = [dict(form) for form in new_forms if len(form) == 5]
    require(len(five_term) == 4 and sparse_rank(five_term) == 3,
            'four five-term forms do not have the expected three-dimensional span')

    observed_registers = {r for _, readout in EXPECTED_RANK9_QUARTET for r in readout}
    terminal_owner = {r: space for space in spaces for r in rank7[space]}
    observed_spaces = {terminal_owner[r] for r in observed_registers}
    require(len(observed_registers) == 9 and len(observed_spaces) == 7,
            'sparse readout block terminal footprint changed')
    require(dimension_union(observed_spaces) == 9,
            'sparse readout block endpoints no longer have a rank-nine join')
    return {
        'four_class_supports': total,
        'gf3_outside_rank_histogram': dict(outside_rank_histogram),
        'screened_candidates': candidate_count,
        'candidate_join_rank_histogram': dict(join_rank_histogram),
        'exact_eligible_rank_histogram': dict(exact_rank_histogram),
        'unique_scalar_forms': len(observed_forms),
        'new_sparse_forms': len(new_forms),
        'new_forms_span': 5,
        'five_term_forms_span': 3,
        'readout_registers': len(observed_registers),
        'readout_endpoint_classes': len(observed_spaces),
        'readout_join_rank': 9,
    }


def normalized_witness(channels, kernel, forms):
    witnesses = [(lam, form) for lam, form in zip(kernel, forms) if form]
    require(len(witnesses) == 1, 'candidate must have one nonzero eligible witness')
    lam, form = witnesses[0]
    coefficients = {r: q for r, q in zip(channels, lam) if q}
    require(7 in coefficients, 'candidate witness missing register 7')
    scale = F(-1) / coefficients[7]
    coefficients = {r: q * scale for r, q in coefficients.items()}
    form = {key: q * scale for key, q in form.items()}
    return coefficients, form


def analyze(name):
    raw, ops, eligible, groups = load_provider(name)
    rank7 = groups[7]
    rank8 = groups[8]
    terminals = sorted({r for g in (rank7, rank8) for rs in g.values() for r in rs})
    rows = terminal_rows(ops, terminals)

    single7 = sum(sparse_rank(eligible_forms(rs, nuisance_kernel(rs, rows, eligible), rows, eligible))
                  for rs in rank7.values())
    single8 = sum(sparse_rank(eligible_forms(rs, nuisance_kernel(rs, rows, eligible), rows, eligible))
                  for rs in rank8.values())
    require(single7 == 0, f'{name} individual rank-seven endpoint exposed eligible input')
    require(single8 == 0, f'{name} individual rank-eight endpoint exposed eligible input')

    pair8_count, pair8_positive = scan_join_rank(rank7, rows, eligible, 2, 8)
    pair9_count, pair9_positive = scan_join_rank(rank7, rows, eligible, 2, 9)
    triple8_count, triple8_positive = scan_join_rank(rank7, rows, eligible, 3, 8)
    triple9_count, triple9_positive = scan_join_rank(rank7, rows, eligible, 3, 9)
    require((pair8_count, pair9_count) == (413, 763), f'{name} rank-eight/nine pair-join counts')
    require((triple8_count, triple9_count) == (2571, 15853),
            f'{name} rank-eight/nine triple-join counts')
    require(not pair9_positive, f'{name} rank-nine pair exposed an eligible input')
    require(len(pair8_positive) == 1 and len(triple8_positive) == 1,
            f'{name} unexpected rank-eight pair/triple eligible observation')

    pair = pair8_positive[0]
    coeffs, form = normalized_witness(pair[0], pair[1], pair[2])
    require(coeffs == EXPECTED_READOUT, f'{name} pair readout identity changed: {coeffs}')
    require(form == EXPECTED_FORM, f'{name} pair input form changed: {form}')
    triple_coeffs, triple_form = normalized_witness(
        triple8_positive[0][0], triple8_positive[0][1], triple8_positive[0][2]
    )
    require(triple_coeffs == EXPECTED_READOUT and triple_form == EXPECTED_FORM,
            f'{name} triple did not reproduce the same four-register witness')

    rank9_by_dimension = defaultdict(int)
    rank9_directions = defaultdict(set)
    for channels, kernel, forms, eligible_rank in triple9_positive:
        rank9_by_dimension[eligible_rank] += 1
        for readout, eligible_form in zip(kernel, forms):
            if eligible_form:
                signature = canonical_rank9_witness(channels, readout, eligible_form)
                rank9_directions[signature[0]].add(signature[1])
    expected_rank9 = expected_rank9_signatures()
    observed_rank9 = {
        (form, next(iter(readouts)))
        for form, readouts in rank9_directions.items()
        if len(readouts) == 1
    }
    require(dict(rank9_by_dimension) == {1: 50, 2: 2},
            f'{name} rank-nine triple eligible-rank histogram: {dict(rank9_by_dimension)}')
    require(len(rank9_directions) == 11 and all(len(v) == 1 for v in rank9_directions.values()),
            f'{name} rank-nine witness de-duplication')
    require(observed_rank9 == expected_rank9,
            f'{name} rank-nine exact witnesses changed: {len(observed_rank9)} forms')
    rank9_forms = [dict(form) for form in rank9_directions]
    require(sparse_rank(rank9_forms) == 5,
            f'{name} rank-nine eligible forms do not span the expected five-space')
    new_rank9_forms = [dict(form) for form in rank9_directions if len(form) in (6, 8)]
    require(len(new_rank9_forms) == 10 and sparse_rank(new_rank9_forms) == 5,
            f'{name} ten additional rank-nine forms are not a five-space')
    require(sum(len(form) == 6 for form in new_rank9_forms) == 5
            and sum(len(form) == 8 for form in new_rank9_forms) == 5,
            f'{name} rank-nine support-size census')

    quartet_result = scan_rank9_quartets(rank7, rows, eligible)

    # Each of the four readouts is necessary; deleting any one kills the signal.
    for removed in EXPECTED_READOUT:
        smaller = [r for r in pair[0] if r != removed]
        kernel = nuisance_kernel(smaller, rows, eligible)
        forms = eligible_forms(smaller, kernel, rows, eligible)
        require(sparse_rank(forms) == 0, f'{name} witness survived deleting register {removed}')

    return {
        'sha256': hashlib.sha256(raw).hexdigest(),
        'individual_rank7_classes': len(rank7),
        'individual_rank8_classes': len(rank8),
        'rank7_pairs_with_rank8_join': pair8_count,
        'positive_pair_classes': len(pair8_positive),
        'rank7_pairs_with_rank9_join': pair9_count,
        'positive_rank9_pair_classes': len(pair9_positive),
        'rank7_triples_with_rank8_join': triple8_count,
        'positive_rank8_triple_classes': len(triple8_positive),
        'rank7_triples_with_rank9_join': triple9_count,
        'positive_rank9_triple_classes': len(triple9_positive),
        'rank9_eligible_rank_histogram': dict(rank9_by_dimension),
        'rank9_unique_forms': len(rank9_directions),
        'rank9_form_span': 5,
        'rank9_quartet_census': quartet_result,
        'witness_readout': coeffs,
        'witness_form': form,
    }


def main():
    results = {name: analyze(name) for name in ('base', 'extra')}
    require({k: v for k, v in results['base'].items() if k != 'sha256'}
            == {k: v for k, v in results['extra'].items() if k != 'sha256'},
            'provider orientation results differ')
    r = results['base']
    print('PASS_CROSS_ENDFRAME_OBSERVABILITY')
    print('pinned PR2979 orientation hashes:', results['base']['sha256'], results['extra']['sha256'])
    print('rank-seven endpoint classes: 49; rank-eight endpoint classes: 126')
    print('individual rank-7/rank-8 classes with eligible signal: 0 / 0')
    print('rank-seven pairs: join-rank 8: 413 (1 positive); join-rank 9: 763 (0 positive)')
    print('rank-seven triples: join-rank 8: 2571 (1 positive, same four-register witness)')
    print('rank-seven triples: join-rank 9: 15853 (52 positive classes; eligible ranks 1:50, 2:2)')
    print('rank-nine triples: 11 exact scalar forms (10 new), spanning 5 dimensions; new supports: five 6-term and five 8-term forms')
    print('rank-nine quartets: 211876 supports; 1353 exact-positive join-rank-9 classes; eligible ranks 1:1258, 2:94, 3:1')
    print('quartets add 6 forms (four 5-term, one 8-term, one 10-term); the six span 5 dimensions')
    print('sparse five-dimensional readout footprint: 9 terminal registers across 7 rank-seven endpoint classes')
    print('readout: -out[7] - out[232] + out[236] + out[238]')
    print('input form: 1/2 * (-h224 + h227 - h229 - h231 - h232 + h233 - h234 + h235 + h236 - h237 + h238 - h239 - h276 - h292)')
    print('exact protected-column and formal-warp cancellation; deleting any one readout kills the signal')
    print('scope: information identities only; no consumer, complete invoice or kappa improvement')


if __name__ == '__main__':
    main()
