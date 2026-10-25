#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact pooled T16 integer optimum near its maximal feasible moment root.

Nick Petalas. Dual/inventory lineage: Ali Romman, Hanson Sun, Rohan Arun.
Discovery used HiGHS; replay uses only integer and Fraction arithmetic.
"""
import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTHS = (4, 5, 7, 8, 9)
CAPS = (8, 16, 32, 48)
INVENTORY = (10752, 7168, 7168, 7168, 8064, 4608, 4320, 17568, 34560)
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
IDLE = {1: 2431, 17: 1, 48: 4887}
EXPONENT_BITS = 160
FRACTION_BITS = 256
OPTIMALITY_WINDOW = (Q(167689, 10**8), Q(167690, 10**8))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pinned_inputs():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    data = {}
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source drift: ' + row['path'])
        if row['path'].endswith('.json'):
            data[row['path']] = json.loads(raw)
    return data


def source_inventory(data):
    prefix = 'research/complex-t16-rare-pattern-exchanges/data/'
    plan, spec = (data[prefix + name] for name in ('PLAN.json', 'SPEC.json'))
    manifest = data['research/community-frontier1094-audit/SELECTED-SOURCE.json']['files']
    for name in ('PLAN.json', 'SPEC.json'):
        raw = (ROOT / (prefix + name)).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == manifest[prefix + name], 'selected binding')
    need(plan['M'] == 73 and plan['live'] == 14336, 'supplier normalization')
    need(plan['T'] == 16 and plan['L'] == 9, 'T16 template')
    ports = len(plan['provider_registry']['gauge44']['ports'])
    need(ports == 112 and len(plan['windows']) == 288, 'bin source')
    bins, widths, calls = Counter(), Counter(), set()
    for capacity, _times in plan['windows'].values():
        need(capacity in CAPS, 'capacity alphabet')
        bins[capacity] += ports
    provider = spec['providers']['gauge44']
    per_call = Counter({int(w): n for w, n in provider['inventory'].items()})
    for row in plan['per_call_widths']:
        call = row['stage'], row['replica']
        need(call not in calls, 'duplicate call')
        calls.add(call)
        need(Counter(row['widths']) == per_call, 'call width inventory')
        widths.update(row['widths'])
    need(calls == set(product(range(9), range(16))), 'complete call set')
    need(tuple(bins[c] for c in CAPS) + tuple(widths[w] for w in WIDTHS) == INVENTORY,
         'fixed integer inventories')
    need({int(r): n for r, n in provider['expected_profile'].items()} == LOCAL,
         'all paid local children')
    previous = data['research/selected-t16-pattern-dual/RESULT.json']
    need(previous['idle_mass'] == 237024 and previous['calls'] == 144, 'predecessor context')
    return INVENTORY


def patterns(cert):
    constants = cert['fractional_dual_constant']
    powers = cert['fractional_dual_power48']
    need(len(constants) == len(powers) == 9, 'dual shape')
    need(all(type(n) is int for n in constants + powers), 'integer dual numerators')
    rows = []
    for index, capacity in enumerate(CAPS):
        for counts in product(*(range(capacity // width + 1) for width in WIDTHS)):
            residual = capacity - sum(n * w for n, w in zip(counts, WIDTHS))
            if residual < 0:
                continue
            A = constants[index] + sum(n * v for n, v in zip(counts, constants[4:]))
            B = powers[index] + sum(n * v for n, v in zip(counts, powers[4:]))
            need(A + 48 * B == 37 * residual, 'dual rank-mass endpoint')
            rows.append((capacity, counts, residual, A, B))
    need(len(rows) == 1163, 'complete pattern enumeration')
    return rows


def add_terms(*expressions):
    total = Counter()
    for expression, sign in expressions:
        for rank, coefficient in expression.items():
            total[rank] += sign * coefficient
    return {rank: coefficient for rank, coefficient in total.items() if coefficient}


def edge_terms(row):
    _capacity, _counts, residual, A, B = row
    return add_terms(({residual: 37} if residual else {}, 1), ({1: A, 48: B}, -1))


def potentials(cert, rows):
    paths = cert['residue_paths']
    need(len(paths) == 37 and paths[0] == [], 'potential origin')
    result = []
    for target, path in enumerate(paths):
        need(isinstance(path, list) and len(path) <= 36, 'simple residue path bound')
        total, residue = {}, 0
        for index in path:
            need(type(index) is int and 0 <= index < len(rows), 'pattern index')
            total = add_terms((total, 1), (edge_terms(rows[index]), 1))
            residue = (residue + rows[index][4]) % 37
        need(residue == target, 'path destination')
        result.append(total)
    return result


def power_interval(rank, exponent):
    """Directed binary-root products enclosing a rational-exponent grid."""
    need(type(rank) is int and 0 <= rank <= 73 and 0 < exponent <= 1, 'power domain')
    if rank in (0, 1) or exponent == 1:
        return Q(rank), Q(rank)
    scale, denominator = 1 << FRACTION_BITS, 1 << EXPONENT_BITS
    low_index = exponent.numerator * denominator // exponent.denominator
    high_index = -(-exponent.numerator * denominator // exponent.denominator)
    lower = upper = rank * scale
    roots = []
    for _ in range(EXPONENT_BITS):
        lower = isqrt(lower * scale)
        squared = upper * scale
        upper = isqrt(squared)
        upper += upper * upper != squared
        roots.append((lower, upper))
    outputs = []
    for index in (low_index, high_index):
        if index == denominator:
            outputs.append((rank * scale, rank * scale))
            continue
        left = right = scale
        for bit, (lo, hi) in enumerate(roots, 1):
            if index & (1 << (EXPONENT_BITS - bit)):
                left = left * lo // scale
                right = (right * hi + scale - 1) // scale
        outputs.append((left, right))
    return Q(outputs[0][0], scale), Q(outputs[1][1], scale)


def interval(terms, powers):
    lower = upper = Q(0)
    for rank, coefficient in terms.items():
        lo, hi = powers[rank]
        lower += coefficient * (lo if coefficient >= 0 else hi)
        upper += coefficient * (hi if coefficient >= 0 else lo)
    return lower, upper


def check_potentials(rows, values, powers):
    strict = symbolic = 0
    least = None
    for residue in range(37):
        for row in rows:
            destination = (residue + row[4]) % 37
            slack = add_terms((values[residue], 1), (edge_terms(row), 1),
                              (values[destination], -1))
            if not slack:
                symbolic += 1
                continue
            gap = interval(slack, powers)[0]
            need(gap > 0, 'residue potential inequality')
            strict += 1
            least = gap if least is None else min(least, gap)
    need(symbolic + strict == 37 * 1163, 'all directed edges')
    return {'symbolic_edges': symbolic, 'strict_edges': strict,
            'minimum_strict_slack': str(least)}


def check_witness(cert, rhs):
    used = [0] * 9
    idle = Counter()
    need(len(cert['integer_patterns']) <= 1163, 'witness size')
    for row in cert['integer_patterns']:
        capacity, counts, count = row['capacity'], row['counts'], row['multiplicity']
        need(capacity in CAPS and type(count) is int and count > 0, 'integer multiplicity')
        need(len(counts) == 5 and all(type(n) is int and n >= 0 for n in counts),
             'integer pattern')
        residual = capacity - sum(n * w for n, w in zip(counts, WIDTHS))
        need(residual >= 0, 'pattern capacity')
        column = [int(capacity == c) for c in CAPS] + counts
        used = [x + count * y for x, y in zip(used, column)]
        if residual:
            idle[residual] += count
    need(tuple(used) == tuple(rhs), 'integer inventory attainment')
    need(dict(idle) == IDLE, 'attaining idle profile')
    need(sum(r * n for r, n in idle.items()) == 237024, 'idle rank mass')
    return dict(idle)


def complete_terms(idle):
    profile = Counter({r: 144 * n for r, n in LOCAL.items()})
    profile.update(idle)
    need(sum(r * n for r, n in profile.items()) == 1041408, 'complete paid rank mass')
    return dict(profile)


def fixed_exponent(cert, saving, check_edges=True):
    need(0 < saving < Q(1, 2), 'saving range')
    rows = patterns(cert)
    values = potentials(cert, rows)
    powers = {rank: power_interval(rank, 1 - saving) for rank in range(74)}
    total_B = sum(n * b for n, b in zip(INVENTORY, cert['fractional_dual_power48']))
    total_A = sum(n * a for n, a in zip(INVENTORY, cert['fractional_dual_constant']))
    need(total_A == 89952, 'inventory constant dual value')
    need(total_B == 180832 and total_B % 37 == 13, 'inventory residue')
    need(values[13] == {17: 37, 1: -5, 48: -13}, 'target reduced cost')
    edge_report = check_potentials(rows, values, powers) if check_edges else {}
    gap = interval(values[13], powers)
    need(gap[0] > 0, 'quantitative integer gap')
    priced = complete_terms(check_witness(cert, INVENTORY))
    priced[73] = -14336
    moment = interval(priced, powers)
    return {'saving': str(saving), 'gap': [str(v / 37) for v in gap],
            'unnormalized_moment_gap': [str(v) for v in moment], **edge_report}


def discover_bracket(cert):
    """Receipt generation only; ordinary replay checks two frozen endpoints."""
    grid = 10**24
    lo, hi = 1676 * 10**18, 1677 * 10**18
    for _ in range(64):
        if hi - lo <= 1:
            break
        mid = (lo + hi) // 2
        report = fixed_exponent(cert, Q(mid, grid), check_edges=False)
        lower, upper = map(Q, report['unnormalized_moment_gap'])
        need(lower > 0 or upper < 0, 'resolved root sign')
        if upper < 0:
            lo = mid
        else:
            hi = mid
    need(hi == lo + 1, 'adjacent root grid points')
    return [str(Q(lo, grid)), str(Q(hi, grid))]


def verify(cert, bracket):
    need(len(bracket) == 2, 'two root endpoints')
    lower, upper = map(Q, bracket)
    need(upper - lower == Q(1, 10**24), 'root bracket width')
    window_lo, window_hi = OPTIMALITY_WINDOW
    need(window_lo <= lower < upper <= window_hi, 'root lies in certified window')
    rows = patterns(cert)
    values = potentials(cert, rows)
    powers = {r: (power_interval(r, 1 - window_hi)[0],
                  power_interval(r, 1 - window_lo)[1]) for r in range(74)}
    window_report = check_potentials(rows, values, powers)
    need(interval(values[13], powers)[0] > 0, 'uniform positive integer gap')
    reports = [fixed_exponent(cert, saving, check_edges=False) for saving in (lower, upper)]
    need(Q(reports[0]['unnormalized_moment_gap'][1]) < 0, 'attaining lower root sign')
    need(Q(reports[1]['unnormalized_moment_gap'][0]) > 0, 'universal upper root sign')
    need(Q('0.02854988') < Q(reports[0]['gap'][0])
         <= Q(reports[0]['gap'][1]) < Q('0.02854989'), 'displayed integer gap bounds')
    need(upper / (1 + upper) < Q('0.001674088611862993'), 'displayed cap bound')
    return {'status': 'exact optimum throughout the named window; no physical packing claim',
            'integer_idle': {str(r): n for r, n in IDLE.items()}, 'root_bracket': bracket,
            'balanced_cap_upper': str(upper / (1 + upper)), 'endpoints': reports,
            'optimality_window': [str(a) for a in OPTIMALITY_WINDOW],
            'uniform_edge_certificate': window_report}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='regenerate this package receipt')
    args = parser.parse_args()
    source_inventory(pinned_inputs())
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    if args.write:
        bracket = discover_bracket(cert)
    else:
        bracket = json.loads((HERE / 'RESULT.json').read_text())['root_bracket']
    result = verify(cert, bracket)
    if args.write:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'receipt drift')
    print('PASS_T16_INTEGER_RESIDUE_OPTIMUM patterns=1163 edges=43031 endpoints=2 '
          'idle=1:2431,17:1,48:4887 no_new_kappa')
    print('root bracket:', *bracket)


if __name__ == '__main__':
    main()
