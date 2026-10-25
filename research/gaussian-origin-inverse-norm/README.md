# Direct elimination puts the inverse infinity norm below 361/100

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the normalized Schur
section on `0,1,2,7,8,9` has inverse infinity norm strictly between
`18/5` and `361/100`. In particular the norm is strictly below the
Neumann ceiling `27`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized section, not an all-size inverse bound.

## The residual certificate

The normalized matrix has diagonal 1. Each off-diagonal entry is enclosed
and then snapped outward onto multiples of `10^{-12}`. Rational
elimination of the midpoint matrix produces an approximate inverse `G`.
The interval product of the snapped matrix with `G` differs from the
identity by an infinity norm below `10^{-11}`. The resulting enclosure
of the true inverse infinity norm lies strictly inside `(18/5, 361/100)`.

The Neumann majorant at the displayed-expression gap remains valid and
is at most `27`. The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-inverse-norm/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-inverse-norm
```

The verifier authenticates the pinned notes and certifies the residual
enclosure.

## Open next questions

The same elimination can enclose the induced 1-norm. Nothing here sums
the absolute values down the columns of the inverse.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
Neumann ceilings on the principal restrictions are the preceding audit.
This inverse norm is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
