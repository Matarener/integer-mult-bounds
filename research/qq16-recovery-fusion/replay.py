"""Full recovery replay adapted from ywz65 PR2707; source-derived routed primitives
by Arham Tahir PR2681. Adds112 owned correction/query temporaries and requires
their zero return. Chris R / Clear1nsight with OpenAI; Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
F16 = tuple((1 << i, 1) for i in range(9,25))

def bridge(P, g, q):
    """Affine translation aligning g(F17) to F16*C_q, including phase."""
    target = P.phase(F16 + ((q, 1),))
    moved = P.phase(P.move(P.F17, g, 0))
    P.need(target[1] == moved[1], 'quadratic bridge discrepancy')
    difference = [(x - y) % 4 for x, y in zip(target[0], moved[0])]
    P.need(all(x in (0, 2) for x in difference), 'odd bridge discrepancy')
    return sum((x // 2) << j for j, x in enumerate(difference))

def replay(P, w, routes, labels, x2, y2, expected, middle=None):
    owned = {s + str(p) for s in ('Z', 'W', 'D') for p in range(112)}
    rows = {name: {(name, P.AXES): Q(1)} for name in owned}; frames = {name: () for name in owned}
    for side, bank in (('X', x2), ('Y', y2)):
        for p in range(112):
            name = side + str(p); rows[name] = bank[p]
            frames[name] = P.F17 + (((labels[p], -1),) if side == 'Y' else ())
    borrowed = {n: dict(r) for n, r in rows.items() if n[0] in ('X', 'Y')}
    borrowed_frames = {n: frames[n] for n in borrowed}
    active = set(); counts = Counter()
    for index, e in enumerate(w):
        op = e[0]; counts[op] += 1
        if op == 'begin':
            P.need(not active, 'overlapping private sweeps')
            active = {'F' + str(k) for k in range(8)}
            if e[2] == 16: active |= {'G' + str(k) for k in range(8)}
            P.need(e[2] == len(active), 'private scratch count')
            for name in active: rows[name], frames[name] = {(name, P.AXES): Q(1)}, ()
        elif op == 'end':
            P.need(len(active) == e[2], 'private boundary')
            P.need(all(not rows[n] and P.phase(frames[n]) == P.phase(()) for n in active), 'scratch leak')
            for name in active: del rows[name], frames[name]
            active = set()
        elif op == 'clear':
            _, name, f = e; P.need(name in owned | active, 'clear borrowed input'); rows[name] = {}
            frames[name] = {'wide': P.F17, 'current': P.F17, 'identity': (), 'query2': F16}.get(f)
            if f.startswith('hole'): frames[name] = P.F17 + ((labels[int(f[4:])], -1),)
            P.need(frames[name] is not None, 'unknown clear frame')
        elif op == 'add':
            _, dst, src, q = e
            P.need(dst in owned | active and dst != src, 'ADD ownership/alias')
            P.need(dst in rows and src in rows, 'nonlive ADD role')
            P.need(P.phase(frames[dst]) == P.phase(frames[src]), 'ADD frame mismatch ' + str(index))
            q = Q(q); P.need(abs(q) in (1, Q(1, 4)), 'unpriced coefficient')
            rows[dst] = P.add(rows[dst], rows[src], q)
            counts['unit_ADD' if abs(q) == 1 else 'quarter_ADD'] += 1
        elif op == 'line':
            _, name, p, sign = e
            P.need(not active and name in owned and sign in (-1, 1), 'line boundary')
            frames[name] += ((labels[p], sign),)
        elif op == 'stage':
            _, name, sign = e
            P.need(not active and name in owned and sign in (-1, 1), 'stage boundary')
            frames[name] += tuple((v, sign) for v in P.BLOCK)
        elif op == 'map':
            _, name, stage, p, inverse = e[:5]
            P.need(not active and name in owned and stage in (1, 2), 'map inside private sweep')
            g = routes[stage][p]; b = P.alignment(g, P.F17) if stage == 1 else bridge(P, g, labels[p])
            if inverse: b = P.act(g, b)
            if len(e) > 5 and e[5] == 'omit_shift': b = 0
            if len(e) > 5 and e[5] == 'wide_shift': b = P.alignment(g, P.F25)
            if len(e) > 5 and e[5] == 'wrong_inverse_shift': b = bridge(P, g, labels[p])
            frames[name] = P.move(frames[name], g, b); rows[name] = P.routed(g, rows[name])
        elif op == 'checkpoint':
            P.need(not active, 'incomplete sweep at checkpoint')
            if middle is not None:
                P.need([rows['Z' + str(p)] for p in range(112)] == middle[0]
                     and [rows['W' + str(p)] for p in range(112)] == middle[1], 'inverse B1 checkpoint')
        else: raise ValueError('unknown event')
    P.need(not active, 'unterminated private sweep')
    for side, bank in zip(('Z', 'W'), expected):
        for p in range(112):
            name = side + str(p)
            P.need(rows[name] == bank[p], 'wrong output ' + name)
            P.need(P.phase(frames[name]) == P.phase(P.F17), 'wrong final frame')
    for p in range(112):
        P.need(not rows['D'+str(p)] and P.phase(frames['D'+str(p)]) == P.phase(()), 'temporary leak')
    P.need(all(rows[n] == r and frames[n] == borrowed_frames[n] for n, r in borrowed.items()), 'borrowed restoration')
    return counts
