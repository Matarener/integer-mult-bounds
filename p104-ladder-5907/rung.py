"""Rung-removal search on a P104 word: delete one intermediate stop X of a register (MOVE A->X, MOVE X->B  ==>  MOVE A->B)
by relocating every event that touches the register at X to a slot where both operands sit in A (before the merged MOVE)
or in B (after it), crossing only commuting events.  No event is added: each success saves one MOVE event.
Every candidate (success or failure, with its reason) is appended to the JSONL log as soon as it is decided.

usage: python3 rung.py WORD.json.gz LOG.jsonl [--limit N] [--regs a,b,c]
Prepared for Matarener with Claude (Anthropic), via Claude Code.  Apache-2.0.
"""
from bisect import bisect_right
from collections import defaultdict
from itertools import product
import json, sys, time
import p104


def writes(e):
    return e[1] if e[0] != 'MOVE' else None


def reads(e):
    return e[2] if e[0] in ('ADD', 'COPY') else None


def timelines(w):
    """charts[reg] = (times, frames): frame of reg in the slot before original event q is frames[bisect_right(times, q-1)-1]."""
    n, m = w['public'], w['owned_fields']
    tl = {r: ([-1], [w['initial'][r]]) for r in range(n)}
    for r in range(n, n+m):
        tl[r] = ([-1], [None])
    moves = defaultdict(list)
    for i, e in enumerate(w['program']):
        if e[0] == 'MOVE':
            tl[e[1]][0].append(i); tl[e[1]][1].append(e[3]); moves[e[1]].append(i)
        elif e[0] == 'INIT':
            tl[e[1]][0].append(i); tl[e[1]][1].append(e[2])
        elif e[0] == 'CLEAR':
            tl[e[1]][0].append(i); tl[e[1]][1].append(None)
    return tl, moves


def chart(tl, reg, q):
    times, frames = tl[reg]
    return frames[bisect_right(times, q-1)-1]


def touches(e, r):
    return e[1] == r or (e[0] in ('ADD', 'COPY') and e[2] == r)


def slots(prog, tl, p, r, A, B, lo, hi, skip):
    """Nearest backward slot (r and partner in A) and forward slot (in B) for event p; lo/hi bound r's stay."""
    e = prog[p]
    d, s = e[1], reads(e)
    partner = s if d == r else d if s == r else None
    if e[0] == 'SCALE':
        partner = None
    def conflict(g):
        wg, rg = writes(g), reads(g)
        return wg is not None and (wg == d or wg == s) or rg is not None and rg == d
    back = None
    q = p
    while q > lo:            # slot q means: just before original event q (crossing events q..p-1)
        if q < p:
            if q not in skip and conflict(prog[q]):
                break
        if partner is None or chart(tl, partner, q) == A:
            back = q
            break
        q -= 1
    fwd = None
    q = p+1
    while q <= hi:
        if q-1 > p and (q-1) not in skip and conflict(prog[q-1]):
            break
        if partner is None or chart(tl, partner, q) == B:
            fwd = q
            break
        q += 1
    return back, fwd


def attempt(w, tl, moves, r, mi):
    prog = w['program']
    i, j = moves[r][mi], moves[r][mi+1]
    A, X, B, priv = prog[i][2], prog[i][3], prog[j][3], prog[i][4]
    lo = moves[r][mi-1] if mi > 0 else -1          # r reaches A after event lo
    nxt = moves[r][mi+2] if mi+2 < len(moves[r]) else len(prog)
    U = [p for p in range(i+1, j) if touches(prog[p], r)]
    skip = set(U) | {i, j}
    opts = {}
    for p in U:
        b, f = slots(prog, tl, p, r, A, B, lo+1, nxt, skip)
        opts[p] = (b, f)
        if b is None and f is None:
            return {'ok': False, 'why': 'no slot', 'event': p, 'U': len(U)}
    choices = [[c for c in ('b', 'f') if opts[p][0 if c == 'b' else 1] is not None] for p in U]
    if len(U) > 14:
        return {'ok': False, 'why': 'too many events', 'U': len(U)}
    tried = 0
    for pick in product(*choices):
        bs = [opts[p][0] for p, c in zip(U, pick) if c == 'b']
        fs = [opts[p][1] for p, c in zip(U, pick) if c == 'f']
        k_lo = max(bs + [i+1]); k_hi = min(fs + [j])
        if k_lo > k_hi:
            continue
        k = k_lo
        tried += 1
        keyed = []
        for q, e in enumerate(prog):
            if q in skip:
                continue
            keyed.append(((q, 1, 0), e))
        keyed.append(((k, 0, 1), ['MOVE', r, A, B, priv]))
        for p, c in zip(U, pick):
            e = list(prog[p])
            if c == 'b':
                q = opts[p][0]; e[-1] = A if e[0] != 'COPY' or True else e[-1]
                keyed.append(((q, 0, 0, p), e))
            else:
                q = opts[p][1]; e[-1] = B
                keyed.append(((q, 0, 2, p), e))
        keyed.sort(key=lambda t: t[0])
        new = dict(w); new['program'] = [e for _, e in keyed]
        try:
            info = p104.price(new)
        except p104.Illegal as x:
            last = str(x)
            continue
        return {'ok': True, 'U': len(U), 'pick': ''.join(pick), 'k': k, 'A': A, 'X': X, 'B': B, 'word': new, **info}
    return {'ok': False, 'why': 'replay rejects all %d splits' % tried if tried else 'no consistent split', 'U': len(U),
            **({'last': last} if tried else {})}


def main():
    w = p104.read(sys.argv[1])
    out = open(sys.argv[2], 'a')
    base = p104.price(w)
    print('base', base, flush=True)
    tl, moves = timelines(w)
    regs = [int(x) for x in sys.argv[sys.argv.index('--regs')+1].split(',')] if '--regs' in sys.argv else sorted(moves)
    limit = int(sys.argv[sys.argv.index('--limit')+1]) if '--limit' in sys.argv else 10**9
    done = 0
    t0 = time.time()
    for r in regs:
        for mi in range(len(moves[r])-1):
            if done >= limit:
                return
            res = attempt(w, tl, moves, r, mi)
            done += 1
            word = res.pop('word', None)
            row = {'reg': r, 'stop': mi, 'i': moves[r][mi], 'j': moves[r][mi+1], **{k: str(v) if k.startswith('kappa') else v for k, v in res.items()}}
            if res['ok']:
                row['gain'] = float(res['kappa_lo']-base['kappa_lo'])
                p104.Path(sys.argv[2]+'.words').mkdir(exist_ok=True)
                (p104.Path(sys.argv[2]+'.words')/('r%d_s%d.json' % (r, mi))).write_text(json.dumps(word['program']))
            out.write(json.dumps(row)+'\n'); out.flush()
            print(done, round(time.time()-t0), json.dumps(row)[:300], flush=True)


if __name__ == '__main__':
    main()
