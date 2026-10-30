# The normalized translated Schur row sums are strictly below 2

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}` and divide each Schur row on `0,1,2,7,8,9` by its diagonal.
Every absolute row sum is strictly below 2.

No new kappa is claimed. The selected record is unchanged. This is one
normalized Schur section, not the note's all-size row norm.

## The six row sums

`GAUSSIAN.md` asks for a diagonal-1 reference with row norm below 2. On
this section the diagonal is 1 after the division, so the absolute row
sum is 1 plus the off-diagonal absolute row sum. Each of those off-sums
lies strictly below a rational lower bound for
`exp(-9 pi/722)+5 exp(-18 pi)`, and that lower bound is strictly below
`1-1/5776`. Adding 1 therefore keeps every row sum strictly below
`2-1/5776`.

Vertices 0 and 9 keep diagonal 1 and identically zero Schur correction,
so their row sums use the original exponent majorant. Vertices 1, 2, 7,
and 8 use the enclosed off-sums divided by the diagonal lower bounds.
The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-norm/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-norm
```

The verifier authenticates the pinned notes and compares each normalized
absolute row sum with 2.

## Open next questions

The note also says that every principal restriction retains the row gap.
Nothing here deletes a subset of the survivor columns.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
normalized gaps are the preceding audit. These row sums are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
