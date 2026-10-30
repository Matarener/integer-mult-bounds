# Retained information after a unit overwrite

This is a scoped rational scalar statement in JosieElliston's PR6045 model,
not a physical helper-split construction. All event indices below are zero based,
with the cut immediately after the indexed event. New derivation by apoursh with
substantial OpenAI Codex assistance; Apache-2.0.

## 1. The information boundary

Let the original prefix map be R: K^n -> K^N, including every live owned field
and zero rows for inactive storage. The original public suffix map is S, and
M=SR is invertible. Let p be the overwritten field, e its unit vector,
ell=e^T R, and d=Se. The new independent input z replaces p, so the entire
available state is

    y = R X + e (z - ell X).

No external copy of X or the retired value is available; changes before the
cut are excluded. A later algorithm can read only this state and input-independent
constants. Let O be the public roles whose final chart is not final[p], as in
PR6040/6045. Its required original output is (MX)_O.

**Theorem 1.** If Rv=e and d_O != 0, no post-cut algorithm can restore the
required O outputs for every X,z. In particular, arbitrarily many linear
corrections, rewritten suffix events or scalar routing do not help under this
fixed-prefix/no-external-information contract.

Indeed, ell v=1. Replacing X by X+v while holding z fixed changes y by
Rv-e ell v=0, whereas the desired O outputs change by (Mv)_O=(Se)_O=d_O.
The two identical states require different answers. The argument permits any
deterministic continuation, even nonlinear or adaptive; this is an algebraic
information statement, not a claim about arbitrary native/address operations
outside this scalar model.

**Exact test.** Rv=e has a solution if and only if

    R M^{-1} d = e.                                           (1)

Necessity follows by multiplying by S, which forces v=M^{-1}d. Sufficiency
is the displayed equation. The verifier recomputes M from the full selected
word: M=I+H, with 104 disjoint X-to-Y shear entries, so H^2=0 and M^{-1}=I-H.
It checks this endpoint, rather than assuming M=I. All owned output rows are
zero and all owned lifetimes are closed.

**Converse, unrestricted readout only.** If e is outside col(R), finite-dimensional
linear algebra supplies a row w with wR=0 and we=1. Thus wy=z-ell X and
R X=y-e wy. Both the original state and z=y_p are recoverable linearly.
This does not produce a local, reversible or priced correction. The witness w
may use several charts, and later erasure may destroy the information. If e is
in col(R) but d_O=0, the original suffix already gives the desired O outputs.

## 2. Combination carriers and a complete finite reduction

At an event t>=i after the cut, let T be the original intervening state map,
R_t=TR, and beta_t=Te. A chart-local combination with coefficients a is a
carrier exactly when

    a R_t = 0,       a beta_t != 0,

because its value in the split word is (a beta_t)(z-ell X). These equations
refer to the uncorrected split word, before inserted corrections change the defect coefficients.

If (1) holds, beta_t=R_t v, so no such a exists at any chart or future event.
This disposes of all future checks for 4,009 of the 4,033 leak classes in the
inherited PR6040 `empty` census on the selected PR6030 word.

For each of the 24 remaining classes set v=M^{-1}d and

    delta_i = Rv-e,       delta_t = T delta_i = R_t v-beta_t.

A combination is a carrier iff aR_t=0 and a delta_t != 0. Therefore:

1. Charts disjoint from supp(delta_t) cannot have carriers.
2. Between events only the destination row/coefficient changes; MOVE also
   changes the two chart banks. A previously tested untouched chart keeps
   both its row matrix and delta restriction, so its answer cannot change.
3. At the initial cut all charts meeting the residual support are tested.
   At later events only the touched charts meeting that support need testing.
4. Once delta is zero, it remains zero under every later original linear event,
   and no further chart test is needed.

At each needed chart the checker performs exact sparse elimination while
carrying source-role coefficients. Each input row yields either a new pivot
or a zero reduced row. Every zero row gives a relation with coefficient one
on its new role and support only on preceding roles plus that role. These
relations are independent, and their number equals rows minus rank, hence
they form the complete left kernel. Testing their delta pairings decides all
linear combinations over Q, without bounded coefficient enumeration. Cached
kernels are invalidated at each touched chart, including INIT, CLEAR and both
ends of MOVE.

The complete reduction performs 1,814 class/chart checks and 196 kernel
computations. In 22 cases no carrier occurs before delta vanishes. Together
with the 4,009 global certificates, **4,031 classes have no combination carrier
at any later event/chart**. This is not an exclusion of every possible
multi-step non-carrier correction in the residual 22 cases.

## 3. The two positive cases

The remaining classes are (cut,p,chart)=(13637,572,595) and (13639,572,595).
Event 13637 is COPY 778 <- 572, so the original rows of 778 and 572 are equal
and nonzero at both cuts. Overwriting 572 gives the literal relation

    field_778 - field_572 = ell X - z.

Both fields are at chart 595. Neither is individually zero in the original
word, so this is a genuine combination carrier that PR6045's single-field
criterion cannot detect. The checker validates the full original row equality,
chart availability and the nonzero beta coefficient -1 at both cuts.

A first witness suffices to classify each positive case. The registered scan
stops those two cases at the witness; it does not claim to enumerate every
later carrier or every possible correction sequence.

## 4. A closed invariant excludes every combination-carrier program

The following enlarged correction class includes a simultaneous multi-ADD
from any chart-local combination carrier: at an original event window, choose
an existing target r at the same chart and a rational row a supported there,
with a R_t=0, and apply the atomic update

    field_r += q * (a fields).

Any finite sequence is allowed; a and q may differ at every update. No original
MOVE, COPY, INIT, CLEAR or other scheduled event is changed, and no fields or
external data are added. Intermediate operations that change the original
rows outside such a completed atomic update are not covered. This is a scalar
relaxation with no restriction on its physical cost or reversibility.

The state retains the form `R_t X + beta (z-ell X)` because a R_t=0. Define

    d = S_t beta,
    delta = beta - R_t M^{-1}d.

Original scheduled events preserve d and propagate delta linearly. A permitted
update sends beta to beta + q e_r(a beta); since a beta=a delta, it sends

    delta -> delta + q (e_r-R_t M^{-1}S_t e_r)(a delta),
    d     -> d     + q (S_t e_r)(a delta).                      (2)

For both positive cuts, initially delta=-e_778. The finite certificate checks
all of the following, not just the two initial snapshots:

- At every window 13637..13651, chart 595 has exactly the six roles
  `[127,572,581,582,731,778]`, and its complete left kernel is generated by
  `778-572`. Every other chart misses 778, so its relations pair to zero with
  any delta in span(e_778).
- At all 15 windows, every one of the six target vectors
  `R_t M^{-1} S_t e_r-e_r` lies in span(e_778): **90 exact projection checks**.
  Thus (2) preserves this residual line, for arbitrarily many corrections.
- Every corresponding full public suffix column lies in the same space W,
  spanned by the columns at cut 13637 with indices `[127,572,581,582,731]`:
  **90 exact full-column span checks**, not only selected output coordinates.
  Both initial d vectors also lie in W.
- Restriction of that basis to outside rows `[127,120,116,176,134]` is upper
  triangular with diagonal `[1,-1,1,-1,-2]`. Its determinant is -2. Hence
  dim(W)=5 and restriction W -> K^O is injective.
- The original events preserve e_778 through 13655. Once 572 leaves at event
  13652, the chart containing 778 has independent rows at all four windows
  13652..13655. There is then no effective correction. CLEAR778 at 13656
  erases the residual, which stays zero forever.

Induction in the number of updates proves delta stays on the certified line
and d stays in W. After the active windows no correction can act effectively.
If a program clears the outside z-leak, d_O=0; injectivity gives d=0 on every
public output, violating the requirement that z reach a V-final output. This
already fails the z condition, irrespective of the non-z rows or pairing.

For the other 4,031 classes, a first effective permitted correction would need
a carrier of the uncorrected word, and none exists. Therefore **none of the
4,033 classes can be legalized by any finite program of these combination-carrier
updates**. The 4,009 information-loss certificates give the stronger arbitrary
post-cut obstruction separately.

This does not rule out general non-carrier edits in the remaining 24 classes,
new routing, a changed prefix, added retained storage or non-unit injections.

## 5. Evidence and limits

The inherited census defines the 4,033 classes; its completeness outside that
definition is not re-proved. Nick Petalas's unmodified module is executed after
byte authentication. The new prefix/suffix interpreter, sparse transpose,
information test and residual scan are separate from PR6045's carrier engine.
A second AI-assisted implementation obtained the same 4,009/24 split and
2/22 residual classification; this is not independent human acceptance.

The registered small controls compare 4,410 decoding cases with an independent
dense row-span oracle, and 3,780 endpoint/pivot cases with Cramer's-rule
membership. They test missing endpoint inversion, retained copies, no single
zero row, wrong signs, dead storage and d_O=0. Four local implementation mutations (wrong endpoint inverse, omitted kernel
relations, wrong suffix ADD sign and retained cleared delta) are rejected by
the production controls. The production kernel is checked
against the independent rank oracle on all 154 matrices in its declared small
domains; every scalar opcode is checked against literal row multiplication.

The all-future statements follow from the written invariants and the complete
finite input census, not from random sampling. No native operator, normalization,
caller, compiler, precision/tape, full paid invoice or outer-bound replay is
claimed. All five selected framework assumptions remain. There is no new κ.
