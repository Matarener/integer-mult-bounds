#!/usr/bin/env python3
"""DEG2C coverage proof: the K=6 MODE 0 run of d2fix covers every (type, L_0-orbit-rep shard) exactly once by an rc=0 output.
A job `d2fix 6 0 TYPE 1 SH NS` handles the L_0 orbit reps with index ri % NS == SH.  Leaf jobs (rc=0 outputs in out/fix: NS=8,
out/fix2: NS=32, out/fix4: NS=128) must tile Z/128 for each of the 5 types: every residue r mod 128 lies in exactly one leaf (r % NS == SH).
Outputs ending rc=124 or without an rc line (killed) carry no verdict and are listed but not used.  Prints PASS/FAIL; exit 1 on FAIL.
usage: coverage.py [OUTDIR]   |   coverage.py --leaves   (prints the leaf jobs 'TYPE SHARD NS NAME' to rerun)"""
import re, sys, os, glob
H = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith('--')]
O = os.path.abspath(args[0]) if args else os.path.join(H, 'out')   # optional: a fresh rerun directory with the same layout
TYPES = {1: 'D7', 2: 'A7', 3: 'E6A1', 4: 'E6', 5: 'D6'}
bad = []; leaves = {}; skipped = []; total_final = 0; nleaf = 0
jobs = {}
for d in ('fix2', 'fix4'):                      # cross-check the NS/SH recorded in the job lists against file names
    for ln in open(os.path.join(O, d, 'jobs.txt')):
        p = ln.split()
        if len(p) >= 7: jobs[(d, p[6])] = (int(p[2]), int(p[4]), int(p[5]), p[0], p[1], p[3])
for d in ('fix', 'fix2', 'fix4'):
    for f in sorted(glob.glob(os.path.join(O, d, 't*.out'))):
        b = os.path.basename(f)
        if d == 'fix':                           # first run: NS=8, name tTsS
            m = re.match(r't(\d)s(\d)\.out$', b)
            if not m: bad.append('unparsed ' + f); continue
            t, sh, ns = int(m.group(1)), int(m.group(2)), 8
        else:                                    # reruns: TYPE, SHARD, NS taken from the job list, cross-checked with the name
            j = jobs.get((d, b[:-4])); m = re.match(r't(\d)s(\d+)_(\d+)', b)
            if j is None or not m or j[3:] != ('6', '0', '1'): bad.append('no/odd job entry for ' + f); continue
            t, sh, ns = j[0], j[1], j[2]
            if int(m.group(1)) != t or sh != int(m.group(3)) and d == 'fix2': bad.append('name/job mismatch ' + b)
            if sh % 8 != int(m.group(2)) % 8 or (d == 'fix4' and sh % 32 != int(m.group(3))): bad.append('shard not inside parent ' + b)
        lines = open(f).read().splitlines()
        rc = lines[-1] if lines and lines[-1].startswith('rc=') else None
        if rc != 'rc=0': skipped.append((d + '/' + b, rc or 'no rc line (killed)')); continue
        ty = [l for l in lines if l.startswith('TYPE ')]
        if len(ty) != 1 or not ty[0].startswith('TYPE %s:' % TYPES[t]): bad.append('type line wrong in ' + f); continue
        fm = re.search(r'\| final (\d+)$', ty[0])
        if not fm or not re.search(r'K=6 states: .*seven7 size \d+ cov \d+', ty[0]): bad.append('no final in ' + f); continue
        total_final += int(fm.group(1)); nleaf += 1
        leaves.setdefault(t, []).append((ns, sh, d + '/' + b, int(fm.group(1))))
if '--leaves' in sys.argv:
    for t in sorted(leaves):
        for ns, sh, n, _ in sorted(leaves[t], key=lambda x: (-x[0], x[1])): print(t, sh, ns, n[:-4].replace('/', ' '))
    sys.exit(0)
print('type  residues(mod 128) covered exactly once   leaf shards (NS:SH)')
for t in sorted(TYPES):
    cnt = [0] * 128
    for ns, sh, _, _ in leaves.get(t, []):
        for r in range(128):
            if r % ns == sh: cnt[r] += 1
    ok = all(c == 1 for c in cnt)
    if not ok: bad.append('type %s coverage: %d residues uncovered, %d multiply covered' % (TYPES[t], cnt.count(0), sum(c > 1 for c in cnt)))
    desc = ' '.join('%d:%d%s' % (ns, sh, '' if ns == 8 else '*') for ns, sh, _, _ in sorted(leaves.get(t, []), key=lambda x: (x[1] % 8, x[0], x[1])))
    print('%-5s %s  %d leaves  %s' % (TYPES[t], 'COMPLETE' if ok else 'GAP', len(leaves.get(t, [])), desc))
print('non-verdict outputs (rc=124 or killed; not used, their residues are tiled by finer leaves): %d' % len(skipped))
for n, r in skipped: print('   %-22s %s' % (n, r))
print('leaf shards with rc=0: %d; sum of "final" six-set counts over them: %d' % (nleaf, total_final))
if total_final: bad.append('nonzero six-set count %d' % total_final)
if bad:
    print('FAIL DEG2C coverage: ' + '; '.join(bad)); sys.exit(1)
print('PASS DEG2C coverage: all 5 types tiled exactly once by %d rc=0 shards; six-set count = %d' % (nleaf, total_final))
