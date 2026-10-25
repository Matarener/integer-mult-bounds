# 319/100 is strictly below 19^10

At `p=19`, `19^10 = 6131066257801`. The number `319/100` is strictly
smaller. The normalized Schur inverse on `0,1,2,7,8,9` has 2-norm
strictly below `319/100`, so that 2-norm is strictly below `p^10`.

No new kappa is claimed. The selected record is unchanged. This is one
normalized section, not the note's all-size 2-norm envelope.

## The power

`FINE-PRIME.md` uses the envelope `||H||_2,||H^-1||_2<=p^10` for a
banded reference matrix. On this section the product of the certified
inverse 1-norm and infinity-norm upper bounds is strictly below
`(319/100)^2`, so the inverse 2-norm is strictly below `319/100`. The
integer power is

```text
19^10 = 6131066257801 > 319/100.
```

The same Machin comparison gives `alpha=3` and
`4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-p10/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-p10
```

The verifier authenticates the pinned notes, rechecks the inverse
2-norm product, and compares `319/100` with `19^10`.

## Open next questions

The same envelope also asks for `||H||_2`. Nothing here bounds the
2-norm of the normalized matrix itself.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. The
inverse 2-norm product is the preceding audit. This power comparison is
this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
