"""Emit ../lean/RankNine/Cert/Signs<k>.lean for a type whose sign step needs a SAT certificate (the F2 elimination
of gen_signs.py does not force the magnitude bits).  Inputs: the CNF and JSON of sign_cnf.py and CaDiCaL's LRAT
proof.  Keeps only the rows, clauses and lemmas the proof needs, renumbers them, rebuilds every original clause
from the row data exactly as RankNine.sClAt does (and checks it against the CNF), replays the RUP checker
RankNine.rupRun with the unit variables, and writes packed tables.  The theorem `mags` has the same statement as
the one from emit_signs.py, so the step-5 certificate is unchanged.
Entries (7 fields): [0,row,p,0,0,0,0] quad, [1,row,p,..] relation sign parity, [2,row,p,..] relation magnitudes,
[3,..] goal, [4,lo,lo',ln,ho,ho',hn] lemma (literals Lt[lo+65536lo' ..], hints Hn as (idx, idx', unit var)).
usage: emit_signsat.py k moduli.json signs.cnf signs.json proof.lrat[.xz] out.lean [signs-out.json]"""
import sys, json, lzma
sys.path.insert(0, '.')
from p104lib import frames, IDX
FR = [tuple(IDX[q] for q in f) for f in frames()]
TAG = 10816
k = int(sys.argv[1]); dm = json.load(open(sys.argv[2])); cnfp, jp, pfp, out = sys.argv[3:7]
sjout = sys.argv[7] if len(sys.argv) > 7 else None
CH = 150
def pack(vals):
    blocks = []
    for b in range(0, len(vals), 256):
        n = 0
        for i, v in enumerate(vals[b:b + 256]):
            assert 0 <= v < 65536, v; n |= v << (16 * i)
        blocks.append(n)
    return '[' + ', '.join(hex(x) for x in blocks) + ']' if blocks else '[]'
def pcode(a, b): return 104 * min(a, b) + max(a, b)
tcode = [c for c, r, f in dm['table']]
cls = []
for line in open(cnfp):
    if line.startswith('p'): continue
    a = list(map(int, line.split())); cls.append(a[:-1])
d = json.load(open(jp)); org = d['origin']; assert len(org) == len(cls)
nK = len(d['classes']); ncls = len(cls)
lem = {}
op = lzma.open if pfp.endswith('.xz') else open
with op(pfp, 'rt') as f:
    for line in f:
        a = line.split()
        if len(a) > 1 and a[1] == 'd': continue
        i = int(a[0]); z = a.index('0', 1); lem[i] = ([int(x) for x in a[1:z]], [int(x) for x in a[z + 1:-1]])
emp = [i for i, (l, h) in lem.items() if not l]; assert emp, 'no empty clause'
need = set(); st = [min(emp)]
while st:
    i = st.pop()
    if i in need: continue
    need.add(i)
    if i > ncls: st.extend(lem[i][1])
ids = sorted(need); idx = {i: j for j, i in enumerate(ids)}
# rows used by the kept original clauses, plus one quadruple row per class (for cqOK)
uq = sorted(set(org[i - 1][1] for i in ids if i <= ncls and org[i - 1][0] == 'q'))
cq = {}
for j, q in enumerate(d['quads']): cq.setdefault(q[10], j)
assert len(cq) == nK
uq = sorted(set(uq) | set(cq.values())); qn = {j: a for a, j in enumerate(uq)}
ur = sorted(set(org[i - 1][1] for i in ids if i <= ncls and org[i - 1][0] in 'pm')); rn = {j: a for a, j in enumerate(ur)}
QR = [d['quads'][j] for j in uq]; RR = [d['rels'][j] for j in ur]
def patcl(atoms, p):   # RankNine.patCl
    P = Q = 0
    for i, a in enumerate(atoms):
        if p >> i & 1 == 0: P |= 1 << a
        else: Q |= 1 << a
    return P, Q
def qatoms(q): t, fi = q[0], q[1]; return [pcode(t, FR[fi][q[2 + i]]) for i in range(4)] + [TAG + q[10]]
def rsatoms(r): return [tcode[r[5 + i]] for i in range(4)]
def rmatoms(r): return [TAG + r[9 + i] for i in range(4)]
def mask(lits):
    P = Q = 0
    for l in lits:
        if l > 0: P |= 1 << (l - 1)
        else: Q |= 1 << (-l - 1)
    return P, Q
E = []; Lt = []; Hn = []; CL = []
for i in ids:
    if i <= ncls:
        o = org[i - 1]
        if o[0] == 'q': e = [0, qn[o[1]], o[2]]; c = patcl(qatoms(d['quads'][o[1]]), o[2])
        elif o[0] == 'p': e = [1, rn[o[1]], o[2]]; c = patcl(rsatoms(d['rels'][o[1]]), o[2])
        elif o[0] == 'm': e = [2, rn[o[1]], o[2]]; c = patcl(rmatoms(d['rels'][o[1]]), o[2])
        else: e = [3]; c = (sum(1 << (TAG + K) for K in range(nK)), 0)
        assert c == mask(cls[i - 1]), ('clause mismatch', i, o)
        E += e + [0] * (7 - len(e)); CL.append(c)
    else:
        l, h = lem[i]; lo, ho = len(Lt), len(Hn) // 3
        Lt += [2 * (abs(x) - 1) + (1 if x > 0 else 0) for x in l]
        Hn += [x for hh in h for x in (idx[hh] % 65536, idx[hh] // 65536, 0)]
        assert len(l) < 65536 and len(h) < 65536
        E += [4, lo % 65536, lo // 65536, len(l), ho % 65536, ho // 65536, len(h)]; CL.append(mask(l))
n = len(ids)
def unit(T, F, c):   # RankNine.unitStep with v = the unit variable
    rp = c[0] ^ (c[0] & F); rq = c[1] ^ (c[1] & T)
    if rp == 0 and rq == 0: return 0, T, F, 0
    if rq == 0 and rp & (rp - 1) == 0: return 1, T | rp, F, rp.bit_length() - 1
    if rp == 0 and rq & (rq - 1) == 0: return 1, T, F | rq, rq.bit_length() - 1
    return 2, T, F, 0
for j in range(n):
    if E[7 * j] != 4: continue
    ho = E[7 * j + 4] + 65536 * E[7 * j + 5]; hn = E[7 * j + 6]
    T, F = CL[j][1], CL[j][0]; ok = False
    for a in range(ho, ho + hn):
        h = Hn[3 * a] + 65536 * Hn[3 * a + 1]; assert h < j
        r, T, F, v = unit(T, F, CL[h]); Hn[3 * a + 2] = v
        if r == 0: ok = True; break
        if r == 2: break
    assert ok, ('RUP replay failed', j)
assert CL[n - 1] == (0, 0)
QS = [x for q in QR for x in q]; RS = [x for r in RR for x in r]
CQ = [qn[cq[c]] for c in range(nK)]
norig = sum(1 for i in ids if i <= ncls)
if sjout: json.dump({'rep': k, 'classes': d['classes']}, open(sjout, 'w'))
m = f'(typeMask.getD {k} 0)'
L = [f'''import RankNine.SignSat
import RankNine.Cert.Packed{k}

/-! T1 sign step for framed type {k} by a CaDiCaL LRAT certificate (generated by gen/emit_signsat.py):
{len(QR)} quadruple rows, {len(RR)} relation rows, {nK} classes, {n} entries ({norig} original clauses,
{n - norig} lemmas), {len(Hn) // 3} hints. -/

namespace RankNine.Signs{k}

open Matrix RankNine.Packed{k}

def nK : ℕ := {nK}
def nq : ℕ := {len(QR)}
def nr : ℕ := {len(RR)}
def nE : ℕ := {n}
def CR : List ℕ := {pack(d['classes'])}
def QS : List ℕ := {pack(QS)}
def RS : List ℕ := {pack(RS)}
def CQ : List ℕ := {pack(CQ)}
def E : List ℕ := {pack(E)}
def Lt : List ℕ := {pack(Lt)}
def Hn : List ℕ := {pack(Hn)}
''']
def chunked(name, pred, n, ch, var, last):
    cs = [(a, min(ch, n - a)) for a in range(0, n, ch)]
    for i, (a, mm) in enumerate(cs):
        L.append(f"theorem {name}{i} : (List.range' {a} {mm}).all ({pred}) = true := by decide +kernel\n")
    L.append(f'theorem {name}_ok : ∀ {var} < {last}, ({pred}) {var} = true := by\n  intro {var} h{var}')
    for i, (a, mm) in enumerate(cs):
        if i < len(cs) - 1:
            L.append(f"  by_cases h{i} : {var} < {a + mm}\n  · exact (all_range'_iff _ {a} {mm}).1 {name}{i} {var} (by omega) (by omega)")
        else:
            L.append(f"  exact (all_range'_iff _ {a} {mm}).1 {name}{i} {var} (by omega) (by simp only [{last}] at h{var}; omega)")
    L.append('')
chunked('c', f'cqOK {m} nQ nK T CR QS CQ nq', nK, 50, 'c', 'nK')
chunked('e', f'sEntryOK {m} nQ nK nq nr T CR QS RS E Lt Hn', n, CH, 'j', 'nE')
L.append(f'''theorem last_ok : sClAt nK T QS RS E Lt (nE - 1) = (0, 0) := by decide +kernel

/-- T1 sign step for type {k}: every quadruple class has magnitude bit 0, i.e. `N = 1/4` on its quadruples
(`RankNine.quad_quarter`). -/
theorem mags {{K : Type*}} [Field K] [CharZero K] (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0)
    (hZ : ∀ x, {m}.testBit x = true → A x ⬝ᵥ u = 0)
    (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0) :
    ∀ c < nK, magN (Nc A B (fld CR c)) = 0 :=
  signsat_sound A B u hu _ hZ hdiag hmask nQ nK nq nr T CR QS RS CQ E Lt Hn nE
    (moduli_geom A B u hu hZ hdiag hmask hcov) (fun c hc => c_ok c hc) (fun j hj => e_ok j hj) last_ok
    (by decide)

end RankNine.Signs{k}
''')
open(out, 'w').write('\n'.join(L) + '\n')
print('SIGNSAT OK type %d quads %d rels %d classes %d entries %d orig %d lemmas %d hints %d lits %d' %
      (k, len(QR), len(RR), nK, n, norig, n - norig, len(Hn) // 3, len(Lt)), flush=True)
