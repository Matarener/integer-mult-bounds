"""GENHUBS `tk gen3` scaffold test (~5 s, venv python -B; no env at import).
1. tk gen3 --list prints the eight stages (retain: RETAINOP) in order (primgen, span added by PRIMGEN, opt-in)
2. census-only yroute + signal on the GENUPGRADE best gen2 word: census = 151 endable sites (model greedy -263.68 R0), the word passes through at
   kappa .0030221767578 (never-lose), stages.jsonl carries the signal ledger (H signal 494.0, owned staging 0)
3. each stage runs alone from --from (signal only)
usage: tests/gen3_test.py"""
import sys, os, subprocess, json, shutil
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); TK = W; PY = sys.executable
OUT = W + '/ext/GENHUBS/testwork'; G = W + '/ext/GENHUBS/g2best.json.gz'

def sh(cmd):
    env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
    p = subprocess.run(cmd, cwd=TK, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True); return p.returncode, p.stdout

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); fails = 0
    def ok(c, m): nonlocal fails; print(('PASS ' if c else 'FAIL ') + m, flush=True); fails += (not c)
    rc, t = sh([PY, '-B', TK + '/tk.py', 'gen3', '--list'])
    ok(rc == 0 and t.split() == ['gen2', 'primgen', 'span', 'yroute', 'signal', 'post', 'retain', 'screens'], 'gen3 --list')
    rc, t = sh([PY, '-B', TK + '/tk.py', 'gen3', '--out', OUT + '/a', '--from', G, '--stages', 'yroute,signal', '--yroute-census-only'])
    ok(rc == 0 and 'with an endable helper 151' in t and 'total -263.68 R0' in t, 'yroute census on g2best: 151 endable sites, model greedy -263.68')
    R = [json.loads(l) for l in open(OUT + '/a/stages.jsonl')] if rc == 0 else []
    ok(len(R) == 2 and all(abs(r['kappa'] - 0.0030221767578) < 1e-12 for r in R), 'census-only pass-through keeps kappa .0030221767578')
    ok(len(R) == 2 and abs(R[1]['H_signal_R0'] - 494.0) < 0.05 and R[1]['owned_staging'] == 0, 'signal ledger recorded (494.0, staging 0)')
    rc, t = sh([PY, '-B', TK + '/tk.py', 'gen3', '--out', OUT + '/b', '--from', G, '--stages', 'signal'])
    ok(rc == 0 and os.path.exists(OUT + '/b/signal.json.gz'), 'single stage from --from')
    print('ALL PASS' if not fails else '%d FAILED' % fails); return 1 if fails else 0

if __name__ == '__main__': sys.exit(main())
