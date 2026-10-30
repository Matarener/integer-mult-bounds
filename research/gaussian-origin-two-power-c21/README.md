# This section's polynomial-inverse error is strictly below 2^{-399}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-149
Taylor sum of `exp(361)` equals
`5171133266652786947468019866487105716247763755628016763378800549360488738504557286755390437381699713345508953020226676041057868298475261656836786342115605448188988238224974729301779509636176576331835394811446832301112213681475415825996795658654929541432056481676093619084574711199029311194157768129956229137968869514675275449701160574157071248704133389640909665218234123/990965396479178069605383061356263873687822070351260383895578627897441370380937743319491877384128545753131977480415646251414507531873032855421707427799102877968550016583041858559696756500384595899513428783604265123840000000000000000000000000000000000`.
That sum is strictly greater than
`102967213888715480012529776983620098488897018489065287574122541842058323927921542635857108462045496028506638982413306298368/25 = 2^{399} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-399}`.

The degree-148 partial sum is strictly below that same target, so this
comparison uses degree 149. The section error is therefore strictly below
`2^{-399}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=21` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-380}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-399}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-380}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-149 partial sum, and that
partial sum already exceeds `2^{399} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:37Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c21/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c21
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-418}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-380}` is the preceding audit. This `C=21`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
