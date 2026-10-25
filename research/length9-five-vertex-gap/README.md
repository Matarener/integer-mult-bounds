# The five-vertex far numerators do not share a positive root

On the length-9 width-2 arc `{0,1,2,3,4}`, no pivot entry zeros both
directions of the far pair at a positive value. The interior path entry
zeros one direction at `809/1296`, one step of `1/1296` below the row-gap
ceiling. The other direction stays nonzero, so the bandwidth remains 3.

No new kappa is claimed. Boundary order is not decided here.

## The two roots

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. Deleting the arc leaves vertices `5, 6, 7, 8`. All four meet the
arc, and the farthest pair is `(5,8)`, at circular distance 3.

Replace the path entry from 1 to 2 by `x`. The far numerators are

```
-481/131072 + 9x/32768,      root 481/36,
-809/262144 + 81x/16384,     root 809/1296.
```

They are not the same function. The endpoint path entry from 0 to 1 splits
at `953/144` and `881/720`, both larger than `5/8`.

Replacing one off-diagonal entry of absolute value `1/8` by a positive `x`
raises that row's absolute sum from `1/2` to `3/8 + x`. This stays below 1
exactly when `x < 5/8`. The root `809/1296` is `5/8 - 1/1296`.

## One direction inside the bound

At `x = 809/1296` the pivot determinant is `587809/589824`. The Schur entry
from 8 to 5 is 0. The opposite entry is `-971/276616`. The bandwidth stays
3, the touching diameter. The row gap is `1295/1296`. The complement is the
complementary block of the inverse. Its 1-norm is `419112/257177` and its
infinity norm is `1022468068/626225995`, inside the width-2 bounds `6714576`
and `1296`.

Every other pivot position was checked the same way. Whenever the two
numerators share a root, that root is negative.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-five-vertex-gap/verify.py
python3 -B scripts/research_package.py --package research/length9-five-vertex-gap
```

The verifier authenticates the pinned note, checks the affine numerators,
and checks every entry of the pivot.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

A six-vertex arc is the remaining length on this cycle where a positive
common root might still keep the row gap below 1.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The four-vertex split is the preceding audit. The five-vertex root
is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
