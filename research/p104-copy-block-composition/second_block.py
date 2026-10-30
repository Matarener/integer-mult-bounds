"""Bind the released second block while preserving unrelated native paths.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The second block and Joel Pulikkan's R22 mechanism retain their source credit.
"""
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path
from sources import need

HERE = Path(__file__).resolve().parent


def encoded(value):
    return json.dumps(value, separators=(',', ':'))


def extend(source):
    plan = json.loads((HERE/'source/SECOND-PLAN.json').read_bytes())
    old = json.loads(gzip.decompress((HERE/'source/SECOND-OLD-WORD.json.gz').read_bytes()))
    published = json.loads(gzip.decompress((HERE/'source/SECOND-WORD.json.gz').read_bytes()))
    old_scalar = [e for e in old['program'] if e[0] != 'MOVE']
    published_scalar = [e for e in published['program'] if e[0] != 'MOVE']
    need([e[:-1] for e in old_scalar] == [e[:-1] for e in published_scalar],
         'The published block preserves all scalar coefficients and order')
    need(published['frames'] == old['frames'] + [plan['basis']], 'Exact released block chart')
    word = deepcopy(source)
    need(plan['basis'] not in word['frames'], 'The second chart has no exact existing copy')
    chart = len(word['frames'])
    word['frames'].append(plan['basis'])
    scalar = [(i, e) for i, e in enumerate(word['program']) if e[0] != 'MOVE']
    keys = [encoded(e) for _, e in scalar]
    changed = []
    roles = set()
    for run in plan['runs']:
        block = old_scalar[run['first_scalar']:run['first_scalar']+run['length']]
        need(sha256(encoded(block).encode()).hexdigest() == run['old_sha256'], 'Exact released scalar block')
        block_keys = [encoded(e) for e in block]
        hits = [i for i in range(len(keys)-len(block)+1) if keys[i:i+len(block)] == block_keys]
        need(len(hits) == 1, 'One literal second-block scalar run')
        for j in range(hits[0], hits[0]+len(block)):
            i, event = scalar[j]
            need(i not in changed and event[0] in ('ADD', 'SCALE') and event[-1] == plan['old_frame'],
                 'Disjoint scalar operation on the declared old chart')
            changed.append(i)
            roles.update(event[1:3] if event[0] == 'ADD' else event[1:2])
            event[-1] = chart
    need(len(changed) == 102 and sorted(roles) == plan['roles'], 'All and only released contacts')
    for kind, role in [('initial', plan['initial_helper']), ('final', plan['final_helper'])]:
        need(word[kind][role] == plan['old_frame'], 'Exact second-block helper endpoint')
        word[kind][role] = chart

    # Change the last old native edge before a changed contact or final boundary.
    # Earlier edges in a query chain retain their destination and their order.
    following = {r: ('final', a, b) for r, (a, b) in enumerate(zip(source['final'], word['final']))}
    destinations = {}
    for i in reversed(range(len(source['program']))):
        before, after = source['program'][i], word['program'][i]
        op, role = before[:2]
        if op == 'MOVE':
            next_use = following.get(role)
            if next_use and next_use[0] in ('scalar', 'final') and before[3] == next_use[1]:
                destinations[i] = next_use[2]
            following[role] = ('move', before[2], before[2])
        else:
            operands = before[1:3] if op in ('ADD', 'COPY') else before[1:2]
            for r in operands:
                following[r] = ('barrier' if op == 'INIT' else 'scalar', before[-1], after[-1])
    current = word['initial'] + [None]*word['owned_fields']
    active, program, native_changes = set(), [], []

    def move(role, frame, where):
        need(current[role] is not None, 'Only a live field can move')
        if current[role] != frame:
            event = ['MOVE', role, current[role], frame, role in active]
            program.append(event)
            native_changes.append(dict(source_index=where, inserted=event))
            current[role] = frame

    for i, event in enumerate(word['program']):
        op, role = event[:2]
        if op == 'MOVE':
            need(event[4] == (role in active), 'Original owned-query flag')
            frame = destinations.get(i, event[3])
            replacement = ['MOVE', role, current[role], frame, role in active]
            need(current[role] is not None, 'Original query has a live source')
            if current[role] != frame:
                program.append(replacement)
            if replacement != event or current[role] == frame:
                native_changes.append(dict(source_index=i, old=event,
                    replacement=None if current[role] == frame else replacement))
            current[role] = frame
        elif op == 'INIT':
            need(role not in active, 'New owned lifetime')
            active.add(role)
            current[role] = event[-1]
            program.append(event)
        else:
            move(role, event[-1], i)
            if op in ('ADD', 'COPY'):
                move(event[2], event[-1], i)
            program.append(event)
            if op == 'CLEAR':
                need(role in active, 'Owned lifetime closes')
                active.remove(role)
                current[role] = None
    for role, frame in enumerate(word['final']):
        move(role, frame, len(source['program']))
    need(not active, 'All owned lifetimes close')
    word['program'] = program
    unchanged = lambda w: [e for e in w['program'] if e[0] == 'MOVE' and e[1] not in roles]
    need(unchanged(word) == unchanged(source), 'Every unrelated native query stays in order')
    before = [e[:-1] for e in source['program'] if e[0] != 'MOVE']
    after = [e[:-1] for e in word['program'] if e[0] != 'MOVE']
    need(before == after, 'Every scalar coefficient, order and copy value is unchanged')
    word['schema'] = 'p104-copy-block-composition/2'
    return word, dict(source_head='4b30391e633ba0c7c674f03586ae97d443e9bc9c',
        changed_scalar_source_indices=changed, roles=sorted(roles), basis=plan['basis'],
        new_frame=chart, native_changes=native_changes,
        scalar_transfer_sha256=sha256(encoded(before).encode()).hexdigest())
