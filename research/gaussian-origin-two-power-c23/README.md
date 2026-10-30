# This section's polynomial-inverse error is strictly below 2^{-437}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-183
Taylor sum of `exp(361)` equals
`1650501676132405388197320574198802985324558206927236643359714851517738141728910248346774170982482595784143444303480849338086638911025148883879789389512493178265275671643032268931508642234256249300651748749453848541010398578859483082790067705947690139020325723073780571340521138945473494225404579121765584479428325739106282189501802673077283810937332188147716289086875609528511283476091317813989893308642521953551104629808236862288149358489752022142258479161/938274854418482662048762791145439963880591035870203676076062603752685933552983904907737558073467255315765288901339648120185359258308390611323453345334582255084018317742865805471208784605013270383731451304663103447919358604402853400809884482428276091291860547067184203460947161907200000000000000000000000000000000000000000000`.
That sum is strictly greater than
`28303412237585278086576451991732598444679149665436335599340255558914054310079826359992058737511056813218169481494007661230168203067392/25 = 2^{437} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-437}`.

The degree-182 partial sum is strictly below that same target, so this
comparison uses degree 183. The section error is therefore strictly below
`2^{-437}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=23` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-418}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-437}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-418}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-183 partial sum, and that
partial sum already exceeds `2^{437} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:41Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c23/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c23
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-456}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-418}` is the preceding audit. This `C=23`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
