# Every width on the length-8 cycle meets the touching diameter

Widths 1 and 2 already meet the diameter of the survivors that touch an
arc. Widths 3 and 4 do too. On this circle there is no width for which a
proper arc falls short of that diameter.

No new kappa is claimed. Boundary order is not decided here.

## The cap

A survivor farther than the width from the arc has no coupling into the
pivot, so its Schur row is copied from `H`. Every farther nonzero entry
joins two survivors that meet the arc. The circular bandwidth is at most
the diameter of that touching set.

The cycle used here has diagonal 1 and equal negative entries at every
positive distance up to the width, scaled so the off-diagonal infinity
norm is `1/2`. The antipode is counted once, so width 4 has seven
neighbors and entry `-1/14`. For every width from 1 through 4, every
rotation, and every proper arc length, the complement meets the touching
diameter. Each inverse is the complementary block of `H^{-1}`.

## One deleted vertex

At width 3 the entry is `-1/12`. Vertices 3 and 7 are opposite, and both
meet vertex 0, while the direct entry between them is zero. The Schur
entry is

```
-(-1/12)(-1/12) = -1/144.
```

The bandwidth is 4, the diameter of the touching set. The inverse has
both induced norms equal to `27/14`, inside the width-3 bounds `2` and `14`.

At width 4 the direct entry between 1 and 5 is already `-1/14`, and the
update through vertex 0 subtracts another `1/196`. The complement entry
is `-15/196`. The bandwidth is again 4. The inverse has both norms equal
to `28/15`, inside the width-4 bounds `2` and `18`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length8-touching-diameter/verify.py
python3 -B scripts/research_package.py --package research/length8-touching-diameter
```

The verifier authenticates the pinned note, checks every width and every
proper arc, and checks the two one-vertex identities and norm bounds.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

Length 8 has no exceptional width. A longer equal-weight cycle is the
next place a touching pair could cancel.

## Credit

Cinna Davis wrote the periodic-section sentence in the PR4100 narrow
Neumann note. The width-1 arc formula and the width-2 diameter are the
preceding audits. The widths 3 and 4, and the resulting census of every
width on this circle, are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
