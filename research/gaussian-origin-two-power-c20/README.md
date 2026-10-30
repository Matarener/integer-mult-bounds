# This section's polynomial-inverse error is strictly below 2^{-380}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-135
Taylor sum of `exp(361)` equals
`757501976127725093044667257873836837660433988322951343086117401299070803389851295756239635181256661396609166393189201258432870655498053194717374521921904490963866233458586875198787267489618306555828831804173583883003413694052934906397093656904387456217983597491135319618769884486978579003724642347734281063168799221118372678667655499/69738395017157881019310411838840408194590270158181444276417171950468317719678738980107227896722531679115841543286797445993661218472803303128064069846707896953019420790449630692723654656000000000000000000000000000000000`.
That sum is strictly greater than
`196394374635153732323703340499153325059694325426226210735554774936787269454806409141267983364192001397145536389185536/25 = 2^{380} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-380}`.

The degree-134 partial sum is strictly below that same target, so this
comparison uses degree 135. The section error is therefore strictly below
`2^{-380}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=20` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-361}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-380}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-361}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-135 partial sum, and that
partial sum already exceeds `2^{380} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:36Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c20/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c20
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-399}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-361}` is the preceding audit. This `C=20`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
