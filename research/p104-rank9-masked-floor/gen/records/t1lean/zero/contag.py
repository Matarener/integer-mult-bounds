"""T1 zero step by contagion (§13.25 stage 2) on the CNF of cnf8.py, search with pysat propagate (C):
for each zero variable z_v: assume z_v; add z_w whenever {units, z_v, .., not z_w} propagates to a conflict; success when
{units, z_v, w..} conflicts; then not z_v becomes a unit; passes to a fixpoint.  Writes the chains (JSON) for the LRAT
reconstruction (lrat8.py).  usage: python3 t1lean/zero/contag.py k [out.json]"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnf8
from pysat.solvers import Minisat22
k = int(sys.argv[1]); t0 = time.time()
VT, VID, cls, org, R, FZ, m = cnf8.build(k)
zs = [i + 1 for i, v in enumerate(VT) if v[0] == 'z']
if len(sys.argv) > 3:      # only the zero variables of the edge table (entries between two lines in no inside frame
    cE = json.load(open(sys.argv[3]))['EDG']                    # are not in it and cannot be refuted anyway)
    gl = {VID[('z', x, y)] for x, y in cE if x != y}; zs = [v for v in zs if v in gl]
sol = Minisat22(bootstrap_with=cls)
units = []; chains = []; zset = set(zs)
def prop(a):     # refuted units are level-0 clauses of the solver (added as found), so only the new part is propagated
    st, imp = sol.propagate(assumptions=a[len(units):]); return st, imp
def unit(v):
    units.append(-v); sol.add_clause([-v])
rounds = 0
while True:
    rounds += 1; changed = False; stuck = 0
    done = {-u for u in units}
    for v in zs:
        if v in done: continue
        st, imp = prop(units + [v])
        if not st: chains.append([v]); unit(v); done.add(v); changed = True; continue
        if -v in imp: continue
        S = [v]; ok = False
        while not ok:
            st, imp = prop(units + S); assigned = {abs(x) for x in imp}
            added = 0
            for w in zs:
                if w in assigned: continue
                st2, _ = prop(units + S + [-w])
                if not st2:
                    S.append(w); added += 1
                    st3, imp = prop(units + S)
                    if not st3: ok = True; break
                    assigned = {abs(x) for x in imp}
            if not added: break
        if ok: chains.append(S); unit(v); done.add(v); changed = True
        else: stuck += 1
    print('pass', rounds, 'units', len(units), 'stuck', stuck, '%.0fs' % (time.time() - t0), flush=True)
    if not changed: break
inv = {i + 1: tuple(v) for i, v in enumerate(VT)}
und = [inv[v][1:] for v in zs if -v not in set(units)]
print('T1Z %d vars %d clauses %d zvars %d refuted %d unrefuted %d passes %d chains-lens max %d %.0fs' % (
    k, len(VT), len(cls), len(zs), len(units), len(und), rounds, max((len(c) for c in chains), default=0), time.time() - t0), flush=True)
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chains-%d.json' % k)
json.dump({'k': k, 'chains': chains, 'unrefuted': und}, open(out, 'w'))
