import json, random, sys
exec(open('exact.py').read().split('def best_colouring')[0])
k = int(sys.argv[1]); rng = random.Random(int(sys.argv[2]))
sets = cliques(k)
masks = [sum(1 << x for x in f) for f in sets]
by = [[] for _ in range(N)]
for i, f in enumerate(sets):
    for x in f: by[x].append(i)
target = N - (N % k)
def search(covered, chosen, depth=[0]):
    depth[0] += 1
    if depth[0] > 200000: return None
    free = [x for x in range(N) if not covered >> x & 1]
    if len(free) <= N % k:
        return list(chosen)
    x = min(free, key=lambda y: sum(1 for i in by[y] if not masks[i] & covered))
    opts = [i for i in by[x] if not masks[i] & covered]; rng.shuffle(opts)
    for i in opts:
        chosen.append(i)
        r = search(covered | masks[i], chosen)
        if r: return r
        chosen.pop()
    if N % k and len(free) > N % k:
        # allow x to be the leftover singleton(s)
        pass
    return None
# for k=3 one label stays single: try each candidate leftover
for left in ([None] if N % k == 0 else rng.sample(range(N), N)):
    cov = 0 if left is None else (1 << left)
    sol = search(cov, [])
    if sol:
        groups = [list(sets[i]) for i in sol] + ([[left]] if left is not None else [])
        json.dump(groups, open('init-k%d.json' % k, 'w')); print('found', len(groups), 'groups'); break
else:
    print('none')
