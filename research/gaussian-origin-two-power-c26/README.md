# This section's polynomial-inverse error is strictly below 2^{-494}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-263
Taylor sum of `exp(361)` equals
`89916265751025145961304792098703888653180736501334798838826990521402037653383736907256429318993471461271319501666908386764117924423358249284313085244615924105835413738700951739263938155001980711974989791002396557014735740213014825150163595521338479711258922498055382082547970463858374467742483225102890564486348970913393467271534700298090319292577462656751203360408022199263139966018541349256651919438692439608369389678645884637480713155868901208814246601968625079836632374786958228292986987109942234445975610188905588775596745926765595484395364154554977039076128164767921418877687444672843004653583622579342205611628565743742113700101670004630101955137701/409507373563476582684684394555330018425039910609161374045739288914555011560347755568211217227427128884635540626380105552827924788735540328763937062182375585250251699070492617872000142559174440453522235743121907598124466180281841027589243901119400433545735460333430169471818519024503661233490302414294321085952289353304195663887238010705972469070588030654786869211586574975035419190152543930606501908134098483666839347616219796363859014073712640000000000000000000000000000000000000000000000000000000000000000`.
That sum is strictly greater than
`4078951577808083033336748098781266131082456299561475265020195103213541722863637433624074841609232133324737704049576807234141815773974376500046094925824/25 = 2^{494} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-494}`.

The degree-262 partial sum is strictly below that same target, so this
comparison uses degree 263. The section error is therefore strictly below
`2^{-494}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=26` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-475}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-494}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-475}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-263 partial sum, and that
partial sum already exceeds `2^{494} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:46Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c26/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c26
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-513}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-475}` is the preceding audit. This `C=26`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
