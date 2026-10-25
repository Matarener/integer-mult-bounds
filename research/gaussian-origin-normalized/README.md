# The normalized translated Schur rows stay below the displayed bound

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, delete the interior
`{3,4,5,6}`. Divide each of the six Schur rows on `0,1,2,7,8,9` by its
diagonal. Every resulting off-diagonal row sum is strictly below
`exp(-2 a theta)+5 exp(-2 a)`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized Schur section, not the note's all-size row gap.

## The six normalized rows

`GAUSSIAN.md` asks for a reference matrix with diagonal 1 whose
off-diagonal infinity norm is at most the displayed expression. On this
section the displayed expression is `exp(-9 pi/722)+5 exp(-18 pi)`.
The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

Vertices 0 and 9 do not meet the interior. Their Schur corrections are
identically zero, so those diagonals are exactly 1 and those rows remain
the original width-2 rows. Each original in-band entry is
`exp(-pi * coefficient)` with a forward step at least `9 pi/722` and
every other step at least `6462 pi/361`. At most one forward step and
three other entries occur, and `exp(36 pi/361)<5/3`, so those two
normalized rows stay strictly below the displayed expression.

Vertices 1, 2, 7, and 8 meet the interior. Their diagonal corrections
lie in the windows already enclosed for this section: `(1/10^99, 1/10^98)`
at 1 and 8, and `(1/10^25, 1/10^24)` at 2 and 7. Dividing the enclosed
off-diagonal absolute row sums by those diagonal lower bounds keeps all
four quotients strictly below the same displayed expression.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-normalized/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-normalized
```

The verifier authenticates the pinned notes and compares the six
normalized off-diagonal row sums with a rational lower bound for the
displayed expression.

## Open next questions

The note also asks for a row gap of at least `1/(16 p^2)` after the
diagonal is restored. Nothing here subtracts these six off-sums from 1.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
Schur diagonals are the preceding audit. These normalized rows are this
audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
