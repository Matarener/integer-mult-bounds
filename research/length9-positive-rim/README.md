# One positive entry cancels only one length-9 rim direction

On the length-9 width-1 cycle, flipping the sign of one neighbor entry does
not zero a touching pair. The one-vertex fill has size `1/16`, so a single
positive entry of that size cancels one Schur direction and leaves the
other. Both directions have to be set before the bandwidth falls below the
touching diameter.

No new kappa is claimed. Boundary order is not decided here.

## The cycle

The diagonal is 1 and each circular neighbor is `-1/4`. Deleting one vertex
leaves its two neighbors, which are not themselves neighbors. Their Schur
entry in each direction is the product of the two spokes:

```
-(-1/4)(-1/4) = -1/16.
```

## A sign flip misses the opposite rim

Vertex 5 is opposite the edge from 0 to 1. Replacing that one entry by
`+1/4` does not appear in either spoke of vertex 5. Both rim entries stay
`-1/16`, and the bandwidth stays 2. The inverse of that complement has both
induced norms equal to `25756/13515`, inside the original bounds `2` and `6`.

The same holds for every directed neighbor sign flip and every proper arc:
every touching Schur entry stays nonzero, and the bandwidth stays equal to
the touching diameter. On the arc `{0,1,2}`, the same flipped entry makes
the two rim directions `1/256` and `-1/256`.

## The fill magnitude cancels one direction

Putting `+1/16` in the single position between survivors 1 and 8 cancels
the product above. That Schur entry is 0. The opposite position is still
absent, so its Schur entry stays `-1/16`. The bandwidth remains 2, which is
still the touching diameter. The complement inverse has both norms
`224944/112943`. The added entry raises the row gap to `9/16` and the
circular bandwidth to 2, and the norms stay inside those bounds.

Putting `+1/16` in both positions zeros both directions. The bandwidth
drops to 1, strictly below the touching diameter 2. The complement inverse
has both norms `1136/571`, again inside the widened bounds.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-positive-rim/verify.py
python3 -B scripts/research_package.py --package research/length9-positive-rim
```

The verifier authenticates the pinned note, checks every neighbor sign
flip, and checks the three one-vertex identities.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

Width 2 has more than one touching pair. One positive entry might zero
both directions of a far pair there; the width-1 one-vertex product does
not.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The equal-weight diameter argument is the preceding audit. The
one-entry cancellation is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
