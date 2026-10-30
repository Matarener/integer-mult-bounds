# Equal-weight cycle arcs meet the touching diameter

On a cycle of any length at least 3, with any width from 1 through half the
length, every proper contiguous arc has Schur bandwidth equal to the
diameter of the survivors that meet the arc. No longer equal-weight cycle
falls short of that diameter, and none keeps the original width.

No new kappa is claimed. Boundary order is not decided here.

## The host

The diagonal is 1. Every positive circular distance up to the width carries
the same negative entry, and the antipode is counted once, so each
off-diagonal row sums to `1/2`. Width 1 on length 9 has entry `-1/4`.
Width 2 has entry `-1/8`.

The note's compression sentence applies to a linear order. On a cycle the
two neighbors of a deleted vertex remain at circular distance 2.

## Why the diameter is met

Order a surviving arc of `M` vertices. A survivor meets the killed arc when
its circular distance to that arc is at most the width. If `M` is at most
twice the width, every survivor meets the arc.

If `M` is at least `2w+1`, the survivors at positions `w-1` and `M-1` both
meet the arc. The two cycle routes between them have lengths `M-w` and
`L+w`, where `L` is the killed length. Those routes sum to the cycle
length, so the circular distance is their minimum. Both lengths are at
least `w+1`, and the boundary case `M=2w+1`, `L=1` exceeds the width by
exactly one.

The killed block is `I-E` with `E` nonnegative. Deleting the couplings
that leave the arc does not increase a row sum, so each row of `E` sums
to at most `1/2`. The inverse is the Neumann series. Consecutive arc
vertices are cycle neighbors, so some walk of length `d` between two arc
vertices has weight `v^d > 0`. Every entry of the inverse is therefore
positive.

A survivor meets the arc exactly when its coupling row is nonzero. For two
such survivors the update against this positive inverse is positive, while
the direct entry is zero or negative, so the Schur entry is negative.
Every touching pair contributes its circular distance.

A survivor that misses the arc has a zero coupling row, so its Schur row
is copied from `H` and stays inside the original width. Whenever such a
survivor exists, the rim pair above is already farther than that width.
The copy cannot set the bandwidth. The bandwidth is the touching diameter.

Equal magnitudes are not required for this sign argument. Every in-band
entry has to be negative, and each off-diagonal row has to sum to less
than 1. A sign change can cancel a rim entry; that case is not included.

## One deleted vertex on length 9

At width 1 the two neighbors of vertex 0 have no direct entry. The Schur
entry is

```
-(-1/4)(-1/4) = -1/16.
```

The bandwidth is 2. The inverse has both induced norms equal to
`528/265`, inside the width-1 bounds `2` and `6`.

At width 2 the survivors 2 and 7 likewise have no direct entry. The Schur
entry is `-1/64`, and the bandwidth is 4. The inverse has both norms
equal to `4772/2435`, inside the width-2 bounds `2` and `10`.

The same equality holds for every proper arc of every equal-weight cycle
of length 3 through 9, and each complement inverse is the complementary
block of `H^{-1}`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/equal-weight-cycle-diameter/verify.py
python3 -B scripts/research_package.py --package research/equal-weight-cycle-diameter
```

The verifier authenticates the pinned note, checks the rim-gap identity,
checks every arc through length 9, and checks the two one-vertex identities.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

A single positive off-diagonal entry can cancel the update. The equal
negative sign pattern is what forces every touching pair to survive.

## Credit

Cinna Davis wrote the periodic-section sentence in the PR4100 narrow
Neumann note. The length-8 census is the preceding audit. The all-length
sign argument is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
