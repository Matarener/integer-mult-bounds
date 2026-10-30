# Exact spectrum and full side rank for the four-subset decoder

This is a scoped proof over Q, also valid over every characteristic-zero
field. It takes the definition of K from Cinna Davis's
[PR #2225](https://github.com/CrocSwap/integer-mult-bounds/pull/2225).
The predecessor's fitting, dyadic-coefficient and physical-support claims
are cited background. They are not reverified here.

Let n >= 5 be odd, let V be the set of four-subsets of [n], and put

    K(S,T) = binomial(|S intersection T|/2, 2).

The new conclusion is that I-K is invertible for every such n. Thus the
exact side response cannot factor through fewer than binomial(n,4) scalar
linear intermediates. This only excludes a factorization with no direct
source-to-output bypass. It is not a lower bound on arbitrary side circuits,
their work, native calls, or their paid rank profile.

## 1. Incidence decomposition

For j=1,2 let W_j have rows indexed by four-subsets and columns by
j-subsets, with entry one for containment and zero otherwise. Since

    binomial(t/2,2) = (1/4) binomial(t,2) - (1/8) binomial(t,1),

the definition gives

    8K = 2 W_2 W_2^T - W_1 W_1^T.                         (1)

Let B be the n-by-binomial(n,2) vertex/pair incidence matrix. Directly
counting four-subsets containing a prescribed union gives

    W_2^T W_2 = a I + (n-4) B^T B + J,
    a = (n-4)(n-5)/2,                                   (2)
    B B^T = (n-2) I + J,
    W_2 B^T = 3 W_1.                                    (3)

Here each J is the all-ones matrix of its displayed size. For (2), the
three entries, according to pair intersection size 2,1,0, are
binomial(n-2,2), n-3, 1. This proves (2) without invoking a spectrum theorem.

Assume n >= 7. Pair-coordinate space is the orthogonal direct sum

    E0 = constants,                       dimension 1,
    E1 = B^T {u : sum(u)=0},              dimension n-1,
    E2 = ker B,                          dimension binomial(n,2)-n.

The formula for B B^T shows that B has row rank n. The three eigenvalues
of W_2^T W_2 in (2) are respectively

    6 binomial(n-2,2), 3 binomial(n-3,2), binomial(n-4,2).

They are positive for n >= 7. Hence W_2 has full column rank and maps
these subspaces injectively into port space. The orthogonal complement
of its image has dimension binomial(n,4)-binomial(n,2).

On W_2 E0 the eigenvalue of W_1 W_1^T is 4 binomial(n-1,3), by its
constant row sum. On W_2 E2 it is zero, by (3). To check the remaining
space directly, counting vertex/pair incidences gives

    W_1^T W_2 = binomial(n-3,2) B + (n-3) J.

For sum(u)=0 use B B^T u=(n-2)u and W_1 u=W_2 B^T u/3.
It follows that W_1 W_1^T acts on W_2 E1 with eigenvalue
binomial(n-2,3). Both terms of (1) vanish on the remaining port space.

## 2. The spectrum

Substitution into (1) gives the following eigenvalues of K, with their
multiplicities. Coincident eigenvalues have additive multiplicities.

| Eigenvalue | Multiplicity |
| --- | ---: |
| (n-2)(n-3)(10-n)/12 | 1 |
| (n-3)(n-4)(20-n)/48 | n-1 |
| (n-4)(n-5)/8 | binomial(n,2)-n |
| 0 | binomial(n,4)-binomial(n,2) |

For odd n >= 7 the first three are nonzero, so rank(K)=binomial(n,2).
This rank statement concerns rational linear intermediates; it supplies
no implementation of a smaller dyadic feature basis.

For n=5, distinct four-subsets intersect in three points. Thus
K=(5/8)I+(3/8)J. Its eigenvalues are 5/2 once and 5/8 four times.
Its rank is five. The n>=7 incidence multiplicities do not apply here.

## 3. No eigenvalue is one

For the first eigenvalue, n=7 and n=9 give 5 and 7/2; every odd n>=11
gives a negative value. For the second, each odd n in [7,15] has numerator
at least 4*3*5=60>48. At n=17 and n=19 its numerators are 546 and 240.
Every odd n>=21 gives a negative value. For the third, n=7 gives 3/4;
every odd n>=9 gives at least 5/2. The zero eigenvalue and the two n=5
eigenvalues also differ from one.

Therefore I-K is invertible for every allowed n. For the first requested
side-map instance n=9, the exact spectra are

    K:     (7/2)^1, (55/8)^8, (5/2)^27, 0^90;
    I-K:   (-5/2)^1, (-47/8)^8, (-3/2)^27, 1^90.

In particular, rank(K)=36 and rank(I-K)=126, and

    det(I-K) = 5 * 3^27 * 47^8 / 2^52.

The source incidence expansion has 45 features. Its feature count is not
asserted to be its rational rank.

## 4. The exact compression obstruction

If all source dependence reaches the output through h scalar linear
intermediates, the side map has a factorization I-K=D A, with A having h
rows and D having h columns. Therefore

    binomial(n,4) = rank(I-K) <= h.

This bound is sharp in that declared algebraic model: A=I and D=I-K use
exactly binomial(n,4) intermediates. No physical cost is assigned to this
attaining factorization. A direct identity contribution and a separate
compressed -K correction fall outside the no-bypass hypothesis and remain
available to a future side circuit. Dirty helpers, restoration, actual
frames, chronology, native orientation and a complete invoice still need
separate constructions and proofs.

## 5. Evidence and scope

The standalone verifier builds the complete integer matrix 8K directly
from intersections at n=5,7,9. Fraction-free elimination checks every
predicted eigenspace dimension and the full determinant of 8K-8I. It also
counts literal pair-incidence Gram entries at n=7,9 and checks the scalar
formulas on a bounded larger domain. The proof above, not that finite
domain, supplies the every-n quantifier. Mutations and an actual rank-four
compression control test the new conclusions. Nothing imports or replays
the predecessor's verifier. The output receipt is generated from results
and package hashes; no receipt is handwritten.

The new result was produced by Nick Petalas. The kernel definition,
decoder motivation and open side-map obligation are by Cinna Davis, with
the subset/compiler ancestry retained in PR #2225. Incidence decompositions
and the rank inequality for a product are classical. No new general
spectral method, supplier, kappa, selected-frontier update, formal-kernel
acceptance or independent human review is claimed.
