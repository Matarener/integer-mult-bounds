# Circular Schur bandwidth follows the arc, not the width alone

On the length-8 circle of width 1, deleting one vertex leaves circular
bandwidth 2. Deleting a three-vertex arc leaves circular bandwidth 4. The
width is the same. No cap depending only on that width fits both
complements.

No new kappa is claimed. The linear interval cap and the Gaussian boundary
order are separate.

## The rim entry

Let `H` be the width-1 cycle with diagonal 1 and nearest-neighbor entries
`-1/4`. A proper arc induces a path. Only the two survivors adjacent to
the ends of the arc meet that path.

The Schur update between those rims is `-1/16` times the corner of the
path inverse. That corner is nonzero. If `T u = e_last`, the first row
says the first unknown is `1/4` times the second. Vanishing of the first
unknown forces every unknown to vanish, and the last row then says `0=1`.

The two rims are `length+1` steps apart along the arc and `n-length-1`
steps apart the other way. Their circular distance is the minimum. Every
other surviving pair keeps an original entry, nonzero only at distance 1,
because no other survivor meets the arc. The circular bandwidth of the
complement is therefore

```
min(length+1, n-length-1).
```

For `n=8` this is 2, 3, 4, 3, 2, 1, 0 as the length runs from 1 through 7.
Every rotation agrees. Each complement's inverse is the complementary
block of `H^{-1}`.

## The two explicit arcs

Deleting `{0}` leaves the entry `-1/16` between 1 and 7, at circular
distance 2. Deleting `{2,3,4}` leaves survivors `{0,1,5,6,7}` and the
entry `-1/224` between 1 and 5, at circular distance 4. The second
inverse has both induced norms equal to `163/84`. The width-1 Neumann
bounds at `rho=1/2` are `2` and `6`, and `163/84` lies below both. The
inverse bound still applies. The original width does not describe the
complement: its circular bandwidth is 4.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/circular-schur-arc/verify.py
python3 -B scripts/research_package.py --package research/circular-schur-arc
```

The verifier authenticates the pinned note, checks every proper arc, and
checks the two explicit complements, including the path-corner formula.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after a boundary
reordering. Nothing here reorders survivors.

A circle of width greater than 1 has a whole rim, not one vertex, at each
end of the arc. The same length formula does not apply.

## Credit

Cinna Davis wrote the periodic-section sentence in the PR4100 narrow
Neumann note. The linear interval cap is the preceding audit. The arc
formula for this width-1 cycle is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
