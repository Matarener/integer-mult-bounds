"""Apply three exact neutral helper relations and join unused transports.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The helper boundary identity extends the retained PR5602 construction.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q


def coalesce(word, L):
    out = deepcopy(word)
    actual = word['initial'] + [None]*word['owned_fields']
    desired, program = actual[:], []

    def flush(role):
        if actual[role] != desired[role]:
            program.append(['MOVE', role, actual[role], desired[role], role >= word['public']])
            actual[role] = desired[role]

    for event in word['program']:
        op, role = event[:2]
        if op == 'MOVE':
            L.need(desired[role] == event[2], 'Chronological transport source')
            desired[role] = event[3]
        elif op == 'INIT':
            L.need(actual[role] is None, 'Fresh owned lifetime')
            actual[role] = desired[role] = event[2]
            program.append(event[:])
        else:
            flush(role)
            if op in ('ADD', 'COPY'):
                flush(event[2])
            program.append(event[:])
            if op == 'CLEAR':
                actual[role] = desired[role] = None
    for role in range(word['public']):
        flush(role)
    out['program'] = program
    return out


def relation(word, witness, L):
    h, cut, frame = (witness[k] for k in ('helper', 'cut', 'frame'))
    n, owned = word['public'], word['owned_fields']
    main = set(word['live']) | {r+112 for r in word['live']}
    L.need(h < n and h not in main and witness['reverse'] is False, 'Forward public helper')
    L.need(word['program'][cut] == witness['anchor'], 'Exact chronological anchor')
    L.need(word['final'][h] == frame, 'The target boundary stays fixed')
    rows = [{r:Q(1)} if r < n else {} for r in range(n+owned)]
    current = word['initial'] + [None]*owned
    for event in word['program'][:cut+1]:
        op, role = event[:2]
        if op == 'MOVE':
            current[role] = event[3]
        elif op in ('INIT', 'CLEAR'):
            rows[role] = {}
            current[role] = event[2] if op == 'INIT' else None
        elif op == 'SCALE':
            rows[role] = {j:Q(event[-2])*a for j,a in rows[role].items()}
        elif op == 'COPY':
            rows[role] = {j:Q(event[-2])*a for j,a in rows[event[2]].items()}
        else:
            L.add(rows[role], rows[event[2]], Q(event[-2]))
    output = {int(j):Q(a) for j,a in witness['output'].items()}
    cancel = {int(j):Q(a) for j,a in witness['cancel'].items()}
    initial = word['initial'][h]
    L.need(h in output and h not in cancel and all(j < n and word['initial'][j] == initial
           for j in output), 'One independent input chart')
    L.need(current[h] == frame and all(current[j] == frame for j in cancel),
           'One cancellation chart')
    row = rows[h].copy()
    for role, coefficient in cancel.items():
        L.add(row, rows[role], -coefficient)
    L.need(row == output, 'Exact prefix relation on every input')
    scale = output[h]
    L.need(scale and abs(scale.numerator) & (abs(scale.numerator)-1) == 0
           and scale.denominator & (scale.denominator-1) == 0, 'Invertible dyadic coefficient')
    tail = word['program'][cut+1:]
    L.need(not any(e[0] in ('ADD', 'COPY') and e[2] == h for e in tail), 'No later helper read')
    removed = [e for e in tail if e[1] == h]
    L.need(len(removed) == witness['removed'] and all(e[0] in ('ADD', 'SCALE') for e in removed),
           'Only declared scalar cleanup is removed')
    preparation = [['ADD', h, j, str(-a/scale), initial] for j,a in sorted(output.items()) if j != h]
    cancellation = [['ADD', h, j, str(-a), frame] for j,a in sorted(cancel.items())]
    if scale != 1:
        cancellation.append(['SCALE', h, str(1/scale), frame])
    out = deepcopy(word)
    out['program'] = preparation + word['program'][:cut+1] + cancellation + [e for e in tail if e[1] != h]
    out = coalesce(out, L)
    return out, {'helper':h, 'cut':cut, 'frame':frame, 'removed_scalar_events':removed,
                 'preparation':preparation, 'cancellation':cancellation}


def owned_events(word):
    n = word['public']
    return [e for e in word['program'] if e[1] >= n or (e[0] in ('ADD', 'COPY') and e[2] >= n)]


def construct(source, witnesses, L):
    L.need([c['helper'] for c in witnesses] == [291,321,369], 'Three declared helper relations')
    word, receipts = deepcopy(source), []
    before = L.replay(word)
    for witness in witnesses:
        old = word
        word, receipt = relation(word, witness, L)
        after = L.replay(word)
        delta = Counter(after['paid'])
        delta.subtract(before['paid'])
        L.need({r:v for r,v in delta.items() if v} == {1:-1,5:-1,6:1}, 'One H1+H5 path becomes H6')
        L.need(after['helpers'] == before['helpers'] and word['initial'] == old['initial']
               and word['final'] == old['final'], 'Every target and independent input stays fixed')
        L.need(owned_events(word) == owned_events(old), 'Every owned operation is retained in order')
        receipt.update(paid=after['paid'], events=len(word['program']), scalar=after['real_scalar_allowance'])
        receipts.append(receipt)
        before = after
    return word, receipts, before
