"""New integer mixed-width placement; upstream word and geometry unchanged.

The public owner/compiler and its authors retain credit. This module changes
the stage assignment and compact bin offsets only.
"""

def _need(value, why):
    if not value:
        raise ValueError(why)

def nominate(widths, windows):
    wide = [h for h, w in enumerate(widths) if w == 8]
    thin = [h for h, w in enumerate(widths) if w == 4]
    _need(len(wide) == 433 and len(thin) == 5, 'nomination.py: required invariant at source line9')
    demands = {0: [(0, 222)], 2: [(0, 211), (1, 433), (2, 22)], 4: [(2, 411), (3, 433), (4, 266)], 6: [(4, 167), (5, 433), (6, 411)], 7: [(6, 22), (7, 433), (8, 211)], 8: [(8, 222)]}
    ids = {s: iter(wide) for s in range(9)}
    slots = []
    for child in [0, 2, 4, 6, 7, 8]:
        queue = [s for s, n in demands[child] for _ in range(n)]
        if child in [0, 8]:
            places = [(cp, 0) for cp in range(222)]
        elif child in [2, 7]:
            places = [(cp, o) for cp in range(222) for o in [0, 8, 16]]
        elif child == 4:
            places = [(cp, o) for cp in range(222) for o in [0, 8, 16, 24, 32]]
        else:
            places = [(cp, o) for cp in range(202) for o in [0, 8, 16, 24, 32]] + [(202, 0)]
        _need(len(queue) == len(places), 'nomination.py: required invariant at source line19')
        for s, (cp, off) in zip(queue, places):
            _need(s in windows[child]['stages'], 'nomination.py: required invariant at source line21')
            slots.append([child, cp, off, 8, s, next(ids[s])])
    for s in range(9):
        _need(next(ids[s], None) is None, 'nomination.py: required invariant at source line23')
    for child, stages in [(2, [0, 1, 2, 3]), (7, [5, 6, 7, 8])]:
        for i, s in enumerate(stages):
            for j, h in enumerate(thin):
                slots.append([child, 5 * i + j, 24, 4, s, h])
    for j, h in enumerate(thin):
        slots.append([6, 202, 8 + 4 * j, 4, 4, h])
    _need(len(slots) == 438 * 9, 'nomination.py: required invariant at source line28')
    return sorted(slots, key=lambda a: (a[0], a[1], a[2], a[4], a[5]))
