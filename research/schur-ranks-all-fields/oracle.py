"""Direct G G' subspace enumeration; pairing law is not used for optimization.

apoursh with substantial OpenAI Codex assistance; Apache-2.0.
The reduction and exhaustive sector-search approach credit Nick Petalas PR6031.
"""
from itertools import product


def install(algebra):
    """Explicitly bind the already source-loaded arithmetic module."""
    globals()["la"] = algebra


def embed(j, v, d):
    return tuple([0] * (j * d) + list(v) + [0] * ((2 - j) * d))


def profile(a, b, h, p):
    d = len(a)
    ts = la.compressed(a, b, h, p)
    g, gp = la.factor_maps(a, b, h, p)
    m = la.mul(g, gp, p)
    options = [la.choices(tuple(map(tuple, t)), p) for t in ts[1:]]
    nchoices = []
    for ns in product(*(o[1] for o in options)):
        nb = [embed(j, v, d) for j, space in enumerate(ns) for v in space]
        nchoices.append((ns, nb))
    base = la.rank(ts[0], p) + sum(d - la.rank(t, p) for t in ts[1:])
    best, witnesses, pairs = {}, {}, 0
    for iss in product(*(o[0] for o in options)):
        ib = [embed(j, v, d) for j, space in enumerate(iss) for v in space]
        mi = [la.apply(m, v, p) for v in ib]
        for ns, nb in nchoices:
            rho = la.rank(mi + nb, p) - len(nb)
            cost = base + len(ib) - len(nb)
            pairs += 1
            if cost < best.get(rho, 10**9):
                best[rho], witnesses[rho] = cost, (iss, ns)
    zero = la.zeros(d, d)
    tt = la.block([[ts[i + 1] if i == j else zero for j in range(3)]
                   for i in range(3)])
    rho0 = la.rank(la.mul(la.mul(tt, m, p), tt, p), p)
    return ts, best, witnesses, rho0, pairs
