# Direct elimination puts the inverse 1-norm below 282/100

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the normalized Schur
section on `0,1,2,7,8,9` has inverse 1-norm strictly between `281/100`
and `282/100`. In particular the norm is strictly below the Neumann
ceiling `3938`, by a factor greater than `1396`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized section, not an all-size inverse bound.

## The column residual

The same denominator-`10^12` midpoint inverse used for the infinity norm
is multiplied by the snapped normalized matrix. The interval residual has
1-norm below `10^{-11}`. The resulting enclosure of the true inverse
1-norm lies strictly inside `(281/100, 282/100)`.

The same elimination still puts the infinity norm strictly between
`18/5` and `361/100`. The Neumann 1-norm ceiling `3938` remains valid.
The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-inverse-one/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-inverse-one
```

The verifier authenticates the pinned notes and certifies both residual
norms.

## Open next questions

The 2-norm is at most the square root of the product of these certified
1-norm and infinity-norm bounds. Nothing here compares that square root
with `321`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
inverse infinity norm is the preceding audit. This 1-norm is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
