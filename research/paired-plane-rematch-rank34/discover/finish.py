import random, sys, json, itertools
exec(open('frames.py').read().split('# Algorithm X')[0])
masks = [sum(1 << x for x in f) for f in frames]
rng = random.Random(int(sys.argv[1]))

def matchings(rest):
    if not rest:
        yield []
        return
    a = rest[0]
    for b in rest[1:]:
        if dot(labels[a], labels[b]) == 0:
            for m in matchings([x for x in rest[1:] if x != b]):
                yield [(a, b)] + m

def chrom(planes):
    n = len(planes)
    orth = [[i != j and all(dot(labels[x], labels[y]) == 0 for x in planes[i] for y in planes[j]) for j in range(n)] for i in range(n)]
    for k in range(1, n + 1):
        def col(i, c):
            if i == n: return True
            for v in range(k):
                if all(c[j] != v or orth[i][j] for j in range(i)):
                    c.append(v)
                    if col(i + 1, c): return True
                    c.pop()
            return False
        if col(0, []): return k
    return n

best = 99
for t in range(int(sys.argv[2])):
    order = list(range(len(frames))); rng.shuffle(order)
    used = 0; sel = []
    for k in order:
        if not masks[k] & used:
            used |= masks[k]; sel.append(k)
    if len(sel) < 12: continue
    rest = [x for x in range(N) if not used >> x & 1]
    for m in itertools.islice(matchings(rest), 2000):
        c = len(sel) + chrom(m)
        if c < best:
            best = c
            print('packing', len(sel), 'rest', len(rest), 'total classes', c, flush=True)
            json.dump({'pairs': [(f[2*i], f[2*i+1]) for k in sel for f in [frames[k]] for i in range(4)] + m}, open('best-pack-%s.json' % sys.argv[1], 'w'))
        if best <= 14: break
    if best <= 14: break
print('best total classes', best)
