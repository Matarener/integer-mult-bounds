"""late-birth feasibility on a realised word: helper h may start at frame g (its first op frame) iff its junk column J_h (adjoint to Y finals in the
load-free content program) lies in the span of adjoints a_z(t) of registers z co-present at g while h is still pure junk (loads z -= c h)."""
import os
import sys, collections, math, gzip, json
from fractions import Fraction as Q
TK=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path[:0]=[TK, TK+'/synth']
import dag as D
def solve(target, vecs):
    """exact: target in span(vecs)? returns coefficient list or None (sparse dict vectors)"""
    piv = {}   # pivot key -> (vec, combo)
    def red(v, cmb):
        v = dict(v); cmb = dict(cmb)
        for p, (pv, pc) in piv.items():
            if p in v:
                f = v[p]
                for k, x in pv.items():
                    t = v.get(k, 0) - f * x
                    if t: v[k] = t
                    else: v.pop(k, None)
                for k, x in pc.items():
                    t = cmb.get(k, 0) - f * x
                    if t: cmb[k] = t
                    else: cmb.pop(k, None)
        return v, cmb
    for t, v in enumerate(vecs):
        v, c = red(v, {t: Q(1)})
        if v:
            p = min(v); f = v[p]
            v = {k: x / f for k, x in v.items()}; c = {k: x / f for k, x in c.items()}
            for q, (qv, qc) in list(piv.items()):
                if p in qv:
                    g = qv[p]
                    for k, x in v.items():
                        s = qv.get(k, 0) - g * x
                        if s: qv[k] = s
                        else: qv.pop(k, None)
                    for k, x in c.items():
                        s = qc.get(k, 0) - g * x
                        if s: qc[k] = s
                        else: qc.pop(k, None)
            piv[p] = (v, c)
    r, c = red(target, {})
    if r: return None
    return {k: -x for k, x in c.items()}
def analyse(path):
    w = D.load(path); dg = D.decompile(w, forms=False); meta = dg['meta']; n = meta['npub']
    role = D.role_fn(w); dim = [len(b) for b in w['frames']]; ops = dg['ops']
    # pure-junk tracking (x-content empty and only own junk) via forms
    F, _ = D.apply_forms([], meta)
    isload = []
    Fm = [{r: Q(1)} for r in range(n)] + [{} for _ in range(meta['nowned'])]
    for i, o in enumerate(ops):
        op, r, s, q, f, _v = o
        L = op == 'ADD' and role(r) == 'Y' and dim[f] == 0 and set(Fm[s]) == {s}
        isload.append(L)
        D.apply_forms([o], meta, init_forms=None) if False else None
        if op in ('INIT', 'CLEAR'): Fm[r] = {}
        elif op == 'SCALE': Fm[r] = {c: v * Q(q) for c, v in Fm[r].items()}
        elif op == 'COPY': Fm[r] = {c: v * Q(q) for c, v in Fm[s].items()}
        else:
            d = Fm[r]
            for c, v in Fm[s].items():
                t = d.get(c, 0) + Q(q) * v
                if t: d[c] = t
                else: d.pop(c, None)
    body = [i for i in range(len(ops)) if not isload[i]]
    # per helper: first op index, frame; T_h first op where h is dst
    first = {}; T = {}
    for i in body:
        o = ops[i]
        for r in ((o[1], o[2]) if o[2] is not None else (o[1],)):
            if r < n and role(r) == 'helper' and r not in first: first[r] = i
        if o[1] < n and role(o[1]) == 'helper' and o[1] not in T: T[o[1]] = i
    cand = {h: ops[first[h]][4] for h in first if dim[ops[first[h]][4]] > 0}
    # co-present (z, i): ops at frame g before T_h involving z
    byframe = collections.defaultdict(list)
    for i in body:
        o = ops[i]
        for r in ((o[1], o[2]) if o[2] is not None else (o[1],)): byframe[o[4]].append((i, r))
    need = collections.defaultdict(list)
    for h, g in cand.items():
        lim = T.get(h, len(ops))
        need[h] = sorted({(i, z) for i, z in byframe[g] if i < lim and z != h})
    snap = set(p for v in need.values() for p in v)
    # reverse sweep (content program) for adjoints; snapshot a_z right after op i
    a = collections.defaultdict(dict)
    for r in range(n):
        if role(r) == 'Y': a[r] = {r: Q(1)}
    S = {}
    for i in reversed(body):
        o = ops[i]; op, r, s, q = o[0], o[1], o[2], o[3]
        for z in (r, s):
            if (i, z) in snap: S[(i, z)] = dict(a[z])
        if op == 'ADD':
            if a[r]:
                d = a[s]; qq = Q(q)
                for k, x in a[r].items():
                    t = d.get(k, 0) + qq * x
                    if t: d[k] = t
                    else: d.pop(k, None)
        elif op == 'COPY':
            d = a[s]; qq = Q(q)
            for k, x in a[r].items():
                t = d.get(k, 0) + qq * x
                if t: d[k] = t
                else: d.pop(k, None)
            a[r] = {}
        elif op == 'SCALE': a[r] = {k: x * Q(q) for k, x in a[r].items()}
        elif op in ('INIT', 'CLEAR'): a[r] = {}
    ok = {}; stats = collections.Counter()
    for h, g in cand.items():
        J = a[h]
        if not J: ok[h] = {}; stats['zero-junk'] += 1; continue
        vecs = [S[p] for p in need[h]]
        c = solve(J, vecs) if vecs else None
        if c is None: stats['infeasible'] += 1
        else: ok[h] = {need[h][k]: v for k, v in c.items()}; stats['feasible'] += 1
    return w, dg, cand, ok, stats, dim
if __name__ == '__main__':
    w, dg, cand, ok, stats, dim = analyse(sys.argv[1])
    print('helpers', sum(1 for r in range(len(w['initial'])) if D.role_fn(w)(r) == 'helper'), 'late candidates', len(cand), dict(stats))
    print('birth dims of feasible', collections.Counter(dim[cand[h]] for h in ok))
