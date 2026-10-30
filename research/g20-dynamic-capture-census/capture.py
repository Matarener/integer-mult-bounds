#!/usr/bin/env python3
"""Dynamic capture census for a G20 BIT local word (atlas PR5586 target B1).  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

Word contract (as in the G20 packages): every wire carries a payload, an F2-linear combination of the
input symbols x_0..x_{n-1}, each with an exact 8x8 rational operator; ADD d s f adds wire s into wire d
(both in frame f); Q d s t k is a paid native query of rank k with action R_s R_t (R_f = I - 2 P_f);
ZERO_Q is a free move of a zero payload; ERASE/INIT only touch owned wires.

A capture owns a retained helper h (its rank-r target is debited, r^t with t = 1 - C).  While h is
dead-forward (its content cannot reach any retained output) every write into h is dropped and h is kept zero,
so its own queries there are free.  At the end of each dead interval h receives an arbitrary injected payload
w (ERASE plus same-frame ADDs).  A paid query is removed iff its whole symbolic payload becomes zero.

Exactness: one forward replay injects a fresh symbol u_(h,j) into h at the last dead moment of each of its
dead intervals.  With h owned, the true payload of query q is
    p_q = rest_q + sum_(h,j) M_(q,h,j) (w_(h,j) + snap_(h,j)),
where rest_q is the replayed payload with u-terms removed and the owned input symbols set to zero, snap is
the replayed content of h just before the injection (owned inputs zeroed), and every coefficient M is a
single matrix (checked).  A query depending on one injected symbol is removed iff w equals the unique value
M^-1 (rest_q + M snap); such queries are grouped by that value.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Fr
from hashlib import sha256
import gzip, itertools, json, math


# ---------------------------------------------------------------- exact 8x8 rational matrices
def _inv(m):
    n = len(m)
    a = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = next(i for i in range(c, n) if a[i][c] != 0)
        a[c], a[p] = a[p], a[c]
        v = a[c][c]
        a[c] = [x / v for x in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return tuple(tuple(row[n:]) for row in a)


def _to_int(a):
    den = 1
    for row in a:
        for x in row:
            den = den * x.denominator // math.gcd(den, x.denominator)
    return den, [[int(x * den) for x in row] for row in a]


def _mul(a, b):
    """Exact rational product, computed over the integers with a common denominator."""
    da, ia = _to_int(a)
    db, ib = _to_int(b)
    cols = list(zip(*ib))
    d = da * db
    return tuple(tuple(Fr(sum(x * y for x, y in zip(r, c)), d) for c in cols) for r in ia)


I8 = tuple(tuple(Fr(int(i == j)) for j in range(8)) for i in range(8))


def _projector(B):
    if not B:
        return tuple(tuple(Fr(0) for _ in range(8)) for _ in range(8))
    Bt = tuple(map(tuple, zip(*B)))
    return _mul(_mul(Bt, _inv(_mul(B, Bt))), B)


class Mats:
    """Interned matrices; payload = dict matrix-id -> bitmask of symbols (F2 multiplicity)."""
    def __init__(self):
        self.ids, self.mats, self.prod, self.invs = {}, [], {}, {}
        self.I = self.get(I8)

    def get(self, m):
        i = self.ids.get(m)
        if i is None:
            i = self.ids[m] = len(self.mats)
            self.mats.append(m)
        return i

    def mul(self, a, b):
        r = self.prod.get((a, b))
        if r is None:
            r = self.prod[(a, b)] = self.get(_mul(self.mats[a], self.mats[b]))
        return r

    def inv(self, a):
        r = self.invs.get(a)
        if r is None:
            r = self.invs[a] = self.get(_inv(self.mats[a]))
        return r


def padd(a, b):
    out = dict(a)
    for m, bits in b.items():
        z = out.get(m, 0) ^ bits
        if z:
            out[m] = z
        else:
            del out[m]
    return out


def pleft(mats, M, p):
    out = {}
    for m, bits in p.items():
        mm = mats.mul(M, m)
        z = out.get(mm, 0) ^ bits
        if z:
            out[mm] = z
        else:
            del out[mm]
    return out


def pmask(p, mask):
    """Keep only the symbols in mask (substitute all others by zero)."""
    out = {}
    for m, b in p.items():
        b &= mask
        if b:
            out[m] = b
    return out


def pkey(mats, p):
    if not p:
        return 'ZERO'
    rows = sorted((mats.mats[m], b) for m, b in p.items())
    return sha256(repr(rows).encode()).hexdigest()[:32]


def support(p):
    s = 0
    for b in p.values():
        s |= b
    return s


def parity(p):
    """F2-linear bitmap: symbol multiplicities summed over all matrices.  For an invertible single matrix M,
    parity(M p) = parity(p), so a vanishing payload has zero parity."""
    s = 0
    for b in p.values():
        s ^= b
    return s


# ---------------------------------------------------------------- the word
class Word:
    def __init__(self, word_path, frames_path, main_wires=222):
        with open(word_path, 'rb') as fh:
            w = json.loads(gzip.decompress(fh.read()))
        with open(frames_path) as fh:
            frames = json.load(fh)['frames']
        self.rec, self.owned, self.start, self.final = w['records'], set(w['owned']), w['start'], w['final']
        self.width = len(self.start)
        self.mats = Mats()
        used = {x for x in self.start + self.final if x is not None}
        for e in self.rec:
            if e[0] == 'ADD':
                used.add(e[3])
            elif e[0] in ('Q', 'ZERO_Q'):
                used |= {e[2], e[3]}
            elif e[0] in ('ERASE', 'INIT') and e[2] is not None:
                used.add(e[2])
        self.dim = {f: frames[str(f)]['dim'] for f in used}
        self.R = {}
        for f in used:
            P = _projector(tuple(tuple(Fr(x) for x in r) for r in frames[str(f)]['B']))
            self.R[f] = self.mats.get(tuple(tuple(I8[i][j] - 2 * P[i][j] for j in range(8)) for i in range(8)))
        self.qm = {}
        self.helpers = [i for i in range(self.width) if i not in self.owned and i >= main_wires]
        self.target_rank = {h: abs(self.dim[self.final[h]] - self.dim[self.start[h]]) for h in self.helpers}
        self.inmask = (1 << self.width) - 1

    def qmat(self, s, t):
        r = self.qm.get((s, t))
        if r is None:
            r = self.qm[(s, t)] = self.mats.mul(self.R[s], self.R[t])
        return r

    # forward replay with optional injections {event index: [(wire, symbol bit)]} applied before the event
    def replay(self, inject=None):
        inject = inject or {}
        mats, st = self.mats, list(self.start)
        fld = [{mats.I: 1 << i} for i in range(self.width)]
        queries, snaps, first_read, paid = [], {}, {}, Counter()
        for ix, e in enumerate(self.rec):
            for (h, bit) in inject.get(ix, ()):
                snaps[bit] = fld[h]
                fld[h] = padd(fld[h], {mats.I: 1 << bit})
            op, d = e[0], e[1]
            if op == 'ERASE':
                fld[d] = {}
                st[d] = e[2]
            elif op == 'INIT':
                st[d] = e[2]
            elif op == 'ADD':
                s, f = e[2], e[3]
                if not (st[d] == f == st[s]):
                    raise ValueError('ADD frame mismatch at %d' % ix)
                first_read.setdefault(s, ix)
                fld[d] = padd(fld[d], fld[s])
            elif op == 'Q':
                if st[d] != e[2] or abs(self.dim[e[2]] - self.dim[e[3]]) != e[4]:
                    raise ValueError('query frame/rank at %d' % ix)
                paid[e[4]] += 1
                queries.append((ix, d, e[4], fld[d]))
                fld[d] = pleft(mats, self.qmat(e[2], e[3]), fld[d])
                st[d] = e[3]
            elif op == 'ZERO_Q':
                if pmask(fld[d], self.inmask):
                    raise ValueError('free move of a nonzero payload at %d' % ix)
                st[d] = e[3]
            else:
                raise ValueError('unknown op ' + op)
        return queries, snaps, first_read, paid, fld

    # backward replay: for each helper, a bytearray dead[ix] = content of h just before event ix cannot reach
    # any retained output other than those in ignore(h) (always including h itself).
    def dead_profiles(self, helpers, ignore=None):
        mats = self.mats
        adj = [({mats.I: 1 << i} if i not in self.owned else {}) for i in range(self.width)]
        ign = {h: (1 << h) | sum(1 << x for x in (ignore or {}).get(h, ())) for h in helpers}
        n = len(self.rec)
        dead = {h: bytearray(n + 1) for h in helpers}

        cur = {h: (support(adj[h]) & ~ign[h]) == 0 for h in helpers}
        for h in helpers:
            dead[h][n] = cur[h]
        for ix in range(n - 1, -1, -1):
            e = self.rec[ix]
            op, d = e[0], e[1]
            touched = d
            if op == 'ADD':
                adj[e[2]] = padd(adj[e[2]], adj[d])
                touched = e[2]
            elif op == 'Q':
                Q = self.qmat(e[2], e[3])
                adj[d] = {mats.mul(m, Q): b for m, b in adj[d].items()}
            elif op == 'ERASE':
                adj[d] = {}
            if touched in cur:
                cur[touched] = (support(adj[touched]) & ~ign[touched]) == 0
            for h in helpers:
                dead[h][ix] = cur[h]
        return dead


def intervals(db):
    """Maximal runs of True in db (indices 0..n); returns [(a, b)] with dead before events a..b."""
    out, ix, n = [], 0, len(db)
    while ix < n:
        a = db.find(1, ix)
        if a < 0:
            break
        b = db.find(0, a)
        if b < 0:
            b = n
        out.append((a, b - 1))
        ix = b
    return out


def moment(k, t):
    return k ** t


# ---------------------------------------------------------------- set analysis
def analyze_sets(W, sets, C, ignore_partners=False):
    """For each owned set H (tuple of helpers): epochs, dead own-wire queries, exact single-symbol groups,
    multi-symbol queries.  Returns per-set records.  With ignore_partners, deadness of h in H ignores all
    outputs of H; otherwise only h's own output."""
    t = 1 - float(C)
    helpers = sorted({h for H in sets for h in H})
    out = []
    if ignore_partners:
        todo = [(H, W.dead_profiles(list(H), {h: set(H) for h in H})) for H in sets]
    else:
        dp = W.dead_profiles(helpers)
        todo = [(H, dp) for H in sets]
    n = len(W.rec)
    cache = {}
    ivs = {}
    for H, dead in todo:
        if ignore_partners:
            ivs = {}
        for h in (H if ignore_partners else helpers):
            if h not in ivs:
                ivs[h] = intervals(dead[h])
        key = (H if ignore_partners else None)
        inject, syms = defaultdict(list), []
        bit = W.width
        for h in (H if ignore_partners else helpers):
            for j, (a, b) in enumerate(ivs[h]):
                if b < n:
                    inject[b].append((h, bit))
                    syms.append((h, j, a, b, bit))
                    bit += 1
        if key not in cache:
            queries, snaps, _, _, fld = W.replay(inject)
            sups = [support(q[3]) for q in queries]
            bybit, bywire = defaultdict(list), defaultdict(list)
            for qi, (ix, d, k, p) in enumerate(queries):
                bywire[d].append(qi)
                s_ = sups[qi] >> W.width
                while s_:
                    low = s_ & -s_
                    bybit[low.bit_length() - 1 + W.width].append(qi)
                    s_ ^= low
            outsup = [support(f) for f in fld]
            cache[key] = (queries, snaps, sups, bybit, bywire, outsup)
        out.append(_set_record(W, H, dead, syms, cache[key], t, ivs))
    return out


def _set_record(W, H, dead, syms, ctx, t, ivs):
    queries, snaps, sups, bybit, bywire, outsup = ctx
    mats = W.mats
    Hs = set(H)
    mysyms = [s for s in syms if s[0] in Hs]
    keep = W.inmask & ~sum(1 << h for h in H)     # owned inputs substituted by zero
    symmask = sum(1 << s[4] for s in mysyms)
    allsym = sum(1 << s[4] for s in syms)
    # no injected symbol of h may reach a retained output other than ignored ones
    for (h, j, a, b, bt) in mysyms:
        for i in range(W.width):
            if i in W.owned or i in Hs:
                continue
            if outsup[i] >> bt & 1:
                raise ValueError('injected symbol of %d reaches retained output %d' % (h, i))
    reads = defaultdict(list)
    for ix, e in enumerate(W.rec):
        if e[0] == 'ADD' and e[2] in Hs:
            reads[e[2]].append(ix)
    free = {}
    for h in H:
        for (a, b) in ivs[h]:
            if not any(a <= r < b for r in reads[h]):
                free[h] = free.get(h, []) + [(a, b)]
    dead_own, groups, multi = [], defaultdict(lambda: defaultdict(list)), []
    cand = sorted({qi for s_ in mysyms for qi in bybit.get(s_[4], ())} | {qi for h in H for qi in bywire.get(h, ())})
    for qi in cand:
        ix, d, k, p = queries[qi]
        if d in Hs and any(a <= ix < b for (a, b) in free.get(d, ())):
            dead_own.append((ix, d, k))
            continue
        dep = [s for s in mysyms if sups[qi] >> s[4] & 1]
        if not dep:
            continue
        if len(dep) > 1:
            # a removed query satisfies parity(rest) + sum parity(snap_s) = sum_{s in dep} parity(w_s):
            # removed queries with the same dependence set share this parity label
            label = parity(pmask(p, keep))
            for s_ in dep:
                label ^= parity(pmask(snaps[s_[4]], keep))
            multi.append((ix, d, k, [(s_[0], s_[1]) for s_ in dep], label))
            continue
        h, j, a, b, bt = dep[0]
        coef = [m for m, bb in p.items() if bb >> bt & 1]
        if len(coef) != 1:
            raise ValueError('composite coefficient at query %d' % ix)
        M = coef[0]
        rest = pmask(p, keep)
        rest = padd(rest, pleft(mats, M, pmask(snaps[bt], keep)))
        v = pleft(mats, mats.inv(M), rest)
        groups[(h, j)][pkey(mats, v)].append((ix, d, k))
    epochs = []
    for (h, j, a, b, bt) in mysyms:
        g = groups.get((h, j), {})
        best = max(g.items(), key=lambda kv: (sum(moment(x[2], t) for x in kv[1]), kv[0])) if g else None
        epochs.append({'helper': h, 'epoch': j, 'dead_from': a, 'inject_before': b, 'groups': len(g),
                       'best_value': best[0] if best else None,
                       'best': [list(x) for x in best[1]] if best else []})
    debit = sum(moment(W.target_rank[h], t) for h in H)
    killed_single = sum(moment(x[2], t) for e in epochs for x in e['best'])
    dmass = sum(moment(k, t) for _, _, k in dead_own)
    classes = defaultdict(lambda: defaultdict(float))
    for ix, d, k, dep, label in multi:
        classes[tuple(map(tuple, dep))][label] += moment(k, t)
    mmass = sum(max(c.values()) for c in classes.values())
    return {'set': list(H), 'epochs': epochs, 'dead_own': [list(x) for x in dead_own],
            'multi': [[ix, d, k, dep] for ix, d, k, dep, _ in multi], 'multi_class_mass': mmass, 'debit': debit,
            'bound': dmass + killed_single + mmass - debit, 'exact_if_no_multi': not multi,
            'groups_by_epoch': {'%d/%d' % hk: {kk: [list(x) for x in vv] for kk, vv in g.items()}
                                for hk, g in groups.items()}}


# ---------------------------------------------------------------- pairs under the individual schedule
def pair_census(W, singles, C):
    """Exact two-helper census.  Each owned helper keeps its individual dead intervals (one live interval
    each on the PR5708 word).  Queries depending on both injections are removed only if their F2 bitmap row
    equals e_a+e_b+bitmap(w_a)+bitmap(w_b); hence all removed double queries share one row (row-class bound).
    Pairs whose bound is positive are enumerated exactly over w_a in groups(a)+{0}, w_b forced by a double or
    in groups(b)+{0}, and symmetrically; the doubles-only case is bounded by the row class."""
    t = 1 - float(C)
    mats = W.mats
    rec1 = {r['set'][0]: r for r in singles}
    helpers = sorted(rec1)
    hmask = sum(1 << h for h in helpers)
    dead_ix = {h: {x[0] for x in rec1[h]['dead_own']} for h in helpers}
    inj = {}
    bit = W.width
    inject = defaultdict(list)
    for h in helpers:
        eps = rec1[h]['epochs']
        if len(eps) != 1:
            raise ValueError('pair census assumes one live interval per helper')
        inject[eps[0]['inject_before']].append((h, bit))
        inj[h] = bit
        bit += 1
    queries, snaps, _, _, _ = W.replay(inject)
    # bitmap rows of the base word (for row classes)
    shared = defaultdict(list)
    for qi, (ix, d, k, p) in enumerate(queries):
        sup = support(p)
        hs = [h for h in helpers if sup >> inj[h] & 1 and not (d == h and ix in dead_ix[h])]
        for a, b in itertools.combinations(hs, 2):
            if (d == a and ix in dead_ix[a]) or (d == b and ix in dead_ix[b]):
                continue
            shared[(a, b)].append(qi)
    G = {h: sum(moment(x[2], t) for e in rec1[h]['epochs'] for x in e['best']) for h in helpers}
    Dm = {h: sum(moment(x[2], t) for x in rec1[h]['dead_own']) for h in helpers}
    deb = {h: moment(W.target_rank[h], t) for h in helpers}

    stats = Counter()
    exact = []
    best_overall = None
    for (a, b), qis in sorted(shared.items()):
        stats['pairs'] += 1
        rows = Counter()
        for qi in qis:
            ix, d, k, p = queries[qi]
            rows[_true_row(W, p, (a, b), inj, snaps)] += moment(k, t)
        rmax = max(rows.values())
        bound = Dm[a] + Dm[b] + G[a] + G[b] + rmax - deb[a] - deb[b]
        donly = Dm[a] + Dm[b] + rmax - deb[a] - deb[b]
        if donly > 0:
            raise ValueError('doubles-only bound positive for pair %s' % ((a, b),))
        if bound <= 0:
            stats['closed_by_row_class_bound'] += 1
            continue
        stats['enumerated'] += 1
        g = _pair_exact(W, queries, snaps, inj, a, b, qis, rec1, t)
        exact.append({'pair': [a, b], 'bound': bound, 'shared': len(qis), 'best_gain': g[0],
                      'best_ranks': g[1]})
        if best_overall is None or g[0] > best_overall[0]:
            best_overall = (g[0], a, b, g[1])
    stats['pairs_without_shared_query_max_gain'] = max(G[h] + Dm[h] - deb[h] for h in helpers) * 2
    return dict(stats), exact, best_overall


def _true_row(W, p, H, inj, snaps):
    """Class label of a double query: its payload with owned inputs zeroed, snapshots folded in, and the
    injected symbols replaced by marker bits; two doubles can both vanish only if these rows coincide."""
    keep = W.inmask & ~sum(1 << h for h in H)
    row = parity(pmask(p, keep))
    for h in H:
        bt = inj[h]
        coef = [m for m, bb in p.items() if bb >> bt & 1]
        if len(coef) != 1:
            raise ValueError('composite coefficient')
        row ^= parity(pmask(snaps[bt], keep))
    return row


def _pair_exact(W, queries, snaps, inj, a, b, qis, rec1, t):
    mats = W.mats
    keep = W.inmask & ~((1 << a) | (1 << b))

    def parts(p):
        Ma = [m for m, bb in p.items() if bb >> inj[a] & 1]
        Mb = [m for m, bb in p.items() if bb >> inj[b] & 1]
        rest = pmask(p, keep)
        if Ma:
            rest = padd(rest, pleft(mats, Ma[0], pmask(snaps[inj[a]], keep)))
        if Mb:
            rest = padd(rest, pleft(mats, Mb[0], pmask(snaps[inj[b]], keep)))
        return (Ma[0] if Ma else None), (Mb[0] if Mb else None), rest

    dead_a = [x for x in rec1[a]['dead_own']]
    dead_b = [x for x in rec1[b]['dead_own']]
    dset = {x[0] for x in dead_a + dead_b}
    qa, qb, qd = [], [], []
    for qi, (ix, d, k, p) in enumerate(queries):
        if ix in dset and d in (a, b):
            continue
        sup = support(p)
        ha, hb = sup >> inj[a] & 1, sup >> inj[b] & 1
        if ha or hb:
            Ma, Mb, rest = parts(p)
            (qd if (ha and hb) else qa if ha else qb).append((k, Ma, Mb, rest))
    va = {'ZERO': {}}
    for k, Ma, Mb, rest in qa:
        v = pleft(mats, mats.inv(Ma), rest)
        va[pkey(mats, v)] = v
    vb = {'ZERO': {}}
    for k, Ma, Mb, rest in qb:
        v = pleft(mats, mats.inv(Mb), rest)
        vb[pkey(mats, v)] = v
    cands = []
    for wa in va.values():
        for wb in vb.values():
            cands.append((wa, wb))
        for k, Ma, Mb, rest in qd:
            cands.append((wa, pleft(mats, mats.inv(Mb), padd(rest, pleft(mats, Ma, wa)))))
    for wb in vb.values():
        for k, Ma, Mb, rest in qd:
            cands.append((pleft(mats, mats.inv(Ma), padd(rest, pleft(mats, Mb, wb))), wb))
    base = sum(moment(x[2], t) for x in dead_a + dead_b) - moment(W.target_rank[a], t) - moment(W.target_rank[b], t)
    best = None
    seen = set()
    for wa, wb in cands:
        sig = (pkey(mats, wa), pkey(mats, wb))
        if sig in seen:
            continue
        seen.add(sig)
        killed = []
        for k, Ma, Mb, rest in qa:
            if not padd(rest, pleft(mats, Ma, wa)):
                killed.append(k)
        for k, Ma, Mb, rest in qb:
            if not padd(rest, pleft(mats, Mb, wb)):
                killed.append(k)
        for k, Ma, Mb, rest in qd:
            if not padd(padd(rest, pleft(mats, Ma, wa)), pleft(mats, Mb, wb)):
                killed.append(k)
        g = base + sum(moment(k, t) for k in killed)
        if best is None or g > best[0]:
            best = (g, sorted(killed))
    return best


# ---------------------------------------------------------------- joint token bound (any number of helpers)
def token_bound(W, singles, C):
    """Joint bound for any owned set under the individual schedule.  Removing query q forces
    parity(p_q) = sum over owned helpers h it depends on of (e_h + parity(w_h) + parity(writes into h)),
    so every removed base-word parity row lies in a d-dimensional span for d owned helpers.  ceil(4 r^t)
    copies of each eligible row are greedily partitioned into N F2-independent sets; a d-dimensional span
    meets each in at most d vectors, so removed t-mass <= N d / 4 (plus the free dead own-wire queries)."""
    t = 1 - float(C)
    helpers = sorted(r['set'][0] for r in singles)
    hmask = sum(1 << h for h in helpers)
    deadq = {x[0] for r in singles for x in r['dead_own']}
    rows = [1 << i for i in range(W.width)]
    eligible = []
    for ix, e in enumerate(W.rec):
        op, d = e[0], e[1]
        if op == 'ERASE':
            rows[d] = 0
        elif op == 'ADD':
            rows[d] ^= rows[e[2]]
        elif op == 'Q' and rows[d] & hmask and ix not in deadq:
            eligible.append((ix, d, e[4], rows[d]))
    remaining = Counter()
    for ix, d, k, row in eligible:
        remaining[row] += math.ceil(4 * k ** t - 1e-12)
    tokens = sum(remaining.values())
    sets = []
    while remaining:
        bs, chosen = _Basis(), []
        for r, cnt in sorted(remaining.items(), key=lambda kv: (-kv[1], kv[0])):
            if bs.add(r):
                chosen.append(r)
        for r in chosen:
            remaining[r] -= 1
            if not remaining[r]:
                del remaining[r]
        sets.append(len(chosen))
    return {'eligible': len(eligible), 'distinct_rows': len({q[3] for q in eligible}), 'tokens': tokens,
            'N': len(sets), 'set_sizes': sets, 'capacity_per_owned_helper': len(sets) / 4}


class _Basis:
    def __init__(self):
        self.b = {}

    def reduce(self, v):
        while v:
            p = v.bit_length() - 1
            if p not in self.b:
                return v
            v ^= self.b[p]
        return 0

    def add(self, v):
        v = self.reduce(v)
        if v:
            self.b[v.bit_length() - 1] = v
            return True
        return False

    def contains(self, v):
        return self.reduce(v) == 0


# ---------------------------------------------------------------- joint deadness
def partner_pairs(W):
    """Ordered pairs (h, p): at some time the content of helper h reaches no retained output except those
    of h and of one other helper p.  Owning both can lengthen h's dead intervals."""
    mats = W.mats
    adj = [({mats.I: 1 << i} if i not in W.owned else {}) for i in range(W.width)]
    hmask = sum(1 << h for h in W.helpers)
    found = set()
    hs = set(W.helpers)

    def check(h):
        u = support(adj[h]) & ~(1 << h)
        if u and not (u & ~hmask) and not (u & (u - 1)):
            found.add((h, u.bit_length() - 1))
    for h in W.helpers:
        check(h)
    for ix in range(len(W.rec) - 1, -1, -1):
        e = W.rec[ix]
        op, d = e[0], e[1]
        touched = d
        if op == 'ADD':
            adj[e[2]] = padd(adj[e[2]], adj[d])
            touched = e[2]
        elif op == 'Q':
            Q = W.qmat(e[2], e[3])
            adj[d] = {mats.mul(m, Q): b for m, b in adj[d].items()}
        elif op == 'ERASE':
            adj[d] = {}
        if touched in hs:
            check(touched)
    return sorted(found)


def reads_before_injection(W, singles):
    """Number of ADD reads of each owned helper before its injection point (must be zero for the
    parity argument: the owned input symbol then never leaves its own wire)."""
    bad = {}
    for r in singles:
        h = r['set'][0]
        b = r['epochs'][0]['inject_before']
        n = sum(1 for ix in range(b) if W.rec[ix][0] == 'ADD' and W.rec[ix][2] == h)
        if n:
            bad[h] = n
    return bad


def exact_joint_pair(W, rec, C):
    """Exact two-helper search under the joint schedule of rec (from analyze_sets with ignore_partners):
    requires one injection per helper; same candidate enumeration as pair_census."""
    t = 1 - float(C)
    a, b = rec['set']
    eps = rec['epochs']
    need = [e for e in eps if e['best'] or any(h == e['helper'] and j == e['epoch']
                                                 for m in rec['multi'] for (h, j) in m[3])]
    if sorted(e['helper'] for e in need) != [a, b]:
        raise ValueError('exact_joint_pair needs one active epoch per helper')
    inject, inj, bit = defaultdict(list), {}, W.width
    for e in need:
        inject[e['inject_before']].append((e['helper'], bit))
        inj[e['helper']] = bit
        bit += 1
    queries, snaps, _, _, _ = W.replay(inject)
    rec1 = {h: {'dead_own': [x for x in rec['dead_own'] if x[1] == h]} for h in (a, b)}
    return _pair_exact(W, queries, snaps, inj, a, b, None, rec1, t)
