#!/usr/bin/env python3
"""Exhaust rational 3x3 latent gauges by classifying matrix/inverse supports."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import io
import itertools
import json
import math
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
PORTS, PLANES, CHANNELS, BLOCK = 112, 56, 34, 3
Q = Fraction


class CheckFailure(Exception):
    pass


def need(ok: bool, message: str) -> None:
    if not ok:
        raise CheckFailure(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authenticate(data: bytes, expected: str, label: str) -> bytes:
    need(sha256(data) == expected, label + ': SHA256 mismatch')
    return data


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def rank_f2(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        row = original
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def pairing_rank(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    rows = [sum(dot(x, y) << j for j, y in enumerate(right)) for x in left]
    return rank_f2(rows)


def load_inputs() -> tuple[list[int], list[tuple[int, int]], list[list[int]]]:
    archive_data = authenticate(ARCHIVE.read_bytes(), ARCHIVE_SHA, 'selected archive')
    with tarfile.open(fileobj=io.BytesIO(archive_data), mode='r:gz') as archive:
        matches = [m for m in archive.getmembers() if m.name == MEMBER]
        need(len(matches) == 1 and matches[0].isfile(), 'unique regular selected-label member')
        stream = archive.extractfile(matches[0])
        need(stream is not None, 'selected-label member is readable')
        label_data = authenticate(stream.read(), MEMBER_SHA, 'selected labels')
    records = json.loads(label_data)['recipes']
    by_port = {row['port']: row['q'] for row in records}
    need(len(records) == len(by_port) == PORTS, '112 unique selected ports')
    need(sorted(by_port) == list(range(PORTS)), 'complete selected port numbering')
    labels = [by_port[i] for i in range(PORTS)]
    need(all(type(x) is int and 0 < x < 512 for x in labels), 'nine-bit labels')
    need(len(set(labels)) == PORTS, 'selected labels are distinct')
    cert_data = authenticate(CERT.read_bytes(), CERT_SHA, 'PR3335 certificate')
    cert = json.loads(cert_data)
    return labels, [tuple(p) for p in cert['pairs']], [list(s) for s in cert['supports']]


def geometry(labels: list[int], pairs: list[tuple[int, int]], supports: list[list[int]]):
    need(len(pairs) == PLANES, '56 paired planes')
    need(sorted(i for pair in pairs for i in pair) == list(range(PORTS)), 'plane partition')
    owner = {port: p for p, pair in enumerate(pairs) for port in pair}
    basis = [(labels[a], labels[b]) for a, b in pairs]
    orthogonal = [[all(dot(x, y) == 0 for x in left for y in right)
                   for right in basis] for left in basis]
    need(all(dot(a, a) == dot(b, b) == 1 and dot(a, b) == 0 for a, b in basis),
         'each paired plane has Gram I2')
    need(len(supports) == CHANNELS and all(s for s in supports), '34 nonempty scalar supports')
    need(sorted(i for support in supports for i in support) == list(range(PORTS)),
         'scalar supports partition all ports')
    channel_planes = []
    for support in supports:
        mask = 0
        for port in support:
            mask |= 1 << owner[port]
        channel_planes.append(mask)
    return basis, channel_planes, [owner[i] for i in range(PORTS)], orthogonal


def plane_vectors(mask: int, basis: list[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(v for p, pair in enumerate(basis) if mask >> p & 1 for v in pair)


def scalar_matrix(supports: list[list[int]]) -> list[list[int]]:
    return [[sum(int(i in s and j in s) for s in supports) for j in range(PORTS)]
            for i in range(PORTS)]


def check_scalar_mask(K: list[list[int]], owner: list[int], orthogonal: list[list[bool]],
                      supports: list[list[int]]) -> None:
    need(all(K[i][i] == 1 for i in range(PORTS)), 'scalar diagonal')
    for i in range(PORTS):
        for j in range(PORTS):
            if i != j and not orthogonal[owner[i]][owner[j]]:
                need(K[i][j] == 0, 'strict scalar plane mask')
    representatives = [s[0] for s in supports]
    need(all(K[i][j] == int(i == j) for i in representatives for j in representatives),
         'rank-34 support minor')


def parity(value: int) -> int:
    return value.bit_count() & 1


def bit(mask: int, index: int) -> int:
    return (mask >> index) & 1


def permutation_parity(p: tuple[int, ...]) -> int:
    return sum(p[i] > p[j] for i in range(len(p)) for j in range(i + 1, len(p))) & 1


def rref(rows: list[tuple[int, ...]], n: int):
    matrix = [[Q(x) for x in row] for row in rows if any(row)]
    pivots = []
    rank = 0
    for col in range(n):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][col]
        matrix[rank] = [x / value for x in matrix[rank]]
        for r in range(len(matrix)):
            if r != rank and matrix[r][col]:
                value = matrix[r][col]
                matrix[r] = [x - value * y for x, y in zip(matrix[r], matrix[rank])]
        pivots.append(col)
        rank += 1
        if rank == len(matrix):
            break
    return matrix[:rank], pivots


def reduce_by_rowspace(vector: tuple[int, ...], basis, pivots) -> tuple[Fraction, ...]:
    value = [Q(x) for x in vector]
    for row, pivot in zip(basis, pivots):
        if value[pivot]:
            factor = value[pivot]
            value = [x - factor * y for x, y in zip(value, row)]
    return tuple(value)


def in_rowspace(vector: tuple[int, ...], basis, pivots) -> bool:
    return not any(reduce_by_rowspace(vector, basis, pivots))


def integer_nullspace(rows: list[tuple[int, ...]], n: int) -> list[tuple[int, ...]]:
    basis, pivots = rref(rows, n)
    free = [col for col in range(n) if col not in pivots]
    result = []
    for col in free:
        vector = [Q(0)] * n
        vector[col] = Q(1)
        for row, pivot in zip(basis, pivots):
            vector[pivot] = -row[col]
        denominator = 1
        for value in vector:
            denominator = math.lcm(denominator, value.denominator)
        result.append(tuple(int(value * denominator) for value in vector))
    return result


def difference_vector(left: int, right: int, n: int) -> tuple[int, ...]:
    return tuple(bit(left, i) - bit(right, i) for i in range(n))


def matching_terms(pattern: int, edge_index: dict[int, int], edge_count: int):
    result = []
    for permutation in itertools.permutations(range(BLOCK)):
        positions = [BLOCK * row + permutation[row] for row in range(BLOCK)]
        if all(bit(pattern, position) for position in positions):
            term = sum(1 << edge_index[position] for position in positions)
            result.append((term, permutation_parity(permutation)))
    return result


def cofactor_products(pattern: int, edge_index: dict[int, int]):
    """Inverse (i,j) has cofactor deleting matrix row j and column i."""
    result = []
    for i in range(BLOCK):
        for j in range(BLOCK):
            rows = [r for r in range(BLOCK) if r != j]
            cols = [c for c in range(BLOCK) if c != i]
            products = []
            for pairs in (((rows[0], cols[0]), (rows[1], cols[1])),
                          ((rows[0], cols[1]), (rows[1], cols[0]))):
                if all(bit(pattern, BLOCK * r + c) for r, c in pairs):
                    products.append(sum(1 << edge_index[BLOCK * r + c] for r, c in pairs))
            result.append((BLOCK * i + j, products))
    return result


def choose_generic_exponents(kernel: list[tuple[int, ...]], forbidden: set[tuple[int, ...]],
                              edge_count: int) -> tuple[int, ...]:
    if not kernel:
        need(not forbidden, 'zero-dimensional kernel has no forbidden nonzero forms')
        return (0,) * edge_count
    forms = []
    for form in sorted(forbidden):
        coefficients = tuple(sum(form[k] * vector[k] for k in range(edge_count))
                             for vector in kernel)
        need(any(coefficients), 'a forbidden form is nonzero on the nullspace')
        forms.append(coefficients)
    # Each nonzero degree-(d-1) polynomial has at most d-1 positive integer roots.
    root_bound = len(forms) * (len(kernel) - 1)
    selected = None
    for n_value in range(1, root_bound + 2):
        if all(sum(coefficients[i] * (n_value ** i)
                   for i in range(len(coefficients))) != 0 for coefficients in forms):
            selected = n_value
            break
    need(selected is not None, 'finite root-bound witness exists')
    z = tuple(sum(vector[k] * selected ** i for i, vector in enumerate(kernel))
              for k in range(edge_count))
    return z


def matrix_support_map(pattern: int, inverse_pattern: int):
    source_columns = tuple(sum(1 << r for r in range(BLOCK)
                               if bit(pattern, BLOCK * r + c)) for c in range(BLOCK))
    inverse_rows = tuple(sum(1 << c for c in range(BLOCK)
                             if bit(inverse_pattern, BLOCK * r + c)) for r in range(BLOCK))
    return source_columns, inverse_rows


def enumerate_rational_support_maps() -> tuple[dict, int, int]:
    """Classify every possible pair (support(G), support(G^-1)) over Q.

    A zero 2x2 cofactor gives a binomial equality. Prime valuations of any
    rational witness lie in the resulting integer nullspace; its entry signs
    solve the parallel F2 equations. A generic integer valuation vector avoids
    every non-forced nonzero cofactor and determinant-monomial collision.
    Base 7 then makes a nonzero determinant coefficient group dominate all
    lower exponent groups, yielding an explicit rational witness for each map.
    """
    support_maps = {}
    invertible_source_patterns = 0
    feasible_pattern_pairs = 0
    for pattern in range(1 << 9):
        edges = [position for position in range(9) if bit(pattern, position)]
        edge_index = {position: i for i, position in enumerate(edges)}
        edge_count = len(edges)
        det_terms = matching_terms(pattern, edge_index, edge_count)
        if not det_terms:
            continue
        invertible_source_patterns += 1
        cofactors = cofactor_products(pattern, edge_index)
        forced_ones = 0
        flexible = []
        impossible = False
        for index, products in cofactors:
            if not products:
                continue
            if len(products) == 1:
                forced_ones |= 1 << index
            else:
                left, right = products
                flexible.append((index, left, right,
                                 difference_vector(left, right, edge_count)))
        for zero_mask in range(1 << len(flexible)):
            constraints = []
            zero_sign_masks = []
            for k, (_, left, right, diff) in enumerate(flexible):
                if bit(zero_mask, k):
                    constraints.append(diff)
                    zero_sign_masks.append(left ^ right)
            rowspace, pivots = rref(constraints, edge_count)
            determinant_groups = {}
            for term, perm_sign in det_terms:
                reduced = reduce_by_rowspace(
                    tuple(bit(term, i) for i in range(edge_count)), rowspace, pivots)
                determinant_groups.setdefault(reduced, []).append((term, perm_sign))
            forced_nonzero_sign_masks = []
            forbidden = set()
            for k, (_, left, right, diff) in enumerate(flexible):
                if bit(zero_mask, k):
                    continue
                if in_rowspace(diff, rowspace, pivots):
                    forced_nonzero_sign_masks.append(left ^ right)
                else:
                    forbidden.add(diff)
            for (left, _), (right, _) in itertools.combinations(det_terms, 2):
                diff = difference_vector(left, right, edge_count)
                if not in_rowspace(diff, rowspace, pivots):
                    forbidden.add(diff)
            kernel = integer_nullspace(constraints, edge_count)
            exponents = choose_generic_exponents(kernel, forbidden, edge_count)
            need(all(sum(diff[k] * exponents[k] for k in range(edge_count)) == 0
                     for diff in constraints), 'zero-cofactor valuation equations')
            need(all(sum(diff[k] * exponents[k] for k in range(edge_count)) != 0
                     for diff in forbidden), 'generic valuation avoids every forbidden hyperplane')
            signs = None
            for sign_mask in range(1 << edge_count):
                if any(parity(sign_mask & mask) != 0 for mask in zero_sign_masks):
                    continue
                if any(parity(sign_mask & mask) != 1 for mask in forced_nonzero_sign_masks):
                    continue
                group_sums = []
                for terms in determinant_groups.values():
                    total = 0
                    for term, perm_sign in terms:
                        total += -1 if (perm_sign ^ parity(sign_mask & term)) else 1
                    group_sums.append(total)
                if any(group_sums):
                    signs = sign_mask
                    break
            if signs is None:
                continue
            inverse_pattern = forced_ones
            for k, (index, _, _, _) in enumerate(flexible):
                if not bit(zero_mask, k):
                    inverse_pattern |= 1 << index
            key = matrix_support_map(pattern, inverse_pattern)
            witness = {
                'matrix_support': pattern,
                'inverse_support': inverse_pattern,
                'zero_flexible_cofactor_mask': zero_mask,
                'edge_sign_mask': signs,
                'edge_exponents': [[edge, exponents[i]] for i, edge in enumerate(edges)],
                'prime_base': 7,
            }
            need(key not in support_maps, 'support masks uniquely determine matrix and inverse masks')
            support_maps[key] = witness
            feasible_pattern_pairs += 1
    return support_maps, invertible_source_patterns, feasible_pattern_pairs


def inverse_matrix(matrix: list[list[Fraction]]):
    n = len(matrix)
    augmented = [[Q(x) for x in row] + [Q(i == j) for j in range(n)]
                 for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if augmented[r][col]), None)
        if pivot is None:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        value = augmented[col][col]
        augmented[col] = [x / value for x in augmented[col]]
        for row in range(n):
            if row != col and augmented[row][col]:
                value = augmented[row][col]
                augmented[row] = [x - value * y
                                  for x, y in zip(augmented[row], augmented[col])]
    return [row[n:] for row in augmented]


def rational_matrix_witness(witness: dict) -> list[list[Fraction]]:
    pattern = witness['matrix_support']
    exponents = dict(witness['edge_exponents'])
    edges = [position for position in range(9) if bit(pattern, position)]
    edge_index = {position: i for i, position in enumerate(edges)}
    matrix = []
    for r in range(BLOCK):
        row = []
        for c in range(BLOCK):
            position = BLOCK * r + c
            if not bit(pattern, position):
                row.append(Q(0))
                continue
            exponent = exponents[position]
            value = Q(7 ** exponent) if exponent >= 0 else Q(1, 7 ** (-exponent))
            if bit(witness['edge_sign_mask'], edge_index[position]):
                value = -value
            row.append(value)
        matrix.append(row)
    return matrix


def verify_symbolic_witness(witness: dict,
                            expected_map: tuple[tuple[int, ...], tuple[int, ...]]) -> None:
    pattern = witness['matrix_support']
    inverse_pattern = witness['inverse_support']
    edges = [position for position in range(9) if bit(pattern, position)]
    edge_index = {position: i for i, position in enumerate(edges)}
    need(set(dict(witness['edge_exponents'])) == set(edges), 'one exponent per nonzero matrix entry')
    need(witness['prime_base'] == 7, 'determinant-dominating rational prime')
    exponents = dict(witness['edge_exponents'])
    cofactors = cofactor_products(pattern, edge_index)
    flexible_zero_mask = 0
    flexible_index = 0
    for index, products in cofactors:
        is_inverse_nonzero = bit(inverse_pattern, index)
        if not products:
            need(not is_inverse_nonzero, 'empty cofactor is zero')
        elif len(products) == 1:
            need(is_inverse_nonzero, 'single cofactor monomial is nonzero')
        else:
            left, right = products
            is_zero = not is_inverse_nonzero
            if is_zero:
                flexible_zero_mask |= 1 << flexible_index
            flexible_index += 1
            left_exp = sum(exponents[edge] for edge in edges if bit(left, edge_index[edge]))
            right_exp = sum(exponents[edge] for edge in edges if bit(right, edge_index[edge]))
            left_sign = parity(witness['edge_sign_mask'] & left)
            right_sign = parity(witness['edge_sign_mask'] & right)
            equal = left_exp == right_exp and left_sign == right_sign
            need(is_inverse_nonzero != equal, 'cofactor zero/nonzero matches inverse support')
    need(witness['zero_flexible_cofactor_mask'] == flexible_zero_mask,
         'recorded flexible zero-cofactor subset')
    det_terms = matching_terms(pattern, edge_index, len(edges))
    need(det_terms, 'matrix support admits a determinant matching')
    determinant_coefficients = Counter()
    for term, perm_sign in det_terms:
        exponent = sum(exponents[edge] for edge in edges if bit(term, edge_index[edge]))
        sign = perm_sign ^ parity(witness['edge_sign_mask'] & term)
        determinant_coefficients[exponent] += -1 if sign else 1
    need(any(determinant_coefficients.values()), 'witness determinant is nonzero')
    source_reader = matrix_support_map(pattern, inverse_pattern)
    need(source_reader == expected_map, 'witness source/inverse support map matches its key')
    matrix = rational_matrix_witness(witness)
    inverse = inverse_matrix(matrix)
    need(inverse is not None, 'explicit base-7 rational witness is invertible')
    for i in range(BLOCK):
        for j in range(BLOCK):
            need(sum(matrix[i][k] * inverse[k][j] for k in range(BLOCK)) == Q(i == j),
                 'exact witness inverse')
    direct_map = matrix_support_map(
        sum(1 << (BLOCK * r + c) for r in range(BLOCK) for c in range(BLOCK)
            if matrix[r][c]),
        sum(1 << (BLOCK * r + c) for r in range(BLOCK) for c in range(BLOCK)
            if inverse[r][c]))
    need(direct_map == expected_map, 'explicit rational matrix realizes support map')


def signed_ternary_maps() -> tuple[set, int]:
    maps = set()
    invertible = 0
    for values in itertools.product((-1, 0, 1), repeat=9):
        matrix = [[Q(values[3 * r + c]) for c in range(BLOCK)] for r in range(BLOCK)]
        inverse = inverse_matrix(matrix)
        if inverse is None:
            continue
        invertible += 1
        pattern = sum(1 << (3 * r + c) for r in range(BLOCK) for c in range(BLOCK)
                      if matrix[r][c])
        inverse_pattern = sum(1 << (3 * r + c) for r in range(BLOCK) for c in range(BLOCK)
                              if inverse[r][c])
        maps.add(matrix_support_map(pattern, inverse_pattern))
    return maps, invertible


def encode(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(x) for x in value]
    return value


def census_invoice(channel_planes: list[int], basis: list[tuple[int, int]],
                   support_maps: dict) -> tuple[dict, dict]:
    vector_cache = {0: ()}
    pairing_cache = {}

    def vectors(mask):
        if mask not in vector_cache:
            vector_cache[mask] = tuple(v for p, pair in enumerate(basis)
                                       if mask >> p & 1 for v in pair)
        return vector_cache[mask]

    def rho(left_mask, right_mask):
        key = (left_mask, right_mask)
        if key not in pairing_cache:
            pairing_cache[key] = pairing_rank(vectors(left_mask), vectors(right_mask))
        return pairing_cache[key]

    base_costs = [rho(mask, mask) for mask in channel_planes]
    need(Counter(base_costs) == Counter({4: 8, 6: 8, 8: 18}) and sum(base_costs) == 224,
         'published full-plane invoice is 224')
    ordered_maps = sorted(support_maps)
    triple_deltas = Counter()
    receipts = []
    strict_improvements = 0
    priced_cases = 0
    global_minimum = 10**9
    for triple in itertools.combinations(range(CHANNELS), BLOCK):
        local_plane_masks = tuple(channel_planes[i] for i in triple)
        baseline = sum(base_costs[i] for i in triple)
        best_invoice = 10**9
        best_map_index = None
        for map_index, (source_columns, inverse_rows) in enumerate(ordered_maps):
            invoice = 0
            for term in range(BLOCK):
                source = 0
                reader = 0
                for old in range(BLOCK):
                    if bit(source_columns[term], old):
                        source |= local_plane_masks[old]
                    if bit(inverse_rows[term], old):
                        reader |= local_plane_masks[old]
                invoice += rho(source, reader)
            priced_cases += 1
            if invoice < best_invoice:
                best_invoice = invoice
                best_map_index = map_index
        delta = best_invoice - baseline
        triple_deltas[delta] += 1
        strict_improvements += int(delta < 0)
        global_minimum = min(global_minimum, 224 - baseline + best_invoice)
        receipts.append([*triple, baseline, best_invoice, best_map_index])
    receipt_digest = sha256(json.dumps(receipts, separators=(',', ':')).encode('utf-8'))
    summary = {
        'channel_triples': len(receipts),
        'rational_support_maps_per_triple': len(ordered_maps),
        'priced_triple_map_cases': priced_cases,
        'minimum_invoice_after_one_triple_gauge': global_minimum,
        'per_triple_minimum_delta_histogram': {
            str(k): v for k, v in sorted(triple_deltas.items())},
        'strict_improvements': strict_improvements,
        'canonical_triple_receipt_sha256': receipt_digest,
    }
    return summary, {'base_costs': base_costs, 'ordered_maps': ordered_maps}


def dense_matrix_control(supports: list[list[int]]) -> dict:
    # An exact determinant-two block, with denominators in its inverse.
    G = [[Q(1), Q(1), Q(0)], [Q(0), Q(2), Q(1)], [Q(0), Q(0), Q(1)]]
    Ginv = inverse_matrix(G)
    need(Ginv is not None and Ginv[1][1] == Q(1, 2), 'determinant-two inverse fixture')
    A = [[Q(int(port in support)) for support in supports] for port in range(PORTS)]
    S = [[Q(i == j) for j in range(CHANNELS)] for i in range(CHANNELS)]
    R = [[Q(i == j) for j in range(CHANNELS)] for i in range(CHANNELS)]
    indices = (0, 1, 2)
    for i in range(BLOCK):
        for j in range(BLOCK):
            S[indices[i]][indices[j]] = G[i][j]
            R[indices[i]][indices[j]] = Ginv[i][j]
    need(all(sum(R[i][k] * S[k][j] for k in range(CHANNELS)) == Q(i == j)
             for i in range(CHANNELS) for j in range(CHANNELS)), 'global inverse fixture')
    source = [[sum(A[i][k] * S[k][t] for k in range(CHANNELS))
               for t in range(CHANNELS)] for i in range(PORTS)]
    reader = [[sum(R[t][k] * A[j][k] for k in range(CHANNELS))
               for t in range(CHANNELS)] for j in range(PORTS)]
    before = scalar_matrix(supports)
    after = [[sum(source[i][t] * reader[j][t] for t in range(CHANNELS))
              for j in range(PORTS)] for i in range(PORTS)]
    need(after == [[Q(x) for x in row] for row in before],
         'determinant-two gauge preserves all scalar K entries')
    wrong = [row[:] for row in R]
    wrong[0][0] += 1
    wrong_reader = [[sum(wrong[t][k] * A[j][k] for k in range(CHANNELS))
                     for t in range(CHANNELS)] for j in range(PORTS)]
    wrong_after = [[sum(source[i][t] * wrong_reader[j][t]
                        for t in range(CHANNELS)) for j in range(PORTS)]
                   for i in range(PORTS)]
    need(wrong_after != after, 'wrong inverse reader control is rejected')
    return {'matrix': [[1, 1, 0], [0, 2, 1], [0, 0, 1]],
            'determinant': 2,
            'inverse': [[1, Q(-1, 2), Q(1, 4)], [0, Q(1, 2), Q(-1, 2)], [0, 0, 1]],
            'scalar_entries_checked': PORTS * PORTS,
            'wrong_inverse_rejected': True}


def verify() -> tuple[dict, dict]:
    labels, pairs, supports = load_inputs()
    basis, channel_planes, owner, orthogonal = geometry(labels, pairs, supports)
    K = scalar_matrix(supports)
    check_scalar_mask(K, owner, orthogonal, supports)
    support_maps, source_patterns, feasible_pairs = enumerate_rational_support_maps()
    need(source_patterns == 247 and feasible_pairs == 487 and len(support_maps) == 487,
         'complete rational 3x3 support/inverse-support classification')
    for support_map, witness in support_maps.items():
        verify_symbolic_witness(witness, support_map)
    bounded_maps, bounded_invertible = signed_ternary_maps()
    need(bounded_invertible == 11808 and len(bounded_maps) == 396,
         'signed-ternary predecessor control')
    need(bounded_maps <= set(support_maps),
         'all 396 signed-ternary maps are covered by the rational census')
    invoice, invoice_detail = census_invoice(channel_planes, basis, support_maps)
    need(invoice['channel_triples'] == 5984 and invoice['priced_triple_map_cases'] == 2914208,
         'all triples and rational maps priced')
    need(invoice['strict_improvements'] == 0
         and invoice['minimum_invoice_after_one_triple_gauge'] == 224
         and invoice['per_triple_minimum_delta_histogram'] == {'0': 5984},
         'no arbitrary rational single-triple gauge reduces invoice')
    fixture = dense_matrix_control(supports)
    ordered_maps = invoice_detail['ordered_maps']
    map_records = []
    for support_map in ordered_maps:
        witness = support_maps[support_map]
        exponent_by_position = dict(witness['edge_exponents'])
        map_records.append({
            'source_column_masks': list(support_map[0]),
            'inverse_reader_row_masks': list(support_map[1]),
            'matrix_support': witness['matrix_support'],
            'inverse_support': witness['inverse_support'],
            'zero_flexible_cofactor_mask': witness['zero_flexible_cofactor_mask'],
            'edge_sign_mask': witness['edge_sign_mask'],
            'edge_exponents_by_matrix_position': [exponent_by_position.get(i)
                                                  for i in range(9)],
            'prime_base': witness['prime_base'],
        })
    certificate = {
        'schema_version': 1,
        'base_commit': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'pr3335_head': '1d46df8b5aeac49d165cae58c1dd1036666bb789',
        'selected_archive_sha256': ARCHIVE_SHA,
        'rank34_certificate_sha256': CERT_SHA,
        'object': 'complete-plane one-total invoice under one arbitrary rational GL3 gauge',
        'baseline_invoice': 224,
        'rational_support_classification': {
            'coefficient_field': 'Q',
            'invertible_source_zero_patterns': source_patterns,
            'feasible_matrix_inverse_support_pairs': feasible_pairs,
            'distinct_support_maps': len(support_maps),
            'witness_form': 'nonzero entries are signed powers of 7 with exact integer exponents; zero cofactors, nonzero cofactors and nonzero determinant are checked exactly',
            'all_support_map_witnesses': map_records,
        },
        'triple_invoice_census': invoice,
        'signed_ternary_control': {
            'invertible_matrices': bounded_invertible,
            'distinct_support_maps': len(bounded_maps),
            'all_maps_in_rational_census': True,
        },
        'exact_scalar_identity_control': fixture,
        'scope_limit': 'one arbitrary rational 3x3 gauge on one triple of the exact published factorization at a time; no sequence of overlapping gauges, larger simultaneous blocks, other factorizations, physical native implementation or supplier admission is covered',
    }
    result = {
        'schema_version': 1,
        'status': 'completed scoped exact negative; no kappa change',
        'task_id': 'coverage-law-change',
        'priority_revision': 6,
        'base_commit': certificate['base_commit'],
        'baseline_copy_invoice': 224,
        'minimum_after_one_arbitrary_rational_three_channel_gauge': 224,
        'rational_support_maps': len(support_maps),
        'channel_triples': invoice['channel_triples'],
        'priced_cases': invoice['priced_triple_map_cases'],
        'strict_improvements': invoice['strict_improvements'],
        'per_triple_minimum_delta_histogram': invoice['per_triple_minimum_delta_histogram'],
        'scope': 'No single arbitrary rational GL3(Q) basis change on any triple of the published 34 channels lowers the complete-plane invoice.',
        'limitations': [
            'This is not a lower bound for sequential or overlapping gauges, blocks of size four or more, or any other scalar factorization.',
            'The tariff is the inherited conditional full-plane proxy; no physical word, supplier, selected-result change or kappa improvement is established.',
        ],
    }
    return certificate, result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-artifacts', action='store_true')
    args = parser.parse_args()
    certificate, result = verify()
    cert_path, result_path = HERE / 'CERTIFICATE.json', HERE / 'RESULT.json'
    if args.write_artifacts:
        cert_path.write_text(json.dumps(encode(certificate), indent=2) + '\n', encoding='utf-8')
        result_path.write_text(json.dumps(encode(result), indent=2) + '\n', encoding='utf-8')
    else:
        need(json.loads(cert_path.read_text(encoding='utf-8')) == encode(certificate),
             'CERTIFICATE.json mismatch')
        need(json.loads(result_path.read_text(encoding='utf-8')) == encode(result),
             'RESULT.json mismatch')
    print('PASS_PAIRED_PLANE_RANK34_RATIONAL_TRIPLE_GAUGE '
          f'maps={certificate["rational_support_classification"]["distinct_support_maps"]} '
          f'triples={certificate["triple_invoice_census"]["channel_triples"]} '
          f'cases={certificate["triple_invoice_census"]["priced_triple_map_cases"]} '
          'baseline=224 minimum=224 improvements=0')


if __name__ == '__main__':
    main()
