# Exact query count over ordinary involution sectors

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Model and result

Let J_0,...,J_(s-1) be commuting ordinary involutions, with s >= 1.
Let Q commute with them and satisfy Q squared = J_0. Write J_mask for
the product selected by the binary mask. A scalar coefficient acts on role
indices and is applied once, not once per address column.

Consider the prescribed linear map from n input fields to m output fields

    F = A(J) + B(J) Q,
    A(J) = sum_mask A_mask J_mask,
    B(J) = sum_mask B_mask J_mask.

A program can use arbitrary scalar combinations of the J_mask, zero owned
storage, COPY, CLEAR, and Q or Q inverse on one whole field per paid query.
Queries can be interleaved with ordinary operations, and later queries can
use earlier results. The program is a fixed linear program. It does not
branch on runtime data. Other address maps and higher-rank Gaussian queries
are not in this lower-bound alphabet.

For a sign vector sigma, let

    E_sigma = product_j (I + sigma_j J_j)/2,
    B_sigma = sum_mask product_(j in mask) sigma_j B_mask.

Assume each sector is nonzero and Q is not a scalar on that sector. Equivalently,
I and Q are linearly independent there. Then the exact minimum paid count is

    q_min = max_sigma rank(B_sigma).

The same upper bound holds without the independence assumption. In that case
it need not be minimal. The compiler uses the full formal Boolean algebra,
so it does not silently discard a sector that is empty in a particular model.

This generalizes the sufficient two-sector construction in PR5578 T6. The
new results are the matching lower bound for interleaved queries, the exact
dyadic emitter, the extension to any finite Boolean family, and the sharp
role-gauge consequence in Section 5. No complete caller or kappa is supplied.

## 2. Lower bound with arbitrary feedback and storage

Fix one sector. Every ordinary operation is now scalar on address space.
Represent each live wire, as a function of the original independent inputs,
by an even coefficient row plus an odd coefficient row times Q. The relation
Q squared = sigma_0 keeps this form after every query. The representation is
unique because I and Q are independent on the sector.

At entry every odd row is zero. Ordinary scalar operations, copies and clears
cannot increase the dimension of the span of all available odd rows. A query
on a wire with coefficients (a,b) changes them to (sigma_0 b,a). Thus it adds
at most one new row a to the total odd-row span. Keeping the old wire or extra
copies does not increase this limit. A Q inverse query differs by the ordinary
scalar sigma_0 and has the same bound.

After q queries, every odd output row lies in a space of dimension at most q.
The required odd output matrix is B_sigma. Hence q >= rank(B_sigma) for every
sector. This proves the lower bound without a one-layer, no-reuse or no-feedback
assumption. Arbitrary initial owned dirt cannot improve it: set that independent
dirt to zero and obtain the same required map on the main inputs.

## 3. Attainment with exact dyadic coefficients

Take rank factorizations B_sigma = U_sigma V_sigma. Pad their inner dimensions
to q = max rank(B_sigma), and put

    U = sum_sigma U_sigma E_sigma,
    V = sum_sigma V_sigma E_sigma.

Complementary sectors satisfy E_sigma E_tau = 0 for sigma != tau and their
sum is I. Consequently UV=B(J). Since every factor commutes with Q, the word

    gather z = Vx; query Q on each of the q z fields;
    output y = A(J)x + UQz; clear z

has endpoint F on every input. The symbol Qz in the scatter means the queried
version of z; the word contains exactly q queries in total. All inputs remain
unchanged during the gather and scatter. Output and work buffers are cleared
before their first read, so their arbitrary initial dirt has no effect.

Dyadic B_sigma admit rank factorizations over the dyadic ring Z[1/2]. To obtain
one, multiply by a common power-of-two denominator d and use integer Smith
form U0(d B_sigma)V0=S. Both U0 and V0 are unimodular, so their inverses have
integer entries. The first r columns of U0 inverse, multiplied by the nonzero
diagonal entries of S/d, and the first r rows of V0 inverse give the required
factorization. There is no division by a nonunit odd pivot.

The inverse Walsh transform divides only by 2^s. Thus every emitted gather,
scatter and direct coefficient is dyadic. The retained PR5615 Smith utility
supplies the factorization step. Each use is checked by exact multiplication
and by the integrality of both inverse basis matrices. The replay computes
the rank again by a separate rational elimination with opposite pivot order.

The compiler emits only CLEAR, shifted scalar ADD and QUERY. It uses m+q
owned fields, including the m output fields. It emits m+2q CLEARs, and at most
2^s(mn+qn+mq) shifted ADDs. Zero coefficients are omitted. A shifted ADD reads
J_mask applied to its source. That address action, coefficient implementation,
movement and field pass all have real nonrecursive costs. The emitted counts
and coefficient bit sizes are component data, not a machine compiler bill.

## 4. Actual lifted Gaussians and a larger sharp example

For the usual lifted central Gaussian Q_f, its square is the ordinary
translation that flips that axis in every digit column. Take this as J_0.
Additional independent spectator-axis translations supply J_1,...,J_(s-1).
They commute with Q_f and with one another. In the Fourier basis the possible
central eigenvalues are i^k for 0 <= k <= f. For f >= 3, both square roots of
each sign occur. Independent spectator signs leave each Boolean sector
nonempty. The hypotheses of Section 1 therefore hold for every f >= 3.
The construction remains valid for f=1,2, but the minimum claim is not made
there because one or more sectors can make Q scalar.

For each of the 2^s sectors give one independent field x_sigma the map

    x_sigma -> x_sigma + (1/2) Q E_sigma x_sigma.

Every B_sigma has rank one. Separate sector queries use 2^s requests; the
compiler uses exactly one. The map is invertible: each diagonal perturbation
has norm at most 1/2, so its inverse norm is at most 2. These outputs are not
canonical Gaussian targets and earn no such credit. The compiler emits the
forward map only; a dyadic exact inverse is not assumed.

The verified examples include 2,4,8,16 and 32 sectors. The 32-sector example
uses one query, 2080 shifted ADDs, 34 CLEARs and 33 owned fields including
outputs. This exposes the ordinary-work tradeoff rather than treating sector
selection as free. The two-sector case is exactly the credited PR5578 T7 map.
Its literal tensor Gaussian matrices are checked at widths 1 through 4.

## 5. Scalar role-gauge boundaries already attain the minimum

Let P and R be scalar role projectors and M an invertible scalar matrix.
The boundary G_R(Q) M G_P(Q) inverse, where G_P(Q)=I+(Q-I)P, has

    A = (I-R) M (I-P) + R M P,
    B(J_0) = R M (I-P) + J_0 (I-R) M P.

Choose bases that split each projector's image and kernel. The two summands
of B_sigma occupy disjoint input and output blocks, for either sign of J_0.
Their total rank is

    rank(R M - M P).

This is the tariff already supplied as an upper bound by PR5578 T3. Sections
1-3 prove that it is exact in the present query alphabet, even with interleaved
queries, extra ordinary spectator sectors and feedback. Thus this form of
sector packing cannot lower an already factored scalar role-gauge boundary.
A lower complete cost must change the boundary defect or the permitted maps.
The statement does not cover noncommuting address-valued role matrices.

## 6. Evidence and limits

The exact replay covers every ordered pair of 2 by 2 sector matrices with
entries -1,0,1, plus rectangular dyadic cases, noncoordinate role projectors,
and interleaved feedback words. It compares complete polynomial actions on
all original inputs and arbitrary initial owned values. A separate literal
tensor-matrix check covers the source two-field example. Corrupt query, sector
mask and cleanup words reject, as does a nondyadic input.

The lower bound is a written proof for the stated algebra. Finite checks are
corroboration, not a formal kernel or independent human review. No actual
selected-caller section has been replaced. Native addresses outside the
specified involution algebra, higher-rank queries, precision, tape movement,
compiler reserves and the full supplier/outer join remain separate obligations.

## 7. Attribution

Dugongue PR5578 T6/T7 supplies two-sector packing and the two-field example;
T3 supplies the role-gauge upper bound. PR5586 C8 names the completed-caller
target. Retain Cao Yifan, DaysSky, Cinna Davis, Nick Petalas, Ryanson Jonathan,
zxv, Jacob Alan Sussman and all source authors named in the pinned notes.
Ali Romman PR5615 supplies the unchanged Smith routine, following the classical
Smith method and the earlier dyadic Euclidean work of Nick Petalas. Boolean
Fourier decomposition and rank factorization are standard methods. The input
files retain their original credit and AI disclosures.
