# Exact LU growth after the actual old-H Schur truncation

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This independently binds a classical elimination argument to the exact producer
used by PR3851 and the factor-cap premise retained in PR5319. It is a scoped
written proof and source execution, not human or formal-kernel acceptance.

## Statement and the premise that changes

Use the induced absolute row-sum norm. Let p>=1 be an integer and H a finite
real matrix with positive diagonal satisfying, in every row,

    H_ii - sum_(j!=i)|H_ij| >= delta=1/(8p),   ||H||_infinity<2.     (1)

Take an admitted principal window H_W, partitioned into interior I and nonempty
boundary B. The boundary keeps its stated order; empty I is allowed. Define

    S=H_BB-H_BI H_II^-1 H_IB,
    A=tau_P(S),             eta=2^-P<=1/(16p),                    (2)

where tau_P truncates each real entry toward zero to the eta grid. Assume S,
in that boundary order, has scalar half-bandwidth b<=2p. Then the exact
no-pivot Doolittle factorization A=LU exists, every pivot is positive, both
triangular factors retain that bandwidth, and

    ||U||<2,          ||L||<=65p²,
    ||L^-1||<=32p,    ||U^-1||<=1040p³.                          (3)

In fact the same argument gives the stronger caps ||L||<=32p and
||U^-1||<=512p², without needing bandwidth for these norm estimates.
No new page precision is installed. The constants do not depend on the
number of boundary rows, cells or RHSs.
All pivots exceed 1/(16p). In particular the actual p>=101, P=32768p domain
of `schur-boundary-residual` satisfies the precision condition.

This derives its exact-factor growth and positive-pivot requirements rather
than assuming them for LU of an unrelated reference. The global old-H
coefficient construction and (1), exact reference correspondence and the
natural boundary bandwidth remain explicit premises. We do not derive them
from a finite fixture. No online scalar/block solve, changed precision policy,
new runtime bound or selected-frontier change is asserted.

The exact input bounds (1) are the retained old-H bounds in
`physical-gaussian-core/PROOF.md` lines 65–76; PR5319 explicitly retains
the original-H gap and the rounded-factor caps in
`schur-boundary-residual/PROOF.md` lines 25–58. In using the new implication
with PR5319, retain the original producer’s `||H||<2` hypothesis as well.
It is not a consequence of the gap alone.

## One elimination step preserves gap and never increases row mass

Let a real current matrix C have positive diagonal and gap at least d>0.
Eliminate one principal coordinate k with pivot c=C_kk>0. For remaining i,j,

    C'_ij=C_ij-C_ik C_kj/c.

For a remaining row i, put r_k=sum_(j!=k)|C_kj| and g_i=C_ii-sum_(j!=i)|C_ij|.
Triangle inequalities give

    C'_ii-sum_(j!=i,k)|C'_ij|
      >= g_i+|C_ik|(1-r_k/c) >= g_i >= d.                (4)

In particular C'_ii>0; this conclusion is obtained before using a positive
diagonal in its absolute row sum. Now the other triangle inequality gives

    sum_(j!=k)|C'_ij|
      <= C_ii+sum_(j!=i,k)|C_ij|+|C_ik|r_k/c
      = sum_j|C_ij|-|C_ik|(1-r_k/c)
      <= sum_j|C_ij|.                                  (5)

Neither nonnegative off-diagonal entries nor symmetric/positive-definite
matrices are assumed. No norm of a column is substituted for a row norm.
Every principal restriction initially removes off-diagonal terms only and
retains (1). Reorder the coordinates to eliminate I first; permutations do
not change row gaps or row masses. Induction proves positive pivots and
(4)-(5) through that elimination. Its remaining matrix is exactly the Schur
complement S, by elementary block elimination. Hence

    S_ii-sum_(j!=i)|S_ij|>=delta,  ||S||<2.              (6)

The argument covers arbitrary finite I, not merely one cell or a contiguous
interior. The assumed half-bandwidth is a separate property of the caller's
particular carve, not a consequence claimed for every Schur complement.

## The actual first rounding loses at most one entry's gap

Toward-zero truncation satisfies |tau_P(x)|<=|x| and |tau_P(x)-x|<eta;
zero remains zero. From S_ii>=delta>eta, its truncated diagonal is positive.
Therefore in each row

    A_ii-sum_(j!=i)|A_ij|
      > S_ii-eta-sum_(j!=i)|S_ij|
      >=delta-eta>=1/(16p),        ||A||<=||S||<2.       (7)

The loss is at most eta, not a dimension times eta estimate: truncating the
off-diagonal magnitudes can only improve the gap. This uses the ACTUAL
rounding rule. Nearest rounding could increase off-diagonal magnitudes and
does not inherit this one-entry estimate. No statement about a different
coefficient quantizer is being silently used.

Since truncation preserves zeros, A has the same bandwidth bound. Applying
(4)-(5) to its natural elimination order gives positive pivots and current
Schur row sums <2 throughout. Each row of U is a pivot row of one such
current Schur matrix, with zeros placed before its diagonal. Thus ||U||<2.
Each strict lower multiplier obeys

    |L_ik|=|C_ik|/C_kk <2/(1/(16p))=32p.                (8)

Natural elimination preserves lower and upper half-bandwidth b. Indeed, for
a fill update with i,j>k, if i-j>b then i-k>b and C_ik=0; if j-i>b then
j-k>b and C_kj=0. The same induction applies at every stage. Therefore a row
of L has at most b<=2p strict lower entries. Its diagonal is exactly one, so

    ||L|| <1+64p²<=65p².                               (9)

For any complex vector x, choose i with |x_i|=||x||_infinity. The positive
diagonal and reverse triangle inequality yield ||Ax||>=gap(A)||x||.
It follows that A is invertible and ||A^-1||<=16p. From A=LU,

    L^-1=U A^-1,       U^-1=A^-1 L.

Equations (7)-(9) now give the remaining two bounds in (3). In particular,
no independently assumed factor-inverse cap or a product of rowwise
amplification factors is used. The proof is valid for complex RHSs although
the exact source matrices and their factorization are real.

A useful sharper form follows directly from the row-mass loss, without
counting nonzeros. For a fixed row i, elimination of k<i loses at least
`|L_ik| gap(C_k)` of its remaining row mass, by (5). Put d=gap(A), M=||A||.
Every pivot-row gap is at least d. At the end the remaining row is U_i and
has mass at least its positive pivot, hence at least d. Telescoping gives

    d sum_(k<i)|L_ik| + ||U_i||_1 <= ||A_i||_1 <= M,
    1+sum_(k<i)|L_ik| <= M/d.

Thus ||L||<=M/d<=32p and ||U^-1||<=M/d²<=512p². The bandwidth hypothesis
still binds the caller's page format; it is not needed for these stronger
norm caps. These sharpen the retained sufficient constants but do not
silently change an online arithmetic allocation or claim a runtime saving.

For the production precision, p<=2^p for p>=1 and hence
16p<=2^(p+4)<=2^(32768p); this proves eta<=1/(16p) on the entire domain.
The finite source fixture uses p16/P24, not production P=32768p. It tests
producer correspondence and satisfies the weaker generic precision inequality;
it is not presented as a production coefficient/locality certificate.

## Actual encoded producer correspondence

The pinned `Window.prepare_schur` in `physical-gaussian-core/gaussian_window.py`
forms the original old-H Schur matrix, constructs `rounded_schur` by
`Rational(value.rounded(axis.P), Count(axis.unit))`, checks that the exact S
has no nonlocal band fill, then calls `lu(rounded_schur)`. The pinned
`Rational.rounded` uses the signed magnitude quotient, so it truncates toward
zero; a negative off-grid control distinguishes floor from this operation.
The reference is therefore A=tau_P(S), rather than S, tau_P(L)tau_P(U), an
inverse of rounded factors, or the separate local q-model.

`gaussian_matrix.lu` is exact Doolittle with unit lower diagonal:

    U_ij=A_ij-sum_(k<i)L_ik U_kj,                j>=i;
    L_ji=(A_ji-sum_(k<i)L_jk U_ki)/U_ii,        j>i.

All coordinates and loops use encoded Counts; Rational arithmetic reduces
after its exact operations. The source checks positivity of each U_ii before
division. By induction on i, the displayed formulas produce the same current
Schur row and multipliers used in (4)-(8). Thus the new theorem discharges
that positivity check and the exact factor caps whenever its stated input
premises hold. This is a source-relative mathematical implication: primitive
arithmetic, ownership and complete record semantics remain inherited.

The physical adapter executes the unchanged Axis and Window constructors for
the retained s13,t14,u=w1,p16,P24 period-crossing case. It observes the original
old-H matrix, principal window, exact S, rounded S and actual factors, and all
writes inside the actual LU call. Observer callbacks copy raw tape bytes only;
they return control to the original operations and supply no payload values or
arithmetic oracle. `no_decode` remains active during setup. Decoding and all
Fraction comparisons occur afterward. A separate rational elimination builds
S and its stage sequence. Every observed factor write is compared to that
sequence, rather than treating endpoint equality alone as evidence of the
actual producer's pivot order.

The fixture's old-H gap and row mass, principal/Schur equality, truncation,
pivots, band zeros, factors, row-mass/gap at all elimination stages and inverse
identities are checked exactly. They corroborate the source binding, not the
universal proof or global production coefficient assumptions. Borrowed source
behavior and the source pool's full cleanup remain checked. The retained
boundary solver is not executed: this task ends at exact setup factors.

## Charges and limits

Nothing changes in physical setup. The producer still computes the exact
old-H kernel inverse, Schur entries, first rounded matrix, exact reduced
rational LU, then separately rounded page factors and reciprocal pivots.
Its full serialized Matrix reads/writes, rational reductions, allocation and
cleanup remain paid. The source's polynomial setup bit-complexity invoice is
retained, not newly proved or charged zero. Observer histories and independent
rational matrices are verification memory, not online algorithm storage.

The implication removes the factor-growth/positive-pivot premises from the
named original-reference residual consumer, conditional on (1)-(2) and the
explicit source contracts. It does not establish the global old-H gap,
coefficient interval accuracy, carve locality, actual RHS size, stored-page
perturbation, online scalar or inverse-block errors, Core normalization,
fast Strassen implementation, physical tensor/CRT or multiplication theorem.
The separately coordinated two-active-column kernel is not part of this work.

## Open next questions

Independently bind the global old-H gap/norm and exact carve bandwidth to the
production coefficient generator; start with its directed weight/kernel
interval receipts and period-cut geometry. Those hypotheses now identify the
remaining analytic boundary without assuming four extra factor caps.
A future page/consumer change must retain tau_P(S) as its exact reference and
pay both its own page perturbation and the original-S comparison.

Credit Jose Manuel/jmbarrancoml PR3851 for the actual physical producer and
published caps; Hiroki KUMAZAKI/kumagi PR5319 for the explicit residual consumer
and released factor-cap question; James Reed for the separate factor-margin
arithmetic; Chafik Boukhalfa, RaD/hipotures, the physical-word and Gaussian
lineage, and classical diagonal-dominant elimination. Frozen sources and
source-specific notices remain unchanged.
