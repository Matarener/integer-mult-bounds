# The normalized matrix 2-norm is strictly below 1226/625

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, every absolute row
sum and every absolute column sum of the normalized Schur section on
`0,1,2,7,8,9` is strictly below `1226/625 = 1.9616`. The 2-norm is
therefore strictly below `1226/625`, which is strictly below `2` and
strictly below `19^10 = 6131066257801`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized section, not the note's all-size 2-norm envelope.

## The row and column sums

`FINE-PRIME.md` asks for both `||H||_2` and `||H^-1||_2` to be at most
`p^10`. `INVERSE-CONDITIONING.md` supplies
`||M||_2^2 <= ||M||_1 ||M||_infinity`. On this snapped normalized matrix
the six row sums and six column sums are each strictly below
`1226/625`, so their product is strictly below `(1226/625)^2`. The
inverse 2-norm remains strictly below `319/100`, which is also strictly
below `19^10`. The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-matrix-norm/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-matrix-norm
```

The verifier authenticates the pinned notes and compares the row and
column sums with `1226/625` and `19^10`.

## Open next questions

The fine-prime note places the eigenvalues of `Q = I - p^{-20} H* H` in
`[0, 1-p^{-40}]`. Nothing here forms that matrix.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
comparison of `319/100` with `19^10` is the preceding audit. These
matrix sums are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
