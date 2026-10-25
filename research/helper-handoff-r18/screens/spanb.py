"""Necessary condition for any helper hand-off inserted at time t into the #4610 word with the prefix
unchanged: h_in (trivial word) in the Q-span of the rows of the registers sharing h's frame F at t,
with h at an intermediate frame (start dim < dim F) and climbs ahead.  Checked exactly whenever a
register at F changes (row or arrival)."""
from relay2 import *
def screen(side):
    back = side == 'backward'; prog = w['programs'][side]
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}; cur['C', 0] = None
    left = Counter(e[2] for e in prog if e[0] == 'climb'); hits = defaultdict(set); checks = 0
    for j, e in enumerate(prog):
        t = step(rows, cur, e, back)
        if e[0] == 'climb': left[e[2]] -= 1
        if not t: continue
        F = cur[t]; RF = [r for r in rows if cur[r] == F]
        for h in RF:
            if h[0] != 'L' or h[1] < 224: continue
            i = h[1]
            if left[i] <= 0 or not dim(c['start'][i]) < dim(F): continue
            checks += 1
            if in_span({(h, ()): Q(1)}, [rows[r] for r in RF]): hits[i].add((dim(c["start"][i]), dim(F), dim(c["final"][i])))
    print(side, 'span checks', checks, 'helpers satisfying the necessary span condition:', len(hits), dict(list(hits.items())[:10]), flush=True)
if __name__ == '__main__':
    for s in ('forward', 'backward'): screen(s)
