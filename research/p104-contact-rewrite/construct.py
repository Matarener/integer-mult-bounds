"""Compose the released changes and apply one four-gate identity.

The A2 identity is from PR3998/4019 and zxv's PR5643 paid construction.
PR5644 supplies the three helper relations. Ali Romman prepared the new
four-gate construction with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q


def roles(event):
    return set(event[1:3]) if event[0] in ('ADD', 'COPY') else {event[1]}


def scalar_word(word):
    return [e for e in word['program'] if e[0] != 'MOVE']


def skeleton(word):
    return [e for e in word['program'] if e[0] != 'MOVE' or e[1] >= word['public']]


def rebuild(word, program, L):
    """Keep the owned paths and rebuild each nested public path."""
    out = deepcopy(word)
    n = word['public']
    current = word['initial'] + [None]*word['owned_fields']
    spaces = [L.span(b) for b in word['frames']]
    events = []

    def move(role, frame):
        old = current[role]
        if old == frame:
            return
        L.need(role < n and spaces[old] < spaces[frame], 'Strict nested public path')
        events.append(['MOVE', role, old, frame, False])
        current[role] = frame

    for event in program:
        op, role = event[:2]
        if op == 'MOVE':
            L.need(role >= n and current[role] == event[2], 'Unchanged owned transport')
            current[role] = event[3]
        elif op == 'INIT':
            L.need(current[role] is None, 'Fresh owned lifetime')
            current[role] = event[2]
        elif op == 'CLEAR':
            L.need(current[role] == event[2], 'Owned erasure frame')
            current[role] = None
        else:
            for operand in sorted(roles(event)):
                move(operand, event[-1])
        events.append(event[:])
    for role, frame in enumerate(word['final']):
        move(role, frame)
    out['program'] = events
    return out


def replace_a2(program, L):
    old = [['ADD', 388, 715, '-4', 825], ['ADD', 340, 388, '1', 825]]
    sites = [i for i in range(len(program)-1) if program[i:i+2] == old]
    L.need(len(sites) == 1, 'Unique published A2 pair')
    i = sites[0]
    return program[:i] + [['ADD', 340, 715, '-4', 396], old[1],
                         ['ADD', 388, 715, '-4', 127]] + program[i+2:]


def check_a2_source(source, published, L):
    for key in source:
        if key not in ('program', 'schema'):
            L.need(source[key] == published[key], 'Published A2 boundary: '+key)
    L.need(replace_a2(scalar_word(source), L) == scalar_word(published),
           'Exact released PR5643 scalar change')
    before, after = L.replay(source), L.replay(published)
    delta = Counter(after['paid'])
    delta.subtract(before['paid'])
    L.need({r:v for r,v in delta.items() if v} == {2:1,3:-1,5:-1,6:1},
           'Exact released PR5643 paid change')


def matrix(gates, labels):
    at = {r:i for i,r in enumerate(labels)}
    rows = [[Q(i == j) for j in range(len(labels))] for i in range(len(labels))]
    for event in gates:
        a, b, q = at[event[1]], at[event[2]], Q(event[3])
        rows[a] = [x+q*y for x,y in zip(rows[a], rows[b])]
    return rows


def rewrite(word, witness, L):
    """Use the old helper value before its source update."""
    p = skeleton(word)
    indices = witness['indices']
    old, new = witness['old'], witness['replacement']
    L.need(indices == sorted(set(indices)) and len(indices) == 4, 'Four ordered source sites')
    L.need([p[i] for i in indices] == old, 'Exact four-gate source anchors')
    c, h, s, x = witness['roles']
    L.need(len({c,h,s,x}) == 4 and max(c,h,s,x) < word['public'], 'Four public roles')
    L.need([e[1:3] for e in old] == [[h,s],[c,s],[c,x],[x,h]], 'Declared source pattern')
    alpha, beta, gamma, delta = (Q(e[3]) for e in old)
    L.need(beta == alpha*gamma*delta, 'Exact compensation coefficient')
    expected = [['ADD', c, h, str(-gamma*delta), 3],
                ['ADD', h, s, str(alpha), 597],
                ['ADD', x, h, str(delta), 652],
                ['ADD', c, x, str(gamma), 652]]
    L.need(new == expected, 'Declared complete replacement')
    L.need([word['frames'][f] for f in (3,597,652)] == [[],[82],[82,268]],
           'Exact zero, one and two dimensional charts')
    omitted = set(indices)
    L.need(not any(roles(e) & {c,h,s} for i,e in enumerate(p)
                   if indices[0] < i < indices[-1] and i not in omitted),
           'No intervening read or write of the three moved roles')
    L.need(indices[-1] == indices[-2]+1, 'The two late gates are consecutive')
    L.need(matrix(old, [c,h,s,x]) == matrix(new, [c,h,s,x]), 'Independent four-column identity')
    changed = []
    for i,event in enumerate(p):
        if i == indices[-1]:
            changed.extend(new)
        elif i not in omitted:
            changed.append(event)
    result = rebuild(word, changed, L)
    result['schema'] = 'p104-contact-rewrite/1'
    before, after = L.replay(word), L.replay(result)
    delta_paid = Counter(after['paid'])
    delta_paid.subtract(before['paid'])
    L.need({r:v for r,v in delta_paid.items() if v} == {1:-2,2:1}, 'Two H1 calls become one H2')
    L.need(before['helpers'] == after['helpers'], 'Every independent target is retained')
    return result, after
