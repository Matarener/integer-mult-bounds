"""T3.4 gluing scan (real data).  For every type: good pairs (pair certificate exists), A2 relation G3 = 0
(Gram determinant of three roots), (M) bad pairs form a matching off the special line, (P) no two A2 triples share
two lines inside O, and for every 5-set {a, a', b, b', e} with two bad pairs a plan: a good independent triangle and
joins (good pair with non-A2 triple) covering a 4-subset."""
import sys, json, itertools, time
sys.path.insert(0, '.')
from p104lib import P, RT, N as NL
d = json.load(open(sys.argv[1]))
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
DROP = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}
def dot(a, b): return sum(x * y for x, y in zip(RT[P[a]], RT[P[b]]))
def G3(a, b, c):
    x, y, z = dot(a, b), dot(a, c), dot(b, c)
    return 5832 + 2 * x * y * z - 18 * (x * x + y * y + z * z)
T0 = time.time(); res = {}
for k in range(387):
    m = int(reps[k]['mask']); Z = [i for i in range(NL) if m >> i & 1]
    if k in DROP: Z = [i for i in Z if i != DROP[k]]
    O = [v for v in range(NL) if v not in set(Z)]
    bad = set(tuple(sorted(p)) for p in d[str(k)]['badp']); u = d[str(k)]['badl']
    good = lambda x, y: tuple(sorted((x, y))) not in bad
    # (P) inside O
    a2 = [t for t in itertools.combinations(O, 3) if G3(*t) == 0]
    Pok = all(len(set(s) & set(t)) <= 1 for s, t in itertools.combinations(a2, 2))
    badu = [p for p in bad if not (u and u[0] in p)]
    from collections import Counter
    Mok = max(Counter(x for p in badu for x in p).values(), default=0) <= 1
    fails = 0; n5 = 0
    for p, q in itertools.combinations(badu, 2):
        for e in O:
            if e in p or e in q or (u and e == u[0]): continue
            S = list(p) + list(q) + [e]; n5 += 1
            ok = False
            for S4 in itertools.combinations(S, 4):
                for T in itertools.combinations(S4, 3):
                    if not (all(good(x, y) for x, y in itertools.combinations(T, 2)) and G3(*T)): continue
                    w = [v for v in S4 if v not in T][0]
                    if any(good(w, x) and good(w, y) and good(x, y) and G3(w, x, y) for x, y in itertools.combinations(T, 2)):
                        ok = True; break
                if ok: break
            if not ok: fails += 1
    res[k] = {'P': Pok, 'M': Mok, 'n5': n5, 'fail5': fails, 'nA2': len(a2)}
    print('[%6.1fs] type %d |O| %d A2 %d (P) %s (M) %s 5-sets %d failing %d' % (time.time() - T0, k, len(O), len(a2), Pok, Mok, n5, fails), flush=True)
json.dump(res, open(sys.argv[2], 'w'))
