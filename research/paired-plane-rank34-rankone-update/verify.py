#!/usr/bin/env python3
"""Classify rational full-support rank-one gauges and price their P112 invoice."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
CERT = ROOT / 'research/paired-plane-rank34-copy-invoice/predecessor/PR3335-CERTIFICATE.json'
CERT_SHA = 'cd5edbe9bf46aa544ee47450adcf0c2dc9eee5a57acda8bc6f4b726ab7f2ae47'
BASE_COMMIT = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PR3335_HEAD = '1d46df8b5aeac49d165cae58c1dd1036666bb789'
CHANNELS, BLOCK, PORTS, PLANES = 34, 4, 112, 56
FULL = (1 << BLOCK) - 1


class CheckFailure(Exception):
    pass


def need(ok: bool, message: str) -> None:
    if not ok:
        raise CheckFailure(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def rank_f2(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def plane_vectors(mask: int, basis: list[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(vector for plane, pair in enumerate(basis) if mask >> plane & 1
                 for vector in pair)


def pairing_rank(left: int, right: int, basis: list[tuple[int, int]]) -> int:
    left_vectors = plane_vectors(left, basis)
    right_vectors = plane_vectors(right, basis)
    rows = [sum(dot(x, y) << j for j, y in enumerate(right_vectors))
            for x in left_vectors]
    return rank_f2(rows)


def load_geometry():
    archive_data = ARCHIVE.read_bytes()
    need(sha256(archive_data) == ARCHIVE_SHA, 'selected archive SHA256')
    with tarfile.open(fileobj=io.BytesIO(archive_data), mode='r:gz') as archive:
        matches = [member for member in archive.getmembers() if member.name == MEMBER]
        need(len(matches) == 1 and matches[0].isfile(), 'unique selected-label archive member')
        stream = archive.extractfile(matches[0])
        need(stream is not None, 'selected labels are readable')
        labels_data = stream.read()
    need(sha256(labels_data) == MEMBER_SHA, 'selected-label member SHA256')
    recipes = json.loads(labels_data)['recipes']
    by_port = {row['port']: row['q'] for row in recipes}
    need(len(by_port) == PORTS and sorted(by_port) == list(range(PORTS)),
         'complete unique 112-port labels')
    labels = [by_port[index] for index in range(PORTS)]
    need(all(type(value) is int and 0 < value < 512 for value in labels),
         'selected labels are nine-bit integers')
    need(len(set(labels)) == PORTS, 'selected labels are distinct')

    cert_data = CERT.read_bytes()
    need(sha256(cert_data) == CERT_SHA, 'PR3335 certificate SHA256')
    cert = json.loads(cert_data)
    pairs = [tuple(pair) for pair in cert['pairs']]
    supports = [list(support) for support in cert['supports']]
    need(len(pairs) == PLANES and sorted(port for pair in pairs for port in pair)
         == list(range(PORTS)), '56 paired planes partition the ports')
    need(len(supports) == CHANNELS and all(supports), '34 nonempty channel supports')
    need(sorted(port for support in supports for port in support) == list(range(PORTS)),
         '34 channel supports partition the ports')
    owner = {port: plane for plane, pair in enumerate(pairs) for port in pair}
    basis = [(labels[left], labels[right]) for left, right in pairs]
    need(all(dot(a, a) == dot(b, b) == 1 and dot(a, b) == 0 for a, b in basis),
         'each paired plane has Gram I2')
    orthogonal = [[all(dot(x, y) == 0 for x in left for y in right)
                   for right in basis] for left in basis]
    channel_planes = []
    for support in supports:
        mask = 0
        for port in support:
            mask |= 1 << owner[port]
        channel_planes.append(mask)
    scalar = [[sum(int(i in support and j in support) for support in supports)
               for j in range(PORTS)] for i in range(PORTS)]
    need(all(scalar[i][i] == 1 for i in range(PORTS)), 'scalar diagonal')
    for i in range(PORTS):
        for j in range(PORTS):
            if i != j and not orthogonal[owner[i]][owner[j]]:
                need(scalar[i][j] == 0, 'strict scalar plane mask')
    representatives = [support[0] for support in supports]
    need(all(scalar[i][j] == int(i == j) for i in representatives
             for j in representatives), 'rank-34 support minor')
    return basis, channel_planes, supports


def form_value(form, point):
    return sum(a * x for a, x in zip(form, point))


def solve_affine(equations, dimension):
    """Return one point and an integer-scaled nullspace basis, or a contradiction."""
    matrix = [[Q(value) for value in (*form, rhs)] for form, rhs in equations]
    pivots = []
    rank = 0
    for column in range(dimension):
        pivot = next((row for row in range(rank, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][column]
        matrix[rank] = [entry / value for entry in matrix[rank]]
        for row in range(len(matrix)):
            if row != rank and matrix[row][column]:
                value = matrix[row][column]
                matrix[row] = [entry - value * pivot_entry
                               for entry, pivot_entry in zip(matrix[row], matrix[rank])]
        pivots.append(column)
        rank += 1
    for row in matrix:
        if not any(row[:dimension]) and row[dimension]:
            return None, [], {'kind': 'inconsistent_equations',
                              'row': [str(value) for value in row]}
    free = [column for column in range(dimension) if column not in pivots]
    point = [Q(0)] * dimension
    for row, pivot in zip(matrix[:rank], pivots):
        point[pivot] = row[dimension]
    nullspace = []
    for free_column in free:
        vector = [Q(0)] * dimension
        vector[free_column] = Q(1)
        for row, pivot in zip(matrix[:rank], pivots):
            vector[pivot] = -row[free_column]
        nullspace.append(tuple(vector))
    return tuple(point), nullspace, None


def feasible_diagonal_pattern(overlap, source_zero_mask: int, inverse_zero_mask: int):
    """Solve the exact affine equalities and avoid every forbidden hyperplane."""
    dimension = len(overlap)
    equations = []
    for local_i in range(dimension):
        unit = tuple(int(j == local_i) for j in range(dimension))
        if source_zero_mask >> local_i & 1:
            equations.append((unit, Q(-1)))
        if inverse_zero_mask >> local_i & 1:
            without_i = tuple(int(j != local_i) for j in range(dimension))
            equations.append((without_i, Q(-1)))
    point, nullspace, contradiction = solve_affine(equations, dimension)
    if contradiction is not None:
        return None, contradiction, 0

    forbidden = []
    for local_i in range(dimension):
        unit = tuple(int(j == local_i) for j in range(dimension))
        forbidden.append((unit, Q(0), 'x_nonzero_' + str(overlap[local_i])))
        if not (source_zero_mask >> local_i & 1):
            forbidden.append((unit, Q(-1), 'source_diagonal_nonzero_' + str(overlap[local_i])))
        if not (inverse_zero_mask >> local_i & 1):
            without_i = tuple(int(j != local_i) for j in range(dimension))
            forbidden.append((without_i, Q(-1),
                              'inverse_diagonal_nonzero_' + str(overlap[local_i])))
    all_coordinates = (1,) * dimension
    forbidden.append((all_coordinates, Q(-1), 'invertible_denominator'))

    for form, target, name in forbidden:
        direction_values = [form_value(form, vector) for vector in nullspace]
        if not any(direction_values) and form_value(form, point) == target:
            return None, {'kind': 'forced_forbidden_hyperplane', 'condition': name,
                          'value': str(form_value(form, point))}, 0

    if not nullspace:
        return point, None, 0

    root_bound = len(forbidden) * len(nullspace)
    for parameter in range(1, root_bound + 2):
        candidate = tuple(point[i] + sum(nullspace[j][i] * parameter ** (j + 1)
                                         for j in range(len(nullspace)))
                          for i in range(dimension))
        if all(form_value(form, candidate) != target
               for form, target, _ in forbidden):
            need(all(form_value(form, candidate) == rhs for form, rhs in equations),
                 'constructed rank-one witness satisfies all zero equations')
            return candidate, None, root_bound
    raise CheckFailure('finite hyperplane root bound did not produce a rational point')


def rank_one_matrix(u, v):
    denominator = 1 + sum(u[i] * v[i] for i in range(BLOCK))
    need(denominator != 0, 'Sherman-Morrison denominator is nonzero')
    matrix = [[Q(i == j) + u[i] * v[j] for j in range(BLOCK)]
              for i in range(BLOCK)]
    inverse = [[Q(i == j) - u[i] * v[j] / denominator for j in range(BLOCK)]
               for i in range(BLOCK)]
    need(all(sum(matrix[i][k] * inverse[k][j] for k in range(BLOCK)) == Q(i == j)
             for i in range(BLOCK) for j in range(BLOCK)),
         'Sherman-Morrison inverse identity')
    need(all(sum(inverse[i][k] * matrix[k][j] for k in range(BLOCK)) == Q(i == j)
             for i in range(BLOCK) for j in range(BLOCK)),
         'reverse Sherman-Morrison inverse identity')
    return matrix, inverse, denominator


def support_pair(matrix, inverse):
    source_columns = tuple(sum(1 << row for row in range(BLOCK)
                               if matrix[row][column]) for column in range(BLOCK))
    inverse_rows = tuple(sum(1 << column for column in range(BLOCK)
                             if inverse[row][column]) for row in range(BLOCK))
    return source_columns, inverse_rows


def rational_support_maps():
    maps = {}
    pattern_table = []
    pattern_keys = []
    max_root_bound = 0
    membership_patterns = []
    for states in itertools.product((1, 2, 3), repeat=BLOCK):
        source_support = tuple(i for i, state in enumerate(states) if state & 1)
        reader_support = tuple(i for i, state in enumerate(states) if state & 2)
        if not source_support or not reader_support:
            continue
        overlap = tuple(i for i, state in enumerate(states) if state == 3)
        membership_patterns.append(states)
        flag_count = 1 << len(overlap)
        for source_zero_mask in range(flag_count):
            for inverse_zero_mask in range(flag_count):
                x, reason, root_bound = feasible_diagonal_pattern(
                    overlap, source_zero_mask, inverse_zero_mask)
                max_root_bound = max(max_root_bound, root_bound)
                row = {
                    'membership_states': list(states),
                    'source_support': list(source_support),
                    'reader_support': list(reader_support),
                    'overlap': list(overlap),
                    'source_zero_mask_on_overlap': source_zero_mask,
                    'inverse_zero_mask_on_overlap': inverse_zero_mask,
                    'feasible': x is not None,
                }
                if x is None:
                    row['obstruction'] = reason
                    pattern_table.append(row)
                    pattern_keys.append(None)
                    continue
                u = tuple(Q(int(i in source_support)) for i in range(BLOCK))
                x_by_channel = {channel: x[k] for k, channel in enumerate(overlap)}
                v = tuple(x_by_channel[i] if i in x_by_channel
                          else Q(int(i in reader_support)) for i in range(BLOCK))
                matrix, inverse, denominator = rank_one_matrix(u, v)
                for i, j in itertools.product(range(BLOCK), repeat=2):
                    if i == j and i in x_by_channel:
                        expected_source = 1 + x_by_channel[i] != 0
                        expected_inverse = 1 + sum(value for channel, value in x_by_channel.items()
                                                    if channel != i) != 0
                    elif i == j:
                        expected_source = expected_inverse = True
                    else:
                        expected_source = expected_inverse = (
                            i in source_support and j in reader_support)
                    need((matrix[i][j] != 0) == expected_source,
                         'source support follows the rank-one rectangle and diagonal flag')
                    need((inverse[i][j] != 0) == expected_inverse,
                         'inverse support follows the rank-one rectangle and diagonal flag')
                key = support_pair(matrix, inverse)
                maps.setdefault(key, {
                    'membership_states': tuple(states),
                    'source_support': source_support,
                    'reader_support': reader_support,
                    'overlap': overlap,
                    'source_zero_mask': source_zero_mask,
                    'inverse_zero_mask': inverse_zero_mask,
                    'x': x,
                    'u': u,
                    'v': v,
                    'denominator': denominator,
                    'matrix': matrix,
                    'inverse': inverse,
                    'source_columns': list(key[0]),
                    'inverse_rows': list(key[1]),
                })
                row['support_pair_index'] = None
                pattern_table.append(row)
                pattern_keys.append(key)
    need(len(membership_patterns) == 79, 'all nonempty S,T membership patterns with union four')
    need(len(pattern_table) == 1294,
         'complete 1294 membership/diagonal-flag parameter cells')
    ordered = sorted(maps.items())
    index_by_key = {key: index for index, (key, _) in enumerate(ordered)}
    for row, key in zip(pattern_table, pattern_keys):
        if row['feasible']:
            row['support_pair_index'] = index_by_key[key]
    return maps, pattern_table, max_root_bound


def rho_function(basis):
    cache = {}
    def rho(left, right):
        key = (left, right) if left <= right else (right, left)
        if key not in cache:
            cache[key] = pairing_rank(left, right, basis)
        return cache[key]
    return rho, cache


def tariff_census(basis, channel_planes, maps):
    rho, cache = rho_function(basis)
    base = [rho(mask, mask) for mask in channel_planes]
    need(Counter(base) == Counter({4: 8, 6: 8, 8: 18}) and sum(base) == 224,
         'published base complete-plane invoice is 224')
    quadruples = tuple(itertools.combinations(range(CHANNELS), BLOCK))
    ordered_maps = sorted(maps.items())
    histogram = Counter()
    receipts = []
    strict_improvements = 0
    minimum_total = 10**9
    best_witness = None
    for channels in quadruples:
        local = [channel_planes[index] for index in channels]
        baseline = sum(base[index] for index in channels)
        unions = [0] * (1 << BLOCK)
        for subset in range(1, 1 << BLOCK):
            bit = subset & -subset
            position = bit.bit_length() - 1
            unions[subset] = unions[subset ^ bit] | local[position]
        best_local = 10**9
        best_index = None
        for index, (_, record) in enumerate(ordered_maps):
            cost = sum(rho(unions[source], unions[reader])
                       for source, reader in zip(record['source_columns'],
                                                 record['inverse_rows']))
            if cost < best_local:
                best_local = cost
                best_index = index
        delta = best_local - baseline
        histogram[delta] += 1
        strict_improvements += int(delta < 0)
        total = 224 - baseline + best_local
        if total < minimum_total:
            minimum_total = total
            best_witness = {
                'channels': list(channels),
                'local_base_invoice': baseline,
                'local_after_invoice': best_local,
                'global_after_invoice': total,
                'delta': delta,
                'support_pair_index': best_index,
            }
        receipts.append([*channels, baseline, best_local, best_index])
    summary = {
        'quadruples': len(quadruples),
        'rational_support_pairs': len(ordered_maps),
        'priced_pair_quadruple_cases': len(quadruples) * len(ordered_maps),
        'minimum_total_invoice': minimum_total,
        'strict_improvement_quadruples': strict_improvements,
        'minimum_delta_histogram': {str(k): v for k, v in sorted(histogram.items())},
        'receipt_sha256': sha256(json.dumps(receipts, separators=(',', ':')).encode()),
        'best_witness': best_witness,
    }
    return base, summary, len(cache)


def scalar_identity_control(supports, maps):
    before = [[sum(int(i in support and j in support) for support in supports)
               for j in range(PORTS)] for i in range(PORTS)]
    for _, record in sorted(maps.items()):
        matrix, inverse = record['matrix'], record['inverse']
        transformed = [[sum(Q(int(port in supports[old])) * matrix[old][term]
                            for old in range(BLOCK)) for term in range(BLOCK)]
                       for port in range(PORTS)]
        after = [[sum(int(port_i in supports[channel] and port_j in supports[channel])
                      for channel in range(BLOCK, CHANNELS))
                   + sum(transformed[port_i][term]
                         * sum(inverse[term][old] * Q(int(port_j in supports[old]))
                               for old in range(BLOCK))
                         for term in range(BLOCK))
                   for port_j in range(PORTS)] for port_i in range(PORTS)]
        need(after == [[Q(value) for value in row] for row in before],
             'all 112x112 scalar fitting entries are preserved')
    first = maps[sorted(maps)[0]]
    wrong = [row[:] for row in first['inverse']]
    wrong[0][0] += 1
    matrix = first['matrix']
    transformed = [[sum(Q(int(port in supports[old])) * matrix[old][term]
                        for old in range(BLOCK)) for term in range(BLOCK)]
                   for port in range(PORTS)]
    wrong_after = [[sum(int(port_i in supports[channel] and port_j in supports[channel])
                        for channel in range(BLOCK, CHANNELS))
                    + sum(transformed[port_i][term]
                          * sum(wrong[term][old] * Q(int(port_j in supports[old]))
                                 for old in range(BLOCK))
                          for term in range(BLOCK))
                    for port_j in range(PORTS)] for port_i in range(PORTS)]
    need(wrong_after != [[Q(value) for value in row] for row in before],
         'wrong inverse is rejected')
    return {'representative_maps_checked': len(maps),
            'scalar_entries_per_map': PORTS * PORTS,
            'wrong_inverse_rejected': True}


def qtext(value):
    return str(Q(value))


def build():
    basis, channel_planes, supports = load_geometry()
    maps, pattern_table, max_root_bound = rational_support_maps()
    generic_householder = tuple(Q(-1, 2) for _ in range(BLOCK))
    pythagorean_householder = (Q(-1, 9), Q(-4, 9), Q(-4, 9), Q(-1))
    controls = {}
    for name, x in (('generic_householder', generic_householder),
                    ('pythagorean_householder', pythagorean_householder),
                    ('nonorthogonal_rank_one', (Q(1),) * BLOCK)):
        matrix, inverse, _ = rank_one_matrix((Q(1),) * BLOCK, x)
        key = support_pair(matrix, inverse)
        need(key in maps, name + ' control is covered by rational support classification')
        controls[name] = {'x': [qtext(value) for value in x],
                          'support_pair_index': sorted(maps).index(key)}
    base, price, rank_cache_cases = tariff_census(basis, channel_planes, maps)
    full_support_maps = {key: record for key, record in maps.items()
                         if record['membership_states'] == (3, 3, 3, 3)}
    need(len(full_support_maps) == 87, 'full-support subfamily matches the independent pilot census')
    _, full_support_price, full_support_rank_cache = tariff_census(
        basis, channel_planes, full_support_maps)
    need(full_support_price['minimum_total_invoice'] == 228
         and full_support_price['strict_improvement_quadruples'] == 0,
         'full-support subfamily retains its pilot negative result')
    dense = scalar_identity_control(supports, maps)
    ordered_maps = sorted(maps.items())
    map_table = []
    for _, record in ordered_maps:
        map_table.append({
            'membership_states': list(record['membership_states']),
            'source_support': list(record['source_support']),
            'reader_support': list(record['reader_support']),
            'overlap': list(record['overlap']),
            'source_zero_mask': record['source_zero_mask'],
            'inverse_zero_mask': record['inverse_zero_mask'],
            'x': [qtext(value) for value in record['x']],
            'u': [qtext(value) for value in record['u']],
            'v': [qtext(value) for value in record['v']],
            'denominator': qtext(record['denominator']),
            'matrix': [[qtext(value) for value in row] for row in record['matrix']],
            'inverse': [[qtext(value) for value in row] for row in record['inverse']],
            'source_columns': record['source_columns'],
            'inverse_rows': record['inverse_rows'],
        })
    certificate = {
        'schema_version': 1,
        'base_commit': BASE_COMMIT,
        'pr3335_head': PR3335_HEAD,
        'selected_archive_sha256': ARCHIVE_SHA,
        'rank34_certificate_sha256': CERT_SHA,
        'family': 'all rational rank-one updates G=I+u v^T with supp(u) union supp(v) equal to the four selected channels',
        'normalization': ('Diagonal similarity normalizes u_i=1 on supp(u) and v_j=1 on supp(v) minus supp(u); '
                          'the only free diagonal products are x_i=u_i*v_i on the overlap. This preserves all supports and tariff.'),
        'support_equations': {
            'invertible_denominator': '1 + sum_{i in supp(u) intersect supp(v)} x_i != 0',
            'source_diagonal_zero_i': 'x_i = -1 for i in the overlap',
            'inverse_diagonal_zero_i': '1 + sum_{j != i, j in overlap} x_j = 0',
            'off_diagonal': 'G_ij and G^-1_ij are nonzero exactly on the rectangle supp(u) x supp(v), away from the diagonal',
            'classification_method': ('Enumerate all nonempty membership patterns S,T with S union T equal to the block; '
                                      'for each overlap, solve every source/inverse diagonal zero-flag system over Q and '
                                      'avoid the finite forbidden hyperplanes with a degree-bounded exact parameter.'),
        },
        'membership_pattern_count': 79,
        'parameter_cell_count': len(pattern_table),
        'feasible_parameter_cell_count': sum(row['feasible'] for row in pattern_table),
        'distinct_rational_support_pair_count': len(maps),
        'infeasible_pattern_obstructions': dict(Counter(
            row['obstruction']['kind'] for row in pattern_table if not row['feasible'])),
        'maximum_constructive_root_bound': max_root_bound,
        'diagonal_pattern_table': pattern_table,
        'rational_support_maps': map_table,
        'householder_and_general_controls': controls,
        'base_channel_invoices': base,
        'four_channel_tariff_census': price,
        'full_support_subfamily_census': full_support_price,
        'cached_pairing_rank_cases': rank_cache_cases,
        'full_support_cached_pairing_rank_cases': full_support_rank_cache,
        'dense_scalar_identity_control': dense,
    }
    result = {
        'schema_version': 1,
        'object': 'all rational rank-one Sherman-Morrison gauges with four-channel support union on the PR3335 fit',
        'base_invoice': 224,
        'parameter_cells': len(pattern_table),
        'feasible_parameter_cells': sum(row['feasible'] for row in pattern_table),
        'full_support_subfamily_support_pairs': len(full_support_maps),
        'full_support_subfamily_minimum_invoice': full_support_price['minimum_total_invoice'],
        'channel_quadruples': price['quadruples'],
        'rational_support_pairs': price['rational_support_pairs'],
        'priced_pair_quadruple_cases': price['priced_pair_quadruple_cases'],
        'minimum_total_invoice': price['minimum_total_invoice'],
        'strict_improvement_quadruples': price['strict_improvement_quadruples'],
        'minimum_delta_histogram': price['minimum_delta_histogram'],
        'kappa_change': None,
        'physical_supplier_claim': False,
    }
    return certificate, result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='write reconstructed evidence files')
    args = parser.parse_args()
    certificate, result = build()
    files = {
        'CERTIFICATE.json': json.dumps(certificate, indent=2, sort_keys=True) + '\n',
        'RESULT.json': json.dumps(result, indent=2, sort_keys=True) + '\n',
    }
    if args.write:
        for name, contents in files.items():
            (HERE / name).write_text(contents, encoding='utf-8')
    else:
        for name, contents in files.items():
            need((HERE / name).is_file(), name + ' missing; run verify.py --write once')
            need((HERE / name).read_text(encoding='utf-8') == contents,
                 name + ' differs from the exact reconstruction')
    print('PASS_RANK_ONE_GAUGE_CENSUS',
          'support_pairs=' + str(result['rational_support_pairs']),
          'minimum=' + str(result['minimum_total_invoice']),
          'improvements=' + str(result['strict_improvement_quadruples']))


if __name__ == '__main__':
    try:
        main()
    except (CheckFailure, OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit('FAIL_RANK_ONE_GAUGE_CENSUS: ' + str(exc)) from exc
