# This section's polynomial-inverse error is strictly below 2^{-475}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-229
Taylor sum of `exp(361)` equals
`569618138540786716876918418531657612524503007077342700104364072746089587976291183612008251683365141547726587524252961444726472029686969080596515823098344141370012080084410454719952981336274625069613144528807730960312997273758957336531184232965493150528938118915642368891359451060208766601152049835900727495243838105051942956523704593289590497951464415720667962994673938213656590027641511686097186570655601800862348305491287807210319041170014939635371570743058797490813273317935210229449053835116863170220555642688414443028543677898257422955568576889169602304592743616283/1524093475838459110286316633820382633817874219511308365980521929887465503387385659418209074004083338717207769392085459973728367028980937058986158160466665197191300728039185768625353796353553869647031781854563893188465646495130920909966044124974209494654368839261479968817275562809069345148901179702806776569964710407347512107665750706610741076370791413822612535778568306688000000000000000000000000000000000000000000000000000000`.
That sum is strictly greater than
`7779982715240636889146324346125156652607834433672857790031805235316356130339884631393575366228546396874881179904130567997249251888226273536770048/25 = 2^{475} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-475}`.

The degree-228 partial sum is strictly below that same target, so this
comparison uses degree 229. The section error is therefore strictly below
`2^{-475}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=25` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-456}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-475}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-456}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-229 partial sum, and that
partial sum already exceeds `2^{475} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:44Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c25/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c25
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-494}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-456}` is the preceding audit. This `C=25`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
