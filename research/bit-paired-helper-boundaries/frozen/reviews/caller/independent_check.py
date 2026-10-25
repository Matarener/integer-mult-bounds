#!/usr/bin/env python3
"""Independent exact B10 caller/owner certificates; no producer imports.

Apache-2.0. Substantial OpenAI Codex assistance. The arbitrary-cover and
all-bank proofs, and their cost/interface hypotheses, are in PROOF-CALLER.md.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from math import gcd
from pathlib import Path
import argparse
import gzip
import json

BASE = Path('/Users/ross/git/math')
LANE = BASE / '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z'
RAW = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/words/r438-t154.json.gz'
HYBRID = LANE / 'bit-native-caller/HYBRID-BUDGET.json'
OWNERS = LANE / 'budgets/PAIRED-HELPER-OWNERS.json'
PINS = {
    RAW: 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022',
    HYBRID: 'b1e743fcc6e7b5482dafeb131270715d70621103f42b46972b13800082d4da84',
    OWNERS: '1d729716c459ae62a89d114a4ab58c03e2326d1770093f58b2db0b6379601cb9',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def rank_integer(rows):
    """Exact rational rank by fraction-free row reduction and gcd content."""
    a = [list(row) for row in rows if any(row)]
    if not a:
        return 0
    rank = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for i in range(rank + 1, len(a)):
            if a[i][col]:
                x, y = a[rank][col], a[i][col]
                a[i] = [x * u - y * v for u, v in zip(a[i], a[rank])]
                content = 0
                for entry in a[i]:
                    content = gcd(content, entry)
                if content:
                    a[i] = [entry // content for entry in a[i]]
        rank += 1
        if rank == len(a):
            break
    return rank


def geometry(raw, saved):
    lines = raw['lines']
    require(lines[:8] == [[2 * (i == j) for j in range(8)] for i in range(8)], 'literal coordinate prefix')
    frames = [[lines[i] for i in frame] for frame in raw['frames']]
    # Reverse chronology finds each retained total's actual last A-phase cut.
    cuts = {}
    for frame, destination, sources in reversed(raw['A']):
        for helper in raw['ret']:
            if helper not in cuts and helper in [destination, *sources]:
                cuts[helper] = frame
    for helper in raw['ret']:
        cuts.setdefault(helper, raw['start'][helper])
    census = []
    for dim in range(1, 8):
        remaining = []
        for port in range(111):
            frame = frames[raw['final'][111 + port]]
            # Quotient by E: dim(K+E) = dim(E)+rank(project_(E-perp) K).
            if dim + rank_integer([row[dim:] for row in frame]) == rank_integer(frame):
                remaining.append(port)
        copy = [rank_integer([row[dim:] for row in frames[cuts[h]]]) for h in raw['ret']]
        census.append({'E_axes': list(range(dim)), 'target_FULL_lifts': 111 - len(remaining),
                       'remaining_cap_ports': len(remaining), 'nine_COPY_ranks': copy,
                       'private_query_rank': sum(copy), 'D_per_call_upper': len(remaining) - sum(copy)})
    require(census == saved['coordinate_planes'], 'every leading-coordinate cap and COPY tariff')
    require(all(row['D_per_call_upper'] <= 0 for row in census), 'fixed uniform common-prefix necessary budget')
    # Remove an actual COPY or FULL lift from the rank-one prefix invoice.
    first = census[0]
    omit_copy = first['remaining_cap_ports'] - sum(first['nine_COPY_ranks'][1:])
    omit_lift = 111 - (first['target_FULL_lifts'] - 1) - first['private_query_rank']
    require(omit_copy == 6 and omit_lift == 1, 'actual tariff omissions detected')
    return {'retained_total_cut_frames': {str(h): cuts[h] for h in raw['ret']},
            'coordinate_planes': census, 'omission_controls': {'omit_first_COPY_D_per_call': omit_copy,
                                                            'omit_one_FULL_lift_D_per_call': omit_lift}}


def add(a, b):
    return [[x ^ y for x, y in zip(row, other)] for row, other in zip(a, b)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) % 2 for col in zip(*b)] for row in a]


def block(a, b, c, d):
    return [a[i] + b[i] for i in range(2)] + [c[i] + d[i] for i in range(2)]


def binary_rank(rows):
    packed = [sum(v << j for j, v in enumerate(row)) for row in rows]
    pivots = {}
    for value in packed:
        while value:
            p = value.bit_length() - 1
            if p in pivots:
                value ^= pivots[p]
            else:
                pivots[p] = value
                break
    return len(pivots)


def seeds(saved):
    I, Z, N = [[1, 0], [0, 1]], [[0, 0], [0, 0]], [[0, 1], [1, 0]]
    d = add(I, N)
    images = [Z, I, N, d]
    require(len({tuple(map(tuple, a)) for a in images}) == 4, 'faithful representation of all four ring elements')
    require(multiply(N, N) == I and multiply(d, d) == Z and d != Z, 'nontrivial square-zero d')
    operations = {'cap_F': block(I, Z, N, I), 'cap_B': block(I, N, Z, I),
                  'FULL_F': block(I, Z, I, N), 'FULL_B': block(N, I, Z, I)}
    operations['cap_FBF'] = multiply(multiply(operations['cap_F'], operations['cap_B']), operations['cap_F'])
    operations['FULL_FBF'] = multiply(multiply(operations['FULL_F'], operations['FULL_B']), operations['FULL_F'])
    operations['FULL_FBF_squared'] = multiply(operations['FULL_FBF'], operations['FULL_FBF'])
    def decode(matrix):
        return [[images.index([row[2*j:2*j+2] for row in matrix[2*i:2*i+2]]) for j in range(2)] for i in range(2)]
    decoded = {name: decode(matrix) for name, matrix in operations.items()}
    require(all(saved[name] == value for name, value in decoded.items()), 'complete faithful binary seed identities')
    normalized = {}
    # A is the N=I constant matrix; C is the coefficient of d=N+I.
    constants = {'cap_F': [[1, 0], [1, 1]], 'FULL_F': [[1, 0], [1, 1]],
                 'cap_B': [[1, 1], [0, 1]], 'FULL_B': [[1, 1], [0, 1]]}
    derivatives = {'cap_F': [[0, 0], [1, 0]], 'FULL_F': [[0, 0], [0, 1]],
                   'cap_B': [[0, 1], [0, 0]], 'FULL_B': [[1, 0], [0, 0]]}
    for name in constants:
        A, C = constants[name], derivatives[name]
        R = multiply(A, C)  # These four constant matrices are involutions.
        require(multiply(A, A) == I and binary_rank(R) == 1, 'normalized derivative rank one')
        rebuilt = block(*[add(I if A[i][j] else Z, d if C[i][j] else Z)
                          for i, j in ((0, 0), (0, 1), (1, 0), (1, 1))])
        require(rebuilt == operations[name], 'all actual derivative coefficients')
        normalized[name] = R
    wrong_seed = multiply(operations['FULL_F'], operations['FULL_F'])
    require(wrong_seed != operations['FULL_FBF'], 'omitted middle hybrid call detected')
    return {'faithful_binary_N': N, 'faithful_binary_d': d, 'decoded_seed_matrices': decoded,
            'normalized_rank_one_derivatives': normalized, 'omitted_middle_B_changes_seed': True}


M = 36
FULL_MASK = (1 << M) - 1


def swap_mask(vector, mask):
    change = (vector ^ (vector >> M)) & mask
    return vector ^ change ^ (change << M)


def mask_axes(axes):
    return sum(1 << a for a in axes)


def fixture(ignore_entry=False, omit_last=False, alias=False):
    owners = [[1 << i for i in range(2 * M)] for _ in range(6)]
    events = []
    for invocation in range(6):
        used = set()
        for role in range(5 if omit_last else 6):
            slot = 0 if alias and role == 1 else role
            owner = (invocation - slot) % 6
            require(owner not in used, 'same-call physical family collision')
            used.add(owner)
            residual = {(6 * slot + j) % M for j in range(6)}
            entrance = {(6 * slot + j) % M for j in (6, 7)}
            require(not residual & entrance, 'eight distinct local footprint axes')
            actual_E = mask_axes({(a + 6 * owner) % M for a in entrance})
            actual_U = mask_axes({(a + 6 * owner) % M for a in residual | entrance})
            # Execute each paired endpoint directly on every binary ADDRESS
            # coordinate column, without composing permutation tables.
            for col, value in enumerate(owners[owner]):
                if not ignore_entry:
                    value = swap_mask(value, actual_E)
                owners[owner][col] = swap_mask(value, actual_U)
            events.append({'invocation': invocation, 'role': role, 'owner': owner,
                           'slot_axes': sorted(residual), 'entrance_axes': sorted(entrance)})
    return owners, events


def owner_certificate(saved):
    actual, events = fixture()
    expected = [swap_mask(1 << i, FULL_MASK) for i in range(72)]
    require(actual == [expected] * 6, '432 independent ADDRESS columns reach full swap')
    require(events == saved['events'], 'all 36 exact owner assignments')
    for j in range(6):
        require(set(events[j]['entrance_axes']) <= set(events[(j + 1) % 6]['slot_axes']), 'every local spectator is in next residual block')
    bad_entry = sum(a != b for owner in fixture(ignore_entry=True)[0] for a, b in zip(owner, expected))
    bad_role = sum(a != b for owner in fixture(omit_last=True)[0] for a, b in zip(owner, expected))
    require(bad_entry > 0 and bad_role > 0, 'omitted paired entrance and role change actual endpoint')
    try:
        fixture(alias=True)
    except ValueError:
        alias_rejected = True
    else:
        alias_rejected = False
    require(alias_rejected, 'actual duplicated adapter rejected')
    # Actual E2={0,1}, U={0,...,7} is first canonically permuted so that
    # its residual is {0,...,5} and its two spectators are {6,7}.
    initial_chart = [6, 7, 0, 1, 2, 3, 4, 5] + list(range(8, 36))
    require(set(initial_chart) == set(range(36)), 'canonical E2 embedding permutation')
    require({initial_chart[i] for i in range(2, 8)} == set(range(6)), 'actual E2 residual chart')
    # Check centrality for all six diagonal charts on all 72 columns.
    def chart(index, shift, one_half=False):
        half, axis = divmod(index, M)
        return half * M + ((axis + shift) % M if not one_half or half == 0 else axis)
    for g in range(6):
        for col in range(72):
            require(chart((col + M) % 72, 6 * g) == (chart(col, 6 * g) + M) % 72, 'diagonal chart centralizes full swap')
    require(any(chart((col + M) % 72, 6, True) != (chart(col, 6, True) + M) % 72 for col in range(72)), 'non-diagonal chart centrality defect')
    inventory = {}
    for width, per_replica, slots in ((6, 318, 6), (8, 111, 4)):
        banks = defaultdict(list)
        same_call = defaultdict(set)
        for replica in range(12):
            for helper in range(per_replica):
                bank, slot = divmod(replica * per_replica + helper, slots)
                require(slot not in same_call[(replica, bank)], 'same-call adapter distinctness in 12-replica fill')
                same_call[(replica, bank)].add(slot)
                banks[bank].append((replica, helper, slot))
        require(all(sorted(x[2] for x in roles) == list(range(slots)) for roles in banks.values()), 'every whole bank receives every role exactly once')
        inventory[str(width)] = {'roles': 12 * per_replica, 'banks': len(banks), 'slots': slots}
    require(inventory['6']['banks'] == 636 and inventory['8']['banks'] == 333, 'integral bank counts')
    stock = Fraction(318, 6) + Fraction(111, 4)
    mass, pad = 318 * 6 + 111 * 8, 111
    require(stock == Fraction(323, 4) and mass + pad == 36 * stock, 'helper-only exact complete mass')
    require(12 * mass + 333 * 4 == 36 * (636 + 333), 'all replicated bank padding paid')
    expected_inventory = {'replicas': 12, 'width6_banks': 636, 'width8_banks': 333,
                          'stock_per_call': str(stock), 'padding_per_call': {'4': str(Fraction(111, 4))},
                          'local_helper_rank_mass': mass, 'padding_rank_mass_per_call': pad}
    require(saved['E2_helper_inventory_only'] == expected_inventory, 'complete retained helper invoice')
    omitted_padding = sum(swap_mask(1 << col, (1 << 32) - 1) != expected[col] for col in range(72))
    require(omitted_padding == 8, 'actual unpaid width-eight-bank padding leaves wrong endpoint')
    return {'m': M, 'cover_invocations': 6, 'physical_owners': 6, 'checked_columns': 432,
            'events': events, 'canonical_E2_chart': initial_chart,
            'twelve_replica_inventory': inventory, 'stock_per_replica': str(stock),
            'local_helper_mass': mass, 'padding_mass_per_replica': pad,
            'padding_query_rank': 4, 'padding_query_count_twelve_replicas': 333,
            'controls': {'ignored_entrance_wrong_columns': bad_entry, 'omitted_role_wrong_columns': bad_role,
                         'same_call_alias_rejected': alias_rejected, 'non_diagonal_chart_fails_centrality': True,
                         'omitted_rank4_padding_wrong_columns': omitted_padding}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    for path, digest in PINS.items():
        require(sha256(path.read_bytes()).hexdigest() == digest, str(path))
    raw = json.loads(gzip.decompress(RAW.read_bytes()))
    hybrid = json.loads(HYBRID.read_bytes())
    owner = json.loads(OWNERS.read_bytes())
    result = {'status': 'PASS_INDEPENDENT_B10_CALLER_OWNER', 'no_new_kappa': True,
              'sources': {str(p): h for p, h in PINS.items()},
              'geometry': geometry(raw, hybrid), 'hybrid': seeds(hybrid),
              'dedicated_owners': owner_certificate(owner),
              'written_proofs': 'PROOF-CALLER.md: arbitrary-dirt interpretation, arbitrary finite cover assignment, all-bank rank bound, conditional uniform-prefix deficit.',
              'limits': 'No native supplier replay, mixed-E/port-mixing theorem, public-window owner fill, free rational-GL compiler, tape theorem or new kappa.'}
    content = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(content)
    else:
        print(content, end='')


if __name__ == '__main__':
    main()
