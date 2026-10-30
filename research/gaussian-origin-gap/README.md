# The normalized translated Schur gaps exceed 1/(16 p^2)

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}` and divide each Schur row on `0,1,2,7,8,9` by its diagonal.
Every row gap, one minus the off-diagonal row sum, is strictly greater
than `1/(16 p^2)=1/5776`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized Schur section, not the note's all-size row gap.

## The six gaps

`GAUSSIAN.md` asks for a diagonal-1 reference with row gap at least
`1/(16 p^2)`. On this section each normalized off-diagonal row sum is
strictly below a rational lower bound for
`exp(-9 pi/722)+5 exp(-18 pi)`. That lower bound is itself strictly
below `1-1/5776`, so each gap exceeds `1/5776`.

Vertices 0 and 9 keep diagonal 1 and identically zero Schur correction,
so their gaps use the original exponent majorant. Vertices 1, 2, 7, and
8 use the enclosed off-sums divided by the diagonal lower bounds. The
same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-gap/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-gap
```

The verifier authenticates the pinned notes and compares each normalized
gap with `1/5776`.

## Open next questions

The same sentence in the note also asks for row norm below 2. Nothing
here adds 1 to these six off-sums.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
normalized row sums are the preceding audit. These gaps are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
