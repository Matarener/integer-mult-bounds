"""Demand-only replay adapted from ywz65 PR2707, using Arham Tahir PR2681 primitives.
Modified ownership/output/cleanup contract: Chris R / Clear1nsight with OpenAI.
Apache-2.0. See PREDECESSORS.json for exact retained source and modifications.
"""
from collections import Counter
from fractions import Fraction as Q
def replay(P, w, routes, labels, x2, y2, expected):
    owned = {'W' + str(p) for p in range(112)}
    rows = {name: {(name, P.AXES): Q(1)} for name in owned}; frames = {name: () for name in owned}
    for side, bank in (('Y', y2),):
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
            P.need(e[2] == len(active), 'private scratch count')
            for name in active: rows[name], frames[name] = {(name, P.AXES): Q(1)}, ()
        elif op == 'end':
            P.need(len(active) == e[2], 'private boundary')
            P.need(all(not rows[n] and P.phase(frames[n]) == P.phase(()) for n in active), 'scratch leak')
            for name in active: del rows[name], frames[name]
            active = set()
        elif op == 'clear':
            _, name, f = e; P.need(name in owned | active, 'clear borrowed input'); rows[name] = {}
            frames[name] = {'wide': P.F17, 'current': P.F17, 'identity': ()}.get(f)
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
        elif op == 'map':
            _, name, stage, p, inverse = e[:5]
            P.need(not active and name in owned and stage == 1, 'map inside private sweep')
            g = routes[stage][p]; b = P.alignment(g, P.F17)
            if inverse: b = P.act(g, b)
            if len(e) > 5 and e[5] == 'omit_shift': b = 0
            frames[name] = P.move(frames[name], g, b); rows[name] = P.routed(g, rows[name])
        else: raise ValueError('unknown event')
    P.need(not active, 'unterminated private sweep')
    for p in P.U:
        name = 'W' + str(p)
        P.need(rows[name] == expected[p], 'wrong demanded output ' + name)
        P.need(P.phase(frames[name]) == P.phase(P.F17), 'wrong demanded output frame')
    for p in P.V:
        name = 'W' + str(p)
        P.need(not rows[name] and P.phase(frames[name]) == P.phase(()), 'temporary leak')
    P.need(all(rows[n] == r and frames[n] == borrowed_frames[n] for n, r in borrowed.items()), 'borrowed restoration')
    return counts
