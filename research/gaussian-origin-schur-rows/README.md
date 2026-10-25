# The translated Schur rows stay below the displayed Gaussian bound

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}`. Every off-diagonal row sum of the Schur complement on
`0,1,2,7,8,9` is strictly below `exp(-2 a theta)+5 exp(-2 a)`. At these
parameters that expression is `exp(-9 pi/722)+5 exp(-18 pi)`.

No new kappa is claimed. The selected record is unchanged. This is one
prime, one shift endpoint, one translated origin, and one interior.

## The six rows

`GAUSSIAN.md` says that all principal restrictions retain the row gap.
Vertices 0 and 9 do not meet the interior, so their Schur rows are the
original width-2 rows. Those rows lie strictly below the displayed
expression by the same majorant as the preceding audit: one forward
step of size `exp(-9 pi/722)` and other in-band entries no larger than
`exp(-6462 pi/361)`, with `exp(36 pi/361)<5/3`.

The other four survivor rows meet the interior. Their Schur off-sums
are strictly below `24/25` and strictly below the displayed expression.
The new entry from vertex 2 to vertex 7 lies strictly between `3/10`
and `2/5`. The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-schur-rows/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-schur-rows
```

The verifier authenticates the pinned notes, compares the untouched
rows with the displayed expression, and encloses the filled rows by
rational interval arithmetic.

## Open next questions

The note's reference matrix has diagonal 1. Nothing here encloses the
six Schur diagonals.

## Credit

Cinna Davis wrote the narrow kernel and the displayed row estimate in
the PR4100 Gaussian note. The translated width-2 row sums are the
preceding audit. These Schur rows are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
