"""Regenerate all T1 moduli certificates and their Lean files (run from this directory).
For each framed type: gen_moduli.py -> cert/moduli-k.json, sim_moduli.py (same semantics as the Lean checker),
emit_packed.py -> ../lean/RankNine/Cert/Packed<k>.lean; then ../lean/RankNine/AllModuli.lean imports all passing types.
Types where the hand route does not close (15 of 387) are reported and skipped.  usage: make_certs.py [workers]"""
import subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor
W = int(sys.argv[1]) if len(sys.argv) > 1 else 3
DROP = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}
os.makedirs('cert', exist_ok=True); os.makedirs('../lean/RankNine/Cert', exist_ok=True)
T0 = time.time()
def one(k):
    env = dict(os.environ); env['DROP'] = str(DROP[k]) if k in DROP else ''
    j = 'cert/moduli-%d.json' % k
    g = subprocess.run([sys.executable, 'gen_moduli.py', str(k), j], env=env, capture_output=True, text=True)
    line = [l for l in g.stdout.splitlines() if l.startswith('rep')]
    if g.returncode != 0 or not line or not line[-1].endswith('ok True'):
        return k, False, 'gen: ' + (line[-1] if line else (g.stderr.strip().splitlines() or ['?'])[-1])
    s = subprocess.run([sys.executable, 'sim_moduli.py', j], capture_output=True, text=True)
    if 'SIM OK' not in s.stdout: return k, False, 'sim failed'
    e = subprocess.run([sys.executable, 'emit_packed.py', str(k), '../lean/RankNine/Cert/Packed%d.lean' % k, '400', j], capture_output=True, text=True)
    os.remove(j)
    return k, e.returncode == 0, line[-1]
good = []
with ThreadPoolExecutor(W) as ex:
    for k, ok, msg in ex.map(one, range(387)):
        print('[%7.1fs] type %d %s %s' % (time.time() - T0, k, 'OK' if ok else 'SKIP', msg), flush=True)
        if ok: good.append(k)
open('../lean/RankNine/AllModuli.lean', 'w').write('\n'.join('import RankNine.Cert.Packed%d' % k for k in sorted(good)) + '\n')
print('DONE types with Lean certificates', len(good), flush=True)
