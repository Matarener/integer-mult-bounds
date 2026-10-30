# Commuting dyadic repairs of the H6 complement

This scoped proof was produced by Nick Petalas. Its H6 spectral premises
and the unrestricted rank-560 comparison are cited from Ross Richardson's
[PR3655](https://github.com/CrocSwap/integer-mult-bounds/pull/3655),
head `7bf23e128e58a33c019268f57129629f603547f7`. They are not audited here.

## Statement and inherited premises

Put D=Z[1/2]. Let K be the symmetric dyadic H6 matrix on N=30960 ports
from the cited source, and put C=I-K. Its cited characteristic polynomial is

```text
char_K(x) = x^30144 (x-39)^224 (x-45)^560
            (x^2+186x-6075)^16.
```

For every B in M_N(D) satisfying BK=KB and C+B in GL_N(D),

```text
ker_Q B is contained in ker_Q K,
rank_Q B >= 816.
```

The minimum is exactly 816. B=K attains it because C+B=I and the cited
symmetry and characteristic polynomial give rank K=816. In particular,
every polynomial correction B=f(K) with dyadic coefficients obeys this
lower bound. The attaining correction cancels the kernel response. It
does not supply an encoder or a useful physical source operation.

The cited unrestricted minimum is 560. Consequently every rank-560 dyadic
repair must fail to commute with K. The new cost of this commutation
restriction is exactly 256 rational rank units. These units are correction
matrix ranks, not Gaussian child ranks or paid native calls.

## An invariant-kernel lemma

Let C,B be finite square matrices over D with BC=CB and R=C+B in GL(D).
Let M=ker_D B. This submodule is saturated: if nonzero d in D and dx is
in M, then dBx=0 in a torsion-free module, so Bx=0. Because D is a PID,
M is free and is a direct summand of D^N. Its rank is dim_Q ker_Q B.
This also follows by clearing a denominator from any rational kernel
vector to obtain a vector in M.

B commutes with R. It therefore commutes with R inverse, which has dyadic
entries. Both R and R inverse preserve M, so R restricts to a dyadic
automorphism of M. On M, R=C. It follows that C restricted to M is an
automorphism, and its determinant is a unit of D.

In a D basis extending a basis of M, C is block upper triangular. Thus
the characteristic polynomial of C restricted to M is a monic divisor
of char_C in D[z]. Its constant coefficient is a dyadic unit. This is the
obstruction: an invariant kernel of a commuting correction cannot retain
a characteristic factor with a nonunit constant coefficient.

The argument holds for every finite N. It permits arbitrary mixing inside
repeated eigenspaces. It does not assume that B is symmetric, diagonal,
normal, diagonalizable, or a polynomial in C.

## Apply the lemma to H6

Substitution z=1-x gives the cited C characteristic factors

```text
char_C(z) = (z-1)^30144 (z+38)^224 (z+44)^560
            (z^2-188z-5888)^16.
```

The quadratic is irreducible over Q. Its discriminant is
58896=144*409, and 20^2<409<21^2. Unique factorization in Q[z] implies
that the characteristic polynomial of C restricted to M has the form

```text
(z-1)^a (z+38)^b (z+44)^c (z^2-188z-5888)^d,
0<=a<=30144, 0<=b<=224, 0<=c<=560, 0<=d<=16.
```

Its determinant, up to sign, has absolute factors

```text
38^b 44^c 5888^d,
38=2*19, 44=4*11, 5888=256*23.
```

The 19-, 11- and 23-adic valuations are respectively b,c,d. A dyadic
unit has all three valuations zero, so b=c=d=0. Thus dim_Q ker B=a<=30144
and rank B>=30960-30144=816.

Furthermore C is diagonalizable over the reals because K is symmetric.
Its restriction to an invariant subspace has the same property. The only
remaining eigenvalue on M is 1, so C acts as the identity on M and K acts
as zero. This gives the stronger kernel containment in the statement.

Together with B=K, this proves the exact minimum. No H6 matrix entries,
Smith factors, predecessor counts or source programs need to be replayed
to deduce this new consequence of the cited characteristic polynomial.

## The hypotheses matter

For C=diag(3,5), the dyadic correction

```text
B = [[2,4],[-4,-8]],  rank B=1,
C+B = [[5,4],[-4,-3]],  det(C+B)=1
```

does not commute with C. Every commuting dyadic repair of this C has
rank two, by the lemma. Thus an unrestricted low-rank repair can genuinely
escape the conclusion. This example is a control for the new hypothesis,
not a replacement for the H6 predecessor's rank-560 certificate.

The ring hypothesis also matters. The commuting rational correction
B=diag(-14/5,0) has rank one and det(C+B)=1, but C+B=diag(1/5,5) is not a
matrix over D. Rational invertibility, or a determinant-one condition
without the dyadic entry condition, does not establish a dyadic automorphism.

Extra directions change the contract. For the one-dimensional C=[3],
the two-dimensional matrix [[3,1],[-1,0]] is unimodular. The theorem fixes
the original dimension and endpoint and makes no claim about such stable
extensions or their dirty-helper restoration.

## Verification boundary

The standalone checker enumerates an explicitly bounded two-dimensional
matrix domain and checks new abstract attaining endpoints under dyadic
conjugation. It also checks the stated characteristic-factor application,
its irreducibility condition, altered factor certificates and essential
hypotheses. Its output counts every domain actually executed.

The finite checks corroborate the invariant-kernel proof. They do not
establish the H6 spectrum, reconstruct its 30960-square matrix, audit the
rank-560 completion, synthesize a paid circuit or prove a multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.
