# T1 (hand route) certificate emitter: copy of kaggle-t2close/emitcert.py with (i) descriptors of rules (a), (b), (c)
# (Lean T1Glue.rs1OK: relOf / rel2Of / rel3Of, inverses by opp), (ii) no diagonal gauge edge.
# Original header:
# Certificate emitter for the Lean checker RankNine/T2Close.lean (T2.3 exact closure).
# Same closure as closure2.py, in "strict" form (an equation's unknown part must lie in ONE component), and it
# records every step in the Lean format:
#   peel [0, e, rels...]   eq [1, root, mode, k, rels...]   fix [2, k, rels...]   link [3, m, p, rels...]   root [4, r]
# Relations: Lean RS index -> list of signed edges (2e for exponent +1, 2e+1 for -1, repeated |c| times);
# rels lists are products of RS entries (the Lean side cancels q against its inverse).
# check_cert() is an exact Python mirror of T2Close.check, run before writing the Lean file.  Apache-2.0.
import collections

BIG = 1000000000


def signed(r):
    out = []
    for e, c in sorted(r.items()):
        out += [2 * e if c > 0 else 2 * e + 1] * abs(c)
    return out


def emit(edges, RV, C, need, notree=(), treerows=None, desc=None, rows=None, diagtree=False):
    E = len(edges)
    adj = collections.defaultdict(list)
    for (x, y), i in edges.items():
        if x != y and y not in notree and (treerows is None or x in treerows):
            adj[('r', x)].append((('c', y), i)); adj[('c', y)].append((('r', x), i))
    root = ('r', C[0]); seen = {root}; order = [root]; tree = set()
    TT = []
    if not diagtree:
        for vv in order:
            for u, i in adj[vv]:
                if u not in seen: seen.add(u); order.append(u); tree.add(i); TT.append((i, u[0] == 'r'))
    else:
        # gauge tree = every diagonal + a spanning tree of the line graph (mu-normalisation of t1mpeel.py)
        x0 = C[0]; tree.add(edges[(x0, x0)]); TT.append((edges[(x0, x0)], False)); lseen = {x0}; lorder = [x0]
        for x in lorder:
            for y in C:
                if y not in lseen and (x, y) in edges and x != y:
                    lseen.add(y); lorder.append(y)
                    tree.add(edges[(x, y)]); TT.append((edges[(x, y)], False))
                    tree.add(edges[(y, y)]); TT.append((edges[(y, y)], True))
    diag = [i for (x, y), i in edges.items() if x == y]; dg = set(diag)
    # ALL entries: (dict, combo) ; combo = list of (base index, sign)
    grp = collections.defaultdict(list)
    for ri, r in enumerate(RV): grp[tuple(sorted((e, c) for e, c in r.items() if e in dg))].append(ri)
    ALL = [(r, ((ri, 1),)) for ri, r in enumerate(RV)]
    for sig, l in grp.items():
        r0 = RV[l[0]]
        for ri in l[1:]:
            d = dict(RV[ri])
            for e, c in r0.items(): d[e] = d.get(e, 0) - c
            ALL.append(({e: c for e, c in d.items() if c}, ((ri, 1), (l[0], -1))))
    RS = []; rsix = {}; DESC = []
    def ix(x, y): return edges[(x, y)]
    def base_list(ri):
        """canonical signed edge list of relation ri (Lean relOf / rel2Of / rel3Of order), exponent +1 form"""
        kind, d = desc[ri]
        if kind == 'a':
            t_, a_, s__, b_ = d[:4]
            return [2 * ix(t_, a_), 2 * ix(a_, s__), 2 * ix(b_, b_), 2 * ix(t_, b_) + 1, 2 * ix(b_, s__) + 1, 2 * ix(a_, a_) + 1]
        if kind == 'b':
            t_, s__, f_, g_, h_ = d[:5]
            return [2 * ix(t_, g_), 2 * ix(g_, s__), 2 * ix(h_, h_), 2 * ix(t_, h_) + 1, 2 * ix(h_, s__) + 1, 2 * ix(g_, g_) + 1]
        t_, s__, f_ = d[:3]
        return [2 * ix(t_, f_), 2 * ix(f_, s__), 2 * ix(t_, s__) + 1, 2 * ix(f_, f_) + 1]
    def lrel(combos):
        out = []
        for ri, s in combos:
            if (ri, s) not in rsix:
                rsix[(ri, s)] = len(RS)
                kind, d = desc[ri]
                if kind == 'a': DESC.append(list(d[:4]) + [1 if s > 0 else 0] + list(d[4]))
                elif kind == 'b': DESC.append(list(d[:5]) + list(d[5]) + list(d[6]))
                else: DESC.append(list(d[:5]) + list(d[5]) + list(d[6]) + list(d[7]))
                bl = base_list(ri)
                if kind == 'a':
                    RS.append(bl if s > 0 else [opp(q) for q in bl])
                else:
                    RS.append(bl if s > 0 else [opp(q) for q in bl])
            out.append(rsix[(ri, s)])
        return out
    gauge = sorted(tree)    # T1: no diagonal scale (rule (c) kills it)
    mask = {e: 0 for e in gauge}; od = {e: 0 for e in gauge}
    PD, PR, SG = {}, {}, {}
    CO, FO, RT = {}, {}, {}
    ST = [None]       # ST[i] = step i
    st = {'fixed': 0, 'ncls': 0}; stats = collections.Counter()
    def add(s): ST.append(s); return len(ST) - 1
    def rmask_raw(r):
        m = 0
        for e, c in r.items():
            if e in mask and c % 2: m ^= mask[e]
        return m
    def rmask(r): return rmask_raw(r) & ~st['fixed']
    rnd = 0
    while True:
        rnd += 1; prog = False
        ch = True
        while ch:
            ch = False
            for r, cb in ALL:
                u = [e for e in r if e not in mask]
                if len(u) == 1 and abs(r[u[0]]) == 1:
                    e = u[0]; mask[e] = rmask(r); od[e] = add([0, e] + lrel(cb)); ch = True; prog = True; stats['peel'] += 1
        basis = {}
        for ai, (r, cb) in enumerate(ALL):
            if not all(e in mask for e in r): continue
            m = rmask(r); cs = {ai}
            while m:
                h = m.bit_length() - 1
                if h in basis: m ^= basis[h][0]; cs ^= basis[h][1]
                else: basis[h] = (m, cs); break
        for h in sorted(basis):
            for h2 in list(basis):
                if h2 != h and basis[h2][0] >> h & 1:
                    basis[h2] = (basis[h2][0] ^ basis[h][0], basis[h2][1] ^ basis[h][1])
        for h, (m, cs) in sorted(basis.items()):
            if m == 1 << h and not st['fixed'] >> h & 1:
                cb = [x for ai in sorted(cs) for x in ALL[ai][1]]
                FO[h] = add([2, h] + lrel(cb)); st['fixed'] |= m; prog = True; stats['fix'] += 1
        # components of 2-unknown links
        par = {}; conflict = {}; ladj = collections.defaultdict(list)
        def find(x):
            p = 0
            while par.get(x, (x, 0))[0] != x: q = par[x]; p ^= q[1]; x = q[0]
            return x, p
        for ai, (r, cb) in enumerate(ALL):
            u = [(e, c) for e, c in r.items() if e not in mask]
            if len(u) != 2 or abs(u[0][1]) != 1 or abs(u[1][1]) != 1: continue
            if rmask(r): continue
            (e1, c1), (e2, c2) = u; s = 0 if c1 * c2 < 0 else 1
            r1, p1 = find(e1); r2, p2 = find(e2)
            if r1 != r2:
                par[r1] = (r2, p1 ^ p2 ^ s); stats['link'] += 1
                ladj[e1].append((e2, ai)); ladj[e2].append((e1, ai))
            elif p1 ^ p2 ^ s and r1 not in conflict: conflict[r1] = ai
        # component equations (as closure2): the unknown part has non-zero net exponent in ONE component; other
        # components (net 0) are removed by multiplying with link relations along tree paths to their roots
        done = {}
        for ai, (r, cb) in enumerate(ALL):
            u = [(e, c) for e, c in r.items() if e not in mask]
            if not u: continue
            net = collections.Counter()
            for e, c in u:
                rt_, p_ = find(e); net[rt_] += c * (-1 if p_ else 1)
            net = {a: b for a, b in net.items() if b}
            if len(net) != 1: continue
            rt, ex = next(iter(net.items()))
            if rt in done: continue
            if abs(ex) == 1: done[rt] = (0, ai)
            elif abs(ex) == 2 and rmask(r) == 0: done[rt] = (1, ai)
        parent = {}
        def tree_of(rt):
            if rt in parent: return
            parent[rt] = None; q = [rt]
            while q:
                p_ = q.pop(0)
                for m_, li in ladj[p_]:
                    if m_ not in parent: parent[m_] = (p_, li); q.append(m_)
        def path_combo(e, c):
            """combos that move an occurrence e^c to the root of its component"""
            out = []
            tree_of(find(e)[0])
            while parent.get(e) is not None:
                p_, li = parent[e]; r, cb = ALL[li]
                sgn = -c * r[e]                    # r^sgn cancels e^c
                out += [(ri, s_ * sgn) for ri, s_ in cb]
                c = sgn * r[p_]; e = p_
            return out
        for rt, ai in conflict.items():
            rt = find(rt)[0]
            if rt not in done: done[rt] = (1, ai)
        for rt, (mode, ai) in done.items():
            # root, then links in BFS order (the union records form a spanning tree of the component)
            PD[rt] = add([4, rt]); PR[rt] = rt; SG[rt] = 0
            members = [rt]; q = [rt]; vis = {rt}
            while q:
                p_ = q.pop(0)
                for m_, li in ladj[p_]:
                    if m_ in vis: continue
                    vis.add(m_); members.append(m_); q.append(m_)
                    r, cb = ALL[li]
                    a = 2 * m_ if r[m_] > 0 else 2 * m_ + 1; b = 2 * p_ if r[p_] > 0 else 2 * p_ + 1
                    SG[m_] = (a + SG[p_] + b + 1) % 2; PR[m_] = rt
                    PD[m_] = add([3, m_, p_] + lrel(cb))
            r, cb = ALL[ai]
            extra = []
            for e, c in r.items():
                if e not in mask and find(e)[0] != rt: extra += path_combo(e, c)
            cb = list(cb) + extra
            comb = collections.Counter()
            for ri, s_ in cb:
                for e, c in RV[ri].items(): comb[e] += s_ * c
            X = rmask_raw({e: c for e, c in comb.items() if c})
            if mode == 0: k = 0; mm = X; stats['compval'] += 1
            else:
                k = st['ncls']; st['ncls'] += 1; mm = 1 << k; RT[k] = rt; stats['odd'] += 1
            i = add([1, rt, mode, k] + lrel(cb))
            if mode == 1: CO[k] = i
            for e in members: mask[e] = mm; od[e] = i
            prog = True
        if not prog: break
    need = list(need)
    cert = {'RS': RS, 'OD': od, 'MK': mask, 'PD': PD, 'PR': PR, 'SG': SG, 'ST': ST, 'L': len(ST) - 1,
            'RT': [RT.get(k, 0) for k in range(st['ncls'])], 'CO': [CO.get(k, BIG) for k in range(st['ncls'])],
            'FO': [FO.get(k, BIG) for k in range(st['ncls'])], 'GA': gauge, 'NE': need, 'n': st['ncls'], 'E': E,
            'DESC': DESC, 'EDG': [list(xy) for xy, i in sorted(edges.items(), key=lambda z: z[1])],
            'TREE': sorted(tree), 'TT': TT, 'DT': diagtree, 'DIAG0': diag[0] if diag else None, 'ROOT': C[0],
            'ROWS': sorted(rows) if rows is not None else None}
    ok = all(e in mask and mask[e] & ~st['fixed'] == 0 for e in need)
    return cert, {'ok': ok, 'edges': E, 'steps': len(ST) - 1, 'RS': len(RS), 'classes': st['ncls'],
                  'fixed': bin(st['fixed']).count('1'), 'rounds': rnd, **stats}


# ---------------- exact mirror of the Lean checker ----------------
def opp(q): return q + 1 if q % 2 == 0 else q - 1


def nrm(l):
    acc = []
    for q in l:
        o = opp(q)
        if o in acc: acc.remove(o)
        else: acc.insert(0, q)
    return acc


def check_cert(c):
    n = c['n']; L = c['L']
    od = lambda e: c['OD'].get(e, BIG); mk = lambda e: c['MK'].get(e, 0)
    pd = lambda e: c['PD'].get(e, BIG); pr = lambda e: c['PR'].get(e, 0); sg = lambda e: c['SG'].get(e, 0)
    CO = lambda k: c['CO'][k] if k < len(c['CO']) else BIG
    FO = lambda k: c['FO'][k] if k < len(c['FO']) else BIG
    RT = lambda k: c['RT'][k] if k < len(c['RT']) else 0
    stp = lambda i: c['ST'][i] if 1 <= i <= L else []
    g = lambda s, j, d=0: s[j] if j < len(s) else d
    def relL(l): return nrm([q for a in l for q in (c['RS'][a] if a < len(c['RS']) else [])])
    def trivB(i, x): return all(not (x >> k & 1) or FO(k) < i for k in range(n))
    def bitsB(i, x): return all(not (x >> k & 1) or CO(k) < i for k in range(n)) and x < 2 ** n
    def xm(l):
        a = 0
        for q in l: a ^= mk(q // 2)
        return a
    asg = lambda i, q: od(q // 2) < i
    unas = lambda i, R: [q for q in R if not asg(i, q)]
    def peelB(i, s):
        R = relL(s[2:]); U = unas(i, R)
        if len(U) != 1: return False
        q = U[0]
        return q // 2 == g(s, 1) and od(g(s, 1)) == i and trivB(i, xm([x for x in R if asg(i, x)]) ^ mk(g(s, 1))) \
            and bitsB(i, mk(g(s, 1)))
    def fixOK(i, s):
        R = relL(s[2:])
        return FO(g(s, 1)) == i and g(s, 1) < n and not unas(i, R) and trivB(i, xm(R) ^ 2 ** g(s, 1))
    def rootOK(i, s): return pd(g(s, 1)) == i and pr(g(s, 1)) == g(s, 1) and sg(g(s, 1)) % 2 == 0
    def linkOK(i, s):
        m, p = g(s, 1), g(s, 2); R = relL(s[3:])
        if not (pd(m) == i and pd(p) < i and pr(m) == pr(p) and trivB(i, xm([x for x in R if asg(i, x)]))): return False
        U = unas(i, R)
        if len(U) != 2: return False
        a, b = U
        return (a // 2 == m and b // 2 == p and (sg(m) + a + sg(p) + b + 1) % 2 == 0) or \
               (a // 2 == p and b // 2 == m and (sg(m) + b + sg(p) + a + 1) % 2 == 0)
    def cnt(U):
        c1 = c2 = 0
        for q in U:
            if (sg(q // 2) + q) % 2 == 0: c1 += 1
            else: c2 += 1
        return c1, c2
    def eqX(i, s): return xm([x for x in relL(s[4:]) if asg(i, x)])
    def eqOK(i, s):
        root = g(s, 1); R = relL(s[4:]); U = unas(i, R); X = eqX(i, s); c1, c2 = cnt(U)
        if not (pd(root) < i and pr(root) == root and sg(root) % 2 == 0 and all(pd(q // 2) < i and pr(q // 2) == root for q in U)):
            return False
        if g(s, 2) == 0: return (c1 == c2 + 1 or c2 == c1 + 1) and bitsB(i, X)
        k = g(s, 3)
        return (c1 == c2 + 2 or c2 == c1 + 2) and trivB(i, X) and k < n and CO(k) == i and RT(k) == root
    def edgeJ(e):
        i = od(e)
        if i == 0: return e in c['GA'] and mk(e) == 0
        if i > L: return True
        s = stp(i)
        if g(s, 0, 9) == 0 and g(s, 1) == e and peelB(i, s): return True
        if g(s, 0, 9) == 1 and eqOK(i, s) and pr(e) == g(s, 1) and pd(e) < i:
            return (g(s, 2) == 0 and mk(e) == eqX(i, s)) or (g(s, 2) != 0 and mk(e) == 2 ** g(s, 3))
        return False
    def pendJ(e):
        i = pd(e)
        if i == 0: return False
        if i > L: return True
        s = stp(i)
        return g(s, 1) == e and ((g(s, 0, 9) == 4 and rootOK(i, s)) or (g(s, 0, 9) == 3 and linkOK(i, s)))
    def coJ(k):
        i = CO(k)
        if i == 0: return False
        if i > L: return True
        s = stp(i)
        return g(s, 0, 9) == 1 and g(s, 2) != 0 and g(s, 3) == k and eqOK(i, s)
    def foJ(k):
        i = FO(k)
        if i == 0: return False
        if i > L: return True
        s = stp(i)
        return g(s, 0, 9) == 2 and g(s, 1) == k and fixOK(i, s)
    def wfB(e): return all(not (mk(e) >> k & 1) or CO(k) <= od(e) for k in range(n)) and mk(e) < 2 ** n
    bad = []
    if not L < BIG: bad.append('L')
    for e in range(c['E']):
        if not edgeJ(e): bad.append(('edge', e))
        if not pendJ(e): bad.append(('pend', e))
        if not wfB(e): bad.append(('wf', e))
    for k in range(n):
        if not coJ(k): bad.append(('co', k))
        if not foJ(k): bad.append(('fo', k))
    for e in c['NE']:
        if not (od(e) <= L and trivB(L + 1, mk(e))): bad.append(('need', e))
    return bad


def check_glue1(c):
    """Python mirror of T1Glue.glue1OK + cov1OK (descriptors (a)/(b)/(c), balance rows/cols, BFS gauge, coverage)."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from p104lib import P, RT, ORTH
    dot = lambda i, j: sum(a * b for a, b in zip(RT[P[i]], RT[P[j]]))
    EDG = c['EDG']; nE = len(EDG); EI = {(x, y): e for e, (x, y) in enumerate(EDG)}
    m = set(c['ROWS']); bad = []
    def eid(x, y): return EI.get((x, y), 0)
    def edgeOK(x, y): e = eid(x, y); return e < nE and EDG[e] == [x, y]
    def pairOK3(t, s, x, y, F):
        return (len(F) == 8 and all(f < 104 for f in F) and len(set(F)) == 8 and x in F and y in F and x != y and
                x in m and y in m and t in m and all(f in m or ORTH[t][f] for f in F) and
                all(f not in m or f in (x, y) or ORTH[t][f] or ORTH[f][s] for f in F))
    for a, (rs, d) in enumerate(zip(c['RS'], c['DESC'])):
        if len(d) == 29:
            t, s, f, g, h = d[:5]; F1, F2, F3 = d[5:13], d[13:21], d[21:29]
            rel = [2 * eid(t, f), 2 * eid(f, s), 2 * eid(t, s) + 1, 2 * eid(f, f) + 1]
            ok = (rs == rel or rs == [opp(q) for q in rel]) and pairOK3(t, s, f, g, F1) and pairOK3(t, s, f, h, F2) and pairOK3(t, s, g, h, F3)
            ok = ok and 2 * dot(t, f) * dot(f, s) == dot(t, s) * dot(f, f)
            ok = ok and all(edgeOK(x, y) for x, y in ((t, f), (f, s), (t, s), (f, f)))
        elif len(d) == 21:
            t, s, f, g, h = d[:5]; F1, F2 = d[5:13], d[13:21]
            rel = [2 * eid(t, g), 2 * eid(g, s), 2 * eid(h, h), 2 * eid(t, h) + 1, 2 * eid(h, s) + 1, 2 * eid(g, g) + 1]
            ok = (rs == rel or rs == [opp(q) for q in rel]) and pairOK3(t, s, f, g, F1) and pairOK3(t, s, f, h, F2)
            ok = ok and dot(t, g) * dot(g, s) * dot(h, h) == dot(t, h) * dot(h, s) * dot(g, g)
            ok = ok and all(edgeOK(x, y) for x, y in ((t, g), (g, s), (h, h), (t, h), (h, s), (g, g)))
        else:
            t, a_, s, b, sg = d[:5]; Fr = list(d[5:]); o = 0 if sg == 1 else 1
            rel = [2 * eid(t, a_) + o, 2 * eid(a_, s) + o, 2 * eid(b, b) + o, 2 * eid(t, b) + 1 - o, 2 * eid(b, s) + 1 - o, 2 * eid(a_, a_) + 1 - o]
            ok = rel == rs and len(set(Fr)) == len(Fr) and a_ in Fr and b in Fr and a_ != b and a_ in m and b in m and t in m
            ok = ok and all(f in m or ORTH[t][f] for f in Fr) and ORTH[t][s]
            ok = ok and all(f not in m or f in (a_, b) or ORTH[t][f] or ORTH[f][s] for f in Fr)
            ok = ok and dot(t, a_) * dot(a_, s) * dot(b, b) == -(dot(t, b) * dot(b, s) * dot(a_, a_))
            ok = ok and all(edgeOK(x, y) for x, y in ((t, a_), (a_, s), (b, b), (t, b), (b, s), (a_, a_)))
        for key in (0, 1):
            acc = collections.Counter()
            for q in rs: acc[EDG[q // 2][key]] += 1 if q % 2 == 0 else -1
            ok = ok and not any(acc.values())
        if not ok: bad.append(('rs', a))
    for e, (x, y) in enumerate(EDG):
        if dot(x, y) == 0: bad.append(('dot', e))
    tr = set(c['TREE'])
    if not c.get('DT') and any(EDG[e][0] == EDG[e][1] for e in tr): bad.append('treediag')
    if not all(e in tr for e in c['GA']): bad.append('GA')
    zm = c['ZM']; NE = set(c['NE'])
    for x in zm:
        for y in zm:
            if x != y and ORTH[x][y]: continue
            if not (edgeOK(x, y) and eid(x, y) in NE): bad.append(('cov', x, y))
    return bad
