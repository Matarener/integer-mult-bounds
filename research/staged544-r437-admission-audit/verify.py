#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent, source-bound OQ4 transition check. No predecessor code is imported.

The selected idle-axis rule is a premise, not a physical all-size theorem.
This checker compares two complete templates and rederives their windows,
coordinate occupancy, owner maps, residual charges, and exact change set.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

P = Path(__file__).resolve().parent

class AuditFailure(ValueError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditFailure(message)

def differences(a: Any, b: Any, path: tuple = ()) -> list[tuple]:
    """Enumerate the complete semantic difference, including added/deleted fields."""
    if type(a) is not type(b):
        return [(path, a, b)]
    if isinstance(a, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                result.append((path + (key,), a.get(key), b.get(key)))
            else:
                result.extend(differences(a[key], b[key], path + (key,)))
        return result
    if isinstance(a, list):
        if len(a) != len(b):
            return [(path, ['length', len(a)], ['length', len(b)])]
        result = []
        for index, (x, y) in enumerate(zip(a, b)):
            result.extend(differences(x, y, path + (index,)))
        return result
    return [] if a == b else [(path, a, b)]

def windows(schedule: list[dict]) -> dict[int, tuple[int, int, list[int]]]:
    """For each child, scan backwards to its latest local or bridge touch.

    This is deliberately a backwards implementation of the retained rule,
    independent of hosting_core.py's forward last-touch state machine.
    Idle events are not touches under that rule.
    """
    result = {}
    for end, child in enumerate(schedule):
        if child['kind'] != 'idle' or child['rank'] <= 0:
            continue
        pair, eligible = child['pair'], []
        for event in reversed(schedule[:end]):
            kind = event['kind']
            if kind == 'bridge' and pair in (event['src'], event['dst']):
                break
            if kind == 'local_cover_sweep':
                if event['pair'] == pair:
                    break
                eligible.append(event['stage'])
        result[child['idx']] = (pair, child['rank'], sorted(eligible))
    return result

def template_audit(t: dict) -> dict:
    require((t['replicas'], t['stages'], t['m'], t['h'], t['live'],
             t['private_centre_reserve']) == (32, 9, 64, 8, 28416, 9), 'stock constants')
    require(all(v == 0 for v in t['banks_per_stage'].values()), 'no unpriced banks')
    win = windows(t['schedule'])
    require({str(k): list(v) for k, v in win.items()} == t['hosting']['windows'], 'window derivation')
    slots = t['hosting']['slots']
    require(len(slots) == 9 * 437, 'complete slot count')
    by_role, used = {}, {(i, c): set() for i in win for c in range(222)}
    for row in slots:
        require(isinstance(row, list) and len(row) == 6 and all(type(v) is int for v in row), 'integer slot')
        child, family, offset, width, stage, helper = row
        require(child in win and 0 <= family < 222 and 0 <= helper < 437 and width == 8, 'slot dimensions')
        require(stage in win[child][2], 'slot chronology')
        require((stage, helper) not in by_role, 'duplicate helper role')
        require(0 <= offset and offset + width <= win[child][1], 'slot capacity')
        coords = set(range(offset, offset + width))
        require(not (used[child, family] & coords), 'slot overlap')
        used[child, family].update(coords)
        by_role[stage, helper] = row
    require(set(by_role) == {(s, h) for s in range(9) for h in range(437)}, 'role coverage')
    remainder = {str(i): Counter() for i in win}
    for (child, family), coords in used.items():
        require(coords == set(range(len(coords))), 'contiguous remainder')
        remainder[str(child)][str(win[child][1] - len(coords))] += 1
    require({i: dict(c) for i, c in remainder.items()} == t['hosting']['remainders'], 'remainder census')
    calls = t['calls']
    require(len(calls) == 288, 'complete call count')
    seen, checked = set(), 0
    local_events = {e['stage']: e for e in t['schedule'] if e['kind'] == 'local_cover_sweep'}
    for call in calls:
        stage, replica = call['stage'], call['replica']
        require(0 <= stage < 9 and 0 <= replica < 32 and (stage, replica) not in seen, 'call coverage')
        seen.add((stage, replica))
        event = local_events[stage]
        require(call['pair'] == event['pair'] and call['orientation'] == ('reverse' if event['reverse'] else 'forward'), 'call chronology')
        owners = call['owners']
        require(len(owners) == 659, 'owner arity')
        # The first 222 source/target owners follow the unchanged data route.
        for register in range(222):
            side, port = divmod(register, 111)
            side ^= int(call['orientation'] == 'reverse')
            family = replica * 888 + (2 * call['pair'] + side) * 111 + port
            require(owners[register] == [family, ['data', stage, port]], 'data owner binding')
        for helper in range(437):
            child, family, offset, width, _, _ = by_role[stage, helper]
            physical = replica * 888 + 222 * win[child][0] + family
            require(owners[222 + helper] == [physical, ['hosted', child, offset, width]], 'helper owner binding')
            checked += 1
    idle = Counter()
    for c in remainder.values():
        for rank, multiplicity in c.items():
            if int(rank):
                idle[int(rank)] += 32 * multiplicity
    return {'helper_owner_occurrences': checked, 'slots_per_replica': len(slots),
            'idle_profile': dict(sorted(idle.items())), 'window6': list(win[6]),
            'window6_remainders_per_replica': dict(remainder['6'])}

def audit(old: dict, new: dict) -> dict:
    # Semantic gates precede the exact-transition gate, so the mutants exercise
    # chronology, coordinate capacity, and actual owner binding, not just hashes.
    a, b = template_audit(old), template_audit(new)
    expected = []
    for replica in range(32):
        call = 192 + replica
        expected.append((('calls', call, 'owners', 644, 0), 888 * replica + 210, 888 * replica + 209))
        expected.append((('calls', call, 'owners', 644, 1, 2), 0, 8))
    expected += [(('hosting', 'remainders', '6', '26'), None, 1),
                 (('hosting', 'remainders', '6', '34'), 2, None),
                 (('hosting', 'remainders', '6', '42'), 11, 12),
                 (('hosting', 'slots', 3044, 1), 210, 209),
                 (('hosting', 'slots', 3044, 2), 0, 8)]
    delta = differences(old, new)
    require(delta == expected, 'exact transition')
    # This exhausts every field, including local programs and their hashes,
    # schedule, data routes, isometries, cover, stock, and unchanged owners.
    profile_delta = {r: b['idle_profile'].get(r, 0) - a['idle_profile'].get(r, 0)
                     for r in a['idle_profile'].keys() | b['idle_profile'].keys()}
    profile_delta = {r: n for r, n in sorted(profile_delta.items()) if n}
    require(profile_delta == {26: 32, 34: -64, 42: 32}, 'paid-profile delta')
    require(sum(profile_delta.values()) == sum(r*n for r, n in profile_delta.items()) == 0,
            'count and rank-mass conservation')
    return {'status': 'PASS_INDEPENDENT_R437_OQ4_TRANSITION',
            'semantic_leaf_changes': len(delta), 'changed_helper_owners': 32,
            'before': a, 'after': b, 'paid_profile_delta': profile_delta,
            'unchanged_local_programs': True, 'unchanged_schedule_and_other_fields': True,
            'child_count_delta': 0, 'rank_mass_delta': 0,
            'no_full_supplier_or_all_size_admission': True}

def controls(old: dict, new: dict) -> list[dict]:
    cases = []
    def mutant(name, message, change):
        bad = copy.deepcopy(new)
        change(bad)
        try:
            audit(old, bad)
        except AuditFailure as error:
            require(str(error) == message, 'wrong control rejection for ' + name + ': ' + str(error))
            cases.append({'name': name, 'rejected_by': message})
        else:
            raise AuditFailure('accepted mutant ' + name)
    mutant('overlapping helper stripes', 'slot overlap', lambda x: x['hosting']['slots'][3044].__setitem__(2, 0))
    mutant('overfull pending child', 'slot capacity', lambda x: x['hosting']['slots'][3044].__setitem__(2, 40))
    mutant('illegal source window', 'slot chronology', lambda x: x['hosting']['slots'][3044].__setitem__(4, 2))
    mutant('stale owner in last replica', 'helper owner binding', lambda x: x['calls'][223]['owners'].__setitem__(644, old['calls'][223]['owners'][644]))
    mutant('stale residual invoice', 'remainder census', lambda x: x['hosting']['remainders'].__setitem__('6', old['hosting']['remainders']['6']))
    # These leave all the new geometry gates valid and fail only the complete
    # transition comparison. They guard against promoting old identity coverage
    # after a seemingly unrelated word or template modification.
    mutant('changed local program', 'exact transition', lambda x: x['local_programs']['forward'][0].__setitem__(0, 'INVALID'))
    mutant('changed cover contract', 'exact transition', lambda x: x.__setitem__('cover', x['cover'] + ' changed'))
    return cases

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path, help='Write the recomputed receipt to a new path.')
    args = parser.parse_args()
    sources = json.loads((P/'SOURCES.json').read_text())
    loaded = {}
    for source in sources['templates']:
        relative = Path(source['local_path'])
        require(not relative.is_absolute() and '..' not in relative.parts, 'relative source path')
        path = P/relative
        require(path.is_file() and not path.is_symlink(), 'regular source file')
        require(not any(parent.is_symlink() for parent in path.parents if parent != P.parent), 'no source aliases')
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == source['sha256'], 'source SHA256')
        require(hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == source['git_blob'], 'source Git blob')
        loaded[source['role']] = json.loads(gzip.decompress(raw))
    result = audit(loaded['previous'], loaded['current'])
    result['negative_controls'] = controls(loaded['previous'], loaded['current'])
    data = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.write_result:
        with args.write_result.open('x', encoding='utf-8') as f:
            f.write(data)
    else:
        require((P/'RESULT.json').read_text() == data, 'committed receipt equality')
    print(data, end='')

if __name__ == '__main__':
    main()
