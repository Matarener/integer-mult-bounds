"""SKELORIGIN sb.py: D3-style rebuild of the SKELETON side (source park stops) of #6030 from the skeleton rules, then YROUTE's yb.py on top.
STRIP (low reader octet o, optionally one primary p): every non-primary read ADD Y += c s of the octet's sites, every SOURCE stop left with no event
  (MOVE s A->f + MOVE s f->B become MOVE s A->B), every Y stop left with no event.
REBUILD source stops (rules only; the swarm's source frames, levels and times are not read back; the (s, Y) incidence is GIVEN = YROUTE's unique solve):
  K0 exit gap : s is read by Y in the gap after A = the last frame of s inside Q_Y (B = next frame of s).
  K1 share    : if Y can nest A itself (Py < A < Ny, idle windows overlap), no new source stop (a park stop is paid only when needed).
  K2 closure  : else a new stop f with L <= f <= U, L = join(x-ports of s, A, Py), U = meet(B, Ny, Q_Y); joint over a connected group
                (sources read by one Y in one gap / Ys reading one source in one gap) when the joint bracket is non-empty.
  K3 level    : the level d minimises tax(s chain + d) + tax(Y chain + d) over [max(dim L, dim A+1, dim Py+1), min(dim U, dim B-1, dim Ny-1)]
                (concave per chain => an endpoint); f = L at d = dim L, f = U at d = dim U.
  K4 tie      : equal tax: the lower level if it balances the Y gap (d - dim Py == dim Ny - d), else the upper.
  time        : both source MOVEs at the start of the common idle window of s and the Y(s).
Then yb.main(--sites, --time settled, --yset all) rebuilds the Y side (reads, Y stops, coefficients). Compared with #6030 (chains of every register).
usage: sb.py WORD OUT.json.gz --octet O [--pair P] [--tie lo|hi|bal] [--force s:frame ...] (force = negative control)"""
import sys, gzip, json, pickle, argparse, collections, io, contextlib
from fractions import Fraction as Q
import os
HERE = os.path.dirname(os.path.abspath(__file__))   # alignbuild/: self-contained copy (no lane-dir imports)
sys.path[:0] = [HERE]
W = os.path.dirname(HERE)   # repo root (only used for default paths)
import rp
from life import rref, perp, dot, tax
S = rp.S
Yd = HERE + '/data/'

def meet(A, B): return perp(rref(list(perp(A)) + list(perp(B))))
def le(A, B): return rref(list(A) + list(B)) == rref(list(B))

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('word'); ap.add_argument('out'); ap.add_argument('--octet', type=int, required=True)
    ap.add_argument('--pair', type=int); ap.add_argument('--tie', default='bal', choices=['lo', 'hi', 'bal']); ap.add_argument('--force', action='append', default=[]); ap.add_argument('--force-span', action='append', default=[])
    ap.add_argument('--no-yb', action='store_true'); ap.add_argument('--stime', default='span', choices=['span', 'instant']); ap.add_argument('--allow-final', action='store_true'); ap.add_argument('--no-group', action='store_true')
    a = ap.parse_args(argv)
    path, w = S.load_word(a.word); w = json.loads(json.dumps(w)); n = len(w['initial'])
    fr = w['frames']; dim = [len(b) for b in fr]; prog0 = w['program']
    spn = {}
    def sp(f):
        if f not in spn: spn[f] = rref(fr[f])
        return spn[f]
    fidx = {}
    for i, b in enumerate(fr): fidx.setdefault(rref(b), i)
    Y1 = pickle.load(open(Yd + 'y1.pkl', 'rb')); Y4 = pickle.load(open(Yd + 'y4.pkl', 'rb')); ro = Y1['ro']
    ch0 = {r: [w['initial'][r]] for r in range(n)}
    for e in prog0:
        if e[0] == 'MOVE' and e[1] < n: ch0[e[1]].append(e[3])
    q = {y: perp(rref(fr[ch0[y][-1]]))[0] for y in ro}
    live = w['live']; port = {c: fr[w['initial'][r]][0] for c, r in enumerate(live)}
    sites = set()
    for r in Y4:
        if a.pair is not None and r['p'] != a.pair: continue
        for (y, f, yd, tr) in r['det']:
            if ro[y] == a.octet: sites.add((r['s'], y, f))
    srcs = sorted({s for s, _, _ in sites}); ys = sorted({y for _, y, _ in sites})
    print('sites', len(sites), sorted(sites))
    # ---------------- strip
    prog1 = [e for e in prog0 if not (e[0] == 'ADD' and (e[2], e[1], e[4]) in sites)]
    nk = len(prog0) - len(prog1)
    sframes = collections.defaultdict(set)
    for (s, y, f) in sites: sframes[s].add(f); sframes[y].add(f)
    stripped = []
    for r in sorted(set(srcs) | set(ys)):
        while True:
            tl = rp.timelines(w, prog1)[r]
            ev = collections.Counter()
            for k, (t0, t1, f) in enumerate(tl):
                ev[k] = sum(1 for t in range(t0 + 1, t1) if prog1[t][0] != 'MOVE' and r in S.regfields(prog1[t]))
            hit = [k for k, (t0, t1, f) in enumerate(tl) if 0 < k < len(tl) - 1 and ev[k] == 0 and f in sframes[r]]
            if not hit: break
            k = hit[0]; tin = tl[k][0]; tout = tl[k + 1][0]
            prog1[tout] = ['MOVE', r, tl[k - 1][2], prog1[tout][3], prog1[tout][4]]
            del prog1[tin]; stripped.append((r, tl[k][2], dim[tl[k][2]], 'S' if r in srcs else 'Y'))
    sstr = [x for x in stripped if x[3] == 'S']; ystr = [x for x in stripped if x[3] == 'Y']
    print('stripped %d reads, %d source stops %s, %d Y stops' % (nk, len(sstr), [(r, d) for r, f, d, _ in sstr], len(ystr)))
    # ---------------- x-content of sources at the end of every visit (public x-part, exact)
    tl1 = rp.timelines(w, prog1)
    colof = {r: c for c, r in enumerate(live)}
    loc = {r: ({colof[r]: Q(1)} if r in colof else {}) for r in range(n)}
    endmark = collections.defaultdict(list)
    for s in srcs:
        for k, (t0, t1, f) in enumerate(tl1[s]): endmark[t1].append((s, k))
    xend = {}
    for t, e in enumerate(prog1):
        for (s, k) in endmark.get(t, ()): xend[(s, k)] = dict(loc[s])
        op = e[0]
        if op == 'MOVE': continue
        if op in ('INIT', 'CLEAR'):
            if e[1] < n: loc[e[1]] = {}
            continue
        if op == 'SCALE':
            if e[1] < n: qq = Q(e[2]); loc[e[1]] = {c: v * qq for c, v in loc[e[1]].items()}
            continue
        d_, s_, qq = e[1], e[2], Q(e[3])
        if d_ >= n: continue
        base = dict(loc[d_]) if op == 'ADD' else {}
        if s_ < n:
            for c, v in loc[s_].items():
                x = base.get(c, 0) + qq * v
                if x: base[c] = x
                else: base.pop(c, None)
        loc[d_] = base
    evts = collections.defaultdict(list)
    for t, e in enumerate(prog1):
        if e[0] != 'MOVE':
            for r in S.regfields(e): evts[r].append(t)
    def idle(r, k):
        """idle window of r between its last event in visit k and its first event in visit k+1: (lo, hi) insertion indices"""
        t0, t1, f = tl1[r][k]; t2 = tl1[r][k + 1][1]
        lo = max([t for t in evts[r] if t0 < t < t1] + [t0])
        hi = min([t for t in evts[r] if t1 < t < t2] + [t2])
        return lo, hi
    def cdims(r, extra):
        return tuple(sorted(set(dim[f] for (t0, t1, f) in tl1[r]) | set(extra)))
    # ---------------- per (s, Y) edge: exit gap (K0) and the Y gap whose idle window overlaps s's
    yset_ = set(ro)
    relay_t = collections.defaultdict(list)     # times at which a Y is read by another Y (Y<-Y relay work)
    for t, e in enumerate(prog1):
        if e[0] == 'ADD' and e[1] in yset_ and e[2] in yset_: relay_t[e[2]].append(t)
    edges = []
    inc = sorted({(s, y) for (s, y, f) in sites})
    for (s, y) in inc:
        ks = [k for k, (t0, t1, f) in enumerate(tl1[s]) if all(dot(q[y], b) == 0 for b in fr[f])]
        kA = ks[-1]
        if kA == len(tl1[s]) - 1: print('  edge', s, y, 'no next frame'); continue
        A = tl1[s][kA][2]; B = tl1[s][kA + 1][2]; slo, shi = idle(s, kA)
        cont = [port[c] for c, v in xend[(s, kA)].items() if v]
        G = []
        t0A, t1A, _ = tl1[s][kA]
        swlo = max([t for t in evts[s] if t0A < t < t1A and prog1[t][0] in ('ADD', 'COPY') and prog1[t][1] == s] + [t0A]); swhi = t1A   # s settled at A
        def wins(lo_y, hi_y):
            return (max(slo, lo_y), min(shi, hi_y)), (max(swlo, lo_y), min(swhi, hi_y))
        for k_, (t0, t1, F) in enumerate(tl1[y]):          # 'at': s joins the Y at an existing Y frame F (Y present there)
            wn, wa = wins(t0, t1)
            if wn[0] < wn[1] or wa[0] < wa[1]: G.append(dict(kind='at', ky=k_, Py=sp(F), Ny=sp(F), wn=wn, wa=wa, final=(k_ == len(tl1[y]) - 1)))
        for ky in range(len(tl1[y]) - 1):                     # 'gap': a new Y stop between two Y frames (both idle)
            ylo, yhi = idle(y, ky); wn, wa = wins(ylo, yhi)
            if wn[0] < wn[1] or wa[0] < wa[1]: G.append(dict(kind='gap', ky=ky, Py=sp(tl1[y][ky][2]), Ny=sp(tl1[y][ky + 1][2]), wn=wn, wa=wa))
        if not G: print('  edge', s, y, 'no Y window overlapping the source idle window'); continue
        if not a.allow_final:     # K5: the reader's final frame Q_Y only when no earlier placement is feasible
            def feas(g_):
                if g_['kind'] == 'at': return (g_['wa'][0] < g_['wa'][1] if g_['Py'] == sp(A) else g_['wn'][0] < g_['wn'][1]) and le(rref(cont), g_['Py']) and le(sp(A), g_['Py']) and g_['Py'] != sp(B) and le(g_['Py'], sp(B)) and all(dot(q[y], b) == 0 for b in g_['Py'])
                L_ = rref(cont + list(sp(A)) + list(g_['Py'])); U_ = meet(meet(sp(B), g_['Ny']), perp((q[y],)))
                if not (g_['wn'][0] < g_['wn'][1] or g_['wa'][0] < g_['wa'][1]): return False
                return le(L_, U_) and max(len(L_), dim[A] + 1, len(g_['Py']) + 1) <= min(len(U_), dim[B] - 1, len(g_['Ny']) - 1)
            if any(feas(g_) for g_ in G if not g_.get('final')): G = [g_ for g_ in G if not g_.get('final')]
        edges.append(dict(s=s, y=y, kA=kA, A=sp(A), B=sp(B), Q=perp((q[y],)), cont=rref(cont), gaps=G))
    # ---------------- components (edges sharing a source gap or a Y gap) and the joint closure search (K1-K4)
    par = list(range(len(edges)))
    def fnd(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    seen = {}
    for i, e in enumerate(edges):
        for kk in (('s', e['s'], e['kA']), ('y', e['y'])):
            if kk in seen: par[fnd(i)] = fnd(seen[kk])
            else: seen[kk] = i
    comps = collections.defaultdict(list)
    for i in range(len(edges)): comps[fnd(i)].append(i)
    import itertools
    def join(*xs): return rref([v for x in xs for v in x])
    def meetall(xs):
        u = xs[0]
        for x in xs[1:]: u = meet(u, x)
        return u
    def strict(a_, b_): return le(a_, b_) and a_ != b_
    for ci, ii in comps.items():
        E = [edges[i] for i in ii]
        low = {}; up = {}
        for j, e in enumerate(E):
            for gi, g_ in enumerate(e['gaps']):
                low[(j, gi)] = join(e['cont'], e['A'], g_['Py']); up[(j, gi)] = meetall([e['B'], g_['Ny'], e['Q']])
        cands = {e['A'] for e in E} | {g_['Py'] for e in E for g_ in e['gaps']}
        keys_ = sorted(low)
        for k in range(1, min(len(E), 4) + 1):
            for sub_ in itertools.combinations(keys_, k):
                if len({j for j, _ in sub_}) < k: continue
                cands.add(join(*[low[x] for x in sub_])); cands.add(meetall([up[x] for x in sub_]))
        base = list(cands)
        for x in base:
            for y_ in base:
                cands.add(join(x, y_)); cands.add(meet(x, y_))
        valid = []
        for e in E:
            v = [(gi, f) for gi, g_ in enumerate(e['gaps']) for f in cands if le(e['cont'], f) and le(e['A'], f) and strict(f, e['B']) and le(f, e['Q'])
                 and ((g_['kind'] == 'at' and f == g_['Py']) or (g_['kind'] == 'gap' and strict(g_['Py'], f) and strict(f, g_['Ny'])))
                 and ((g_['wa'][0] < g_['wa'][1]) if f == e['A'] else (g_['wn'][0] < g_['wn'][1]))]
            valid.append(v)
        if any(not v for v in valid): print('  component', [(e['s'], e['y']) for e in E], 'NO VALID FRAME'); continue
        best = []
        for asg in itertools.product(*valid):
            ok = True; cost = 0.0; bal = 0; sdim = 0
            grp = collections.defaultdict(set)
            for e, (gi, f) in zip(E, asg):
                if f != e['A']: grp[('s', e['s'], e['kA'])].add(f)
                if e['gaps'][gi]['kind'] == 'gap': grp[('y', e['y'], e['gaps'][gi]['ky'])].add(f)
            for (key, r, k_), fs in grp.items():
                fs = sorted(fs, key=len)
                if any(not strict(x, y_) for x, y_ in zip(fs, fs[1:])): ok = False; break
                cost += tax(cdims(r, [len(f) for f in fs])) - tax(cdims(r, []))
                sdim += sum(len(f) for f in fs)
                if key == 'y':
                    Py_ = dim[tl1[r][k_][2]]; Ny_ = dim[tl1[r][k_ + 1][2]]
                    bal += sum(1 for f in fs if len(f) - Py_ == Ny_ - len(f))
            if ok: best.append((round(cost, 9), -bal if a.tie == 'bal' else 0, sdim if a.tie == 'lo' else -sdim, asg))
        if not best: print('  component', [(e['s'], e['y']) for e in E], 'NO CHAIN-CONSISTENT ASSIGNMENT'); continue
        best.sort(key=lambda x: x[:3]); m = best[0][0]
        nt = len({b[3] for b in best if b[0] == m})
        for j, (e, (gi, f)) in enumerate(zip(E, best[0][3])):
            e['f'] = f; e['d'] = len(f); e['win'] = e['gaps'][gi]['wa' if f == e['A'] else 'wn']; e['ky'] = e['gaps'][gi]['ky']
            e['how'] = ('K1' if f == e['A'] else ('Yat' if e['gaps'][gi]['kind'] == 'at' else ('L' if f == low[(j, gi)] else ('U' if f == up[(j, gi)] else 'closure')))) + ('/tie%d' % nt if nt > 1 else '')
    for x in a.force:
        s_, f_ = map(int, x.split(':'))
        for e in edges:
            if e['s'] == s_: e['f'] = rref(fr[f_]); e['d'] = dim[f_]; e['how'] = 'FORCED'
    for x in a.force_span:
        s_, vs = x.split(':'); f_ = rref([int(v) for v in vs.split('.')])
        for e in edges:
            if e['s'] == int(s_): e['f'] = f_; e['d'] = len(f_); e['how'] = 'FORCED-SPAN'
    print('rule placements (s, Y, how, level, frame):')
    for e in edges: print('   ', e['s'], e['y'], e.get('how'), e.get('d'), e.get('f'))
    if any('f' not in e for e in edges): print('RESULT: UNPLACED'); return 'UNPLACED'
    # ---------------- insert source stops
    ins = collections.defaultdict(list); dele = set()
    bys = collections.defaultdict(list)
    for e in edges:
        if e['f'] == e['A']: continue
        bys[(e['s'], e['kA'])].append(e)
    for (s, kA), es in bys.items():
        fs = sorted({e['f'] for e in es}, key=len)
        for x, y_ in zip(fs, fs[1:]):
            if not le(x, y_): print('RESULT: SCHEDULE non-nested new stops on', s); return 'SCHEDULE'
        mv = tl1[s][kA][1]; old = prog1[mv]; dele.add(mv)
        # time: s enters each new stop at the start of its window (after the previous stop's entry) and leaves the last one at its window end
        win = {f: (max(e['win'][0] for e in es if e['f'] == f), min(e['win'][1] for e in es if e['f'] == f)) for f in fs}
        tin = []; t = -1
        for f in fs:
            t = max(win[f][0] + 1, t + 1 if tin else win[f][0] + 1)
            if t > win[f][1]: print('RESULT: SCHEDULE window', s); return 'SCHEDULE'
            tin.append(t)
        for j in range(len(fs) - 1):
            if tin[j + 1] > win[fs[j]][1]: print('RESULT: SCHEDULE order', s); return 'SCHEDULE'
        tout = win[fs[-1]][1] if a.stime == 'span' else tin[-1]
        fids = []
        for f in fs:
            if f not in fidx: fr.append(sorted(f, reverse=True)); dim.append(len(f)); fidx[f] = len(fr) - 1; print('  NEW frame', f)
            fids.append(fidx[f])
        prev = old[2]
        for t_, fi in zip(tin, fids): ins[t_].append(['MOVE', s, prev, fi, old[4]]); prev = fi
        ins[tout].append(['MOVE', s, prev, old[3], old[4]])
    prog2 = []
    for t in range(len(prog1) + 1):
        prog2 += ins.get(t, [])
        if t < len(prog1) and t not in dele: prog2.append(prog1[t])
    w2 = dict(w); w2['program'] = prog2; w2['frames'] = fr
    # ---------------- compare source chains with the swarm
    ch2 = {r: [w['initial'][r]] for r in range(n)}
    for e in prog2:
        if e[0] == 'MOVE' and e[1] < n: ch2[e[1]].append(e[3])
    sdiff = [(s, [dim[f] for f in ch0[s]], [dim[f] for f in ch2[s]]) for s in srcs if ch0[s] != ch2[s]]
    print('source chains differing from #6030 after the skeleton rebuild: %d %s' % (len(sdiff), sdiff[:10]))
    tmp = a.out.replace('.json.gz', '_skel.json.gz')
    with gzip.open(tmp, 'wt') as fh: json.dump(w2, fh)
    if a.no_yb: return dict(sdiff=len(sdiff), edges=edges)
    import routing as yb
    sarg = ','.join('%d:%d' % (s, y) for (s, y) in inc)
    r = yb.main([tmp, a.out, '--sites', sarg, '--time', 'settled', '--yset', 'all'])
    if not isinstance(r, dict): print('RESULT(yb):', r); return r
    _, w3 = S.load_word(a.out); w3 = json.loads(json.dumps(w3))
    ch3 = {r_: [w3['initial'][r_]] for r_ in range(n)}
    for e in w3['program']:
        if e[0] == 'MOVE' and e[1] < n: ch3[e[1]].append(e[3])
    diff = [(r_, [dim[f] for f in ch0[r_]], [dim[f] for f in ch3[r_]]) for r_ in range(n) if ch0[r_] != ch3[r_]]
    ms0 = collections.Counter(json.dumps(e) for e in prog0); ms3 = collections.Counter(json.dumps(e) for e in w3['program'])
    print('FINAL: registers whose chain differs from #6030: %d %s' % (len(diff), diff[:8]))
    print('FINAL: event multiset equal to #6030: %s (events %d vs %d)' % (ms0 == ms3, len(w3['program']), len(prog0)))
    print('FINAL: kappa %.15f base %.15f' % (r['kappa'], r['base']))
    return dict(kappa=r['kappa'], base=r['base'], nchdiff=len(diff), sdiff=len(sdiff), multiset=(ms0 == ms3), edges=len(edges), sstr=len(sstr), ystr=len(ystr))

if __name__ == '__main__': r = main(); print({k: v for k, v in r.items() if k != 'edges'} if isinstance(r, dict) else r)
