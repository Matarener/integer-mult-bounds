#!/usr/bin/env python3
"""[BULKGEN] tests for `tk rebuild` / `tk anatomy` (toolkit/alignbuild/).
usage: tests/alignbuild_test.py --fast | --quick | --anatomy
 --fast   (~30 s)  anatomy smoke on #6030 (published ledger numbers: markets 62 births, hub O-net 117.9 / NET 351.4, 52 pure copies, d8 67.6; lifetimes from the shipped
          end-anatomy cache) + a 2-step `tk rebuild` (skeleton octet 0, hub 233) at exact kappa through the real CLI
 --quick  the FULL rebuild of #6030 (all five sides, 45+ steps, ~60-70 min): kappa == #6030 exactly, legal, events <= 26000, SPAN5/JR 0, native 0 bad.  Heavy: run via $TK_HQ
          (regress.py --quick calls it only with --alignbuild-full; the hq job name is documented in MAP.md)
Prints ALL PASS and exits 0 on success."""
import sys, os, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); TK = os.path.dirname(HERE)
AB = TK + '/alignbuild'; OUT = AB + '/out/test'
K6030 = 0.003125811557911897
fails = []


def need(c, what):
    print(('PASS ' if c else 'FAIL ') + what, flush=True)
    if not c: fails.append(what)


def tk(*a):
    r = subprocess.run([sys.executable, '-B', TK + '/tk.py'] + list(a), capture_output=True, text=True); return r.returncode, r.stdout + r.stderr


def anatomy_smoke():
    rc, o = tk('anatomy', '6030', '--json')
    need(rc == 0, 'tk anatomy 6030 --json runs')
    try: a = json.loads(o[o.index('{'):])
    except Exception: need(False, 'anatomy JSON parses: ' + o[-300:]); return
    need(abs(a['invoice']['kappa_pred'] - 0.0031259) < 5e-7, 'anatomy: law-predicted kappa %.7f ~ .0031259' % a['invoice']['kappa_pred'])
    need(a['skeleton']['X']['n'] == 104 and a['skeleton']['Y']['n'] == 104, 'anatomy: 104 X + 104 Y mains')
    t = a['hubs_total']
    need(abs(t['O-net'] - 117.90) < 0.01 and abs(t['NET'] - 351.41) < 0.01 and abs(t['cpy'] - 233.51) < 0.01 and abs(t['d8'] - 67.55) < 0.01, 'anatomy: hub ledger reproduces HUBCOST (O-net 117.90, cpy 233.51, NET 351.41, d8 67.55)')
    need(a['copies']['n_pure_crossing'] == 52 and a['copies']['copy_events'] == 23, 'anatomy: 52 pure crossing copies, 23 COPY events')
    g = a['lifetimes']['groups']
    need(g['markets']['n'] == 62 and abs(g['markets']['net_lo'] - 240.9) < 0.1, 'anatomy: market births 62, net 240.9 (attrib6030)')
    need(abs(a['lifetimes']['total_L'] - 976.1) < 0.1 and abs(a['lifetimes']['enabling_cost'] - 311.3) < 0.1, 'anatomy: lifetime L 976.1, enabling cost 311.3 (attrib6030)')


def rebuild_mini():
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(AB + '/data/manifest_6030.json'))
    man['plan'] = [dict(man['plan'][0], items=[0]), dict(man['plan'][3], items=[233])]
    mf = OUT + '/mini_manifest.json'; json.dump(man, open(mf, 'w'))
    rc, o = tk('rebuild', '6030', '--manifest', mf, '--workdir', OUT + '/mini', '--out', OUT + '/mini/final.json.gz', '--no-checks', '--json')
    need(rc == 0, 'tk rebuild (skeleton octet 0 + hub 233) exits 0: ' + o[-200:].replace('\n', ' | '))
    try: s = json.loads(o[o.index('{\n'):])
    except Exception: need(False, 'rebuild JSON parses: ' + o[-300:]); return
    need(s['exact'] and abs(s['kappa_out'] - K6030) < 1e-13 and s['steps_ok'] == 2 and s['events_ok'], 'rebuild mini: 2/2 steps OK at exact kappa .003125811557911897, events <= 26000')


def rebuild_full():
    rc, o = tk('rebuild', '6030', '--workdir', OUT + '/full', '--out', OUT + '/full/final.json.gz', '--json')
    print(o[-1500:])
    try: s = json.loads(o[o.index('{\n'):])
    except Exception: need(False, 'rebuild JSON parses'); return
    need(s['exact'] and abs(s['kappa_out'] - K6030) < 1e-13, 'rebuild 6030 (all sides): kappa == #6030 exactly (%s)' % s['kappa_str'])
    need(s['legal'] and s['events'] <= 26000, 'rebuild 6030: legal, %s events <= 26000' % s['events'])
    c = s.get('checks', {})
    need(c.get('validate_ok') and c.get('check_ok'), 'rebuild 6030: SPAN5/JR 0 on all frames, native 0 bad pairs')
    need(s['steps_ok'] >= s['steps'] - 1, 'rebuild 6030: steps ok %d/%d (FULLWORD: 44/45, signal root 1 reads is the known GAP); gaps %s' % (s['steps_ok'], s['steps'], s['gaps']))


if __name__ == '__main__':
    A = sys.argv[1:]
    if '--fast' in A or not A: anatomy_smoke(); rebuild_mini()
    if '--anatomy' in A: anatomy_smoke()
    if '--quick' in A: rebuild_full()
    print('ALL PASS' if not fails else 'FAILS %d: %s' % (len(fails), fails)); sys.exit(1 if fails else 0)
