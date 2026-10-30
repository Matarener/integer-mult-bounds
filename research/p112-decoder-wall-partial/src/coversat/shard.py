#!/usr/bin/env python3
"""One COVERSAT shard: generate the CNF, solve with kissat (DRAT proof), check the proof with drat-trim.
usage: shard.py ORBIT LAM(e.g. 4,2,1) WORKDIR [--cuts POOL.json] [--it N] [--sha SHA256] [--certs LIST.json]
  without --cuts: the pure cover model (stage 1).  With --cuts: cover model + ratio lemma + exact Lemma-B rank cuts from the pool
  (a list of [X, Y] bitmask pairs for this orbit), as in cutenc.build_cuts.
Prints one line  SHARD <name> <UNSAT|SAT|UNKNOWN> <VERIFIED|NOPROOF|FAIL> vars=.. clauses=.. sha256=.. kissat=..s drat=..s"""
import sys, os, json, time, hashlib, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from enc import build, write
o = int(sys.argv[1]); lam = [int(x) for x in sys.argv[2].split(',')]; work = sys.argv[3]
cuts = None; want = None
if '--cuts' in sys.argv: cuts = [tuple(x) for x in json.load(open(sys.argv[sys.argv.index('--cuts') + 1]))]
if '--sha' in sys.argv: want = sys.argv[sys.argv.index('--sha') + 1]
os.makedirs(work, exist_ok=True)
name = 'o%d_b%d_%s%s' % (o, sum(lam), ''.join(map(str, lam)), '_cuts' if cuts is not None else '')
cnf = os.path.join(work, name + '.cnf'); prf = os.path.join(work, name + '.drat')
if cuts is None: c, S, B = build(o, lam)
else:
    from cutenc import build_cuts
    c, S, B = build_cuts(o, lam, cuts)
it = int(sys.argv[sys.argv.index('--it') + 1]) if '--it' in sys.argv else 0
certs = []
if '--certs' in sys.argv:       # list of Nullstellensatz certificate files (JSON paths): checked, then turned into no-good clauses
    from nogoods import check_cert, core_images
    for cp in json.load(open(sys.argv[sys.argv.index('--certs') + 1])):
        cj = json.load(open(cp)); assert cj['orbit'] == o and len(cj['pats']) == len(lam)
        assert check_cert(o, cj['pats'], cj['cells'], cj['cert']), 'bad certificate ' + os.path.basename(cp)
        for lits in core_images(o, lam, cj['pats'], [tuple(x) for x in cj['cells']]): c.add([-l for l in lits])
        certs.append(os.path.basename(cp))
write(c, cnf, ('COVERSAT-CEGAR2 o%d_b%d_%s it %d cuts %d certs 0 cube []' % (o, sum(lam), ''.join(map(str, lam)), it, len(cuts))) if cuts is not None else 'COVERSAT orbit %d lam %s sing True cube None%s; S vars k,t,s -> 1 + 64k + 8t + s for k < %d' % (o, lam, '' if o == 0 else ' sym True ferrers True', len(lam)))
sha = hashlib.sha256(open(cnf, 'rb').read()).hexdigest()
if want and want != sha: print('SHARD', name, 'CNF_SHA_MISMATCH', sha); sys.exit(2)
kissat = os.environ.get('KISSAT') or shutil.which('kissat'); dt = os.environ.get('DRAT_TRIM') or shutil.which('drat-trim')
assert kissat and dt, 'need kissat and drat-trim (see README)'
t0 = time.time(); r = subprocess.run([kissat, '-q', cnf, prf], capture_output=True, text=True); t1 = time.time() - t0
status = 'UNSAT' if r.returncode == 20 else 'SAT' if r.returncode == 10 else 'UNKNOWN'
ver = 'NOPROOF'; t2 = 0
if status == 'UNSAT':
    t0 = time.time(); d = subprocess.run([dt, cnf, prf, '-t', '3000'], capture_output=True, text=True); t2 = time.time() - t0
    ver = 'VERIFIED' if 's VERIFIED' in d.stdout else 'FAIL'
print('SHARD %s %s %s certs=%d vars=%d clauses=%d sha256=%s kissat=%.0fs drat=%.0fs' % (name, status, ver, len(certs), c.n, len(c.cl), sha, t1, t2), flush=True)
for f in (cnf, prf):
    if os.path.exists(f): os.remove(f)
sys.exit(0 if (status == 'UNSAT' and ver == 'VERIFIED') else 1)
