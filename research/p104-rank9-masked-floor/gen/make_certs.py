"""Regenerate all T1 moduli certificates and their Lean files (run from this directory).
For each framed type: gen_moduli.py -> cert/moduli-k.json, sim_moduli.py (same semantics as the Lean checker),
emit_packed.py -> ../lean/RankNine/Cert/Packed<k>.lean; gen_signs.py + emit_signs.py -> Cert/Signs<k>.lean; then ../lean/RankNine/AllModuli.lean imports all passing types.
Types where the hand route does not close (15 of 387) are reported and skipped.  usage: make_certs.py [workers] [comma-separated types]"""
import subprocess, sys, os, time
from concurrent.futures import ThreadPoolExecutor
W = int(sys.argv[1]) if len(sys.argv) > 1 else 3
TYPES = list(map(int, sys.argv[2].split(','))) if len(sys.argv) > 2 else list(range(387))
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
    if e.returncode != 0: return k, False, 'emit failed'
    js = 'cert/signs-%d.json' % k
    g2 = subprocess.run([sys.executable, 'gen_signs.py', str(k), j, js], capture_output=True, text=True)
    sl = [l for l in g2.stdout.splitlines() if 'SIGNS OK' in l]
    if g2.returncode != 0 or not sl:
        return k, False, 'signs: ' + ((g2.stdout + g2.stderr).strip().splitlines() or ['?'])[-1]
    e2 = subprocess.run([sys.executable, 'emit_signs.py', str(k), js, '../lean/RankNine/Cert/Signs%d.lean' % k], capture_output=True, text=True)
    if e2.returncode != 0: return k, False, 'emit signs failed'
    jf = 'cert/step5-%d.json' % k
    g3 = subprocess.run([sys.executable, 'gen_step5.py', str(k), j, js, jf], capture_output=True, text=True)
    fl = [l for l in g3.stdout.splitlines() if 'STEP5 OK' in l]
    if g3.returncode != 0 or not fl:
        return k, False, 'step5: ' + ((g3.stdout + g3.stderr).strip().splitlines() or ['?'])[-1]
    e3 = subprocess.run([sys.executable, 'emit_step5.py', str(k), jf, '../lean/RankNine/Cert/Step5c%d.lean' % k], capture_output=True, text=True)
    os.remove(j); os.remove(js); os.remove(jf)
    return k, e3.returncode == 0, line[-1] + ' | ' + sl[-1].split('] ')[-1] + ' | ' + fl[-1].split('] ')[-1]
good = []
with ThreadPoolExecutor(W) as ex:
    for k, ok, msg in ex.map(one, TYPES):
        print('[%7.1fs] type %d %s %s' % (time.time() - T0, k, 'OK' if ok else 'SKIP', msg), flush=True)
        if ok: good.append(k)
open('../lean/RankNine/AllModuli.lean', 'w').write('\n'.join('import RankNine.Cert.Packed%d\nimport RankNine.Cert.Signs%d\nimport RankNine.Cert.Step5c%d' % (k, k, k) for k in sorted(good)) + '\n')
print('DONE types with Lean certificates', len(good), flush=True)
