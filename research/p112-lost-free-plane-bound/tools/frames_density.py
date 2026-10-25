import json, itertools, random, sys
from density import max_lostfree, q, dot
F = json.load(open("frames12.json"))
rng = random.Random(1)
for k in (2, 3, 4):
    seen = set()
    for combo in rng.sample(list(itertools.combinations(range(12), k)), min(6, len(list(itertools.combinations(range(12), k))))):
        C = [a for i in combo for a in F[i]]
        lo, hi, st = max_lostfree(C, seconds=60)
        print("frames %d (|C|=%d): max lost-free [%d,%d] %s density %.3f" % (k, len(C), lo, hi, st, hi / len(C)), flush=True)
