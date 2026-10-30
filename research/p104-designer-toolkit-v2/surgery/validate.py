"""tk surgery / validate: SPAN5 x-part span law + JR junk-aware chart rank law on the CHANGED frames of a spliced word.
usage: validate.py BASEWORD NEWWORD [--column COL.json.gz] [--frames i,j,..] [--all] [--lo 8] [--no-jr] [--no-law]
Changed frames = frames visited by the column's registers in the base word UNION in the new word (needs --column; or --frames / --all).
  LAW (SPAN5 val0.py / s5lib): at every frame of dim 1..lo (default 8; 0 violations on 6030 at lo=4 and lo=8), span(x of arrivals) == span(x of departures)  [EXACT necessary; census = SUBOPT cen.run]
  JR  (FRAMELP / CHARTLP fullrep.py, re-implemented chart-restricted): per chart m of dim 1..8, rho <= Cc + min(|PJ|, NCe) + Yend + Xb + dirty, full-coordinate exact replay.
Reports violations in base vs new (a violation present in BOTH is the base word's own slack, e.g. JR is tight at 985/999 charts, not a splice regression)."""
import sys, os, json, gzip, argparse, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import swlib as S
from fractions import Fraction as Q
C = S.C

def visited(w, regs):
    """frame indices visited (initial + MOVE targets) by registers regs"""
    regs = set(regs); fr = {w['initial'][r] for r in regs if r < len(w['initial'])}
    for e in w['program']:
        if e[0] == 'MOVE' and e[1] in regs: fr.add(e[3]); fr.add(e[2])
    return fr
def changed_frames(w, nw, col, info):
    base = visited(w, col['orig_members']); new_ids = {info['name2new'][nm] for nm in col['regs']}
    return base, visited(nw, new_ids)

# ---------------------------------------------------------------- LAW
def law(w, frames=None, lo=4):
    """-> (frames checked, violations [(dim, #visits, ranks)]).  frames = set of global frame indices (None = all)"""
    s5 = S._s5(); R = S.census(w); B = s5.bottom(R, lo)
    want = None if frames is None else {s5.spanset(w['frames'][i]) for i in frames}
    byf = collections.defaultdict(list)
    for r, I in B.items():
        for (d, f, a, dp) in I['stops']:
            if d >= 1: byf[f].append((r, a, dp))
    n = 0; bad = []
    for f, L in byf.items():
        if want is not None and f not in want: continue
        ok, rk = s5.span_eq([a for _, a, _ in L], [dp for _, _, dp in L]); n += 1
        if not ok: bad.append((s5.dimof(f), len(L), rk))
    return n, bad

# ---------------------------------------------------------------- JR
def _addv(a, b, q):
    for k, v in b.items():
        x = a.get(k, 0) + q * v
        if x: a[k] = x
        else: a.pop(k, None)
class _Basis:
    def __init__(s): s.rows = {}
    def add(s, v):
        v = dict(v)
        while True:
            ks = [k for k in v if k in s.rows]
            if not ks: break
            k = ks[0]; _addv(v, s.rows[k], -v[k])
        if not v: return False
        p = min(v, key=repr); c = v[p]; s.rows[p] = {k: x / c for k, x in v.items()}; return True
def _rank(vs):
    B = _Basis(); return sum(1 for v in vs if v and B.add(v))

def jr(w, charts=None):
    """JR per chart (fullrep.py semantics, full coordinates: public r -> coordinate r, owned reads formal ('O', reg, version)).  charts = set of frame idx or None.
    -> (checked, violating chart list [(m, dim, rho, bound)])"""
    n = len(w['initial']); live = set(w['live']); ycol = {r + 112 for r in live}
    role = lambda r: 'O' if r >= n else ('X' if r in live else ('Y' if r in ycol else 'H'))
    dimf = [len(b) for b in w['frames']]; val = {r: {r: Q(1)} for r in range(n)}
    stops = {r: [dict(f=w['initial'][r], arr=dict(val[r]), rd=False)] for r in range(n)}
    over = collections.Counter()
    for e in w['program']:
        op = e[0]
        if op == 'MOVE':
            if e[1] < n: stops[e[1]].append(dict(f=e[3], arr=dict(val[e[1]]), rd=False))
            continue
        if op in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR') and e[1] >= n: over[e[1]] += 1; continue
        if op == 'SCALE': q = Q(e[2]); val[e[1]] = {k: v * q for k, v in val[e[1]].items()}; continue
        if op in ('INIT', 'CLEAR'): val[e[1]] = {}; continue
        d, s, q = e[1], e[2], Q(e[3])
        if s >= n: src = {('O', s, over[s]): Q(1)}
        else: src = val[s]
        if op == 'COPY': val[d] = {}
        _addv(val[d], src, q)
    final = val
    def clean(r):
        f = final[r]; ro = role(r)
        if any(isinstance(k, tuple) for k in f): return False
        if ro in ('H', 'X'): return f == {r: 1}
        if ro == 'Y': return f.get(r) == 1 and all(role(k) == 'X' or k == r for k in f)
        return False
    visits = collections.defaultdict(list)
    for r in range(n):
        S_ = stops[r]
        for k, st in enumerate(S_): visits[st['f']].append(dict(r=r, k=k, last=(k == len(S_) - 1), v=st['arr'], role=role(r)))
    bad = []; cnt = 0
    for m, V in visits.items():
        dm = dimf[m]
        if not (1 <= dm <= 8) or (charts is not None and m not in charts): continue
        cnt += 1
        xpart = lambda v: {k: x for k, x in v.items() if k in live}
        rho = _rank([xpart(u['v']) for u in V if (u['k'] > 0 or u['role'] == 'X')])
        Nset = {u['r'] for u in V if u['last'] and u['k'] > 0 and u['role'] == 'H' and clean(u['r'])}
        cont = [u for u in V if u['k'] > 0 and not u['last']]
        Cc = sum(1 for u in cont if xpart(u['v'])); PJ = [u for u in cont if not xpart(u['v'])]
        NCe = sum(1 for u in V if u['k'] > 0 and u['last'] and u['r'] in Nset and xpart(u['v']))
        Yend = sum(1 for u in V if u['last'] and u['role'] == 'Y'); Xb = sum(1 for u in V if u['k'] == 0 and u['role'] == 'X')
        dirty = sum(1 for u in V if u['last'] and u['role'] == 'H' and not clean(u['r']))
        bound = Cc + min(len(PJ), NCe) + Yend + Xb + dirty
        if rho > bound: bad.append((m, dm, rho, bound))
    return cnt, bad

def run(w, nw, col=None, info=None, frames=None, all_frames=False, lo=8, do_law=True, do_jr=True):
    if all_frames or (col is None and frames is None): chg_b = chg_n = None; ch = None
    elif frames is not None: chg_b = chg_n = None; ch = set(frames)
    else:
        b, nn = changed_frames(w, nw, col, info); ch = b | nn
    out = dict(n_changed=None if ch is None else len(ch), lo=lo)
    if do_law:
        out['law_n_base'], lb = law(w, ch, lo); out['law_n_new'], ln = law(nw, ch, lo); out['law_bad_base'] = len(lb); out['law_bad'] = len(ln); out['law_examples'] = ln[:5]
    else: out['law_bad'] = 0
    if do_jr:
        # frame indices of the new word include appended frames; the base only knows the old ones: a chart set is global frame idx for both
        out['jr_n_base'], jb = jr(w, ch); out['jr_n_new'], jn = jr(nw, ch); out['jr_bad_base'] = len(jb); out['jr_bad_new'] = len(jn); out['jr_examples'] = jn[:5]
    else: out['jr_bad_base'] = out['jr_bad_new'] = 0
    return out
def fmt(r):
    L = ['validate: %s frames (global idx) in scope' % ('ALL' if r['n_changed'] is None else r['n_changed'])]
    if 'law_n_new' in r: L.append('  SPAN5 law dims 1..%d: base %d frames / %d violations; new %d frames / %d violations %s' % (r['lo'], r['law_n_base'], r['law_bad_base'], r['law_n_new'], r['law_bad'], r['law_examples']))
    if 'jr_n_new' in r: L.append('  JR charts dim 1..8: base %d charts / %d violations; new %d charts / %d violations %s' % (r['jr_n_base'], r['jr_bad_base'], r['jr_n_new'], r['jr_bad_new'], r['jr_examples']))
    return '\n'.join(L)

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0]); ap.add_argument('base'); ap.add_argument('new'); ap.add_argument('--column'); ap.add_argument('--frames')
    ap.add_argument('--all', action='store_true'); ap.add_argument('--lo', type=int, default=8); ap.add_argument('--no-jr', action='store_true'); ap.add_argument('--no-law', action='store_true')
    a = ap.parse_args(argv); _, w = S.load_word(a.base); _, nw = S.load_word(a.new)
    col = info = None
    if a.column:
        import splice; col = splice.load_column(a.column); nw2, info = splice.splice(w, col, allow_drift=True)
    r = run(w, nw, col, info, frames=[int(x) for x in a.frames.split(',')] if a.frames else None, all_frames=a.all, lo=a.lo, do_law=not a.no_law, do_jr=not a.no_jr)
    print(fmt(r)); return 0 if (r['law_bad'] == 0 and r['jr_bad_new'] <= r['jr_bad_base']) else 3
if __name__ == '__main__': sys.exit(main())
