# COVERSAT stage-2 no-goods from Nullstellensatz certificates (stdlib).
# A candidate (patterns S_0..S_{m-1}, one row-mask list per term) restricted to a set of masked cells C is refuted when the exact-support
# system  sum_{k covers (t,s)} q_k(t) p_k(s) - delta_ts = 0  (gauge: p_k = 1 at the first column of term k met in C; every variable
# invertible: v*w - 1 = 0) has 1 in its ideal, i.e. sum_i cof_i * eq_i = 1.  check_cert() rebuilds the system from (orbit, pats, cells)
# and checks that identity with exact Fraction polynomial arithmetic.  The no-good is the clause "not (the pattern on C)", applied to
# every image under Aut(B) x transpose x reorderings of equal-size terms (all symmetries of the shard).
import re, itertools
from fractions import Fraction
from lib import orbit, aut
def system(o, pats, cells):
    T, B = orbit(o); Q = {}; P = {}; names = []; gauged = set()
    def nv(): names.append('x(%d)' % (len(names) + 1)); return names[-1]
    for (t, s) in sorted(cells, key=lambda x: (x[1], x[0])):
        for k, S in enumerate(pats):
            if not S[t] >> s & 1: continue
            if (k, t) not in Q: Q[k, t] = nv()
            if (k, s) not in P:
                if k not in gauged: P[k, s] = '1'; gauged.add(k)
                else: P[k, s] = nv()
    eqs = []
    for (t, s) in cells:
        terms = ['%s*%s' % (Q[k, t], P[k, s]) for k, S in enumerate(pats) if S[t] >> s & 1]
        e = '+'.join(terms) if terms else '0'
        if t == s: e += '-1'
        if e != '0': eqs.append(e)
    base = list(names)
    for v in base: w = nv(); eqs.append('%s*%s-1' % (v, w))
    return names, eqs
# ---- polynomials: dict {tuple of sorted (var, exp)} -> Fraction
def padd(a, b, sgn=1):
    r = dict(a)
    for m, c in b.items():
        r[m] = r.get(m, 0) + sgn * c
        if r[m] == 0: del r[m]
    return r
def pmul(a, b):
    r = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            d = dict(m1)
            for v, e in m2: d[v] = d.get(v, 0) + e
            m = tuple(sorted(d.items())); r[m] = r.get(m, 0) + c1 * c2
            if r[m] == 0: del r[m]
    return r
def parse(s):
    toks = re.findall(r'x\(\d+\)|\d+|[()+\-*^]', s.replace(' ', '')); pos = [0]
    def peek(): return toks[pos[0]] if pos[0] < len(toks) else None
    def nxt(): pos[0] += 1; return toks[pos[0] - 1]
    def atom():
        t = nxt()
        if t == '(': v = expr(); assert nxt() == ')'; r = v
        elif t == '-': r = padd({}, atom(), -1)
        elif t.startswith('x'): r = {((int(t[2:-1]),1),): Fraction(1)}
        else: r = {(): Fraction(int(t))}
        while peek() == '^':
            nxt(); e = int(nxt()); b = r; r = {(): Fraction(1)}
            for _ in range(e): r = pmul(r, b)
        return r
    def term():
        v = atom()
        while peek() == '*': nxt(); v = pmul(v, atom())
        return v
    def expr():
        v = term()
        while peek() in ('+', '-'):
            op = nxt(); w = term(); v = padd(v, w, 1 if op == '+' else -1)
        return v
    v = expr(); assert pos[0] == len(toks), s
    return v
def check_cert(o, pats, cells, cert):
    names, eqs = system(o, pats, [tuple(c) for c in cells])
    assert eqs == cert['eqs'] and names == cert['vars'], 'certificate system differs from the rebuilt exact-support system'
    tot = {}
    for c, e in zip(cert['cof'], cert['eqs']): tot = padd(tot, pmul(parse(c), parse(e)))
    return tot == {(): Fraction(1)}
def core_images(o, lam, pats, cells):
    T, B = orbit(o); G = aut([[int(x) for x in r] for r in B]); out = set()
    blocks = [[k for k in range(len(lam)) if lam[k] == r] for r in sorted(set(lam), reverse=True)]
    for g in G:
        for tr in (0, 1):
            mp = (lambda t, s: (g[t], g[s])) if not tr else (lambda t, s: (g[s], g[t]))
            for perms in itertools.product(*[itertools.permutations(b) for b in blocks]):
                order = [k for pb in perms for k in pb]; lits = []
                for j, k in enumerate(order):
                    for (t, s) in cells:
                        t2, s2 = mp(t, s); v = 1 + 64 * j + 8 * t2 + s2
                        lits.append(v if pats[k][t] >> s & 1 else -v)
                out.add(tuple(sorted(lits)))
    return sorted(out)
