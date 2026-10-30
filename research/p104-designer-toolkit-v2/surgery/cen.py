"""SUBOPT census: exact local-content replay of a word, per-stop contents, cancellation by dim.
usage: cen.py WORD out.pkl   (read-only on the word)"""
import sys, math, collections, pickle
import os
TK = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, TK)
from tkcommon import load
from fractions import Fraction as Q

def main(spec, out):
    _, w = load(spec); return run(w, out)

def run(w, out):
    F = w['frames']; live = w['live']; n = len(w['initial']); LV = set(live)
    ports = w['ports']; col = {r: c for c, r in enumerate(live)}; ycol = {r + 112: c for c, r in enumerate(live)}
    dimf = [len(b) for b in F]
    def span(b):
        S = {0}
        for v in b: S |= {x ^ v for x in S}
        return S
    SP = [span(b) for b in F]
    pidx = {p: c for c, p in enumerate(ports)}
    PF = [frozenset(pidx[x] for x in S if x in pidx) for S in SP]
    par = lambda a, b: bin(a & b).count('1') & 1
    JF = [frozenset(c for c, p in enumerate(ports) if all(not par(p, v) for v in b)) for b in F]
    def role(r):
        if r >= n: return 'O'
        if r in LV: return 'X'
        if r in ycol: return 'Y'
        return 'H'
    prog = w['program']
    loc = collections.defaultdict(dict)
    for r in live: loc[r] = {col[r]: Q(1)}
    cur = {r: w['initial'][r] for r in range(n)}
    # stops[r] = list of dict(frame, t0, arrive=content at arrival, events=[...])
    stops = {r: [dict(f=w['initial'][r], t0=-1, arr={}, ev=[])] for r in range(n)}
    for r in live: stops[r][0]['arr'] = {col[r]: Q(1)}
    # late-junk: helpers born at a frame of dim > 0 carry their initial value e_h (cannot be cancelled by dim-0 pre-loads)
    jnk = collections.defaultdict(dict)
    for r in range(n):
        if role(r) == 'H' and dimf[w['initial'][r]] > 0: jnk[r] = {r: Q(1)}
    for r in range(n): stops[r][0]['arrj'] = dict(jnk[r])
    over = collections.Counter()          # version counter of owned registers
    taint = collections.defaultdict(bool)   # content carries an owned-derived part (read an owned register, directly or through a tainted source)
    for r in range(n): stops[r][0]['arrt'] = False
    evrec = []   # per ADD/COPY: (t, op, d, s, q, frame, dim, roled, roles, supS, supD_before, supD_after, shrink)
    ownread = collections.Counter()
    for t, e in enumerate(prog):
        op = e[0]
        if op == 'MOVE':
            r = e[1]; cur[r] = e[3]
            if r < n: stops[r].append(dict(f=e[3], t0=t, arr=dict(loc[r]), arrj=dict(jnk[r]), arrt=taint[r], ev=[]))
            continue
        if op == 'TAINT': taint[e[1]] = True; continue
        if op == 'OSYM':
            r_, key, q_ = e[1], e[2], Q(e[3]); bj0 = dict(jnk[r_]); x = bj0.get(key, 0) + q_
            if x: bj0[key] = x
            else: bj0.pop(key, None)
            jnk[r_] = bj0; taint[r_] = True; continue
        if op in ('ADD', 'COPY', 'SCALE', 'INIT', 'CLEAR') and e[1] >= n: over[e[1]] += 1
        if op == 'INIT': loc[e[1]] = {}; jnk[e[1]] = {}; cur[e[1]] = e[2]; continue
        if op == 'CLEAR': loc[e[1]] = {}; jnk[e[1]] = {}; continue
        if op == 'SCALE':
            q = Q(e[2]); loc[e[1]] = {c: v * q for c, v in loc[e[1]].items()}; jnk[e[1]] = {c: v * q for c, v in jnk[e[1]].items()}
            if e[1] < n: stops[e[1]][-1]['ev'].append(('S', t, q))
            continue
        d, s, q, fi = e[1], e[2], Q(e[3]), e[4]
        before = dict(loc[d]) if op == 'ADD' else {}
        if role(s) == 'O':
            ownread[(role(d), dimf[fi])] += 1
            src = {}; taint[d] = True
            if role(d) != 'O':      # formal owned symbol (owned register, version) enters d's balance coordinates
                key = ('O', s, over[s]); bj0 = dict(jnk[d]) if op == 'ADD' else {}
                x = bj0.get(key, 0) + q
                if x: bj0[key] = x
                else: bj0.pop(key, None)
                jnk[d] = bj0
        else:
            src = loc[s]
            if taint[s] and role(d) != 'O': taint[d] = True
        nd = dict(before)
        for c, v in src.items():
            x = nd.get(c, 0) + q * v
            if x: nd[c] = x
            else: nd.pop(c, None)
        loc[d] = nd
        bj = dict(jnk[d]) if (op == 'ADD' or role(s) == 'O') else {}
        if role(s) != 'O':
            for c, v in jnk[s].items():
                x = bj.get(c, 0) + q * v
                if x: bj[c] = x
                else: bj.pop(c, None)
        jnk[d] = bj
        removed = set(before) - set(nd); added = set(nd) - set(before)
        rec = (t, op, d, s, q, fi, dimf[fi], role(d), role(s), len(src), len(before), len(nd), len(removed), len(added))
        evrec.append(rec)
        if d < n: stops[d][-1]['ev'].append(('in', t, s, q, len(src)))
        if s < n: stops[s][-1]['ev'].append(('out', t, d, q, len(src)))
    final = {r: dict(loc[r]) for r in range(n)}
    finalj = {r: dict(jnk[r]) for r in range(n)}
    finalt = {r: taint[r] for r in range(n)}
    res = dict(stops=stops, evrec=evrec, final=final, finalj=finalj, finalt=finalt, dimf=dimf, PF=PF, JF=JF, F=F, ports=ports,
               roles={r: role(r) for r in range(n)}, n=n, col=col, ycol=ycol, ownread=ownread)
    pickle.dump(res, open(out, 'wb'))
    # report: cancellation by dim
    by = collections.defaultdict(collections.Counter)
    for rec in evrec:
        t, op, d, s, q, fi, dm, rd, rs, ss, sb, sa, rem, add = rec
        if ss == 0: continue
        k = by[dm]; k['contentful'] += 1; k[rd + '<-' + rs] += 1
        if rem: k['shrink'] += 1; k['shrink_' + rd + '<-' + rs] += 1
    for dm in sorted(by): print(dm, dict(by[dm]))
    print('owned reads', dict(ownread))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
