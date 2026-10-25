# An integral coefficient-path proof of the synthetic transform

## Statement

Let R be any commutative ring with identity, let r=2^ell with ell>=2,
and work in A=R[y]/(y^r+1). Choose a nonempty finite list of axis lengths
t_i=2^a_i, where 1<=a_i<=ell. Set M=product_i t_i. No primality,
field, characteristic-zero, or invertibility assumption is needed yet.

At level h, process exactly the axes with h<a_i. On each such address
bit apply the unnormalized butterfly C=[[1,1],[1,-1]]. Then multiply
the whole polynomial record by y^E, where

    E = -sum_(i:h<a_i) (r/2^h) x_(i,h) k_(i,<h),
    k_(i,<h) = sum_(v<h) 2^v x_(i,v).

The forward procedure uses decreasing h. The opposite procedure uses
increasing h, with the inverse monomial before the butterflies. The
bits in this formula are named axis bits, wherever they occur physically.
Let L be any permutation of address-bit positions, preserving the complete
polynomial suffix. Relocate by L before the forward procedure and undo L
after the opposite procedure. Let U_- and U_+ be these integral operators.

For logical coordinates j and k, define the unnormalized tensor character
matrices W_± by

    W_±[j,k] = y^(±sum_i (2r/t_i) j_i k_i).

Let B reverse the a_i bits within each axis. Then, for all these sizes,

    U_- = L B W_-,       U_+ = W_+ B^-1 L^-1,
    U_+ U_- = M I,       U_- U_+ = M I.                 (1)

If 2 is a unit in R, put F_±=W_±/M and A_±=U_±/M. Equation (1) gives

    A_- = L B F_-,       A_+ = F_+ B^-1 L^-1,
    A_+ A_- = A_- A_+ = I/M.                          (2)

In particular, the normalized opposite is 1/M times the inverse. It is
not an unscaled inverse. The integral identities also hold when 2 is
not invertible, but a normalized operator is then not defined by (2).

The invertibility boundary is sharp: for the nonempty axes specified above,
U_- and U_+ are invertible over A if and only if 2 is a unit in R. More
precisely, their determinants are a signed monomial unit times
`2^(M log2(M)/2)`. This distinguishes a scaled inverse from an actual inverse
over integral or even-characteristic coefficient rings.

The complex specialization independently corroborates the exact algebra
already proved in the retained source. The ring-general statement and the
explicit coefficient path are the extension here. This is an informal
all-size proof. The executable receipt supplies separate finite checks.

## One-axis path calculation

First ignore L and take one axis, with input address k and final address x.
Process h=a-1,...,0. Before its butterfly, bit h still equals the input bit
k_h. The bits below h still equal the original input bits. The upper bits
already equal their chosen output bits. There is exactly one contributing
path from input k to output x: at each butterfly choose its output bit x_h.
Its butterfly coefficient is (-1)^(x_h k_h), and its subsequent twiddle is
y^(-(r/2^h) x_h (k mod 2^h)).

Since y^r=-1, their product is

    y^(-(r/2^h) x_h (k mod 2^(h+1))).                (3)

The sign exponent may be written with a minus sign because y^(2r)=1.
All fractions r/2^h here are integers. Multiplying (3) over h gives the
path exponent

    e(x,k) = -sum_(h=0)^(a-1) (r/2^h) x_h (k mod 2^(h+1)).

Write rev_a(x)=sum_h x_h 2^(a-1-h). The desired Fourier exponent is

    -(2r/2^a) rev_a(x) k = -sum_h (r/2^h) x_h k.

For each h the difference from the path exponent is a multiple of 2r,
because k-(k mod 2^(h+1)) is divisible by 2^(h+1). Thus the path
coefficient is exactly y^(-(2r/t) rev_a(x) k) in A. This proves the
one-axis forward formula without evaluating roots or dividing a geometric
series. It remains valid over rings with zero divisors and in characteristic 2.

## Several axes, layout, and the opposite

A butterfly on axis i commutes with every butterfly on another axis.
Its two paired entries have identical axis-j addresses for j!=i, so it
also commutes with every axis-j twiddle. Axis-i twiddles are diagonal and
commute with the other twiddles. Consequently grouping all participating
butterflies before one combined monomial does not change the operator.
There is again one path for each complete input/output address pair.
Multiply the one-axis coefficients to obtain W_- with the output bits
reversed independently in each axis. This proves U_-=L B W_-.

There is an involution on A which fixes R and sends y to y^-1. It exists
because y is a unit and (y^-1)^r=-1. Transpose a matrix and apply this
involution to its entries. Each C is fixed; each diagonal monomial becomes
its inverse; and L becomes L^-1. Reversing the order of the forward steps
therefore gives precisely the stated opposite procedure. Also W_- becomes
W_+, since its exponent is symmetric in its input/output coordinates.
This proves U_+=W_+ B^-1 L^-1.

Finally C^2=2I over every R. A round with m_h participating axes has
C_h^2=2^m_h I. In U_+U_-, cancel the adjacent inverse/forward monomials,
then replace the adjacent C_h C_h by 2^m_h I. Repeat for all levels.
The layout cancels. Since sum_h m_h=sum_i a_i, the product is M I.
For U_-U_+, cancel L^-1L first and eliminate rounds in the other order;
each diagonal conjugation of 2^m_h I is unchanged. The result is again
M I. No cancellation of the scalar M is used. When 2 is invertible,
division by M gives (2).

For example over Z/2Z, with one length-two axis, C is a nonzero matrix
but C^2=0. This is consistent with (1), where M=2=0, and prevents
claiming an inverse from an integral scaled-inverse identity.

## Sharp invertibility boundary

As a matrix on M polynomial records, each named-bit butterfly is a direct
sum of M/2 copies of C, so its determinant is (-2)^(M/2). There are
sum_i a_i=log2(M) such named-bit butterflies. Every intervening monomial
diagonal and every layout permutation has signed monomial determinant,
which is a unit. Multiplying determinants proves the stated determinant
formula for both directions. If 2 is a unit in R, (1) supplies the inverse
of U_- as U_+/M, and the inverse of U_+ as U_-/M.

For necessity there is also a direct obstruction, independent of determinants.
If 2 is not a unit, R/2R is a nonzero ring. Base-change all operators to
A/2A=(R/2R)[y]/(y^r+1), which is nonzero since the polynomial is monic.
Select any axis participating in the first forward round, and put 1 at
two logical input addresses differing only in that axis's first processed
bit, with zero everywhere else. After L these remain the paired entries
of that named-bit butterfly. In characteristic 2, C sends their equal
values to zero. Other-axis butterflies commute with this one. All later
operations preserve zero. Thus this nonzero vector lies in the kernel
of the reduced U_-. An invertible original matrix would stay invertible
under this quotient, a contradiction. The opposite is the involuted
transpose of the forward matrix, so its invertibility is equivalent.

This is a residue obstruction. For example U_- over Z need not have a
nonzero integral kernel; reduction modulo 2 still rules out a unimodular
inverse. No assertion about an integral kernel follows from this argument.

## The retained exact-K layout

For the concrete retained layout, a_i is ell or ell-1 and 1<=K<ell.
Write ell-1=qK+b, 0<=b<K. Start with axis-major, decreasing-bit order.
Move all existing top bits (i,ell-1), then the bottom levels
(i,h) with h=b-1,...,0, to a prefix. Each move preserves the relative
order of the unselected bits. The remaining bits on every axis are
ell-2,...,b, exactly qK bits. They form q complete K-bit chunks.

The retained whole-chunk exchanges transpose these dq chunks from
axis-major order (i,j) to group-major order (j,i). The resulting slot list is

    [(i,ell-1) for long axes i]
    + [(i,h) for h=b-1,...,0 and all axes i]
    + [(i,ell-2-jK-o) for j=0,...,q-1, all i, o=0,...,K-1].

Every named bit occurs once. Therefore L is a permutation for all these
parameters, including b=0, K=1, and one axis. For a nonprefix level h,
j=floor((ell-2-h)/K) and o=(ell-2-h) mod K identify the same offset o
in one consecutive K-bit chunk per axis. All prefix and suffix fields
remain complete. Reading the lower named bits gives k_(i,<h) regardless
of their physical positions. Thus this concrete layout satisfies the
hypotheses of (1) and (2) for every finite permitted shape and K.

This proves the exact positional admission and algebra only. It does not
prove that a physical callee implements a round, that its borrowed tapes
are restored, or that the claimed movement/runtime charges are paid.

## Relation to retained work and stopping point

The source's `synthetic-characters` and `synthetic-transform-cost` arguments
already establish the complex identities. The earlier
`synthetic-layout-independent` package checks its literal indexed movements
against a separate character oracle over finite domains and explicitly
disclaims an all-size theorem. PR2298 uses the same exact algebra before
its rounding, convolution, and recovery bounds. This proof supplies an
explicit all-size corroboration and integral base-change statement; it
does not identify a defect in those sources or replace their authorship.

All coefficients may be arbitrary correlated elements of A. No disk or
independence hypothesis is needed for the exact identities. Applying Q_p
between rounds changes the operator and is outside (1). Characteristic 2
does not admit (2). No production T74 native/ordinary/hosting refinement,
full outer tape execution, analytic bound, supplier, or improved kappa is
established. Independent human and formal proof-kernel review are unclaimed.
