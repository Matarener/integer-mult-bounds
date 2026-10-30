#!/usr/bin/env python3
"""LEVERBANK regress (~30 s): the default gen2 chain stays bit-exact and the lever bank is opt-in.
  1. importing gen2/levers/{bank,stack} does not change os.environ;
  2. `tk gen2 --stages order,purex --expect` (default, no --lever) -> o1 5cd4a131bcc23a2b, r104 a691733502945e0a (content sha) and kappa .0030170593878;
  3. levers/stack.py with NO lever on that o1 == purex2's r104 bit-for-bit (content sha);
  4. one lever (own:479@560, OWNEDRANK m479) reproduces kappa .003017361261390575 (IncrWord == lane word)."""
import sys, os, json, gzip, hashlib, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.abspath(HERE + '/..')
fails = []
def need(c, what):
    print(('PASS ' if c else 'FAIL ') + what, flush=True)
    if not c: fails.append(what)
def csha(p): return hashlib.sha256(gzip.open(p).read()).hexdigest()[:16]
def main():
    before = dict(os.environ)
    for p in (TK, TK + '/synth', TK + '/gen2', TK + '/gen2/levers'):
        if p not in sys.path: sys.path.insert(0, p)
    import bank, stack   # noqa
    need(dict(os.environ) == before, 'gen2/levers bank+stack import without changing os.environ')
    tmp = tempfile.mkdtemp(); out = tmp + '/g'
    r = subprocess.run([sys.executable, '-B', TK + '/tk.py', 'gen2', '--out', out, '--stages', 'order,purex', '--expect'], capture_output=True, text=True)
    need(r.returncode == 0, 'tk gen2 --stages order,purex --expect exit 0 (default chain, no lever)')
    recs = {x['word']: x for x in (json.loads(l) for l in open(out + '/stages.jsonl'))} if os.path.exists(out + '/stages.jsonl') else {}
    need(recs.get('o1', {}).get('content_sha') == '5cd4a131bcc23a2b', 'o1 content sha 5cd4a131bcc23a2b')
    need(recs.get('r104', {}).get('content_sha') == 'a691733502945e0a' and abs(recs['r104']['kappa'] - 0.0030170593878) < 1e-13, 'default r104 content sha a691733502945e0a, kappa .0030170593878')
    need('r104L' not in recs, 'no lever word written by the default chain')
    env = dict(os.environ); env.pop('TK_FREE_BOUNDS', None)
    S = TK + '/gen2/levers/stack.py'
    r = subprocess.run([sys.executable, '-B', S, out + '/o1.json.gz', tmp + '/b.json.gz', '--dims', '4,8', '--xstops'], capture_output=True, text=True, env=env)
    need(r.returncode == 0 and os.path.exists(tmp + '/b.json.gz') and csha(tmp + '/b.json.gz') == 'a691733502945e0a', 'stack.py with no lever == purex2 r104 (content sha)')
    r = subprocess.run([sys.executable, '-B', S, out + '/o1.json.gz', tmp + '/m.json.gz', '--dims', '4,8', '--xstops', '--lever', 'own:479@560'], capture_output=True, text=True, env=env)
    need(r.returncode == 0 and 'kappa 0.0030173612614' in r.stdout and 'legal True viol 0' in r.stdout, 'own:479@560 lever reproduces OWNEDRANK m479 kappa .0030173612614, legal')
    need(dict(os.environ) == before, 'os.environ unchanged at the end')
    print('\n%d failed' % len(fails)); print('ALL PASS' if not fails else 'FAILED'); sys.exit(1 if fails else 0)
main()
