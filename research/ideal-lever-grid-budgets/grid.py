#!/usr/bin/env python3
"""Ideal combined-lever budget grid for the selected complex local word.

Extends `research/complex-local-word-ceiling/levers.py` (seven one-at-a-time rows)
to the full grid of the three published lever families:

  * centre charge   c in {64 selected, 32 shared-by-two-calls, 0 free};
  * local shape     word (published profile), or all non-centre paid mass delivered
                    as (fractional) children of rank r in {8, 16, 32};
  * unpaid coords   u in {1 coverage law, 2 what-if changed coverage law};

plus the two three-lever rows that combine u = 2 with centre-free/shared and rank 16.

Every row keeps the parent premises: m = 73, 896 live families over nine stages
(w = 896/9 live families per call), outer halving guard R = 51, fractional idle
remainder at rank R, paid centre charge c in the coverage identity. The ceiling is
the exact rational bracket of the parent `ceiling()` at grid 1e-12; the reported
a_cap is the certified upper grid point, kappa_cap = a_cap / (1 + a_cap) under the
retained balanced reduction.

These are ideal favorable relaxations for planning and screening, exactly like the
published lever rows: every row omits whatever cost realizing the lever would add
elsewhere, needs an actual word/contract on both suppliers and all-size admission,
and establishes no kappa, supplier or frontier change.

Douglas Colkitt's ceiling model; grid built by Nick Petalas with AI assistance.
Apache-2.0.
"""
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'complex-local-word-ceiling'))
import ceiling as C  # noqa: E402

M, FAM, ST = 73, 896, 9
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
MASS = sum(r * n for r, n in WORD.items())  # 5586
GRID = Q(1, 10 ** 12)
TARGET = Q(1, 99)  # ambitious planning saving

# centre variants: (tag, charge, rank-8 centre copies per call)
CENTRES = [('sel', 64, 8), ('shr', 32, 4), ('free', 0, 0)]
# local shapes: 'word' keeps the published non-centre profile; else rank r
SHAPES = ['word', 8, 16, 32]
UNPAID = [1, 2]


def profile(centre_tag, shape):
    """Per-call paid profile (dict rank -> Fraction count) for one centre/shape cell.

    The sel rows reproduce the parent levers exactly: at centre charge 64 the whole
    local mass (including the centre products) is delivered as rank-r children. When
    centre copies are retained (shared) or removed (free), only the non-centre mass
    5522 is reshaped; retained shared copies stay rank-8 children.
    """
    charge, copies = next((c, k) for t, c, k in CENTRES if t == centre_tag)
    prof = {}
    if shape == 'word':
        for r, n in WORD.items():
            prof[r] = Q(copies if r == 8 else n)
    elif centre_tag == 'sel':
        prof[shape] = Q(MASS, shape)
    else:
        if copies:
            prof[8] = Q(copies)
        prof[shape] = prof.get(shape, Q(0)) + Q(MASS - 64, shape)
    prof = {r: n for r, n in prof.items() if n > 0}
    mass = sum(r * n for r, n in prof.items())
    assert mass == {64: MASS, 32: MASS - 32, 0: MASS - 64}[charge], (centre_tag, shape, mass)
    return prof, charge


def row(centre_tag, shape, unpaid, grid=GRID):
    prof, charge = profile(centre_tag, shape)
    lo, hi = C.ceiling(prof, M, FAM, ST, charge, grid=grid, unpaid=unpaid)
    return lo, hi


def compute_rows():
    rows = []
    for centre_tag, _, _ in CENTRES:
        for shape in SHAPES:
            for unpaid in UNPAID:
                lo, hi = row(centre_tag, shape, unpaid)
                rows.append(dict(centre=centre_tag, shape=str(shape), unpaid=unpaid,
                               a_lo=str(lo), a_hi=str(hi),
                               kappa_hi=str(hi / (1 + hi))))
    return rows


def main():
    rows = compute_rows()
    base = next(Q(r['a_hi']) for r in rows
                if (r['centre'], r['shape'], r['unpaid']) == ('sel', 'word', 1))
    for r in rows:
        a = Q(r['a_hi'])
        print(f"centre={r['centre']:>4s} shape={r['shape']:>4s} unpaid={r['unpaid']} "
              f"a_cap={float(a):.9f} x{float(a / base):.3f} "
              f"kappa_cap={float(Q(r['kappa_hi'])):.9f} "
              f"target={float(TARGET):.6f} {'REACHES' if a / (1 + a) >= TARGET else 'no'}")


if __name__ == '__main__':
    main()
