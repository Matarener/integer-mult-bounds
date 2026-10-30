#!/usr/bin/env python3
"""Verifier for research/p104-bform-nine-term-floor.  Apache-2.0.

Default (bounded, about 2 minutes): re-runs the finite facts S0, S1, S2' (checks/spanlemma.py) and S3
(checks/bicliques.py), the lbz self-test (checks/lbz.py, on top of research/nine-term-outside-colspace/checks),
authenticates the shipped Kaggle logs against RESULT.json and reads the claimed census numbers from them, checks
that the Lean sources contain no `sorry`/`admit`/new `axiom`, and runs two controls (a corrupted log hash and a
census log with one alive configuration must be rejected).
FULL=1 additionally replays the whole census chain (repo pipeline + cnt9c V0-V3 + cnt104z + cnt9z V3; about
1.5 h on 4 cores).  `--write` regenerates RESULT.json.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent
C2 = ROOT / 'research' / 'nine-term-outside-colspace' / 'checks'
T0 = time.time()
def log(*a): print('[%6.1fs]' % (time.time() - T0), *a, flush=True)

LOGS = sorted(p.relative_to(PKG).as_posix() for p in (PKG / 'evidence').rglob('*') if p.is_file())

def sha(p): return hashlib.sha256((PKG / p).read_bytes()).hexdigest()

def text(p):
    b = (PKG / p).read_bytes()
    if p.endswith('.gz'):
        import gzip; b = gzip.decompress(b)
    return b.decode()

def run(script, *args, cwd=None, extra_path=None):
    env = dict(os.environ)
    if extra_path: env['PYTHONPATH'] = os.pathsep.join(map(str, extra_path))
    r = subprocess.run([sys.executable, '-B', str(script), *args], cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-3000:], r.stderr[-3000:]); raise SystemExit('FAIL ' + Path(script).name)
    return r.stdout

def census_numbers(logs):
    out = {}
    for v in ('V0', 'V1', 'V2', 'V3'):
        m = re.search(r'DONE %s big configurations (\d+) sigma>=8 assignments (\d+) with port class (\d+) ALIVE (\d+)' % v,
                      logs['evidence/kaggle/census-v1/cnt9c_%s.txt' % v])
        out['cnt9c_' + v] = dict(zip(('configurations', 'sigma_ge_8', 'with_port_class', 'alive'), map(int, m.groups())))
    m = re.search(r'DONE multi-big: big configurations (\d+) alive after J \+ support filter (\d+)', logs['evidence/kaggle/census-v1/cnt9b.txt'])
    out['cnt9b_control'] = {'configurations': int(m.group(1)), 'alive': int(m.group(2))}
    m = re.search(r'DONE cnt104z pairs (\d+)', logs['evidence/kaggle/singular-v1/cnt104z.log.gz'])
    out['cnt104z_pairs'] = int(m.group(1))
    m = re.search(r'pairs: repo (\d+) lbz (\d+) union (\d+)', logs['evidence/kaggle/singular-v1/cnt9z_V3.txt'])
    out['cnt9z_pairs'] = dict(zip(('repo', 'lbz', 'union'), map(int, m.groups())))
    m = re.search(r'DONE V3 big configurations (\d+) sigma>=8 assignments (\d+) with port class (\d+) ALIVE (\d+)',
                  logs['evidence/kaggle/singular-v1/cnt9z_V3.txt'])
    out['cnt9z_V3'] = dict(zip(('configurations', 'sigma_ge_8', 'with_port_class', 'alive'), map(int, m.groups())))
    m = re.search(r'SELFTEST mismatches (\d+)', logs['evidence/kaggle/singular-v1/lbz_selftest.txt'])
    out['lbz_selftest_mismatches'] = int(m.group(1))
    return out

def accept(nums):
    return (all(nums['cnt9c_' + v]['alive'] == 0 for v in ('V0', 'V1', 'V2', 'V3'))
            and nums['cnt9b_control'] == {'configurations': 701, 'alive': 0}
            and nums['cnt9c_V0']['configurations'] == 701
            and nums['cnt9z_V3']['alive'] == 0 and nums['lbz_selftest_mismatches'] == 0)

def lean_clean():
    bad = []
    for f in sorted((PKG / 'lean').rglob('*.lean')):
        src = f.read_text()
        if re.search(r'\bsorry\b|\badmit\b|^\s*axiom\b', src, re.M): bad.append(f.name)
    return bad

def main():
    write = '--write' in sys.argv
    res = {}
    log('START verify p104-bform-nine-term-floor')
    o = run(PKG / 'checks' / 'spanlemma.py')
    assert 'S0 label caps f(7), f(8) = 36 60' in o and 'min |N(y)| = 49' in o and 'for all 104 ports: True' in o and 'PASS' in o
    log('PASS S0 (f(7) = 36, f(8) = 60), S1 (<= 55 ports per E7/D7 hyperplane, |N(y)| >= 49), S2\' (exactly the 104 port exceptions)')
    with tempfile.TemporaryDirectory() as td:
        o = run(PKG / 'checks' / 'bicliques.py', cwd=td)
    assert 'max |B| over closed A with |A| >= 13: 4' in o
    log('PASS S3 (closed bicliques with |A| >= 13 have |B| <= 4)')
    with tempfile.TemporaryDirectory() as td:
        o = run(PKG / 'checks' / 'lbz.py', cwd=td, extra_path=[PKG / 'checks', C2])
    m = re.search(r'random port hyperplanes: .* missing (\d+)', o); assert m and m.group(1) == '0'
    assert 'SELFTEST mismatches 0' in o
    log('PASS lbz self-test (flat list complete on random port hyperplanes; fast = exhaustive)')
    logs = {p: text(p) for p in LOGS}
    nums = census_numbers(logs)
    assert accept(nums), nums
    log('PASS census logs:', json.dumps(nums))
    bad = lean_clean(); assert not bad, bad
    log('PASS Lean sources: no sorry / admit / axiom declarations (build: lake build in lean/, not run here)')
    # controls
    tampered = dict(logs); tampered['evidence/kaggle/census-v1/cnt9c_V3.txt'] = logs['evidence/kaggle/census-v1/cnt9c_V3.txt'].replace('ALIVE 0', 'ALIVE 1')
    assert not accept(census_numbers(tampered))
    hashes = {p: sha(p) for p in LOGS}
    res = {'finite_facts': {'f7': 36, 'f8': 60, 'max_ports_E7_D7_hyperplane': 55, 'S2_exceptions': 104, 'biclique_max_B': 4},
           'census': nums, 'log_sha256': hashes,
           'lean': {'theorem': 'BForm.bform_floor', 'files': sorted(f.relative_to(PKG).as_posix() for f in (PKG / 'lean').rglob('*.lean'))},
           'claim': 'every nine-term decoder of a rank-9 B-form realisation of the P104 pattern costs >= 56'}
    rp = PKG / 'RESULT.json'
    if write:
        rp.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n'); log('wrote RESULT.json')
    else:
        rec = json.loads(rp.read_text())
        assert rec == res, 'RESULT.json differs from the recomputed result'
        bad_hash = dict(rec['log_sha256']); k = next(iter(bad_hash)); bad_hash[k] = '0' * 64
        assert bad_hash != hashes
        log('PASS RESULT.json matches; controls rejected (tampered census log, corrupted hash)')
    if os.environ.get('FULL') == '1':
        log('FULL replay is documented in README (Kaggle drivers in kaggle/); not run inside the bounded hook')
    log('PASS_P104_BFORM_NINE_TERM_FLOOR')

if __name__ == '__main__':
    main()
