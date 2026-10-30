"""Direct check of an explicit leak correction, independent of the suffix/telescoping algebra.  Apache-2.0.

Python 3.12, standard library only.  Simulates the split word forward with one extra input coordinate 'z':
after event `cut`, field p holds z (unit injection); each correction (after_event t, target r', source f, mu)
inserts ADD r' += q f at the chart shared by r' and f, with q = mu / (z-coefficient of f), after checking that
f carries z (and, with pure_sources=True, that f's value is a pure multiple of z).  Source eligibility otherwise
needs no check: check() validates the whole corrected map.  Returns the final z-column over the public roles and the non-z rows.
"""
from fractions import Fraction as Q


def add(dst, src, q):
    for k, v in src.items():
        x = dst.get(k, 0) + q * v
        if x:
            dst[k] = x
        else:
            dst.pop(k, None)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def simulate(w, cut, p, corrections=(), pure_sources=False):
    n = w['public']; m = w['owned_fields']; N = n + m
    rows = [{r: Q(1)} if r < n else {} for r in range(N)]
    cur = list(w['initial']) + [None] * m
    by_t = {}
    for c in corrections:
        need(cut is not None and cut <= c['after_event'] < len(w['program']), 'correction inside the program, after the cut')
        by_t.setdefault(c['after_event'], []).append(c)
    for t, e in enumerate(w['program']):
        op, r = e[0], e[1]
        if op == 'MOVE':
            need(cur[r] == e[2], 'MOVE from the current chart'); cur[r] = e[3]
        elif op == 'INIT':
            rows[r] = {}; cur[r] = e[2]
        elif op == 'CLEAR':
            rows[r] = {}; cur[r] = None
        elif op == 'SCALE':
            rows[r] = {k: v * Q(e[-2]) for k, v in rows[r].items()}
        elif op == 'COPY':
            need(cur[r] == cur[e[2]], 'COPY is chart-local'); rows[r] = {k: v * Q(e[-2]) for k, v in rows[e[2]].items()}
        else:
            need(cur[r] == cur[e[2]], 'ADD is chart-local'); add(rows[r], rows[e[2]], Q(e[-2]))
        if cut is not None and t == cut:
            rows[p] = {'z': Q(1)}
        for c in by_t.get(t, ()):
            f, r2 = c['source'], c['target']
            need(cur[f] is not None and cur[f] == cur[r2] == c['chart'], 'correction is chart-local')
            need(rows[f].get('z'), 'correction source carries z')
            need(not pure_sources or set(rows[f]) == {'z'}, 'correction source is a pure multiple of z')
            q = Q(c['mu']) / rows[f]['z']
            add(rows[r2], dict(rows[f]), q)
    zcol = {r: rows[r]['z'] for r in range(n) if rows[r].get('z')}
    nonz = [{k: v for k, v in rows[r].items() if k != 'z'} for r in range(n)]
    return zcol, nonz


def check(w, cut, p, corrections, full=True, pure_sources=False):
    """Exact claims for one corrected split, with V = final[p] and O = roles whose final chart is not V:
    z still reaches a V-final output; the z-column vanishes on O; and (full=True) every O output's non-z row equals
    the ORIGINAL word's row, i.e. the split leaves no defect outside V.  full=False checks only the z-part (the
    PR6040 necessary condition).  Returns a summary; raises ValueError on failure."""
    V = w['final'][p]; n = w['public']
    O = [r for r in range(n) if w['final'][r] != V]
    _, orig = simulate(w, None, p)
    z0, nz0 = simulate(w, cut, p)
    z1, nz1 = simulate(w, cut, p, corrections, pure_sources)
    need(bool({r for r in z1 if w['final'][r] == V}), 'z still reaches a V-final output')
    need(all(r not in z1 for r in O), 'no z-leak to a role whose final chart is not V')
    defect = [r for r in O if nz1[r] != orig[r]]
    if full:
        need(not defect, 'no non-z defect on O outputs')
    return {'z_leak_before': sorted(r for r in z0 if r in set(O)), 'O_nonz_defect_after': defect}
