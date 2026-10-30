#!/usr/bin/env python3
"""Independent finite certificates for the fixed B13 optimistic invoice.

Apache-2.0. Substantial OpenAI Codex assistance. Does not import the producer.
All-odd-L reasoning is in PROOF-ACCOUNTING.md; samples audit serialization only.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import isqrt
from pathlib import Path
import argparse
import gzip
import json

BASE = Path('/Users/ross/git/math')
RUN = BASE / '.research-automation/runs'
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
PRUNED = RUN / 'kappa-3605-successor-20261018T0940Z/major-frontier/root-pruned-code/BIT-PRUNED-WORD.json.gz'
SAVED = RUN / 'kappa-changed-endpoints-20261019T0153Z/coded-bit-boundary/KER-CODE-NATIVE-REJECTION.json'
PINS = {
    RAW: 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
    PRUNED: '1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870',
    SAVED: 'f01694055292f9897ca9e109fd026c8c9b26c8c5bb3723b51ef192be9c7411c1',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_gzip(path):
    require(sha256(path.read_bytes()).hexdigest() == PINS[path], str(path))
    return json.loads(gzip.decompress(path.read_bytes()))


def span(vectors):
    """Closure enumeration (at most 512 elements), without elimination."""
    result = {0}
    for v in vectors:
        result |= {x ^ v for x in result}
    return result


def reconstruct(raw, records):
    # Reverse adjoints, independent of the producer's 660-row forward replay.
    rows = []
    for output in raw['ret']:
        row = 1 << output
        for _, destination, sources in reversed(raw['D'] + raw['A']):
            if row >> destination & 1:
                for source in sources:
                    row ^= 1 << source
        rows.append(row & ((1 << 111) - 1))
    columns = [sum(((r >> p) & 1) << j for j, r in enumerate(rows))
               for p in range(111)]
    require(len(rows) == 9 and len(span(columns)) == 512, 'reader rank nine')
    bulk = [r for r in records if r[0] not in (2, 3)
            and r[-1] not in {21, 22, 23, 24, 31, 32, 33}]
    histogram = Counter(r[4] for r in bulk if r[0] == 0)
    counts = Counter(r[1] % 111 for r in bulk if r[0] == 0 and r[1] < 222)
    masses = Counter()
    for op, destination, _, _, rank, _ in bulk:
        if op == 0:
            masses[destination] += rank
    require(all(masses[p] == 7 for p in range(222)), 'each native public path has mass seven')
    require(all(masses[p] == 8 for p in range(222, 651)), 'each of 429 helper paths has mass eight')
    require(set(masses) == set(range(651)), 'complete active-field coverage')
    require(histogram == {1: 1295, 2: 1342, 3: 79, 4: 44, 5: 93, 6: 11, 7: 9}, 'bulk histogram')
    return rows, columns, bulk, histogram, counts


def basis_certificate(columns, counts, saved):
    selected = saved['dependent_ports']
    require(len(selected) == len(set(selected)) == 9, 'nine distinct selected ports')
    # Exhaust the 512 combinations of the proposed basis to invert its map.
    inverse = {}
    for selector in range(512):
        image = 0
        for i, p in enumerate(selected):
            if selector >> i & 1:
                image ^= columns[p]
        require(image not in inverse, 'selected columns independent')
        inverse[image] = selector
    # Threshold-rank lower bound proves global weight optimality. For each w,
    # any basis has at most rank({columns of weight <= w}) elements <= w.
    thresholds = []
    previous_rank = 0
    minimum = 0
    for w in sorted(set(counts.values())):
        cardinality = len(span(columns[p] for p in range(111) if counts[p] <= w))
        rank = cardinality.bit_length() - 1
        require(cardinality == 1 << rank, 'threshold is a binary subspace')
        minimum += w * (rank - previous_rank)
        thresholds.append({'weight': w, 'rank_at_most_weight': rank})
        previous_rank = rank
    require(sum(counts[p] for p in selected) == minimum == 44, 'global minimum MOVE-event count')
    # Fundamental-circuit exchange inequalities supply a second certificate.
    exchange_checks = 0
    for p in range(111):
        if p not in selected:
            for i, b in enumerate(selected):
                if inverse[columns[p]] >> i & 1:
                    require(counts[b] <= counts[p], 'no cheaper single exchange')
                    exchange_checks += 1
    free = [p for p in range(111) if p not in selected]
    encoder = [0] * 111
    for j, p in enumerate(free):
        encoder[p] = 1 << j
        coefficients = inverse[columns[p]]
        for i, b in enumerate(selected):
            if coefficients >> i & 1:
                encoder[b] |= 1 << j
    require(encoder == saved['encoder_rows_102'] and free == saved['public_ports'], 'all encoder coefficients')
    weights = [encoder[p].bit_count() for p in selected]
    require(sum(weights) == 470, 'parity ADD count')
    # Actual gate omission: delete a one in the generated encoder. The image
    # of its affected public coordinate becomes exactly the nonzero column R_p.
    bad = encoder[:]
    bad[selected[0]] ^= bad[selected[0]] & -bad[selected[0]]
    def residual(code):
        out = [0] * 9
        for p, coefficients in enumerate(code):
            for i in range(9):
                if columns[p] >> i & 1:
                    out[i] ^= coefficients
        return out
    require(not any(residual(encoder)), 'complete RE=0')
    require(any(residual(bad)), 'actual parity ADD omission rejected')
    return {'ports': selected, 'event_count_minimum': minimum,
            'thresholds': thresholds, 'fundamental_exchange_checks': exchange_checks,
            'parity_row_weights': weights, 'ADDs_per_bank': sum(weights),
            'ADDs_prepare_unprepare_both_banks': 4 * sum(weights),
            'actual_parity_ADD_omission_residual': residual(bad)}


def invoice(histogram, L, omit_parity=False, extra_public_bank=False):
    require(isinstance(L, int) and L >= 3 and L % 2 == 1, 'odd L>=3 only')
    m = 7 * L + 1
    B = (L - 1) // 2
    cap = isqrt((m * m - 1) // 2)
    children = Counter({r: Fraction(L * n) for r, n in histogram.items()})
    if omit_parity:
        # Mutation supplied by actual selected-port MOVE histogram, not a
        # free numerical subtraction from the claimed final deficit.
        for r, n in OMITTED_PARITY.items():
            children[r] -= L * n
    idle = Counter({14 * j: 2 for j in range(1, B)})
    idle[7] += B - 1
    def add_partition(total, multiplicity):
        full, remainder = divmod(total, cap)
        children[cap] += multiplicity * full
        if remainder:
            children[remainder] += multiplicity
    for r, n in idle.items():
        add_partition(r, 204 * n)
    if extra_public_bank:
        # Changed endpoint allowance, with its added idle interval charged:
        # a hypothetical extra bank contributes stock 102 and idle mass
        # 102*(m-1), hence net endpoint credit 102. This is a sensitivity
        # control only, not a construction of a legal extra-bank schedule.
        add_partition(m - 1, 102)
    q, pad = divmod(m, 8)
    helper_stock = Fraction(429 * L, q)
    add_partition(pad, helper_stock)
    children = {r: n for r, n in sorted(children.items()) if n}
    require(all(0 < r < m and n > 0 for r, n in children.items()), 'all children positive and strictly contracting')
    stock = 102 * (L - 1 + int(extra_public_bank)) + helper_stock
    mass = sum(r * n for r, n in children.items())
    deficit = m * stock - mass
    return {'L': L, 'm': m, 'public_fields': 102 * (L - 1 + int(extra_public_bank)),
            'public_parity_cells_per_active_call': 18,
            'helper_stock_relaxation': str(helper_stock), 'W': str(stock),
            'H': {str(r): str(n) for r, n in children.items()},
            'rank_mass': str(mass), 'D': str(deficit),
            'private_parity_native_mass_per_call': 126}


OMITTED_PARITY = Counter()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    raw = read_gzip(RAW)
    pruned = read_gzip(PRUNED)
    require(sha256(SAVED.read_bytes()).hexdigest() == PINS[SAVED], 'saved source receipt pin')
    saved = json.loads(SAVED.read_bytes())
    rows, columns, bulk, histogram, counts = reconstruct(raw, pruned['records'])
    basis = basis_certificate(columns, counts, saved)
    selected = set(basis['ports'])
    OMITTED_PARITY.update(r[4] for r in bulk if r[0] == 0 and r[1] < 222 and r[1] % 111 in selected)
    require(sum(r * n for r, n in OMITTED_PARITY.items()) == 126, '18 actual private paths')
    checks = []
    for old in saved['optimistic_complete_invoices']:
        new = invoice(histogram, old['L'])
        require(all(new[k] == old[k] for k in new), 'every serialized invoice coefficient')
        require(Fraction(new['D']) == -24 * old['L'] - 102, 'deficit identity at serialized example')
        checks.append(new)
    normal = invoice(histogram, 3)
    omitted = invoice(histogram, 3, omit_parity=True)
    endpoint = invoice(histogram, 3, extra_public_bank=True)
    require(normal['D'] == '-174' and omitted['D'] == '204' and endpoint['D'] == '-72', 'controls detect actual invoice changes')
    rejected = []
    for invalid in (1, 2, 4, 0, -3):
        try:
            invoice(histogram, invalid)
        except ValueError:
            rejected.append(invalid)
    require(rejected == [1, 2, 4, 0, -3], 'invalid domains rejected')
    output = {'status': 'PASS_INDEPENDENT_B13_ACCOUNTING', 'no_new_kappa': True,
              'sources': {str(p): sha256(p.read_bytes()).hexdigest() for p in (RAW, PRUNED, SAVED)},
              'reader_rows': rows, 'bulk_histogram': dict(sorted(histogram.items())),
              'basis_and_encoder': basis, 'actual_private_MOVE_histogram': dict(sorted(OMITTED_PARITY.items())),
              'invoice_examples': checks,
              'controls': {'normal_L3_D': normal['D'], 'omit_actual_18_parity_paths_L3_D': omitted['D'],
                           'extra_102_endpoint_credit_L3_D': endpoint['D'], 'invalid_L_rejected': rejected},
              'all_parameter_proof': 'PROOF-ACCOUNTING.md: odd L>=3; D=-24L-102; every a>0 fails the fixed complete optimistic moment.',
              'limits': 'No minimum parity-ADD claim, native code admission, integral owner schedule, positive supplier or new kappa.'}
    data = json.dumps(output, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(data)
    else:
        print(data, end='')


if __name__ == '__main__':
    main()
