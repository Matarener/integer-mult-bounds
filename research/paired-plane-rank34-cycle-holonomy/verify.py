#!/usr/bin/env python3
"""Price every signed-unit shear word around four-channel cycles."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
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
CHANNELS, BLOCK, PORTS, PLANES = 34, 4, 112, 56
BASE_COMMIT = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PR3335_HEAD = '1d46df8b5aeac49d165cae58c1dd1036666bb789'


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
         == list(range(PORTS)), '56 disjoint paired planes partition the ports')
    need(len(supports) == CHANNELS and all(supports), '34 nonempty channel supports')
    need(sorted(port for support in supports for port in support) == list(range(PORTS)),
         'channel supports partition the ports')
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


def identity(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def matmul(left, right):
    n = len(left)
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def shear(i: int, j: int, coefficient: int):
    matrix = [list(row) for row in identity(BLOCK)]
    matrix[i][j] = coefficient
    return tuple(tuple(row) for row in matrix)


def support_pair(matrix, inverse):
    source_columns = tuple(sum(1 << row for row in range(BLOCK) if matrix[row][column])
                           for column in range(BLOCK))
    inverse_rows = tuple(sum(1 << column for column in range(BLOCK)
                             if inverse[row][column]) for row in range(BLOCK))
    return source_columns, inverse_rows


def poly_add(left, right):
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, 0) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def poly_mul(left, right):
    result = {}
    for left_mask, left_coefficient in left.items():
        for right_mask, right_coefficient in right.items():
            need(not (left_mask & right_mask), 'cycle variable appears in two factors')
            monomial = left_mask | right_mask
            result[monomial] = result.get(monomial, 0) + left_coefficient * right_coefficient
            if result[monomial] == 0:
                del result[monomial]
    return result


def poly_identity():
    return [[{0: int(i == j)} if i == j else {}
             for j in range(BLOCK)] for i in range(BLOCK)]


def poly_matmul(left, right):
    result = []
    for i in range(BLOCK):
        row = []
        for j in range(BLOCK):
            value = {}
            for k in range(BLOCK):
                value = poly_add(value, poly_mul(left[i][k], right[k][j]))
            row.append(value)
        result.append(row)
    return result


def symbolic_cycle(order, inverse=False):
    edges = ((order[0], order[1]), (order[1], order[2]),
             (order[2], order[3]), (order[3], order[0]))
    factors = list(enumerate(edges))
    if inverse:
        factors.reverse()
    matrix = poly_identity()
    for variable, (i, j) in factors:
        factor = poly_identity()
        factor[i][j] = {1 << variable: -1 if inverse else 1}
        matrix = poly_matmul(matrix, factor)
    return matrix


def check_rational_support_lemma():
    """Prove support cells by exact square-free polynomial path expansion."""
    digests = []
    rational_samples = set()
    for order in itertools.permutations(range(BLOCK)):
        source = symbolic_cycle(order)
        inverse = symbolic_cycle(order, inverse=True)
        exceptional = source[order[0]][order[0]]
        need(exceptional == {0: 1, (1 << BLOCK) - 1: 1},
             'the only two-term entry is 1 plus the full cycle product')
        need(all(len(source[i][j]) <= 1
                 for i in range(BLOCK) for j in range(BLOCK)
                 if (i, j) != (order[0], order[0])),
             'all other source entries are zero or a single path monomial')
        need(all(len(inverse[i][j]) <= 1
                 for i in range(BLOCK) for j in range(BLOCK)),
             'all inverse entries are zero or a single path monomial')
        encoded = json.dumps([source, inverse], sort_keys=True,
                             separators=(',', ':')).encode()
        digests.append([list(order), sha256(encoded)])

    # Exact rational witnesses exercise both full-cycle product cells and all
    # zero-edge patterns, independently of the ±1 representatives.
    for order in itertools.permutations(range(BLOCK)):
        edges = ((order[0], order[1]), (order[1], order[2]),
                 (order[2], order[3]), (order[3], order[0]))
        for zero_mask in range(1 << BLOCK):
            values = [Fraction(0) if zero_mask >> i & 1
                      else Fraction((2, -3, 5, 7)[i]) for i in range(BLOCK)]
            rational_samples.add(check_rational_witness(order, edges, values))
        rational_samples.add(check_rational_witness(
            order, edges, [Fraction(value) for value in (2, 3, 5, 7)]))
        rational_samples.add(check_rational_witness(
            order, edges, [Fraction(2), Fraction(3), Fraction(5), Fraction(-1, 30)]))
    return sha256(json.dumps(digests, separators=(',', ':')).encode()), rational_samples


def check_rational_witness(order, edges, coefficients):
    matrix = identity(BLOCK)
    factors = [(edge, coefficient) for edge, coefficient in zip(edges, coefficients)
               if coefficient]
    for (i, j), coefficient in factors:
        matrix = matmul(matrix, shear(i, j, coefficient))
    inverse = identity(BLOCK)
    for (i, j), coefficient in reversed(factors):
        inverse = matmul(inverse, shear(i, j, -coefficient))
    need(matmul(matrix, inverse) == identity(BLOCK)
         and matmul(inverse, matrix) == identity(BLOCK),
         'rational cycle coefficient witness has exact inverse')
    return support_pair(matrix, inverse)


def cycle_maps():
    """Enumerate cycle prefixes and representatives of every rational support cell."""
    maps_by_depth = {}
    word_counts = {}
    for depth in range(1, BLOCK + 1):
        maps = {}
        word_count = 0
        for order in itertools.permutations(range(BLOCK)):
            edges = ((order[0], order[1]), (order[1], order[2]),
                     (order[2], order[3]), (order[3], order[0]))
            for coefficients in itertools.product((-1, 1), repeat=depth):
                factors = [(edge, coefficient)
                           for edge, coefficient in zip(edges[:depth], coefficients)]
                matrix = identity(BLOCK)
                for (i, j), coefficient in factors:
                    matrix = matmul(matrix, shear(i, j, coefficient))
                inverse = identity(BLOCK)
                for (i, j), coefficient in reversed(factors):
                    inverse = matmul(inverse, shear(i, j, -coefficient))
                need(matmul(matrix, inverse) == identity(BLOCK)
                     and matmul(inverse, matrix) == identity(BLOCK),
                     'exact inverse of each unimodular shear word')
                key = support_pair(matrix, inverse)
                if key not in maps:
                    maps[key] = {
                        'source_columns': list(key[0]),
                        'inverse_rows': list(key[1]),
                        'cycle_order': list(order),
                        'coefficients': list(coefficients),
                        'matrix': [list(row) for row in matrix],
                        'inverse': [list(row) for row in inverse],
                    }
                word_count += 1
        maps_by_depth[depth] = maps
        word_counts[depth] = word_count
    expected_words = {1: 48, 2: 96, 3: 192, 4: 384}
    expected_maps = {1: 12, 2: 24, 3: 24, 4: 48}
    need(word_counts == expected_words, 'cycle word census')
    need({depth: len(maps) for depth, maps in maps_by_depth.items()} == expected_maps,
         'distinct support-pair census')
    rational_maps = {}
    parameter_representatives = 0
    for order in itertools.permutations(range(BLOCK)):
        edges = ((order[0], order[1]), (order[1], order[2]),
                 (order[2], order[3]), (order[3], order[0]))
        for zero_mask in range(1 << BLOCK):
            coefficients = tuple(0 if zero_mask >> edge & 1 else 1
                                 for edge in range(BLOCK))
            classes = [coefficients]
            if zero_mask == 0:
                # With all four weights nonzero, only the product -1 can cancel
                # a diagonal 1 + product term; all other rational products share
                # the same support as the all-positive representative.
                classes.append((-1, 1, 1, 1))
            for coefficients in classes:
                factors = [(edge, coefficient)
                           for edge, coefficient in zip(edges, coefficients) if coefficient]
                matrix = identity(BLOCK)
                for (i, j), coefficient in factors:
                    matrix = matmul(matrix, shear(i, j, coefficient))
                inverse = identity(BLOCK)
                for (i, j), coefficient in reversed(factors):
                    inverse = matmul(inverse, shear(i, j, -coefficient))
                need(matmul(matrix, inverse) == identity(BLOCK)
                     and matmul(inverse, matrix) == identity(BLOCK),
                     'exact inverse of each rational-cell representative')
                key = support_pair(matrix, inverse)
                if key not in rational_maps:
                    rational_maps[key] = {
                        'source_columns': list(key[0]),
                        'inverse_rows': list(key[1]),
                        'cycle_order': list(order),
                        'coefficients': list(coefficients),
                        'zero_edge_mask': zero_mask,
                        'matrix': [list(row) for row in matrix],
                        'inverse': [list(row) for row in inverse],
                    }
                parameter_representatives += 1
    need(parameter_representatives == 408 and len(rational_maps) == 193,
         'complete rational cycle support-cell representatives')
    for order in itertools.permutations(range(BLOCK)):
        edges = ((order[0], order[1]), (order[1], order[2]),
                 (order[2], order[3]), (order[3], order[0]))
        for zero_mask in range(1 << BLOCK):
            values = [0 if zero_mask >> i & 1 else 1 for i in range(BLOCK)]
            key = check_rational_witness(order, edges, values)
            need(key in rational_maps, 'zero-pattern representative is classified')
        need(check_rational_witness(order, edges, (-1, 1, 1, 1)) in rational_maps,
             'product-minus-one representative is classified')
    return maps_by_depth, word_counts, rational_maps, parameter_representatives


def census(basis, channel_planes, maps_by_depth, rational_maps):
    base = [pairing_rank(mask, mask, basis) for mask in channel_planes]
    need(Counter(base) == Counter({4: 8, 6: 8, 8: 18}) and sum(base) == 224,
         'published base complete-plane invoice 224')
    rho_cache = {}

    def rho(left, right):
        key = (left, right) if left <= right else (right, left)
        if key not in rho_cache:
            rho_cache[key] = pairing_rank(left, right, basis)
        return rho_cache[key]

    quadruples = tuple(itertools.combinations(range(CHANNELS), BLOCK))
    summaries = []
    families = [('prefix_' + str(depth), depth, maps)
                for depth, maps in sorted(maps_by_depth.items())]
    families.append(('all_rational_cycle_parameters', None, rational_maps))
    for family, depth, maps in families:
        ordered_maps = sorted(maps.items())
        delta_histogram = Counter()
        receipts = []
        best_total = 10**9
        best_witness = None
        strict_sets = 0
        priced_cases = 0
        for channels in quadruples:
            local = [channel_planes[index] for index in channels]
            baseline = sum(base[index] for index in channels)
            unions = [0] * (1 << BLOCK)
            for subset in range(1, 1 << BLOCK):
                bit = subset & -subset
                local_index = bit.bit_length() - 1
                unions[subset] = unions[subset ^ bit] | local[local_index]
            best_local = 10**9
            best_map_index = None
            for map_index, (_, record) in enumerate(ordered_maps):
                local_cost = sum(
                    rho(unions[source_mask], unions[reader_mask])
                    for source_mask, reader_mask in zip(
                        record['source_columns'], record['inverse_rows']))
                priced_cases += 1
                if local_cost < best_local:
                    best_local = local_cost
                    best_map_index = map_index
            delta = best_local - baseline
            delta_histogram[delta] += 1
            strict_sets += int(delta < 0)
            total = 224 - baseline + best_local
            if total < best_total:
                best_total = total
                best_witness = {
                    'channels': list(channels),
                    'local_base_invoice': baseline,
                    'local_after_invoice': best_local,
                    'global_after_invoice': total,
                    'delta': delta,
                    'support_map_index': best_map_index,
                }
            receipts.append([*channels, baseline, best_local, best_map_index])
        receipt_sha = sha256(json.dumps(receipts, separators=(',', ':')).encode())
        summary = {
            'family': family,
            'prefix_shears': depth,
            'quadruples': len(quadruples),
            'unique_support_pairs': len(ordered_maps),
            'priced_map_quadruple_cases': priced_cases,
            'minimum_total_invoice': best_total,
            'strict_improvement_quadruples': strict_sets,
            'minimum_delta_histogram': {str(k): v for k, v in sorted(delta_histogram.items())},
            'receipt_sha256': receipt_sha,
            'best_witness': best_witness,
        }
        if depth is not None and depth <= 2:
            need(strict_sets == 0 and best_total >= 224,
                 'pair/triple prefix agrees with the exhaustive lower-block censuses')
        summaries.append(summary)
    return base, summaries, len(rho_cache)


def dense_scalar_identity_control(supports, rational_maps):
    """Check every representative on all 112^2 scalar entries, plus a bad inverse."""
    matrix = [[int(port in support) for support in supports] for port in range(PORTS)]
    before = [[sum(matrix[i][channel] * matrix[j][channel]
                   for channel in range(CHANNELS)) for j in range(PORTS)]
              for i in range(PORTS)]

    for _, record in sorted(rational_maps.items()):
        gauge = record['matrix']
        current_inverse = record['inverse']
        transformed = [[sum(matrix[i][old] * gauge[old][term]
                            for old in range(BLOCK)) for term in range(BLOCK)]
                       for i in range(PORTS)]
        after = [[sum(matrix[i][channel] * matrix[j][channel]
                      for channel in range(BLOCK, CHANNELS))
                   + sum(transformed[i][term]
                         * sum(current_inverse[term][old] * matrix[j][old]
                                for old in range(BLOCK))
                         for term in range(BLOCK))
                   for j in range(PORTS)] for i in range(PORTS)]
        need(after == before, 'exact 112x112 scalar identity for every rational-cell representative')

    first_record = rational_maps[sorted(rational_maps)[0]]
    wrong = [row[:] for row in first_record['inverse']]
    wrong[0][0] += 1
    gauge = first_record['matrix']
    transformed = [[sum(matrix[i][old] * gauge[old][term]
                        for old in range(BLOCK)) for term in range(BLOCK)]
                   for i in range(PORTS)]
    wrong_after = [[sum(matrix[i][channel] * matrix[j][channel]
                        for channel in range(BLOCK, CHANNELS))
                    + sum(transformed[i][term]
                          * sum(wrong[term][old] * matrix[j][old]
                                 for old in range(BLOCK))
                          for term in range(BLOCK))
                    for j in range(PORTS)] for i in range(PORTS)]
    need(wrong_after != before, 'wrong inverse is rejected by the scalar-identity control')
    return {
        'representative_maps_checked': len(rational_maps),
        'scalar_entries_per_map': PORTS * PORTS,
        'wrong_inverse_rejected': True,
    }


def build():
    basis, channel_planes, supports = load_geometry()
    support_lemma_sha, rational_samples = check_rational_support_lemma()
    maps_by_depth, word_counts, rational_maps, parameter_representatives = cycle_maps()
    need(rational_samples <= set(rational_maps),
         'non-unit rational samples land in the classified support cells')
    base, summaries, rho_pairs = census(basis, channel_planes, maps_by_depth, rational_maps)
    scalar_control = dense_scalar_identity_control(supports, rational_maps)
    support_census = []
    for depth, maps in sorted(maps_by_depth.items()):
        ordered = sorted(maps.items())
        support_census.append({
            'prefix_shears': depth,
            'all_ordered_words': word_counts[depth],
            'distinct_support_pairs': len(ordered),
            'maps': [record for _, record in ordered],
        })
    minimum = min(row['minimum_total_invoice'] for row in summaries)
    certificate = {
        'schema_version': 1,
        'base_commit': BASE_COMMIT,
        'pr3335_head': PR3335_HEAD,
        'selected_archive_sha256': ARCHIVE_SHA,
        'rank34_certificate_sha256': CERT_SHA,
        'generator': ('For each permutation (a,b,c,d), multiply the first k factors '
                      'E_ab(x0) E_bc(x1) E_cd(x2) E_da(x3), where E_ij(x)=I+x e_ij '
                      'and each x is rational. The polynomial path expansion classifies '
                      'every rational support cell by the zero-edge mask and, when all '
                      'edges are nonzero, whether their product is -1.'),
        'rational_support_lemma_sha256': support_lemma_sha,
        'base_channel_invoices': base,
        'cycle_support_census': support_census,
        'all_rational_parameter_representatives': parameter_representatives,
        'all_rational_cycle_support_pairs': [record for _, record in sorted(rational_maps.items())],
        'dense_scalar_identity_control': scalar_control,
        'four_channel_price_census': summaries,
        'cached_pairing_rank_cases': rho_pairs,
        'minimum_invoice_in_any_screened_prefix': minimum,
    }
    result = {
        'schema_version': 1,
        'object': 'rational four-cycle shear gauges in the exact PR3335 rank-34 fit',
        'scope': ('All rational coefficients, including zero coefficients, for each of the 24 ordered '
                  'simple four-cycle shear words, priced on all 46,376 channel quadruples.'),
        'base_invoice': 224,
        'minimum_invoice_by_prefix': {
            str(row['prefix_shears']): row['minimum_total_invoice']
            for row in summaries if row['prefix_shears'] is not None},
        'strict_improvement_quadruples_by_prefix': {
            str(row['prefix_shears']): row['strict_improvement_quadruples']
            for row in summaries if row['prefix_shears'] is not None},
        'all_nonzero_cycle_minimum_invoice': summaries[3]['minimum_total_invoice'],
        'all_nonzero_cycle_strict_improvement_quadruples': summaries[3]['strict_improvement_quadruples'],
        'all_rational_cycle_minimum_invoice': summaries[-1]['minimum_total_invoice'],
        'all_rational_cycle_strict_improvement_quadruples': summaries[-1]['strict_improvement_quadruples'],
        'rational_support_pairs': len(rational_maps),
        'rational_parameter_representatives': parameter_representatives,
        'dense_scalar_identity_control': scalar_control,
        'minimum_invoice_in_any_screened_prefix': minimum,
        'kappa_change': None,
        'physical_supplier_claim': False,
    }
    return certificate, result


def main() -> None:
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
    print('PASS_FOUR_CHANNEL_CYCLE_HOLONOMY',
          'minimums=' + json.dumps(result['minimum_invoice_by_prefix'], sort_keys=True),
          'full_rational_min=' + str(result['all_rational_cycle_minimum_invoice']),
          'full_nonzero_min=' + str(result['all_nonzero_cycle_minimum_invoice']),
          'improvements=' + json.dumps(result['strict_improvement_quadruples_by_prefix'], sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (CheckFailure, OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit('FAIL_FOUR_CHANNEL_CYCLE_HOLONOMY: ' + str(exc)) from exc
