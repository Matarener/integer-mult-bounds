"""Zero step of T1 as CNF (for an LRAT certificate).  Variable code+1 means N_code = 0 (code = 104*min + max).
Clauses: every frame relation N_ta N_sa = N_tb N_sb gives (w_ta or w_sa) <-> (w_tb or w_sb) (4 clauses);
every frame-sum quadruple (sum of its 4 terms = 1) gives "not all four zero"; goal clause: some pair of the moduli
cover set is zero.  UNSAT => N != 0 on the whole cover set.  Writes DIMACS + origin JSON (relation: t,s,frame,a,b;
quadruple: t, frame).  usage: zero_cnf.py rep out.cnf out.json   (env DROP as in make_certs)"""
import sys, json, os
sys.path.insert(0, '.')
k = int(sys.argv[1]); outc, outj = sys.argv[2], sys.argv[3]
sys.argv = ['x', str(k)]
_src = open('logker.py').read(); exec(_src[:_src.index('rng = np.random')])
def code(a, b): return 104 * min(a, b) + max(a, b)
FRi = {tuple(sorted(f)): i for i, f in enumerate(FR)}
cls = []; org = []; seen = set(); qseen = set()
for F in FZ:
    Fs = set(F); fi = FRi[tuple(sorted(F))]
    for t in Z:
        if t in Fs: continue
        Tt = [f for f in F if not ORTH[t][f]]
        q = tuple(sorted(code(t, f) for f in Tt))
        if q not in qseen:
            qseen.add(q); cls.append([-(c + 1) for c in q]); org.append(['q', t, fi])
        for s in Z:
            if s <= t or s in Fs or not ORTH[t][s]: continue
            com = [f for f in Tt if not ORTH[s][f]]
            if len(com) == 2:
                a, b = com
                key = (code(t, a), code(s, a), code(t, b), code(s, b))
                if key in seen: continue
                seen.add(key)
                x, y, u, v = (c + 1 for c in key)
                for c in ([-x, u, v], [-y, u, v], [-u, x, y], [-v, x, y]):
                    cls.append(c); org.append(['r', t, s, fi, a, b])
qcov = sorted(set(c for q in qseen for c in q))
allp = sorted(code(*pr) for pr in pairs)
cov = qcov if os.environ.get("ZGOAL", "q") == "q" else allp
cls.append([c + 1 for c in cov]); org.append(['g'])
nv = 104 * 104
with open(outc, 'w') as f:
    f.write('p cnf %d %d\n' % (nv, len(cls)))
    for c in cls: f.write(' '.join(map(str, c)) + ' 0\n')
json.dump({'rep': k, 'origin': org, 'cov': cov, 'qcov': qcov}, open(outj, 'w'))
print('rep %d pairs %d quad-covered %d uncovered %d clauses %d (rel %d, quads %d)' % (k, len(allp), len(qcov),
      len(set(allp) - set(qcov)), len(cls), len(seen), len(qseen)), flush=True)
