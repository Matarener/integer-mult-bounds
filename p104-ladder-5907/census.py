"""Stop census of a P104 accumulated-block word: per register, its itinerary of frames and the events at each stop."""
import gzip, json, sys
from collections import Counter, defaultdict
w = json.loads(gzip.decompress(open(sys.argv[1], 'rb').read()))
n, m = w['public'], w['owned_fields']
live = set(w['live']); main = live | {r+112 for r in live}
dim = [len(f) for f in w['frames']]
cur = list(w['initial']) + [None]*m
stops = defaultdict(list)   # reg -> list of [frame, start_event, end_event, nreads, nwrites]
for r in range(n): stops[r].append([cur[r], -1, None, 0, 0])
for i, e in enumerate(w['program']):
    op, r = e[0], e[1]
    if op == 'MOVE':
        stops[r][-1][2] = i; stops[r].append([e[3], i, None, 0, 0]); cur[r] = e[3]
    elif op == 'INIT':
        cur[r] = e[2]; stops[r].append([e[2], i, None, 0, 0])
    elif op == 'CLEAR':
        stops[r][-1][2] = i; cur[r] = None
    else:
        stops[r][-1][4] += 1
        if op in ('ADD', 'COPY'): stops[e[2]][-1][3] += 1
kind = lambda r: 'main' if r in main else ('helper' if r < n else 'owned')
tot = Counter(); free = []
for r in range(n):
    s = stops[r]
    tot[kind(r), len(s)] += 1
    for j in range(1, len(s)-1):
        f, a, b, nr, nw = s[j]
        if kind(r) == 'helper':
            print('H', r, 'stop', j, 'of', len(s), 'frame', f, 'dim', dim[s[j-1][0]], '->', dim[f], '->', dim[s[j+1][0]], 'reads', nr, 'writes', nw, 'events', a, b)
print(sorted(tot.items()))
