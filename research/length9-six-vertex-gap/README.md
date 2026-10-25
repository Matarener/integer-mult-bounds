# Six-vertex far directions vanish together only below diagonal dominance

On the length-9 width-2 arc `{0,1,2,3,4,5}`, the path entry from 1 to 2 has
no positive far-rim root. The only positive common roots are diagonal
entries, and each is strictly less than `1/2`. At the endpoint diagonal
`3821/116272`, both directions of the far pair vanish and the Schur
bandwidth falls from 2 to 1. Scaling that diagonal back to 1 makes the
off-diagonal row sum `58136/3821`, which is larger than 1.

No new kappa is claimed. Boundary order is not decided here.

## The path entry

The diagonal is 1 and every positive circular distance up to 2 carries
`-1/8`. Deleting the arc leaves vertices `6, 7, 8`. All three meet the arc.
The farthest pair is `(6,8)`, at circular distance 2.

Replace the path entry from 1 to 2 by `x`. The far numerators are

```
-114917/1048576 - 1233x/65536,    root -114917/19728,
-114521/1048576 - 1035x/65536,    root -114521/16560.
```

Both roots are negative, so this entry does not zero either far direction
at a positive value.

## The diagonal root

A diagonal change leaves the off-diagonal absolute row sum at `1/2`. The
endpoint diagonal `H_00` has the same numerator in both far directions,

```
3821/1048576 - 7267x/65536,    root 3821/116272.
```

The same root occurs at `H_55`. The inner diagonals share
`5773/118224` at positions 1 and 4, and `8653/121104` at positions 2 and 3.
Each of these three values is less than `1/2`.

At `H_00 = 3821/116272` the pivot determinant is `-4020911/952500224`. Both
Schur entries between 6 and 8 are 0. The entry between 6 and 7 is
`-1095/33128`, and the entry between 7 and 8 is `14169/3884`, so the
bandwidth is 1. The complement is the complementary block of the inverse.
Its 1-norm and infinity norm are both `3986274320/3731061379`.

Writing the matrix as that diagonal times `I - E` gives `E` an absolute
row sum `58136/3821 > 1`. The narrow bound `rho < 1` does not apply. No
off-diagonal pivot entry has a root in `(0, 5/8]`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/length9-six-vertex-gap/verify.py
python3 -B scripts/research_package.py --package research/length9-six-vertex-gap
```

The verifier authenticates the pinned note, checks the path and diagonal
numerators, and checks every entry of the pivot.

## Open next questions

The Gaussian caller still claims bandwidth `O(W)` after survivors are
placed in boundary order. Nothing here reorders the survivors.

A seven-vertex arc leaves one pair of survivors. Whether that pair has a
positive common root inside diagonal dominance is the remaining length on
this cycle.

## Credit

Cinna Davis wrote the narrow Neumann bounds in the PR4100 conditioning
note. The five-vertex split is the preceding audit. The six-vertex diagonal
root is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
