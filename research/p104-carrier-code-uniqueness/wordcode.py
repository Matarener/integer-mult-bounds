"""The owned-delivery code of an actual P104 local word (accumulated-block schema 2).  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.

decompose() replays the word with exact rationals and splits every public row into a lives-in-frame part and an
owned-delivered part (Lemma 1 of PROOF.md): the lives-in-frame part only grows by ADDs between public roles, which share
a frame, so its live coordinates always sit on ports of the role's current frame; everything a public role receives
from an owned field goes to the owned-delivered part.  The function checks that invariant after every event, checks
the partner endpoints (the live projection of partner l + 112 is e_l), and returns the owned-delivered parts w_l of the
104 partners together with every distinct owned-to-public delivered vector (live coordinates).
"""
from fractions import Fraction as Q
import gzip
import json


def load(path):
    return json.loads(gzip.decompress(open(path, 'rb').read()))


def spans(w):
    out = []
    for basis in w['frames']:
        s = {0}
        for v in basis:
            s |= {x ^ v for x in s}
        out.append(frozenset(s))
    return out


def dyadic(w):
    """True when every scalar of the program lies in Z[1/2] (so every row is 3-integral)"""
    for e in w['program']:
        if e[0] in ('ADD', 'COPY', 'SCALE'):
            q = Q(e[-2]); d = q.denominator
            if q == 0 or d & (d - 1):
                return False
    return True


def m3(q):
    return (q.numerator * pow(q.denominator, -1, 3)) % 3


def decompose(w):
    S = spans(w); n, m = w['public'], w['owned_fields']
    live = sorted(w['live'])
    port = {l: [x for x in S[w['initial'][l]] if x][0] for l in live}
    cur = list(w['initial']) + [None] * m
    lp = [dict() for _ in range(n)]          # lives-in-frame part of every public role (keys: live roles)
    od = [dict() for _ in range(n)]          # owned-delivered part of every public role
    orow = [dict() for _ in range(m)]        # owned rows (live coordinates)
    for l in live:
        lp[l] = {l: Q(1)}
    deliveries = {}

    def addto(t, src, q):
        for k, v in src.items():
            x = t.get(k, 0) + q * v
            if x:
                t[k] = x
            else:
                t.pop(k, None)

    for i, e in enumerate(w['program']):
        op, r = e[0], e[1]
        if op == 'MOVE':
            cur[r] = e[3]; continue
        if op in ('INIT', 'CLEAR'):
            if r < n:
                raise ValueError('INIT/CLEAR on a public role at event %d' % i)
            orow[r - n] = {}; cur[r] = e[2] if op == 'INIT' else None; continue
        q = Q(e[-2])
        if op == 'SCALE':
            if r < n:
                lp[r] = {k: q * v for k, v in lp[r].items()}; od[r] = {k: q * v for k, v in od[r].items()}
            else:
                orow[r - n] = {k: q * v for k, v in orow[r - n].items()}
            continue
        s = e[2]
        if r < n:
            if op == 'COPY':
                raise ValueError('COPY into a public role at event %d' % i)
            if s < n:
                addto(lp[r], lp[s], q); addto(od[r], od[s], q)
            else:
                addto(od[r], orow[s - n], q)
                vec = tuple(orow[s - n].get(l, Q(0)) for l in live)
                if any(vec):
                    key = tuple(m3(x) for x in vec)
                    deliveries.setdefault(key, sum(1 for x in vec if x))
            F = S[cur[r]]
            if not all(port[k] in F for k in lp[r]):
                raise ValueError('frame invariant broken at event %d' % i)
        else:
            t = {} if op == 'COPY' else orow[r - n]
            if s < n:
                addto(t, lp[s], q); addto(t, od[s], q)
            else:
                addto(t, orow[s - n], q)
            orow[r - n] = t
    W = []
    for l in live:
        p = l + 112
        F = S[cur[p]]
        if not (all(port[k] in F for k in lp[p]) and l not in lp[p]):
            raise ValueError('partner %d: lives-in-frame part leaves its frame or contains its own live' % p)
        full = dict(lp[p]); addto(full, od[p], Q(1))
        if full != {l: Q(1)}:
            raise ValueError('partner %d: live projection is not e_l' % p)
        W.append([od[p].get(k, Q(0)) for k in live])
    return [port[l] for l in live], W, deliveries
