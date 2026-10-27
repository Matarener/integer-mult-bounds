"""Rung removal with compensated read shifts (generalises the PR5827 rewrite and the PR5907 rerouting).

Remove an intermediate stop X of register r (MOVE A->X at i, MOVE X->B at j  ==>  one MOVE A->B at slot k, k = i or j).
Every event e (dst += q*src) at X that touches r is re-placed at a slot p' where both operands sit in r's new chart
(A before k, B after k).  If the operand that is READ (src) receives writes src += c*u between p and p', each such write is
forwarded as one compensating event dst += (+/-) q*c*u, placed at the first slot after (backward shift) or before (forward shift)
the write where dst and u share a chart and u still holds the value it had at the write.  Shifts that cross a read of dst
are refused.  Each candidate program is checked by the exact replay (all rows, charts, nesting, ownership) and priced.
Every stop and its outcome is appended to the JSONL log as soon as it is decided.

usage: python3 rung2.py WORD.json.gz LOG.jsonl [--window N] [--maxcomp C] [--shard k/K]
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
from bisect import bisect_right
from collections import defaultdict
from fractions import Fraction as Q
import json, sys, time
import p104
from rung import timelines, chart
CH = chart

ARG = lambda k, d: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
WINDOW = int(ARG('--window', 3000))
MAXCOMP = int(ARG('--maxcomp', 6))
NSLOT = int(ARG('--nslot', 6))
MAXREAD = int(ARG('--maxread', 4))


def dyadic(q):
    return q != 0 and q.denominator & (q.denominator-1) == 0 and abs(q)+1 < 2**16


def value_interval(prog, x, t, skip):
    """Slots (a, b) between which register x holds the value it has just after event t (writes to x bound it)."""
    a = t+1
    b = t+1
    while b < len(prog) and (b in skip or prog[b][1] != x or prog[b][0] == 'MOVE'):
        b += 1
    return a, b


def place(prog, tl, d, u, coef, a, b, near, r, A, B, skip):
    """Placements of ADD d += coef*u in slots [a, b] (u constant there): nearest slot to `near` per chart of r."""
    out = []
    for H in ((A, B) if d == r or u == r else (None,)):
        fr = lambda x, q: H if x == r else CH(tl, x, q)
        zs = sorted(range(a, b+1), key=lambda z: abs(z-near))[:WINDOW]
        for z in zs:
            cd = fr(d, z)
            if cd is not None and cd == fr(u, z):
                out.append((z, ['ADD', d, u, str(coef), cd], H)); break
    return out


def plan_event(prog, tl, p, r, A, B, lo, hi, skip):
    """Options for event p: list of lists of (slot, event, chart-of-r-or-None)."""
    from itertools import product
    e = prog[p]
    if e[0] != 'ADD':
        return []
    d, s, qq = e[1], e[2], Q(e[3])
    opts = []
    for H in ((A, B) if r is not None else (None,)):
        fr = lambda x, q: H if x == r else CH(tl, x, q)
        for direction in (-1, 1):
            q = p if direction < 0 else p+1
            comps = []
            readers = []
            steps = 0
            found = 0
            while lo < q <= hi and steps < WINDOW:
                idx = q if direction < 0 else q-1
                if idx != p and idx not in skip and 0 <= idx < len(prog):
                    g = prog[idx]
                    if g[0] in ('ADD', 'COPY') and g[2] == d:
                        if g[0] != 'ADD' or g[1] == s or len(readers) >= MAXREAD:
                            break
                        readers.append((idx, g))
                        idx = -1
                    if idx >= 0 and g[1] == d and g[0] in ('SCALE', 'COPY', 'INIT', 'CLEAR'):
                        break
                    if g[1] == s and g[0] != 'MOVE':
                        if g[0] != 'ADD' or g[2] == d:
                            break
                        comps.append((idx, g))
                        if len(comps) > MAXCOMP:
                            break
                cd = fr(d, q)
                if cd is not None and cd == fr(s, q):
                    sign = 1 if direction < 0 else -1
                    alts, ok = [], True
                    for cidx, g in comps:
                        c, u = Q(g[3]), g[2]
                        coef = sign*qq*c
                        if not dyadic(coef):
                            ok = False; break
                        a_, b_ = value_interval(prog, u, cidx, skip)
                        # u keeps its value from the last write before cidx too
                        a2 = cidx
                        while a2 > 0 and (a2-1 in skip or prog[a2-1][1] != u or prog[a2-1][0] == 'MOVE'):
                            a2 -= 1
                        pl = place(prog, tl, d, u, coef, max(a2, lo+1), min(b_, hi), p, r, A, B, skip)
                        if not pl:
                            ok = False; break
                        alts.append(pl)
                    # readers of dst crossed by the shift see (backward) or miss (forward) q*s: correct each reader
                    if ok and readers:
                        sl = q if direction < 0 else p          # s holds the shifted-in value around this slot
                        a3 = sl
                        while a3 > 0 and (a3-1 in skip or prog[a3-1][1] != s or prog[a3-1][0] == 'MOVE'):
                            a3 -= 1
                        b3 = sl
                        while b3 < len(prog) and (b3 in skip or prog[b3][1] != s or prog[b3][0] == 'MOVE'):
                            b3 += 1
                        for ridx, g in readers:
                            t_, c_ = g[1], Q(g[3])
                            coef = -sign*c_*qq
                            if not dyadic(coef) or t_ == s:
                                ok = False; break
                            pl = place(prog, tl, t_, s, coef, max(a3, lo+1), min(b3, hi), ridx, r, A, B, skip)
                            if not pl:
                                ok = False; break
                            alts.append(pl)
                    if ok:
                        ev = list(e); ev[-1] = cd
                        head = (q, ev, H)
                        for pick in product(*alts):
                            opts.append([head] + list(pick))
                    found += 1
                    if found >= NSLOT:
                        break
                q += direction
                steps += 1
    return opts


def attempt(w, tl, moves, r, mi):
    from itertools import product
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
    options = []
    for p in U:
        o = plan_event(prog, tl, p, r, A, B, lo, nxt, skip)
        if not o:
            return {'ok': False, 'why': 'no plan', 'event': p, 'U': len(U)}
        options.append(sorted(o, key=len)[:24])
    best, count = None, 0
    for combo in product(*options):
        count += 1
        if count > 20000:
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
    for c, (r, mi) in enumerate(stops):
        for mode in ('any',):
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
