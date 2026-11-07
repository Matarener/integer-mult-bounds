"""Stage-3 record (Lean `RankNine.T2.St3`, T1Stage3.lean) for one hard type k (NOTE §13.25 stage 3).

* BIG = frames E with |E ∩ Z| >= 4 leaving Z; their possible supports = non-empty subsets of E \\ Z.
* Branch order = closing order of t2hand/killed-T1_k.txt (orbit representatives), each expanded to its images under
  the stabiliser of Z in the group of order 384 (so every support appears; checked).
* Branch i (support σ): dead mask m_i = Z ∪ σ^⊥; extra valid frames XF_i = frames E not inside m_i such that every
  non-empty τ ⊆ E \\ m_i is an earlier support or (τ ≠ σ and σ ∪ τ orthogonal) (D2).  T1 record by the usual pipeline
  (t1case / contag / lrat8 / emit_t2zero / wdata with T1MASK, T1XF, T1TGT = Z).  If the record is Gram on all of Z:
  s = 104; else ZKILL: s ∈ σ, rows X ⊆ zm ∩ m_i ∩ s^⊥, columns Y ⊆ zm, 8 x 8 integer block with adjugate.
* Branch (a): mask Z, XF = BIG.
Writes out/st3-k/br-<i>.txt (one number stream per branch), a0.txt, and assembles ST3_k.txt (field order of
T1Stage3 decoder).  Branches run in parallel (P workers).  usage: P=4 python3 t1lean/st3.py k [i0 i1]"""
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
T2K = os.environ.get('KIND') == 'T2'      # T2: frameless type k (orbitsW entries without frame), target Gram on C
rw = [r for r in json.load(open(os.path.join(BASE, 'orbitsW.json'))) if r['frame'] != T2K]
TAG = ('t2-%d' if T2K else 'st3-%d') % k; PRE = 'T2S' if T2K else 'S3'
m0 = int(rw[k]['mask']); Z = [i for i in range(N) if m0 >> i & 1]; Zs = frozenset(Z)
UPOOR = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}     # poor types: target Z - {u} (NOTE §4; T3 special U = u)
Zt = Zs - {UPOOR[k]} if k in UPOOR and not T2K else Zs; mt = sum(1 << x for x in Zt)
OUT = os.path.join(HERE, 'st3', TAG); os.makedirs(OUT, exist_ok=True)
def bits(S): return sum(1 << s for s in S)
def perp(S): return frozenset(x for x in range(N) if all(OR[x][s] for s in S))
def subsets(O):
    return [frozenset(c) for r in range(1, len(O) + 1) for c in itertools.combinations(sorted(O), r)]
BIG = [tuple(E) for E in FR if len(set(E) & Zs) >= 4 and set(E) - Zs]
need = set()
for E in BIG: need |= set(subsets(set(E) - Zs))
AUT = json.load(open(os.path.join(BASE, 'aut384.json')))
stab = [g for g in AUT if all(g[x] in Zs for x in Z)]
order = []; seen = set()
for l in open(os.path.join(BASE, 't2hand', ('killed-%d.txt' if T2K else 'killed-T1_%d.txt') % k)):
    if not l.strip(): continue
    S0 = frozenset(map(int, l.strip().split(',')))
    for g in stab:
        S = frozenset(g[x] for x in S0)
        if S not in seen: seen.add(S); order.append(S)
miss = need - seen
print('type', k, '|Z|', len(Z), 'BIG', len(BIG), 'supports needed', len(need), 'listed', len(order), 'missing', len(miss), flush=True)
assert not miss
def orth_set(U): return all(OR[a][b] for a, b in itertools.combinations(sorted(U), 2))
def valid_frames(m, sig, prev):
    ms = frozenset(x for x in range(N) if m >> x & 1); XF = []
    for E in FR:
        O = set(E) - ms
        if not O: continue
        if all(t in prev or (t != sig and orth_set(sig | t)) for t in subsets(O)): XF.append(sorted(E))
    return XF
def sh(cmd, env):
    return subprocess.run(['bash', '-c', cmd], env=env, cwd=BASE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
def pipeline(name, m, XF):
    """T1 record on dead mask m with extra frames XF, target Z; returns (cert dict, record numbers) or None"""
    xf = os.path.join(OUT, name + '-xf.json'); json.dump(XF, open(xf, 'w'))
    S = os.path.join(OUT, name); ex = os.path.join(OUT, name + '-excl.json')
    for cfg in ({'DTREE': '', 'RULES': 'ac'}, {'DTREE': '1', 'RULES': 'abc'}, {'DTREE': '', 'RULES': 'abc'}):
      excl = []
      for _round in range(4):
        json.dump(excl, open(ex, 'w'))
        env = dict(os.environ, T1MASK=str(m), T1XF=xf, T1TGT=str(mt), T1NAME=name, T1K=str(k), T1EXCL=ex, **cfg)
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
def zkill(sig, m, zm):
    zms = set(zm)
    Y = indep8(sorted(zms))
    if Y is None: return None
    for s in sorted(sig):
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
    f = next((i for i, F in enumerate(PFR) if all(x in set(zm) for x in F)), 0)
    out = [f, len(PL)]
    for v, k0, X, Nn, No, D, pm in PL:
        out += [v, k0, len(X)] + list(X) + [len(Nn)]
        for r in Nn: out += [len(r)] + [zz(x) for x in r]
        out += [len(No)] + [zz(x) for x in No] + [zz(D), pm]
    return f, out, sorted(zms)
def zz(v): return 2 * v if v >= 0 else -2 * v - 1          # zig-zag for integers (T3Decode.rint)
def branch(i):
    sig = order[i]; prev = set(order[:i]); t0 = time.time()
    m = m0 | bits(perp(sig))
    XF = valid_frames(m, sig, prev)
    res = pipeline(PRE + '_%d_%d' % (k, i), m, XF)
    if res is None: return i, 'PIPE FAIL', None
    c, nums, cfg = res
    f, pout, zm = pins(m, c['ZM'])
    if set(zm) >= Zt:
        out = [bits(sig)] + nums + [len(XF)] + [x for E in XF for x in E] + [104, 0, 0, 0, zz(0)] + pout
        tag = 'GRAM'
    else:
        zk = zkill(sig, m, zm)
        if zk is None: return i, 'ZKILL FAIL |zm|=%d |Z|=%d' % (len(zm), len(Z)), None
        s, X, Y, J, dd = zk
        if len(sig) == 1: return i, 'ZKILL on a one-line support', None
        out = [bits(sig)] + nums + [len(XF)] + [x for E in XF for x in E] + [s, 8] + X + [8] + Y + \
              [8] + [v for row in J for v in [8] + [zz(a) for a in row]] + [zz(dd)] + pout
        tag = 'ZKILL s=%d' % s
    open(os.path.join(OUT, 'br-%d.txt' % i), 'w').write(' '.join(map(str, out)) + '\n')
    return i, '%s |σ|=%d XF %d zm %d->%d (Z %d) cfg %s %.0fs' % (tag, len(sig), len(XF), len(c['ZM']), len(zm), len(Z), cfg, time.time() - t0), out
if __name__ == '__main__':
    lo, hi = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (0, len(order))
    log = open(os.path.join(OUT, 'log.txt'), 'a', buffering=1)
    if lo == 0 and not os.path.exists(os.path.join(OUT, 'a0.txt')):
        res = pipeline(PRE + '_%d_a' % k, m0, [sorted(E) for E in BIG])
        if res is not None: f0, pout0, zma = pins(m0, res[0]['ZM'])
        ok = res is not None and set(zma) >= Zt
        msg = 'branch (a): %s' % ('OK' if ok else 'FAIL ' + ('pipe' if res is None else 'zm %d/%d' % (len(zma), len(Z))))
        print(msg, flush=True); log.write(msg + '\n')
        if ok: open(os.path.join(OUT, 'a0.txt'), 'w').write(' '.join(map(str, res[1] + pout0)) + '\n')
    todo = [i for i in range(lo, hi) if not os.path.exists(os.path.join(OUT, 'br-%d.txt' % i))]
    with Pool(int(os.environ.get('P', '4'))) as pool:
        for i, msg, _ in pool.imap_unordered(branch, todo):
            line = 'branch %d %s %s' % (i, sorted(order[i]), msg); print(line, flush=True); log.write(line + '\n')
    nb = len(order)
    if os.environ.get('PARTIAL'):      # test: the first branches present
        nb = next((i for i in range(len(order)) if not os.path.exists(os.path.join(OUT, 'br-%d.txt' % i))), len(order))
    done = all(os.path.exists(os.path.join(OUT, 'br-%d.txt' % i)) for i in range(nb)) and \
        os.path.exists(os.path.join(OUT, 'a0.txt'))
    if done:
        a0 = open(os.path.join(OUT, 'a0.txt')).read().split()
        RD = os.path.join(HERE, 'records', TAG); os.makedirs(RD, exist_ok=True)
        open(os.path.join(RD, 'head.txt'), 'w').write(' '.join(map(str, [m0, mt, len(BIG)] + [x for E in BIG for x in sorted(E)])) + ' ' + ' '.join(a0) + ' %d\n' % nb)
        import shutil
        for i in range(nb): shutil.copy(os.path.join(OUT, 'br-%d.txt' % i), os.path.join(RD, 'br-%d.txt' % i))
        print('ST3 %d written: %d branches' % (k, nb), flush=True)
