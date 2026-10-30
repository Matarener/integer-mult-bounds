"""RELAYTOP: generic forward rank-1 relay greedy (RELAYLAT rh.build generalised to an abstract instance) + dual composition.

Instance (all in one coordinate system with the parity form):
  src[s]  basis of source s's birth frame (bottom: [p_i]; dual: [p_j])
  snk[k]  basis of sink k's 'orthogonality set' (bottom: [p_j]; dual: basis of piece frame g_t); sink k servable at frame f iff f perp snk[k]
  C[k][s] sign (+-1) of sink k's coefficient on source s (0 / missing = not wanted)
Rects (A sources, B sinks, v signs on A, frame key g, register).  Stages k=2..K: pair merges at G = g1+g2 (dim <= k), children by ratio class
(butterfly reuses both registers); every extra destination of a rect is a BIRTH.  land=True: final landings at each sink's Q (= snk^perp).
Registers carry chains of dims in the instance's own coordinates (tax is invariant under d -> 9-d).  No side effects at import."""
import math, collections, random, heapq, sys
from fractions import Fraction as Fr
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import geo
par = geo.par

def rref(vs):
    piv = {}
    for v in vs:
        for p in sorted(piv, reverse=True):
            if (v >> p) & 1: v ^= piv[p]
        if v:
            p = v.bit_length() - 1
            for q in piv:
                if (piv[q] >> p) & 1: piv[q] ^= v
            piv[p] = v
    return tuple(sorted(piv.values()))

def span_set(b):
    S = {0}
    for v in b: S |= {x ^ v for x in S}
    return S

def perp(basis):
    """basis of the orthogonal complement (parity form, nondegenerate standard dot)"""
    out = []
    for x in range(1, 512):
        if all(not par(x, v) for v in basis): out.append(x)
    return rref(out)

H = lambda x: x * math.log(x) if x > 0 else 0.0
def tax(ds):
    ds = sorted(set(ds)); D = ds[-1] - ds[0]
    return H(D) - sum(H(b - a) for a, b in zip(ds, ds[1:])) if D > 0 else 0.0

def _mu(a, d, b):
    """tax of one stop at dim d inside a jump a -> b (0 if d is not strictly inside)"""
    return H(b - a) - H(d - a) - H(b - d) if a < d < b else 0.0

class Inst:
    def __init__(self, src, snk, C):
        self.src = src; self.snk = snk; self.C = C   # C: dict sink -> dict source -> sign
        self.adj = collections.defaultdict(set)
        for k, row in C.items():
            for s in row: self.adj[s].add(k)
        self._fc = {}
        # sink orth sets as span sets for fast test: f perp snk iff all f-basis perp all snk-basis
        self.snkb = [tuple(b) for b in snk]
        self.readers = [[k] for k in range(len(snk))]   # Y mains served by sink k (pair sinks: both)
        self.sw = [1] * len(snk)   # sink weight (entries per port delivered: pair sinks 2)
    def frame(self, vs):
        key = rref(vs)
        if key not in self._fc:
            J = frozenset(k for k, b in enumerate(self.snkb) if all(not par(x, y) for x in key for y in b))
            self._fc[key] = (key, len(key), J)
        return self._fc[key]

class Net:
    def __init__(self):
        self.regs = {}; self.rects = {}; self.nr = 0; self.nreg = 0; self.ops = []
    def op(self, dst, src, q, fk):
        self.ops.append((dst, src, Fr(q), fk, len(fk)))
    def newreg(self, role, born_key, born_dim, tag=None):
        r = self.nreg; self.nreg += 1
        self.regs[r] = dict(role=role, chain=[born_dim], frames=[born_key], tag=tag); return r
    def stop(self, reg, fk, d):
        R = self.regs[reg]
        if R['frames'][-1] == fk: return
        assert d > R['chain'][-1], (R, fk, d)
        R['chain'].append(d); R['frames'].append(fk)
    def newrect(self, A, B, v, g, reg, sc=1):
        rid = self.nr; self.nr += 1
        self.rects[rid] = dict(A=frozenset(A), B=set(B), v=dict(v), g=g, reg=reg, sc=Fr(sc)); return rid

def build(I, K=7, theta=(0, 0, 6, 4, 3, 2, 2, 2, 1), lam=4.0, rounds=2, seed=0, land=True, weight=None, verbose=False, eps=0.0, pairdirs=None, pairbonus=0.0, gshape='ent'):
    """weight[s]: value of source s per sink (bottom: 1 per port; dual: |A_t| entries per piece is irrelevant -> 1)."""
    rnd = random.Random(seed); N = Net(); F0 = I.frame([])
    wt = weight or (lambda s: 1)
    live = set()
    for s, b in enumerate(I.src):
        f = I.frame(list(b)); r = N.newreg('X', f[0], f[1], tag=s)
        live.add(N.newrect([s], I.adj[s] & f[2], {s: 1}, f[0], r))
    def coef(k, R):
        a = next(iter(R['A'])); return I.C[k][a] * R['v'][a]
    stats = []
    for k in [kk for kk in range(2, K + 1) for _ in range(rounds)]:
        cand = {}
        pieces = list(live)
        for x in range(len(pieces)):
            r1 = pieces[x]; R1 = N.rects[r1]
            for y in range(x + 1, len(pieces)):
                r2 = pieces[y]; R2 = N.rects[r2]
                if R1['A'] & R2['A']: continue
                common = R1['B'] & R2['B']
                if len(common) < theta[k]: continue
                G = I.frame(list(R1['g']) + list(R2['g']))
                if G[1] > k: continue
                R = common & G[2]
                if pairdirs is not None and len(R1['A']) == 1 and len(R2['A']) == 1:
                    a1 = next(iter(R1['A'])); a2 = next(iter(R2['A']))
                    if (I.src[a1][0] ^ I.src[a2][0]) not in pairdirs and pairbonus == 0: continue
                if len(R) >= theta[k]: cand[(r1, r2)] = (G, R)
        used = collections.defaultdict(set); ndest = collections.Counter(); acc = []
        def dbirth(r, Rf):
            rem = N.rects[r]['B'] - used[r]
            before = (ndest[r] + (1 if rem else 0) - 1) if ndest[r] else 0
            after = ndest[r] + 1 + (1 if rem - Rf else 0) - 1
            return after - before
        wA = {r: sum(wt(s) for s in N.rects[r]['A']) for r in pieces}; nz = {}
        heap = [(-len(R) * 2, rnd.random(), r1, r2) for (r1, r2), (G, R) in cand.items()]
        heapq.heapify(heap)
        while heap:
            negv, _, r1, r2 = heapq.heappop(heap)
            G, R = cand[(r1, r2)]
            Rf = {j for j in R if j not in used[r1] and j not in used[r2]}
            if len(Rf) < theta[k]: continue
            if gshape == 'ent': gain = sum(I.sw[j] for j in Rf) * (wA[r1] + wA[r2]) - lam * (dbirth(r1, Rf) + dbirth(r2, Rf))
            elif gshape.startswith('tax'):   # GENUPGRADE (opt-in): exact chain-tax marginal (Lemma 4) of the two G stops + birth chains instead of a flat birth price
                tw = float(gshape[3:] or 1.0); g1 = len(N.rects[r1]['g']); g2 = len(N.rects[r2]['g']); kk = G[1]
                dt = _mu(g1, kk, 9) + _mu(g2, kk, 9) + dbirth(r1, Rf) * tax([0, g1, kk, 9]) + dbirth(r2, Rf) * tax([0, g2, kk, 9])
                gain = tw * sum(I.sw[j] for j in Rf) * (wA[r1] + wA[r2]) - dt
            else: gain = sum(I.sw[j] for j in Rf) - lam * (dbirth(r1, Rf) + dbirth(r2, Rf))
            if gain <= 0: continue
            if eps: gain *= 1 + eps * nz.setdefault((r1, r2), rnd.random())
            if pairbonus and len(N.rects[r1]['A']) == 1 and len(N.rects[r2]['A']) == 1 and (I.src[next(iter(N.rects[r1]['A']))][0] ^ I.src[next(iter(N.rects[r2]['A']))][0]) in pairdirs: gain *= 1 + pairbonus
            if heap and -heap[0][0] > gain + 1e-9:
                heapq.heappush(heap, (-gain, rnd.random(), r1, r2)); continue
            used[r1] |= Rf; used[r2] |= Rf; ndest[r1] += 1; ndest[r2] += 1; acc.append((r1, r2, G, Rf))
        dest = collections.defaultdict(list)
        for e, (r1, r2, G, Rf) in enumerate(acc): dest[r1].append(e); dest[r2].append(e)
        newlive = set(); births = 0; arrive = {}
        for rid in list(live):
            R = N.rects[rid]; ds = dest.get(rid, []); rest = R['B'] - used[rid]
            if not ds: newlive.add(rid); continue
            regs = [R['reg']] + [None] * (len(ds) - 1 + (1 if rest else 0))
            gdim = len(R['g'])
            for t in range(1, len(regs)):
                nr = N.newreg('H', F0[0], 0); N.stop(nr, R['g'], gdim); regs[t] = nr; births += 1; N.op(nr, R['reg'], 1, R['g'])
            for t, e in enumerate(ds): arrive[(e, rid)] = regs[t]
            if rest: newlive.add(N.newrect(R['A'], rest, R['v'], R['g'], regs[len(ds)], R['sc']))
        for e, (r1, r2, G, Rf) in enumerate(acc):
            R1, R2 = N.rects[r1], N.rects[r2]
            a1, a2 = arrive[(e, r1)], arrive[(e, r2)]
            N.stop(a1, G[0], G[1]); N.stop(a2, G[0], G[1])
            cls = collections.defaultdict(set)
            for j in Rf: cls[coef(j, R2) * coef(j, R1)].add(j)
            regs = [a1, a2]; sc1, sc2 = R1['sc'], R2['sc']
            items = sorted(cls.items())
            if len(items) == 1:
                N.op(a1, a2, sc1 * items[0][0] / sc2, G[0]); scs = [sc1]
            else:   # butterfly: a1 -> sc1 (v1 - v2), a2 -> sc2/2 (v1 + v2)
                N.op(a1, a2, -sc1 / sc2, G[0]); N.op(a2, a1, sc2 / (2 * sc1), G[0]); scs = [sc1, sc2 / 2]
            for t, (s, Bc) in enumerate(items):
                v = dict(R1['v']); v.update({a: s * R2['v'][a] for a in R2['A']})
                newlive.add(N.newrect(R1['A'] | R2['A'], Bc, v, G[0], regs[t], scs[t]))
        live = newlive
        nent = sum(len(N.rects[r]['A']) * len(N.rects[r]['B']) for r in live)
        stats.append((k, len(acc), births, len(live), round(nent / max(1, len(live)), 2)))
        if verbose: print('  stage', k, 'merges', len(acc), 'births', births, 'live', len(live), 'mean rect', stats[-1][-1], flush=True)
    N.live = live
    if land:
        for rid in live:
            R = N.rects[rid]
            for t, j in enumerate(sorted(R['B'])):
                reg = R['reg'] if t == 0 else None
                if reg is None:
                    reg = N.newreg('H', F0[0], 0); N.stop(reg, R['g'], len(R['g'])); N.op(reg, R['reg'], 1, R['g'])
                Q = I.frame(list(perp(I.snkb[j])))
                N.stop(reg, Q[0], Q[1])
                for y in I.readers[j]:
                    a = next(iter(R['A'])); res = Fr(geo.RES[y, a]).limit_denominator(8)
                    c = -res / (R['sc'] * R['v'][a])
                    for b in R['A']: assert -Fr(geo.RES[y, b]).limit_denominator(8) == c * R['sc'] * R['v'][b], ('rank1', y, b)
                    N.op(('Y', y), reg, c, Q[0])
    return N, stats

def r0(N, top=9):
    tot = collections.Counter()
    for r, Rg in N.regs.items():
        ch = Rg['chain'] + ([top] if Rg['chain'][-1] != top else [])
        tot[Rg['role']] += tax(ch)
    return dict(tot), sum(tot.values())

def bottom_inst():
    P = geo.PORTS; m = geo.m; SG = {j: {i: (1 if geo.RES[j, i] > 0 else -1) for i in range(m) if geo.ORTH[j, i]} for j in range(m)}
    return Inst([[p] for p in P], [[p] for p in P], SG)

def dual_inst(Nb):
    """dual sources = readers j ([p_j]); dual sinks = live bottom pieces t (basis g_t); C[t][j] = sign of reader j on piece t"""
    P = geo.PORTS; m = geo.m
    pcs = sorted(Nb.live); C = {}
    snk = []
    for k, rid in enumerate(pcs):
        R = Nb.rects[rid]; a = next(iter(R['A']))
        C[k] = {j: (1 if geo.RES[j, a] > 0 else -1) * R['v'][a] for j in R['B']}
        snk.append(list(R['g']))
    return Inst([[p] for p in P], snk, C), pcs

if __name__ == '__main__':
    pass

def _plan(I, R1, R2, G, R, coef):
    """absorption accounting for one merge at G: returns (births, classes dict, absorber index or None)"""
    cls = collections.defaultdict(set)
    for j in R: cls[coef(j, R2) * coef(j, R1)].add(j)
    rest = [R1['B'] - R, R2['B'] - R]
    if len(cls) == 2: return (bool(rest[0]) + bool(rest[1])), cls, None
    best = None
    for b in (0, 1):
        o = 1 - b
        nb = bool(rest[b]) + (bool(rest[o]) and not rest[o] <= G[2])
        if best is None or nb < best[0]: best = (nb, cls, b)
    return best

def build2(I, K=7, theta=(0, 0, 6, 4, 3, 2, 2, 2, 1), lam=1.0, rounds=3, seed=0, land=True, gainmode='land', verbose=False):
    """ABSORPTION greedy: like build but a merge's two registers host any two of {child classes, rests}; a register whose rest stays inside J(G)
    continues from G for free; births = demands that no arriving register can host.  Each rect joins <= 1 merge per round."""
    rnd = random.Random(seed); N = Net(); F0 = I.frame([])
    live = set()
    for s, b in enumerate(I.src):
        f = I.frame(list(b)); r = N.newreg('X', f[0], f[1], tag=s)
        live.add(N.newrect([s], I.adj[s] & f[2], {s: 1}, f[0], r))
    def coef(k, R):
        a = next(iter(R['A'])); return I.C[k][a] * R['v'][a]
    stats = []
    for k in [kk for kk in range(2, K + 1) for _ in range(rounds)]:
        pieces = list(live); cand = []
        for x in range(len(pieces)):
            r1 = pieces[x]; R1 = N.rects[r1]
            for y in range(x + 1, len(pieces)):
                r2 = pieces[y]; R2 = N.rects[r2]
                if R1['A'] & R2['A']: continue
                common = R1['B'] & R2['B']
                if len(common) < theta[k]: continue
                G = I.frame(list(R1['g']) + list(R2['g']))
                if G[1] > k: continue
                R = common & G[2]
                if len(R) < theta[k]: continue
                nb, cls, b = _plan(I, R1, R2, G, R, coef)
                val = sum(I.sw[j] for j in R)
                if gainmode == 'ent': val = val * (len(R1['A']) + len(R2['A'])) / 8.0
                g = val - lam * nb
                if g > 0: cand.append((g, rnd.random(), r1, r2, G, R, cls, b, nb))
        cand.sort(reverse=True); busy = set(); acc = []
        for c in cand:
            if c[2] in busy or c[3] in busy: continue
            busy |= {c[2], c[3]}; acc.append(c)
        newlive = set(live) - busy; births = 0
        for (g, _, r1, r2, G, R, cls, b, nb) in acc:
            Rs = [N.rects[r1], N.rects[r2]]; regs = [Rs[0]['reg'], Rs[1]['reg']]
            rest = [Rs[0]['B'] - R, Rs[1]['B'] - R]
            def vchild(s):
                v = dict(Rs[0]['v']); v.update({a: s * Rs[1]['v'][a] for a in Rs[1]['A']}); return v
            def born_at(Rr):
                nr = N.newreg('H', F0[0], 0); N.stop(nr, Rr['g'], len(Rr['g'])); return nr
            A = Rs[0]['A'] | Rs[1]['A']
            if b is None:
                for a in (0, 1):
                    if rest[a]: nr = born_at(Rs[a]); births += 1; newlive.add(N.newrect(Rs[a]['A'], rest[a], Rs[a]['v'], Rs[a]['g'], nr))
                for t, (s, Bc) in enumerate(sorted(cls.items())):
                    N.stop(regs[t], G[0], G[1]); newlive.add(N.newrect(A, Bc, vchild(s), G[0], regs[t]))
            else:
                o = 1 - b; (s, Bc), = cls.items()
                if rest[b]: nr = born_at(Rs[b]); births += 1; newlive.add(N.newrect(Rs[b]['A'], rest[b], Rs[b]['v'], Rs[b]['g'], nr))
                N.stop(regs[b], G[0], G[1]); newlive.add(N.newrect(A, Bc, vchild(s), G[0], regs[b]))
                if rest[o] and rest[o] <= G[2]:
                    N.stop(regs[o], G[0], G[1]); newlive.add(N.newrect(Rs[o]['A'], rest[o], Rs[o]['v'], G[0], regs[o]))
                elif rest[o]:
                    newlive.add(N.newrect(Rs[o]['A'], rest[o], Rs[o]['v'], Rs[o]['g'], regs[o]))
                    nr = born_at(Rs[o]); births += 1; N.stop(nr, G[0], G[1])
                else:
                    N.stop(regs[o], G[0], G[1])
        live = newlive
        nent = sum(len(N.rects[r]['A']) * len(N.rects[r]['B']) for r in live)
        stats.append((k, len(acc), births, len(live), round(nent / max(1, len(live)), 2)))
        if verbose: print('  stage', k, 'merges', len(acc), 'births', births, 'live', len(live), 'mean rect', stats[-1][-1], 'entries', nent, flush=True)
    N.live = live
    if land:
        for rid in live:
            R = N.rects[rid]
            for t, j in enumerate(sorted(R['B'])):
                reg = R['reg'] if t == 0 else None
                if reg is None:
                    reg = N.newreg('H', F0[0], 0); N.stop(reg, R['g'], len(R['g']))
                Q = I.frame(list(perp(I.snkb[j])))
                N.stop(reg, Q[0], Q[1])
    return N, stats
