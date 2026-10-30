"""For each pure-window hand-off candidate (relay2), list the outside holders E of h_in and whether each
ever visits the hand-off frame F (needed for successor pre-subtraction / post-correction)."""
from relay2 import *
def visits(prog):
    vis = defaultdict(set)
    for r, f in enumerate(c['start']): vis['L', r].add(f)
    for e in prog:
        if e[0] == 'climb': vis['L', e[2]].add(e[4])
        elif e[0] == 'warp': vis[tuple(e[1])].add(e[4])
        elif e[0] == 'scalar': vis[tuple(e[1][1])].add(e[2])
        elif e[0] == 'center': vis['C', e[1]].add(e[3])
    return vis
for side in ('forward', 'backward'):
    back = side == 'backward'; prog = w['programs'][side]; vis = visits(prog)
    win = windows(side); at = defaultdict(list)
    for h, a, b in win: at[a].append(h)
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(c['start'])}; cur['C', 0] = None
    stat = Counter(); nE = Counter()
    for j, e in enumerate(prog):
        step(rows, cur, e, back)
        for h in at.get(j, ()):
            F = cur[h]
            E = [r for r in rows if cur[r] != F and any(k[0] == h for k in rows[r])]
            nv = sum(1 for r in E if F in vis[r])
            stat['all E-holders visit F' if nv == len(E) else ('some' if nv else 'none visit F')] += 1
            nE[len(E)] += 1
    print(side, 'candidates', len(win), dict(stat), 'E-size histogram', dict(sorted(nE.items())))
