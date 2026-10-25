#!/usr/bin/env python3
"""Exhaust every rational two-channel gauge by its projective support cells."""
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
CERT = HERE.parents[1] / 'research/paired-plane-rank34-copy-invoice/predecessor/PR3335-CERTIFICATE.json'
CERT_SHA = 'cd5edbe9bf46aa544ee47450adcf0c2dc9eee5a57acda8bc6f4b726ab7f2ae47'
PORTS, PLANES, CHANNELS = 112, 56, 34
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


def geometry(labels: list[int], pairs: list[tuple[int, int]],
             supports: list[list[int]]) -> tuple[list[tuple[int, int]], list[int], list[int], list[list[int]]]:
    need(len(pairs) == PLANES, '56 paired planes')
    need(sorted(i for pair in pairs for i in pair) == list(range(PORTS)), 'plane partition')
    owner = {port: p for p, pair in enumerate(pairs) for port in pair}
    plane_vectors = [(labels[a], labels[b]) for a, b in pairs]
    orthogonal = [[all(dot(x, y) == 0 for x in a for y in b)
                   for b in plane_vectors] for a in plane_vectors]
    need(all(dot(a, a) == dot(b, b) == 1 and dot(a, b) == 0 for a, b in plane_vectors),
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
    return plane_vectors, channel_planes, [owner[i] for i in range(PORTS)], orthogonal


def plane_vectors(mask: int, basis: list[tuple[int, int]]) -> tuple[int, ...]:
    return tuple(v for p, pair in enumerate(basis) if mask >> p & 1 for v in pair)


def union_planes(channel_mask: int, channel_planes: list[int]) -> int:
    result = 0
    while channel_mask:
        bit = channel_mask & -channel_mask
        result |= channel_planes[bit.bit_length() - 1]
        channel_mask ^= bit
    return result


def support_mask(vector: tuple[Fraction, ...]) -> int:
    return sum(1 << i for i, value in enumerate(vector) if value)


def linear_combination(a: tuple[Fraction, ...], b: tuple[Fraction, ...],
                       alpha: Fraction, beta: Fraction) -> tuple[Fraction, ...]:
    return tuple(alpha * x + beta * y for x, y in zip(a, b))


def direction_profile(state, i: int, j: int, slope: Fraction | None,
                      channel_planes: list[int], basis: list[tuple[int, int]]) -> tuple[int, int]:
    if slope is None:
        source = state.columns[j]
        dual_reader = tuple(-x for x in state.rows[i])
    else:
        source = linear_combination(state.columns[i], state.columns[j], Q(1), slope)
        dual_reader = linear_combination(state.rows[i], state.rows[j], -slope, Q(1))
    source_channels = support_mask(source)
    reader_channels = support_mask(dual_reader)
    return (union_planes(source_channels, channel_planes),
            union_planes(reader_channels, channel_planes))


def projective_candidates(state, i: int, j: int) -> list[Fraction | None]:
    """One exact slope per support cell, plus infinity and two generic points."""
    critical: set[Fraction] = set()
    ci, cj = state.columns[i], state.columns[j]
    ri, rj = state.rows[i], state.rows[j]
    for left, right in zip(ci, cj):
        if right:
            critical.add(-left / right)
    for left, right in zip(ri, rj):
        if left:
            critical.add(right / left)
    generic: list[Fraction] = []
    q = Q(0)
    while len(generic) < 2:
        if q not in critical:
            generic.append(q)
        q += 1
    # None is the projective point at infinity.
    return sorted(critical) + generic + [None]


def local_pair_minimum(state, i: int, j: int, channel_planes: list[int],
                       basis: list[tuple[int, int]]) -> dict:
    slopes = projective_candidates(state, i, j)
    profiles = {s: direction_profile(state, i, j, s, channel_planes, basis) for s in slopes}
    best = None
    support_cases = 0
    for x, y in itertools.combinations(slopes, 2):
        sx, dx = profiles[x]
        sy, dy = profiles[y]
        invoice = (pairing_rank(plane_vectors(sx, basis), plane_vectors(dy, basis))
                   + pairing_rank(plane_vectors(sy, basis), plane_vectors(dx, basis)))
        support_cases += 1
        if best is None or invoice < best[0]:
            best = (invoice, x, y)
    need(best is not None, 'at least two projective directions')
    return {'invoice': best[0], 'slope_x': best[1], 'slope_y': best[2],
            'candidate_slopes': len(slopes), 'support_cases': support_cases}


class GaugeState:
    def __init__(self) -> None:
        self.columns = [tuple(Q(i == j) for i in range(CHANNELS)) for j in range(CHANNELS)]
        self.rows = [tuple(Q(i == j) for j in range(CHANNELS)) for i in range(CHANNELS)]

    def apply(self, i: int, j: int, x: Fraction | None,
              y: Fraction | None) -> tuple[list[tuple[Fraction, ...]], list[tuple[Fraction, ...]]]:
        def projective(slope):
            return (Q(0), Q(1)) if slope is None else (Q(1), slope)
        ax, cx = projective(x)
        ay, cy = projective(y)
        det = ax * cy - ay * cx
        need(det != 0, 'singular two-channel basis')
        old_i, old_j = self.columns[i], self.columns[j]
        row_i, row_j = self.rows[i], self.rows[j]
        new_columns = [linear_combination(old_i, old_j, ax, cx),
                       linear_combination(old_i, old_j, ay, cy)]
        # Rows of G^-1, paired to the corresponding new source columns.
        new_rows = [linear_combination(row_i, row_j, cy / det, -ay / det),
                    linear_combination(row_i, row_j, -cx / det, ax / det)]
        return new_columns, new_rows

    def check_inverse(self) -> None:
        for i in range(CHANNELS):
            for j in range(CHANNELS):
                value = sum((self.rows[i][k] * self.columns[j][k]
                             for k in range(CHANNELS)), Q(0))
                need(value == Q(i == j), 'exact basis/inverse identity')


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


def rational_fixture(K: list[list[int]], supports: list[list[int]]) -> dict:
    state = GaugeState()
    # slopes 0 and 2 give G=[[1,1],[0,2]], with a genuine half in its inverse.
    new_columns, new_rows = state.apply(0, 1, Q(0), Q(2))
    S = [[new_columns[j][i] if j < 2 else Q(i == j) for j in range(CHANNELS)]
         for i in range(CHANNELS)]
    R = [[new_rows[j][i] if j < 2 else Q(i == j) for i in range(CHANNELS)]
         for j in range(CHANNELS)]
    need(S[1][1] == 2 and R[1][1] == Q(1, 2), 'determinant-two rational fixture')
    need(all(sum((R[i][k] * S[k][j] for k in range(CHANNELS)), Q(0)) == Q(i == j)
             for i in range(CHANNELS) for j in range(CHANNELS)), 'S inverse fixture')
    A = [[int(port in support) for support in supports] for port in range(PORTS)]
    source_terms = [[sum((A[i][k] * S[k][t] for k in range(CHANNELS)), Q(0))
                     for t in range(CHANNELS)] for i in range(PORTS)]
    reader_terms = [[sum((R[t][k] * A[j][k] for k in range(CHANNELS)), Q(0))
                     for t in range(CHANNELS)] for j in range(PORTS)]
    after = [[sum((source_terms[i][t] * reader_terms[j][t]
                   for t in range(CHANNELS)), Q(0)) for j in range(PORTS)]
             for i in range(PORTS)]
    need(after == [[Q(x) for x in row] for row in K],
         'dense rational 112x112 fitting matrix is preserved')
    wrong_R = [row[:] for row in R]
    wrong_R[0][0], wrong_R[0][1] = Q(1), Q(-1)
    wrong_reader_terms = [[sum((wrong_R[t][k] * A[j][k] for k in range(CHANNELS)), Q(0))
                           for t in range(CHANNELS)] for j in range(PORTS)]
    wrong = [[sum((source_terms[i][t] * wrong_reader_terms[j][t]
                   for t in range(CHANNELS)), Q(0)) for j in range(PORTS)]
             for i in range(PORTS)]
    need(after != wrong, 'wrong inverse reader factor is rejected')
    return {'matrix': [[1, 1], [0, 2]], 'determinant': 2,
            'inverse': [[1, Q(-1, 2)], [0, Q(1, 2)]],
            'scalar_entries_checked': PORTS * PORTS,
            'wrong_inverse_rejected': True}


def encode(value):
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(x) for x in value]
    return value


def verify() -> tuple[dict, dict]:
    labels, pairs, supports = load_inputs()
    basis, channel_planes, owner, orthogonal = geometry(labels, pairs, supports)
    K = scalar_matrix(supports)
    check_scalar_mask(K, owner, orthogonal, supports)
    baseline = [pairing_rank(plane_vectors(mask, basis), plane_vectors(mask, basis))
                for mask in channel_planes]
    need(Counter(baseline) == Counter({4: 8, 6: 8, 8: 18}) and sum(baseline) == 224,
         'published full-plane invoice is 224')
    state = GaugeState()
    deltas: Counter[int] = Counter()
    pairs_receipt = []
    candidate_slope_counts: Counter[int] = Counter()
    projective_case_counts: Counter[int] = Counter()
    candidate_cases = 0
    max_slopes = 0
    for i, j in itertools.combinations(range(CHANNELS), 2):
        local = local_pair_minimum(state, i, j, channel_planes, basis)
        delta = local['invoice'] - baseline[i] - baseline[j]
        deltas[delta] += 1
        candidate_slope_counts[local['candidate_slopes']] += 1
        projective_case_counts[local['support_cases']] += 1
        candidate_cases += local['support_cases']
        max_slopes = max(max_slopes, local['candidate_slopes'])
        pairs_receipt.append({'channels': [i, j], 'base_invoice': baseline[i] + baseline[j],
                              'minimum_invoice': local['invoice'], 'minimum_delta': delta,
                              'candidate_slopes': local['candidate_slopes'],
                              'projective_support_cases': local['support_cases'],
                              'witness_slopes': [encode(local['slope_x']), encode(local['slope_y'])]})
    need(len(pairs_receipt) == 561, 'every unordered channel pair')
    need(deltas == Counter({0: 561}), 'no rational two-channel gauge lowers the invoice')
    fixture = rational_fixture(K, supports)
    pair_receipt_digest = sha256(json.dumps(
        pairs_receipt, sort_keys=True, separators=(',', ':')).encode('utf-8'))
    certificate = {
        'schema_version': 1,
        'base_commit': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'pr3335_head': '1d46df8b5aeac49d165cae58c1dd1036666bb789',
        'selected_archive_sha256': ARCHIVE_SHA,
        'rank34_certificate_sha256': CERT_SHA,
        'object': 'complete-plane one-total invoice under one arbitrary rational two-channel gauge',
        'baseline_invoice': 224,
        'gauge_domain': {
            'group': 'GL2(Q)',
            'channels': 34,
            'unordered_channel_pairs': 561,
            'parameterization': 'two distinct points of P1(Q), representing the columns of an invertible 2x2 matrix up to nonzero column scaling',
            'support_partition': 'finite rational slopes where a source coordinate or inverse-reader coordinate vanishes, plus infinity and two distinct generic rational slopes',
            'complete_projective_support_cases': candidate_cases,
            'maximum_candidate_slopes_per_channel_pair': max_slopes,
        },
        'pair_census': {
            'unordered_channel_pairs': len(pairs_receipt),
            'candidate_slope_count_histogram': {
                str(k): v for k, v in sorted(candidate_slope_counts.items())},
            'projective_support_case_count_histogram': {
                str(k): v for k, v in sorted(projective_case_counts.items())},
            'complete_projective_support_cases': candidate_cases,
            'minimum_delta_histogram': {str(k): v for k, v in sorted(deltas.items())},
            'canonical_pair_receipt_sha256': pair_receipt_digest,
        },
        'strict_improvements': 0,
        'rational_identity_control': fixture,
        'scope_limit': 'only a single arbitrary rational 2-channel gauge on the exact PR3335 factorization at its published basis; sequential gauges, simultaneous blocks of size at least 3, other scalar factorizations, native implementation and supplier admission are not covered',
    }
    result = {
        'schema_version': 1,
        'status': 'completed scoped exact negative; no kappa change',
        'task_id': 'coverage-law-change',
        'priority_revision': 6,
        'base_commit': certificate['base_commit'],
        'baseline_copy_invoice': 224,
        'minimum_after_one_arbitrary_rational_two_channel_gauge': 224,
        'unordered_channel_pairs': 561,
        'complete_projective_support_cases': candidate_cases,
        'strict_improvements': 0,
        'per_pair_minimum_delta_histogram': certificate['pair_census']['minimum_delta_histogram'],
        'scope': 'No single GL2(Q) basis change on any pair of the published 34 channels lowers the exact complete-plane invoice.',
        'limitations': [
            'This is not a lower bound for sequential or overlapping gauges, simultaneous blocks of size three or more, or any other factorization.',
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
    print('PASS_PAIRED_PLANE_RANK34_RATIONAL_PAIR_GAUGE pairs=561 '
          f'projective_cases={certificate["gauge_domain"]["complete_projective_support_cases"]} '
          'baseline=224 minimum=224 improvements=0')


if __name__ == '__main__':
    main()
