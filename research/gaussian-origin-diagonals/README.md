# The translated Schur diagonals are positive and at most 1

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}`. All six diagonal entries of the Schur complement on
`0,1,2,7,8,9` are strictly positive and at most 1. Vertices 0 and 9
are exactly 1. The diagonals at 1 and 8 lie strictly between
`1-1/10^98` and `1-1/10^99`. The diagonals at 2 and 7 lie strictly
between `1-1/10^24` and `1-1/10^25`.

No new kappa is claimed. The selected record is unchanged. This is one
Schur section, not a normalization of the note's reference matrix.

## The six diagonals

`GAUSSIAN.md` asks for a reference matrix with diagonal 1. On this
section the original diagonal is 1. Vertices 0 and 9 do not meet the
interior, so the Schur correction on those diagonal slots is zero and
the diagonal stays 1.

Vertices 1, 2, 7, and 8 meet the interior. Each of those diagonal
corrections is strictly positive, so those four diagonals are strictly
below 1 and still within `1/10^24` of 1. The same Machin comparison
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-diagonals/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-diagonals
```

The verifier authenticates the pinned notes and encloses the six
diagonal corrections by rational interval arithmetic.

## Open next questions

Dividing each survivor row by its diagonal restores diagonal 1. Nothing
here checks the off-diagonal row sums after that division.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
survivor row sums are the preceding audit. These diagonals are this
audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
