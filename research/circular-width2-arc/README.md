# Width 2 does not survive an arc on the length-8 circle

Deleting one vertex from the width-2 cycle leaves circular bandwidth 4.
Deleting the arc `{2,3,4}` also leaves bandwidth 4. The original width is
2 in both cases. The width-1 length formula does not give these values.

No new kappa is claimed. Boundary order is not decided here.

## Where a new entry can sit

A survivor that lies more than distance 2 from the arc has no coupling
into the pivot, so its Schur row is the corresponding row of `H`. Those
entries already have circular distance at most 2. Every farther nonzero
entry joins two survivors that each meet the arc. The circular bandwidth
is therefore at most the diameter of that touching set.

On this host the bound is met for every proper arc. The diameter, and
hence the bandwidth, is 4, 4, 4, 3, 2, 1, 0 as the arc length runs from
1 through 7. Rotating the arc does not change it. Each complement's
inverse is the complementary block of `H^{-1}`.

## Two exact arcs

The cycle has diagonal 1 and entries `-1/8` at distance 1 and 2, so the
off-diagonal infinity norm is `1/2`. Deleting vertex 0 leaves the entry

```
-(-1/8)(-1/8) = -1/64
```

between survivors 2 and 6. They are opposite, at circular distance 4.
The other rows that do not meet vertex 0 keep distance at most 2, so the
bandwidth is exactly 4.

Deleting `{2,3,4}` leaves survivors `{0,1,5,6,7}`. The entry between 1
and 5 is `-5/216`, again at distance 4. The inverse has both induced
norms equal to `2257/1240`. The width-2 Neumann bounds at this row gap
are `2` and `10`, and `2257/1240` lies below both. The inverse bound
still applies. The original width does not describe the complement.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/circular-width2-arc/verify.py
python3 -B scripts/research_package.py --package research/circular-width2-arc
```

The verifier authenticates the pinned note, checks every proper arc
against the touching diameter, and checks the one-vertex and three-vertex
entries, the block identity, and the original bounds.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. These complements stay on the original circle.

The touching-diameter cap is proved as an upper bound for any width. This
host meets it at width 2. A width-3 cycle is the next place that equality
could fail.

## Credit

Cinna Davis wrote the periodic-section sentence in the PR4100 narrow
Neumann note. The width-1 arc formula is the preceding audit. The width-2
diameter and the two explicit entries are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
