"""Direct check of an explicit post-cut correction program, independent of the kernel and suffix algebra.  Apache-2.0.

Python 3.12, standard library only.  A *batch* (after_event t, chart X, comb c, target r', mu) adds mu (z - l) to
field r', where l = row_p(cut) is the retired value: it reads the chart-local combination c . state, whose value in
the split word is kappa (z - l), and adds (mu / kappa) times it.  `emit` lowers every batch into primitive
chart-local events (SCALE r' / COPY r' when r' is in the support of c, then ADDs), and returns the corrected word.
`check` re-simulates that corrected word with a plain event simulator and compares it with the original word.
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


def step(rows, cur, e):
    op, r = e[0], e[1]
    if op == 'MOVE':
        need(cur[r] == e[2], 'MOVE from the current chart'); cur[r] = e[3]
    elif op == 'INIT':
        rows[r] = {}; cur[r] = e[2]
    elif op == 'CLEAR':
        rows[r] = {}; cur[r] = None
    elif op == 'SCALE':
        need(Q(e[-2]) != 0, 'nonzero SCALE'); rows[r] = {k: v * Q(e[-2]) for k, v in rows[r].items()}
    elif op == 'COPY':
        need(cur[r] is not None and cur[r] == cur[e[2]], 'COPY is chart-local')
        rows[r] = {k: v * Q(e[-2]) for k, v in rows[e[2]].items() if v * Q(e[-2])}
    elif op == 'ADD':
        need(cur[r] is not None and cur[r] == cur[e[2]] and r != e[2], 'ADD is chart-local')
        add(rows[r], rows[e[2]], Q(e[-2]))
    else:
        need(False, 'unknown op')


def start(w):
    n = w['public']; m = w['owned_fields']
    return [{r: Q(1)} if r < n else {} for r in range(n + m)], list(w['initial']) + [None] * m


def emit(w, cut, p, batches):
    """Lower the batches into primitive events; returns (corrected program, inserted events)."""
    rows, cur = start(w)
    rows = None   # only the z-coefficients are needed to choose the coefficients
    zc = {}
    by_t = {}
    for b in batches:
        need(cut <= b['after_event'] < len(w['program']), 'batch after the cut')
        by_t.setdefault(b['after_event'], []).append(b)
    prog, ins = [], []
    for t, e in enumerate(w['program']):
        prog.append(e)
        op, r = e[0], e[1]
        if op == 'MOVE': cur[r] = e[3]
        elif op == 'INIT': cur[r] = e[2]
        elif op == 'CLEAR': cur[r] = None
        _act(zc, e)
        if t == cut:
            zc = {p: Q(1)}
        for b in by_t.get(t, ()):
            X, c, tgt = b['chart'], {int(k): Q(v) for k, v in b['comb'].items()}, b['target']
            need(all(cur[f] == X for f in c) and cur[tgt] == X, 'batch is chart-local')
            kappa = sum(x * zc.get(f, 0) for f, x in c.items())
            need(kappa != 0, 'combination carries z')
            q = Q(b['mu']) / kappa
            evs = []
            others = [(f, x) for f, x in sorted(c.items()) if f != tgt]
            s = 1 + q * c.get(tgt, 0)
            if s == 0:
                f0, x0 = others[0]; others = others[1:]
                evs.append(['COPY', tgt, f0, str(q * x0), X])
            elif s != 1:
                evs.append(['SCALE', tgt, str(s), X])
            evs += [['ADD', tgt, f, str(q * x), X] for f, x in others]
            for ev in evs:
                _act(zc, ev)
            prog += evs; ins += evs
    return prog, ins


def _act(v, e):
    op, r = e[0], e[1]
    if op in ('INIT', 'CLEAR'):
        v.pop(r, None)
    elif op == 'SCALE':
        if r in v: v[r] *= Q(e[-2])
    elif op == 'COPY':
        y = Q(e[-2]) * v.get(e[2], 0)
        if y: v[r] = y
        else: v.pop(r, None)
    elif op == 'ADD':
        y = v.get(r, 0) + Q(e[-2]) * v.get(e[2], 0)
        if y: v[r] = y
        else: v.pop(r, None)


def run(w, prog, cut_index=None, p=None):
    """Plain simulation; after program position cut_index, field p holds the fresh input 'z'."""
    rows, cur = start(w)
    for j, e in enumerate(prog):
        step(rows, cur, e)
        if j == cut_index:
            rows[p] = {'z': Q(1)}
    return rows, cur


def check(w, cut, p, batches):
    """Exact claims for the corrected split (V = final[p], O = public roles whose final chart is not V): the corrected
    word ends in the original final charts; every O output equals the ORIGINAL output exactly (no z, no non-z
    defect); z reaches a V-final output.  Returns the final z-column over public roles."""
    n = w['public']; V = w['final'][p]
    O = [r for r in range(n) if w['final'][r] != V]
    orig, cur0 = run(w, w['program'])
    prog, ins = emit(w, cut, p, batches)
    need(prog[:cut + 1] == w['program'][:cut + 1], 'prefix up to the cut unchanged')
    new, cur1 = run(w, prog, cut, p)
    need(cur1 == cur0, 'final charts unchanged')
    zcol = {r: new[r]['z'] for r in range(n) if new[r].get('z')}
    need(all(r not in zcol for r in O), 'no z-leak to a role whose final chart is not V')
    need(all(new[r] == orig[r] for r in O), 'every O output equals the original output')
    need(any(w['final'][r] == V for r in zcol), 'z still reaches a V-final output')
    return zcol, ins
