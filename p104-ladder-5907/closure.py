"""For every register stop [i, j], size of the smallest register set R containing the register such that every event in [i, j]
touching R touches only R (a closed window that can be re-synthesized in isolation)."""
import json, sys
from collections import Counter, defaultdict
import p104
from rung import timelines
w = p104.read(sys.argv[1]); prog = w['program']
tl, moves = timelines(w)
regs_of = lambda e: {e[1]} | ({e[2]} if e[0] in ('ADD', 'COPY') else set())
by = defaultdict(list)
for i, e in enumerate(prog):
    for x in regs_of(e): by[x].append(i)
from bisect import bisect_left, bisect_right
hist = Counter(); rows = []
for r in sorted(moves):
    for mi in range(len(moves[r])-1):
        i, j = moves[r][mi], moves[r][mi+1]
        R = {r}; todo = [r]; ev = set()
        while todo and len(R) <= 8:
            x = todo.pop()
            for p in by[x][bisect_left(by[x], i):bisect_right(by[x], j)]:
                if p in ev: continue
                ev.add(p)
                for y in regs_of(prog[p]):
                    if y not in R: R.add(y); todo.append(y)
        size = len(R) if len(R) <= 8 else 99
        hist[size] += 1
        if size <= 6: rows.append({'reg': r, 'stop': mi, 'i': i, 'j': j, 'R': sorted(R), 'events': len(ev)})
print(sorted(hist.items()))
json.dump(rows, open(sys.argv[2], 'w'))
print(len(rows))
