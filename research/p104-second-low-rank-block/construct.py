"""Reframe two exact scalar runs and rebuild every native path.

The R22 mechanism is by Joel Pulikkan (GamingPuzzled).
This second block is by Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
import json
from sources import need


def construct(source, plan):
    word = deepcopy(source)
    old = plan['old_frame']
    new = len(word['frames'])
    word['frames'].append(plan['basis'])
    scalar = [e for e in word['program'] if e[0] != 'MOVE']
    changed, roles = [], set()
    for run in plan['runs']:
        start, length = run['first_scalar'], run['length']
        block = scalar[start:start+length]
        need(len(block) == length, 'Complete scalar run')
        raw = json.dumps(block, separators=(',', ':')).encode()
        need(sha256(raw).hexdigest() == run['old_sha256'], 'Exact source scalar run')
        for i, event in enumerate(block, start):
            need(event[0] in ('ADD', 'SCALE') and event[-1] == old,
                 'Public scalar operation on the old chart')
            need(i not in changed, 'Disjoint scalar runs')
            changed.append(i)
            roles.update(event[1:3] if event[0] == 'ADD' else event[1:2])
            event[-1] = new
    need(len(changed) == 102 and sorted(roles) == plan['roles'], 'Exact changed contact block')
    for key, helper in (('initial', plan['initial_helper']), ('final', plan['final_helper'])):
        need(word[key][helper] == old, 'Exact old helper boundary')
        word[key][helper] = new

    current = word['initial']+[None]*word['owned_fields']
    active, program = set(), []

    def move(role, frame):
        if current[role] != frame:
            need(current[role] is not None, 'Transport of a live field')
            program.append(['MOVE', role, current[role], frame, role in active])
            current[role] = frame

    for event in scalar:
        op, role, frame = event[0], event[1], event[-1]
        if op == 'INIT':
            need(role not in active, 'New owned lifetime')
            active.add(role)
            current[role] = frame
        elif op == 'CLEAR':
            move(role, frame)
            active.remove(role)
            current[role] = None
        else:
            move(role, frame)
            if op in ('ADD', 'COPY'):
                move(event[2], frame)
        program.append(event)
    for role, frame in enumerate(word['final']):
        move(role, frame)
    need(not active, 'All owned lifetimes close')
    word['program'] = program
    word['schema'] = 'p104-second-rank4-block/1'
    return word, {'changed_scalar_indices': changed, 'roles': sorted(roles),
                  'old_frame': old, 'new_frame': new, 'basis': plan['basis'],
                  'initial_helper': plan['initial_helper'], 'final_helper': plan['final_helper']}
