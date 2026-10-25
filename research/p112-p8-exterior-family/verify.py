"""Exact P8 exterior-family replay; Python standard library only.

Prepared by flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
Default execution reads and checks RESULT.json without writing any files.
"""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'research/p112-rational-decoder-gate/CANDIDATE.json':
        'dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b',
    'research/adaptive-kernel-demotion/inputs/DATA-PHASES.json':
        'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
}
GROUPS = [17, 18, 29, 30, 31, 32]
# Each row below is one query column in coordinates (c0,c1,c2,h).
QUERIES = [[0, 0, 0, 1], [0, 1, 1, 2], [1, 0, 1, 1],
           [1, 1, 0, 1], [2, 1, 1, 0], [1, 0, 0, 1]]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_hash(value):
    data = json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')
    return sha256(data).hexdigest()


def read_input(path):
    raw = (ROOT / path).read_bytes()
    require(sha256(raw).hexdigest() == INPUTS[path], 'Input SHA256: ' + path)
    return json.loads(raw)


def rref(rows):
    matrix = [list(map(Fraction, row)) for row in rows]
    pivots = []
    for column in range(len(matrix[0]) if matrix else 0):
        pivot = next((r for r in range(len(pivots), len(matrix))
                      if matrix[r][column]), None)
        if pivot is None:
            continue
        row = len(pivots)
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        divisor = matrix[row][column]
        matrix[row] = [entry / divisor for entry in matrix[row]]
        for other in range(len(matrix)):
            if other != row:
                multiplier = matrix[other][column]
                matrix[other] = [a - multiplier * b
                                 for a, b in zip(matrix[other], matrix[row])]
        pivots.append(column)
    return matrix, pivots


def rational_rank(rows):
    return len(rref(rows)[1])


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit in pivots:
                row ^= pivots[bit]
            else:
                pivots[bit] = row
                break
    return len(pivots)


def geometry():
    candidate, data = [read_input(path) for path in INPUTS]
    ports = [candidate['groups'][group] for group in GROUPS]
    require(all(len(group) == 3 for group in ports), 'Complete physical triads')
    targets = [[ports[2*j][0], ports[2*j+1][0]] for j in range(3)]
    require(targets == [[0, 67], [7, 64], [1, 75]], 'Fixed target marking')
    marks = list(map(set, candidate['factor_supports']))
    require(all(set(mark) in marks for mark in targets), 'Canonical target marks')
    labels = {row['port']: row['q'] for row in data['recipes']}
    unions = [[labels[p] for g in range(6) if mask >> g & 1 for p in ports[g]]
              for mask in range(64)]
    tariffs = []
    for source in unions:
        row = []
        for reader in unions:
            gram_rows = [sum(((a & b).bit_count() % 2) << j
                             for j, b in enumerate(reader)) for a in source]
            row.append(binary_rank(gram_rows))
        tariffs.append(row)
    for source in range(64):
        for reader in range(64):
            for group in range(6):
                require(tariffs[source][reader] <= tariffs[source | 1 << group][reader],
                        'Source rank monotonicity')
                require(tariffs[source][reader] <= tariffs[source][reader | 1 << group],
                        'Reader rank monotonicity')
    return ports, targets, tariffs


def source_strata():
    """Derive all affine zeros; nonroot values have the generic support."""
    classes = []
    alphabets = []
    for target in range(3):
        roots = sorted({Fraction(-q[target], q[3]) for q in QUERIES if q[3]},
                       reverse=True)
        generic = sum(1 << i for i, q in enumerate(QUERIES) if q[target] or q[3])
        patterns = []
        for value in roots:
            support = sum(1 << i for i, q in enumerate(QUERIES)
                          if q[target] + q[3] * value)
            require(support & generic == support, 'Root/generic support inclusion')
            patterns.append({'h': str(value), 'query_support_mask': support})
        for left in patterns:
            for right in patterns:
                if left is not right:
                    require(left['query_support_mask'] & right['query_support_mask']
                            != left['query_support_mask'], 'Undominated root antichain')
        require(all((2 * x).denominator == 1 for x in roots), 'Half-integer root encoding')
        alphabet = tuple(int(2 * x) for x in roots)
        alphabets.extend([alphabet, alphabet])
        classes.append({'target': target, 'generic_support_mask': generic,
                        'root_patterns': patterns})
    require(alphabets == [(0, -2)]*2 + [(0, -1, -2)]*4, 'Complete root alphabets')
    return alphabets, classes


def reader_supports():
    options = []
    checks = 0
    for target in range(3):
        minimal = []
        demand = [int(i == target) for i in range(4)]
        for mask in sorted(range(64), key=lambda m: (m.bit_count(), m)):
            columns = [QUERIES[i] for i in range(6) if mask >> i & 1]
            spans = rational_rank(columns) == rational_rank(columns + [demand])
            checks += 1
            if spans and not any(old & mask == old for old in minimal):
                minimal.append(mask)
        options.append(minimal)
    require([len(row) for row in options] == [5, 6, 6], 'Minimal reader support counts')
    return [options[g // 2] for g in range(6)], options, checks


def recover(mask, target):
    indices = [i for i in range(6) if mask >> i & 1]
    augmented = [[QUERIES[i][r] for i in indices] + [int(r == target)]
                 for r in range(4)]
    reduced, pivots = rref(augmented)
    require(pivots == list(range(len(indices))), 'Independent consistent minimal reader')
    reader = [Fraction(0)] * 6
    for row, index in enumerate(indices):
        reader[index] = reduced[row][-1]
    require(all(sum(QUERIES[i][r] * reader[i] for i in range(6)) == int(r == target)
                for r in range(4)), 'Exact coefficient reader')
    return reader


def masks_for_exterior(twice_h):
    return [sum(1 << g for g in range(6)
                if 2 * QUERIES[i][g // 2] + QUERIES[i][3] * twice_h[g])
            for i in range(6)]


def optimize(costs, options):
    """Complete branch-and-bound; never sum bounds for unassigned groups."""
    used = {mask: [i for i in range(6) if mask >> i & 1]
            for row in options for mask in row}
    increments = [[[costs[i][mask | 1 << g] - costs[i][mask] for mask in range(64)]
                   for i in range(6)] for g in range(6)]
    require(all(x >= 0 for group in increments for row in group for x in row),
            'Monotone incremental tariff')

    def invoice(choices):
        readers = [sum(1 << g for g, mask in enumerate(choices) if mask >> i & 1)
                   for i in range(6)]
        return sum(costs[i][readers[i]] for i in range(6)), readers

    witness = [row[0] for row in options]
    best, _ = invoice(witness)
    nodes = 0

    def visit(depth, readers, partial, choices):
        nonlocal best, witness, nodes
        nodes += 1
        if partial >= best:
            return
        if depth == 6:
            best, witness = partial, choices[:]
            return
        next_options = None
        for group in range(depth, 6):
            additions = [(sum(increments[group][i][readers[i]] for i in used[mask]), mask)
                         for mask in options[group]]
            # Each single-group minimum is a lower bound on every completion.
            if partial + min(extra for extra, _ in additions) >= best:
                return
            if group == depth:
                next_options = sorted(additions)
        for extra, mask in next_options:
            if partial + extra >= best:
                continue
            extended = readers[:]
            for i in used[mask]:
                extended[i] |= 1 << depth
            visit(depth + 1, extended, partial + extra, choices + [mask])

    visit(0, [0]*6, 0, [])
    cost, readers = invoice(witness)
    require(cost == best, 'Exact optimum witness invoice')
    return {'optimum': best, 'group_query_masks': witness,
            'query_reader_masks': readers,
            'term_costs': [costs[i][readers[i]] for i in range(6)], 'branch_nodes': nodes}


def check_witness(twice_h, solution, tariffs):
    readers = [recover(mask, g // 2)
               for g, mask in enumerate(solution['group_query_masks'])]
    for source in range(6):
        for output in range(6):
            value = sum(Fraction(2 * QUERIES[i][source // 2]
                                 + QUERIES[i][3] * twice_h[source], 2) * readers[output][i]
                        for i in range(6))
            require(value == int(source // 2 == output // 2), 'Marked physical endpoint')
    reader_masks = [sum(1 << g for g in range(6) if readers[g][i]) for i in range(6)]
    require(reader_masks == solution['query_reader_masks'], 'Actual reader supports')
    source_masks = masks_for_exterior(twice_h)
    term_costs = [tariffs[source_masks[i]][reader_masks[i]] for i in range(6)]
    require(term_costs == solution['term_costs'] and sum(term_costs) == solution['optimum'],
            'Actual complete-group invoice')
    return readers


def controls(targets, options, tariffs):
    # An omitted -1/2 root cannot be replaced by x=0: it cancels q1 specifically.
    half_support = {i for i, q in enumerate(QUERIES) if q[1] - Fraction(q[3], 2)}
    zero_support = {i for i, q in enumerate(QUERIES) if q[1]}
    require(not zero_support <= half_support, 'Missing half-root rejection control')
    # Rank-three E permits extra reader equations, so the rank-four qualifier matters.
    require(QUERIES[5] == [1, 0, 0, 1], 'Extra-reader control coefficient')
    require(QUERIES[5][:3] == [1, 0, 0], 'h=0 physical extra-reader control')
    require(QUERIES[5] != [1, 0, 0, 0], 'h=0 extra reader fails retained AR equation')
    outputs = [p for pair in targets for p in pair]
    outside = next(p for p in range(112) if p not in outputs)
    # Outside h rows can be deleted even when this collapses the coordinate rank.
    old = [[int(p in targets[j]) for j in range(3)] + [int(p == outside)]
           for p in range(112)]
    new = [row[:3] + [0] for row in old]
    require(rational_rank(old) == 4 and rational_rank(new) == 3, 'Outside-source rank drop')
    readers = [recover(options[g][0], g // 2) for g in range(6)]
    old_q = [[sum(row[j] * q[j] for j in range(4)) for q in QUERIES] for row in old]
    new_q = [[sum(row[j] * q[j] for j in range(4)) for q in QUERIES] for row in new]
    require(all(not new_q[p][i] or old_q[p][i] for p in range(112) for i in range(6)),
            'Outside-source pointwise dominance')
    for physical in (old_q, new_q):
        for source in range(112):
            for g, output in enumerate(outputs):
                got = sum(physical[source][i] * readers[g][i] for i in range(6))
                require(got == int(source in targets[g // 2]), 'Outside deletion endpoint')
    original = [2, -2, 0, 0, 0, 0]
    reduced = [0, -2, 0, 0, 0, 0]
    results = []
    for exterior in (original, reduced):
        source_masks = masks_for_exterior(exterior)
        solution = optimize([tariffs[mask] for mask in source_masks], options)
        check_witness(exterior, solution, tariffs)
        results.append(solution['optimum'])
    require(results == [21, 18], 'Original and support-reduced controls')
    return {'missing_half_root_rejected': True, 'rank3_extra_reader_control': True,
            'outside_source_deletion_rank_drop': [4, 3],
            'outside_endpoint_columns_checked': 2*112*6,
            'original_and_reduced_costs': results}


def replay():
    require(rational_rank(QUERIES) == 4, 'Rank-four coefficient dictionary')
    ports, targets, tariffs = geometry()
    alphabets, zero_classes = source_strata()
    options, minimal, subset_checks = reader_supports()
    cache = {}
    rows = []
    attaining = []
    histogram = {}
    ranks = {'3': 0, '4': 0}
    for twice_h in product(*alphabets):
        source_masks = masks_for_exterior(twice_h)
        coordinate_rows = [[int(j == g // 2) for j in range(3)]
                           + [Fraction(twice_h[g], 2)] for g in range(6)]
        rank = rational_rank(coordinate_rows)
        require(rank == 3 + int(any(twice_h[g] != twice_h[g+1] for g in (0, 2, 4))),
                'Coordinate rank classification')
        ranks[str(rank)] += 1
        key = tuple(tuple(tariffs[mask]) for mask in source_masks)
        if key not in cache:
            cache[key] = optimize(key, options)
        solution = cache[key]
        require(solution['optimum'] >= 18, 'Family invoice floor')
        check_witness(twice_h, solution, tariffs)
        row = {'twice_h': list(twice_h), 'physical_coordinate_rank': rank,
               'source_group_masks': source_masks, 'optimum': solution['optimum']}
        rows.append(row)
        label = str(solution['optimum'])
        histogram[label] = histogram.get(label, 0) + 1
        if rank == 4 and solution['optimum'] == 18:
            attaining.append({**row, 'group_query_masks': solution['group_query_masks'],
                              'query_reader_masks': solution['query_reader_masks'],
                              'term_costs': solution['term_costs']})
    require(len(rows) == 324 and ranks == {'3': 18, '4': 306}, 'Complete source coverage')
    require(len(attaining) == 6, 'Rank-four attainment coverage')
    return {'status': 'PASS_P8_ALL_RANK4_EXTERIORS_FIXED_MARKING',
            'scientific_inputs': INPUTS, 'groups': GROUPS, 'physical_ports': ports,
            'targets': targets, 'query_columns': QUERIES,
            'zero_pattern_classes': zero_classes,
            'minimal_reader_supports': minimal, 'reader_subset_tests': subset_checks,
            'source_strata': len(rows), 'coordinate_rank_counts': ranks,
            'full_tariff_entries': 4096, 'tariff_table_sha256': canonical_hash(tariffs),
            'distinct_tariff_rows': len(set(map(tuple, tariffs))),
            'distinct_six_query_tariff_tables': len(cache),
            'reader_support_cells_per_stratum': 32400,
            'total_branch_nodes': sum(row['branch_nodes'] for row in cache.values()),
            'marked_endpoint_entries_checked': 324*36,
            'minimum_rows_sha256': canonical_hash(rows),
            'optimum_histogram': histogram, 'rank4_minimum': 18,
            'rank4_attaining_strata': attaining,
            'controls': controls(targets, options, tariffs)}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', action='store_true',
                        help='explicitly replace RESULT.json with the recomputed receipt')
    arguments = parser.parse_args()
    result = replay()
    receipt = HERE / 'RESULT.json'
    if arguments.write_receipt:
        receipt.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    else:
        require(json.loads(receipt.read_text(encoding='utf-8')) == result,
                'RESULT.json differs from the complete regenerated result')
    print(result['status'])


if __name__ == '__main__':
    main()
