"""Exact extracted E8 root enumeration; Apache-2.0; substantial Codex assistance."""
from itertools import combinations, product

def need(ok, label):
    if not ok: raise ValueError(label)

def canonical_roots():
    roots = []
    for i,j in combinations(range(8),2):
        for x,y in product((-2,2),repeat=2):
            a = [0]*8; a[i],a[j] = x,y; roots.append(tuple(a))
    roots.extend(a for a in product((-1,1),repeat=8) if sum(a) % 4 == 0)
    return sorted({a if next(x for x in a if x) > 0 else tuple(-x for x in a) for a in roots})
