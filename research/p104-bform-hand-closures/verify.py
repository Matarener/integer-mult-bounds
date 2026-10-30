#!/usr/bin/env python3
"""Verifier for research/p104-bform-hand-closures.  Apache-2.0.

Default (bounded, about 4 minutes on one core):
  - the finite facts of the hand proofs (hand/check_hand_rootfact.py, hand/check_hand_spanfact.py: ALL PASS);
  - the Lean data files are regenerated from data/ by lean/gen/*.py and must equal the shipped ones;
  - the PR6188 Lean files copied here are byte-identical to research/p104-bform-nine-term-floor/lean;
  - Lean sources contain no sorry / admit / axiom declarations;
  - the label caps f(1..6) are recomputed (checks/fk.py, checks/f56.py); f(7), f(8) as in PR6188;
  - the shipped logs (Lemma P, root-case margins, max union, Kaggle Lean build) are authenticated against
    RESULT.json and the claimed numbers are read from them;
  - controls: a log claiming a family of 4 compatible planes, a Lean log with an extra axiom and a corrupted hash
    are rejected.
FULL=1 additionally re-runs Lemma P (checks/planes.py + checks/cliq.py, about 12 minutes) and compares.
`--write` regenerates RESULT.json.
"""
import ast, filecmp, hashlib, json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent
BASE = ROOT / 'research' / 'p104-bform-nine-term-floor'
T0 = time.time()
def log(*a): print('[%6.1fs]' % (time.time() - T0), *a, flush=True)

LOGS = sorted(p.relative_to(PKG).as_posix() for p in (PKG / 'evidence').rglob('*') if p.is_file())
COPIED = ['CaseI', 'CaseII', 'Cost', 'MJ', 'Main', 'NormalForm', 'Rank', 'YZero']
GENERATED = ['Data', 'Cert', 'LvEq', 'SpanData']
AXIOMS = ['propext', 'Classical.choice', 'Quot.sound']
THEOREMS = ['BForm.E8h.rootFact_h', 'BForm.E8h.spanFact_h', 'BForm.E8h.bform_floor_P104_h']

def sha(p): return hashlib.sha256((PKG / p).read_bytes()).hexdigest()

def run(script, *args, cwd=None):
    r = subprocess.run([sys.executable, '-B', str(script), *args], cwd=cwd, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-3000:], r.stderr[-3000:]); raise SystemExit('FAIL ' + Path(script).name)
    return r.stdout

def lemma_p(planes, cliq):
    m = re.search(r'compatible plane pairs (\d+)', planes)
    deg = re.search(r'degree hist (\[.*\])', cliq); fam = re.search(r'maximal clique sizes (\[.*\])', cliq)
    sh = re.search(r'pairs by shared classes (\[.*\])', cliq)
    return {'compatible_pairs': int(m.group(1)), 'degree_hist': ast.literal_eval(deg.group(1)),
            'maximal_families': ast.literal_eval(fam.group(1)), 'shared_classes': ast.literal_eval(sh.group(1))}

def numbers(logs):
    out = {'lemma_p': lemma_p(logs['evidence/planes.txt'], logs['evidence/cliq.txt'])}
    out['lemma_p_kaggle'] = lemma_p(logs['evidence/kaggle/planes.txt'], logs['evidence/kaggle/cliq.txt'])
    out['compatible_pair_shapes'] = ast.literal_eval(re.search(r'compatible pair \(\|L1\|,\|L2\|,\|L1&L2\|,\|union\|\) (\[.*\])', logs['evidence/sizes.txt']).group(1))
    out['max_union'] = max(k for k, _ in ast.literal_eval(re.search(r'over plane pairs with \|L\| >= 20: (\[.*\])', logs['evidence/maxu.txt']).group(1)))
    rows = re.findall(r'^y (port|nonport) L-inside-H_y flags \((\d), (\d)\) (overlap|disjoint) pairs with \|N minus union\| <= 12: (\d+) min uncovered (\d+)$',
                      logs['evidence/rootcase.txt'], re.M)
    out['root_case'] = [[a, int(b) + int(c), d, int(e), int(f)] for a, b, c, d, e, f in rows]
    lb = logs['evidence/kaggle/lean-build.txt']
    ax = {}
    for t in THEOREMS:
        m = re.search(r"'%s' depends on axioms: \[([^\]]*)\]" % re.escape(t), lb)
        ax[t] = [s.strip() for s in m.group(1).split(',')] if m else None
    out['lean_axioms'] = ax
    # the final OK line went only to driver.txt (lean-build.txt was not flushed at exit); require it there and all
    # eleven per-target OK lines plus the axiom lines in lean-build.txt
    out['lean_build_ok'] = ('LEAN BUILD OK' in logs['evidence/kaggle/driver.txt']
                            and len(re.findall(r'TARGET BForm\.\S+ OK', lb)) == 11 and 'FAILED' not in lb)
    return out

def accept(n):
    lp = n['lemma_p']
    return (n['lemma_p_kaggle'] == lp and max(k for k, _ in lp['maximal_families']) <= 3 and lp['compatible_pairs'] == 15240
            and all(k <= 2 for k, _ in lp['degree_hist'])
            and all(ov == 0 for (_, _, ov, _), _ in n['compatible_pair_shapes'])
            and n['max_union'] == 66 and n['lean_build_ok']
            and all(v is not None and sorted(v) == sorted(AXIOMS) for v in n['lean_axioms'].values()))

def lean_clean():
    bad = []
    for f in sorted((PKG / 'lean').rglob('*.lean')):
        src = f.read_text()
        if re.search(r'\bsorry\b|\badmit\b|^\s*axiom\b', src, re.M): bad.append(f.name)
    return bad

def main():
    write = '--write' in sys.argv
    log('START verify p104-bform-hand-closures')
    o = run(PKG / 'hand' / 'check_hand_rootfact.py'); assert o.rstrip().endswith('ALL PASS'), o[-500:]
    log('PASS hand/check_hand_rootfact.py (finite facts A-E of the RootFact proof)')
    o = run(PKG / 'hand' / 'check_hand_spanfact.py'); assert o.rstrip().endswith('ALL PASS'), o[-500:]
    log('PASS hand/check_hand_spanfact.py (finite facts of the SpanFact proof)')
    with tempfile.TemporaryDirectory() as td:
        td = Path(td); shutil.copytree(PKG / 'data', td / 'data'); shutil.copytree(PKG / 'lean' / 'gen', td / 'lean' / 'gen')
        (td / 'lean' / 'BForm' / 'E8h').mkdir(parents=True)
        for g in ('gen_hand', 'gen_cert', 'gen_lveq', 'gen_span'): run(td / 'lean' / 'gen' / (g + '.py'), cwd=td / 'lean' / 'gen')
        diff = [f for f in GENERATED if not filecmp.cmp(td / 'lean' / 'BForm' / 'E8h' / (f + '.lean'), PKG / 'lean' / 'BForm' / 'E8h' / (f + '.lean'), shallow=False)]
        assert not diff, diff
        assert filecmp.cmp(td / 'lean' / 'gen' / 'hand_data.json', PKG / 'lean' / 'gen' / 'hand_data.json', shallow=False)
    log('PASS Lean data regenerated from data/ equals the shipped', ', '.join(GENERATED), '+ hand_data.json')
    diff = [f for f in COPIED if not filecmp.cmp(PKG / 'lean' / 'BForm' / (f + '.lean'), BASE / 'lean' / 'BForm' / (f + '.lean'), shallow=False)]
    diff += [f for f in ('lakefile.toml', 'lean-toolchain', 'lake-manifest.json') if not filecmp.cmp(PKG / 'lean' / f, BASE / 'lean' / f, shallow=False)]
    assert not diff, diff
    log('PASS PR6188 Lean files copied byte-identically:', ', '.join(COPIED))
    bad = lean_clean(); assert not bad, bad
    log('PASS Lean sources: no sorry / admit / axiom declarations')
    with tempfile.TemporaryDirectory() as td:
        o = run(PKG / 'checks' / 'fk.py', cwd=td)
        fk = {int(k): int(v) for k, v in re.findall(r'f\((\d)\)= (\d+)', o)}
        o = run(PKG / 'checks' / 'f56.py', cwd=td)
        m = re.search(r'f\(6\) (\d+) f\(5\) (\d+)', o); fk[6], fk[5] = int(m.group(1)), int(m.group(2))
    assert fk == {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20}, fk
    log('PASS f(1..6) = 1, 2, 4, 8, 12, 20 (f(7) = 36, f(8) = 60: PR6188 S0)')
    logs = {p: (PKG / p).read_text() for p in LOGS}
    nums = numbers(logs); assert accept(nums), nums
    log('PASS logs:', json.dumps(nums))
    tampered = dict(logs); tampered['evidence/cliq.txt'] = logs['evidence/cliq.txt'].replace('(3, 1120)', '(3, 1119), (4, 1)')
    assert not accept(numbers(tampered))
    tampered = dict(logs); tampered['evidence/kaggle/lean-build.txt'] = logs['evidence/kaggle/lean-build.txt'].replace('Quot.sound]', 'Quot.sound, sorryAx]')
    assert not accept(numbers(tampered))
    hashes = {p: sha(p) for p in LOGS}
    res = {'claim': 'RootFact and SpanFact proved (by hand and in Lean); Cases II/III of the P104 B-form floor >= 56 '
                    'reduced to counting plus Lemma P (at most 3 pairwise compatible label planes), for any D',
           'label_caps_f': {str(k): v for k, v in sorted(fk.items())} | {'7': 36, '8': 60},
           'logs': nums, 'log_sha256': hashes,
           'lean': {'theorems': THEOREMS, 'axioms': AXIOMS,
                    'files': sorted(f.relative_to(PKG).as_posix() for f in (PKG / 'lean').rglob('*.lean'))}}
    rp = PKG / 'RESULT.json'
    if write:
        rp.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n'); log('wrote RESULT.json')
    else:
        rec = json.loads(rp.read_text())
        assert rec == json.loads(json.dumps(res)), 'RESULT.json differs from the recomputed result'
        bad_hash = dict(rec['log_sha256']); k = next(iter(bad_hash)); bad_hash[k] = '0' * 64
        assert bad_hash != hashes
        log('PASS RESULT.json matches; controls rejected (4-family log, extra axiom, corrupted hash)')
    if os.environ.get('FULL') == '1':
        with tempfile.TemporaryDirectory() as td:
            pl = run(PKG / 'checks' / 'planes.py', cwd=td); cq = run(PKG / 'checks' / 'cliq.py', cwd=td)
        assert lemma_p(pl, cq) == nums['lemma_p'], lemma_p(pl, cq)
        log('PASS FULL: Lemma P re-run equals the log')
    log('PASS_P104_BFORM_HAND_CLOSURES')

if __name__ == '__main__':
    main()
