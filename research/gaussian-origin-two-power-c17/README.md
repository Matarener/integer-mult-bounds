# This section's polynomial-inverse error is strictly below 2^{-323}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-100
Taylor sum of `exp(361)` equals
`184815978517684490740844659077199914137867681033228529994468824307473853380387806562332060374008927639068543556147368343235418922601991634205441845143545646638968412007436071787828585087885472530049082378482381428846083359082081154408569441882228347/2217107385066404208006679739956864798233881512919209788998338869402746250387021625286185197340810455722149518749101231133687808000000000000000000000000`.
That sum is strictly greater than
`1362759728917540632568023848536174249116525485263544467226212545790576185048048670914649811465535488/25 = 2^{323} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-323}`.

The degree-99 partial sum is strictly below that same target, so this
comparison uses degree 100. The section error is therefore strictly below
`2^{-323}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=17` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-304}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-323}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-304}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-100 partial sum, and that
partial sum already exceeds `2^{323} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:31Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c17/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c17
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-342}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-304}` is the preceding audit. This `C=17`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
