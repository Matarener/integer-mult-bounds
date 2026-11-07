"""T2 record by orbits (Lean `RankNine.T2S`): for frameless representative k, the items are the support orbit
representatives of t2hand/killed-k.txt in closing order, each preceded by its joint items (S, S') from
t2hand/jkill-k.txt (type 7).  Item j assumes its supports (σ, and ctx = S' if joint) and that no image under the
stabiliser of C of an earlier item holds; dead mask C ∪ σ^⊥ (∪ ctx^⊥).  A frame leaving the mask is valid if every
non-empty τ of its outside set is excluded: an image of an earlier plain item, D2 with σ or ctx, or an image of an
earlier joint item together with σ or ctx.  Closing: Gram on C (then the pair certificates give the contradiction),
or ZKILL at s ∈ σ ∪ ctx with {s} excluded.  Stream per item as st3.py plus ctx at the end.
usage: P=4 python3 t1lean/t2s.py k [i0 i1]"""
import os, sys, json, itertools, subprocess, time
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(BASE, 't2hand', 'rev'))
from common import N, OR, FR
GEN = os.environ.get('GEN', os.path.normpath(os.path.join(BASE, '..')))
sys.path.insert(0, GEN)
from rank_cert import rootv, cert as rcert_of
from p104lib import frames as plframes, IDX as PIDX
PFR = [tuple(PIDX[q] for q in f) for f in plframes()]     # frame order of Lean `frL`
import sympy
k = int(sys.argv[1])
T2K = True
rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if not r['frame']]
TAG = 't2s-%d' % k; PRE = 'T2O'
m0 = int(rw[k]['mask']); Z = [i for i in range(N) if m0 >> i & 1]; Zs = frozenset(Z)
UPOOR = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}     # poor types: target Z - {u} (NOTE §4; T3 special U = u)
DROP = {int(a): set(b) for a, b in json.load(open(os.path.join(BASE, 't2hand', 't2drop.json'))).items()}
Zt = Zs - DROP.get(k, set())      # T2 target: C minus lines no item can pin (no frame inside the Gram set)
mt = sum(1 << x for x in Zt)
OUT = os.path.join(HERE, 'st3', TAG); os.makedirs(OUT, exist_ok=True)
def bits(S): return sum(1 << s for s in S)
def perp(S): return frozenset(x for x in range(N) if all(OR[x][s] for s in S))
def subsets(O):
    return [frozenset(c) for r in range(1, len(O) + 1) for c in itertools.combinations(sorted(O), r)]
BIG = [tuple(E) for E in FR if len(set(E) & Zs) >= 4 and set(E) - Zs]
need = set()
for E in BIG: need |= set(subsets(set(E) - Zs))
import re
LEAN = os.environ.get('LEANDIR', os.path.normpath(os.path.join(BASE, '..', '..', 'lean', 'RankNine')))
_gs = open(os.path.join(LEAN, 'GrpData.lean')).read(); _gs = _gs[_gs.index('def grpData'):]; _gs = _gs[_gs.index(':= [') + 4:]
_gs = _gs[:_gs.index(']]') + 1]
GRP = [list(map(int, re.findall(r'\d+', b))) for b in re.findall(r'\[([^\[\]]*)\]', _gs)]
assert len(GRP) == 384
STAB = [g for g in range(384) if all(GRP[g][x] in Zs for x in Z)]
def img(g, S): return frozenset(GRP[g][x] for x in S)
items = []; plain = []
JK = {}
jf = os.path.join(BASE, 't2hand', 'jkill-%d.txt' % k)
if os.path.exists(jf):
    for l in open(jf):
        if l.strip():
            a, b = l.strip().split('|'); JK.setdefault(frozenset(map(int, a.split(','))), []).append(frozenset(map(int, b.split(','))))
for l in open(os.path.join(BASE, 't2hand', 'killed-%d.txt' % k)):
    if not l.strip(): continue
    S0 = frozenset(map(int, l.strip().split(',')))
    for S1 in dict.fromkeys(JK.get(S0, [])): items.append((S0, S1))
    items.append((S0, None))
covered = set(img(g, S) for S, c in items if c is None for g in STAB)
miss = need - covered
print('type', k, '|C|', len(Z), 'BIG', len(BIG), 'supports needed', len(need), 'items', len(items),
      'joint', sum(1 for _, c in items if c is not None), 'stab', len(STAB), 'missing', len(miss), flush=True)
assert not miss
def prevsets(j):
    PS = set(); PJ = set()
    for S, c in items[:j]:
        for g in STAB:
            if c is None: PS.add(img(g, S))
            else: PJ.add(frozenset([img(g, S), img(g, c)]))
    return PS, PJ
def orth_set(U): return all(OR[a][b] for a, b in itertools.combinations(sorted(U), 2))
def excl(t, sig, ctx, PS, PJ):
    return (t in PS or (t != sig and orth_set(sig | t)) or (ctx is not None and t != ctx and orth_set(ctx | t)) or
            frozenset([sig, t]) in PJ or (ctx is not None and frozenset([ctx, t]) in PJ))
def valid_frames(m, sig, ctx, PS, PJ):
    ms = frozenset(x for x in range(N) if m >> x & 1); XF = []
    for E in FR:
        O = set(E) - ms
        if not O: continue
        if all(excl(t, sig, ctx, PS, PJ) for t in subsets(O)): XF.append(sorted(E))
    return XF
def sh(cmd, env):
    return subprocess.run(['bash', '-c', cmd], env=env, cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def pipeline(name, m, XF, tgt=None):
    """T1 record on dead mask m with extra frames XF, target Z; returns (cert dict, record numbers) or None"""
    xf = os.path.join(OUT, name + '-xf.json'); json.dump(XF, open(xf, 'w'))
    S = os.path.join(OUT, name); ex = os.path.join(OUT, name + '-excl.json')
    for cfg in ({'DTREE': '', 'RULES': 'ac'}, {'DTREE': '1', 'RULES': 'abc'}, {'DTREE': '', 'RULES': 'abc'}):
      excl = []
      for _round in range(4):
        json.dump(excl, open(ex, 'w'))
        env = dict(os.environ, T1MASK=str(m), T1XF=xf, T1TGT=str(mt if tgt is None else tgt), T1NAME=name, T1K=str(k), T1EXCL=ex, **cfg)
        cert = os.path.join(HERE, 'cert', name + '.json')
        if os.path.exists(cert): os.remove(cert)
        r = sh('python3 t1lean/t1case.py', env)
        if not os.path.exists(cert): break
        c = json.load(open(cert))
        r = sh(f'python3 t1lean/zero/contag.py {k} {S}-chains.json {cert} > {S}-contag.txt 2>&1', env)
        und = json.load(open(S + '-chains.json'))['unrefuted'] if r.returncode == 0 else None
        if und is None: break
        if und:
            excl += [list(e) for e in und]; continue
        r = sh(f'python3 t1lean/zero/lrat8.py {k} {cert} {S}-chains.json {S}-origin.json {S}-proof.lrat > /dev/null && '
               f'ZJSON={S}-zj.json python3 kaggle-t2zero/emit_t2zero.py {cert} {S}-origin.json {S}-proof.lrat {name} /dev/null > /dev/null && '
               f'python3 t1lean/wdata.py {cert} {S}-zj.json {S}-rec.txt > /dev/null', env)
        if r.returncode == 0 and os.path.exists(S + '-rec.txt'):
            nums = list(map(int, open(S + '-rec.txt').read().split()))
            for f in ('-origin.json', '-proof.lrat', '-chains.json'):
                try: os.remove(S + f)
                except OSError: pass
            return c, nums, cfg
        break
    return None
def dotv(a, b): return sum(x * y for x, y in zip(rootv(a), rootv(b)))
def indep8(cand):
    """8 lines of cand with independent roots (greedy), or None"""
    sel = []; M = sympy.Matrix(0, 9, [])
    for x in cand:
        M2 = M.col_join(sympy.Matrix([rootv(x)]))
        if M2.rank() > M.rows: M = M2; sel.append(x)
        if len(sel) == 8: return sel
    return None
def zkill(sig, m, zm, ctx=None, PS=(), PJ=()):
    zms = set(zm)
    Y = indep8(sorted(zms))
    if Y is None: return None
    for s in sorted(sig | (ctx or frozenset())):
        if not excl(frozenset([s]), sig, ctx, PS, PJ): continue
        X = indep8([x for x in sorted(zms) if m >> x & 1 and OR[x][s]])
        if X is None: continue
        D = sympy.Matrix([[dotv(x, y) for y in Y] for x in X]); dd = D.det()
        if dd == 0: continue
        J = D.adjugate()
        return s, X, Y, [[int(J[i, j]) for j in range(8)] for i in range(8)], int(dd)
    return None
def pins(m, zm):
    """iterated rank-7 pins of dead lines over the Gram set; returns (f, PL numbers, final zm)"""
    zms = set(zm); PL = []; ch = True
    while ch:
        ch = False
        for v in range(N):
            if not (m >> v & 1) or v in zms: continue
            k0 = next(i for i in range(9) if rootv(v)[i])
            c = rcert_of([x for x in sorted(zms) if OR[x][v]], [k0])
            if c is None: continue
            PL.append((v, k0) + tuple(c)); zms.add(v); ch = True
    f = next((i for i, F in enumerate(PFR) if all(x in set(zm) for x in F)), None)
    if f is None:
        if PL: return 0, [0, 0], sorted(set(zm))    # pins need a frame inside the Gram set: no pins (record zm only)
        f = 0
    out = [f, len(PL)]
    for v, k0, X, Nn, No, D, pm in PL:
        out += [v, k0, len(X)] + list(X) + [len(Nn)]
        for r in Nn: out += [len(r)] + [zz(x) for x in r]
        out += [len(No)] + [zz(x) for x in No] + [zz(D), pm]
    return f, out, sorted(zms)
def zz(v): return 2 * v if v >= 0 else -2 * v - 1          # zig-zag for integers (T3Decode.rint)
def branch(i):
    sig, ctx = items[i]; PS, PJ = prevsets(i); t0 = time.time()
    m = m0 | bits(perp(sig)) | (bits(perp(ctx)) if ctx is not None else 0)
    XF = valid_frames(m, sig, ctx, PS, PJ)
    res = pipeline(PRE + '_%d_%d' % (k, i), m, XF, tgt=m)     # Gram set may leave C (a frame inside it is needed for pins)
    if res is None: return i, 'PIPE FAIL', None
    c, nums, cfg = res
    f, pout, zm = pins(m, c['ZM'])
    if pout == [0, 0] and not set(zm) >= Zt and zkill(sig, m, zm, ctx, PS, PJ) is None:
        res2 = pipeline(PRE + '_%d_%d' % (k, i), m, XF)       # no frame for pins: retry with target C
        if res2 is not None:
            c2, nums2, cfg2 = res2
            f2, pout2, zm2 = pins(m, c2['ZM'])
            if set(zm2) >= Zt or zkill(sig, m, zm2, ctx, PS, PJ) is not None:
                c, nums, cfg, f, pout, zm = c2, nums2, cfg2, f2, pout2, zm2
    if pout is None: return i, 'NOFRAME |zm|=%d' % len(c['ZM']), None
    cx = bits(ctx) if ctx is not None else 0
    if set(zm) >= Zt:
        out = [bits(sig)] + nums + [len(XF)] + [x for E in XF for x in E] + [104, 0, 0, 0, zz(0)] + pout + [cx]
        tag = 'GRAM'
    else:
        zk = zkill(sig, m, zm, ctx, PS, PJ)
        if zk is None: return i, 'ZKILL FAIL |zm|=%d |Z|=%d' % (len(zm), len(Z)), None
        s, X, Y, J, dd = zk
        out = [bits(sig)] + nums + [len(XF)] + [x for E in XF for x in E] + [s, 8] + X + [8] + Y + \
              [8] + [v for row in J for v in [8] + [zz(a) for a in row]] + [zz(dd)] + pout + [cx]
        tag = 'ZKILL s=%d' % s
    json.dump({'XF': XF, 'm': m, 's': (104 if tag == 'GRAM' else s)}, open(os.path.join(OUT, 'br-%d.json' % i), 'w'))
    open(os.path.join(OUT, 'br-%d.txt' % i), 'w').write(' '.join(map(str, out)) + '\n')
    return i, '%s |σ|=%d ctx %s XF %d zm %d->%d (C %d) cfg %s %.0fs' % (tag, len(sig), sorted(ctx) if ctx else '-', len(XF), len(c['ZM']), len(zm), len(Z), cfg, time.time() - t0), out
if __name__ == '__main__':
    lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, len(items))
    log = open(os.path.join(OUT, 'log.txt'), 'a', buffering=1)
    if lo == 0 and not os.path.exists(os.path.join(OUT, 'a0.txt')):
        res = pipeline(PRE + '_%d_a' % k, m0, [sorted(E) for E in BIG])
        if res is not None: f0, pout0, zma = pins(m0, res[0]['ZM'])
        ok = res is not None and pout0 is not None and set(zma) >= Zt
        msg = 'branch (a): %s' % ('OK' if ok else 'FAIL ' + ('pipe' if res is None else 'zm %d/%d' % (len(zma), len(Z))))
        print(msg, flush=True); log.write(msg + '\n')
        if ok: open(os.path.join(OUT, 'a0.txt'), 'w').write(' '.join(map(str, res[1] + pout0)) + '\n')
    todo = [i for i in range(lo, hi) if not os.path.exists(os.path.join(OUT, 'br-%d.txt' % i))]
    with Pool(int(os.environ.get('P', '4'))) as pool:
        for i, msg, _ in pool.imap_unordered(branch, todo):
            line = 'item %d %s %s' % (i, sorted(items[i][0]), msg); print(line, flush=True); log.write(line + '\n')
    nb = len(items)
    if os.environ.get('PARTIAL'):      # test: the first branches present
        nb = next((i for i in range(len(items)) if not os.path.exists(os.path.join(OUT, 'br-%d.txt' % i))), len(items))
    done = all(os.path.exists(os.path.join(OUT, 'br-%d.txt' % i)) for i in range(nb)) and \
        os.path.exists(os.path.join(OUT, 'a0.txt'))
    if done:
        IMG = {}; JIMG = {}
        for i, (S, c) in enumerate(items):
            for g in STAB:
                if c is None: IMG.setdefault(img(g, S), (i, g))
                else: JIMG.setdefault(frozenset([img(g, S), img(g, c)]), (i, g))
        def d2(t, a): return t != a and orth_set(a | t)
        def wit(t, j, sig, ctx):
            """witness (τ, i, g, kind) for τ in item j, or None if zero / D2 suffices"""
            if not t or d2(t, sig) or (ctx is not None and d2(t, ctx)): return None
            e = IMG.get(t)
            if e is not None and e[0] < j: return (bits(t), e[0], e[1], 0)
            for a in [sig] + ([ctx] if ctx is not None else []):
                e = JIMG.get(frozenset([a, t]))
                if e is not None and e[0] < j: return (bits(t), e[0], e[1], 1)
            raise AssertionError(('no witness', j, sorted(t)))
        def ewlist(j, sig, ctx, frames, m, s):
            ms = frozenset(x for x in range(N) if m >> x & 1); EW = {}
            for E in frames:
                for t in subsets(set(E) - ms):
                    w = wit(t, j, sig, ctx)
                    if w: EW[w[0]] = w
            if s != 104:
                w = wit(frozenset([s]), j, sig, ctx)
                if w: EW[w[0]] = w
            return [x for w in EW.values() for x in w], len(EW)
        a0 = open(os.path.join(OUT, 'a0.txt')).read().split()
        EW0 = {}
        for E in BIG:
            for t in subsets(set(E) - Zs):
                e = IMG.get(t); assert e is not None, ('BIG support without plain item', sorted(t))
                EW0[bits(t)] = (bits(t), e[0], e[1], 0)
        RD = os.path.join(HERE, 'records', TAG); os.makedirs(RD, exist_ok=True)
        head = [mt, len(BIG)] + [x for E in BIG for x in sorted(E)] + [int(x) for x in a0] + [len(EW0)] + \
            [x for w in EW0.values() for x in w] + [len(STAB)] + STAB + [nb]
        open(os.path.join(RD, 'head.txt'), 'w').write(' '.join(map(str, head)) + '\n')
        nw = 0
        for i in range(nb):
            sig, ctx = items[i]; info = json.load(open(os.path.join(OUT, 'br-%d.json' % i)))
            ew, n = ewlist(i, sig, ctx, info['XF'], info['m'], info['s']); nw += n
            open(os.path.join(RD, 'br-%d.txt' % i), 'w').write(open(os.path.join(OUT, 'br-%d.txt' % i)).read().strip() +
                ' %d %s\n' % (n, ' '.join(map(str, ew))))
        print('T2S %d written: %d items, %d witnesses, EW0 %d' % (k, nb, nw, len(EW0)), flush=True)
