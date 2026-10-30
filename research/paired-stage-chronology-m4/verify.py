"""Exact minimum paired-stage loss under the mixed chronology cut at m = 4.

Model: Ali Romman's PR #5631 binary normalized paired-stage controller
(n = 2m - 2 fields, L = 2m rank-one square-zero queries, two calls per stage).
For every query Gram system K, every stage pairing and every compatible
rank-two projector choice this computes the largest total target rank
sum r_c subject to: pair commutation (E_c idempotent), pairwise commuting
targets, and the mixed coefficient cut (*) of PR #5631 Section 4.
D = 4m - sum r_c. Standard library only. Produced by Nick Petalas. Apache-2.0.
"""
import argparse, hashlib, itertools, json, os, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
H = 2  # rank of I - K: L = n + 2


def need(c, msg):
    if not c:
        raise AssertionError(msg)


def dot(a, b):
    return bin(a & b).count('1') & 1


def outer(u, v, n):
    return tuple(v if u >> i & 1 else 0 for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def table(b, n):
    t = [0] * (1 << n)
    for x in range(1, 1 << n):
        lo = x & -x
        t[x] = t[x ^ lo] ^ b[lo.bit_length() - 1]
    return t


def mul(a, b, n):
    tb = table(b, n)
    return tuple(tb[x] for x in a)


def rank(a):
    piv = {}
    for x in a:
        while x:
            i = x.bit_length() - 1
            if i not in piv:
                piv[i] = x
                break
            x ^= piv[i]
    return len(piv)


def gram_systems(L):
    """All L x L idempotents K = I + XY over F2 with zero diagonal, rank(XY) = 2."""
    pairs = [(x, y) for x in range(1, 1 << H) for y in range(1 << H) if dot(x, y)]
    ks = set()
    for seq in itertools.product(pairs, repeat=L):
        m = [0] * H
        for x, y in seq:
            for a in range(H):
                if y >> a & 1:
                    m[a] ^= x
        if m != [1 << a for a in range(H)]:
            continue
        ks.add(tuple((1 << i) ^ sum(dot(seq[i][0], seq[j][1]) << j
                                    for j in range(L)) for i in range(L)))
    return sorted(ks)


def reverse_transpose(k):
    L = len(k)
    return tuple(sum((k[L - 1 - j] >> (L - 1 - i) & 1) << j for j in range(L))
                 for i in range(L))


def orbit_reps(ks):
    kset = set(ks)
    reps = []
    for k in ks:
        r = reverse_transpose(k)
        need(r in kset, 'reversal closure')
        if k <= r:
            reps.append((k, 1 if k == r else 2))
    return reps


def field_frame(k):
    """Return (u_i, v_i) with sum u_i v_i = I_n and v_i u_j = K[i][j]."""
    L = len(k)
    n = L - H
    cols = [sum((k[r] >> c & 1) << r for r in range(L)) for c in range(L)]
    piv = {}
    basis = []

    def reduce(x):
        co = 0
        for i in sorted(piv, reverse=True):
            if x >> i & 1:
                x ^= piv[i][0]
                co ^= piv[i][1]
        return x, co
    for c in cols:
        red, co = reduce(c)
        if red:
            piv[red.bit_length() - 1] = (red, co ^ (1 << len(basis)))
            basis.append(c)
    need(len(basis) == n, 'rank n')
    us = []
    for c in cols:
        red, co = reduce(c)
        need(red == 0, 'column in span')
        us.append(co)
    vs = [sum((basis[q] >> i & 1) << q for q in range(n)) for i in range(L)]
    for i in range(L):
        for j in range(L):
            need(dot(vs[i], us[j]) == (k[i] >> j & 1), 'Gram')
    return n, us, vs


def stage_candidates(n, us, vs):
    """For each ordered call pair i<j: {E: rank E} over commuting compatible
    projectors P_i, P_j with [P_i, S_i] = [P_j, S_j], S_i = sum_{l>i} R_l."""
    L = len(us)
    zero = (0,) * n
    tails = [zero] * L
    t = zero
    for i in reversed(range(L)):
        tails[i] = t
        t = add(t, outer(us[i], vs[i], n))
    need(t == tuple(1 << i for i in range(n)), 'sum R = I')
    groups = []
    for i in range(L):
        u, v, s = us[i], vs[i], tails[i]
        ts = table(s, n)
        su = sum(dot(s[r], u) << r for r in range(n))
        vs_ = 0
        for q in range(n):
            if v >> q & 1:
                vs_ ^= s[q]
        g = {}
        for a in range(1 << n):
            if not dot(v, a):
                continue
            sa = sum(dot(s[r], a) << r for r in range(n))
            base = add(outer(a, vs_, n), outer(sa, v, n))
            av = outer(a, v, n)
            for b in range(1 << n):
                if not dot(b, u) or dot(b, a):
                    continue
                bs = ts[b]
                p = add(outer(u, b, n), av)
                comm = add(add(base, outer(u, bs, n)), outer(su, b, n))
                g.setdefault(comm, {})[p] = None
        groups.append(g)
    out = {}
    for i, j in itertools.combinations(range(L), 2):
        es = {}
        for key, pis in groups[i].items():
            pjs = list(groups[j].get(key, ()))
            if not pjs:
                continue
            tjs = [table(p, n) for p in pjs]
            for pi in pis:
                ti = table(pi, n)
                for pj, tj in zip(pjs, tjs):
                    if tuple(tj[x] for x in pi) == tuple(ti[x] for x in pj):
                        e = add(pi, pj)
                        if e not in es:
                            es[e] = (rank(e), pi, pj)
        out[(i, j)] = es
    return out


def pairings(rem):
    if not rem:
        yield []
        return
    a = rem[0]
    for q in range(1, len(rem)):
        for rest in pairings(rem[1:q] + rem[q + 1:]):
            yield [(a, rem[q])] + rest


def best(n, L, cands):
    lists = {p: sorted(((r[0], e, table(e, n), r) for e, r in d.items()),
                       key=lambda z: -z[0]) for p, d in cands.items()}
    top = [-1, None]

    def bt(ls, k, chosen, s, pr):
        if s + 4 * (len(ls) - k) <= top[0]:
            return
        if k == len(ls):
            top[0] = s
            top[1] = (pr, [c[2] for c in chosen])
            return
        for r, e, te, info in ls[k]:
            if all(tuple(te[x] for x in f) == tuple(tf[x] for x in e)
                   for f, tf, _ in chosen):
                chosen.append((e, te, info))
                bt(ls, k + 1, chosen, s + r, pr)
                chosen.pop()
    for pr in pairings(list(range(L))):
        ls = [lists[p] for p in pr]
        if all(ls):
            bt(ls, 0, [], 0, pr)
    return top


def solve(k):
    L = len(k)
    n, us, vs = field_frame(k)
    top = best(n, L, stage_candidates(n, us, vs))
    return None if top[0] < 0 else 2 * L - top[0]


def census(L, shard, shards, jobs):
    reps = orbit_reps(gram_systems(L))
    mine = [r for idx, r in enumerate(reps) if idx % shards == shard]
    with Pool(jobs) as pool:
        ds = pool.map(solve, [k for k, _ in mine], chunksize=8)
    hist = {}
    weighted = {}
    for (k, w), d in zip(mine, ds):
        key = 'none' if d is None else str(d)
        hist[key] = hist.get(key, 0) + 1
        weighted[key] = weighted.get(key, 0) + w
    h = hashlib.sha256(json.dumps([[list(k), d] for (k, _), d in zip(mine, ds)]).encode()).hexdigest()
    return dict(L=L, shard=shard, shards=shards, systems=len(mine),
                reps_hist=dict(sorted(hist.items())), systems_hist=dict(sorted(weighted.items())),
                sha256=h)


def load_mixed():
    sys.path.insert(0, os.path.join(HERE, '..', 'paired-stage-chronology-cut'))
    import chronology
    return chronology


def witness_check(k):
    """Rebuild one optimal word and check it with PR #5631's own mixed routine."""
    L = len(k)
    n, us, vs = field_frame(k)
    top = best(n, L, stage_candidates(n, us, vs))
    pr, infos = top[1]
    ps = [None] * L
    labels = [None] * L
    for c, ((i, j), (r, pi, pj)) in enumerate(zip(pr, infos)):
        ps[i], ps[j] = list(pi), list(pj)
        labels[i] = labels[j] = c
    for i in range(L):
        p = tuple(ps[i])
        r = outer(us[i], vs[i], n)
        need(mul(p, p, n) == p and rank(p) == 2, 'rank-two idempotent')
        need(mul(p, r, n) == r and mul(r, p, n) == r, 'compatible')
        need(dot(vs[i], us[i]) == 0, 'square zero')
    es = []
    for c in range(L // 2):
        i, j = pr[c]
        e = add(tuple(ps[i]), tuple(ps[j]))
        need(mul(e, e, n) == e, 'stage idempotent')
        es.append(e)
    for e, f in itertools.combinations(es, 2):
        need(mul(e, f, n) == mul(f, e, n), 'commuting targets')
    chron = load_mixed()
    cand = dict(n=n, u=list(us), v=list(vs))
    need(chron.mixed(cand, ps, labels) == {}, 'PR5631 mixed coefficient')
    d = 2 * L - sum(rank(e) for e in es)
    # control: exchanging the first two calls changes chronology and must
    # break the mixed coefficient for some stage.
    sw = [1, 0] + list(range(2, L))
    bad = dict(n=n, u=[us[i] for i in sw], v=[vs[i] for i in sw])
    broke = chron.mixed(bad, [ps[i] for i in sw], [labels[i] for i in sw]) != {}
    # reversal symmetry (Lemma 2): reversing the call order keeps every
    # mixed coefficient because [P_i, sum_{j<i} R_j] = [P_i, sum_{j>i} R_j].
    rev = dict(n=n, u=list(reversed(us)), v=list(reversed(vs)))
    need(chron.mixed(rev, list(reversed(ps)), list(reversed(labels))) == {}, 'reversal lemma')
    return d, [list(p) for p in pr], [sorted(rank(e) for e in es)], broke


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--m', type=int, default=4)
    ap.add_argument('--shard', type=int)
    ap.add_argument('--shards', type=int, default=7)
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--print', action='store_true')
    a = ap.parse_args()
    result = json.load(open(os.path.join(HERE, 'RESULT.json')))
    if a.shard is None:
        small = census(6, 0, 1, a.jobs)
        need(small['systems_hist'] == result['m3_control']['systems_hist'], 'm=3 census')
        need(min(int(x) for x in small['systems_hist'] if x != 'none') == 0, 'm=3 positive control D=0')
        w = result['m4_witness']
        d, pr, ranks, broke = witness_check(tuple(w['K']))
        need(d == w['D'] == result['m4_min_D'], 'witness D')
        need(pr == w['pairing'] and ranks == w['ranks'], 'witness shape')
        need(broke, 'reversed-order control must fail')
        need(sum(result['m4_systems_hist'].values()) == 35008, 'system count')
        print('PASS_PAIRED_STAGE_CHRONOLOGY_M4_WITNESS', json.dumps(dict(D=d, pairing=pr, ranks=ranks)))
        return
    res = census(2 * a.m, a.shard, a.shards, a.jobs)
    if a.print:
        print(json.dumps(res, sort_keys=True))
        return
    need(res == result['m4_shards'][a.shard], 'shard %d differs from RESULT.json' % a.shard)
    print('PASS_PAIRED_STAGE_CHRONOLOGY_M4_SHARD', a.shard, json.dumps(res['systems_hist'], sort_keys=True))


if __name__ == '__main__':
    main()
