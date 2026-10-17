import json, random, sys, time
exec(open('exact.py').read().split('def k4(rng)')[0])
rng = random.Random(int(sys.argv[1])); T = float(sys.argv[2])
eight = cliques(8); m8 = [sum(1 << x for x in f) for f in eight]
best = None; t0 = time.time(); tries = 0
while time.time() - t0 < T:
    order = list(range(len(eight))); rng.shuffle(order); used = 0; sel = []
    for k in order:
        if not m8[k] & used: used |= m8[k]; sel.append(eight[k])
    if len(sel) < 11: continue
    tries += 1
    rest = [x for x in range(N) if not used >> x & 1]
    tets = cliques(4, rest); mt = [sum(1 << x for x in t) for t in tets]
    full = sum(1 << x for x in rest)
    def cover(c, ch):
        if c == full: return list(ch)
        x = next(y for y in rest if not c >> y & 1)
        for i, t in enumerate(tets):
            if x in t and not mt[i] & c:
                ch.append(t); r = cover(c | mt[i], ch)
                if r: return r
                ch.pop()
        return None
    sol = cover(0, [])
    if not sol: continue
    groups = [list(f[:4]) for f in sel] + [list(f[4:]) for f in sel] + [list(t) for t in sol]
    s, colour = best_colouring(groups, rng, 300)
    if best is None or s < best:
        best = s; print('t=%.0f frames=%d supports=%d' % (time.time() - t0, len(sel), s), flush=True)
        json.dump({'k': 4, 'groups': groups, 'colour': colour, 'supports': s}, open('k4frames-best-%s.json' % sys.argv[1], 'w'))
print('tries', tries, 'best', best)
