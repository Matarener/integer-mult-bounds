#!/usr/bin/env python3
"""Chart-assignment rigidity of the P104 local word (PR6030, PR5907, PR5827).

The paid rank of a MOVE in PR5827's local.py is |dim(to) - dim(from)| and a
productive helper's rank is dim(final) - dim(initial).  Scalar events need a
common chart but do not care which one.  This verifier searches five classes of
edits that keep the scalar program's content and change only charts, MOVEs or
event timing.  Class A proposals and positive class B proposals are replayed by
the unmodified PR5827 local.py; classes C, D and E are priced by the nesting
rule and the per-LOCAL proxy (none is positive on the real words):

  A. rung skip by commuting retiming: delete one stay a -> b -> c of a register,
     moving each of its scalar events (commuting) to a slot where the partner is
     at a (before the merged move) or c (after it);
  B. meeting re-chart to an existing frame: a connected set of stays joined by
     scalar events at frame b moves to another listed frame (a rank-0 move
     disappears); optionally helper (not main) endpoints may follow;
  C. the same, to an arbitrary subspace: cost depends only on dimension, so the
     best frame is found exactly over every dimension between the span of the
     lower neighbours and the intersection of the upper ones;
  D. split skip: delete a stay a -> b -> c and re-chart each partner
     sub-meeting wholesale to a (events before a threshold) or c (after);
  E. joint re-chart of two meetings linked by a MOVE, over listed frames.

Three synthetic controls on the PR6030 word (an inserted unread rung, a
worsened meeting chart, and a rung holding two SCALEs) must be found.  Gains use t = 1 - 0.0031258 per LOCAL
call, as a ranking proxy; a positive find would still need the full chain.

Prepared by Josie Elliston with Claude Opus 5.5 (Anthropic) via Claude Code.
Apache-2.0.
"""
import bisect
import copy
import gzip
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORDS = {
    'PR6030': 'research/p104-helper470-twin-rung-removal/WORD.json.gz',
    'PR5907': 'research/p104-helper468-rung-removal/WORD.json.gz',
    'PR5827': 'research/p104-unread-path-resynthesis/WORD.json.gz',
}
C0 = 0.0031258
T_EXP = 1 - C0
EPS = 1e-12


def h(x):
    return abs(x) ** T_EXP if x else 0.0


def load_local():
    path = ROOT / 'research/p104-unread-path-resynthesis/local.py'
    spec = importlib.util.spec_from_file_location('pr5827_local', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L = load_local()


def span_mask(basis):
    s = {0}
    for v in basis:
        s |= {x ^ v for x in s}
    m = 0
    for x in s:
        m |= 1 << x
    return m


def mask_dim(m):
    return bin(m).count('1').bit_length() - 1


def span_of_masks(ms):
    elems = {0}
    for m in ms:
        x = m
        while x:
            lb = x & -x
            v = lb.bit_length() - 1
            x ^= lb
            if v not in elems:
                elems |= {e ^ v for e in elems}
    out = 0
    for e in elems:
        out |= 1 << e
    return out


def regs(e):
    return (e[1], e[2]) if e[0] in ('ADD', 'COPY') else (e[1],)


def rw(e):
    """(reads, additive writes, overwriting/multiplicative writes) on rows."""
    op = e[0]
    if op == 'ADD':
        return {e[2]}, {e[1]}, set()
    if op == 'COPY':
        return {e[2]}, set(), {e[1]}
    if op == 'SCALE':
        return {e[1]}, set(), {e[1]}
    if op in ('INIT', 'CLEAR'):
        return set(), set(), {e[1]}
    return set(), set(), set()


def commute(e, x):
    r1, a1, o1 = rw(e)
    r2, a2, o2 = rw(x)
    w1, w2 = a1 | o1, a2 | o2
    return not (w1 & r2 or w2 & r1 or o1 & w2 or o2 & w1)


class Word:
    def __init__(self, w):
        self.w = w
        self.P = w['program']
        self.F = w['frames']
        self.dim = [len(f) for f in self.F]
        self.M = [span_mask(f) for f in self.F]
        self.public, self.owned = w['public'], w['owned_fields']
        live = set(w['live'])
        self.main = live | {r + 112 for r in live}
        self._timeline()
        self._stays()

    def sub(self, a, b):
        return self.M[a] & ~self.M[b] == 0

    def _timeline(self):
        self.moves = defaultdict(list)
        self.touch = defaultdict(list)
        for t, e in enumerate(self.P):
            if e[0] == 'MOVE':
                self.moves[e[1]].append((t, e[2], e[3]))
                self.touch[e[1]].append(t)
            else:
                for r in regs(e):
                    self.touch[r].append(t)
        self.move_times = {r: [m[0] for m in ms] for r, ms in self.moves.items()}

    def frame_at(self, r, s):
        """Frame seen by an event inserted before original event s."""
        ms = self.moves.get(r, [])
        k = bisect.bisect_left(self.move_times.get(r, []), s)
        if k:
            return ms[k - 1][2]
        if r < self.public:
            return self.w['initial'][r]
        f = None
        for t in self.touch[r]:
            if t >= s:
                break
            if self.P[t][0] == 'INIT':
                f = self.P[t][2]
            elif self.P[t][0] == 'CLEAR':
                f = None
        return f

    def _stays(self):
        w, P = self.w, self.P
        self.stays, open_stay = [], {}
        self.ev_stays = defaultdict(list)

        def open_(r, f, s, prev, kind):
            self.stays.append(dict(reg=r, frame=f, start=s, end=None, prev=prev,
                                   next=None, kind=kind, nextkind=None))
            open_stay[r] = len(self.stays) - 1
        for r in range(self.public):
            open_(r, w['initial'][r], -1, None, 'initial')
        for i, e in enumerate(P):
            op = e[0]
            if op == 'MOVE':
                sid = open_stay[e[1]]
                self.stays[sid].update(end=i, next=e[3], nextkind='move')
                open_(e[1], e[3], i, e[2], 'move')
            elif op == 'INIT':
                open_(e[1], e[2], i, None, 'init')
                self.ev_stays[i].append(open_stay[e[1]])
            elif op == 'CLEAR':
                sid = open_stay.pop(e[1])
                self.stays[sid].update(end=i, nextkind='clear')
                self.ev_stays[i].append(sid)
            else:
                for r in regs(e):
                    self.ev_stays[i].append(open_stay[r])
        for r, sid in open_stay.items():
            self.stays[sid].update(end=len(P), nextkind='final')
        par = list(range(len(self.stays)))

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for i, sids in self.ev_stays.items():
            for s in sids[1:]:
                par[find(s)] = find(sids[0])
        self.root = [find(s) for s in range(len(self.stays))]
        self.comp = defaultdict(list)
        for s, rt in enumerate(self.root):
            self.comp[rt].append(s)
        self.stay_events = defaultdict(list)
        for i, sids in self.ev_stays.items():
            for s in sids:
                self.stay_events[s].append(i)
        for s in self.stay_events:
            self.stay_events[s].sort()
        for members in self.comp.values():
            assert len({self.stays[m]['frame'] for m in members}) == 1

    # ---- class B/D helpers -------------------------------------------------
    def member_ok(self, st, f, allow_end):
        """(paid_old, paid_new, endpoint_changed) for re-charting stay st to f, or None."""
        r, b = st['reg'], st['frame']
        priv = r >= self.public
        a, c = st['prev'], st['next']
        M, dim = self.M, self.dim
        if a is not None and a != f and M[a] == M[f]:
            return None
        if c is not None and c != f and M[c] == M[f]:
            return None
        old = new = 0.0
        endch = False
        if st['kind'] == 'move':
            if not (self.sub(f, a) if priv else self.sub(a, f)):
                return None
            old += h(dim[b] - dim[a])
            new += h(dim[f] - dim[a])
        elif st['kind'] == 'initial' and f != b:
            if r in self.main or not allow_end:
                return None
            endch = True
        if st['nextkind'] == 'move':
            if not (self.sub(c, f) if priv else self.sub(f, c)):
                return None
            old += h(dim[c] - dim[b])
            new += h(dim[c] - dim[f])
        elif st['nextkind'] == 'final' and f != b:
            if r in self.main or not allow_end:
                return None
            endch = True
        return old, new, endch

    def apply_rechart(self, root, f):
        P2 = [list(e) for e in self.P]
        ini, fin = list(self.w['initial']), list(self.w['final'])
        drop = set()
        for m in self.comp[root]:
            st = self.stays[m]
            r = st['reg']
            if st['kind'] == 'move':
                if f == st['prev']:
                    drop.add(st['start'])
                else:
                    P2[st['start']][3] = f
            elif st['kind'] == 'initial':
                ini[r] = f
            elif st['kind'] == 'init':
                P2[st['start']][2] = f
            if st['nextkind'] == 'move':
                if f == st['next']:
                    drop.add(st['end'])
                else:
                    P2[st['end']][2] = f
            elif st['nextkind'] == 'final':
                fin[r] = f
            elif st['nextkind'] == 'clear':
                P2[st['end']][2] = f
            for i in self.stay_events[m]:
                if self.P[i][0] not in ('INIT', 'CLEAR'):
                    P2[i][-1] = f
        w2 = dict(self.w)
        w2['program'] = [e for i, e in enumerate(P2) if i not in drop]
        w2['initial'], w2['final'] = ini, fin
        return w2


def replay_ok(w2):
    try:
        return L.replay(w2)
    except ValueError:
        return None


def target_gain(W, w2):
    """Signed change of the per-LOCAL proxy moment: helper credits minus paid."""
    base, new = L.replay(W.w), L.replay(w2)
    def mom(c):
        return sum(n * h(r) for r, n in c.items())
    return (mom(new['helpers']) - mom(base['helpers'])) - (mom(new['paid']) - mom(base['paid']))


# ---- class A ---------------------------------------------------------------
def class_a(W):
    P = W.P
    out = Counter()
    passes = []

    def slots(t, rs, lo, hi, skip):
        # Events of the deleted stay itself are relocated too, so they are not
        # barriers here; the exact replay rejects any proposal whose relocated
        # events end up in a non-equivalent order.
        e = P[t]
        inter = sorted({x for r in rs for x in W.touch[r] if lo < x < hi and x != t and x not in skip})
        res = []
        s, pos = t + 1, bisect.bisect_right(inter, t)
        while True:
            nxt = inter[pos] if pos < len(inter) else hi
            res.append((s, nxt))
            if nxt >= hi or (P[nxt][0] != 'MOVE' and not commute(e, P[nxt])):
                break
            s, pos = nxt + 1, pos + 1
        s, pos = t, bisect.bisect_left(inter, t) - 1
        while pos >= 0:
            prv = inter[pos]
            res.append((prv + 1, s))
            if P[prv][0] != 'MOVE' and not commute(e, P[prv]):
                break
            s, pos = prv, pos - 1
        if pos < 0:
            res.append((lo + 1, s))
        return res

    def partner_slots(p, f, x, y):
        if x > y:
            return []
        cands = [x] + [m[0] + 1 for m in W.moves.get(p, []) if x <= m[0] + 1 <= y]
        return [s for s in cands if W.frame_at(p, s) == f]

    for r in sorted(W.moves):
        ms = W.moves[r]
        for k in range(len(ms) - 1):
            out['stays'] += 1
            (i, a, b), (j, _, c) = ms[k], ms[k + 1]
            lo = ms[k - 1][0] if k else -1
            hi = ms[k + 2][0] if k + 2 < len(ms) else len(P)
            ops = [t for t in W.touch[r] if i < t < j and P[t][0] != 'MOVE']
            if any(P[t][0] in ('INIT', 'CLEAR') for t in ops):
                out['init/clear inside'] += 1
                continue
            plan = []
            skip = set(ops)
            for t in ops:
                e = P[t]
                A, C = [], []
                if e[0] == 'SCALE':
                    # no partner: any reachable slot where r is at a or at c
                    for x, y in slots(t, {r}, lo, hi, skip):
                        for u, v, out_ in ((max(x, lo + 1), min(y, j), A), (max(x, i + 1), min(y, hi), C)):
                            if u <= v:
                                out_ += [u, v]
                    plan.append((t, A, C))
                    continue
                p = e[2] if e[1] == r else e[1]
                for x, y in slots(t, set(regs(e)), lo, hi, skip):
                    A += partner_slots(p, a, max(x, lo + 1), min(y, j))
                    C += partner_slots(p, c, max(x, i + 1), min(y, hi))
                plan.append((t, A, C))
            chosen = None
            for T in range(i, j + 1):
                choice = []
                for t, A, C in plan:
                    As = [s for s in A if s <= T]
                    Cs = [s for s in C if s > T]
                    if As:
                        choice.append((t, a, max(As)))
                    elif Cs:
                        choice.append((t, c, min(Cs)))
                    else:
                        break
                else:
                    chosen = (T, choice)
                    break
            if chosen is None:
                out['no retiming'] += 1
                continue
            T, choice = chosen
            moved = {t: (f, s) for t, f, s in choice}
            ins = defaultdict(list)
            for t, f, s in choice:
                ev = list(P[t])
                ev[-1] = f
                ins[s].append((t, ev))
            new = []
            for idx, e in enumerate(P):
                new += [ev for _, ev in sorted(ins.get(idx, []))]
                if idx == T:
                    new.append(['MOVE', r, a, c, P[i][4]])
                if idx in (i, j):
                    continue
                if idx in moved:
                    continue
                new.append(e)
            new += [ev for _, ev in sorted(ins.get(len(P), []))]
            w2 = dict(W.w)
            w2['program'] = new
            if replay_ok(w2) is None:
                out['proposal rejected by replay'] += 1
                continue
            out['replay pass'] += 1
            passes.append({'register': r, 'frames': [a, b, c], 'gain': target_gain(W, w2)})
    return dict(out), passes


# ---- class B ---------------------------------------------------------------
def class_b(W, allow_end):
    """Nesting-legal re-charts are priced exactly in the proxy; only gainers are replayed."""
    legal, passes = 0, []
    for root, members in W.comp.items():
        b = W.stays[members[0]]['frame']
        for f in range(len(W.F)):
            if f == b or W.M[f] == W.M[b]:
                continue
            res = [W.member_ok(W.stays[m], f, allow_end) for m in members]
            if any(x is None for x in res):
                continue
            g = sum(x[0] - x[1] for x in res)
            ok = True
            for m, x in zip(members, res):
                if not x[2]:
                    continue
                st = W.stays[m]
                r = st['reg']
                ini, fin = W.w['initial'][r], W.w['final'][r]
                ini2 = f if st['kind'] == 'initial' else ini
                fin2 = f if st['nextkind'] == 'final' else fin
                if W.dim[fin2] - W.dim[ini2] <= 0:
                    ok = False
                    break
                g += h(W.dim[fin2] - W.dim[ini2]) - h(W.dim[fin] - W.dim[ini])
            if not ok:
                continue
            legal += 1
            if g > EPS:
                w2 = W.apply_rechart(root, f)
                if replay_ok(w2) is not None:
                    passes.append({'meeting': root, 'from': b, 'to': f, 'gain': target_gain(W, w2)})
    return legal, passes


# ---- class C ---------------------------------------------------------------
def class_c(W, allow_end):
    FULL = (1 << 512) - 1
    free, slack, positive = 0, 0, []
    for root, members in W.comp.items():
        b = W.stays[members[0]]['frame']
        lows, highs, terms, fixed = [], [], [], False
        for m in members:
            st = W.stays[m]
            r = st['reg']
            priv = r >= W.public
            a, c = st['prev'], st['next']
            if st['kind'] == 'move':
                (highs if priv else lows).append(W.M[a])
                terms.append(('down' if priv else 'up', W.dim[a]))
            elif st['kind'] == 'initial':
                if r in W.main or not allow_end:
                    fixed = True
                else:
                    terms.append(('credit_from', W.dim[W.w['final'][r]]))
            if st['nextkind'] == 'move':
                (lows if priv else highs).append(W.M[c])
                terms.append(('down_to' if priv else 'up_to', W.dim[c]))
            elif st['nextkind'] == 'final':
                if r in W.main or not allow_end:
                    fixed = True
                else:
                    terms.append(('credit_to', W.dim[W.w['initial'][r]]))
        if fixed:
            continue
        free += 1
        Lm = span_of_masks(lows)
        Hm = FULL
        for x in highs:
            Hm &= x
        assert Lm & ~Hm == 0

        def cost(d):
            tot = 0.0
            for k, x in terms:
                if k in ('up', 'down'):
                    tot += h(d - x)       # in-move from x (up) or into d from x (down)
                elif k in ('up_to', 'down_to'):
                    tot += h(x - d)
                elif k == 'credit_from':
                    if x - d <= 0:
                        return float('inf')
                    tot -= h(x - d)
                else:
                    if d - x <= 0:
                        return float('inf')
                    tot -= h(d - x)
            return tot
        dl, dh, db = mask_dim(Lm), mask_dim(Hm), W.dim[b]
        slack += dl < dh
        best = min(cost(d) for d in range(dl, dh + 1))
        if cost(db) - best > EPS:
            positive.append({'meeting': root, 'frame': b, 'dims': [dl, db, dh], 'gain': cost(db) - best})
    return free, slack, positive


# ---- class D ---------------------------------------------------------------
def class_d(W):
    out, positive = Counter(), []
    for sid, st in enumerate(W.stays):
        if st['kind'] != 'move' or st['nextkind'] != 'move':
            continue
        out['stays'] += 1
        a, b, c = st['prev'], st['frame'], st['next']
        members = W.comp[W.root[sid]]
        par = {m: m for m in members if m != sid}

        def f2(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x
        for m in par:
            for i in W.stay_events[m]:
                for s2 in W.ev_stays[i]:
                    if s2 in par and s2 != m:
                        par[f2(s2)] = f2(m)
        groups = defaultdict(list)
        for m in par:
            groups[f2(m)].append(m)
        evs = W.stay_events[sid]
        eg = []
        for i in evs:
            ps = [s2 for s2 in W.ev_stays[i] if s2 != sid]
            eg.append(f2(ps[0]) if ps and W.P[i][0] != 'SCALE' else None)

        def gcost(g, f):
            tot = 0.0
            for m in groups[g]:
                res = W.member_ok(W.stays[m], f, False)
                if res is None:
                    return None
                tot += res[0] - res[1]
            return tot
        gs = {g for g in eg if g is not None}
        gA = {g: gcost(g, a) for g in gs}
        gC = {g: gcost(g, c) for g in gs}
        x, y = W.dim[b] - W.dim[a], W.dim[c] - W.dim[b]
        base = h(x) + h(y) - h(x + y)
        best = None
        for T in range(len(evs) + 1):
            sa = {eg[k] for k in range(T) if eg[k] is not None}
            sc = {eg[k] for k in range(T, len(evs)) if eg[k] is not None}
            if sa & sc or any(gA[g] is None for g in sa) or any(gC[g] is None for g in sc):
                continue
            g = base + sum(gA[q] for q in sa) + sum(gC[q] for q in sc)
            best = g if best is None else max(best, g)
        if best is None:
            out['no legal threshold'] += 1
        else:
            out['legal threshold'] += 1
            if best > EPS:
                positive.append({'stay': sid, 'register': st['reg'], 'frames': [a, b, c], 'gain': best})
    return dict(out), positive


# ---- class E ---------------------------------------------------------------
def class_e(W):
    """Joint re-chart of two meetings linked by at least one MOVE, over listed frames."""
    st = W.stays
    # moves as (event, from_stay, to_stay)
    mv_from = {}
    for sid, s in enumerate(st):
        if s['kind'] == 'move':
            mv_from[s['start']] = sid
    move_pairs = {}  # event -> (from stay, to stay)
    for sid, s in enumerate(st):
        if s['nextkind'] == 'move':
            move_pairs[s['end']] = (sid, mv_from[s['end']])
    stay_moves = defaultdict(list)
    for ev, (x, y) in move_pairs.items():
        stay_moves[x].append(ev); stay_moves[y].append(ev)
    def fixed(K):
        return any((st[m]['kind'] == 'initial' or st[m]['nextkind'] == 'final') for m in W.comp[K])
    links = set()
    for ev, (x, y) in move_pairs.items():
        K1, K2 = W.root[x], W.root[y]
        if K1 != K2 and not fixed(K1) and not fixed(K2):
            links.add((K1, K2))
    def frame_of(sid, assign):
        return assign.get(W.root[sid], st[sid]['frame'])
    def cost_and_ok(Ks, assign):
        evs = set(ev for K in Ks for m in W.comp[K] for ev in stay_moves[m])
        tot = 0.0
        for ev in evs:
            x, y = move_pairs[ev]
            a, b = frame_of(x, assign), frame_of(y, assign)
            priv = st[x]['reg'] >= W.public
            if a == b:
                continue
            if W.M[a] == W.M[b]:
                return None
            if not (W.sub(b, a) if priv else W.sub(a, b)):
                return None
            tot += h(W.dim[b] - W.dim[a])
        return tot
    def single_cands(K, other):
        # frames legal for K against moves not touching `other`
        out = []
        for f in range(len(W.F)):
            ok = True
            for m in W.comp[K]:
                for ev in stay_moves[m]:
                    x, y = move_pairs[ev]
                    if W.root[x] == other or W.root[y] == other:
                        continue
                    a = f if W.root[x] == K else st[x]['frame']
                    b = f if W.root[y] == K else st[y]['frame']
                    priv = st[x]['reg'] >= W.public
                    if a == b: continue
                    if W.M[a] == W.M[b] or not (W.sub(b, a) if priv else W.sub(a, b)):
                        ok = False; break
                if not ok: break
            if ok: out.append(f)
        return out
    n_pairs = n_legal = 0; positive = []
    for K1, K2 in sorted(links):
        n_pairs += 1
        base = cost_and_ok((K1, K2), {})
        c1, c2 = single_cands(K1, K2), single_cands(K2, K1)
        for f1 in c1:
            for f2 in c2:
                if f1 == st[W.comp[K1][0]]['frame'] and f2 == st[W.comp[K2][0]]['frame']:
                    continue
                c = cost_and_ok((K1, K2), {K1: f1, K2: f2})
                if c is None: continue
                n_legal += 1
                if base - c > EPS:
                    positive.append((base - c, K1, K2, f1, f2))
    return {'linked_free_pairs': n_pairs, 'legal_joint_recharts': n_legal, 'positive': len(positive)}, positive

def analyse(w):
    W = Word(w)
    a_stats, a_pass = class_a(W)
    b_legal, b_pos = class_b(W, False)
    be_legal, be_pos = class_b(W, True)
    c_free, c_slack, c_pos = class_c(W, False)
    ce_free, ce_slack, ce_pos = class_c(W, True)
    d_stats, d_pos = class_d(W)
    e_stats, e_pos = class_e(W)
    return {
        'events': len(W.P), 'moves': sum(len(v) for v in W.moves.values()),
        'stays': len(W.stays), 'meetings': len(W.comp),
        'A_rung_skip_retiming': {'counts': a_stats, 'replay_passing_skips': len(a_pass),
                                 'positive': sum(1 for x in a_pass if x['gain'] > EPS)},
        'B_existing_frame_rechart': {'nesting_legal': b_legal, 'positive': len(b_pos)},
        'B_with_helper_endpoints': {'nesting_legal': be_legal, 'positive': len(be_pos)},
        'C_any_subspace': {'free_meetings': c_free, 'with_dimension_slack': c_slack, 'positive': len(c_pos)},
        'C_with_helper_endpoints': {'free_meetings': ce_free, 'with_dimension_slack': ce_slack, 'positive': len(ce_pos)},
        'D_split_skip': {'counts': d_stats, 'positive': len(d_pos)},
        'E_joint_pair_rechart': e_stats,
    }, (a_pass, b_pos, c_pos, d_pos, e_pos)


def controls(w):
    W = Word(w)
    P = W.P
    # control 1: split the first public rank>=2 move a->c through a listed frame b.
    for idx, e in enumerate(P):
        if e[0] == 'MOVE' and not e[4] and W.dim[e[3]] - W.dim[e[2]] >= 2:
            a, c = e[2], e[3]
            bs = [b for b in range(len(W.F)) if W.sub(a, b) and W.sub(b, c)
                  and W.M[b] not in (W.M[a], W.M[c])]
            if bs:
                break
    w1 = copy.deepcopy(w)
    w1['program'] = P[:idx] + [['MOVE', e[1], a, bs[0], False], ['MOVE', e[1], bs[0], c, False]] + P[idx + 1:]
    assert L.replay(w1)
    # control 3: the same rung, now holding two SCALE -1 events that class A must relocate in order.
    w3 = copy.deepcopy(w)
    w3['program'] = P[:idx] + [['MOVE', e[1], a, bs[0], False], ['SCALE', e[1], '-1', bs[0]],
                               ['SCALE', e[1], '-1', bs[0]], ['MOVE', e[1], bs[0], c, False]] + P[idx + 1:]
    assert L.replay(w3)
    # control 2: re-chart the first fully-moving meeting to a smaller listed frame that strictly worsens it.
    w2 = None
    for root, members in W.comp.items():
        b = W.stays[members[0]]['frame']
        if any(W.stays[m]['kind'] != 'move' or W.stays[m]['nextkind'] != 'move' for m in members):
            continue
        for f in range(len(W.F)):
            if f == b or W.M[f] == W.M[b] or W.dim[f] >= W.dim[b]:
                continue
            if any(f in (W.stays[m]['prev'], W.stays[m]['next']) for m in members):
                continue
            res = [W.member_ok(W.stays[m], f, False) for m in members]
            if all(x is not None for x in res) and sum(x[0] - x[1] for x in res) < -1e-9:
                w2 = W.apply_rechart(root, f)
                ctrl2 = {'meeting': root, 'from': b, 'to': f, 'worsening': -sum(x[0] - x[1] for x in res)}
                break
        if w2 is not None:
            break
    assert L.replay(w2)
    r1, p1 = analyse(w1)
    r2, p2 = analyse(w2)
    r3, p3 = analyse(w3)
    return {
        'occupied_rung': {'found_by': {'A': r3['A_rung_skip_retiming']['positive'],
                                       'B': r3['B_existing_frame_rechart']['positive']},
                          'best_gain': round(max(x['gain'] for x in p3[0]), 12)},
        'inserted_rung': {'event': idx, 'register': e[1], 'frames': [a, bs[0], c],
                          'found_by': {'A': r1['A_rung_skip_retiming']['positive'],
                                       'B': r1['B_existing_frame_rechart']['positive'],
                                       'C': r1['C_any_subspace']['positive'],
                                       'D': r1['D_split_skip']['positive']},
                          'best_gain': round(max(x['gain'] for x in p1[1]), 12)},
        'worsened_meeting': {**ctrl2, 'worsening': round(ctrl2['worsening'], 12),
                             'found_by': {'B': r2['B_existing_frame_rechart']['positive'],
                                          'C': r2['C_any_subspace']['positive'],
                                          'E': r2['E_joint_pair_rechart']['positive']},
                             'best_gain': round(max(x['gain'] for x in p2[1]), 12)},
    }


def main():
    result = {'scope': 'Chart/MOVE/timing edits of the fixed scalar program; per-LOCAL proxy t = 1 - 0.0031258.',
              'words': {}}
    for name, rel in WORDS.items():
        w = json.loads(gzip.decompress((ROOT / rel).read_bytes()))
        result['words'][name], _ = analyse(w)
    w = json.loads(gzip.decompress((ROOT / WORDS['PR6030']).read_bytes()))
    result['controls_on_PR6030'] = controls(w)
    for name, r in result['words'].items():
        for key in ('A_rung_skip_retiming', 'B_existing_frame_rechart', 'B_with_helper_endpoints',
                    'C_any_subspace', 'C_with_helper_endpoints', 'D_split_skip', 'E_joint_pair_rechart'):
            assert r[key]['positive'] == 0, (name, key)
    ctl = result['controls_on_PR6030']
    assert all(v >= 1 for v in ctl['inserted_rung']['found_by'].values())
    assert all(v >= 1 for v in ctl['worsened_meeting']['found_by'].values())
    assert all(v >= 1 for v in ctl['occupied_rung']['found_by'].values())
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    out = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        out.write_text(text)
    elif out.read_text() != text:
        raise SystemExit('RESULT.json differs from the regenerated result')
    print('PASS_P104_CHART_ASSIGNMENT_RIGIDITY')


if __name__ == '__main__':
    main()
