# Conditional paid-return, approximation and invoice audit

**Verdict: no gap found in the implication in PR5526 REPAIR.md Sections 2–4,
under the stated invariant-history, unitary-coset and one-field pricing
premises.** This is an independent AI-assisted derivation and exact finite
corroboration. It does not independently establish the actual caller's
observation inventory or grade claims, prove the Clifford Gram theorem anew,
or constitute proof-kernel/human acceptance.

Audited source: Ali Romman's PR5526 at
`45f7de73b168721cdf7ec8c1769b1b594493716a`, retained on canonical main
`5e0052ca0aa3036a3afa8b0438927377c8d97d53`. SOURCES.json binds the exact
documents, declarations and receipts consumed here. DLamdata's PR5547 audits
the earlier core Gram theorem, explicitly excluding this later bridge.

## 1. Fix one width and make the premises explicit

Let V be a complex Hilbert space of dimension d. In the source,
d = 2^(17f). Let H be a finite projective unitary group of h elements,
represented on V, and let A be the linear span of its chosen unitary lifts.
Products may acquire scalar phases: A remains a unital algebra. Assume
dim A = h. Work in the finite-dimensional space of operator rows
Hom(V^b,V), with inner product tr(R* S)/d.

The initial history module M is A-invariant. Each required row t_j has
one unitary target T_j in its own input position j, with zeros elsewhere.
Let F be the frame with bh columns U_g t_j, for g in H and j in 1..b.
The consumed physical-alphabet premise is

    ||F c - m||^2 >= lambda ||c||^2   for all c and m in M, lambda > 0. (A)

In PR5526, (A) follows from the lower Gram bound on the complete projective
Clifford alphabet and disjoint initial/target coefficient supports, separately
in every independent input column. It is NOT an orthogonality assertion.
The initial support is allowed to have relations among its own coefficients;
choose a representation in that support and apply the full Gram inequality.
The target coefficients are still c because the supports are disjoint.

The source-specific b=104, allowed initial grades {0,1,7}, target grade 9,
left-grade invariance, complete original observations and same-capacity
premises remain inherited. The verifier checks their retained declarations
and source bytes. It does not replay the 5,408 native grade calculations or
establish that no additional machine observation exists.

## 2. Arbitrary paid feedback does not bypass the quotient dimension

Represent each new return b_i by its actual linear map on the original
independent inputs after composing its dependencies on earlier returns.
That map can be arbitrary; it need not lie in the Clifford span, be unitary,
or commute with A. For each completed prefix, available rows are in

    M + A b_1 + ... + A b_q.

This follows by induction: ordinary steps are A-actions and scalar linear
combinations; adding a paid row adds its cyclic module. Keep a conceptual
history when a physical row is overwritten or cleared. Each map
A -> A b_i, a -> a b_i, is linear and surjective, so its image has dimension
at most h. Zero divisors can reduce that dimension and do not invalidate
the upper bound. Dependence of b_i on earlier returns does not increase it.

Let Q be orthogonal projection onto M-perp. Taking the infimum in (A)
gives (QF)*QF >= lambda I_(bh). Thus QF has rank bh. If all targets are
returned, A-invariance implies that all their orbit columns are available.
Their projection must fit in N = Q(sum_i A b_i), whose dimension is at most
qh. Consequently bh <= qh and q >= b. No freeness or division-ring
assumption is used. Changing a frozen original paid input would change M
and lies outside this inference.

## 3. The normalization and orbit factor in the error bound

For arbitrary approximate returned rows y_j in the available module, set
e_j=t_j-y_j. Every U_g y_j is available. If P projects onto N, then

    sum_(g,j) ||U_g e_j||^2 >= ||(I-P) QF||_HS^2
                                  >= lambda (b-q)_+ h.

For the last inequality, rank(P QF) <= qh, so its kernel has dimension
at least (b-q)h. On an orthonormal basis of this kernel, QF has squared
norm at least lambda per vector. Complete the basis and sum nonnegative
terms. This proves the rank-approximation inequality directly.

Unitary left action makes the left side h sum_j ||e_j||^2. Divide by h
ONCE. If E stacks the b error rows, the chosen row norm gives

    d^(-1) ||E||_HS^2 >= lambda (b-q)_+.

Since E maps V^b to V^b, rank(E) <= bd and
||E||_HS^2 <= bd ||E||_op^2. Hence

    ||E||_op^2 >= lambda (1-q/b)_+.

Restriction to these inputs and selection of these outputs are contractions,
so the complete endpoint has at least this operator norm error. This is one
worst-case vector in a direct sum, not b simultaneous per-field maximizers.
The proof permits q and the linear program to depend on the fixed width.
It excludes nonlinear rounding/branching and free actions outside A.

## 4. Independent exact fixtures, including nonorthogonal supports

The new checker uses standard-library rational dense matrices, not the
source's Clifford/group-code implementation. Its main fixture has V=R^3,
H generated by the cyclic coordinate shift S, and T=diag(1,1,-1).
The six coefficient matrices I,S,S^2,T,ST,S^2T have normalized Gram matrix

    [ I_3       I_3/3 ]
    [ I_3/3     I_3   ].

Thus its lower eigenvalue is 2/3. Removing the initial H-support gives
relative Gram matrix (8/9) I_3. With b separate inputs, these matrices
repeat block-diagonally. This example deliberately tests a nonzero overlap:
declaring independent supports orthogonal would give the false constant 1.
The sharper relative constant 8/9 is a fixture calculation, not a claimed
improvement to the 17-axis caller.

The checker examines 175 prefixes with b=2 or 3, including 120 arbitrary
rational returns outside the initial-plus-target coefficient span. New
returns include a nonordinary shear of the preceding return. Exact
Gram-Schmidt projection computes the minimum total normalized squared error
over the entire available module. Each prefix satisfies both the quotient
dimension bound and the orbit/error identity. Direct target-return controls
attain (8/9)(b-q); these are enlarged-oracle fixtures, not native suppliers.

A second, orthogonal fixture uses H={I,Z}, T=X and two two-dimensional
inputs. It exhausts all 81 ternary assignments of the four off-diagonal paid
row entries. The exact one-return error distribution is 64 cases at 1,
16 at 3/2, and one at 2. Diagonal entries already lie in the initial module.
Neither finite domain is claimed to enumerate arbitrary paid programs.

Seven semantic controls expose normalization twice, a missing orbit division,
false orthogonality, cached targets, singular targets, discarded retained
history and a noninvariant initial history. In particular, with diagonal
ordinary algebra, one return [P0,P1] supplies the two singular rows [P0,0]
and [0,P1]. This verifies why counting target rows without full cyclic-module
dimension would be invalid. Four in-memory code defects must separately fail
their intended diagnostics, including a dropped rank-one charge and a changed
target credit. All checks use explicit exceptions and also run under -O.

## 5. From source-declared invoice to a loss at every power tariff

The checker parses only the literal P and Tar dictionaries in Dugongue's
retained mixed-thin checker; it does not execute it. Adding 104 rank-one jobs
matches REPAIR-INVOICE.json exactly. Original target credits stay fixed.
For d_r = P_r + 104 [r=1] - Tar_r, it computes ALL integer hinges
K(k)=sum_r d_r min(r,k), k=1..17:

    5996, 7134, 7448, 6742, 5838, 4854, 3870, 2900, 1800,
    1576, 1352, 1128, 904, 680, 456, 232, 8.

For an increasing concave phi with phi(0)=0, let
s_k=phi(k)-phi(k-1). The exact identity

    phi(r) = s_17 min(r,17) + sum_(k=1..16) (s_k-s_(k+1)) min(r,k)

follows by telescoping slopes. Nonnegative coefficients prove the invoice
loss. For phi(r)=r^p, 0<p<=1, s_17>0 and K(17)=8 make it strict.
With 96 returns K(17)=0 and the earlier hinges are positive, so positive
margin is still impossible; q<=95 is necessary. It is not a claim that
every q<=95 is profitable. At q=95 and p=1 the margin is exactly 1, showing
the rank-mass cutoff itself cannot be reduced by this argument.

The reference saving is the SOURCE-BOUND rational
605457647/200000000000, not a lookup of a future selected record. For
p=1-saving, an independent rational series enclosure gives the margin

    [18018715749583/500000000000, 2252339468941/62500000000]
      = [36.037431499166, 36.037431503056].

It contains the predecessor's finer interval and proves 36 < margin < 37.
Therefore positive margin permits at most 36 added positive-rank returns;
the inherited width-84 lambda=125/126 gives squared operator error at least
2125/3276. The same arithmetic checks the width-72 and q=95/103 bounds.

The enclosure is independent of the existing interval engine. For each
integer rank r<=17, put z=(r-1)/(r+1). Sum 96 terms of
log r = 2 sum_(k>=0) z^(2k+1)/(2k+1). The omitted positive tail is at most
2 z^193 / (193 (1-z^2)). Monotonicity of exp(-x), its alternating
degree-9 lower and degree-8 upper sums for 0<=x<1, and outward rounding on
a 10^-12 grid bound r exp(-saving log r). Sum interval endpoints with the
appropriate signs of the paid/target coefficients. No floating point enters
the acceptance arithmetic. More endpoint digits are not this contribution;
the check independently closes the error-to-budget implication.

## 6. What remains outside this audit

The proof bridge is conditional on the source's complete initial history,
grade invariance and target/capacity model. Literal source-word and all-width
native correctness remain separate, as do the core Clifford Gram theorem,
one-return-per-positive-rank-job pricing contract, precision/storage, new
multi-output suppliers, and the complete multiplication theorem. The
histograms are optimistic source declarations, not a fresh physical recount.
The checker consumes receipts as declarations and does not call them a replay.

Credit: Ali Romman's PR5526 supplies the reviewed theorem and application;
Chris R / Clear1nsight's PR5425/5446 and Ali Romman's PR5449 supply the history
dimension method; Dugongue/PR4948 and Chris R/PR4978 supply the frozen caller
and its prior audit; DLamdata/PR5547 identifies this unaudited bridge. The
existing invoice-comparator lineage, including mightyOil, and zxv's interval
arithmetic retain credit. Projection, dimension, concave-order telescoping,
and log/exponential series are classical methods. No new general lower-bound
theorem or literature-priority claim is made. Prepared for
josecarlosgonzalezroque-design with substantial OpenAI Codex assistance;
Apache-2.0. No subagents or independent human reviewers were used.
