import random, sys, json
exec(open('frames.py').read().split('# Algorithm X')[0])
masks = [sum(1 << x for x in f) for f in frames]
rng = random.Random(int(sys.argv[1]))
best = 0; bestsel = None
for t in range(int(sys.argv[2])):
    order = list(range(len(frames))); rng.shuffle(order)
    used = 0; sel = []
    for k in order:
        if not masks[k] & used:
            used |= masks[k]; sel.append(k)
    if len(sel) > best:
        best, bestsel = len(sel), sel
        print('packing', best, flush=True)
print('max greedy packing', best)
json.dump([frames[k] for k in bestsel], open('packing-%s.json' % sys.argv[1], 'w'))
