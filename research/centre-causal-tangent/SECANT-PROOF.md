# A discrete two-point strengthening

Clear1nsight with substantial OpenAI assistance. Apache-2.0.

The first-variation theorem requires correctness near z=1. The following
strengthening only requires the same fixed linear programme to work for two
scalar oracles, +1 and -1. It still does NOT prove a lower bound for one fixed
native Fourier operator whose coefficients and identities are known.

## Causal feedback factorisation

Use the exact source and final-response matrices C and B from PROOF.md.
Let K map additive centre-output errors at z=1 to later centre-input changes.
In chronological order K is strictly lower triangular, including changes
within a local call. Thus K is nilpotent. This is the same causal feedback
principle used in Tekalign/PR2814, applied here to the full input/output map.

For centre multiplier z and delta=z-1, the vector e of innovations satisfies

    e = delta (C x + K e).

Hence, with baseline endpoint F(1)=I,

    F(z)-I = B (I-delta K)^(-1) delta C.

Since I-delta K is unitriangular, its determinant is one for every scalar delta.
For delta nonzero, its inverse times delta is invertible. B is injective and
C surjective on the1152-dimensional site space. Consequently

    rank(F(z)-I)=1152 for every z != 1.

In particular rank(F(-1)-F(1))=1152. For the reciprocal forward/backward model,
z=-1 also assigns -1 to every centre, so the same two-point conclusion holds.
More generally the formula uses a diagonal Delta; invertibility requires its
entries nonzero. Only the common -2 case is claimed by the finite certificate.

## Two-point query-rank theorem

For two sequences of matrices M_t(-1), M_t(1), the telescoping product identity
expresses F(-1)-F(1) as the sum, over t, of

    P M_(s-1)(-1)...M_(t+1)(-1)
          [M_t(-1)-M_t(1)] M_(t-1)(1)...M_0(1) J.

Thus the rank difference is at most the sum of the gate-difference ranks.
Parameter-independent free maps contribute zero, and a single-register oracle
multiplication by z or its inverse contributes rank one. Any fixed causal linear
circuit correct for both oracle choices therefore needs at least1152 queries.
There is no continuity assumption. Both +1 and -1 satisfy z^4=1, so merely
restricting an otherwise unknown oracle to fourth roots of unity does not
permit generic half-sharing for this endpoint.

This does not say a fixed known operator needs1152 recursive calls. Known
operator-dependent free maps, different required outputs, nonlinear algorithms,
larger-rank gates and costs outside this scalar query model remain separate.
The z^4 I example in PROOF.md has zero two-point difference and is correctly
NOT rejected by the secant bound, even though its derivative at1 is nonzero.

## Bound finite checks

secant.py reconstructs every local feedback row, composes them through the
actual owners and bridges, and verifies strict triangularity in the literal
centre order. It solves e=-2(Cx+Ke) on a dense signed rational fixture, and
compares all1152 innovations and all14336 final outputs against a separately
coded full scalar execution at z=-1. Every2,835,792 scalar instruction remains
present. The generic feedback/resolvent reconstruction and the literal point
interpreter do not share state-update routines. They share the pinned archive,
source parser and the credited mathematical semantics.

A cycle mutation is rejected. Omitting K must change the actual selected output,
so the feedback control cannot pass by testing an already feed-forward zero K.
The full rank theorem follows from the written factorisation and certified
B/C ranks, not from the single dense fixture. No extra native/source/hosting
premise is discharged. No independent human or proof-kernel review is claimed.

This is a refinement within the same conditional contract, not a selected
frontier change. Source inputs remain pinned at canonical20ecf289. The second
checkpoint found main unchanged; targeted centre/secant PR search found no
match, which is not exhaustive novelty evidence.
