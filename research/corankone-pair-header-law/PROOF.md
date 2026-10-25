# Two overlapping corank-one requests

## Contract and claim type

This is a scoped counting proof. Let K be a finite field of order q, m >= 2,
and let U,V be rank-one idempotents on K^m with UV = VU = 0. Put
P = I-U and Q = I-V. A header G in GL_m(K) passes a request R when every
leading principal minor of GRG^-1 of orders 1 through rank(R) is nonzero.
We count headers passing both P and Q, with each complete header weighted
equally. No restriction on the permitted header subset is implicit.

P and Q commute. Their image intersection has dimension m-2, so for m > 2
this is outside the orthogonal-request hypothesis of #4246. The theorem
also differs from a nested rank-one/rank-r pair. At m=2, P and Q themselves
are orthogonal rank-one requests, giving an overlap with #4239.

## The general transfer law

For a 2 by 2 matrix A over K, define

```text
w(A) = 2q^2-1  if A = 0,
       q-1      if rank(A) = 1,
       0        if rank(A) = 2.

S = {A : A_11 != 1 and A_22 != 1}.
f_0(A) = 1 if A = 0, otherwise 0.
f_(j+1)(B) = sum_(A in S) f_j(A) w(B-A),  B in S.
C(q,m) = sum_(A in S) f_(m-1)(A) w(I_2-A).
D(q,m) = (q^m-1)(q^m-q) q^(2m-4).
```

**Theorem 1.** The joint passing fraction is C(q,m)/D(q,m). The recurrence
has exactly q^2(q-1)^2 states and applies to every finite field, including
nonprime fields. The number of passing headers is C(q,m)|GL_(m-2)(K)|,
with |GL_0(K)| = 1.

**Proof.** Orthogonality gives a direct decomposition
K^m = im(U) + im(V) + (ker(U) intersect ker(V)). Choose nonzero vectors for the
two one-dimensional images and a basis of the last summand. In this basis
U = e_1 e_1^T and V = e_2 e_2^T. Changing this fixed basis permutes the
complete header domain. It suffices to count this canonical pair.

Write X = (u,v) for the first two columns of G, and Y = (a;b) for the first
two rows of G^-1. Then YX = I_2 and the conjugated requests are I-ua and I-vb.
Conversely every pair X,Y with YX = I_2 arises. The remaining columns of G
can be any ordered basis of ker(Y), giving exactly |GL_(m-2)(K)| headers
for every such pair. There are (q^m-1)(q^m-q) choices of X. Each row of Y
solves two independent linear equations, giving q^(m-2) choices per row.
Thus there are D(q,m) pairs, all with the same header fiber.

The rank-one determinant identity gives

```text
det((I-ua)[1..j,1..j]) = 1 - sum_(i=1)^j a_i u_i.
```

The identity holds by multilinearity: choosing the rank-one part from two
columns gives zero, leaving the identity term and j single-column terms.
This is the corank-one guard reduction of #4227, with the proof included
here to specify the exact interface.

Let x_i = (u_i,v_i) be row i of X and y_i = (a_i,b_i)^T be column i of Y.
The partial sums A_j = sum_(i=1)^j y_i x_i have their two diagonal entries
equal to the prefix sums in the two determinant guards. Thus each A_j
for 1 <= j < m must belong to S, and A_m = YX = I_2. There are no other
guard conditions: both requests have rank m-1.

For a fixed increment A, the number of ordered pairs y,x with yx=A is
w(A). For zero, either x=0 or y=0, giving 2q^2-1 pairs. For a nonzero
rank-one matrix, choose one factorization; all others rescale its factors
by a nonzero scalar and its inverse, giving q-1 pairs. Rank two is
impossible. The coordinate choices are independent before imposing their
sum, so the recurrence counts every admissible X,Y once. The equal fibers
then prove both formulas. S has q-1 choices for each diagonal entry and q
for each off-diagonal entry. QED.

## Binary closed form and correlation

Put n=m-1. Define

```text
C(2,m) = (9^n - 2*7^n + 5^n)/4.
```

**Theorem 2.** This is the exact joint numerator in Theorem 1 for every
m >= 2. Hence

```text
Pr(P and Q pass) = (9^(m-1) - 2*7^(m-1) + 5^(m-1))
                  / (4(2^m-1)(2^m-2)2^(2m-4)).
```

It vanishes exactly at m=2 and is positive for every m>=3. For example,
the fractions at m=3,4,5,6 are 1/84, 1/80, 149/14880 and 85/11904.

**Proof.** In F_2, both diagonal entries of a safe state must be zero.
The safe states are determined by their off-diagonal bits. A safe-state
increment can only be zero, E_12 or E_21, with weights 7,1,1. The fourth
zero-diagonal matrix has rank two and weight zero. The last increment
I_2-A has both diagonal entries one, and has rank one exactly when both
off-diagonal entries of A are one. Its weight is then one.

We therefore need the number of length-n walks from (0,0) to (1,1), with
seven stationary choices and one choice toggling each bit. The four
characters of F_2^2 have eigenvalues 9,7,7,5. Character inversion at (1,1)
gives (9^n-7^n-7^n+5^n)/4. Equivalently, expanding
(7+x+y)^n modulo x^2=y^2=1 and extracting xy gives the same expression.

For n=1 the count is zero. For n>=2, the word containing one E_12, one
E_21 and n-2 zero increments gives a positive count. QED.

**Corollary.** The two full-guard passing events are strictly negatively
correlated over F_2 for every m>=2. Their joint fraction is asymptotic to
(1/4)(9/16)^(m-1), and its ratio to the product of the marginal fractions
tends to one from below.

**Proof.** The single corank-one fraction, from #4227, is
s_m = 3^n/((2^m-1)2^(m-1)). The binary guard reduction also proves it
directly: the first n coordinate products are zero, giving three choices
each, and the last product is one. A normalized rank-one factor pair has
(2^m-1)2^(m-1) possibilities and equal header fibers. Therefore

```text
joint / s_m^2 = (2^m-1)/(2^m-2)
               * (1 - 2(7/9)^n + (5/9)^n).
```

This is less than one because
(2^(n+1)-1)(2*7^n-5^n) > 2^n 7^n > 9^n for n>=1. The stated limits
follow by dividing the exact numerator and denominator by their leading
powers. QED.

## Scope

The general transfer theorem covers all finite fields, but the replay
implements q in {2,3,4,5,7}; F_4 uses x^2+x+1. Only q=2 has a closed form
here. The proof is written mathematics, without a proof-kernel check.
The binary case is outside the odd-prime preparation domain of the retained
normalizer. Its algebraic count does not admit a binary physical caller.
Even the odd-field recurrence supplies no request producer, header selection
or emission, dispatch, dirty return, stock or complete cost invoice. Neither
a supplier nor a complete multiplication theorem follows.
