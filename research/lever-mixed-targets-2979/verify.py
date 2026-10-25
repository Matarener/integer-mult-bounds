#!/usr/bin/env python3
"""Registered check of research/lever-mixed-targets-2979: the recursion lever priced on a community word.

Run from the repository root (the hub's runner does this for the registered instance, #2979):
    python3 -B research/lever-mixed-targets-2979/verify.py --part main
    python3 -B research/lever-mixed-targets-2979/verify.py --part controls
The second instance (#3945, not registered here; archived on main on 20 October 2026 with the same files as its
head) runs the same way, from its folder on main by default, see README.md section 6:
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945 [--source <its package folder>]
and so does #3945 with every head kept (design B: the same words and the same price of the circuit, with the table of
hosts that this package carries in fills/3945H/, made by the community's own allocation programs with one added
condition), the instance of the highest Lean-checked bound:
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945H [--source <the package folder of #3945>]
and so does the FULL cut on the same table (instance 3945F: every head removed, job 25 on its array, and every other
rank-48 block split into two blocks of 24 on the same role), the instance of the highest Lean-checked bound:
    python3 -B research/lever-mixed-targets-2979/verify.py --instance 3945F [--source <the package folder of #3945>]
Standard library only.  The instance's input files are re-checked by sha256 (instances/<id>.json).  Everything is
written to a temporary folder outside the repository and removed at the end (--keep DIR keeps a copy).

--part main
  1. pins: every input file and every data file of this package equals its recorded sha256; the word's stated
     local profile, widths, zero buffers and complex root are read from the community's own files;
  2. my conversion of both words (gauge44 and extra) into the gcert format: tools/transport.py (the community's
     native canonical form, rebuilt from the borrowed word, exact replay on all 632 columns in both orientations)
     and tools/lower_w.py (frames, warps, residual widths = the word's widths helper by helper, the community's local
     profile, the full program replayed to the community's endpoint, 7 wrong versions of each word rejected); the
     stated local profile, widths and zero buffers equal what the conversion finds; the content hashes of the
     results equal the recorded ones;
  3. the head test (tools/g0_staged.py) in my network (network/: the step order of my Lean network, read from the
     Lean source as data; nothing is compiled here) on the word's ORDER, DISPATCH, PLAN, TEMPLATE and FILL rows:
     no role outside a window, no bin over its rank, one use per call and role, the global paid profile equal to
     the community's PROFILE.json digit for digit, and the number of literal rank-48 heads; and the head test's own
     controls (gate A4 moved before its climb: no heads; gate C2 deleted: the other rank-48 blocks become tails);
  4. the price (tools/price_ours.py): the uniform root of my profile equals the community's stated complex root to
     all 24 digits; the half cut (each head cut by 24 of its 48 axes, job 49 on its array) and, as a what-if, the
     full cut;
  5. the rate certificate (tools/rate_cert.py) on the half-cut profile DERIVED from the measured heads (for a
     full-cut instance, "rate": {"cut": "full"}: the full-cut profile, heads removed with job 25 and the other
     rank-48 blocks split 24 + 24): exact rational enclosures prove the mixed rate inequality at the figure N/10^10
     and refute it at (N+1)/10^10, and the derived profile equals the histogram of the Lean rate module recorded in
     instances/<id>.json.
--part controls
  6. regression: the same head test on the earlier T74 circuit (controls/t74) finds the 11,010 heads (6,150 +
     4,860) of the first head test, and that circuit's global profile;
  7. price controls: with a single head, or with one head fewer, the figure is refused; a profile that is not
     separated (job 25 on the head arrays while blocks of 48 stay; for a full-cut instance, the full cut without
     the split) is refused; one grid step above is refused.
Prints PASS_LEVER_MIXED_TARGETS_<instance>_<PART> on success; any failed check stops with FAIL.
"""
import argparse, gzip, hashlib, json, shutil, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path

PKG = Path(__file__).resolve().parent
TOOLS = PKG / 'tools'
T37 = '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def content_sha(p):
    obj = json.loads(gzip.decompress(Path(p).read_bytes()))
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def need(ok, what):
    if not ok:
        raise SystemExit('FAIL: ' + what)
    print('  ok  ' + what, flush=True)


def run(*args, out=None, expect_rc=0):
    t = time.time()
    r = subprocess.run([sys.executable, '-I', '-B', *map(str, args)], capture_output=True, text=True)
    if r.returncode != expect_rc:
        sys.stderr.write(r.stdout[-4000:] + r.stderr[-4000:])
        raise SystemExit('FAIL: %s exited %d (expected %d)' % (Path(str(args[0])).name, r.returncode, expect_rc))
    if out:
        Path(out).write_text(r.stdout)
    print('      (%s %.1f s)' % (Path(str(args[0])).name, time.time() - t), flush=True)
    return r.stdout


def key(obj, dotted):
    for k in dotted.split('.'):
        obj = obj[k]
    return obj


def stage_inputs(src, I, work, name):
    """the owner-package layout g0_staged.py reads: <dir>/inputs/{ORDER,DISPATCH,PLAN,TEMPLATE}"""
    d = work / name / 'inputs'
    d.mkdir(parents=True)
    for f, k in (('ORDER.json', 'order'), ('DISPATCH.json', 'dispatch'), ('PLAN.json.gz', 'plan'), ('TEMPLATE.json.gz', 'template')):
        shutil.copyfile(src / I['files'][k], d / f)
    return d.parent


def head_test(pkgdir, fill, gb, ge, profile, out, label):
    run(TOOLS / 'g0_staged.py', PKG, pkgdir, fill, gb, ge, profile, out, '--label', label,
        '--gates', PKG / 'network' / 'Gates.lean', '--xhost', PKG / 'network' / 'XHost')
    return json.loads(Path(out).read_text())


def half_cut(profile, W, heads):
    ch = {int(r): int(n) for r, n in profile.items()}
    other = ch.pop(48) - heads
    assert other >= 0
    ch[24] = ch.get(24, 0) + heads
    if other:
        ch[48] = other
    return dict(children={str(r): n for r, n in sorted(ch.items())}, W=W, H=heads, kc=49, m=73)


def full_cut(profile, W, heads):
    """the full cut: every head removed (job 73 - 48 = 25 on its array), every other rank-48 block split 24 + 24"""
    ch = {int(r): int(n) for r, n in profile.items()}
    other = ch.pop(48) - heads
    assert other >= 0
    if other:
        ch[24] = ch.get(24, 0) + 2 * other
    return dict(children={str(r): n for r, n in sorted(ch.items())}, W=W, H=heads, kc=25, m=73)


def cut_of(I):
    return I['rate'].get('cut', 'half')


def rate(work, name, prof, N, expect_rc=0):
    p = work / ('profile-%s.json' % name)
    p.write_text(json.dumps(prof))
    return json.loads(run(TOOLS / 'rate_cert.py', p, N, expect_rc=expect_rc))


def fill_of(I, src):
    """the instance's table of hosts: the word's own FILL, or one this package carries (fill_in_package)"""
    return PKG / I['fill_in_package'] if I.get('fill_in_package') else src / I['files']['fill']


def profile_of(I, src):
    """the paid profile of that table: the word's own PROFILE.json, or one this package carries (profile_in_package)"""
    return PKG / I['profile_in_package'] if I.get('profile_in_package') else src / I['files']['profile']


def part_main(I, src, work):
    print('1. pins', flush=True)
    for rel, h in I['inputs_sha256'].items():
        need(sha(src / rel) == h, 'input %s sha256 %s...' % (rel, h[:12]))
    if I.get('fill_in_package'):
        need(sha(fill_of(I, src)) == I['fill_in_package_sha256'],
             "this package's table of hosts %s sha256 %s..." % (I['fill_in_package'], I['fill_in_package_sha256'][:12]))
    if I.get('profile_in_package'):
        need(sha(profile_of(I, src)) == I['profile_in_package_sha256'],
             "this package's paid profile of that table %s sha256 %s..." % (I['profile_in_package'], I['profile_in_package_sha256'][:12]))
    R = json.loads((PKG / 'RESULT.json').read_text())
    for rel, h in R['package_data_sha256'].items():
        need(sha(PKG / rel) == h, 'package file %s sha256 %s...' % (rel, h[:12]))
    S = I['stated']
    for c in S['sources']:
        need(key(json.loads((src / c['file']).read_text()), c['key']) == S[c['what']],
             'stated %s: %s %s = %s' % (c['what'], c['file'], c['key'], json.dumps(S[c['what']])[:64]))

    print('2. my conversion of the two words', flush=True)
    E = I['lowering']
    g1b = {}
    for prov, w in (('gauge44', 'base'), ('extra', 'extra')):
        word = src / I['files']['word_' + w]
        can, aud = work / ('%s.canonical.json.gz' % w), work / ('%s.transport-audit.json' % w)
        run(TOOLS / 'transport.py', word, can, aud)
        a = json.loads(aud.read_text())
        need(a['free_algebra_replay'].startswith('both orientations exact'), '%s: transport replay exact in both orientations' % w)
        need(a['R'] == E['R'] and a['zero_buffers'] == S['zero_buffers'] and a['warps'] == E['warps'] and a['tadds'] == E['tadds'],
             '%s: R %d, %d zero buffers (= stated), %d warps, %d twisted additions' % (w, a['R'], a['zero_buffers'], a['warps'], a['tadds']))
        need(a['local_profile'] == S['local_profile'], '%s: local profile = stated %s' % (w, json.dumps(a['local_profile'])))
        need(a['widths_hist'] == S['width_inventory'], '%s: width histogram = stated %s' % (w, json.dumps(a['widths_hist'])))
        need(content_sha(can) == E[w]['canonical_content_sha256'], '%s: canonical content sha256 as recorded' % w)
        g1w, rep = work / ('%s.gcert1w.json.gz' % w), work / ('lower-%s.json' % w)
        run(TOOLS / 'lower_w.py', can, g1w, rep, '--provider', prov, '--word', word, '--mutants')
        L = json.loads(rep.read_text())
        fp = L['frames_and_price']
        need(fp['hist_equals_hub_local_profile'] and fp['invoice'][0] == fp['invoice'][1] and fp['max_block_rank'] <= 8,
             '%s: block histogram = the local profile, invoice %d = %d, blocks of rank <= 8' % (w, fp['invoice'][0], fp['invoice'][1]))
        need(L['full_replay']['endpoint'].startswith('exact on all 632 columns'), '%s: full program replayed to the endpoint on all 632 columns' % w)
        need(L['width_inventory']['equals_residuals_per_helper'], "%s: residual widths = the word's widths, helper by helper" % w)
        need(len(L['mutants']) == 7 and all(v.startswith('rejected') for v in L['mutants'].values()), '%s: 7 of 7 wrong versions rejected' % w)
        need(content_sha(g1w) == E[w]['gcert1w_content_sha256'], '%s: gcert/1w content sha256 as recorded' % w)
        g1b[w] = work / ('S%s-%s.gcert1b.json.gz' % (I['id'], w))
        run(TOOLS / 'lower_w.py', '--to-1b', g1w, g1b[w])
        need(content_sha(g1b[w]) == E[w]['gcert1b_content_sha256'], '%s: gcert/1b content sha256 as recorded' % w)

    print('3. the head test in my network', flush=True)
    pk = stage_inputs(src, I, work, 'pkg')
    g = head_test(pk, fill_of(I, src), g1b['base'], g1b['extra'], profile_of(I, src), work / 'g0.json', '#' + I['id'])
    m, H = g['G0'], I['heads']
    need(g['fill'] == I['fill'], 'FILL: %(rows)d roles, %(roles_per_call)d per call, %(calls)d calls, %(replicas)d replicas' % g['fill'])
    need(not m['violations'] and m['loads_over_rank'] == 0 and m['one_use_per_call_and_role'],
         'every role inside a window of my network, no bin over its rank, one use per call and role')
    need(g['call_blocks']['global_profile_equals_hub'], "global paid profile = %s, digit for digit" % (
        "this package's PROFILE.json of that table" if I.get('profile_in_package') else "the community's PROFILE.json"))
    need(g['call_blocks']['all_call_blocks_rank_le_8'], 'every block inside a call has rank <= 8')
    by = {(c['hub_child'], c['cls']): c['count'] for c in m['classes'] if c['remainder'] == 48}
    need(m['heads_rank48_unhosted'] == H['total'] and by.get((8, 'HEAD-literal')) == H['child8'] and by.get((10, 'HEAD-literal')) == H['child10'],
         'literal rank-48 heads: %d (child 8: %s, child 10: %s)' % (m['heads_rank48_unhosted'], by.get((8, 'HEAD-literal')), by.get((10, 'HEAD-literal'))))
    need(m['rank48_by_class'].get('neither', 0) == H['other_rank48'], 'other rank-48 blocks (neither heads nor tails): %d' % H['other_rank48'])
    n1, n2 = g['control_gateA4_before_climbA4'], g['control_without_gateC2']
    need(n1['rank48_by_class'].get('HEAD-literal', 0) == 0,
         'control: gate A4 moved before its climb -> 0 heads (all %d rank-48 blocks "neither")' % n1['rank48_by_class'].get('neither', 0))
    need(n2['rank48_by_class'].get('TAIL-literal', 0) == H['other_rank48'],
         'control: gate C2 deleted -> the %d other rank-48 blocks become tails' % H['other_rank48'])

    print('4. the price', flush=True)
    lo = Fraction(S['complex_lower'])
    dec = lambda q: '0.' + str(q.numerator * 10 ** 24 // q.denominator).rjust(24, '0')
    P = json.loads(run(TOOLS / 'price_ours.py', work / 'g0.json', dec(lo), dec(lo + Fraction(1, 10 ** 24)), out=work / 'price.json'))
    need(P['b_reproduces_stated_lower_digit_for_digit'], 'uniform root of my profile = the stated complex root to 24 digits (%s)' % P['b_hub_engine'])
    need(P['half_cut']['separated'] and P['half_cut']['b'] == I['price']['half_cut'], 'half cut (job 49 on the head arrays): b = %s, separated' % P['half_cut']['b'])
    if cut_of(I) == 'full':
        need(P['full_cut']['separated'] and P['full_cut']['b'] == I['price']['full_cut'],
             'full cut (heads removed, job 25 on the head arrays; the other rank-48 blocks split 24 + 24): b = %s, separated' % P['full_cut']['b'])
    else:
        need(P['full_cut']['b'] == I['price']['full_cut_what_if'], 'full cut, what-if only: b = %s' % P['full_cut']['b'])

    print('5. the rate certificate', flush=True)
    cut = full_cut if cut_of(I) == 'full' else half_cut
    prof = cut(g['call_blocks']['global_profile'], P['W'], m['heads_rank48_unhosted'])
    need(prof == I['rate']['profile'], 'derived %s-cut profile = %s' % (cut_of(I), (
        'the histogram of the Lean rate module (%s)' % I['rate']['module']) if I['rate'].get('module') else
        'the recorded histogram (this instance has no Lean rate module: checked by computer, not proved in Lean)'))
    c = rate(work, 'half', prof, I['rate']['N'])
    need(c['PASS'], 'rate inequality proved at %d/10^10 (relative margin %.3e) and refuted at %d/10^10' % (c['N'], c['relative_margin'], c['N'] + 1))


def part_controls(I, src, work):
    print('6. regression: the T74 circuit', flush=True)
    t = PKG / 'controls' / 't74'
    pk = work / 't74pkg'
    shutil.copytree(t / 'inputs', pk / 'inputs')
    tpl = src / I['files']['template']
    need(sha(tpl) == T37, 'the T37 template of the instance (sha256 21297b20...) is the one T74 uses')
    shutil.copyfile(tpl, pk / 'inputs' / 'TEMPLATE.json.gz')
    g = head_test(pk, t / 'FILL.json.gz', t / 'gauge44.gcert1b.json.gz', t / 'extra.gcert1b.json.gz', t / 'PROFILE.json',
                  work / 'g0-T74.json', 'T74 control')
    m = g['G0']
    by = {(c['hub_child'], c['cls']): c['count'] for c in m['classes'] if c['remainder'] == 48}
    need(m['heads_rank48_unhosted'] == 11010 and by.get((8, 'HEAD-literal')) == 6150 and by.get((10, 'HEAD-literal')) == 4860,
         'T74: 11,010 heads (6,150 + 4,860), as the first head test found')
    need(m['remainder_profile'] == {'48': 22748} and g['call_blocks']['global_profile_equals_hub'] and not m['violations'],
         "T74: remainders {48: 22,748}, global profile = that circuit's, no violations")

    print('7. price controls', flush=True)
    prof, N = I['rate']['profile'], I['rate']['N']
    uni = {int(r): n for r, n in prof['children'].items()}
    if cut_of(I) == 'full':          # the uniform profile back: the split halves rejoined, the heads restored
        uni[48] = uni.get(48, 0) + uni.pop(24, 0) // 2 + prof['H']
    else:
        uni[48] = uni.get(48, 0) + uni.pop(24)
    uni = {str(r): n for r, n in sorted(uni.items())}
    cut = full_cut if cut_of(I) == 'full' else half_cut
    c0 = rate(work, 'one', cut(uni, prof['W'], 1), N, expect_rc=1)
    need(not c0['holds_at_N'], 'with a single head the figure is refused')
    c1 = rate(work, 'minus1', cut(uni, prof['W'], prof['H'] - 1), N, expect_rc=1)
    need(not c1['holds_at_N'], 'with one head fewer (%d) the figure is refused' % (prof['H'] - 1))
    u = work / 'profile-unseparated.json'
    if cut_of(I) == 'full':          # the full cut without the split: rank-48 blocks stay while the cut job is 25
        uns = {int(r): n for r, n in prof['children'].items()}
        k = uns.pop(24, 0) // 2
        uns[48] = k if k else prof['H']   # no split blocks (every rank-48 block a head): the heads stay as blocks of 48
        u.write_text(json.dumps(dict(prof, children={str(r): n for r, n in sorted(uns.items())})))
    else:
        u.write_text(json.dumps(dict(prof, kc=25)))
    r = subprocess.run([sys.executable, '-I', '-B', str(TOOLS / 'rate_cert.py'), str(u), str(N)], capture_output=True, text=True)
    need(r.returncode != 0 and 'not separated' in r.stderr, 'a profile that is not separated (job 25 while blocks of 48 stay) is refused')
    c2 = rate(work, 'plus1', prof, N + 1, expect_rc=1)
    need(not c2['holds_at_N'], 'one grid step above the figure (%d/10^10) is refused' % (N + 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--part', choices=['main', 'controls', 'all'], default='all')
    ap.add_argument('--instance', default='2979', help='instances/<id>.json (default 2979, the registered instance)')
    ap.add_argument('--source', default=None, help="folder of the word's package files (default: the instance's path on main)")
    ap.add_argument('--keep', default=None, help='copy the working folder here at the end (must not exist)')
    a = ap.parse_args()
    I = json.loads((PKG / 'instances' / (a.instance + '.json')).read_text())
    src = Path(a.source or I['source_default']).resolve()
    t0 = time.time()
    work = Path(tempfile.mkdtemp(prefix='lever-%s-' % I['id']))
    try:
        if a.part in ('main', 'all'):
            part_main(I, src, work)
        if a.part in ('controls', 'all'):
            part_controls(I, src, work)
        if a.keep:
            shutil.copytree(work, a.keep)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print('PASS_LEVER_MIXED_TARGETS_%s_%s figure %s heads %d seconds %.0f' % (
        I['id'], a.part.upper(), '%.7e' % (I['rate']['N'] / 1e10), I['heads']['total'], time.time() - t0))


if __name__ == '__main__':
    main()
