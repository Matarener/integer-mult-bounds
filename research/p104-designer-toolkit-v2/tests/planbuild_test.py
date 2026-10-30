#!/usr/bin/env python3
"""[PLANBUILD] tests for toolkit/planbuild (plan -> word realiser).  usage: tests/planbuild_test.py   (~10 s, foreground OK)
 1. plan.py reproduces CLASSBREAK's pm4 totals from the picks alone: base 7794.52, fix 7744.50 (hub roles re-solved, d8sig).
 2. build.py on the realisable no-hub pick (planbuild/out/r_nohub.pick): realised R0 == model 7661.68, value check exact, helpers clean, frame-legal
    up to the residual-only items.
 3. build.py on CLASSBREAK fix.pick: realised R0 == model R0 of the effective pick (0.0000), value check exact.
4. [PLANBUILD2] build.py --alt sink on planbuild/out/sink_hpg.pick: the 31 second holders a' are realised EXACTLY with an explicit fresh sink Z (0,3,9) each:
    realised - model(effective pick) == 31 x 5.7286 (the sink tax; a' + Z == copy, so no gain without a resident sink), value check exact, 3 residual-only violations.
[PLANBUILD5] 10-12: build.py --force-only A,B,.. --repair (exact F9 repair of the dirty registers of forced d fusions): 26 / 38 own sites jointly exact at the model price; site 306 (Y x-contamination) stays unrepairable.
Prints ALL PASS and exits 0 on success."""
import sys, os, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE); PB = TK + '/planbuild'
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); CB = W + '/ext/CLASSBREAK'
fails = []

def need(c, what):
    print(('PASS ' if c else 'FAIL ') + what, flush=True)
    if not c: fails.append(what)

def run(*a):
    r = subprocess.run([sys.executable, '-B'] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr

rc, o = run(PB + '/plan.py', CB + '/base.pick', CB + '/fix.pick', '--d8sig')
r0 = re.findall(r'^R0 ([0-9.]+)', o, re.M)
need(rc == 0 and r0 == ['7794.52', '7744.50'], 'plan.py reproduces pm4 base/fix: %s' % r0)
os.makedirs(PB + '/out/test', exist_ok=True)
for name, pick in (('r_nohub', PB + '/out/r_nohub.pick'), ('fix', CB + '/fix.pick')):
    rc, o = run(PB + '/build.py', pick, PB + '/out/test/%s.json.gz' % name)
    m = re.search(r'realised - model ([-0-9.]+)', o)
    need(rc == 0 and m and abs(float(m.group(1))) < 1e-4, '%s: realised R0 == model of the effective pick (%s)' % (name, m.group(1) if m else o[-300:]))
    need('exactly on all 104 rows' in o and 'required final form: 0 []' in o, '%s: value check exact, helpers/X clean' % name)
    v = re.search(r'legal \w+ viol (\d+)', o)
    need(v and int(v.group(1)) == 3, '%s: only the 3 residual-only violations' % name)
    if name == 'r_nohub': need('R0 realised' in o and ' 7661.68 ' in o, 'r_nohub realised R0 7661.68')
rc, o = run(PB + '/build.py', PB + '/out/sink_hpg.pick', PB + '/out/test/sink_hpg_alt.json.gz', '--alt', 'sink')
m = re.search(r'realised - model ([-0-9.]+)', o); nz = re.search(r"'alta': (\d+)", o)
need(rc == 0 and m and nz and abs(float(m.group(1)) - int(nz.group(1)) * 5.7286) < 2e-3, "sink_hpg --alt sink: realised - model = %s = %s x 5.7286" % (m.group(1) if m else o[-200:], nz.group(1) if nz else '?'))
need('exactly on all 104 rows' in o and 'required final form: 0 []' in o, 'sink_hpg --alt sink: value check exact, helpers/X clean')
v = re.search(r'legal \w+ viol (\d+)', o); need(v and int(v.group(1)) == 3, 'sink_hpg --alt sink: only the 3 residual-only violations')
# [PLANBUILD3] 7. every cycle-block fusion d saves exactly one fresh-sink price (5.7286) over the best own fallback (a / b), own and alt alike: the d' lemma's arithmetic
HP = W + '/ext/PLANBUILD2/hpg_paid.pick'
rc, o = run(PB + '/dgain.py', HP)
for kk in ("('b', 'alt') 59", "('b', 'own') 56"):
    need(rc == 0 and re.search(re.escape(kk) + r'.*vs best own fallback 5\.7286', o), 'dgain hpg_paid %s: saving vs best own fallback = 5.7286' % kk)
# 8. the exact counterexample: ONE forced naive fusion (dual site 306: dsrc + psrc, p a bottom source, d written by the F0 block) leaves residue on the bottom destinations
rc, o = run(PB + '/build.py', HP, PB + '/out/test/force306.json.gz', '--alt', 'sink', '--force-only', '306')
need(rc == 0 and 'VALUE CHECK FAILED: 10 entries' in o and 'required final form: 7 ' in o, 'forced fusion at dual site 306: value check fails (10 Y entries, 7 dirty registers)')
# 9. pm8 (--realisable) point: model == realisable. realised - model(effective pick, no hubs) == 14 a' sinks x 5.7286, effective pick == input pick (no fallback), value check exact
rc, o = run(PB + '/build.py', PB + '/out/pm8_hpg.pick', PB + '/out/test/pm8_hpg.json.gz', '--alt', 'sink')
m = re.search(r'realised - model ([-0-9.]+)', o); nz = re.search(r"'alta': (\d+)", o); fbk = re.search(r'fallback cost ([-0-9.]+)', o)
need(rc == 0 and m and nz and abs(float(m.group(1)) - int(nz.group(1)) * 5.7286) < 2e-3 and fbk and abs(float(fbk.group(1))) < 1e-6, 'pm8_hpg: realised - model = %s = %s x 5.7286, no fallback' % (m.group(1) if m else o[-200:], nz.group(1) if nz else '?'))
need('exactly on all 104 rows' in o and 'required final form: 0 []' in o, 'pm8_hpg: value check exact, helpers/X clean')
# [PLANBUILD5] 10. DEFERRED-CANCEL / exact F9 repair: 26 own cycle-block d fusions forced TOGETHER on hpg_paid.pick (sites exact one by one in pb5b_own4.json), build.py --repair:
#     realised - model(effective pick) == 36 a' sinks x 5.7286 (the fusions cost exactly their MODEL price), value check exact, helpers/X clean, dyadic coefficients, 3 residual-only violations
S26 = '116,118,141,143,152,162,172,175,176,195,202,228,246,275,279,280,286,291,309,313,326,328,400,410,444,447'
rc, o = run(PB + '/build.py', HP, PB + '/out/test/force26.json.gz', '--alt', 'sink', '--force-only', S26, '--repair')
m = re.search(r'realised - model ([-0-9.]+)', o)
need(rc == 0 and m and abs(float(m.group(1)) - 36 * 5.7286) < 2e-3, '26 forced d + F9 repair: realised - model = %s = 36 x 5.7286' % (m.group(1) if m else o[-200:]))
need('exactly on all 104 rows' in o and 'required final form: 0 []' in o and 'unrepairable []' in o, '26 forced d + F9 repair: value check exact, 0 dirty, nothing unrepairable')
v = re.search(r'legal \w+ viol (\d+)', o); need(v and int(v.group(1)) == 3, '26 forced d + F9 repair: only the 3 residual-only violations (all coefficients dyadic)')
# 11. the Y-contamination sites stay UNREPAIRABLE (site 306 forced + repair still fails the value check; PLANBUILD4's t306 diagnosis was this class, not the whole class)
rc, o = run(PB + '/build.py', HP, PB + '/out/test/force306r.json.gz', '--alt', 'sink', '--force-only', '306', '--repair')
need(rc == 0 and 'VALUE CHECK FAILED' in o, 'forced site 306 + F9 repair: value check still fails (Y x-contamination is not repairable at F9)')
# 12. all 38 own cycle-block d fusions that are exact at the MODEL price (pb5b_own4.json), forced jointly + F9 repair (large multipliers split to < 2^15: verifier coefficient bound)
S38 = '116,118,122,129,139,141,143,152,154,162,172,175,176,195,196,202,221,228,246,264,268,275,279,280,286,291,292,304,309,313,315,326,328,338,400,410,444,447'
rc, o = run(PB + '/build.py', HP, PB + '/out/test/force38.json.gz', '--alt', 'sink', '--force-only', S38, '--repair')
m = re.search(r'realised - model ([-0-9.]+)', o); ev = re.search(r'events (\d+)', o)
need(rc == 0 and m and abs(float(m.group(1)) - 36 * 5.7286) < 2e-3, '38 forced d + F9 repair: realised - model = %s = 36 x 5.7286 (the fusions cost their model price)' % (m.group(1) if m else o[-200:]))
need('exactly on all 104 rows' in o and 'required final form: 0 []' in o and 'unrepairable []' in o, '38 forced d + F9 repair: value check exact, 0 dirty')
v = re.search(r'legal \w+ viol (\d+)', o); need(v and int(v.group(1)) == 3, '38 forced d + F9 repair: only the 3 residual-only violations (dyadic, |coef| < 2^15)')
need(ev and 18500 < int(ev.group(1)) < 20500, '38 forced d + F9 repair: word has %s events (F9 repair is event-hungry: ~200 per site; cap 26000)' % (ev.group(1) if ev else '?'))
# 13. all 41 alt (second-holder) d fusions that are individually exact+legal (pb5l), forced jointly: each carries its own fresh a' sink (5.7286); 3 of them are the +3.1395 Y-main sites
S41 = '115,124,131,134,136,145,147,149,159,166,188,201,205,224,227,237,249,250,270,283,285,298,319,332,351,352,364,367,373,374,380,389,395,405,408,413,415,416,423,436,442'
rc, o = run(PB + '/build.py', HP, PB + '/out/test/force41alt.json.gz', '--alt', 'sink', '--force-only', S41, '--repair')
m = re.search(r'realised - model ([-0-9.]+)', o)
need(rc == 0 and m and abs(float(m.group(1)) - (77 * 5.7286 + 3 * 3.1395)) < 3e-3, '41 forced alt d + F9 repair: realised - model = %s = 77 sinks x 5.7286 + 3 x 3.1395' % (m.group(1) if m else o[-200:]))
need('exactly on all 104 rows' in o and 'required final form: 0 []' in o and 'unrepairable []' in o, '41 forced alt d + F9 repair: value check exact, 0 dirty')
v = re.search(r'legal \w+ viol (\d+)', o); need(v and int(v.group(1)) == 3, '41 forced alt d + F9 repair: only the 3 residual-only violations')
print('ALL PASS' if not fails else 'FAILURES: %d' % len(fails)); sys.exit(1 if fails else 0)
