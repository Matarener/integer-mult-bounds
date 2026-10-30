# The product bound puts the inverse 2-norm strictly below 319/100

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the normalized Schur
section on `0,1,2,7,8,9` has inverse 2-norm strictly below `319/100`.
In particular the norm is strictly below the Neumann ceiling `321`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized section, not an all-size inverse bound.

## The product

`INVERSE-CONDITIONING.md` uses
`||M||_2^2 <= ||M||_1 ||M||_infinity`. The certified inverse 1-norm is
strictly below `282/100`, and the certified infinity norm is strictly
below `361/100`. Their product of round ceilings is

```text
(282/100)*(361/100) = 101802/10000,
```

and `319^2 < 101802 < 320^2`, so that ceiling product lies strictly
between `(319/100)^2` and `(16/5)^2`. The residual upper bounds
themselves multiply to a number strictly below `(319/100)^2`. The
inverse 2-norm is therefore strictly below `319/100`, which is strictly
below `16/5` and strictly below `321`.

The same elimination still puts the infinity norm in `(18/5, 361/100)`
and the 1-norm in `(281/100, 282/100)`. The same Machin comparison gives
`alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-inverse-two/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-inverse-two
```

The verifier authenticates the pinned notes, rechecks the residual
norms, and compares the product with `321`.

## Open next questions

`FINE-PRIME.md` uses a 2-norm envelope `p^10`. Nothing here compares
`319/100` with `19^10`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
inverse 1-norm is the preceding audit. This 2-norm bound is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
