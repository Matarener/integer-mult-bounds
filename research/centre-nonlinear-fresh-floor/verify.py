#!/usr/bin/env python3
"""Nonlinear/adaptive centre sharing: fresh-information floor and packing screen.

Checks, from the repository root:
1. premise: replays research/centre-history-innovation/verify.py unchanged in an isolated
   subprocess and binds its PASS line and receipt digest (Q(ker H) = M^8 under its premises);
2. sharpness of the finite-precision count (Theorem 2): on small dyadic grids, Kronecker packing
   of k b-bit coordinates into one word is injective exactly when the word has >= k*b bits;
3. packing screen: exact ceiling brackets of research/complex-local-word-ceiling/ceiling.py for
   regrouping the 64 centre mass into larger children, with mass conservation asserted;
4. controls: halving the centre information reproduces the x1.90 lever; a rank-73 child, a
   mass-changing pack and a corrupted predecessor digest are rejected.

usage: verify.py [--write]   (--write regenerates RESULT.json)
Mark (Matarener), with substantial Claude (Anthropic) assistance. Apache-2.0.
"""
import argparse
import importlib.util
import itertools
import json
import subprocess
import sys
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRED = ROOT / 'research/centre-history-innovation'
CEIL = ROOT / 'research/complex-local-word-ceiling/ceiling.py'
M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Q(1, 10 ** 12)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT / row['path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['path'])
    return pins['base_commit']


def premise():
    """Replay the predecessor verifier and bind its receipt digest."""
    out = subprocess.run([sys.executable, '-I', '-B', str(PRED / 'verify.py')], cwd=ROOT,
                         capture_output=True, text=True, timeout=300)
    need(out.returncode == 0, 'predecessor verifier failed: ' + out.stderr[-400:])
    line = out.stdout.strip().splitlines()[-1]
    expected = json.loads((PRED / 'RESULT.json').read_text(encoding='utf-8'))['sha256']
    need(line == 'PASS_CENTRE_HISTORY_INNOVATION sha256=' + expected, 'predecessor receipt: ' + line)
    return expected


def digest_matches(line, expected):
    return line == 'PASS_CENTRE_HISTORY_INNOVATION sha256=' + expected


def packing_sharpness():
    """Kronecker packing of k b-bit values into one w-bit word: injective iff w >= k*b."""
    rows = []
    for k, b in [(2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (4, 1)]:
        vals = list(itertools.product(range(1 << b), repeat=k))
        for w in range(1, k * b + 1):
            # best possible map into w bits: pigeonhole bound on distinct images
            injective_possible = len(vals) <= (1 << w)
            need(injective_possible == (w >= k * b), 'counting bound')
        packed = {sum(v << (b * i) for i, v in enumerate(t)) for t in vals}
        need(len(packed) == len(vals) and max(packed) < (1 << (k * b)), 'Kronecker packing attains k*b')
        # the same packing truncated to k*b-1 bits collides
        trunc = {p & ((1 << (k * b - 1)) - 1) for p in packed}
        need(len(trunc) < len(vals), 'one bit short collides')
        rows.append([k, b, len(vals)])
    return rows


def load_ceiling():
    spec = importlib.util.spec_from_file_location('imb_ceiling', CEIL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def screen(C):
    def cap(local, centre=64):
        return C.ceiling(local, M, FAM, ST, centre, grid=GRID)

    base_mass = sum(r * n for r, n in WORD.items())
    rest = {r: n for r, n in WORD.items() if r != 8}
    cases = [('selected 8 x rank-8', WORD)]
    for k in (2, 4, 8):
        cases.append((f'pack {k} totals: {8 // k} x rank-{8 * k}', {**rest, 8 * k: Q(8, k)}))
    cases.append(('ideal regroup: fractional rank-72', {**rest, 72: Q(64, 72)}))
    rows = []
    base = None
    for name, local in cases:
        need(sum(r * Q(n) for r, n in local.items()) == base_mass, 'packing conserves mass: ' + name)
        lo, hi = cap(local)
        base = hi if base is None else base
        rows.append(dict(name=name, local={str(r): str(n) for r, n in sorted(local.items())},
                         a_lo=str(lo), a_hi=str(hi), ratio_hi=f'{float(hi / base):.9f}'))
    best = max(Q(r['a_hi']) for r in rows)
    need(best / base < Q(1007, 1000), 'packing ceiling below +0.7%')
    return rows, best / base


def controls(C, base_hi):
    out = []
    lo, hi = C.ceiling({**WORD, 8: 4}, M, FAM, ST, 32, grid=GRID)
    ratio = hi / base_hi
    need(Q(19, 10) < ratio < Q(191, 100), 'two-call halving lever reproduces x1.90')
    out.append(['halved_centre_information_x1.90', str(hi), f'{float(ratio):.6f}'])
    try:
        C.ceiling({**{r: n for r, n in WORD.items() if r != 8}, 73: Q(64, 73)}, M, FAM, ST, 64, grid=GRID)
        raise AssertionError('rank-73 child accepted')
    except ValueError:
        out.append(['rank_73_child_rejected'])
    rest = {r: n for r, n in WORD.items() if r != 8}
    try:
        local = {**rest, 16: 2}  # packs 8 totals into 2 rank-16 words: loses half the bits
        need(sum(r * Q(n) for r, n in local.items()) == sum(r * n for r, n in WORD.items()), 'mass')
        raise AssertionError('mass-losing pack accepted')
    except ValueError:
        out.append(['mass_losing_pack_rejected'])
    need(not digest_matches('PASS_CENTRE_HISTORY_INNOVATION sha256=' + '0' * 64, '1' * 64),
         'corrupted digest rejected')
    out.append(['corrupted_predecessor_digest_rejected'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    base_commit = check_sources()
    digest = premise()
    sharp = packing_sharpness()
    C = load_ceiling()
    rows, best = screen(C)
    ctl = controls(C, Q(rows[0]['a_hi']))
    result = dict(base_commit=base_commit, predecessor_receipt=digest, packing_sharpness=sharp,
                  screen=rows, best_packing_ratio=f'{float(best):.9f}', controls=ctl)
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(text, encoding='utf-8', newline='\n')
    need(path.read_text(encoding='utf-8') == text, 'RESULT.json mismatch (run with --write)')
    print(f'PASS_CENTRE_NONLINEAR_FRESH_FLOOR premise={digest[:12]} packing_best=x{float(best):.6f} '
          f'controls={len(ctl)} no_new_kappa')


if __name__ == '__main__':
    main()
