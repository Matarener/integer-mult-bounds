"""Rung removal with partner-stop substitution (the PR5907 mechanism, automated).

For a stop X of register r (A -> X -> B), every partner o met at X swaps one adjacent stop of its own: its next stop Y
for B ('fwd') or its previous stop Y for A ('bwd'), when strict nesting allows.  o's other events at Y lose their common
chart and are re-placed by rung2's compensated shifts; then r's stop X is removed by rung2.attempt.  Every candidate
is replayed exactly and priced; each outcome is appended to the JSONL log at once.

usage: python3 subst.py WORD.json.gz CENSUS.json LOG.jsonl [--shard k/K] [--maxother N]
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
from itertools import product
import json, sys, time
import p104, rung2, rung4
ENGINE = rung4 if '--engine' in sys.argv and sys.argv[sys.argv.index('--engine')+1] == 'rung4' else rung2
from rung import timelines

ARG = lambda k, d: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
MAXOTHER = int(ARG('--maxother', 4))


def substitute(w, o, kind, X, A, B):
    """Swap o's stop adjacent to its X-stop.  Returns (word, broken event indices) or None."""
    prog = w['program']
    tl, moves = timelines(w)
    times, frames = tl[o]
    live = set(w['live'])
    stops = [(frames[a], times[a]) for a in range(len(times))]      # (frame, entering event or -1)
    a = next((a for a in range(len(stops)) if stops[a][0] == X), None)
    if a is None:
        return None
    t = a+1 if kind == 'fwd' else a-1
    if not 0 <= t < len(stops):
        return None
    new = B if kind == 'fwd' else A
    m_in = stops[t][1]
    m_out = stops[t+1][1] if t+1 < len(stops) else None
    w1 = dict(w); p1 = [list(e) for e in prog]
    if m_in == -1:
        if o in live:
            return None
        w1['initial'] = list(w['initial']); w1['initial'][o] = new
    else:
        p1[m_in][3] = new
    if m_out is None:
        if o-112 in live:
            return None
        w1['final'] = list(w['final']); w1['final'][o] = new
        end = len(prog)
    else:
        p1[m_out][2] = new
        end = m_out
    broken = []
    for q in range(m_in+1, end):
        e = p1[q]
        if e[0] in ('ADD', 'COPY') and o in (e[1], e[2]) or e[0] == 'SCALE' and e[1] == o:
            e[-1] = new
            if e[0] != 'SCALE':
                broken.append(q)
    w1['program'] = p1
    return w1, broken


def repair(w1, broken):
    """Re-place each broken event by a compensated shift (no special register)."""
    prog = w1['program']
    tl, _ = timelines(w1)
    skip = set(broken)
    options = []
    for p in broken:
        o = rung2.plan_event(prog, tl, p, None, None, None, -1, len(prog), skip)
        if not o and ENGINE is rung4:
            e = prog[p]
            ctx = rung4.Ctx(prog, tl, None, None, None, -1, len(prog), skip)
            o = rung4.plan_virtual(ctx, e[1], e[2], rung4.Q(e[3]), p, p, rung4.DEPTH)
        if not o:
            return None
        options.append(sorted(o, key=len)[:6])
    best = None
    for combo in product(*options):
        ins = [x for opt in combo for x in opt]
        if best is None or len(ins) < len(best):
            best = ins
        break
    keyed = [((q, 1, 0), e) for q, e in enumerate(prog) if q not in skip]
    for n, (q, e, H) in enumerate(best):
        keyed.append(((q, 0, 1, n), e))
    keyed.sort(key=lambda t: t[0])
    w2 = dict(w1); w2['program'] = [e for _, e in keyed]
    return w2, len(best)-len(broken)


def main():
    w = p104.read(sys.argv[1])
    cands = json.load(open(sys.argv[2]))
    k, K = map(int, ARG('--shard', '0/1').split('/'))
    cands = cands[k::K]
    out = open(sys.argv[3], 'a')
    base = p104.price(w)
    print('base', {a: str(b) for a, b in base.items()}, flush=True)
    wd = p104.Path(sys.argv[3]+'.words'); wd.mkdir(exist_ok=True)
    t0 = time.time()
    for c, cand in enumerate(cands):
        r, mi, A, X, B = cand['reg'], cand['stop'], cand['A'], cand['X'], cand['B']
        for pick in product(*cand['partners']):
            if any(op[3] > MAXOTHER for op in pick):
                row = {'reg': r, 'stop': mi, 'pick': pick, 'ok': False, 'why': 'partner stop too busy'}
            else:
                row = {'reg': r, 'stop': mi, 'pick': pick}
                rung4.DEADLINE[0] = time.time()+rung4.BUDGET
                cur, added, okk = w, 0, True
                for kind, o, Y, nev in pick:
                    s = substitute(cur, o, kind, X, A, B)
                    if s is None:
                        row.update(ok=False, why='substitute refused (%s %d)' % (kind, o)); okk = False; break
                    w1, broken = s
                    try:
                        rp = repair(w1, broken)
                    except rung4.Timeout:
                        row.update(ok=False, why='time budget (repair)'); okk = False; break
                    if rp is None:
                        row.update(ok=False, why='repair failed (%s %d, %d broken)' % (kind, o, len(broken))); okk = False; break
                    cur, add = rp; added += add
                if okk:
                    try:
                        p104.replay(cur)
                    except p104.Illegal as x:
                        row.update(ok=False, why='partner step replay: '+str(x)); okk = False
                if okk:
                    tl, moves = timelines(cur)
                    mi2 = next((m for m in range(len(moves[r])-1) if cur['program'][moves[r][m]][3] == X), None)
                    if mi2 is None:
                        row.update(ok=False, why='stop vanished')
                    else:
                        res = rung2.attempt(cur, tl, moves, r, mi2)
                        if not res['ok'] and ENGINE is rung4:
                            res = rung4.attempt(cur, tl, moves, r, mi2)
                        word = res.pop('word', None)
                        row.update({a: str(b) if a.startswith('kappa') else b for a, b in res.items()})
                        row['added_partner'] = added
                        if res['ok']:
                            row['gain'] = float(res['kappa_lo']-base['kappa_lo'])
                            row['events_delta'] = res['events']-base['events']
                            (wd/('r%d_s%d_%d.json' % (r, mi, hash(str(pick)) % 10**6))).write_text(json.dumps(word))
            out.write(json.dumps(row)+'\n'); out.flush()
            print(c, round(time.time()-t0), json.dumps(row)[:260], flush=True)


if __name__ == '__main__':
    main()
