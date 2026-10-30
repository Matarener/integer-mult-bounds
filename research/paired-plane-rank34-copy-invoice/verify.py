#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Full-port one-total tariff of PR3335's literal scalar factors.

No predecessor Python is imported. This is not a native compiler replay.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
MEMBER_SHA = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'
CERT = HERE / 'predecessor/PR3335-CERTIFICATE.json'
CERT_SHA = 'cd5edbe9bf46aa544ee47450adcf0c2dc9eee5a57acda8bc6f4b726ab7f2ae47'


class CheckFailure(Exception):
    pass


def need(ok, why):
    if not ok:
        raise CheckFailure(why)


def authenticate(data, digest, name):
    need(hashlib.sha256(data).hexdigest() == digest, name + ': SHA256 mismatch')
    return data


def dot(x, y):
    return (x & y).bit_count() % 2


def binary_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def span(vectors):
    # Independent finite-set oracle, with no row-reduction calls.
    values = {0}
    for vector in vectors:
        values |= {v ^ vector for v in values}
    return values


def pairing_rank(left, right):
    rows = [sum(dot(x, y) << j for j, y in enumerate(right)) for x in left]
    rank = binary_rank(rows)
    values = span(left)
    radical = {x for x in values if all(dot(x, y) == 0 for y in right)}
    oracle = (len(values) // len(radical)).bit_length() - 1
    need(rank == oracle, 'pairing rank disagrees with finite-set oracle')
    return rank


def load_inputs():
    data = authenticate(ARCHIVE.read_bytes(), ARCHIVE_SHA, 'selected archive')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        handle = archive.extractfile(MEMBER)
        need(handle is not None, 'missing selected label member')
        member = authenticate(handle.read(), MEMBER_SHA, 'selected labels')
    records = json.loads(member)['recipes']
    by_port = {r['port']: r['q'] for r in records}
    need(len(by_port) == len(records) == 112, 'duplicate or missing label record')
    need(sorted(by_port) == list(range(112)), 'selected port numbering')
    labels = [by_port[p] for p in range(112)]
    need(all(type(q) is int and 0 < q < 512 for q in labels), 'nine-bit labels')
    need(len(set(labels)) == 112, 'distinct selected labels')
    cert = json.loads(authenticate(CERT.read_bytes(), CERT_SHA, 'PR3335 certificate'))
    return labels, cert


def geometry(labels, pairs):
    need(len(pairs) == 56 and all(len(p) == 2 for p in pairs), '56 pairs')
    need(all(type(p) is int for pair in pairs for p in pair), 'integer ports')
    need(sorted(p for pair in pairs for p in pair) == list(range(112)), 'perfect matching')
    bases, owner = [], {}
    for n, (a, b) in enumerate(pairs):
        q, r = labels[a], labels[b]
        need(dot(q, q) == dot(r, r) == 1 and dot(q, r) == 0, 'Gram-I2 pair')
        bases.append((q, r))
        owner[a] = owner[b] = n
    orth = [[all(dot(x, y) == 0 for x in a for y in b) for b in bases] for a in bases]
    return bases, owner, orth


def scalar_fit(supports, owner, orth):
    need(len(supports) == 34, 'literal 34 channels')
    need(all(s and all(type(i) is int for i in s) for s in supports), 'nonempty integer supports')
    need(sorted(i for s in supports for i in s) == list(range(112)), 'disjoint support partition')
    K = [[sum(int(i in s and j in s) for s in supports) for j in range(112)] for i in range(112)]
    forced = 0
    for i in range(112):
        for j in range(112):
            if i == j or not orth[owner[i]][owner[j]]:
                need(K[i][j] == int(i == j), 'scalar plane-mask entry')
                forced += 1
    representatives = [s[0] for s in supports]
    need(all(K[i][j] == int(i == j) for i in representatives for j in representatives),
         'rank-34 support minor')
    return K, forced


def invoice(labels, supports, bases, owner):
    costs, line_costs = [], []
    for support in supports:
        # Each touched port carries its WHOLE plane, including its partner.
        full = [q for i in support for q in bases[owner[i]]]
        cost = pairing_rank(full, full)
        need(binary_rank(full) == 2 * len(support), 'orthogonal direct plane sum')
        need(cost == 2 * len(support), 'nondegenerate full-port pairing')
        costs.append(cost)
        singleton_labels = [labels[i] for i in support]
        line_costs.append(pairing_rank(singleton_labels, singleton_labels))
    return costs, line_costs


def check_columns(supports, correction, keep_dirt=True):
    for column in range(224):
        x = [int(column == i) for i in range(112)]
        y = [int(column == 112 + i) for i in range(112)]
        totals = [sum(x[j] for j in s) for s in supports]
        out = [(y[i] if keep_dirt else 0)
               + sum(totals[t] for t, s in enumerate(supports) if i in s)
               + sum(correction[i][j] * x[j] for j in range(112)) for i in range(112)]
        need(out == [y[i] + x[i] for i in range(112)], 'dirty scalar endpoint column')
        # x is untouched. This is a scalar program, not a physical lifetime check.


def expanded_identity(K, bases, owner):
    rows = []
    for i in range(112):
        for q in bases[owner[i]]:
            row = 0
            for j in range(112):
                for beta, r in enumerate(bases[owner[j]]):
                    row |= ((K[i][j] * dot(q, r)) % 2) << (2 * j + beta)
            rows.append(row)
    need(rows == [1 << i for i in range(224)], 'expanded masked transfer is I224')
    need(binary_rank(rows) == 224, 'expanded integral floor')


def rejects(action, name):
    try:
        action()
    except CheckFailure:
        return name
    raise CheckFailure('failure control was accepted: ' + name)


def equal_receipt(actual, expected):
    # Canonical JSON equality distinguishes true from 1 and false from 0.
    def encode(value):
        return json.dumps(value, sort_keys=True, separators=(',', ':'))
    need(encode(actual) == encode(expected), 'receipt mismatch')


def controls(labels, cert, owner, orth, costs, correction):
    supports = cert['supports']
    result = []
    bad = copy.deepcopy(cert['pairs'])
    bad[0][0] = bad[0][1]
    result.append(rejects(lambda: geometry(labels, bad), 'duplicate_matching_port'))
    bad_supports = copy.deepcopy(supports)
    bad_supports[0][0] = bad_supports[1][0]
    result.append(rejects(lambda: scalar_fit(bad_supports, owner, orth), 'support_overlap'))
    bad_supports = copy.deepcopy(supports)
    first = bad_supports[0][0]
    partner = next(i for i in cert['pairs'][owner[first]] if i != first)
    other = next(t for t, s in enumerate(bad_supports) if partner in s)
    pos = bad_supports[other].index(partner)
    bad_supports[0][1], bad_supports[other][pos] = partner, bad_supports[0][1]
    result.append(rejects(lambda: scalar_fit(bad_supports, owner, orth), 'same_plane_cross_entry'))
    bad_correction = copy.deepcopy(correction)
    i, j = next((i, j) for i in range(112) for j in range(112) if correction[i][j])
    bad_correction[i][j] = 0
    result.append(rejects(lambda: check_columns(supports, bad_correction), 'missing_free_correction'))
    result.append(rejects(lambda: check_columns(supports, correction, False), 'lost_target_dirt'))
    result.append(rejects(lambda: equal_receipt(costs, [len(s) for s in supports]), 'singleton_label_undercharge_112'))
    result.append(rejects(lambda: equal_receipt(costs, [2] * 34), 'rank_two_per_channel_undercharge_68'))
    result.append(rejects(lambda: authenticate(CERT.read_bytes() + b' ', CERT_SHA, 'mutant'), 'changed_predecessor_bytes'))
    result.append(rejects(lambda: authenticate(b'wrong archive', ARCHIVE_SHA, 'mutant'), 'changed_archive_bytes'))
    result.append(rejects(lambda: authenticate(b'wrong labels', MEMBER_SHA, 'mutant'), 'changed_label_bytes'))
    result.append(rejects(lambda: equal_receipt({'rank': 1}, {'rank': True}), 'typed_receipt'))
    return result


def verify():
    labels, cert = load_inputs()
    bases, owner, orth = geometry(labels, cert['pairs'])
    supports = cert['supports']
    K, forced = scalar_fit(supports, owner, orth)
    clique = cert['clique_planes']
    need(len(clique) == len(set(clique)) == 17 and all(type(p) is int and 0 <= p < 56 for p in clique), '17-plane witness')
    need(all(not orth[a][b] for a in clique for b in clique), 'pairwise nonorthogonal clique')
    ports = [p for n in clique for p in cert['pairs'][n]]
    need(all(K[i][j] == int(i == j) for i in ports for j in ports), 'forced I34 minor')
    costs, line_costs = invoice(labels, supports, bases, owner)
    correction = [[int(i == j) - K[i][j] for j in range(112)] for i in range(112)]
    need(all(not correction[i][j] or orth[owner[i]][owner[j]] for i in range(112) for j in range(112)), 'only free corrections')
    check_columns(supports, correction)
    expanded_identity(K, bases, owner)
    classes = Counter(tuple(sorted(owner[i] for i in s)) for s in supports)
    need(len(classes) == 17 and set(classes.values()) == {2}, 'two channels per orthogonal class')
    W, N, m = 896, 9, 73
    C = sum(costs)
    mass = (m - 2) * W + C * N
    moment0 = Fraction(mass, m * W)
    need(C == 224 and moment0 == Fraction(293, 292), 'zero-saving screen')
    return {
        'schema_version': 1,
        'predecessor_head': '1d46df8b5aeac49d165cae58c1dd1036666bb789',
        'certificate_sha256': CERT_SHA,
        'ports': 112, 'planes': 56, 'scalar_channels': 34,
        'required_scalar_mask_entries': forced,
        'exact_scalar_fitting_rank': 34,
        'forced_identity_minor': 34,
        'expanded_binary_identity_rank': 224,
        'scalar_dirty_input_columns': 224,
        'free_endpoint_correction_entries': sum(bool(v) for row in correction for v in row),
        'orthogonal_class_size_histogram': dict(sorted(Counter(map(len, classes)).items())),
        'support_size_histogram': dict(sorted(Counter(map(len, supports)).items())),
        'channel_pairing_ranks': costs,
        'pairing_rank_histogram': dict(sorted(Counter(costs).items())),
        'total_copy_tariff': C,
        'incorrect_singleton_label_tariff': sum(line_costs),
        'incorrect_rank_two_per_channel_tariff': 2 * len(supports),
        'coverage_screen': {'W': W, 'N': N, 'm': m, 'unpaid': 2,
                            'paid_mass': mass, 'capacity': m * W,
                            'zero_saving_moment': str(moment0),
                            'deficit_per_call': str(Fraction(2 * W, N) - C)},
        'rejection_controls': controls(labels, cert, owner, orth, costs, correction),
        'scope': 'Exact full-port one-total tariff and conditional coverage screen; no native word or supplier admission.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write a new receipt; existing paths are refused')
    args = parser.parse_args()
    receipt = verify()
    if args.output:
        with args.output.open('x', encoding='utf-8') as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write('\n')
    else:
        equal_receipt(receipt, json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8')))
    print('PASS_PAIRED_PLANE_RANK34_COPY_INVOICE channels=34 ranks=4:8,6:8,8:18 C=224 moment0=293/292')


if __name__ == '__main__':
    main()
