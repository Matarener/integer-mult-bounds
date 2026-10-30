# This section's polynomial-inverse error is strictly below 2^{-57}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-10
Taylor sum of `exp(361)` equals `38657793315667161768372101/3628800`.
That sum is strictly greater than `11493186249049505792/25 = 2^{57} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-57}`.

The degree-9 partial sum is strictly below that same target, so this
comparison uses degree 10. The section error is therefore strictly below
`2^{-57}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=3` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant itself
is the preceding audit; this package replays that proof and adds the
`2^{-57}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-38}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-10 partial sum, and that
partial sum already exceeds `2^{57} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:27:56Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c3/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c3
```

The verifier authenticates the pinned notes, replays the preceding
majorant proof, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-76}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-19}` and the bound by `2^{-38}` are the preceding
audits. This `C=3` comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
