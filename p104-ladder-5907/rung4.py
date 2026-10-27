"""Rung removal with recursive compensations (successor of rung2.py).

A virtual update  d += q*s  carries a value time vt (s is read with the value it holds at vt) and an effect time et
(readers of d must see it from et on).  It may be executed at any slot z where d and s share a chart; then
  * every write s += c*u between z and vt becomes a compensation  d += (+/-) q*c*u  (value time = that write),
  * every read t += c*d between z and et becomes a compensation  t += (-/+) c*q*s  (effect time = that read),
and each compensation is itself a virtual update, placed recursively (depth-limited).  SCALE/COPY/INIT/CLEAR crossings are
refused.  A stop X of register r (A -> X -> B) is removed by placing every event of r at X this way, with r held in A
before the merged MOVE A->B and in B after it.  Every candidate is checked by exact replay and priced; every outcome is
logged at once.

usage: python3 rung4.py WORD.json.gz LOG.jsonl [--depth D] [--window N] [--nalt K] [--shard k/K] [--regs ...]
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product
import json, sys, time
import p104
from rung import timelines, chart

ARG = lambda k, d: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
DEPTH = int(ARG('--depth', 2))
WINDOW = int(ARG('--window4', 1500))
NALT = int(ARG('--nalt', 4))
MAXC = int(ARG('--maxc', 5))
BUDGET = float(ARG('--budget', 20))
DEADLINE = [0.0]


class Timeout(Exception):
    pass


def dyadic(q):
    return q != 0 and q.denominator & (q.denominator-1) == 0 and abs(q)+1 < 2**16


class Ctx:
    def __init__(self, prog, tl, r, A, B, lo, hi, skip):
        self.prog, self.tl, self.r, self.A, self.B, self.lo, self.hi, self.skip = prog, tl, r, A, B, lo, hi, skip

    def hyps(self, d, s):
        return (self.A, self.B) if self.r is not None and self.r in (d, s) else (None,)

    def fr(self, x, z, H):
        return H if x == self.r else chart(self.tl, x, z)


def crossing(ctx, a, b):
    """Original event indices in [a, b) that are not being moved."""
    return [i for i in range(max(a, 0), min(b, len(ctx.prog))) if i not in ctx.skip]


def plan_virtual(ctx, d, s, q, vt, et, depth):
    """Alternatives: lists of (slot, event, H) realising d += q*s(vt) with effect at et."""
    if not dyadic(q) or d == s:
        return []
    prog = ctx.prog
    out = []
    if time.time() > DEADLINE[0]:
        raise Timeout()
    for H in ctx.hyps(d, s):
        centre = et
        zs = sorted(range(max(ctx.lo+1, centre-WINDOW), min(ctx.hi, centre+WINDOW)+1), key=lambda z: (abs(z-centre), z))
        for z in zs:
            cd = ctx.fr(d, z, H)
            if cd is None or cd != ctx.fr(s, z, H):
                continue
            comps, bad = [], False
            for i in crossing(ctx, min(z, vt), max(z, vt)):
                g = prog[i]
                if g[1] == s and g[0] != 'MOVE':
                    if g[0] != 'ADD' or g[2] == d:
                        bad = True; break
                    sign = 1 if z < vt else -1
                    comps.append((d, g[2], sign*q*Q(g[3]), i, z))
            if bad:
                continue
            for i in crossing(ctx, min(z, et), max(z, et)):
                g = prog[i]
                if g[0] == 'COPY' and g[2] == d or g[1] == d and g[0] in ('SCALE', 'COPY', 'INIT', 'CLEAR'):
                    bad = True; break
                if g[0] == 'ADD' and g[2] == d:
                    if g[1] == s:
                        bad = True; break
                    sign = -1 if z < et else 1
                    comps.append((g[1], s, sign*Q(g[3])*q, z if z < et else vt, i))
            if bad or len(comps) > MAXC or (comps and depth == 0):
                continue
            alts = []
            for (d2, s2, q2, vt2, et2) in comps:
                sub = plan_virtual(ctx, d2, s2, q2, vt2, et2, depth-1)
                if not sub:
                    bad = True; break
                alts.append(sorted(sub, key=len)[:2])
            if bad:
                continue
            for pick in product(*alts):
                out.append([(z, ['ADD', d, s, str(q), cd], H)] + [x for p_ in pick for x in p_])
            if len(out) >= NALT:
                return out
    return out


def attempt(w, tl, moves, r, mi):
    prog = w['program']
    i, j = moves[r][mi], moves[r][mi+1]
    A, X, B, priv = prog[i][2], prog[i][3], prog[j][3], prog[i][4]
    lo = moves[r][mi-1] if mi > 0 else -1
    nxt = moves[r][mi+2] if mi+2 < len(moves[r]) else len(prog)
    touch = lambda p: prog[p][1] == r or (prog[p][0] in ('ADD', 'COPY') and prog[p][2] == r)
    U = [p for p in range(i+1, j) if touch(p)]
    before = [p for p in range(lo+1, i) if touch(p)]
    after = [p for p in range(j+1, nxt) if touch(p)]
    klo = (before[-1]+1) if before else lo+1
    khi = after[0] if after else nxt
    skip = set(U) | {i, j}
    ctx = Ctx(prog, tl, r, A, B, -1, len(prog), skip)
    options = []
    for p in U:
        e = prog[p]
        if e[0] != 'ADD':
            return {'ok': False, 'why': 'non-ADD at stop (%s)' % e[0], 'U': len(U)}
        try:
            o = plan_virtual(ctx, e[1], e[2], Q(e[3]), p, p, DEPTH)
        except Timeout:
            return {'ok': False, 'why': 'time budget', 'event': p, 'U': len(U)}
        if not o:
            return {'ok': False, 'why': 'no plan', 'event': p, 'U': len(U)}
        options.append(sorted(o, key=len)[:NALT])
    best, count = None, 0
    for combo in product(*options):
        count += 1
        if count > 5000:
            break
        ins = [x for o in combo for x in o]
        a_hi = max([z for z, e, H in ins if H == A] + [klo])
        b_lo = min([z for z, e, H in ins if H == B] + [khi])
        if a_hi > b_lo:
            continue
        cost = len(ins)-len(U)
        if best is None or cost < best[0]:
            best = (cost, ins, a_hi)
    if best is None:
        return {'ok': False, 'why': 'no consistent k', 'U': len(U)}
    cost, ins, k = best
    keyed = [((q, 1, 0), e) for q, e in enumerate(prog) if q not in skip]
    keyed.append(((k, 0, 1), ['MOVE', r, A, B, priv]))
    for n, (q, e, H) in enumerate(ins):
        keyed.append(((q, 0, 0 if H == A else 2 if H == B else 1, n), e))
    keyed.sort(key=lambda t: t[0])
    new = dict(w); new['program'] = [e for _, e in keyed]
    try:
        info = p104.price(new)
    except p104.Illegal as x:
        return {'ok': False, 'why': 'replay: '+str(x), 'U': len(U), 'added': cost}
    return {'ok': True, 'U': len(U), 'added': cost, 'k': k, 'A': A, 'X': X, 'B': B, 'word': new, **info}


def main():
    w = p104.read(sys.argv[1])
    out = open(sys.argv[2], 'a')
    base = p104.price(w)
    print('base', {k: str(v) for k, v in base.items()}, flush=True)
    tl, moves = timelines(w)
    kk, K = map(int, ARG('--shard', '0/1').split('/'))
    stops = [(r, mi) for r in sorted(moves) for mi in range(len(moves[r])-1)][kk::K]
    if '--regs' in sys.argv:
        regs = {int(x) for x in ARG('--regs', '').split(',')}
        stops = [s for s in stops if s[0] in regs]
    wd = p104.Path(sys.argv[2]+'.words'); wd.mkdir(exist_ok=True)
    t0 = time.time()
    done = set()
    if p104.Path(sys.argv[2]).exists():
        done = {(x['reg'], x['stop']) for x in map(json.loads, open(sys.argv[2]))}
    for c, (r, mi) in enumerate(stops):
        if (r, mi) in done:
            continue
        DEADLINE[0] = time.time()+BUDGET
        res = attempt(w, tl, moves, r, mi)
        word = res.pop('word', None)
        row = {'reg': r, 'stop': mi, **{a: str(b) if a.startswith('kappa') else b for a, b in res.items()}}
        if res['ok']:
            row['gain'] = float(res['kappa_lo']-base['kappa_lo'])
            row['events_delta'] = res['events']-base['events']
            (wd/('r%d_s%d.json' % (r, mi))).write_text(json.dumps(word['program']))
        out.write(json.dumps(row)+'\n'); out.flush()
        print(c, round(time.time()-t0), json.dumps(row)[:240], flush=True)


if __name__ == '__main__':
    main()
