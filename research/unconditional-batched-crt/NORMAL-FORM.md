# Good-packet normal form over the full local ring

Independent algebra audit, 2026-10-19. This proves one auxiliary identity;
it does not establish a multiplication exponent or the machine cost.

Let R be a commutative ring, C the m-coordinate reversal, and P an
idempotent whose image is a free rank-r direct summand. Suppose unit-pivot
northeast elimination gives unit lower triangular L and R0 with

    T = L P C R0 = E D C,

where E=diag(I_r,0), and D is diagonal with unit entries delta_0,...,
delta_(r-1) on the first r positions (put 1 on the remaining positions).
The remaining block is zero over R: elimination gives a block diagonal
matrix with an invertible r-by-r block and a Schur block S; split rank r
implies S=0. More explicitly, the projection onto the selected r rows is
an isomorphism on im(P), since its restriction to r image columns has unit
determinant. Every other image column has the unique linear combination
given by those rows, so its eliminated remainder is zero. Reduction modulo
the residue field alone would not suffice for this conclusion.

Set

    U = L P L^-1,  S0 = R0^-1 C L^-1,  J = C D^-1 E.

Then TS0=U, TJ=E, ET=T, UT=T. Since im(U) is precisely the first r-coordinate
summand and U is its projector, EU=U and UE=E. These equalities hold in R,
without division by a nonunit. Define

    X = S0 E - J U,
    Q = [[I,0],[X,I]] diag(L,R0^-1).

In particular TX=E-U. For the unweighted partial interchange

    N(P) = [[I-P, P C],[C P, I-C P C]],

direct block multiplication gives

    diag(L,R0^-1) N(P) diag(L^-1,R0)
      = [[I-U,T],[S0 U,I-S0 T]],

and hence

    Q N(P) Q^-1 = [[I-E,T],[J,I-JT]].

The lower-left block reduces as follows, recording the cancellation that
is easy to get wrong:

    S0 U - X(U+TX) + S0 TX
      = S0 E - X E = J.

The lower-right block is I+XT-S0T=I-JT. Thus the transformed map exchanges
head coordinate k and tail coordinate m-1-k with weights delta_k and
delta_k^-1 for k<r, and fixes the other coordinates. This is exactly one
weighted reversed r-coordinate child.

## Agreement with the retained coefficient construction

In `research/selected-bit-recursive-closure/vendor/controlled_normalizer.py`,
`left=L`, `right=R0`, `a0=-U[:r]`, and `b=-S0[:,:r]`. Its first r columns
of `cross` are S0 E-J, while the other columns are -J U. Because UE=E,
these are exactly X=S0E-JU. The apparently different formulas therefore
agree for every admitted ring value, not only the small test moduli.

Head elimination uses lower shears from k to i>k. Column elimination
right-multiplies by lower shears; executing their negatives in chronological
order on the tail implements R0^-1. Cross shears all go from the earlier
head bank to the later tail bank. All slots, including zero coefficients,
remain in the schedule. The inverse adapter reverses this schedule and
negates its coefficients.

For an arbitrary diagonal unit A on the head coordinates, conjugate the
entire identity by B=diag(A,I). The adapter becomes B Q B^-1: an elementary
head shear with coefficient c at i,k has coefficient A_i c/A_k, its cross coefficient is X_ik/A_k,
and its tail coefficient is unchanged. The child weights are A_k delta_k.
These are precisely `coefficient` and `child_weights` in the retained source.
No weight enters the pivot itinerary.

For f columns, apply these identities on the disjoint column fibers. Physical
tail index m*f-1-(k*f+j) is (m-1-k)*f+(f-1-j), agreeing with `schedule`.
The rf selected positions form one child; all columns and high-header
values stay in its packet. The low class fixes only whether pivots are units;
their full values, X, and the generated weights use the full ring R.

This supplies BIT.md's good branch. FALLBACK.md supplies its other branch,
and BIT.md proves the uniform physical costs. COMPLEX.md and PROOF.md
give the subsequent callers.
