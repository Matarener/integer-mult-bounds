"""Sign step of T1 with ordered (mu) parity facts, for the types where the unordered sign model of sign_cnf.py is SAT.
Arc values mu(x->y) = M x y / M x x.  For dead rows t ⊥ s and a frame inside the dead set whose only lines not
orthogonal to both are a, b, the frame expansion of A_t . B_s = 0 gives the ordered relation
  mu(t->a) mu(a->s) = - mu(t->b) mu(b->s),
and mu(x->y) mu(y->x) = N{x,y}.  An integer combination  sum_i a_i r_i + sum_e c_e sym_e  with zero exponent on every
arc (r_i = ordered relation exponent vectors, sym_e = (x->y)+(y->x)) gives  (-1)^(sum a_i) prod_e N_e^(c_e) = 1, and
since N_e^2 is 1/16 or 1/4 (moduli step) this is the parity fact  sum_{c_e odd} sigma_e = sum a_i (mod 2).
All arcs used lie on cover pairs (N != 0 there, so every mu is nonzero).  The integer lattice of such combinations is
computed by an exact echelon over the arc coordinates with tracked combinations; every lattice row turns out to have
exactly two odd pairs (an XOR of two signs), giving two clauses each.  These clauses are added to the CNF of
sign_cnf.py.  usage: mu_cnf.py rep moduli.json out.cnf out.json"""
import sys, json, os, math
_argv = list(sys.argv); k = int(_argv[1])
sys.argv = ['sign_cnf.py', str(k), _argv[2], _argv[3] + '.base', _argv[4] + '.base']
exec(open('sign_cnf.py').read())
os.remove(_argv[3] + '.base'); os.remove(_argv[4] + '.base')
sys.argv = _argv; outc, outj = _argv[3], _argv[4]
covc = set(c for q in Q for c in q[3])
def arc(x, y): return 104 * x + y
# ordered relations with all four pairs in the cover
OR = []; seen = set()
for fi in FZ:
    F = FR[fi]
    for t in Z:
        if t in F: continue
        ks = [j for j in range(8) if not ORTH[t][F[j]]]
        for s in Z:
            if s == t or s in F or not ORTH[t][s]: continue
            com = [j for j in ks if not ORTH[s][F[j]]]
            if len(com) != 2: continue
            ka, kb = com; a, b = F[ka], F[kb]
            if not all(code(x, y) in covc for x, y in ((t, a), (a, s), (t, b), (b, s))): continue
            key = (arc(t, a), arc(a, s), arc(t, b), arc(b, s))
            if key in seen: continue
            seen.add(key); OR.append((t, s, fi, ka, kb, key))
covl = sorted(covc)
# echelon over integer vectors: keys int >= 0 are arcs (eliminated), ('v',) value, ('p', c) sigma coordinate of pair c,
# ('g', i) ordered relation i, ('h', c) 2*sym of pair c, ('s', c) sym of pair c (tracked combination)
def eg(a, b):
    if b == 0: return (1, 0)
    q, r = divmod(a, b); s, t = eg(b, r); return (t, s - q * t)
piv = {}; Krows = []
def lead(v):
    ks = [x for x in v if type(x) is int]
    return max(ks) if ks else None
def add(v):
    while True:
        h = lead(v)
        if h is None:
            if any(x[0] in 'vp' and c for x, c in v.items() if type(x) is tuple): Krows.append(v)
            return
        if v[h] < 0: v = {j: -c for j, c in v.items()}
        if h not in piv: piv[h] = v; return
        p = piv[h]; a, b = p[h], v[h]
        if b % a == 0:
            f = b // a
            for j, c in p.items():
                nv = v.get(j, 0) - f * c
                if nv: v[j] = nv
                else: v.pop(j, None)
        else:
            g = math.gcd(a, b); x, y = eg(a, b); keys = set(p) | set(v)
            newp = {j: x * p.get(j, 0) + y * v.get(j, 0) for j in keys}
            other = {j: (b // g) * p.get(j, 0) - (a // g) * v.get(j, 0) for j in keys}
            piv[h] = {j: c for j, c in newp.items() if c}; v = {j: c for j, c in other.items() if c}
for i, (t, s, fi, ka, kb, key) in enumerate(OR):
    v = {('v',): 1, ('g', i): 1}
    for j, c in zip(key, (1, 1, -1, -1)): v[j] = v.get(j, 0) + c
    add({j: c for j, c in v.items() if c})
for c in covl:
    x, y = c // 104, c % 104
    add({arc(x, y): 2, arc(y, x): 2, ('h', c): 1})
    add({arc(x, y): 1, arc(y, x): 1, ('p', c): 1, ('s', c): 1})
# K rows (arc part zero): parity facts
xors = []; nskip = 0
for v in Krows:
    odd = sorted(x[1] for x, c in v.items() if type(x) is tuple and x[0] == 'p' and c % 2)
    A = v.get(('v',), 0)
    symc = {}
    for x, c in v.items():
        if type(x) is tuple and x[0] in 'hs': symc[x[1]] = symc.get(x[1], 0) + (2 * c if x[0] == 'h' else c)
    assert sorted(c for c, e in symc.items() if e % 2) == odd
    # check: arc exponents of the combination vanish
    ex = {}
    for x, c in v.items():
        if type(x) is tuple and x[0] == 'g':
            for j, e in zip(OR[x[1]][5], (1, 1, -1, -1)): ex[j] = ex.get(j, 0) + c * e
    for cc, e in symc.items():
        for j in (arc(cc // 104, cc % 104), arc(cc % 104, cc // 104)): ex[j] = ex.get(j, 0) + e
    assert all(e == 0 for e in ex.values())
    if not odd:
        assert A % 2 == 0, 'inconsistent parity fact'
        continue
    if len(odd) > 4: nskip += 1; continue
    terms_o = [[x[1], c] for x, c in v.items() if type(x) is tuple and x[0] == 'g']
    terms_s = [[cc, symc[cc]] for cc in odd] + [[cc, e] for cc, e in sorted(symc.items()) if e % 2 == 0 and e]
    xi = len(xors); xors.append({'o': terms_o, 's': terms_s, 'L': len(odd), 'A': A})
    for p in range(1 << len(odd)):
        if (bin(p).count('1') + A) % 2 == 1:
            cls.append([(cc + 1) if p >> i & 1 == 0 else -(cc + 1) for i, cc in enumerate(odd)]); org.append(['x', xi, p])
# keep the goal clause last
gi = [i for i, o in enumerate(org) if o[0] == 'g'][0]
cls.append(cls.pop(gi)); org.append(org.pop(gi))
with open(outc, 'w') as f:
    f.write('p cnf %d %d\n' % (TAG + nK, len(cls)))
    for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
json.dump({'rep': k, 'classes': qroots, 'origin': org,
           'quads': [[t, fi] + ks + [entry[c] for c in cs] + [Kof[root[cs[0]]]] for (t, fi, ks, cs) in Q],
           'rels': [[t, s, fi, ka, kb] + [entry[c] for c in rc] + [Kof[root[c]] for c in rc] for (t, s, fi, ka, kb, rc) in R],
           'ords': [list(o[:5]) for o in OR], 'xors': xors}, open(outj, 'w'))
print('rep %d ordered relations %d lattice rows %d parity facts %d (skipped long %d) max terms %d clauses %d' %
      (k, len(OR), len(Krows), len(xors), nskip, max((len(x['o']) + len(x['s']) for x in xors), default=0), len(cls)), flush=True)
