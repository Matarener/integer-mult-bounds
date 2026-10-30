"""GENUPGRADE wires, exactness test (~25 s, venv python -B; no env at import).
1. purex2 --lawprune --dyfix on the GENPIPE2 o1 word = r104 content sha a691733502945e0a (a solving config is untouched)
2. purex2 --lawprune on the gauge-0 L2 config (built here from route_b) solves at .0030132035411 (drop 259)
3. alignbuild/hoist.py on IOROOT2 out_r2b -> kappa .0031283932032711 (r245g) LEGAL; on r245g -> 0 sites, no file
usage: tests/genupgrade_test.py"""
import sys, os, subprocess, gzip, hashlib, re, tempfile
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); TK = W; PY = sys.executable
OUT = W + '/ext/GENUPGRADE/testwork'

def sh(cmd, cwd=OUT):
    env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
    p = subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True); return p.returncode, p.stdout

def main():
    os.makedirs(OUT, exist_ok=True); fails = 0
    def ok(c, m): nonlocal fails; print(('PASS ' if c else 'FAIL ') + m, flush=True); fails += (not c)
    o1 = W + '/ext/GENPIPE2/run/o1.json.gz'
    rc, t = sh([PY, '-B', TK + '/gen2/purex2.py', o1, OUT + '/r104.json.gz', '--dims', '4,8', '--xstops', '--lawprune', '--dyfix'])
    ok(rc == 0 and hashlib.sha256(gzip.open(OUT + '/r104.json.gz').read()).hexdigest()[:16] == 'a691733502945e0a', 'lawprune identity on r104')
    rc, t = sh([PY, '-B', TK + '/gen2/route_b.py', '0', OUT + '/g0o1.json.gz', '--dirs', '51,30,45,120,85,75,102', '--gauge', '0'])
    rc, t = sh([PY, '-B', TK + '/gen2/purex2.py', OUT + '/g0o1.json.gz', OUT + '/g0px.json.gz', '--dims', '4,8', '--xstops', '--lawprune'])
    ok(rc == 0 and 'class L2_exit drop [259]' in t and 'kappa 0.0030132035411' in t, 'lawprune L2 drop 259 -> .0030132035411')
    rc, t = sh([PY, '-B', TK + '/alignbuild/hoist.py', W + '/ext/IOROOT2/out_r2b.json.gz', OUT + '/r2b_h.json.gz'])
    ok(rc == 0 and 'kappa 0.003128393203271' in t.splitlines()[-1], 'hoist r2b -> r245g kappa')
    if os.path.exists(OUT + '/r245_h.json.gz'): os.remove(OUT + '/r245_h.json.gz')
    rc, t = sh([PY, '-B', TK + '/alignbuild/hoist.py', W + '/ext/IOROOT2/CANDIDATE-IOROOT2_6030_r245g.json.gz', OUT + '/r245_h.json.gz'])
    ok(rc == 0 and 'accepted 0 sites' in t and not os.path.exists(OUT + '/r245_h.json.gz'), 'hoist r245g: 0 sites, unchanged')
    print('ALL PASS' if not fails else '%d FAILED' % fails); return 1 if fails else 0

if __name__ == '__main__': sys.exit(main())
