#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The recorded u=2 plane-port screen misses the rank-8/u2 16-child slack.

The selected-centre / rank-8 / two-unpaid integer cell from PR #3889 passes
a = 1/98 after 16 added rank-1 children on the nine-call pool and fails at 17.
That boundary is recomputed here from the selected local mass and
research/complex-local-word-ceiling/ceiling.py. It is not a physical producer.

The plane-port contract (ctoth, discussion 1587; research/plane-port-copy-budgets)
is the recorded endpoint that leaves two unpaid coordinates. Its source-bound
copy invoice of 112 rank-2 drops per call (C = 224; paired-plane-native-payload)
demands more paid mass than 73 coordinates per family, so it cannot be an
additive bill on a feasible u=2 histogram. Dropping that invoice and shortening
224 data units as rank-1 children, the most favorable screen in the copy-budget
package, still has relaxation moment > 1 at a = 1/98. The certified rank-1
deficit of that screen is strictly larger than the cell's whole 16-child slack.

No new kappa. The selected conditional result is unchanged.
"""
import ast
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
A = Q(1, 98)
CALLS = 9
FAMILIES = 896
WIDTH = 73
SELECTED_MASS = 5586
CENTRE = 64
RANK_CAP = 8
IDLE_CAP = 51
COPY_CHARGE = 224
POOL_RANK1_SLACK = 16


class Fail(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Fail(why)


def pins():
    data = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    out = {}
    for row in data['files']:
        if row['usage'] == 'input':
            path = ROOT / row['path']
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            need(digest == row['sha256'], 'pin mismatch: ' + row['path'])
            out[row['path']] = path
    return out


def load_ceiling(path):
    spec = importlib.util.spec_from_file_location('pinned_ceiling', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def literal_assignments(path, names):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id in names:
            found[target.id] = ast.literal_eval(node.value)
        elif isinstance(target, ast.Tuple):
            value = node.value
            if not isinstance(value, ast.Tuple) or len(value.elts) != len(target.elts):
                continue
            for name_node, value_node in zip(target.elts, value.elts):
                if isinstance(name_node, ast.Name) and name_node.id in names:
                    found[name_node.id] = ast.literal_eval(value_node)
    need(set(found) == set(names), 'plane-port constants missing: ' + ','.join(sorted(set(names) - set(found))))
    return found


def optimum(mass, cap):
    need(type(mass) is int and mass >= 0, 'mass')
    need(type(cap) is int and 0 < cap <= IDLE_CAP, 'cap')
    quotient, remainder = divmod(mass, cap)
    histogram = {}
    if quotient:
        histogram[cap] = quotient
    if remainder:
        histogram[remainder] = 1
    return histogram


def moment(ceiling, histogram, families, saving):
    low = high = Q(0)
    for rank, count in histogram.items():
        left, right = ceiling.child_cost(rank, WIDTH, saving)
        low += count * left
        high += count * right
    return low / families, high / families


def ideal_pool(ceiling):
    per_call = optimum(SELECTED_MASS, RANK_CAP)
    need(per_call == {8: 698, 2: 1}, 'rank-8 optimum of the selected mass')
    paid = Counter({rank: count * CALLS for rank, count in per_call.items()})
    paid_mass = SELECTED_MASS * CALLS
    need(sum(rank * count for rank, count in paid.items()) == paid_mass, 'ideal paid mass')
    idle_mass = (WIDTH - 2) * FAMILIES + CENTRE * CALLS - paid_mass
    need(idle_mass == 13918, 'ideal idle mass')
    idle = optimum(idle_mass, IDLE_CAP)
    need(idle == {51: 272, 46: 1}, 'ideal idle histogram')
    histogram = Counter(paid) + Counter(idle)
    low, high = moment(ceiling, histogram, FAMILIES, A)
    unit_low, unit_high = ceiling.child_cost(1, WIDTH, A)
    extra = int((1 - high) * FAMILIES / unit_high)
    need(high + Q(extra, FAMILIES) * unit_high < 1 < low + Q(extra + 1, FAMILIES) * unit_low,
         'ideal surcharge boundary')
    need(extra == POOL_RANK1_SLACK, 'published 16-child boundary')
    saturated = high + Q(POOL_RANK1_SLACK, FAMILIES) * unit_high
    need(saturated < 1, 'sixteen rank-1 children still pass')
    return dict(paid=dict(paid), idle=idle, moment_low=low, moment_high=high,
                unit_low=unit_low, unit_high=unit_high, saturated_high=saturated)


def plane_words(constants):
    word = dict(constants['CWORD'])
    need(word == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, 'selected local word')
    need(constants['CDATA_DROP'] == 224, 'data shrink')
    need((constants['CM'], constants['CFAM'], constants['CST']) == (WIDTH, FAMILIES, CALLS),
         'plane-port template')
    unchanged = {rank: count for rank, count in word.items() if not (rank == 8 and count == 8)}
    need(8 not in unchanged, 'centre copies remain')
    shrink = dict(unchanged)
    shrink[1] -= 224
    need(min(shrink.values()) > 0, 'shrink underflow')
    need(max(shrink) == 5, 'shrink is not a rank-8 delivery')
    need(sum(rank * count for rank, count in shrink.items()) == 5298, 'shrink mass')
    native = dict(shrink)
    native[2] = native.get(2, 0) + 112
    return unchanged, shrink, native


def rank1_deficit(moment_low, unit_high):
    """Largest d such that subtracting d maximum rank-1 costs leaves the lower moment >= 1."""
    need(moment_low > 1, 'profile does not fail')
    deficit = int((moment_low - 1) * FAMILIES / unit_high)
    need(moment_low - Q(deficit, FAMILIES) * unit_high >= 1, 'deficit enclosure')
    need(moment_low - Q(deficit + 1, FAMILIES) * unit_high < 1, 'deficit not maximal')
    return deficit


def screen(ceiling, local, centre, unpaid):
    low, high = ceiling.relax(local, WIDTH, FAMILIES, CALLS, centre, A, unpaid=unpaid)
    need(low <= high, 'crossed enclosure')
    return low, high


def coverage_controls(ceiling, word):
    mass = sum(rank * count for rank, count in word.items())
    need(mass == SELECTED_MASS, 'selected mass')
    per_call = Q(FAMILIES, CALLS)
    line_total = (WIDTH - 1) * per_call + CENTRE
    need(line_total - mass == 1646, 'line-port idle 1646')
    replica_paid = mass * CALLS
    replica_law = (WIDTH - 1) * FAMILIES + CENTRE * CALLS
    need(replica_law - replica_paid == 1646 * CALLS, 'nine-call line-port identity')
    need(ceiling.max_idle_rank(WIDTH) == IDLE_CAP, 'halving guard')
    # The same local word at unpaid=1 and a=1/98 is far above one. u=2 is load-bearing.
    line_low, _line_high = screen(ceiling, word, CENTRE, 1)
    need(line_low > 1, 'line-port word fails a=1/98')
    # A vacuous idle-only word must be able to pass, so a later failure is not a dead engine.
    empty_low, empty_high = screen(ceiling, {1: 1}, 1, 2)
    need(empty_high < 1, 'near-empty u=2 word passes a=1/98')


def native_obstruction():
    demanded = (WIDTH - 2) * FAMILIES + COPY_CHARGE * CALLS
    capacity = WIDTH * FAMILIES
    need(demanded == 65632 and capacity == 65408, 'native mass arithmetic')
    need(Q(demanded, capacity) == Q(293, 292), 'native mass ratio')
    need(demanded - capacity == 224, 'native overspend')
    per_call_deficit = Q(COPY_CHARGE) - 2 * Q(FAMILIES, CALLS)
    need(per_call_deficit == Q(224, 9), 'copy charge exceeds two unpaid coordinates')


def main():
    pinned = pins()
    ceiling = load_ceiling(pinned['research/complex-local-word-ceiling/ceiling.py'])
    constants = literal_assignments(
        pinned['research/plane-port-copy-budgets/verify.py'],
        {'CWORD', 'CDATA_DROP', 'CM', 'CFAM', 'CST'})
    word = constants['CWORD']
    coverage_controls(ceiling, word)
    native_obstruction()
    ideal = ideal_pool(ceiling)
    unchanged, shrink, native = plane_words(constants)
    rows = {
        'unchanged_c0': screen(ceiling, unchanged, 0, 2),
        'shrink_c0': screen(ceiling, shrink, 0, 2),
        'shrink_plus_112_rank2': screen(ceiling, native, COPY_CHARGE, 2),
    }
    for name, (low, _high) in rows.items():
        need(low > 1, name + ' does not fail a=1/98')
    shrink_deficit = rank1_deficit(rows['shrink_c0'][0], ideal['unit_high'])
    unchanged_deficit = rank1_deficit(rows['unchanged_c0'][0], ideal['unit_high'])
    need(shrink_deficit == 68, 'favorable-screen deficit')
    need(unchanged_deficit == 147, 'unchanged-screen deficit')
    # shrink_low >= 1 + 68 * uh / F > saturated_high + 68 * uh / F,
    # and saturated_high already includes the 16 passing rank-1 children.
    need(rows['shrink_c0'][0] - Q(shrink_deficit, FAMILIES) * ideal['unit_high']
         >= 1 > ideal['saturated_high'], 'shrink screen is not above the saturated cell')
    selected = json.loads((ROOT / 'certificates/selected-result.json').read_text(encoding='utf-8'))
    need(Q(selected['kappa']) == Q(836330098538459, 500000000000000000), 'selected kappa moved')
    receipt = {
        'status': 'PASS_RANK8_U2_PLANE_PORT_SLACK',
        'target_a': '1/98',
        'target_kappa': '1/99',
        'ideal_extra_rank1_pass': POOL_RANK1_SLACK,
        'ideal_moment_high': str(ideal['moment_high']),
        'shrink_c0_moment_low': str(rows['shrink_c0'][0]),
        'shrink_rank1_deficit': shrink_deficit,
        'unchanged_rank1_deficit': unchanged_deficit,
        'native_mass_ratio': '293/292',
        'native_overspend': 224,
        'shrink_max_rank': 5,
        'no_new_kappa': True,
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    path = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(text, encoding='utf-8')
    else:
        need(path.read_text(encoding='utf-8') == text, 'RESULT.json differs')
    print(receipt['status']
          + ' extra_pass=' + str(POOL_RANK1_SLACK)
          + ' shrink_deficit=' + str(shrink_deficit)
          + ' unchanged_deficit=' + str(unchanged_deficit)
          + ' above_saturated_cell=true'
          + ' native=293/292'
          + ' no_new_kappa=true')


if __name__ == '__main__':
    try:
        main()
    except Fail as exc:
        print('FAIL_RANK8_U2_PLANE_PORT_SLACK', exc, file=sys.stderr)
        sys.exit(1)
