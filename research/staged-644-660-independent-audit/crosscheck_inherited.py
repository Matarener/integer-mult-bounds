#!/usr/bin/env python3
"""Optional differential check (not part of the registered replay or of the independent evidence).

Compares this package's forward/dual endpoint verdicts with the inherited
PR3133 `audit_local.walg_apply` contract on random mutants of the PR3605 base
word, to detect any misreading of the contract.  It deliberately imports the
inherited auditor from main, so it is a fidelity check, not an independent one.
Usage: python3 -I -B crosscheck_inherited.py SEED TRIALS (expected: disagree 0).

Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import copy, gzip, json, random, sys, types
from fractions import Fraction as Q
from pathlib import Path
PKG = Path(__file__).resolve().parent
REPO = PKG.parents[1]
sys.path.insert(0, str(PKG))
import audit_core as C
import hashlib
src = REPO / 'research/rank7-coupled-586-588-carrier-fold/vendor/audit_local.py'
if hashlib.sha256(src.read_bytes()).hexdigest() != 'a38940094f7d19cd6376aafdd4734fa68eabc9aff4c98c3c4a3e9540328b1c90':
    raise SystemExit('inherited auditor differs from the PR3605-pinned bytes')
audit = types.ModuleType('inherited'); audit.__file__ = str(src)
exec(compile(src.read_bytes(), str(src), 'exec'), audit.__dict__)

# Program assembly follows the endpoint driver in PR3605 verify.py (RossRichardson), for a like-for-like comparison.
def inherited_endpoint(word, dual):
    live = sorted(set(range(704)) - set(word['removed'])); restored = set(map(int, word['helper_final']))
    rows = {r: {(r, ()): Q(1)} for r in live}; rows.update({r + 704: {} for r in restored})
    program = [['corr', c['target'], c['source'], tuple(c['operator_word']), Q(c['coefficient'])] for c in word['initial_corrections']]
    program += word['precondition'] + word['compensation'] + word['A'] + word['cut']; warps = {}
    for op, rec in enumerate(word['warps'], 1): warps.setdefault(rec[0], []).append(['warp', rec[1], op])
    for i in range(len(word['B']) + 1):
        program += warps.get(i, [])
        if i < len(word['B']): program.append(word['B'][i])
    program += word['restore'] + word['cleanup']
    for g in program: audit.walg_apply(g, rows, dual, 10 ** 6)
    expected = {r: {(r, ()): Q(1)} for r in live}
    for t in range(112): expected[t if dual else 112 + t][(112 + t if dual else t, ())] = Q(-1 if dual else 1)
    bad = [r for r in live if rows[r] != expected[r]]; dirty = [r for r in restored if rows[r + 704]]
    return not bad and not dirty

def mine(word, dual):
    rows = C.forward_rows(word, dual=dual, symbolic_buffers=False)
    bad, dirty, leaks, _ = C.endpoint_defects(word, rows, dual=dual)
    return not bad and not dirty and not leaks

w0 = json.loads(gzip.decompress((PKG / 'inputs/STAGED644-660-base.json.gz').read_bytes()))
rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 3605)
agree = disagree = 0; kinds = {}
for trial in range(int(sys.argv[2]) if len(sys.argv) > 2 else 40):
    w = copy.deepcopy(w0); kind = rng.choice(['flipB', 'dropB', 'swapB', 'coefB', 'flipcleanup', 'dropcorr', 'flipcorr', 'none', 'dropcleanupwarp', 'swapwarppos'])
    regen = True
    if kind == 'flipB':
        i = rng.choice([i for i, g in enumerate(w['B']) if g[0] == 'add']); w['B'][i][3] *= -1
    elif kind == 'dropB':
        i = rng.randrange(len(w['B'])); w['B'].pop(i)
        for rec in w['warps']:
            if rec[0] > i: rec[0] -= 1
    elif kind == 'swapB':
        i = rng.randrange(len(w['B']) - 1); w['B'][i], w['B'][i + 1] = w['B'][i + 1], w['B'][i]
    elif kind == 'coefB':
        i = rng.choice([i for i, g in enumerate(w['B']) if g[0] == 'add']); w['B'][i][4] *= 2
    elif kind == 'flipcleanup':
        regen = False; i = rng.choice([i for i, g in enumerate(w['cleanup']) if g[0] == 'add']); w['cleanup'][i][3] *= -1
    elif kind == 'dropcleanupwarp':
        regen = False; i = rng.choice([i for i, g in enumerate(w['cleanup']) if g[0] == 'warp']); w['cleanup'].pop(i)
    elif kind == 'dropcorr':
        w['initial_corrections'].pop(rng.randrange(len(w['initial_corrections'])))
    elif kind == 'flipcorr':
        c = w['initial_corrections'][rng.randrange(len(w['initial_corrections']))]; c['coefficient'] = str(-Q(c['coefficient']))
    elif kind == 'swapwarppos':
        k = rng.randrange(len(w['warps'])); w['warps'][k][0] = max(0, w['warps'][k][0] - 1)
    if regen: w['cleanup'] = C.derive_cleanup(w)
    for dual in (False, True):
        a, b = mine(w, dual), inherited_endpoint(w, dual)
        kinds.setdefault(kind, []).append((dual, a, b))
        if a == b: agree += 1
        else: disagree += 1; print('DISAGREE', trial, kind, dual, a, b)
print('agree', agree, 'disagree', disagree)
if disagree:
    raise SystemExit('verdicts disagree with the inherited contract')
print({k: sum(1 for d, a, b in v if a) for k, v in kinds.items()}, {k: len(v) for k, v in kinds.items()})
