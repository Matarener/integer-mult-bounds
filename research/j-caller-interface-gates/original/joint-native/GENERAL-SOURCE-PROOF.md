# Arbitrary source monomials leave the fixed-core support gap

This is the strongest fixed-architecture result in this lane. It extends
`UNIVERSAL-KERNEL-PROOF.md` from the old whole-plane swaps to arbitrary
physical source monomials. It keeps the scalar core, scalar retraction
word and diagonal continuation. It does not assume a causal support for
the source monomials, does not commute them through a Fourier frame,
and does not impose a Clifford or tensor-product assumption on them.

Let `q>=2`, `k=2q+1`, and `m=4q+4`. Put `F_0=I` and
`F_s=N_s F_(s-1)`. The actual native `N_s` has rank/support arity `2f`.
The exact response J obeys `J^2=-I` and the desired output is `F_k J`.
For a separately admitted source query

    K_s=F_(s-1) J F_(s-1)^-1,

the physical stage applies K_s to the source, makes its scalar delivery,
applies a physical source monomial S_s, and applies fresh N_s to every
other bank. Its retarded source code is exactly

    B_s=F_s^-1 S_s F_(s-1) J,
    D_s=B_s J=-F_s^-1 S_s F_(s-1).                  (1)

Both original fields are arbitrary. Equation (1) follows from the
literal stage and does not identify a raw source code with S_s.

The same arbitrary-B scalar/core interface has

    Q1=J^-1 B1 J,
    K=[[B2+Q1-I,I-B2],[Q1-I,I]],
    Dv=D_(2q+1) (-D_(2q-1))...(-D5).

Its required original-t/current-V coefficient is

    C=F_k B1^-1 J B2^-1 Dv^-1 F_k^-1.

The two entrance codes telescope **without a commutation**:

    B1^-1 J B2^-1
      = J^-1 S1^-1 F1 J J^-1 F1^-1 S2^-1 F2
      = J^-1 S1^-1 S2^-1 F2.

Inserting N1 between S1^-1 and S2^-1 is generally false; it would require
an additional frame-commutation relation. Define

    G=S1^-1 S2^-1 F2 Dv^-1,
    R=-F_k G^-1=-F_k Dv F2^-1 S2 S1.

Exactly as before, `C R=F_k J`: only `J^-1=-J` is used.

Now substitute (1) into Dv. There are q-1 factors D_s, each with a minus
sign, and q-2 recurrence minus signs. Their combined sign is always -1.
Every adjacent fresh prefix then cancels literally:

    Dv=-F_k^-1 S_k N_(k-1) S_(k-2) N_(k-3)...S5 F4,

because `F_(s-1) F_(s-2)^-1=N_(s-1)`. Hence

    R=S_k N_(k-1) S_(k-2) N_(k-3)...S5 N4 N3 S2 S1. (2)

The sign in (2) is **plus for every q**. No N_i/S_j commutation has
occurred. Even mutual commutation of the N_i is unnecessary for this
telescope when the prefix convention above is used.

There are exactly q native N factors in (2), each with row support
`2^(2f)`, and q+1 source monomial factors, each with row support1.
Arbitrary cancellations can only reduce support. Thus

    maximum row support(R)<=2^(2qf).                 (3)

If the required target `T=F_k J` is full native, each row of T has
`2^(mf)` nonzeros, including its actual declared monomial gauges.
`T=C R` and (3) force every row of the required coefficient to have
at least `2^((2q+4)f)` nonzeros. Consequently every complete joint tail
in the native/monomial/binary-ADD model satisfies

    total actual native arity + literal binary ADD count
        >=(2q+4)f.                                  (4)

The full bank/address state includes all arbitrary dirty helpers. This
is an unfactored joint inverse bound: public-reader fusion, arbitrary
monomial bank/address routing and restoration of additional dirty banks
do not change the required original-column equation.

For the fixed separate-call prefix, full target support also forces each
Clifford K_s to have native arity at least2f, by
`T=(F_k F_(s-1)^-1) K_s F_(s-1)` and native-arity subadditivity.
The two fresh factors together have arity `(m-2)f`. The prefix's native
mass is therefore at least `nm-2q`. With the parent's separately stated
positive-volume full-scan transfer premises, a cleanup below native
mass `(2q+4)` is inadmissible. Under those combined premises the complete
mass is at least `nm+4`, which cannot beat the full-output stock nm.

This last cost conclusion assumes the separately exposed query sites,
the native fresh progresses and the literal full-scan implementation.
It is not a conclusion about every O(f) controller. Partial/local scan
work, cross-cut fusion or a changed transfer model must be evaluated
from its real volume bill.

The producer checks (1)--(2), the generic base collapse and `C R=T` in a
free noncommutative operator algebra at q2..25. Apart from `J^2=-I`,
every N_s and S_s is an independent invertible generator. A falsely
commuted N1 and a wrong final sign are both rejected. The written
telescope proves the all-q identity; the finite grid corroborates it.
The actual frozen-J physical prefix and inverse coefficient are pinned
independently at q2/q3 in `LITERAL-INVERSE-BINDING.json`.

The meaningful remaining changes are a different scalar core or retained
continuation, a changed delivery map, cross-cut query fusion, or a new
terminal input/target/coupled-owner contract. Choosing another response J
or another physical monomial S_s inside this fixed architecture does
not reopen it. No improved kappa, full supplier, owner, precision or
fixed-tape theorem is claimed.
