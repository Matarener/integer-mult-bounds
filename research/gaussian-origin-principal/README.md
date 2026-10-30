# Every principal restriction of the normalized section keeps the row gap

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}` and divide each Schur row on `0,1,2,7,8,9` by its diagonal.
In every one of the six rows, every subset of the other five columns has
absolute sum strictly below `1-1/5776`. Every principal restriction
therefore has row gap strictly greater than `1/(16 p^2)=1/5776`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized Schur section, not the note's all-size restriction claim.

## The 192 deletions

`GAUSSIAN.md` says that all principal restrictions retain the row gap.
A row of a principal submatrix keeps the diagonal entry and some subset
of the other columns. There are five other survivor columns, so each row
has 32 subsets and the section has 192 row deletions.

Vertices 0 and 9 do not meet the interior. Their Schur rows are the
original width-2 rows and their diagonals are 1. Each in-band entry is
bounded by the forward majorant `exp(-9 pi/722)` or by the common other
majorant, and every out-of-band entry is zero. Vertices 1, 2, 7, and 8
use the enclosed absolute entries divided by the diagonal lower bounds.
The full-row sums lie strictly below a rational lower bound for
`exp(-9 pi/722)+5 exp(-18 pi)`, and that lower bound is strictly below
`1-1/5776`. Every subset sum is at most the full-row sum, so it stays
strictly below `1-1/5776`. The same Machin comparison gives `alpha=3`
and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-principal/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-principal
```

The verifier authenticates the pinned notes and compares all 192
normalized row deletions with `1-1/5776`.

## Open next questions

The narrow inverse bound also needs the bandwidth of this section.
Nothing here encloses the individual separator corners.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
normalized row sums are the preceding audit. These principal restrictions
are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
