# P104 source-consuming role exchange with eight residual replacements

This is a changed terminal consumer contract, not another fixed-cover census and not an admitted multiplication supplier. It starts after the retained PR1972/PR1991 forward channel, consumes its source bank, and produces every corrected sum `w = x+y`. It returns an explicit invertible encoding of the remaining data instead of pretending that the original source bank is restored.

The new result has two parts. An exact chronological tail returns `(w,q,v_N)` without adding a clean bank or touching the 72 original dirty helpers. A modulo-three argument proves that replacing at least eight of the naive 104 residual outputs is necessary in the specified reversible dyadic-linear model, even when arbitrary dyadic recoding and native chart changes are granted. Our tail replaces exactly eight. The corrected sums are not left in the original Y bank locations.

Canonical base is `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. The selected conditional kappa remains `0.001672660197076918`. Only this opt-in package is added. `TASK.json` records the explicit user assignment and changed scope.

## The exact boundary

Write `A=G/2=R^t R/8`, where R is the retained 8 by 104 doubled-root matrix. The predecessor channel leaves X holding x in FULL, Y holding `v=y+A x` in each target hyperplane, and its 72 arbitrary dirty helpers logically restored in FULL. Its native channel identity is inherited, not re-proved by this package.

Choose the eight mutually orthogonal retained roots `2(e0 +/- e2)`, `2(e1 +/- e3)`, `2(e4 +/- e6)`, and `2(e5 +/- e7)`. In canonical port order their indices are

```
J = [0, 1, 3, 6, 22, 31, 93, 103].
```

Let N be the other 96 indices and `B=A[J,N]`. All 384 nonzero B entries are signed halves. The pivot block is `A[J,J]=I`, and `A[N,N]=B^t B`.

Lift all 104 Y arrays to FULL. While every X_N source is still unchanged, perform both `X_J += B X_N` and `Y_J -= B X_N`. Thus X_J becomes `q=x_J+B x_N`, and Y_J already equals `w_J`. Then perform `X_N -= B^t X_J` and `X_N += Y_N`, producing `w_N`. Return X_N and Y_J to their respective target hyperplanes. Leave X_J and Y_N in FULL.

The final corrected-sum locations are X_N and Y_J. The residual locations are X_J for q and Y_N for v_N. All original dirty helper locations are untouched by the tail. Logical restoration at a changed frame is not a claim that the original physical input array is bitwise unchanged.

The inverse boundary equations are

```
x_N = w_N - v_N + B^t q,
x_J = q - B x_N,
y   = w - x.
```

They use only dyadic coefficients. They prove information preservation, not a free decoder or a caller that already accepts this representation. PROOF.md proves the identity, the modulo-three lower bound, and its precise exclusions.

## Invoice and stopping decision

The generated tail contains 1,664 formal events. These comprise 1,248 unit Gaussian array additions/subtractions, 104 exact array halvings, 104 restoring doublings, and 208 rank-one frame conversions. There are no new banks, private erasures, or clean-input assumptions. No source-independent dirty helper is substituted for a data pivot.

Under the inherited native dimension-gap tariff, the added profile is `208 H1`. Adding it to the retained channel gives `(1282,58,86,104,48,24,8,8)` at ranks 1 through 8, with total rank mass 2,576. These are formal frame conversions of the same hyperplane/FULL pairs already considered by the predecessor terminal audit. We have not recompiled their native recipes or executed their signed-floor implementations under the changed bank roles.

For 512 complex words per array, the scalar part alone has 1,277,952 real additions/subtractions, 106,496 real halvings, and 106,496 real doublings. These counts exclude native-pair arithmetic, addressing, movement, and control. In normalised common-chart coordinates, integer initial x and y require at most two fractional bits during the scalar tail, with a sharp coefficient denominator of four. The maximum row one-norm, including the channel-exit entrance, is exactly 26, giving a `26H` bound per real component. This does not certify the physical native entrance, the original channel's internal width, or accumulated rounding error.

Even granting the unchanged width-nine, 280-role bare local-mass relaxation, this profile has `M(0)=2576/(9*280)=46/45>1`. That numerical stop is inherited from the earlier 208-rank terminal-correction tariff, not a new general P104 lower bound. The changed logical boundary supplies no additional capacity or coverage by itself. A different consumer needs its own law and complete bill.

The decision is **NARROW**. Retain the exact changed-boundary module and the sharp eight-replacement result. Do not expand it into a supplier construction under the unchanged failed budget.

## Reproduction and evidence boundaries

From a complete checkout at the contribution head, use Python 3.12 and the standard library.

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-role-exchange-residue
```

The default primary command authenticates all three frozen source files, compares the 16-root extraction, and binds every original X, Y, and dirty-helper exit frame. It then checks all 280 independent input columns through the newly generated tail. The second implementation imports no primary code and reconstructs the complete endpoint using quarter-integer arithmetic and a different root enumeration. It also checks 16 signed fixtures. Tests distinguish the new output locations, arbitrary dirty inputs, the ordinary source-preserving correction shear, and malformed or altered receipts.

A portable algebra-only mode is deliberately weaker.

```sh
python3 -I -B research/p104-role-exchange-residue/verify.py --algebra-only
python3 -I -O -B research/p104-role-exchange-residue/verify.py --algebra-only
python3 -I -B research/p104-role-exchange-residue/independent.py --algebra-only
python3 -I -O -B research/p104-role-exchange-residue/test_verify.py
```

This mode uses the explicitly transcribed geometry and prints `ALGEBRA_ONLY`. It does not authenticate the complete repository sources. Normal mode fails closed when those files are missing. Frozen RESULT.json is compared without rewriting it. The canonical result digest is `0b869d0e68b8e21468a15977a31432d8b17f5a528558edec7eaf6c5461d63b78`.

Local algebra replays passed on CPython 3.13.5. Full source-bound and registered Python 3.12 results, where subsequently observed, belong in the PR handoff with their exact public head and run identifier. No native recipe replay, original 4,058-event channel replay, full selected cold replay, independent human review, or formal proof-kernel acceptance is claimed here.

## Relationship to predecessor work

Rohan Arun's PR1972 and Chafik Boukhalfa's PR1991 supply the forward channel and native lineage. The retained `p104-side-correction-rank-obstruction` package already proves the rational correction rank and determinant, the root-coordinate factorisation, and the 208-rank terminal screen. Its 2,376-add common-chart word and 1,352-add snapshot word are not new contributions here. The covariance identity `RR^t=104I`, ordinary Gaussian elimination, and modular rank arguments are likewise not claimed as new mathematics.

PR2383 already grants the complete root code for free under its monotone immutable-source contract. PR3427 and Sagar Thakrar's PR3810 address changed source preconditioning and fixed-cover support; the latter's channel-Y-read probe motivates testing coefficients and dirty-state semantics rather than interpreting support as a circuit. Their bounds do not transfer to a source-consuming changed output interface. Our eight-replacement result does not contradict PR3810's rank-23 preconditioner bound.

Clear1nsight's PR3609 uses eight in-place data pivots for a different dual-entrance completion. That pivot technique is related, not a newly discovered general technique here. The present object is the original forward 104-source/104-target terminal channel, with a different returned-source contract and a sharp modular obstruction to leaving every old channel-Y residual intact. PR3620 and the later caller audit reinforce the need to price the actual changed consumer rather than donate a boundary conversion.

Prepared by Clear1nsight with substantial OpenAI assistance. The two checking implementations share the same assisted session and sources. New work is Apache-2.0; source geometry and predecessor results retain their authorship and notices. See SOURCES.json for immutable source bindings and bounded overlap coverage.

## Open next questions

A useful continuation must name an actual consumer of `(w,q,v_N)` and prove its input/output intertwiner, ownership, return, and complete coverage law. Its first test is the full budget, because the unchanged width-nine relaxation already fails. Original-source decoding, residual erasure, and physical bank relabelling are not free operations.

Only after that gate passes should the 208 hyperplane/FULL recipes be rebound to the new bank roles and replayed with an actually supplied physical entrance. The scalar two-bit result alone does not establish exact native halves, finite-width safety, routing, tape use, or all-size admission. TASK.json records these concrete blockers without reserving them.
