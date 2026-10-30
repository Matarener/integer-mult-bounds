"""JOINTFRAMES: per helper of a realised word, junk column J_h (adjoint to Y finals, load-free program) support size and first-use frame dim."""
import sys, collections
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import late
from fractions import Fraction as Q
def junkcols(path):
    import dag as D
    w = D.load(path); dg = D.decompile(w, forms=False); meta = dg['meta']; n = meta['npub']
    role = D.role_fn(w); dim = [len(b) for b in w['frames']]; ops = dg['ops']
    # load = ADD into Y at dim 0 from a helper (pure junk loads)
    body = [i for i, o in enumerate(ops) if not (o[0] == 'ADD' and o[1] < n and role(o[1]) == 'Y' and dim[o[4]] == 0)]
    first = {}
    for i in body:
        o = ops[i]
        for r in ((o[1], o[2]) if o[2] is not None else (o[1],)):
            if r < n and role(r) == 'helper' and r not in first: first[r] = i
    a = collections.defaultdict(dict)
    for r in range(n):
        if role(r) == 'Y': a[r] = {r: Q(1)}
    J = {}
    for i in reversed(body):
        o = ops[i]; op, r, s, q = o[0], o[1], o[2], o[3]
        if op == 'ADD':
            if a[r]:
                d = a[s]; qq = Q(q)
                for k, x in a[r].items():
                    t = d.get(k, 0) + qq * x
                    if t: d[k] = t
                    else: d.pop(k, None)
        elif op == 'COPY':
            d = a[s]; qq = Q(q)
            for k, x in a[r].items():
                t = d.get(k, 0) + qq * x
                if t: d[k] = t
                else: d.pop(k, None)
            a[r] = {}
        elif op == 'SCALE': a[r] = {k: x * Q(q) for k, x in a[r].items()}
        elif op in ('INIT', 'CLEAR'): a[r] = {}
    for h in first: J[h] = dict(a[h])
    return w, dg, ops, first, J, dim
if __name__ == '__main__':
    w, dg, ops, first, J, dim = junkcols(sys.argv[1])
    c = collections.Counter(); byd = collections.defaultdict(collections.Counter)
    for h, i in first.items():
        s = len(J[h]); d = dim[ops[i][4]]
        c[min(s, 9)] += 1; byd[d][min(s, 9)] += 1
    print('supp |J_h| hist', sorted(c.items()))
    for d in sorted(byd): print(' first-use dim', d, sorted(byd[d].items()))
