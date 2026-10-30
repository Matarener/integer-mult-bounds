"""Relay with deferred cancellation (R18).
Candidate: helper h pure (row == h_in, trivial word) at an intermediate frame F (start dim < dim F)
with climbs ahead, at time t.  Rewrite: new register R' starting at F; at t, for every register r at
F holding a*h_in (trivial word): r -= a*h ; r += a*R' (free ADDs at F); every later op on h is renamed
to R'; h retires at frame F.  Valid iff the h_in-content held OUTSIDE F at time t (vector E) is driven
exactly to 0 by the remaining program (the rest of the renamed program acts on E linearly).
Gain: rank (d1-d0) target -> (dF-d0) + (d1-dF), paid climbs unchanged."""
import sys
from collections import Counter, defaultdict
from relay import *

def step(rows, cur, e, back):
    k = e[0]; touched = None
    if k == 'scalar':
        g, frame = e[1:]; t = tuple(g[1]); touched = t
        if g[0] == 'clear': rows[t] = {}; cur[t] = frame
        elif g[0] == 'copy': rows[t] = dict(rows[tuple(g[2])])
        elif g[0] == 'add': v.add(rows[t], rows[tuple(g[2])], Q(g[3], g[4]))
        else: q = Q(g[2], g[3]); rows[t] = {a: q*x for a, x in rows[t].items()}
    elif k == 'warp':
        _, r, op, o, n = e; t = tuple(r); touched = t; rows[t] = v.warp(rows[t], op, back); cur[t] = n
    elif k == 'climb':
        touched = ('L', e[2]); cur[touched] = e[4]
    elif k == 'center': cur['C', e[1]] = e[3]
    return touched

def propagate(prog, j0, E, back):
    E = {r: dict(x) for r, x in E.items() if x}
    for e in prog[j0+1:]:
        if not E: break
        k = e[0]
        if k == 'scalar':
            g = e[1]; t = tuple(g[1])
            if g[0] == 'clear': E.pop(t, None)
            elif g[0] == 'copy':
                s = tuple(g[2]);
                if s in E: E[t] = dict(E[s])
                else: E.pop(t, None)
            elif g[0] == 'add':
                s = tuple(g[2])
                if s in E:
                    d = E.setdefault(t, {}); v.add(d, E[s], Q(g[3], g[4]))
                    if not d: E.pop(t)
            elif t in E:
                q = Q(g[2], g[3]); E[t] = {a: q*x for a, x in E[t].items()}
        elif k == 'warp':
            _, r, op, o, n = e; t = tuple(r)
            if t in E: E[t] = v.warp(E[t], op, back)
    return E

def windows(side):
    back = side == 'backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}; cur['C', 0] = None
    left = Counter(e[2] for e in prog if e[0] == 'climb'); open_ = {}; win = []
    for j, e in enumerate(prog):
        t = step(rows, cur, e, back)
        if e[0] == 'climb': left[e[2]] -= 1
        if t and t[0] == 'L' and t[1] >= 224:
            i = t[1]
            if t in open_: win.append((t, open_.pop(t), j - 1))
            if left[i] > 0 and dim(c['start'][i]) < dim(cur[t]) and rows[t] == {(t, ()): Q(1)}:
                open_[t] = j
    return win

def screen(side, samples=6):
    back = side == 'backward'; prog = w['programs'][side]
    win = windows(side)
    times = defaultdict(list)
    for h, a, b in win:
        ts = sorted({a, b} | {a + (b - a) * s // samples for s in range(samples + 1)})
        for t in ts: times[t].append(h)
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}; cur['C', 0] = None
    res = []; why = Counter()
    for j, e in enumerate(prog):
        step(rows, cur, e, back)
        for h in times.get(j, ()):
            F = cur[h]
            inF = {r: {k: x for k, x in rows[r].items() if k[0] == h} for r in rows if cur[r] == F and r != h}
            if any(wd != () for x in inF.values() for (var, wd) in x): why['nontrivial word at F'] += 1; continue
            E = {r: {k: x for k, x in rows[r].items() if k[0] == h} for r in rows if cur[r] != F}
            E = {r: x for r, x in E.items() if x}
            Ef = propagate(prog, j, E, back)
            ok = not Ef
            why['valid' if ok else 'E survives'] += 1
            res.append((h[1], j, dim(c['start'][h[1]]), dim(F), dim(c['final'][h[1]]), len(E), ok, sum(1 for x in inF.values() if x)))
    print(side, 'pure windows', len(win), 'tests', sum(why.values()), dict(why), flush=True)
    good = sorted({(r[0], r[2], r[3], r[4]) for r in res if r[6]})
    print(side, 'VALID relays (helper, d0, dF, d1):', len(good), good[:60], flush=True)
    return res

if __name__ == '__main__':
    import pickle
    out = {s: screen(s) for s in (sys.argv[1:] or ('forward', 'backward'))}

