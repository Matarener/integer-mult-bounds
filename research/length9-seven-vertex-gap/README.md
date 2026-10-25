# Seven-vertex survivor directions vanish together only below dominance

On the length-9 width-2 arc `{0,1,2,3,4,5,6}`, the path entry from 1 to 2
has no positive survivor root. The positive common roots are the inner
diagonals `4429/115952`, `8717/120240`, and `45349/602964`. Each is less
than `1/2`. At the center diagonal, both directions of the surviving pair
vanish and the complement is diagonal. Scaling that diagonal back to 1
makes the off-diagonal row sum `301482/45349`, which is larger than 1.

No new kappa is claimed. Boundary order is not decided here.

## The surviving pair

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. Deleting the arc leaves vertices `7` and `8`, at circular distance
1. On the unperturbed host both Schur entries equal `-557615/3416976`, and
the pivot determinant is `213561/262144`.

Replace the path entry from 1 to 2 by `x`. The survivor numerators are

```
-569603/4194304 - 2997x/131072,    root -569603/95904,
-568165/4194304 - 5275x/262144,    root -113633/16880.
```

Both roots are negative.

## The diagonal roots

A diagonal change leaves the off-diagonal absolute row sum at `1/2`. The
endpoint diagonals `H_00` and `H_66` share the root `-199/2236`. At that
negative value both survivor entries are 0 and the pivot determinant is
`-112451/1048576`.

The inner diagonals share a positive root:

```
H_11 and H_55:  4429/115952,
H_22 and H_44:  8717/120240,
H_33:           45349/602964.
```

Each is less than `1/2`. At `H_33 = 45349/602964` the pivot determinant is
`-8934121/1951399936`. Both Schur entries between 7 and 8 are 0, and both
survivor diagonals are `2435/2196`. The complement is the complementary
block of the inverse. Its 1-norm and infinity norm are both `2196/2435`.

Writing the matrix as that diagonal times `I - E` gives `E` an absolute
row sum `301482/45349 > 1`. The narrow bound `rho < 1` does not apply. No
off-diagonal pivot entry has a root in `(0, 5/8]`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-seven-vertex-gap/verify.py
python3 -B scripts/research_package.py --package research/length9-seven-vertex-gap
```

The verifier authenticates the pinned note, checks the path and diagonal
numerators, and checks every entry of the pivot.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors. A length-8
arc on this cycle leaves one survivor, so it has no off-diagonal pair left
to cancel.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The six-vertex diagonal roots are the preceding audit. The
seven-vertex survivor roots are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
