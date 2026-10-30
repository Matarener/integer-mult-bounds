#!/usr/bin/env python3
"""[BULKEVAL] smoke test for `tk bulk` on a 2-word mini corpus (#6030 + #5551 from toolkit/words).
usage: tests/bulk_test.py [--fast]
 default  all five steps incl. check --native (~40 s)
 --fast   price,shipcheck,gapmap,anatomy only (~6 s; used by regress --fast)
Checks: every step OK per word, exact kappa of both words, gapmap of #6030 vs itself = 0, summary sorted by kappa, per-side ledger columns present,
resume (second run evaluates 0 words, results.jsonl not grown), --only filter.  Prints ALL PASS and exits 0 on success."""
import sys, os, json, subprocess, shutil, csv
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
D = TK + '/out/bulk_test'
FAST = '--fast' in sys.argv
K = {'6030': 0.003125811557911897, '5551': 0.00304153116715}
fails = []


def need(c, what):
    print(('PASS ' if c else 'FAIL ') + what, flush=True)
    if not c: fails.append(what)


def tk(*a):
    r = subprocess.run([sys.executable, '-B', TK + '/tk.py'] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr


shutil.rmtree(D, ignore_errors=True); os.makedirs(D + '/words')
rows = []
for n in ('6030', '5551'):
    shutil.copy(TK + '/words/%s.json.gz' % n, D + '/words/%s.json.gz' % n)
    import gzip, hashlib
    sha = hashlib.sha256(gzip.open(D + '/words/%s.json.gz' % n).read()).hexdigest()[:16]
    rows.append(dict(id='w' + n, kind='swarm', source='PR#' + n, sha=sha, file='words/%s.json.gz' % n, claimed_kappa=None, public=770 if n == '6030' else 735))
open(D + '/manifest.jsonl', 'w').write('\n'.join(json.dumps(r) for r in rows) + '\n')
steps = 'price,shipcheck,gapmap,anatomy' if FAST else 'price,check,shipcheck,gapmap,anatomy'
out = D + '/results.jsonl'
rc, o = tk('bulk', D, '--out', out, '--steps', steps, '--ref', '6030', '--jobs', '2')
need(rc == 0 and '2 to (re)evaluate' in o, 'tk bulk runs on the mini corpus (rc %d)' % rc)
res = [json.loads(l) for l in open(out)]
need(len(res) == 2, '2 result records')
bysha = {r['id']: r for r in res}
for n in ('6030', '5551'):
    r = bysha['w' + n]
    need(all(v.get('ok') for v in r['steps'].values()) and len(r['steps']) == len(steps.split(',')), '%s: all steps ok (%s)' % (n, ','.join(k for k, v in r['steps'].items() if not v.get('ok'))))
    need(abs(r['steps']['price']['kappa'] - K[n]) < (1e-13 if n == '6030' else 1e-10), '%s: exact kappa %.13f' % (n, r['steps']['price']['kappa']))
    if not FAST: need(r['steps']['check']['legal_native'] and r['steps']['check']['native_bad'] == 0, '%s: check --native legal, 0 bad pairs' % n)
need(abs(bysha['w6030']['steps']['gapmap']['delta_total']) < 1e-6, 'gapmap of #6030 vs #6030 = 0')
need(bysha['w6030']['steps']['gapmap']['rows'].get('H signal (touch owned)', [0])[0] > 0, 'per-side ledger rows present')
need(bysha['w6030']['steps']['shipcheck']['verdict'].startswith('SHIPPABLE AS-IS'), '#6030 shipcheck SHIPPABLE AS-IS')
csvp = D + '/results.summary.csv'
need(os.path.exists(csvp) and os.path.exists(D + '/results.summary.md'), 'summary.csv + summary.md written')
rr = list(csv.DictReader(open(csvp)))
need([r['id'] for r in rr] == ['w6030', 'w5551'] and 'R0_X' in rr[0] and 'R0_Htop' in rr[0], 'summary sorted by kappa, ledger columns present')
size = os.path.getsize(out)
rc, o = tk('bulk', D, '--out', out, '--steps', steps, '--jobs', '2')
need(rc == 0 and '0 to (re)evaluate' in o and os.path.getsize(out) == size, 'resume: second run evaluates nothing, results unchanged')
rc, o = tk('bulk', D, '--out', out, '--steps', steps, '--only', 'w5551', '--force', '--jobs', '1')
need(rc == 0 and '1 to (re)evaluate' in o, '--only + --force redoes exactly one word')
shutil.rmtree(D, ignore_errors=True)
print('ALL PASS' if not fails else 'FAILED: %s' % fails)
sys.exit(1 if fails else 0)
