# This section's polynomial-inverse error is strictly below 2^{-342}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-111
Taylor sum of `exp(361)` equals
`6353171131141597829025344014979879829604670669629252202018633071809904094086879998896092707789700738791724065464570956495989313613656490316793713922580898191511717245681687462314894918003757584603652634738483969094593729926424682246463167795382587566585376745168443662175157/101654470252354618165879784522391953056061680140877411857873360467840901211176817221234856289946610934587139259842734742404663471390884361351987200000000000000000000000000`.
That sum is strictly greater than
`714478572754719543167824087501333724720804913617853201633096523207449606906471341576499920353642669932544/25 = 2^{342} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-342}`.

The degree-110 partial sum is strictly below that same target, so this
comparison uses degree 111. The section error is therefore strictly below
`2^{-342}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=18` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-323}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-342}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-323}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-111 partial sum, and that
partial sum already exceeds `2^{342} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:32Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c18/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c18
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-361}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-323}` is the preceding audit. This `C=18`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
