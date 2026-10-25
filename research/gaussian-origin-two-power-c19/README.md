# This section's polynomial-inverse error is strictly below 2^{-361}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-122
Taylor sum of `exp(361)` equals
`7865466154204711118348371151713360914254526871037724606681900274827251963463628250671329107304562086655419793234735735723025190925263578200902596440071250737886827843735854710014020895847943970075529886732130070171183812232755364518972803850229221642113940404556793805130960094452952104522640540309421/496810457911212115619371041077295155227482058310677492331996395431007986880727574984977862532577970954578106426303073835399977576123122252996310187815549491664335667200000000000000000000000000`.
That sum is strictly greater than
`374592541952426399848372155187899255866421366550877019377812909959387339505780046732459990242370608133593628672/25 = 2^{361} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-361}`.

The degree-121 partial sum is strictly below that same target, so this
comparison uses degree 122. The section error is therefore strictly below
`2^{-361}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=19` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-342}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-361}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-342}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-122 partial sum, and that
partial sum already exceeds `2^{361} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:34Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c19/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c19
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-380}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-342}` is the preceding audit. This `C=19`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
