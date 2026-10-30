# Two FULL shears on arbitrary owners retain a low-grade image

This is a scoped algebraic proof, produced by Nick Petalas. It answers the
scratch-reading follow-up in unpaidmoon's [PR #5843](https://github.com/CrocSwap/integer-mult-bounds/pull/5843).
The changed hypothesis is the location of each elementary shear. Either
source or destination may now be any owner, including an identity scratch
owner. No physical realization of that larger macro is assumed.

## Statement

Let A be a unital algebra over a field K and B a unital subalgebra with
finite positive dimension d over K. Let F_r be increasing K-linear
subspaces of A with B contained in F_0, B F_r B contained in F_r, and
F_r F_s contained in F_(r+s). Fix nonnegative s,t and a K-linear
B-bimodule projection pi on A which fixes every element of F_(s+t).

There are n >= 2 owners. Allow arbitrary L,W,R in GL_n(B). Let

    D1 = diag(a_0,...,a_(n-1)),  a_i in F_s and a_i a unit of A,
    D2 = diag(b_0,...,b_(n-1)),  b_i in F_t and b_i a unit of A.

Choose any distinct p_1,q_1 and any distinct p_2,q_2 from the n owners.
The two elementary shears and FULL factors are

    E1 = I + e_(p_1) c_1 e_(q_1)^T,   T1 = D1 E1,
    E2 = I + e_(p_2) c_2 e_(q_2)^T,   T2 = D2 E2,

where c_1,c_2 are arbitrary elements of A. They need not be central, pure
words, or invertible. Neither coefficient has a grade bound. Matrix
products act on columns from right to left.

Apply pi entrywise, and regard pi(L T2 W T1 R) as a K-linear map from
B^n to A^n by left multiplication. Then

    rank_K pi(L T2 W T1 R) >= (n-1)d.                 (1)

In particular, if pi(g_0)=pi(g_1)=0, this word cannot equal

    J = diag(g_0,g_1,I,...,I),

because rank_K pi(J)=(n-2)d. The statement requires arbitrary initial
scratch inputs and their identity endpoint. It grants reads and writes
of those inputs inside either shear.

## Proof

Set S = {x in B^n : x_(q_1)=0}. It has dimension (n-1)d. On this exact
subspace E1 x=x, regardless of whether q_1 is main or scratch. Therefore
u=W D1 x has every coordinate in F_s. Also x -> u is injective, since
D1 is invertible over A and W is invertible over B and hence over A.

Suppose pi(D2 E2 u)=0. Row q_2 is untouched by E2 since p_2 != q_2.
Its output is b_(q_2) u_(q_2), which lies in F_(s+t). The projection fixes
this element, so its vanishing forces u_(q_2)=0 because b_(q_2) is a unit.
This kills the entire c_2 u_(q_2) term. Every remaining output is now
b_i u_i, again in F_(s+t). Projected vanishing forces all u_i=0. Thus
pi(T2 W T1) is injective on S and has rank at least (n-1)d.

Finally the bimodule property gives

    pi(L T2 W T1 R) = L pi(T2 W T1) R.

Right multiplication by R is an automorphism of the domain B^n. Left
multiplication by L is an automorphism of the codomain A^n. Both preserve
the K-rank. This proves (1). Since pi fixes B, the displayed target has
exactly the scratch image B^(n-2), proving its exclusion.

No commutation, positivity, domain property, or inverse grade bound is
used. In particular B may have zero divisors. The free subspace is chosen
using the actual first read coordinate, which removes any need for the
main-only endpoint restriction on the two shears.

## Sharpness and hypothesis controls

When a unit g satisfies pi(g)=pi(g^-1)=0, take D1=D2=I and W=I. On any
two owners choose E1=I+e_1 g e_0^T and E2=I-e_0 g^-1 e_1^T. The exact
two-owner product is

    E2 E1 = [[0,-g^-1],[g,1]].

Its projection has rank d on those owners and identity on the others.
Thus the uniform lower bound (n-1)d is attained. The labels 0,1 in this
example can be replaced by any distinct owner indices, including scratch.
This equality example is elementary algebra and is not a native construction.

The unit condition, the cutoff s+t, and W in GL_n(B) are essential to this
argument. Setting D1=0 destroys the bound. Two grade-one factors on
different coordinates can have grade two, so cutoff one cannot retain
them. A high-grade diagonal W outside Mat_n(B) can make the entire
projected map vanish. Three queries can attain diag(g,g^-1), after a
scalar signed swap, through the usual three-shear identity. These are
explicit controls of the theorem's hypotheses, not new optimization claims.

## Application to the cited FULL boundary

Chris R / Clear1nsight's [PR #4920](https://github.com/CrocSwap/integer-mult-bounds/pull/4920)
supplies the full-monomial Clifford grade model and its tensor-separation
lemma. unpaidmoon's #5843 supplies the main-only two-shear rank argument
with identity scratch and explicitly asks about a scratch-reading shear.
The contribution here removes that restriction by choosing S using q_1.
No predecessor numerical result is replayed or recertified.

For that model, take B to be the full monomial subgroup algebra and F_r
the span of words of Fourier grade at most r. These spaces have the
required bimodule and product properties. Use s=t=8 and pi=pi_(<=16).
The actual diagonal transverse factors have grade eight on main owners
and identity on scratch, so they satisfy the hypotheses even when the
new shear touches scratch. Two pure grade-17 main targets with restored
identity scratch remain impossible in this enlarged algebraic class.

The cited separation lemma transfers the obstruction to every sufficiently
large tensor width in the fixed finite columnwise alphabet. This use is
conditional on the predecessor's stated grade and separation premises.
It supplies no new width bound, literal native implementation, or claim
about accidental relations at small widths.

thu-nmrc's [PR #5200](https://github.com/CrocSwap/integer-mult-bounds/pull/5200)
is a different extension. It covers joint native main banks and identity
scratch, with possibly dense query blocks confined to the main owners.
The present result permits scratch in either single-coordinate query;
it does not extend #5200's multiple-query block theorem to scratch blocks.
Credit its joint-bank result and the retained Cinna Davis, Cao Yifan,
zxv, Jacob Alan Sussman, Ali Romman, Dugongue and native/compiler lineage.

## Evidence limits

The executable is a fresh finite group-algebra example, not a Clifford
operator replay. Its complete declared owner-pair enumeration corroborates
the new coordinate freedom. The written argument proves the arbitrary
field and owner-count statement. Neither is proof-kernel verification.
Productive transformed helpers, clean COPY/CLEAR, noninvertible controls,
new query blocks, changed transverse grades and noncolumnwise operations
require their own analysis. No invoice, supplier admission, new kappa, or
complete multiplication theorem is claimed.
