# This section's polynomial-inverse tail is strictly below p^{10} exp(-p^2)

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, let `H` be the
normalized Schur section on `0,1,2,7,8,9` and let
`Q = I - p^{-20} H* H`. For `J = 19^{42} = ceil(p^{42})` and
`r = 1 - 19^{-40}`,

`(1 - 19^{-40})^{19^{42}} < exp(-361)`.

The audited error identity is `P - H^{-1} = -Q^J H^{-1}`. Its 2-norm is at
most `||Q||_2^J ||H^{-1}||_2`. This section has `||Q||_2 < r` and
`||H^{-1}||_2 < 319/100`, so the error is strictly below
`(319/100) exp(-361)`, and therefore strictly below
`19^{10} exp(-361) = p^{10} exp(-p^2)`.

The coarser expression `p^{-20} r^J / (1-r) * (1226/625)` equals
`19^{20} (1226/625) r^J` and is strictly larger than `p^{10} exp(-p^2)`.
It does not witness the displayed threshold. No new kappa is claimed. The
selected record is unchanged. This is one normalized section, not the
note's all-size tail. The matrix `Q` is not formed.

## The two series bounds

`exp(19^{-40}) < (1 - 19^{-40})^{-1}`, so raising to the power `19^{40}`
gives `(1 - 19^{-40})^{19^{40}} < exp(-1)` and
`(1 - 19^{-40})^{19^{42}} < exp(-361)`. The same series gives a matching
lower bound: the coarser majorant is more than
`19^{10} (1226/625) (1 - 361/(19^{40}-1))` times `exp(-361)`, and that
rational factor is strictly greater than 1. `||M||_2^2 <= ||M||_1 ||M||_infinity`
supplies `||H^{-1}||_2 < 319/100 < 19^{10}`. The same Machin comparison
gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-q-tail/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-q-tail
```

The verifier authenticates the pinned notes and checks both series
comparisons.

## Open next questions

`FINE-PRIME.md` says this error is below `2^{-Cp}` for every fixed `C`
eventually. Nothing here compares `(319/100) exp(-361)` with `2^{-19}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}` and
that a term-by-term tail only produces a `p^{30}` factor. The eigenvalue
interval is the preceding audit. Binding the identity to this section's
`319/100` constant is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
