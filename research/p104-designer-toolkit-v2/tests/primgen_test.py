"""PRIMGEN fan-out landing test (~20 s, venv python -B; no env at import).  Model level only (no word is built):
1. fanland base model on gen2's b0 config (seed 0, D3 dirs) = route_b model R0 9049.065 (bit-identical bottom + edges.land)
2. exact greedy (O1 relaxed): model R0 8980.89 (delta -68.17, 26 direct landings); the realised word delta is EXACT -68.170732 (module docstring sec 2)
3. purex-aware on the o1 config (seed 0, order dirs): every Y's Q ender worth 3.14, 0 improving sites (the lever = purex's ender at equal tax)
usage: tests/primgen_test.py"""
import sys, os, subprocess
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); PY = sys.executable; PG = W + '/ext/PRIMGEN'

def sh(args):
    env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
    p = subprocess.run([PY, '-B', PG + '/fanland.py'] + args, cwd=PG, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True); return p.returncode, p.stdout

def main():
    fails = 0
    def ok(c, m): nonlocal fails; print(('PASS ' if c else 'FAIL ') + m, flush=True); fails += (not c)
    rc, t = sh(['--seed', '0'])
    ok(rc == 0 and 'base model R0 9049.07' in t, 'b0 base model R0 9049.07')
    ok(rc == 0 and 'FANLAND model R0 8980.89 (delta -68.17)' in t and "'direct_landings': 26" in t, 'b0 greedy -68.17, 26 direct landings')
    rc, t = sh(['--seed', '0', '--dirs', '51,30,45,75,120,102,85', '--purex-aware'])
    ok(rc == 0 and '(3.14, 104)' in t and 'improving 0' in t and '(delta +0.00)' in t, 'o1 purex-aware: 104 Q enders at 3.14, 0 sites')
    print('ALL PASS' if not fails else '%d FAILED' % fails); return 1 if fails else 0

if __name__ == '__main__': sys.exit(main())
