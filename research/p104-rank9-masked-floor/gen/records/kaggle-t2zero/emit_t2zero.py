"""Emit RankNine/T2Cert/Z_<Name>.lean (T2 zero step, RankNine/T2Zero.lean) from the origin JSON of t2zero_cnf.py and
CaDiCaL's LRAT proof.  Keeps only the clauses/lemmas the proof needs, renumbers variables densely (most used first,
from 1), builds the entry table exactly as `entryOK` / `clOf` read it, replays the Lean checks in Python (`mirror`)
including RUP with unit variables, and writes BT tables.  Edge tables ER, EC are written as in the gluing file (emit_t2lean.py).
usage: emit_t2zero.py cert.json[.gz] origin.json[.xz] proof.lrat[.xz] Name out.lean      Apache-2.0."""
import sys, json, gzip, lzma, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../kaggle-t2close')
from p104lib import frames, IDX, ORTH
import emit_t2lean as ET
FR = [tuple(IDX[q] for q in f) for f in frames()]
CH = 150


def opn(p, mode='rt'):
    return lzma.open(p, mode) if p.endswith('.xz') else gzip.open(p, mode) if p.endswith('.gz') else open(p, mode)


def main(cp, op, pp, name, out):
    c = json.load(opn(cp)); o = json.load(opn(op))
    VT0, org, s0, m = o['VT'], o['origin'], o['s0'], o['m']
    s0L = s0 if s0 >= 0 else 104
    VID = {tuple(v): i + 1 for i, v in enumerate(VT0)}
    ncls = len(org)
    lem = {}
    with opn(pp) as f:
        for line in f:
            a = line.split()
            if len(a) > 1 and a[1] == 'd': continue
            i = int(a[0]); z = a.index('0', 1); lem[i] = ([int(x) for x in a[1:z]], [int(x) for x in a[z + 1:-1]])
    root = min(i for i, (l, h) in lem.items() if not l)
    need = set(); st = [root]
    while st:
        i = st.pop()
        if i in need: continue
        need.add(i)
        if i > ncls: st.extend(lem[i][1])
    ids = sorted(need)
    gi = [i for i in ids if i <= ncls and org[i - 1][0] == 'G']
    if not gi: ids = ids + []   # goal not used: still fine (proof refutes without it)
    def kz(x, y): return ORTH[x][y] or y == s0
    def terms(F, t, s): return [f for f in F if m >> f & 1 and not kz(t, f) and not kz(f, s)]
    # original clause -> (kind data in old variable ids)
    def orig(i):
        g = org[i - 1]
        if g[0] == 'd':
            pv, k = g[1], g[2]; _, t, f, s = VT0[pv - 1]
            return [0, k, pv, VID[('z', t, f)], VID[('z', f, s)]]
        if g[0] in 'AB':
            fi, t, s = g[1], g[2], g[3]; F = FR[fi]
            L = terms(F, t, s); ps = [VID[('p', t, f, s)] for f in L]
            zt = 0 if t == s or kz(t, s) else VID[('z', t, s)]
            return [1, fi, t, s, zt] + ps if g[0] == 'A' else [2, fi, t, s, zt, g[4]] + ps
        return [3]
    raw = []
    for i in ids:
        if i <= ncls: raw.append(('o', orig(i)))
        else: raw.append(('l', lem[i]))
    # variable renumbering (most used first), goal variables included
    goal_old = {e: VID[('z', x, y)] for e, (x, y) in enumerate(c['EDG']) if x != y}
    cnt = collections.Counter()
    for kd, r in raw:
        if kd == 'o':
            if r[0] == 0: cnt.update(r[2:5])
            elif r[0] == 1: cnt.update(([r[4]] if r[4] else []) + r[5:])
            elif r[0] == 2: cnt.update(([r[4]] if r[4] else []) + r[6:])
        else: cnt.update(abs(x) for x in r[0])
    for v in goal_old.values(): cnt[v] += 0
    order = sorted(cnt, key=lambda v: (-cnt[v], v))
    NV = {v: j + 1 for j, v in enumerate(order)}
    VT = {NV[v]: ([0, VT0[v - 1][1], VT0[v - 1][2]] if VT0[v - 1][0] == 'z' else [1] + VT0[v - 1][1:]) for v in order}
    fis = sorted({r[1] for kd, r in raw if kd == 'o' and r[0] in (1, 2)})
    FI = {fi: j for j, fi in enumerate(fis)}; FT = {j: list(FR[fi]) for fi, j in FI.items()}
    idx = {i: j for j, i in enumerate(ids)}
    EN = []
    for (kd, r), i in zip(raw, ids):
        if kd == 'o':
            if r[0] == 0: EN.append([0, r[1], NV[r[2]], NV[r[3]], NV[r[4]]])
            elif r[0] == 1: EN.append([1, FI[r[1]], r[2], r[3], NV[r[4]] if r[4] else 0] + [NV[v] for v in r[5:]])
            elif r[0] == 2: EN.append([2, FI[r[1]], r[2], r[3], NV[r[4]] if r[4] else 0, r[5]] + [NV[v] for v in r[6:]])
            else: EN.append([3])
        else:
            l, h = r
            EN.append([4, len(l)] + [2 * NV[abs(x)] + (1 if x > 0 else 0) for x in l] + [y for x in h for y in (idx[x], 0)])
    G = 0
    for v in goal_old.values(): G |= 1 << NV[v]
    GV = {e: NV[v] for e, v in goal_old.items()}
    n = len(EN)

    # ---- mirror of the Lean checker
    def mk(l):
        x = 0
        for v in l: x |= 1 << v
        return x
    def zl(z): return [] if z == 0 else [z]
    def clOf(e):
        k = e[0]
        if k == 0: return (0, mk([e[2], e[3]])) if e[1] == 0 else (0, mk([e[2], e[4]])) if e[1] == 1 else (mk(e[2:5]), 0)
        if k == 1: return (mk(zl(e[4]) + e[5:]), 0)
        if k == 2:
            ps = e[6:]; i = e[5]; return (mk(ps[:i] + ps[i + 1:]), mk(zl(e[4]) + [ps[i]]))
        if k == 3: return (G, 0)
        lits = e[2:2 + e[1]]
        return (mk([x // 2 for x in lits if x % 2 == 1]), mk([x // 2 for x in lits if x % 2 == 0]))
    CL = [clOf(e) for e in EN]
    def log2(x): return x.bit_length() - 1
    def unit(T, F, cl):
        rp = cl[0] ^ (cl[0] & F); rq = cl[1] ^ (cl[1] & T)
        if rp == 0 and rq == 0: return 0, T, F, 0
        if rq == 0 and rp == 1 << log2(rp): return 1, T | rp, F, log2(rp)
        if rp == 0 and rq == 1 << log2(rq): return 1, T, F | rq, log2(rq)
        return 2, T, F, 0
    def tOK(fi, t, s, ps):
        F = FT.get(fi, [])
        L = [f for f in F if m >> f & 1 and not (ORTH[t][f] or f == s0L) and not (ORTH[f][s] or s == s0L)]
        return (F != [] and all(f < 104 for f in F) and t < 104 and s < 104 and m >> t & 1 and
                all(m >> f & 1 or ORTH[t][f] for f in F) and len(ps) == len(L) and
                all(VT.get(ps[j]) == [1, t, L[j], s] for j in range(len(ps))))
    for j, e in enumerate(EN):
        k = e[0]
        if k == 0:
            w = VT.get(e[2], [])
            ok = e[1] < 3 and len(w) == 4 and w[0] == 1 and VT.get(e[3]) == [0, w[1], w[2]] and VT.get(e[4]) == [0, w[2], w[3]]
        elif k == 1:
            ok = tOK(e[1], e[2], e[3], e[5:]) and (e[2] == e[3] if e[4] == 0 else VT.get(e[4]) == [0, e[2], e[3]])
        elif k == 2:
            ok = tOK(e[1], e[2], e[3], e[6:]) and e[5] < len(e[6:]) and \
                ((ORTH[e[2]][e[3]] or e[3] == s0L) if e[4] == 0 else VT.get(e[4]) == [0, e[2], e[3]])
        elif k == 3: ok = True
        else:
            nl = e[1]; hs = e[2 + nl:]; hp = [(hs[2 * q], hs[2 * q + 1]) for q in range(len(hs) // 2)]
            ok = all(h < j for h, _ in hp)
            T, F = CL[j][1], CL[j][0]; conf = False
            for q, (h, _) in enumerate(hp):
                r_, T, F, v = unit(T, F, CL[h]); e[2 + nl + 2 * q + 1] = v
                if r_ == 0: conf = True; break
                if r_ == 2: break
            ok = ok and conf
            CL[j] = clOf(e)
        assert ok, ('entry check failed', j, e[:8])
    assert CL[n - 1] == (0, 0), 'last entry is not the empty clause'
    for e, (x, y) in enumerate(c['EDG']):
        assert x < 104 and (x == y or (G >> GV[e] & 1 and VT[GV[e]] == [0, x, y]))

    if os.environ.get('ZJSON'):
        open(os.environ['ZJSON'], 'w').write(json.dumps({'VT': {str(a): b for a, b in VT.items()}, 'FT': {str(a): b for a, b in FT.items()},
                   'EN': EN, 'G': G, 'GV': {str(a): b for a, b in GV.items()}, 'n': n, 'm': m}))     # C encoder
    # ---- Lean
    L = [f"import RankNine.T2Zero\n",
         f"/-! T2 zero step for case {name} (generated by emit_t2zero.py from a CaDiCaL LRAT proof): {n} entries, "
         f"{len(VT)} variables, {len(FT)} frames. -/\n", f"namespace RankNine.T2.Z_{name}\n", "open RankNine.T2\n",
         "set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n"]
    ET.DEFS.clear()
    for nm, ent in (("VT", sorted(VT.items())), ("FT", sorted(FT.items())), ("EN", list(enumerate(EN)))):
        t = ET.bt(ent, ET.lst, "z" + nm + "_", "List ℕ"); L += ET.DEFS; ET.DEFS.clear(); L.append(f"def z{nm} : BT (List ℕ) := {t}")
    t = ET.bt(sorted(GV.items()), str, "zGV_", "ℕ"); L += ET.DEFS; ET.DEFS.clear(); L.append(f"def zGV : BT ℕ := {t}")
    # edge tables exactly as emit_t2lean.py writes ER / EC (the gluing file), so the two can be identified by `rfl`
    EDG = c['EDG']
    t = ET.bt([(e, x) for e, (x, y) in enumerate(EDG) if x != 0], str, "tER_"); L += ET.DEFS; ET.DEFS.clear(); L.append(f"def ER : BT ℕ := {t}")
    t = ET.bt([(e, y) for e, (x, y) in enumerate(EDG) if y != 0], str, "tEC_"); L += ET.DEFS; ET.DEFS.clear(); L.append(f"def EC : BT ℕ := {t}")
    L += [f"def zG : ℕ := {hex(G)}", f"def zn : ℕ := {n}", f"def zm : ℕ := {m}", f"def zs0 : ℕ := {s0L}", ""]
    chunks = [(a, min(CH, n - a)) for a in range(0, n, CH)]
    for i, (a, mm) in enumerate(chunks):
        L.append(f"theorem ze{i} : (List.range' {a} {mm}).all (entryOK zm zs0 zG zVT zFT zEN) = true := by decide +kernel")
    L.append("theorem zentries_ok : ∀ j < zn, entryOK zm zs0 zG zVT zFT zEN j = true := by\n  intro j hj")
    for i, (a, mm) in enumerate(chunks):
        if i < len(chunks) - 1:
            L.append(f"  by_cases h{i} : j < {a + mm}\n  · exact (RankNine.all_range'_iff _ {a} {mm}).1 ze{i} j (by omega) (by omega)")
        else:
            L.append(f"  exact (RankNine.all_range'_iff _ {a} {mm}).1 ze{i} j (by omega) (by simp only [zn] at hj; omega)")
    L.append(f'''
theorem zlast_ok : clOf zG (zEN.get [] (zn - 1)) = (0, 0) := by decide +kernel

theorem zedges_ok : (List.range {c['E']}).all (fun e => decide (ER.get 0 e < 104) && (decide (ER.get 0 e = EC.get 0 e) ||
    (zG.testBit (zGV.get 0 e) && zVT.get [] (zGV.get 0 e) == [0, ER.get 0 e, EC.get 0 e]))) = true := by decide +kernel

/-- zero step: every edge of the table is non-zero -/
theorem nonzero {{K : Type*}} [Field K] [CharZero K] (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (hs0 : zs0 < 104 → ∀ x, zm.testBit x = true → Mx A B x zs0 = 0)
    (hFT : ∀ fi, zFT.get [] fi ≠ [] → ExpOK A B zm (zFT.get [] fi)) :
    ∀ e < {c['E']}, Mx A B (ER.get 0 e) (EC.get 0 e) ≠ 0 :=
  t2_zero A B hdiag hmask zm zs0 zG hs0 zVT zFT zEN hFT zn zentries_ok zlast_ok (by decide) ER EC zGV {c['E']} zedges_ok

end RankNine.T2.Z_{name}
''')
    open(out, 'w').write('\n'.join(L) + '\n')
    nl = sum(1 for e in EN if e[0] == 4); nh = sum((len(e) - 2 - e[1]) // 2 for e in EN if e[0] == 4)
    print(f'ZERO OK {name} entries {n} orig {n - nl} lemmas {nl} hints {nh} vars {len(VT)} frames {len(FT)}', flush=True)


if __name__ == '__main__':
    main(*sys.argv[1:6])
