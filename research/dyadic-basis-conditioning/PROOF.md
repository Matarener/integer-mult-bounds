# Optimal conditioning with a prescribed dyadic row and column

This contribution was produced by Nick Petalas. Apache-2.0.

Write D=Z[1/2]. Let a=(a_1,a_2) be a real dyadic row and b=(b_1,b_2)^T
a real dyadic column with ab=1. A compatible completion is R in GL_2(D)
such that aR=e_1^T and Re_1=b. Equivalently, the first column of R is b
and the first row of R^{-1} is a. The Euclidean condition number is
cond_2(R)=||R||_2 ||R^{-1}||_2. Set A=a_1^2+a_2^2 and B=b_1^2+b_2^2.
Both are positive and AB>=1 by Cauchy-Schwarz.

## Theorem

Every compatible completion has the unique form

    R_{k,s} = [ b, s 2^k (-a_2,a_1)^T ],   k in Z, s in {1,-1}.

Put q_k=A 2^k+B 2^{-k}. Then

    cond_2(R_{k,s}) = (q_k+sqrt(q_k^2-4))/2.

The optimal exponents are exactly the integers satisfying

    2^{2k-1} <= B/A <= 2^{2k+1}.

There is one such integer except when B/A is an odd power of two,
meaning 2^{2j+1} for an integer j. In that case j and j+1 both minimize.
The sign s is free. These are all minimizers, with no hidden choice of
another basis vector.

## Proof of the classification

The first-column constraint writes R=[b,z]. The other constraint says az=0.
Since a is nonzero, the real kernel of a is the line spanned by
(-a_2,a_1)^T, so z=t(-a_2,a_1)^T for a unique real t. Directly,

    det R = t(a_1 b_1+a_2 b_2) = t.

Because R is a dyadic matrix, its determinant belongs to D. Invertibility
over D requires that determinant to be a unit. The units of D are exactly
s 2^k: a dyadic number and its reciprocal both have power-of-two
denominators exactly when its reduced numerator has no odd prime factor.
Thus t=s 2^k. Conversely every displayed R has dyadic entries, unit
determinant, first column b and aR=(1,0), so it is a compatible completion.
This also proves the asserted inverse-row characterization.

## Proof of the condition number and optimum

Let the singular values be sigma_1>=sigma_2>0, and put c=sigma_1/sigma_2.
Their squared sum is the squared Frobenius norm B+t^2 A. Their product is
|det R|=|t|. Therefore

    c+c^{-1} = (sigma_1^2+sigma_2^2)/(sigma_1 sigma_2)
             = B/|t|+A|t| = q_k.

Solving c^2-q_k c+1=0 with c>=1 proves the formula. This expression is
strictly increasing in q>=2. Hence minimizing q suffices. Its successive
differences have the sign of A 2^{2k+1}-B, because

    q_{k+1}-q_k = A 2^k-B 2^{-k-1}.

The differences are negative before their single sign change and positive
afterward. Comparing k with its two neighbors gives precisely the two
displayed inequalities. They cover all positive B/A, overlap only at the
stated equality boundaries, and exclude every other exponent globally.
This is an all-integer proof, rather than a bounded search.

An exact implementation needs two candidates. Let e=floor(log_2(B/A)),
computed by bit lengths and a rational comparison. The candidates are
floor(e/2) and floor(e/2)+1. Comparing their rational q values retains all
ties and requires neither logarithmic approximation nor eigenvalue rounding.

## Dyadic reversibility can cost more than real completion

If R is allowed to be any real invertible matrix with the same two
constraints, its parameter t can be any nonzero real number. Arithmetic-
geometric mean gives q(t)>=2 sqrt(AB), with equality exactly when
|t|=sqrt(B/A). Its optimum condition number is therefore

    sqrt(AB)+sqrt(AB-1).

The dyadic optimum equals that real optimum exactly when sqrt(B/A) is a
power of two. Otherwise the dyadic optimum is strictly greater. A dyadic
matrix that is merely invertible over Q need not be invertible over D;
allowing an odd determinant silently changes the arithmetic contract.

## The source pair

Ali Romman's PR5611 supplies a=(3,5), b=(2,-1)^T as a legal pair with no
individual unit entry in a, and gives the compatible completion
[[2,5],[-1,-3]]. That constructor and its correctness are cited, not audited.
The new optimization has A=34, B=5. At k=-1,

    R = [[2,-5/2],[-1,3/2]],    det R=1/2,    q=27,
    cond_2(R)=(27+sqrt(725))/2.

Indeed 1/8 < 5/34 < 1/2, so k=-1 is the unique optimal exponent.
Its two determinant signs are the only optimal completions. The cited
unit-determinant completion has q=39, so the new one is strictly better.
The unconstrained real optimum is sqrt(170)+13 and is strictly smaller
than the dyadic optimum, since 27^2>4*170. The example shows a genuine
arithmetic conditioning penalty rather than a numerical eigenvalue artifact.

At a=(1,0), b=(1,1)^T, B/A=2. Both k=0 and k=1 minimize, with q=3.
This is an exact tie control for the optimizer.

## Helper-interface scope

The source dual-pair interface is the motivation and the compatible input
contract. This theorem optimizes its two-role endpoint basis, without extra
roles. For arbitrary independent complex banks of the same positive size,
R tensor I and its inverse have these same Euclidean norms and condition
number, because their Gram matrices tensor the corresponding scalar Gram
matrix with I. This is a scalar bank change, not a tensor power of R.

Endpoint conditioning alone does not certify intermediate scalar growth,
componentwise rounded error, a gate-count optimum, a physically legal helper
cut, source delivery, dirty restoration in a complete word, frames, ownership,
stock, tape cost, compiler closure or outer funding. More workspace changes
the optimization domain. No selected assumption, complete multiplication
theorem, supplier admission or new kappa follows. The all-pair result is this
written proof; the accompanying finite checker corroborates it. Classical
two-by-two singular-value identities and dyadic-unit algebra are not claimed
as new general tools. Independent human and formal proof-kernel review are
unclaimed.
