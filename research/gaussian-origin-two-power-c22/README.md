# This section's polynomial-inverse error is strictly below 2^{-418}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-165
Taylor sum of `exp(361)` equals
`5260814564995170496507579779554589692559648601553154213271379056139863819632650422713794691020817353323396678394579961583838916345124694289065678301457146758830914852566135126246066416205498406722466315561251265348071232810205247442558679830453146749724302354063205814786731546061013507958818129111416860375547497691196442861360506827251447196928816164800623544539987172593654965534375234341490441647617825177943/1596811768248432992343050888968299689023296992495136178373351413497595123761779714066399208932786377661629876667819503149187802847745073309239503985671084950866619087305511904664362840251374034686694004582046427904812825815239452889374354445434880000000000000000000000000000000000000000`.
That sum is strictly greater than
`53984474635286861584809211715188214196546840029595061491661559217289074535522129745468251681348909021793688738811507532558761984/25 = 2^{418} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-418}`.

The degree-164 partial sum is strictly below that same target, so this
comparison uses degree 165. The section error is therefore strictly below
`2^{-418}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=22` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-399}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-418}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-399}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-165 partial sum, and that
partial sum already exceeds `2^{418} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:39Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c22/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c22
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-437}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-399}` is the preceding audit. This `C=22`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
