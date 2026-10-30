"""Emit a retained native copy for each changed scalar contact group.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source program and its predecessor credit are retained in NOTICE.
"""
from copy import deepcopy


def need(ok, why):
    if not ok:
        raise ValueError(why)


def span(basis):
    out = {0}
    for value in basis:
        out |= {item ^ value for item in tuple(out)}
    return out


def graph(word):
    """Bind every scalar read to its actual role and source version."""
    frames = []

    def node(frame):
        index = len(frames)
        frames.append(frame)
        return index

    public = word['public']
    current = [node(frame) for frame in word['initial']] + [None]*word['owned_fields']
    initial = current[:public]
    versions = [0]*len(current)
    groups, events = {}, []
    for index, event in enumerate(word['program']):
        op, role = event[:2]
        old = current[role]
        source = current[event[2]] if op in ('ADD', 'COPY') else None
        if op == 'MOVE':
            current[role] = node(event[3])
        elif op == 'INIT':
            current[role] = node(event[2])
        elif op == 'CLEAR':
            current[role] = None
        elif source is not None:
            key = (event[2], versions[event[2]])
            group = groups.setdefault(key, {'source': event[2], 'node': source, 'uses': []})
            need(group['node'] == source, 'Unchanged native source version')
            group['uses'].append((index, current[role]))
        events.append((old, current[role], source))
        versions[role] = index+1
    return frames, initial, current[:public], groups, events


def construct(source, request):
    word = deepcopy(source)
    anchor = request['anchor']
    changed = set(request['changed_nodes'])
    frames, initial, final, groups, events = graph(source)
    need(len(changed) == len(request['changed_nodes']), 'Distinct changed chart nodes')
    need(all(type(node) is int and 0 <= node < len(frames) for node in changed),
         'Fixed chart node IDs')
    need(type(anchor) is int and 0 <= anchor < len(word['frames']), 'Fixed anchor frame')

    def frame(node):
        return anchor if node in changed else frames[node]

    start, stop, redirect, caches = {}, {}, {}, []
    spaces = [span(basis) for basis in word['frames']]
    for key, group in groups.items():
        before = frame(group['node'])
        uses = [index for index, destination in group['uses'] if frame(destination) != before]
        if not uses:
            continue
        targets = {frame(destination) for index, destination in group['uses'] if index in uses}
        need(len(targets) == 1, 'One changed target frame per cache')
        after = targets.pop()
        need(spaces[after] < spaces[before], 'Owned cache has a strict reverse query')
        item = {'source': group['source'], 'source_version': key[1],
                'from': before, 'to': after, 'first': min(uses), 'last': max(uses), 'uses': uses}
        index = len(caches)
        caches.append(item)
        start.setdefault(item['first'], []).append(index)
        stop.setdefault(item['last'], []).append(index)
        for use in uses:
            need(use not in redirect, 'One source operand')
            redirect[use] = index

    public = word['public']
    next_slot = public+word['owned_fields']
    available, active, program = [], {}, []
    skipped = 0
    for index, (original, record) in enumerate(zip(source['program'], events)):
        for cache_index in start.get(index, []):
            cache = caches[cache_index]
            if available:
                slot = min(available)
                available.remove(slot)
            else:
                slot = next_slot
                next_slot += 1
            active[cache_index] = slot
            cache['owned_role'] = slot
            program.extend([
                ['INIT', slot, cache['from']],
                ['COPY', slot, cache['source'], '1', cache['from']],
                ['MOVE', slot, cache['from'], cache['to'], True],
            ])
        event = list(original)
        op, role = event[:2]
        old, new, source_node = record
        if op == 'MOVE':
            before, after = frame(old), frame(new)
            event[2:4] = [before, after]
            if before == after:
                event = None
                skipped += 1
            else:
                need(spaces[after] < spaces[before] if event[4] else spaces[before] < spaces[after],
                     'Retained nested native query')
        elif op == 'INIT':
            event[2] = frame(new)
        elif op == 'CLEAR':
            event[2] = frame(old)
        else:
            event[-1] = frame(new)
            if index in redirect:
                event[2] = active[redirect[index]]
            elif source_node is not None:
                need(frame(source_node) == frame(new), 'Actual scalar coframe')
        if event is not None:
            program.append(event)
        for cache_index in stop.get(index, []):
            program.append(['CLEAR', active[cache_index], caches[cache_index]['to']])
            available.append(active.pop(cache_index))

    need(not active, 'All retained copies are cleared')
    word['program'] = program
    word['initial'] = [frame(node) for node in initial]
    word['final'] = [frame(node) for node in final]
    word['owned_fields'] = next_slot-public
    main = set(word['live']) | {role+112 for role in word['live']}
    need(all(word[side][role] == source[side][role] for side in ('initial', 'final') for role in main),
         'Fixed main endpoints')
    word['schema'] = 'p104-retained-native-copy/1'
    witness = {'caches': caches, 'changed_nodes': sorted(changed), 'anchor': anchor,
               'removed_zero_queries': skipped,
               'added_owned_labels': word['owned_fields']-source['owned_fields']}
    return word, witness
