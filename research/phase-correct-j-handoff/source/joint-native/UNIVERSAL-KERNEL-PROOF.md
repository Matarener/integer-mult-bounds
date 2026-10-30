# The fixed-core joint cleanup is independent of the kernel choice

This theorem extends the original-column coefficient gate. It retains the
same initial core, source post-ADDRESS swaps, scalar diagonal-handoff
architecture, and actual output contract `T=F J`. It does not separately
undo `Du` or `Dv`, and it does not assume that `J` is an X-character
quadratic, a Clifford, or a bitwise tensor. Its scope is an exact linear
operator identity and a row-support bound; the transfer cost of growing
full scans is a separate theorem owned by the parent.

Let `q>=2`, `k=2q+1`, `m=4q+4`, and `f>=1`. The physical native planes
`N_i` obey `N_i^2=-I` exactly. Whole-plane swaps `P_s=(0,s)` relabel
them without extra phase. Put

    F=product_(j=1..k) Nj,
    Dv=(-1)^(q-2) (P_(2q+1)N0)...(P5N0),
    G=N0 P1 N0 P2 Dv^-1.

Assume an actual invertible operator `J` with its exact phase contract
`J^2=-I`, admitted queries/source maps, and the original-column interface
of `JOINT-COEFFICIENT-PROOF.md`. That interface gives

    C=F J^-1 G F^-1

as the coefficient from current V to the output on the original t
input. It is part of the unique full joint inverse and is independent of
the arbitrary public-reader block. Define

    R=-F G^-1.

Then, with no commutations at all,

    C R = -F J^-1 G F^-1 F G^-1
        = -F J^-1
        = F J = T.                                  (1)

The sign in (1) is essential: `J^-1=-J`. All global Gaussian phases are
retained, and there is no replacement of the output gauge by `E=N F`.

## The complement R is fixed and has arity 2qf

Use the exact signed plane algebra in which a word is
`sign * product_(i in S) N_i * P_pi`. Its multiplication rules are

    P_pi N_i = N_(pi(i)) P_pi,
    N_i N_j = N_j N_i,
    N_i^2 = -I.

They hold for every f for the actual typed Gaussian operators, not just
for their binary tableaus. Moving the permutations right in

    R^-1=-G F^-1

leaves precisely the native planes

    {3,4,6,8,...,2q}.                                (2)

There are q distinct planes in (2). The remaining factor is a literal
whole-plane ADDRESS permutation and the accumulated sign. Thus

    arity(R)=arity(R^-1)=2qf,                         (3)
    maximum row support(R)=2^(2qf).

The producer keeps the exact sign and permutation, checks the signed
algebra and both inverse orders for all q in its finite grid, and
independently extracts the actual complete binary shear of `R^-1`.
It is the diagonal projection onto (2), on both p/q halves and every
chunk bit. Written permutation relabelling proves the formula for all
q. Actual Gaussian amplitudes check the normal-form phases at q2/q3.

## Universal coefficient support

Suppose the actual desired output `T=F J` is full native on mf axes,
including both of its declared monomial adapters. Every physical row of
T has exactly `2^(mf)` nonzeros. For each row y, equation (1) and row
support submultiplicativity give

    2^(mf) <= support(C_row_y) * 2^(2qf).

Therefore every such coefficient row has at least

    support(C_row_y) >= 2^((2q+4)f).                  (4)

C need not be a Clifford. If it is a Clifford, (4) is the native-arity
lower bound `arity(C)>=(2q+4)f`. The frozen even-parity J attains this
bound exactly. A different affine X-character linear part, a wider
quadratic support, or an operator J outside that class cannot improve
the bound while leaving (1), (2), and the full target unchanged.

The producer includes actual phase-exact checks for the frozen J, old
common N, and a genuinely nontrivial X-character linear-part example:
`J'=M N0 SWAP(plane1,plane2) M^-1`, with the frozen monomial source
chart M. The disjoint SWAP commutes with N0, so `J'^2=-I` for every f.
All three examples have a full actual FJ endpoint. The broader proof is
(1)--(4), not extrapolation from these examples.

## Complete circuit consequence

For the full bank-by-address linear tail, include every arbitrary extra
dirty bank and every private row. Let `A(f)` be the sum of the actual
arities of its one-bank native Fourier children, and let `S(f)` be its
number of literal binary bank ADD primitives. Physical monomial maps,
pointwise Gaussian scalars/phases and bank/address permutations have
row branching1. ADD has branching at most2 and a rank-r child has
branching `2^r`. Hence the full row support is at most
`2^(A(f)+S(f))`, including all possible cancellations. From (4),

    A(f)+S(f)>=(2q+4)f.                              (5)

Neither bounded scalar coefficients nor a finite monomial dictionary is
assumed. An operator-valued ADD must expose its binary ADDs or its actual
branching, and an additive native query must expose its delivery ADD.
Extra dirty banks, their restoration and coupling to public outputs do
not remove this original-column coefficient.

Thus `A(f)=R f` with `R<2q` requires `S(f)>4f`. A bounded-in-f or o(f)
ADD count cannot rescue the current prefix. A paid O(f) construction is
not excluded by (5) alone.

The parent's source-bound [full-scan transfer note](../root-joint/FULL-SCAN-TRANSFER.md)
separately assumes each counted ADD scans a positive fixed fraction of
the field volume in the retained integer-width transfer. Under exactly
those implementation premises, linearly many ADD scans cost
`Omega(V e)` and violate the required sublinear e-power toll. This
conclusion does not cover partial/local scans, a fused implementation
with a different volume bill, a changed contraction/precision model or
another transfer theorem. No automatic prohibition of arbitrary O(f)
controllers is inferred from a count alone.

## Source query lower bound and the fixed-profile cost gate

For a separately exposed physical source/continuation query, write

    K_s=F_s J F_s^-1,
    T=(F_k F_s^-1) K_s F_s.

The two fresh factors together have native arity `(m-2)f`. If K_s is a
Clifford, native-arity subadditivity and full arity(T)=mf imply

    arity(K_s)>=2f.                                  (6)

Without a Clifford assumption, the same row-support argument gives
`maximum row support(K_s)>=2^(2f)`. Calling that an arity still needs
an admitted native implementation. It must not be assigned a binary
B-rank merely by analogy.

Under the separate-call architecture, the `n*k` stage advances and
`q+2` shared-input/continuation/final calls therefore have native mass
at least `2(nk+q+2)=nm-2q`. With the full-scan transfer premises, (5)
requires cleanup native mass at least `2q+4`. The complete mass is then
at least `nm+4`, exceeding the full independent-output stock nm.
For proper child ranks and any exponent p in (0,1), `(r/m)^p>=r/m`, so
this mass inequality already prevents a favorable full-output moment.

This paragraph retains separately paid query sites and fresh progresses.
Cross-cut query fusion or a changed physical source/delivery map must
receive its own whole-word invoice and is outside that counting premise.

## What actually reopens the problem

The obstruction is not a global supplier lower bound. A changed initial
core or post-source map can change G and hence the complement R. A
different terminal coupled-owner contract changes the required inverse
coefficient. A cross-cut prefix/tail fusion can change the separate-call
profile. A different fully priced local/partial-scan implementation can
leave the full-scan transfer model. Each is a material construction
change requiring all original columns, literal inverse, phases and costs.

Merely choosing another J or enlarging the monomial alphabet inside a
cleanup of this fixed original-column map does not change (1).

All evidence is local mathematical derivation and exact finite replay.
No formal-kernel proof, admitted all-size multiplication supplier,
owner allocation, precision/tape realization or new kappa is claimed.
