"""Emit ../lean/RankNine/Cert/Glue<k>.lean (T3.4 gluing data, RankNine.GlueData) for framed type k.
O' = lines outside the reduced Z minus the bad line u (special types); bad = pairs in O' without a pair
certificate; T = pair certificates for all other pairs.  Replays pcOK / coverOK / matchOK / fiveOK in Python.
usage: emit_glue.py k out.lean [log.txt]"""
import sys, json, itertools, time
sys.path.insert(0, '.')
from p104lib import ORTH, P, RT, N as NL
from rank_cert import cert, rootv, check
k = int(sys.argv[1]); out = sys.argv[2]
DROP = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
T0 = time.time()
m = int(reps[k]['mask']); Z = [i for i in range(NL) if m >> i & 1]
if k in DROP: Z = [i for i in Z if i != DROP[k]]
Zs = set(Z); zm = sum(1 << x for x in Z)
O = [v for v in range(NL) if v not in Zs]
def dot(a, b): return sum(x * y for x, y in zip(rootv(a), rootv(b)))
def G3(a, b, c):
    x, y, z = dot(a, b), dot(a, c), dot(b, c)
    return 5832 + 2 * x * y * z - 18 * (x * x + y * y + z * z)
badl = []; LT = []
for v in O:
    rv = rootv(v); k0 = next(i for i in range(9) if rv[i])
    c = cert([x for x in Z if ORTH[x][v]], [k0])
    if c is None: badl.append(v); continue
    assert check(*c) and all(x in Zs and dot(v, x) == 0 for x in c[0])
    LT.append((v, k0) + tuple(c))
assert len(badl) <= 1, badl
OL = [v for v in O if v not in badl]                       # line certificates (columns, dead rows)
OLs = set(OL); sm = zm | sum(1 << x for x in OL)            # pair-certificate mask: Z and the gramm columns
Op = [v for v in O if not (k in DROP and v == DROP[k])]     # glued rows (the dead DROP line is never live)
T = []; bad = []
for a in range(len(Op)):
    for b in range(a + 1, len(Op)):
        v, w = Op[a], Op[b]; rv, rw = rootv(v), rootv(w)
        k0, k1 = next((i, j) for i in range(9) for j in range(i + 1, 9) if rv[i] * rw[j] - rv[j] * rw[i])
        c = cert([x for x in Z + OL if ORTH[x][v] and ORTH[x][w]], [k0, k1])
        if c is None: bad.append((v, w)); continue
        X, N, No, D, pm = c
        assert check(X, N, No, D, pm) and all((x in Zs or x in OLs) and dot(v, x) == 0 and dot(w, x) == 0 for x in X)
        T.append((v, w, k0, k1, X, N, No, D, pm))
SP = None
if badl:
    u = badl[0]; ku = next(i for i in range(9) if rootv(u)[i]); X0 = [x for x in Z if ORTH[x][u]]
    good = [(s_, cert(X0 + [s_], [ku])) for s_ in OL if ORTH[s_][u]]
    good = [(s_, c) for s_, c in good if c is not None]
    SP = next((u, ku, s1, c1, s2, c2) for s1, c1 in good for s2, c2 in good if s1 < s2 and ORTH[s1][s2])
    for s_, c in ((SP[2], SP[3]), (SP[4], SP[5])):
        assert check(*c) and all((x in Zs or x == s_) and dot(u, x) == 0 for x in c[0])
# replay coverOK, matchOK, fiveOK
isb = lambda x, y: (x, y) in bad or (y, x) in bad
deg = {}
for p in bad:
    for x in p: deg[x] = deg.get(x, 0) + 1
assert max(deg.values(), default=0) <= 1, 'matching fails'
def planB(a, a2, b, b2, e):
    t = lambda x, y: G3(x, y, e) != 0
    return (t(a, b) and t(a2, b)) or (t(a, b) and t(a, b2)) or (t(a2, b2) and t(a2, b)) or (t(a2, b2) and t(a, b2))
n5 = 0
for p in bad:
    for q in bad:
        for e in Op:
            if len({p[0], p[1], q[0], q[1], e}) < 5: continue
            n5 += 1; assert planB(p[0], p[1], q[0], q[1], e), ('plan', p, q, e)
L = lambda xs: '[' + ', '.join(str(x) for x in xs) + ']'
ents = ',\n  '.join(f'⟨{v}, {w}, {k0}, {k1}, ⟨{L(X)}, [{", ".join(L(r) for r in N)}], {L(No)}, {D}, {pm}⟩⟩'
                   for v, w, k0, k1, X, N, No, D, pm in T)
lents = ',\n  '.join(f'({v}, {k0}, ⟨{L(X)}, [{", ".join(L(r) for r in N)}], {L(No)}, {D}, {pm}⟩)'
                    for v, k0, X, N, No, D, pm in LT)
def rc(c):
    X, N, No, D, pm = c
    return f'⟨{L(X)}, [{", ".join(L(r) for r in N)}], {L(No)}, {D}, {pm}⟩'
sptxt = ''
if SP:
    u, ku, s1, c1, s2, c2 = SP
    sptxt = f'''
/-! special line `u = {u}`: its dead row is pinned by the orthogonal columns {s1} ⊥ {s2} -/
def Cs : RCert := {rc(c1)}
def Ct : RCert := {rc(c2)}
theorem hCs : lcxOK zm {s1} {u} {ku} Cs = true := by decide +kernel
theorem hCt : lcxOK zm {s2} {u} {ku} Ct = true := by decide +kernel
theorem hst : dot {s1} {s2} = 0 ∧ dot {u} {s1} = 0 ∧ dot {u} {s2} = 0 ∧ ({s1} : ℕ) ∈ OL ∧ ({s2} : ℕ) ∈ OL := by
  decide +kernel
theorem hSP : SpecialH zm U OL := fun _ =>
  ⟨{s1}, {s2}, {ku}, {ku}, Cs, Ct, by norm_num, by norm_num, hst.1, hst.2.1, hst.2.2.1, hst.2.2.2.1, hst.2.2.2.2, hCs, hCt⟩
'''
else:
    sptxt = '''
theorem hSP : SpecialH zm U OL := fun h => absurd h (by norm_num [U])
'''
CH = 80
def chunked(name, typ, items):
    parts = [items[i:i + CH] for i in range(0, len(items), CH)] or [[]]
    out = [f'def {name}{i} : List ({typ}) := [\n  ' + ',\n  '.join(c) + ']' for i, c in enumerate(parts)]
    out.append(f'def {name} : List ({typ}) := ' + ' ++ '.join(f'{name}{i}' for i in range(len(parts))))
    return '\n'.join(out)
tdefs = chunked('T', 'PCert', ents.split(',\n  ') if T else []) + '\n' + \
    chunked('LT', 'ℕ × ℕ × RCert', lents.split(',\n  ') if LT else [])
src = f'''import RankNine.T3

/-! T3.4 gluing data for framed type {k} (generated by gen/emit_glue.py): |O'| = {len(Op)}, bad line {badl},
{len(bad)} bad pairs, {len(T)} pair certificates (mask Z ∪ OL), {len(LT)} line certificates, {n5} five-sets with two bad pairs. -/

namespace RankNine.Glue{k}

open Matrix

def zm : ℕ := {zm}
def sm : ℕ := {sm}
def OL : List ℕ := {L(OL)}
def O : List ℕ := {L(Op)}
def bad : List (ℕ × ℕ) := [{", ".join(f"({a}, {b})" for a, b in bad)}]
{tdefs}

theorem hO : O.all (· < 104) = true := by decide +kernel
theorem hT : T.all (pcOK sm) = true := by decide +kernel
theorem hc : coverOK O bad T = true := by decide +kernel
theorem hm : matchOK O bad = true := by decide +kernel
theorem hf : fiveOK O bad = true := by decide +kernel
theorem hL : lineOK zm OL LT = true := by decide +kernel
theorem hz : zm < 2 ^ 104 := by decide +kernel
theorem hsm : (List.range 104).all (fun s => !sm.testBit s || zm.testBit s || decide (s ∈ OL)) = true := by
  decide +kernel
theorem hsmlt : sm < 2 ^ 104 := by decide +kernel
theorem hOL : OL.all (· < 104) = true := by decide +kernel
def U : ℕ := {SP[0] if SP else 104}
theorem hcov : (List.range 104).all (fun v => zm.testBit v || decide (v ∈ OL) || v == U) = true := by
  decide +kernel
{sptxt}

/-- T3.3 for type {k}: a vector orthogonal to `𝟙` and to `ρ(Z ∩ O_v)` (`v ∈ O`) is a multiple of `ρ_v` -/
theorem line {{K : Type*}} [Field K] [CharZero K] {{v : ℕ}} (hv : v ∈ OL) (d : Fin 9 → K)
    (h1 : d ⬝ᵥ vK K ones9L = 0) (hd : ∀ s, zm.testBit s = true → dot v s = 0 → d ⬝ᵥ rho K s = 0) :
    ∃ a : K, d = a • rho K v :=
  line_of_data hL hv d h1 hd

/-- T3.4 for type {k}: five live rows outside `Z` (and off the bad line) force one centre for all of them -/
theorem glue {{K : Type*}} [Field K] [CharZero K] {{h : ℕ → Fin 9 → K}} {{τ : ℕ → K}} {{L : ℕ → Prop}}
    (R : RowHyp sm h τ (fun v => v ∈ O ∧ L v))
    (five : ∃ x1 x2 x3 x4 x5, (x1 ∈ O ∧ L x1) ∧ (x2 ∈ O ∧ L x2) ∧ (x3 ∈ O ∧ L x3) ∧ (x4 ∈ O ∧ L x4) ∧
      (x5 ∈ O ∧ L x5) ∧ dist5B x1 x2 x3 x4 x5 = true) :
    ∃ Λ, ∀ v, v ∈ O → L v → Gl h Λ v :=
  glue_of_data hO hT hc hm hf R five

end RankNine.Glue{k}
'''
open(out, 'w').write(src)
msg = f'[{time.time() - T0:6.1f}s] type {k} |Z| {len(Z)} |O| {len(O)} badl {badl} bad {len(bad)} certs {len(T)} five {n5} bytes {len(src)}'
print(msg, flush=True)
if len(sys.argv) > 3: open(sys.argv[3], 'a').write(msg + '\n')
