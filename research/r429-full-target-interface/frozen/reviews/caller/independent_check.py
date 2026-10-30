#!/usr/bin/env python3
"""Independent matrix, fresh-factor and cost audit of the fixed BIT callers.

No historical producer imports. Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/Users/ross/git/math')
RUN = BASE / '.research-automation/runs/kappa-major-20261018T1330Z'
STAR = RUN / 'shared-helper-algebra/BIT-SEEDED-STAR.json'
FULL = RUN / 'bit-endpoint/BIT-FULL-COMPENSATION.json'
PRESSURE = BASE / '.research-automation/runs/kappa-changed-endpoints-20261019T0153Z/budgets/SEEDED-STAR-PRESSURE.json'
SOURCE = BASE / 'integer-mult-bounds/research/bit-r438-transport-rehost/verify_rehost.py'
WORD = SOURCE.parent / 'words/r438-t154.json.gz'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def identity(n=16):
    return [1 << i for i in range(n)]


def mm(a, b):
    result = []
    for row in a:
        value = 0
        for j, brow in enumerate(b):
            if row >> j & 1:
                value ^= brow
        result.append(value)
    return result


def event_matrix(kind, i, j):
    # Faithful regular representation: 1 -> I2, N -> [[0,1],[1,0]].
    a = identity()
    if kind in ('old_F', 'old_B', 'CNOT'):
        src, dst = (j, i) if kind == 'old_B' else (i, j)
        shift = 0 if kind == 'CNOT' else 1
        for bit in range(2):
            a[2 * dst + bit] ^= 1 << (2 * src + (bit ^ shift))
    elif kind == 'exchange':
        for bit in range(2):
            a[2 * i + bit], a[2 * j + bit] = a[2 * j + bit], a[2 * i + bit]
    elif kind in ('new_F', 'new_F_inverse'):
        for bit in range(2):
            source_bit = bit ^ (kind == 'new_F_inverse')
            a[2 * j + bit] = (1 << (2 * j + (bit ^ 1))) ^ (1 << (2 * i + source_bit))
    else:
        raise ValueError(kind)
    return a


def inverse_kind(kind):
    return {'new_F': 'new_F_inverse', 'new_F_inverse': 'new_F'}.get(kind, kind)


def expand_ring_rows(rows):
    # The frozen receipt encodes a+bN as a+2*b. Convert only for comparison.
    out = [0] * 16
    for i, row in enumerate(rows):
        for j, coefficient in enumerate(row):
            need(coefficient in range(4), 'ring coefficient range')
            for bit in range(2):
                if coefficient & 1:
                    out[2 * i + bit] ^= 1 << (2 * j + bit)
                if coefficient & 2:
                    out[2 * i + bit] ^= 1 << (2 * j + (bit ^ 1))
    return out


def difference_witness(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        delta = x ^ y
        if delta:
            return {'output_binary_coordinate': i,
                    'input_binary_coordinate': (delta & -delta).bit_length() - 1,
                    'difference_row_mask': delta}
    raise ValueError('missing defect')


ZERO = (0,) * 9


def nscale(row):
    return {(bank, n ^ 1, powers) for bank, n, powers in row}


def gscale(row, stages, sign=1):
    out = set()
    for bank, n, powers in row:
        powers = list(powers)
        for s in stages:
            powers[s] += sign
        out.add((bank, n, tuple(powers)))
    return out


def polynomial_event(rows, kind, i, j):
    rows = [set(row) for row in rows]
    if kind == 'old_F':
        rows[j] ^= nscale(rows[i])
    elif kind == 'old_B':
        rows[i] ^= nscale(rows[j])
    elif kind == 'CNOT':
        rows[j] ^= rows[i]
    elif kind == 'exchange':
        rows[i], rows[j] = rows[j], rows[i]
    elif kind == 'new_F':
        rows[j] = rows[i] ^ nscale(rows[j])
    elif kind == 'new_F_inverse':
        rows[j] = nscale(rows[i] ^ rows[j])
    else:
        raise ValueError(kind)
    return rows


def lower_log(x):
    z = (x - 1) / (x + 1)
    return 2 * z * (1 + z * z / 3)


def main():
    saved = json.loads(STAR.read_bytes())
    full = json.loads(FULL.read_bytes())
    pressure = json.loads(PRESSURE.read_bytes())
    hashes = {str(p): sha256(p.read_bytes()).hexdigest()
              for p in (STAR, FULL, PRESSURE, SOURCE, WORD)}
    need(hashes[str(FULL)] == '1ee06005d3b82ff592640d9aa4be2021b6de0a0b27fba5723aa06c36a6adbd20', 'full source pin')
    need(hashes[str(SOURCE)] == pressure['profile_source_sha256'] == '4774841de10a8386204519174c5e56eb14f5852b20058db38a65a1034eeba275', 'seed profile source pin')
    need(hashes[str(WORD)] == pressure['seed_word_sha256'] == 'a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022', 'seed word pin')
    sequence = [('old_F', 0, 1), ('old_B', 0, 1), ('old_F', 0, 1), ('exchange', 0, 1)]
    sequence += [('new_F', 0, j) for j in range(2, 8)]
    sequence += [('CNOT', 0, j) for j in range(7, 1, -1)]
    need(sequence == [(e['kind'], e['source'], e['target']) for e in saved['word']], 'literal sequence')
    total = identity()
    prefixes = []
    for kind, i, j in sequence:
        op = event_matrix(kind, i, j)
        inv = event_matrix(inverse_kind(kind), i, j)
        need(mm(inv, op) == mm(op, inv) == identity(), 'each exact event inverse')
        total = mm(op, total)
        prefixes.append(total)
    target = [1 << (i ^ 1) for i in range(16)]
    need(total == target, 'faithful 16 by 16 ring representation endpoint')
    need(prefixes == [expand_ring_rows(p) for p in saved['prefix_rows']], 'all saved prefixes')
    for kind, i, j in reversed(sequence):
        total = mm(event_matrix(inverse_kind(kind), i, j), total)
    need(total == identity(), 'literal reverse inverse')
    defects = {}
    for name, omitted in [('missing_seed_B', 1), ('missing_terminal_CNOT', len(sequence) - 1)]:
        bad = identity()
        for k, (kind, i, j) in enumerate(sequence):
            if k != omitted:
                bad = mm(event_matrix(kind, i, j), bad)
        defects[name] = difference_witness(bad, target)
    single = mm(event_matrix('CNOT', 0, 1), event_matrix('new_F', 0, 1))
    need(single[:4] == [1, 2, 8, 4], 'pure new F leaves raw source unchanged')

    # Explicit Laurent monomials in nine independent commuting Gs and N^2=1.
    rows = [{(i, 0, ZERO)} for i in range(8)]
    cursors = [0] * 8
    expanded = []
    idle_windows = [[] for _ in range(8)]
    active = [[] for _ in range(8)]
    stage = 0
    def fresh(bank, stages, idle):
        nonlocal rows
        if stages:
            rows[bank] = gscale(rows[bank], stages)
            expanded.append(('G', bank, tuple(stages)))
            if idle:
                idle_windows[bank].append(7 * len(stages))
    completed = False
    for kind, i, j in sequence:
        if kind in ('old_F', 'old_B', 'new_F'):
            for bank in (i, j):
                fresh(bank, tuple(range(cursors[bank], stage)), True)
                expected_powers = (1,) * stage + (0,) * (9 - stage)
                need(all(p == expected_powers for _, _, p in rows[bank]), 'matched fresh prefixes')
                active[bank].append(stage)
            rows = polynomial_event(rows, kind, i, j)
            expanded.append(('local', kind, i, j))
            for bank in (i, j):
                fresh(bank, (stage,), False)
                cursors[bank] = stage + 1
            stage += 1
        else:
            if kind == 'CNOT' and not completed:
                for bank in range(8):
                    fresh(bank, tuple(range(cursors[bank], 9)), True)
                completed = True
            rows = polynomial_event(rows, kind, i, j)
            expanded.append(('local', kind, i, j))
    need(rows == [{(i, 1, (1,) * 9)} for i in range(8)], 'full fresh-factor endpoint Gamma9 N I8')
    windows = [{'bank': i, 'active_stages': active[i], 'fresh_idle_query_ranks': idle_windows[i]}
               for i in range(8)]
    need(windows == saved['public_fresh_idle_windows'], 'actual changed idle windows')
    for event in reversed(expanded):
        if event[0] == 'G':
            rows[event[1]] = gscale(rows[event[1]], event[2], -1)
        else:
            _, kind, i, j = event
            rows = polynomial_event(rows, inverse_kind(kind), i, j)
    need(rows == [{(i, 0, ZERO)} for i in range(8)], 'full Laurent-word reverse inverse')

    nodes = ast.parse(SOURCE.read_bytes()).body
    candidates = [ast.literal_eval(n.value) for n in nodes if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'LOCAL_B' for t in n.targets)]
    need(len(candidates) == 1, 'one literal old seed profile')
    seed = candidates[0]
    need(seed == {1:1322, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:18}, 'old seed profile')
    mass = sum(r * c for r, c in seed.items())
    need(mass == 5121 and max(seed) == 7, 'old seed complete mass and maximum rank')
    new_mass = sum(int(r) * c for r, c in full['forward']['profile'].items())
    need(new_mass == 5097 == 15 * 111 + 8 * 429, 'new full-target mass')
    need(full['new_target_rank1_lifts'] == 111 and full['private_excess'] == 0, 'all target lifts and zero private excess')
    # Polynomial coefficients in L: local + untouched fresh - hosted helper mass.
    coefficients = {1: new_mass - 14 * 111 - 8 * 429, 2: 7 * 111}
    need(coefficients == {1: 111, 2: 777}, 'all-L direct polynomial equals111 L(1+7L)')
    width8_slots_per_port = sum(r // 8 for row in idle_windows for r in row)
    idle_mass = 111 * sum(r for row in idle_windows for r in row)
    helpers = 3 * 438 + 6 * 429
    complete_mass = 3 * mass + 6 * new_mass + idle_mass - 8 * helpers
    need(width8_slots_per_port == 42 and helpers == 3888, 'aggregate changed capacity')
    need(8 * 111 * 64 - complete_mass == 33, 'eight-bank optimistic D33 arithmetic')
    need(8 * 111 * 64 - (complete_mass + 6 * 3) == 15, 'historical private3 D15 arithmetic')
    lower = Q(3 * mass, 500) * lower_log(Q(22, 7))
    need(lower == Q(21108762, 609725) == Q(pressure['pressure_strict_lower']) > 33, 'exact all-L pressure witness')
    controls = {'two_seeds_lower': str(Q(2 * mass, 500) * lower_log(Q(22, 7))),
                'max_rank8_lower': str(Q(3 * mass, 500) * lower_log(Q(22, 8))),
                'D35_lower': str(lower)}
    need(Q(controls['two_seeds_lower']) < 33 and Q(controls['max_rank8_lower']) < 33 and lower < 35,
         'sensitivity controls lose this coarse certificate only')
    result = {'status': 'PASS_INDEPENDENT_B05_CALLER_ALGEBRA_AND_CONDITIONAL_PRESSURE',
              'scientific_pin': '20ecf2891d80b5acf18d980b2164fb44ea7faa90', 'source_sha256': hashes,
              'ring_method': 'Faithful regular representation N=2x2 swap;16x16 binary matrices',
              'events': len(sequence), 'matrix_prefixes_matched': len(prefixes),
              'formal_endpoint': 'Gamma9*N*I8', 'formal_literal_inverse': True,
              'fresh_method': 'Laurent monomials in9 independent commuting invertible Gs, N exponent modulo2',
              'expanded_events': len(expanded), 'defect_witnesses': defects,
              'public_fresh_idle_windows': windows, 'width8_slots_per_port': width8_slots_per_port,
              'aggregate_slots': 111 * width8_slots_per_port, 'helper_occurrences': helpers,
              'aggregate_capacity_is_not_owner_allocation': True,
              'old_seed_profile': seed, 'old_seed_mass': mass, 'new_full_mass': new_mass,
              'direct_mass_polynomial_in_L': coefficients, 'direct_deficit': 0,
              'false_deficit_if_target_lifts_omitted': '111*L',
              'eight_bank_ideal_complete_mass': complete_mass, 'eight_bank_parent_mass': 8 * 111 * 64,
              'old_private3_ideal_deficit': 15, 'new_zero_private_ideal_deficit': 33,
              'pressure_lower': str(lower), 'pressure_excess_over33': str(lower - 33),
              'sensitivity_witnesses': controls,
              'limits': ['Native interfaces at changed cuts remain premises.', 'No chronological owner allocation or rounded/physical compiler.', 'No positive supplier or new kappa.', 'Sensitivity controls do not prove a changed model passes.']}
    (HERE / 'INDEPENDENT-RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
    print('16 exact prefixes; fresh Gamma9 N endpoint and inverse;2 word defects; directD0; historicalD15/currentD33; pressure21108762/609725>33')


if __name__ == '__main__':
    main()
