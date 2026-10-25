# Proof and boundary of the slice test

## 1. Fixed formal model

Pin the two live inputs in SOURCES.json. The native payload has 632
persistent fields and one owned center. Treat each active main input and
all 408 helper inputs as a separate formal column. A row is a finite
rational linear combination of pairs `(input, warp_word)`. Each warp word
is a reduced word in the named source warp generators. Left multiplication
cancels an adjacent inverse. COPY, CLEAR, SCALE, and ADD act on the exact
rows. A paid climb changes the source frame but not its formal logical
row. Adapter and phase records do not change this row either.

This is the source's formal row convention. It does not replace physical
native admission. In particular, two distinct free words need not denote
distinct physical maps. Extra physical identities can produce other
candidates outside this test.

Initialize the unused main bank, or both banks, to zero. Replay each full
word and check all 632 endpoint rows and the owned center. The endpoints
are `(x,y+x,h)` forward and `(x-y,y,h)` backward. All helper columns remain
independent; no helper relation or owned-helper target deletion is used.

## 2. The declared backward slice

Every row write makes a new version. ADD depends on the old target and the
source; SCALE, warp, and paid jobs depend on the old target; COPY depends
only on its source; CLEAR has no value dependency. A retained output asks
for its final version. Take the transitive closure of these dependencies,
including the final owned-center clear. Then omit each paid event whose
row is proved zero in the complete replay.

Induction on source order proves that each retained version has the same
formal row after this deletion. Every dependency which can change that row
is retained. A deleted paid job on zero has zero output. The verifier also
replays the selected record sequence and checks the demanded endpoints,
so the implementation does not rely only on this induction.

The slice keeps the original scalar decomposition. It does not perform
algebraic reassociation, common-subexpression elimination, new response
reuse, or physical frame optimization. An owned field that is not demanded
can be cleared at the end. Such ordinary cleanup adds no Gaussian child.
All necessary physical movement or frame repair is granted for free in
the invoice. No legal native supplier is asserted for a sliced record list.

The two forward prefix variants omit records 0 through 6,036. Record 6,037
is the pinned `entry_adapters` phase. The exact replay checks the 520
retained rows in the X-to-X case, or all 408 helpers in the helper-only
case, and the owned center. Each variant has the same paid histogram as
its corresponding full-prefix slice. This is a check of these two
specified prefixes, not a theorem about every shorter preconditioner.

## 3. Complete target credit

Derive the helper ranks from the source entrance and exit frame dimensions.
They give 28 H4, 7 H7, 47 H8, and 326 H9 targets in either orientation.
All of them are credited, even though the slice is not physically admitted.
The source same-bank maps have rank eight. The nonzero cross-bank map has
rank nine. Credit 112 targets of the applicable rank when one main output
bank is retained. The helper-only cases receive no main targets.

These declarations define the price test. They do not assert independent
native targets for an arbitrary coupled interface. A different target
contract needs a separate invoice and proof.

## 4. Exact cost sign for every power

For a case, let d_r be its paid count minus its target count at rank r.
All ranks lie between one and nine. Define

    K(a) = sum_r d_r min(r,a),  1 <= a <= 9.

For an increasing concave function f on these integer ranks with f(0)=0,
put b_a=f(a)-f(a-1). Direct summation gives

    sum_r d_r f(r)
      = b_9 K(9) + sum_(a=1)^8 (b_a-b_(a+1)) K(a).

All coefficients on the right are nonnegative. For f(r)=r^t and
0<t<1, all coefficients are positive. The exact receipt has K(a)>=0
in every case and K(1)>0. Therefore paid cost is strictly greater than
target credit for every such t. In the usual t=1-kappa parametrization,
none of these invoices contracts for any 0<kappa<1.

This is a classical concave-order identity. The shared source tool gives
a second implementation of the hinge-sign comparison. The contribution
here is the authenticated source restriction, complete target accounting,
and exact certificates for the stated candidate slices.

## 5. What remains open

A new scalar word, a nontrivial relation among retained fields, physical
identities beyond the free-word model, a different output contract, or a
joint caller can escape this class. The dependency slice is deterministic;
it is not a proof that all legal prunings have been considered. This proof
makes no claim about their cost or the selected multiplication frontier.
