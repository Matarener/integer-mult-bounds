"""Core of the ladder search on P104 accumulated-block words: exact replay, invoice and kappa root.  Apache-2.0.

Independent re-implementation (imports nothing from the CrocSwap packages); prepared for Matarener with Claude (Anthropic), via Claude Code.
Rules follow the PR5827/PR5907 local checker as replayed by our audit (Internal branch claude/project-thread-xe83by, audit-5907/audit.py).
"""
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction as Q
import gzip, json
from pathlib import Path

CROC = Path('/home/user/croc')
CONTROLLER = CROC/'research/p104-productive-controller/CONTROLLER.json'


class Illegal(Exception):
    pass


def need(ok, why):
    if not ok:
        raise Illegal(why)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def spans(w):
    out = []
    for basis in w['frames']:
        s = {0}
        for v in basis:
            s |= {x ^ v for x in s}
        out.append(frozenset(s))
    return out


def replay(w, S=None, rows_check=True):
    """Exact replay.  Returns (paid Counter, helper Counter, info).  Raises Illegal with the first violation."""
    S = S or spans(w)
    n, m = w['public'], w['owned_fields']
    live = set(w['live'])
    cur = list(w['initial'])+[None]*m
    rows = [{r: Q(1)} for r in range(n+m)] if rows_check else None
    owned, paid, peak = set(), Counter(), 0
    dims = [len(f) for f in w['frames']]
    for i, e in enumerate(w['program']):
        op, r = e[0], e[1]
        need(0 <= r < n+m, 'role index at %d' % i)
        if op == 'MOVE':
            a, b, private = e[2], e[3], e[4]
            need(cur[r] == a and (r in owned) == private, 'transport source/ownership at %d' % i)
            need(S[b] < S[a] if private else S[a] < S[b], 'strict nesting at %d' % i)
            paid[abs(dims[b]-dims[a])] += 1
            cur[r] = b
        elif op == 'INIT':
            need(r >= n and r not in owned, 'owned init at %d' % i)
            owned.add(r); peak = max(peak, len(owned))
            cur[r] = e[2]
            if rows_check: rows[r] = {}
        elif op == 'CLEAR':
            need(r in owned and cur[r] == e[2], 'owned erasure at %d' % i)
            owned.discard(r); cur[r] = None
            if rows_check: rows[r] = {}
        else:
            q, f = Q(e[-2]), e[-1]
            need(q != 0 and cur[r] == f, 'destination chart at %d' % i)
            d = q.denominator
            need(d & (d-1) == 0, 'dyadic coefficient at %d' % i)
            if op == 'SCALE':
                if rows_check: rows[r] = {k: q*v for k, v in rows[r].items()}
            else:
                s = e[2]
                need(s != r and 0 <= s < n+m and cur[s] == f, 'common chart at %d' % i)
                if op == 'COPY':
                    need(r in owned, 'COPY into owned field at %d' % i)
                    if rows_check:
                        need(not rows[r], 'COPY into cleared owned field at %d' % i)
                        rows[r] = {k: q*v for k, v in rows[s].items()}
                else:
                    need(op == 'ADD', 'opcode at %d' % i)
                    if rows_check:
                        t = rows[r]
                        if r is not None:
                            t = dict(t)
                            for k, v in rows[s].items():
                                x = t.get(k, 0)+q*v
                                if x: t[k] = x
                                else: t.pop(k, None)
                            rows[r] = t
    need(not owned and cur[:n] == w['final'], 'public and owned exits')
    if rows_check:
        for r in range(n+m):
            expected = {r: Q(1)} if r < n else {}
            if r-112 in live:
                expected[r-112] = Q(1)
            need(rows[r] == expected, 'endpoint row %d' % r)
    main = live | {r+112 for r in live}
    helpers = Counter()
    for r in range(n):
        if r in main:
            continue
        a, b = w['initial'][r], w['final'][r]
        need(S[a] < S[b], 'helper %d nesting' % r)
        helpers[dims[b]-dims[a]] += 1
    return paid, helpers, {'events': len(w['program']), 'peak_owned': peak}


_C = None


def invoice(paid_local, helpers_local):
    """Complete invoice (paid P, targets T) = 18 forward local calls + the fixed caller part (closed formula of PR5827 PROOF.md)."""
    P = Counter({r: 18*v for r, v in paid_local.items()}); T = Counter({r: 18*v for r, v in helpers_local.items()})
    P[1] += 1560; T[145] += 208
    for L in (7, 8):
        for j in range(1, L+1):
            P[8*(j+1)] += 208; T[1+8*(j+1)] += 208
    return +P, +T


def margin(P, T, kap):
    t = 1-kap
    return sum(n*(t*Decimal(r).ln()).exp() for r, n in T.items())-sum(n*(t*Decimal(r).ln()).exp() for r, n in P.items())


def kappa(P, T, grid=10**14):
    """Raw crossing (lo, hi) on the 1e-14 grid, as in the authors' engine."""
    getcontext().prec = 50
    lo, hi = 0, 10**12
    while hi-lo > 1:
        mid = (lo+hi)//2
        if margin(P, T, Decimal(mid)/grid) > 0:
            lo = mid
        else:
            hi = mid
    return Q(lo, grid), Q(hi, grid)


def price(w, rows_check=True):
    paid, helpers, info = replay(w, rows_check=rows_check)
    P, T = invoice(paid, helpers)
    lo, hi = kappa(P, T)
    info.update(paid_calls=sum(P.values()), targets=sum(T.values()),
                surplus=sum(r*v for r, v in T.items())-sum(r*v for r, v in P.items()), kappa_lo=lo, kappa_hi=hi)
    return info
