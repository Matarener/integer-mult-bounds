# This section's polynomial-inverse error is strictly below 2^{-19}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-3
Taylor sum of `exp(361)` equals `23719508/3`. That sum is strictly
greater than `41811968/25 = 2^{19} * (319/100)`, and the next Taylor
term is positive, so

`(319/100) exp(-361) < 2^{-19}`.

The section error is therefore strictly below `2^{-19}`. No new kappa is
claimed. The selected record is unchanged. This is the case `C=1` on one
normalized section, not the note's claim for every fixed `C`. The matrix
`Q` is not formed.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit bounds this section by
`(319/100) exp(-361)`. Every term of the exponential series is positive,
so `exp(361)` is strictly larger than its degree-3 partial sum, and that
partial sum already exceeds `2^{19} * (319/100)`. The same Machin
comparison gives `alpha=3` and `4 log(304)<=9 pi<=5 log(304)`.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power
```

The verifier authenticates the pinned notes and checks the Taylor
comparison.

## Open next questions

The same majorant has not been compared with `2^{-38}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `(319/100) exp(-361)` is the preceding audit. This
power-of-two comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
