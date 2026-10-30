"""Collect an unread update sum before its paid native conversion.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
NOTICE retains the P104 word and native source credit.
"""
from copy import deepcopy


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(basis):
    values = {0}
    for vector in basis:
        values |= {value ^ vector for value in tuple(values)}
    return values


def graph(word):
    """Number the constant-frame intervals of each physical field."""
    frames = []

    def node(frame):
        index = len(frames)
        frames.append(frame)
        return index

    public = word['public']
    current = [node(frame) for frame in word['initial']] + [None]*word['owned_fields']
    initial = current[:public]
    records = []
    for event in word['program']:
        op, role = event[:2]
        before = current[role]
        source = current[event[2]] if op in ('ADD', 'COPY') else None
        if op == 'MOVE':
            current[role] = node(event[3])
        elif op == 'INIT':
            current[role] = node(event[2])
        elif op == 'CLEAR':
            current[role] = None
        records.append((before, current[role], source))
    return frames, initial, current[:public], records


def construct(source, request):
    word = deepcopy(source)
    frames, initial, final, records = graph(source)
    changed = set(request['changed_nodes'])
    anchor = request['anchor']
    need(len(changed) == len(request['changed_nodes']), 'Distinct changed nodes')
    need(all(type(node) is int and 0 <= node < len(frames) for node in changed),
         'Actual changed frame nodes')
    need(type(anchor) is int and 0 <= anchor < len(word['frames']), 'Actual anchor frame')

    def frame(node):
        return anchor if node in changed else frames[node]

    group = request['accumulation']
    role, before, after, uses = (group[key] for key in ('role', 'before', 'after', 'uses'))
    need(uses == sorted(set(uses)) and len(uses) >= 2, 'Ordered distinct update events')
    need(all(type(index) is int and 0 <= index < len(source['program']) for index in uses),
         'Actual update indices')
    spaces = [span(basis) for basis in word['frames']]
    need(spaces[after] < spaces[before], 'Strict reverse accumulated query')
    first, last = uses[0], uses[-1]
    selected = set(uses)
    for index in range(first, last+1):
        event = source['program'][index]
        op, destination = event[:2]
        need(not (op in ('ADD', 'COPY') and event[2] == role),
             'Destination is not read before the sum is delivered')
        if destination == role:
            need(index in selected and op == 'ADD', 'Only the declared pending additions')
        if index in selected:
            need(op == 'ADD' and destination == role, 'Declared update destination')
            need(frame(records[index][1]) == after
                 and frame(records[index][2]) == before, 'Actual sum and destination frames')

    slot = word['public']+word['owned_fields']
    program, removed = [], 0
    for index, (original, record) in enumerate(zip(source['program'], records)):
        if index == first:
            program.append(['INIT', slot, before])
        event = list(original)
        op, destination = event[:2]
        old, new, source_node = record
        if op == 'MOVE':
            a, b = frame(old), frame(new)
            event[2:4] = [a, b]
            if a == b:
                event = None
                removed += 1
            else:
                need(spaces[b] < spaces[a] if event[4] else spaces[a] < spaces[b],
                     'Every retained query is nested in its declared direction')
        elif op == 'INIT':
            event[2] = frame(new)
        elif op == 'CLEAR':
            event[2] = frame(old)
        else:
            event[-1] = frame(new)
            if index in selected:
                event[1], event[-1] = slot, before
            if source_node is not None:
                need(frame(source_node) == event[-1], 'Actual common scalar frame')
        if event is not None:
            program.append(event)
        if index == last:
            program.extend([
                ['MOVE', slot, before, after, True],
                ['ADD', role, slot, '1', after],
                ['CLEAR', slot, after],
            ])

    word['program'] = program
    word['initial'] = [frame(node) for node in initial]
    word['final'] = [frame(node) for node in final]
    word['owned_fields'] += 1
    word['schema'] = 'p104-accumulated-native-updates/1'
    main = set(word['live']) | {role+112 for role in word['live']}
    need(all(word[side][role] == source[side][role]
             for side in ('initial', 'final') for role in main), 'Fixed main endpoints')
    return word, {
        'anchor': anchor, 'changed_nodes': sorted(changed),
        'accumulation': dict(group, owned_role=slot),
        'removed_queries': removed,
    }
