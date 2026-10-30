"""R16 lever F screen: can b = Z Q Y (#5415) be bought with few paid rank-one jobs?
b_k = sum_j M_kj/2 Km_k^-1 Kp_j Q Y_j. If Km_k^-1 Kp_j conjugates Q to one common operator per mode
(or per class), b costs one H1 per (mode, class) instead of 112 H1 (Q on every Y_j).
Uses the repository's exact Clifford evaluator (tableau + absolute zero-state phase)."""
import json, sys, importlib.util
from pathlib import Path
from collections import Counter, defaultdict
ROOT = Path.home()/'imb-r16'
cp = ROOT/'research/coded-native-caller/clifford_exact.py'
spec = importlib.util.spec_from_file_location('ce', cp); ce = importlib.util.module_from_spec(spec); sys.modules['ce'] = ce; spec.loader.exec_module(ce)
normal = json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
prov = json.loads((ROOT/'research/native-rank8-helper-provider/PROVIDER.json').read_text())
M = normal['mode_columns']
def literal(word):
    op = ce.ident(9)
    for e in word:
        if e[0] == 'P': part = ce.perm(9, tuple(e[1]))
        elif e[0] == 'D': part = ce.diag(9, tuple(e[1]), tuple(e[2]))
        elif e[0] == 'X': part = ce.xgate(9, e[1])
        elif e[0] == 'phase': part = ce.Op(9, ce.identity(9), [('phase', e[1])])
        else: raise ValueError(e)
        op = op.then(part)
    return op
def equal(a, b): return a.tab == b.tab and a.zero_state() == b.zero_state()
def key(op): return (op.tab, tuple(map(tuple, op.zero_state()[0])) if False else repr(op.zero_state()))
canonical = json.loads(__import__('gzip').decompress((ROOT/'research/native-center-free-code/SOURCE-WORD.json.gz').read_bytes()))['canonical']
R = ce.canonical_frame(9, canonical['frames'][1])
Dop = ce.fourier(9, range(1, 9))
Q1 = Dop.adjoint().then(R); Q2 = R.then(Dop.adjoint())
print('Q well defined (D,Q commute in R):', equal(Q1, Q2), ' Q rank', ce.rank([x for x, _, _ in Q1.tab[9:]]))
Q = Q1
Kp = [literal(r['K_word']) for r in normal['ports']]
Km = [None]*8
for rec in prov['mode_boundaries']:
    Km[rec['mode']] = literal(rec['input_K']['literal_word'])
print('Kp commute with Q:', sum(equal(k.then(Q), Q.then(k)) for k in Kp), '/112;  with D:', sum(equal(k.then(Dop), Dop.then(k)) for k in Kp))
print('Km commute with Q:', sum(equal(k.then(Q), Q.then(k)) for k in Km), '/8;  with D:', sum(equal(k.then(Dop), Dop.then(k)) for k in Km))
# conjugate classes per mode: C = Kp_j then Km_k^-1 (operator applied to Y_j); need C Q C^-1
total = 0; per = []
tabcls = Counter()
for k in range(8):
    cls = defaultdict(list)
    for j in range(112):
        if not M[k][j]: continue
        C = Kp[j].then(Km[k].adjoint())
        conj = C.adjoint().then(Q).then(C)   # operator equal to C Q C^-1 in 'then' order
        cls[(conj.tab, repr(conj.zero_state()))].append(j)
        tabcls[conj.tab] += 1
    per.append(len(cls)); total += len(cls)
print('distinct conjugates of Q per mode:', per, 'total', total, '(break-even ~55 + 8 restore)')
print('distinct conjugate tableaux overall:', len(tabcls))
# port-level: distinct Kp Q Kp^-1 (sharing Q Y_j across modes)
pc = Counter((lambda c: (c.tab, repr(c.zero_state())))(k.adjoint().then(Q).then(k)) for k in Kp)
print('distinct port conjugates Kp^-1 Q Kp:', len(pc))
# coarser: Q_a, Q_b groupable (common left monomial E, right monomials free) iff Q_b^-1 Q_a is monomial
def rk(op): return ce.rank([x for x, _, _ in op.tab[9:]])
tot2 = 0; per2 = []
for k in range(8):
    reps = []
    for j in range(112):
        if not M[k][j]: continue
        C = Kp[j].then(Km[k].adjoint()); conj = C.adjoint().then(Q).then(C)
        for r in reps:
            if rk(conj.then(r.adjoint())) == 0: break
        else: reps.append(conj)
    per2.append(len(reps)); tot2 += len(reps)
print('monomial-coset classes per mode:', per2, 'total', tot2)
reps = []
for j in range(112):
    conj = Kp[j].adjoint().then(Q).then(Kp[j])
    for r in reps:
        if rk(conj.then(r.adjoint())) == 0: break
    else: reps.append(conj)
print('port-level monomial-coset classes (shared over modes):', len(reps))
# other composition order (left/right coset) and controls
for name, f in (('left', lambda a, r: r.adjoint().then(a)), ('right', lambda a, r: a.then(r.adjoint()))):
    reps = []
    for j in range(112):
        conj = Kp[j].adjoint().then(Q).then(Kp[j])
        if not any(rk(f(conj, r)) == 0 for r in reps): reps.append(conj)
    print(name, 'coset classes over ports:', len(reps))
print('control rank(Q Q^-1)=', rk(Q.then(Q.adjoint())), ' rank(Q)=', rk(Q), ' rank(R)=', rk(R), ' rank(D)=', rk(Dop))
cj = [Kp[j].adjoint().then(Q).then(Kp[j]) for j in range(112)]
print('rank histogram of pairwise Q_a Q_b^-1 (first 20 ports):', Counter(rk(cj[a].then(cj[b].adjoint())) for a in range(20) for b in range(20) if a != b))
