# The four-vertex far numerators do not share a positive root

On the length-9 width-2 arc `{0,1,2,3}`, no pivot entry zeros both
directions of the far pair at a positive value. The interior path entry
does zero one direction at `161/648`, and that value keeps the row gap
below 1. The other direction stays nonzero, so the bandwidth remains 4.

No new kappa is claimed. Boundary order is not decided here.

## The two roots

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. The only survivors at circular distance 4 are vertices 4 and 8.
Replace the path entry from 1 to 2 by `x`. The far numerators are the
affine functions

```
-241/32768 + x/4096,       root 241/8,
-161/32768 + 81x/4096,     root 161/648.
```

They are not the same function, so no value zeros both directions. The
endpoint path entry from 0 to 1 splits in the same way, at `233/72` and
`14/9`. Both of those roots are larger than `5/8`.

Replacing one off-diagonal entry of absolute value `1/8` by a positive `x`
raises that row's absolute sum from `1/2` to `3/8 + x`. The sum stays below
1 exactly when `x < 5/8`. Thus `161/648` is inside the row-gap bound and
`241/8` is not.

## One direction inside the bound

At `x = 161/648` the pivot determinant is `5041/5184`. The Schur entry from
8 to 4 is 0. The opposite entry is `-605/80656`. The bandwidth stays 4.
The row gap is `101/162`. The complement is the complementary block of the
inverse, and both induced norms equal `1854891296/1028005865`, inside the
width-2 bounds `162/61` and `75330/3721`.

Every other pivot position was checked the same way. Whenever the two
numerators share a root, that root is negative. The negative roots are the
two diagonal values `-49/72` and `-85/36`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-four-vertex-gap/verify.py
python3 -B scripts/research_package.py --package research/length9-four-vertex-gap
```

The verifier authenticates the pinned note, checks the affine numerators,
and checks every entry of the pivot.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

A five-vertex arc is the remaining length on this cycle where a positive
common root might still keep the row gap below 1.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The three-vertex root `17/8` is the preceding audit. The four-vertex
split is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
