"""Generate the search certificate (pre-order tree) for one part of the root options.  Apache-2.0.
usage: gen8.py PORTS.json PART NPARTS OUT [MAXDEPTH]
Tokens (one per line): 'n j' internal node branching on port j; 'd j' dead node (port j has no consistent canonical
option); 's' complete solution; 'x' (only with MAXDEPTH, for smoke tests) node cut at depth MAXDEPTH."""
import json, sys, time
from code8 import Model
ports = json.load(open(sys.argv[1])); PART, NP = int(sys.argv[2]), int(sys.argv[3]); OUT = open(sys.argv[4], 'w')
MAXD = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
M = Model(ports); t0 = time.time(); last = [t0]; cnt = [0, 0, 0]; maxdepth = [0]
print('START part', PART, 'of', NP, 'variables', M.NV, flush=True)
# wrap apply/undo with explicit marks
def rec2(d, rest, cls):
    if time.time() - last[0] > 60:
        last[0] = time.time()
        print('progress %.0fs nodes %d dead %d solutions %d maxdepth %d' % (time.time() - t0, cnt[0], cnt[1], cnt[2], maxdepth[0]), flush=True); OUT.flush()
    maxdepth[0] = max(maxdepth[0], d)
    if not rest:
        OUT.write('s\n'); cnt[2] += 1; M.solution()
        print('SOLUTION at %.0fs' % (time.time() - t0), flush=True); return
    if d >= MAXD:
        OUT.write('x\n'); return
    j, opts = M.choose(rest, cls)
    if not opts:
        OUT.write('d %d\n' % j); cnt[1] += 1; return
    OUT.write('n %d\n' % j); cnt[0] += 1
    if d == 0:
        opts = [c for i, c in enumerate(opts) if i % NP == PART]
        print('root port', j, 'options in this part', len(opts), flush=True)
    for c in opts:
        mk = M.mark(); assert M.apply(j, c)
        rec2(d + 1, rest - {j}, M.merged(j, c, cls))
        M.undo(mk)
rec2(0, frozenset(M.others), {t: i for i, t in enumerate(M.T)})
OUT.close()
print('DONE part %d of %d internal %d dead %d solutions %d maxdepth %d time %.0fs' % (PART, NP, cnt[0], cnt[1], cnt[2], maxdepth[0], time.time() - t0), flush=True)
