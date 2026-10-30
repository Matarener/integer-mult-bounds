"""Split a helper with a retained buffer and time-separated scalar contacts.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
NOTICE retains all source credit.
"""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(dst, src, coefficient):
    for index, value in tuple(src.items()):
        result = dst.get(index, Q(0)) + coefficient*value
        if result:
            dst[index] = result
        else:
            dst.pop(index, None)


def inverse(events):
    return [[e[0], *e[1:-2], str(1/Q(e[-2]) if e[0] == 'SCALE' else -Q(e[-2])), e[-1]]
            for e in reversed(events)]


def boundary_basis(c, d, pivot, frame):
    need(sum(c.get(r, Q(0))*v for r, v in d.items()) == 1 and d.get(pivot),
         'Unit pairing and nonzero physical pivot')
    events = [['ADD', pivot, r, str(-q), frame] for r, q in sorted(c.items()) if r != pivot]
    if d[pivot] != 1:
        events.append(['SCALE', pivot, str(d[pivot]), frame])
    events.extend(['ADD', r, pivot, str(q/d[pivot]), frame]
                  for r, q in sorted(d.items()) if r != pivot)
    return events


def history_identity(word, plan):
    """Compute the input row and output column at the exact contact times."""
    size = word['public']+word['owned_fields']
    collected, delivered = {}, {}
    tables = []
    for name in ('collection', 'injection'):
        table = defaultdict(list)
        for item in plan[name]:
            time = item['time2']
            need(type(time) is int and 0 <= time <= 2*len(word['program']), 'Contact time')
            need(time % 2 == 0 or time//2 in plan['queries'], 'Paid interior contact')
            table[time].append((item['role'], Q(item['coefficient'])))
        tables.append(table)

    def observe(table, time, rows, total):
        for role, q in table.get(time, []):
            need(0 <= role < size and q, 'Actual nonzero contact operand')
            add(total, rows[role], q)

    rows = [{r: Q(1)} for r in range(size)]
    for index, event in enumerate(word['program']):
        observe(tables[0], 2*index, rows, collected)
        op, role = event[:2]
        if op == 'MOVE':
            observe(tables[0], 2*index+1, rows, collected)
        elif op in ('INIT', 'CLEAR'):
            rows[role] = {}
        elif op == 'SCALE':
            rows[role] = {r: Q(event[-2])*v for r, v in rows[role].items()}
        elif op == 'COPY':
            rows[role] = {r: Q(event[-2])*v for r, v in rows[event[2]].items()}
        else:
            need(op == 'ADD', 'Source opcode')
            add(rows[role], rows[event[2]], Q(event[-2]))
    observe(tables[0], 2*len(word['program']), rows, collected)

    columns = [{r: Q(1)} for r in range(size)]
    observe(tables[1], 2*len(word['program']), columns, delivered)
    for index in reversed(range(len(word['program']))):
        event = word['program'][index]
        op, role = event[:2]
        if op in ('INIT', 'CLEAR'):
            columns[role] = {}
        elif op == 'SCALE':
            columns[role] = {r: Q(event[-2])*v for r, v in columns[role].items()}
        elif op in ('ADD', 'COPY'):
            add(columns[event[2]], columns[role], Q(event[-2]))
            if op == 'COPY':
                columns[role] = {}
        observe(tables[1], 2*index, columns, delivered)
        if op == 'MOVE':
            observe(tables[1], 2*index+1, columns, delivered)
    c = {int(r): Q(q) for r, q in plan['input'].items()}
    d = {int(r): Q(q) for r, q in plan['output'].items()}
    need(collected == c and delivered == d, 'Complete temporal input and output identities')
    main = set(word['live']) | {r+112 for r in word['live']}
    eligible = {r for r in range(word['public']) if r not in main
                and word['initial'][r] == 3 and word['final'][r] == 127}
    need(set(c) | set(d) <= eligible, 'Only independent full-boundary helpers')
    return c, d


def construct(source, plan):
    word = deepcopy(source)
    public, owned = word['public'], word['owned_fields']
    pivot, frame, cut = plan['pivot'], plan['frame'], plan['time2']
    buffer = public+1+owned
    need(plan['buffer'] == buffer, 'Fixed owned buffer label')
    c, d = history_identity(source, plan)
    before = boundary_basis(c, d, pivot, 3)
    after = inverse(before)
    for event in after:
        event[-1] = 127
    queries = set(plan['queries'])
    need(len(queries) == len(plan['queries']), 'Distinct paid access points')
    need([source['program'][i] for i in sorted(queries)] == plan['query_events'],
         'Exact paid source queries')
    collection, injection = defaultdict(list), defaultdict(list)
    for name, table in (('collection', collection), ('injection', injection)):
        for item in plan[name]:
            table[item['time2']].append((item['role'], Q(item['coefficient'])))
    first, last = min(collection), max(injection)
    need(first <= max(collection) <= cut <= min(injection) <= last, 'Causal contact order')
    need(cut % 2 == 0 or cut//2 in queries, 'Physical pivot access')

    def rename(event, continuation):
        event = event.copy()
        for index in (1, 2) if event[0] in ('ADD', 'COPY') else (1,):
            role = event[index]
            event[index] = public if continuation and role == pivot else role+1 if role >= public else role
        return event

    def swap(a, b):
        return [['ADD', a, b, '1', frame], ['ADD', b, a, '-1', frame],
                ['ADD', a, b, '1', frame], ['SCALE', b, '-1', frame]]

    program = list(before)

    def at(time):
        if time == first:
            program.append(['INIT', buffer, frame])
        for role, q in collection.get(time, []):
            program.append(['ADD', buffer, role+1 if role >= public else role, str(q), frame])
        if time == cut:
            program.extend(swap(pivot, buffer))
            program.extend(swap(public, buffer))
            program.append(['ADD', buffer, pivot, '-1', frame])
        for role, q in injection.get(time, []):
            target = public if role == pivot else role+1 if role >= public else role
            program.append(['ADD', target, buffer, str(q), frame])
        if time == last:
            program.append(['CLEAR', buffer, frame])

    for index, event in enumerate(word['program']):
        at(2*index)
        if index in queries:
            need(event[0] == 'MOVE', 'Subdivide an actual native query')
            program.append(rename(['MOVE', event[1], event[2], frame, event[4]], 2*index >= cut))
            at(2*index+1)
            program.append(rename(['MOVE', event[1], frame, event[3], event[4]], 2*index+1 >= cut))
        else:
            program.append(rename(event, 2*index >= cut))
    at(2*len(word['program']))
    program.extend(rename(event, True) for event in after)
    word.update(program=program, public=public+1, owned_fields=owned+1,
                schema='p104-asynchronous-helper-hubs/1')
    word['initial'].append(frame)
    word['final'].append(word['final'][pivot])
    word['final'][pivot] = frame
    return word, {'pivot': pivot, 'frame': frame, 'time2': cut, 'buffer': buffer,
                  'collection': plan['collection'], 'injection': plan['injection'],
                  'input': plan['input'], 'output': plan['output'],
                  'paid_access_points': plan['query_events'],
                  'input_basis': before, 'output_inverse': after,
                  'buffer_start_time2': first, 'buffer_stop_time2': last}
