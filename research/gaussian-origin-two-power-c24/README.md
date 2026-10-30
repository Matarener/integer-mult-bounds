# This section's polynomial-inverse error is strictly below 2^{-456}

At `p=19`, `beta0=-1/2`, bandwidth 2, and `t_i=i`, the error of
`P = p^{-20} sum_{j<J} Q^j H*` on the normalized Schur section
`0,1,2,7,8,9` is strictly below `(319/100) exp(-361)`. The degree-204
Taylor sum of `exp(361)` equals
`40094964013020926876279498715089065990091799703903192924599891975568075047336562948188643648377920567793840537831813332477271608350189126183778399386507642633921678678568064471319014640059675625850594770819929567950354949564535351895036083240517724297106425979895364860894847463764746313615516197036986548265709980788581624542418829695216811538750166888704731247310442323691372051294427685837303318820645168155615191126104978350226371954762219154614603150215365432528622049037810030376224473451392885149210181/43256986238123995776914811889885227784029662690732675344245166494292456928440971631890911560969965944527839942895595502234611557996597267269398309245322401180303855680208669509252558824309958060045226996298772563181369767940773137429352758654506344736042030756157831784347920605194085028070648048128127034852553414835961856000000000000000000000000000000000000000000000000`.
That sum is strictly greater than
`14839139395219110277454994861841500573363942019792285518706903906471931706123132002627516491372196954488527641113530288691042426849796816896/25 = 2^{456} * (319/100)`,
and the next Taylor term is positive, so

`(319/100) exp(-361) < 2^{-456}`.

The degree-203 partial sum is strictly below that same target, so this
comparison uses degree 204. The section error is therefore strictly below
`2^{-456}`. No new kappa is claimed. The selected record is unchanged.
This is the case `C=24` on one normalized section, not the note's claim
for every fixed `C`. The matrix `Q` is not formed. The majorant and the
`2^{-437}` comparison are the preceding audits; this package replays
those proofs and adds the `2^{-456}` comparison.

## The Taylor comparison

`FINE-PRIME.md` says the polynomial error is below `2^{-Cp}` for every
fixed `C` eventually. The preceding audit puts this section below
`2^{-437}`. Every term of the exponential series is positive, so
`exp(361)` is strictly larger than its degree-204 partial sum, and that
partial sum already exceeds `2^{456} * (319/100)`.

Upstream main `12fa8c5c844be21bfefb38a19503fbd867a11244` was fetched at
`2026-10-21T15:50:43Z`. Priority revision 7 and the selected kappa were
unchanged, so this comparison continues the open question of the
preceding package.

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/gaussian-origin-two-power-c24/verify.py
python3 -B scripts/research_package.py --package research/gaussian-origin-two-power-c24
```

The verifier authenticates the pinned notes, replays the preceding
bound, and checks the Taylor comparison.

## Open next questions

The same majorant has not been compared with `2^{-475}`.

## Credit

Cinna Davis wrote the narrow kernel in the PR4100 Gaussian note. Nick
Petalas's HALO audit records the identity `P - H^{-1} = -Q^J H^{-1}`.
The bound by `2^{-437}` is the preceding audit. This `C=24`
comparison is this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
