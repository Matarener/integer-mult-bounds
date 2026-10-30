"""SIGGEN test (~15 s): (1) generic contract floor on r245g reproduces SIGFLOOR's gap 5.27 R0 (449/226 at frame 709);
(2) siggen exact re-solve of one root family (feeds + reads) on W6167 returns W6167's kappa exactly; (3) feedplan runs (CP-SAT OPTIMAL) on p1o."""
import os
import sys, subprocess
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); SG = W + '/ext/SIGGEN'; PY = sys.executable
sys.path.insert(0, SG)
import contract as C
fails = 0
def check(name, ok, info=''):
    global fails
    print(('PASS ' if ok else 'FAIL ') + name, info); fails += (not ok)
w = C.load(W + '/ext/IOROOT2/CANDIDATE-IOROOT2_6030_r245g.json.gz'); c, g = C.build(w); F = C.floor(c, g)
gap = sum(x['actual'] - x['floor'] for x in F.values())
check('contract floor r245g gap 5.27', abs(gap - 5.274) < 0.01 and len(c['roots']) == 8, '%.3f, %d carriers' % (gap, len(F)))
out = SG + '/out/test_W6167_g5.json.gz'
p = subprocess.run([PY, '-B', SG + '/siggen.py', W + '/ext/FRONTIER/W6167.json.gz', out, '--roots', '5', '--workdir', SG + '/out/test_steps'], capture_output=True, text=True)
fin = [l for l in p.stdout.splitlines() if l.startswith('FINAL')]
check('siggen W6167 family 5 exact', bool(fin) and 'kappa 0.003128652015904' in fin[0], fin[0][:120] if fin else p.stdout[-300:])
q = subprocess.run([PY, '-B', SG + '/feedplan.py', W + '/ext/SKELGEN/runs/p1o.json.gz', '--tl', '20'], capture_output=True, text=True)
last = (q.stdout.strip().splitlines() or [''])[-1]
check('feedplan p1o 634.61 OPTIMAL', '634.61' in last and 'OPTIMAL' in last, last)
print('ALL PASS' if not fails else '%d FAILED' % fails)
sys.exit(1 if fails else 0)
