# V4: is the LP's fractional decoder plan realizable by an EXACT decoder within budget?
# 1. Re-solve the final LP of v4_rank_lp.py (rows = term types (W_A, W_R), columns = cliques / cores) and read the primal
#    x_t (a fractional multiset of term types whose total tariff equals the LP bound).
# 2. Take ceil(x_t) copies of every type in the support (cap COPY_CAP).  Each copy k is a rank-1 term u_k v_k^T with
#    supp u_k inside the ports of planes(W_A), supp v_k inside the ports of planes(W_R); it may also stay unused.
# 3. CP-SAT: total tariff of used copies <= BUDGET; every fixed mask entry (p,q) must equal target, with a slack bit
#    allowed per entry; minimise the number of violated entries.  0 violations = a real decoder within budget.
# Every reported solution is re-verified from scratch (mask + true tariffs of the actual supports).
import json, math, os, pickle, sys, time
import numpy as np, scipy.optimize as so, scipy.sparse as sp
from v4lib import *
MODE = os.environ.get('V4_MODE', 'budget')   # budget: min violations s.t. cost<=BUDGET ; repair: min cost + 2*violations
BUDGET = int(os.environ.get('V4_BUDGET', '163')); TL = float(os.environ.get('V4_TL', '10800')); COPY_CAP = 4
T0 = time.time()
def log(*a): print(time.strftime('%H:%M:%S'), '%6.0fs' % (time.time() - T0), *a, flush=True)
labels, pairs = load_geometry(); planes = [(labels[a], labels[b]) for a, b in pairs]; NP = len(planes); NPORT = 112
E = [0] * NPORT
for i, (a, b) in enumerate(pairs): E[a] = i; E[b] = i
ORTH = [[i != j and all(dot(x, y) == 0 for x in planes[i] for y in planes[j]) for j in range(NP)] for i in range(NP)]
d = pickle.load(open('v4_spans.pkl', 'rb')); spans, inside = d['spans'], d['inside']; n = len(spans)
st = pickle.load(open(sys.argv[1] if len(sys.argv) > 1 else 'v4_rank_state.pkl', 'rb'))
rowsT, cols = st['rows'], st['cols']
colsL = sorted(cols.items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))
imask = np.array([sum(1 << v for v in ins) for ins in inside], dtype=np.uint64)
xm = np.array([sum(1 << v for v in X) for X, _ in colsL], dtype=np.uint64)
ra = imask[[a for a, r in rowsT]]; rr = imask[[r for a, r in rowsT]]
Tm = np.zeros((len(rowsT), len(colsL)), dtype=bool)
for c0 in range(0, len(colsL), 500):
    Tm[:, c0:c0+500] = ((ra[:, None] & xm[None, c0:c0+500]) != 0) & ((rr[:, None] & xm[None, c0:c0+500]) != 0)
A = sp.csr_matrix(Tm.astype(np.float64)); del Tm
rhs = np.array([float(pair_rank(spans[a], spans[r])) for a, r in rowsT]); obj = np.array([v for _, (v, _) in colsL])
res = so.linprog(-obj, A_ub=A, b_ub=rhs, bounds=(0, None), method='highs'); assert res.status == 0
x = -res.ineqlin.marginals; sup = [t for t in np.argsort(-x) if x[t] > 1e-7]
log('LP value %.4f, primal cost %.4f, support %d types' % (-res.fun, float(x @ rhs), len(sup)))
plan = [{'a': int(rowsT[t][0]), 'r': int(rowsT[t][1]), 'x': float(x[t]), 'tariff': int(rhs[t]),
         'A': inside[rowsT[t][0]], 'R': inside[rowsT[t][1]]} for t in sup]
json.dump(plan, open('v4_realize_plan.json', 'w'), indent=0)
from collections import Counter
log('support by (tariff,|A|,|R|):', sorted(Counter((p['tariff'], len(p['A']), len(p['R'])) for p in plan).items())[:40])

from ortools.sat.python import cp_model
copies = []
for p in plan:
    for _ in range(min(COPY_CAP, max(1, math.ceil(p['x'] - 1e-6)))): copies.append(p)
EXTRA = int(os.environ.get('V4_EXTRA', '0'))
if EXTRA:
    # widen the term pool: symmetric terms (A = R = planes of W) on the spans with the lowest tariff per plane
    have = {(c['a'], c['r']) for c in plan}
    cand = []
    for i in range(n):
        if len(inside[i]) >= 2 and (i, i) not in have:
            cand.append((pair_rank(spans[i], spans[i]) / len(inside[i]), i))
    cand.sort()
    for _, i in cand[:EXTRA]:
        t = pair_rank(spans[i], spans[i]); pe = {'a': i, 'r': i, 'x': 0.0, 'tariff': int(t), 'A': inside[i], 'R': inside[i]}
        copies += [pe, pe]
    log('extra symmetric types added:', min(EXTRA, len(cand)), 'best tariff/plane', round(cand[0][0], 3) if cand else None)
log('copies', len(copies), 'max possible cost', sum(p['tariff'] for p in copies), 'budget', BUDGET)
PA = [[q for q in range(NPORT) if E[q] in set(c['A'])] for c in copies]
PR = [[q for q in range(NPORT) if E[q] in set(c['R'])] for c in copies]
md = cp_model.CpModel()
u = [{p: md.NewBoolVar('') for p in PA[k]} for k in range(len(copies))]
v = [{q: md.NewBoolVar('') for q in PR[k]} for k in range(len(copies))]
used = [md.NewBoolVar('') for _ in copies]
for k in range(len(copies)):
    for b in list(u[k].values()) + list(v[k].values()): md.AddImplication(b, used[k])
costexpr = sum(c['tariff'] * used[k] for k, c in enumerate(copies))
if MODE == 'budget': md.Add(costexpr <= BUDGET)
fixed = [(p, q, int(p == q)) for p in range(NPORT) for q in range(NPORT) if p == q or E[p] == E[q] or not ORTH[E[p]][E[q]]]
one = md.NewBoolVar(''); md.Add(one == 1)
slack = []; nprod = 0
byA = [set(x) for x in PA]; byR = [set(x) for x in PR]
for (p, q, t) in fixed:
    ks = [k for k in range(len(copies)) if p in byA[k] and q in byR[k]]
    prods = []
    for k in ks:
        z = md.NewBoolVar(''); md.AddMultiplicationEquality(z, [u[k][p], v[k][q]]); prods.append(z)
    nprod += len(prods)
    s = md.NewBoolVar(''); slack.append(s)
    md.AddBoolXOr(prods + [s] + ([] if t else [one]))
log('model: fixed entries', len(fixed), 'products', nprod)
if MODE == 'repair':
    # every violated cell can be fixed by one extra rank-1 term of tariff <= 2 -> objective is an upper bound on an exact decoder
    CAP = os.environ.get('V4_CAP')
    if CAP: md.Add(costexpr + 2 * sum(slack) <= int(CAP))
    HINT = os.environ.get('V4_HINT')
    if HINT and os.path.exists(HINT):
        # warm start: map each term of a known solution to a compatible unused copy
        ht = [(int(a, 16), int(b, 16)) for a, b in json.load(open(HINT))['terms']]
        free = list(range(len(copies))); hu = {}; nmap = 0
        for U, V in ht:
            for k in free:
                if all(p in u[k] for p in range(NPORT) if U >> p & 1) and all(q in v[k] for q in range(NPORT) if V >> q & 1):
                    hu[k] = (U, V); free.remove(k); nmap += 1; break
        for k in range(len(copies)):
            U, V = hu.get(k, (0, 0))
            for p_, var in u[k].items(): md.AddHint(var, (U >> p_) & 1)
            for q_, var in v[k].items(): md.AddHint(var, (V >> q_) & 1)
        log('hint: mapped %d of %d known terms onto copies' % (nmap, len(ht)))
    md.Minimize(costexpr + 2 * sum(slack))
else:
    md.Minimize(sum(slack))
class CB(cp_model.CpSolverSolutionCallback):
    def __init__(s): super().__init__(); s.best = None
    def on_solution_callback(s):
        val = int(s.ObjectiveValue()); nv = sum(s.Value(x) for x in slack)
        log('solution: objective %d (violated cells %d, bound %d)' % (val, nv, int(s.BestObjectiveBound())))
        terms = []
        for k in range(len(copies)):
            U = sum(1 << p for p in PA[k] if s.Value(u[k][p])); V = sum(1 << q for q in PR[k] if s.Value(v[k][q]))
            if U and V: terms.append([hex(U), hex(V)])
        json.dump({'objective': val, 'violated': nv, 'terms': terms}, open('v4_realize_best.json', 'w'))
        s.n = getattr(s, 'n', 0) + 1
        json.dump({'objective': val, 'violated': nv, 'terms': terms}, open('v4_realize_sol_%03d_obj%d_v%d.json' % (s.n, val, nv), 'w'))
solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = TL; solver.parameters.num_workers = 4
stt = solver.Solve(md, CB())
log('status', solver.StatusName(stt), 'objective', solver.ObjectiveValue() if stt in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
    'bound', solver.BestObjectiveBound())
out = {'budget': BUDGET, 'status': solver.StatusName(stt), 'lp_value': float(-res.fun), 'copies': len(copies)}
if stt in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    terms = []
    for k in range(len(copies)):
        U = sum(1 << p for p in PA[k] if solver.Value(u[k][p])); V = sum(1 << q for q in PR[k] if solver.Value(v[k][q]))
        if U and V: terms.append((U, V))
    rows = [0] * NPORT
    for U, V in terms:
        for p in range(NPORT):
            if U >> p & 1: rows[p] ^= V
    viol = sum(1 for p, q, t in fixed if (rows[p] >> q & 1) != t)
    pm = lambda w: [i for i in range(NP) if any(w >> pp & 1 for pp in (pairs[i][0], pairs[i][1]))]
    sp_ = lambda D: span([vv for i in D for vv in planes[i]])
    cost = sum(pair_rank(sp_(pm(U)), sp_(pm(V))) for U, V in terms)
    out.update(violations_verified=viol, true_cost=cost, terms=[[hex(U), hex(V)] for U, V in terms],
               lower_bound_violations=solver.BestObjectiveBound())
    log('VERIFIED: violations %d, true cost %d, terms %d' % (viol, cost, len(terms)))
    if viol == 0: log('*** EXACT DECODER WITHIN BUDGET FOUND: cost', cost)
json.dump(out, open('v4_realize_result.json', 'w'), indent=1)
print('mode', MODE, flush=True)
