"""Simulate RankNine.Moduli.run on a certificate (same semantics as the Lean checker) and check quadruple facts."""
import json, sys
d = json.load(open(sys.argv[1])); rels = [tuple(r) for r in d['rels']]; cov = set(d['cov'])
def orient(o, r):
    x, p, y, q = r
    return [(x, p, y, q), (p, x, y, q), (x, p, q, y), (p, x, q, y), (y, q, x, p), (q, y, x, p), (y, q, p, x), (q, y, p, x)][o % 8]
def g(l, i, dflt): return l[i] if 0 <= i < len(l) else dflt
facts = []
for s in d['steps']:
    t = s[0]
    if t == 0:
        _, i, j, oi, oj = s; x, p, y, q = orient(oi, g(rels, i, (0,) * 4)); x2, q2, y2, p2 = orient(oj, g(rels, j, (0,) * 4))
        assert (x2, q2, y2, p2) == (x, q, y, p) and p in cov and q in cov; facts.append((x, y))
    elif t == 1:
        _, i, o, kk = s; x, p, y, q = orient(o, g(rels, i, (0,) * 4)); u, v = g(facts, kk, (0, 0))
        assert (u, v) == (x, y) and x in cov; facts.append((p, q))
    elif t == 2:
        _, kk, l = s; u, v = g(facts, kk, (0, 0)); v2, w = g(facts, l, (0, 0)); assert v2 == v; facts.append((u, w))
    else:
        _, kk = s; u, v = g(facts, kk, (0, 0)); facts.append((v, u))
for q, qf in zip(d['quads'], d['quadfacts']):
    r = qf[0]
    for c, fi in zip(q, qf[1:]):
        assert (c == r and fi == -1) or facts[fi] == (r, c)
print('SIM OK', len(facts), 'facts')
