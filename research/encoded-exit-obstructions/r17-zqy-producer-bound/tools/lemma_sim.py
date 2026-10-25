"""Randomized control for the potential lemma on 3 qubits: random straight-line programs with free monomial
ops, scalar ADDs and paid jobs (random Cliffords, any rank).  Checks dim S (span of values at non-base right-Mon
classes over all fields) never exceeds #jobs, and that the bound is attained by a constructive program."""
import random, sys, importlib.util
from fractions import Fraction as F
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import exit_lb as E          # reuses evaluator, cls(), qrank()
ce = E.ce; n = 3
def rmono():
    while True:
        G = tuple(random.randrange(1, 8) for _ in range(n))
        if ce.rank(list(G)) == n: break
    Qd = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            b = random.randrange(2); Qd[i][j] = Qd[j][i] = b
    Qr = tuple(sum(Qd[i][j] << j for j in range(n)) for i in range(n))
    alpha = tuple((Qd[i][i] + 2*random.randrange(2)) % 4 for i in range(n))
    return ce.perm(n, G).then(ce.diag(n, Qr, alpha)).then(ce.xgate(n, random.randrange(8))).then(ce.Op(n, ce.identity(n), [('phase', random.randrange(4))]))
def rjob():
    op = rmono()
    for _ in range(random.randrange(1, 4)): op = op.then(ce.cgate(n, 1 << random.randrange(n), random.choice((1, -1)))).then(rmono())
    return op
key = lambda o: (o.tab, repr(o.zero_state()))
def act(g, val):   # left multiplication of a formal value {key: (op, {var: coeff})}
    out = {}
    for op, vec in val.values():
        x = op.then(g); out[key(x)] = (x, dict(vec))
    return out
def add(a, b, c):
    out = {k: (o, dict(v)) for k, (o, v) in a.items()}
    for k, (o, v) in b.items():
        if k not in out: out[k] = (o, {})
        for var, x in v.items(): out[k][1][var] = out[k][1].get(var, 0) + c * x
    return out
def S_dim(fields):
    vals = []
    for f in fields:
        per = {}
        for op, vec in f.values():
            k = E.cls(op)
            if k == E_BASE: continue
            d = per.setdefault(k, {})
            for var, x in vec.items(): d[var] = d.get(var, 0) + x
        vals += list(per.values())
    return E.qrank(vals)
E.n = n; E_BASE = E.cls(ce.ident(n))
random.seed(17); worst = 0
for trial in range(300):
    V = random.randrange(2, 7)
    I = ce.ident(n); fields = [{key(I): (I, {v: F(1)})} for v in range(V)]
    jobs = 0
    for step in range(random.randrange(3, 14)):
        r = random.random()
        a = random.randrange(len(fields))
        if r < 0.35: fields.append(act(rmono(), fields[a]))
        elif r < 0.7: fields.append(add(fields[a], act(rmono(), fields[random.randrange(len(fields))]), F(random.choice((1, -1, 2)), random.choice((1, 2)))))
        else: fields.append(act(rjob(), fields[a])); jobs += 1
        s = S_dim(fields); assert s <= jobs, (trial, s, jobs); worst = max(worst, s - jobs)
print('300 random programs: max(dim S - #jobs) =', worst, '(lemma requires <= 0)')
# attainment: one job per variable on separate fields reaches dim S = V
I = ce.ident(n); fields = [{key(I): (I, {v: F(1)})} for v in range(4)]
fields += [act(rjob(), f) for f in list(fields)]
print('one job per variable: dim S =', S_dim(fields), 'with 4 jobs')
# negative control: if a rank-1 C gate were free, the potential can exceed the number of paid jobs
I = ce.ident(n); fields = [{key(I): (I, {v: F(1)})} for v in range(4)]
fields += [act(ce.cgate(n, 1), f) for f in list(fields)]
print('mutation (C gate treated as free): dim S =', S_dim(fields), 'with 0 paid jobs (lemma would be violated)')
