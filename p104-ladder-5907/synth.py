"""Closed-window re-synthesis on a P104 word (generalises the PR5827 seven-event rewrite).

A window is a register stop [i, j] together with the smallest register set R such that every event in [i, j] that touches R
touches only R.  Inside such a window the events of R can be replaced by any legal sequence with the same entry/exit charts
and the same linear transfer on R.  We search (BFS with state dedupe) for sequences in which every register visits a
subsequence of its original frames (so ranks only merge), using the original ADD/SCALE edges plus two-step composites,
with at most the original number of events and strictly fewer MOVEs.  Every window and its outcome is logged as JSONL.

usage: python3 synth.py WORD.json.gz WINDOWS.json LOG.jsonl [--max-states N] [--shard k/K]
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
from fractions import Fraction as Q
import json, sys, time
import p104
from rung import timelines, chart

ARG = lambda k, d: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d


def transfer(ops, R):
    idx = {x: a for a, x in enumerate(R)}
    M = [[Q(int(a == b)) for b in range(len(R))] for a in range(len(R))]
    for e in ops:
        if e[0] == 'ADD':
            r, s, q = idx[e[1]], idx[e[2]], Q(e[3])
            M[r] = [x+q*y for x, y in zip(M[r], M[s])]
        elif e[0] == 'SCALE':
            r, q = idx[e[1]], Q(e[2])
            M[r] = [q*x for x in M[r]]
    return tuple(tuple(row) for row in M)


def solve(w, S, win, max_states):
    prog = w['program']
    tl, _ = TL
    i, j, R = win['i'], win['j'], win['R']
    ev = [p for p in range(i, j+1) if prog[p][1] in R or (prog[p][0] in ('ADD', 'COPY') and prog[p][2] in R)]
    ops = [prog[p] for p in ev]
    if any(e[0] in ('COPY', 'INIT', 'CLEAR') for e in ops):
        return {'ok': False, 'why': 'owned lifecycle in window'}
    if any(e[0] in ('ADD',) and (e[1] not in R or e[2] not in R) for e in ops):
        return {'ok': False, 'why': 'not closed'}
    idx = {x: a for a, x in enumerate(R)}
    entry = tuple(chart(tl, x, i) for x in R)
    exit_ = tuple(chart(tl, x, j+1) for x in R)
    itin = {x: [chart(tl, x, i)] for x in R}
    priv = {}
    for e in ops:
        if e[0] == 'MOVE':
            itin[e[1]].append(e[3]); priv[e[1]] = e[4]
    nmoves = sum(1 for e in ops if e[0] == 'MOVE')
    target = transfer(ops, R)
    edges = {(e[1], e[2], Q(e[3])) for e in ops if e[0] == 'ADD'}
    for (r, s, q1) in list(edges):
        for (s2, t, q2) in list(edges):
            if s2 == s and t != r:
                p = q1*q2
                if p.denominator & (p.denominator-1) == 0:
                    edges.add((r, t, p))
    scales = {(e[1], Q(e[2])) for e in ops if e[0] == 'SCALE'}
    dims = DIMS
    # BFS over (position-in-itinerary per register, matrix); the chart of x is itin[x][pos]
    n = len(R)
    start = (tuple(0 for _ in R), transfer([], R))
    goal_pos = tuple(len(itin[x])-1 for x in R)
    frontier = {start: []}
    seen = {start}
    best = None
    for depth in range(len(ops)):
        nxt = {}
        for (pos, M), path in frontier.items():
            charts = [itin[x][pos[a]] for a, x in enumerate(R)]
            succ = []
            for a, x in enumerate(R):
                for b in range(pos[a]+1, len(itin[x])):
                    p2 = list(pos); p2[a] = b
                    succ.append((tuple(p2), M, ['MOVE', x, charts[a], itin[x][b], priv[x]]))
            for (r, s, q) in edges:
                if charts[idx[r]] == charts[idx[s]]:
                    M2 = list(M); ra, sa = idx[r], idx[s]
                    M2[ra] = tuple(u+q*v for u, v in zip(M[ra], M[sa]))
                    succ.append((pos, tuple(M2), ['ADD', r, s, str(q), charts[ra]]))
            for (r, q) in scales:
                M2 = list(M); ra = idx[r]; M2[ra] = tuple(q*u for u in M[ra])
                succ.append((pos, tuple(M2), ['SCALE', r, str(q), charts[ra]]))
            for p2, M2, e in succ:
                st = (p2, M2)
                if st in seen:
                    continue
                seen.add(st)
                np = path+[e]
                if p2 == goal_pos and M2 == target:
                    k = sum(1 for x in np if x[0] == 'MOVE')
                    if k < nmoves and (best is None or (k, len(np)) < (best[0], len(best[1]))):
                        best = (k, np)
                nxt[st] = np
                if len(seen) > max_states:
                    return {'ok': False, 'why': 'state cap', 'events': len(ops), 'moves': nmoves, 'depth': depth,
                            **({'found': best[1], 'found_moves': best[0]} if best else {})}
        frontier = nxt
        if best is not None:
            break
    if best is None:
        return {'ok': False, 'why': 'no shorter itinerary', 'events': len(ops), 'moves': nmoves, 'states': len(seen)}
    return {'ok': True, 'events': len(ops), 'moves': nmoves, 'new': best[1], 'new_moves': best[0], 'old': ops, 'ev': ev,
            'states': len(seen)}


def splice(w, ev, new):
    prog = list(w['program'])
    first = ev[0]
    keep = [e for q, e in enumerate(prog) if q not in set(ev)]
    # place the new block where the first old event was (all other events in [i, j] do not touch R)
    pos = sum(1 for q in range(first) if q not in set(ev))
    out = dict(w); out['program'] = keep[:pos]+new+keep[pos:]
    return out


def main():
    global TL, DIMS
    w = p104.read(sys.argv[1])
    wins = json.load(open(sys.argv[2]))
    k, K = map(int, ARG('--shard', '0/1').split('/'))
    wins = wins[k::K]
    maxs = int(ARG('--max-states', 200000))
    S = p104.spans(w)
    TL = timelines(w); DIMS = [len(f) for f in w['frames']]
    base = p104.price(w)
    out = open(sys.argv[3], 'a')
    t0 = time.time()
    for c, win in enumerate(wins):
        res = solve(w, S, win, maxs)
        row = {'reg': win['reg'], 'stop': win['stop'], 'i': win['i'], 'j': win['j'], 'R': win['R'], **res}
        if res['ok']:
            cand = splice(w, res['ev'], res['new'])
            try:
                info = p104.price(cand)
                row.update(legal=True, events_total=info['events'], kappa_lo=str(info['kappa_lo']),
                           gain=float(info['kappa_lo']-base['kappa_lo']), paid_calls=info['paid_calls'])
            except p104.Illegal as x:
                row.update(legal=False, illegal=str(x))
        out.write(json.dumps(row)+'\n'); out.flush()
        print(c, round(time.time()-t0), json.dumps({k: v for k, v in row.items() if k not in ('new', 'old', 'found')})[:260], flush=True)


if __name__ == '__main__':
    main()
