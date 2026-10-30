"""Replica-indexed owner overlay, scoped before physical CALL/RETURN.

Apache-2.0. Chris R / Clear1nsight with substantial OpenAI Codex assistance.
The input schedule, local words and proposed 63 moves are predecessor work.
"""
import ast
import copy
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(value, reason):
    if not value:
        raise ValueError(reason)


def retained_symmetry_check(template):
    """Execute the actual retained guard, with PR3967's private=659 adaptation."""
    tree = ast.parse((HERE / 'inputs/catalogue.py').read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Catalogue')
    bind = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_bind')
    stage_loop = copy.deepcopy(next(n for n in bind.body if isinstance(n, ast.For)
                                   and isinstance(n.target, ast.Name) and n.target.id == 'stage'))
    need(isinstance(stage_loop, ast.For) and len(stage_loop.body) == 5,
         'retained catalogue stage-loop shape')
    stage_loop.body = stage_loop.body[:2]
    class Private(ast.NodeTransformer):
        def visit_Constant(self, node):
            return ast.copy_location(ast.Constant(659), node) if node.value == 661 else node
    stage_loop = Private().visit(stage_loop)
    program = ast.fix_missing_locations(ast.Module(body=[stage_loop], type_ignores=[]))
    exec(compile(program, '<retained replica symmetry guard>', 'exec'),
         {'t': template, 'need': need})


def compile_owners(template, moves):
    t = copy.deepcopy(template)
    last, seen, windows = {}, [], {}
    for position, event in enumerate(t['schedule']):
        if event['kind'] == 'local_cover_sweep':
            seen.append((position, event['stage'], event['pair']))
            last[event['pair']] = position
        elif event['kind'] == 'bridge':
            last[event['dst']] = last[event['src']] = position
        elif event['kind'] == 'idle':
            stages = [s for p, s, pair in seen
                      if last.get(event['pair'], -1) < p < position and pair != event['pair']]
            if event['rank'] and stages:
                windows[str(event['idx'])] = [event['pair'], event['rank'], sorted(stages)]
    need(windows == t['hosting']['windows'], 'windows derived from literal chronology')
    calls = {(c['stage'], c['replica']): c for c in t['calls']}
    need(len(calls) == 288, 'complete stage-replica call domain')
    changed = set()
    for move in moves:
        key = move['stage'], move['call_replica'], move['helper']
        need(key not in changed, 'duplicate moved logical owner')
        changed.add(key)
        call = calls[key[:2]]
        old, new = move['old'], move['new']
        role = 222 + move['helper']
        need(call['owners'][role] == [old['family'], ['hosted', old['child'], old['offset'], 8]],
             'exact predecessor owner')
        call['owners'][role] = [new['family'], ['hosted', new['child'], new['offset'], 8]]
    occupancy = defaultdict(set)
    count = 0
    for call in t['calls']:
        for family, route in call['owners'][222:]:
            need(route[0] == 'hosted', 'host-all domain')
            _, child, offset, width = route
            pair, capacity, stages = t['hosting']['windows'][str(child)]
            need(call['stage'] in stages and pair != call['pair'], 'untouched destination window')
            need(0 <= family < 28416 and (family % 888) // 222 == pair,
                 'absolute destination family pair')
            need(width == 8 and 0 <= offset and offset + width <= capacity,
                 'whole residual within destination')
            cells = set(range(offset, offset + width))
            need(not cells.intersection(occupancy[child, family]), 'disjoint absolute owner cells')
            occupancy[child, family].update(cells)
            count += 1
    need(count == 125856, 'each logical helper hosted exactly once')
    profile = Counter()
    for call in t['calls']:
        for event in t['local_programs'][call['orientation']]:
            if event[0] == 0 and event[4]: profile[event[4]] += 1
            elif event[0] == 2: profile[event[5]] += 1
    idle_records = []
    for event in t['schedule']:
        if event['kind'] != 'idle' or not event['rank']: continue
        child, pair, capacity = event['idx'], event['pair'], event['rank']
        for replica in range(32):
            for cp in range(222):
                family = replica * 888 + pair * 222 + cp
                used = occupancy[child, family]
                need(used == set(range(len(used))), 'compact occupied prefix')
                rank = capacity - len(used)
                if rank:
                    profile[rank] += 1
                    idle_records.append([child, replica, cp, family, len(used), rank])
    need(sum(profile.values()) == 903456, 'all paid requests retained')
    need(sum(r*n for r,n in profile.items()) == 1808352, 'rank mass retained')
    return t, profile, idle_records


def retained_emit(template):
    """Execute the unchanged final stream-emission block of pinned emit_k.py."""
    source = (HERE / 'inputs/emit_k.py').read_text()
    start = source.index('    expanded=hashlib.sha256(); count=0; local=2*V+R\n')
    end = source.index("    res['additional_interface']=", start)
    code = '\n'.join(line[4:] for line in source[start:end].splitlines())
    scope = {'t': template, 'res': {}, 'hashlib': hashlib, 'json': json,
             'V': 111, 'R': 437, 'LIVE': 28416}
    exec(compile(code, '<unchanged retained mapped stream emitter>', 'exec'), scope)
    return scope['res']


def independent_emit(template):
    """Use the separately retained predecessor audit encoder without adaptation."""
    source = ast.parse((HERE / 'inputs/audit_hosted_k.py').read_text())
    function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'digest')
    scope = {'hashlib': hashlib, 'json': json, 'V': 111}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[function], type_ignores=[])),
                 '<retained independent audit encoder>', 'exec'), scope)
    return scope['digest'](template)


def changed_event_count(before, after):
    count = 0
    for old, new in zip(before['calls'], after['calls']):
        changed = {i for i,(a,b) in enumerate(zip(old['owners'],new['owners'])) if a != b}
        for z in before['local_programs'][old['orientation']]:
            count += z[1] in changed or (z[0] != 0 and z[2] in changed)
    return count
