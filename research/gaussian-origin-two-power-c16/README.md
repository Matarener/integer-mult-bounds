# This section's polynomial-inverse error is strictly below 2^{-304}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-90
Taylor sum of `exp(361)` equals
`1008461552729788200989800802405954753234693592775569902838255455490087277816909294018935754107007376895651622119939917382602344107238743700543391700077302773742199329686772050318414292641076836359907423406908813857646289193/7515118022184638367041343654170790994448993776291097727630764006676063269370736326234865270945389714044092416000000000000000000000`.
That sum is strictly greater than
`2599257905802804246078536698410366533501673670317734655811715213376190538498017637090015051776/25 = 2^{304} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-304}`.

The degree-89 partial sum is strictly below that same target, so this
comparison uses degree 90. The section error is therefore strictly below
`2^{-304}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=16` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-285}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-304}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-285}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-90 partial sum, and that
partial sum already exceeds `2^{304} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:29Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c16/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c16
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-323}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-285}` is the preceding audit. This `C=16`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
