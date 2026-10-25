"""Source-faithful standard-library geometry adaptation for the C03 Pauli audit.

Frozen source hashes and the literal adaptations are recorded in ORIGINS.json.
No historical module imports, ambient repository reads, NumPy or Git calls.
Substantial OpenAI Codex assistance; inherited source attribution is preserved.
"""
from itertools import combinations, product
H=17
FULL=tuple(1 << i for i in reversed(range(H)))

def need(ok, label):
    if not ok: raise ValueError(label)

def basis(words):
    piv = {}
    for v in words:
        for k in sorted(piv, reverse=True):
            if v >> k & 1: v ^= piv[k]
        if v:
            k = v.bit_length()-1
            for j in list(piv):
                if piv[j] >> k & 1: piv[j] ^= v
            piv[k] = v
    return tuple(piv[k] for k in sorted(piv, reverse=True))

def included(a,b): return len(basis(a+b)) == len(b)

def perp(v):
    k = (v & -v).bit_length()-1
    return basis((1 << i) ^ ((1 << k) if v >> i & 1 else 0) for i in range(H) if i != k)

def mm(a,b):
    return [xor(b[j] for j in range(len(b)) if row >> j & 1) for row in a]

def xor(xs):
    z = 0
    for x in xs: z ^= x
    return z

def tr(a,n): return [sum(((row >> j) & 1) << i for i,row in enumerate(a)) for j in range(n)]

def inv(a):
    n = len(a); work = [row | (1 << (n+i)) for i,row in enumerate(a)]
    for j in range(n):
        p = next(i for i in range(j,n) if work[i] >> j & 1)
        work[j],work[p] = work[p],work[j]
        for i in range(n):
            if i != j and work[i] >> j & 1: work[i] ^= work[j]
    need([r & ((1<<n)-1) for r in work] == [1<<i for i in range(n)], "binary inverse")
    return [r >> n for r in work]

def cong(t,m): return mm(mm(t,m),tr(t,len(t)))

def symp(m):
    n = len(m); t = [1<<i for i in range(n)]; work = list(m)
    for k in range(0,n,2):
        a,b = next((a,b) for a in range(k,n) for b in range(k,n) if work[a] >> b & 1)
        for cur,dst in ((a,k),(b if b != k else a,k+1)):
            t[cur],t[dst] = t[dst],t[cur]
        work = cong(t,m)
        for i in range(k+2,n):
            left,right = (work[i] >> (k+1)) & 1,(work[i] >> k) & 1
            if left: t[i] ^= t[k]
            if right: t[i] ^= t[k+1]
        work = cong(t,m)
    need(work == [1 << (i^1) for i in range(n)], "symplectic congruence")
    return t

def canonical_roots():
    roots = []
    for i,j in combinations(range(8),2):
        for x,y in product((-2,2),repeat=2):
            a = [0]*8; a[i],a[j] = x,y; roots.append(tuple(a))
    roots.extend(a for a in product((-1,1),repeat=8) if sum(a) % 4 == 0)
    return sorted({a if next(x for x in a if x) > 0 else tuple(-x for x in a) for a in roots})

def dot(a,b):
    z = sum(x*y for x,y in zip(a,b))
    need(z % 4 == 0, "integral E8 pairing")
    return z//4

def packed_root_pairs(roots):
    # Same exact lattice-to17-bit fit as mixed_rectangle.actual_labels,
    # but without its quadratic all-pairs diagnostic on the whole domain.
    gram = [sum((dot(a,c)&1) << j for j,c in enumerate(roots)) for a in roots]
    work = list(gram)
    available, selected = list(range(120)), []
    while any(work[a] >> c & 1 for a in available for c in available):
        a,c = next((a,c) for a in available for c in available if work[a] >> c & 1)
        selected.extend((a,c))
        left, right = work[a], work[c]
        work = [row ^ (right if left >> i & 1 else 0)
                    ^ (left if right >> i & 1 else 0)
                for i,row in enumerate(work)]
        available.remove(a)
        available.remove(c)
    small = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(selected))
             for i in selected]
    inverse = inv(small)
    form = inverse+[row << 8 for row in inverse]
    even = [((1 << 16)-1) ^ (1 << i) for i in range(16)]
    change = mm(inv(symp(form)), symp(even))
    need(cong(change, even) == form, 'pinned standard-dot isometry')
    mapping = mm(change, [(1 << i)|(1 << 16) for i in range(16)])
    coordinates = [sum(((gram[i] >> j)&1) << k for k,j in enumerate(selected))
                   for i in range(120)]
    return [[((1 << 17)-1) ^ mm([x|(y << 8)], mapping)[0]
             for y in coordinates] for x in coordinates]

def orthogonal_involution(roots):
    position = {a:i for i,a in enumerate(roots)}
    mates = []
    for a in roots:
        c = list(a)
        if all(x % 2 == 0 for x in a):
            nonzero = [i for i,x in enumerate(a) if x]
            c[nonzero[1]] *= -1
        else:
            for i in range(4,8):
                c[i] *= -1
        mates.append(position[tuple(c)])
    need(all(i != j and mates[j] == i and dot(roots[i], roots[j]) == 0
             for i,j in enumerate(mates)), 'explicit120-root orthogonal involution')
    pairs = [(i,j) for i,j in enumerate(mates) if i < j]
    need(len(pairs) == 60, 'sixty orthogonal b-pairs')
    return pairs
